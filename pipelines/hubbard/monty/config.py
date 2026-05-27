"""The Monty on the Run EngineConfig — Monty as a config on the shared
Hubbard '85 core (pipelines/hubbard/).

Rob Hubbard's *Monty on the Run* (1985) — the same engine family as
Commando and Devils Galop. 3 music subtunes, 20 instruments, freq
table at $8400, instrument records at $93B4. The 16 PSID sound effects
(subtunes 3-18) are shipped — see extract/sfx.py.
"""

import os

from pipelines.hubbard.config import EngineConfig
from pipelines.hubbard.monty.extract.engine_model import extract
from pipelines.hubbard.monty.extract.sfx import extract_sfx

# config.py -> monty -> pipelines -> repo root  (3 dirnames)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

SID = os.path.join(ROOT, 'hvsc84', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Monty_on_the_Run.sid')


def _extract(subtune=0):
    return extract(subtune=subtune, sid_path=SID)


def _resetspd(subtune, binary, load):
    """Tick divider — one less than the score's frames-per-tick."""
    return _extract(subtune).score.tempo - 1


MONTY = EngineConfig(
    name='monty',
    sid_path=SID,
    instr_base=0x93B4,
    instr_count=20,
    freq_table_base=0x8400,
    extract=_extract,
    resetspd=_resetspd,
    subtunes=(0, 1, 2),
    arp_interval=12,
    vib_onset=8,                # vibrato gate CMP #$08 at $8201
    incby2_step=-1,             # fx bit1 = DEC v_freq_hi on odd frames ($831A)
    freeze_on_stop=True,        # $FE freezes voices (hold + effects, no gate-off)
    has_sfx=True,               # 16 SFX at $9454 ($8506 SFX init)
    extract_sfx=extract_sfx,
    sfx_state_ofs=251,          # SFX engine state at $84FB (freqtab+251)
    sfx_framectr_ofs=250,       # SFX-readable frame counter at $84FA
)
