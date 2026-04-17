# third_webots_pkg
This is an example webots diffdrive robot that has Lidar and IMU capability. 

The wheels don't have hall sensors on purpose, this is for me to test SLAM with
dead reckoning and some sensors, as well as other robot configurations. I will
probably add the hall sensors back someday. With this robot body I have a good
deal of control over how to map which is nice.

---

Now that I've added SLAM, I find it definitely helps to just use hall sensors.
Will be important to know when buying stuff for IRL robot.

## Quickstart
Build normally with `colcon build` and `source install/local_setup.bash`.

Then launch the whole sim minus mapping with
`ros2 launch third_webots_pkg robot_launch.py`

In another terminal you can run mapping with 
`ros2 launch third_webots_pkg mapping_launch.py`

Or just
`ros2 launch third_webots_pkg full_stack.py`
for all of it

![Webots SLAM](webots_slam.png)


## Files
### `worlds/my_world.wbt`

Taken from building a world and robot file from an empty webots world and going
from there.

Currently the robot in this world has its URDF counterpart living in
`resource/robot_model.urdf`. Update it by running the world file in webots,
right click `Robot "my_robot"` in the scene tree on the left and select "Export
URDF". Save the new file and go into `launch/robot_launch.py` and update
`robot_model_path` with the correct path name along with updating `setup.py`.

See the lidar visuals by setting View > optional rendering > show lidar rays
there are by default 4 lidar ray layers, for 2D lidar we only need 1 so make
sure to set that.

### `resource/third_webots_robot.urdf`

This file hooks up the sensors (lidar and imu so far) to ros2 via the
webots_ros2_driver plugins

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

    <plugin type="webots_ros2_driver::Ros2IMU">
      <enabled>true</enabled>
      <updateRate>20</updateRate>
      <topicName>/imu</topicName>
      <alwaysOn>true</alwaysOn>
      <frameName>imu_link</frameName>
      <inertialUnitName>imu</inertialUnitName> <!-- Ensure this matches whats in robot_model.urdf -->
      <gyroName>gyro</gyroName>
      <accelerometerName>accelerometer</accelerometerName>
    </plugin>

    <plugin type="webots_ros2_control::Ros2Control" />
</webots>
```

This file also contains the necessary plugin information to integrate ros2
diffdrive controls directly with webots motors.

Many of the Hardware Interfaces necessary can be listed with this command after
running `robot_launch.py`

`ros2 service call /controller_manager/list_hardware_interfaces controller_manager_msgs/srv/ListHardwareInterfaces {}`

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

### `ros2control.yml`

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

    use_stamped_vel: false           # subscribe to cmd_vel that uses twist_vel (newer ros2 versions)
    base_frame_id: "base_link"       # frame of robot base
    odom_frame_id: "odom_unfiltered" # frame of odometry base
    enable_odom_tf: false      # publish to odom->base_link for rviz
    open_loop: true            # integrate wheel vels, like the one below kinda
    use_feedback: true         # integrate wheel vels, dont use the position feedback. key for getting dead reckoning
    
    pose_covariance_diagonal: [0.0002, 0.0002, 0.000, 0.000, 0.000, 0.001]
    twist_covariance_diagonal: [0.001, 0.000, 0.000, 0.000, 0.000, 0.001]

    linear:
      x:
        max_velocity: 0.15 # Maximal speed of robot

joint_state_broadcaster:
  ros__parameters:
    base_frame_id: base_link
```

The important parts are in diffdrive_controller for getting the names of what
diffdrive will be controlling, wheel separation, radius, covariance and such.
`open_loop` and `use_feedback` ensures diffdrive doesn't use the position sensor
that isn't actually publishing anything. This config above assumes dead
reckoning. Turn those two to false if you are going to use hall sensors.

Notice odom_frame_id is not just odom, this is because we will publish real odom
in `/ekf_filter_node`. This is just where we publish raw odometery. So we set
`enable_odom_tf` to false. Set it to true if you get rid of ekf and want to roll
with pure odom again.

### `ekf.yml`
The config for the ekf_filter_node goes, see [robot_localization's example
ekf.yaml](https://github.com/cra-ros-pkg/robot_localization/blob/rolling-devel/params/ekf.yaml)
for what each config does.

The important things to remember are that this node is where tf for odom to base
link is published, both must not be messed with.

`process_noise_covariance` is the hardest to configure for especially if you
dont have the sensor or odom errors for the actual parts you are using. That's a
problem with webots it seems.

### `mapper_params_online_async.yaml`
Config for online async SLAM. See [slam_toolbox's
docs](https://github.com/SteveMacenski/slam_toolbox?tab=readme-ov-file#configuration)
for more examples.

I didn't mess with this much, just with min and max laser range.