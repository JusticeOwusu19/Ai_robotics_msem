import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    bridge_params = os.path.join(get_package_share_directory(
        "robot_desc"), "config", "gz_bridge.yaml")
    robot_xacro_name = "HJRobo"
    model_file = os.path.join(get_package_share_directory(
        "robot_desc"), "model", "robot.urdf.xacro")
    robot_description = xacro.process_file(model_file).toxml()

    gz_sim_launch = PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory(
            "ros_gz_sim"), "launch", "gz_sim.launch.py")
    )

    gazebolaunch = IncludeLaunchDescription(
        gz_sim_launch,
        launch_arguments={"gz_args": "-r empty.sdf"}.items(),
    )

    spawnNode = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-topic", "robot_description", "-name", robot_xacro_name],
        output="screen"
    )

    
    # jointStateBroadcasterSpawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["joint_state_broadcaster",
    #                "--controller-manager", "/controller_manager"],
    #     output="screen",
    # )

    # diffDriveSpawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["diff_drive_controller",
    #                "--controller-manager", "/controller_manager"],
    #     output="screen",
    # )

    # spawnJointStateAfterRobot = RegisterEventHandler(
    #     OnProcessExit(
    #         target_action=spawnNode,
    #         on_exit=[jointStateBroadcasterSpawner],
    #     )
    # )

    # spawnDiffDriveAfterJSB = RegisterEventHandler(
    #     OnProcessExit(
    #         target_action=jointStateBroadcasterSpawner,
    #         on_exit=[diffDriveSpawner],
    #     )
    # )

    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "--ros-args",
            "-p",
            f"config_file:={bridge_params}",
        ],
    )

    launchDescriptionObject = LaunchDescription()
    launchDescriptionObject.add_action(gazebolaunch)
    launchDescriptionObject.add_action(nodeRobotStatePublisher)
    launchDescriptionObject.add_action(spawnNode)
    launchDescriptionObject.add_action(ros_gz_bridge)
    # launchDescriptionObject.add_action(spawnJointStateAfterRobot)
    # launchDescriptionObject.add_action(spawnDiffDriveAfterJSB)

    return launchDescriptionObject
