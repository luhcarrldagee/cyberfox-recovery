# Building CyberFox

## Host

- Linux x86_64 (Ubuntu 22.04 or 24.04 tested by upstream)
- About 100 GB free disk. OrangeFox quotes about 45 GB for 12.1 and about 85 GB for 14.1, and 16.0 is larger.
- 16 GB RAM or more, plus swap
- Packages: follow the [OrangeFox build guide](https://wiki.orangefox.tech/dev/building). On Ubuntu:

```bash
sudo apt install git-core gnupg flex bison build-essential zip curl zlib1g-dev libc6-dev-i386 \
  x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc unzip \
  fontconfig python3 python3-pip rsync bc lz4 cpio
mkdir -p ~/bin && curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo && chmod +x ~/bin/repo
export PATH=~/bin:$PATH
pip install pillow    # optional, recolors 4 orange PNG icons
```

## One command

```bash
tools/build.sh --top ~/cyberfox_src --sync
```

| Flag | Effect |
|---|---|
| `--sync` | runs `orangefox_sync.sh --branch 16.0` and clones the device tree (`R12_16`) into `device/google/pixels` |
| `--prepare` | applies every patch but skips the compile, so you can inspect or build by hand |
| `--stable` | `--build-type Stable` (MTP off at boot, as upstream); default is Beta |
| `-j N` | parallel jobs passed to the device build |

The build runs in this order:

1. `device/google/pixels/patches/apply_patches.py --apply`, which applies the device maintainer's patches. On a partial tree they report "target file is missing", but a full sync applies them cleanly.
2. `tools/apply_theme.py --top`, which applies the CyberFox theme. It is idempotent. Run it with `--check` for a dry run.
3. `tools/integrate.sh`, which adds the Lab zips to `recovery/root/FFiles/CyberFox` and `cfx` to `recovery/root/system/bin`.
4. `device/google/pixels/build.sh -n CyberFox --build-type Beta --no-patches`.
5. The script copies `builds/OrangeFox-*-CyberFox-aio.*` into `dist/CyberFox-*-aio.*` and writes SHA256SUMS.

Always run the full pipeline when you rebuild. If you run the device tree's `build.sh` without `--no-patches`, its patcher restores the original `en.xml` and `ru.xml` and removes the CyberFox name from those two languages. Running `tools/apply_theme.py` again fixes that.

## Building by hand

```bash
cd ~/cyberfox_src
python3 device/google/pixels/patches/apply_patches.py --apply --root .
python3 ~/cyberfox/tools/apply_theme.py --top .
bash ~/cyberfox/tools/integrate.sh .
cd device/google/pixels && ./build.sh -n CyberFox --build-type Beta --no-patches
```

## Changing things

| Want to change | Edit | Then |
|---|---|---|
| Colors | `STYLE_VARS`, `ACCENT_MAP`, `TINT_MAP` in `tools/apply_theme.py` | rebuild |
| Logo, splash or glow art | `branding/generate_assets.py` | `python3 branding/generate_assets.py` (needs Playwright + Chromium) |
| Add a Lab tool | add a `t_<name>` function and a case entry in `zips/cfx.sh`, and an entry in `zips/tools.json` | `python3 tools/gen_lab_page.py && tools/test_zips.sh` |
| Lab page layout | `tools/gen_lab_page.py` | regenerate |

## Tests

```bash
tools/build_zips.sh && tools/test_zips.sh     # 28 mock-device checks, no phone needed
```
