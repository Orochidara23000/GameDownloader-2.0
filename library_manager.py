#!/usr/bin/env python3
"""
Library Manager for Steam Games Downloader
Manages the collection of downloaded games
"""

import os
import logging
import json
import pandas as pd
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class LibraryManager:
    """Manages the game library"""
    
    def __init__(self):
        """Initialize the library manager"""
        self.library_file = "game_library.json"
        self.library = self._load_library()
        logger.info("Library Manager initialized")
        
    def _load_library(self):
        """Load game library from file or create a new one"""
        try:
            if os.path.exists(self.library_file):
                with open(self.library_file, 'r') as f:
                    library = json.load(f)
                logger.info(f"Loaded library with {len(library)} games")
                return library
            else:
                logger.info("No existing library found, creating new")
                return {}
        except Exception as e:
            logger.error(f"Error loading library: {str(e)}")
            return {}
            
    def _save_library(self):
        """Save library to file"""
        try:
            with open(self.library_file, 'w') as f:
                json.dump(self.library, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving library: {str(e)}")
            return False
            
    def add_game(self, app_id, name, location):
        """Add or update a game in the library"""
        app_id = str(app_id)  # Ensure string format
        
        self.library[app_id] = {
            'name': name,
            'location': str(location),
            'size': self._get_folder_size(location),
            'added_date': time.time(),
            'last_played': None
        }
        
        logger.info(f"Added/updated game in library: {name} (AppID: {app_id})")
        self._save_library()
        return True
        
    def remove_game(self, app_id):
        """Remove a game from the library"""
        app_id = str(app_id)
        
        if app_id in self.library:
            game = self.library[app_id]
            del self.library[app_id]
            self._save_library()
            logger.info(f"Removed game from library: {game['name']} (AppID: {app_id})")
            return True
        
        logger.warning(f"Attempted to remove non-existent game with AppID: {app_id}")
        return False
        
    def get_game(self, app_id):
        """Get a game from the library"""
        return self.library.get(str(app_id))
        
    def get_all_games(self):
        """Get all games in the library"""
        return self.library
        
    def update_last_played(self, app_id):
        """Update the last played timestamp for a game"""
        app_id = str(app_id)
        
        if app_id in self.library:
            self.library[app_id]['last_played'] = time.time()
            self._save_library()
            return True
        return False
        
    def _get_folder_size(self, folder_path):
        """Calculate the total size of files in a folder (in MB)"""
        try:
            path = Path(folder_path)
            if not path.exists():
                return 0
                
            total_size = 0
            for path in Path(folder_path).rglob('*'):
                if path.is_file():
                    total_size += path.stat().st_size
                    
            return round(total_size / (1024 * 1024), 2)  # Convert to MB
        except Exception as e:
            logger.error(f"Error calculating folder size: {str(e)}")
            return 0
            
    def get_library_dataframe(self):
        """Convert library to pandas DataFrame for UI display"""
        try:
            if not self.library:
                # Return empty dataframe with column headers
                return pd.DataFrame(columns=["App ID", "Name", "Location", "Size", "Last Played"])
                
            data = []
            for app_id, game in self.library.items():
                last_played = "Never" if not game['last_played'] else time.strftime(
                    "%Y-%m-%d %H:%M", time.localtime(game['last_played'])
                )
                
                data.append([
                    app_id,
                    game['name'],
                    game['location'],
                    f"{game['size']} MB",
                    last_played
                ])
                
            return pd.DataFrame(data, columns=["App ID", "Name", "Location", "Size", "Last Played"])
            
        except Exception as e:
            logger.error(f"Error creating library dataframe: {str(e)}")
            return pd.DataFrame(columns=["App ID", "Name", "Location", "Size", "Last Played"])

# Singleton instance
_instance = None

def get_library_manager():
    """Get the singleton library manager instance"""
    global _instance
    if _instance is None:
        _instance = LibraryManager()
    return _instance

if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    lib = get_library_manager()
    print(f"Library contains {len(lib.get_all_games())} games") 