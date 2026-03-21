import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    model_file = os.path.join(get_package_share_directory(
        "robot_desc"), "model", "robot.urdf.xacro")
    robot_description = xacro.process_file(model_file).toxml()

    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description}],
    )

    node_joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="screen",
    )

    node_rviz = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
    )

    launch_description = LaunchDescription()
    launch_description.add_action(node_robot_state_publisher)
    #launch_description.add_action(node_joint_state_publisher)
    launch_description.add_action(node_rviz)

    return launch_description
