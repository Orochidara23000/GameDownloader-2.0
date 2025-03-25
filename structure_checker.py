#!/usr/bin/env python3
"""
Application Structure Checker
"""

import os
import sys
import importlib
import traceback

def print_separator():
    print("-" * 80)

def check_python_path():
    """Check and fix Python path if needed"""
    print("Checking Python path:")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}")
    
    if current_dir not in sys.path:
        print("  WARNING: Current directory not in Python path")
        sys.path.insert(0, current_dir)
        print("  Added current directory to Python path")

def check_imports():
    """Check if core modules can be imported"""
    print("Testing imports:")
    modules = [
        'config',
        'steamcmd_manager',
        'download_manager',
        'library_manager',
        'steam_api'
    ]
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  OK: {module} imports successfully")
        except ImportError as e:
            print(f"  ERROR: Failed to import {module}: {str(e)}")
            traceback.print_exc()

def main():
    print_separator()
    print("STEAM GAMES DOWNLOADER - STRUCTURE CHECKER")
    print_separator()
    
    check_python_path()
    print_separator()
    
    check_imports()
    print_separator()
    
    print("Check complete!")

if __name__ == "__main__":
    sys.exit(main())