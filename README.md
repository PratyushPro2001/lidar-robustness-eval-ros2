
# LiDAR Robustness Evaluation (ROS2)

A ROS2-based simulation framework for evaluating how LiDAR degradation affects SLAM and mapping performance.

## Overview

This project demonstrates how sensor degradation (noise and reduced range) impacts mapping accuracy even when the robot trajectory is fixed.

## Pipeline

/scan_clean → lidar_degrader → /scan_degraded → SLAM

## Features

- Gaussian noise injection into LiDAR scans
- Range limitation to simulate degraded sensors
- Comparative evaluation (ideal vs degraded)
- Visualization of mapping and trajectory impact

## Purpose

This repository is a standalone evaluation demo and does not include any proprietary system code. It reflects a simulation-side validation approach for improving perception robustness before deployment.

## Key Files

- src/lidar_degrader/.../lidar_degrader_node.py
- scripts/run_all_cases.sh
- scripts/visualize_results.py

# warehouse_sim_backup
A PX4 + Gazebo simulation of an autonomous drone performing warehouse mapping using LiDAR and camera sensors, with ArUco markers for aisle identification and ROS2 sensor streaming.


## Development context

This public repository packages a prototype evaluation workflow developed over the prior two weeks into a standalone demo for sharing. It is a public-safe version of a simulation-side validation tool used to study LiDAR degradation effects before broader deployment.

