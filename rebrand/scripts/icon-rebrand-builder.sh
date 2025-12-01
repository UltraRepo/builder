#!/bin/bash

# icon-rebrand-builder.sh
# Rebrand KiloCode extension icons to UltraRepo Builder icons after VSIX build.
# Usage: bash icon-rebrand-builder.sh <path-to-extension-assets-folder>

set -e
REBRAND_ICONS="$(cd "$(dirname "$0")/../assets/icons" && pwd)"
TARGET_ICONS="$1"

if [ -z "$TARGET_ICONS" ]; then
  echo "Usage: bash $0 <path-to-extension-assets-folder>" >&2
  exit 1
fi

# Mapping: KiloCode icon name | UltraRepo Builder icon name (from rebrand/assets/icons)
MAPPING="
kilo.png|icon.png
kilo-dark.png|icon.png
kilo-light.svg|icon-light.svg
kilo-dark.svg|icon-dark.svg
icon-dark.svg|icon-dark.svg
icon-home.png|icon-home.png
logo-outline-black.gif|logo-outline-black.gif
logo-outline-yellow.gif|logo-outline-yellow.gif
logo-outline-black.png|logo-outline-black.png
icon.png|icon.png
"

# Check directories before running the loop
if [ ! -d "$REBRAND_ICONS" ]; then
  echo "[ERROR] Rebrand icons directory not found: $REBRAND_ICONS" >&2
  exit 2
fi
if [ ! -d "$TARGET_ICONS" ]; then
  echo "[ERROR] Target icons directory not found: $TARGET_ICONS" >&2
  exit 3
fi

echo "$MAPPING" | while IFS='|' read -r KILO_ICON BUILDER_ICON; do
  [ -z "$KILO_ICON" ] && continue
  SRC="$REBRAND_ICONS/$BUILDER_ICON"
  DEST="$TARGET_ICONS/$KILO_ICON"
  if [ -f "$SRC" ]; then
    cp "$SRC" "$DEST"
    echo "Replaced $DEST with $SRC"
  else
    echo "[WARN] UltraRepo Builder icon not found: $SRC (skipped $DEST)" >&2
  fi
done

# Repeat mapping into sibling images directory if it exists (for webviews using IMAGES_BASE_URI)
TARGET_IMAGES="${TARGET_ICONS%/icons}/images"
if [ -d "$TARGET_IMAGES" ]; then
  echo "$MAPPING" | while IFS='|' read -r KILO_ICON BUILDER_ICON; do
    [ -z "$KILO_ICON" ] && continue
    SRC="$REBRAND_ICONS/$BUILDER_ICON"
    DEST="$TARGET_IMAGES/$KILO_ICON"
    if [ -f "$SRC" ]; then
      cp "$SRC" "$DEST"
      echo "Replaced $DEST with $SRC"
    else
      echo "[WARN] UltraRepo Builder icon not found: $SRC (skipped $DEST)" >&2
    fi
  done
fi

# Always copy logo-outline-black.gif to both src/assets/icons and assets/icons
for ICONS_DIR in "$TARGET_ICONS" "${TARGET_ICONS/src\/assets\/icons/assets\/icons}"; do
  if [ -d "$ICONS_DIR" ]; then
    SRC_GIF="$REBRAND_ICONS/logo-outline-black.gif"
    DEST_GIF="$ICONS_DIR/logo-outline-black.gif"
    if [ -f "$SRC_GIF" ]; then
      cp "$SRC_GIF" "$DEST_GIF"
      echo "Replaced $DEST_GIF with $SRC_GIF (forced)"
    fi
  fi
done

echo "Icon rebranding complete."
