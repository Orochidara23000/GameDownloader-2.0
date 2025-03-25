# Use official Python image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    tar \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install SteamCMD
RUN mkdir -p /usr/local/steamcmd && \
    cd /usr/local/steamcmd && \
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf - && \
    chmod +x steamcmd.sh && \
    ln -s /usr/local/steamcmd/steamcmd.sh /usr/local/bin/steamcmd

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create data directories
RUN mkdir -p /data/{downloads,config,logs}

# Set startup command
CMD ["./startup.sh"]