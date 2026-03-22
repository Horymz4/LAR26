import threading, time
import numpy as np
from robolab_turtlebot import Turtlebot, Rate, get_time

from hsv_seg import find_ball, find_garage_center
from calibrate import get_green_ball_average_color_bgr
from beep_beep import ParkController


Button_press = threading.Event()
StateofBumper = threading.Event()
garage_stage = threading.Event()
outgarage_stage = threading.Event()
see_garage = threading.Event()
ending_stage = threading.Event()
processing_image = threading.Event()


vision_data = {"pos":None, "radius":None, "avg_x":None, "dist":None}
vision_lock = threading.Lock()
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']
button_states = ["pressed","not pressed"]

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
    print("Start bumper vlákna")

    turtle.register_bumper_event_cb(bumper_cb)
    StateofBumper.wait()
    
    print("Konec bumper vlákna")


def reasoning(pos,radius,avg_x,dist):
    IMG_CENTER_X = 334
    if (not garage_stage.is_set()) and radius is not None and pos is not None and 150 > radius > 5 and IMG_CENTER_X + 30 > pos[0] > IMG_CENTER_X - 30:
        garage_stage.set()
        print("SEE BALL")
    if (not outgarage_stage.is_set()) and radius is not None and pos is not None and 70 > radius > 55:
        outgarage_stage.set()
        print("BALL CLOSE")
    if (not see_garage.is_set()) and avg_x is not None and IMG_CENTER_X + 30 > avg_x > IMG_CENTER_X - 30:
        see_garage.set()
        print("SEE GARAGE")
    if (not ending_stage.is_set()) and dist is not None and see_garage.is_set() and dist < 2:
        ending_stage.set()
        print("PARKING")

def pohyb(turtle):
    print("Start pohybového vlákna")
    rate = Rate(10)

    stage1(turtle,rate) #garage
    stage2(turtle,rate) #going to the ball
    stage3(turtle,rate) #going round the ball
    stage4(turtle,rate) #garage
    stage5(turtle,rate) #parking
 
    print("Konec pohybového vlákna")

def stage1(turtle,rate):
    print("Stage 1 start")

    lin_speed = 0
    ang_speed = -np.pi/20
    while not StateofBumper.is_set() and not garage_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        set_process_img()


    turtle.cmd_velocity(linear = 0, angular = 0)
    print("Stage 1 end")
    time.sleep(1)
    

def stage2(turtle,rate):
    print("Stage 2 start")

    ang_speed = 0
    lin_speed = 0.08
    while not StateofBumper.is_set() and not outgarage_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        ang_speed = P_reg_ball()    # max ≈ 0.8 rad/s
        set_process_img()

    turtle.cmd_velocity(linear = 0, angular = 0)
    time.sleep(1)
    print("Stage 2 end")

def stage3(turtle,rate):
    print("Stage 3 start")

    do_half_circle(turtle,rate )
    get_close_to_ball(turtle,rate)

    print("Stage 3 end")

def stage4(turtle,rate):
    print("Stage 4 start")

    looking_for_garage_spin(turtle,rate)
    get_close_to_garage(turtle,rate)

    print("Stage 4 end")


def stage5(turtle,rate):
    print("Stage 5 start")

    park = ParkController(stop_dist=0.47, sound=True)
    while not StateofBumper.is_set():
        done = park.step(turtle)
        if done:
            print("Zaparkováno!")
            break
        rate.sleep()

    turtle.cmd_velocity(linear=0, angular=0)
    print("Stage 5 end")
    time.sleep(1)

def P_reg_gar():
    IMG_CENTER_X = 334
    with vision_lock:
        if vision_data["avg_x"] is not None:
            avg_x = vision_data["avg_x"]
            error_x = avg_x - IMG_CENTER_X
        else: error_x = 0
    print(f'errorP: {error_x}')
    return ((-error_x / IMG_CENTER_X) * 1.2) 

def P_reg_ball():
    IMG_CENTER_X = 334
    radius = pos = None
    with vision_lock:
        if vision_data["pos"] is not None:
            pos = vision_data["pos"][0]
            radius = vision_data["radius"]
    if radius is not None and pos is not None:
        error_x = pos - IMG_CENTER_X
    else: error_x = 0
    print(f'errorP: {error_x}')
    return ((-error_x / IMG_CENTER_X) * 0.8) 

def get_close_to_ball(turtle,rate):
    print("Get close to ball start")   

    min = 0.4
    back_to_0 = 0.2
    lin_speed = 0.14      
    ang_speed = 0.4 
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
            print(f"Left origin zone ")

        if left_origin and dist < back_to_0:
            print(f"Returned to origin with tolerance ", back_to_0)
            break
        set_process_img()
        # TODO PROCESSING IMAGE SET ??

    print("Get close to ball end")  
    turtle.cmd_velocity(linear = 0, angular = 0)
    time.sleep(1) 


def looking_for_garage_spin(turtle,rate):
    print("looking for garage spin start")

    lin_speed = 0
    ang_speed = -np.pi/12
    while not StateofBumper.is_set() and not see_garage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()   
        set_process_img()

    turtle.cmd_velocity(linear = 0, angular = 0)
    print("looking for garage spin end")
    time.sleep(1)

def get_close_to_garage(turtle,rate):
    print("getting close to garage start")

    IMG_CENTER_X = 334
    ang_speed = 0
    lin_speed = 0.08
    while not StateofBumper.is_set() and not ending_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()

        ang_speed = P_reg_gar() 
        set_process_img()

    turtle.cmd_velocity(linear = 0, angular = 0)
    print("getting close to garage end")
    time.sleep(1)

def do_half_circle(turtle,rate):
    print("Half circle maneuver start")
    
    turtle.reset_odometry()
    t = get_time()
    lin_speed = 0
    ang_speed = -np.pi/8
    while get_time() - t < 8 and not StateofBumper.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()

    turtle.cmd_velocity(linear = 0, angular = 0)
    print("Half circle maneuver end")
    time.sleep(1)

def obraz(turtle,ref_img):
    print("Start obrazového vlákna")

    pos = (0,0)
    radius = 0
    avg_x = 0
    dist = 0
    while not StateofBumper.is_set():
        if not processing_image.is_set():
            turtle.wait_for_rgb_image()
            rgb = turtle.get_rgb_image()
            if not outgarage_stage.is_set():
                pos,radius = ball_image(rgb,ref_img)
            else:
                avg_x, dist = garage_image(rgb, [100,86,134], turtle)

            processing_image.set()
            reasoning(pos,radius,avg_x,dist)

    print("Konec obrazového vlákna")

def ball_image(rgb, ref_img):
    pos, radius = find_ball(rgb,ref_img)
    with vision_lock:
        vision_data["pos"] = pos
        vision_data["radius"] = radius
    if pos is not None: print(f'position: {pos} radius {radius}\n')
    return pos,radius

def garage_image(rgb,ref,turtle):
    avg_x, dist = find_garage_center(rgb, ref, turtle)
    with vision_lock:
        vision_data["avg_x"] = avg_x
        vision_data["dist"] = dist
    return avg_x, dist

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

def set_process_img():
    if processing_image.is_set():
        processing_image.clear()
        processing_image.wait()

def main():
    turtle = Turtlebot(rgb=True, depth=True, pc = True)

    # ref = calibrate(turtle)
    ref = [38, 120, 76]
    print("Starting threads")

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
