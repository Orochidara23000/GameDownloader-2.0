#!/bin/bash
set -e

# Activate virtual environment (if needed)
python -m venv --copies /opt/venv
source /opt/venv/bin/activate

# Run the application
exec python app_launcher.py --host 0.0.0.0 --port ${PORT:-7860} --no-browser