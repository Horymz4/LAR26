from robolab_turtlebot import Turtlebot, Rate
import math

turtle = Turtlebot()
rate = Rate(10)

# Constants
LIN_SPEED = 0.2   # meters per second
ANG_SPEED = 0.5   # radians per second
SIDE_TIME = 2.0   # seconds to drive straight
# 90 degrees is pi/2 radians. Time = distance / speed
TURN_TIME = (math.pi / 2) / ANG_SPEED 

def move(linear, angular, duration):
    # Resetting the time to track this specific movement
    start_time = turtle.get_time()
    while turtle.get_time() - start_time < duration:
        turtle.cmd_velocity(linear=linear, angular=angular)
        rate.sleep()
    # Stop briefly after every action
    turtle.cmd_velocity(0, 0)
    rate.sleep()

# 1. Initial +90 degree turn (Counter-Clockwise)
move(0, ANG_SPEED, TURN_TIME)

# 2. The four sides of the square with -90 degree turns (Clockwise)
for _ in range(4):
    move(LIN_SPEED, 0, SIDE_TIME)  # Go linear
    move(0, -ANG_SPEED, TURN_TIME) # Turn -90 degrees
