"""Tests for pyrobotics.kinematics."""

from __future__ import annotations

import math

import numpy as np
import pytest

from pyrobotics.kinematics import (
    DiffDriveRobot,
    Pose2D,
    PlanarRRRobot,
    euler_to_rotation,
    rot_x,
    rot_y,
    rot_z,
)


# ---------------------------------------------------------------------------
# Pose2D
# ---------------------------------------------------------------------------


class TestPose2D:
    def test_as_array(self):
        p = Pose2D(1.0, 2.0, math.pi / 2)
        arr = p.as_array()
        np.testing.assert_allclose(arr, [1.0, 2.0, math.pi / 2])

    def test_homogeneous_identity(self):
        p = Pose2D(0, 0, 0)
        np.testing.assert_allclose(p.homogeneous(), np.eye(3), atol=1e-10)

    def test_homogeneous_translation(self):
        p = Pose2D(3.0, 4.0, 0.0)
        H = p.homogeneous()
        np.testing.assert_allclose(H[:2, 2], [3.0, 4.0], atol=1e-10)
        np.testing.assert_allclose(H[:2, :2], np.eye(2), atol=1e-10)

    def test_add(self):
        a = Pose2D(1, 2, 0.1)
        b = Pose2D(3, 4, 0.2)
        c = a + b
        assert c.x == pytest.approx(4.0)
        assert c.y == pytest.approx(6.0)
        assert c.theta == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# DiffDriveRobot
# ---------------------------------------------------------------------------


class TestDiffDriveRobot:
    def test_straight_line(self):
        """Equal wheel speeds → straight motion along x-axis."""
        robot = DiffDriveRobot(wheel_radius=0.1, wheel_base=0.3)
        v = 10.0
        dt = 0.1
        robot.step(v, v, dt)
        expected_x = 0.1 * v * dt  # r * v * dt
        assert robot.pose.x == pytest.approx(expected_x, rel=1e-6)
        assert robot.pose.y == pytest.approx(0.0, abs=1e-10)
        assert robot.pose.theta == pytest.approx(0.0, abs=1e-10)

    def test_spin_in_place(self):
        """Opposite wheel speeds → pure rotation."""
        robot = DiffDriveRobot(wheel_radius=0.05, wheel_base=0.20)
        v = 5.0
        dt = 0.1
        robot.step(-v, v, dt)
        # x and y should remain ≈ 0 for small dt
        assert robot.pose.x == pytest.approx(0.0, abs=1e-6)
        assert robot.pose.y == pytest.approx(0.0, abs=1e-6)
        assert robot.pose.theta != pytest.approx(0.0)

    def test_full_circle(self):
        """After a full circle the robot should return near the origin."""
        robot = DiffDriveRobot(wheel_radius=0.05, wheel_base=0.20)
        v_l, v_r = 8.0, 10.0
        dt = 0.001
        # Compute period of the circle
        r = robot.wheel_radius
        L = robot.wheel_base
        omega = r * (v_r - v_l) / L
        T = 2 * math.pi / abs(omega)
        steps = int(T / dt)
        for _ in range(steps):
            robot.step(v_l, v_r, dt)
        assert robot.pose.x == pytest.approx(0.0, abs=0.05)
        assert robot.pose.y == pytest.approx(0.0, abs=0.05)

    def test_initial_pose_default(self):
        robot = DiffDriveRobot()
        assert robot.pose.x == 0.0
        assert robot.pose.y == 0.0
        assert robot.pose.theta == 0.0


# ---------------------------------------------------------------------------
# Rotation helpers
# ---------------------------------------------------------------------------


class TestRotationHelpers:
    def test_rot_x_identity_at_zero(self):
        np.testing.assert_allclose(rot_x(0), np.eye(3), atol=1e-12)

    def test_rot_y_identity_at_zero(self):
        np.testing.assert_allclose(rot_y(0), np.eye(3), atol=1e-12)

    def test_rot_z_identity_at_zero(self):
        np.testing.assert_allclose(rot_z(0), np.eye(3), atol=1e-12)

    def test_rot_z_90(self):
        R = rot_z(math.pi / 2)
        expected = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=float)
        np.testing.assert_allclose(R, expected, atol=1e-10)

    def test_euler_to_rotation_zero(self):
        np.testing.assert_allclose(
            euler_to_rotation(0, 0, 0), np.eye(3), atol=1e-12
        )

    def test_euler_orthogonal(self):
        R = euler_to_rotation(0.3, 0.5, 1.1)
        np.testing.assert_allclose(R @ R.T, np.eye(3), atol=1e-10)
        assert math.isclose(np.linalg.det(R), 1.0, abs_tol=1e-10)


# ---------------------------------------------------------------------------
# PlanarRRRobot
# ---------------------------------------------------------------------------


class TestPlanarRRRobot:
    def test_fk_fully_extended(self):
        """With q1=q2=0 the arm points straight right."""
        arm = PlanarRRRobot(l1=0.5, l2=0.4)
        x, y = arm.forward_kinematics(0.0, 0.0)
        assert x == pytest.approx(0.9, rel=1e-6)
        assert y == pytest.approx(0.0, abs=1e-10)

    def test_fk_folded(self):
        """With q2=π the second link points back; total length = |l1 - l2|."""
        arm = PlanarRRRobot(l1=0.5, l2=0.4)
        x, y = arm.forward_kinematics(0.0, math.pi)
        assert x == pytest.approx(0.1, abs=1e-6)
        assert y == pytest.approx(0.0, abs=1e-6)

    def test_jacobian_shape(self):
        arm = PlanarRRRobot()
        J = arm.jacobian(0.1, 0.2)
        assert J.shape == (2, 2)

    def test_jacobian_finite_difference(self):
        """Jacobian columns should match finite-difference approximation."""
        arm = PlanarRRRobot(l1=0.5, l2=0.4)
        q1, q2 = 0.5, 0.8
        eps = 1e-6
        J = arm.jacobian(q1, q2)

        x0, y0 = arm.forward_kinematics(q1, q2)
        x1, y1 = arm.forward_kinematics(q1 + eps, q2)
        x2, y2 = arm.forward_kinematics(q1, q2 + eps)

        dfdq1 = np.array([(x1 - x0) / eps, (y1 - y0) / eps])
        dfdq2 = np.array([(x2 - x0) / eps, (y2 - y0) / eps])

        np.testing.assert_allclose(J[:, 0], dfdq1, atol=1e-5)
        np.testing.assert_allclose(J[:, 1], dfdq2, atol=1e-5)
