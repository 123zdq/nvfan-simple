#!/bin/bash
set -e

# 拉取代码并设置/更新 Python 环境（无需 sudo）

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 拉取远程更新（仅在 git 仓库内有效）
if git rev-parse --git-dir > /dev/null 2>&1; then
    git fetch origin 2>/dev/null || true
    if ! git diff --quiet HEAD origin/main 2>/dev/null; then
        echo "Repository has updates, pulling latest changes..."
        git pull origin main
    fi
fi

# 创建虚拟环境或更新依赖
if [ ! -d ".venv" ]; then
    echo "Setting up Python environment..."
    uv venv --seed --python 3.12
    source ./.venv/bin/activate
    uv pip install nvidia-ml-py
    echo "Environment setup complete"
else
    echo "Virtual environment already exists. Updating dependencies..."
    source ./.venv/bin/activate
    uv pip install --upgrade nvidia-ml-py
    echo "Dependencies updated"
fi

echo "Update complete. Run 'sudo bash service_setup.sh' to update systemd service."
