"""The One Man and his Droid EngineConfig — One Man and his Droid on
the shared Hubbard '85 core (pipelines/hubbard/).

Rob Hubbard's *One Man and his Droid* (1985 Mastertronic). Load
$1000, init $1000 (trampoline to $1F70), play $1012. 14 PSID
subtunes: subtune 0 = the 3-voice main song, subtunes 1..13 =
drum/SFX patterns (sample playback via the $139F engine + $1600
16-byte recipes).

Instruments at $1588 (8-byte records). Freq table at $1422
(96 entries, standard Hubbard '85 PAL table). See
docs/hubbard_one_man_and_his_droid_disassembly.s.

Fx-flag layout:
  bit 0 = freq slide (drum/skydive) → shared fx_skydive
  bit 1 = alt slide (mid-note bend) → shared fx_incby2
  bit 2 = octave-trill arpeggio (4-frame toggle) → shared fx_arp
  bit 3 = linear PWM → shared fx_pwm mode='linear'
"""

import os

from pipelines.one_man_and_his_droid.extract.engine_model import extract
from pipelines.one_man_and_his_droid.extract.sfx import extract_sfx
from pipelines.hubbard.config import EngineConfig

# config.py -> one_man_and_his_droid -> pipelines -> repo root  (3 dirnames)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

SID = os.path.join(ROOT, 'demo', 'hubbard',
                   'One_Man_and_his_Droid_original.sid')


def _extract(subtune=0):
    return extract(subtune=subtune, sid_path=SID)


def _resetspd(subtune, binary, load):
    return _extract(subtune).score.tempo - 1


ONE_MAN_AND_HIS_DROID = EngineConfig(
    name='one_man_and_his_droid',
    sid_path=SID,
    instr_base=0x1588,
    instr_count=32,
    freq_table_base=0x1422,
    extract=_extract,
    resetspd=_resetspd,
    subtunes=(0,),
    arp_interval=12,
    # Vibrato gated on `(v_durfield & $1F) >= $08` ($11F7).
    vib_onset=8,
    # $150D=$00 and $150E=$01 at load: first DEC wraps to $FF, reloads
    # to $01, equal-check passes, note-load on frame 0 (default
    # behavior, no defer — unlike Hunter Patrol's speed_ctr_init=1).
    # bit 1 = "alt slide" ($132C): DEC v_fhi each odd frame, write OLD,
    # gated on (dur_field & $1F) >= $10 AND v_dur < $18.
    incby2_step=-1,
    incby2_onset=16,
    incby2_late_gate=24,
    # bit 2 = "octave-trill arpeggio (4-frame toggle)": tests
    # `frame_ctr & $04`. NON-zero (= bit 2 set, frames 4-7, 12-15, ...)
    # → base; ZERO (frames 0-3, 8-11, ...) → +12. Period = 8 frames
    # with the cycle 4 high + 4 base. Set arp_period=5 (so ARP_MASK=4
    # = $04) and arp_phase_invert=True (to swap the base/+12 sense).
    arp_period=5,
    arp_phase_invert=True,
    # 13 drum/SFX overlays at $1600 — same 16-byte format as Commando.
    has_sfx=True,
    extract_sfx=extract_sfx,
)
