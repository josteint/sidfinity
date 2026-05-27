"""sfx.py — Thing on a Spring sound-effect extraction.

17 PSID subtunes: subtune 0 = the song, subtunes 1..16 = SFX overlays.
Each SFX is a 2-voice register snapshot plus a freq-table pitch sweep,
exactly the same 16-byte record shape as Commando's SFX. Only the
addresses differ; see pipelines/hubbard/sfx.py for the field layout.
"""

from pipelines.hubbard.sfx import SoundEffect, extract_sfx as _extract_sfx

SFX_TABLE = 0xCDA2       # 16 SFX × 16 bytes
FREQ_TABLE = 0xC3A9      # shared note-frequency table


def extract_sfx(sid_path: str) -> tuple[list[SoundEffect], bytes]:
    return _extract_sfx(sid_path, SFX_TABLE, FREQ_TABLE)
