"""
Module 3 — Part 1: ML Visualization
Monocular depth estimation on a heritage-site frame using MiDaS (small variant),
rendered as a colour-mapped depth heatmap.

Model: MiDaS v2.1 small (isl-org/MiDaS), loaded from local weights
       (midas_v21_small.pt, downloaded from the official GitHub release).
Input: source_frame.jpg
Output: outputs/ml_depth_heatmap.png, outputs/depth_raw.npy
"""
import os
import sys
import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "midas_repo"))
from midas.midas_net_custom import MidasNet_small  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")
os.makedirs(OUT, exist_ok=True)

device = torch.device("cpu")

# --- Load MiDaS small model from local weights ---
model = MidasNet_small(
    os.path.join(HERE, "midas_v21_small.pt"),
    features=64,
    backbone="efficientnet_lite3",
    exportable=True,
    non_negative=True,
    blocks={"expand": True},
)
model.to(device).eval()

# --- Preprocess input frame ---
img_path = os.path.join(HERE, "source_frame.jpg")
img_bgr = cv2.imread(img_path)
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

net_size = 256
resized = cv2.resize(img_rgb, (net_size, net_size), interpolation=cv2.INTER_CUBIC)
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
normed = (resized - mean) / std
input_tensor = torch.from_numpy(normed.transpose(2, 0, 1)).unsqueeze(0).float().to(device)

# --- Inference ---
with torch.no_grad():
    prediction = model(input_tensor)
    prediction = torch.nn.functional.interpolate(
        prediction.unsqueeze(1),
        size=img_bgr.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze()

depth = prediction.cpu().numpy()
depth_norm = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)

np.save(os.path.join(OUT, "depth_raw.npy"), depth)

# --- Visualization: side-by-side source + depth heatmap ---
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
axes[0].imshow(img_rgb)
axes[0].set_title("Source frame")
axes[0].axis("off")

im = axes[1].imshow(depth_norm, cmap="inferno")
axes[1].set_title("MiDaS monocular depth estimate")
axes[1].axis("off")
fig.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04, label="relative depth (near \u2192 far)")

fig.suptitle("ML Visualization: Monocular Depth Estimation (MiDaS v2.1 small)", fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "ml_depth_heatmap.png"), dpi=150)
print("Saved:", os.path.join(OUT, "ml_depth_heatmap.png"))
print("Depth range:", depth.min(), depth.max())
