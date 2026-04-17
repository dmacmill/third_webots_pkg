import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)
    package_dir = get_package_share_directory('third_webots_pkg')

    slam_toolbox_params_path = os.path.join(package_dir, 'config', 'mapper_params_online_async.yaml')
    online_async_share = PathJoinSubstitution([
        FindPackageShare('slam_toolbox'),
        'launch',
        'online_async_launch.py'
    ])
    online_async_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(online_async_share),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_toolbox_params_path
        }.items()
    )


    return LaunchDescription([
        online_async_launch
    ])