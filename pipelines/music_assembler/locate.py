"""Music Assembler — locate the player base and every data table in a member.

Music Assembler ("masm", Marco Swagerman / Oscar Giesen, Dutch USA-Team 1989)
is HVSC's 3rd-largest engine family (6,351 SIDs). The editor emits a
SELF-RELOCATING save: it patches every absolute operand for the chosen load
address, so nothing but the entry OFFSETS is stable across members. Everything
here is therefore anchored the reloc-invariant way documented in
`docs/spec_player_RE_grounded.md`: find the sequence-pointer-fetch routine (the
`cadaver/sidid` recognition signature), then read the LIVE table addresses out
of its own operands.

Entry points, relative to the player base (confirmed on the grounded member
`OPM/Sid_Slam` AND on the two relocated players packed inside the DMC
compilation `Bayliss_Richard/Freespace_2075`):

    base+$00  IRQ install / cold start      base+$21  play (per frame)
    base+$18  raster IRQ handler            base+$48  init (subtune select)

The work block sits at base+$81..base+$90 (per-track read position, gate/flags,
duration counter, sequence number; master speed counter at +$90).

NOTE the tables are found via OPERANDS, never via fixed offsets. The base is
anchored on init's fixed prefix at base+$48, NOT on the signature and NOT on
the work block — those offsets are build-dependent, and using either as the
primary anchor costs ~50 members and admits false positives. With the init
anchor the signature offset measures `+$91` for ALL 5,618 members that locate
(pipelines/music_assembler/census.py), i.e. ONE dominant build — which supersedes the
`+$91/+$B5/+$70/+$191` spread reported in docs/README.md. See the CORRECTION
block at the head of docs/spec_player_RE_grounded.md.
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

# The sidid `Music_Assembler/MC` signature = the per-track sequence-pointer
# fetch. Groups capture the operands we need:
#   LDY seqnum,X / CPY #$FE / BNE +9 / LDA flags,X / AND #$FE / STA flags,X /
#   RTS / LDA seqptrA,Y / STA zp
_SIG = re.compile(
    rb'\xBC(..)\xC0\xFE\xD0\x09\xBD(..)\x29\xFE\x9D(..)\x60\xB9(..)\x85(.)',
    re.DOTALL)

# The second pointer-table load immediately follows: LDA seqptrB,Y / STA zp
_SIG2 = re.compile(rb'\xB9(..)\x85(.)', re.DOTALL)

# init()'s fixed opening, documented as present in EVERY member (grounded spec
# "Init writes (fixed, every subtune): $D418 = $1F, $D417 = $F0"):
#   LDA #$1F / STA $D418 / LDA #$F0 / STA $D417
# This is the primary base anchor. It beats deriving the base from the
# signature or the work block, because BOTH of those sit at version-dependent
# offsets: the signature is at base+$91 on the dominant build but at base+$BC
# and others elsewhere, and the work block moves with it. init() is at base+$48
# on every build measured.
_INIT_PREFIX = re.compile(rb'\xA9\x1F\x8D\x18\xD4\xA9\xF0\x8D\x17\xD4')
_INIT_OFF = 0x48


def _rd16(b: bytes, i: int) -> int:
    return b[i] | (b[i + 1] << 8)


class MasmLayout:
    """Located addresses for one Music Assembler player instance."""

    __slots__ = ('base', 'play', 'init', 'seqnum', 'flags', 'readpos',
                 'durctr', 'speedctr', 'seqptr_lo', 'seqptr_hi', 'sig_off')

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def __repr__(self):
        return ('MasmLayout(base=$%04X sig=+$%X seqptr_lo=$%04X seqptr_hi=$%04X '
                'seqnum=$%04X speed=$%04X)'
                % (self.base, self.sig_off, self.seqptr_lo, self.seqptr_hi,
                   self.seqnum, self.speedctr))


def _play_shape(mem, base: int) -> bool:
    """play() at base+$21 is `LDX #$00 / DEC speedctr / BMI ...` on every
    member seen (V1.0 and the relocated Freespace copies). The DEC operand IS
    the master speed counter, so this doubles as the base validator."""
    p = base + 0x21
    return (p + 6 < 0x10000 and mem[p] == 0xA2 and mem[p + 1] == 0x00
            and mem[p + 2] == 0xCE and mem[p + 5] == 0x30)


def _bases(mem, window: bytes, lo: int, sig_at: int) -> list:
    """Candidate player bases for a signature match at `sig_at`, best first.

    The init prefix is the reliable anchor (base+$48 on every build measured);
    the work-block rule (`seqnum - $8D`) only holds for the dominant +$91
    build, so it is a fallback rather than the primary. Both are validated by
    the caller against the play-body shape.
    """
    out = []
    # nearest init prefix at or before the signature (init precedes the
    # sequence-fetch routine in every build seen)
    best = None
    for m in _INIT_PREFIX.finditer(window):
        a = lo + m.start()
        if a <= sig_at and (best is None or a > best):
            best = a
    if best is not None:
        out.append(best - _INIT_OFF)
    return out


def locate(mem: bytes, lo: int = 0, hi: int = 0x10000) -> 'MasmLayout | None':
    """Locate the Music Assembler player in `mem` within [lo, hi).

    Returns a `MasmLayout`, or None when no validated player is present.
    `mem` is a full 64K map (a relocated/packed player must already have been
    materialised into it — see the DMC C31 relocating-wrapper path).
    """
    window = bytes(mem[lo:hi])
    for m in _SIG.finditer(window):
        seqnum = _rd16(m.group(1), 0)          # base+$8D  (per-track seq #)
        flags = _rd16(m.group(2), 0)           # base+$84  (gate/flags)
        if _rd16(m.group(3), 0) != flags:      # STA must target the same byte
            continue
        ptr_a = _rd16(m.group(4), 0)
        zp_a = m.group(5)[0]
        # the sibling `LDA ptrB,Y / STA zp+1` follows immediately
        tail = window[m.end():m.end() + 5]
        m2 = _SIG2.match(tail)
        if not m2:
            continue
        ptr_b = _rd16(m2.group(1), 0)
        zp_b = m2.group(2)[0]
        # ($FA),Y is little-endian: whichever load targets the LOWER zp byte
        # supplies the pointer LO byte. (The grounded spec's table names are
        # swapped relative to its own disassembly — trust the zp target.)
        if zp_a == zp_b:
            continue
        seqptr_lo, seqptr_hi = ((ptr_a, ptr_b) if zp_a < zp_b
                                else (ptr_b, ptr_a))
        sig_at = lo + m.start()
        cands = _bases(mem, window, lo, sig_at) + [seqnum - 0x8D]
        for base in cands:
            if not (0 < base and _play_shape(mem, base)):
                continue
            # the signature is a routine INSIDE the player (~1 KB of code), so
            # a base that puts it thousands of bytes away is a coincidental
            # `_play_shape` hit, not a player. Guards the work-block fallback.
            if not (0 < sig_at - base < 0x400):
                continue
            return MasmLayout(
                base=base, play=base + 0x21, init=base + 0x48,
                seqnum=seqnum, flags=flags,
                readpos=base + 0x81, durctr=base + 0x8A,
                speedctr=_rd16(mem, base + 0x24),  # the DEC operand in play()
                seqptr_lo=seqptr_lo, seqptr_hi=seqptr_hi,
                sig_off=sig_at - base)
    return None


def song_speed(mem, lay: 'MasmLayout') -> 'int | None':
    """The master-speed reload constant (`LDA #$xx / STA speedctr` on the
    advance path in play()) — the manual's F1-F8 song speed. One byte -> USF
    tempo. None when the expected shape isn't there."""
    for a in range(lay.base + 0x26, lay.base + 0x60):
        if (mem[a] == 0xA9 and mem[a + 2] == 0x8D
                and _rd16(mem, a + 3) == lay.speedctr):
            return mem[a + 1]
    return None
