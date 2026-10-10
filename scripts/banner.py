"""Draws assets/banner-light.svg and assets/banner-dark.svg.

The cherry tree has exactly one blossom for every star on csakura: the script asks GitHub
for the count, grows that many pink cells from the trunk outwards, and the workflow in
.github/workflows/bloom.yml reruns it every day. Pure SVG and CSS, no JavaScript.

    python scripts/banner.py            # live star count
    python scripts/banner.py 300        # preview a bigger tree
"""
import json, math, os, random, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = open(os.path.join(ROOT, 'scripts', 'font.b64')).read().strip()
W, H, CELL = 1200, 340, 11
TREE_X, TREE_Y = 985, 300                      # trunk base, in px
PINKS = ['#f9c9da', '#f4a6c3', '#ec82ab', '#d9608f', '#b84677']


def stars():
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    req = urllib.request.Request('https://api.github.com/repos/realstrawhat/csakura',
                                 headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'realstrawhat-banner'})
    if os.environ.get('GITHUB_TOKEN'):
        req.add_header('Authorization', 'Bearer ' + os.environ['GITHUB_TOKEN'])
    return json.load(urllib.request.urlopen(req, timeout=20))['stargazers_count']


def grow(n):
    """n blossom cells, filled from the middle of each cluster outwards, so a few more stars
    make the crown a little fuller and many more make it bigger."""
    rnd = random.Random(26)
    trunk = []
    for y in range(0, 10):
        x = round(math.sin(y / 4) * 1.2)
        trunk += [(x, -y), (x + 1, -y)]
    for bx, by, dx in [(0, -6, -1), (1, -8, 1), (0, -10, -1), (1, -11, 1)]:
        trunk += [(bx + dx * i, by - i // 2) for i in range(1, 6)]
    blobs = [(-6, -13, 6.0), (6, -13, 6.2), (0, -17, 6.8), (-9, -9, 4.4), (9, -10, 4.6), (-3, -11, 5), (4, -18, 4.5)]
    jitter = {}
    scale = 0.55
    while True:
        cells = {}
        for cx, cy, r in blobs:
            r *= scale
            for x in range(int(cx - 12), int(cx + 13)):
                for y in range(int(cy - 12), int(cy + 13)):
                    j = jitter.setdefault((x, y), rnd.uniform(-1.2, .6))
                    d = math.hypot(x - cx, (y - cy) * 1.15) / max(r, .1)
                    if d * r < r + j * scale:
                        order = d + j * .08
                        if order < cells.get((x, y), (9,))[0]:
                            light = (-(x - cx) - (y - cy)) / (r * 2) + jitter[(x, y)] * .2
                            cells[(x, y)] = (order, light)
        if len(cells) >= n or scale > 3:
            break
        scale += .05
    picked = sorted(cells.items(), key=lambda kv: kv[1][0])[:n]
    return trunk, {k: v[1] for k, v in picked}


def petals(rnd):
    out, css = [], []
    for i in range(16):
        x0 = rnd.uniform(560, 1220); y0 = rnd.uniform(-60, 120)
        dur = rnd.uniform(7, 12); delay = -rnd.uniform(0, dur)
        dx = -rnd.uniform(320, 620); dy = rnd.uniform(320, 400); rot = rnd.choice([-1, 1]) * rnd.uniform(200, 540)
        s = rnd.uniform(.7, 1.25); col = rnd.choice(PINKS[:4])
        css.append(f'@keyframes p{i}{{from{{transform:translate({x0:.0f}px,{y0:.0f}px) rotate(0) scale({s:.2f})}}'
                   f'to{{transform:translate({x0 + dx:.0f}px,{y0 + dy:.0f}px) rotate({rot:.0f}deg) scale({s:.2f})}}}}'
                   f'.p{i}{{animation:p{i} {dur:.1f}s linear {delay:.1f}s infinite}}')
        out.append(f'<path class="p{i}" fill="{col}" opacity=".9" d="M0-9C5-9 9-4 8 2 7 7 3 10 0 7-3 10-7 7-8 2-9-4-5-9 0-9Z"/>')
    return ''.join(out), ''.join(css)


def svg(dark, n):
    bg, ink, soft, accent = ('#0d1117', '#f2f3f5', '#9aa3ad', '#7b95ff') if dark else ('#f6f5f2', '#141519', '#5c616b', '#2b4fd8')
    trunk, bloom = grow(n)
    wood = '#8a6150' if dark else '#6b4a3a'
    cells = [f'<rect x="{x * CELL}" y="{y * CELL}" width="{CELL}" height="{CELL}" fill="{wood}"/>' for x, y in trunk if (x, y) not in bloom]
    for (x, y), l in bloom.items():
        k = 0 if l > .55 else 1 if l > .2 else 2 if l > -.15 else 3 if l > -.45 else 4
        cells.append(f'<rect x="{x * CELL}" y="{y * CELL}" width="{CELL}" height="{CELL}" fill="{PINKS[k]}"/>')
    p, pcss = petals(random.Random(7))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Kodi Alex, UX designer and developer in Berlin. The cherry tree has {n} blossoms, one for every star on csakura.">
<style>
@font-face{{font-family:IT;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:100 900}}
.n{{font:800 112px IT,'Helvetica Neue',Arial,sans-serif;letter-spacing:-5px;fill:{ink}}}
.r{{font:500 26px IT,'Helvetica Neue',Arial,sans-serif;letter-spacing:-.3px;fill:{ink}}}
.t{{font:400 21px IT,'Helvetica Neue',Arial,sans-serif;fill:{soft}}}
.u{{font:600 19px IT,'Helvetica Neue',Arial,sans-serif;fill:{accent}}}
.c{{font:500 13px IT,'Helvetica Neue',Arial,sans-serif;fill:{soft};text-anchor:middle}}
.c b{{font-weight:700}}
{pcss}
@keyframes sway{{0%,100%{{transform:translate({TREE_X}px,{TREE_Y}px) rotate(-.6deg)}}50%{{transform:translate({TREE_X}px,{TREE_Y}px) rotate(.6deg)}}}}
.tree{{animation:sway 6s ease-in-out infinite;transform-origin:0 0}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<rect width="{W}" height="{H}" rx="18" fill="{bg}"/>
<g class="tree">{''.join(cells)}</g>
{p}
<text class="n" x="56" y="150">Kodi Alex</text>
<rect x="60" y="176" width="64" height="5" rx="2.5" fill="{accent}"/>
<text class="r" x="58" y="226">UX designer &amp; developer · Berlin</text>
<text class="t" x="58" y="262">I design it, then I build it.</text>
<text class="u" x="58" y="296">kodialex.com</text>
<text class="c" x="{TREE_X + CELL}" y="326">{n} blossoms, one for every star on csakura</text>
</svg>'''


if __name__ == '__main__':
    n = stars()
    for dark in (False, True):
        path = os.path.join(ROOT, 'assets', f'banner-{"dark" if dark else "light"}.svg')
        open(path, 'w', encoding='utf8', newline='\n').write(svg(dark, n))
    print('blossoms:', n)
