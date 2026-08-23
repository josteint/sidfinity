"""DMC V5 per-SID extract config.

Like V4, the editor's packer patches the player's absolute data-table
operands per song. The config carries the CODE OFFSETS of the operand
sites; the extract reads the actual table addresses by dataflow and
derives region sizes from the address deltas (V4-style). See
pipelines/dmc/v5/disassembly.s (the annotated family-3/5 player) +
RE_NOTES.md for the site map.

Offsets are relative to the load address ($1000 for the standard
family-3 layout; family-4 is a distinct branch — play +$95 not +$A1 —
and will need its own site map).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DMCV5Config:
    sid_path: str
    name: str = ''
    base: int = 0x1000
    # operand sites (address of the abs,y operand low byte) — the player
    # reads each table at these code positions; the packer patches the
    # absolute base per song.
    op_orderlist: int = 0x1047   # track-pointer record ($1878)
    op_secp_lo: int = 0x114F     # sector pointer table LO ($196E)
    op_secp_hi: int = 0x1154     # sector pointer table HI ($1972)
    op_instr: int = 0x12CC       # instrument table ($1976), 8 bytes/instr
    op_freq_lo: int = 0x13A6     # freq table LO ($170F)
    op_freq_hi: int = 0x13AC     # freq table HI ($176F)
    op_wave_ctrl: int = 0x1386   # wave-table ctrl array ($199E)
    op_wave_freq: int = 0x1390   # wave-table freq/offset array ($19AB)
    op_pulse_lo: int = 0x13C1    # pulse-table arg LO ($19B8)
    op_pulse_hi: int = 0x13C7    # pulse-table arg HI ($19BF)
    op_filter_lo: int = 0x13F0   # filter-table arg LO ($19C6)
    op_filter_hi: int = 0x13F6   # filter-table arg HI ($19C7)
    cia_period: int = 0          # CIA1 timer A latch for multispeed (0 = VBI)
    family4: bool = False        # the Jupiter41 V5 variant (play +$95): same
                                 # data format, different player (2-phase $1016
                                 # timing, $D416-only filter) + $EF/$F0 sector
                                 # cmds. Operand sites overridden by the factory.
    n_songs: 'int | None' = None  # orderlist-record count override. A packed
                                 # COMPILATION sub-player (ledger C31) owns
                                 # fewer songs than the FILE header declares;
                                 # None = the PSID header count (standalone).
    play_phases: str = ''        # ledger C18 per-call phase schedule
                                 # ('P_F123_F123_...') for a WRAPPER member
                                 # whose play vector runs the full play only
                                 # every Nth call and an effects-only pass on
                                 # the others. '' = no wrapper (canon).
    post_init_sub: 'int | None' = None  # RELOCATED sub-player (C31+C26): the
                                 # wrapper copies it into RAM, so every memory
                                 # read uses the RAM left by THIS subtune's
                                 # init (snapshot at the landing), not the
                                 # file image. None = the image (standalone).


KATUSHA = DMCV5Config(sid_path='DEMOS/G-L/Katusha.sid', name='katusha')

# family-4 (Jupiter41) operand sites — the $1000-based code PCs (the abs,Y
# operand LOW byte). The factory relocates them by (load-$1000). See
# pipelines/dmc/family4/RE_NOTES.md for the full site derivation.
FAMILY4_SITES = {
    'op_orderlist': 0x1047, 'op_secp_lo': 0x1147, 'op_secp_hi': 0x114C,
    'op_instr': 0x1339, 'op_freq_lo': 0x1686, 'op_freq_hi': 0x168F,
    'op_wave_ctrl': 0x1658, 'op_wave_freq': 0x165F,
    # pulse: family-4's pulse_run adds $23BC->PW_lo / $23A3->PW_hi, but the
    # composer does PW_lo += pulse_hi / PW_hi += pulse_lo — so op_pulse_lo must
    # read $23A3 ($14D0) and op_pulse_hi $23BC ($14C6) (swapped vs the raw read).
    'op_pulse_lo': 0x14D0, 'op_pulse_hi': 0x14C6,
    'op_filter_lo': 0x1496, 'op_filter_hi': 0x14A7,
}
