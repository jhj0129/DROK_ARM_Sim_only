#!/usr/bin/env bash
set -euo pipefail
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$WS/tools/source_env.sh"
ros2 action send_goal --feedback /arm_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory "{trajectory: {joint_names: [JOINT1, JOINT2, JOINT3, JOINT4, JOINT5, JOINT6], points: [{positions: [-0.000001628, 0.297361544, 0.296742637, -0.000030712, 0.000061231, 0.000102331], time_from_start: {sec: 3, nanosec: 0}}]}}"
