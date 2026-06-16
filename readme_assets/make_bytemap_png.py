#!/usr/bin/env python3
"""Render Gorilla.sid as a hex-editor-style colored byte map PNG.

Reuses the region definitions from make_bytemap.py. Hex-dump layout:
column-offset header across the top, file-offset gutter down the left,
colored cells separated by white gaps (no grid lines).
"""
from PIL import Image, ImageDraw, ImageFont
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mb", os.path.join(HERE, "make_bytemap.py"))
mb = importlib.util.module_from_spec(spec); spec.loader.exec_module(mb)

DATA = open(os.path.join(HERE, "Gorilla.sid"), "rb").read()
COLS = mb.COLS
ROWS = (len(DATA) + COLS - 1) // COLS

# compact geometry
PITCH = 21      # cell pitch (px)
GAP   = 3       # white gap between cells
SQ    = PITCH - GAP
PAD   = 14
rgb   = lambda h: tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
COLOR = {c: rgb(r) for _, c, r, _ in mb.REGIONS}

F   = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", s)
hexf, addrf, legf = F(12), F(11), F(13)
titlef = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
GREY = (110, 110, 110)

GUT   = 46      # left address gutter width
HDR   = 16      # top column-header height
TITLE = 30

leg_rows = (len(mb.REGIONS) + 1) // 2
W = PAD + GUT + COLS * PITCH + PAD
H = PAD + TITLE + HDR + ROWS * PITCH + 18 + leg_rows * 22 + PAD
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

def ctext(cx, cy, t, font, fill):
    bb = d.textbbox((0, 0), t, font=font)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), t, font=font, fill=fill)

d.text((PAD, PAD), "Gorilla.sid — 1922 bytes", font=titlef, fill="black")
ox, oy = PAD + GUT, PAD + TITLE + HDR

# top column-offset header
for c in range(COLS):
    ctext(ox + c * PITCH + SQ / 2, PAD + TITLE + HDR / 2, f"{c:02X}", addrf, GREY)
# left file-offset gutter + cells
for r in range(ROWS):
    cy = oy + r * PITCH + SQ / 2
    d.text((PAD, cy - 6), f"{r * COLS:04X}", font=addrf, fill=GREY)
    for c in range(COLS):
        i = r * COLS + c
        if i >= len(DATA):
            break
        x, y = ox + c * PITCH, oy + r * PITCH
        d.rectangle([x, y, x + SQ, y + SQ], fill=COLOR[mb.region_of(i)])
        ctext(x + SQ / 2, y + SQ / 2, f"{DATA[i]:02X}", hexf, (15, 15, 15))

# legend
ly = oy + ROWS * PITCH + 14
for k, (name, cname, rgbhex, end) in enumerate(mb.REGIONS):
    start = 0 if k == 0 else mb.REGIONS[k - 1][3]
    col, row = k % 2, k // 2
    x = PAD + col * (W // 2 - PAD); y = ly + row * 22
    d.rectangle([x, y, x + 16, y + 16], fill=COLOR[cname])
    d.text((x + 24, y + 1), f"{name}  [{start}..{end})", font=legf, fill="black")

out = os.path.join(HERE, "gorilla_bytemap.png")
img.save(out)
print("wrote", out, img.size)
