from threading_variables import Button_press, StateofBumper, processing_image, exited_garage, garage_stage, outgarage_stage, see_garage, ending_stage, vision_data, vision_lock
from calibrate import get_green_ball_average_color_bgr
from hsv_seg import find_ball, find_garage_center
from constants import IMG_CENTER_X
import numpy as np
# Callbacks -------------------------------------------
def bumper_cb(msg):
    bumper_names = ['LEFT', 'CENTER', 'RIGHT']
    state_names = ['RELEASED', 'PRESSED']
    bumper = bumper_names[msg.bumper]
    state = state_names[msg.state]
    if msg.state == 1:
        StateofBumper.set()
    print(bumper," state ", state)

def button_cb(msg):
    button_states = ["pressed","not pressed"]
    state = button_states[msg.state]
    if msg.state == 1:
        Button_press.set()
    print(state)

# Calibration -----------------------------------------
def calibrate(turtle):
    print("Start kalibrace")

    turtle.register_button_event_cb(button_cb)
    Button_press.wait()
    Button_press.clear()

    turtle.wait_for_rgb_image()
    rgb = turtle.get_rgb_image()
    ref_image = get_green_ball_average_color_bgr(rgb)
    
    turtle.register_button_event_cb(button_cb)
    Button_press.wait()

    print("Konec kalibrace")
    return ref_image

# Image reasoning and image utils ---------------------
def reasoning(pos,radius,avg_x,dist, ratio):
    if (not exited_garage.is_set()) and ratio is not None and  ratio < 0.45:
        exited_garage.set()
    if (not garage_stage.is_set()) and radius is not None and pos is not None and 150 > radius > 5  and IMG_CENTER_X + 30 > pos[0] > IMG_CENTER_X - 30:
        garage_stage.set()
        print("SEE BALL")
    if (not outgarage_stage.is_set()) and radius is not None and pos is not None and IMG_CENTER_X + 100 > pos[0] > IMG_CENTER_X - 100 and 60 > radius > 55:
        outgarage_stage.set()
        print("BALL CLOSE")
    if (not see_garage.is_set()) and avg_x is not None and IMG_CENTER_X + 30 > avg_x > IMG_CENTER_X - 30:
        see_garage.set()
        print("SEE GARAGE")
    if (not ending_stage.is_set()) and dist is not None and see_garage.is_set() and dist < 1.1:
        ending_stage.set()
        print("PARKING")

def ball_image(rgb, ref_img):
    pos, radius = find_ball(rgb,ref_img)
    with vision_lock:
        vision_data["pos"] = pos
        vision_data["radius"] = radius
    if pos is not None: print("position: ", pos, " radius: ", radius)
    return pos,radius

def garage_image(rgb,ref,turtle):
    avg_x, dist = find_garage_center(rgb, ref, turtle)
    with vision_lock:
        vision_data["avg_x"] = avg_x
        vision_data["dist"] = dist
    return avg_x, dist

# to see if we are in garage
def garage_wall_percentage(pc, dist = 0.7):
    if pc is None:
        return None
    ratio = 1
    h = pc.shape[0]
    bottom = pc[h//2:, :, :]
    z = bottom[:, :, 2]
    if z is not None:
        ratio = np.mean(z < dist)
    
    return ratio

# Image processing util -------------------------------
def set_process_img():
    if processing_image.is_set():
        processing_image.clear()
        processing_image.wait()

# P regulators - both return angular speed ------------

def P_reg_ball():
    radius = pos = None
    with vision_lock:
        if vision_data["pos"] is not None:
            pos = vision_data["pos"][0]
            radius = vision_data["radius"]
    if radius is not None and pos is not None and IMG_CENTER_X + 30 > pos > IMG_CENTER_X - 30 and radius < 55:
        error_x = pos - IMG_CENTER_X
    else: error_x = 0
    print(f'errorP: {error_x}')
    return ((-error_x / IMG_CENTER_X) * 0.8) 

def P_reg_gar():
    with vision_lock:
        if vision_data["avg_x"] is not None:
            avg_x = vision_data["avg_x"]
            error_x = avg_x - IMG_CENTER_X
        else: 
            return 0
    print(f'errorP: {error_x}')
    return ((-error_x / IMG_CENTER_X) * 1.2) 
