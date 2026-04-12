import time
import numpy as np
from threading_variables import (
        garage_stage, StateofBumper,
        odometry_stage, outgarage_stage,
        see_garage, ending_stage,
        exited_garage,
)
from robolab_turtlebot import get_time
from utils import (
        P_reg_garage_spinning, set_process_img,
        P_reg_ball, P_reg_gar,
        P_reg_ball_spinning,
)
from beep_beep import ParkController
from constants import (
        linear_0, angular_0,
        stop_distance, angular_spinning,
        angular_around_the_ball, linear_around_the_ball,
        linear_the_rest, angular_quater_spin
)

direction = 1
centered = False


def move_until(
        turtle, rate,
        lin_speed, ang_speed,
        condition_fn, text,
        time_sleep=0.1, ang_speed_reg=None,
        image_processing=True
        ):

    print(text + " start")
    speed = ang_speed
    while not StateofBumper.is_set() and condition_fn():
        if image_processing:
            set_process_img()
        if ang_speed_reg is not None:
            reg_speed = ang_speed_reg()
            if reg_speed is not None:
                speed = reg_speed
        turtle.cmd_velocity(linear=lin_speed, angular=speed)
        rate.sleep()

        if text == "Stage 2":
            print(ang_speed)
    turtle.cmd_velocity(linear=linear_0, angular=angular_0)
    print(text + " end")
    time.sleep(time_sleep)


# Stage 1 ------------------------------------
def stage1(turtle, rate):
    time.sleep(0.5)
    find_opening(turtle, rate)
    go_forward_a_little(turtle, rate, 5.5)

    turtle.reset_odometry()


def find_opening(turtle, rate):
    move_until(
        turtle, rate,
        linear_0, angular_spinning*0.5,
        lambda: not exited_garage.is_set(),
        "Find opening"
    )


# Stage 2 ------------------------------------
def stage2(turtle, rate):

    move_until(
        turtle, rate,
        linear_0, -angular_spinning,
        lambda: not garage_stage.is_set(),
        "Stage 2",
        ang_speed_reg=lambda: P_reg_ball_spinning(-angular_spinning)
    )


# Stage 3 ------------------------------------
def stage3(turtle, rate):

    move_until(
        turtle, rate,
        linear_the_rest, angular_0,
        condition_fn=lambda: not outgarage_stage.is_set(),
        text="Stage 3",
        time_sleep=0.5,
        ang_speed_reg=P_reg_ball
    )

    go_forward_a_little(turtle, rate, 3.5)


def cond_time(t, how_long):
    return get_time() - t < how_long


def go_forward_a_little(turtle, rate, how_long):

    t = get_time()
    move_until(
        turtle, rate,
        linear_the_rest, angular_0,
        lambda: cond_time(t, how_long),
        text="going a bit forward"
    )


# Stage 4 ------------------------------------
def stage4(turtle, rate):
    print("Stage 4 start")

    odometry = turtle.get_odometry()

    do_quater_spin(turtle, rate, odometry[1])
    go_around_the_ball(turtle, rate)

    odometry = turtle.get_odometry()
    print(f'odometry before axis {odometry}')
    return_to_axis(turtle, rate)

    print("Stage 4 konec")


def do_quater_spin(turtle, rate, y_odo):
    global direction, centered

    t = get_time()
    m = -1 if y_odo > 0 else 1
    direction = m

    if abs(y_odo) < 0.25:
        centered = True
    move_until(
        turtle, rate,
        linear_0, m*angular_quater_spin,
        lambda: cond_time(t, 9),
        text="Half corcle maneuver",
    )


def cond_angle(turtle, ang, tolerance, t):
    odometry = turtle.get_odometry()
    a_curr = odometry[2]
    return abs(a_curr - ang) > tolerance or cond_time(t, 8)


def go_around_the_ball(turtle, rate):

    tolerance = 0.08
    ang = direction * np.pi/2
    if centered:
        ang = -ang

        print("ball is too centered")
    t = get_time()

    move_until(
        turtle, rate,
        linear_around_the_ball, direction*angular_around_the_ball,
        lambda: cond_angle(turtle, ang, tolerance, t),
        text="go_around_the_ball",
        time_sleep=0.5
    )


def cond_y(turtle, backwards):
    x_curr, y_curr, a_curr = turtle.get_odometry()
    print("y", x_curr, y_curr, a_curr)
    a_curr = backwards * a_curr
    if a_curr < 0:
        return y_curr > 0
    else:
        return y_curr < 0


def return_to_axis(turtle, rate):

    x_curr, y_curr, a_curr = turtle.get_odometry()
    print("mid", x_curr, y_curr, a_curr)
    speed = 1
    if centered:
        speed = -1

    move_until(
        turtle, rate,
        speed * linear_the_rest, angular_0,
        lambda: cond_y(turtle, speed),
        text="return_to_axis"
    )

    print(x_curr, y_curr, a_curr)
    odometry_stage.set()


# Stage 5 ------------------------------------
def stage5(turtle, rate):
    print("Stage 5 start")

    x_curr, y_curr, a_curr = turtle.get_odometry()
    print(x_curr, y_curr, a_curr)
    if np.sqrt(x_curr**2 + y_curr**2) < 0.45:
        print("too close to starting point!!")
        turn_to_garage(turtle, rate)
        see_garage.set()
        ending_stage.set()

    else:
        looking_for_garage_spin(turtle, rate)
        get_close_to_garage(turtle, rate)

    print("Stage 5 konec")


def turn_to_garage(turtle, rate):
    m = 1 if centered else -1
    t = get_time()

    move_until(
        turtle, rate,
        linear_0, angular_spinning*m*direction,
        condition_fn=lambda: cond_angle(turtle, np.pi, 0.1, t),
        text="sping towards garage"
    )


def looking_for_garage_spin(turtle, rate):
    m = 1 if centered else -1

    move_until(
        turtle, rate,
        linear_0, (-0.1+angular_spinning)*m*direction,
        condition_fn=lambda: not see_garage.is_set(),
        text="looking_for_garage_spin",
        ang_speed_reg=lambda: P_reg_garage_spinning(
            (-0.1 + angular_spinning) * m * direction
            )
    )


def get_close_to_garage(turtle, rate):

    move_until(
        turtle, rate,
        linear_the_rest, angular_0,
        condition_fn=lambda: not ending_stage.is_set(),
        text="get_close_to_garage",
        ang_speed_reg=P_reg_gar,
    )


# Stage 6 ------------------------------------
def stage6(turtle, rate):
    print("Stage 6 start")

    park = ParkController(stop_dist=stop_distance, sound=True)
    while not StateofBumper.is_set():
        done = park.step(turtle)
        if done:
            print("Zaparkováno!")
            break
        rate.sleep()
        set_process_img()

    turtle.cmd_velocity(linear=linear_0, angular=angular_0)
    print("Stage 6 konec")
    time.sleep(1)
