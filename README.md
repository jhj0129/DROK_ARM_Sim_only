# DROK_ARM_Sim_only

Vanilla ROS 2 Humble + MuJoCo workspace for DROK ARM controller development without physical hardware.

## Scope

Included: synchronized DROK ARM MuJoCo model, ROS2 simulation bridge, joint feedback, real-compatible trajectory/gripper action endpoints, reusable FK/IK library, HOME pose, 5 cm TCP correction.

Not included: grasp practice, YOLO, camera logic, supply-box logic, autonomous sequences, example IK targets, or application-specific motion code.

## Geometry baseline

- `ARM_BASE_LINK` world spawn: `(0, 0, 1.0 m)` fixed in the air.
- `gripper_tcp`: `gripper_center + [0.05, 0, 0] m` in the local frame.
- HOME: approximately `[0, 17°, 17°, 0, 0, 0]` using the calibrated exact values in `config/arm_config.yaml`.

## Install once

```bash
cd ~
git clone https://github.com/jhj0129/DROK_ARM_Sim_only.git
cd ~/DROK_ARM_Sim_only
bash tools/setup.sh
```

## Run

Terminal 1:
```bash
source ~/DROK_ARM_Sim_only/tools/source_env.sh
bash ~/DROK_ARM_Sim_only/tools/run_sim.sh
```

The MuJoCo viewer opens and the simulator exposes the same primary ROS2 action endpoints as the real arm bridge.

Terminal 2, feedback check:
```bash
source ~/DROK_ARM_Sim_only/tools/source_env.sh
ros2 topic echo /joint_states --once
```

HOME:
```bash
bash ~/DROK_ARM_Sim_only/tools/go_home.sh
```

## Controller interface

Arm trajectory:
`/arm_controller/follow_joint_trajectory`

Gripper:
`/gripper_controller/gripper_cmd`

Feedback:
`/joint_states`

Optional direct joint command:
`/drok_arm/joint_command`

See `docs/INTERFACE.md`.

## Kinematics

`src/drok_arm_kinematics` contains only the reusable FK/IK library. No IK demo executable or practice target is included.
