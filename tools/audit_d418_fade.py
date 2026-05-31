"""Probe every Hubbard '85 engine for an undetected $D418 song-end fade.

Captures both the HVSC original and the rebuilt .sidfinity.sid at
2 * HVSC songlength (past the standard verify window of 1.5x), then
compares the per-frame $D418 trace. Flags any subtune where the two
traces diverge past the 1.5x verify boundary — these are master-VOL
divergences the snapshot verify window may miss when the song's
post-songlength behaviour is in scope.

Prints one row per subtune:
  ENGINE  sub  orig_d418_var  rb_d418_var  first_diff_frame  within_1.5x?  config

`config` shows the engine's current master_vol_* setup. If `subtrahend`
is None and a diff is reported past the 1.5x boundary, the fade is
likely unimplemented for that engine.

Run:
    python3 tools/audit_d418_fade.py
"""

import os
import sys
from importlib import import_module
from multiprocessing import Pool

sys.path.insert(0, '.')

# (module-name-under-pipelines.hubbard, EngineConfig var name)
ENGINES = [
    ('commando',             'COMMANDO'),
    ('thing_on_a_spring',    'THING_ON_A_SPRING'),
    ('chimera',              'CHIMERA'),
    ('monty',                'MONTY'),
    ('action_biker',         'ACTION_BIKER'),
    ('confuzion',            'CFG'),
    ('hunter_patrol',        'HUNTER_PATROL'),
    ('battle_of_britain',    'CFG'),
    ('human_race',           'HUMAN_RACE'),
    ('devils_galop',         'DEVILS_GALOP'),
    ('one_man_and_his_droid','ONE_MAN_AND_HIS_DROID'),
]

D418_OFFSET = 0x18


def _capture_d418(args):
    """Worker: capture $D418 trace for (sid, n_frames, subtune)."""
    sid, n_frames, subtune = args
    from pipelines.hubbard.inst_program import capture
    cap = capture(sid, n_frames=n_frames, subtune=subtune)
    return [snap[D418_OFFSET] for snap in cap.snapshots]


def _rebuilt_path(cfg) -> str:
    return cfg.sid_path.replace('.sid', '.sidfinity.sid')


def _config_str(cfg) -> str:
    sv = getattr(cfg, 'master_vol_subtrahend_voice', None)
    if sv is None:
        return 'subtrahend=None'
    base = getattr(cfg, 'master_vol_base', 0xA0)
    trig = getattr(cfg, 'master_vol_trigger', 'inst_change')
    return f'voice=V{sv+1} base=${base:02X} trig={trig}'


def main() -> int:
    from pipelines.hubbard.verify import subtune_frames

    # Build the work list: one job per (engine, subtune, original-or-rebuild).
    # Keyed by (engine_name, st, kind) -> args for the pool.
    jobs: dict = {}
    plan: list = []  # [(engine_name, st, cfg, win_verify, win_20)]
    skipped: list = []  # engines without a rebuild
    for nick, varname in ENGINES:
        cfg = getattr(import_module(f'pipelines.hubbard.{nick}.config'),
                      varname)
        rb = _rebuilt_path(cfg)
        if not os.path.exists(rb):
            skipped.append((cfg.name, rb))
            continue
        win_verify = subtune_frames(cfg, passes=1.5)
        win_20 = subtune_frames(cfg, passes=2.0)
        digi_set = set(cfg.digi_subtunes or ())
        for st in range(len(cfg.subtunes)):
            if st in digi_set:
                plan.append((cfg.name, st, cfg, 0, 0))
                continue
            jobs[(cfg.name, st, 'orig')] = (cfg.sid_path, win_20[st], st)
            jobs[(cfg.name, st, 'rb')]   = (rb,            win_20[st], st)
            plan.append((cfg.name, st, cfg, win_verify[st], win_20[st]))

    print(f'Capturing $D418 traces for {len(jobs)} subtune × side jobs '
          f'in parallel...', flush=True)
    items = list(jobs.items())
    items.sort(key=lambda kv: -kv[1][1])  # heaviest first
    with Pool() as pool:
        results = pool.map(_capture_d418, [v for _, v in items])
    traces = {k: r for (k, _), r in zip(items, results)}

    print()
    print(f'{"ENGINE":24s} {"sub":>3s} {"orig_var":>9s} {"rb_var":>7s} '
          f'{"first_diff":>11s} {"in_1.5x":>8s}  config', flush=True)
    print('-' * 100, flush=True)

    any_undetected = False
    digi_set_for: dict = {p[2].name: set(p[2].digi_subtunes or ())
                          for p in plan}
    for cfg_name, st, cfg, w_verify, w20 in plan:
        if st in digi_set_for[cfg_name]:
            print(f'{cfg_name:24s} {st:>3d}  (digi — skipped)', flush=True)
            continue
        orig = traces[(cfg_name, st, 'orig')]
        rb   = traces[(cfg_name, st, 'rb')]
        orig_var = len(set(orig)) > 1
        rb_var   = len(set(rb))   > 1
        n = min(len(orig), len(rb))
        first = next((i for i in range(n) if orig[i] != rb[i]), None)
        if first is None and len(orig) != len(rb):
            first = n
        in_window = ('yes' if first is not None and first < w_verify
                     else ('no' if first is not None else '-'))
        flag = ''
        # Undetected fade signal: traces differ AND original varies AND
        # the first divergence falls past the 1.5x verifier boundary.
        if first is not None and orig_var and in_window == 'no':
            flag = '  *** UNDETECTED FADE ***'
            any_undetected = True
        print(f'{cfg_name:24s} {st:>3d} {str(orig_var):>9s} '
              f'{str(rb_var):>7s} {str(first):>11s} {in_window:>8s}  '
              f'{_config_str(cfg)}{flag}', flush=True)

    print('-' * 100, flush=True)
    for name, rb in skipped:
        print(f'SKIPPED  {name}  (rebuild missing at {rb})')
    if any_undetected:
        print('FAIL — at least one engine has an undetected song-end fade.')
        return 1
    print('OK — no undetected $D418 divergence past the 1.5x verify window.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
