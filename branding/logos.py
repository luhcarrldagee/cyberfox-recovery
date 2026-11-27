"""CyberFox logo concepts (Plasma Circuit palette).

Every logo is plain SVG (paths, polygons, circles, linear gradients, opacity)
so OrangeFox's nanosvg renderer can draw it inside recovery. The glow halo in
the previews is a separate blurred PNG layer, which is how the recovery shows it.
"""
from pathlib import Path

OUT = Path(__file__).parent / "logos"
OUT.mkdir(exist_ok=True)
BLUE, VIOLET, ICE = "#2F8CFF", "#A066FF", "#D6E6FF"

GRAD = f'''<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
 <stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="gv" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#5AA6FF"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="gd" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#16306E"/><stop offset="1" stop-color="#2A1257"/></linearGradient>
</defs>'''


def svg(body, vb="0 0 256 256"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="512" height="512">{GRAD}{body}</svg>'


# 1. Circuit Fox: faceted solid head, circuit traces running out of the ears
circuit_fox = svg(f'''
<g stroke="url(#g)" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
 <path d="M58 60 L58 28 L30 28"/><path d="M198 60 L198 28 L226 28"/>
 <path d="M44 112 L18 112 L18 150"/><path d="M212 112 L238 112 L238 150"/>
</g>
<g fill="{VIOLET}"><circle cx="30" cy="28" r="7"/><circle cx="226" cy="28" r="7"/>
 <circle cx="18" cy="150" r="7"/><circle cx="238" cy="150" r="7"/></g>
<polygon points="58,60 104,98 128,90 152,98 198,60 186,140 128,214 70,140" fill="url(#gd)"
 stroke="url(#g)" stroke-width="6" stroke-linejoin="round"/>
<polygon points="58,60 104,98 92,128" fill="{BLUE}" fill-opacity="0.55"/>
<polygon points="198,60 152,98 164,128" fill="{VIOLET}" fill-opacity="0.55"/>
<polygon points="128,90 152,98 128,150 104,98" fill="#5AA6FF" fill-opacity="0.25"/>
<polygon points="84,134 116,142 108,150 88,146" fill="{ICE}"/>
<polygon points="172,134 140,142 148,150 168,146" fill="{ICE}"/>
<polygon points="118,186 138,186 128,200" fill="{ICE}"/>
<path d="M128 150 L128 184" stroke="url(#gv)" stroke-width="4"/>
''')

# 2. Hex Fox: fox mask inside a hexagon badge with a circuit ring
hex_fox = svg(f'''
<polygon points="128,14 226,71 226,185 128,242 30,185 30,71" fill="#04061A"
 stroke="url(#g)" stroke-width="7" stroke-linejoin="round"/>
<polygon points="128,34 208,80 208,176 128,222 48,176 48,80" fill="none"
 stroke="{BLUE}" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="10 8"/>
<path d="M76 70 L110 104 L128 98 L146 104 L180 70 L172 140 L128 192 L84 140 Z"
 fill="none" stroke="url(#g)" stroke-width="7" stroke-linejoin="round"/>
<path d="M110 104 L128 150 L146 104" fill="none" stroke="url(#gv)" stroke-width="5" stroke-linejoin="round"/>
<polygon points="96,132 120,138 114,146" fill="{ICE}"/><polygon points="160,132 136,138 142,146" fill="{ICE}"/>
<path d="M128 150 L128 172" stroke="{VIOLET}" stroke-width="5" stroke-linecap="round"/>
<g fill="{VIOLET}"><circle cx="128" cy="14" r="8"/><circle cx="226" cy="185" r="8"/><circle cx="30" cy="185" r="8"/></g>
<g fill="{BLUE}"><circle cx="226" cy="71" r="6"/><circle cx="30" cy="71" r="6"/><circle cx="128" cy="242" r="6"/></g>
''')

# 3. Tail Monogram: fox ears on top of a circuit "C", tail swoosh, "F" trace inside
monogram = svg(f'''
<path d="M188 70 A82 82 0 1 0 188 186" fill="none" stroke="url(#g)" stroke-width="18" stroke-linecap="round"/>
<polygon points="74,62 92,18 118,50" fill="url(#gv)"/>
<polygon points="138,50 164,18 182,62" fill="url(#gv)"/>
<path d="M188 186 C212 172 232 196 214 222 C204 236 180 238 164 228" fill="none"
 stroke="{VIOLET}" stroke-width="10" stroke-linecap="round"/>
<g stroke="{ICE}" stroke-width="9" stroke-linecap="round" fill="none">
 <path d="M112 92 L112 168"/><path d="M112 92 L158 92"/><path d="M112 128 L148 128"/></g>
<g fill="{BLUE}"><circle cx="158" cy="92" r="9"/><circle cx="148" cy="128" r="9"/></g>
<circle cx="112" cy="168" r="9" fill="{VIOLET}"/>
''')

LOGOS = {"1_circuit_fox": ("Circuit Fox", circuit_fox),
         "2_hex_fox": ("Hex Fox", hex_fox),
         "3_tail_monogram": ("Tail Monogram", monogram)}

for k, (_, s) in LOGOS.items():
    (OUT / f"{k}.svg").write_text(s)
