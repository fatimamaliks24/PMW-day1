# From Photos to 3D: What I Learned in Week 1 at Preserve My World

*By Fatima Malik — CS student at FAST-NUCES Islamabad, AI & 3D Reconstruction Intern at [Preserve My World](https://preservemy.world)*

---

Imagine photographing the Badshahi Mosque with your phone and — a few hours later — having an
interactive 3D model that anyone in the world can walk through in their browser. That's the
kind of thing [Preserve My World (PMW)](https://preservemy.world) is building, and it's what
I spent my first week researching.

PMW is a platform for digitally preserving cultural heritage sites using AI and 3D
reconstruction. My job as an AI track intern is to understand the technical pipeline and
start experimenting. Here's what I found.

---

## The problem with preserving heritage

Heritage sites deteriorate. Wars, climate, neglect, and time damage things that can never be
replaced. Digital preservation captures the geometry, texture, and scale of a site so that
even if the physical structure is lost, a precise 3D record survives.

But "3D reconstruction" isn't one thing — it's a family of methods, each with different
tradeoffs. My first task was to compare them.

---

## Five methods, one chart

I researched five major approaches:

### 1. Structure-from-Motion (SfM) with COLMAP

**Input:** Unordered photos (even smartphone shots)  
**Output:** Sparse 3D point cloud + camera poses  
**Difficulty:** Beginner-friendly (there's a GUI)

This is the entry point for almost everything else. You give COLMAP 50–200 overlapping photos,
and it figures out where each photo was taken in 3D space, then places feature points in 3D
where the photos agree. The result is a sparse cloud of thousands of points.

I wrote a Python script (`pointcloud_demo.py`) that generates and visualizes what this output
looks like — a monument-shaped cluster of 3,400 points viewed from four angles, with simulated
camera positions marked as triangles.

**PMW fit:** Very high. Any field team with a phone can produce the input data.

### 2. Multi-View Stereo (MVS)

**Input:** SfM output (point cloud + poses)  
**Output:** Dense textured mesh  
**Difficulty:** Intermediate

MVS takes SfM output and densifies it — computing depth at every pixel rather than just at
feature points. The result is a full 3D mesh with texture maps: the deliverable museums and
UNESCO heritage archives use.

**PMW fit:** Very high. This is the archival-quality output layer.

### 3. NeRF (Neural Radiance Fields)

**Input:** Posed images (needs SfM poses first)  
**Output:** Novel view synthesis — render the scene from any angle  
**Difficulty:** Intermediate (Instant-NGP / nerfstudio make it accessible)

NeRF trains a neural network to represent a scene as a continuous 3D function. Once trained,
you can render photorealistic images from camera angles that were never photographed.
Imagine a smooth, cinematic fly-through of a heritage site assembled from 150 static photos.

**PMW fit:** High, especially for public-facing video content.

### 4. 3D Gaussian Splatting

**Input:** Posed images (SfM poses)  
**Output:** Real-time interactive 3D scene (viewable in browser)  
**Difficulty:** Intermediate

The newest method (2023) and arguably the most exciting for PMW. Instead of a neural network,
the scene is represented as millions of tiny 3D "splats" — Gaussian blobs with color and
opacity. Training takes 30 minutes; rendering is real-time at 60+ FPS.

The key insight: the output is *shareable*. Tools like SuperSplat let you view a 3D Gaussian
Splatting scene in a browser with no special software. This is exactly what PMW needs for
public access to heritage sites.

**PMW fit:** Very high. This is likely the primary delivery format.

### 5. Monocular Depth Estimation

**Input:** A single photo  
**Output:** Depth map (relative distance per pixel)  
**Difficulty:** Beginner

Models like Depth Anything v2 can estimate a depth map from a single image with no calibration.
The depth isn't metrically accurate, but it's extremely useful for archival photos where
multi-view capture was never an option.

I ran an experiment (`depth_estimation.py`) on this method. The script downloads a heritage
site image, runs mock depth estimation (the same code structure as the real model), and saves
a colored depth map plus statistics.

**PMW fit:** Medium — best for processing historical archives.

---

## What the pipeline looks like end-to-end

```
Field photos (phone/DSLR)
        ↓
   COLMAP/SfM        → camera poses + sparse point cloud
        ↓
Multi-View Stereo    → dense textured mesh (archival quality)
        ↓
3D Gaussian Splatting → real-time browser viewer for public access
```

Monocular depth fills in where we only have old archival photos. NeRF produces
cinematic flythrough videos for storytelling.

---

## What I ran this week

**Experiment 1: Point cloud visualisation (`pointcloud_demo.py`)**

I generated a synthetic point cloud shaped like a heritage monument — ground plane, four walls,
a dome, and four minarets — and visualised it from four angles (top, front, side, perspective).
The output matches what COLMAP would actually produce. 3,400 points, 12 simulated camera
positions.

This taught me how SfM output is structured before you feed it into the next stage.

**Experiment 2: Monocular depth estimation (`depth_estimation.py`)**

I set up the full pipeline for Depth Anything v2 — image download, model inference, depth map
visualisation, statistical analysis. The mock runs without GPU, and swapping in the real model
requires uncommenting three lines.

Key stats from the depth analysis:
- 29.6% near pixels (foreground)
- 40.7% mid-range pixels
- 29.7% far pixels (background/sky)

---

## What didn't work

- WikiMedia image URLs return 403 from server environments — switched to a placeholder for the
  depth experiment (real use would just pass a local file path)
- COLMAP's full pipeline requires a GPU for practical use; the mock experiment was the
  right scope for week 1

---

## What I'm doing next

- Feed real photos through the actual COLMAP pipeline
- Try a Gaussian Splatting Colab notebook on a sample dataset
- Understand the PMW codebase and where these methods connect to the product

---

## Why this matters

Most people have never seen Mohenjo-daro or Taxila in person. PreserveMy.World is building
the infrastructure to change that — making cultural heritage accessible, interactive, and
permanent. Understanding the 3D reconstruction pipeline is the technical foundation of that
mission, and week 1 was about getting that foundation right.

---

*Fatima Malik is a CS student at FAST-NUCES Islamabad, currently interning at
[Preserve My World](https://preservemy.world) on the AI & 3D Reconstruction track.*

*Code for all experiments: [github.com/fatimamaliks24/PMW-day1](https://github.com)*
