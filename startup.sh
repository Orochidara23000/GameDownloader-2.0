#!/bin/bash
set -e

# Initialize directories
mkdir -p /data/{downloads,config,logs}

# Install SteamCMD if missing
if ! command -v steamcmd &>/dev/null; then
    echo "Installing SteamCMD..."
    mkdir -p ~/steamcmd
    cd ~/steamcmd
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -
    chmod +x steamcmd.sh
    ln -s ~/steamcmd/steamcmd.sh /usr/local/bin/steamcmd
    cd -
fi

# Verify Python environment
if [ ! -f "/opt/venv/bin/activate" ]; then
    echo "Setting up Python virtual environment..."
    python -m venv /opt/venv
    . /opt/venv/bin/activate
    pip install -r requirements.txt
fi

# Activate virtual environment
source /opt/venv/bin/activate

# Find main application
APP_FILE=""
for file in app_launcher.py main.py run.py; do
    if [ -f "$file" ]; then
        APP_FILE="$file"
        break
    fi
done

if [ -z "$APP_FILE" ]; then
    echo "Error: No application file found!"
    exit 1
fi

# Start application
exec python "$APP_FILE" \
    --host 0.0.0.0 \
    --port ${PORT:-7860} \
    --no-browser