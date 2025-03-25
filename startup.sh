#!/bin/sh
# Steam Games Downloader - Startup Script

# Ensure proper signal handling
trap 'echo "Caught signal, shutting down gracefully..."; kill -TERM $PID; sleep 3; kill -9 $PID 2>/dev/null; echo "Process terminated"' INT TERM

# Set environment variables
export STEAMCMD_PATH="/home/appuser/steamcmd"
export PATH="${STEAMCMD_PATH}:${PATH}"
export ENVIRONMENT="cloud"  # Set environment type for cloud deployment
export PYTHONUNBUFFERED=1   # Ensure Python output isn't buffered

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

# Start health check server separately for faster responses
echo "Starting health check server..."
python -c "
import os
from flask import Flask
import threading

app = Flask('health_check')

@app.route('/health')
def health():
    return '{\"status\": \"healthy\"}'

@app.route('/')
def home():
    return 'Steam Games Downloader health check - main app running on port 8080'

threading.Thread(
    target=lambda: app.run(host='0.0.0.0', port=8081, debug=False),
    daemon=True
).start()
" &

HEALTH_PID=$!
echo "Health check server started with PID ${HEALTH_PID}"

# Run main application
echo "Starting Steam Games Downloader application..."
python app_launcher.py \
    --host 0.0.0.0 \
    --port ${PORT:-7860} &

PID=$!
echo "Main application started with PID ${PID}"

# Print a message every 30 seconds to keep logs active
counter=0
while kill -0 $PID 2>/dev/null; do
    counter=$((counter + 1))
    echo "Application is still running at $(date) - uptime ${counter} intervals"
    sleep 30
done

# If we get here, the main process has stopped
echo "Main application process (PID ${PID}) has exited."
kill -9 $HEALTH_PID 2>/dev/null

# Wait for the main process to terminate completely
wait $PID 2>/dev/null
EXIT_CODE=$?
echo "Application has terminated with exit code $EXIT_CODE"