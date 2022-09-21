#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: runOWReplay.sh <instance-id>"
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

SCRIPT_DIR=$( cd "${0%/*}" && pwd -P )

python outfitwar_match.py replay \
$SCRIPT_DIR/replay/files/$1/metagame_events.json \
$SCRIPT_DIR/replay/files/$1/facility_events.json \
$SCRIPT_DIR/replay/files/$1/death_events.json \
$SCRIPT_DIR/replay/files/$1/vehicle_destroy_events.json

