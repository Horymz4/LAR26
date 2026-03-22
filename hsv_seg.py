import cv2 as cv
import numpy as np

def hue_distance(H, H_ref):
    H = H.astype(np.int16)
    diff = np.abs(H - int(H_ref))
    return np.minimum(diff, 180 - diff)

def HSV_mask(image, ref_color):

    if isinstance(image, str):
        img = cv.imread(image)
    else:
        img = image.astype(np.uint8)

    img = img[100:, :]

    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    H, S, V = cv.split(img_hsv)
    hsv_ref = cv.cvtColor(np.uint8([[ref_color]]), cv.COLOR_BGR2HSV)

    H_ref = hsv_ref[0,0,0]
    S_ref = hsv_ref[0,0,1]
    V_ref = hsv_ref[0,0,2]

    H_par = 40 # barevnej rozdÃ­l
    S_par = 40
    V_par = 40

    mask = (hue_distance(H, H_ref) < H_par) & (S > S_par) & (V > V_par)
    mask = mask.astype(np.uint8) * 255
    # cv.imshow("V", V)
    # cv.imshow("H", H)
    #
    # cv.imshow("Mask", mask)
    cv.waitKey(1)

    return mask
    
def find_ball_in_mask(mask):
    contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    circle = None
    best_score = 0

    for c in contours:
        area = cv.contourArea(c) 
        if area < 50 or area > 20000:
            continue
        epsilon = 0.01 * cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, epsilon, True)
        perimeter = cv.arcLength(approx, True)
        area = cv.contourArea(approx)
        circularity = 4 * 3.141 * area / (perimeter * perimeter)
        if circularity < 0.7:
            continue

        score = area * circularity

        if score > best_score:
            best_score = score
            circle = approx 
    
    if circle is None:
        return None, None
    (x, y), r = cv.minEnclosingCircle(circle)

    return (x, y), r

def normalize_rect(rect):
    (cx, cy), (w, h), angle = rect

    if w > h:
        w, h = h, w
        angle += 90   

    if angle < -45:
        angle += 90
    elif angle > 45:
        angle -= 90

    return ((int(cx), int(cy)), (int(w), int(h)), angle)

def find_two_largest_rectangles_in_mask(mask):
    contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    contours = [c for c in contours if cv.contourArea(c) >= 100]
    contours = sorted(contours, key=cv.contourArea, reverse=True)
    rectangles = []

    for c in contours:
        if(len(rectangles) == 2):
            continue

        rect = cv.minAreaRect(c)
        rect = normalize_rect(rect)

        (cx, cy), (w, h), angle = rect

        cx, cy = int(cx), int(cy)
        w, h = int(w), int(h)

        box = cv.boxPoints(rect)
        box = box.astype(int)

        if(cv.contourArea(c) / (w*h) > 0.8):
            rectangles.append((cx, cy, w, h, angle))
    if len(rectangles) == 1:
        rectangles.append(None)

    if len(rectangles) == 0:
        return None

    return rectangles

def find_ball(image, ref_colour):
    maska = HSV_mask(image, ref_colour) 
    return find_ball_in_mask(maska)

def find_rectangles(image, ref_colour):
    maska = HSV_mask(image, ref_colour) 
    return find_two_largest_rectangles_in_mask(maska)
