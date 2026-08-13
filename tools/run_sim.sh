#!/usr/bin/env bash

WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=============================================="
echo " DROK ARM MuJoCo SIM DEBUG"
echo " WS = $WS"
echo "=============================================="

source /opt/ros/humble/setup.bash

if [ -f "$WS/.venv/bin/activate" ]; then
    source "$WS/.venv/bin/activate"
fi

if [ -f "$WS/install/setup.bash" ]; then
    source "$WS/install/setup.bash"
fi

echo
echo "[1] ROS2:"
which ros2 || true

echo
echo "[2] Python:"
which python3 || true
python3 --version || true

echo
echo "[3] MuJoCo:"
python3 -c "import mujoco; print('mujoco =', mujoco.__version__)" || true

echo
echo "[4] ROS package:"
ros2 pkg prefix drok_arm_mujoco || true

echo
echo "[5] Starting MuJoCo node..."
echo

ros2 run drok_arm_mujoco mujoco_node

RET=$?

echo
echo "=============================================="
echo " MuJoCo node stopped"
echo " EXIT CODE = $RET"
echo "=============================================="
echo
read -rp "오류 확인 후 Enter를 누르세요..."

exit 0
