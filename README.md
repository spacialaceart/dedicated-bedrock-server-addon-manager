# Minecraft Bedrock Server Pack Manager

A utility to automatically scan and sync your Minecraft Bedrock world's resource and behavior packs.

**Tested on:** Minecraft Bedrock Server version 1.21.131.1. Doesn't work for Java.

> **Note:** You still have to manually add the resource/behavior packs to the folders. This tool (for now) only scans and syncs the JSON files.

## What It Does

- Scans `resource_packs/` and `behavior_packs/` folders for `manifest.json` files
- Extracts `uuid` and `version` from each pack's manifest
- Outputs to `world_resource_packs.json` and `world_behavior_packs.json`
- Detects and skips duplicate pack IDs
- Removes orphaned entries (packs listed in JSON but no longer have folders)
- Creates the JSON files if they don't exist

> **Download:** See [Releases](../../releases) on the right for the `.exe` file.

## Usage

1. Download `ScanPacks.exe` from [Releases](../../releases)
2. Place it in your world folder (same level as `level.dat`):

```
worlds/
└── YourWorldName/
    ├── level.dat
    ├── behavior_packs/
    ├── resource_packs/
    └── ScanPacks.exe  <-- Place here
```

3. Double-click `ScanPacks.exe`
4. Done!

## Output Format

The scripts generate JSON files in this format:

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
  Minecraft Bedrock Pack Scanner
============================================================

Working directory: C:\...\worlds\Bedrock level

Scanning resource packs in: C:\...\worlds\Bedrock level\resource_packs

  [OK] Multiplayer Waypoint System! RP: xxxxxx-... v1.0.23
  [OK] World Map RP: c62bb4f5-... v1.2.7
  [SKIP] Some Folder: No manifest.json found
  [DUPLICATE] Another Pack: pack_id abc123... already exists

Removed orphaned entries:
  [REMOVED] old-pack-id-no-longer-exists

--------------------------------------------------
Resource Packs Summary:
  Processed: 9 packs
  Duplicates: 0
  Skipped: 1
  Removed: 1 orphaned entries
  Total in output: 9
  Updated: world_resource_packs.json

============================================================
  Scan complete!
============================================================
```

## For Developers

*Regular users can ignore this section.*

### Requirements

- Python 3.6 or newer
- No external dependencies (uses only standard library)

### Run as Python Script

```powershell
# Scan both resource and behavior packs
python scan_packs.py

# Or scan individually
python scan_resource_packs.py
python scan_behavior_packs.py
```

### Build Your Own .exe

```powershell
# Install PyInstaller (one time)
pip install pyinstaller

# Create the exe
pyinstaller --onefile --name "ScanPacks" scan_packs.py

# Move from dist/ folder to world folder
move dist\ScanPacks.exe .
```

## Feature Requests / Issues

Want to request a feature or report a bug?
- Open an issue on [GitHub](../../issues)
- DM me on Discord: **zegrassreturns**

---

*Not affiliated with any packs mentioned nor Mojang.*

