from pathlib import Path
from playwright.sync_api import sync_playwright
import sys
sys.path.insert(0,".")
import importlib; M=importlib.import_module(sys.argv[1] if len(sys.argv)>1 else "logos"); LOGOS=M.LOGOS; NAME=sys.argv[2] if len(sys.argv)>2 else "logo_options"
F=(Path("../previews/fonts").resolve()).as_uri()
cards=""
for k,(n,s) in LOGOS.items():
    inner=s.replace('width="512" height="512"','width="380" height="380"')
    cards+=f'''<div class="card"><div class="stage"><div class="halo">{inner}</div><div class="crisp">{inner}</div></div>
    <div class="t">{n}</div><div class="row">
    <div class="sm">{s.replace('width="512" height="512"','width="120" height="120"')}</div>
    <div class="word"><div class="w">CYBERFOX</div><div class="r">RECOVERY</div></div></div></div>'''
html=f'''<html><head><style>
@font-face{{font-family:R;src:url({F}/Rajdhani-SemiBold.ttf)}}
@font-face{{font-family:O;src:url({F}/Orbitron.ttf)}}
body{{margin:0;width:1800px;height:1000px;background:radial-gradient(ellipse at 50% 0%,#0B0F33,#000 70%);font-family:R;color:#D6E6FF}}
h1{{font-family:O;color:#2F8CFF;font-size:54px;margin:40px 50px 0;text-shadow:0 0 18px #2F8CFF}}
.sub{{margin:6px 52px 0;font-size:28px;color:#7F95C8}}
.wrap{{display:flex;gap:40px;padding:40px 50px}}
.card{{flex:1;border:3px solid;border-image:linear-gradient(135deg,#2F8CFF,#A066FF) 1;background:#03051480;padding:30px;text-align:center}}
.stage{{position:relative;height:440px;display:flex;align-items:center;justify-content:center}}
.halo{{position:absolute;filter:blur(22px);opacity:.85}}.crisp{{position:relative}}
.t{{font-size:44px;letter-spacing:4px;margin:4px 0 20px}}
.row{{display:flex;align-items:center;justify-content:center;gap:22px;background:#000;padding:18px;border-top:1px solid #2F8CFF40}}
.word{{text-align:left}}.w{{font-size:58px;letter-spacing:8px;background:linear-gradient(90deg,#4FA3FF,#B07CFF);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 0 12px #2F8CFF)}}
.r{{font-size:24px;letter-spacing:14px;color:#7F95C8}}
</style></head><body><h1>CyberFox logo options{" - round 2" if NAME!="logo_options" else ""}</h1><div class="sub">Plasma Circuit palette · large mark with glow, plus the small header lockup</div>
<div class="wrap">{cards}</div></body></html>'''
Path("logos/_sheet.html").write_text(html)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1800,"height":1000})
    pg.goto(Path("logos/_sheet.html").resolve().as_uri()); pg.wait_for_timeout(600)
    pg.screenshot(path=f"logos/{NAME}.png"); b.close()
