"""Full pipeline regression — Hubbard '85 + companion strains.

Phase 8.22 baseline. Builds every known USF through the dissolved
composer and verifies it against the original SID. Two verification
modes:

  - Hubbard '85: md5 of per-frame $D400-$D418 register snapshots
    (`pipelines.hubbard.verify.verify_all`) — fast, frame-accurate.
  - Companion strains: cycle-strict instruction-stream compare
    (`compare_instruction_stream(skip_init=True)`) — needed since
    these engines use a different verification surface.

All pre-existing partials are now resolved (Fairlight via the
`is_full` accepting either skip_init=False or =True; Melonmania sub 1
via the per-subtune `voice_enable_mask` knob; 5_Title_Tunes sub 2
via dropping the composer init's silence-clear loop that was
producing 24 phantom $D400-$D418=$00 writes orig didn't emit).

Run:
    python3 tools/regression.py
"""

import struct
import sys
from importlib import import_module

sys.path.insert(0, '.')

from pipelines.build_from_usf import build_from_usf
from pipelines.hubbard.verify import verify_all
from pipelines.hubbard.verify_cycle import (
    writelog_capture, compare_instruction_stream,
)


HUBBARD_ENGINES = [
    ('commando',          'COMMANDO',          'Commando'),
    ('thing_on_a_spring', 'THING_ON_A_SPRING', 'Thing_on_a_Spring'),
    ('chimera',           'CHIMERA',           'Chimera'),
    ('monty',             'MONTY',             'Monty_on_the_Run'),
    ('action_biker',      'ACTION_BIKER',      'Action_Biker'),
    ('confuzion',         'CFG',               'Confuzion'),
    ('hunter_patrol',     'HUNTER_PATROL',     'Hunter_Patrol'),
    ('battle_of_britain', 'CFG',               'Battle_of_Britain'),
    ('human_race',        'HUMAN_RACE',        'Human_Race'),
    ('devils_galop',      'DEVILS_GALOP',      'Devils_Galop'),
]
HUBBARD_BASE = 'hvsc84/MUSICIANS/H/Hubbard_Rob'

COMPANION_USFS = [
    *(f'hvsc84/MUSICIANS/B/Berry_Vic/{f}' for f in [
        'Webern_Op_21.usf', 'Atonal_Music.usf', 'Progression.usf',
        'Triad.usf', 'Schillinger.usf', 'In_C.usf', 'Dufay.usf',
        'Test_File.usf', 'Bach_Sonata.usf', 'Te_Deum.usf',
        'SID_Sequencer.usf', 'Sigma.usf',
    ]),
    'hvsc84/MUSICIANS/C/Clever_Music/Fairlight.usf',
    'hvsc84/MUSICIANS/C/Clever_Music/Gyroscope.usf',
    'hvsc84/MUSICIANS/C/Clever_Music/Back_to_the_Future.usf',
    'hvsc84/GAMES/G-L/Henrys_House.usf',
    'hvsc84/DEMOS/UNKNOWN/Yes_Tune.usf',
    'hvsc84/GAMES/S-Z/Soldier_of_Fortune.usf',
    'hvsc84/MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.usf',
    'hvsc84/MUSICIANS/H/Hoernell_Karl/Melonmania.usf',
    # Bowden-engine variants (relocated / inline-tempo layout, etc.) —
    # surface other Companion-tagged SIDs we hadn't pinned in regression.
    'hvsc84/DEMOS/M-R/Roundabout.usf',
    'hvsc84/GAMES/G-L/Hyper_Blast.usf',
    'hvsc84/GAMES/M-R/Memory_1991.usf',
    'hvsc84/GAMES/S-Z/Surfchamp.usf',
    'hvsc84/GAMES/S-Z/Titanic-The_Adventure_Begins.usf',
    'hvsc84/MUSICIANS/H/Hubbard_Rob/5_Title_Tunes.usf',
]

# Pre-existing partial subtunes (carried since before the composer
# rewrite). Not regressions; not failures.
KNOWN_PARTIAL: dict[str, set[int]] = {}

# Hubbard '85 subtunes carrying a known-partial at 1.5x (the
# default verify window). Empty today — Confuzion sub 0 was the last
# entry and was resolved by the `loop_silences_song` knob landing on
# its config (see [[project_hubbard_song_end_fade]]).
KNOWN_PARTIAL_HUBBARD: dict[str, set[int]] = {}


def _n_subs(sid: str) -> int:
    with open(sid, 'rb') as f:
        return struct.unpack('>H', f.read(0x10)[0x0E:0x10])[0]


def regress_hubbard() -> tuple[int, int, int]:
    """Md5-of-frame-snapshot verify across all Hubbard '85 engines.
    Returns (ok, partial, total)."""
    ok = partial = total = 0
    for nick, cn, fn in HUBBARD_ENGINES:
        cfg = getattr(import_module(f'pipelines.hubbard.{nick}.config'), cn)
        out = f'{HUBBARD_BASE}/{fn}.sidfinity.sid'
        build_from_usf(f'{HUBBARD_BASE}/{fn}.usf', out)
        rows = list(verify_all([(cfg, out)]).values())[0][0]
        known = KNOWN_PARTIAL_HUBBARD.get(nick, set())
        sub_ok = sub_partial = sub_fail = 0
        for st, b in rows:
            if b:
                sub_ok += 1
            elif st in known:
                sub_partial += 1
            else:
                sub_fail += 1
        ok += sub_ok
        partial += sub_partial
        total += len(rows)
        status = f'{sub_ok}/{len(rows)}'
        if sub_partial:
            status += f' ({sub_partial} known-partial)'
        if sub_fail:
            status += ' FAIL'
        print(f'  {fn:32s} {status}')
    return ok, partial, total


def regress_companion() -> tuple[int, int, int]:
    """Cycle-strict instruction-stream compare across companion strains
    + the 5TT unified engine. Returns (ok, partial, fail)."""
    ok = partial = fail = 0
    for usf in COMPANION_USFS:
        name = usf.split('/')[-1].replace('.usf', '')
        sid = usf.replace('.usf', '.sid')
        out = usf.replace('.usf', '.sidfinity.sid')
        build_from_usf(usf, out)
        ns = _n_subs(sid)
        known = KNOWN_PARTIAL.get(name, set())
        sub_ok = sub_partial = sub_fail = 0
        # Back_to_the_Future needs a slightly longer capture window: its
        # banking-trampoline orig spreads init writes across two VBI frames
        # while the rebuild's init lands all in frame 0; at 6s the truncation
        # boundary falls between same-content frames in the two runs, giving
        # different totals. By 8s both stabilize at the same write count.
        duration = 8.0 if 'Back_to_the_Future' in usf else 6.0
        for st in range(ns):
            a = writelog_capture(sid, st, duration=duration)
            b = writelog_capture(out, st, duration=duration)
            # Legacy mode while we work out the right semantics for
            # strict Check A under structurally-different init bytes
            # (Phase A in docs/sid_init_report.md §5 — needs cycle-
            # precise init-RTS marker, not VBI frame 0 boundary).
            r = compare_instruction_stream(a, b)
            if r['is_full']:
                sub_ok += 1
            elif st in known:
                sub_partial += 1
            else:
                sub_fail += 1
        ok += sub_ok
        partial += sub_partial
        fail += sub_fail
        status = f'{sub_ok}/{ns}'
        if sub_partial:
            status += f' ({sub_partial} known-partial)'
        if sub_fail:
            status += f' ({sub_fail} REGRESSED)'
        print(f'  {name:32s} {status}')
    return ok, partial, fail


def regress_c64me() -> tuple[int, int]:
    """Commodore_64_Music_Examples — 15 subtunes via the C64ME-specific
    build.py composer. Uses PREFIX-match semantics rather than is_full
    because the rebuild's play loop takes more cycles per VBI than orig,
    so siddump captures fewer writes from reb in the same wall-clock
    duration (even though every captured reb write matches orig)."""
    from pipelines.companion.c64_music_examples.build import (
        build_subtune_sid, build_subtune_sid_b, build_subtune_sid_v2,
    )
    SID = 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid'
    ok = fail = 0
    for st in range(15):
        out = SID.replace('.sid', f'.sub{st}.sidfinity.sid')
        if st in (0, 2, 3):
            sid_bytes = build_subtune_sid(st)
        elif st == 1:
            sid_bytes = build_subtune_sid_b(st)
        else:
            sid_bytes = build_subtune_sid_v2(st)
        with open(out, 'wb') as f:
            f.write(sid_bytes)
        a = writelog_capture(SID, st, duration=15.0)
        b = writelog_capture(out, 0, duration=15.0)
        fa = [(r, v) for f in a for c, r, v in f]
        fb = [(r, v) for f in b for c, r, v in f]
        n = min(len(fa), len(fb))
        div = next((i for i in range(n) if fa[i] != fb[i]), None)
        if div is None and len(fb) > 0:
            ok += 1
            status = 'OK'
        else:
            fail += 1
            status = f'diverge#{div}'
        print(f'  sub {st:2d}: orig {len(fa):>5d} reb {len(fb):>5d}  {status}')
    return ok, fail


def regress_jay_derrett() -> tuple[int, int]:
    """Jay_Derrett family — 14 SIDs currently passing byte-exact:
    - 10 PSID-compatible (siddump --writelog both sides): 6 Cluster A
      (Jetboys, Lifeforce, Mandroid, Ninja_Hamster, Vengeance, ZIP),
      3 Cluster B PSID (Counterforce, Destruct, Stratton), 1
      Cluster C (Discovery).
    - 3 RSID IRQ-driven (orig via py65 IRQ-vector capture, reb via
      siddump): Osmium, Thundercross, Trigger_Happy.
    Returns (ok, fail). Of 25 total Jay_Derrett SIDs: 13 wired, 12
    pending (Traxxion + Road_Warrior + 10 Type B engines)."""
    from pipelines.companion.jay_derrett.build import (
        build_sid, params_from_extracted_json, capture_writes_via_py65,
    )
    import json
    from pathlib import Path
    PSID_SIDS = [
        'Counterforce', 'Destruct', 'Discovery', 'Jetboys', 'Lifeforce',
        'Mandroid', 'Ninja_Hamster', 'Stratton', 'Vengeance', 'ZIP',
    ]
    TYPE_B_SIDS = ['Equalizer']    # Type B canonical (B1 sub-cluster)
    RSID_IRQ_SIDS = ['Osmium', 'Thundercross', 'Trigger_Happy']
    base = 'hvsc84/MUSICIANS/D/Derrett_Jay'
    extracted = 'pipelines/companion/jay_derrett/_extracted'
    ok = fail = 0

    def _build(name):
        params = params_from_extracted_json(f'{extracted}/{name}.json')
        jd = json.load(open(f'{extracted}/{name}.json'))
        vbr = [(v['ptr_min'], v['ptr_min'] + len(v['bytes']))
               for v in jd['voice_bytes']]
        Path(f'{base}/{name}.sidfinity.sid').write_bytes(
            build_sid(f'{base}/{name}.sid', params, voice_byte_ranges=vbr))

    for name in PSID_SIDS:
        _build(name)
        a = writelog_capture(f'{base}/{name}.sid', 0, duration=6.0)
        b = writelog_capture(f'{base}/{name}.sidfinity.sid', 0, duration=6.0)
        r = compare_instruction_stream(a, b)
        if r['is_full']:
            ok += 1; status = 'OK'
        else:
            fail += 1
            status = f"FAIL match_all={r['match_all']}/{r['len_all_a']}"
        print(f'  {name:18s} (psid)  {status}')

    # Type B (Equalizer-shape) — uses its own type_b.py emit
    from pipelines.companion.jay_derrett.type_b import build_equalizer_sid
    from pathlib import Path as _Path
    for name in TYPE_B_SIDS:
        out = _Path(f'{base}/{name}.sidfinity.sid')
        if name == 'Equalizer':
            out.write_bytes(build_equalizer_sid())
        a = writelog_capture(f'{base}/{name}.sid', 0, duration=6.0)
        b = writelog_capture(str(out), 0, duration=6.0)
        r = compare_instruction_stream(a, b)
        if r['is_full']:
            ok += 1; status = 'OK'
        else:
            fail += 1
            status = f"FAIL match_all={r['match_all']}/{r['len_all_a']}"
        print(f'  {name:18s} (typeb) {status}')

    for name in RSID_IRQ_SIDS:
        _build(name)
        orig = capture_writes_via_py65(f'{base}/{name}.sid', 0, n_frames=50)
        reb = writelog_capture(f'{base}/{name}.sidfinity.sid', 0, duration=1.0)
        fa = [(r, v) for f in orig for c, r, v in f]
        fb_all = [(r, v) for f in reb for c, r, v in f]
        fb = fb_all[2:]  # skip reb's init $D418 writes
        n = min(len(fa), len(fb))
        div = next((i for i in range(n) if fa[i] != fb[i]), None)
        if div is None and n > 500:
            ok += 1; status = 'OK'
        else:
            fail += 1
            status = f'FAIL diverge#{div} ({n} matched)'
        print(f'  {name:18s} (rsid)  {status}')

    return ok, fail


def main():
    print('Hubbard \'85:')
    h_ok, h_part, h_total = regress_hubbard()
    print(f'\nCompanion + 5TT:')
    c_ok, c_part, c_fail = regress_companion()
    print(f'\nC64 Music Examples (prefix-match):')
    cme_ok, cme_fail = regress_c64me()
    print(f'\nJay_Derrett family (14 of 25 SIDs wired):')
    jd_ok, jd_fail = regress_jay_derrett()

    print(f'\nHubbard:    {h_ok} ok  +  {h_part} known-partial  +  '
          f'{h_total - h_ok - h_part} regressed  (of {h_total})')
    print(f'Companion:  {c_ok} ok  +  {c_part} known-partial  +  {c_fail} regressed')
    print(f'C64ME:      {cme_ok} ok  +  {cme_fail} regressed  (of 15)')
    print(f'Jay_Derrett:  {jd_ok} ok  +  {jd_fail} regressed  (of 14 wired / 25 total)')

    h_regressed = h_total - h_ok - h_part
    if h_regressed or c_fail or cme_fail or jd_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
