import threading
from robolab_turtlebot import Turtlebot, Rate, get_time

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
    #turtle = Turtlebot(rgb=True, depth=True, pc=True)

    rate = Rate(10)
    turtle.register_bumper_event_cb(bumper_cb)
    t = get_time()
    
    while ((get_time() - t) < 20) and (StateofBumper == 0):
        turtle.register_bumper_event_cb(bumper_cb)
        rate.sleep()

