#!/usr/bin/env python3

import math
import random
from typing import List

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LidarDegraderNode(Node):
    def __init__(self) -> None:
        super().__init__('lidar_degrader')

        self.declare_parameter('input_topic', '/scan')
        self.declare_parameter('output_topic', '/scan_degraded')
        self.declare_parameter('noise_stddev', 0.02)
        self.declare_parameter('drop_probability', 0.05)
        self.declare_parameter('max_range_cap', 3.5)

        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        output_topic = self.get_parameter('output_topic').get_parameter_value().string_value

        self.sub = self.create_subscription(
            LaserScan,
            input_topic,
            self.scan_callback,
            10
        )
        self.pub = self.create_publisher(LaserScan, output_topic, 10)

        self.get_logger().info(f'Subscribing to: {input_topic}')
        self.get_logger().info(f'Publishing degraded scan to: {output_topic}')

    def scan_callback(self, msg: LaserScan) -> None:
        noise_stddev = float(self.get_parameter('noise_stddev').value)
        drop_probability = float(self.get_parameter('drop_probability').value)
        max_range_cap = float(self.get_parameter('max_range_cap').value)

        out = LaserScan()
        out.header = msg.header
        out.angle_min = msg.angle_min
        out.angle_max = msg.angle_max
        out.angle_increment = msg.angle_increment
        out.time_increment = msg.time_increment
        out.scan_time = msg.scan_time
        out.range_min = msg.range_min
        out.range_max = min(msg.range_max, max_range_cap) if max_range_cap > 0.0 else msg.range_max
        out.intensities = list(msg.intensities)

        degraded_ranges: List[float] = []

        for r in msg.ranges:
            if math.isinf(r) or math.isnan(r):
                degraded_ranges.append(r)
                continue

            if random.random() < drop_probability:
                degraded_ranges.append(float('inf'))
                continue

            noisy_r = r + random.gauss(0.0, noise_stddev)

            if noisy_r < msg.range_min:
                noisy_r = msg.range_min

            if max_range_cap > 0.0:
                if noisy_r > max_range_cap:
                    degraded_ranges.append(float('inf'))
                    continue
            else:
                if noisy_r > msg.range_max:
                    degraded_ranges.append(float('inf'))
                    continue

            degraded_ranges.append(float(noisy_r))

        out.ranges = degraded_ranges
        self.pub.publish(out)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LidarDegraderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
