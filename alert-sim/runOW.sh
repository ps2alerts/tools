#!/bin/bash

# Edit these values to adjust scenarios
RED_OUTFIT="37581466630125066"  # LCOF
BLUE_OUTFIT="37575759950005295" # TTA
WORLD="1"
CAPTURE_RATE="5"
DEATH_RATE="1.0" # seconds per death
DEATH_DELAY="0.0"

if [[ ! -d .venv ]]; then
    echo "Preparing virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

python outfit-wars-match.py $1 -r $RED_OUTFIT -b $BLUE_OUTFIT -w $WORLD -c $CAPTURE_RATE -d $DEATH_RATE -l $DEATH_DELAY
