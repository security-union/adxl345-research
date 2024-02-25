#!/bin/bash

# Configuration variables
PI_IP="192.168.0.194" # Change this to your Pi's IP address or hostname
PI_USER="ubuntu" # Change this to your Pi's username
LOCAL_PROJECT_DIR="./code" # Local project directory to sync
PI_PROJECT_DIR="/home/ubuntu/accelerometers" # Destination directory on Pi
MAIN_PY_SCRIPT="main.py" # Python script to run

# Check for correct usage
if [ "$#" -ne 0 ]; then
    echo "Usage: $0"
    exit 1
fi

# Add argument to optionally install dependencies
if [ "$1" == "install" ]; then
    INSTALL_DEPENDENCIES=true
else
    INSTALL_DEPENDENCIES=false
fi

# Step 1: Sync code with Raspberry Pi
echo "Syncing code to Raspberry Pi..."
rsync -avz --exclude '.git/' --exclude 'env/' $LOCAL_PROJECT_DIR $PI_USER@$PI_IP:$PI_PROJECT_DIR

# Check if rsync was successful
if [ "$?" -ne 0 ]; then
    echo "Failed to sync files."
    exit 1
fi

# Step 2: Install dependencies
if [ "$INSTALL_DEPENDENCIES" = true ]; then
    echo "Installing dependencies on Raspberry Pi..."
    ssh $PI_USER@$PI_IP "cd $PI_PROJECT_DIR/code && sudo -S ./install_dependencies.sh"
fi

# Step 3: Run program and get output
echo "Running program on Raspberry Pi and fetching output..."
ssh $PI_USER@$PI_IP "sudo -S python3 $PI_PROJECT_DIR/code/$MAIN_PY_SCRIPT"
