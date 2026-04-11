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
    THRESHOLD = 40
    if (not exited_garage.is_set()) and ratio is not None and  ratio < 0.15:
        exited_garage.set()

    if (not garage_stage.is_set()) and radius is not None and pos is not None and 150 > radius > 5  and IMG_CENTER_X + THRESHOLD > pos[0] > IMG_CENTER_X - THRESHOLD:
        garage_stage.set()
        print("SEE BALL")

    if (not outgarage_stage.is_set()) and radius is not None and pos is not None and IMG_CENTER_X + 100 > pos[0] > IMG_CENTER_X - 100 and 60 > radius > 55:
        outgarage_stage.set()
        print("BALL CLOSE")
    if (not see_garage.is_set()) and avg_x is not None and IMG_CENTER_X + THRESHOLD > avg_x > IMG_CENTER_X - THRESHOLD:
        see_garage.set()
        print("SEE GARAGE")
    if (not ending_stage.is_set()) and see_garage.is_set() and avg_x is None:
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
    avg_x = find_garage_center(rgb, ref, turtle)
    with vision_lock:
        vision_data["avg_x"] = avg_x
        # vision_data["dist"] = dist
    return avg_x

# def garage_wall_percentage(pc, dist = 0.7):
#     if pc is None8
#         return None
#     ratio = 1
#     h = pc.shape[0]
#     bottom = pc[h//2:, :, :]
#     z = bottom[:, :, 2]
#     print(f'wall%: {z}')
#     if z is not None:
#         ratio = np.mean(z < dist)
#     return ratio

# # to see if we are in garage
def garage_wall_percentage(pc, dist=0.3):
    if pc is None:
        return None

    h = pc.shape[0]
    bottom = pc[h//2:, :, :]
    z = bottom[:, :, 2]
    
    # Filter out invalid depth values (NaN, inf, and non-positive)
    valid_mask = np.isfinite(z) & (z >= 0)
    # print(f"NaN: {np.isnan(z).sum()}, Inf: {np.isinf(z).sum()}, Zero: {(z == 0).sum()}, Valid: {valid_mask.sum()}")
    if not np.any(valid_mask):
        return None  # No valid depth data at all

    valid_z = z[valid_mask]
    ratio = np.mean(valid_z < dist)
    print(ratio)
    return ratio

# Image processing util -------------------------------
def set_process_img():
    if processing_image.is_set():
        processing_image.clear()
        processing_image.wait()

# P regulators - all return angular speed ------------

def P_reg_ball_spinning(stable):
    radius = pos = None
    with vision_lock:
        if vision_data["pos"] is not None:
            pos = vision_data["pos"][0]
            radius = vision_data["radius"]
    speed = stable*2

    HYSTERESIS = 30
    if radius is not None and pos is not None and pos > IMG_CENTER_X+HYSTERESIS:
        speed = stable/2
    elif radius is not None and pos is not None and pos < IMG_CENTER_X-HYSTERESIS:
        speed = -stable/2
    elif radius is not None and pos is not None and pos >= IMG_CENTER_X-HYSTERESIS and pos <= IMG_CENTER_X+HYSTERESIS:
        speed = None
    print(f'speed: {speed}')
    return speed

def P_reg_garage_spinning(stable):
    HYSTERESIS = 25
    avg_x = None
    with vision_lock:
        if vision_data["avg_x"] is not None:
            avg_x = vision_data["avg_x"]
    speed = stable*2
    if avg_x is not None and avg_x > IMG_CENTER_X+HYSTERESIS:
        speed = -stable/2
    elif avg_x is not None and avg_x < IMG_CENTER_X+HYSTERESIS:
        speed = stable/2
    elif avg_x is not None and avg_x >= IMG_CENTER_X-HYSTERESIS and avg_x <= IMG_CENTER_X+HYSTERESIS:
        speed = None
    return speed


def P_reg_ball():
    radius = pos = None
    with vision_lock:
        if vision_data["pos"] is not None:
            pos = vision_data["pos"][0]
            radius = vision_data["radius"]
    if radius is not None and pos is not None and IMG_CENTER_X + 110 > pos > IMG_CENTER_X - 110 and radius < 55:
        error_x = pos - IMG_CENTER_X
    else: error_x = 0
    print(f'errorP: {error_x}')
    return ((-error_x / IMG_CENTER_X) * 1.05)  

def P_reg_gar():
    with vision_lock:
        if vision_data["avg_x"] is not None:
            avg_x = vision_data["avg_x"]
            error_x = avg_x - IMG_CENTER_X
        else: 
            return 0
    print(f'errorP: {error_x}')
    return ((-error_x / IMG_CENTER_X) * 1.) 
