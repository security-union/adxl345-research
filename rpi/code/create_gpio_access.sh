#!/bin/bash

# Define the udev rule path
UDEV_RULE_PATH="/etc/udev/rules.d/99-gpio.rules"

# Define the udev rule content
UDEV_RULE='SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c '\''chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio; chown -R root:gpio /dev/gpiochip* && chmod -R 770 /dev/gpiochip*'\''"'

# Function to create a gpio group and add the current user
setup_gpio_group() {
    echo "Creating gpio group..."
    sudo groupadd gpio || echo "Group gpio already exists."
    echo "Adding the current user to the gpio group..."
    sudo usermod -aG gpio $USER
}

# Function to create the udev rule for GPIO access
create_udev_rule() {
    echo "Creating udev rule for GPIO access..."
    echo $UDEV_RULE | sudo tee $UDEV_RULE_PATH > /dev/null
}

# Main function to setup GPIO access
setup_gpio_access() {
    setup_gpio_group
    create_udev_rule
    echo "Reloading udev rules..."
    sudo udevadm control --reload-rules && sudo udevadm trigger
    echo "Setup complete. Please reboot for changes to take effect."
}

# Execute the main function
setup_gpio_access
