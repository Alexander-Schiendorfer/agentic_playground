"""Example: differential-drive simulation without ROS2.

Run from the repo root::

    poetry run python examples/basic_kinematics.py

or, after ``pip install -e .``::

    python examples/basic_kinematics.py
"""

from __future__ import annotations

import math
import sys
import os

# Allow running the script without installing the package first.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pyrobotics.kinematics import DiffDriveRobot, Pose2D, PlanarRRRobot
from pyrobotics.simulation import Simulator


# ---------------------------------------------------------------------------
# 1.  Differential-drive: drive a circle
# ---------------------------------------------------------------------------

def circle_controller(t: float, pose: Pose2D) -> tuple[float, float]:
    """Drive in a circle: right wheel slightly faster than left."""
    return 8.0, 10.0  # rad/s – constant difference → constant curvature


robot = DiffDriveRobot(wheel_radius=0.05, wheel_base=0.20)
sim = Simulator(robot=robot, dt=0.05)
result = sim.run(circle_controller, duration=5.0, initial_pose=Pose2D(0, 0, 0))

print(f"Circle demo – final pose: {result.poses[-1]}")
print(f"  Total steps recorded: {len(result.times)}")


# ---------------------------------------------------------------------------
# 2.  Differential-drive: square path (open-loop)
# ---------------------------------------------------------------------------

FORWARD_SPEED = 10.0   # rad/s
TURN_SPEED    = 10.0   # rad/s (one wheel stationary)
SEGMENT_TIME  = 2.0    # seconds per straight segment
TURN_TIME     = 0.785  # ≈ 90 ° turn at this speed

schedule = [
    (SEGMENT_TIME, (FORWARD_SPEED, FORWARD_SPEED)),   # forward
    (TURN_TIME,    (0.0, TURN_SPEED)),                 # left turn
] * 4


def square_controller(t: float, pose: Pose2D) -> tuple[float, float]:
    elapsed = 0.0
    for duration, speeds in schedule:
        if t < elapsed + duration:
            return speeds
        elapsed += duration
    return (0.0, 0.0)


robot2 = DiffDriveRobot(wheel_radius=0.05, wheel_base=0.20)
sim2 = Simulator(robot=robot2, dt=0.05)
total_time = sum(d for d, _ in schedule)
result2 = sim2.run(square_controller, duration=total_time, initial_pose=Pose2D(0, 0, 0))

print(f"\nSquare demo – final pose: {result2.poses[-1]}")


# ---------------------------------------------------------------------------
# 3.  Planar RR arm – forward kinematics & Jacobian
# ---------------------------------------------------------------------------

arm = PlanarRRRobot(l1=0.5, l2=0.4)
q1, q2 = math.pi / 4, math.pi / 3
x, y = arm.forward_kinematics(q1, q2)
J = arm.jacobian(q1, q2)

print(f"\nPlanar RR arm (l1={arm.l1}, l2={arm.l2})")
print(f"  q1={math.degrees(q1):.1f}°, q2={math.degrees(q2):.1f}°")
print(f"  end-effector: ({x:.4f}, {y:.4f})")
print(f"  Jacobian:\n{J}")


# ---------------------------------------------------------------------------
# 4.  Optional: plot results (skipped if matplotlib unavailable)
# ---------------------------------------------------------------------------

try:
    import matplotlib  # noqa: F401
    Simulator.plot(result, title="Circle trajectory")
    Simulator.plot(result2, title="Square trajectory")
except ImportError:
    print("\nmatplotlib not found – skipping plots.")
