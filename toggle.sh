#!/bin/bash

# --- CONFIGURATION ---
LOGFILE="/tmp/parakeet_dictation.log"
PIDFILE="/tmp/parakeet_rec.pid"
AUDIOFILE="/tmp/parakeet_audio.wav"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="python"
TRANSCRIBE_SCRIPT="$PROJECT_DIR/transcribe.py"

# Environment variables for KDE/D-Bus
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"

# Helper: Send notifications
send_notify() {
    notify-send -u low -t 2000 "$1" "$2"
}

# --- LOGIC ---

# 1. STOP MODE: If PID file exists, stop recording and transcribe
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping recording (PID $PID)..." >> "$LOGFILE"
        
        # Give a small buffer for audio to finalize
        sleep 0.5
        kill -SIGINT "$PID"
        
        # Wait until process ends
        tail --pid=$PID -f /dev/null 2>/dev/null
        rm -f "$PIDFILE"
        
        send_notify "🧠 Transcribing..." "NVIDIA Parakeet is working..."
        
        # Transcribe
        TEXT=$("$PYTHON_CMD" "$TRANSCRIBE_SCRIPT" --input "$AUDIOFILE" 2>>"$LOGFILE")
        
        if [ ! -z "$TEXT" ]; then
            # Copy to clipboard and type it
            if command -v xclip &> /dev/null; then
                echo -n "$TEXT " | xclip -selection clipboard -f
            elif command -v wl-copy &> /dev/null; then
                echo -n "$TEXT " | wl-copy
            else
                # Fallback to direct typing if clipboard tools are missing
                xdotool type --clearmodifiers --delay 0 "$TEXT "
                exit 0
            fi
            
            # Simulate paste
            sleep 0.1
            xdotool key --clearmodifiers Control+v
            send_notify "✅ Done" "Dictation inserted."
        else
            send_notify "🤷 Empty" "No text recognized."
        fi
        
        rm -f "$AUDIOFILE"
        exit 0
    else
        # Stale PID file
        rm -f "$PIDFILE"
    fi
fi

# 2. START MODE: Start recording
rm -f "$AUDIOFILE"
rec -q "$AUDIOFILE" rate 16k &
NEW_PID=$!

# Verify it started correctly
sleep 0.3
if ! kill -0 "$NEW_PID" 2>/dev/null; then
    send_notify "❌ Error" "Could not start recording (Microphone busy?)."
    exit 1
fi

echo $NEW_PID > "$PIDFILE"
send_notify "🎙️ Recording..." "Press shortcut again to stop"
