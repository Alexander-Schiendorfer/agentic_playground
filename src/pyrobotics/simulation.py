"""2-D robot simulation loop (no ROS2 required).

Provides a lightweight ``Simulator`` class that steps a robot through a
sequence of wheel-velocity commands and records the trajectory.  Plotting
is optional and only attempted when ``matplotlib`` is importable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np

from .kinematics import DiffDriveRobot, Pose2D


@dataclass
class SimResult:
    """Container for a simulation trajectory."""

    times: list[float] = field(default_factory=list)
    poses: list[Pose2D] = field(default_factory=list)

    def xs(self) -> list[float]:
        return [p.x for p in self.poses]

    def ys(self) -> list[float]:
        return [p.y for p in self.poses]

    def thetas(self) -> list[float]:
        return [p.theta for p in self.poses]


# A *controller* is any callable: (t, pose) -> (v_left, v_right)
Controller = Callable[[float, Pose2D], tuple[float, float]]


class Simulator:
    """Simulate a :class:`~pyrobotics.kinematics.DiffDriveRobot`.

    Parameters
    ----------
    robot : DiffDriveRobot
        The robot model to simulate.
    dt : float
        Fixed time step in seconds.
    """

    def __init__(self, robot: DiffDriveRobot | None = None, dt: float = 0.05) -> None:
        self.robot = robot or DiffDriveRobot()
        self.dt = dt

    def run(
        self,
        controller: Controller,
        duration: float,
        initial_pose: Pose2D | None = None,
    ) -> SimResult:
        """Run the simulation.

        Parameters
        ----------
        controller :
            Function ``(t, pose) -> (v_left, v_right)`` supplying wheel
            velocities (rad/s) at each time step.
        duration :
            Total simulation time in seconds.
        initial_pose :
            Override the robot's starting pose; defaults to the current
            ``robot.pose``.

        Returns
        -------
        SimResult
            Recorded trajectory.
        """
        if initial_pose is not None:
            self.robot.pose = initial_pose

        result = SimResult()
        t = 0.0
        steps = int(duration / self.dt)

        result.times.append(t)
        result.poses.append(Pose2D(*self.robot.pose.as_array()))

        for _ in range(steps):
            v_l, v_r = controller(t, self.robot.pose)
            self.robot.step(v_l, v_r, self.dt)
            t += self.dt
            result.times.append(t)
            result.poses.append(Pose2D(*self.robot.pose.as_array()))

        return result

    # ------------------------------------------------------------------
    # Convenience: plot trajectory
    # ------------------------------------------------------------------

    @staticmethod
    def plot(result: SimResult, title: str = "Trajectory") -> None:  # pragma: no cover
        """Plot the (x, y) trajectory using matplotlib (if available)."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not available – skipping plot.")
            return

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))

        ax = axes[0]
        ax.plot(result.xs(), result.ys(), "b-", linewidth=1.5)
        ax.plot(result.xs()[0], result.ys()[0], "go", label="start")
        ax.plot(result.xs()[-1], result.ys()[-1], "rs", label="end")
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        ax.set_title(title)
        ax.legend()
        ax.set_aspect("equal")
        ax.grid(True)

        ax2 = axes[1]
        ax2.plot(result.times, np.degrees(result.thetas()), "m-", linewidth=1.5)
        ax2.set_xlabel("time [s]")
        ax2.set_ylabel("heading [°]")
        ax2.set_title("Heading over time")
        ax2.grid(True)

        plt.tight_layout()
        plt.show()
