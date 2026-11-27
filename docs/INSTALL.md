# Installing CyberFox on a Pixel 6a

CyberFox uses the installer from the leegarchat Pixel AIO tree. The recovery is written to `vendor_boot` on both slots.

## Before you start

1. Unlock the bootloader. This wipes the phone.
2. Install [Android platform-tools](https://developer.android.com/tools/releases/platform-tools) (`adb`, `fastboot`) on your PC.
3. Get a stock `vendor_boot.img` that matches your current Android build, from the factory image for your build. Keep it, because it is your rollback.

## Install from a PC (recommended)

```bash
unzip CyberFox-R12.0-CyberFox-aio.zip -d cyberfox
adb reboot bootloader
cd cyberfox
./install-desktop.sh          # Windows: install-desktop.bat
# wait for:  RESULT: OK
fastboot reboot recovery
```

Do **not** use `fastboot boot`. The AIO image is not designed to boot that way.

## Install from the phone

If you already run OrangeFox, TWRP or an older CyberFox, flash the AIO zip from Install. The installer backs up your current vendor_boot to `/sdcard/backup_vendor_boot/` first.

## After installing

1. Open **Settings, then CyberFox Lab, then Backup critical partitions**.
2. Copy `/sdcard/CyberFox/Backups/<date>/` to your PC (`adb pull /sdcard/CyberFox`).
3. Optional: put your stock image at `/sdcard/CyberFox/stock_vendor_boot.img` so **Restore stock recovery** works offline.

## Rollback

```bash
adb reboot bootloader
fastboot flash vendor_boot_a stock_vendor_boot.img
fastboot flash vendor_boot_b stock_vendor_boot.img
fastboot reboot
```

You can also run **CyberFox Lab, then Restore stock recovery** from inside CyberFox.

## Things to know

- OTAs and ROM installs replace `vendor_boot`, which removes CyberFox. Reinstall it afterwards, or use OrangeFox's "Reflash after flashing a ROM" option.
- The Google logo and the "bootloader unlocked" warning are drawn by the signed bootloader and cannot be changed. The CyberFox splash appears right after them.
- If the tools refuse to run on another Pixel, they are working as intended. The device check is for `bluejay`. To override it at your own risk, create `/sdcard/CyberFox/.skip_device_check`.
