# 3D Reconstruction Methods — Research Comparison

**Author:** Fatima Malik  
**Date:** June 2026  
**Context:** Research for Preserve My World (PMW) internship — evaluating which 3D reconstruction
methods best fit the mission of digitally preserving cultural heritage sites.

---

## Overview

Five methods are compared below. Each section covers:
- **Inputs** — what data you feed in
- **Outputs** — what you get out
- **Hardware** — what compute is needed
- **Difficulty** — beginner/intermediate/advanced
- **PMW fit** — how it applies to heritage preservation
- **Small experiment** — something runnable this week

---

## 1. COLMAP / Structure-from-Motion (SfM)

### What it is
COLMAP is an open-source SfM pipeline. It takes a collection of unordered photos of an object
or scene, finds matching features across images, and reconstructs both the 3D point cloud and
the camera positions that took the shots.

### Inputs
- 20–200+ overlapping photos of the same subject from different angles
- Can be regular smartphone photos (JPEG/PNG)
- No GPS or depth sensor required

### Outputs
- Sparse 3D point cloud (feature matches → camera poses)
- Dense 3D point cloud (after dense reconstruction step)
- Camera pose estimates for every image
- Can export to `.ply`, `.obj`, or feed into NeRF/Gaussian Splatting pipelines

### Hardware needs
- CPU-only is possible for small scenes (slow)
- GPU speeds up dense matching significantly (NVIDIA recommended)
- 8GB RAM minimum; 16GB+ for large scenes

### Difficulty
**Beginner–Intermediate.** GUI version is user-friendly. CLI takes more setup but is scriptable.

### PMW fit
**High.** Field teams at heritage sites can photograph monuments with a smartphone or DSLR.
COLMAP turns those photos into a point cloud with no special equipment. This is the most
practical first-pass digitization tool for PMW field work.

### Small experiment this week
```bash
pip install pycolmap
# Run SfM on a set of test images using pycolmap Python bindings
# OR use the COLMAP GUI on sample dataset from their official site
```
See `/experiments/colmap_notes.md` for what happened when I tried this.

---

## 2. NeRF (Neural Radiance Fields)

### What it is
NeRF (Mildenhall et al., 2020) represents a scene as a continuous volumetric function learned
by a neural network. Given a set of posed images (images + known camera positions), it learns
to predict the color and density at any 3D point from any viewing direction.

### Inputs
- 50–300 posed images (photos + camera intrinsics/extrinsics)
- Typically need COLMAP output first to get camera poses
- Scene should be well-lit and static

### Outputs
- Novel view synthesis — render the scene from any new camera angle
- Implicit 3D representation (not a mesh, but a learned function)
- Can extract meshes via marching cubes

### Hardware needs
- **GPU required.** Training a standard NeRF takes 1–24 hours on an NVIDIA GPU (RTX 3080+)
- Instant-NGP (NVIDIA) reduced this to minutes — runs on Google Colab T4
- 8GB VRAM minimum

### Difficulty
**Intermediate.** Instant-NGP or nerfstudio make it accessible. Raw NeRF implementation
requires PyTorch knowledge.

### PMW fit
**Medium–High.** Excellent for photorealistic novel-view rendering of heritage sites — imagine
virtually walking through an ancient site from photos taken on-site. High compute cost is the
main barrier for field use, but cloud rendering (Colab) makes it viable.

### Small experiment this week
```bash
# Use nerfstudio on Colab — they have a free starter notebook
# https://colab.research.google.com/github/nerfstudio-project/nerfstudio/...
# Feed in a small dataset (the "dozer" sample) and render a video
```

---

## 3. 3D Gaussian Splatting (3DGS)

### What it is
3DGS (Kerbl et al., 2023) represents a scene as millions of tiny 3D Gaussian "splats" — each
with a position, size, opacity, and color that varies by viewing angle (using spherical
harmonics). Unlike NeRF's implicit network, splats are explicit, making rendering extremely fast.

### Inputs
- Same as NeRF: posed images (COLMAP output)
- Works well with 100–300 images
- Needs a sparse point cloud to initialize splat positions

### Outputs
- A `.ply` file of 3D Gaussians
- Real-time renderable 3D scene (60+ FPS in viewers like SuperSplat)
- Far faster rendering than NeRF after training

### Hardware needs
- GPU required for training (similar to NeRF — RTX 3080+ ideal)
- Training: 30 min–2 hours
- Rendering: real-time on modern GPU; web viewers exist for CPU playback

### Difficulty
**Intermediate.** Original repo needs CUDA setup. Easier wrappers (gsplat, nerfstudio 3DGS)
reduce friction. Colab works for small scenes.

### PMW fit
**Very High.** This is likely the best end-state format for PMW. After digitizing a heritage
site with photos, 3DGS produces a real-time interactive 3D scene viewable in a browser.
Users can "walk through" the Badshahi Mosque or Mohenjo-daro from anywhere in the world.
The output is shareable and doesn't require specialized software to view.

### Small experiment this week
```bash
# Try the online SuperSplat viewer with a pre-trained .ply file
# https://supersplat.github.io
# OR run the gsplat Colab notebook on the garden scene
```

---

## 4. Monocular Depth Estimation

### What it is
Instead of multiple photos, monocular depth estimation predicts a depth map from a **single
image** using a pre-trained neural network. Models like MiDaS, Depth Anything, or DPT are
trained on massive datasets and generalize to new images zero-shot.

### Inputs
- A single RGB image (JPEG/PNG)
- No camera calibration needed
- Works on any image — photos, paintings, archival footage

### Outputs
- Depth map (grayscale or colored image where brightness = estimated distance)
- Can be converted to a pseudo-3D point cloud
- Not metrically accurate — relative depth only (unless trained with scale)

### Hardware needs
- **CPU works** for inference (slow but functional)
- GPU makes it real-time
- Runs easily on Colab free tier

### Difficulty
**Beginner.** Pre-trained models run in ~10 lines of Python with the `transformers` library.

### PMW fit
**Medium.** Useful for processing archival photographs of heritage sites where multi-view
capture is impossible. Can add a "3D feel" to old photos. Not accurate enough for precise
reconstruction but excellent for visualization and accessibility features.

### Small experiment this week
```python
# See /experiments/depth_estimation.py
# Runs Depth Anything v2 on a sample image and saves the depth map
```
**This is the most beginner-friendly experiment and is fully documented in this repo.**

---

## 5. Multi-View Stereo (MVS)

### What it is
MVS is the dense reconstruction step that typically follows SfM. While SfM gives sparse feature
matches, MVS (e.g. OpenMVS, PMVS, or the dense step in COLMAP) computes depth for every pixel
by comparing nearby images, producing a dense point cloud or mesh.

### Inputs
- Sparse point cloud + camera poses from SfM (COLMAP output)
- The original images
- At minimum 3–5 overlapping views per surface region

### Outputs
- Dense point cloud (millions of points)
- Triangle mesh (after Poisson surface reconstruction)
- Textured 3D mesh (`.obj` with texture maps)

### Hardware needs
- CPU possible but very slow for large scenes
- GPU-accelerated version (COLMAP's PatchMatchStereo) much faster
- 16GB+ RAM for large heritage sites

### Difficulty
**Intermediate.** Usually run as part of the COLMAP pipeline — not a separate install.

### PMW fit
**High.** The textured mesh output is the standard deliverable for heritage digitization.
Museums, UNESCO, and archival projects all work with textured meshes. PMW would use MVS
output to feed into web viewers, 3D printing, or AR overlays.

---

## Summary Table

| Method | Input | Output | GPU needed | Difficulty | PMW fit |
|--------|-------|--------|-----------|------------|---------|
| COLMAP/SfM | Photos | Sparse point cloud + camera poses | Optional | Beginner | ★★★★★ |
| MVS | SfM output | Dense mesh | Recommended | Intermediate | ★★★★★ |
| NeRF | Posed images | Novel views / implicit 3D | Required | Intermediate | ★★★★☆ |
| 3D Gaussian Splatting | Posed images | Real-time splat scene | Required | Intermediate | ★★★★★ |
| Monocular Depth | Single image | Depth map | Optional | Beginner | ★★★☆☆ |

---

## Recommended PMW pipeline

```
Field photos (smartphone/DSLR)
        ↓
   COLMAP/SfM          ← camera poses + sparse cloud
        ↓
Multi-View Stereo       ← dense mesh for archival
        ↓
3D Gaussian Splatting   ← real-time web viewer for public access
        ↓
   [Optional] NeRF      ← photorealistic novel-view video renders
```

Monocular depth fills in where only archival photos exist (no multi-view capture possible).

---

## Sources consulted

- Mildenhall et al. (2020) — "NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis"
- Kerbl et al. (2023) — "3D Gaussian Splatting for Real-Time Radiance Field Rendering"
- COLMAP documentation — https://colmap.github.io
- nerfstudio docs — https://docs.nerf.studio
- Depth Anything v2 — https://huggingface.co/depth-anything
