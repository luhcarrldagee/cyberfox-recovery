"""Generate every CyberFox image asset from the Glitch Fox logo.

Outputs
  theme/overlay/portrait_hdpi/images/SVG/Logos/logo_{o,w,d,cfx}.svg  (nanosvg-safe vector logo)
  theme/overlay/portrait_hdpi/images/Splash/{original,user}.png     (1080x2400 splash backdrop)
  theme/overlay/portrait_hdpi/images/Cyber/circuit_bg.png           (page backdrop, RGBA)
  theme/overlay/portrait_hdpi/images/Cyber/glow_line.png            (action-bar glow strip)
  theme/overlay/portrait_hdpi/images/Cyber/logo_glow.png            (halo behind logos)
  theme/overlay/portrait_hdpi/images/Cyber/cfx_icon.png             (108x108 settings icon)
  branding/png/*                                                     (logo, banner, splash renders)

Run: python3 branding/generate_assets.py
"""
import random
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "theme/overlay/portrait_hdpi/images"
PNG = ROOT / "branding/png"
FONTS = (ROOT / "theme/overlay/common/fonts").as_uri()
for d in (IMG / "SVG/Logos", IMG / "Splash", IMG / "Cyber", PNG):
    d.mkdir(parents=True, exist_ok=True)

BLUE, VIOLET, ICE, DEEP1, DEEP2 = "#2F8CFF", "#A066FF", "#D6E6FF", "#16306E", "#2A1257"
HEAD = "50,44 100,90 128,82 156,90 206,44 196,136 128,220 60,136"

# Vector logo: only polygons, rects, linear gradients, opacity and translate,
# which nanosvg (the OrangeFox GUI SVG renderer) supports. viewBox is cropped
# to the mark so OrangeFox's scale="2.0" produces a ~430px splash logo.
LOGO_BODY = f'''<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="gd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{DEEP1}"/><stop offset="1" stop-color="{DEEP2}"/></linearGradient>
</defs>
<polygon points="{HEAD}" fill="{VIOLET}" fill-opacity="0.45" transform="translate(8,0)"/>
<polygon points="{HEAD}" fill="{BLUE}" fill-opacity="0.45" transform="translate(-8,0)"/>
<polygon points="{HEAD}" fill="url(#gd)" stroke="url(#g)" stroke-width="5" stroke-linejoin="round"/>
<polygon points="84,128 118,138 110,148 88,142" fill="{ICE}"/>
<polygon points="172,128 138,138 146,148 168,142" fill="{ICE}"/>
<polygon points="118,190 138,190 128,204" fill="{ICE}"/>
<rect x="30" y="100" width="70" height="6" fill="{BLUE}"/>
<rect x="170" y="164" width="64" height="6" fill="{VIOLET}"/>
<rect x="150" y="70" width="40" height="4" fill="{ICE}" fill-opacity="0.8"/>
<rect x="44" y="176" width="40" height="4" fill="{ICE}" fill-opacity="0.8"/>'''
VB = (20, 30, 216, 200)


def logo_svg(w=None, h=None):
    w, h = w or VB[2], h or VB[3]
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{VB[0]} {VB[1]} {VB[2]} {VB[3]}" width="{w}" height="{h}">\n{LOGO_BODY}\n</svg>\n')


for name in ("logo_o", "logo_w", "logo_d", "logo_cfx"):
    (IMG / "SVG/Logos" / f"{name}.svg").write_text(logo_svg())
(PNG / "cyberfox_logo.svg").write_text(logo_svg())


def circuit_svg(w, h, seed, opacity, dots=True):
    """Random orthogonal circuit traces with via dots."""
    rnd = random.Random(seed)
    paths, vias = [], []
    for _ in range(22):
        x, y = rnd.randrange(40, w - 40, 30), rnd.randrange(0, h, 40)
        d = f"M{x} {y}"
        for _ in range(rnd.randint(2, 4)):
            if rnd.random() < 0.5:
                y = max(0, min(h, y + rnd.choice([-1, 1]) * rnd.randrange(120, 520, 40)))
            else:
                x = max(30, min(w - 30, x + rnd.choice([-1, 1]) * rnd.randrange(60, 300, 30)))
            d += f" L{x} {y}"
        paths.append(d)
        vias.append((x, y))
    p = "".join(f'<path d="{d}"/>' for d in paths)
    v = "".join(f'<circle cx="{x}" cy="{y}" r="8"/>' for x, y in vias) if dots else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<g fill="none" stroke="{BLUE}" stroke-opacity="{opacity}" stroke-width="3" '
            f'stroke-linejoin="round">{p}</g><g fill="{VIOLET}" fill-opacity="{opacity*1.8}">{v}</g></svg>')


def html(body, w, h, bg="transparent"):
    return f'''<html><head><style>
@font-face{{font-family:R;src:url({FONTS}/Rajdhani-SemiBold.ttf)}}
@font-face{{font-family:RB;src:url({FONTS}/Rajdhani-Bold.ttf)}}
*{{margin:0;padding:0}} html,body{{width:{w}px;height:{h}px;background:{bg};overflow:hidden}}
.abs{{position:absolute}}
</style></head><body>{body}</body></html>'''


def big_logo(px):
    return logo_svg(px, round(px * VB[3] / VB[2])).split("\n", 1)[1]


JOBS = []

# Splash backdrop: AMOLED black, violet/blue nebula, circuit traces, halo at the
# exact centre (OrangeFox centres both the backdrop and the logo on %center_y%).
splash = f'''<div class="abs" style="inset:0;background:
  radial-gradient(ellipse 620px 520px at 50% 50%, rgba(47,140,255,.30), transparent 70%),
  radial-gradient(ellipse 900px 700px at 100% 0%, rgba(160,102,255,.22), transparent 70%),
  radial-gradient(ellipse 900px 700px at 0% 100%, rgba(47,140,255,.20), transparent 70%), #000"></div>
<div class="abs" style="inset:0">{circuit_svg(1080, 2400, 7, 0.16)}</div>
<div class="abs" style="inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 2px,transparent 2px 6px)"></div>'''
JOBS += [("splash_bg", IMG / "Splash/original.png", 1080, 2400, html(splash, 1080, 2400, "#000"), False)]

# Page backdrop: very faint traces, mostly transparent so text stays readable.
JOBS += [("circuit_bg", IMG / "Cyber/circuit_bg.png", 1080, 2400,
          html(f'<div class="abs" style="inset:0">{circuit_svg(1080, 2400, 21, 0.09)}</div>', 1080, 2400), True)]

# Glow strip drawn under the action bar on every page.
JOBS += [("glow_line", IMG / "Cyber/glow_line.png", 1080, 36, html(f'''
<div class="abs" style="left:0;right:0;top:12px;height:12px;filter:blur(7px);
 background:linear-gradient(90deg,transparent,{BLUE} 25%,{VIOLET} 75%,transparent)"></div>
<div class="abs" style="left:0;right:0;top:17px;height:2px;
 background:linear-gradient(90deg,transparent,{BLUE} 20%,{VIOLET} 80%,transparent)"></div>''', 1080, 36), True)]

# Halo placed behind the logo on the splash and About/Lab pages.
JOBS += [("logo_glow", IMG / "Cyber/logo_glow.png", 640, 640, html(f'''
<div class="abs" style="left:120px;top:120px;width:400px;height:400px;border-radius:50%;filter:blur(70px);
 background:radial-gradient(circle,{BLUE} 0%,{VIOLET} 60%,transparent 75%);opacity:.75"></div>''', 640, 640), True)]

# 108x108 icon for the Settings list (same footprint as stock bs_btn_* icons).
JOBS += [("cfx_icon", IMG / "Cyber/cfx_icon.png", 108, 108, html(f'''
<div class="abs" style="inset:0;border-radius:50%;background:rgba(47,140,255,.20)"></div>
<div class="abs" style="left:14px;top:18px">{big_logo(80)}</div>''', 108, 108), True)]

# Branding renders.
glow_logo = lambda px: f'''<div style="position:relative;width:{px}px;height:{round(px*VB[3]/VB[2])}px">
<div class="abs" style="inset:0;filter:blur({px//14}px);opacity:.9">{big_logo(px)}</div>
<div class="abs" style="inset:0">{big_logo(px)}</div></div>'''
JOBS += [("logo_1024", PNG / "cyberfox_logo_1024.png", 1024, 1024, html(
    f'<div style="display:flex;align-items:center;justify-content:center;height:1024px">{glow_logo(760)}</div>',
    1024, 1024), True)]
JOBS += [("logo_512_dark", PNG / "cyberfox_logo_512_dark.png", 512, 512, html(
    f'<div style="display:flex;align-items:center;justify-content:center;height:512px">{glow_logo(380)}</div>',
    512, 512, "#000"), False)]
word = (f'background:linear-gradient(90deg,#4FA3FF,#B07CFF);-webkit-background-clip:text;color:transparent;'
        f'filter:drop-shadow(0 0 14px {BLUE}) drop-shadow(0 0 30px {VIOLET})')
JOBS += [("banner", PNG / "cyberfox_banner.png", 1600, 600, html(f'''
<div class="abs" style="inset:0;background:radial-gradient(ellipse at 20% 50%,rgba(47,140,255,.25),transparent 60%),
 radial-gradient(ellipse at 90% 0%,rgba(160,102,255,.25),transparent 60%),#000"></div>
<div class="abs" style="inset:0">{circuit_svg(1600, 600, 3, 0.14)}</div>
<div class="abs" style="left:110px;top:120px">{glow_logo(390)}</div>
<div class="abs" style="left:600px;top:170px;font-family:RB;font-size:150px;letter-spacing:16px;{word}">CYBERFOX</div>
<div class="abs" style="left:610px;top:350px;font-family:R;font-size:42px;letter-spacing:22px;color:#7F95C8">RECOVERY · PIXEL 6a</div>
''', 1600, 600, "#000"), False)]


def splash_preview():
    return html(f'''{splash}
<div class="abs" style="left:220px;top:880px;width:640px;height:640px;background:url(../../theme/overlay/portrait_hdpi/images/Cyber/logo_glow.png)"></div>
<div class="abs" style="left:324px;top:1000px">{big_logo(432)}</div>
<div class="abs" style="top:1560px;width:1080px;text-align:center;font-family:RB;font-size:120px;letter-spacing:14px;{word}">CYBERFOX</div>
<div class="abs" style="top:1720px;width:1080px;text-align:center;font-family:R;font-size:46px;letter-spacing:20px;color:#7F95C8">RECOVERY</div>''',
        1080, 2400, "#000")


with sync_playwright() as p:
    b = p.chromium.launch()
    for name, out, w, h, doc, transparent in JOBS:
        pg = b.new_page(viewport={"width": w, "height": h})
        tmp = PNG / f"_{name}.html"
        tmp.write_text(doc)
        pg.goto(tmp.as_uri())
        pg.wait_for_timeout(250)
        pg.screenshot(path=str(out), omit_background=transparent)
        tmp.unlink()
        pg.close()
    # splash preview needs logo_glow.png, generated above
    pg = b.new_page(viewport={"width": 1080, "height": 2400})
    tmp = PNG / "_splash_preview.html"
    tmp.write_text(splash_preview())
    pg.goto(tmp.as_uri())
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(PNG / "cyberfox_splash_preview.png"))
    tmp.unlink()
    b.close()

# OrangeFox treats Splash/user.png as the active splash backdrop; ship ours there
# too so the CyberFox splash is the default before any user customisation.
(IMG / "Splash/user.png").write_bytes((IMG / "Splash/original.png").read_bytes())

# Quantise the large backdrops to keep the recovery ramdisk small.
from PIL import Image
for f in (IMG / "Splash/original.png", IMG / "Splash/user.png"):
    Image.open(f).convert("RGB").quantize(colors=128, dither=Image.Dither.NONE).save(f, optimize=True)
for f in (IMG / "Cyber/circuit_bg.png",):
    Image.open(f).quantize(colors=64, method=Image.Quantize.FASTOCTREE).save(f, optimize=True)
# Header strip drawn behind every action bar (pages render lists before the
# base template, so a full-screen backdrop would cover content; the header is safe).
hdr = Image.open(IMG / "Cyber/circuit_bg.png").convert("RGBA").crop((0, 300, 1080, 540))
fade = Image.new("L", (1080, 240))
for y in range(240):
    fade.paste(int(255 * (0.35 + 0.65 * y / 239)), (0, y, 1080, y + 1))
hdr.putalpha(Image.composite(hdr.getchannel("A"), Image.new("L", (1080, 240), 0), fade))
tint = Image.new("RGBA", (1080, 240), (47, 140, 255, 0))
for y in range(240):
    tint.paste((47, 140, 255, int(26 * y / 239)), (0, y, 1080, y + 1))
Image.alpha_composite(tint, hdr).save(IMG / "Cyber/header_bg.png", optimize=True)
print("assets ok")
