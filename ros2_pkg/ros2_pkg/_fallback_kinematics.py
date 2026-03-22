"""Fallback kinematics used when pyrobotics is not installed.

This module mirrors the minimal API needed by diff_drive_node.py so the ROS2
node can work in environments where the pyrobotics Poetry package is not
installed alongside the ROS2 workspace.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class KinPose2D:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0

    def as_array(self) -> list[float]:
        return [self.x, self.y, self.theta]


@dataclass
class DiffDriveRobot:
    wheel_radius: float = 0.05
    wheel_base: float = 0.20
    pose: KinPose2D = field(default_factory=KinPose2D)

    def step(self, v_left: float, v_right: float, dt: float = 0.1) -> KinPose2D:
        r = self.wheel_radius
        L = self.wheel_base
        v = r * (v_right + v_left) / 2.0
        omega = r * (v_right - v_left) / L
        theta_new = self.pose.theta + omega * dt
        if abs(omega) < 1e-9:
            dx = v * math.cos(self.pose.theta) * dt
            dy = v * math.sin(self.pose.theta) * dt
        else:
            dx = (v / omega) * (math.sin(theta_new) - math.sin(self.pose.theta))
            dy = (v / omega) * (math.cos(self.pose.theta) - math.cos(theta_new))
        self.pose = KinPose2D(self.pose.x + dx, self.pose.y + dy, theta_new)
        return self.pose
