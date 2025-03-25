#!/bin/sh
# Steam Games Downloader - Startup Script

# Ensure proper signal handling
trap 'echo "Caught signal, stopping gracefully..."; kill -TERM $PID; wait $PID' INT TERM

# Set environment variables
export STEAMCMD_PATH="/home/appuser/steamcmd"
export PATH="${STEAMCMD_PATH}:${PATH}"
export ENVIRONMENT="cloud"  # Set environment type for cloud deployment

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
python app_launcher.py \
    --host 0.0.0.0 \
    --port ${PORT:-7860} &

PID=$!

# Print a message every 30 seconds to keep logs active
while kill -0 $PID 2>/dev/null; do
    echo "Application is still running at $(date)"
    sleep 30
done

# Wait for the process to terminate
wait $PID
echo "Application has terminated with exit code $?"