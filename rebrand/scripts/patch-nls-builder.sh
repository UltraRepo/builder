#!/bin/bash
# patch-nls-builder.sh
# Patch all package.nls.*.json files and package.json to use UltraRepo Builder branding.
# Usage: bash patch-nls-builder.sh <kilocode-src-dir>

set -e
SRC_DIR="$1"
if [ -z "$SRC_DIR" ]; then
  echo "Usage: bash $0 <kilocode-src-dir>" >&2
  exit 1
fi

# Patch all localization files
for f in "$SRC_DIR"/package.nls*.json; do
  if [ -f "$f" ]; then
    # Use jq to update the fields in-place
    tmp=$(mktemp)
    # Update specific fields
    jq '.["extension.displayName"] = "UltraRepo App Builder" | .["extension.description"] = "AI App Development Assistant"' "$f" > "$tmp" && mv "$tmp" "$f"
    
    # Global replace of "UltraRepo" with "UltraRepo" in values
    # We use sed on the file content for this, as it's easier than mapping every key in jq
    # We use a temporary file for sed output
    sed -i '' 's/"UltraRepo"/"UltraRepo"/g' "$f"
    sed -i '' 's/"UltraRepo:/"UltraRepo:/g' "$f"
    
    echo "Patched $f"
  fi
done

# Patch the main package.json to use UltraRepo Builder extension ID
PACKAGE_JSON="$SRC_DIR/package.json"
if [ -f "$PACKAGE_JSON" ]; then
  tmp=$(mktemp)
  jq '.name = "builder" | .publisher = "UltraRepo"' "$PACKAGE_JSON" > "$tmp" && mv "$tmp" "$PACKAGE_JSON"
  echo "Patched $PACKAGE_JSON - set UltraRepo Builder extension ID (UltraRepo.builder)"
fi
