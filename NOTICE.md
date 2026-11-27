# Notices and credits

CyberFox Recovery is a derivative work distributed under the GNU General Public License v3.0 (see `LICENSE`).

## Upstream projects

- **OrangeFox Recovery** by the OrangeFox Team. CyberFox's recovery engine, GUI, theme structure and pages come from OrangeFox (`fox_16.0`): https://gitlab.com/OrangeFox. The About page and splash credit OrangeFox, and the "OrangeFox websites" string is left unchanged on purpose.
- **TWRP** by TeamWin. OrangeFox is based on TWRP: https://github.com/TeamWin
- **Pixel AIO device tree** by leegarchat. This covers the Pixel 6 to 11 device tree, kernel handling, installer and maintainer patches: https://github.com/leegarchat/twrp_device_google_pixels (branch `R12_16`)

CyberFox only changes theme assets and XML, adds `pages/cyberfox.xml`, and adds files to the device ramdisk (`/FFiles/CyberFox`, `/system/bin/cfx`). It does not change upstream C++ code.

## Fonts

- **Rajdhani** by the Indian Type Foundry, under the SIL Open Font License 1.1 (`theme/overlay/common/fonts/Rajdhani-OFL.txt`).
- Preview-only fonts in `previews/fonts` (Exo 2, Fira Code, Orbitron) are under the SIL OFL and are not shipped in the recovery.

## Branding

The Glitch Fox logo, splash, glow and circuit artwork are original to CyberFox and are released under the same GPL-3.0 as the rest of the repo.

"OrangeFox" is the name of the upstream project. CyberFox is an independent re-skin and is not affiliated with or endorsed by the OrangeFox Team, TeamWin or Google. "Pixel" is a trademark of Google LLC.
