# CyberFox Lab tools

Every tool is a small flashable zip that runs the shared engine `cfx.sh` with one tool id. Inside the recovery the zips live in `/FFiles/CyberFox`, and the engine is also installed as `/system/bin/cfx` for the terminal and `adb shell`.

| Lab item | Zip | Terminal | What it does |
|---|---|---|---|
| Backup critical partitions | `CFX-Backup-Critical.zip` | `cfx backup-critical` | boot, vendor_boot, dtbo, vbmeta, efs, persist |
| Restore critical partitions | `CFX-Restore-Critical.zip` | `cfx restore-critical` | Newest backup to active slot, SHA-256 checked |
| File Vault: back up my files | `CFX-Vault-Backup.zip` | `cfx vault-backup` | Photos, downloads, docs, music to USB-OTG |
| File Vault: restore my files | `CFX-Vault-Restore.zip` | `cfx vault-restore` | Newest vault back to storage, fixes owners |
| Disable AVB / verity | `CFX-Disable-AVB.zip` | `cfx avb-disable` | Patches vbmeta on both slots (may need Format) |
| Switch active slot | `CFX-Switch-Slot.zip` | `cfx slot-switch` | Marks the other A/B slot active for next boot |
| Bootloop rescue | `CFX-Rescue-Bootloop.zip` | `cfx rescue-modules` | Disables all Magisk / KernelSU / APatch modules |
| Re-enable modules | `CFX-Reenable-Modules.zip` | `cfx enable-modules` | Undoes Bootloop rescue only |
| Clean caches | `CFX-Clean-Caches.zip` | `cfx clean-caches` | dalvik, package and /data/cache; keeps data |
| Restore stock recovery | `CFX-Restore-Stock-Recovery.zip` | `cfx restore-stock-recovery` | Saved stock vendor_boot to both slots |
| Device report | `CFX-Device-Report.zip` | `cfx report` | Props, partitions, mounts, logs to Reports |

## Safety rules built into the engine

- **Device check.** Tools that touch partitions refuse to run unless `ro.product.device`, `ro.build.product` or `ro.product.vendor.device` is `bluejay`. To override, create `/sdcard/CyberFox/.skip_device_check`.
- **Confirmation.** Restore, AVB, slot switch and stock-recovery restore wait for a key press: Vol+ continues and Vol- cancels. If no key is pressed within 10 seconds, the tool cancels.
- **Checksums.** Critical restore checks the SHA-256 of every image and refuses if any image fails. It also refuses a backup taken on a different device.
- **efs and persist.** These partitions are backed up but never restored unless you create `ALLOW_EFS_RESTORE` inside that backup folder.
- **AVB.** The tool only patches partitions that start with the `AVB0` magic, and it backs them up to `/sdcard/CyberFox/Backups/vbmeta-<date>` first.
- **Modules.** Bootloop rescue marks the modules it disables with `.cfx_disabled`. Re-enable only touches those, so modules you disabled yourself stay disabled.

## Output locations

| Path | Contents |
|---|---|
| `/sdcard/CyberFox/Backups/<date>/` | `*.img`, `sha256.txt`, `manifest.txt` |
| `/sdcard/CyberFox/Vault/` or `<usb-otg>/CyberFox/Vault/` | `vault-<date>.tar` + `.sha256` |
| `/sdcard/CyberFox/Reports/` | `report-<date>.txt` |

## Using the zips elsewhere

The zips work in any TWRP-based recovery: run `tools/build_zips.sh` and flash `dist/zips/CFX-*.zip`.

## Testing

`tools/test_zips.sh` builds a fake `/dev/block/by-name`, `/data` and `/sdcard` in a temp folder and runs every tool through the engine and through a real `update-binary`. The `CFX_*` environment variables in the header of `zips/cfx.sh` point the engine at those fake paths.
