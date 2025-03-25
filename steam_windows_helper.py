#!/usr/bin/env python3
"""
Windows Helper for SteamCMD 
Provides Windows-specific functionality for Steam Games Downloader
"""

import os
import sys
import logging
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

def is_windows():
    """Check if running on Windows"""
    return os.name == 'nt'

def download_steamcmd(install_path):
    """Download SteamCMD for Windows"""
    if not is_windows():
        logger.warning("This function is only for Windows environments")
        return False
        
    try:
        # Ensure path exists
        os.makedirs(install_path, exist_ok=True)
        
        # Download SteamCMD
        url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
        zip_path = os.path.join(install_path, "steamcmd.zip")
        
        logger.info(f"Downloading SteamCMD from {url}")
        urllib.request.urlretrieve(url, zip_path)
        
        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_path)
            
        # Clean up
        os.remove(zip_path)
        
        return os.path.exists(os.path.join(install_path, "steamcmd.exe"))
    
    except Exception as e:
        logger.error(f"Error downloading SteamCMD: {str(e)}")
        return False

def test_steamcmd(install_path):
    """Test if SteamCMD works on Windows"""
    if not is_windows():
        logger.warning("This function is only for Windows environments")
        return False
        
    executable = os.path.join(install_path, "steamcmd.exe")
    
    if not os.path.exists(executable):
        logger.error(f"SteamCMD executable not found at {executable}")
        return False
        
    try:
        # Test SteamCMD
        result = subprocess.run(
            [executable, "+quit"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        return result.returncode == 0
    
    except Exception as e:
        logger.error(f"Error testing SteamCMD: {str(e)}")
        return False

def install_local_steamcmd():
    """Install SteamCMD in the current directory"""
    if not is_windows():
        return False
        
    local_path = os.path.join(os.getcwd(), "steamcmd")
    return download_steamcmd(local_path)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    if not is_windows():
        print("This script is only for Windows environments")
        sys.exit(1)
    
    print("SteamCMD Windows Helper")
    print("-----------------------")
    
    # Try to install locally
    print("Attempting to install SteamCMD locally...")
    if install_local_steamcmd():
        print("SteamCMD installed successfully")
    else:
        print("Failed to install SteamCMD")