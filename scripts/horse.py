"""Muybridge's "The Horse in Motion" (1878, public domain) redrawn as ASCII and set galloping in
an SVG: 15 frames flipped with CSS steps, the ground scrolling underneath. Built locally:

    python scripts/horse.py path/to/horse.gif path/to/SpaceMono.woff2 path/to/InterTight.woff2
"""
import base64, os, subprocess, sys, tempfile
from PIL import Image, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIF, MONO, SANS = sys.argv[1:4]
COLS, ROWS = 100, 29
RAMP = ' .:-=+*#%@'
W, H = 1200, 380
FS, LH = 11.4, 11.6        # mono font size and line height, px
CW = FS * 0.6              # Space Mono advance


def subset(src, text):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'f.woff2')
        subprocess.run([sys.executable, '-m', 'fontTools.subset', src, '--text=' + text, '--flavor=woff2', '--output-file=' + out], check=True)
        return base64.b64encode(open(out, 'rb').read()).decode()


def frames():
    im = Image.open(GIF)
    out = []
    for i in range(im.n_frames):
        im.seek(i)
        g = im.convert('L').crop((0, 0, 300, 186))              # drop the frame number at the bottom
        g = ImageOps.autocontrast(g.filter(ImageFilter.GaussianBlur(.8)), cutoff=2)
        g = g.resize((COLS, ROWS), Image.LANCZOS)
        px = g.load()
        lines = []
        for y in range(ROWS):
            row = ''
            for x in range(COLS):
                v = px[x, y]
                dark = max(0, (178 - v) / 120)                   # paper is light, horse is dark
                row += ' ' if dark < .1 else RAMP[min(len(RAMP) - 1, 1 + int(dark * (len(RAMP) - 1)))]
            lines.append(row.rstrip())
        out.append(lines)
    return out


def svg(dark, fr):
    bg, ink, soft, accent = ('#0d1117', '#f2f3f5', '#9aa3ad', '#ec82ab') if dark else ('#f6f5f2', '#141519', '#5c616b', '#d9608f')
    n = len(fr); dur = n / 15                                     # Muybridge's 15 frames, about real gallop speed
    mono = subset(MONO, RAMP + "_.,-'` muybridge 1878 redrawn in ascii, 15 frames ·")
    sans = subset(SANS, 'made to move.')
    ox, oy = 46, 30
    groups = []
    for i, lines in enumerate(fr):
        tspans = ''.join(f'<tspan x="{ox}" y="{oy + j * LH:.1f}">{l.replace("&", "&amp;").replace("<", "&lt;")}</tspan>' for j, l in enumerate(lines) if l)
        groups.append(f'<text class="f" style="animation-delay:{-i * dur / n:.4f}s">{tspans}</text>')
    ground = "_  .  _,  - .  _  `  .  _   - ,  .   _  .  '  _  .  -  _ ,  .  _  " * 3
    gy = oy + ROWS * LH + 4
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="An ASCII horse galloping: Muybridge's The Horse in Motion, 1878. Made to move.">
<style>
@font-face{{font-family:SM;src:url(data:font/woff2;base64,{mono}) format('woff2')}}
@font-face{{font-family:IT;src:url(data:font/woff2;base64,{sans}) format('woff2');font-weight:100 900}}
text.f,.g{{font:400 {FS}px SM,ui-monospace,Menlo,Consolas,monospace;white-space:pre;fill:{ink}}}
.g{{fill:{soft}}}
text.f{{opacity:0;animation:show {dur:.3f}s step-end infinite}}
@keyframes show{{0%{{opacity:1}}{100 / n:.3f}%{{opacity:0}}100%{{opacity:0}}}}
@keyframes run{{from{{transform:translateX(0)}}to{{transform:translateX(-{len(ground) // 3 * CW:.1f}px)}}}}
.run{{animation:run {dur * 2.2:.2f}s linear infinite}}
.big{{font:800 76px IT,'Helvetica Neue',Arial,sans-serif;letter-spacing:-3.5px;fill:{ink}}}
.cap{{font:400 13px SM,ui-monospace,monospace;fill:{soft}}}
.dot{{fill:{accent}}}
@media (prefers-reduced-motion:reduce){{text.f{{animation:none}}text.f:first-of-type{{opacity:1}}.run{{animation:none}}}}
</style>
<rect width="{W}" height="{H}" rx="18" fill="{bg}"/>
<clipPath id="c"><rect x="20" y="0" width="{COLS * CW + 70:.0f}" height="{H}"/></clipPath>
<g clip-path="url(#c)">{''.join(groups)}<text class="g run" x="0" y="{gy:.1f}">{ground}</text></g>
<text class="big" x="800" y="196">made to</text>
<text class="big" x="800" y="272">move<tspan class="dot">.</tspan></text>
<text class="cap" x="802" y="314">muybridge, 1878 · redrawn in ascii, 15 frames</text>
</svg>'''


fr = frames()
for dark in (False, True):
    p = os.path.join(ROOT, 'assets', f'horse-{"dark" if dark else "light"}.svg')
    open(p, 'w', encoding='utf8', newline='\n').write(svg(dark, fr))
    print(p, os.path.getsize(p) // 1024, 'KB')
print('\n'.join(fr[3]))
