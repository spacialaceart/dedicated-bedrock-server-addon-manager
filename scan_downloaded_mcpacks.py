#!/usr/bin/env python3
"""
Minecraft Bedrock .mcpack Extractor

Scans the downloaded_addons directory for .mcpack files, extracts them,
and routes the pack to the appropriate directory (resource_packs or behavior_packs)
based on folder naming conventions.

NOTE: Auto-detection is based on folder naming patterns and is NOT guaranteed
to be 100% accurate. Please double-check the results after running.
"""

import re
import shutil
import sys
import zipfile
from pathlib import Path


# Regex patterns for pack type detection (case-insensitive)
# Match suffixes like: " BP", "_BP", "-BP", " B", " Behavior Pack", etc.
BEHAVIOR_PATTERN = re.compile(r'[\s_-]?(BP|BH|Behavior\s*Pack|B)$', re.IGNORECASE)
RESOURCE_PATTERN = re.compile(r'[\s_-]?(RP|RS|Resource\s*Pack|R)$', re.IGNORECASE)


def get_script_dir():
    """Get the directory where the script/exe is located."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return Path(sys.executable).parent.resolve()
    else:
        # Running as script
        return Path(__file__).parent.resolve()


def detect_pack_type(folder_name: str) -> str | None:
    """
    Detect pack type from folder name using regex patterns.
    
    Returns:
        'behavior' for behavior packs
        'resource' for resource packs
        None if no match found
    """
    if BEHAVIOR_PATTERN.search(folder_name):
        return 'behavior'
    elif RESOURCE_PATTERN.search(folder_name):
        return 'resource'
    return None


def prompt_pack_type(folder_name: str) -> str | None:
    """
    Prompt user to select pack type when auto-detection fails.
    
    Returns:
        'behavior', 'resource', or None to skip
    """
    print(f"\n  Cannot auto-detect pack type for: {folder_name}")
    print("  Select destination:")
    print("    [1] behavior_packs")
    print("    [2] resource_packs")
    print("    [S] Skip this pack")
    
    while True:
        choice = input("  Enter choice (1/2/S): ").strip().upper()
        if choice == '1':
            return 'behavior'
        elif choice == '2':
            return 'resource'
        elif choice == 'S':
            return None
        else:
            print("  Invalid choice. Please enter 1, 2, or S.")


def prompt_conflict_resolution(folder_name: str, destination: str) -> str:
    """
    Prompt user to resolve folder conflict.
    
    Returns:
        'overwrite', 'skip', or 'rename'
    """
    print(f"\n  Conflict: '{folder_name}' already exists in {destination}")
    print("  Choose action:")
    print("    [O] Overwrite existing folder")
    print("    [S] Skip (keep existing)")
    print("    [R] Rename new folder")
    
    while True:
        choice = input("  Enter choice (O/S/R): ").strip().upper()
        if choice == 'O':
            return 'overwrite'
        elif choice == 'S':
            return 'skip'
        elif choice == 'R':
            return 'rename'
        else:
            print("  Invalid choice. Please enter O, S, or R.")


def get_unique_folder_name(destination_dir: Path, base_name: str) -> str:
    """Generate a unique folder name by appending a suffix."""
    counter = 1
    new_name = f"{base_name}_{counter}"
    while (destination_dir / new_name).exists():
        counter += 1
        new_name = f"{base_name}_{counter}"
    return new_name


def move_folder_to_destination(source: Path, destination_dir: Path, folder_name: str) -> tuple[bool, str]:
    """
    Move a folder to destination, handling conflicts.
    
    Returns:
        (success: bool, final_name: str)
    """
    dest_path = destination_dir / folder_name
    
    if dest_path.exists():
        action = prompt_conflict_resolution(folder_name, destination_dir.name)
        
        if action == 'skip':
            return False, folder_name
        elif action == 'overwrite':
            shutil.rmtree(dest_path)
        elif action == 'rename':
            folder_name = get_unique_folder_name(destination_dir, folder_name)
            dest_path = destination_dir / folder_name
    
    shutil.move(str(source), str(dest_path))
    return True, folder_name


def extract_mcpack(mcpack_path: Path, temp_dir: Path) -> Path | None:
    """
    Extract .mcpack file to temp directory.
    
    Unlike .mcaddon files which contain multiple pack folders,
    .mcpack files contain a single pack's contents directly.
    
    Returns:
        Path to the extracted pack folder, or None if extraction failed
    """
    # Create a subfolder for this mcpack using its filename (without extension)
    extract_dir = temp_dir / mcpack_path.stem
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with zipfile.ZipFile(mcpack_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Check if contents are nested in a single subfolder or directly in extract_dir
        # Some .mcpack files have contents directly at root, others have them in a subfolder
        items = list(extract_dir.iterdir())
        
        if len(items) == 1 and items[0].is_dir():
            # Contents are in a single subfolder - return that folder
            return items[0]
        else:
            # Contents are directly in extract_dir - return extract_dir itself
            # The folder name will be based on the .mcpack filename
            return extract_dir
            
    except zipfile.BadZipFile:
        print(f"  [ERROR] {mcpack_path.name}: Not a valid ZIP/mcpack file")
    except Exception as e:
        print(f"  [ERROR] {mcpack_path.name}: Extraction failed - {e}")
    
    return None


def process_mcpack(mcpack_path: Path, temp_dir: Path, behavior_dir: Path, resource_dir: Path) -> dict:
    """
    Process a single .mcpack file.
    
    Returns:
        Dict with processing stats
    """
    stats = {
        'behavior_moved': 0,
        'resource_moved': 0,
        'skipped': 0,
        'errors': 0
    }
    
    print(f"\n  Extracting: {mcpack_path.name}")
    
    extracted_folder = extract_mcpack(mcpack_path, temp_dir)
    
    if not extracted_folder:
        print(f"  [ERROR] Failed to extract {mcpack_path.name}")
        stats['errors'] += 1
        return stats
    
    folder_name = extracted_folder.name
    pack_type = detect_pack_type(folder_name)
    
    if pack_type is None:
        # No auto-detection match, ask user to select
        pack_type = prompt_pack_type(folder_name)
    
    if pack_type is None:
        print(f"    [SKIP] {folder_name}: Skipped by user")
        stats['skipped'] += 1
        return stats
    
    if pack_type == 'behavior':
        destination_dir = behavior_dir
    else:
        destination_dir = resource_dir
    
    success, final_name = move_folder_to_destination(extracted_folder, destination_dir, folder_name)
    
    if success:
        print(f"    [OK] {folder_name} -> {destination_dir.name}/{final_name}")
        if pack_type == 'behavior':
            stats['behavior_moved'] += 1
        else:
            stats['resource_moved'] += 1
    else:
        print(f"    [SKIP] {folder_name}: Kept existing")
        stats['skipped'] += 1
    
    return stats


def main():
    script_dir = get_script_dir()
    
    print("=" * 60)
    print("  Minecraft Bedrock .mcpack Extractor")
    print("=" * 60)
    print(f"\nWorking directory: {script_dir}")
    
    # Define directories
    downloaded_addons_dir = script_dir / "downloaded_addons"
    temp_dir = script_dir / "temp"
    behavior_dir = script_dir / "behavior_packs"
    resource_dir = script_dir / "resource_packs"
    
    # Check if downloaded_addons exists
    if not downloaded_addons_dir.exists():
        print(f"\nError: downloaded_addons directory not found at {downloaded_addons_dir}")
        print("Please create the folder and place .mcpack files inside.")
        input("\nPress Enter to exit...")
        return
    
    # Find all .mcpack files
    mcpack_files = list(downloaded_addons_dir.glob("*.mcpack"))
    
    if not mcpack_files:
        print(f"\nNo .mcpack files found in {downloaded_addons_dir}")
        input("\nPress Enter to exit...")
        return
    
    print(f"\nFound {len(mcpack_files)} .mcpack file(s):")
    for f in mcpack_files:
        print(f"  - {f.name}")
    
    # Create destination directories if they don't exist
    behavior_dir.mkdir(exist_ok=True)
    resource_dir.mkdir(exist_ok=True)
    
    # Create temp directory
    temp_dir.mkdir(exist_ok=True)
    
    # Process each .mcpack file
    total_stats = {
        'behavior_moved': 0,
        'resource_moved': 0,
        'skipped': 0,
        'errors': 0,
        'mcpacks_processed': 0
    }
    
    print(f"\n{'-'*50}")
    print("Processing .mcpack files...")
    
    for mcpack_path in mcpack_files:
        stats = process_mcpack(mcpack_path, temp_dir, behavior_dir, resource_dir)
        total_stats['behavior_moved'] += stats['behavior_moved']
        total_stats['resource_moved'] += stats['resource_moved']
        total_stats['skipped'] += stats['skipped']
        total_stats['errors'] += stats['errors']
        total_stats['mcpacks_processed'] += 1
    
    # Clean up temp directory
    print(f"\n{'-'*50}")
    print("Cleaning up temp folder...")
    try:
        shutil.rmtree(temp_dir)
        print("  [OK] Temp folder deleted")
    except Exception as e:
        print(f"  [WARN] Could not delete temp folder: {e}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  .mcpack files processed: {total_stats['mcpacks_processed']}")
    print(f"  Behavior packs moved: {total_stats['behavior_moved']}")
    print(f"  Resource packs moved: {total_stats['resource_moved']}")
    print(f"  Skipped: {total_stats['skipped']}")
    print(f"  Errors: {total_stats['errors']}")
    print("=" * 60)
    
    # Reminder note
    print("\nNOTE: Auto-detection is based on folder naming patterns and")
    print("is NOT guaranteed to be 100% accurate. Please double-check")
    print("the moved packs in behavior_packs/ and resource_packs/ folders.")
    
    # Pause so the user can see the output when running as exe
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()

