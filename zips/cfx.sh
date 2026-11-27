#!/system/bin/sh
# CyberFox Lab tool engine - one script, many tools.
# Usage: cfx.sh <tool-id>      (run from a flashable zip or as /system/bin/cfx)
#        cfx.sh list
# Copyright (C) 2026 CyberFox contributors. GPL-3.0-or-later.
#
# Every path is overridable so the whole engine can be tested on a PC:
#   CFX_BYNAME  block device dir   (default /dev/block/by-name)
#   CFX_SDCARD  internal storage    (default /sdcard, falls back to /data/media/0)
#   CFX_DATA    data partition      (default /data)
#   CFX_OTG     USB-OTG mount       (default /usb-otg)
#   CFX_PROPS   file with key=value props used instead of getprop (tests)
#   CFX_ASSUME_YES=1  skip the volume-key confirmation (tests / scripted use)

CFX_VERSION="1.0"
DEVICE_CODENAMES="bluejay"

BYNAME="${CFX_BYNAME:-/dev/block/by-name}"
DATA="${CFX_DATA:-/data}"
OTG="${CFX_OTG:-/usb-otg}"
if [ -n "$CFX_SDCARD" ]; then
  SDCARD="$CFX_SDCARD"
elif [ -d /sdcard ] && [ -w /sdcard ]; then
  SDCARD=/sdcard
else
  SDCARD="$DATA/media/0"
fi
CFX_HOME="$SDCARD/CyberFox"

# ---------------------------------------------------------------- output
ui_print() {
  if [ -n "$OUTFD" ] && [ "$OUTFD" != "1" ]; then
    printf 'ui_print %s\nui_print\n' "$1" >&"$OUTFD"
  else
    printf '%s\n' "$1"
  fi
}
log()   { ui_print "  $1"; }
ok()    { ui_print "  [ OK ] $1"; }
warn()  { ui_print "  [WARN] $1"; }
abort() { ui_print "  [FAIL] $1"; ui_print " "; exit 1; }

banner() {
  ui_print " "
  ui_print "  ===================================="
  ui_print "   C Y B E R F O X   L A B   v$CFX_VERSION"
  ui_print "   $1"
  ui_print "  ===================================="
}

# ---------------------------------------------------------------- props
prop() {
  if [ -n "$CFX_PROPS" ] && [ -f "$CFX_PROPS" ]; then
    sed -n "s/^$1=//p" "$CFX_PROPS" | head -n 1
  elif command -v getprop >/dev/null 2>&1; then
    getprop "$1"
  fi
}

device_name() {
  for p in ro.product.device ro.build.product ro.product.vendor.device ro.product.system.device; do
    v="$(prop "$p")"
    [ -n "$v" ] && { echo "$v"; return; }
  done
  echo unknown
}

check_device() {
  [ -f "$CFX_HOME/.skip_device_check" ] && { warn "Device check skipped by user flag"; return 0; }
  for p in ro.product.device ro.build.product ro.product.vendor.device; do
    v="$(prop "$p")"
    for c in $DEVICE_CODENAMES; do
      [ "$v" = "$c" ] && { ok "Device: Pixel 6a ($c)"; return 0; }
    done
  done
  abort "This tool is for Pixel 6a (bluejay), found '$(device_name)'. Create $CFX_HOME/.skip_device_check to override."
}

slot() {
  s="$(prop ro.boot.slot_suffix)"
  if [ -z "$s" ] && command -v bootctl >/dev/null 2>&1; then
    n="$(bootctl get-current-slot 2>/dev/null)"
    [ "$n" = "0" ] && s=_a
    [ "$n" = "1" ] && s=_b
  fi
  echo "$s"
}

other_slot() {
  case "$(slot)" in _a) echo _b ;; _b) echo _a ;; *) echo "" ;; esac
}

# ---------------------------------------------------------------- helpers
stamp() { date +%Y%m%d-%H%M%S 2>/dev/null || echo now; }

sha() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  elif command -v toybox >/dev/null 2>&1; then toybox sha256sum "$1" | cut -d' ' -f1
  else echo nosha; fi
}

human() {
  b="$(wc -c < "$1" 2>/dev/null | tr -d ' ')"
  [ -z "$b" ] && b=0
  echo "$((b / 1048576)) MB"
}

# Read a volume key. Vol+ = yes, Vol- = no. 10 s timeout = no.
confirm() {
  ui_print " "
  ui_print "  >> $1"
  if [ "$CFX_ASSUME_YES" = "1" ]; then
    log "CFX_ASSUME_YES=1, continuing"
    return 0
  fi
  if ! command -v getevent >/dev/null 2>&1; then
    warn "No key input available, cancelling for safety"
    return 1
  fi
  ui_print "  >> Vol UP = continue    Vol DOWN = cancel"
  i=0
  while [ $i -lt 10 ]; do
    ev="$(timeout 1 getevent -lqc 1 2>/dev/null)"
    case "$ev" in
      *KEY_VOLUMEUP*DOWN*)   ok "Confirmed"; return 0 ;;
      *KEY_VOLUMEDOWN*DOWN*) warn "Cancelled"; return 1 ;;
    esac
    i=$((i + 1))
  done
  warn "No answer in 10 s, cancelled"
  return 1
}

part_exists() { [ -e "$BYNAME/$1" ]; }

dump_part() { # name dest
  dd if="$BYNAME/$1" of="$2" bs=4096 2>/dev/null || return 1
  [ -s "$2" ]
}

flash_part() { # image name
  [ -e "$BYNAME/$2" ] || { warn "$2 not present, skipped"; return 1; }
  dd if="$1" of="$BYNAME/$2" bs=4096 conv=fsync 2>/dev/null || dd if="$1" of="$BYNAME/$2" bs=4096 2>/dev/null
}

mount_data() {
  [ -n "$CFX_DATA" ] && return 0
  grep -q " /data " /proc/mounts 2>/dev/null || mount /data 2>/dev/null
  grep -q " /data " /proc/mounts 2>/dev/null || abort "/data is not mounted (decrypt it first)"
}

newest_dir() { # parent
  ls -1d "$1"/*/ 2>/dev/null | sort | tail -n 1 | sed 's:/$::'
}

# ---------------------------------------------------------------- tools
CRIT_SLOTTED="boot init_boot vendor_boot dtbo vbmeta vbmeta_system vbmeta_vendor"
CRIT_SHARED="efs efs_backup modem_userdata persist"

t_backup_critical() {
  banner "Backup critical partitions"
  check_device
  mount_data
  s="$(slot)"
  log "Active slot: ${s:-none}"
  dir="$CFX_HOME/Backups/$(stamp)"
  mkdir -p "$dir" || abort "Cannot create $dir"
  man="$dir/manifest.txt"
  {
    echo "cyberfox_version=$CFX_VERSION"
    echo "device=$(device_name)"
    echo "slot=$s"
    echo "build=$(prop ro.build.fingerprint)"
    echo "date=$(stamp)"
  } > "$man"
  : > "$dir/sha256.txt"
  n=0
  for p in $CRIT_SLOTTED; do
    part_exists "$p$s" || continue
    if dump_part "$p$s" "$dir/$p.img"; then
      echo "$(sha "$dir/$p.img")  $p.img" >> "$dir/sha256.txt"
      echo "part=$p slotted=1" >> "$man"
      ok "$p$s  ($(human "$dir/$p.img"))"; n=$((n + 1))
    else
      warn "$p$s failed"
    fi
  done
  for p in $CRIT_SHARED; do
    part_exists "$p" || continue
    if dump_part "$p" "$dir/$p.img"; then
      echo "$(sha "$dir/$p.img")  $p.img" >> "$dir/sha256.txt"
      echo "part=$p slotted=0" >> "$man"
      ok "$p  ($(human "$dir/$p.img"))"; n=$((n + 1))
    else
      warn "$p failed"
    fi
  done
  [ "$n" -gt 0 ] || abort "No partitions found in $BYNAME"
  ui_print " "
  ok "$n images saved to $dir"
  log "Copy this folder to your PC - efs/persist are unique to your phone."
}

t_restore_critical() {
  banner "Restore critical partitions"
  check_device
  mount_data
  dir="${CFX_RESTORE_DIR:-$(newest_dir "$CFX_HOME/Backups")}"
  [ -n "$dir" ] && [ -f "$dir/manifest.txt" ] || abort "No backup found in $CFX_HOME/Backups"
  log "Backup: $dir"
  bdev="$(sed -n 's/^device=//p' "$dir/manifest.txt")"
  [ "$bdev" = "$(device_name)" ] || [ -f "$CFX_HOME/.skip_device_check" ] || abort "Backup is from '$bdev', this is '$(device_name)'"
  log "Verifying checksums"
  while read -r h f; do
    [ -z "$f" ] && continue
    [ -f "$dir/$f" ] || abort "Missing $f"
    [ "$h" = "nosha" ] && continue
    [ "$(sha "$dir/$f")" = "$h" ] || abort "Checksum mismatch: $f"
  done < "$dir/sha256.txt"
  ok "All checksums match"
  s="$(slot)"
  confirm "Flash this backup to slot ${s:-none}?" || exit 0
  allow_efs=0
  [ -f "$dir/ALLOW_EFS_RESTORE" ] && allow_efs=1
  grep '^part=' "$dir/manifest.txt" | while read -r line; do
    p="$(echo "$line" | sed 's/^part=\([^ ]*\).*/\1/')"
    case "$line" in
      *slotted=1*) target="$p$s" ;;
      *)
        if [ "$allow_efs" != "1" ]; then
          warn "$p skipped (create ALLOW_EFS_RESTORE in the backup folder to restore it)"
          continue
        fi
        target="$p" ;;
    esac
    if flash_part "$dir/$p.img" "$target"; then ok "$target restored"; else warn "$target failed"; fi
  done
  ui_print " "
  ok "Restore finished. Reboot when ready."
}

VAULT_DIRS="DCIM Pictures Download Documents Music Movies Recordings"

vault_root() {
  if [ -d "$OTG" ] && [ -w "$OTG" ] && grep -q " $OTG " /proc/mounts 2>/dev/null; then
    echo "$OTG/CyberFox/Vault"
  elif [ -n "$CFX_OTG" ] && [ -d "$CFX_OTG" ] && [ -w "$CFX_OTG" ]; then
    echo "$CFX_OTG/CyberFox/Vault"
  else
    echo "$CFX_HOME/Vault"
  fi
}

t_vault_backup() {
  banner "File Vault - backup"
  mount_data
  root="$(vault_root)"
  case "$root" in "$CFX_HOME"*) warn "No USB-OTG drive, saving to internal storage (lost on Format Data)" ;; *) ok "Saving to USB-OTG" ;; esac
  set --
  for d in $VAULT_DIRS; do [ -d "$SDCARD/$d" ] && set -- "$@" "$d"; done
  [ $# -gt 0 ] || abort "Nothing to back up"
  mkdir -p "$root" || abort "Cannot create $root"
  out="$root/vault-$(stamp).tar"
  log "Folders: $*"
  (cd "$SDCARD" && tar -cf "$out" "$@") || abort "tar failed"
  echo "$(sha "$out")  $(basename "$out")" > "$out.sha256"
  ok "$(basename "$out")  ($(human "$out"))"
  ok "Vault saved to $root"
}

t_vault_restore() {
  banner "File Vault - restore"
  mount_data
  f=""
  for r in "$OTG/CyberFox/Vault" "$CFX_HOME/Vault"; do
    c="$(ls -1 "$r"/vault-*.tar 2>/dev/null | sort | tail -n 1)"
    [ -n "$c" ] && { f="$c"; break; }
  done
  [ -n "$f" ] || abort "No vault-*.tar found on USB-OTG or in $CFX_HOME/Vault"
  log "Vault: $f"
  if [ -f "$f.sha256" ]; then
    [ "$(sha "$f")" = "$(cut -d' ' -f1 "$f.sha256")" ] || abort "Checksum mismatch"
    ok "Checksum OK"
  fi
  confirm "Extract into internal storage (existing files with the same name are overwritten)?" || exit 0
  (cd "$SDCARD" && tar -xf "$f") || abort "tar failed"
  chown -R 1023:1023 "$SDCARD"/DCIM "$SDCARD"/Pictures "$SDCARD"/Download "$SDCARD"/Documents \
    "$SDCARD"/Music "$SDCARD"/Movies "$SDCARD"/Recordings 2>/dev/null
  command -v restorecon >/dev/null 2>&1 && restorecon -R "$SDCARD" 2>/dev/null
  ok "Files restored. Android rescans media on next boot."
}

# vbmeta header: magic "AVB0" at 0, flags uint32 big-endian at 120; byte 123 holds the low bits.
t_avb_disable() {
  banner "Disable AVB / dm-verity"
  check_device
  confirm "Patch vbmeta on both slots? Back-ups are saved first." || exit 0
  dir="$CFX_HOME/Backups/vbmeta-$(stamp)"
  mkdir -p "$dir"
  n=0
  for s in _a _b; do
    p="vbmeta$s"
    part_exists "$p" || continue
    magic="$(dd if="$BYNAME/$p" bs=1 count=4 2>/dev/null)"
    [ "$magic" = "AVB0" ] || { warn "$p: no AVB0 header, skipped"; continue; }
    dump_part "$p" "$dir/$p.img" || { warn "$p: backup failed, skipped"; continue; }
    printf '\003' | dd of="$BYNAME/$p" bs=1 seek=123 count=1 conv=notrunc 2>/dev/null || { warn "$p: write failed"; continue; }
    ok "$p patched (verity + verification off)"; n=$((n + 1))
  done
  [ "$n" -gt 0 ] || abort "No vbmeta partition patched"
  log "Backup: $dir"
  warn "If the phone stops at a 'corrupt' screen, Format Data once."
}

t_slot_switch() {
  banner "Switch active slot"
  check_device
  cur="$(slot)"; nxt="$(other_slot)"
  [ -n "$nxt" ] || abort "Cannot detect the current slot"
  log "Current: $cur  ->  next boot: $nxt"
  confirm "Boot from slot $nxt next time?" || exit 0
  if command -v bootctl >/dev/null 2>&1; then
    n=0; [ "$nxt" = "_b" ] && n=1
    bootctl set-active-boot-slot "$n" || abort "bootctl failed"
  elif [ -n "$CFX_STATE" ]; then
    echo "$nxt" > "$CFX_STATE"
  else
    abort "bootctl not available in this recovery; use: fastboot --set-active=${nxt#_}"
  fi
  ok "Slot $nxt will boot next"
}

MOD_DIRS="adb/modules adb/ksu/modules adb/ap/modules"

t_rescue_modules() {
  banner "Bootloop rescue"
  mount_data
  n=0
  for md in $MOD_DIRS; do
    for m in "$DATA/$md"/*/; do
      [ -d "$m" ] || continue
      if [ ! -f "$m/disable" ]; then
        touch "$m/disable" "$m/.cfx_disabled"
        ok "disabled $(basename "$m")"; n=$((n + 1))
      fi
    done
  done
  [ "$n" -gt 0 ] && ok "$n modules disabled. Reboot to system." || log "No active modules found"
}

t_enable_modules() {
  banner "Re-enable modules"
  mount_data
  n=0
  for md in $MOD_DIRS; do
    for m in "$DATA/$md"/*/; do
      [ -f "$m/.cfx_disabled" ] || continue
      rm -f "$m/disable" "$m/.cfx_disabled"
      ok "enabled $(basename "$m")"; n=$((n + 1))
    done
  done
  [ "$n" -gt 0 ] && ok "$n modules re-enabled" || log "Nothing to re-enable"
}

t_clean_caches() {
  banner "Clean caches"
  mount_data
  for d in "$DATA/dalvik-cache" "$DATA/cache" "$DATA/system/package_cache"; do
    [ -d "$d" ] || continue
    rm -rf "${d:?}"/* 2>/dev/null
    ok "cleared ${d#"$DATA"/}"
  done
  ok "Done. First boot will take a little longer."
}

t_restore_stock_recovery() {
  banner "Restore stock recovery"
  check_device
  mount_data
  img=""
  for c in "$SDCARD/backup_vendor_boot/"*.img "$CFX_HOME/stock_vendor_boot.img"; do
    [ -f "$c" ] && img="$c"
  done
  if [ -z "$img" ]; then
    d="$(ls -1d "$CFX_HOME/Backups"/2*/ 2>/dev/null | sort | head -n 1)"
    [ -n "$d" ] && [ -f "$d/vendor_boot.img" ] && img="$d/vendor_boot.img"
  fi
  [ -n "$img" ] || abort "No stock vendor_boot image found (put one at $CFX_HOME/stock_vendor_boot.img)"
  log "Image: $img ($(human "$img"))"
  confirm "Flash this vendor_boot to both slots? CyberFox will be removed." || exit 0
  for s in _a _b; do
    if flash_part "$img" "vendor_boot$s"; then ok "vendor_boot$s"; else warn "vendor_boot$s failed"; fi
  done
  ok "Stock recovery restored"
}

t_report() {
  banner "Device report"
  mkdir -p "$CFX_HOME/Reports"
  out="$CFX_HOME/Reports/report-$(stamp).txt"
  {
    echo "CyberFox $CFX_VERSION device report - $(stamp)"
    echo "device=$(device_name) slot=$(slot)"
    echo "fingerprint=$(prop ro.build.fingerprint)"
    echo "bootloader=$(prop ro.bootloader)  baseband=$(prop gsm.version.baseband)"
    echo "security_patch=$(prop ro.build.version.security_patch)"
    echo; echo "== partitions =="; ls -l "$BYNAME" 2>/dev/null
    echo; echo "== mounts =="; cat /proc/mounts 2>/dev/null
    echo; echo "== storage =="; df -h 2>/dev/null
    echo; echo "== modules =="; for md in $MOD_DIRS; do ls -1 "$DATA/$md" 2>/dev/null; done
    echo; echo "== recovery.log (tail) =="; tail -n 200 /tmp/recovery.log 2>/dev/null
  } > "$out" 2>&1
  ok "Saved $out"
}

usage() {
  echo "CyberFox Lab $CFX_VERSION"
  echo "usage: cfx <tool>"
  echo "tools: backup-critical restore-critical vault-backup vault-restore avb-disable"
  echo "       slot-switch rescue-modules enable-modules clean-caches"
  echo "       restore-stock-recovery report"
}

case "$1" in
  backup-critical)        t_backup_critical ;;
  restore-critical)       t_restore_critical ;;
  vault-backup)           t_vault_backup ;;
  vault-restore)          t_vault_restore ;;
  avb-disable)            t_avb_disable ;;
  slot-switch)            t_slot_switch ;;
  rescue-modules)         t_rescue_modules ;;
  enable-modules)         t_enable_modules ;;
  clean-caches)           t_clean_caches ;;
  restore-stock-recovery) t_restore_stock_recovery ;;
  report)                 t_report ;;
  list|help|-h|--help|"") usage ;;
  *) usage; exit 2 ;;
esac
