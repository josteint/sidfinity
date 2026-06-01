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
        for st in range(ns):
            a = writelog_capture(sid, st, duration=6.0)
            b = writelog_capture(out, st, duration=6.0)
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


def main():
    print('Hubbard \'85:')
    h_ok, h_part, h_total = regress_hubbard()
    print(f'\nCompanion + 5TT:')
    c_ok, c_part, c_fail = regress_companion()

    print(f'\nHubbard:    {h_ok} ok  +  {h_part} known-partial  +  '
          f'{h_total - h_ok - h_part} regressed  (of {h_total})')
    print(f'Companion:  {c_ok} ok  +  {c_part} known-partial  +  {c_fail} regressed')

    h_regressed = h_total - h_ok - h_part
    if h_regressed or c_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
