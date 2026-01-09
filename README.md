# Minecraft Self-hosted Bedrock Server Pack Manager

A utility to automatically scan and sync your Minecraft Bedrock world's resource and behavior packs.

**Tested on:** Minecraft Bedrock Server version 1.21.131.1. Doesn't work for Java.

## What It Does

### Addon Manager (`addon_manager.py`)
- Extracts `.mcaddon` and `.mcpack` files from `downloaded_addons/`
- Routes extracted packs to `behavior_packs/` or `resource_packs/` based on folder naming
- Scans all packs and generates `world_resource_packs.json` and `world_behavior_packs.json`
- Reports folders missing `manifest.json` (these won't work in-game)

### Pack Scanner (`scan_packs.py`)
- Scans `resource_packs/` and `behavior_packs/` folders for `manifest.json` files
- Extracts `uuid` and `version` from each pack's manifest
- Outputs to `world_resource_packs.json` and `world_behavior_packs.json`
- Detects and skips duplicate pack IDs
- Removes orphaned entries (packs listed in JSON but no longer have folders)
- Creates the JSON files if they don't exist

### Addon Extractor (`scan_downloaded_addons.py`)
- Extracts both `.mcaddon` and `.mcpack` files from `downloaded_addons/`
- Auto-detects pack type from folder naming (BP/RP suffixes)
- Prompts for manual selection when auto-detection fails
- Handles conflicts with existing folders

> **Download:** See [Releases](../../releases) on the right for the `.exe` file.

## Usage

1. Download from [Releases](../../releases)
2. Place in your world folder (same level as `level.dat`)
3. Create new folder named downloaded_addons:

```
worlds/
└── YourWorldName/
    ├── level.dat
    ├── behavior_packs/
    ├── resource_packs/
    ├── downloaded_addons/     <-- Put .mcaddon/.mcpack files here
    └── AddonManager.exe       <-- Place here
```

3. Double-click `AddonManager.exe`
4. Done!

## Output Format

The scripts edits the world_behavior_packs or world_resource_packs JSON files in this format:

```json
[
  {
    "pack_id": "xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx",
    "version": [1, 0, 23]
  },
  {
    "pack_id": "xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx",
    "version": [1, 2, 7]
  }
]
```

## Sample Console Output

```
============================================================
  Minecraft Bedrock Addon Manager
============================================================

Working directory: C:\...\worlds\Bedrock level

============================================================
  STEP 1: Extracting Downloaded Addons
============================================================

Found 2 .mcaddon file(s):
  - CoolAddon.mcaddon
  - AnotherPack.mcaddon

--------------------------------------------------
Processing .mcaddon files...

  Extracting: CoolAddon.mcaddon
    [OK] CoolAddon BP -> behavior_packs/CoolAddon BP
    [OK] CoolAddon RP -> resource_packs/CoolAddon RP

--------------------------------------------------
Cleaning up temp folder...
  [OK] Temp folder deleted

--------------------------------------------------
Extraction Summary:
  .mcaddon files processed: 2
  .mcpack files processed: 0
  Behavior packs moved: 2
  Resource packs moved: 2
  Skipped: 0
  Errors: 0

============================================================
  STEP 2: Scanning Pack Directories
============================================================

Scanning resource packs in: C:\...\worlds\Bedrock level\resource_packs

  [OK] CoolAddon RP: xxxxxx-... v1.0.0
  [OK] World Map RP: c62bb4f5-... v1.2.7

--------------------------------------------------
Resource Packs Summary:
  Processed: 2 packs
  Duplicates: 0
  Skipped: 0
  Removed: 0 orphaned entries
  Total in output: 2
  Updated: world_resource_packs.json

Scanning behavior packs in: C:\...\worlds\Bedrock level\behavior_packs

  [OK] CoolAddon BP: yyyyyy-... v1.0.0
  [SKIP] Broken Folder: No manifest.json found

--------------------------------------------------
Behavior Packs Summary:
  Processed: 1 packs
  Duplicates: 0
  Skipped: 1
  Removed: 0 orphaned entries
  Total in output: 1
  Updated: world_behavior_packs.json

============================================================
  Folders Missing manifest.json (Won't Work In-Game)
============================================================

behavior_packs/ (1 folder(s)):
  [!] Broken Folder

Total: 1 folder(s) without manifest.json
These folders will NOT be recognized by Minecraft.

============================================================
  Addon Manager Complete!
============================================================

What was done:
  - Extracted 2 addon file(s) -> 4 pack(s)
  - Synced world_resource_packs.json with resource_packs/
  - Synced world_behavior_packs.json with behavior_packs/
  - Found 1 folder(s) without manifest.json

Current packs in resource_packs/ (2):
  - CoolAddon RP
  - World Map RP

Current packs in behavior_packs/ (2):
  - Broken Folder
  - CoolAddon BP

NOTE: Auto-detection for pack types is based on folder naming
patterns and is NOT guaranteed to be 100% accurate.

Press Enter to exit...
```

## For Developers

*Regular users can ignore this section.*

### Requirements

- Python 3.6 or newer
- No external dependencies (uses only standard library)

### Run as Python Script

```powershell
# Full addon management (extract + scan + report)
python addon_manager.py

# Or individual scripts:
python scan_packs.py              # Scan packs only
python scan_downloaded_addons.py  # Extract addons only
python scan_resource_packs.py     # Scan resource packs only
python scan_behavior_packs.py     # Scan behavior packs only
```

### Build Your Own .exe

```powershell
# Install PyInstaller (one time)
pip install pyinstaller

# Create the addon manager exe (recommended)
pyinstaller --onefile --name "AddonManager" addon_manager.py

# Move from dist/ folder to world folder
move dist\AddonManager.exe .
```

## Planned Features

- **Config file for pack management**
  - Track which `.mcaddon`/`.mcpack` files correspond to which installed packs
  - Remember pack_id mappings for behavior and resource packs
  - Manual matching for packs that can't be auto-detected

- **Pack deletion via script**
  - Remove packs from `behavior_packs/` and `resource_packs/` folders
  - Automatically update JSON files when packs are removed
  - Batch delete multiple packs at once

- **GUI (Graphical User Interface)**
  - Visual pack browser with drag-and-drop support
  - One-click extraction and installation
  - Easy pack enable/disable toggling
  - Visual conflict resolution

## Feature Requests / Issues

Want to request a feature or report a bug?
- Open an issue on [GitHub](../../issues)
- DM me on Discord: **zegrassreturns**

---

*Not affiliated with any packs mentioned nor Mojang.*

