# Module: ML Visualizations, AR Lines, Capture-to-3D — Notes

## What this covers
Three small pipelines, each runnable standalone, that go from a single captured
frame to (1) an ML-generated depth visualization, (2) an AR-style structural
line overlay, and (3) a first capture-to-3D point-cloud view.

## Important caveat: proxy image
This sandbox has no network access to the real Rohtas Fort footage/photos sourced
in the previous module (only pypi/github/npm-class domains are reachable here).
So `source_frame.jpg` is a **synthetic stand-in** — a procedurally drawn fort
facade (gate arch, bastions, crenellations, masonry coursing) built to have the
same kind of structure (arches, straight wall lines, near/far depth layers) a
real gate photo would have. **Swap in an actual PMW capture frame and every
script below runs unchanged** — nothing is hardcoded to the synthetic image
beyond the filename.

## 1. ML Visualization — `01_ml_depth_visualization.py`
- **Model:** MiDaS v2.1 small (isl-org/MiDaS), CPU inference.
- **Weights:** downloaded directly from the official GitHub release
  (`midas_v21_small_256.pt`, ~82 MB) rather than via `torch.hub`, since
  `torch.hub`'s auto-fetch needed a manual trust confirmation and this was
  more reliable in a scripted/CI-style run.
- **What it does:** loads the frame, runs monocular depth inference, upsamples
  the depth map back to source resolution, and renders a side-by-side
  source/heatmap figure (`inferno` colormap).
- **Result:** `outputs/ml_depth_heatmap.png` — the gate reads as nearest,
  the wall as mid-depth, the sky as farthest, which matches the geometry
  built into the proxy frame. Raw depth array saved to `outputs/depth_raw.npy`
  and reused by Part 3.
- **Next step on real data:** this is the same model PMW's methods comparison
  doc already lists (Monocular Depth Estimation) — swapping in a real capture
  frame is a one-line change.

## 2. AR Line Overlay — `02_ar_line_overlay.py`
- **Approach:** classical CV, not learned — bilateral filter (denoise while
  preserving edges) → Canny edge detection → probabilistic Hough transform to
  pull out straight line segments → filtered by length → drawn as a cyan
  overlay with small anchor dots at segment endpoints, styled the way an AR
  annotation layer would draw over a live camera feed.
- **Tuning:** first pass (Canny 50/140, Hough threshold 45) only caught 7
  strong lines — the gate arch and wall corners. Loosened to Canny 30/100,
  Hough threshold 28, minLineLength 22 to also pick up the masonry coursing
  lines; landed on 27 detected segments, which is a much more legible overlay.
- **Result:** `outputs/ar_line_overlay.png` (final overlay) and
  `outputs/ar_edges_debug.png` (raw Canny edge map, kept for debugging).
- **Next step on real data:** for a live AR overlay this line set would need
  per-frame tracking (optical flow or a marker/SLAM anchor) so lines don't
  swim between frames — this script only handles the single-frame detection
  half of that problem.

## 3. Capture-to-3D — `03_capture_to_3d.py`
- **Approach:** reuses the MiDaS depth map from Part 1, converts MiDaS's
  inverse-depth output to a pseudo-metric depth, and unprojects every pixel
  into 3D camera space with a pinhole model (assumed 60° FOV — no real
  calibration available for the proxy frame). Each 3D point is coloured with
  its source pixel. Subsampled every 4th pixel to keep the point count
  manageable (~24.5k points).
- **Result:**
  - `outputs/capture_to_3d_views.png` — the same point cloud rendered from
    three angles (front, 3/4, top-down) so the shape reads as 3D in a static
    screenshot.
  - `outputs/point_cloud.ply` — ASCII PLY point cloud, opens directly in
    MeshLab, CloudCompare, Blender, or `open3d` in Colab.
- **This is deliberately the single-frame baseline, not the full pipeline.**
  PMW's methods comparison already scopes the fuller path — COLMAP/SfM for
  multi-view camera pose → MVS for a dense surface → NeRF or 3D Gaussian
  Splatting for the final renderable model. This script is the fastest
  possible "does a single capture frame produce a plausible 3D view at all"
  check before investing in the multi-view pipeline; it does not do
  multi-view fusion, so there's no real geometric accuracy guarantee — it's a
  depth-plausibility demo, not a measured reconstruction.

## How to run
```bash
pip install torch torchvision timm opencv-python numpy matplotlib
git clone --depth 1 https://github.com/isl-org/MiDaS.git midas_repo
curl -L -o midas_v21_small.pt \
  https://github.com/isl-org/MiDaS/releases/download/v2_1/midas_v21_small_256.pt
python3 01_ml_depth_visualization.py
python3 02_ar_line_overlay.py
python3 03_capture_to_3d.py
```
Same steps work unmodified in a Colab notebook cell-by-cell — Colab's GPU
runtime will just make Part 1 faster.

## Gaps / what's next
- Replace `source_frame.jpg` with a real PMW-captured frame (ideally one
  already used in the Rohtas Fort footage sourcing pass).
- Part 3 needs real camera intrinsics (or at least a measured FOV) once run
  on an actual capture, instead of the assumed 60°.
- Multi-view fusion (COLMAP/SfM → MVS) is the next milestone toward a proper
  reconstruction — this module only proves the single-frame depth-to-3D step
  works end-to-end.
