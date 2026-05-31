"""The Confuzion EngineConfig — Hubbard '85 family, stripped variant.

Rob Hubbard's *Confuzion* (1985 Incentive Software). Single subtune.
Standard Hubbard '85 row-major instrument table (8-byte records) at
$1146; freq table at $0AFD; init $0867; play $0858.

Engine is a STRIPPED Hubbard '85: only vibrato + bidirectional PWM.
No bit-0/1/2 skydive/arp/incby2 effect dispatch (fx_flags bits 0-2
are unused by the runtime). No bit-3 linear PW. Frame counter lives
in zero page $A2, advanced via self-modifying `INC $085C` (the
operand byte of a `LDA #imm`) at end of play.
"""

import os

from pipelines.hubbard.confuzion.extract.engine_model import extract
from pipelines.hubbard.config import EngineConfig

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

SID = os.path.join(ROOT, 'hvsc84', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Confuzion.sid')


def _extract(subtune=0):
    return extract(subtune=subtune, sid_path=SID, ft_base=0x0AFD)


def _resetspd(subtune, binary, load):
    return _extract(subtune).score.tempo - 1


CFG = EngineConfig(
    name='confuzion',
    sid_path=SID,
    instr_base=0x1146,
    instr_count=12,
    freq_table_base=0x0AFD,
    extract=_extract,
    resetspd=_resetspd,
    subtunes=(0,),
    arp_interval=12,
    vib_onset=8,
    speed_ctr_init=2,
    # Song-end fade: the engine's bit-7 instrument-change note path
    # writes $D418 = clamp($A0 - $0BC2, 0..$0F), where $0BC2 = V2's
    # orderlist position (an absolute counter that doesn't reset on
    # song-loop). Once V2 has advanced past $91 patterns the formula
    # drops below $0F and the master VOL fades to $00 over the next
    # ~22 seconds. See [[project_hubbard_song_end_fade]].
    master_vol_subtrahend_voice=1,
    master_vol_base=0xA0,
    # V2 ends via $FE just past BASE+1 ($A1). Without the underflow
    # clamp, the buggy SBC wrap would jump $D418 back to $0F at the
    # next inst-change. With it, the formula correctly writes $00 for
    # vol_progress > BASE. See [[project_hubbard_song_end_fade]].
    master_vol_underflow_clamp=True,
    # Engine's tie path ($807A BVS $80C0) jumps over the v_slide clear
    # at $807C — so a tie note must preserve whatever slide was set on
    # the head note. Without this the slide is lost on the first tie.
    tie_preserves_slide=True,
)
