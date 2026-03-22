import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    TimerAction,
    RegisterEventHandler
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    # ------------------------------------------------------------------ #
    # Robot description — processed ONCE here and passed to RSP           #
    # ------------------------------------------------------------------ #
    model_file = os.path.join(
        get_package_share_directory("robot_desc"),
        "model",
        "robot.urdf.xacro"
    )
    robot_description = xacro.process_file(model_file).toxml()

    # ------------------------------------------------------------------ #
    # Robot State Publisher                                                #
    # ------------------------------------------------------------------ #
    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True
        }]
    )

    # ------------------------------------------------------------------ #
    # Gazebo                                                               #
    # ------------------------------------------------------------------ #
    gz_sim_launch = PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory("ros_gz_sim"),
            "launch",
            "gz_sim.launch.py"
        )
    )

    gazebo_launch = IncludeLaunchDescription(
        gz_sim_launch,
        launch_arguments={"gz_args": "-r empty.sdf"}.items(),
    )

    # ------------------------------------------------------------------ #
    # Spawn robot — delayed to give Gazebo time to start                  #
    # ------------------------------------------------------------------ #
    spawn_node = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",
            "-name", "HJRobo",
            "-z", "0.15"        # <-- prevents ground collision physics jitter
        ],
        output="screen"
    )

    delayed_spawn = TimerAction(
        period=3.0,             # wait 3s for Gazebo to be ready
        actions=[spawn_node]
    )

    # ------------------------------------------------------------------ #
    # ROS-Gazebo Bridge                                                    #
    # ------------------------------------------------------------------ #
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
        parameters=[{
            "use_sim_time": True    # <-- ADDED
        }]
    )

    # ------------------------------------------------------------------ #
    # RViz — delayed until after spawn so TF tree is populated            #
    # ------------------------------------------------------------------ #
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        parameters=[{
            "use_sim_time": True    # <-- ADDED
        }]
    )

    delayed_rviz = TimerAction(
        period=5.0,             # wait for robot to be spawned first
        actions=[rviz_node]
    )

    # ------------------------------------------------------------------ #
    # Launch Description                                                 #
    # ------------------------------------------------------------------ #
    return LaunchDescription([
        node_robot_state_publisher,     # 1. RSP first
        gazebo_launch,                  # 2. Start Gazebo
        delayed_spawn,                  # 3. Spawn robot after 3s
        ros_gz_bridge,                  # 4. Bridge
        delayed_rviz,                   # 5. RViz last after 5s
    ])
