"""CyberFox logo concepts, round 2 (nanosvg-safe SVG)."""
from logos import svg, OUT, BLUE, VIOLET, ICE

# 4. Visor Fox: angular head with a glowing horizontal visor band across the eyes
visor = svg(f'''
<polygon points="52,40 100,84 128,78 156,84 204,40 196,128 128,218 60,128" fill="url(#gd)"
 stroke="url(#g)" stroke-width="6" stroke-linejoin="round"/>
<polygon points="64,58 92,84 70,96" fill="{BLUE}" fill-opacity="0.6"/>
<polygon points="192,58 164,84 186,96" fill="{VIOLET}" fill-opacity="0.6"/>
<polygon points="40,112 216,112 206,140 50,140" fill="{BLUE}" fill-opacity="0.18"/>
<polygon points="46,116 210,116 202,136 54,136" fill="url(#g)"/>
<rect x="74" y="122" width="34" height="8" fill="{ICE}"/><rect x="148" y="122" width="34" height="8" fill="{ICE}"/>
<path d="M128 140 L128 176" stroke="url(#gv)" stroke-width="5" stroke-linecap="round"/>
<polygon points="116,180 140,180 128,198" fill="{ICE}"/>
<g fill="{VIOLET}"><circle cx="40" cy="126" r="6"/><circle cx="216" cy="126" r="6"/></g>
''')

# 5. Power Fox: fox ears on a power symbol (recovery = power-on rescue)
power = svg(f'''
<path d="M86 78 A78 78 0 1 0 170 78" fill="none" stroke="url(#g)" stroke-width="18" stroke-linecap="round"/>
<path d="M128 40 L128 122" stroke="{ICE}" stroke-width="18" stroke-linecap="round"/>
<polygon points="58,96 66,26 108,64" fill="url(#gv)"/>
<polygon points="198,96 190,26 148,64" fill="url(#gv)"/>
<polygon points="70,82 72,46 94,66" fill="#04061A"/>
<polygon points="186,82 184,46 162,66" fill="#04061A"/>
<polygon points="98,150 120,158 112,166" fill="{ICE}"/><polygon points="158,150 136,158 144,166" fill="{ICE}"/>
<polygon points="118,196 138,196 128,210" fill="{VIOLET}"/>
''')

# 6. Glitch Fox: fox head sliced into offset bands like a digital glitch
def band(y0, y1, dx, color, op):
    return (f'<clipPath id="c{y0}"><rect x="0" y="{y0}" width="256" height="{y1-y0}"/></clipPath>'
            f'<g clip-path="url(#c{y0})" transform="translate({dx},0)"><polygon points="{HEAD}" '
            f'fill="{color}" fill-opacity="{op}"/></g>')
HEAD = "50,44 100,90 128,82 156,90 206,44 196,136 128,220 60,136"
glitch = svg(f'''
<polygon points="{HEAD}" fill="{VIOLET}" fill-opacity="0.45" transform="translate(8,0)"/>
<polygon points="{HEAD}" fill="{BLUE}" fill-opacity="0.45" transform="translate(-8,0)"/>
<polygon points="{HEAD}" fill="url(#gd)" stroke="url(#g)" stroke-width="5" stroke-linejoin="round"/>
<polygon points="84,128 118,138 110,148 88,142" fill="{ICE}"/>
<polygon points="172,128 138,138 146,148 168,142" fill="{ICE}"/>
<polygon points="118,190 138,190 128,204" fill="{ICE}"/>
<rect x="30" y="100" width="70" height="6" fill="{BLUE}"/><rect x="170" y="164" width="64" height="6" fill="{VIOLET}"/>
<rect x="150" y="70" width="40" height="4" fill="{ICE}" fill-opacity="0.8"/>
<rect x="44" y="176" width="40" height="4" fill="{ICE}" fill-opacity="0.8"/>
''')

LOGOS = {"4_visor_fox": ("Visor Fox", visor),
         "5_power_fox": ("Power Fox", power),
         "6_glitch_fox": ("Glitch Fox", glitch)}
for k, (_, s) in LOGOS.items():
    (OUT / f"{k}.svg").write_text(s)
