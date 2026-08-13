#!/usr/bin/env bash
set -e
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source /opt/ros/humble/setup.bash
if [ -f "$WS/.venv/bin/activate" ]; then source "$WS/.venv/bin/activate"; fi
if [ -f "$WS/install/setup.bash" ]; then source "$WS/install/setup.bash"; fi
export DROK_ARM_SIM_WS="$WS"
echo "[DROK ARM SIM ENV READY]"
echo "WS=$WS"
