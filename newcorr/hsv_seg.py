import cv2 as cv
import numpy as np

# Dinstence of hue ----------------------------------
def hue_distance(H, H_ref):
    H = H.astype(np.int16)
    diff = np.abs(H - int(H_ref))
    return np.minimum(diff, 180 - diff)

# Mask of same colored objects ----------------------
def HSV_mask(image, ref_color, ball):

    img = image.astype(np.uint8)
    if ball:
        img = img[100:, :]

    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    H, S, V = cv.split(img_hsv)
    hsv_ref = cv.cvtColor(np.uint8([[ref_color]]), cv.COLOR_BGR2HSV)
    H_ref = hsv_ref[0,0,0]

    # Color difference --------------------------------
    if ball:
        H_par = 20
        S_par = 40
        V_par = 40
    else:
        H_par = 20
        S_par = 40
        V_par = 40
    mask = (hue_distance(H, H_ref) < H_par) & (S > S_par) & (V > V_par)
    mask = mask.astype(np.uint8) * 255
    
    return mask

# Circles in mask -----------------------------------
def find_ball_in_mask(mask, MIN_DIAMETER, MAX_DIAMETER):
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

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

    if r < MIN_DIAMETER or r > MAX_DIAMETER:
        print("Diameter out of bounds: ", r)
        return None, None

    return (x, y), r

# Find ball ----------------------------------------
def find_ball(image, ref_colour, MIN_DIAMETER = 5, MAX_DIAMETER = 70):
    maska = HSV_mask(image, ref_colour, True) 
    return find_ball_in_mask(maska, MIN_DIAMETER, MAX_DIAMETER)

# Normalize size of rectangle ----------------------
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

# Two largest rectangles in mask -------------------
def find_two_largest_rectangles_in_mask(mask):
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    contours = [c for c in contours if cv.contourArea(c) >= 100]
    contours = sorted(contours, key=cv.contourArea, reverse=True)
    
    rectangles = []
    first_height = None

    for c in contours:
        if len(rectangles) == 2:
            continue

        rect = cv.minAreaRect(c)
        rect = normalize_rect(rect)

        (cx, cy), (w, h), angle = rect
        cx, cy, w, h = int(cx), int(cy), int(w), int(h)

        if h < 40:
            continue

        if first_height is not None:
            if not (0.85 * first_height <= h <= 1.15 * first_height):
                continue

        if(cv.contourArea(c) / (w*h) > 0.6):
            rectangles.append((cx, cy, w, h, angle))
            if first_height is None:
                first_height = h

    if len(rectangles) == 1:
        rectangles.append(None)

    if len(rectangles) == 0:
        return None

    return rectangles

# Find rectangles ----------------------------------
def find_rectangles(image, ref_colour):
    maska = HSV_mask(image, ref_colour, False) 
    return find_two_largest_rectangles_in_mask(maska)

# Distance of point on depth camera ----------------
def get_distance_at_pixel(turtle, x, y):
    pc = turtle.get_point_cloud()
    if pc is None:
        print("Point cloud není smuloch")
        return None

    h, w, _ = pc.shape

    if not (0 <= x < w and 0 <= y < h):
        print("Pixel je mimo obraz")
        return None
    
    z = pc[y, x, 2]

    if not np.isfinite(z):
        print("Sus hloubka v tomto pixelu")
        return None

    print("DistG = ", z)
    return float(z)

# Returns center of garage -------------------------
def find_garage_center(image, ref_colour, turtle):
    rects = find_rectangles(image, ref_colour)
    # No rectangle ------------------------------------
    if rects is None:                            
        print("Nevidím žádný obdélník")
        return None, None
    
    # One rectangle -----------------------------------
    if rects[1] is None:                           
        print("Vidím jeden obdélník")
        return None, None

    x1 = rects[0][0]
    x2 = rects[1][0]
    y = rects[0][1]
    # Center of garage in pixels ----------------------
    avg_x = (x1 + x2) // 2                       
    # dist = get_distance_at_pixel(turtle, avg_x, y)

    print("X = ", avg_x)

    return avg_x
