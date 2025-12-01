#!/bin/bash
# refactor-commands-builder.sh
# Refactor command IDs and view IDs from 'ultrarepo.' to 'builder.'
# Usage: bash refactor-commands-builder.sh <kilocode-src-dir>

set -e
SRC_DIR="$1"
if [ -z "$SRC_DIR" ]; then
  echo "Usage: bash $0 <kilocode-src-dir>" >&2
  exit 1
fi

echo "🔧 Refactoring command IDs in $SRC_DIR..."

# 1. Patch package.json
PACKAGE_JSON="$SRC_DIR/package.json"
if [ -f "$PACKAGE_JSON" ]; then
  # Replace ultrarepo. with builder. in command IDs and view IDs
  # We use a temporary file
  # Exclude ultrarepo.com by matching ultrarepo. followed by a capital letter or specific lowercase words
  # Actually, command IDs are camelCase or lowercase.
  # Let's be specific about the patterns we saw in grep.
  
  # Replace "ultrarepo." with "builder." globally, but revert "builder.com" to "ultrarepo.com"
  sed -i '' 's/ultrarepo\./builder./g' "$PACKAGE_JSON"
  sed -i '' 's/builder\.com/ultrarepo.com/g' "$PACKAGE_JSON"
  
  # Replace "UltraRepo.ultrarepo" with "AirVeo.builder"
  sed -i '' 's/UltraRepo\.ultrarepo/AirVeo.builder/g' "$PACKAGE_JSON"
  
  echo "Patched $PACKAGE_JSON"
fi

# 2. Patch extension.ts
EXTENSION_TS="$SRC_DIR/extension.ts"
if [ -f "$EXTENSION_TS" ]; then
  # Replace ultrarepo. with builder.
  sed -i '' 's/ultrarepo\./builder./g' "$EXTENSION_TS"
  sed -i '' 's/builder\.com/ultrarepo.com/g' "$EXTENSION_TS"
  
  # Replace UltraRepo.ultrarepo
  sed -i '' 's/UltraRepo\.ultrarepo/AirVeo.builder/g' "$EXTENSION_TS"
  
  # Replace ultrarepoHomePanel with builderHomePanel (variable name/view type)
  sed -i '' 's/ultrarepoHomePanel/builderHomePanel/g' "$EXTENSION_TS"
  
  echo "Patched $EXTENSION_TS"
fi

# 3. Patch registerCommands.ts (if it contains hardcoded strings, though it mostly uses getCommand)
# Just in case
REGISTER_COMMANDS="$SRC_DIR/activate/registerCommands.ts"
if [ -f "$REGISTER_COMMANDS" ]; then
  sed -i '' 's/ultrarepo\./builder./g' "$REGISTER_COMMANDS"
  sed -i '' 's/builder\.com/ultrarepo.com/g' "$REGISTER_COMMANDS"
  echo "Patched $REGISTER_COMMANDS"
fi

echo "✅ Command refactoring complete."
