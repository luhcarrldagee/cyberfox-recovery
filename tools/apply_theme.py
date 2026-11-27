#!/usr/bin/env python3
"""Apply the CyberFox (Plasma Circuit) theme to an OrangeFox source tree.

    python3 tools/apply_theme.py --top ~/OrangeFox_16          # apply
    python3 tools/apply_theme.py --top ~/OrangeFox_16 --check  # dry run, report only
    python3 tools/apply_theme.py --theme-dir /path/to/gui/theme # patch a bare theme dir

Idempotent: every edit checks for its own marker before changing anything.
Works on fox_12.1, fox_14.1 and fox_16.0 (same theme layout).
"""
import argparse
import colorsys
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "theme/overlay"
MARK = "CyberFox"

# --- Plasma Circuit palette ---------------------------------------------------
ACCENT_MAP = {"ED6F02": "2F8CFF", "D86100": "1F6FE0", "FA7B2A": "5AA6FF"}
STYLE_VARS = {
    "background": "#000000", "power_bg": "#000000", "power_hl": "#10163A",
    "highlight_color": "#2F8CFF2E", "highlight_color_full": "#2F8CFF22",
    "text": "#D6E6FF", "text_secondary": "#8EA2D6", "text_action": "#D6E6FF",
    "text_status": "#BFD4FF", "text_menu": "#D6E6FF", "text_light": "#8EA2D6",
    "text_hl_btn": "#001018", "text_dark": "#8EA2D6",
    "disabled_bg": "#0E1230", "disabled_text": "#6B7AA6",
    "linecolor": "#2F8CFF40", "darktransparent": "#000010CC",
    "groupitems_clr": "#070A1A", "actbar_color": "#5AA6FF", "neutral_light": "#3A4680",
    "cards_bg": "#070A1A", "keyboard_bg": "#04061A", "keyboard_hl": "#2F8CFF33",
}
TINT_MAP = {"#FFFFFF": "#BFD4FF", "#100E0D": "#0A0D22"}
FONT_MAP = {"Roboto-Regular": "Rajdhani-Medium", "Roboto-Medium": "Rajdhani-SemiBold",
            "GoogleSans-Regular": "Rajdhani-Medium", "GoogleSans-Medium": "Rajdhani-SemiBold"}
FONT_SCALE = 1.08
ORANGE_PNGS = ["Default/Icons/bs_btn_set_custom.png", "Default/Icons/bs_btn_set_screen.png",
               "Default/FullscreenIcons/empty_folder.png", "Default/FullscreenIcons/fox_lock.png"]

HEADER_XML = """
\t\t\t<!-- CyberFox: circuit header + electric glow line -->
\t\t\t<image>
\t\t\t\t<condition var1="cfx_hud" var2="1"/>
\t\t\t\t<placement x="0" y="%cfx_hdr_y%"/>
\t\t\t\t<image resource="cfx_header"/>
\t\t\t</image>
\t\t\t<image>
\t\t\t\t<condition var1="cfx_glow" var2="1"/>
\t\t\t\t<placement x="0" y="%cfx_glow_y%"/>
\t\t\t\t<image resource="cfx_glow_line"/>
\t\t\t</image>"""

LAB_ITEM = """
\t\t\t\t<listitem name="CyberFox Lab">
\t\t\t\t\t<icon res="cfx_icon"/>
\t\t\t\t\t<action function="page">cyberfox</action>
\t\t\t\t</listitem>"""


class Patcher:
    def __init__(self, theme: Path, check: bool):
        self.t = theme
        self.p = theme / "portrait_hdpi"
        self.check = check
        self.changes = []

    # helpers
    def read(self, f: Path) -> str:
        return f.read_bytes().decode("utf-8", "replace")

    def write(self, f: Path, new: str, what: str):
        old = self.read(f) if f.exists() else None
        if old == new:
            return
        self.changes.append(f"{f.relative_to(self.t)}: {what}")
        if not self.check:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(new.encode("utf-8"))

    def copy(self, src: Path, dst: Path):
        if dst.exists() and dst.read_bytes() == src.read_bytes():
            return
        self.changes.append(f"{dst.relative_to(self.t)}: copied")
        if not self.check:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)

    # steps
    def overlay(self):
        for src in sorted(OVERLAY.rglob("*")):
            if src.is_file():
                self.copy(src, self.t / src.relative_to(OVERLAY))

    def ui_include(self):
        f = self.p / "ui.xml"
        s = self.read(f)
        if "cyberfox.xml" in s:
            return
        s2, n = re.subn(r'([ \t]*)<xml name="/twres/pages/fox.xml"/>',
                        r'\g<0>\n\1<xml name="/twres/pages/cyberfox.xml"/>', s, count=1)
        if not n:
            sys.exit("ui.xml: fox.xml include not found - unsupported OrangeFox version")
        self.write(f, s2, "include pages/cyberfox.xml")

    def accent(self):
        for f in sorted(self.p.rglob("*.xml")):
            s = self.read(f)
            s2 = s
            for a, b in ACCENT_MAP.items():
                s2 = re.sub(a, b, s2, flags=re.I)
            if s2 != s:
                self.write(f, s2, "orange accent -> electric blue")

    def cyber_style(self):
        black = self.p / "themes/styles/Black.xml"
        s = self.read(black)
        if MARK in s:
            return
        for k, v in STYLE_VARS.items():
            s, n = re.subn(rf'(<variable name="{k}" value=")[^"]*(")', rf"\g<1>{v}\g<2>", s)
        for a, b in TINT_MAP.items():
            s = re.sub(f'tint="{a}"', f'tint="{b}"', s, flags=re.I)
        s = s.replace("<recovery>", "<recovery>\r\n\t<!-- CyberFox Plasma Circuit style (generated from Black) -->", 1)
        self.write(black, s, "Black -> CyberFox Plasma Circuit style")
        self.write(self.p / "themes/style.xml", s, "default style = CyberFox")

    def fonts(self):
        for f in [self.p / "themes/font.xml"] + sorted((self.p / "themes/sed").glob("font_*.xml")):
            s = self.read(f)
            if MARK in s:
                continue
            if f.name == "font.xml":
                for a, b in FONT_MAP.items():
                    s = s.replace(f'"{a}.ttf"', f'"{b}.ttf"')
                s = re.sub(r'(filename="Rajdhani-[A-Za-z]+\.ttf" size=")(\d+)"',
                           lambda m: f'{m.group(1)}{round(int(m.group(2)) * FONT_SCALE)}"', s)
                s = s.replace("<resources>", "<resources>\r\n\t\t<!-- CyberFox: Rajdhani -->", 1)
                self.write(f, s, "fonts -> Rajdhani")

    def splash_templates(self):
        for f in sorted((self.p / "themes/sed").glob("splash*.xml")):
            s = self.read(f)
            s2 = s.replace("<text>OrangeFox</text>", "<text>CyberFox</text>")
            if s2 != s:
                self.write(f, s2, "splash label -> CyberFox")

    def languages(self):
        for f in sorted((self.t / "common/languages").glob("*.xml")):
            s = self.read(f)
            def fix(m):
                if m.group(1) == "fox_websites":
                    return m.group(0)
                return m.group(0).replace("OrangeFox", "CyberFox")
            s2 = re.sub(r'<string name="([^"]+)">[^<]*</string>', fix, s)
            if s2 != s:
                self.write(f, s2, "OrangeFox -> CyberFox in strings")

    def header(self):
        f = self.p / "pages/templates/base.xml"
        s = self.read(f)
        if "cfx_header" in s:
            return
        n = 0
        for tpl in ("ab_main", "ab_ex"):
            s, k = re.subn(rf'(<template name="{tpl}">\s*<template name="status_bg"/>)',
                           lambda m: m.group(1) + HEADER_XML, s, count=1)
            n += k
        if not n:
            sys.exit("base.xml: ab_main/ab_ex templates not found")
        self.write(f, s, f"circuit header + glow line in {n} action-bar templates")

    def settings_entry(self):
        f = self.p / "pages/settings.xml"
        s = self.read(f)
        if 'function="page">cyberfox<' in s:
            return
        s2, n = re.subn(r'(<page name="settings">\s*<listbox style="group_list">\s*<placement[^>]*/>\s*<iconsize[^>]*/>)',
                        lambda m: m.group(1) + LAB_ITEM, s, count=1)
        if not n:
            sys.exit("settings.xml: settings listbox not found")
        self.write(f, s2, "CyberFox Lab entry at top of Settings")

    def recolor_pngs(self):
        try:
            from PIL import Image
        except ImportError:
            print("note: Pillow not installed, 4 orange PNG icons keep their colour (pip install pillow)")
            return
        for rel in ORANGE_PNGS:
            f = self.p / "images" / rel
            if not f.exists():
                continue
            im = Image.open(f).convert("RGBA")
            if im.info.get("cyberfox") or self._is_blue(im):
                continue
            px = im.load()
            for y in range(im.height):
                for x in range(im.width):
                    r, g, b, a = px[x, y]
                    if not a:
                        continue
                    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                    if 0.0 <= h < 0.17 and s > 0.25:
                        nh = 0.585 + (h / 0.17) * 0.05  # orange..yellow -> electric blue
                        r2, g2, b2 = colorsys.hsv_to_rgb(nh, s * 0.82, v)
                        px[x, y] = (int(r2 * 255), int(g2 * 255), int(b2 * 255), a)
            self.changes.append(f"portrait_hdpi/images/{rel}: hue-shifted orange -> blue")
            if not self.check:
                im.save(f, optimize=True)

    @staticmethod
    def _is_blue(im):
        n = o = 0
        for r, g, b, a in list(im.getdata() if not hasattr(im, "get_flattened_data") else im.get_flattened_data())[::11]:
            if a < 40:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s > 0.5 and v > 0.4:
                o += 0.02 < h < 0.12
                n += 0.55 < h < 0.8
        return n > o

    def run(self):
        if not (self.p / "ui.xml").exists():
            sys.exit(f"{self.p}/ui.xml not found - is this an OrangeFox gui/theme dir?")
        for step in (self.overlay, self.ui_include, self.accent, self.cyber_style, self.fonts,
                     self.splash_templates, self.languages, self.header, self.settings_entry,
                     self.recolor_pngs):
            step()
        verb = "would change" if self.check else "changed"
        print(f"CyberFox theme: {len(self.changes)} files {verb}")
        for c in self.changes:
            print("  " + c)
        return self.changes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--top", type=Path, help="OrangeFox source root (contains bootable/recovery)")
    g.add_argument("--theme-dir", type=Path, help="path to gui/theme directly")
    ap.add_argument("--check", action="store_true", help="report changes without writing")
    a = ap.parse_args()
    theme = a.theme_dir or a.top / "bootable/recovery/gui/theme"
    Patcher(theme.resolve(), a.check).run()


if __name__ == "__main__":
    main()
