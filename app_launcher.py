#!/usr/bin/env python3
"""
Steam Games Downloader - Main Launcher
"""

import os
import sys
import logging
import argparse
from pathlib import Path

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
    parser.add_argument(
        '--no-share',
        action='store_true',
        help='Disable public URL sharing'
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

def verify_tunnel_binary():
    """Verify that the Gradio tunneling binary exists"""
    logger = logging.getLogger('launcher')
    binary_path = "/usr/local/lib/python3.10/site-packages/gradio/frpc_linux_amd64_v0.3"
    
    if os.path.exists(binary_path):
        logger.info(f"Gradio tunneling binary found at {binary_path}")
        return True
    else:
        logger.warning(f"Gradio tunneling binary not found at {binary_path}")
        return False

def launch_interface(args):
    """Launch the Gradio interface"""
    from gradio_interface import create_interface
    
    # Get the interface
    interface = create_interface()
    
    # Determine if sharing should be enabled
    enable_sharing = not args.no_share and verify_tunnel_binary()
    
    logger.info(f"Launching interface with sharing={'enabled' if enable_sharing else 'disabled'}")
    
    # Use queue=True to ensure the server keeps running
    interface.launch(
        server_name=args.host,
        server_port=args.port,
        share=enable_sharing,
        prevent_thread_lock=False,  # Changed to False to block main thread
        show_api=False,
        quiet=True
    )
    
    # The code below won't execute until the server is shut down
    logger.info("Interface server has stopped")

def main():
    """Main application entry point"""
    args = parse_arguments()
    logger = configure_logging(args.debug)
    
    logger.info("Starting Steam Games Downloader")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Working directory: {os.getcwd()}")
    
    try:
        # Add signal handlers for graceful shutdown
        import signal
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down gracefully...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        initialize_environment()
        launch_interface(args)
        
        # This will only be reached if interface.launch() finishes (which it shouldn't)
        logger.warning("Interface launch returned unexpectedly. Container will exit.")
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()