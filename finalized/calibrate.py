import cv2 as cv
import numpy as np

import time
from robolab_turtlebot import Turtlebot
# Returns average color on mask -----------------
def average_color_on_mask(image, mask):

    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    m = mask > 0

    H = hsv[:,:,0][m]
    S = hsv[:,:,1][m]
    V = hsv[:,:,2][m]

    if len(H) == 0:
        print("Average color on mask: blank mask")
        return None  

    H_avg = int(np.mean(H))
    S_avg = int(np.mean(S))
    V_avg = int(np.mean(V))

    return (H_avg, S_avg, V_avg)

# Creates mask where pixels are green ---------------
def HSV_green_mask(img):

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    H, S, V = cv.split(hsv)

    # Hue 35–85 = most of green shades ----------------
    mask = (H > 35) & (H < 85) & (S > 40) & (V > 40)
    mask = mask.astype(np.uint8) * 255

    return mask

# Finds green circle on mask ------------------------
def find_green_ball(image, circularity_min = 0.5):

    mask = HSV_green_mask(image)
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    best_circle = None
    best_score = 0

    for c in contours:
        area = cv.contourArea(c)
        if area < 500 or area > 500000:
            continue

        perimeter = cv.arcLength(c, True)
        if perimeter == 0:
            continue

        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity < circularity_min:
            continue

        (x, y), r = cv.minEnclosingCircle(c)

        score = area * circularity
        if score > best_score:
            best_score = score
            best_circle = (int(x), int(y), int(r))

    if best_circle:
        x, y, r = best_circle
        return best_circle
    
    return None

# returns average color of ball --------------------
def get_green_ball_average_color_bgr(img):                           

    mask = HSV_green_mask(img)   
    circle = find_green_ball(img)                   

    if circle is None:
        print("Míček nenalezen")
        return None
    
    avg_hsv = average_color_on_mask(img, mask)      
    
    avg_hsv_img = np.uint8([[[avg_hsv[0], avg_hsv[1], avg_hsv[2]]]])
    avg_bgr = cv.cvtColor(avg_hsv_img, cv.COLOR_HSV2BGR)[0,0]
    print(avg_bgr)  
    return tuple(int(x) for x in avg_bgr)

if __name__ == '__main__':
    turtle = Turtlebot(rgb=True, pc=True)
    time.sleep(1)
    rgb = turtle.get_rgb_image()
    print(get_green_ball_average_color_bgr(rgb))


