#!/usr/bin/env bash
set -euo pipefail
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source /opt/ros/humble/setup.bash
cd "$WS"
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install "mujoco>=3.1,<4" numpy pyyaml
rosdep install --from-paths src --ignore-src -r -y || true
colcon build --symlink-install
cat <<MSG
[DROK ARM SIM SETUP COMPLETE]
Next:
  source $WS/tools/source_env.sh
  bash $WS/tools/run_sim.sh
MSG
