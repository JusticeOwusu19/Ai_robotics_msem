import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    model_file = os.path.join(
        get_package_share_directory("mecha_robot_desc"),
        "model",
        "robot.urdf.xacro"
    )
    robot_description = xacro.process_file(model_file).toxml()

    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True        # <-- ADDED
        }],
    )

    # NOTE: joint_state_publisher is commented out correctly —
    # Gazebo publishes joint states via the bridge, not this node.
    # Enabling it would conflict with Gazebo's joint states.

    launch_description = LaunchDescription()
    launch_description.add_action(node_robot_state_publisher)

    return launch_description
    # RViz is removed from here — it belongs in the main launch file
    # so it gets sim_time and starts after everything else is ready
