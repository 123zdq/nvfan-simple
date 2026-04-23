#!/bin/bash

# NVIDIA GPU Fan Control - Uninstallation script
# Stops, disables, and removes the systemd service

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stop the service if it's running
if systemctl is-active --quiet nvfan-simple; then
    echo "Stopping service: nvfan-simple..."
    sudo systemctl stop nvfan-simple
    echo "Service stopped"
fi

# Disable the service if it's enabled
if systemctl is-enabled --quiet nvfan-simple; then
    echo "Disabling service: nvfan-simple..."
    sudo systemctl disable nvfan-simple
    echo "Service disabled"
fi

# Remove the service file from systemd directory
sudo rm -f "/etc/systemd/system/nvfan-simple.service"
echo "Removed service file: /etc/systemd/system/nvfan-simple.service"

# Reload systemd configuration
echo "Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "Complete: Service stopped and uninstalled"