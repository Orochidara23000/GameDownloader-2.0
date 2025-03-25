FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    tar \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install SteamCMD
RUN mkdir -p /usr/local/steamcmd && \
    cd /usr/local/steamcmd && \
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf - && \
    chmod +x steamcmd.sh && \
    ln -s /usr/local/steamcmd/steamcmd.sh /usr/local/bin/steamcmd

WORKDIR /app

# Copy files and set permissions
COPY . .
RUN chmod +x startup.sh && \
    chown -R nobody:nogroup /app && \
    mkdir -p /data/{downloads,config,logs} && \
    chown -R nobody:nogroup /data

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run as non-root user
USER nobody

CMD ["./startup.sh"]