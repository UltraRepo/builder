#!/bin/bash
# build-airveo-complete.sh
# Complete AirVeo Builder build with proper branding, command refactoring, and icon restoration
# Usage: bash build-airveo-complete.sh

set -e

# Define all script paths before changing directories
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REBRAND_WEBVIEWS_SCRIPT="$SCRIPT_DIR/rebrand-webviews-builder.sh"
PATCH_NLS_SCRIPT="$SCRIPT_DIR/patch-nls-builder.sh"
REBRAND_SCRIPT="$SCRIPT_DIR/icon-rebrand-builder.sh"

ROOT="$(cd "$(dirname "$0")/../../build/kilocode" && pwd)"
cd "$ROOT"

echo "🚀 Starting complete AirVeo Builder build process..."
echo "📁 Build directory: $ROOT"

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install

# --- Step 0: Apply AirVeo Builder webview and file rebranding ---
if [ -x "$REBRAND_WEBVIEWS_SCRIPT" ]; then
  echo ""
  echo "🎨 Step 0: Applying AirVeo Builder webview and file rebranding..."
  NO_BACKUP=true bash "$REBRAND_WEBVIEWS_SCRIPT"
else
  echo "[WARN] Webview rebranding script not found or not executable: $REBRAND_WEBVIEWS_SCRIPT"
fi

# --- Step 1: Apply AirVeo Builder branding (extension ID, display name) ---
SRC_DIR="$ROOT/src"
if [ -x "$PATCH_NLS_SCRIPT" ]; then
  echo ""
  echo "🏷️  Step 1: Applying AirVeo Builder branding..."
  bash "$PATCH_NLS_SCRIPT" "$SRC_DIR"
else
  echo "[ERROR] AirVeo Builder branding script not found or not executable: $PATCH_NLS_SCRIPT"
  exit 1
fi

# --- Step 1.5: Refactor command IDs (ultrarepo. -> builder.) ---
REFACTOR_COMMANDS_SCRIPT="$SCRIPT_DIR/refactor-commands-builder.sh"
if [ -x "$REFACTOR_COMMANDS_SCRIPT" ]; then
  echo ""
  echo "🔧 Step 1.5: Refactoring command IDs..."
  bash "$REFACTOR_COMMANDS_SCRIPT" "$SRC_DIR"
else
  echo "[WARN] Command refactoring script not found or not executable: $REFACTOR_COMMANDS_SCRIPT"
fi

# --- Step 2: Apply AirVeo Builder icon rebranding BEFORE building ---
SRC_ICONS_DIR="$ROOT/src/assets/icons"
SRC_IMAGES_DIR="$ROOT/src/assets/images"
if [ -x "$REBRAND_SCRIPT" ]; then
  echo ""
  echo "🎨 Step 2: Applying AirVeo Builder icon rebranding (src/assets/icons & src/assets/images)..."
  bash "$REBRAND_SCRIPT" "$SRC_ICONS_DIR"
  if [ -d "$SRC_IMAGES_DIR" ]; then
    bash "$REBRAND_SCRIPT" "$SRC_IMAGES_DIR"
  fi
else
  echo "[WARN] Icon rebrand script not found or not executable: $REBRAND_SCRIPT"
fi

# --- Step 3: Force clean build to avoid cache issues ---
echo ""
echo "🧹 Step 3: Cleaning previous build artifacts..."
pnpm run clean

# --- Step 4: Build the extension ---
echo ""
echo "🔨 Step 4: Building extension..."
pnpm build

# --- Step 5: Find and package the built VSIX ---
VSIX_ORIG=$(ls -1v bin/*.vsix 2>/dev/null | tail -n1)
if [ -z "$VSIX_ORIG" ]; then
  VSIX_ORIG=$(ls -1v dist/*.vsix 2>/dev/null | tail -n1)
fi
if [ -z "$VSIX_ORIG" ]; then
  echo "[ERROR] No .vsix file found after build!" >&2
  exit 1
fi

# Get version from src/package.json
VERSION=$(jq -r .version src/package.json)

# Ensure dist directory exists
mkdir -p dist

# Copy/rename to dist/airveo-$VERSION.vsix
VSIX_OUT="dist/airveo-$VERSION.vsix"
if [ "$VSIX_ORIG" != "$VSIX_OUT" ]; then
  mv "$VSIX_ORIG" "$VSIX_OUT"
fi

# --- Step 6: Apply icon rebranding to build assets (if needed) ---
ASSETS_DIR="$ROOT/assets/icons"
if [ -x "$REBRAND_SCRIPT" ] && [ -d "$ASSETS_DIR" ]; then
  echo ""
  echo "🎨 Step 6: Applying AirVeo Builder icon rebranding (build assets)..."
  bash "$REBRAND_SCRIPT" "$ASSETS_DIR"
fi

echo ""
echo "🎉 AirVeo Builder build complete!"
echo ""
echo "📦 VSIX Output: $VSIX_OUT"
echo "🏷️  Extension ID: AirVeo.builder"
echo "📛 Display Name: AirVeo Builder"
echo "🎨 Icons: AirVeo Builder branded"
echo "⚙️  Commands: builder.* prefixed"
echo ""
echo "🔍 To install and test:"
echo "   code --install-extension $VSIX_OUT"
echo ""
echo "⚠️  Note: If you had UltraRepo.ultrarepo installed, you may need to:"
echo "   1. Uninstall the old extension first"
echo "   2. Reload VS Code after installation"
echo "   3. Test all functionality with new builder.* commands"
echo ""
