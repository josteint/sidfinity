#!/usr/bin/env python3
"""Read-only CBM disk-image reader (D64 / D71 / D81) — directory + file extract.

    python3 tools/cbm_diskimg.py hvsc85/*.d64            # list directories
    python3 tools/cbm_diskimg.py --extract DIR IMAGE...  # write every PRG out

Step one of BACKLOG ITEM 26 — "rip the HVSC disk mags with our own pipeline",
a capability demo parked hard until engine coverage is broad (near the end of
the project). HVSC ships ten disk images at the root of the collection — the
10-Years / 20-Years anniversary disk mags and the HVSC_Intro disks — which
`tools/build_sid_db.py` never sees, because it walks for `.sid` files. They
contain music: 37 `musicN` PRGs on `10_Years_HVSC_2.d64`, and 17 tunes on
`20_Years_HVSC.d64` whose directory art advertises "17 exclusives!".

⚠ It is NOT a corpus-growth item, and must not be re-opened as one — that was
the original framing and it was refuted (points 2 and 3 below). The value is
the demonstration: every member we have ever built arrived pre-ripped, and a
disk mag gives none of that.

 1. It is ALL PACKED. sidid identifies 0 of the 37 and 0 of the 17 as any
    player, the 20-Years main binary comes back `Crunched:Exomizer`, and the
    load addresses are nonsense ($CD23, $3226, ...). Extraction would need a
    depacker (Exomizer decruncher, or emulate-the-disk-and-rip) — a capability
    the project does not have. This reader stops exactly there.
 2. The "17 exclusives" are ALREADY IN HVSC. `DOCUMENTS/Update_Announcements/
    20160712.txt` (Update #65, the same date the disk's directory art carries)
    says HVSC produced an exclusive music disk for its 20th birthday, and the
    catalogue holds EXACTLY 17 SIDs credited `2016 ... HVSC`. Same convention
    on the 2006 disk. Not proven per-tune — only a depacker would settle that —
    but an exact count match against an explicit claim of 17 is hard to explain
    otherwise. (`Update65.hvs` is no help either way: it records only
    REPLACE/MOVE/DELETE, so new files never appear in it. STIL has no entries.)
 3. The engine diversity cuts BOTH ways. The 46 anniversary-disk tunes span 17
    distinct engines (GoatTracker_V2.x 15, DMC 5, Geir_Tjelta/SIDDuzz'It 4,
    Laxity_NewPlayer_V21 3, ...), most unmigrated. As a corpus argument that
    is dead — they are already ordinary `.sid`, so depacking reaches no engine
    the catalogue does not already expose. As the DEMO's gating condition it is
    the whole point: attempt this before those engines are migrated and it
    mostly reports "cannot build this player", which demonstrates nothing.

⭐ And because the tunes are already ripped, the demo gets GROUND TRUTH for
free: our output per tune can be diffed against HVSC's own hand-made rip,
which is far stronger than "it plays". That is what makes it a capstone rather
than a stunt.

The one loose end, if a smaller bite is wanted first: the 10-Years disk has 37
`musicN` files against only 29 tunes credited `2006 ... HVSC`. That disk never
advertised a count, so it probably mixed exclusive with pre-existing material,
but those 8 are the only place unexplained content could sit.

VALIDATE ANY CHANGE against the BAM disk name — `10_Years_HVSC_2.d64` reads
`hvsc` and `20_Years_HVSC.d64` reads `>hvsc 20 years!<`. Wrong track/sector
arithmetic garbles those immediately, which is what makes them a cheap
self-check on the offset maths.

NOT handled: `10_Years_HVSC.dfi` is not a disk image at all — its header reads
`DREAMLOAD FILE ARCHIVE`, a Dreamload loader archive needing its own parser.
"""
from __future__ import annotations

import argparse
import os
import sys

FTYPE = {0: 'DEL', 1: 'SEQ', 2: 'PRG', 3: 'USR', 4: 'REL'}


def petscii(b: bytes) -> str:
    """PETSCII -> ASCII for display; $A0 pads terminate a filename."""
    out = []
    for c in b:
        if c == 0xA0:
            break
        if 0x41 <= c <= 0x5A:
            out.append(chr(c).lower())
        elif 0xC1 <= c <= 0xDA:
            out.append(chr(c - 0x80))
        elif 32 <= c < 127:
            out.append(chr(c))
        else:
            out.append(f'<{c:02X}>')
    return ''.join(out).rstrip()


def _sectors(track: int) -> int:
    """Sectors on a 1541 track (the zone layout D64/D71 are built from)."""
    return 21 if track <= 17 else 19 if track <= 24 else 18 if track <= 30 else 17


def _off_d64(track: int, sector: int, side_tracks: int = 35) -> int:
    off = 0
    for t in range(1, track):
        off += _sectors(t if t <= side_tracks else t - side_tracks) * 256
    return off + sector * 256


def _off_d81(track: int, sector: int) -> int:
    return ((track - 1) * 40 + sector) * 256


def _offset(kind: str):
    return _off_d81 if kind == 'd81' else _off_d64


def kind_of(path: str) -> str:
    e = os.path.splitext(path)[1].lower()
    return 'd81' if e == '.d81' else 'd71' if e == '.d71' else 'd64'


def disk_name(data: bytes, kind: str) -> str:
    """The disk name — the cheap self-check that the offsets are right.

    ⚠ It does NOT live at the same place in both formats, and reading the D64
    offset on a D81 returns sixteen $00 bytes rather than an error (caught that
    way the first time this ran). The 1541/1571 keep it in the BAM sector at
    18/0 offset $90; the 1581's header sector at 40/0 holds the directory link
    and format byte first and the name at offset $04.
    """
    if kind == 'd81':
        hdr = _off_d81(40, 0)
        return petscii(data[hdr + 0x04:hdr + 0x14])
    bam = _off_d64(18, 0)
    return petscii(data[bam + 0x90:bam + 0xA0])


def read_dir(data: bytes, kind: str):
    """Yield (name, filetype, size_blocks, first_track, first_sector)."""
    off = _offset(kind)
    t, s = (40, 3) if kind == 'd81' else (18, 1)
    seen = set()
    while t and (t, s) not in seen:
        seen.add((t, s))
        base = off(t, s)
        if base + 256 > len(data):
            return
        blk = data[base:base + 256]
        for e in range(8):
            ent = blk[e * 32:(e + 1) * 32]
            if ent[2]:
                yield (petscii(ent[5:21]), FTYPE.get(ent[2] & 7, '?'),
                       ent[30] | (ent[31] << 8), ent[3], ent[4])
        t, s = blk[0], blk[1]


def read_file(data: bytes, kind: str, track: int, sector: int) -> bytes:
    """Follow the sector chain; returns the file incl. its 2-byte load address.

    The last sector's link is (0, bytes-used+1) rather than a next address —
    reading it as a full sector appends up to 254 bytes of slack.
    """
    off = _offset(kind)
    out = bytearray()
    seen = set()
    t, s = track, sector
    while t and (t, s) not in seen:
        seen.add((t, s))
        blk = data[off(t, s):off(t, s) + 256]
        if len(blk) < 256:
            break
        nt, ns = blk[0], blk[1]
        out += blk[2:256] if nt else blk[2:2 + max(0, ns - 1)]
        t, s = nt, ns
    return bytes(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('images', nargs='+')
    ap.add_argument('--extract', metavar='DIR',
                    help='also write every PRG into DIR as <image>__<name>.prg')
    a = ap.parse_args()
    for path in a.images:
        data = open(path, 'rb').read()
        kind = kind_of(path)
        print(f'\n=== {path}  ({len(data):,} bytes, {kind}, '
              f'disk name {disk_name(data, kind)!r}) ===')
        for name, ft, blocks, t, s in read_dir(data, kind):
            print(f'   {blocks:4d}  {ft}  {name}')
            if a.extract and ft == 'PRG':
                os.makedirs(a.extract, exist_ok=True)
                safe = ''.join(c if c.isalnum() else '_' for c in name)[:24]
                blob = read_file(data, kind, t, s)
                stem = os.path.splitext(os.path.basename(path))[0]
                with open(os.path.join(a.extract, f'{stem}__{safe}.prg'), 'wb') as f:
                    f.write(blob)
    return 0


if __name__ == '__main__':
    sys.exit(main())
