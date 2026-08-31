#!/bin/bash
# Publishes a launcher build to the web root that nginx serves at /apk/.
#
# Filenames carry a content hash and are never reused: replacing a file at a stable
# URL while someone is mid-download hands them a corrupt package, which Android
# reports as the useless "app not installed".
set -euo pipefail

APK="${1:-../argosy-launcher/app/build/outputs/apk/debug/app-debug.apk}"
DEST="${APK_PUBLISH_DIR:-/var/www/apk}"

[[ -f "$APK" ]] || { echo "No APK at $APK" >&2; exit 1; }
mkdir -p "$DEST"

hash=$(md5sum "$APK" | cut -c1-8)
name="gameio-${hash}.apk"
size=$(stat -c%s "$APK")

# Copy then rename, so a download can never see a half-written file.
cp "$APK" "$DEST/.incoming-$name"
mv "$DEST/.incoming-$name" "$DEST/$name"

# The landing page reads this to name the current build on its download button.
cat > "$DEST/.latest.json.tmp" <<JSON
{"file": "$name", "size": $size, "published": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
JSON
mv "$DEST/.latest.json.tmp" "$DEST/latest.json"

echo "published $name ($((size / 1048576)) MB)"
