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

# Download to user directory first
mkdir -p ~/.gradio
curl -L https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64 -o ~/.gradio/frpc_linux_amd64_v0.3
chmod +x ~/.gradio/frpc_linux_amd64_v0.3

# Try to create a symlink to the system location
mkdir -p /usr/local/lib/python3.10/site-packages/gradio || true
ln -sf ~/.gradio/frpc_linux_amd64_v0.3 /usr/local/lib/python3.10/site-packages/gradio/frpc_linux_amd64_v0.3 || true

# Run application
exec python app_launcher.py \
    --host 0.0.0.0 \
    --port ${PORT:-7860} \
    --no-browser