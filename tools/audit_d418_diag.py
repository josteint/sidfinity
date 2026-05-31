"""Diagnostic for the flagged audit cases — print $D418 trace summaries
for the original and rebuild around the divergence point."""

import sys
sys.path.insert(0, '.')

from importlib import import_module
from pipelines.hubbard.inst_program import capture
from pipelines.hubbard.verify import subtune_frames

CASES = [
    ('thing_on_a_spring', 'THING_ON_A_SPRING', 0),
    ('confuzion',         'CFG',               0),
]


def _runs(trace: list[int], start: int, end: int):
    """Compress trace[start:end] into (value, run_length) tuples."""
    out = []
    cur_v = trace[start]
    cur_n = 1
    for v in trace[start+1:end]:
        if v == cur_v:
            cur_n += 1
        else:
            out.append((cur_v, cur_n))
            cur_v = v; cur_n = 1
    out.append((cur_v, cur_n))
    return out


for nick, varname, st in CASES:
    cfg = getattr(import_module(f'pipelines.hubbard.{nick}.config'),
                  varname)
    rb = cfg.sid_path.replace('.sid', '.sidfinity.sid')
    nf = subtune_frames(cfg, passes=2.0)[st]
    win_11 = subtune_frames(cfg, passes=1.1)[st]
    print(f'\n=== {cfg.name} sub {st}  (1.1x={win_11}  2.0x={nf}) ===')
    orig = [s[0x18] for s in capture(cfg.sid_path, n_frames=nf, subtune=st).snapshots]
    rebt = [s[0x18] for s in capture(rb,            n_frames=nf, subtune=st).snapshots]
    # Find first diff
    first = next((i for i in range(min(len(orig), len(rebt)))
                  if orig[i] != rebt[i]), None)
    print(f'first diff frame: {first}  (1.1x boundary = {win_11})')
    if first is None:
        continue
    print('\n--- orig $D418 RLE (from first diff −20 to end) ---')
    s = max(0, first - 20)
    for v, n in _runs(orig, s, len(orig)):
        print(f'  ${v:02X} × {n}')
    print('\n--- rebuild $D418 RLE (same range) ---')
    for v, n in _runs(rebt, s, len(rebt)):
        print(f'  ${v:02X} × {n}')
