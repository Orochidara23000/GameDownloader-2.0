#!/usr/bin/env python3
"""
Download Manager for Steam Games Downloader
Handles download queue and processes using SteamCMD
"""

import os
import logging
import queue
import threading
from pathlib import Path
import time

# Configure logger
logger = logging.getLogger(__name__)

class DownloadManager:
    """Manages game downloads using SteamCMD"""
    
    def __init__(self):
        """Initialize the download manager"""
        self.download_queue = queue.Queue()
        self.active_downloads = {}
        self.lock = threading.Lock()
        self.worker_thread = None
        self.running = False
        
        # Get configuration
        from config import get_config
        self.config = get_config()
        
        logger.info("Download Manager initialized")

    def add_download(self, app_id, game_name):
        """Add a game to download queue"""
        # Check if SteamCMD is available
        from steamcmd_manager import get_steamcmd
        steamcmd = get_steamcmd()
        if not steamcmd.is_installed():
            try:
                # Try to install SteamCMD before adding to queue
                logger.info("SteamCMD not installed, attempting installation...")
                if not steamcmd.install():
                    raise RuntimeError("Failed to install SteamCMD. Downloads will not work.")
            except Exception as e:
                logger.error(f"SteamCMD installation error: {str(e)}")
                raise RuntimeError(f"Cannot add download: SteamCMD installation failed: {str(e)}")
        
        with self.lock:
            download_id = f"{app_id}-{int(time.time())}"
            self.download_queue.put({
                'id': download_id,
                'app_id': app_id,
                'name': game_name,
                'status': 'queued',
                'progress': 0
            })
            logger.info(f"Added download {download_id}: {game_name} (AppID: {app_id})")
            return download_id

    def start_worker(self):
        """Start the download worker thread"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._process_queue)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            logger.info("Download worker thread started")

    def stop_worker(self):
        """Stop the download worker thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
        logger.info("Download worker stopped")

    def _process_queue(self):
        """Process items from download queue"""
        from steamcmd_manager import get_steamcmd
        
        while self.running:
            try:
                # Get item from queue with timeout
                try:
                    item = self.download_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Extract download ID
                download_id = item['id']
                
                # Update status to downloading
                with self.lock:
                    self.active_downloads[download_id] = item
                    item['status'] = 'downloading'
                
                logger.info(f"Starting download {download_id}: {item['name']}")
                
                try:
                    # Get SteamCMD instance
                    steamcmd = get_steamcmd()
                    
                    # Verify SteamCMD is installed
                    if not steamcmd.is_installed():
                        logger.error("SteamCMD not installed, attempting to install now...")
                        if not steamcmd.install():
                            raise RuntimeError("SteamCMD installation failed")
                    
                    # Set download path
                    base_download_path = self.config.get('download_path', 'data/downloads')
                    download_path = os.path.join(
                        base_download_path,
                        'steamapps',
                        'common',
                        f"app_{item['app_id']}"
                    )
                    
                    # Ensure directory exists
                    try:
                        os.makedirs(download_path, exist_ok=True)
                    except Exception as path_error:
                        logger.error(f"Failed to create download directory: {str(path_error)}")
                        # Try alternate directory
                        download_path = os.path.join(os.getcwd(), 'downloads', f"app_{item['app_id']}")
                        os.makedirs(download_path, exist_ok=True)
                        logger.info(f"Using alternate download path: {download_path}")
                    
                    # Start download
                    success = steamcmd.download_game(
                        app_id=item['app_id'],
                        install_dir=download_path,
                        username=self.config.get('username') if not self.config.get('anonymous_login', True) else None,
                        password=self.config.get('password') if not self.config.get('anonymous_login', True) else None,
                        validate=self.config.get('validate_files', True),
                        platform=self.config.get('default_platform', 'windows')
                    )
                    
                    # Update status based on result
                    with self.lock:
                        if success:
                            item['status'] = 'completed'
                            item['progress'] = 100
                            logger.info(f"Download completed: {item['name']}")
                            
                            # Update library
                            try:
                                from library_manager import get_library_manager
                                lib = get_library_manager()
                                lib.add_game(
                                    app_id=item['app_id'],
                                    name=item['name'],
                                    location=download_path
                                )
                            except Exception as lib_error:
                                logger.error(f"Failed to update library: {str(lib_error)}")
                        else:
                            item['status'] = 'failed'
                            logger.error(f"Download failed: {item['name']}")
                        
                        self.download_queue.task_done()
                
                except Exception as e:
                    logger.error(f"Error during download of {item['name']}: {str(e)}")
                    with self.lock:
                        item['status'] = 'failed'
                        item['error'] = str(e)
                        self.download_queue.task_done()
                    
            except Exception as e:
                logger.error(f"Critical error in download worker: {str(e)}")
                # Sleep briefly to avoid CPU spinning on continuous errors
                time.sleep(1)

    def get_download_status(self, download_id):
        """Get status of a download"""
        with self.lock:
            if download_id in self.active_downloads:
                return self.active_downloads[download_id]
            return None

    def get_queue_status(self):
        """Get current queue status"""
        with self.lock:
            return {
                'queued': self.download_queue.qsize(),
                'active': len(self.active_downloads),
                'downloads': list(self.active_downloads.values())
            }

# Singleton instance
_instance = None

def get_download_manager():
    """Get the singleton download manager instance"""
    global _instance
    if _instance is None:
        _instance = DownloadManager()
    return _instance

if __name__ == "__main__":
    # Test the download manager
    logging.basicConfig(level=logging.INFO)
    
    dm = get_download_manager()
    dm.start_worker()
    
    # Add test download
    test_id = dm.add_download(730, "Counter-Strike: Global Offensive")
    
    try:
        while True:
            status = dm.get_download_status(test_id)
            if status and status['status'] in ['completed', 'failed']:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        dm.stop_worker()