"""Monty sound-effect extraction — the Hubbard '85 SFX format (shared
core, pipelines/hubbard/sfx.py). Monty's 16 SFX records live at $9454
and the sweep reads the freq table at $8400. The SFX init at $8506
(see docs/hubbard_monty_disassembly.s) is structurally Commando's
$53A5 sub-engine — only the addresses differ.
"""

from pipelines.hubbard.sfx import extract_sfx as _extract_sfx

SFX_TABLE = 0x9454
FREQ_TABLE = 0x8400


def extract_sfx(sid_path):
    """Monty's 16 SFX records at $9454, freq table at $8400."""
    return _extract_sfx(sid_path, SFX_TABLE, FREQ_TABLE)
