# Parakeet Dictation for Kubuntu

A fast, local, and private speech-to-text tool using NVIDIA's Parakeet TDT models. Designed to work like "Win+H" on Linux (X11).

## Prerequisites (Kubuntu/Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3-pip python3-venv python3-pyaudio libsox-dev xdotool notify-send
```

## Setup

1. **Clone/Move** this folder to your preferred location.
2. **Create a virtual environment:**
   ```bash
   cd parakeet-dictation
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Test the toggle script:**
   Run `./toggle.sh` manually to ensure it initializes the model and starts listening (check notifications).

## Setting up Win+H Shortcut

To make this feel like Windows dictation:

1. Open **System Settings** -> **Shortcuts** -> **Global Shortcuts**.
2. Click **Add New Shortcut** or find "Custom Shortcuts".
3. Create a new "Command/URL" shortcut:
   - **Name:** Voice Typing Toggle
   - **Trigger:** Win+H (Meta+H)
   - **Action:** Path to your `toggle.sh`, e.g., `/mnt/windows/Projects/Programming/parakeet-dictation/toggle.sh`
4. Apply changes.

## Usage

- Press **Win+H** to start dictation. A notification will appear.
- Speak your sentence.
- The tool will automatically type the text into your focused window once it detects silence.
- Press **Win+H** again to stop the background process.
