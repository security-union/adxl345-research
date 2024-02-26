#!/bin/bash

./create_gpio_access.sh

# Update package list and upgrade all your packages
sudo apt-get update

# Install Python3 and pip if they are not installed
sudo apt-get install -y python3 python3-pip

# Install system dependencies for GPIO and SPI interface
sudo apt-get install -y python3-dev i2c-tools

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt


