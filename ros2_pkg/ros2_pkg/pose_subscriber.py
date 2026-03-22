"""Pose subscriber node.

Subscribes to ``/robot_pose`` (``geometry_msgs/Pose2D``) and prints each
incoming pose to the ROS2 logger.

Usage::

    ros2 run ros2_pkg pose_subscriber
"""

from __future__ import annotations

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D


class PoseSubscriber(Node):
    """Listen to ``/robot_pose`` and log each pose."""

    def __init__(self) -> None:
        super().__init__("pose_subscriber")
        self._sub = self.create_subscription(
            Pose2D, "/robot_pose", self._callback, 10
        )
        self.get_logger().info("PoseSubscriber ready – listening on /robot_pose")

    def _callback(self, msg: Pose2D) -> None:
        self.get_logger().info(
            f"pose: x={msg.x:.3f}  y={msg.y:.3f}  "
            f"theta={math.degrees(msg.theta):.1f}°"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = PoseSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
