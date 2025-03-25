#!/usr/bin/env python3
"""
Configuration Manager for Steam Games Downloader
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "download_path": os.path.join(os.path.expanduser("~"), "steam_downloads"),
    "steamcmd_path": os.path.join(os.path.expanduser("~"), "steamcmd"),
    "anonymous_login": True,
    "username": "",
    "password": "",  
    "default_platform": "windows",
    "language": "english",
    "max_concurrent_downloads": 1,
    "validate_files": True,
    "auto_update": True
}

class ConfigManager:
    def __init__(self):
        """Initialize configuration"""
        self.config_file = "config.json"
        self.config = self._load_config()
        
    def _load_config(self):
        """Load or create config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Merge with defaults for missing keys
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                
                logger.info("Loaded existing config file")
            else:
                config = DEFAULT_CONFIG.copy()
                self._save_config(config)
                logger.info("Created new config file with defaults")
                
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return DEFAULT_CONFIG.copy()
    
    def _save_config(self, config):
        """Save config to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set config value"""
        self.config[key] = value
        return self._save_config(self.config)
    
    def reset(self):
        """Reset to default config"""
        self.config = DEFAULT_CONFIG.copy()
        return self._save_config(self.config)

# Singleton instance
_config = None

def get_config():
    """Get configuration instance"""
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config

if __name__ == "__main__":
    # Test the config manager
    logging.basicConfig(level=logging.INFO)
    cfg = get_config()
    
    print("Current configuration:")
    for k, v in cfg.config.items():
        print(f"{k}: {v}")
    
    # Test setting a value
    cfg.set("test_value", 123)
    print("\nSet test_value:", cfg.get("test_value"))