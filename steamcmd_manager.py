#!/usr/bin/env python3
"""
SteamCMD Manager - Container Optimized
"""

import os
import logging
import subprocess
import urllib.request
import tarfile
import shutil
import stat
from pathlib import Path

logger = logging.getLogger(__name__)

class SteamCMD:
    """Container-optimized SteamCMD manager"""
    
    def __init__(self, install_path="/root/steamcmd"):
        self.install_path = Path(install_path)
        self.steamcmd_sh = self.install_path / "steamcmd.sh"
        self.linux32_dir = self.install_path / "linux32"
        self._ensure_install_path()
        
    def _ensure_install_path(self):
        """Ensure installation directory exists"""
        self.install_path.mkdir(parents=True, exist_ok=True)
        self.linux32_dir.mkdir(exist_ok=True)
        
    def is_installed(self):
        """Check if SteamCMD is properly installed"""
        return (self.steamcmd_sh.exists() and 
                (self.linux32_dir / "steamcmd").exists())
    
    def install(self):
        """Install SteamCMD in container-friendly way"""
        if self.is_installed():
            logger.info("SteamCMD already installed")
            return True
            
        try:
            # Download and extract SteamCMD
            url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"
            tar_path = self.install_path / "steamcmd_linux.tar.gz"
            
            logger.info(f"Downloading SteamCMD from {url}")
            urllib.request.urlretrieve(url, tar_path)
            
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(self.install_path)
            
            # Set executable permissions
            self.steamcmd_sh.chmod(0o755)
            (self.install_path / "steamcmd").chmod(0o755)
            
            # Copy to linux32 if needed
            if not (self.linux32_dir / "steamcmd").exists():
                shutil.copy2(
                    self.install_path / "steamcmd",
                    self.linux32_dir / "steamcmd"
                )
                (self.linux32_dir / "steamcmd").chmod(0o755)
            
            tar_path.unlink()
            return True
            
        except Exception as e:
            logger.error(f"Installation failed: {str(e)}")
            return False
    
    def run_command(self, commands, timeout=300):
        """Run SteamCMD with given commands"""
        if not self.is_installed() and not self.install():
            raise RuntimeError("SteamCMD not available")
        
        cmd = [str(self.steamcmd_sh)] + commands
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True
            )
            logger.debug(f"SteamCMD output:\n{result.stdout}")
            return True
        except subprocess.TimeoutExpired:
            logger.error("SteamCMD command timed out")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"SteamCMD failed: {e.stderr}")
            return False
    
    def download_game(self, app_id, install_dir, **kwargs):
        """Download a game with container-friendly defaults"""
        commands = [
            "+force_install_dir", str(install_dir),
            "+login", "anonymous",
            "+app_update", str(app_id),
            "+quit"
        ]
        
        if kwargs.get("validate", True):
            commands.insert(-1, "validate")
        
        if platform := kwargs.get("platform"):
            commands.insert(1, "+@sSteamCmdForcePlatformType")
            commands.insert(2, platform)
        
        return self.run_command(commands, timeout=3600)

# Singleton instance
_instance = None

def get_steamcmd():
    global _instance
    if _instance is None:
        _instance = SteamCMD()
    return _instance

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sm = get_steamcmd()
    
    if not sm.is_installed():
        print("Installing SteamCMD...")
        sm.install()
    
    print("Testing SteamCMD...")
    if sm.run_command(["+quit"]):
        print("✅ SteamCMD working correctly")
    else:
        print("❌ SteamCMD test failed")