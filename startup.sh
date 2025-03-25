#!/bin/sh
# Steam Games Downloader - Startup Script

# Set environment variables
export STEAMCMD_PATH="/home/appuser/steamcmd"
export PATH="${STEAMCMD_PATH}:${PATH}"

# Verify SteamCMD installation
if [ ! -f "${STEAMCMD_PATH}/steamcmd.sh" ]; then
    echo "Installing SteamCMD..."
    mkdir -p ${STEAMCMD_PATH}
    cd ${STEAMCMD_PATH}
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -
    chmod +x steamcmd.sh
fi

# Verify Gradio binary exists
if [ -f "/usr/local/lib/python3.10/site-packages/gradio/frpc_linux_amd64_v0.3" ]; then
    echo "Gradio tunneling binary is already installed"
else
    echo "WARNING: Gradio tunneling binary is missing, sharing functionality will be disabled"
fi

# Run application
echo "Starting Steam Games Downloader application..."
exec python app_launcher.py \
    --host 0.0.0.0 \
    --port ${PORT:-7860}