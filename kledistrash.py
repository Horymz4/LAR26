from __future__ import print_function
import threading, time, sys
import numpy as np
from robolab_turtlebot import Turtlebot, Rate, get_time

from imageio import imwrite 

StateofBumper = threading.Event()
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
    print('{} bumper {}'.format(bumper, state))


def bumper(turtle):
    turtle.register_bumper_event_cb(bumper_cb)
    StateofBumper.wait()

def pohyb(turtle):
    # Move forward until bumper pressed
    while not StateofBumper.is_set():
        turtle.cmd_velocity(linear=0.1)
        time.sleep(0.05)   # small delay to reduce CPU usage

    # Stop robot
    turtle.cmd_velocity(linear=0)

def obraz(turtle):
    i = 0
    while not StateofBumper.is_set():
        turtle.wait_for_rgb_image()
        rgb = turtle.get_rgb_image()
        filename = "image" + str(i) + ".png"
        i += 1 
        print(f'Image saved as {filename}')
        imwrite(filename, rgb)
def main():
    # Initialize turtlebot class
    turtle = Turtlebot(rgb=True)

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
