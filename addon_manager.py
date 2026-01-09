#!/usr/bin/env python3
"""
Minecraft Bedrock Addon Manager

Master script that combines:
1. Extraction of .mcaddon and .mcpack files from downloaded_addons/
2. Scanning of manifest.json files in behavior_packs/ and resource_packs/
3. Reporting of folders missing manifest.json (won't work in-game)

This is a unified workflow for managing Minecraft Bedrock addons.
"""

import json
import sys
from pathlib import Path

# Import from our other scripts
from scan_downloaded_addons import run_extraction
from scan_packs import scan_packs


def get_script_dir():
    """Get the directory where the script/exe is located."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return Path(sys.executable).parent.resolve()
    else:
        # Running as script
        return Path(__file__).parent.resolve()


def find_folders_without_manifest(packs_dir: Path) -> list[str]:
    """
    Find all folders in a packs directory that don't have manifest.json.
    
    Args:
        packs_dir: Path to the packs directory
    
    Returns:
        List of folder names without manifest.json
    """
    folders_without_manifest = []
    
    if not packs_dir.exists():
        return folders_without_manifest
    
    for folder in sorted(packs_dir.iterdir()):
        if not folder.is_dir():
            continue
        
        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            folders_without_manifest.append(folder.name)
    
    return folders_without_manifest


def report_missing_manifests(script_dir: Path) -> dict:
    """
    Report all folders that are missing manifest.json files.
    
    Returns:
        Dict with lists of problematic folders for each pack type
    """
    behavior_dir = script_dir / "behavior_packs"
    resource_dir = script_dir / "resource_packs"
    
    missing = {
        'behavior': find_folders_without_manifest(behavior_dir),
        'resource': find_folders_without_manifest(resource_dir)
    }
    
    total_missing = len(missing['behavior']) + len(missing['resource'])
    
    if total_missing > 0:
        print(f"\n{'='*60}")
        print("  Folders Missing manifest.json (Won't Work In-Game)")
        print("=" * 60)
        
        if missing['behavior']:
            print(f"\nbehavior_packs/ ({len(missing['behavior'])} folder(s)):")
            for folder in missing['behavior']:
                print(f"  [!] {folder}")
        
        if missing['resource']:
            print(f"\nresource_packs/ ({len(missing['resource'])} folder(s)):")
            for folder in missing['resource']:
                print(f"  [!] {folder}")
        
        print(f"\nTotal: {total_missing} folder(s) without manifest.json")
        print("These folders will NOT be recognized by Minecraft.")
    else:
        print(f"\n{'='*60}")
        print("  All pack folders have manifest.json - Good!")
        print("=" * 60)
    
    return missing


def main():
    script_dir = get_script_dir()
    
    print("=" * 60)
    print("  Minecraft Bedrock Addon Manager")
    print("=" * 60)
    print(f"\nWorking directory: {script_dir}")
    
    # =========================================================================
    # STEP 1: Extract downloaded addons
    # =========================================================================
    print(f"\n{'='*60}")
    print("  STEP 1: Extracting Downloaded Addons")
    print("=" * 60)
    
    extraction_stats = run_extraction(script_dir)
    
    # Print extraction summary if any files were processed
    if extraction_stats['mcaddons_processed'] > 0 or extraction_stats['mcpacks_processed'] > 0:
        print(f"\n{'-'*50}")
        print("Extraction Summary:")
        print(f"  .mcaddon files processed: {extraction_stats['mcaddons_processed']}")
        print(f"  .mcpack files processed: {extraction_stats['mcpacks_processed']}")
        print(f"  Behavior packs moved: {extraction_stats['behavior_moved']}")
        print(f"  Resource packs moved: {extraction_stats['resource_moved']}")
        print(f"  Skipped: {extraction_stats['skipped']}")
        print(f"  Errors: {extraction_stats['errors']}")
    
    # =========================================================================
    # STEP 2: Scan pack directories and generate JSON files
    # =========================================================================
    print(f"\n{'='*60}")
    print("  STEP 2: Scanning Pack Directories")
    print("=" * 60)
    
    # Define pack directories
    resource_packs_dir = script_dir / "resource_packs"
    behavior_packs_dir = script_dir / "behavior_packs"
    
    # Scan resource packs
    resource_output = script_dir / "world_resource_packs.json"
    print()
    scan_packs(resource_packs_dir, resource_output, "resource")
    
    print()
    
    # Scan behavior packs
    behavior_output = script_dir / "world_behavior_packs.json"
    scan_packs(behavior_packs_dir, behavior_output, "behavior")
    
    # =========================================================================
    # STEP 3: Report folders without manifest.json
    # =========================================================================
    missing_manifests = report_missing_manifests(script_dir)
    
    # =========================================================================
    # Final Summary
    # =========================================================================
    print(f"\n{'='*60}")
    print("  Addon Manager Complete!")
    print("=" * 60)
    
    print("\nWhat was done:")
    if extraction_stats['mcaddons_processed'] > 0 or extraction_stats['mcpacks_processed'] > 0:
        total_files = extraction_stats['mcaddons_processed'] + extraction_stats['mcpacks_processed']
        total_packs = extraction_stats['behavior_moved'] + extraction_stats['resource_moved']
        print(f"  - Extracted {total_files} addon file(s) -> {total_packs} pack(s)")
    else:
        print("  - No addon files to extract")
    
    print("  - Synced world_resource_packs.json with resource_packs/")
    print("  - Synced world_behavior_packs.json with behavior_packs/")
    
    total_missing = len(missing_manifests['behavior']) + len(missing_manifests['resource'])
    if total_missing > 0:
        print(f"  - Found {total_missing} folder(s) without manifest.json")
    
    # List current folders in pack directories (final state)
    resource_folders = []
    behavior_folders = []
    
    if resource_packs_dir.exists():
        resource_folders = [f.name for f in sorted(resource_packs_dir.iterdir()) if f.is_dir()]
    if behavior_packs_dir.exists():
        behavior_folders = [f.name for f in sorted(behavior_packs_dir.iterdir()) if f.is_dir()]
    
    print(f"\nCurrent packs in resource_packs/ ({len(resource_folders)}):")
    if resource_folders:
        for folder in resource_folders:
            print(f"  - {folder}")
    else:
        print("  (none)")
    
    print(f"\nCurrent packs in behavior_packs/ ({len(behavior_folders)}):")
    if behavior_folders:
        for folder in behavior_folders:
            print(f"  - {folder}")
    else:
        print("  (none)")
    
    print("\nNOTE: Auto-detection for pack types is based on folder naming")
    print("patterns and is NOT guaranteed to be 100% accurate.")
    
    # Pause so the user can see the output when running as exe
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()

