FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    tar \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app user and directories
RUN useradd -m appuser && \
    mkdir -p /home/appuser/steamcmd && \
    mkdir -p /data/{downloads,config,logs} && \
    chown -R appuser:appuser /home/appuser /data

WORKDIR /app

# Copy application files
COPY --chown=appuser:appuser . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to appuser
USER appuser

# Install SteamCMD as appuser
RUN cd /home/appuser/steamcmd && \
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf - && \
    chmod +x steamcmd.sh

# Set PATH to include SteamCMD
ENV PATH="/home/appuser/steamcmd:${PATH}"

CMD ["./startup.sh"]