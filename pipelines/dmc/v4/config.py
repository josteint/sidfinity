"""DMC V4 per-SID extract config.

The DMC editor's packer patches the player's absolute data-table
operands per song (see pipelines/dmc/v4/disassembly.s — KEY FINDING).
The config therefore carries the CODE OFFSETS of the operand sites,
and the extract reads the actual table addresses from the binary by
dataflow. Only the freq tables, the instrument base and the per-note
vibrato-depth table are fixed (code-addressed).

All offsets are relative to the load address (= $1000 for the
standard family-1 layout; the operand sites are code positions and
move only if the player code itself is shifted, which the factory
must detect).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DMCV4Config:
    sid_path: str                     # HVSC-relative path
    name: str = ''
    # player base address. Canonical = $1000; relocated members carry
    # the same engine at a different base (operand sites + fixed tables
    # all shift by base - $1000). Extract reads from the relocated
    # addresses; the composer always emits OUR engine at $1000, so the
    # rebuild + verdict are base-independent (relocation is extract-only).
    base: int = 0x1000
    # operand sites (address of the abs,y operand low byte)
    op_instr: int = 0x1227            # instrument records (always $18F0)
    op_wavectrl: int = 0x159C         # wave table CTRL array
    op_wavefreq: int = 0x15B9         # wave table FREQ array
    op_filtdef: int = 0x1296          # filter definition table
    op_tunetab: int = 0x180E          # tune pointer records
    op_secp_lo: int = 0x1103          # sector pointer table LO
    op_secp_hi: int = 0x1108          # sector pointer table HI
    # fixed (code-addressed) tables
    freq_lo_addr: int = 0x1647
    freq_hi_addr: int = 0x16A7
    vibdepth_addr: int = 0x1888       # per-note vibrato depth (96 bytes,
                                      # first 6 overlap player code)
    d417_shadow_addr: int = 0x1018    # routing shadow — NOT cleared by
                                      # init; file-image leftover primes
                                      # the play stream's $D417 writes
    # Track-loop variant (factory-probed): the canonical player's $FF
    # loops to track position 0; the JSR-$1042 hook variant reads the
    # NEXT track byte as the loop position ($FF nn).
    track_loop_target: bool = False
    # CIA multispeed (factory-probed): when the PSID play() is driven by
    # a CIA1 timer A (a multispeed wrapper at 2-6x), this is the timer
    # latch the original programs ($DC04/$DC05, read by running init in
    # py65). The composer sets the PSID speed bit + programs the SAME
    # latch so libsidplayfp drives our play() at the identical rate.
    # 0 = single-speed VBI.
    cia_period: int = 0


ZAKS = DMCV4Config(
    sid_path='MUSICIANS/A/Amadeus_Slash_Design/Geometrical_Zaks.sid',
    name='geometrical_zaks',
)
