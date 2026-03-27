#!/usr/bin/env python3

import csv
import os
import yaml
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

BASE = os.path.expanduser("~/antioch_sim")
MAPS = os.path.join(BASE, "maps")
PATHS = os.path.join(BASE, "paths")
RESULTS = os.path.join(BASE, "results")

CASES = ["ideal", "mild", "strong"]
TITLES = {
    "ideal": "Ideal LiDAR",
    "mild": "Mildly Degraded LiDAR",
    "strong": "Strongly Degraded LiDAR",
}

def load_map(case_name):
    yaml_path = os.path.join(MAPS, f"{case_name}.yaml")
    with open(yaml_path, "r") as f:
        meta = yaml.safe_load(f)

    image_path = meta["image"]
    if not os.path.isabs(image_path):
        image_path = os.path.join(MAPS, os.path.basename(image_path))

    arr = np.array(Image.open(image_path))
    return arr, meta

def load_path(case_name):
    csv_path = os.path.join(PATHS, f"{case_name}_path.csv")
    xs, ys = [], []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            xs.append(float(row["x"]))
            ys.append(float(row["y"]))
    return np.array(xs), np.array(ys)

def world_to_pixel(xs, ys, meta, img_shape):
    resolution = float(meta["resolution"])
    origin_x = float(meta["origin"][0])
    origin_y = float(meta["origin"][1])

    height, width = img_shape[:2]

    px = (xs - origin_x) / resolution
    py = height - ((ys - origin_y) / resolution)
    return px, py

def save_overlay_comparison():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for ax, case in zip(axes, CASES):
        img, meta = load_map(case)
        xs, ys = load_path(case)
        px, py = world_to_pixel(xs, ys, meta, img.shape)

        ax.imshow(img, cmap="gray", origin="upper")
        ax.plot(px, py, linewidth=2, label="Trajectory")
        ax.scatter(px[0], py[0], s=60, marker="o", label="Start")
        ax.scatter(px[-1], py[-1], s=60, marker="x", label="End")

        ax.set_title(TITLES[case])
        ax.axis("off")
        ax.legend()

    plt.tight_layout()
    out = os.path.join(RESULTS, "map_trajectory_overlay.png")
    plt.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved {out}")

if __name__ == "__main__":
    os.makedirs(RESULTS, exist_ok=True)
    save_overlay_comparison()
