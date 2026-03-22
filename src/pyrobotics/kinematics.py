"""Basic 2-D / 3-D kinematics helpers.

These utilities are intentionally dependency-light (numpy only) so they work
on any platform – including Windows – without a full ROS2 installation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


# ---------------------------------------------------------------------------
# Pose helpers
# ---------------------------------------------------------------------------


@dataclass
class Pose2D:
    """2-D rigid-body pose: (x, y, theta [rad])."""

    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.theta], dtype=float)

    def homogeneous(self) -> np.ndarray:
        """Return the 3×3 SE(2) homogeneous transformation matrix."""
        c, s = math.cos(self.theta), math.sin(self.theta)
        return np.array(
            [
                [c, -s, self.x],
                [s, c, self.y],
                [0.0, 0.0, 1.0],
            ]
        )

    def __add__(self, other: "Pose2D") -> "Pose2D":
        return Pose2D(
            self.x + other.x,
            self.y + other.y,
            self.theta + other.theta,
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Pose2D(x={self.x:.3f}, y={self.y:.3f}, theta={math.degrees(self.theta):.1f}°)"


# ---------------------------------------------------------------------------
# Differential-drive robot kinematics
# ---------------------------------------------------------------------------


@dataclass
class DiffDriveRobot:
    """Simple differential-drive kinematic model.

    Parameters
    ----------
    wheel_radius : float
        Radius of each drive wheel in metres.
    wheel_base : float
        Distance between the two drive wheels in metres.
    pose : Pose2D
        Current pose of the robot (default: origin, facing +x).
    """

    wheel_radius: float = 0.05
    wheel_base: float = 0.20
    pose: Pose2D = field(default_factory=Pose2D)

    def step(self, v_left: float, v_right: float, dt: float = 0.1) -> Pose2D:
        """Advance the robot by one time-step using the unicycle model.

        Parameters
        ----------
        v_left, v_right : float
            Rotational velocities of the left / right wheels (rad/s).
        dt : float
            Time step in seconds.

        Returns
        -------
        Pose2D
            The updated pose (also stored in ``self.pose``).
        """
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

        self.pose = Pose2D(self.pose.x + dx, self.pose.y + dy, theta_new)
        return self.pose


# ---------------------------------------------------------------------------
# Rotation helpers (SO3)
# ---------------------------------------------------------------------------


def rot_x(angle: float) -> np.ndarray:
    """3×3 rotation matrix about the x-axis (angle in radians)."""
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def rot_y(angle: float) -> np.ndarray:
    """3×3 rotation matrix about the y-axis (angle in radians)."""
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)


def rot_z(angle: float) -> np.ndarray:
    """3×3 rotation matrix about the z-axis (angle in radians)."""
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def euler_to_rotation(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """Compose a 3×3 rotation matrix from ZYX Euler angles (radians)."""
    return rot_z(yaw) @ rot_y(pitch) @ rot_x(roll)


# ---------------------------------------------------------------------------
# 2-DOF planar arm (RR robot) – forward kinematics
# ---------------------------------------------------------------------------


@dataclass
class PlanarRRRobot:
    """2-DOF revolute–revolute planar arm.

    Parameters
    ----------
    l1, l2 : float
        Link lengths in metres.
    """

    l1: float = 0.5
    l2: float = 0.4

    def forward_kinematics(self, q1: float, q2: float) -> tuple[float, float]:
        """Return the (x, y) position of the end-effector.

        Parameters
        ----------
        q1, q2 : float
            Joint angles in radians.
        """
        x = self.l1 * math.cos(q1) + self.l2 * math.cos(q1 + q2)
        y = self.l1 * math.sin(q1) + self.l2 * math.sin(q1 + q2)
        return x, y

    def jacobian(self, q1: float, q2: float) -> np.ndarray:
        """Return the 2×2 geometric Jacobian at joint configuration (q1, q2)."""
        s1, c1 = math.sin(q1), math.cos(q1)
        s12 = math.sin(q1 + q2)
        c12 = math.cos(q1 + q2)
        J = np.array(
            [
                [-self.l1 * s1 - self.l2 * s12, -self.l2 * s12],
                [self.l1 * c1 + self.l2 * c12, self.l2 * c12],
            ]
        )
        return J
