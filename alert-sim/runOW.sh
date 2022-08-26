#!/bin/sh

if [[ ! -d .venv ]]; then
    echo "Preparing virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirments.txt
else
    source .venv/bin/activate
fi

python outfit-wars-match.py
