#!/bin/bash
if [[ $# -ne 1 ]]; then
    echo "Usage: nuke-alert.sh <ps2alerts instance id>"
    exit 1
fi

if test ! -d .venv; then
    echo "Preparing virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

python nuke-alert.py $1
