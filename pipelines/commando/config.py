"""The Commando EngineConfig — Commando as a config on the shared
Hubbard '85 core (pipelines/hubbard/)."""

import os

from pipelines.commando.extract.engine_model import extract
from pipelines.hubbard.config import EngineConfig
from pipelines.hubbard.inst_interp import subtune_resetspd

# config.py -> commando -> pipelines -> repo root  (3 dirnames)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

COMMANDO = EngineConfig(
    name='commando',
    sid_path=os.path.join(ROOT, 'demo', 'hubbard', 'Commando_original.sid'),
    instr_base=0x5591,
    instr_count=13,
    extract=extract,
    resetspd=subtune_resetspd,
    arp_interval=12,
)
