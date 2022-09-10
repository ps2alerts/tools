#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: runOW.sh <service-id>"
    exit 1
fi

# Edit these values to adjust scenarios
RED_OUTFIT="37570391403474491"  # UN17
BLUE_OUTFIT="37571208657592881" # HMRD
WORLD="1"
CAPTURE_RATE="60" # seconds between captures
DEATH_RATE="1.0" # seconds per death
DEATH_DELAY="30.0"

if [[ ! -d .venv ]]; then
    echo "Preparing virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

python outfitwars_match.py fake $1 -r $RED_OUTFIT -b $BLUE_OUTFIT -w $WORLD -c $CAPTURE_RATE -d $DEATH_RATE -l $DEATH_DELAY
