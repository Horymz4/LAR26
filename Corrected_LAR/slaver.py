import threading

from robolab_turtlebot import Turtlebot, Rate
from stages import stage1, stage2, stage3, stage4, stage5
from utils import bumper_cb, reasoning, ball_image, garage_image
from threading_variables import StateofBumper, processing_image, outgarage_stage
from utils import calibrate


# Bumper thread ---------------------------------------
def bumper(turtle):
    print("Start bumper vlákna")

    turtle.register_bumper_event_cb(bumper_cb)
    StateofBumper.wait()
    
    print("Konec bumper vlákna")

# Movement thread -------------------------------------
def pohyb(turtle):
    print("Start pohybového vlákna")
    rate = Rate(10)

    stage1(turtle,rate) # garage ----------------------
    stage2(turtle,rate) # going to the ball -----------
    stage3(turtle,rate) # going round the ball --------
    stage4(turtle,rate) # garage ----------------------
    stage5(turtle,rate) # parking ---------------------
 
    print("Konec pohybového vlákna")

# Image thread ----------------------------------------
def obraz(turtle,ref_img):
    print("Start obrazového vlákna")

    pos = (0,0)
    radius = avg_x = dist = 0
    while not StateofBumper.is_set():
        if not processing_image.is_set():
            turtle.wait_for_rgb_image()
            rgb = turtle.get_rgb_image()
            # looking for ball ------------------------
            if not outgarage_stage.is_set():                         
                pos,radius = ball_image(rgb,ref_img)
            # looking for garage ----------------------
            else:                                                    
                avg_x, dist = garage_image(rgb, [165,90,121], turtle)

            processing_image.set()
            reasoning(pos,radius,avg_x,dist)

    print("Konec obrazového vlákna")


# Main ------------------------------------------------
def main():
    # Turtle initalization ----------------------------
    turtle = Turtlebot(rgb=True, depth=True, pc = True)

    # Calibration -------------------------------------
    #ref = calibrate(turtle)
    ref = [31, 70, 54]

    # Threading ---------------------------------------
    print("Starting threads")

    t1 = threading.Thread(target=bumper, args=(turtle,))
    t2 = threading.Thread(target=obraz, args=(turtle,ref))
    t3 = threading.Thread(target=pohyb, args=(turtle,))

    thread_arr = [t1,t2,t3]
    for i in thread_arr: i.start()
    for i in thread_arr: i.join()
        
    print("All threads completed")

if __name__ == '__main__':
    main()
