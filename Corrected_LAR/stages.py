import time
import numpy as np
from threading_variables import garage_stage, StateofBumper, outgarage_stage, see_garage, ending_stage

from robolab_turtlebot import get_time
from utils import set_process_img,  P_reg_ball, P_reg_gar
from beep_beep import ParkController
from constants import linear_0, angular_0, stop_distance, angular_spinning, angular_around_the_ball, linear_around_the_ball, linear_the_rest, angular_quater_spin


# Stage 1 ------------------------------------
def stage1(turtle,rate):
    print("Stage 1 start")

    lin_speed = linear_0
    ang_speed = angular_spinning
    while not StateofBumper.is_set() and not garage_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        set_process_img()


    turtle.cmd_velocity(linear_0, angular = angular_0)
    print("Stage 1 konec")
    time.sleep(1)
    

# Stage 2 ------------------------------------
def stage2(turtle,rate):
    print("Stage 2 start")

    ang_speed = angular_0
    lin_speed = linear_the_rest
    while not StateofBumper.is_set() and not outgarage_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()
        ang_speed = P_reg_ball()
        set_process_img()

    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    time.sleep(1)
    print("Stage 2 konec")

# Stage 3 ------------------------------------
def stage3(turtle,rate):
    print("Stage 3 start")

    do_quater_spin(turtle,rate )
    go_around_the_ball(turtle,rate)

    print("Stage 3 konec")

def do_quater_spin(turtle,rate):
    print("Half circle maneuver start")
    
    turtle.reset_odometry()
    t = get_time()
    lin_speed = linear_0
    ang_speed = angular_quater_spin
    while get_time() - t < 8 and not StateofBumper.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()

    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    print("Half circle maneuver konec")
    time.sleep(1)

def go_around_the_ball(turtle,rate):
    print("go_around_the_ball start")   

    min_dist = 0.4
    tolerance = 0.2
    left_origin = False

    lin_speed = linear_around_the_ball      
    ang_speed = angular_around_the_ball
    
    while not StateofBumper.is_set():
        odometry = turtle.get_odometry() 
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()

        x, y = odometry[0], odometry[1]
        dist = np.sqrt(x**2 + y**2)
        print(odometry,dist,left_origin)

        if not left_origin and dist > min_dist:
            left_origin = True
            print("Left origin zone")

        if left_origin and dist < tolerance:
            print("Returned to origin with tolerance ", tolerance)
            break
        set_process_img()
        # TODO PROCESSING IMAGE SET ??

    print("go_around_the_ball konec")  
    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    time.sleep(1) 


# Stage 4 ------------------------------------
def stage4(turtle,rate):
    print("Stage 4 start")

    looking_for_garage_spin(turtle,rate)
    get_close_to_garage(turtle,rate)

    print("Stage 4 konec")

def looking_for_garage_spin(turtle,rate):
    print("looking_for_garage_spin start")

    lin_speed = linear_0
    ang_speed = angular_spinning
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
    lin_speed = linear_the_rest
    while not StateofBumper.is_set() and not ending_stage.is_set():
        turtle.cmd_velocity(linear = lin_speed, angular = ang_speed)
        rate.sleep()

        ang_speed = P_reg_gar() 
        set_process_img()

    turtle.cmd_velocity(linear = linear_0, angular = angular_0)
    print("get_close_to_garage konec")
    time.sleep(1)

# Stage 5 ------------------------------------
def stage5(turtle,rate):
    print("Stage 5 start")

    park = ParkController(stop_dist = stop_distance, sound = True)
    while not StateofBumper.is_set():
        done = park.step(turtle)
        if done:
            print("Zaparkováno!")
            break
        rate.sleep()

    turtle.cmd_velocity(linear=linear_0, angular=angular_0)
    print("Stage 5 konec")
    time.sleep(1)