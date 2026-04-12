import threading
import time
import sys

from robolab_turtlebot import Turtlebot, Rate
from stages import stage1, stage2, stage3, stage4, stage5, stage6
from utils import bumper_cb, reasoning, ball_image, garage_image
from threading_variables import (
    StateofBumper, processing_image,
    odometry_stage, exited_garage,
    ending_stage,
)

from utils import garage_wall_percentage
from beep_beep import get_bottom_half_distance


# Bumper thread ---------------------------------------
def bumper(turtle):
    print("Start bumper vlákna")

    turtle.register_bumper_event_cb(bumper_cb)
    StateofBumper.wait()

    print("Konec bumper vlákna")


# Movement thread -------------------------------------
def pohyb(turtle):
    print("Start pohyboveho vlakna")
    rate = Rate(10)

    stage1(turtle, rate)  # find opening, exit
    stage2(turtle, rate)  # spin to find ball
    stage3(turtle, rate)  # drive to ball
    stage4(turtle, rate)  # circumnavigate
    stage5(turtle, rate)  # find + approach garage
    stage6(turtle, rate)  # park

    StateofBumper.set()
    print("Konec pohyboveho vlakna")


# Image thread ----------------------------------------
def obraz(turtle, ref_green, ref_purple):
    print("Start obrazového vlákna")
    time.sleep(1)

    pos = (0, 0)
    radius = avg_x = h = 0
    ratio = None

    while not StateofBumper.is_set():
        if not processing_image.is_set():

            # Stage 1 -- point cloud for distance
            if not exited_garage.is_set():
                pc = turtle.get_point_cloud()
                if pc is not None:
                    ratio = garage_wall_percentage(pc)

                processing_image.set()

            # Stage 2, 3, 4 -- rgb for ball
            elif not odometry_stage.is_set():

                turtle.wait_for_rgb_image()
                rgb = turtle.get_rgb_image()
                pos, radius = ball_image(rgb, ref_green)
                avg_x = None

                processing_image.set()

            # Stage 5 -- rgb for garage
            elif not ending_stage.is_set():
                turtle.wait_for_rgb_image()
                rgb = turtle.get_rgb_image()
                avg_x, h = garage_image(rgb, ref_purple, turtle)
                pos = radius = None
                processing_image.set()

            # Stage 6 -- point cloud for distace
            else:
                pc = turtle.get_point_cloud()
                get_bottom_half_distance(pc)
                processing_image.set()

            reasoning(pos, radius, avg_x, h, ratio)
    print("Konec obrazového vlákna")


# Main ------------------------------------------------
def main():
    # Turtle initalization ----------------------------
    turtle = Turtlebot(rgb=True, pc=True)
    time.sleep(1)

    # Calibration -------------------------------------
    if len(sys.argv) > 1 and sys.argv[1]:
        raw = sys.argv[1]
        ref_green = [int(x) for x in raw.strip("[]").split(",")]
    else:
        ref_green = [52, 108, 80]

    if len(sys.argv) > 2 and sys.argv[2]:
        raw = sys.argv[2]
        ref_purple = [int(x) for x in raw.strip("[]").split(",")]
    else:
        ref_purple = [111, 67, 83]

    # Threading ---------------------------------------
    print("Starting threads")

    t1 = threading.Thread(target=bumper, args=(turtle,))
    t2 = threading.Thread(target=obraz, args=(turtle, ref_green, ref_purple))
    t3 = threading.Thread(target=pohyb, args=(turtle,))

    thread_arr = [t1, t2, t3]
    for i in thread_arr:
        i.start()
    for i in thread_arr:
        i.join()

    print("All threads completed")


if __name__ == '__main__':
    main()
