from setuptools import find_packages, setup

package_name = "ros2_pkg"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Alexander Schiendorfer",
    maintainer_email="maintainer@example.com",
    description="Minimal ROS2 Python package for the pyrobotics playground.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "diff_drive_node = ros2_pkg.diff_drive_node:main",
            "pose_subscriber = ros2_pkg.pose_subscriber:main",
        ],
    },
)
