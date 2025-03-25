#!/bin/sh
# Auto-set permissions on startup
find /app -name "*.sh" -exec chmod +x {} \;
find /app -name "*.py" -exec chmod +x {} \;

# Set environment
export STEAMCMD_PATH="/home/appuser/steamcmd"
export PATH="${STEAMCMD_PATH}:${PATH}"

# Verify SteamCMD
if [ ! -f "${STEAMCMD_PATH}/steamcmd.sh" ]; then
    echo "Installing SteamCMD..."
    mkdir -p ${STEAMCMD_PATH}
    cd ${STEAMCMD_PATH}
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -
    chmod +x steamcmd.sh
fi

# Run application
exec python app_launcher.py \
    --host 0.0.0.0 \
    --port ${PORT:-7860} \
    --no-browser