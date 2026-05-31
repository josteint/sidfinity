"""The Chimera EngineConfig — Chimera on the shared Hubbard '85 core
(pipelines/hubbard/).

Rob Hubbard's *Chimera* (1985 Firebird). The binary is two players:
a music engine at $C200/$C203/$C206 (the standard '85 tracker) and a
digi/SFX player at $C000. Only the 2 music subtunes are migrated here;
the SFX subtunes use the digi player and are not shipped.

Instruments at $C662 (8-byte records), freq table at $C567.
See pipelines/hubbard/chimera/disassembly.s.
"""

import os

from pipelines.hubbard.chimera.extract.engine_model import extract
from pipelines.hubbard.config import EngineConfig

# config.py -> chimera -> pipelines -> repo root  (3 dirnames)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

SID = os.path.join(ROOT, 'hvsc84', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Chimera.sid')


def _extract(subtune=0):
    return extract(subtune=subtune, sid_path=SID)


def _resetspd(subtune, binary, load):
    """Tick divider — one less than the score's frames-per-tick."""
    return _extract(subtune).score.tempo - 1


CHIMERA = EngineConfig(
    name='chimera',
    sid_path=SID,
    instr_base=0xC662,
    instr_count=19,
    freq_table_base=0xC567,
    extract=_extract,
    resetspd=_resetspd,
    subtunes=(0, 1),
    arp_interval=12,
    arp_period=8,       # arp frame & 7 — base 1-of-8, +12 7-of-8 ($C539)
    linear_pw_or=0x40,  # linear PW does ORA #$40 on pw_lo ($C412)
    incby2_step=1,      # fx bit 1 does INC v_fhi (+1, $C526)
    incby2_onset=0x11,  # fx bit 1 needs dur field >= $11
    has_sfx=False,
    vib_onset=8,        # vibrato gate CMP #$08 at $C3D3
    speed_ctr_init=2,   # $C652/$C653 tick gate defers note-load 2 frames
    digi_subtunes=(2, 3),  # 1-bit wavetoggle samples via $C000 player
    is_rsid=True,          # IRQ-driven, KERNAL ROM required
)
