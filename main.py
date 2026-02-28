from __future__ import print_function
import threading

from robolab_turtlebot import Turtlebot, Rate, get_time

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

StateofBumper = 0

def bumper_cb(msg):
    """Bumber callback."""

    global StateofBumper
    # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper = bumper_names[msg.bumper]

    # msg.state stores the event 0:RELEASED, 1:PRESSED
    state = state_names[msg.state]
    if msg.state == 1:
        StateofBumper = 1
    else: 
        StateofBumper = 0

    # Print the event
    print('{} bumper {}'.format(bumper, state))


def main():
    # Initialize turtlebot class
    turtle = Turtlebot(rgb=True, depth=True, pc=True)

    rate = Rate(10)
    t = get_time()
    t1 = threading.Thread(target=bumper, args=(turtle))
    t2 = threading.Thread(target=obraz, args=(turtle))
    t3 = threading.Thread(target=pohyb, args=(turtle))
    arr = [t1,t2,t3]
    for i in arr:
        i.start()
    for i in arr:
        i.join()
    print("All threads completed")


        


def bumper(turtle):
    while StateofBumper == 0:
        turtle.register_bumper_event_cb(bumper_cb)

def pohyb(turtle):
    while True: turtle.cmd_velocity(linear=0.05)


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
