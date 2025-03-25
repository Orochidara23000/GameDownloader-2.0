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
    
    def __init__(self):
        # Auto-detect install path - use local directory if in Windows or permission issues
        default_path = os.path.join(os.getcwd(), 'steamcmd')
        if os.name == 'posix' and os.access('/home/appuser', os.W_OK):
            default_path = '/home/appuser/steamcmd'
            
        self.install_path = Path(os.environ.get('STEAMCMD_PATH', default_path))
        self.steamcmd_sh = self.install_path / "steamcmd.sh"
        self.linux32_dir = self.install_path / "linux32"
        
        # Log the path we're using
        logger.info(f"Using SteamCMD path: {self.install_path}")
        
        # Ensure permissions (try but don't fail if permissions can't be set)
        if self.steamcmd_sh.exists():
            try:
                os.chmod(self.steamcmd_sh, 0o755)
            except PermissionError:
                logger.warning(f"Cannot set executable permissions on {self.steamcmd_sh} - continuing anyway")
        
        self._ensure_install_path()
        
    def _ensure_install_path(self):
        """Create directory with correct permissions"""
        try:
            self.install_path.mkdir(parents=True, exist_ok=True)
            self.linux32_dir.mkdir(exist_ok=True)
            try:
                os.chmod(self.install_path, 0o755)
            except PermissionError:
                logger.warning(f"Cannot set permissions on {self.install_path} - continuing anyway")
        except Exception as e:
            logger.error(f"Error setting up SteamCMD: {str(e)}")
            raise
        
    def is_installed(self):
        """Check if SteamCMD is properly installed"""
        # First check if files exist
        basic_check = (self.steamcmd_sh.exists() and 
                (self.linux32_dir / "steamcmd").exists())
                
        if not basic_check:
            return False
            
        # Try to run a simple command to verify it works
        try:
            # Make a very brief test call
            test_result = subprocess.run(
                [str(self.steamcmd_sh), "+quit"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                check=False
            )
            return test_result.returncode == 0
        except Exception as e:
            logger.warning(f"SteamCMD exists but fails to run: {str(e)}")
            return False
    
    def install(self):
        """Install SteamCMD in container-friendly way"""
        if self.is_installed():
            logger.info("SteamCMD already installed")
            return True
            
        try:
            # Check for and install dependencies if needed
            self._ensure_dependencies()
            
            # Create directory if it doesn't exist
            self.install_path.mkdir(parents=True, exist_ok=True)
                
            # Download and extract SteamCMD
            if os.name == 'posix':  # Linux/Mac
                url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"
            else:  # Windows
                url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
                
            logger.info(f"Downloading SteamCMD from {url}")
            
            # Download to a temp file first to avoid permission issues
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
                
            try:
                # Download SteamCMD
                urllib.request.urlretrieve(url, temp_path)
                
                # Extract based on file type
                if url.endswith('.tar.gz'):
                    with tarfile.open(temp_path, 'r:gz') as tar:
                        tar.extractall(self.install_path)
                elif url.endswith('.zip'):
                    import zipfile
                    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                        zip_ref.extractall(self.install_path)
                
                # Set executable permissions if needed
                if os.name == 'posix':
                    try:
                        if self.steamcmd_sh.exists():
                            self.steamcmd_sh.chmod(0o755)
                        if (self.install_path / "steamcmd").exists():
                            (self.install_path / "steamcmd").chmod(0o755)
                    except PermissionError as e:
                        logger.warning(f"Permission error setting executable bit: {e}")
                        # Continue anyway as it might still work
                
                # Create linux32 directory and copy steamcmd if needed (for Linux)
                if os.name == 'posix':
                    self.linux32_dir.mkdir(exist_ok=True)
                    if not (self.linux32_dir / "steamcmd").exists() and (self.install_path / "steamcmd").exists():
                        try:
                            shutil.copy2(
                                self.install_path / "steamcmd",
                                self.linux32_dir / "steamcmd"
                            )
                            (self.linux32_dir / "steamcmd").chmod(0o755)
                        except Exception as e:
                            logger.warning(f"Could not copy steamcmd to linux32 dir: {e}")
                            # Not critical, continue
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            # Run once to trigger first-time setup
            logger.info("Running SteamCMD first-time setup...")
            self.run_command(["+quit"], timeout=120)
            
            return True
            
        except PermissionError as e:
            logger.error(f"Permission error during installation: {str(e)}")
            logger.info("Trying alternate install location...")
            
            # Try to use a different directory
            old_path = self.install_path
            self.install_path = Path(os.path.join(os.getcwd(), 'data', 'steamcmd'))
            self.steamcmd_sh = self.install_path / "steamcmd.sh"
            self.linux32_dir = self.install_path / "linux32"
            
            logger.info(f"Changed install path to: {self.install_path}")
            
            # Try again with the new path (but don't recurse indefinitely)
            return self.install()
            
        except Exception as e:
            logger.error(f"Installation failed: {str(e)}")
            return False
    
    def _ensure_dependencies(self):
        """Ensure required dependencies are installed"""
        try:
            # Check if we're on a Linux system
            if os.name != 'posix':
                # On Windows, we need different dependencies
                logger.info("Running on Windows - checking for Visual C++ Redistributable")
                # Windows just needs Visual C++ Redistributable which should be present
                # We'll just log and continue
                return
            
            # On Linux, we need 32-bit libraries
            logger.info("Running on Linux - checking for dependencies")
            
            # Check processor architecture
            import platform
            is_64bit = platform.architecture()[0] == '64bit'
            
            # Check distribution type
            if shutil.which('apt-get'):
                logger.info("Installing dependencies via apt-get")
                # Update package lists
                subprocess.run(
                    ["apt-get", "update", "-y"],
                    check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                
                # Install required packages
                packages = ["curl", "ca-certificates"]
                
                # Add architecture-specific packages
                if is_64bit:
                    # 64-bit system needs 32-bit compatibility libraries
                    try:
                        # Enable 32-bit architecture if needed
                        subprocess.run(
                            ["dpkg", "--add-architecture", "i386"],
                            check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                        )
                        packages.extend(["lib32gcc-s1", "lib32stdc++6", "libc6-i386"])
                    except Exception as e:
                        logger.warning(f"Could not enable i386 architecture: {e}")
                        # Try to install without it
                
                # Install all required packages
                cmd = ["apt-get", "install", "-y"] + packages
                logger.info(f"Running: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                
                if result.returncode != 0:
                    logger.warning(f"Failed to install some dependencies: {result.stderr}")
                return
            
            # Check for yum (Red Hat/CentOS/Fedora)
            elif shutil.which('yum'):
                logger.info("Installing dependencies via yum")
                
                # Install required packages  
                packages = ["curl"]
                
                # Add architecture-specific packages
                if is_64bit:
                    # 64-bit system needs 32-bit compatibility libraries
                    packages.extend(["glibc.i686", "libstdc++.i686"])
                
                # Install all required packages
                cmd = ["yum", "install", "-y"] + packages
                logger.info(f"Running: {' '.join(cmd)}")
                subprocess.run(
                    cmd,
                    check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                return
                
            # Check for pacman (Arch Linux)
            elif shutil.which('pacman'):
                logger.info("Installing dependencies via pacman")
                subprocess.run(
                    ["pacman", "-Sy", "--noconfirm", "lib32-gcc-libs", "lib32-glibc"],
                    check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                return
                
            # If we get here, we don't know the package manager
            logger.warning("No known package manager found - skipping dependency installation")
            logger.warning("You may need to install the following manually:")
            if is_64bit:
                logger.warning("- 32-bit glibc libraries")
                logger.warning("- 32-bit libstdc++ libraries")
                logger.warning("- curl")
                
        except Exception as e:
            logger.warning(f"Error installing dependencies: {str(e)}")
    
    def run_command(self, commands, timeout=300):
        """Run SteamCMD with given commands"""
        if not self.is_installed() and not self.install():
            raise RuntimeError("SteamCMD not available")
        
        # Determine which executable to use based on platform
        if os.name == 'posix':  # Linux/Mac
            executable = str(self.steamcmd_sh)
        else:  # Windows
            executable = str(self.install_path / "steamcmd.exe")
            
        cmd = [executable] + commands
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            # Add environment variables for better error handling
            env = os.environ.copy()
            if os.name == 'posix':
                env['STEAM_NOINTERACTIVE'] = '1'
            
            # Run the command with better error capture
            result = subprocess.run(
                cmd,
                check=False,  # Changed to False to handle errors ourselves
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True,
                env=env,
                cwd=str(self.install_path)  # Run from the steamcmd directory
            )
            
            # Log the output regardless of success/failure
            logger.debug(f"SteamCMD output:\n{result.stdout}")
            if result.stderr:
                logger.debug(f"SteamCMD stderr:\n{result.stderr}")
            
            # Check return code
            if result.returncode != 0:
                logger.error(f"SteamCMD failed with return code {result.returncode}")
                if "you are missing 32-bit libraries" in result.stderr or "you are missing 32-bit libraries" in result.stdout:
                    logger.error("Missing 32-bit libraries. Please install them manually.")
                    if os.name == 'posix':
                        logger.error("For Debian/Ubuntu: sudo apt-get install lib32gcc-s1 lib32stdc++6")
                        logger.error("For RHEL/CentOS: sudo yum install glibc.i686 libstdc++.i686")
                return False
                
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"SteamCMD command timed out after {timeout} seconds")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"SteamCMD failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error running SteamCMD: {str(e)}")
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