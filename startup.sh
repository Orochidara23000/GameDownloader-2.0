#!/bin/bash
set -e

# Initialize directories
mkdir -p /data/{downloads,config,logs}

# Install SteamCMD to standard location
if [ ! -f "/usr/local/bin/steamcmd" ]; then
    echo "Installing SteamCMD..."
    mkdir -p /usr/local/steamcmd
    cd /usr/local/steamcmd
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -
    chmod +x steamcmd.sh
    ln -s /usr/local/steamcmd/steamcmd.sh /usr/local/bin/steamcmd
fi

# Activate virtual environment
source /opt/venv/bin/activate

# Run the application (prioritize app_launcher.py)
if [ -f "app_launcher.py" ]; then
    exec python app_launcher.py --host 0.0.0.0 --port ${PORT:-7860}
elif [ -f "main.py" ]; then
    exec python main.py --host 0.0.0.0 --port ${PORT:-7860}
else
    echo "Error: No application entry point found!"
    exit 1
fi