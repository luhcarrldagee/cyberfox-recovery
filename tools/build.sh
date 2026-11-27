#!/usr/bin/env bash
# CyberFox full pipeline for Pixel 6a (bluejay).
#
#   tools/build.sh --top ~/cyberfox_src --sync     # first time: sync OrangeFox 16.0 + device tree, then build
#   tools/build.sh --top ~/cyberfox_src            # rebuild
#   tools/build.sh --top ~/cyberfox_src --prepare  # patch everything, skip the long compile
#
# Steps
#   1. (optional) sync OrangeFox fox_16.0 and leegarchat/twrp_device_google_pixels (R12_16)
#   2. device-tree maintainer patches      (patches/apply_patches.py --apply)
#   3. CyberFox theme                      (tools/apply_theme.py)
#   4. Lab zips + cfx engine into ramdisk   (tools/integrate.sh)
#   5. compile with the device tree's build.sh (--no-patches, step 2 already ran)
#   6. rename OrangeFox-*-CyberFox-aio.* -> CyberFox-*-aio.* into dist/
#
# Needs a Linux x86_64 host with ~100 GB free disk, 16 GB+ RAM, and the usual
# AOSP build packages (see docs/BUILDING.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOP=""; SYNC=0; PREPARE=0; TYPE="Beta"; JOBS=""
OF_BRANCH="16.0"; DT_BRANCH="R12_16"
DT_URL="https://github.com/leegarchat/twrp_device_google_pixels.git"

while [ $# -gt 0 ]; do
  case "$1" in
    --top) TOP="$2"; shift 2 ;;
    --sync) SYNC=1; shift ;;
    --prepare) PREPARE=1; shift ;;
    --stable) TYPE="Stable"; shift ;;
    -j) JOBS="$2"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown option $1"; exit 2 ;;
  esac
done
[ -n "$TOP" ] || { echo "--top <dir> is required"; exit 2; }
mkdir -p "$TOP"; TOP="$(cd "$TOP" && pwd)"
say() { printf '\n\033[1;34m[cyberfox]\033[0m %s\n' "$1"; }

if [ "$SYNC" = 1 ]; then
  say "Syncing OrangeFox $OF_BRANCH into $TOP"
  command -v repo >/dev/null || { echo "install 'repo' first (docs/BUILDING.md)"; exit 1; }
  tmp="$(mktemp -d)"
  git clone --depth 1 https://gitlab.com/OrangeFox/sync.git "$tmp/sync"
  (cd "$tmp/sync" && ./orangefox_sync.sh --branch "$OF_BRANCH" --path "$TOP")
  rm -rf "$tmp"
  if [ ! -d "$TOP/device/google/pixels/.git" ]; then
    say "Cloning Pixel AIO device tree ($DT_BRANCH)"
    git clone -b "$DT_BRANCH" "$DT_URL" "$TOP/device/google/pixels"
  else
    git -C "$TOP/device/google/pixels" pull --ff-only
  fi
fi

[ -d "$TOP/bootable/recovery/gui/theme" ] || { echo "$TOP has no OrangeFox source - run with --sync"; exit 1; }
DT="$TOP/device/google/pixels"
[ -x "$DT/build.sh" ] || { echo "device tree missing at $DT - run with --sync"; exit 1; }

say "Device-tree maintainer patches"
if [ -f "$DT/patches/apply_patches.py" ]; then
  python3 "$DT/patches/apply_patches.py" --apply --root "$TOP"
fi

say "Applying CyberFox theme"
python3 "$ROOT/tools/apply_theme.py" --top "$TOP"

say "Integrating CyberFox Lab zips"
bash "$ROOT/tools/integrate.sh" "$TOP"

if [ "$PREPARE" = 1 ]; then
  say "Prepared. Compile with: cd $DT && ./build.sh -n CyberFox --build-type $TYPE --no-patches"
  exit 0
fi

say "Compiling (this takes a while)"
args=(-n CyberFox --build-type "$TYPE" --no-patches)
[ -n "$JOBS" ] && args+=(-j "$JOBS")
(cd "$DT" && ./build.sh "${args[@]}")

say "Collecting artifacts"
mkdir -p "$ROOT/dist"
found=0
for f in "$DT"/builds/OrangeFox-*-CyberFox-aio.*; do
  [ -e "$f" ] || continue
  b="$(basename "$f")"
  cp "$f" "$ROOT/dist/${b/OrangeFox-/CyberFox-}"
  echo "  dist/${b/OrangeFox-/CyberFox-}"
  found=1
done
[ "$found" = 1 ] || { echo "no build output found in $DT/builds"; exit 1; }
(cd "$ROOT/dist" && sha256sum CyberFox-*-aio.* > SHA256SUMS-recovery)
say "Done. Flash with docs/INSTALL.md (unzip, run install-desktop.sh in fastboot)."
