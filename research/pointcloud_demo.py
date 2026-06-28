"""
pointcloud_demo.py
------------------
Experiment: Simulate and visualise a sparse 3D point cloud
            (as produced by COLMAP Structure-from-Motion)
Author: Fatima Malik
Date: June 2026
Internship: Preserve My World (PMW)

What this does:
    Generates a synthetic sparse point cloud that mimics the kind of output
    COLMAP would produce from photos of a heritage site.  It then:
      1. Visualises the point cloud from multiple viewing angles
      2. Simulates camera positions (like COLMAP estimates)
      3. Saves a multi-panel figure as output

    In a real PMW workflow you would replace the synthetic points with
    the actual COLMAP .txt or .ply output — the visualisation code is
    identical.

How to run:
    pip install numpy matplotlib scipy
    python pointcloud_demo.py

Output:
    - outputs/pointcloud_view.png  : 4-panel 3D visualisation
    - logs/pointcloud_log.txt      : run log
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
LOG_FILE   = os.path.join(os.path.dirname(__file__), "logs", "pointcloud_log.txt")


def log(msg: str):
    print(msg)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# ── SYNTHETIC DATA ────────────────────────────────────────────────────────────

def generate_heritage_site_pointcloud(rng: np.random.Generator):
    """
    Produce a synthetic point cloud shaped roughly like a domed monument
    (think Badshahi Mosque or a similar heritage structure) — ground plane,
    walls, and a central dome.
    """
    points_list, colors_list = [], []

    # Ground plane
    n_ground = 800
    x = rng.uniform(-4, 4, n_ground)
    z = rng.uniform(-4, 4, n_ground)
    y = rng.normal(0, 0.05, n_ground)
    pts = np.column_stack([x, y, z])
    col = np.tile([0.55, 0.45, 0.35], (n_ground, 1))   # sandy ground
    points_list.append(pts); colors_list.append(col)

    # Four walls
    for xc, zc, axis in [(-3, 0, "x"), (3, 0, "x"), (0, -3, "z"), (0, 3, "z")]:
        n_wall = 300
        if axis == "x":
            wx = rng.normal(xc, 0.08, n_wall)
            wy = rng.uniform(0, 2.5, n_wall)
            wz = rng.uniform(-3, 3, n_wall)
        else:
            wx = rng.uniform(-3, 3, n_wall)
            wy = rng.uniform(0, 2.5, n_wall)
            wz = rng.normal(zc, 0.08, n_wall)
        points_list.append(np.column_stack([wx, wy, wz]))
        colors_list.append(np.tile([0.85, 0.82, 0.76], (n_wall, 1)))  # stone

    # Central dome
    n_dome = 600
    theta = rng.uniform(0, 2 * np.pi, n_dome)
    phi   = rng.uniform(0, np.pi / 2, n_dome)
    r     = rng.normal(1.4, 0.04, n_dome)
    dx = r * np.sin(phi) * np.cos(theta)
    dy = r * np.cos(phi) + 2.2
    dz = r * np.sin(phi) * np.sin(theta)
    points_list.append(np.column_stack([dx, dy, dz]))
    colors_list.append(np.tile([0.78, 0.75, 0.70], (n_dome, 1)))

    # Minarets (4 corners)
    for mx, mz in [(-2.8, -2.8), (2.8, -2.8), (-2.8, 2.8), (2.8, 2.8)]:
        n_min = 200
        mxa = rng.normal(mx, 0.1, n_min)
        mya = rng.uniform(0, 3.5, n_min)
        mza = rng.normal(mz, 0.1, n_min)
        points_list.append(np.column_stack([mxa, mya, mza]))
        colors_list.append(np.tile([0.80, 0.77, 0.72], (n_min, 1)))

    points = np.vstack(points_list)
    colors = np.clip(np.vstack(colors_list), 0, 1)
    return points, colors


def generate_camera_positions(n_cams: int = 12) -> np.ndarray:
    """Simulate camera positions arranged in a ring around the site."""
    angles = np.linspace(0, 2 * np.pi, n_cams, endpoint=False)
    r = 6.0
    cams = np.column_stack([
        r * np.cos(angles),
        np.full(n_cams, 1.5),
        r * np.sin(angles),
    ])
    return cams


# ── VISUALISATION ─────────────────────────────────────────────────────────────

def plot_pointcloud(points: np.ndarray, colors: np.ndarray, cameras: np.ndarray):
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0d1117")

    views = [
        ("Top view",       90, -90),
        ("Front view",      5, -90),
        ("Side view",       5,   0),
        ("Perspective",    25,  -60),
    ]

    for idx, (title, elev, azim) in enumerate(views, 1):
        ax = fig.add_subplot(2, 2, idx, projection="3d")
        ax.set_facecolor("#0d1117")

        ax.scatter(
            points[:, 0], points[:, 2], points[:, 1],
            c=colors, s=1.2, alpha=0.7, linewidths=0
        )
        ax.scatter(
            cameras[:, 0], cameras[:, 2], cameras[:, 1],
            c="#C18D52", s=40, marker="^", zorder=5,
            label="Camera positions"
        )

        ax.set_xlabel("X", color="#5A8F76", fontsize=8)
        ax.set_ylabel("Z", color="#5A8F76", fontsize=8)
        ax.set_zlabel("Y", color="#5A8F76", fontsize=8)
        ax.tick_params(colors="#748B91", labelsize=7)
        for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
            pane.fill = False
            pane.set_edgecolor("#203B37")

        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title, color="#EEE8B2", fontsize=11, pad=8)
        if idx == 1:
            ax.legend(fontsize=8, facecolor="#203B37", labelcolor="#EEE8B2",
                      loc="upper right")

    fig.suptitle(
        "Synthetic COLMAP-style Point Cloud — Heritage Monument\n"
        "Preserve My World (PMW) Internship Experiment · Fatima Malik · June 2026",
        color="#EEE8B2", fontsize=13, y=0.98
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "pointcloud_view.png")
    plt.savefig(out_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close()
    log(f"[save] Point cloud visualisation → {out_path}")
    return out_path


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log("PMW Experiment: Point Cloud Visualisation")
    log("Author: Fatima Malik | FAST-NUCES | June 2026")
    log("=" * 60)

    rng = np.random.default_rng(42)

    log("[generate] Building synthetic heritage site point cloud...")
    points, colors = generate_heritage_site_pointcloud(rng)
    log(f"[generate] Total points: {len(points):,}")
    log(f"[generate] Bounding box X: [{points[:,0].min():.2f}, {points[:,0].max():.2f}]")
    log(f"[generate] Bounding box Y: [{points[:,1].min():.2f}, {points[:,1].max():.2f}]")
    log(f"[generate] Bounding box Z: [{points[:,2].min():.2f}, {points[:,2].max():.2f}]")

    cameras = generate_camera_positions(12)
    log(f"[generate] Simulated {len(cameras)} camera positions")

    log("[visualise] Rendering 4-panel point cloud figure...")
    out_path = plot_pointcloud(points, colors, cameras)

    log("\n[analysis] What this represents:")
    log("  In a real PMW workflow, these points come from COLMAP's")
    log("  Structure-from-Motion pipeline fed 50-200 photos of a heritage site.")
    log("  The triangles (▲) show estimated camera positions — COLMAP works")
    log("  out where each photo was taken in 3D space.")
    log("  This sparse cloud feeds into Multi-View Stereo (dense reconstruction)")
    log("  and from there into Gaussian Splatting for real-time web viewing.")

    log("\n[done] Experiment complete.")
    log(f"       Output → {out_path}")


if __name__ == "__main__":
    main()
