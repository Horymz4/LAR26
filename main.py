from __future__ import print_function

from robolab_turtlebot import Turtlebot, Rate, get_time

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']


bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']


def bumper_cb(msg):
    """Bumber callback."""
    # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper = bumper_names[msg.bumper]

    # msg.state stores the event 0:RELEASED, 1:PRESSED
    state = state_names[msg.state]

    # Print the event
    print('{} bumper {}'.format(bumper, state))


def main():
    # Initialize turtlebot class
    turtle = Turtlebot(rgb=True, depth=True, )

    press = turtle.register_bumper_event_cb(bumper_cb)
    t = get_time()
    
    rate = Rate(10)
    while ((get_time() - t) < 20) and turtle.register_bumper_event_cb(bumper_cb != "PRESSED"):
         
        turtle.cmd_velocity(linear=0.1)
        rate.sleep()




if __name__ == '__main__':
    main()
