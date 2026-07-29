import os
import xacro
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Path to your xacro file
    pkg_share = get_package_share_directory('fairino_description')
    xacro_file = os.path.join(pkg_share, 'urdf_dual_arms', 'fairino3_dual_arms.urdf.xacro')

    # Process xacro → URDF
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = robot_description_config.toxml()

    # RViz config file (optional, you can create one in your package)
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'display.rviz')

    return LaunchDescription([
        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),

        # Joint State Publisher GUI (optional, for manual joint sliders)
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            parameters=[os.path.join(pkg_share, 'config', 'initial_positions.yaml')],
            output='screen'
        ),

        # RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_file],
            output='screen'
        ),
    ])
