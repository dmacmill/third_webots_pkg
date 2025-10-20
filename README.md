# third_webots_pkg

Adding lidar and rest of TF tree:

1. open webots without ros2. open the world for editing and add a Lidar node to the 
children in my_robot. save by clicking the icon on the screen or ctrl-shift-s

2. add a child shape to the lidar node. set that shapes geometry to cylinder, 
appearance to whatever. 

3. see the lidar vis by setting View > optional rendering > show lidar rays
there are by default 4 lidar ray layers, for 2D lidar we only need 1 so make sure 
to set that.

4. `third_webots_robot.urdf` setup the integration of the lidar next to the robot:

```xml
<webots>
    <device reference="top lidar" type="Lidar">
        <ros>
            <frameName>top lidar</frameName> <!-- Ensure matches whats in robot_model.urdf -->
            <enabled>true</enabled>
            <scanRate>10</scanRate>
            <topicName>~/scan</topicName>
            <alwaysOn>true</alwaysOn>
        </ros>
    </device>
    <plugin type="webots_ros2_control::Ros2Control" />
</webots>
```

5. below the webots tag in the same `third_webots_robot.urdf` file add what's necessary 
for the webots_controller node. This will add controllers that we can see with the 
command `ros2 service call /controller_manager/list_hardware_interfaces controller_manager_msgs/srv/ListHardwareInterfaces {}`

```xml
<ros2_control name="WebotsControl" type="system">
    <hardware>
        <plugin>webots_ros2_control::Ros2ControlSystem</plugin>
    </hardware>
    <joint name="right wheel motor">
        <state_interface name="position" /> <!-- still needed despite not having hall sensor-->
        <state_interface name="velocity"/>
        <command_interface name="velocity" />
    </joint>
    <joint name="left wheel motor">
        <state_interface name="position" />
        <state_interface name="velocity"/>
        <command_interface name="velocity" />
    </joint>
</ros2_control>
```

Notice that we also add the position interface despite not using hall sensors. 
This is necessary for diffdrive_controller to work, but we can still use dead 
reckoning by adjusting some settings below.

6. Add file `ros2control.yml` (don't forget to add in setup.py and launch.py!)

```yml
controller_manager:
  ros__parameters:
    update_rate: 50 # from webots WorldInfo basicTimeStep=20ms, 1/ts = 50hz

    diffdrive_controller:
      type: diff_drive_controller/DiffDriveController

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

diffdrive_controller:
  ros__parameters:
    left_wheel_names: ["left wheel motor"]
    right_wheel_names: ["right wheel motor"]

    wheel_separation: 0.09
    wheel_radius: 0.025

    # The real separation between wheels is not resulting in a perfect odometry
    # wheel_separation_multiplier: 1.112

    use_stamped_vel: false     # subscribe to cmd_vel that uses twist_vel (newer ros2 versions)
    base_frame_id: "base_link" # frame of robot base
    odom_frame_id: "odom"      # frame of odometry base
    enable_odom_tf: true       # publish to odom->base link for rviz
    open_loop: true            # integrate wheel vels, like the one below kinda
    use_feedback: true         # integrate wheel vels, dont use the position feedback. key for getting dead reckoning
    
    linear:
      x:
        max_velocity: 0.15 # Maximal speed of robot

joint_state_broadcaster:
  ros__parameters:
    base_frame_id: base_link
```

The important parts are in diffdrive_controller for getting the names of what 
diffdrive will be controlling, wheel separation and radius, open_loop and 
use_feedback to ensure diffdrive doesn't use the position sensor that isn't 
actually publishing anything. We will use dead reckoning. Turn these to false 
if you are going to use hall sensors.

7. Add this file to robot_launch.py, along with the nodes needed to launch 
the controller manager with the diffdrive controller.

