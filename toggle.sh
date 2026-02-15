#!/bin/bash

# Configuration
DIR="/mnt/windows/Projects/Programming/parakeet-dictation"
PID_FILE="/tmp/voicetype.pid"
VENV_PYTHON="$DIR/.venv/bin/python3"
SCRIPT="$DIR/voicetype.py"
LOG_FILE="/tmp/voicetype.log"

export DISPLAY=:0
export XAUTHORITY=$HOME/.Xauthority

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "Sending stop signal to $PID..." >> $LOG_FILE
        # Notify user instantly that we registered the stop
        notify-send "Voice Typing" "Stopping recording..." -i media-playback-stop
        kill -INT $PID
        
        # Wait for process to finish
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null; then
                rm "$PID_FILE"
                exit 0
            fi
            sleep 1
        done
        
        # Force kill if still stuck
        kill -9 $PID
        rm "$PID_FILE"
        exit 0
    fi
    rm "$PID_FILE"
fi

# Start the script in the background
$VENV_PYTHON $SCRIPT >> $LOG_FILE 2>&1 &
echo $! > "$PID_FILE"
echo "Started process $! at $(date)" >> $LOG_FILE
