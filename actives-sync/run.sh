#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

if test ! -d "SCRIPT_DIR/.venv"; then
    echo "Preparing virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    source .venv/bin/activate
fi

python SyncActivesToDev.py
