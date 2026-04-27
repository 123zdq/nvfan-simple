#!/bin/bash

# 卸载 systemd 服务：停止、禁用、删除

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 如果服务正在运行则停止
if systemctl is-active --quiet nvfan-simple; then
    echo "Stopping service: nvfan-simple..."
    sudo systemctl stop nvfan-simple
    echo "Service stopped"
fi

# 如果服务已启用开机自启则禁用
if systemctl is-enabled --quiet nvfan-simple; then
    echo "Disabling service: nvfan-simple..."
    sudo systemctl disable nvfan-simple
    echo "Service disabled"
fi

# 删除服务文件
sudo rm -f "/etc/systemd/system/nvfan-simple.service"
echo "Removed service file: /etc/systemd/system/nvfan-simple.service"

# 重载 systemd 配置
echo "Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "Complete: Service stopped and uninstalled"