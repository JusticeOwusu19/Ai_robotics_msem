import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # Robot name and description
    robot_xacro_name = "HJRobo"
    model_file = os.path.join(
        get_package_share_directory("robot_desc"),
        "model",
        "robot.urdf.xacro"
    )
    robot_description = xacro.process_file(model_file).toxml()

    # Include Gazebo launch
    gz_sim_launch = PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory("ros_gz_sim"),
            "launch",
            "gz_sim.launch.py"
        )
    )

    gazebolaunch = IncludeLaunchDescription(
        gz_sim_launch,
        launch_arguments={"gz_args": "-r empty.sdf"}.items(),
    )

    # Include robot state publisher launch (rsp.launch.py)
    rsp_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("robot_desc"),
                "launch",
                "rsp.launch.py"
            )
        )
    )

    # Spawn robot in Gazebo at z = 0.5
    spawnNode = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",
            "-name", robot_xacro_name,
            "-z", "0"
        ],
        output="screen"
    )

    # Bridge configuration
    bridge_params = os.path.join(
        get_package_share_directory("robot_desc"),
        "config",
        "gz_bridge.yaml"
    )
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "--ros-args",
            "-p",
            f"config_file:={bridge_params}",
        ],
    )

    # Final launch description
    launchDescriptionObject = LaunchDescription()
    launchDescriptionObject.add_action(rsp_launch)
    launchDescriptionObject.add_action(gazebolaunch)
    
    launchDescriptionObject.add_action(spawnNode)
    launchDescriptionObject.add_action(ros_gz_bridge)
    
    return launchDescriptionObject
