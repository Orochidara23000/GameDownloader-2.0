#!/usr/bin/env python3
"""
Import Fixer Script
Simplified version since we're using a flat structure
"""

import os
import re
import glob

def fix_file_imports(file_path):
    """Clean up imports in a single file"""
    print(f"Processing file: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove any relative imports from old structure
    content = re.sub(r'from \.(ui|modules|utils)', 'from', content)
    content = re.sub(r'from (ui|modules|utils)\.', 'from ', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("Fixing imports in Python files...")
    
    # Process all Python files in current directory
    for py_file in glob.glob("*.py"):
        if py_file not in ['import_fixer.py', 'structure_checker.py']:
            fix_file_imports(py_file)
    
    print("Import fixes completed!")

if __name__ == "__main__":
    main()