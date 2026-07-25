"""
Module 3 — Part 2: AR Line Overlays
Detects the dominant structural edges of a heritage-site frame (gate arch,
wall courses, bastion outlines) and renders them as a cyan AR-style overlay,
the way an AR heritage-annotation app would draw structural guide lines on
top of a live camera feed.

Pipeline: grayscale -> bilateral filter (denoise, keep edges) -> Canny ->
probabilistic Hough transform -> filtered by length -> drawn as overlay.

Input: source_frame.jpg
Output: outputs/ar_line_overlay.png
"""
import os
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")
os.makedirs(OUT, exist_ok=True)

img = cv2.imread(os.path.join(HERE, "source_frame.jpg"))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Keep structural edges, suppress texture noise
filtered = cv2.bilateralFilter(gray, d=7, sigmaColor=40, sigmaSpace=40)
edges = cv2.Canny(filtered, 30, 100)

# Probabilistic Hough transform -> straight line segments (walls, courses, arch chords)
lines = cv2.HoughLinesP(
    edges, rho=1, theta=np.pi / 180, threshold=28,
    minLineLength=22, maxLineGap=8,
)

overlay = img.copy()
ar_color = (255, 230, 0)  # cyan-ish, BGR, reads as an AR "guide line" against warm masonry

count = 0
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.hypot(x2 - x1, y2 - y1)
        if length < 35:
            continue
        cv2.line(overlay, (x1, y1), (x2, y2), ar_color, 2, cv2.LINE_AA)
        count += 1

# small "AR anchor" dots at line endpoints, like a marker-tracking overlay would show
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        for (x, y) in [(x1, y1), (x2, y2)]:
            cv2.circle(overlay, (x, y), 2, (0, 140, 255), -1, cv2.LINE_AA)

blended = cv2.addWeighted(overlay, 0.85, img, 0.15, 0)

label = f"AR structural lines detected: {count}"
cv2.putText(blended, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(blended, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 1, cv2.LINE_AA)

cv2.imwrite(os.path.join(OUT, "ar_line_overlay.png"), blended)
cv2.imwrite(os.path.join(OUT, "ar_edges_debug.png"), edges)
print("Lines detected:", count)
print("Saved:", os.path.join(OUT, "ar_line_overlay.png"))
