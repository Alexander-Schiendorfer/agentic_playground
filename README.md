# agentic_playground – Python Robotics Playground

A self-contained Python robotics project that:

* uses **[Poetry](https://python-poetry.org/)** for dependency management
* runs **natively on Windows, Linux and macOS** (no C compiler required for the core package)
* ships optional **[ROS2](https://docs.ros.org/)** integration via a colcon-buildable `ros2_pkg`

---

## Repository layout

```
agentic_playground/
├── pyproject.toml           # Poetry project (package: pyrobotics)
├── src/
│   └── pyrobotics/
│       ├── __init__.py
│       ├── kinematics.py    # Pose2D, DiffDriveRobot, PlanarRRRobot, SO3 helpers
│       └── simulation.py    # Simulator – step a robot with a controller function
├── ros2_pkg/                # colcon-buildable ROS2 Python package
│   ├── package.xml
│   ├── setup.py / setup.cfg
│   └── ros2_pkg/
│       ├── diff_drive_node.py   # publisher: /robot_pose  subscriber: /cmd_vel
│       └── pose_subscriber.py   # echo /robot_pose to logger
├── examples/
│   ├── basic_kinematics.py  # standalone demo (no ROS2 needed)
│   └── ros2_example.py      # annotated setup instructions
└── tests/
    ├── test_kinematics.py
    └── test_simulation.py
```

---

## Quick-start (no ROS2)

### 1 · Install Poetry

```powershell
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Linux / macOS
curl -sSL https://install.python-poetry.org | python3 -
```

### 2 · Install the project

```bash
cd agentic_playground
poetry install
```

Poetry creates a virtual environment automatically.  On Windows it is placed
under `%APPDATA%\pypoetry\virtualenvs\` by default.

### 3 · Run the demo

```bash
poetry run python examples/basic_kinematics.py
```

Expected output (matplotlib plots shown if available):

```
Circle demo – final pose: Pose2D(x=0.539, y=1.621, theta=143.2°)
Square demo – final pose: Pose2D(x=0.990, y=-0.037, theta=444.0°)
Planar RR arm (l1=0.5, l2=0.4)
  end-effector: (0.2500, 0.7399)
  Jacobian: ...
```

### 4 · Run the tests

```bash
poetry run pytest
```

---

## Package overview (`pyrobotics`)

### `pyrobotics.kinematics`

| Symbol | Description |
|---|---|
| `Pose2D` | 2-D rigid-body pose `(x, y, θ)` with SE(2) homogeneous matrix |
| `DiffDriveRobot` | Differential-drive forward kinematics (unicycle model) |
| `PlanarRRRobot` | 2-DOF revolute–revolute arm: FK + geometric Jacobian |
| `rot_x/y/z` | Elementary SO(3) rotation matrices |
| `euler_to_rotation` | ZYX Euler → 3×3 rotation matrix |

### `pyrobotics.simulation`

| Symbol | Description |
|---|---|
| `Simulator` | Steps a `DiffDriveRobot` using a controller `(t, pose) → (v_l, v_r)` |
| `SimResult` | Trajectory container with `.xs()`, `.ys()`, `.thetas()` helpers |
| `Simulator.plot` | Optional matplotlib trajectory visualisation |

---

## ROS2 integration

### ROS2 on Windows

ROS2 **Jazzy** and **Humble** both support Windows 10/11 (64-bit).

1. Follow the official installer guide:
   <https://docs.ros.org/en/jazzy/Installation/Windows-Install-Binary.html>

2. After installation, open **ROS2 Command Prompt** (or run the setup script):

   ```powershell
   C:\dev\ros2_jazzy\local_setup.ps1
   ```

3. Verify the installation:

   ```powershell
   ros2 --version
   ```

### Building the `ros2_pkg` package

```bash
# create a colcon workspace
mkdir -p ~/ros2_ws/src
cp -r ros2_pkg ~/ros2_ws/src/

cd ~/ros2_ws
colcon build --symlink-install

# source the overlay (Linux)
source install/setup.bash

# source the overlay (Windows PowerShell)
.\install\setup.ps1
```

### Running the nodes

```bash
# Terminal 1 – differential-drive simulator
ros2 run ros2_pkg diff_drive_node

# Terminal 2 – send velocity commands
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
    "{linear: {x: 0.5}, angular: {z: 0.3}}"

# Terminal 3 – receive pose updates
ros2 run ros2_pkg pose_subscriber
# or:
ros2 topic echo /robot_pose
```

The `diff_drive_node` accepts the following ROS2 parameters:

| Parameter | Default | Description |
|---|---|---|
| `wheel_radius` | `0.05` m | Radius of each drive wheel |
| `wheel_base` | `0.20` m | Wheel-to-wheel distance |

Override at launch:

```bash
ros2 run ros2_pkg diff_drive_node \
    --ros-args -p wheel_radius:=0.08 -p wheel_base:=0.30
```

### How the pure-Python kinematics interoperate with ROS2

`diff_drive_node.py` imports `DiffDriveRobot` directly from the `pyrobotics`
Poetry package.  This means the core maths are tested independently of ROS2.
If `pyrobotics` is not installed in the ROS2 Python environment a thin
fallback (`ros2_pkg/_fallback_kinematics.py`) is used automatically.

---

## Windows compilation notes

The `pyrobotics` package is **pure Python** (numpy/scipy/matplotlib are
pre-built wheels on PyPI for Windows x64 — no compiler needed).

`roboticstoolbox-python` also ships Windows wheels.  If you need to build any
extension from source on Windows, install the
[Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
and run:

```powershell
winget install Microsoft.VisualStudio.2022.BuildTools
```

---

## Development

```bash
# lint
poetry run ruff check src tests

# type-check
poetry run mypy src

# tests with coverage
poetry run pytest --cov=pyrobotics --cov-report=term-missing
```
