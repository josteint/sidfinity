"""Music Assembler — the preset (instrument) table.

8 bytes per preset. Every field below was established by finding its READ SITE
in the player (all `abs,Y` addressing forms, not just `LDA` — `+6` is reached
by `SBC`/`ADC` and a LDA-only scan misses it entirely) and reading what the
value does:

  +0  attack/decay        -> $D405            ($C235)
  +1  sustain/release     -> $D406            ($C23A)
  +2  waveform/control    -> $D404 next frame ($C252; the note-init frame
                             writes the PREVIOUS ctrl with the gate cleared,
                             which is the engine's hard-restart)
  +3  pulse width init    -> seeds BOTH pulse work slots ($C258)
  +4  pulse slide step    -> added to the pulse work value every frame, gated
                             on +7 bit $40 ($C324)
  +5  vibrato delay+rate  -> `LSR A x3` = the DELAY countdown ($C277); the low
                             nibble is the RATE compared against a per-voice
                             frame counter ($C310)
  +6  vibrato depth       -> added/subtracted from the note frequency each
                             half-cycle, direction from a 4-entry table
                             ($C2ED / $C300)
  +7  Fx flags + arpeggio -> low nibble = arpeggio table index (0 = none,
                             $C2A9); high bits are effect enables seen tested
                             as $10 (vibrato), $20, $40 (pulse slide), $F0
                             ($C288 -> the per-voice work byte $FD,X)

NOTE the docs place the "Fx + arpeggio value" at +6 and call +4/+6 uncertain.
Both are wrong: the Fx+arpeggio byte is +7 and +6 is the vibrato depth.

The table base is located from the player's own operand (relocation-invariant),
anchored on the distinctive per-voice SR write:

    LDA preset+0,Y / STA zp / LDA preset+1,Y / LDY voicebase,X / STA $D406,Y
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PRESET_STRIDE = 8

# LDA p0,Y / STA zp / LDA p1,Y / LDY voicebase,X / STA $D406,Y
_PRESET_SITE = re.compile(
    rb'\xB9(..)\x85(.)\xB9(..)\xBC(..)\x99\x06\xD4', re.DOTALL)


@dataclass
class Preset:
    id: int
    ad: int                 # +0
    sr: int                 # +1
    waveform: int           # +2
    pulse_init: int         # +3
    pulse_step: int         # +4
    vib_byte: int           # +5 (raw)
    vib_depth: int          # +6
    fx: int                 # +7 (raw)

    # --- derived views, exactly as the player derives them ---
    @property
    def vib_delay(self) -> int:
        return self.vib_byte >> 3

    @property
    def vib_rate(self) -> int:
        return self.vib_byte & 0x0F

    @property
    def arp_index(self) -> int:
        return self.fx & 0x0F

    @property
    def vib_on(self) -> bool:
        return bool(self.fx & 0x10)

    @property
    def pulse_slide_on(self) -> bool:
        return bool(self.fx & 0x40)


def preset_table(mem, lo: int = 0, hi: int = 0x10000):
    """(preset_table_base, voice_base_array) located from the player's own
    operands, or None when the anchor isn't present.

    `lo`/`hi` bound the search to ONE player's code block. That matters
    whenever more than one MA player is present in the same 64K — a DMC C31
    compilation packs several, and an unbounded search returns the FIRST
    player's table for every one of them (its address is not materialised for
    the others, so every preset field reads back as zero)."""
    m = _PRESET_SITE.search(bytes(mem[lo:hi]))
    if not m:
        return None
    p0 = m.group(1)[0] | (m.group(1)[1] << 8)
    p1 = m.group(3)[0] | (m.group(3)[1] << 8)
    if p1 != p0 + 1:                     # +0 and +1 must be adjacent
        return None
    vb = m.group(4)[0] | (m.group(4)[1] << 8)
    return p0, vb


def presets(mem, base: int, count: int) -> list:
    """Decode `count` presets from the table at `base`."""
    out = []
    for i in range(count):
        a = base + i * PRESET_STRIDE
        out.append(Preset(id=i, ad=mem[a], sr=mem[a + 1], waveform=mem[a + 2],
                          pulse_init=mem[a + 3], pulse_step=mem[a + 4],
                          vib_byte=mem[a + 5], vib_depth=mem[a + 6],
                          fx=mem[a + 7]))
    return out
