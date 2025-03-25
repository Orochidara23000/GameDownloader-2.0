#!/usr/bin/env python3
"""
Steam Games Downloader - Main Launcher
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import urllib.request
import shutil

def install_gradio_tunnel_binary():
    """Download and install the Gradio tunneling binary."""
    logger = logging.getLogger('launcher')
    binary_url = "https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64"
    target_filename = "frpc_linux_amd64_v0.3"
    target_directory = "/usr/local/lib/python3.10/site-packages/gradio"
    target_path = os.path.join(target_directory, target_filename)
    
    logger.info(f"Checking for Gradio tunneling binary at {target_path}")
    
    if os.path.exists(target_path):
        logger.info("Gradio tunneling binary already exists")
        return True
    
    logger.info(f"Downloading Gradio tunneling binary from {binary_url}")
    try:
        # Create a temporary file
        temp_file, _ = urllib.request.urlretrieve(binary_url)
        
        # Copy to the target location
        logger.info(f"Copying binary to {target_path}")
        shutil.copy2(temp_file, target_path)
        
        # Set executable permissions
        logger.info("Setting executable permissions")
        try:
            os.chmod(target_path, 0o755)
        except Exception as e:
            logger.warning(f"Could not set permissions: {str(e)}")
        
        logger.info("Gradio tunneling binary installed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to install Gradio tunneling binary: {str(e)}")
        return False

def configure_logging(debug=False):
    """Set up logging configuration"""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('steam_downloader.log')
        ]
    )
    return logging.getLogger('launcher')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Steam Games Downloader Launcher'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('PORT', 7860)),
        help='Web server port'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Web server host'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Disable auto-launching browser'
    )
    return parser.parse_args()

def initialize_environment():
    """Ensure required environment is set up"""
    # Create essential directories
    Path('data/downloads').mkdir(parents=True, exist_ok=True)
    Path('data/config').mkdir(parents=True, exist_ok=True)
    
    # Initialize components
    from steamcmd_manager import get_steamcmd
    get_steamcmd()  # Auto-initializes if needed

def launch_interface(args):
    """Launch the Gradio interface"""
    from gradio_interface import create_interface
    
    # Get the interface
    interface = create_interface()
    
    # Check if tunneling binary exists before enabling sharing
    binary_path = os.environ.get("GRADIO_TUNNEL_BINARY_PATH")
    enable_sharing = binary_path and os.path.exists(binary_path)
    
    interface.launch(
        server_name=args.host,
        server_port=args.port,
        share=enable_sharing,  # Only enable if binary exists
        prevent_thread_lock=True
    )

def setup_gradio_sharing():
    """Set up Gradio sharing with user permissions"""
    logger = logging.getLogger('launcher')
    
    # Create user-writable directory
    user_gradio_dir = os.path.expanduser("~/.gradio")
    os.makedirs(user_gradio_dir, exist_ok=True)
    
    # Define file paths
    binary_path = os.path.join(user_gradio_dir, "frpc_linux_amd64_v0.3")
    
    # Set environment variable to tell Gradio where to find the binary
    logger.info(f"Setting GRADIO_TUNNEL_BINARY_PATH to {binary_path}")
    os.environ["GRADIO_TUNNEL_BINARY_PATH"] = binary_path
    
    # Download the binary if needed
    if not os.path.exists(binary_path):
        logger.info(f"Downloading Gradio tunneling binary to {binary_path}")
        try:
            urllib.request.urlretrieve(
                "https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64", 
                binary_path
            )
            os.chmod(binary_path, 0o755)
            logger.info("Successfully downloaded and configured Gradio tunneling binary")
            return True
        except Exception as e:
            logger.error(f"Failed to download tunneling binary: {str(e)}")
            return False
    else:
        logger.info("Gradio tunneling binary already exists")
        return True

def main():
    """Main application entry point"""
    args = parse_arguments()
    logger = configure_logging(args.debug)
    
    logger.info("Starting Steam Games Downloader")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Working directory: {os.getcwd()}")
    
    try:
        initialize_environment()
        
        # Set up Gradio sharing with user permissions
        logger.info("Setting up Gradio tunneling...")
        sharing_setup = setup_gradio_sharing()
        
        launch_interface(args)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()