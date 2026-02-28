import cv2
import numpy as np

# ---------------------------------------------------------
# 1) Načtení obrázku
# ---------------------------------------------------------
img = cv2.imread("image.png")
img_f = img.astype(np.float32)

# ---------------------------------------------------------
# 2) TVOJE REFERENČNÍ BARVA (v BGR!)
# ---------------------------------------------------------
ref_bgr = np.array([100, 128, 63], dtype=np.float32)   # <-- sem dáš svou barvu

# ---------------------------------------------------------
# 3) Převod referenční barvy do HSV
# ---------------------------------------------------------
ref_patch = np.uint8([[ref_bgr]])          # 1×1 pixel
ref_hsv = cv2.cvtColor(ref_patch, cv2.COLOR_BGR2HSV)[0,0]

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
norm_rgb_vis = (norm_rgb * 255).clip(0,255).astype(np.uint8)

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

# ---------------------------------------------------------
# 8) Segmentace v HSV
# ---------------------------------------------------------
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
H, S, V = cv2.split(hsv)
print("ref HSV:", ref_hsv)

# prahy (můžeš si doladit)
tH = 40
tS = 120
tV = 100

mask_hsv = (
    (np.abs(H - ref_hsv[0]) < tH) &
    (S > tS) &
    (V > tV)
).astype(np.uint8) * 255
print("min intensity:", intensity.min(), "max:", intensity.max())
print("min dist:", dist.min(), "max:", dist.max())

# ---------------------------------------------------------
# 9) Uložení výsledků
# ---------------------------------------------------------
# ---------------------------------------------------------
# DETEKCE STŘEDU A POLOMĚRU KOLEČKA
# ---------------------------------------------------------

# vyber masku, kterou chceš použít
mask = mask_rgb   # nebo mask_hsv

# najdeme kontury
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if len(contours) == 0:
    print("Nenašla se žádná kontura.")
else:
    # vezmeme největší konturu (koule)
    cnt = max(contours, key=cv2.contourArea)

    # najdeme nejmenší kruh, který ji obalí
    (x, y), r = cv2.minEnclosingCircle(cnt)

    # převod na int
    x, y, r = int(x), int(y), int(r)

    # výpis
    print("Střed koule:", (x, y))
    print("Poloměr koule:", r)