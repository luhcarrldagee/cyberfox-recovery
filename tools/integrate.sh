#!/usr/bin/env bash
# Put the CyberFox Lab zips and the cfx engine into the Pixel device tree's ramdisk.
#   tools/integrate.sh <OrangeFox TOP>
# Result in the recovery ramdisk:
#   /FFiles/CyberFox/CFX-*.zip   (used by the Lab page)
#   /system/bin/cfx              (terminal: `cfx list`, `cfx backup-critical`, ...)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOP="$(cd "${1:?usage: integrate.sh <OrangeFox source root>}" && pwd)"
DT="$TOP/device/google/pixels"
[ -d "$DT/recovery/root" ] || { echo "device tree not found at $DT"; exit 1; }

bash "$ROOT/tools/build_zips.sh" "$ROOT/dist/zips" >/dev/null
dst="$DT/recovery/root/FFiles/CyberFox"
rm -rf "$dst"; mkdir -p "$dst"
cp "$ROOT"/dist/zips/*.zip "$dst/"
install -m 0755 "$ROOT/zips/cfx.sh" "$DT/recovery/root/system/bin/cfx"
echo "integrated $(find "$dst" -name '*.zip' | wc -l) zips -> ${dst#"$TOP"/}"
echo "installed cfx engine -> device/google/pixels/recovery/root/system/bin/cfx"
