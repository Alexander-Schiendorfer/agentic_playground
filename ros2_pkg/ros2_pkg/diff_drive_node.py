"""Differential-drive ROS2 node.

Subscribes to ``/cmd_vel`` (``geometry_msgs/Twist``) and publishes the
simulated robot pose on ``/robot_pose`` (``geometry_msgs/Pose2D``) at a
fixed rate.

Usage (after building the ROS2 workspace)::

    ros2 run ros2_pkg diff_drive_node
"""

from __future__ import annotations

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D, Twist

# Reuse the pure-Python kinematics (no ROS2 dependency in that module)
try:
    from pyrobotics.kinematics import DiffDriveRobot, Pose2D as KinPose2D
except ImportError:
    # Fallback: inline a minimal DiffDriveRobot so the node still works even
    # if the pyrobotics package is not installed in the ROS2 environment.
    from ros2_pkg._fallback_kinematics import DiffDriveRobot, KinPose2D  # type: ignore[no-redef]


TIMER_PERIOD = 0.05  # seconds (20 Hz)


class DiffDriveNode(Node):
    """Simulate a differential-drive robot and publish its pose."""

    def __init__(self) -> None:
        super().__init__("diff_drive_node")

        # Parameters --------------------------------------------------------
        self.declare_parameter("wheel_radius", 0.05)
        self.declare_parameter("wheel_base", 0.20)

        wheel_radius = self.get_parameter("wheel_radius").value
        wheel_base = self.get_parameter("wheel_base").value

        # Robot model -------------------------------------------------------
        self._robot = DiffDriveRobot(
            wheel_radius=wheel_radius,
            wheel_base=wheel_base,
        )
        self._v_left: float = 0.0
        self._v_right: float = 0.0

        # ROS interfaces ----------------------------------------------------
        self._pose_pub = self.create_publisher(Pose2D, "/robot_pose", 10)
        self._cmd_sub = self.create_subscription(
            Twist, "/cmd_vel", self._cmd_callback, 10
        )
        self._timer = self.create_timer(TIMER_PERIOD, self._timer_callback)

        self.get_logger().info(
            f"DiffDriveNode started "
            f"(r={wheel_radius} m, L={wheel_base} m, dt={TIMER_PERIOD} s)"
        )

    # ------------------------------------------------------------------
    def _cmd_callback(self, msg: Twist) -> None:
        """Convert Twist (linear.x, angular.z) to wheel velocities."""
        v = msg.linear.x
        omega = msg.angular.z
        r = self._robot.wheel_radius
        L = self._robot.wheel_base
        # Inverse kinematics: wheel velocities from v and omega
        self._v_right = (2 * v + omega * L) / (2 * r)
        self._v_left = (2 * v - omega * L) / (2 * r)

    def _timer_callback(self) -> None:
        self._robot.step(self._v_left, self._v_right, TIMER_PERIOD)
        pose_msg = Pose2D()
        pose_msg.x = self._robot.pose.x
        pose_msg.y = self._robot.pose.y
        pose_msg.theta = self._robot.pose.theta
        self._pose_pub.publish(pose_msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = DiffDriveNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
