#!/bin/bash
set -e

# NVIDIA GPU Fan Control - Service setup script
# Installs and configures systemd service (requires sudo)

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install/update systemd service
echo "Installing/updating systemd service..."
sed "s|%SCRIPT_DIR%|$SCRIPT_DIR|g" "service.template" | sudo tee "/etc/systemd/system/nvfan-simple.service" > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable nvfan-simple
sudo systemctl restart nvfan-simple
sudo systemctl status nvfan-simple

echo "Service setup complete."
