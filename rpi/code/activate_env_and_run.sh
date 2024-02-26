#!/bin/bash

source .venv/bin/activate

if [ -z "$1" ]; then
    echo "Usage: $0 <python_script>"
    exit 1
fi

echo "Running $1"

sudo python3 $1