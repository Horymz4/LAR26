from __future__ import print_function
import threading
import time

from robolab_turtlebot import Turtlebot, Rate, get_time
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
        turtle.cmd_velocity(linear=0.5)
        time.sleep(0.05)   # small delay to reduce CPU usage

    # Stop robot
    turtle.cmd_velocity(linear=0)

def obraz(turtle):
    while turtle.is_shutting_down(self) == 0:
        print("obraz")

def main():
    # Initialize turtlebot class
    turtle = Turtlebot(rgb=True, depth=True)

    rate = Rate(10)
    t = get_time()
    t1 = threading.Thread(target=bumper, args=(turtle,))
    # t2 = threading.Thread(target=obraz, args=(turtle,))
    t3 = threading.Thread(target=pohyb, args=(turtle,))
    arr = [t1,t3]
    for i in arr:
        i.start()
    for i in arr:
        i.join()
    print("All threads completed")


        
if __name__ == '__main__':
    main()
