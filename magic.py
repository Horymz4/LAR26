from os import path

import cv2
import numpy as np

def image_segmentation(path, ref_bgr):
    # ---------------------------------------------------------
    # 1) Načtení obrázku
    # ---------------------------------------------------------
    # img = cv2.imread(path)
    # img_f = img.astype(np.float32)

    img_f = path

    # ---------------------------------------------------------
    # 2) TVOJE REFERENČNÍ BARVA (v BGR!)
    # ---------------------------------------------------------
    ref_bgr = np.array(ref_bgr, dtype=np.float32)   # <-- sem dáš svou barvu

    # ---------------------------------------------------------
    # 4) Výpočet intenzity I = ||BGR||
    # ---------------------------------------------------------
    intensity = np.linalg.norm(img_f, axis=2)
    intensity_safe = intensity.copy()
    intensity_safe[intensity_safe == 0] = 1.0

    # ---------------------------------------------------------
    # 5) Normalizovaný RGB
    # ---------------------------------------------------------
    norm_rgb = img_f / intensity_safe[..., None]

    # ---------------------------------------------------------
    # 6) Normalizovaná referenční barva
    # ---------------------------------------------------------
    ref_int = np.linalg.norm(ref_bgr)
    ref_norm = ref_bgr / ref_int

    # ---------------------------------------------------------
    # 7) Segmentace podle normalizovaného RGB
    # ---------------------------------------------------------
    t1 = 40     # práh intenzity
    t2 = 0.14    # práh vzdálenosti v norm. RGB

    dist = np.linalg.norm(norm_rgb - ref_norm, axis=2)
    mask_rgb = ((intensity > t1) & (dist < t2)).astype(np.uint8) * 255

    return mask_rgb

def get_ball_position_and_radius(image_path, ref_bgr):

    # získáme segmentační masku
    mask = image_segmentation(image_path, ref_bgr)

    # najdeme kontury
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("Nenašla se žádná kontura.")
        return None, None
    else:
        # vezmeme největší konturu (koule)
        cnt = max(contours, key=cv2.contourArea)

        # najdeme nejmenší kruh, který ji obalí
        (x, y), r = cv2.minEnclosingCircle(cnt)

        # převod na int
        x, y, r = int(x), int(y), int(r)

        return (x, y), r

def detect_two_largest_rectangles(image_path, ref_bgr, min_area=100):
    
    mask = image_segmentation(image_path, ref_bgr)

    # najdeme všechny kontury
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # filtrujeme malé kontury
    contours = [c for c in contours if cv2.contourArea(c) >= min_area]

    if len(contours) == 0:
        print("Nenašel se žádný obdélník.")
        return []

    # seřadíme podle plochy (od největší)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # vezmeme max 2 největší
    contours = contours[:2]

    rectangles = []

    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        (cx, cy), (w, h), angle = rect

        cx, cy = int(cx), int(cy)
        w, h = int(w), int(h)

        # rohy obdélníku
        box = cv2.boxPoints(rect)
        box = box.astype(int)

        rectangles.append((cx, cy, w, h, angle))

    return rectangles



ball_pos, ball_radius = get_ball_position_and_radius("image.png", [100, 86, 134])
rectangles = detect_two_largest_rectangles("imageBrana.png", [100, 86, 134])
