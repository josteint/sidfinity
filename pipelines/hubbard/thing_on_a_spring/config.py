"""The Thing on a Spring EngineConfig — Thing on a Spring on the
shared Hubbard '85 core (pipelines/hubbard/).

Rob Hubbard's *Thing on a Spring* (1985 Gremlin Graphics). Load
$C000, init $CECB, play $C012. 17 PSID subtunes: subtune 0 is the
song; subtunes 1..16 are SFX overlays (not migrated yet).

Instruments at $CD2A (8-byte records × 15). Freq table at $C3A9
(96 entries, standard Hubbard '85 PAL table). See
pipelines/hubbard/thing_on_a_spring/disassembly.s.

Fx flag layout:
  bit 0 = freq_hi down-sweep (drum)        → shared fx_skydive
  bit 1 = freq_hi up-sweep                  → shared fx_incby2 (step=+?)
  bit 2 = arpeggio (+24 semitones, odd fr) → shared fx_arp (interval=24)
  (no bit 3 used)
"""

import os

from pipelines.hubbard.thing_on_a_spring.extract.engine_model import extract
from pipelines.hubbard.thing_on_a_spring.extract.sfx import extract_sfx
from pipelines.hubbard.config import EngineConfig

# config.py -> thing_on_a_spring -> pipelines -> repo root  (3 dirnames)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

SID = os.path.join(ROOT, 'hvsc84', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Thing_on_a_Spring.sid')


def _extract(subtune=0):
    return extract(subtune=subtune, sid_path=SID)


def _resetspd(subtune, binary, load):
    """Tick divider — frames-per-tick - 1."""
    return _extract(subtune).score.tempo - 1


THING_ON_A_SPRING = EngineConfig(
    name='thing_on_a_spring',
    sid_path=SID,
    instr_base=0xCD2A,
    instr_count=15,
    freq_table_base=0xC3A9,
    extract=_extract,
    resetspd=_resetspd,
    subtunes=(0,),
    # Arpeggio adds +24 semitones (2 octaves) on odd frames.
    arp_interval=24,
    # Tempo $C494=$01, $C495=$01 → first note-load on frame 1 (same
    # pattern as Hunter Patrol's $A418=$01).
    speed_ctr_init=1,
    # fx bit 1 (up-sweep) at $C2CA: INC v_fhi_acc, write OLD to FREQ_HI
    # every frame. No long-note guard, no odd-frame gate.
    incby2_step=1,
    incby2_every_frame=True,
    incby2_onset=0,
    # 16 SFX overlays at $CDA2 — same 16-byte record format as Commando.
    has_sfx=True,
    extract_sfx=extract_sfx,
    # Song-end fade: engine writes $D418 = clamp($47 - V3_orderpos, 0..$0F)
    # on every instrument-change note ($C0C0-$C0CC). V3's pattern-end
    # counter ($C46F = $C46D + V3) drives the fade — same mechanism as
    # Confuzion but with V3 (not V2) and a different base ($47 vs $A0).
    # See [[project_hubbard_song_end_fade]].
    master_vol_subtrahend_voice=2,
    master_vol_base=0x47,
    master_vol_trigger='every_note',
    # V3's master_vol counter IS V3's orderlist position — on the
    # engine's $FF loop, V3_orderpos resets to orderLoop[V3]=0 and
    # the master_VOL fade restarts in the next pass. Without this,
    # vol_progress keeps climbing past 78 and the formula's upper
    # clamp pins $D418=$0F for the rest of the run.
    master_vol_reset_on_loop=True,
)
