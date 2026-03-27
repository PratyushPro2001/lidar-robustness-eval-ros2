#!/usr/bin/env python3

from collections import deque
import csv
import math
from pathlib import Path

import rclpy
from nav_msgs.msg import Odometry, Path as NavPath
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node


def yaw_from_quaternion(x, y, z, w):
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


class OdomToPath(Node):
    def __init__(self):
        super().__init__('odom_to_path')

        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('path_topic', '/trajectory_path')
        self.declare_parameter('frame_id', 'odom')
        self.declare_parameter('max_poses', 2000)
        self.declare_parameter('csv_path', '')

        odom_topic = self.get_parameter('odom_topic').value
        path_topic = self.get_parameter('path_topic').value
        self.frame_id = self.get_parameter('frame_id').value
        self.max_poses = int(self.get_parameter('max_poses').value)
        self.csv_path = self.get_parameter('csv_path').value

        self.path_pub = self.create_publisher(NavPath, path_topic, 10)
        self.odom_sub = self.create_subscription(Odometry, odom_topic, self.odom_cb, 10)

        self.path = NavPath()
        self.path.header.frame_id = self.frame_id
        self.pose_buffer = deque(maxlen=self.max_poses)

        self.csv_file = None
        self.csv_writer = None

        if self.csv_path:
            csv_path_obj = Path(self.csv_path).expanduser()
            csv_path_obj.parent.mkdir(parents=True, exist_ok=True)
            self.csv_file = open(csv_path_obj, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['stamp_sec', 'stamp_nanosec', 'x', 'y', 'yaw'])
            self.get_logger().info(f'Writing trajectory CSV to {csv_path_obj}')

        self.get_logger().info(f'Subscribing to {odom_topic}')
        self.get_logger().info(f'Publishing path to {path_topic}')
        self.get_logger().info(f'Frame ID: {self.frame_id}')

    def odom_cb(self, msg: Odometry):
        pose = PoseStamped()
        pose.header = msg.header
        pose.header.frame_id = self.frame_id
        pose.pose = msg.pose.pose

        self.pose_buffer.append(pose)

        self.path.header.stamp = msg.header.stamp
        self.path.header.frame_id = self.frame_id
        self.path.poses = list(self.pose_buffer)
        self.path_pub.publish(self.path)

        if self.csv_writer is not None:
            q = msg.pose.pose.orientation
            yaw = yaw_from_quaternion(q.x, q.y, q.z, q.w)
            p = msg.pose.pose.position
            self.csv_writer.writerow([
                msg.header.stamp.sec,
                msg.header.stamp.nanosec,
                p.x,
                p.y,
                yaw,
            ])
            self.csv_file.flush()

    def destroy_node(self):
        if self.csv_file is not None:
            self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = OdomToPath()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
