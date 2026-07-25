"""
Module 3 — Part 3: Capture-to-3D
First pass at turning a single captured frame into a 3D view: takes the
MiDaS depth map from Part 1, unprojects every pixel into camera space using
a pinhole camera model, colours each 3D point with its source pixel colour,
and renders the resulting point cloud from three angles (front, 3/4, top)
so the shape reads as 3D rather than as a flat depth image.

This is the "single-frame depth-to-point-cloud" baseline. The PMW pipeline
notes (see /areas/pmw-internship.md) track the fuller multi-view path
(COLMAP/SfM -> MVS -> NeRF / 3D Gaussian Splatting) as the next step once
multiple calibrated angles of a real capture are available.

Input: source_frame.jpg, outputs/depth_raw.npy (from Part 1)
Output: outputs/capture_to_3d_views.png, outputs/point_cloud.ply
"""
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")

img = cv2.imread(os.path.join(HERE, "source_frame.jpg"))
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
H, W = img_rgb.shape[:2]

depth = np.load(os.path.join(OUT, "depth_raw.npy"))
# MiDaS outputs inverse depth (higher = closer). Convert to a pseudo-metric
# depth so the gate reads as nearer than the sky/back wall.
inv = depth - depth.min() + 1.0
pseudo_depth = 1.0 / inv
pseudo_depth = (pseudo_depth - pseudo_depth.min()) / (pseudo_depth.max() - pseudo_depth.min())
pseudo_depth = 1.0 + pseudo_depth * 4.0  # scene depth roughly in [1, 5] "units"

# Simple pinhole intrinsics (assumed fov, no calibration available for a
# synthetic proxy frame -- swap in real calibrated intrinsics for a live capture)
fov_deg = 60.0
fx = fy = (W / 2) / np.tan(np.radians(fov_deg / 2))
cx, cy = W / 2, H / 2

# Subsample for a manageable point count
step = 4
ys, xs = np.mgrid[0:H:step, 0:W:step]
zs = pseudo_depth[ys, xs]
X = (xs - cx) * zs / fx
Y = -(ys - cy) * zs / fy  # flip so up is up
Z = zs
colors = img_rgb[ys, xs].reshape(-1, 3) / 255.0

pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)

# --- Write a .ply point cloud (openable in MeshLab / CloudCompare / Colab open3d) ---
ply_path = os.path.join(OUT, "point_cloud.ply")
with open(ply_path, "w") as f:
    f.write("ply\nformat ascii 1.0\n")
    f.write(f"element vertex {len(pts)}\n")
    f.write("property float x\nproperty float y\nproperty float z\n")
    f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
    f.write("end_header\n")
    rgb255 = (colors * 255).astype(np.uint8)
    for p, c in zip(pts, rgb255):
        f.write(f"{p[0]:.4f} {p[1]:.4f} {p[2]:.4f} {c[0]} {c[1]} {c[2]}\n")

# --- Render three angles so the point cloud reads as 3D in a static screenshot ---
fig = plt.figure(figsize=(15, 5.5))
views = [
    ("Front view", 0, -90),
    ("3/4 view", -20, -60),
    ("Top-down view", 85, -90),
]
for i, (title, elev, azim) in enumerate(views, start=1):
    ax = fig.add_subplot(1, 3, i, projection="3d")
    ax.scatter(pts[:, 0], pts[:, 2], pts[:, 1], c=colors, s=1.5, depthshade=False)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Z (depth)")
    ax.set_zlabel("Y")
    ax.set_box_aspect([1, 1, 0.6])

fig.suptitle("Capture-to-3D: single-frame depth unprojected to a coloured point cloud", fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "capture_to_3d_views.png"), dpi=150)

print("Saved:", os.path.join(OUT, "capture_to_3d_views.png"))
print("Saved:", ply_path, "-", len(pts), "points")
