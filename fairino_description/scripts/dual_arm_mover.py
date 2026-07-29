#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import math

class DualArmTrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('dual_arm_trajectory_publisher')

        # Publishers for both arms
        self.left_pub = self.create_publisher(
            JointTrajectory,
            '/left_arm_controller/joint_trajectory',
            10
        )
        self.right_pub = self.create_publisher(
            JointTrajectory,
            '/right_arm_controller/joint_trajectory',
            10
        )

        self.angle = -math.pi/2
        self.direction = 1
        self.timer = self.create_timer(0.5, self.step)  # publish every 0.5s

    def step(self):
        # Build left arm trajectory
        left_msg = JointTrajectory()
        left_msg.joint_names = [f"left_joint{i}" for i in range(1, 7)]
        left_point = JointTrajectoryPoint()
        left_point.positions = [
            -math.pi - self.angle, self.angle, math.pi/2, 0.0, math.pi, 0.0
        ]
        left_point.time_from_start.sec = 1
        left_msg.points.append(left_point)

        # Build right arm trajectory
        right_msg = JointTrajectory()
        right_msg.joint_names = [f"right_joint{i}" for i in range(1, 7)]
        right_point = JointTrajectoryPoint()
        right_point.positions = [
            math.pi + self.angle, -math.pi - self.angle, -math.pi/2, math.pi, math.pi, 0.0
        ]
        right_point.time_from_start.sec = 1
        right_msg.points.append(right_point)

        # Publish both
        self.left_pub.publish(left_msg)
        self.right_pub.publish(right_msg)

        self.get_logger().info(f"Sent left={left_point.positions}, right={right_point.positions}")

        # Increment angle slowly
        self.angle += 0.01 * self.direction
        if abs(self.angle) < 0.6 or abs(self.angle) > (math.pi/2):
            self.direction *= -1


def main(args=None):
    rclpy.init(args=args)
    node = DualArmTrajectoryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
