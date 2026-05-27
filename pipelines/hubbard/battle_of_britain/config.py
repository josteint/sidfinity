"""The Battle of Britain EngineConfig — Hubbard '85 family.

Rob Hubbard's *Battle of Britain* (1985 Personal Software Services).
Single subtune. Standard Hubbard '85 row-major instrument table
(8-byte records) at $8420, freq table at $8326, init $8EAA, play $8006.

Per prior session research (see commits 3c979d7..1d2ae5f):
- 19 instruments
- 96-entry freq table at $8326
- PSID speed = CIA timer ($01)
- Frame counter seed value $DC at offset $50
"""

import os

from pipelines.hubbard.battle_of_britain.extract.engine_model import extract
from pipelines.hubbard.config import EngineConfig

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

SID = os.path.join(ROOT, 'demo', 'hubbard', 'Battle_of_Britain_original.sid')


def _extract(subtune=0):
    return extract(subtune=subtune, sid_path=SID, ft_base=0x8326)


def _resetspd(subtune, binary, load):
    return _extract(subtune).score.tempo - 1


CFG = EngineConfig(
    name='battle_of_britain',
    sid_path=SID,
    instr_base=0x8420,
    instr_count=19,
    freq_table_base=0x8326,
    extract=_extract,
    resetspd=_resetspd,
    subtunes=(0,),
    arp_interval=12,
    arp_period=8,
    frame_ctr_init=0xDC,
    incby2_step=-1,
    incby2_onset=12,
    vib_onset=8,
    # Engine's tie path (BVS $80C0) jumps over the v_slide clear at
    # $807C — preserves slide set on the head note across ties.
    tie_preserves_slide=True,
)
