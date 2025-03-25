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
    
    interface = create_interface()
    interface.launch(
        server_name=args.host,
        server_port=args.port,
        share=True,
        prevent_thread_lock=True
    )

def main():
    """Main application entry point"""
    args = parse_arguments()
    logger = configure_logging(args.debug)
    
    logger.info("Starting Steam Games Downloader")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Working directory: {os.getcwd()}")
    
    try:
        initialize_environment()
        launch_interface(args)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()