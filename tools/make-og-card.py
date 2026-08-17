#!/usr/bin/env python3
"""Draws the OG card for the mesh note in all four languages.

House style shared with deepsrt.com and foldic.app/notes: dark brand-colour
gradient, mark and bold wordmark top-left, a heavy light-on-dark sans headline,
the nodes-lost/data-lost stat row where the others put a subline, a monospace
URL in the accent colour bottom-left, and a large ghosted brand motif bleeding
off the right edge — here the spoke mesh with two nodes gone.
"""
from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1200, 630

# Dark greens: recilic's DEEP pushed down for the background.
BG_TOP = (16, 45, 33)
BG_BOT = (9, 27, 20)
GHOST = (28, 62, 47)          # motif, barely off the background
GHOST_HI = (38, 78, 60)       # live nodes/spokes, one step brighter
INK = (238, 246, 240)         # headline
MUTED = (140, 170, 155)       # labels, units
ACCENT = (95, 206, 154)       # url, live accents
WARN = (224, 122, 112)        # the red "2"

DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
HELV = "/System/Library/Fonts/HelveticaNeue.ttc"
MENLO = "/System/Library/Fonts/Menlo.ttc"
HIRAGINO = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
HIRA_GB = "/System/Library/Fonts/Hiragino Sans GB.ttc"   # W6 covers Traditional Chinese
SDGOTHIC = "/System/Library/Fonts/AppleSDGothicNeo.ttc"


SITE = "/Users/pahud/repo/recilic-site"
LOGO = Image.open(f"{SITE}/logo-512.png").convert("RGBA").resize((84, 84), Image.LANCZOS)


def F(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


LOCALES = {
    'en': dict(
        suffix='',
        # Heavy gothic, not Didot: the register the deepsrt/foldic cards set.
        headline=[("The mesh ships:", F(HELV, 58, 1)), ("lose any two, lose nothing.", F(HELV, 50, 1))],
        label=("nodes lost · data lost", F(HELV, 26)),
        units=("nodes", "bytes", F(HELV, 27)),
        url="recilic.app/notes",
    ),
    'zh': dict(
        suffix='-zh',
        headline=[("網格上線：", F(HIRA_GB, 58, 2)), ("任兩台消失，備份完好。", F(HIRA_GB, 50, 2))],
        label=("失去的節點 · 失去的資料", F(HIRA_GB, 25, 2)),
        units=("個節點", "位元組", F(HIRA_GB, 25, 2)),
        url="recilic.app/zh/notes",
    ),
    'ja': dict(
        suffix='-ja',
        headline=[("メッシュ登場：", F(HIRAGINO, 52)), ("どの2台が消えても、", F(HIRAGINO, 44)), ("失うものはゼロ。", F(HIRAGINO, 44))],
        label=("失われたノード · 失われたデータ", F(HIRAGINO, 24)),
        units=("ノード", "バイト", F(HIRAGINO, 24)),
        url="recilic.app/ja/notes",
    ),
    'ko': dict(
        suffix='-ko',
        headline=[("메시 출시:", F(SDGOTHIC, 52, 6)), ("어느 두 대가 사라져도", F(SDGOTHIC, 44, 6)), ("잃는 것은 없습니다.", F(SDGOTHIC, 44, 6))],
        label=("잃은 노드 · 잃은 데이터", F(SDGOTHIC, 25, 2)),
        units=("노드", "바이트", F(SDGOTHIC, 25, 2)),
        url="recilic.app/ko/notes",
    ),
}


def gradient(img):
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)],
               fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOT)))


def ghost_mesh(d):
    """The spoke mesh, oversized and low-contrast, bleeding off the right edge."""
    hub = (940, 330)
    radius = 235
    nodes = []
    for i in range(6):
        angle = -90 + i * 60
        nodes.append((hub[0] + radius * math.cos(math.radians(angle)),
                      hub[1] + radius * math.sin(math.radians(angle))))
    for i, (nx, ny) in enumerate(nodes):
        dead = i in (1, 4)
        if dead:
            steps = 16
            for s in range(steps):
                if s % 2:
                    continue
                t0, t1 = s / steps, (s + 1) / steps
                d.line([(hub[0] + (nx - hub[0]) * t0, hub[1] + (ny - hub[1]) * t0),
                        (hub[0] + (nx - hub[0]) * t1, hub[1] + (ny - hub[1]) * t1)],
                       fill=GHOST, width=6)
        else:
            d.line([hub, (nx, ny)], fill=GHOST_HI, width=6)
        r = 46
        colour = GHOST if dead else GHOST_HI
        d.ellipse([nx - r, ny - r, nx + r, ny + r], outline=colour, width=8)
    r = 62
    d.ellipse([hub[0] - r, hub[1] - r, hub[0] + r, hub[1] + r], fill=GHOST_HI)


for lang, spec in LOCALES.items():
    img = Image.new("RGB", (W, H))
    gradient(img)
    d = ImageDraw.Draw(img)

    ghost_mesh(d)

    img.paste(LOGO, (72, 52), LOGO)
    d.text((176, 62), "Recilic", font=F(HELV, 46, 1), fill=INK)

    # Headline: two or three lines, top-aligned so the stat row stays put.
    y = 176 if len(spec['headline']) == 3 else 190
    for text, font in spec['headline']:
        d.text((78, y), text, font=font, fill=INK)
        y += font.size + 12

    d.text((78, 366), spec['label'][0], font=spec['label'][1], fill=MUTED)
    big = F(HELV, 118, 1)
    unit_font = spec['units'][2]
    d.text((78, 398), "2", font=big, fill=WARN)
    d.text((158, 466), spec['units'][0], font=unit_font, fill=MUTED)
    d.line([(268, 468), (336, 468)], fill=MUTED, width=4)
    d.polygon([(336, 460), (352, 468), (336, 476)], fill=MUTED)
    d.text((374, 398), "0", font=big, fill=ACCENT)
    d.text((452, 466), spec['units'][1], font=unit_font, fill=MUTED)
    d.text((78, 560), spec['url'], font=F(MENLO, 26, 1), fill=ACCENT)

    out = f"/Users/pahud/repo/recilic-site/og-card-mesh-went-quiet{spec['suffix']}.png"
    img.save(out, optimize=True)
    print(f"{lang}: {out.split('/')[-1]}")
