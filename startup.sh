#!/bin/sh
set -e

# Initialize environment
export PATH="/usr/local/bin:$PATH"

# Run the application
exec python app_launcher.py \
    --host 0.0.0.0 \
    --port ${PORT:-7860} \
    --no-browser