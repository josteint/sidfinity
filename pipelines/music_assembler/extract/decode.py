"""Music Assembler — orderlist + sequence-stream decode.

GROUNDED IN THE PLAYER CODE, not the prose specs. The decode below was read
off the real dispatch in `OPM/Sid_Slam.sid` ($C091-$C1C4; see the disassembly
quoted in docs/spec_player_RE_grounded.md's CORRECTION block) and it
CONTRADICTS both research docs on the command ranges — see `SEQUENCE FORMAT`.

Sequence dispatch, exactly as the player branches ($C0AE onward):

    AA = stream[readpos]
      AA >= $80 -> $C0D2:  CMP #$A0
                             BCC -> $C0EC  PRESET   ($80..$9F)
                             else          HOLD     ($A0..$FF)
      AA <  $60 ->         NOTE            ($00..$5F)
      else      ->         REST+release    ($60..$7F)

SEQUENCE FORMAT (the corrected map):

  $00..$5F  NOTE index, ALWAYS followed by a flags/duration byte BB:
              BB bits 0-4 = duration
              BB bit 5    = SLIDE  -> consume 2 more bytes (CC, DD)
              BB bit 7    = FILTER -> consume 2 more bytes (CC, DD)
              BB bit 6    = legato/hold flag (kept raw by the player at
                            base+$141,X; no extra bytes)
            When both bit7 and bit5 are set the player takes the FILTER path
            first ($C12C BMI precedes the bit-5 test), so bit 5 is not
            re-examined — filter wins.
  $60..$7F  REST with release; duration = AA & $1F. No follow byte.
  $80..$9F  PRESET select; id = AA & $1F (the player does ASL A x3 = id*8, so
            the range is 32 presets, NOT the 16 the docs claim for $Ax).
            Carries NO duration of its own: the player immediately re-reads
            the next byte and dispatches it as a note (< $60) or a
            rest/hold (>= $60).
  $A0..$FF  HOLD; duration = AA & $1F. No follow byte.
  $FF       ...is therefore also "HOLD $1F" by range, but the END-OF-PATTERN
            test at $C188 is applied to the byte reached AFTER the current
            event completes, so $FF is only a terminator in that position.

ORDERLIST (per track, 2 bytes per entry, from init $C05F and the advance path
at $C193):

    [seq#] [transpose<<4 | repeat]
      seq# $FE  -> STOP (the player clears the gate bit and returns)
      seq# $FF  -> LOOP the orderlist back to entry 0
      seq# $FD  -> LOOP to entry nn, where nn is the FOLLOWING byte
                   (VARIANT ONLY — see below)
    `repeat` is the LOW nibble: the sequence plays repeat+1 times (the player
    DECs it and restarts while it stays >= 0). `transpose` is the HIGH nibble,
    added to every note index in the sequence.

THE $FD ORDERLIST VARIANT. The base build steps the orderlist inline
(`INY / INY / LDA ($fa),Y` at base+$1A0). A variant replaces the second INY
with `JSR <stub>`, and the stub adds a targeted loop:

    INY / LDA ($fa),Y / CMP #$FD / BNE rts
    INY / LDA ($fa),Y / ASL A / STA orderpos,X / TAY / BCC re-read

so `$FD nn` sets the orderlist position to entry `nn` (`ASL A` = *2 for the
2-byte entries) and re-reads from there — the jc64dis docs' VoiceTracker
"restart from command". 260 of the family's members carry it.

It is detected POSITIVELY (ledger C13: never infer a variant from the absence
of something) by the opcode at base+$1A1 plus the stub's own `CMP #$FD` shape.
A base-build member is decoded WITHOUT the sentinel, so a stray $FD there
stays an ordinary sequence number — which is what its player would do.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

NOTE_MAX = 0x5F
REST_LO, REST_HI = 0x60, 0x7F
PRESET_LO, PRESET_HI = 0x80, 0x9F
HOLD_LO = 0xA0

END_OF_PATTERN = 0xFF
ORDER_STOP = 0xFE
ORDER_LOOP = 0xFF
ORDER_LOOP_TO = 0xFD      # `$FD nn` -> loop to entry nn (variant only)


@dataclass
class Event:
    """One decoded sequence event."""
    kind: str                 # 'note' | 'rest' | 'hold' | 'preset'
    value: int = 0            # note index / preset id
    duration: int = 0         # frames (the engine's own units)
    legato: bool = False      # flags bit 6
    slide: tuple | None = None    # (lo, hi) when flags bit 5
    filt: tuple | None = None     # (cutoff_speed, frames) when flags bit 7
    raw_flags: int = 0


@dataclass
class OrderEntry:
    seq: int
    transpose: int
    repeat: int


@dataclass
class Track:
    entries: list = field(default_factory=list)   # list[OrderEntry]
    loops: bool = False        # ended on $FF/$FD (loop) rather than $FE
    loop_to: int = 0           # target ENTRY index ($FD nn); 0 for plain $FF
    addr: int = 0


def track_tables(mem, lay) -> 'tuple[int, int] | None':
    """(lo_table, hi_table) for the 3 per-track orderlist pointers.

    Located by the pointer-load shape the player uses in BOTH init and the
    orderlist-advance path: `LDA lo,X / STA zp / LDA hi,X / STA zp+1`, where
    zp is the same pointer pair the sequence fetch uses. Operand-located, so
    it survives the editor's relocation.
    """
    zp = mem[lay.base + 0xA5]        # the STA zp operand in the seq fetch
    pat = re.compile(rb'\xBD(..)\x85' + bytes([zp])
                     + rb'\xBD(..)\x85' + bytes([zp + 1]), re.DOTALL)
    m = pat.search(bytes(mem[lay.base:lay.base + 0x400]))
    if not m:
        return None
    lo = m.group(1)[0] | (m.group(1)[1] << 8)
    hi = m.group(2)[0] | (m.group(2)[1] << 8)
    return lo, hi


def has_fd_loop(mem, lay) -> bool:
    """Does this build carry the `$FD nn` targeted-loop stub? (positive test)"""
    a = lay.base + 0x1A1
    if mem[a] != 0x20:                       # base build has INY ($C8) here
        return False
    t = mem[a + 1] | (mem[a + 2] << 8)       # JSR target
    return (mem[t] == 0xC8 and mem[t + 1] == 0xB1        # INY / LDA (zp),Y
            and mem[t + 3] == 0xC9 and mem[t + 4] == 0xFD)   # CMP #$FD


def orderlist(mem, addr: int, max_entries: int = 256,
              fd_loop: bool = False) -> Track:
    """Decode one track's orderlist at `addr`.

    `fd_loop` enables the `$FD nn` targeted-loop sentinel — pass what
    `has_fd_loop()` reports for this member's player, never a guess.
    """
    t = Track(addr=addr)
    a = addr
    for _ in range(max_entries):
        seq = mem[a]
        if seq == ORDER_STOP:
            return t
        if seq == ORDER_LOOP:
            t.loops = True
            return t
        if fd_loop and seq == ORDER_LOOP_TO:
            t.loops = True
            t.loop_to = mem[a + 1]
            return t
        b = mem[a + 1]
        t.entries.append(OrderEntry(seq=seq, transpose=b >> 4, repeat=b & 0x0F))
        a += 2
    return t


def sequence(mem, addr: int, max_bytes: int = 4096) -> list:
    """Decode the sequence byte stream at `addr` into Events.

    Stops at the end-of-pattern `$FF` in TERMINATOR position (i.e. where the
    player's $C188 check runs: after a completed event).
    """
    out, i = [], 0
    while i < max_bytes:
        aa = mem[(addr + i) & 0xFFFF]
        if aa == END_OF_PATTERN:
            return out
        i += 1
        if PRESET_LO <= aa <= PRESET_HI:
            out.append(Event('preset', value=aa & 0x1F))
            continue                      # no duration; next byte dispatches
        if aa >= HOLD_LO:
            out.append(Event('hold', duration=aa & 0x1F))
            continue
        if REST_LO <= aa <= REST_HI:
            out.append(Event('rest', duration=aa & 0x1F))
            continue
        # NOTE: always carries a flags/duration byte
        bb = mem[(addr + i) & 0xFFFF]
        i += 1
        ev = Event('note', value=aa, duration=bb & 0x1F,
                   legato=bool(bb & 0x40), raw_flags=bb)
        if bb & 0x80:                     # FILTER wins over slide (BMI first)
            ev.filt = (mem[(addr + i) & 0xFFFF],
                       mem[(addr + i + 1) & 0xFFFF])
            i += 2
        elif bb & 0x20:                   # SLIDE
            ev.slide = (mem[(addr + i) & 0xFFFF],
                        mem[(addr + i + 1) & 0xFFFF])
            i += 2
        out.append(ev)
    raise ValueError('sequence at $%04X did not terminate' % addr)


def walk(mem, lay) -> dict:
    """Decode a whole member: 3 orderlists + every referenced sequence."""
    tt = track_tables(mem, lay)
    if tt is None:
        raise ValueError('track pointer tables not located')
    tlo, thi = tt
    fd = has_fd_loop(mem, lay)
    tracks, seqs = [], {}
    for x in range(3):
        a = mem[tlo + x] | (mem[thi + x] << 8)
        tr = orderlist(mem, a, fd_loop=fd)
        tracks.append(tr)
        for e in tr.entries:
            if e.seq not in seqs:
                sa = (mem[lay.seqptr_lo + e.seq]
                      | (mem[lay.seqptr_hi + e.seq] << 8))
                seqs[e.seq] = (sa, sequence(mem, sa))
    return {'tracks': tracks, 'sequences': seqs,
            'track_ptr': (tlo, thi), 'fd_loop': fd}
