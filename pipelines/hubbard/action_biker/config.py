"""The Action Biker EngineConfig — Action Biker on the shared
Hubbard '85 core (pipelines/hubbard/).

Rob Hubbard's *Action Biker* (1985 Mastertronic). Load $C000,
init $CBBB, play $C00D. 3 music subtunes, 12 instruments at $CB5B,
freq table at $C2FC. See docs/hubbard_action_biker_disassembly.s.
"""

import os

from pipelines.hubbard.action_biker.extract.engine_model import extract
from pipelines.hubbard.config import EngineConfig

# config.py -> action_biker -> pipelines -> repo root  (3 dirnames)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

SID = os.path.join(ROOT, 'demo', 'hubbard', 'Action_Biker_original.sid')


def _extract(subtune=0):
    return extract(subtune=subtune, sid_path=SID)


def _resetspd(subtune, binary, load):
    """Tick divider — one less than the score's frames-per-tick."""
    return _extract(subtune).score.tempo - 1


ACTION_BIKER = EngineConfig(
    name='action_biker',
    sid_path=SID,
    instr_base=0xCB5B,
    instr_count=12,
    freq_table_base=0xC2FC,
    extract=_extract,
    resetspd=_resetspd,
    subtunes=(0, 1, 2),
    arp_interval=12,
    vib_onset=8,                # vibrato gate CMP #$08 at $C1B5
    has_sfx=False,
    speed_ctr_init=1,           # $C3E7 starts $01 — first note-load on frame 1
    first_frame_gate_off=True,  # $C28E clears V1/V2/V3 ctrl in play frame 0
    voice_starts=(1, 2, 2),     # subtune 0 starts at V2 ($C3F2), skipping V3
    stop_fill=0x80,             # $FE ends the song writing $80 everywhere ($C2DC)
)
