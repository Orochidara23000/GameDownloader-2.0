# Steam Games Downloader

A containerized application for downloading Steam games using SteamCMD with a user-friendly web interface.

## Features

- Web-based interface using Gradio
- Download Steam games using SteamCMD
- Automatic game library management
- Container-optimized design

## Quick Start

### Using Docker

```bash
# Build the container
docker build -t steam-downloader .

# Run the container
docker run -p 8080:8080 -v /path/to/downloads:/app/data/downloads steam-downloader
```

### Access the Application

The application will be available at:
- http://localhost:8080 (when running locally)
- Public URL (if share=True and the tunneling binary was successfully installed)

## Configuration

Configuration options are stored in `config.json` and include:

- `download_path`: Path where games are downloaded
- `steamcmd_path`: Path to SteamCMD installation
- `anonymous_login`: Whether to use anonymous login (true/false)
- `username`: Steam username (if anonymous_login is false)
- `password`: Steam password (if anonymous_login is false)
- `default_platform`: Default platform for downloads (windows, linux, mac)

## Container Access Options

### 1. Direct Access
Access the application directly via the container's IP and port.

### 2. Port Mapping
When running locally, map the container's port to a host port:
```bash
docker run -p 8080:8080 steam-downloader
```

### 3. Public URL via Gradio's Sharing Feature
The application attempts to create a public URL using Gradio's sharing feature. This requires the Gradio tunneling binary to be properly installed during container build.

### 4. Reverse Proxy / Ingress
For production deployments, it's recommended to set up a proper reverse proxy or Kubernetes ingress to expose the service.

## Troubleshooting

### Sharing Not Available
If public sharing is not available, ensure:
1. The container build completed successfully
2. The Gradio tunneling binary was installed properly
3. The container has outbound internet access for tunneling

### Permission Issues
If you encounter permission issues with SteamCMD or downloads, ensure:
1. Your container user has appropriate permissions
2. Volume mounts are properly configured

## Development

### Project Structure
- `app_launcher.py`: Main application entry point
- `steamcmd_manager.py`: SteamCMD interaction
- `download_manager.py`: Download queue management
- `library_manager.py`: Game library management
- `gradio_interface.py`: Web interface
- `startup.sh`: Container startup script
- `Dockerfile`: Container definition 