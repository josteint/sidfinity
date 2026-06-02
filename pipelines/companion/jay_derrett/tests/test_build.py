"""Acceptance test for the Jay_Derrett clean composer (Phase 2)."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from pipelines.companion.jay_derrett.build import build_ninja_hamster_sid
from pipelines.hubbard.verify_cycle import (
    writelog_capture, compare_instruction_stream,
)


def test_ninja_hamster_byte_exact():
    """Composer must produce byte-exact SID writes vs orig at the
    regression-standard 6s capture window."""
    sid_orig = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   'Ninja_Hamster.sid')
    sid_reb = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                  'Ninja_Hamster.sidfinity.sid')

    # Build into reb file
    Path(sid_reb).write_bytes(build_ninja_hamster_sid())

    a = writelog_capture(sid_orig, 0, duration=6.0)
    b = writelog_capture(sid_reb, 0, duration=6.0)
    r = compare_instruction_stream(a, b)
    assert r['is_full'], (
        f"compare_instruction_stream failed: match_all="
        f"{r['match_all']}/{r['len_all_a']}/{r['len_all_b']}")
