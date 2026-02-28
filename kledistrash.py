from __future__ import print_function
import threading, time, sys
import numpy as np
from robolab_turtlebot import Turtlebot, Rate, get_time

from magic import get_ball_position_and_radius, detect_two_largest_rectangles
from imageio import imwrite 

StateofBumper = threading.Event()
garage_stage = threading.Event()
outgarage_stage = threading.Event()
ball_stage = threading.Event()
ending_stage = threading.Event()

pi = np.pi

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

StateofBumper = threading.Event()   

def bumper_cb(msg):
    """Bumber callback."""
    # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper = bumper_names[msg.bumper]
    # msg.state stores the event 0:RELEASED, 1:PRESSED
    state = state_names[msg.state]
    if msg.state == 1:
        StateofBumper.set()

    # Print the event
    print(f'{bumper} bumper {state}')


def bumper(turtle):
    turtle.register_bumper_event_cb(bumper_cb)
    StateofBumper.wait()

def pohyb(turtle):
    lin_speed = 0
    ang_speed = pi/6

    # Go 
    while not StateofBumper.is_set() :
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        time.sleep(0.05)

        if not garage_stage.is_set():
            lin_speed = 0
            ang_speed = pi/6

        elif not outgarage_stage.is_set():
            lin_speed = 0.05
            ang_speed = 0

        elif not ball_stage.is_set():
            lin_speed = 0.05
            ang_speed = pi/12

        elif not ending_stage.is_set():
            lin_speed = 0.05
            ang_speed = 0
        
    # Stop robot
    turtle.cmd_velocity(linear=0, angular=0)

def obraz(turtle):
    (x,y) = (0,0)
    radius = 0
    while not StateofBumper.is_set():
        turtle.wait_for_rgb_image()
        rgb = turtle.get_rgb_image()

        #temporary fix 
        # filename = "image.png"
        # print(f'Image saved as {filename}')
        # imwrite(filename,rgb)

        (x, y), radius = get_ball_position_and_radius(rgb,[100,86,134])
        if 280 > x > 320:
            pass

def main():
    # Initialize turtlebot class
    turtle = Turtlebot(rgb=True, depth=True)

    rate = Rate(10)
    # t = get_time()
    t1 = threading.Thread(target=bumper, args=(turtle,))
    t2 = threading.Thread(target=obraz, args=(turtle,))
    t3 = threading.Thread(target=pohyb, args=(turtle,))
    arr = [t1,t2,t3]
    for i in arr:
        i.start()
    for i in arr:
        i.join()
    print("All threads completed")


        
if __name__ == '__main__':
    main()
