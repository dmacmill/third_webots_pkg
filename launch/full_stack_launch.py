import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)
    package_dir = get_package_share_directory('third_webots_pkg')

    # Include robot_launch.py
    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(package_dir, 'launch', 'robot_launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # Include mapping_launch.py
    mapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(package_dir, 'launch', 'mapping_launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # Launch RViz2
    rviz_config_path = os.path.join(package_dir, 'rviz', 'default.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        # arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        robot_launch,
        mapping_launch,
        rviz_node
    ])
