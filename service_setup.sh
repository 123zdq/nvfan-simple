#!/bin/bash
set -e

# 安装/更新 systemd 服务（需要 sudo）

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 生成服务文件并安装
echo "Installing/updating systemd service..."
sed "s|%SCRIPT_DIR%|$SCRIPT_DIR|g" "service.template" | sudo tee "/etc/systemd/system/nvfan-simple.service" > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable nvfan-simple
sudo systemctl restart nvfan-simple
sudo systemctl status nvfan-simple

echo "Service setup complete."
