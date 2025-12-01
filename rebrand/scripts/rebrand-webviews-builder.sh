#!/bin/bash
# rebrand-webviews-builder.sh
# Copy all rebranded files from rebrand/kilocode/ to build/kilocode/
# This includes webviews, documentation, and other customized files for UltraRepo Builder
# Usage: bash rebrand-webviews-builder.sh
# Environment variables:
#   NO_BACKUP=true    Skip creating backup files (default: false)

set -e

# Get the absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REBRAND_DIR="$PROJECT_ROOT/rebrand/kilocode"
BUILD_DIR="$PROJECT_ROOT/build/kilocode"

echo "🎨 Starting UltraRepo Builder webview and file rebranding..."
echo "📁 Source: $REBRAND_DIR"
echo "📁 Target: $BUILD_DIR"

# Check if source directory exists
if [ ! -d "$REBRAND_DIR" ]; then
  echo "[ERROR] Rebrand source directory not found: $REBRAND_DIR" >&2
  exit 1
fi

# Check if target directory exists
if [ ! -d "$BUILD_DIR" ]; then
  echo "[ERROR] Build target directory not found: $BUILD_DIR" >&2
  exit 2
fi

# Function to copy files with logging
copy_file() {
  local src="$1"
  local dest="$2"
  local rel_path="$3"
  
  # Create destination directory if it doesn't exist
  local dest_dir="$(dirname "$dest")"
  if [ ! -d "$dest_dir" ]; then
    mkdir -p "$dest_dir"
    echo "📁 Created directory: $dest_dir"
  fi
  
  # Skip backup creation - not needed when copying rebrand files to build directory
  # Backup logic removed to prevent accumulation of .backup files
  
  # Copy the file
  cp "$src" "$dest"
  echo "📄 Copied: $rel_path"
}

# Find all files in rebrand/kilocode and copy them to build/kilocode
copied_count=0
while IFS= read -r -d '' file; do
  # Get relative path from rebrand/kilocode
  rel_path="${file#$REBRAND_DIR/}"
  
  # Skip if it's the rebrand directory itself
  if [ "$rel_path" = "." ]; then
    continue
  fi
  
  # Construct destination path
  dest_file="$BUILD_DIR/$rel_path"
  
  # Copy the file
  copy_file "$file" "$dest_file" "$rel_path"
  ((copied_count++))
  
done < <(find "$REBRAND_DIR" -type f -print0)

# Ensure critical files are present and up to date
CRITICAL_FILES=(
  "src/extension.ts"
  "src/package.nls.json"
)

ensured_count=0
for rel in "${CRITICAL_FILES[@]}"; do
  src_file="$REBRAND_DIR/$rel"
  dest_file="$BUILD_DIR/$rel"
  if [ -f "$src_file" ]; then
    dest_dir="$(dirname "$dest_file")"
    [ -d "$dest_dir" ] || { mkdir -p "$dest_dir" && echo "📁 Created directory: $dest_dir"; }
    cp "$src_file" "$dest_file"
    echo "⭐ Ensured critical file: $rel"
    ((ensured_count++))
  else
    echo "⚠️  Critical file not found in rebrand (skipped): $rel"
  fi
done

echo ""
echo "✅ UltraRepo Builder webview rebranding complete!"
echo "📊 Files processed: $copied_count"
echo "🔒 Critical files ensured: $ensured_count (${CRITICAL_FILES[*]})"
echo ""
echo "📝 Summary:"
echo "   • All files copied from rebrand/kilocode/ to build/kilocode/"
echo "   • Directory structure preserved"
echo "   • extension.ts and package.nls.json verified/copied when present"
echo ""
echo "🔄 Next steps:"
echo "   1. Review copied files for correctness"
echo "   2. Run the main build process"
echo "   3. Test extension functionality"
echo ""
