#!/bin/bash
set -e

# NVIDIA GPU Fan Control - Update script
# Fetches updates and sets up Python environment (no sudo required)

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Fetch latest changes from remote repository (only if git repo)
if git rev-parse --git-dir > /dev/null 2>&1; then
    git fetch origin 2>/dev/null || true
    if ! git diff --quiet HEAD origin/main 2>/dev/null; then
        echo "Repository has updates, pulling latest changes..."
        git pull origin main
    fi
fi

# Check if virtual environment exists
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
