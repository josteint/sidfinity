"""Music Assembler — the arpeggio table.

Selected by the low nibble of preset+7 (0 = no arpeggio). The runner is a
`JSR` from the per-voice effect path; everything below is read off it
($C3E5-$C436 in the grounded member):

    TAY                       ; Y = arpeggio index (preset+7 & $0F)
    LDA arpLo,Y / STA fa      ; 16-entry lo/hi pointer tables
    LDA arpHi,Y / STA fb
    LDY steppos,X             ; BYTE offset into the step stream
    LDA (fa),Y / AND gatemask,X / STA ctrl,X    ; [0] WAVEFORM
    INY / LDA (fa),Y
      BMI +                   ;   [1] NOTE OFFSET: bit7 set = ABSOLUTE
      CLC / ADC curnote,X     ;       else RELATIVE to the playing note
    + AND #$7F / STA <smc>    ;       masked to 7 bits -> freq table index
    INY / LDA (fa),Y / BEQ +  ; [2] FILTER low-pass value; 0 = leave alone
      STA <smc filter base>
    INY / LDA (fa),Y          ; PEEK the next step's first byte
      CMP #$FE / BCC +        ;   < $FE  -> continue
      BEQ stop                ;   == $FE -> STOP (clears the arp nibble in the
      LDY #$00                ;              voice's Fx byte, so it stops)
    +                         ;   == $FF -> LOOP back to offset 0
    TYA / STA steppos,X       ; advance by 3
    LDY #<smc note> / LDA freqLo,Y ... freqHi,Y   ; emit the arpeggio's pitch

So a STEP IS 3 BYTES and the terminator is the FOURTH byte peeked — i.e. the
sentinel occupies the first byte slot of what would be the next step, and the
step stream is `(wave, note, filter) * n` followed by a single $FE or $FF.

The waveform is masked with the voice's gate mask, which the sequence decoder
sets to $FF on a note and $FE on a rest — that is how a rest releases the gate
while an arpeggio keeps running.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

ARP_STEP = 3
ARP_STOP = 0xFE
ARP_LOOP = 0xFF
ARP_SLOTS = 16                 # the index is a nibble

# TAY / LDA arpLo,Y / STA zp / LDA arpHi,Y / STA zp+1 / LDY steppos,X
_ARP_SITE = re.compile(rb'\xA8\xB9(..)\x85(.)\xB9(..)\x85(.)\xBC(..)',
                       re.DOTALL)


@dataclass
class ArpStep:
    waveform: int
    note: int                  # raw byte
    filter_lp: int             # 0 = no change

    @property
    def absolute(self) -> bool:
        """bit7 set = an ABSOLUTE note index; else an offset from the note."""
        return bool(self.note & 0x80)

    @property
    def offset(self) -> int:
        return self.note & 0x7F


@dataclass
class Arp:
    id: int
    addr: int
    steps: list
    loops: bool                # ended on $FF (loop to 0) rather than $FE stop


def arp_tables(mem, lo: int = 0, hi: int = 0x10000):
    """(lo_table, hi_table) for the 16 arpeggio pointers, or None.

    `lo`/`hi` bound the search to one player's block — see preset_table()."""
    m = _ARP_SITE.search(bytes(mem[lo:hi]))
    if not m:
        return None
    lo = m.group(1)[0] | (m.group(1)[1] << 8)
    hi = m.group(3)[0] | (m.group(3)[1] << 8)
    zp_a, zp_b = m.group(2)[0], m.group(4)[0]
    if zp_b != zp_a + 1:
        return None
    return lo, hi


def arp(mem, lo_tab: int, hi_tab: int, idx: int, max_steps: int = 128) -> Arp:
    """Decode arpeggio `idx` (1..15; 0 means 'no arpeggio')."""
    a = mem[lo_tab + idx] | (mem[hi_tab + idx] << 8)
    steps, i = [], 0
    for _ in range(max_steps):
        b0 = mem[(a + i) & 0xFFFF]
        if b0 >= ARP_STOP:
            return Arp(id=idx, addr=a, steps=steps, loops=b0 == ARP_LOOP)
        steps.append(ArpStep(waveform=b0,
                             note=mem[(a + i + 1) & 0xFFFF],
                             filter_lp=mem[(a + i + 2) & 0xFFFF]))
        i += ARP_STEP
    raise ValueError('arpeggio %d at $%04X did not terminate' % (idx, a))
