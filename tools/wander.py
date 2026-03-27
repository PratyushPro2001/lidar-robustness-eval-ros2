#!/usr/bin/env python3
import random
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class Wander(Node):
    def __init__(self):
        super().__init__('wander')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(LaserScan, '/scan', self.on_scan, 10)
        self.timer = self.create_timer(0.1, self.on_timer)

        self.front_min = 999.0
        self.turning = False
        self.turn_dir = 1.0

        # Tune these if needed
        self.safe_dist = 0.45      # meters
        self.forward_speed = 0.12  # m/s
        self.turn_speed = 0.8      # rad/s

    def on_scan(self, msg: LaserScan):
        # Look at a ~30° cone in front
        n = len(msg.ranges)
        if n == 0:
            return
        # indices around the front (0) and wrap
        width = max(1, int(n * 30 / 360))
        front_indices = list(range(0, width)) + list(range(n - width, n))

        vals = []
        for i in front_indices:
            r = msg.ranges[i]
            if msg.range_min < r < msg.range_max and r == r:  # not NaN
                vals.append(r)
        self.front_min = min(vals) if vals else 999.0

    def on_timer(self):
        cmd = Twist()

        # If too close, start turning (random direction)
        if self.front_min < self.safe_dist:
            if not self.turning:
                self.turning = True
                self.turn_dir = random.choice([-1.0, 1.0])
            cmd.angular.z = self.turn_dir * self.turn_speed
            cmd.linear.x = 0.0
        else:
            # Go forward, add tiny random wiggle so it doesn't get stuck
            self.turning = False
            cmd.linear.x = self.forward_speed
            cmd.angular.z = random.uniform(-0.15, 0.15)

        self.pub.publish(cmd)

def main():
    rclpy.init()
    node = Wander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # stop robot on exit
        stop = Twist()
        node.pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
