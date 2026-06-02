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


import pytest
from pipelines.companion.jay_derrett.build import (
    build_sid, params_from_extracted_json,
)


CLUSTER_A_SIDS = [
    'Jetboys', 'Lifeforce', 'Mandroid', 'Ninja_Hamster', 'Vengeance', 'ZIP',
]


@pytest.mark.parametrize('name', CLUSTER_A_SIDS)
def test_cluster_a_byte_exact(name):
    """All Cluster A SIDs (NH-shape engine variant: 24-byte program,
    stride 26, direct dispatch) must produce byte-exact SID writes."""
    sid_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   f'{name}.sid')
    reb_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   f'{name}.sidfinity.sid')
    json_path = str(ROOT / 'pipelines' / 'companion' / 'jay_derrett' /
                    '_extracted' / f'{name}.json')
    params = params_from_extracted_json(json_path)
    import json
    jd = json.load(open(json_path))
    voice_byte_ranges = [
        (vb['ptr_min'], vb['ptr_min'] + len(vb['bytes']))
        for vb in jd['voice_bytes']
    ]
    Path(reb_path).write_bytes(
        build_sid(sid_path, params, voice_byte_ranges=voice_byte_ranges))
    a = writelog_capture(sid_path, 0, duration=6.0)
    b = writelog_capture(reb_path, 0, duration=6.0)
    r = compare_instruction_stream(a, b)
    assert r['is_full'], (
        f"{name}: match_all={r['match_all']}/{r['len_all_a']}/{r['len_all_b']}")
