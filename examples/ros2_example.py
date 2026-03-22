"""Example: running the pyrobotics DiffDriveRobot inside a ROS2 node (stub).

This file shows *how* you would integrate the pure-Python kinematics from
the ``pyrobotics`` Poetry package into a ROS2 node.  It is **not** meant to
be run directly – use the full node in ``ros2_pkg/ros2_pkg/diff_drive_node.py``
after building the ROS2 workspace.

Prerequisites (Windows or Linux)
---------------------------------
1. Install ROS2 Jazzy (or Humble) from https://docs.ros.org/en/jazzy/Installation.html
2. Source the ROS2 environment::

       # Linux / macOS (bash)
       source /opt/ros/jazzy/setup.bash

       # Windows (PowerShell)
       C:\\dev\\ros2_jazzy\\local_setup.ps1

3. Create and build a colcon workspace::

       mkdir -p ~/ros2_ws/src
       cd ~/ros2_ws/src
       # Copy (or symlink) the ros2_pkg directory here
       cp -r <repo_root>/ros2_pkg .
       cd ~/ros2_ws
       colcon build --symlink-install
       source install/setup.bash   # (or install\\setup.ps1 on Windows)

4. Run the node::

       ros2 run ros2_pkg diff_drive_node

5. In another terminal, publish velocity commands::

       ros2 topic pub /cmd_vel geometry_msgs/Twist \\
           "{linear: {x: 0.5}, angular: {z: 0.3}}"

6. Watch the pose::

       ros2 run ros2_pkg pose_subscriber
       # or:
       ros2 topic echo /robot_pose
"""

# ruff: noqa: F401
print(__doc__)
