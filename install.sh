#!/bin/bash
# install.sh - Setup script for Secure Chat

echo "Installing dependencies..."

# Detect OS
if [ -f /etc/debian_version ]; then
    sudo apt update
    sudo apt install -y socat openssl python3 python3-pip python3-pyqt5
elif [ -f /etc/redhat-release ]; then
    sudo yum install -y socat openssl python3 python3-pip
fi

# Install python requirements
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p client/keys client/downloads client/uploads client/temp
mkdir -p server/logs server/pipes server/shared

# Set permissions
chmod +x server/server.sh
chmod +x server/handle_client.sh
chmod +x client/client.sh
chmod +x client/encryption/*.sh

echo "Setup complete. Run server/server.sh to start the backend."
