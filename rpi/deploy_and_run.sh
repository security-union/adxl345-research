#!/bin/bash

# Configuration variables
PI_IP="192.168.0.194" # Change this to your Pi's IP address or hostname
PI_USER="ubuntu" # Change this to your Pi's username
LOCAL_PROJECT_DIR="./code" # Local project directory to sync
PI_PROJECT_DIR="/home/ubuntu/accelerometers" # Destination directory on Pi
MAIN_PY_SCRIPT="activate_env_and_run.sh" # Python script to run

# Add help message
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "Usage: $0 --program <python-program-to-run> [--install]"
    echo "Syncs code to Raspberry Pi, installs dependencies, and runs program."
    echo "Optional argument 'install' installs dependencies."
    exit 0
fi

# Add argument to determine --program <program> to run, it is mandatory
if [ "$1" == "--program" ]; then
    MAIN_PY_SCRIPT="${MAIN_PY_SCRIPT} $2"
else 
    echo "Usage: $0 --program <python-program-to-run> [--install]"
    echo "Error: No program specified."
    exit 1
fi

# Add argument to optionally install dependencies
if [ "$3" == "--install" ]; then
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
ssh $PI_USER@$PI_IP "cd $PI_PROJECT_DIR/code && sudo -S ./$MAIN_PY_SCRIPT"
