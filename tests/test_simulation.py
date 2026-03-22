"""Tests for pyrobotics.simulation."""

from __future__ import annotations

import math

import pytest

from pyrobotics.kinematics import DiffDriveRobot, Pose2D
from pyrobotics.simulation import SimResult, Simulator


class TestSimResult:
    def test_accessors(self):
        r = SimResult()
        r.times = [0.0, 0.1]
        r.poses = [Pose2D(0, 0, 0), Pose2D(0.1, 0.0, 0.0)]
        assert r.xs() == [0.0, 0.1]
        assert r.ys() == [0.0, 0.0]
        assert r.thetas() == [0.0, 0.0]


class TestSimulator:
    def _constant_controller(self, vl: float, vr: float):
        def ctrl(t: float, pose: Pose2D) -> tuple[float, float]:
            return vl, vr

        return ctrl

    def test_initial_pose_recorded(self):
        sim = Simulator(dt=0.1)
        result = sim.run(
            self._constant_controller(0, 0),
            duration=0.0,
            initial_pose=Pose2D(1.0, 2.0, 0.5),
        )
        assert len(result.poses) == 1
        assert result.poses[0].x == pytest.approx(1.0)

    def test_step_count(self):
        sim = Simulator(dt=0.1)
        result = sim.run(
            self._constant_controller(5, 5),
            duration=1.0,
            initial_pose=Pose2D(),
        )
        # initial pose + 10 steps
        assert len(result.times) == 11
        assert len(result.poses) == 11

    def test_zero_velocity_stays_at_origin(self):
        sim = Simulator(dt=0.1)
        result = sim.run(
            self._constant_controller(0, 0),
            duration=2.0,
            initial_pose=Pose2D(),
        )
        for pose in result.poses:
            assert pose.x == pytest.approx(0.0, abs=1e-12)
            assert pose.y == pytest.approx(0.0, abs=1e-12)

    def test_straight_motion_distance(self):
        """Constant forward velocity should cover v*t distance."""
        robot = DiffDriveRobot(wheel_radius=0.1, wheel_base=0.3)
        sim = Simulator(robot=robot, dt=0.01)
        v = 10.0  # rad/s → linear = r*v = 1 m/s
        duration = 2.0
        result = sim.run(
            self._constant_controller(v, v),
            duration=duration,
            initial_pose=Pose2D(),
        )
        expected_x = robot.wheel_radius * v * duration
        assert result.poses[-1].x == pytest.approx(expected_x, rel=1e-3)
        assert result.poses[-1].y == pytest.approx(0.0, abs=1e-6)

    def test_initial_pose_override(self):
        sim = Simulator(dt=0.1)
        result = sim.run(
            self._constant_controller(0, 0),
            duration=0.0,
            initial_pose=Pose2D(5.0, -3.0, math.pi),
        )
        assert result.poses[0].x == pytest.approx(5.0)
        assert result.poses[0].y == pytest.approx(-3.0)
        assert result.poses[0].theta == pytest.approx(math.pi)
