"""The Hunter Patrol EngineConfig — Hunter Patrol on the shared
Hubbard '85 core (pipelines/hubbard/).

Rob Hubbard's *Hunter Patrol* (1985 Mastertronic). Load $A000, init
$AE1E, play $A006. 1 PSID subtune. 3 active voices.

Instruments at $A427 (8-byte records, up to 32 records though the
extractor returns the 15 in use). Freq table at $A32D — 125 entries
(extended past the standard 96 — pitches 96-124 extend further up
than Commando's table). See pipelines/hubbard/hunter_patrol/disassembly.s.
"""

import os

from pipelines.hubbard.hunter_patrol.extract.engine_model import extract
from pipelines.hubbard.config import EngineConfig

# config.py -> hunter_patrol -> pipelines -> repo root  (3 dirnames)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

SID = os.path.join(ROOT, 'hvsc84', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Hunter_Patrol.sid')


def _extract(subtune=0):
    return extract(subtune=subtune, sid_path=SID)


def _resetspd(subtune, binary, load):
    """Tick divider — frames-per-tick - 1."""
    return _extract(subtune).score.tempo - 1


HUNTER_PATROL = EngineConfig(
    name='hunter_patrol',
    sid_path=SID,
    instr_base=0xA427,
    instr_count=32,
    freq_table_base=0xA32D,
    extract=_extract,
    resetspd=_resetspd,
    subtunes=(0,),
    arp_interval=12,
    # Hunter Patrol gates vibrato on (raw note byte & $1F) >= 8 ($A194
    # CMP #$08). Default 6 fires too eagerly on short notes.
    vib_onset=8,
    # Hunter Patrol ships with the sub-frame counter $A418=$01 (reload
    # $A419=$02), so the first note-load lands on frame 1 — frame 0 is
    # effects-only. Matches the disasm "TEMPO INITIAL STATE" block.
    speed_ctr_init=1,
    # Hunter Patrol's $A426 (music frame counter) is $1E at load time;
    # first play() INCs to $1F (odd). Default $FF gives $00 on frame 0
    # which would flip the arp / skydive parity.
    frame_ctr_init=0x1E,
    # Hunter Patrol's skydive (fx_flags bit 1, $A2C9) DECrements
    # v_fhi every odd frame, gated on (note duration field & $1F) >=
    # $0C AND v_dur countdown < $09. Maps to the shared fx_incby2 with
    # step=-1, onset=12, and the new "late-in-note" gate at 9.
    incby2_step=-1,
    incby2_onset=12,
    incby2_late_gate=9,
    has_sfx=False,
)
