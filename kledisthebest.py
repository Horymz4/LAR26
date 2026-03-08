from robolab_turtlebot import Turtlebot, Rate
import math

turtle = Turtlebot()
rate = Rate(10)

def turn_90_degrees(direction):
    """Turns exactly 90 degrees using sensor feedback."""
    # 1. Reset odometry so the current heading is 0
    turtle.reset_odometry()
    
    # Define target angle (90 deg = pi/2 rad)
    target = math.pi / 2
    speed = 0.2 if direction == "left" else -0.2
    
    # 2. Loop until the sensor 'a' value matches the target
    while not turtle.is_shutting_down():
        _, _, current_angle = turtle.get_odometry()
        
        # Check if we've reached the absolute value of 1.57 radians
        if abs(current_angle) >= target:
            break
            
        turtle.cmd_velocity(linear=0, angular=speed)
        rate.sleep()
    
    # 3. Stop movement
    turtle.cmd_velocity(0, 0)

def drive_straight(distance):
    """Drives a specific distance using x,y odometry."""
    turtle.reset_odometry()
    while not turtle.is_shutting_down():
        x, y, _ = turtle.get_odometry()
        # Calculate current distance from origin using Pythagoras
        current_dist = math.sqrt(x**2 + y**2)
        
        if current_dist >= distance:
            break
            
        turtle.cmd_velocity(linear=0.2, angular=0)
        rate.sleep()
    turtle.cmd_velocity(0, 0)

# --- EXECUTION ---
# First, the +90 turn you requested
turn_90_degrees("left")
turn_90_degrees("left")
# Then, the 4 sides of the square with -90 (right) turns
for _ in range(4):
    drive_straight(1) # Move 0.5 meters
    turn_90_degrees("right")
