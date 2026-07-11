#!/usr/bin/env python3
"""Enhanced database initialization script that can preserve existing data or initialize fresh"""

import os
import sys
from pathlib import Path

def check_existing_db():
    """Check if database already exists"""
    return os.path.exists("smart_farmer.db")

def init_fresh():
    """Initialize with fresh sample data (original behavior)"""
    print("Initializing with fresh sample data...")
    os.system("python db_init.py")

def init_with_preserved_data():
    """Initialize system but preserve existing database and images if they exist"""
    print("Preserving existing data and initializing system...")
    
    # Check if we have existing database and uploads
    has_db = os.path.exists("smart_farmer.db")
    has_uploads = os.path.exists("static/images/uploads")
    
    if has_db:
        print("Found existing database, preserving it...")
    else:
        print("No existing database found, creating fresh...")
        os.system("python db_init.py")
        return
    
    if has_uploads:
        print("Found existing uploads, preserving them...")
    else:
        print("Creating uploads directory...")
        os.makedirs("static/images/uploads", exist_ok=True)
    
    print("System initialized with preserved data!")

def main():
    print("Smart Farmer Marketplace - Enhanced Initialization")
    print("="*50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--fresh":
            init_fresh()
        elif sys.argv[1] == "--preserve":
            init_with_preserved_data()
        else:
            print("Usage:")
            print("  python init_with_data.py               - Auto-detect and preserve if possible")
            print("  python init_with_data.py --fresh      - Force fresh initialization")
            print("  python init_with_data.py --preserve   - Preserve existing data")
    else:
        # Auto-detect: if database exists, preserve it; otherwise, create fresh
        if check_existing_db():
            print("Existing database detected. Preserving current data...")
            init_with_preserved_data()
        else:
            print("No existing database found. Creating fresh data...")
            init_fresh()

if __name__ == "__main__":
    main()