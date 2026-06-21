"""Full pipeline regression — Hubbard '85 + companion + FC + DMC families.

Builds every canary/portfolio member through the composer and verifies it
against the original SID's write-log. Verification surfaces per family:

  - Hubbard '85: `pipelines.hubbard.verify.verify_all` (write-log overlap).
  - Companion strains + 5TT: `compare_instruction_stream` (cycle-strict).
  - C64ME / Jay_Derrett: prefix / instruction-stream compares.
  - FC + DMC: `verify_featuredriven` / `verify_dmc` (trichotomy).

PARALLEL: every per-member verify is an independent task (build to a distinct
path + capture + compare); they run across a Pool(8) — the same pool-safety the
family batch tools (fc_family_batch / dmc_family_batch) already rely on. Tasks
return structured results; the main process prints them grouped per family in
the original order and aggregates the verdict. Set REGRESSION_JOBS=1 to force
sequential (debugging).

Run:
    python3 tools/regression.py
"""

import os
import struct
import sys
from multiprocessing import Pool

sys.path.insert(0, '.')


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
    'hvsc84/DEMOS/M-R/Roundabout.usf',
    'hvsc84/GAMES/G-L/Hyper_Blast.usf',
    'hvsc84/GAMES/M-R/Memory_1991.usf',
    'hvsc84/GAMES/S-Z/Surfchamp.usf',
    'hvsc84/GAMES/S-Z/Titanic-The_Adventure_Begins.usf',
    'hvsc84/MUSICIANS/H/Hubbard_Rob/5_Title_Tunes.usf',
]

# Pre-existing partial subtunes (carried since before the composer rewrite).
KNOWN_PARTIAL: dict[str, set[int]] = {}
KNOWN_PARTIAL_HUBBARD: dict[str, set[int]] = {}


def _n_subs(sid: str) -> int:
    with open(sid, 'rb') as f:
        return struct.unpack('>H', f.read(0x10)[0x0E:0x10])[0]


# --------------------------------------------------------------------------
# Per-family workers — each returns a result dict:
#   {family, group?, line, ok, partial, fail, total}
# (counts in the family's NATIVE aggregation unit, matching the old summary).
# --------------------------------------------------------------------------

def _w_hubbard(nick: str, cn: str, fn: str) -> dict:
    from importlib import import_module
    from pipelines.build_from_usf import build_from_usf
    from pipelines.hubbard.verify import verify_all
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
    status = f'{sub_ok}/{len(rows)}'
    if sub_partial:
        status += f' ({sub_partial} known-partial)'
    if sub_fail:
        status += ' FAIL'
    return {'family': 'Hubbard', 'line': f'  {fn:32s} {status}',
            'ok': sub_ok, 'partial': sub_partial, 'fail': sub_fail,
            'total': len(rows)}


def _w_companion(usf: str) -> dict:
    from pipelines.build_from_usf import build_from_usf
    from pipelines.hubbard.verify_cycle import (
        writelog_capture, compare_instruction_stream)
    name = usf.split('/')[-1].replace('.usf', '')
    sid = usf.replace('.usf', '.sid')
    out = usf.replace('.usf', '.sidfinity.sid')
    build_from_usf(usf, out)
    ns = _n_subs(sid)
    known = KNOWN_PARTIAL.get(name, set())
    sub_ok = sub_partial = sub_fail = 0
    duration = 8.0 if 'Back_to_the_Future' in usf else 6.0
    for st in range(ns):
        a = writelog_capture(sid, st, duration=duration)
        b = writelog_capture(out, st, duration=duration)
        r = compare_instruction_stream(a, b)
        if r['is_full']:
            sub_ok += 1
        elif st in known:
            sub_partial += 1
        else:
            sub_fail += 1
    status = f'{sub_ok}/{ns}'
    if sub_partial:
        status += f' ({sub_partial} known-partial)'
    if sub_fail:
        status += f' ({sub_fail} REGRESSED)'
    return {'family': 'Companion', 'line': f'  {name:32s} {status}',
            'ok': sub_ok, 'partial': sub_partial, 'fail': sub_fail,
            'total': ns}


def _w_c64me(st: int) -> dict:
    from pipelines.hubbard.verify_cycle import writelog_capture
    from pipelines.companion.c64_music_examples.build import (
        build_subtune_sid, build_subtune_sid_b, build_subtune_sid_v2)
    SID = 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid'
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
    ok = div is None and len(fb) > 0
    status = 'OK' if ok else f'diverge#{div}'
    return {'family': 'C64ME',
            'line': f'  sub {st:2d}: orig {len(fa):>5d} reb {len(fb):>5d}  {status}',
            'ok': int(ok), 'partial': 0, 'fail': int(not ok), 'total': 1}


def _w_jd(kind: str, name: str) -> dict:
    """Jay_Derrett — kind in {psid, typeb, rsid}."""
    import json
    from pathlib import Path
    from pipelines.hubbard.verify_cycle import (
        writelog_capture, compare_instruction_stream)
    base = 'hvsc84/MUSICIANS/D/Derrett_Jay'
    extracted = 'pipelines/companion/jay_derrett/_extracted'

    def _build(nm):
        from pipelines.companion.jay_derrett.build import (
            build_sid, params_from_extracted_json)
        params = params_from_extracted_json(f'{extracted}/{nm}.json')
        jd = json.load(open(f'{extracted}/{nm}.json'))
        vbr = [(v['ptr_min'], v['ptr_min'] + len(v['bytes']))
               for v in jd['voice_bytes']]
        Path(f'{base}/{nm}.sidfinity.sid').write_bytes(
            build_sid(f'{base}/{nm}.sid', params, voice_byte_ranges=vbr))

    if kind == 'psid':
        _build(name)
        a = writelog_capture(f'{base}/{name}.sid', 0, duration=6.0)
        b = writelog_capture(f'{base}/{name}.sidfinity.sid', 0, duration=6.0)
        r = compare_instruction_stream(a, b)
        ok = r['is_full']
        status = 'OK' if ok else f"FAIL match_all={r['match_all']}/{r['len_all_a']}"
        tag = 'psid'
    elif kind == 'typeb':
        from pipelines.companion.jay_derrett.type_b import build_type_b_sid
        out = Path(f'{base}/{name}.sidfinity.sid')
        out.write_bytes(build_type_b_sid(name))
        a = writelog_capture(f'{base}/{name}.sid', 0, duration=6.0)
        b = writelog_capture(str(out), 0, duration=6.0)
        r = compare_instruction_stream(a, b)
        if name == 'Dracula':            # CIA-driven → prefix-match
            ok = r['match_all'] == r['len_all_a']
            detail = (f"match_all={r['match_all']}/{r['len_all_a']} "
                      f"(prefix; reb_extras={r['len_all_b'] - r['match_all']})")
        else:
            ok = r['is_full']
            detail = f"match_all={r['match_all']}/{r['len_all_a']}"
        status = 'OK' if ok else f'FAIL {detail}'
        tag = 'typeb'
    else:  # rsid
        from pipelines.companion.jay_derrett.build import (
            capture_writes_via_py65)
        _build(name)
        orig = capture_writes_via_py65(f'{base}/{name}.sid', 0, n_frames=50)
        reb = writelog_capture(f'{base}/{name}.sidfinity.sid', 0, duration=1.0)
        fa = [(r, v) for f in orig for c, r, v in f]
        fb = [(r, v) for f in reb for c, r, v in f][2:]  # skip reb init $D418
        n = min(len(fa), len(fb))
        div = next((i for i in range(n) if fa[i] != fb[i]), None)
        ok = div is None and n > 500
        status = 'OK' if ok else f'FAIL diverge#{div} ({n} matched)'
        tag = 'rsid'
    return {'family': 'Jay_Derrett',
            'line': f'  {name:18s} ({tag})  {status}',
            'ok': int(ok), 'partial': 0, 'fail': int(not ok), 'total': 1}


def _w_fc_canary(modpath: str, attr: str, name: str, subtunes) -> dict:
    from importlib import import_module
    from pipelines.future_composer.verify import verify_featuredriven
    cfg = getattr(import_module(modpath), attr)
    result = verify_featuredriven(cfg, subtunes=subtunes)
    subs = result['subtunes']
    sub_ok = sum(1 for v in subs.values() if v['is_full'])
    sub_fail = len(subs) - sub_ok
    status = f'{sub_ok}/{len(subs)}'
    if sub_fail:
        status += f' ({sub_fail} REGRESSED)'
    return {'family': 'FC', 'line': f'  {name:18s} {status}',
            'ok': sub_ok, 'partial': 0, 'fail': sub_fail, 'total': len(subs)}


def _w_fc_portfolio(sid: str) -> dict:
    from pipelines.future_composer.verify import verify_featuredriven
    from pipelines.future_composer.standard.config import fc_standard_config
    result = verify_featuredriven(fc_standard_config('hvsc84/' + sid))
    subs = result['subtunes']
    sub_ok = sum(1 for v in subs.values() if v['is_full'])
    sub_fail = len(subs) - sub_ok
    status = f'{sub_ok}/{len(subs)}'
    if sub_fail:
        status += f' ({sub_fail} REGRESSED)'
    return {'family': 'FC', 'group': 'FC-standard portfolio (feature-cover of '
            'the verified family):',
            'line': f'  {sid.split("/")[-1][:18]:18s} {status}',
            'ok': sub_ok, 'partial': 0, 'fail': sub_fail, 'total': len(subs)}


def _w_dmc(label: str, kind: str, ref: str, group: str | None) -> dict:
    """DMC — kind 'zaks' (module attr ref) or 'cfg' (sid for dmc_v4_config)."""
    from pipelines.dmc.verify import verify_dmc
    if kind == 'zaks':
        from pipelines.dmc.v4.config import ZAKS
        cfg = ZAKS
    else:
        from pipelines.dmc.v4.factory import dmc_v4_config
        cfg = dmc_v4_config(ref)
    r = verify_dmc(cfg)
    n_ok = sum(1 for s in r['subtunes'].values() if s['is_full'])
    n = len(r['subtunes'])
    status = f'{n_ok}/{n}'
    if not r['ok']:
        status += ' (REGRESSED)'
    res = {'family': 'DMC', 'line': f'  {label:24s} {status}',
           'ok': int(r['ok']), 'partial': 0, 'fail': int(not r['ok']),
           'total': 1}
    if group:
        res['group'] = group
    return res


# --------------------------------------------------------------------------
# Task dispatch (picklable: top-level fn + plain-data args)
# --------------------------------------------------------------------------

_WORKERS = {
    'hubbard': _w_hubbard, 'companion': _w_companion, 'c64me': _w_c64me,
    'jd': _w_jd, 'fc_canary': _w_fc_canary, 'fc_portfolio': _w_fc_portfolio,
    'dmc': _w_dmc,
}


def _run_task(task: tuple) -> dict:
    order, kind, args = task
    res = _WORKERS[kind](*args)
    res['order'] = order
    return res


def _build_tasks() -> list:
    """Flat task list in the original print order."""
    import json
    tasks = []

    def add(kind, *args):
        tasks.append((len(tasks), kind, args))

    for nick, cn, fn in HUBBARD_ENGINES:
        add('hubbard', nick, cn, fn)
    for usf in COMPANION_USFS:
        add('companion', usf)
    for st in range(15):
        add('c64me', st)
    for nm in ('Counterforce', 'Destruct', 'Discovery', 'Jetboys', 'Lifeforce',
               'Mandroid', 'Ninja_Hamster', 'Stratton', 'Vengeance', 'ZIP'):
        add('jd', 'psid', nm)
    for nm in ('Equalizer', 'Death_or_Glory', 'Sqij', 'Dracula'):
        add('jd', 'typeb', nm)
    for nm in ('Osmium', 'Thundercross', 'Trigger_Happy'):
        add('jd', 'rsid', nm)
    fc = 'pipelines.future_composer'
    add('fc_canary', f'{fc}.cybernoid_ii.config', 'CYBERNOID_II', 'Cybernoid_II', None)
    add('fc_canary', f'{fc}.hawkeye.config', 'HAWKEYE', 'Hawkeye', None)
    add('fc_canary', f'{fc}.adrenalin.config', 'ADRENALIN', 'Adrenalin[0]', [0])
    add('fc_canary', f'{fc}.standard.config', 'FC_STANDARD', 'Jarre_2', None)
    pf = os.path.join(os.path.dirname(__file__), 'fc_regression_portfolio.json')
    if os.path.exists(pf):
        for sid in json.load(open(pf))['portfolio']:
            add('fc_portfolio', sid)
    add('dmc', 'Geometrical_Zaks', 'zaks', '', None)
    dpf = os.path.join(os.path.dirname(__file__), 'dmc_regression_portfolio.json')
    if os.path.exists(dpf):
        grp = 'DMC v4 portfolio (feature-cover of the verified family):'
        for sid in json.load(open(dpf))['portfolio']:
            add('dmc', sid.split('/')[-1][:24], 'cfg', sid, grp)
    grp2 = 'DMC family-2 canaries (variant cover):'
    for sid in ('DEMOS/G-L/Kajun_Klog.sid',
                'MUSICIANS/A/Albartus_Jan/Lameness.sid',
                'MUSICIANS/B/Bakewell_Dwayne/Fury.sid',
                'MUSICIANS/M/MAC2/Bells_Are_Sounding.sid'):
        add('dmc', sid.split('/')[-1][:24], 'cfg', sid, grp2)
    return tasks


# Family print order + headers.
_FAMILY_ORDER = [
    ('Hubbard', "Hubbard '85:"),
    ('Companion', 'Companion + 5TT:'),
    ('C64ME', 'C64 Music Examples (prefix-match):'),
    ('Jay_Derrett', 'Jay_Derrett family (17 of 20 SIDs wired):'),
    ('FC', 'Future Composer family (4 canaries: Cyb II + Hawkeye + '
           'Adrenalin[0] + Jarre_2/standard):'),
    ('DMC', 'DMC family (canary: Geometrical_Zaks/v4):'),
]


def main():
    # The per-task builds run in parallel; suppress the per-build hvsc84.csv
    # write-through (a full-CSV rewrite — racy under Pool). Regression is a
    # verification gate, not a record step, so it never needs to touch the CSV.
    os.environ['SIDFINITY_NO_DB_WRITE'] = '1'
    tasks = _build_tasks()
    jobs = int(os.environ.get('REGRESSION_JOBS', '8'))
    n = len(tasks)
    print(f'Regression: {n} tasks across {jobs} workers '
          f'(live progress in completion order)\n', flush=True)

    def _tick(i, r):
        mark = 'ok' if not r['fail'] else 'FAIL'
        label = r['line'].strip().split('  ')[0][:28]
        print(f'  [{i:>2}/{n}] {mark:>4}  {label}', flush=True)

    results = []
    if jobs <= 1:
        for i, t in enumerate(tasks, 1):
            r = _run_task(t); results.append(r); _tick(i, r)
    else:
        with Pool(jobs) as pool:
            for i, r in enumerate(pool.imap_unordered(_run_task, tasks), 1):
                results.append(r); _tick(i, r)
    print()
    results.sort(key=lambda r: r['order'])

    agg = {}            # family -> [ok, partial, fail, total]
    for fam, header in _FAMILY_ORDER:
        print(header)
        seen_groups = set()
        a = [0, 0, 0, 0]
        for r in results:
            if r['family'] != fam:
                continue
            if r.get('group') and r['group'] not in seen_groups:
                seen_groups.add(r['group'])
                print(r['group'])
            print(r['line'])
            a[0] += r['ok']; a[1] += r['partial']
            a[2] += r['fail']; a[3] += r['total']
        agg[fam] = a
        print()

    h_ok, h_part, _, h_total = agg['Hubbard']
    h_reg = h_total - h_ok - h_part
    c_ok, c_part, c_fail, _ = agg['Companion']
    cme_ok, _, cme_fail, _ = agg['C64ME']
    jd_ok, _, jd_fail, _ = agg['Jay_Derrett']
    fc_ok, _, fc_fail, _ = agg['FC']
    dmc_ok, _, dmc_fail, _ = agg['DMC']

    print(f'Hubbard:    {h_ok} ok  +  {h_part} known-partial  +  '
          f'{h_reg} regressed  (of {h_total})')
    print(f'Companion:  {c_ok} ok  +  {c_part} known-partial  +  {c_fail} regressed')
    print(f'C64ME:      {cme_ok} ok  +  {cme_fail} regressed  (of 15)')
    print(f'Jay_Derrett:  {jd_ok} ok  +  {jd_fail} regressed  (of 17 wired / 20 total)')
    print(f'FC:         {fc_ok} ok  +  {fc_fail} regressed')
    print(f'DMC:        {dmc_ok} ok  +  {dmc_fail} regressed')

    if h_reg or c_fail or cme_fail or jd_fail or fc_fail or dmc_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
