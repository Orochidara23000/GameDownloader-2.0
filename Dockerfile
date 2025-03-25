FROM python:3.10-slim

# 1. Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    tar \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 2. Create user and set permissions
RUN useradd -m appuser && \
    mkdir -p /app/data/{downloads,config,logs} && \
    chown -R appuser:appuser /app && \
    mkdir -p /home/appuser/steamcmd && \
    chown -R appuser:appuser /home/appuser

# 3. Install SteamCMD
RUN cd /home/appuser/steamcmd && \
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf - && \
    chmod +x steamcmd.sh && \
    ln -s /home/appuser/steamcmd/steamcmd.sh /usr/local/bin/steamcmd

WORKDIR /app

# 4. Copy files and set permissions
COPY --chown=appuser:appuser . .
RUN find . -name "*.sh" -exec chmod +x {} \; && \
    find . -name "*.py" -exec chmod +x {} \; && \
    chmod -R 755 /app

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Final setup
USER appuser
ENV PATH="/home/appuser/steamcmd:${PATH}"

# 7. Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-7860}/ || exit 1

CMD ["./startup.sh"]