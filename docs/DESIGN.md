# Plasma Circuit design notes

## Palette

| Token | Hex | Used for |
|---|---|---|
| background | `#000000` | AMOLED black page background |
| cards / groups | `#070A1A` | list groups, cards |
| accent | `#2F8CFF` | buttons, switches, progress, selection (replaces OrangeFox `#ED6F02`) |
| accent dark | `#1F6FE0` | pressed states (replaces `#D86100`) |
| accent light | `#5AA6FF` | page titles (`actbar_color`), splash wordmark, zip icons |
| plasma violet | `#A066FF` | glow gradient end, logo stroke |
| text | `#D6E6FF` | body text |
| text secondary | `#8EA2D6` | subtitles, captions |
| icon tint | `#BFD4FF` | all monochrome SVG icons (was white) |
| line | `#2F8CFF40` | dividers |
| highlight | `#2F8CFF2E` | touch highlight |

Warning colors (low battery, errors) stay warm on purpose so they still read as warnings.

## Glow in a recovery

The TWRP/OrangeFox renderer cannot blur or add text shadows. CyberFox gets its glow from pre-rendered PNGs:

- `Cyber/header_bg.png` (1080x240) is a circuit-trace strip drawn behind every action bar, with `cfx_hud` as its toggle.
- `Cyber/glow_line.png` (1080x36) is a blue-to-violet glowing rule under every page title, with `cfx_glow` as its toggle.
- `Cyber/logo_glow.png` (640x640) is the halo behind the logo on the splash and About page.
- `Splash/user.png` (1080x2400) is the circuit backdrop with a plasma halo.

OrangeFox draws a page's list before its base template, so a full-screen backdrop would cover the lists. That is why the circuit art lives in the header strip and on the splash and About screens.

## Typeface

Rajdhani (SemiBold for UI and titles, Medium for body), scaled 1.08x because its x-height is small. The OrangeFox font picker still works, so choosing another font replaces Rajdhani.

## Logo

The Glitch Fox is a faceted fox head with blue and violet offset copies and scan-line bars. It is drawn with plain polygons and rects (no filters or clip paths) so nanosvg in the recovery renders it exactly. Its viewBox is `20 30 216 200`.
