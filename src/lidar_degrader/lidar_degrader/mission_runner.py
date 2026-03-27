#!/usr/bin/env python3

import math
import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


def yaw_from_quaternion(x, y, z, w):
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def normalize_angle(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


class MissionRunner(Node):
    def __init__(self):
        super().__init__('mission_runner')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_cb, 10)

        self.x = None
        self.y = None
        self.yaw = None

        self.linear_speed = 0.16
        self.angular_speed = 0.38
        self.side_length = 3.0
        self.turn_angle = math.pi / 2.0
        self.position_tol = 0.05
        self.angle_tol = 0.04

    def odom_cb(self, msg: Odometry):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        self.yaw = yaw_from_quaternion(q.x, q.y, q.z, q.w)

    def wait_for_odom(self):
        self.get_logger().info('Waiting for /odom ...')
        while rclpy.ok() and (self.x is None or self.y is None or self.yaw is None):
            rclpy.spin_once(self, timeout_sec=0.1)
        self.get_logger().info('Odometry received.')

    def publish_cmd(self, linear_x=0.0, angular_z=0.0):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.pub.publish(msg)

    def stop_robot(self):
        for _ in range(8):
            self.publish_cmd(0.0, 0.0)
            time.sleep(0.05)

    def drive_forward(self, distance):
        start_x = self.x
        start_y = self.y
        self.get_logger().info(f'Driving forward {distance:.2f} m')

        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)

            dx = self.x - start_x
            dy = self.y - start_y
            traveled = math.sqrt(dx * dx + dy * dy)
            remaining = distance - traveled

            if remaining <= self.position_tol:
                break

            speed = self.linear_speed if remaining > 0.25 else 0.05
            self.publish_cmd(linear_x=speed, angular_z=0.0)

        self.stop_robot()
        time.sleep(0.4)

    def turn_left(self, angle_rad):
        start_yaw = self.yaw
        target = normalize_angle(start_yaw + angle_rad)
        self.get_logger().info(f'Turning left {math.degrees(angle_rad):.1f} deg')

        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)

            error = normalize_angle(target - self.yaw)
            if abs(error) <= self.angle_tol:
                break

            speed = self.angular_speed if abs(error) > 0.2 else 0.12
            self.publish_cmd(linear_x=0.0, angular_z=speed)

        self.stop_robot()
        time.sleep(0.4)

    def run_mission(self):
        self.wait_for_odom()
        self.get_logger().info('Starting square mission in 2 seconds...')
        time.sleep(2.0)

        for i in range(4):
            self.get_logger().info(f'=== Side {i+1}/4 ===')
            self.drive_forward(self.side_length)
            if i < 3:
                self.turn_left(self.turn_angle)

        self.stop_robot()
        self.get_logger().info('Mission complete.')

def main(args=None):
    rclpy.init(args=args)
    node = MissionRunner()
    try:
        node.run_mission()
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
