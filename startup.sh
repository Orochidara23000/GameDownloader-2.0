#!/bin/bash
# Simplified Startup Script for Steam Games Downloader

set -e

# Configuration
APP_DIR="/app"
DATA_DIR="/data"
LOG_DIR="/var/log/steamdownloader"
STEAMCMD_DIR="/root/steamcmd"

# Initialize directories
mkdir -p ${DATA_DIR}/downloads
mkdir -p ${LOG_DIR}
mkdir -p ${STEAMCMD_DIR}

# Check dependencies
echo "=== Checking dependencies ==="
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found!"
    exit 1
fi

# Install Python dependencies
echo "=== Installing Python packages ==="
pip install -r ${APP_DIR}/requirements.txt

# Check SteamCMD
echo "=== Checking SteamCMD ==="
if [ ! -f "${STEAMCMD_DIR}/steamcmd.sh" ]; then
    echo "Installing SteamCMD..."
    cd ${STEAMCMD_DIR}
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -
    chmod +x steamcmd.sh
    cd ${APP_DIR}
fi

# Initialize SteamCMD
echo "=== Testing SteamCMD ==="
if ! ${STEAMCMD_DIR}/steamcmd.sh +quit; then
    echo "WARNING: SteamCMD initialization failed - downloads may not work"
fi

# Start application
echo "=== Starting Application ==="
cd ${APP_DIR}

# Auto-select launcher script
LAUNCHER=""
for script in app_launcher.py main.py run.py simple.py; do
    if [ -f "$script" ]; then
        LAUNCHER="$script"
        break
    fi
done

if [ -z "$LAUNCHER" ]; then
    echo "ERROR: No launcher script found!"
    exit 1
fi

# Run with basic python command
exec python3 ${LAUNCHER} \
    --host 0.0.0.0 \
    --port ${PORT:-7860} \
    --no-browser