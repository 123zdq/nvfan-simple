#!/bin/bash
set -e
# 手动启动风扇控制器（不依赖 systemd）

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# GPU优化设置 2x3090
# 1. 开启 persistence mode
sudo nvidia-smi -pm 1 -i 0,1
# 2. 拉高功耗墙
sudo nvidia-smi -pl 380 -i 0,1
# 3. 提高目标温度
sudo nvidia-smi -gtt 88 -i 0,1

# 激活虚拟环境并运行
source ./.venv/bin/activate
python ./nvidia_fan_control.py