#!/usr/bin/env bash
# Build one flashable zip per tool listed in zips/tools.json into dist/zips/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/dist/zips}"
rm -rf "$OUT"; mkdir -p "$OUT"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

python3 - "$ROOT/zips/tools.json" > "$TMP/list" <<'PY'
import json, sys
for t in json.load(open(sys.argv[1]))["tools"]:
    print(t["id"], t["zip"])
PY

while read -r id name; do
  d="$TMP/$name"
  mkdir -p "$d/META-INF/com/google/android"
  cp "$ROOT/zips/update-binary" "$d/META-INF/com/google/android/update-binary"
  echo "#MAGISK" > "$d/META-INF/com/google/android/updater-script"
  cp "$ROOT/zips/cfx.sh" "$d/cfx.sh"
  echo "$id" > "$d/cfx.cmd"
  chmod 0755 "$d/cfx.sh" "$d/META-INF/com/google/android/update-binary"
  (cd "$d" && find . -type f -exec env TZ=UTC touch -t 202601010000 {} + && zip -qXD -r "$OUT/$name.zip" META-INF cfx.sh cfx.cmd)
  echo "built $name.zip"
done < "$TMP/list"
(cd "$OUT" && sha256sum ./*.zip > SHA256SUMS)
echo "zips -> $OUT"
