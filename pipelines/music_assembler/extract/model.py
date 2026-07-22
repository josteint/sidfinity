"""Music Assembler — the extracted musical model.

Ties the four decoders (`locate`, `decode`, `presets`, `arps`) into one typed
model per member. This is the extract-side representation; USF serialisation
and the composer read from it.

The model carries MUSIC, not addresses: every table has been resolved to
values, and nothing here records where in the original image anything lived
(the Core Tenet — the original's memory map is a historical artifact).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                'tools'))

from pipelines.music_assembler.locate import locate, song_speed   # noqa: E402
from pipelines.music_assembler.extract import arps as _arps       # noqa: E402
from pipelines.music_assembler.extract import decode as _decode   # noqa: E402
from pipelines.music_assembler.extract import presets as _presets  # noqa: E402

FREQ_NOTES = 96


@dataclass
class MasmModel:
    speed: int = 2                      # master speed divider (F1-F8)
    tracks: list = field(default_factory=list)      # 3 x decode.Track
    sequences: dict = field(default_factory=dict)   # seq# -> [decode.Event]
    presets: list = field(default_factory=list)     # [presets.Preset]
    arps: dict = field(default_factory=dict)        # idx -> arps.Arp
    freq_lo: list = field(default_factory=list)     # 96 entries
    freq_hi: list = field(default_factory=list)
    # PSID header content
    title: str = ''
    author: str = ''
    released: str = ''
    songs: int = 1
    start_song: int = 1
    flags: int = 0
    # INIT PRIMING (trichotomy 4.5 voice_state + 4.2 SID priming). The
    # player's init clears ONLY the 16-byte work block (base+$81..$90:
    # readpos/ctrlw/orderpos/durctr/seqnum/speedctr) and then loads each
    # track's first orderlist entry. EVERY other per-voice byte keeps its
    # FILE-IMAGE leftover, and those leftovers are audible from frame 1:
    # `noteflg` carries bit6 ("note already initialised"), so a voice whose
    # first event is a REST — which never writes noteflg — SKIPS its note-init
    # entirely. Sid_Slam ships $41/$6F/$41 there, which is exactly why V1/V2
    # emit no SR/AD while V3 (whose fetch overwrote it) does.
    prime: dict = field(default_factory=dict)


def _freq_tables(mem, lay) -> 'tuple[list, list] | None':
    """The note freq tables, from the note handler's own operands:
    `LDA freqLo,Y / STA .. / STA ..` then `LDA freqHi,Y`."""
    import re
    # LDA freqlo,Y / STA a,X / STA b,X / LDA freqhi,Y
    pat = re.compile(rb'\xB9(..)\x9D..\x9D..\xB9(..)', re.DOTALL)
    m = pat.search(bytes(mem[lay.base:lay.base + 0x400]))
    if not m:
        return None
    lo = m.group(1)[0] | (m.group(1)[1] << 8)
    hi = m.group(2)[0] | (m.group(2)[1] << 8)
    return ([mem[lo + i] for i in range(FREQ_NOTES)],
            [mem[hi + i] for i in range(FREQ_NOTES)])


def extract(sid_path: str, hvsc_root: str = 'hvsc84') -> MasmModel:
    """Extract `sid_path` into a MasmModel. Raises on anything unhandled —
    the caller decides whether a member is in scope."""
    from seed_disassembly import parse_psid
    s = parse_psid(os.path.join(hvsc_root, sid_path))
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    return extract_mem(mem, hdr=s)


def extract_mem(mem, hdr: dict | None = None, lo: int = 0,
                hi: int = 0x10000) -> MasmModel:
    """Extract a Music Assembler player already materialised in `mem`.

    Used directly when the player does not live at its run address in the file
    image — a DMC C31 RELOCATING wrapper copies MA players into RAM per
    subtune, so the caller runs the wrapper first and hands the resulting
    memory here (`lo`/`hi` bound the search to that player's block)."""
    s = hdr or {}
    lay = locate(mem, lo, hi)
    if lay is None:
        raise ValueError('no Music Assembler player located')
    w = _decode.walk(mem, lay)

    used = sorted({e.value for _, ev in w['sequences'].values()
                   for e in ev if e.kind == 'preset'})
    pt = _presets.preset_table(mem, lo, hi)
    if pt is None:
        raise ValueError('preset table not located')
    pres = _presets.presets(mem, pt[0], (max(used) + 1) if used else 0)

    at = _arps.arp_tables(mem, lo, hi)
    arp_map = {}
    for idx in sorted({p.arp_index for p in pres if p.arp_index}):
        if at is None:
            raise ValueError('arpeggio referenced but tables not located')
        arp_map[idx] = _arps.arp(mem, at[0], at[1], idx)

    ft = _freq_tables(mem, lay)
    if ft is None:
        raise ValueError('freq tables not located')

    # base-relative leftovers. Safe for this build: the census measures the
    # signature at +$91 for ALL 5,618 located members, i.e. one uniform layout.
    off3 = {'gmask': 0x031, 'curnote': 0x0C9, 'nfrqlo': 0x0CC,
            'nfrqhi': 0x0CF, 'vibfr': 0x0DD, 'pwfr': 0x0E0, 'pwdir': 0x0E3,
            'noteflg': 0x141, 'arppos': 0x144, 'sl1': 0x147, 'sl2': 0x14A,
            'vibdly': 0x14D, 'sfrqhi': 0x2B6, 'rattle': 0x2B9,
            'vibph': 0x2BD, 'presetx': 0x3D9, 'pwlo': 0x3DC,
            'pwhi': 0x3DF, 'sfrqlo': 0x3E2}
    off1 = {'fcutr': 0x266, 'fdurr': 0x26B, 'fdur': 0x296, 'fcut': 0x29E,
            'fvel': 0x2A0}
    prime = {k: [mem[lay.base + o + i] for i in range(3)]
             for k, o in off3.items()}
    prime.update({k: mem[lay.base + o] for k, o in off1.items()})

    sp = song_speed(mem, lay)
    return MasmModel(
        speed=sp if sp is not None else 2,
        tracks=w['tracks'],
        sequences={k: ev for k, (_, ev) in w['sequences'].items()},
        presets=pres, arps=arp_map,
        freq_lo=ft[0], freq_hi=ft[1], prime=prime,
        title=s.get('title', ''), author=s.get('author', ''),
        released=s.get('released', ''),
        songs=s.get('songs', 1), start_song=s.get('start', 1))
