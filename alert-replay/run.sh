#!/bin/bash

if test ! -d .venv; then
    echo "Preparing virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

python find_metagames.py $1 $2 $3 $4
