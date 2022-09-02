#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Usage: runOWMatches.sh <service-id> <world>"
    exit 1
fi

if [[ ! -d .venv ]]; then
    echo "Preparing virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

python outfitwar_dispatcher.py $1 $2
