#!/bin/bash
# Nixpacks-compatible Startup Script

set -e

# Initialize directories
mkdir -p /data/downloads
mkdir -p /data/config

# Install SteamCMD if not present
if [ ! -f "$HOME/steamcmd/steamcmd.sh" ]; then
    echo "Installing SteamCMD..."
    mkdir -p "$HOME/steamcmd"
    cd "$HOME/steamcmd"
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -
    chmod +x steamcmd.sh
    cd -
fi

# Test SteamCMD
echo "Testing SteamCMD..."
if ! "$HOME/steamcmd/steamcmd.sh" +quit; then
    echo "Warning: SteamCMD test failed - downloads may not work"
fi

# Find and run the main application
LAUNCHER=""
for script in app_launcher.py main.py run.py; do
    if [ -f "$script" ]; then
        LAUNCHER="$script"
        break
    fi
done

if [ -z "$LAUNCHER" ]; then
    echo "Error: No launcher script found!"
    exit 1
fi

exec python "$LAUNCHER" --host 0.0.0.0 --port ${PORT:-7860}