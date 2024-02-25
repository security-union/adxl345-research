#!/bin/bash

# Update package list and upgrade all your packages
sudo apt-get update

# Install Python3 and pip if they are not installed
sudo apt-get install -y python3 python3-pip

# Install system dependencies for GPIO and SPI interface
sudo apt-get install -y python3-dev python3-rpi.gpio

# Use pip to install Python dependencies directly with apt
sudo apt install -y python3-spidev python3-RPi.GPIO
