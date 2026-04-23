#!/bin/bash
# NVIDIA GPU Fan Control - Manual execution script
# Run this script to manually start the fan controller (without systemd)

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Change to script directory
cd "$SCRIPT_DIR"
# Activate virtual environment and run the controller
source ./.venv/bin/activate
python ./nvidia_fan_control.py