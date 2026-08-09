"""The Human Race EngineConfig — Human Race on the shared Hubbard '85
core (pipelines/hubbard/).

Rob Hubbard's *The Human Race* (1985 Mastertronic). Load $A000, init
$B1A3, play $A006. All music (V3 unused — only V1 + V2 carry music
for the PSID).

Instruments at $A463 (8-byte records, 23 instruments), freq table
at $A364 (96+ semitone entries). See pipelines/hubbard/human_race/disassembly.s.

⚠ HVSC #85 SHIPS A RE-ASSEMBLED RIP. #84 loaded at $0980 (init $0980
trampolining to $1A9C, play $0986); #85 is the SAME player re-assembled
at $A000 (+$9680), plus an 89-byte tail at $B160-$B1B8 carrying a 6th
subtune. The two images align at file offset 0 and their freq table and
instrument records are BYTE-IDENTICAL at the shifted addresses; the ~589
differing bytes are the absolute-address operands. So the migration was
exactly these two base constants — subtunes 0-4 verify FULL unchanged.
The disassembly.s in this directory still documents the #84 addresses;
subtract $9680 to read it against #85.

The #85 header declares 6 songs (speed $2F: subtunes 0-3 and 5 CIA-timed)
but the engine's own song table still holds 5, because the 6th is reached
through the new init at $B1A3 rather than a table entry. `subtunes` below
therefore stays (0..4) — see the note there.
"""

import os

from pipelines.hubbard.human_race.extract.engine_model import extract
from pipelines.hubbard.config import EngineConfig

# config.py -> human_race -> pipelines -> repo root  (3 dirnames)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

SID = os.path.join(ROOT, 'hvsc85', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Human_Race.sid')


def _extract(subtune=0):
    return extract(subtune=subtune, sid_path=SID)


def _resetspd(subtune, binary, load):
    """Tick divider — one less than the score's frames-per-tick."""
    return _extract(subtune).score.tempo - 1


HUMAN_RACE = EngineConfig(
    name='human_race',
    sid_path=SID,
    instr_base=0xA463,
    instr_count=23,
    freq_table_base=0xA364,
    extract=_extract,
    resetspd=_resetspd,
    # The #85 header declares 6 songs, but the engine's song table holds 5:
    # the 6th (index 5) is "subtune #5 as slow as Rob Hubbard wanted in 1985"
    # per the official changelog, reached via the new $B1A3 init rather than a
    # song-table entry, and CIA-timed (speed bit 5). It is NOT yet extracted —
    # adding it here without that work would ship a wrong subtune, which is
    # worse than shipping five right ones.
    subtunes=(0, 1, 2, 3, 4),
    arp_interval=12,
    # HR's `fx_arp` cycles 1 frame base + 7 frames +octave, keyed on
    # `frame_ctr & 7`. Confirmed via src/usf/audit.py on V1 inst 16
    # (drumarp-only) subtune 3 frames 512-555. Shared-core default is
    # 2 (Commando's alternate-every-frame); HR is period 8.
    arp_period=8,
    # HR's `fx_skydive` (bit 1) increments v_fhi by 1 on odd frames
    # after the note has been held long enough ((v_flags & $1F) >= $11
    # = 17). Confirmed via src/usf/audit.py on V1 inst 21
    # (skydive+PWmode) subtune 4 frames 575-604: $0CAA writes old v_fhi
    # then INC v_fhi on odd frames. Same shape as shared-core
    # `fx_incby2`; Commando defaults are step=2 onset=3.
    incby2_step=1,
    incby2_onset=17,
    # HR's linear PWM (fx_flags bit 3, $0B8F) ORs the running pw_lo
    # with $40 each frame ("force bit 6 — PW>=$40 always"). Commando's
    # shared default is 0; HR uses $40.
    linear_pw_or=0x40,
    has_sfx=False,
    # HR's vibrato gate is `v_flags & $1F >= 8` ($0B50). Our extractor
    # stores playback duration (encoded + 1), so the equivalent test
    # is `playback_dur >= 9`. Hence vib_onset=9, not 8.
    vib_onset=9,
    # Human Race uses only V1+V2 for music; V3 is silent across all
    # subtunes. The per-voice loop starts at V2 (index 1), processing
    # V2 then V1 (decrementing), skipping V3.
    voice_starts=(1, 1, 1, 1, 1),
    # Human Race's engine init at $1A9C zeros per-voice state at
    # runtime; it does NOT read load-time bytes from the freq-table
    # overlap region. Disable seeding to avoid leaking those bytes as
    # spurious initial values for v_inst etc.
    seed_overlap=False,
)
