#!/usr/bin/env python3
"""Script to export the current database and uploaded images for transfer to another system"""

import sqlite3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

def export_system_data():
    """Export the current database and uploaded images"""
    
    print("Exporting Smart Farmer Marketplace data...")
    
    # Create export directory
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_subdir = export_dir / f"export_{timestamp}"
    export_subdir.mkdir(exist_ok=True)
    
    # Export database
    db_source = "instance/database.db"
    db_dest = export_subdir / "database.db"
    
    if os.path.exists(db_source):
        # Create instance directory in export if it doesn't exist
        (export_subdir / "instance").mkdir(exist_ok=True)
        db_dest = export_subdir / "instance" / "database.db"
        shutil.copy2(db_source, db_dest)
        print(f"Copied database: {db_source} -> {db_dest}")
    else:
        print(f"Warning: Database {db_source} not found")
    
    # Export uploaded images
    uploads_source = Path("static/images/uploads")
    uploads_dest = export_subdir / "uploads"
    
    if uploads_source.exists():
        shutil.copytree(uploads_source, uploads_dest, dirs_exist_ok=True)
        print(f"Copied uploaded images: {uploads_source} -> {uploads_dest}")
    else:
        print(f"Warning: Uploads directory {uploads_source} not found")
        uploads_dest.mkdir(exist_ok=True)  # Create empty directory
    
    # Create manifest file
    manifest = {
        "export_timestamp": timestamp,
        "database_exists": os.path.exists(db_source),
        "uploads_exists": uploads_source.exists(),
        "uploads_count": len(list(uploads_dest.glob("*"))) if uploads_dest.exists() else 0,
        "version": "1.0"
    }
    
    manifest_file = export_subdir / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Created manifest: {manifest_file}")
    print(f"\nExport completed! Files saved to: {export_subdir}")
    print(f"\nTo transfer to another system:")
    print(f"1. Copy the '{export_subdir}' folder to the new system")
    print(f"2. Run 'python export_data.py import {export_subdir.name}' on the new system")

def import_system_data(export_folder_name):
    """Import database and uploaded images from exported data"""
    
    print(f"Importing Smart Farmer Marketplace data from {export_folder_name}...")
    
    export_path = Path("exports") / export_folder_name
    
    if not export_path.exists():
        print(f"Error: Export folder '{export_path}' not found!")
        return False
    
    # Load manifest
    manifest_file = export_path / "manifest.json"
    if not manifest_file.exists():
        print(f"Error: Manifest file '{manifest_file}' not found!")
        return False
    
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)
    
    print(f"Manifest loaded: {manifest}")
    
    # Import database
    db_source = export_path / "instance" / "database.db"
    db_dest = Path("instance/database.db")
    
    if db_source.exists():
        # Create instance directory if it doesn't exist
        Path("instance").mkdir(exist_ok=True)
        if db_dest.exists():
            backup_name = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db_dest, backup_name)
            print(f"Backed up existing database to: {backup_name}")
        
        shutil.copy2(db_source, db_dest)
        print(f"Copied database: {db_source} -> {db_dest}")
    else:
        print(f"Warning: Database file not found in export: {db_source}")
    
    # Import uploaded images
    uploads_source = export_path / "uploads"
    uploads_dest = Path("static/images/uploads")
    
    if uploads_source.exists():
        # Create destination directory if it doesn't exist
        uploads_dest.mkdir(parents=True, exist_ok=True)
        
        # Copy all files from source to destination
        for file_path in uploads_source.iterdir():
            if file_path.is_file():
                dest_file = uploads_dest / file_path.name
                shutil.copy2(file_path, dest_file)
                print(f"Copied image: {file_path.name} -> {dest_file}")
        
        print(f"Imported uploaded images from: {uploads_source}")
    else:
        print(f"Warning: Uploads directory not found in export: {uploads_source}")
    
    print("\nImport completed successfully!")
    print("You can now start the application with your preserved data.")
    return True

def list_exports():
    """List available exports"""
    export_dir = Path("exports")
    if not export_dir.exists():
        print("No exports directory found.")
        return
    
    exports = list(export_dir.iterdir())
    if not exports:
        print("No exports found.")
        return
    
    print("Available exports:")
    for exp in sorted(exports):
        if exp.is_dir():
            manifest_file = exp / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                print(f"- {exp.name} ({manifest.get('export_timestamp', 'unknown')})")
            else:
                print(f"- {exp.name} (no manifest)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Smart Farmer Marketplace Data Export/Import Tool")
        print("Usage:")
        print("  python export_data.py export           - Export current data")
        print("  python export_data.py import <folder>  - Import data from folder")
        print("  python export_data.py list             - List available exports")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "export":
        export_system_data()
    elif command == "import":
        if len(sys.argv) < 3:
            print("Error: Please specify the export folder name")
            print("Usage: python export_data.py import <folder>")
            sys.exit(1)
        import_system_data(sys.argv[2])
    elif command == "list":
        list_exports()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: export, import, list")
        sys.exit(1)