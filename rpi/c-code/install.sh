#!/bin/bash


sudo apt install unzip

# Install pigpio
wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
pushd pigpio-master
make
sudo make install
popd

# Install https://github.com/nagimov/adxl345spi
sudo apt-get update
git clone https://github.com/nagimov/adxl345spi
pushd adxl345spi
sudo make
sudo make install
popd