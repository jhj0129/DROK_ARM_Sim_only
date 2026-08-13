# DROK_ARM_Sim_only

DROK ARM용 **ROS 2 Humble + MuJoCo 독립 시뮬레이션 워크스페이스**입니다.

이 저장소의 목적은 실제 로봇이 없는 환경에서도 DROK ARM의 새로운 제어 코드, 통신 구조, 궤적 생성기, IK 기반 제어 등을 바로 개발하고 검증할 수 있는 **바닐라 시뮬레이션 베이스**를 제공하는 것입니다.

특정 작업용 예제나 잡기 데모를 포함하지 않으며, 로봇 모델 / 기구학 / MuJoCo / ROS 2 통신 계층을 기본 환경으로 제공합니다.

---

## 1. Current verified status

현재 Ubuntu + ROS 2 Humble 환경에서 다음 항목을 확인했습니다.

- `drok_arm_description` 빌드 성공
- `drok_arm_kinematics` 빌드 성공
- `drok_arm_mujoco` 빌드 성공
- MuJoCo 3.4.0 실행 확인
- MuJoCo Viewer 실행 확인
- DROK ARM HOME 자세 스폰 확인
- ROS 2 simulation backend 실행 확인
- `/joint_states` feedback interface 제공
- 실제 팔과 호환되는 arm/gripper action interface 제공
- `ARM_BASE_LINK` world Z = 1.0 m 적용
- `gripper_tcp` local +X 0.05 m TCP 보정 적용

현재 기준 OS / middleware:

```text
Ubuntu
ROS 2 Humble
Python 3.10
MuJoCo 3.4.0
```

Wayland 환경에서 다음 GLFW warning이 출력될 수 있습니다.

```text
Wayland: The platform does not provide the window position
```

Viewer가 정상적으로 열리는 경우 이 warning은 시뮬레이션 실행 자체에는 영향을 주지 않습니다.

---

## 2. Repository purpose

이 저장소는 application-specific controller가 아니라 **DROK ARM의 가상 하드웨어 및 기본 개발환경**입니다.

구조는 다음과 같습니다.

```text
New Controller / IK / RC / Teleoperation / VLA / Trajectory
                         |
                         v
                ROS 2 command interface
                         |
                         v
                DROK ARM MuJoCo Bridge
                         |
                         v
                      MuJoCo
                         |
                         v
                    /joint_states
```

따라서 앞으로 새로운 로봇 동작 코드를 작성할 때 실제 팔을 연결하지 않고도 먼저 이 환경에서 동작을 검증할 수 있습니다.

---

## 3. Included

이 저장소에는 다음 기능이 포함됩니다.

- DROK ARM robot description
- robot meshes
- MuJoCo model
- ROS 2 ↔ MuJoCo bridge
- JOINT1 ~ JOINT6 arm joints
- gripper joint interface
- joint state feedback
- arm trajectory action interface
- gripper action interface
- direct joint command interface
- reusable FK / IK kinematics library
- calibrated HOME pose
- gripper TCP correction
- standalone setup / build / run scripts

특정 작업을 위한 다음 기능들은 의도적으로 포함하지 않습니다.

```text
grasp practice
supply_box sequence
YOLO
camera perception
autonomous grasp sequence
specific IK target example
application-specific trajectory example
vehicle integration
```

---

## 4. Geometry baseline

### ARM base

MuJoCo world에서 DROK ARM의 base는 지면에서 1 m 위에 고정됩니다.

```text
ARM_BASE_LINK world position

X = 0.0 m
Y = 0.0 m
Z = 1.0 m
```

로봇 내부의 FK / IK 계산은 계속 `ARM_BASE_LINK` 기준으로 수행되므로 world의 1 m spawn offset은 로봇 내부 기구학 좌표에 직접 더하지 않습니다.

### TCP

현재 실물 측정 결과를 반영한 TCP 보정값:

```text
gripper_tcp
=
gripper_center + [0.05, 0.0, 0.0] m
```

즉 gripper local +X 방향으로 5 cm 보정되어 있습니다.

설정 파일:

```text
config/arm_config.yaml
```

---

## 5. HOME pose

현재 calibrated HOME pose:

```yaml
JOINT1: -0.000001628
JOINT2:  0.297361544
JOINT3:  0.296742637
JOINT4: -0.000030712
JOINT5:  0.000061231
JOINT6:  0.000102331
```

대략적인 degree 값:

```text
JOINT1 =  0 deg
JOINT2 = 17 deg
JOINT3 = 17 deg
JOINT4 =  0 deg
JOINT5 =  0 deg
JOINT6 =  0 deg
```

MuJoCo는 이 HOME 자세를 기본 기준 자세로 사용합니다.

---

## 6. Clone

```bash
cd ~

git clone https://github.com/jhj0129/DROK_ARM_Sim_only.git

cd ~/DROK_ARM_Sim_only
```

---

## 7. Initial setup

최초 한 번:

```bash
cd ~/DROK_ARM_Sim_only

bash tools/setup.sh
```

또는 직접 빌드할 경우 반드시 **워크스페이스 디렉토리 안에서** 실행합니다.

```bash
cd ~/DROK_ARM_Sim_only

source /opt/ros/humble/setup.bash

colcon build --symlink-install
```

주의:

```bash
cd ~
colcon build --symlink-install
```

처럼 HOME 디렉토리에서 실행하면 안 됩니다.

`colcon`이 홈 디렉토리 아래의 다른 ROS workspace, backup directory, Python package 등을 함께 탐색하면서 duplicate package error가 발생할 수 있습니다.

---

## 8. Build check

```bash
cd ~/DROK_ARM_Sim_only

source /opt/ros/humble/setup.bash
source ~/DROK_ARM_Sim_only/install/setup.bash

ros2 pkg list | grep drok_arm
```

정상 예:

```text
drok_arm_description
drok_arm_kinematics
drok_arm_mujoco
```

MuJoCo package 확인:

```bash
ros2 pkg prefix drok_arm_mujoco
```

정상 예:

```text
/home/<USER>/DROK_ARM_Sim_only/install/drok_arm_mujoco
```

---

## 9. Run simulation

### Terminal 1 — MuJoCo simulation

```bash
source ~/DROK_ARM_Sim_only/tools/source_env.sh

bash ~/DROK_ARM_Sim_only/tools/run_sim.sh
```

정상 실행 시 MuJoCo Viewer가 열리고 simulation backend에서 다음 interface를 제공합니다.

```text
Action  : /arm_controller/follow_joint_trajectory
Action  : /gripper_controller/gripper_cmd
Direct  : /drok_arm/joint_command
Feedback: /joint_states
```

---

## 10. Feedback check

### Terminal 2

```bash
source ~/DROK_ARM_Sim_only/tools/source_env.sh

ros2 topic echo /joint_states --once
```

이 topic은 MuJoCo 내부 로봇의 joint feedback을 제공합니다.

---

## 11. HOME command

```bash
source ~/DROK_ARM_Sim_only/tools/source_env.sh

bash ~/DROK_ARM_Sim_only/tools/go_home.sh
```

Simulation에서는 JOINT1 ~ JOINT6을 calibrated `HOME_Q`로 이동시킵니다.

실제 팔의 power-cycle 문제를 처리하기 위한 JOINT1 HOLD 예외는 Sim-only HOME에는 적용하지 않습니다.

---

## 12. ROS 2 interfaces

### Arm trajectory

```text
/arm_controller/follow_joint_trajectory
```

실제 팔 제어 프로그램과의 호환을 위한 arm trajectory action endpoint입니다.

### Gripper

```text
/gripper_controller/gripper_cmd
```

gripper action endpoint입니다.

### Direct joint command

```text
/drok_arm/joint_command
```

저수준 또는 새로운 제어기 개발 시 사용할 수 있는 direct joint command interface입니다.

### Joint feedback

```text
/joint_states
```

MuJoCo 내부 joint 상태를 ROS 2로 제공합니다.

상세 interface는 다음 문서를 참고합니다.

```text
docs/INTERFACE.md
```

---

## 13. Kinematics

Reusable FK / IK library:

```text
src/drok_arm_kinematics
```

이 패키지는 앞으로 다른 controller에서 재사용하기 위한 기구학 라이브러리입니다.

포함 목적:

```text
FK
IK
robot geometry
joint limits
TCP geometry
```

이 저장소에서는 특정 물체를 잡는 IK 예제, 특정 Cartesian target, 연습 trajectory를 기본 기능으로 제공하지 않습니다.

---

## 14. Workspace structure

```text
DROK_ARM_Sim_only/
├── README.md
├── .gitignore
│
├── config/
│   └── arm_config.yaml
│
├── docs/
│   └── INTERFACE.md
│
├── src/
│   ├── drok_arm_description/
│   ├── drok_arm_kinematics/
│   └── drok_arm_mujoco/
│
└── tools/
    ├── setup.sh
    ├── source_env.sh
    ├── run_sim.sh
    └── go_home.sh
```

`build/`, `install/`, `log/`, `__pycache__/`, virtual environment 등의 생성 파일은 Git에 포함하지 않습니다.

---

## 15. Development concept

향후 새로운 controller는 가능한 한 simulation과 real robot에서 동일한 상위 명령 구조를 사용할 수 있도록 개발합니다.

```text
                Controller
                    |
              ROS 2 interface
                    |
        +-----------+-----------+
        |                       |
        v                       v
   MuJoCo Bridge             Real Bridge
        |                       |
      MuJoCo                  RMD / CAN
        |                       |
   Simulation                 Real ARM
```

이를 통해 다음과 같은 개발 순서를 목표로 합니다.

```text
1. Controller 작성
2. DROK_ARM_Sim_only에서 검증
3. 동일한 상위 명령 구조로 실제 로봇 연결
```

---

## 16. Current scope

현재 저장소는 **DROK ARM simulation / communication / kinematics baseline**입니다.

새로운 로봇 동작을 구현할 때 이 저장소 자체에 특정 task logic을 계속 추가하기보다는, 이 workspace의 interface와 kinematics library를 기반으로 별도의 controller 또는 application package를 작성하는 것을 기본 방향으로 합니다.
