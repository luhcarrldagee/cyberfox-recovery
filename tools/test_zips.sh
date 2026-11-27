#!/usr/bin/env bash
# Mock-device tests for the CyberFox Lab engine and the built zips. Runs on any Linux PC.
# shellcheck disable=SC2034,SC2012,SC2115
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENG="$ROOT/zips/cfx.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
pass() { echo "PASS  $1"; PASS=$((PASS+1)); }
fail() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }
check() { if eval "$2"; then pass "$1"; else fail "$1"; fi; }

setup() {
  rm -rf "$T/dev" "$T/data" "$T/otg"
  mkdir -p "$T/dev" "$T/data/media/0" "$T/otg"
  for p in boot_a boot_b vendor_boot_a vendor_boot_b dtbo_a init_boot_a vbmeta_system_a efs persist; do
    head -c 65536 /dev/urandom > "$T/dev/$p"
  done
  for s in a b; do
    { printf 'AVB0'; head -c 252 /dev/zero; } > "$T/dev/vbmeta_$s"
  done
  printf 'ro.product.device=%s\nro.boot.slot_suffix=_a\nro.build.fingerprint=google/bluejay/test\n' "${1:-bluejay}" > "$T/props"
  export CFX_BYNAME="$T/dev" CFX_DATA="$T/data" CFX_SDCARD="$T/data/media/0" CFX_OTG="$T/nootg" CFX_PROPS="$T/props" CFX_ASSUME_YES=1 CFX_STATE="$T/slot"
  unset OUTFD
}
run() { sh "$ENG" "$@" > "$T/out" 2>&1; }
H="$T/data/media/0/CyberFox"

# ---- device check
setup oriole
run backup-critical; rc=$?; check "wrong device is refused" '[ $rc -ne 0 ] && grep -q "for Pixel 6a" "$T/out"'
mkdir -p "$H" && touch "$H/.skip_device_check"
run backup-critical; check "skip_device_check override works" 'grep -q "images saved" "$T/out"'

# ---- backup / restore critical
setup
run backup-critical; rc=$?
B="$(ls -1d "$H"/Backups/2*/ | head -n1)"
check "backup exits 0" '[ $rc -eq 0 ]'
check "backup dumps slot _a images" '[ -f "$B/boot.img" ] && [ -f "$B/vendor_boot.img" ] && [ -f "$B/vbmeta.img" ]'
check "backup includes efs and persist" '[ -f "$B/efs.img" ] && [ -f "$B/persist.img" ]'
check "boot image matches device" 'cmp -s "$B/boot.img" "$T/dev/boot_a"'
check "sha256 list complete" '[ "$(wc -l < "$B/sha256.txt")" -eq "$(ls "$B"/*.img | wc -l)" ]'

orig="$(sha256sum "$T/dev/boot_a" | cut -c1-64)"
head -c 65536 /dev/urandom > "$T/dev/boot_a"; head -c 65536 /dev/urandom > "$T/dev/efs"
run restore-critical
check "restore puts boot_a back" '[ "$(sha256sum "$T/dev/boot_a" | cut -c1-64)" = "$orig" ]'
check "efs NOT restored without ALLOW_EFS_RESTORE" '! cmp -s "$B/efs.img" "$T/dev/efs" && grep -q "efs skipped" "$T/out"'
touch "$B/ALLOW_EFS_RESTORE"; run restore-critical
check "efs restored with ALLOW_EFS_RESTORE" 'cmp -s "$B/efs.img" "$T/dev/efs"'
echo x >> "$B/boot.img"; run restore-critical; rc=$?
check "corrupt backup is rejected" '[ $rc -ne 0 ] && grep -q "Checksum mismatch" "$T/out"'

# ---- vault
setup
mkdir -p "$T/data/media/0/DCIM/Camera" "$T/data/media/0/Download"
echo photo > "$T/data/media/0/DCIM/Camera/a.jpg"; echo doc > "$T/data/media/0/Download/b.pdf"
run vault-backup
check "vault tar created internally" 'ls "$H"/Vault/vault-*.tar >/dev/null 2>&1'
rm -rf "$T/data/media/0/DCIM" "$T/data/media/0/Download"
run vault-restore
check "vault restores files" '[ "$(cat "$T/data/media/0/DCIM/Camera/a.jpg")" = photo ] && [ -f "$T/data/media/0/Download/b.pdf" ]'
export CFX_OTG="$T/otg"; run vault-backup
check "vault prefers USB-OTG when present" 'ls "$T"/otg/CyberFox/Vault/vault-*.tar >/dev/null 2>&1'

# ---- avb
setup
run avb-disable
check "vbmeta_a flag byte = 3" '[ "$(od -An -tu1 -j123 -N1 "$T/dev/vbmeta_a" | tr -d " ")" = 3 ]'
check "vbmeta_b flag byte = 3" '[ "$(od -An -tu1 -j123 -N1 "$T/dev/vbmeta_b" | tr -d " ")" = 3 ]'
check "vbmeta size unchanged" '[ "$(wc -c < "$T/dev/vbmeta_a")" -eq 256 ]'
check "vbmeta backed up first" 'ls "$H"/Backups/vbmeta-*/vbmeta_a.img >/dev/null 2>&1'
setup; head -c 256 /dev/zero > "$T/dev/vbmeta_a"; rm "$T/dev/vbmeta_b"; run avb-disable; rc=$?
check "non-AVB vbmeta is left alone" '[ $rc -ne 0 ] && [ "$(od -An -tu1 -j123 -N1 "$T/dev/vbmeta_a" | tr -d " ")" = 0 ]'

# ---- slot
setup; run slot-switch
check "slot switch _a -> _b" '[ "$(cat "$T/slot")" = _b ]'

# ---- modules
setup
mkdir -p "$T/data/adb/modules/modA" "$T/data/adb/modules/modB" "$T/data/adb/ksu/modules/modK"
touch "$T/data/adb/modules/modB/disable"
run rescue-modules
check "rescue disables active modules" '[ -f "$T/data/adb/modules/modA/disable" ] && [ -f "$T/data/adb/ksu/modules/modK/disable" ]'
run enable-modules
check "re-enable restores only CyberFox-disabled ones" '[ ! -f "$T/data/adb/modules/modA/disable" ] && [ -f "$T/data/adb/modules/modB/disable" ]'

# ---- caches
setup
mkdir -p "$T/data/dalvik-cache/arm64" "$T/data/cache" "$T/data/app/x"
touch "$T/data/dalvik-cache/arm64/a.dex" "$T/data/app/x/base.apk"
run clean-caches
check "dalvik-cache emptied, apps kept" '[ -z "$(ls -A "$T/data/dalvik-cache")" ] && [ -f "$T/data/app/x/base.apk" ]'

# ---- stock recovery
setup
mkdir -p "$T/data/media/0/backup_vendor_boot"
head -c 65536 /dev/urandom > "$T/data/media/0/backup_vendor_boot/vendor_boot.img"
run restore-stock-recovery
check "stock vendor_boot flashed to both slots" 'cmp -s "$T/data/media/0/backup_vendor_boot/vendor_boot.img" "$T/dev/vendor_boot_a" && cmp -s "$T/data/media/0/backup_vendor_boot/vendor_boot.img" "$T/dev/vendor_boot_b"'

# ---- report
setup; run report
check "report written" 'ls "$H"/Reports/report-*.txt >/dev/null 2>&1'

# ---- confirmation refuses without input
setup; unset CFX_ASSUME_YES; cp "$T/dev/vbmeta_a" "$T/va"; run avb-disable
check "no key input = no changes" 'cmp -s "$T/va" "$T/dev/vbmeta_a"'

# ---- built zips through update-binary
if [ -d "$ROOT/dist/zips" ]; then
  setup
  Z="$ROOT/dist/zips/CFX-Device-Report.zip"
  mkdir -p "$T/zx"; unzip -q "$Z" -d "$T/zx"
  # run the real update-binary (OUTFD=3 -> captured) via a /tmp-safe copy
  sed "s#W=/tmp/cfx#W=$T/w#" "$T/zx/META-INF/com/google/android/update-binary" > "$T/ub"
  sh "$T/ub" 3 3 "$Z" 3> "$T/out" > /dev/null 2>&1
  check "update-binary runs zip end to end" 'grep -q "ui_print" "$T/out" && ls "$H"/Reports/report-*.txt >/dev/null 2>&1'
  n="$(ls "$ROOT"/dist/zips/*.zip | wc -l)"
  check "all 11 zips built" '[ "$n" -eq 11 ]'
fi

echo; echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
