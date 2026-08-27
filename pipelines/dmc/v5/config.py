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
    ed_variant: bool = False     # Ed's hand-built V5 player (sole carrier):
                                 # the family-4 HEAD over family-3/5 SEMANTICS
                                 # at its own code offsets. Like `family4`
                                 # this is a DISPATCHER fact — it selects the
                                 # operand-site map and the leftover addresses
                                 # in the extract, and never reaches the USF
                                 # or the composer (Principle §8): what
                                 # crosses is the mechanism knobs.
    data_post_init: bool = False  # INIT-UNPACKER member (ledger C26): the
                                 # song data is absent from the file image —
                                 # the init GENERATES/relocates it into RAM,
                                 # so every table read comes from post-init
                                 # RAM instead. Measured by the factory (the
                                 # off-image table addresses must actually be
                                 # WRITTEN by the init), never assumed.
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

# The opcode each family-4 site's instruction must have. THE HEAD SHAPE IS NOT
# A PLAYER IDENTITY: `_detect_v5` admits family-4 on `JMP base+$40 /
# JMP base+$95` alone — no body check at all, unlike the family-3/5 path's
# masked instruction compare — and one HVSC member wears that head over a
# completely different program (see ED_KIDS_SITES). Applying this site map to
# it read a `STA` opcode byte plus its operand low byte as "orderlist $D89D".
# Census over all 650 family-4-head members: 647 match 12/12, the two most
# heavily re-assembled match 10/12 and 11/12 (their filter sites carry a
# wedge), and the impostor matches 0/12 — so "not one site is where it should
# be" separates a different PLAYER from a wedged MEMBER without a tuned
# threshold, and is ledger C13's positive detection of the minority.
FAMILY4_SITE_OPS = {
    'op_orderlist': 0xB9, 'op_secp_lo': 0xB9, 'op_secp_hi': 0xB9,
    'op_instr': 0xB9, 'op_freq_lo': 0xB9, 'op_freq_hi': 0xB9,
    'op_wave_ctrl': 0xB9, 'op_wave_freq': 0xB9,
    'op_pulse_lo': 0xB9, 'op_pulse_hi': 0xB9,
    'op_filter_lo': 0xB9, 'op_filter_hi': 0xD9,   # filter_hi is the CMP abs,Y
}

# ---- Ed's hand-built V5 player (MUSICIANS/E/Ed/We_Were_All_Kids, the sole
#      HVSC carrier) ---------------------------------------------------------
# Wears the family-4 head but is 2.0% byte-identical to the Jupiter41 player
# over the code window (the other 649 family-4-head members: 47-100%). What it
# actually is: family-3/5 SEMANTICS at its own code offsets — canon track
# commands ($FF loop / $FE stop / $FD,$FC transpose), canon sector commands
# ($F3 vol, $F4 gate-tie, $F5 gate-toggle, $F9 filter, $FA slide, $FD dur,
# $FE gate), canon 8-byte instrument records, canon interleaved tune record,
# curnote at the canon base+$0F. So it gets a site map rather than a refusal.
#
# Sites read off its disassembly (`tools/seed_disassembly.py`) and confirmed by
# the rebuild: its note-init writes reproduce the original's byte for byte
# ($D406=$7E $D405=$00 $D404=$09 on V1, ...) — the table addresses they resolve
# to are therefore right.
ED_KIDS_SITES = {
    'op_orderlist': 0x1045,   # $1044 LDA tunerec,Y   (init track-ptr copy)
    'op_secp_lo': 0x1140,     # $113F LDA secp_lo,Y
    'op_secp_hi': 0x1145,     # $1144 LDA secp_hi,Y
    'op_instr': 0x124A,       # $1249 LDA instr,Y     (8 bytes/instrument)
    'op_freq_lo': 0x132A,     # $1329 LDA freq_lo,Y   (96 entries)
    'op_freq_hi': 0x1330,     # $132F LDA freq_hi,Y
    'op_wave_ctrl': 0x130B,   # $130A LDA wave_ctrl,Y
    'op_wave_freq': 0x1315,   # $1314 LDA wave_freq,Y
    'op_pulse_lo': 0x1345,    # $1344 LDA pulse_lo,Y
    'op_pulse_hi': 0x134B,    # $134A LDA pulse_hi,Y
    'op_filter_lo': 0x1370,   # $136F LDA filter_lo,Y
    'op_filter_hi': 0x1376,   # $1375 LDA filter_hi,Y
}
ED_KIDS_SITE_OPS = {f: 0xB9 for f in ED_KIDS_SITES}

# Leftover-state addresses. Ed keeps curnote at the canon base+$0F, but its
# speed counter and initial filter values live as SELF-MODIFIED IMMEDIATES
# inside the play body rather than in the canon $1013/$1015-$1017 block (which
# on this member is the embedded title text — reading it there produced a
# 5-frame phantom startup delay and a nonsense filter prime).
ED_KIDS_STATE = {
    'lo_spdctr': 0x10D8,   # $10D7 CMP #imm — the MAIN/TICK toggle
    'lo_fclo': 0x10BA,     # $10B9 LDA #imm -> STA $D415
    'lo_fchi': 0x10BF,     # $10BE LDA #imm -> STA $D416
}
# init `LDA #$04 / STA $1096` seeds the play-head's own `LDA #imm / BEQ`
# lead-in counter: its first FOUR play() calls emit nothing (family-3 seeds 2,
# family-4 has no counter). Probed, never assumed (ledger C19).
ED_KIDS_SKIP_IMM = 0x1090
ED_KIDS_SKIP_SHAPE = ((0x108F, 0xA9), (0x1091, 0x8D))   # LDA #imm / STA abs

# Structural signature of Ed's init at base+$40, with every packer-patched and
# relocated operand byte wildcarded: LDY #0 / LDX #0 / (LDA rec,Y / STA ptr,X)
# x2 / INY INY INX / CPX #3 / BNE. Exactly ONE carrier in HVSC under a
# family-4 head (14 other files carry the same skeleton at other offsets under
# other heads, and none of them is routed to V5).
ED_KIDS_INIT_SKEL = (0xA0, 0x00, 0xA2, 0x00,
                     0xB9, None, None, 0x9D, None, None,
                     0xB9, None, None, 0x9D, None, None,
                     0xC8, 0xC8, 0xE8, 0xE0, 0x03, 0xD0, 0xED)
