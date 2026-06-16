#!/usr/bin/env python3
"""
Generate a lualatex/TikZ byte-map figure of Gorilla.sid for the README.

Gorilla.sid is 1922 bytes = 31 rows x 62 columns. Every byte is drawn as a
hex cell, background-coloured by which structural region it belongs to.

The region boundaries below were extracted from the actual file with the
project's GoatTracker parser (deprecated/python_experiments/gt_parser.py +
deprecated/gt2_pipeline/gt2_parse_direct.py) and verified to tile the file
exactly (the region sizes sum to 1922).

File-offset map (the C64 image loads at $1000; file offset 126 == $1000,
because 124 header bytes + 2 load-address bytes precede it):

    file off   C64 addr   region
    0   ..124             PSID header (container)
    124 ..126             load address word ($1000, little-endian)
    126 ..1044  $1000     6502 player code
    1044..1196  $1396     frequency table
    1196..1223  $142E     pointer tables (orderlist + pattern address tables)
    1223..1258  $1449     instruments
    1258..1343  $146C     effect tables (wave / pulse / filter / speed)
    1343..1361  $14C1     orderlists (the arrangement)
    1361..1922  $14D3     patterns (the notes)

Run:  python3 readme_assets/make_bytemap.py
Out:  readme_assets/gorilla_bytemap.tex   (compile with lualatex)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SID  = os.path.join(HERE, "Gorilla.sid")
OUT  = os.path.join(HERE, "gorilla_bytemap.tex")

COLS, CELL = 31, 0.42         # 31 columns (62 rows), cell size in cm

# (name, LaTeX colour name, RGB hex, end-offset-exclusive). Listed in file order.
REGIONS = [
    ("PSID header",        "rHeader", "C5CAE9", 124),
    ("Load address",       "rLoad",   "9FA8DA", 126),
    ("Player code (6502)", "rCode",   "FFE0B2", 1044),
    ("Frequency table",    "rFreq",   "C8E6C9", 1196),
    ("Pointer tables",     "rPtr",    "E1BEE7", 1223),
    ("Instruments",        "rInst",   "B2DFDB", 1258),
    ("Effect tables (wave/pulse/filter)", "rTab", "F8BBD0", 1343),
    ("Orderlists",         "rOrder",  "FFF9C4", 1361),
    ("Patterns",           "rPatt",   "BBDEFB", 1922),
]

def region_of(off):
    for name, cname, rgb, end in REGIONS:
        if off < end:
            return cname
    raise IndexError(off)

def main():
    data = open(SID, "rb").read()
    n = len(data)
    # sanity: regions tile the file exactly
    assert REGIONS[-1][3] == n, f"regions end at {REGIONS[-1][3]}, file is {n}"
    rows = (n + COLS - 1) // COLS

    L = []
    add = L.append
    add(r"\documentclass[border=6pt]{standalone}")
    add(r"\usepackage{fontspec}")
    add(r"\usepackage{tikz}")
    for _, cname, rgb, _ in REGIONS:
        add(rf"\definecolor{{{cname}}}{{HTML}}{{{rgb}}}")
    add(r"\newcommand{\cell}[3]{% #1=col #2=row #3=hex; \rcol holds the colour")
    add(r"  \node[anchor=north west, minimum size=%gcm, inner sep=0pt," % CELL)
    add(r"       fill=\rcol, draw=black!12, line width=0.1pt,")
    add(r"       font=\ttfamily\fontsize{5}{5}\selectfont]")
    add(r"      at (#1*%g, -#2*%g) {\strut #3};}" % (CELL, CELL))
    add(r"\begin{document}\begin{tikzpicture}")

    # cells
    for i, b in enumerate(data):
        c, r = i % COLS, i // COLS
        add(rf"\def\rcol{{{region_of(i)}}}\cell{{{c}}}{{{r}}}{{{b:02X}}}")

    # legend, below the grid
    gridbottom = -rows * CELL
    add(rf"\begin{{scope}}[shift={{(0,{gridbottom-0.6:.2f})}}]")
    lx, ly, percol = 0.0, 0.0, 5
    for k, (name, cname, rgb, end) in enumerate(REGIONS):
        start = 0 if k == 0 else REGIONS[k-1][3]
        col, row = k // percol, k % percol
        x = col * 9.5
        y = -row * 0.62
        add(rf"\node[anchor=west, minimum size=0.42cm, inner sep=0pt, fill={cname}, draw=black!20] at ({x},{y}) {{}};")
        add(rf"\node[anchor=west, font=\ttfamily\scriptsize] at ({x+0.55},{y}) {{{name} \textcolor{{black!55}}{{[{start}..{end})}}}};")
    add(r"\end{scope}")

    add(r"\end{tikzpicture}\end{document}")
    open(OUT, "w").write("\n".join(L) + "\n")
    print(f"wrote {OUT}  ({n} bytes -> {rows} rows x {COLS} cols)")

if __name__ == "__main__":
    main()
