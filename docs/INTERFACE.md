# DROK ARM Simulation Interface

This repository is a vanilla simulation hardware workspace. It intentionally contains no grasp, YOLO, practice target, autonomous sequence, or application-specific controller.

## ROS 2 interfaces

- `/joint_states` (`sensor_msgs/msg/JointState`): JOINT1..JOINT6 + JOINT7 feedback.
- `/arm_controller/follow_joint_trajectory` (`control_msgs/action/FollowJointTrajectory`): same arm action endpoint used by the real DROK bridge.
- `/gripper_controller/gripper_cmd` (`control_msgs/action/GripperCommand`): same gripper action endpoint used by the real DROK bridge.
- `/drok_arm/joint_command` (`sensor_msgs/msg/JointState`): optional direct position command for controller development.
- `/drok_arm/sim_ready` (`std_msgs/msg/Bool`): simulator-ready heartbeat.

## Coordinate contract

- `ARM_BASE_LINK` is fixed at world `[0, 0, 1.0]` m.
- Robot FK/IK remains expressed relative to `ARM_BASE_LINK`; the 1 m world spawn offset is not added to IK targets.
- `gripper_tcp` is `+0.05 m` along local X from `gripper_center`.
