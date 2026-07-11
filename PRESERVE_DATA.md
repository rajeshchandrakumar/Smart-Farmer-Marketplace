# Preserving Admin-Updated Images and Data

This document explains how to maintain your admin-updated product images and other data when moving the Smart Farmer Marketplace project to another system.

## The Issue
By default, when you run `db_init.py` on a new system, it recreates the database with only the original sample data, losing:
- Admin-updated product images
- Farmer-added products  
- Any other customizations made after initial setup

## Solution: Export and Import Tool

We've created a tool to help you preserve your data when moving between systems.

### Step 1: Export Data from Current System
On your current system, run:
```bash
python export_data.py export
```

This creates an export folder with:
- Current database (smart_farmer.db) containing all your updates
- Uploaded images in the static/images/uploads/ folder
- A manifest file with metadata

### Step 2: Transfer Files
Copy the entire `exports` folder to your new system.

### Step 3: Import Data on New System
On the new system, run:
```bash
python export_data.py import <export_folder_name>
```

Replace `<export_folder_name>` with the name of the export folder (e.g., `export_20260205_123045`).

### Step 4: Start the Application
Run the application normally:
```bash
python app.py
```

## Alternative: Enhanced Initialization

If you want to preserve existing data in the same location:
```bash
python init_with_data.py --preserve
```

This will keep existing database and uploaded images while ensuring the system structure is properly set up.

## Important Notes

1. **Always export before major changes** - Run the export command regularly to maintain current backups
2. **Upload directory structure** - The tool preserves the exact file structure of uploaded images
3. **Database consistency** - The exported database maintains all relationships between products, images, and other entities
4. **Backup existing data** - When importing, the tool backs up any existing database on the target system

## Checking Available Exports
To see what exports are available:
```bash
python export_data.py list
```

## Starting Fresh
If you need to start with completely fresh sample data:
```bash
python init_with_data.py --fresh
```

Using these tools, your admin-updated product images and all customizations will persist when moving the project to another system.