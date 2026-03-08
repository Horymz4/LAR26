from __future__ import print_function
import threading, time, sys
import numpy as np
import cv2 as cv
from robolab_turtlebot import Turtlebot, Rate, get_time


# from pepa import get_ball_position_and_radius
from hsv_seg import find_ball, find_rectangles
from ezisop import go_to_origin
from imageio import imwrite 

StateofBumper = threading.Event()
garage_stage = threading.Event()
outgarage_stage = threading.Event()
ball_stage = threading.Event()
ending_stage = threading.Event()
processing_image = threading.Event()

pi = np.pi

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

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

def reasoning(turtle,pos,radius):
    if (not garage_stage.is_set()) and radius is not None and pos is not None and 150 > radius > 15 and 350 > pos[0] > 250:
        garage_stage.set()
    elif (not outgarage_stage.is_set()) and radius is not None and pos is not None and 70 > radius > 45:
        outgarage_stage.set()
        print("Ball close")
def make_square(turtle):
    pass
def pohyb(turtle):
    lin_speed = 0
    ang_speed = pi/24

    # Go 
    while not StateofBumper.is_set() :
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)

        if not garage_stage.is_set():
            if  processing_image.is_set():
                lin_speed = 0
                ang_speed = pi/24
                processing_image.clear()
                processing_image.wait()

        elif not outgarage_stage.is_set():
            if  processing_image.is_set():
                lin_speed = 0.1
                ang_speed = 0
                processing_image.clear()
                processing_image.wait()

        elif not ball_stage.is_set():
            make_square(turtle)
        elif not ending_stage.is_set():
            lin_speed = 0.05
            ang_speed = 0
    # Stop robot
    turtle.cmd_velocity(linear=0, angular=0)

def obraz(turtle):
    pos = (0,0)
    radius = 0
    while not StateofBumper.is_set():
        if not processing_image.is_set():
            turtle.wait_for_rgb_image()
            rgb = turtle.get_rgb_image()
            
            # cv.imshow("asdad",rgb)
            print(np.unique(rgb.reshape(-1,3), axis=0)[:20])
            sanitycheck = rgb.copy() 
            # print(sanitycheck)
            pos, radius = find_ball(sanitycheck,[100,149,100])
            processing_image.set()
            print(f'position: {pos} radius {radius}\n')
        
            reasoning(turtle,pos,radius) 

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
