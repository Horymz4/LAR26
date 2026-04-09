import time
import numpy as np
from threading_variables import garage_stage, StateofBumper,odometry_stage, outgarage_stage, see_garage, ending_stage, exited_garage

from robolab_turtlebot import get_time
from utils import set_process_img,  P_reg_ball, P_reg_gar
from beep_beep import ParkController
from constants import linear_0, angular_0, stop_distance, angular_spinning, angular_around_the_ball, linear_around_the_ball, linear_the_rest, angular_quater_spin

def stage1(turtle, rate):
    time.sleep(0.5)
    find_opening(turtle,rate)
    go_forward_a_little(turtle,rate,8)

    turtle.reset_odometry()

def find_opening(turtle,rate):
    lin_speed = linear_0
    ang_speed = angular_spinning
    while not StateofBumper.is_set() and not exited_garage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        set_process_img()

    print("Opening found")
    turtle.cmd_velocity(linear_0, angular = angular_0)
    time.sleep(1)

    
# Stage 2 ------------------------------------
def stage2(turtle,rate):
    print("Stage 2 start")

    lin_speed = linear_0
    ang_speed =- angular_spinning
    while not StateofBumper.is_set() and not garage_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        set_process_img()


    turtle.cmd_velocity(linear_0, angular = angular_0)
    print("Stage 2 konec")
    time.sleep(1)
    

# Stage 3 ------------------------------------
def stage3(turtle,rate):
    print("Stage 3 start")

    ang_speed = angular_0
    lin_speed = linear_the_rest
    while not StateofBumper.is_set() and not outgarage_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        ang_speed = P_reg_ball()
        set_process_img()

    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    time.sleep(0.5)
    go_forward_a_little(turtle,rate, 4.2)
    print("Stage 3 konec")

def go_forward_a_little(turtle,rate,how_long):
    print("going a bit forward")

    ang_speed = angular_0
    lin_speed = linear_the_rest

    t = get_time()
    while not StateofBumper.is_set() and get_time() - t < how_long:
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        set_process_img()

    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    time.sleep(1)


# Stage 4 ------------------------------------
def stage4(turtle,rate):
    print("Stage 4 start")

    odometry = turtle.get_odometry()

    do_quater_spin(turtle,rate )
    go_around_the_ball(turtle,rate,odometry[0] ,odometry[1])

    odometry = turtle.get_odometry()
    print(f'odometry before axis {odometry}')
    return_to_axis(turtle,rate,odometry)

    print("Stage 4 konec")

def do_quater_spin(turtle,rate):
    print("Half circle maneuver start")
    
    t = get_time()
    lin_speed = linear_0
    ang_speed = angular_quater_spin
    while get_time() - t < 8 and not StateofBumper.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()

    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    print("Half circle maneuver konec")
    time.sleep(1)

def go_around_the_ball(turtle,rate,x_odo,y_odo):
    print("go_around_the_ball start")   

    min_dist = 0.4
    tolerance = 0.1
    left_origin = False

    lin_speed = linear_around_the_ball      
    ang_speed = angular_around_the_ball
    
    while not StateofBumper.is_set():
        odometry = turtle.get_odometry() 
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()

        x, y = odometry[0], odometry[1]
        x = x - x_odo
        y = y - y_odo
        dist = np.sqrt(x**2 + y**2)
        # print(odometry,dist,left_origin)

        if not left_origin and dist > min_dist:
            left_origin = True
            print("Left origin zone")

        if left_origin and dist < tolerance:
            print("Returned to origin with tolerance ", tolerance)
            break
        set_process_img()
    
    odometry_stage.set()
    print("go_around_the_ball konec")  
    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    time.sleep(1) 

def return_to_axis(turtle,rate, odometry):
    y = odometry[1]

    if y > 0: ang = -np.pi/2
    else: ang = np.pi/2
    lin_speed = linear_0
    ang_speed = np.sign(ang) * angular_spinning

    x_curr,y_curr,a_curr = turtle.get_odometry()
    while not StateofBumper.is_set() and abs(a_curr - ang) > 0.08:
        x_curr,y_curr,a_curr = turtle.get_odometry()
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        print("ang",x_curr,y_curr,a_curr)

        set_process_img()

    turtle.cmd_velocity(linear_0, angular = angular_0)
    time.sleep(0.5)
    print("mid",x_curr,y_curr,a_curr)
    lin_speed = linear_the_rest
    ang_speed = angular_0
    while not StateofBumper.is_set() and (-0.05 > y_curr or y_curr > 0.05) :
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)

        x_curr,y_curr,a_curr = turtle.get_odometry()
        rate.sleep()
        set_process_img()
        print("y",x_curr,y_curr,a_curr)
    print("returned to axis")
    print(x_curr,y_curr,a_curr)

# Stage 5 ------------------------------------
def stage5(turtle,rate):
    print("Stage 5 start")

    looking_for_garage_spin(turtle,rate)
    get_close_to_garage(turtle,rate)

    print("Stage 5 konec")

def looking_for_garage_spin(turtle,rate):
    print("looking_for_garage_spin start")

    lin_speed = linear_0
    ang_speed = -(angular_spinning + 0.6)
    while not StateofBumper.is_set() and not see_garage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()   
        set_process_img()

    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    print("looking_for_garage_spin konec")
    time.sleep(1)

def get_close_to_garage(turtle,rate):
    print("get_close_to_garage start")
    
    ang_speed = angular_0
    lin_speed = linear_the_rest +0.12
    while not StateofBumper.is_set() and not ending_stage.is_set():
        ang_speed = P_reg_gar() 
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()   
        set_process_img()

    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    print("get_close_to_garage konec")
    time.sleep(1)

# Stage 6 ------------------------------------
def stage6(turtle,rate):
    print("Stage 6 start")

    park = ParkController(stop_dist = stop_distance, sound = True)
    while not StateofBumper.is_set():
        done = park.step(turtle)
        if done:
            print("Zaparkováno!")
            break
        rate.sleep()

    turtle.cmd_velocity(linear=linear_0, angular=angular_0)
    print("Stage 6 konec")
    time.sleep(1)
