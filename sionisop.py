from __future__ import print_function
import threading, time, sys
import numpy as np
import cv2 as cv
from robolab_turtlebot import Turtlebot, Rate, get_time

from hsv_seg import find_ball, find_rectangles
from calibrate import get_green_ball_average_color_bgr
# from ezisop import go_to_origin
#from kledisbest import make_square
from imageio import imwrite 

Button_press = threading.Event()
StateofBumper = threading.Event()
garage_stage = threading.Event()
outgarage_stage = threading.Event()
ball_stage = threading.Event()
ending_stage = threading.Event()
processing_image = threading.Event()

pi = np.pi
IMG_CENTER_X = 300

vision_data = {"pos":None, "radius":None}

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

def reasoning(turtle,pos,radius):
    if (not garage_stage.is_set()) and radius is not None and pos is not None and 150 > radius > 15 and 312.5 > pos[0] > 287.5:
        turtle.cmd_velocity(linear = 0, angular = 0)
        time.sleep(0.1)
        garage_stage.set()
    elif (not outgarage_stage.is_set()) and radius is not None and pos is not None and 70 > radius > 45:
        outgarage_stage.set()
        print("Ball close")
        turtle.cmd_velocity(linear=0, angular=0)

def pohyb(turtle):
    print("start pohyb")
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

    #outgarage_stage
    ang_speed = 0
    lin_speed = 0.05
    while not StateofBumper.is_set() and not outgarage_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        
        error_x = vision_data["pos"][0] - IMG_CENTER_X
        print(f'errorP: {error_x}')
        ang_speed = -error_x / IMG_CENTER_X * 0.8    # max ≈ 0.8 rad/s
        if processing_image.is_set():
            processing_image.clear()
            processing_image.wait()
    



        # elif not ball_stage.is_set():
        #     print("HEHE")
        #     #make_square(turtle)
        # elif not ending_stage.is_set():
        #     lin_speed = 0.05
        #     ang_speed = 0
    # Stop robot
    turtle.cmd_velocity(linear=0, angular=0)

def obraz(turtle,ref_img):
    pos = (0,0)
    radius = 0
    while not StateofBumper.is_set():
        if not processing_image.is_set():
            turtle.wait_for_rgb_image()
            rgb = turtle.get_rgb_image()
            
            sanitycheck = rgb.copy() 

            pos, radius = find_ball(sanitycheck,ref_img)
            vision_data["pos"] = pos
            vision_data["radius"] = radius
            processing_image.set()
            print(f'position: {pos} radius {radius}\n')
        
            reasoning(turtle,pos,radius) 

def calibrate(turtle):
    turtle.register_button_event_cb(button_cb)
    Button_press.wait()
    Button_press.clear()

    turtle.wait_for_rgb_image()
    rgb = turtle.get_rgb_image()
    ref_image = get_green_ball_average_color_bgr(rgb)
    
    turtle.register_button_event_cb(button_cb)
    Button_press.wait()

    return ref_image


def main():
    turtle = Turtlebot(rgb=True, depth=True)

    ref = calibrate(turtle)
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
