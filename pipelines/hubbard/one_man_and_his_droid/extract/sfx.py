"""One Man and his Droid sound-effect extraction.

14 PSID subtunes: subtune 0 = main music, subtunes 1..13 = drum/SFX
patterns played through the secondary "drum engine" at $139F. Each
SFX is a 16-byte record at $1600 + idx*16 — same shared Hubbard '85
format used by Commando / Thing on a Spring.
"""

from pipelines.hubbard.sfx import SoundEffect, extract_sfx as _extract_sfx

SFX_TABLE = 0x1600       # 13 SFX × 16 bytes (last 3 slots unused)
FREQ_TABLE = 0x1422
NUM_SFX = 13


def extract_sfx(sid_path: str) -> tuple[list[SoundEffect], bytes]:
    return _extract_sfx(sid_path, SFX_TABLE, FREQ_TABLE, NUM_SFX)
