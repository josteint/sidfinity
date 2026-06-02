"""Acceptance test for the Jay_Derrett emulator (Phase 1)."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from pipelines.companion.jay_derrett.emulator import validate_ninja_hamster


def test_ninja_hamster_300_seconds():
    """Emulator must produce byte-exact SID writes matching siddump
    writelog for at least 15,000 frames (300s = full song + loops)."""
    r = validate_ninja_hamster(15000)
    assert r['first_div'] is None, (
        f"Diverged at write {r['first_div']}: "
        f"emu={r['div_emu']} vs orig={r['div_orig']}")
    assert min(r['n_emu'], r['n_orig']) > 200_000, (
        f"Too few writes captured: emu={r['n_emu']} orig={r['n_orig']}")
