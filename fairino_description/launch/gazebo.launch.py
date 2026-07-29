import os
import xacro
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('fairino_description')
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim')
    
    xacro_file = os.path.join(pkg_share, 'urdf_dual_arms', 'fairino3_dual_arms.urdf.xacro')

    # Process Xacro to URDF
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {"robot_description": robot_description_config.toxml()}

    # 1. Ignition Gazebo Launch
    # Fortress uses the 'ign_gazebo.launch.py' or 'gz_sim.launch.py'
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(), # -r starts simulation immediately
    )

    # 2. Robot State Publisher
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[robot_description],
    )

    # 3. Spawn Entity in Ignition
    # Note: Ignition uses 'create' instead of 'spawn_entity.py'
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'fairino_dual_arms',
            '-topic', 'robot_description',
        ],
        output='screen',
    )

    # 4. ROS-GZ Bridge (Essential for communication)
    # This maps Ignition topics (like clock) to ROS 2 topics
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        output='screen'
    )

    # 5. Controller Spawners
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    left_arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_arm_controller"],
    )

    right_arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["right_arm_controller"],
    )

    return LaunchDescription([
        gazebo,
        bridge,
        rsp,
        spawn,
        joint_state_broadcaster_spawner,
        left_arm_controller_spawner,
        right_arm_controller_spawner
    ])