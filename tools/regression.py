"""Full pipeline regression — Hubbard '85 + companion + FC + DMC families.

Builds every canary/portfolio member through the composer and verifies it
against the original SID's write-log. Verification surfaces per family:

  - Hubbard '85: `pipelines.hubbard.verify.verify_all` (write-log overlap).
  - Companion strains + 5TT: `compare_instruction_stream` (cycle-strict).
  - C64ME / Jay_Derrett: prefix / instruction-stream compares.
  - FC + DMC: `verify_featuredriven` / `verify_dmc` (trichotomy).

PARALLEL: every per-member verify is an independent task (build to a distinct
path + capture + compare); they run across a pool sized by `src.jobs`
(all available CPUs, capped at the task count) — the same pool-safety the
family batch tools (fc_family_batch / dmc_family_batch) already rely on. Tasks
return structured results; the main process prints them grouped per family in
the original order and aggregates the verdict. Set REGRESSION_JOBS=1 to force
sequential (debugging), or REGRESSION_JOBS=N / SIDFINITY_JOBS=N to pin width.

Run:
    python3 tools/regression.py
"""

import os
import struct
import sys
from multiprocessing import Pool

sys.path.insert(0, '.')

from src.jobs import default_jobs


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
HUBBARD_BASE = 'hvsc85/MUSICIANS/H/Hubbard_Rob'

COMPANION_USFS = [
    *(f'hvsc85/MUSICIANS/B/Berry_Vic/{f}' for f in [
        'Webern_Op_21.usf', 'Atonal_Music.usf', 'Progression.usf',
        'Triad.usf', 'Schillinger.usf', 'In_C.usf', 'Dufay.usf',
        'Test_File.usf', 'Bach_Sonata.usf', 'Te_Deum.usf',
        'SID_Sequencer.usf', 'Sigma.usf',
    ]),
    'hvsc85/MUSICIANS/C/Clever_Music/Fairlight.usf',
    'hvsc85/MUSICIANS/C/Clever_Music/Gyroscope.usf',
    'hvsc85/MUSICIANS/C/Clever_Music/Back_to_the_Future.usf',
    'hvsc85/GAMES/G-L/Henrys_House.usf',
    'hvsc85/DEMOS/UNKNOWN/Yes_Tune.usf',
    'hvsc85/GAMES/S-Z/Soldier_of_Fortune.usf',
    'hvsc85/MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.usf',
    'hvsc85/MUSICIANS/H/Hoernell_Karl/Melonmania.usf',
    'hvsc85/DEMOS/M-R/Roundabout.usf',
    'hvsc85/GAMES/G-L/Hyper_Blast.usf',
    'hvsc85/GAMES/M-R/Memory_1991.usf',
    'hvsc85/GAMES/S-Z/Surfchamp.usf',
    'hvsc85/GAMES/S-Z/Titanic-The_Adventure_Begins.usf',
    'hvsc85/MUSICIANS/H/Hubbard_Rob/5_Title_Tunes.usf',
]

# Pre-existing partial subtunes (carried since before the composer rewrite).
KNOWN_PARTIAL: dict[str, set[int]] = {}
KNOWN_PARTIAL_HUBBARD: dict[str, set[int]] = {}

# Jay_Derrett RSID members whose rebuild reproduces the IRQ-driven MUSIC but
# not the main-loop $D418 volume-register DIGI. Not a regression — a gap that
# was always there and is only now visible: the verdict used to capture the
# original with py65, which follows the IRQ handler only and is structurally
# blind to main-loop writes. On these two that digi is ~97% of everything the
# chip receives (Trigger_Happy: 29,053 of 29,671 writes; Thundercross: 37,194
# of 37,893) and the rebuild emits 2. Filtering $D418, py65 and siddump agree
# on the music exactly, so the two capture methods never disagreed — py65
# simply saw less. Osmium has no digi and matches 708/708.
# Removing them from this set is the definition of "the digi is modelled".
KNOWN_PARTIAL_JD: set[str] = {'Trigger_Happy', 'Thundercross'}


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
    # jobs=1: we are already inside a regression Pool worker, and Pool workers
    # are daemonic — an inner Pool would die with "daemonic processes are not
    # allowed to have children" on any cache miss. The outer pool is the
    # parallelism. See src/jobs.py.
    rows = list(verify_all([(cfg, out)], jobs=1).values())[0][0]
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
    SID = 'hvsc85/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid'
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
    base = 'hvsc85/MUSICIANS/D/Derrett_Jay'
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
        # The ORIGINAL is captured with siddump --force-rsid, not py65. These
        # are RSID tunes with play=$0000 that install their own IRQ handler at
        # $0314; plain siddump sees 0 writes (which is why py65 was used here),
        # but --force-rsid runs the real RSID environment and captures the true
        # stream — ~100x faster (10.3s -> 0.1s) and, unlike py65, it sees
        # main-loop writes too. See KNOWN_PARTIAL_JD for what that exposed.
        #
        # Both sides are now captured the same way, so this uses the project's
        # standard comparator instead of the old hand-rolled prefix walk (which
        # sliced [2:] off the rebuild to paper over the mismatched init).
        _build(name)
        a = writelog_capture(f'{base}/{name}.sid', 0, duration=1.0,
                             force_rsid=True)
        b = writelog_capture(f'{base}/{name}.sidfinity.sid', 0, duration=1.0)
        r = compare_instruction_stream(a, b)
        ok = r['is_full']
        detail = (f"match_all={r['match_all']}/{r['len_all_a']} "
                  f"reb_len={r['len_all_b']}")
        if not ok and name in KNOWN_PARTIAL_JD:
            return {'family': 'Jay_Derrett',
                    'line': f'  {name:18s} (rsid)  KNOWN-PARTIAL '
                            f'(main-loop $D418 digi not modelled) {detail}',
                    'ok': 0, 'partial': 1, 'fail': 0, 'total': 1}
        status = 'OK' if ok else f'FAIL {detail}'
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
    result = verify_featuredriven(fc_standard_config('hvsc85/' + sid))
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


def _w_masm(sid: str, group: str | None) -> dict:
    """Music Assembler — the FULL round trip, SID -> USF -> SID, so a green
    portfolio member proves its stored USF really specifies the music."""
    import tempfile
    from pipelines.music_assembler.extract.model import extract
    from pipelines.music_assembler.extract.to_usf import model_to_usf
    from pipelines.music_assembler.from_usf import build_masm_sid
    from pipelines.music_assembler.verify import verify
    from src.usf.parser import parse_file
    from src.usf.writer import write_file
    td = tempfile.mkdtemp()
    up = os.path.join(td, 'a.usf')
    write_file(model_to_usf(extract(sid)), up)
    out = os.path.join(td, 'a.sid')
    with open(out, 'wb') as f:
        f.write(build_masm_sid(parse_file(up)))
    r = verify(sid, out)
    ok = 1 if r.get('is_full') else 0
    return {'family': 'Music_Assembler',
            'group': group or 'Music_Assembler portfolio '
                              '(feature-cover of the verified family):',
            'line': '  %-24s %s' % (sid.split('/')[-1][:24],
                                    'FULL' if ok else 'REGRESSED'),
            'ok': ok, 'partial': 0, 'fail': 1 - ok, 'total': 1}


def _w_masm_hetero(_unused: str, group: str | None) -> dict:
    """Freespace_2075 — the DMC + Music Assembler heterogeneous member
    (ledger C31). Its subtunes 1-2 are MA players, so MA composer changes can
    break it, but it is DMC-CLASSIFIED and therefore invisible to the MA
    family batch. Cross-family canary; corpus ownership stays with DMC f1."""
    import tempfile
    from pipelines.music_assembler.heterogeneous import build, FREESPACE
    from pipelines.music_assembler.verify import verify
    rel = FREESPACE
    out = os.path.join(tempfile.mkdtemp(), 'fs.sid')
    with open(out, 'wb') as f:
        f.write(build(rel))            # spec detected + observed, not hardcoded
    ok = sum(1 for s in (0, 1, 2) if verify(rel, out, subtune=s).get('is_full'))
    status = '%d/3' % ok
    if ok < 3:
        status += ' (%d REGRESSED)' % (3 - ok)
    return {'family': 'Music_Assembler',
            'group': group or '',
            'line': '  %-24s %s' % ('Freespace_2075 (DMC+MA)', status),
            'ok': ok, 'partial': 0, 'fail': 3 - ok, 'total': 3}


def _w_gtv1(sid: str, group: str | None) -> dict:
    """GoatTracker V1 — build THROUGH a written+parsed .usf, never the
    in-memory UsfFile. Building in-memory is what let V1's .usf go unreadable
    (list-valued params, `loop: -1`, its whole row-command vocabulary) with no
    check noticing, so the round trip is the thing worth guarding."""
    import tempfile
    from pipelines.goattracker.v1.extract.engine_model import parse_sid, extract
    from pipelines.goattracker.v1.extract.to_usf import model_to_usf
    from pipelines.goattracker.v1.composer import build_v1_sid
    from pipelines.hubbard.verify_cycle import writelog_capture
    from src.usf.parser import parse_file
    from src.usf.writer import write_file
    orig = os.path.join('hvsc85', sid)
    td = tempfile.mkdtemp()
    up = os.path.join(td, 'a.usf')
    write_file(model_to_usf(extract(parse_sid(orig))), up)
    out = os.path.join(td, 'a.sid')
    with open(out, 'wb') as f:
        f.write(build_v1_sid(parse_file(up)))
    dur = 30.0
    try:
        from src import sid_db
        r = sid_db.query('SELECT songlength_s FROM sids WHERE path=?', [sid])
        if r and r[0][0]:
            dur = max(8.0, float(r[0][0]) * 1.1)
    except Exception:
        pass

    def flat(fr):
        return [(w[1], w[2]) for f in fr[1:] for w in f]
    a = flat(writelog_capture(orig, 0, duration=dur))
    b = flat(writelog_capture(out, 0, duration=dur))
    n = min(len(a), len(b))
    first = next((i for i in range(n) if a[i] != b[i]), None)
    ok = 1 if (first is None and len(a) == len(b)) else 0
    return {'family': 'GoatTracker_V1',
            'group': group or '',        # family header already says it
            'line': '  %-24s %s' % (sid.split('/')[-1][:24],
                                    'FULL' if ok else 'REGRESSED'),
            'ok': ok, 'partial': 0, 'fail': 1 - ok, 'total': 1}


def _w_dmc(label: str, kind: str, ref: str, group: str | None) -> dict:
    """DMC — kind 'zaks' (module attr ref) or 'cfg' (sid for dmc_v4_config)."""
    if kind == 'zaks':
        from pipelines.dmc.verify import verify_dmc
        from pipelines.dmc.v4.config import ZAKS
        r = verify_dmc(ZAKS)
    else:
        # CANONICAL DISPATCH, not `dmc_v4_config` — a portfolio member whose
        # real build path is a compilation must be built the way the family
        # batch builds it, else it reads as REGRESSED with sub 0 FULL and the
        # rest garbage (ledger C20 4th layer; found 2026-08-22 when the
        # re-derived portfolios pulled in Defuzion_3 + Nyaaaah_9).
        from pipelines.dmc.verify import verify_member
        r = verify_member(ref)
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


def _w_basic(sid: str, dur: float, group: str | None) -> dict:
    """Basic_Program — full SID->USF->SID round-trip of one member."""
    from pipelines.basic_program.usf_roundtrip import roundtrip
    r = roundtrip(sid, dur)
    ok = r.get('status') == 'FULL'
    status = 'FULL' if ok else r.get('status', '?')
    res = {'family': 'Basic_Program', 'line': f'  {sid.split("/")[-1][:24]:24s} {status}',
           'ok': int(ok), 'partial': 0, 'fail': int(not ok), 'total': 1}
    if group:
        res['group'] = group
    return res


# --------------------------------------------------------------------------
# Task dispatch (picklable: top-level fn + plain-data args)
# --------------------------------------------------------------------------

_WORKERS = {
    'hubbard': _w_hubbard, 'companion': _w_companion, 'c64me': _w_c64me,
    'jd': _w_jd, 'fc_canary': _w_fc_canary, 'fc_portfolio': _w_fc_portfolio,
    'dmc': _w_dmc, 'basic': _w_basic,
    'masm': _w_masm, 'masm_hetero': _w_masm_hetero, 'gtv1': _w_gtv1,
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
    # FAMILY 2 (closed 2026-08-21 at 2,924/2,924): its own derived
    # portfolio, tier-1 beside family 1's. Until this landed, all of f2 was
    # guarded by the four hand-picked canaries below — which covered none of
    # the f2 grind's levers (the vib-swell wedges, pulse_tail_hi, the $FF
    # loop immediate, filter_before_voice, the C31 dispatch wrappers).
    f2seen = set()
    f2pf = os.path.join(os.path.dirname(__file__),
                        'dmc_f2_regression_portfolio.json')
    if os.path.exists(f2pf):
        grp = 'DMC family-2 portfolio (feature-cover of the closed family):'
        for sid in json.load(open(f2pf))['portfolio']:
            f2seen.add(sid)
            add('dmc', sid.split('/')[-1][:24], 'cfg', sid, grp)
    grp2 = 'DMC family-2 canaries (variant cover):'
    for sid in ('DEMOS/G-L/Kajun_Klog.sid',
                'MUSICIANS/A/Albartus_Jan/Lameness.sid',
                'MUSICIANS/B/Bakewell_Dwayne/Fury.sid',
                'MUSICIANS/M/MAC2/Bells_Are_Sounding.sid'):
        if sid not in f2seen:            # portfolio already covers it
            add('dmc', sid.split('/')[-1][:24], 'cfg', sid, grp2)
    # ledger C29: a track $FF loop into an out-of-image ($0000) sector that
    # sonifies live zeropage — guards the libsidplayfp low-RAM overlay path.
    add('dmc', 'Centric_tune_4_v8', 'cfg',
        'MUSICIANS/P/PVCF/Worktunes/Centric_tune_4_version_8.sid',
        'DMC family-1 out-of-image loop sector (ledger C29):')
    bpf = os.path.join(os.path.dirname(__file__), 'basic_program_regression_portfolio.json')
    if os.path.exists(bpf):
        grp = 'Basic_Program portfolio (round-trip feature-cover):'
        for m in json.load(open(bpf))['portfolio']:
            add('basic', m['sid'], m['dur'], grp)
    mpf = os.path.join(os.path.dirname(__file__),
                       'masm_regression_portfolio.json')
    if os.path.exists(mpf):
        for sid in json.load(open(mpf))['portfolio']:
            add('masm', sid, None)
    # Cross-family: MA composer changes can break this DMC-owned member, and
    # the MA family batch cannot see it (it is DMC-classified).
    add('masm_hetero', '', 'DMC + Music_Assembler heterogeneous member '
                           '(ledger C31), MA-side canary:')
    # GoatTracker V1: one FULL canary per player variant, built through a
    # written+parsed .usf (the round trip, not the in-memory UsfFile).
    for sid in ('MUSICIANS/N/Ne7/Manifold_28B.sid',          # player1 tracker
                'MUSICIANS/N/Ne7/Startup.sid',
                'DEMOS/G-L/Lazy_Jones.sid',                  # player2 gamemusic
                'MUSICIANS/Z/Zynthaxx/Ob-la-di_Ob-la-da.sid'):
        add('gtv1', sid, None)
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
    ('Basic_Program', 'Basic_Program family (RSID-BASIC round-trip portfolio):'),
    ('Music_Assembler',
     'Music Assembler family (SID -> USF -> SID round-trip portfolio):'),
    ('GoatTracker_V1',
     'GoatTracker V1 (SID -> USF -> SID canaries, one per player variant):'),
]


def main():
    tasks = _build_tasks()
    jobs = default_jobs('REGRESSION_JOBS', cap=len(tasks))
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
    jd_ok, jd_part, jd_fail, _ = agg['Jay_Derrett']
    fc_ok, _, fc_fail, _ = agg['FC']
    dmc_ok, _, dmc_fail, _ = agg['DMC']
    bp_ok, _, bp_fail, _ = agg['Basic_Program']
    ma_ok, _, ma_fail, _ = agg['Music_Assembler']
    gt_ok, _, gt_fail, _ = agg['GoatTracker_V1']

    print(f'Hubbard:    {h_ok} ok  +  {h_part} known-partial  +  '
          f'{h_reg} regressed  (of {h_total})')
    print(f'Companion:  {c_ok} ok  +  {c_part} known-partial  +  {c_fail} regressed')
    print(f'C64ME:      {cme_ok} ok  +  {cme_fail} regressed  (of 15)')
    print(f'Jay_Derrett:  {jd_ok} ok  +  {jd_part} known-partial  +  '
          f'{jd_fail} regressed  (of 17 wired / 20 total)')
    print(f'FC:         {fc_ok} ok  +  {fc_fail} regressed')
    print(f'DMC:        {dmc_ok} ok  +  {dmc_fail} regressed')
    print(f'Basic_Program: {bp_ok} ok  +  {bp_fail} regressed')
    print(f'Music_Assembler: {ma_ok} ok  +  {ma_fail} regressed')
    print(f'GoatTracker_V1: {gt_ok} ok  +  {gt_fail} regressed')

    if (h_reg or c_fail or cme_fail or jd_fail or fc_fail or dmc_fail
            or bp_fail or ma_fail or gt_fail):
        sys.exit(1)


if __name__ == '__main__':
    main()
