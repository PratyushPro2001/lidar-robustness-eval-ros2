#!/usr/bin/env bash
set -eo pipefail

WS=~/antioch_sim
MAP_DIR="$WS/maps"
PATH_DIR="$WS/paths"

mkdir -p "$MAP_DIR" "$PATH_DIR"

set +u
source /opt/ros/humble/setup.bash
source "$WS/install/setup.bash"
set -u

export TURTLEBOT3_MODEL=waffle_pi
export LIBGL_ALWAYS_SOFTWARE=1
export GAZEBO_MODEL_PATH=/opt/ros/humble/share/turtlebot3_gazebo/models:$HOME/.gazebo/models:${GAZEBO_MODEL_PATH:-}
export GAZEBO_MODEL_DATABASE_URI=""

cleanup() {
  pkill -9 gzclient || true
  pkill -9 gzserver || true
  pkill -9 -f robot_state_publisher || true
  pkill -9 -f spawn_entity || true
  pkill -9 -f async_slam_toolbox_node || true
  pkill -9 -f lidar_degrader_node || true
  pkill -9 -f odom_to_path || true
  pkill -9 -f mission_runner || true
  sleep 4
}

check_outputs() {
  local CASE_NAME="$1"
  test -f "$MAP_DIR/${CASE_NAME}.yaml"
  test -f "$MAP_DIR/${CASE_NAME}.pgm"
  test -f "$PATH_DIR/${CASE_NAME}_path.csv"
}

run_case() {
  local CASE_NAME="$1"
  local SCAN_TOPIC="$2"
  local USE_DEGRADER="$3"
  local NOISE="$4"
  local DROP="$5"
  local CAP="$6"

  echo "=============================="
  echo "RUNNING CASE: $CASE_NAME"
  echo "=============================="

  cleanup

  ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py x_pose:=-1.5 y_pose:=-1.5 > "/tmp/${CASE_NAME}_gazebo.log" 2>&1 &
  sleep 8

  # Force headless: keep gzserver, kill gzclient
  pkill -9 gzclient || true
  sleep 2

  if [ "$USE_DEGRADER" = "true" ]; then
    ros2 run lidar_degrader lidar_degrader_node \
      --ros-args \
      -p input_topic:=/scan \
      -p output_topic:="$SCAN_TOPIC" \
      -p noise_stddev:="$NOISE" \
      -p drop_probability:="$DROP" \
      -p max_range_cap:="$CAP" > "/tmp/${CASE_NAME}_degrader.log" 2>&1 &
    sleep 3
  fi

  ros2 launch lidar_degrader slam_scan.launch.py scan_topic:="$SCAN_TOPIC" > "/tmp/${CASE_NAME}_slam.log" 2>&1 &
  sleep 8

  ros2 run lidar_degrader odom_to_path \
    --ros-args \
    -p csv_path:="$PATH_DIR/${CASE_NAME}_path.csv" > "/tmp/${CASE_NAME}_path.log" 2>&1 &
  sleep 3

  if ! ros2 run lidar_degrader mission_runner > "/tmp/${CASE_NAME}_mission.log" 2>&1; then
    echo "Mission failed for case: $CASE_NAME"
    cleanup
    exit 1
  fi

  sleep 3

  if ! ros2 run nav2_map_server map_saver_cli -f "$MAP_DIR/${CASE_NAME}" > "/tmp/${CASE_NAME}_mapsave.log" 2>&1; then
    echo "Map save failed for case: $CASE_NAME"
    cleanup
    exit 1
  fi

  sleep 3

  if ! check_outputs "$CASE_NAME"; then
    echo "Expected outputs missing for case: $CASE_NAME"
    cleanup
    exit 1
  fi

  echo "Saved outputs for case: $CASE_NAME"
  echo "  Map:  $MAP_DIR/${CASE_NAME}.yaml + .pgm"
  echo "  Path: $PATH_DIR/${CASE_NAME}_path.csv"

  cleanup
  sleep 6
}

run_case "ideal" "/scan" "false" "0.0" "0.0" "3.5"
run_case "mild" "/scan_degraded_mild" "true" "0.03" "0.08" "2.0"
run_case "strong" "/scan_degraded_strong" "true" "0.08" "0.20" "1.2"

echo "DONE. Outputs saved in:"
echo "  $MAP_DIR"
echo "  $PATH_DIR"
