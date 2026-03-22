from __future__ import print_function
import threading, time, sys
import numpy as np
import cv2 as cv
from robolab_turtlebot import Turtlebot, Rate, get_time

from hsv_seg import find_ball, find_garage_center, find_rectangles
from calibrate import get_green_ball_average_color_bgr
from beep_beep import ParkController
# from ezisop import go_to_origin
#from kledisbest import make_square
from imageio import imwrite 

Button_press = threading.Event()
StateofBumper = threading.Event()
garage_stage = threading.Event()
outgarage_stage = threading.Event()
see_garage = threading.Event()
ending_stage = threading.Event()
processing_image = threading.Event()

pi = np.pi
IMG_CENTER_X = 320

vision_data = {"pos":None, "radius":None}
vision_lock = threading.Lock()
# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']
button_states = ["pressed","not pressed"]
# coppied from the example script
def bumper_cb(msg):
    bumper = bumper_names[msg.bumper]
    state = state_names[msg.state]
    if msg.state == 1:
        StateofBumper.set()
    print(f'{bumper} bumper {state}')

def button_cb(msg):
    state = button_states[msg.state]
    if msg.state == 1:
        Button_press.set()
    print(f'{state}')

def bumper(turtle):
    turtle.register_bumper_event_cb(bumper_cb)
    StateofBumper.wait()


def reasoning(turtle,pos,radius,avg_x):
    if (not garage_stage.is_set()) and radius is not None and pos is not None and 150 > radius > 15 and 350 > pos[0] > 290:
        time.sleep(0.1)
        garage_stage.set()
    if (not outgarage_stage.is_set()) and radius is not None and pos is not None and 70 > radius > 55:
        outgarage_stage.set()
        print("Ball close")
    if (not see_garage.is_set()) and avg_x is not None and 350 > avg_x > 290:
        see_garage.set()
        print("garage seen")

def pohyb(turtle):
    print("Start pohybového vlákna")
    rate = Rate(10)

    #garage
    lin_speed = 0
    ang_speed = -pi/20
    while not StateofBumper.is_set() and not garage_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        
        if processing_image.is_set():
            processing_image.clear()
            processing_image.wait()   

    turtle.cmd_velocity(linear = 0, angular = 0)
    print("Ball centred")
    time.sleep(1)

    #outgarage_stage
    ang_speed = 0
    lin_speed = 0.08
    while not StateofBumper.is_set() and not outgarage_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        radius = pos = None
        with vision_lock:
            if vision_data["pos"] is not None:
                pos = vision_data["pos"][0]
                radius = vision_data["radius"]
        if radius is not None and pos is not None:
            error_x = pos - IMG_CENTER_X
        else: error_x = 0
        print(f'errorP: {error_x}')

        ang_speed = -error_x / IMG_CENTER_X * 0.8    # max ≈ 0.8 rad/s
        if processing_image.is_set():
            processing_image.clear()
            processing_image.wait()

    turtle.cmd_velocity(linear = 0, angular = 0)
    time.sleep(2)

    print("Odometry reseted")
    turtle.reset_odometry()

    #ball_stage
    t = get_time()
    lin_speed = 0
    ang_speed = -pi/8
    while get_time() - t < 8:
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
    min = 0.4
    back_0 = 0.1
    lin_speed = 0.15      
    ang_speed = 0.50 
    left_origin = False

    while not StateofBumper.is_set():
        odometry = turtle.get_odometry() 
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()

        x, y = odometry[0], odometry[1]
        dist = np.sqrt(x**2 + y**2)
        print(odometry,dist,left_origin)

        if not left_origin and dist > min:
            left_origin = True
            print(f"Left origin zone (dist={dist:.2f} m), watching for return")
 
        if left_origin and dist < back_0:
            print(f"Returned to origin (dist={dist:.3f} m), circle done")
            break


    #ending_stage
    lin_speed = 0
    ang_speed = -pi/24
    while not StateofBumper.is_set() and not see_garage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()   

        if processing_image.is_set():
            processing_image.clear()
            processing_image.wait()
    
    turtle.cmd_velocity(linear = 0, angular = 0)
    time.sleep(1)

    park = ParkController(stop_dist=0.47, sound=True)

    while True:
        done = park.step(turtle)

        if done:
            print("Zaparkováno!")
            break

        rate.sleep()

    # Stop robot
    turtle.cmd_velocity(linear=0, angular=0)

def obraz(turtle,ref_img):
    print("Start obrazového vlákna")

    pos = (0,0)
    radius = 0
    while not StateofBumper.is_set():
        if not processing_image.is_set():
            turtle.wait_for_rgb_image()
            rgb = turtle.get_rgb_image()
            
            if not outgarage_stage.is_set():
                pos, radius = find_ball(rgb,ref_img)
                with vision_lock:
                    vision_data["pos"] = pos
                    vision_data["radius"] = radius
            else:
                avg_x = find_garage_center(rgb, [100,86,134])
            processing_image.set()
            print(f'position: {pos} radius {radius}\n')
        
            reasoning(turtle,pos,radius,avg_x) 

def calibrate(turtle):
    print("Start kalibrace")

    turtle.register_button_event_cb(button_cb)
    Button_press.wait()
    Button_press.clear()

    turtle.wait_for_rgb_image()
    rgb = turtle.get_rgb_image()
    ref_image = get_green_ball_average_color_bgr(rgb)
    
    turtle.register_button_event_cb(button_cb)
    Button_press.wait()
    print("Konec kalibrace")

    return ref_image


def main():
    turtle = Turtlebot(rgb=True, depth=True, pc = True)

    # ref = calibrate(turtle)
    ref = [67, 128, 105]
    print("Starting threads")
    # rate = Rate(10)
    t1 = threading.Thread(target=bumper, args=(turtle,))
    t2 = threading.Thread(target=obraz, args=(turtle,ref))
    t3 = threading.Thread(target=pohyb, args=(turtle,))
    arr = [t1,t2,t3]
    for i in arr:
        i.start()
    for i in arr:
        i.join()
    print("All threads completed")

if __name__ == '__main__':
    main()
