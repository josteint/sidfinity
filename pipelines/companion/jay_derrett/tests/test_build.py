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
from pipelines.companion.jay_derrett.type_b import build_type_b_sid


TYPE_B_SIDS = ['Equalizer', 'Death_or_Glory', 'Sqij', 'Dracula']
TYPE_B_PREFIX_MATCH = {'Dracula'}  # CIA-driven; reb has trailing extras


@pytest.mark.parametrize('name', TYPE_B_SIDS)
def test_type_b_byte_exact(name):
    """Type B SIDs (Equalizer-shape engine, 5-byte inst program,
    per-voice unrolled PWM mod)."""
    sid_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   f'{name}.sid')
    reb_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   f'{name}.sidfinity.sid')
    Path(reb_path).write_bytes(build_type_b_sid(name))
    a = writelog_capture(sid_path, 0, duration=6.0)
    b = writelog_capture(reb_path, 0, duration=6.0)
    r = compare_instruction_stream(a, b)
    if name in TYPE_B_PREFIX_MATCH:
        assert r['match_all'] == r['len_all_a'], (
            f"{name}: prefix-match failed match_all={r['match_all']}"
            f"/{r['len_all_a']}/{r['len_all_b']}")
    else:
        assert r['is_full'], (
            f"{name}: match_all={r['match_all']}/{r['len_all_a']}"
            f"/{r['len_all_b']}")


CLUSTER_A_SIDS = [
    'Jetboys', 'Lifeforce', 'Mandroid', 'Ninja_Hamster', 'Vengeance', 'ZIP',
]

# Cluster B SIDs verifiable via siddump --writelog (PSID-compatible orig).
CLUSTER_B_PSID_SIDS = ['Counterforce', 'Destruct', 'Stratton']

# Cluster C SIDs (stride-24, no off-slide path, no-INC dispatch).
CLUSTER_C_SIDS = ['Discovery']

# Cluster B IRQ-driven SIDs (RSID orig with play=$0000). Verified
# via py65 capture for orig + siddump for reb (which ships as PSID).
CLUSTER_B_IRQ_SIDS = ['Osmium', 'Thundercross', 'Trigger_Happy']


def _build_and_load_data(name):
    """Build + return (sid_path, reb_path, params, vbr)."""
    sid_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   f'{name}.sid')
    reb_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   f'{name}.sidfinity.sid')
    json_path = str(ROOT / 'pipelines' / 'companion' / 'jay_derrett' /
                    '_extracted' / f'{name}.json')
    params = params_from_extracted_json(json_path)
    import json
    jd = json.load(open(json_path))
    vbr = [(vb['ptr_min'], vb['ptr_min'] + len(vb['bytes']))
           for vb in jd['voice_bytes']]
    Path(reb_path).write_bytes(
        build_sid(sid_path, params, voice_byte_ranges=vbr))
    return sid_path, reb_path


@pytest.mark.parametrize('name', CLUSTER_A_SIDS + CLUSTER_B_PSID_SIDS + CLUSTER_C_SIDS)
def test_psid_byte_exact(name):
    """SIDs whose orig is PSID — verify via siddump --writelog both sides."""
    sid_path, reb_path = _build_and_load_data(name)
    a = writelog_capture(sid_path, 0, duration=6.0)
    b = writelog_capture(reb_path, 0, duration=6.0)
    r = compare_instruction_stream(a, b)
    assert r['is_full'], (
        f"{name}: match_all={r['match_all']}/{r['len_all_a']}/{r['len_all_b']}")


@pytest.mark.parametrize('name', CLUSTER_B_IRQ_SIDS)
def test_rsid_irq_byte_exact(name):
    """RSID IRQ-driven SIDs (play=$0000) — orig captured via py65
    (follows IRQ vector at $0314/$0315 after init), reb captured
    via siddump (reb ships as PSID with normal play addr). Compare
    write sequences as prefix-match (different end-of-capture
    boundary handling)."""
    from pipelines.companion.jay_derrett.build import capture_writes_via_py65
    sid_path, reb_path = _build_and_load_data(name)
    orig = capture_writes_via_py65(sid_path, 0, n_frames=50)
    reb = writelog_capture(reb_path, 0, duration=1.0)
    fa = [(r, v) for f in orig for c, r, v in f]
    fb_all = [(r, v) for f in reb for c, r, v in f]
    # reb has 2 init $D418 writes before the per-frame play; py65
    # capture starts at play frame 0 (post-init).
    fb = fb_all[2:]
    n = min(len(fa), len(fb))
    div = next((i for i in range(n) if fa[i] != fb[i]), None)
    assert div is None, (
        f"{name}: diverge at write {div}: orig={fa[div]} reb={fb[div]}")
    assert n > 500, f"{name}: too few matched writes: {n}"
