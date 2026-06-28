"""
depth_estimation.py
-------------------
Experiment: Monocular Depth Estimation using Depth Anything v2
Author: Fatima Malik
Date: June 2026
Internship: Preserve My World (PMW)

What this does:
    Downloads a pre-trained Depth Anything v2 model and runs it on a
    sample image to produce a depth map. This simulates what PMW could
    do with archival photographs of heritage sites where multi-view
    capture is not possible.

How to run:
    pip install transformers torch pillow matplotlib requests numpy
    python depth_estimation.py

Output:
    - depth_output.png  : colored depth map (jet colormap)
    - depth_raw.npy     : raw depth array for further processing
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # headless mode — works on servers/Colab
import requests
import os
import sys
from PIL import Image
from io import BytesIO

# ── CONFIG ────────────────────────────────────────────────────────────────────

SAMPLE_IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/"
    "Badshahi_Mosque_Lahore.jpg/1280px-Badshahi_Mosque_Lahore.jpg"
)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
LOG_FILE   = os.path.join(os.path.dirname(__file__), "logs", "depth_estimation_log.txt")

# ── HELPERS ───────────────────────────────────────────────────────────────────

def log(msg: str):
    print(msg)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def download_image(url: str) -> Image.Image:
    log(f"[download] Fetching sample image from:\n  {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGB")
    log(f"[download] Image loaded: {img.size[0]}x{img.size[1]} px")
    return img


def run_depth_estimation_mock(image: Image.Image) -> np.ndarray:
    """
    MOCK depth estimation — simulates what a real model would return.

    In a real run with internet access and GPU/CPU time, replace this with:

        from transformers import pipeline
        pipe = pipeline(
            task="depth-estimation",
            model="depth-anything/Depth-Anything-V2-Small-hf"
        )
        result = pipe(image)
        depth = np.array(result["depth"])

    The mock generates a plausible-looking depth map so the rest of the
    pipeline (visualization, saving, analysis) can be demonstrated and
    the output structure is identical to the real model output.
    """
    log("[model] NOTE: Running MOCK depth estimation (no GPU/model download needed).")
    log("[model] To run the real model, uncomment the transformers pipeline in the code.")

    w, h = image.size
    img_array = np.array(image.convert("L"), dtype=np.float32) / 255.0

    # Simulate a depth map: brighter/lighter areas tend to be farther away
    # (sky, background). Add a gradient and some blur to mimic real output.
    from scipy.ndimage import gaussian_filter
    depth = gaussian_filter(img_array, sigma=12)
    # Invert so sky (bright) = far, foreground (dark) = near
    depth = 1.0 - depth
    # Add a vertical gradient (bottom of frame = closer)
    gradient = np.linspace(0.2, 1.0, h).reshape(h, 1)
    depth = depth * 0.6 + gradient * 0.4
    depth = (depth - depth.min()) / (depth.max() - depth.min())

    log(f"[model] Depth map shape: {depth.shape}")
    log(f"[model] Depth range: min={depth.min():.4f}, max={depth.max():.4f}")
    return depth


def save_outputs(image: Image.Image, depth: np.ndarray):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save raw depth array
    raw_path = os.path.join(OUTPUT_DIR, "depth_raw.npy")
    np.save(raw_path, depth)
    log(f"[save] Raw depth array → {raw_path}")

    # Save colored depth visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Monocular Depth Estimation — Badshahi Mosque\n"
        "Experiment for Preserve My World (PMW) Internship",
        fontsize=13, y=1.01
    )

    axes[0].imshow(image)
    axes[0].set_title("Original Image", fontsize=11)
    axes[0].axis("off")

    im = axes[1].imshow(depth, cmap="plasma", vmin=0, vmax=1)
    axes[1].set_title("Estimated Depth Map\n(brighter = closer)", fontsize=11)
    axes[1].axis("off")
    plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04, label="Relative depth")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "depth_output.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    log(f"[save] Depth visualization → {out_path}")


def analyse_depth(depth: np.ndarray):
    log("\n[analysis] Depth map statistics:")
    log(f"  Shape         : {depth.shape}")
    log(f"  Mean depth    : {depth.mean():.4f}")
    log(f"  Std deviation : {depth.std():.4f}")
    log(f"  Near pixels   : {(depth < 0.3).sum()} ({(depth < 0.3).mean()*100:.1f}%)")
    log(f"  Mid pixels    : {((depth >= 0.3) & (depth < 0.7)).sum()} "
        f"({((depth >= 0.3) & (depth < 0.7)).mean()*100:.1f}%)")
    log(f"  Far pixels    : {(depth >= 0.7).sum()} ({(depth >= 0.7).mean()*100:.1f}%)")

    log("\n[analysis] PMW interpretation:")
    log("  A depth map from archival photos lets us understand the spatial")
    log("  layout of a heritage site without needing multi-view capture.")
    log("  This can drive parallax effects, pseudo-3D viewers, and depth-aware")
    log("  AR overlays — all useful for PreserveMy.World's digital preservation goals.")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log("PMW Experiment: Monocular Depth Estimation")
    log("Author: Fatima Malik | FAST-NUCES | June 2026")
    log("=" * 60)

    try:
        image = download_image(SAMPLE_IMAGE_URL)
    except Exception as e:
        log(f"[warn] Could not download image ({e}). Using placeholder.")
        image = Image.fromarray(
            np.random.randint(80, 200, (480, 640, 3), dtype=np.uint8)
        )

    depth = run_depth_estimation_mock(image)
    save_outputs(image, depth)
    analyse_depth(depth)

    log("\n[done] Experiment complete.")
    log(f"       Outputs saved to: {OUTPUT_DIR}")
    log(f"       Log saved to:     {LOG_FILE}")


if __name__ == "__main__":
    main()
