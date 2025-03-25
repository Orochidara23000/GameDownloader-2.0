#!/usr/bin/env python3
"""
Steam Games Downloader - Main Launcher
"""

import os
import sys
import logging
import argparse
import threading
from pathlib import Path

# Add health check server
from flask import Flask
import threading

def start_health_check_server(port=8081):
    """Start a simple health check server"""
    app = Flask("health_check")
    
    @app.route('/health')
    def health_check():
        return '{"status": "healthy"}'
    
    @app.route('/')
    def root():
        return 'Steam Games Downloader is running. Access the UI on port 8080.'
    
    # Run in a separate thread
    threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False),
        daemon=True
    ).start()
    
    logging.getLogger('launcher').info(f"Health check server running on port {port}")

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
    parser.add_argument(
        '--health-port',
        type=int,
        default=8081,
        help='Health check server port'
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
    
    # Get the logger
    logger = logging.getLogger('launcher')
    
    # Get the interface
    interface = create_interface()
    
    # Determine if sharing should be enabled
    enable_sharing = not args.no_share and verify_tunnel_binary()
    
    logger.info(f"Launching interface with sharing={'enabled' if enable_sharing else 'disabled'}")
    
    # Start in a thread to avoid blocking if health checks are important
    if os.environ.get('ENVIRONMENT') == 'cloud':
        # In cloud environment, run in thread to allow health checks to respond
        thread = threading.Thread(
            target=lambda: interface.launch(
                server_name=args.host,
                server_port=args.port,
                share=enable_sharing,
                prevent_thread_lock=True,
                show_api=False,
                quiet=True
            )
        )
        thread.daemon = True
        thread.start()
        
        # Keep the main thread alive
        try:
            while thread.is_alive():
                thread.join(1)  # Join with timeout to keep checking if alive
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            
        logger.info("Interface thread has stopped")
    else:
        # For local/development environment, block on the interface
        interface.launch(
            server_name=args.host,
            server_port=args.port,
            share=enable_sharing,
            prevent_thread_lock=False,
            show_api=False,
            quiet=True
        )
        
        logger.info("Interface server has stopped")

def main():
    """Main application entry point"""
    args = parse_arguments()
    logger = configure_logging(args.debug)
    
    logger.info("Starting Steam Games Downloader")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Working directory: {os.getcwd()}")
    
    try:
        # Set up signal handling
        import signal
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down gracefully...")
            # Don't exit immediately to allow cleanup
            threading.Timer(2.0, lambda: sys.exit(0)).start()
        
        # Install signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start health check server first
        if os.environ.get('ENVIRONMENT') == 'cloud':
            # In cloud environment, health checks are critical
            logger.info("Starting health check server for cloud environment")
            start_health_check_server(args.health_port)
        
        # Initialize environment and resources
        initialize_environment()
        
        # Launch the main interface
        launch_interface(args)
        
        # This will only be reached if interface.launch() finishes
        logger.warning("Interface launch returned unexpectedly. Container will exit.")
        
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()