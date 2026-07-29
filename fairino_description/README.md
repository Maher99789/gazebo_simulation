```mermaid
    subgraph Gazebo
      World[Empty World]
      Robot[dual_arms URDF + gz_ros2_control plugin]
      JointStatePublisher[Joint State Publisher]
    end

    subgraph ROS2
      ControllerManager[Controller Manager]
      Controllers[Trajectory / DiffDrive Controllers]
      Topics[/cmd_vel, /joint_states]
    end

    World --> Robot
    Robot --> JointStatePublisher
    Robot --> ControllerManager
    ControllerManager --> Controllers
    Controllers --> Topics
    JointStatePublisher --> Topics

    subgraph Bridge
      IgnitionTopics[ignition.msgs.*]
      Ros2Topics[geometry_msgs / sensor_msgs]
    end

    Topics <--> Bridge
    IgnitionTopics <--> Bridge
```
🔎 Bridge Testing

ign topic -e -t /chatter 
Shows messages published inside Gazebo’s Ignition Transport layer.
Useful to confirm Gazebo is producing data.

ros2 topic echo /chatter  
Shows messages on the ROS 2 DDS layer.
Useful to confirm the bridge forwards Ignition messages into ROS 2.

Difference:
    ign topic -e -t /chatter → Gazebo side.
    ros2 topic echo /chatter → ROS 2 side.
    Seeing the same message on both confirms the bridge is functional.

ign topic -l  
Lists all active Ignition Transport topics inside Gazebo.
Useful for discovering what Gazebo is publishing.

ros2 topic list  
Lists all active ROS 2 topics.
Useful for discovering what ROS 2 nodes are publishing/subscribing.

⚙️ Controller Integration

    The gz_ros2_control plugin is added to the URDF.

    It loads a YAML configuration file (rrbot_controllers.yaml) that defines:

        joint_state_broadcaster (publishes joint states).

        rrbot_controller (controls joints defined in URDF).

    When Gazebo spawns the robot, the plugin starts a controller manager.

    The controller manager reads joints from the URDF and exposes them as ROS 2 interfaces.

🚀 Launch File Workflow

A launch file is used to run multiple nodes at once:

    Gazebo simulation (spawns RRBot).

    ros_gz_bridge (connects Ignition ↔ ROS 2 topics).

    controller_manager (loads controllers from YAML).

This ensures the entire pipeline starts with a single command.


✅ State Flow Summary

    Gazebo loads RRBot with the gz_ros2_control plugin.

    Controller Manager reads joints from URDF and YAML.

    Controllers expose ROS 2 topics (/cmd_vel, /joint_states).

    Bridge connects Ignition topics ↔ ROS 2 topics.

    Tests:

        ign topic -e -t /chatter ↔ ros2 topic echo /chatter → confirms bridge.

        ign topic -l ↔ ros2 topic list → shows available topics.

        ros2 control list_controllers → shows active controllers.

        ros2 topic pub /cmd_vel ... → moves the robot in Gazebo.

# Bridge Verification

4.1. Run the Bridge
ros2 run ros_gz_bridge parameter_bridge / chatter@std_msgs / msg /
String@ignition . msgs . StringMsg

4.2. Publish a ROS 2 Message
```bash
ros2 topic pub / chatter std_msgs / msg / String " data : ␣ ’ Hello ␣ Gazebo ␣ Ignition ’ "
-- once
```

4.3. Echo the Topic
• ROS 2 side:
```bash
ros2 topic echo / chatter
```
Shows payloads in ROS 2 DDS.

• Gazebo side:
```bash
ign topic -e -t / chatter
```
Shows payloads in Gazebo Transport.

# Controllers verification 
1.run gazebo launch
```bash
ros2 launch fairino_description gazebo.launch.py 
```
this what shell log 

```bash
[ign gazebo-1] [INFO] [1785315557.832028303] [gz_ros2_control]: Loading controller_manager
[ign gazebo-1] [INFO] [1785315558.033447816] [controller_manager]: Loading controller 'left_arm_controller'
[spawner-6] [INFO] [1785315558.046366343] [spawner_left_arm_controller]: Loaded left_arm_controller
[ign gazebo-1] [INFO] [1785315558.047178939] [controller_manager]: Loading controller 'right_arm_controller'
[ign gazebo-1] [INFO] [1785315558.052485529] [controller_manager]: Loading controller 'joint_state_broadcaster'
[spawner-7] [INFO] [1785315558.053656608] [spawner_right_arm_controller]: Loaded right_arm_controller
[ign gazebo-1] [INFO] [1785315558.071350045] [controller_manager]: Configuring controller 'left_arm_controller'
[spawner-5] [INFO] [1785315558.072402989] [spawner_joint_state_broadcaster]: Loaded joint_state_broadcaster
[ign gazebo-1] [INFO] [1785315558.073141882] [left_arm_controller]: configure successful
[ign gazebo-1] [INFO] [1785315558.073456857] [controller_manager]: Configuring controller 'right_arm_controller'
[ign gazebo-1] [INFO] [1785315558.074009515] [right_arm_controller]: configure successful
[ign gazebo-1] [INFO] [1785315558.074128614] [controller_manager]: Configuring controller 'joint_state_broadcaster'
[ign gazebo-1] [INFO] [1785315558.074182488] [joint_state_broadcaster]: 'joints' or 'interfaces' parameter is empty. All available state interfaces will be published
[ign gazebo-1] [WARN] [1785315558.185315798] [gz_ros2_control]:  Desired controller update period (0.01 s) is slower than the gazebo simulation period (0.001 s).
[ign gazebo-1] [INFO] [1785315558.197403486] [left_arm_controller]: activate successful
[spawner-6] [INFO] [1785315558.210264095] [spawner_left_arm_controller]: Configured and activated left_arm_controller
[ign gazebo-1] [INFO] [1785315558.224041474] [right_arm_controller]: activate successful
[spawner-7] [INFO] [1785315558.249175826] [spawner_right_arm_controller]: Configured and activated right_arm_controller
[spawner-5] [INFO] [1785315558.300156124] [spawner_joint_state_broadcaster]: Configured and activated joint_state_broadcaster
[INFO] [spawner-6]: process has finished cleanly [pid 10869]
[INFO] [spawner-7]: process has finished cleanly [pid 10871]
[INFO] [spawner-5]: process has finished cleanly [pid 10867]
```

When launching with a controller‑enabled description, the log shows:

    Controller manager is loaded.

    Controllers (left_arm_controller, right_arm_controller, joint_state_broadcaster) are loaded, configured, and activated.

    Warnings may appear if the desired update period is slower than Gazebo’s simulation period, but controllers still activate successfully.

    Each spawner process reports clean completion once controllers are active.

2.joint states
To verify that joint states are being published:
```bash
ros2 topic echo \joint_states
```
This displays the current positions, velocities, and efforts for all joints in both arms. The output confirms that the joint_state_broadcaster is active and publishing data from Gazebo into ROS 2. 

```bash
---
header:
  stamp:
    sec: 180
    nanosec: 800000000
  frame_id: base_link
name:
- left_joint5
- left_joint4
- left_joint6
- right_joint1
- right_joint2
- right_joint3
- right_joint4
- left_joint1
- left_joint2
- left_joint3
- right_joint5
- right_joint6
position:
- 1.0277304319816621e-16
- 2.7273592117631175e-15
- -9.39723889476036e-14
- -1.964762640319587e-19
- 3.443290829930981e-12
- 7.777454721307638e-12
- 2.5989535628814997e-15
- 1.7069704063053744e-19
- -3.4431828682197297e-12
- -7.77683095641712e-12
- -3.3140714780004693e-18
- -9.39743041383492e-14
velocity:
- -4.686209780684417e-19
- 6.938893903907228e-18
- 6.579751934271405e-18
- -1.1092425839887097e-18
- -3.387284756069947e-18
- 6.938893903907228e-18
- -6.938893903907228e-18
- -3.848176558494693e-19
- -1.1750464560785281e-18
- 0.0
- -5.250651360911001e-18
- 9.595189226496714e-18
effort:
- -4.6018576079113795e-06
- -0.000404979431802205
- 0.0003991103864256372
- 2.1708130949147633e-15
- -12.92974941867607
- -12.929997133461272
- -0.0003861092013439923
- 2.3843077175064742e-14
- 12.92945375858337
- 12.929206043639704
- -1.4275046022152795e-09
- 0.0003991111181387646
```
3. Send Position Commands
With the controllers active, you can send position commands directly to the arms.

    Left Arm Controller  
    Publish a Float64MultiArray with six values (one per joint):
```bash
ros2 topic pub /left_arm_controller/commands std_msgs/msg/Float64MultiArray "{
  data: [0.0, -1.57, 1.57, 0.0, 0.5, -0.5]
}" --once
```
This command sets the six joints of the left arm to the specified positions in radians. The controller applies them immediately, and the updated positions can be observed on /joint_states.

```bash
header:
  stamp:
    sec: 538
    nanosec: 810000000
  frame_id: base_link
name:
- left_joint5
- left_joint4
- left_joint6
- right_joint1
- right_joint2
- right_joint3
- right_joint4
- left_joint1
- left_joint2
- left_joint3
- right_joint5
- right_joint6
position:
- 0.5000000001160025
- -0.0028827798747943886
- -0.5000000000000944
- -1.9094603885889098e-19
- 3.4432908429783074e-12
- 7.777454721316434e-12
- 2.5989188684033493e-15
- -1.13287901811063e-12
- -1.56655469808294
- 1.5700000002788232
- -3.334556016917782e-18
- -9.397430569011221e-14
```