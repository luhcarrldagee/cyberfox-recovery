"""Render CyberFox recovery UI mockups (1080x2400, Pixel 6a) for 3 design options."""
import json
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
FONTS = (ROOT / "fonts").as_uri()

THEMES = {
    "A_neon_grid": dict(
        name="Neon Grid", bg="#03060D", bg2="#061024", card="rgba(0,229,255,0.06)",
        line="rgba(0,229,255,0.35)", accent="#00E5FF", accent2="#0091FF", text="#C9F7FF",
        sub="#6FB8D6", head="Orbitron", body="Exo2", radius="6px", cut=True,
        deco="grid", tag="Cyan neon on deep navy, HUD grid, cut-corner panels"),
    "B_plasma_circuit": dict(
        name="Plasma Circuit", bg="#000000", bg2="#05051A", card="rgba(47,140,255,0.08)",
        line="rgba(47,140,255,0.45)", accent="#2F8CFF", accent2="#A066FF", text="#D6E6FF",
        sub="#7F95C8", head="Rajdhani", body="Rajdhani", radius="14px", cut=False,
        deco="circuit", tag="Electric blue + plasma violet, circuit traces, AMOLED black"),
    "C_holo_glass": dict(
        name="Holo Glass", bg="#040A14", bg2="#0B1C33", card="rgba(140,233,255,0.07)",
        line="rgba(140,233,255,0.22)", accent="#8BE9FF", accent2="#3D7BFF", text="#EAFBFF",
        sub="#8FB3C9", head="Exo2", body="Exo2", radius="40px", cut=False,
        deco="aurora", tag="Ice-blue holographic glass cards, soft aurora, minimal"),
}

ICONS = {
    "install": '<path d="M12 3v12m0 0l-5-5m5 5l5-5M4 19h16"/>',
    "wipe": '<path d="M4 7h16M9 7V4h6v3m-8 0l1 13h8l1-13"/>',
    "backup": '<path d="M12 16V6m0 0l-4 4m4-4l4 4M5 20h14"/>',
    "restore": '<path d="M4 12a8 8 0 1 0 3-6.2M4 4v4h4"/>',
    "files": '<path d="M3 6h7l2 2h9v11H3z"/>',
    "term": '<path d="M4 6l6 6-6 6M12 18h8"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6z"/>',
    "slot": '<path d="M7 7h10l-3-3m3 13H7l3 3"/>',
    "rescue": '<path d="M12 2v6m0 8v6M2 12h6m8 0h6"/><circle cx="12" cy="12" r="4"/>',
    "broom": '<path d="M14 4l6 6M4 20l8-8m-6 0l6 6"/>',
    "vault": '<rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="12" cy="12" r="3"/>',
    "chip": '<rect x="7" y="7" width="10" height="10"/><path d="M9 3v4m6-4v4M9 17v4m6-4v4M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    "report": '<path d="M6 3h9l3 3v15H6zM9 12h6M9 16h6"/>',
    "power": '<path d="M12 3v9M6.3 6.3a8 8 0 1 0 11.4 0"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
}


def icon(k, size=64, color="currentColor"):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[k]}</svg>')


FINAL = "--final" in sys.argv
GLITCH = (ROOT.parent / "branding/png/cyberfox_logo.svg").read_text() if FINAL else ""


def logo(t, size=360):
    if FINAL:
        body = re.sub(r"^<\?xml[^>]*>\s*", "", GLITCH)
        body = re.sub(r'width="[^"]*" height="[^"]*"', f'width="{size}" height="{size * 200 // 216}"', body, count=1)
        return f'<span style="display:inline-block;filter:drop-shadow(0 0 18px #2F8CFF) drop-shadow(0 0 40px #A066FF80)">{body}</span>'
    a, b = t["accent"], t["accent2"]
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 200 200">
  <defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>
    <filter id="gl"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <g filter="url(#gl)" fill="none" stroke="url(#lg)" stroke-width="5" stroke-linejoin="round">
    <path d="M30 30 L78 72 L100 64 L122 72 L170 30 L160 104 L100 172 L40 104 Z"/>
    <path d="M78 72 L100 120 L122 72"/>
    <path d="M58 104 L82 112 M142 104 L118 112"/>
    <path d="M100 120 L100 150"/>
  </g>
  <g fill="{a}" filter="url(#gl)">
    <circle cx="82" cy="112" r="6"/><circle cx="118" cy="112" r="6"/>
    <circle cx="30" cy="30" r="5"/><circle cx="170" cy="30" r="5"/><circle cx="100" cy="150" r="5"/>
  </g></svg>'''


def deco(t):
    a = t["accent"]
    if t["deco"] == "grid":
        return f'''<div class="deco" style="background:
          linear-gradient(rgba(0,229,255,.07) 2px, transparent 2px) 0 0/90px 90px,
          linear-gradient(90deg, rgba(0,229,255,.07) 2px, transparent 2px) 0 0/90px 90px,
          radial-gradient(ellipse at 50% 0%, rgba(0,145,255,.25), transparent 60%);"></div>
          <div class="scan"></div>'''
    if t["deco"] == "circuit":
        paths = "".join(
            f'<path d="M{x} 0 V{y} H{x+dx} V2400" />' for x, y, dx in
            [(80, 600, 120), (300, 1500, -140), (760, 900, 160), (980, 1800, -200), (520, 2100, 90)])
        dots = "".join(f'<circle cx="{x}" cy="{y}" r="9"/>' for x, y in
                       [(80, 600), (200, 600), (300, 1500), (160, 1500), (760, 900), (920, 900), (980, 1800), (780, 1800)])
        return f'''<svg class="deco" viewBox="0 0 1080 2400" preserveAspectRatio="none">
          <g stroke="{a}" stroke-opacity=".12" stroke-width="3" fill="none">{paths}</g>
          <g fill="{t["accent2"]}" fill-opacity=".3">{dots}</g></svg>
          <div class="deco" style="background:radial-gradient(ellipse at 90% 10%, rgba(160,102,255,.22), transparent 50%),
            radial-gradient(ellipse at 0% 100%, rgba(47,140,255,.2), transparent 55%)"></div>'''
    return '''<div class="deco" style="background:
        radial-gradient(ellipse 900px 600px at 15% 8%, rgba(61,123,255,.35), transparent 70%),
        radial-gradient(ellipse 800px 700px at 95% 55%, rgba(139,233,255,.18), transparent 70%),
        radial-gradient(ellipse 900px 600px at 30% 100%, rgba(120,90,255,.2), transparent 70%);"></div>'''


def css(t):
    clip = ("clip-path: polygon(28px 0,100% 0,100% calc(100% - 28px),calc(100% - 28px) 100%,0 100%,0 28px);"
            if t["cut"] else "")
    glass = "backdrop-filter: blur(30px);" if t["deco"] == "aurora" else ""
    return f'''
@font-face{{font-family:Orbitron;src:url({FONTS}/Orbitron.ttf)}}
@font-face{{font-family:Exo2;src:url({FONTS}/Exo2-Regular.ttf);font-weight:400}}
@font-face{{font-family:Exo2;src:url({FONTS}/Exo2-Medium.ttf);font-weight:600}}
@font-face{{font-family:Rajdhani;src:url({FONTS}/Rajdhani-SemiBold.ttf)}}
@font-face{{font-family:Fira;src:url({FONTS}/FiraCode-Medium.ttf)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:2400px;overflow:hidden;background:linear-gradient(180deg,{t["bg"]},{t["bg2"]});
  color:{t["text"]};font-family:{t["body"]};position:relative}}
.deco{{position:absolute;inset:0;width:1080px;height:2400px}}
.scan{{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 2px,transparent 2px 6px)}}
.glow{{color:{t["accent"]};text-shadow:0 0 8px {t["accent"]},0 0 24px {t["accent"]},0 0 48px {t["accent2"]}}}
.head{{font-family:{t["head"]};letter-spacing:4px}}
.status{{position:absolute;top:0;left:0;right:0;height:120px;display:flex;align-items:center;
  justify-content:space-between;padding:30px 56px 0;font-size:38px;font-family:{t["body"]};color:{t["text"]}}}
.panel{{background:{t["card"]};border:2px solid {t["line"]};border-radius:{t["radius"]};{clip}{glass}
  box-shadow:0 0 30px rgba(0,0,0,.4), inset 0 0 40px {t["card"]}}}
.sub{{color:{t["sub"]}}}
.bar{{height:18px;border-radius:9px;background:rgba(255,255,255,.08);overflow:hidden}}
.bar>i{{display:block;height:100%;background:linear-gradient(90deg,{t["accent2"]},{t["accent"]});
  box-shadow:0 0 20px {t["accent"]}}}
.ico{{color:{t["accent"]};filter:drop-shadow(0 0 8px {t["accent"]})}}
.nav{{position:absolute;bottom:0;left:0;right:0;height:210px;display:flex;justify-content:space-around;
  align-items:center;border-top:2px solid {t["line"]};background:rgba(0,0,0,.35);font-size:32px}}
.nav div{{display:flex;flex-direction:column;align-items:center;gap:10px;color:{t["sub"]}}}
.nav .on{{color:{t["accent"]};text-shadow:0 0 12px {t["accent"]}}}
.toggle{{width:120px;height:64px;border-radius:32px;background:{t["accent"]};position:relative;
  box-shadow:0 0 22px {t["accent"]}}}
.toggle:after{{content:"";position:absolute;right:8px;top:8px;width:48px;height:48px;border-radius:50%;background:{t["bg"]}}}
.toggle.off{{background:rgba(255,255,255,.15);box-shadow:none}}
.toggle.off:after{{left:8px;right:auto;background:{t["sub"]}}}
'''


def status(t):
    return f'''<div class="status"><span>12:45</span>
      <span class="sub" style="font-family:Fira;font-size:32px">CPU 38°C · SLOT A</span><span>87%</span></div>'''


def splash(t):
    return f'''{deco(t)}{status(t)}
<div style="position:absolute;top:640px;width:100%;text-align:center">{logo(t, 440)}</div>
<div class="head glow" style="position:absolute;top:1200px;width:100%;text-align:center;font-size:132px;font-weight:700">CYBERFOX</div>
<div class="head sub" style="position:absolute;top:1370px;width:100%;text-align:center;font-size:46px;letter-spacing:18px">RECOVERY</div>
<div style="position:absolute;top:1900px;left:240px;right:240px"><div class="bar"><i style="width:64%"></i></div>
  <div class="sub" style="text-align:center;margin-top:34px;font-family:Fira;font-size:30px;white-space:nowrap;margin-left:-120px;margin-right:-120px">decrypting /data · loading modules</div></div>
<div class="sub" style="position:absolute;bottom:90px;width:100%;text-align:center;font-size:32px">R12.0 · Pixel 6a (bluejay) · based on OrangeFox</div>'''


def home(t):
    tiles = [("install", "Install"), ("wipe", "Wipe"), ("backup", "Backup"),
             ("restore", "Restore"), ("files", "Files"), ("term", "Terminal")]
    grid = "".join(f'''<div class="panel" style="height:300px;display:flex;flex-direction:column;align-items:center;
        justify-content:center;gap:26px"><span class="ico">{icon(k, 96)}</span>
        <span style="font-size:44px;font-weight:600">{n}</span></div>''' for k, n in tiles)
    return f'''{deco(t)}{status(t)}
<div style="position:absolute;top:170px;left:56px;right:56px;display:flex;align-items:center;gap:30px">
  {logo(t, 130)}<div><div class="head glow" style="font-size:72px;font-weight:700">CYBERFOX</div>
  <div class="sub" style="font-size:34px">Pixel 6a · Android 17 · unlocked</div></div></div>
<div class="panel" style="position:absolute;top:400px;left:56px;right:56px;padding:44px 48px">
  <div style="display:flex;justify-content:space-between;font-size:40px"><span>Internal storage</span><span class="glow">82.4 / 128 GB</span></div>
  <div class="bar" style="margin:26px 0 40px"><i style="width:64%"></i></div>
  <div style="display:flex;justify-content:space-between;font-size:34px" class="sub">
    <span>Decrypted ✓</span><span>Battery 87% · 4.21 V</span><span>vendor_boot_a</span></div></div>
<div style="position:absolute;top:780px;left:56px;right:56px;display:grid;grid-template-columns:1fr 1fr;gap:40px">{grid}</div>
<div class="panel" style="position:absolute;top:1880px;left:56px;right:56px;height:150px;display:flex;align-items:center;gap:30px;padding:0 44px">
  <span class="ico">{icon("chip", 70)}</span><div><div style="font-size:42px;font-weight:600">CyberFox Lab</div>
  <div class="sub" style="font-size:32px">11 one-tap tools · prebuilt zips</div></div>
  <span class="glow" style="margin-left:auto;font-size:60px">›</span></div>
<div class="nav"><div class="on">{icon("menu", 60)}Menu</div><div>{icon("wipe", 60)}Wipe</div>
  <div>{icon("files", 60)}Files</div><div>{icon("backup", 60)}Backup</div></div>'''


TOOL_ICONS = {"backup-critical": "shield", "restore-critical": "restore", "vault-backup": "vault",
              "vault-restore": "vault", "avb-disable": "chip", "slot-switch": "slot", "rescue-modules": "rescue",
              "enable-modules": "rescue", "clean-caches": "broom", "restore-stock-recovery": "power", "report": "report"}


def lab_final(t):
    tools = json.loads((ROOT.parent / "zips/tools.json").read_text())["tools"]
    tools.append({"id": "", "title": "Interface and quick reboot", "desc": "Glow toggles, reboot to system or fastboot"})
    rows = "".join(f'''<div class="panel" style="height:112px;display:flex;align-items:center;gap:32px;padding:0 36px;margin-bottom:16px">
      <span class="ico">{icon(TOOL_ICONS.get(x["id"], "menu"), 58)}</span><div style="flex:1;min-width:0"><div style="font-size:38px;font-weight:600">{x["title"]}</div>
      <div class="sub" style="font-size:27px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{x["desc"]}</div></div>
      <span class="glow" style="font-size:50px">›</span></div>''' for x in tools)
    return f'''{deco(t)}{status(t)}
<div style="position:absolute;top:150px;left:56px;right:56px;display:flex;align-items:center;gap:28px">
  {logo(t, 110)}<div><div class="head glow" style="font-size:62px;font-weight:700">CYBERFOX LAB</div>
  <div class="sub" style="font-size:31px;margin-top:4px">11 tools · prebuilt zips in /FFiles/CyberFox</div></div></div>
<div style="position:absolute;top:340px;left:56px;right:56px">{rows}</div>
<div class="nav"><div>{icon("power", 60)}System</div><div>{icon("power", 60)}Bootloader</div>
  <div class="on">{icon("chip", 60)}Lab</div><div>{icon("restore", 60)}Recovery</div></div>'''


def lab(t):
    if FINAL:
        return lab_final(t)
    items = [("shield", "Backup critical partitions", "boot · vendor_boot · dtbo · vbmeta · efs"),
             ("restore", "Restore critical partitions", "SHA-256 verified before flashing"),
             ("vault", "File Vault backup / restore", "DCIM, Pictures, Download → USB-OTG"),
             ("chip", "Disable AVB / verity", "patches vbmeta flags on both slots"),
             ("slot", "Switch active slot", "A ⇄ B with confirmation"),
             ("rescue", "Bootloop rescue", "disables all Magisk / KernelSU modules"),
             ("broom", "Clean caches", "dalvik-cache + /data/cache, keeps data"),
             ("report", "Device report", "props, partitions, logs → /sdcard/CyberFox")]
    rows = "".join(f'''<div class="panel" style="height:150px;display:flex;align-items:center;gap:36px;padding:0 40px;margin-bottom:26px">
      <span class="ico">{icon(k, 72)}</span><div style="flex:1"><div style="font-size:42px;font-weight:600">{n}</div>
      <div class="sub" style="font-size:31px;margin-top:6px">{d}</div></div>
      <span class="glow" style="font-size:56px">›</span></div>''' for k, n, d in items)
    return f'''{deco(t)}{status(t)}
<div style="position:absolute;top:170px;left:56px;right:56px">
  <div class="head glow" style="font-size:66px;font-weight:700">CYBERFOX LAB</div>
  <div class="sub" style="font-size:34px;margin-top:10px">Tools run from built-in zips in /FFiles/CyberFox</div></div>
<div style="position:absolute;top:360px;left:56px;right:56px">{rows}
  <div class="panel" style="padding:30px 40px;display:flex;flex-direction:column;gap:30px">
    <div style="display:flex;align-items:center;justify-content:space-between;font-size:40px">HUD grid background<div class="toggle"></div></div>
    <div style="display:flex;align-items:center;justify-content:space-between;font-size:40px">Glow intensity: high<div class="toggle"></div></div>
    <div style="display:flex;align-items:center;justify-content:space-between;font-size:40px">Auto-backup before flash<div class="toggle off"></div></div>
  </div></div>
<div class="nav"><div>{icon("power", 60)}System</div><div>{icon("power", 60)}Bootloader</div>
  <div class="on">{icon("chip", 60)}Lab</div><div>{icon("restore", 60)}Recovery</div></div>'''


EXTRA = {
 "circuit": """.ico{color:#A066FF!important;filter:drop-shadow(0 0 10px #A066FF)!important}
  .panel{border-image:linear-gradient(135deg,#2F8CFF,#A066FF) 1;border-width:3px}
  .head{letter-spacing:10px;text-transform:uppercase}
  .glow{background:linear-gradient(90deg,#4FA3FF,#B07CFF);-webkit-background-clip:text;color:transparent!important;
   text-shadow:none;filter:drop-shadow(0 0 14px #2F8CFF) drop-shadow(0 0 30px #A066FF)}""",
 "aurora": """.panel{background:linear-gradient(160deg,rgba(255,255,255,.10),rgba(139,233,255,.03));
   border:2px solid rgba(255,255,255,.14);box-shadow:0 20px 60px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.25)}
  .nav{left:60px;right:60px;bottom:50px;height:170px;border-radius:85px;border:2px solid rgba(255,255,255,.14);
   background:rgba(255,255,255,.06);backdrop-filter:blur(30px)}
  .head{letter-spacing:2px;font-weight:600}""",
 "grid": """.panel{border-left:6px solid #00E5FF}
  .head{font-weight:800}""",
}

def page(t, body):
    return f"<html><head><style>{css(t)}{EXTRA[t['deco']]}</style></head><body>{body}</body></html>"


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 2400})
    for key, t in THEMES.items():
        if FINAL and key != "B_plasma_circuit":
            continue
        for nm, fn in [("1_splash", splash), ("2_home", home), ("3_lab", lab)]:
            hp = OUT / f"_{key}_{nm}.html"
            hp.write_text(page(t, fn(t)))
            pg.goto(hp.as_uri()); pg.wait_for_timeout(500)
            pg.screenshot(path=str(OUT / (f"final_{nm}.png" if FINAL else f"{key}_{nm}.png")))
            hp.unlink()
    b.close()
print("done")
