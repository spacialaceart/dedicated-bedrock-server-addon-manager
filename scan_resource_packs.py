#!/usr/bin/env python3
"""
Resource Pack Manifest Scanner

Scans the resource_packs directory for manifest.json files,
extracts UUID and version from each, and outputs to world_resource_packs.json.
Also removes any orphaned pack_ids that no longer have folders.
"""

import json
from pathlib import Path


def scan_resource_packs():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()
    
    resource_packs_dir = script_dir / "resource_packs"
    output_file = script_dir / "world_resource_packs.json"
    
    if not resource_packs_dir.exists():
        print(f"Error: resource_packs directory not found at {resource_packs_dir}")
        return
    
    # Read existing JSON file to track removed entries
    existing_pack_ids = set()
    is_new_file = not output_file.exists()
    
    if not is_new_file:
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                for entry in existing_data:
                    if "pack_id" in entry:
                        existing_pack_ids.add(entry["pack_id"])
        except Exception as e:
            print(f"Warning: Could not read existing {output_file.name}: {e}")
    else:
        print(f"Note: {output_file.name} does not exist, will create new file.\n")
    
    results = []
    seen_pack_ids = set()
    processed_count = 0
    skipped_count = 0
    duplicate_count = 0
    
    print(f"Scanning resource packs in: {resource_packs_dir}\n")
    
    # Iterate through all subdirectories in resource_packs
    for folder in sorted(resource_packs_dir.iterdir()):
        if not folder.is_dir():
            continue
        
        manifest_path = folder / "manifest.json"
        
        if not manifest_path.exists():
            print(f"  [SKIP] {folder.name}: No manifest.json found")
            skipped_count += 1
            continue
        
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  [ERROR] {folder.name}: Invalid JSON - {e}")
            skipped_count += 1
            continue
        except Exception as e:
            print(f"  [ERROR] {folder.name}: Failed to read - {e}")
            skipped_count += 1
            continue
        
        # Extract header.uuid and header.version
        header = manifest.get("header", {})
        pack_id = header.get("uuid")
        version = header.get("version")
        
        if not pack_id:
            print(f"  [SKIP] {folder.name}: No uuid found in header")
            skipped_count += 1
            continue
        
        if not version:
            print(f"  [SKIP] {folder.name}: No version found in header")
            skipped_count += 1
            continue
        
        # Check for duplicates
        if pack_id in seen_pack_ids:
            print(f"  [DUPLICATE] {folder.name}: pack_id {pack_id} already exists")
            duplicate_count += 1
            continue
        
        # Add to results
        seen_pack_ids.add(pack_id)
        results.append({
            "pack_id": pack_id,
            "version": version
        })
        
        version_str = ".".join(map(str, version))
        print(f"  [OK] {folder.name}: {pack_id} v{version_str}")
        processed_count += 1
    
    # Find and report removed pack_ids (in old JSON but not in current folders)
    removed_pack_ids = existing_pack_ids - seen_pack_ids
    removed_count = len(removed_pack_ids)
    
    if removed_pack_ids:
        print(f"\nRemoved orphaned entries:")
        for pack_id in removed_pack_ids:
            print(f"  [REMOVED] {pack_id}")
    
    # Write output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Processed: {processed_count} packs")
    print(f"  Duplicates: {duplicate_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Removed: {removed_count} orphaned entries")
    print(f"  Total in output: {len(results)}")
    if is_new_file:
        print(f"\nCreated: {output_file}")
    else:
        print(f"\nUpdated: {output_file}")


if __name__ == "__main__":
    scan_resource_packs()
