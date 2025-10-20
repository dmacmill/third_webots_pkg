import os
import launch
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from webots_ros2_driver.webots_launcher import WebotsLauncher
from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.wait_for_controller_connection import WaitForControllerConnection


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)

    package_dir = get_package_share_directory('third_webots_pkg')
    robot_description_path = os.path.join(package_dir, 'resource', 'third_webots_robot.urdf')
    robot_model_path = os.path.join(package_dir, 'resource', 'robot_model.urdf')
    ros2_control_params = os.path.join(package_dir, 'resource', 'ros2control.yml')
    use_twist_stamped = 'ROS_DISTRO' in os.environ and (os.environ['ROS_DISTRO'] in ['rolling', 'jazzy', 'kilted'])
    if use_twist_stamped:
        mappings = [('/diffdrive_controller/cmd_vel', '/cmd_vel'), ('/diffdrive_controller/odom', '/odom')]
    else:
        mappings = [('/diffdrive_controller/cmd_vel_unstamped', '/cmd_vel'), ('/diffdrive_controller/odom', '/odom')]

    webots = WebotsLauncher(
        world=os.path.join(package_dir, 'worlds', 'my_world.wbt'),
        ros2_supervisor=True
    )

    footprint_publisher = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments= ['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint'],
        name="base_to_footprint_publisher"
    )

    map_to_odom_publisher = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=["0", "0", "0", "0", "0", "0", "map", "odom"],
        name="map_to_odom_publisher"
    )

    # TF tree
    with open(robot_model_path, 'r') as f:
        robot_model = f.read()
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            'robot_description': robot_model
        }]
    )

    # ROS Control Spawners
    controller_manager_timeout = ['--controller-manager-timeout', '50']
    controller_manager_prefix = 'python.exe' if os.name == 'nt' else 'python3'
    diffdrive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        prefix=controller_manager_prefix,
        arguments=['diffdrive_controller'] + controller_manager_timeout
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable='spawner',
        output="screen",
        prefix=controller_manager_prefix,
        arguments=['joint_state_broadcaster'] + controller_manager_timeout,
    )

    ros_control_spawners = [diffdrive_controller_spawner, joint_state_broadcaster_spawner]
    # ros_control_spawners = [diffdrive_controller_spawner]

    # Spawn a robot
    my_robot_driver = WebotsController(
        robot_name='my_robot',
        parameters=[
            {'robot_description': robot_description_path,
             'use_sim_time': use_sim_time,
             'set_robot_state_publisher': True},
             ros2_control_params
        ],
        remappings=mappings,
        respawn=True
    )

    # nodes should wait for each other before proceeding
    waiting_nodes = WaitForControllerConnection(
        target_driver=my_robot_driver,
        nodes_to_start=ros_control_spawners
    )

    return LaunchDescription([
        webots,
        webots._supervisor,
        robot_state_publisher,
        footprint_publisher,
        map_to_odom_publisher,
        waiting_nodes,
        my_robot_driver,

        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=webots,
                on_exit=[launch.actions.EmitEvent(event=launch.events.Shutdown())],
            )
        )
    ])

