# Rebrand Scripts for UltraRepo/KiloCode

## Overview
This document explains how the rebranding scripts work in the UltraRepo/KiloCode project and how they are integrated into the complete build process.

## Complete Build Process

The main build script is `rebrand/scripts/build-ultrarepo-complete.sh`, which orchestrates a 6-step rebranding and build process:

### Step 0: Webview and File Rebranding
- **Script**: `rebrand/scripts/rebrand-webviews.sh`
- **Purpose**: Copies all custom UltraRepo files from `rebrand/kilocode/*` to `build/kilocode/*`
- **Features**:
  - Preserves directory structure
  - Creates automatic backups (`.backup.[timestamp]`)
  - Handles webviews, documentation, and any custom files
- **Example**: `rebrand/kilocode/README.md` → `build/kilocode/README.md`

### Step 1: Extension Identity Rebranding
- **Script**: `rebrand/scripts/patch-nls-ultrarepo-proper.sh`
- **Purpose**: Updates extension identity and localization
- **Changes**:
  - Extension ID: `kilocode.kilo-code` → `UltraRepo.ultrarepo`
  - Publisher: `kilocode` → `UltraRepo`
  - Display name: Updates all 23+ language files to "UltraRepo AI Coder (KiloCode fork)"

### Step 2: Command Refactoring
- **Script**: `rebrand/scripts/refactor-kilocode-commands.sh`
- **Purpose**: Refactors all VS Code commands and contexts
- **Changes**:
  - Commands: `kilo-code.*` → `ultrarepo.*`
  - Ghost contexts: `kilocode.ghost.*` → `ultrarepo.ghost.*`
  - Walkthrough IDs: Updates to `ultrarepoWalkthrough`
  - Processes 25+ files including TypeScript, JSON, and built assets

### Step 3: Icon Rebranding
- **Script**: `rebrand/scripts/icon-rebrand.sh`
- **Purpose**: Replaces KiloCode icons with UltraRepo icons
- **Mapping**:
  - `kilo.png` → `icon.png`
  - `kilo-dark.svg` → `icon-dark.svg`
  - `kilo-light.svg` → `icon-light.svg`
  - `logo-outline-black.png` → `logo-outline-black.png`
- **Location**: `build/kilocode/src/assets/icons/`

### Step 4: Clean Build
- **Command**: `pnpm run clean`
- **Purpose**: Removes previous build artifacts to ensure clean compilation

### Step 5: Extension Build
- **Command**: `pnpm build`
- **Purpose**: Compiles and packages the extension
- **Output**: Creates `ultrarepo-4.83.1.vsix` in `build/kilocode/bin/`

### Step 6: Final Packaging
- **Purpose**: Copies VSIX to `build/kilocode/dist/` for distribution
- **Final Output**: `build/kilocode/dist/ultrarepo-4.83.1.vsix`

## Individual Scripts

### Core Rebranding Scripts

#### `rebrand-webviews.sh`
- **NEW**: Copies custom UltraRepo files and webviews
- **Usage**: `bash rebrand/scripts/rebrand-webviews.sh`
- **Features**: Automatic backup, directory creation, detailed logging

#### `patch-nls-ultrarepo-proper.sh`
- **Purpose**: Sets proper UltraRepo extension identity
- **Usage**: `bash rebrand/scripts/patch-nls-ultrarepo-proper.sh <src-dir>`
- **Key Change**: Creates `UltraRepo.ultrarepo` extension ID

#### `refactor-kilocode-commands.sh`
- **Purpose**: Updates all command IDs and references
- **Usage**: `bash rebrand/scripts/refactor-kilocode-commands.sh <src-dir>`
- **Scope**: 25+ files across TypeScript, JSON, and built assets

#### `icon-rebrand.sh`
- **Purpose**: Visual rebranding with UltraRepo icons
- **Usage**: `bash rebrand/scripts/icon-rebrand.sh <icons-dir>`
- **Safety**: Checks file existence before replacement

### Legacy Scripts

#### `patch-nls-ultrarepo.sh`
- **Status**: Legacy (maintains original `kilocode.kilo-code` ID)
- **Use Case**: For testing compatibility with original commands
- **Recommendation**: Use `patch-nls-ultrarepo-proper.sh` for production

## Integration with Build Process

### Automated Complete Build
```bash
bash rebrand/scripts/build-ultrarepo-complete.sh
```

This single command handles:
1. Dependency installation (`pnpm install`)
2. All 6 rebranding and build steps
3. Error handling and validation
4. Final VSIX packaging

### Manual Step-by-Step Build
```bash
# Step 0: Custom files
bash rebrand/scripts/rebrand-webviews.sh

# Step 1: Extension identity
bash rebrand/scripts/patch-nls-ultrarepo-proper.sh build/kilocode/src

# Step 2: Command refactoring
bash rebrand/scripts/refactor-kilocode-commands.sh build/kilocode/src

# Step 3: Icon rebranding
bash rebrand/scripts/icon-rebrand.sh build/kilocode/src/assets/icons

# Step 4-5: Build
cd build/kilocode
pnpm run clean
pnpm build
```

## File Backup System

All scripts create automatic backups:
- **Pattern**: `*.backup.[timestamp]`
- **Location**: Same directory as original file
- **Purpose**: Rollback capability if issues arise
- **Example**: `package.json.backup.1756010127`

## Troubleshooting

### Common Issues

1. **Script Not Executable**
   ```bash
   chmod +x rebrand/scripts/*.sh
   ```

2. **Missing Dependencies**
   ```bash
   cd build/kilocode && pnpm install
   ```

3. **Icons Not Changing**
   - Verify UltraRepo icons exist in `rebrand/assets/icons/`
   - Check script execution order (icon rebranding after file copying)
   - Ensure fresh VSIX installation

4. **Commands Not Working**
   - Verify extension ID changed to `UltraRepo.ultrarepo`
   - Check command refactoring completed successfully
   - Confirm VS Code extension reload

### Validation Commands

```bash
# Check extension identity
jq '.name, .publisher' build/kilocode/src/package.json

# Verify command refactoring
grep -c "ultrarepo\." build/kilocode/src/package.json

# Check icon replacement
ls -la build/kilocode/src/assets/icons/

# Verify final VSIX
ls -la build/kilocode/dist/
```

## Project Structure

```
rebrand/
├── scripts/
│   ├── build-ultrarepo-complete.sh    # Main automated build
│   ├── rebrand-webviews.sh            # Step 0: Custom files
│   ├── patch-nls-ultrarepo-proper.sh  # Step 1: Extension identity  
│   ├── refactor-kilocode-commands.sh  # Step 2: Command refactoring
│   ├── icon-rebrand.sh               # Step 3: Icon rebranding
│   └── patch-nls-ultrarepo.sh        # Legacy script
├── assets/icons/                      # UltraRepo branded icons
└── kilocode/                         # Custom UltraRepo files
    └── README.md                     # Example custom file
```

## Next Steps

1. **Add Custom Files**: Place any custom webviews or files in `rebrand/kilocode/`
2. **Run Complete Build**: Use `build-ultrarepo-complete.sh` for full automation
3. **Test Extension**: Install and verify all rebranding is applied correctly
4. **Iterate**: Add more custom files as needed for UltraRepo features
