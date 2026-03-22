import cv2 as cv
import numpy as np

def average_color_on_mask(image, mask):
    # převod do HSV
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # maska musí být 0/255 → uděláme boolean
    m = mask > 0

    # vybereme jen pixely, kde maska = 1
    H = hsv[:,:,0][m]
    S = hsv[:,:,1][m]
    V = hsv[:,:,2][m]

    if len(H) == 0:
        return None  # nic tam není

    # zprůměrování
    H_avg = int(np.mean(H))
    S_avg = int(np.mean(S))
    V_avg = int(np.mean(V))

    return (H_avg, S_avg, V_avg)

def HSV_green_mask(image):

    if isinstance(image, str):
        img = cv.imread(image)
    else:
        img = image.copy()

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    H, S, V = cv.split(hsv)

    # ZELENÝ ROZSAH – volnější
    # Hue 35–85 je většina zelených odstínů
    mask = (H > 35) & (H < 85) & (S > 40) & (V > 40)

    mask = mask.astype(np.uint8) * 255

    cv.imshow("HSV Mask", mask)
    cv.waitKey(1)

    return mask

def find_green_ball(image):

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
        if circularity < 0.6:
            continue

        (x, y), r = cv.minEnclosingCircle(c)

        score = area * circularity
        if score > best_score:
            best_score = score
            best_circle = (int(x), int(y), int(r))

    if best_circle:
        x, y, r = best_circle
        out = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
        cv.circle(out, (x, y), r, (0, 255, 255), 3)
        cv.circle(out, (x, y), 5, (255, 0, 255), -1)
        cv.imshow("Detected Green Ball", out)
        cv.waitKey(0)
        return best_circle

    print("Kruh nenalezen")
    cv.waitKey(0)
    return None

def get_green_ball_average_color_bgr(image_path):
    # načteme obrázek JEDNOU
    if isinstance(image_path, str):
        img = cv.imread(image_path)
    else:
        img = image_path.astype(np.uint8)


    # 1) vytvoříme masku zeleného míčku
    mask = HSV_green_mask(img)

    # 2) najdeme míček
    circle = find_green_ball(img)

    if circle is None:
        print("Míček nenalezen")
        return None

    # 3) zprůměrujeme barvu na masce
    avg_hsv = average_color_on_mask(img, mask)

    if avg_hsv is None:
        print("Maska je prázdná")
        return None

    # 4) převedeme průměrnou barvu z HSV → BGR
    avg_hsv_img = np.uint8([[[avg_hsv[0], avg_hsv[1], avg_hsv[2]]]])
    avg_bgr = cv.cvtColor(avg_hsv_img, cv.COLOR_HSV2BGR)[0,0]
    print(avg_bgr)
    return tuple(int(x) for x in avg_bgr)

# color_bgr = get_green_ball_average_color_bgr("input.jpeg")
# print("Průměrná barva míčku (BGR):", color_bgr)
