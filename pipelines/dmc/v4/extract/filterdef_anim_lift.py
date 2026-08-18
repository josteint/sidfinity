"""Deconstruct the two Ed appended filter-def DRIVERS into typed
`filter_mod` contour entries (ledger C19 33rd-occurrence rule; the C1
parametric space; owner-approved res/period/loop_to growth 2026-08-16).

The factory probes (`_filterdef_anim_probe` / `_filterdef_anim3_probe`)
template-match the drivers and capture their constants; those constants
stay EXTRACT-INTERNAL. This module simulates the driver play-by-play
(the literal semantics of the byte-exact-verified former composer
emitters) against the decoded filter-def cell seeds, then encodes each
animated cell's value trajectory as a filter_mod entry:

  - resonance sweeps  -> single-tap `res`-target one-shot contours
  - cutoff ramps/LFOs -> init(/stop)-cell contours, `period`-clocked,
                         with a one-time lead-in and `loop_to` the cycle

Every emitted entry is REPLAY-VERIFIED: the entry runs through a Python
mirror of the composer's contour walker and must reproduce the simulated
per-play cell values exactly over the whole window (the C32 "observe,
don't fit" re-derivation assert). A cell that cannot be encoded exactly
raises — never a silent approximation.
"""
from __future__ import annotations

import math

SIM_PLAYS = 100_000       # > any verify window at 50 Hz (~33 min)
MAX_CYCLE_TICKS = 4096    # steady-state search bound (ticks)


# ---------------------------------------------------------------- drivers

def _sim_anim(consts: str, defs: dict) -> dict[tuple[int, str], list[int]]:
    """filterdef_anim (Cliche_Beat): phase 1 ramps defs 0-2's res cell
    every p1 plays until def0 hits the cap, then phase 2 walks a
    generated triangle into def0/def1's init-cutoff cells every p2
    plays (def0's index decrements, def1's advances by 2)."""
    step, cap, c1s, p1, c2s, p2, ts, td = (
        int(x, 16) for x in consts.split(','))
    tri = [(ts + i) & 0xFF for i in range(0x80)] + \
          [(td - i) & 0xFF for i in range(0x80)]
    st = {(d, 'res'): (defs[d]['res'] << 4) & 0xF0 for d in (0, 1, 2)}
    st[(0, 'init')] = defs[0]['init']
    st[(1, 'init')] = defs[1]['init']
    # series[p] = the state VISIBLE TO PLAY p's body — the driver runs
    # BEFORE the body, so its counters already decrement at play 0 (the
    # off-by-one that made Only_Ones' clamped sweep diverge, 2026-08-16)
    ser = {k: [] for k in st}
    ph, c1, c2, x0, x1 = 0, c1s, c2s, 0, 0
    for _ in range(SIM_PLAYS):
        if ph == 0:
            c1 -= 1
            if c1 == 0:
                c1 = p1
                if st[(0, 'res')] == cap:
                    ph = 1
                else:
                    for d in (0, 1, 2):
                        st[(d, 'res')] = (st[(d, 'res')] + step) & 0xFF
        else:
            c2 -= 1
            if c2 == 0:
                c2 = p2
                st[(0, 'init')] = tri[x0]
                x0 = (x0 - 1) & 0xFF
                st[(1, 'init')] = tri[x1]
                x1 = (x1 + 2) & 0xFF
        for k in st:
            ser[k].append(st[k])
    return ser


def _sim_anim3(consts: str, defs: dict) -> dict[tuple[int, str], list[int]]:
    """filterdef_anim3 (Only_Ones): phase A (every p1 plays) ramps def
    s2's init/stop up while its res nibble staircases, then walks def
    s1's init/stop down; phase B (every play) stores halved-triangle
    taps into both defs' init/stop, x1 advancing per p8 plays and x2
    per p8*p2."""
    (p1, cap2, rescap, dncap, x1s, x2s, p8, p2,
     add2, add1, step, d0, s2, s1) = (int(x, 16) for x in consts.split(','))
    tri = [(i + step) & 0xFF for i in range(0x80)] + \
          [(d0 - i) & 0xFF for i in range(0x80)]
    st = {(s2, 'res'): (defs[s2]['res'] << 4) & 0xF0,
          (s2, 'init'): defs[s2]['init'], (s2, 'stop'): defs[s2]['stop'],
          (s1, 'init'): defs[s1]['init'], (s1, 'stop'): defs[s1]['stop']}
    # series[p] = state visible to play p's body (driver runs first —
    # see _sim_anim's off-by-one note)
    ser = {k: [] for k in st}
    ph, c1, cnt, x1, x2, c8, c2 = 0, p1, (x2s + 1) & 0xFF, x1s, x2s, p8, p2
    for _ in range(SIM_PLAYS):
        if ph == 0:
            c1 -= 1
            if c1 == 0:
                c1 = p1
                if st[(s2, 'init')] != cap2:
                    st[(s2, 'init')] = (st[(s2, 'init')] + 1) & 0xFF
                    st[(s2, 'stop')] = (st[(s2, 'stop')] + 1) & 0xFF
                st[(s2, 'res')] = (cnt << 4) & 0xFF
                if cnt != rescap:
                    cnt += 1
                elif st[(s1, 'init')] != dncap:
                    st[(s1, 'init')] = (st[(s1, 'init')] - 1) & 0xFF
                    st[(s1, 'stop')] = (st[(s1, 'stop')] - 1) & 0xFF
                else:
                    ph = 1
        else:
            v = ((tri[x1] >> 1) + add2) & 0xFF
            st[(s2, 'init')] = st[(s2, 'stop')] = v
            v = ((tri[x2] >> 1) + add1) & 0xFF
            st[(s1, 'init')] = st[(s1, 'stop')] = v
            c8 -= 1
            if c8 == 0:
                c8 = p8
                x1 = (x1 + 1) & 0xFF
                c2 -= 1
                if c2 == 0:
                    c2 = p2
                    x2 = (x2 + 1) & 0xFF
        for k in st:
            ser[k].append(st[k])
    return ser


# ----------------------------------------------------- encode one series

def replay_walker(entry: dict, n: int) -> list[int]:
    """Python mirror of the composer's NEW contour walker (playfmn:
    period countdown seeded P - (init_phase mod P); tick BEFORE store).
    Returns the value visible to play p's body for p in 0..n-1. Must
    stay in lockstep with composer_asm's playfmn chunk."""
    p = entry.get('period', 1)
    runs = entry['steps']
    v = entry['start'] & 0xFF
    c = p - (entry['init_phase'] % p)
    cur = 0
    f = runs[0][1] if runs else 0
    held = not runs
    out = []
    for _ in range(n):
        c -= 1
        if c == 0:
            c = p
            if not held:
                v = (v + runs[cur][0]) & 0xFF
                f -= 1
                if f == 0:
                    cur += 1
                    if cur == len(runs):
                        if not entry.get('loop', True):
                            held = True
                        else:
                            cur = entry.get('loop_to') or 0
                            f = runs[cur][1]
                    else:
                        f = runs[cur][1]
        out.append(v)
    return out


def _rle(deltas: list[int]) -> list[tuple[int, int]]:
    runs: list[list[int]] = []
    for d in deltas:
        if runs and runs[-1][0] == d and runs[-1][1] < 255:
            runs[-1][1] += 1
        else:
            runs.append([d, 1])
    return [tuple(r) for r in runs]


def _normalize(e: dict) -> dict:
    """Match the parser's key conventions exactly (round-trip object
    equality): loop omitted when True, period omitted when 1,
    stop_phase always present."""
    if e.get('period', 1) == 1:
        e.pop('period', None)
    if e.get('loop', True):
        e.pop('loop', None)
    if e.get('loop_to') is None:
        e.pop('loop_to', None)
    e.setdefault('stop_phase', None)
    return e


def _encode_series(series: list[int]) -> dict:
    """Encode one cell's per-play value series as walker fields,
    replay-verified exact. Tries the change-cadence gcd as the tick
    period first (compact, readable), then period 1 (always exact)."""
    changes = [i for i in range(1, len(series)) if series[i] != series[i - 1]]
    if not changes:
        return _normalize({'start': series[0], 'init_phase': 0,
                           'steps': [(0, 1)], 'loop': False})
    # tick period = gcd of the change GAPS (the cadence); the first
    # change's absolute play only fixes the grid offset r, never the
    # period (including it collapsed Cliche's 12-play LFO to gcd 4).
    per = 0
    for g in (b - a for a, b in zip(changes, changes[1:])):
        per = math.gcd(per, g)
    per = per or changes[0]
    for p in dict.fromkeys((max(1, min(per, 255)), 1)):
        r = changes[0] % p               # tick grid: plays ≡ r (mod p)
        if any(cp % p != r for cp in changes):
            continue
        phase = (p - (r + 1)) % p        # walker: c = p - phase -> first
        #                                  tick at 0-indexed play r
        ticks = list(range(r, len(series), p))
        prev = [series[0]] + [series[t] for t in ticks[:-1]]
        deltas = [((series[t] - pv) + 128) % 256 - 128
                  for t, pv in zip(ticks, prev)]
        last = (changes[-1] - r) // p    # tick index of the last change
        if len(ticks) - 1 - last > MAX_CYCLE_TICKS:
            # one-shot: constant tail to window end -> terminal hold
            e = {'start': series[0], 'init_phase': phase, 'period': p,
                 'steps': _rle(deltas[:last + 1]), 'loop': False}
        else:
            # looping: smallest REAL cycle with a (possibly empty)
            # prefix. A candidate must repeat over a substantial tail
            # (>= 3 cycles and >= 1024 ticks) — without that floor, a
            # 1-tick "cycle" matching the last two window deltas
            # false-fires: exact over the window, garbage beyond it.
            e = None
            for cyc in range(1, MAX_CYCLE_TICKS + 1):
                tail_need = max(3 * cyc, 1024)
                if tail_need > len(deltas):
                    break
                k0 = len(deltas) - tail_need
                if any(deltas[i] != deltas[i + cyc]
                       for i in range(k0, len(deltas) - cyc)):
                    continue
                pre = next(k for k in range(k0 + 1)
                           if all(deltas[i] == deltas[i + cyc]
                                  for i in range(k, k0)))
                prefix, cycle = _rle(deltas[:pre]), _rle(deltas[pre:pre + cyc])
                e = {'start': series[0], 'init_phase': phase, 'period': p,
                     'steps': prefix + cycle, 'loop': True,
                     'loop_to': len(prefix) or None}
                break
            if e is None:
                continue
        e = _normalize(e)
        if replay_walker(e, len(series)) == series:
            return e
    raise ValueError('filterdef_anim lift: cell series not exactly '
                     'encodable as a filter_mod contour')


# ------------------------------------------------------------- public

def lift_filterdef_anim(key: str, consts: str, filter_defs: dict) -> list:
    """Simulate driver `key` and return its filter_mod entries (sorted
    by (prog, target)): res sweeps + cutoff contours, all replay-
    verified. `filter_defs` = the decoded 0-based def records (the
    composer's fdres/fdinit/fdstop seed source)."""
    ser = (_sim_anim if key == 'filterdef_anim' else _sim_anim3)(
        consts, filter_defs)
    entries = []
    for (d, kind) in sorted(ser):
        if kind == 'stop':
            continue                     # carried by the init entry's dual tap
        series = ser[(d, kind)]
        two_tap = kind == 'init' and (d, 'stop') in ser
        if two_tap and ser[(d, 'stop')] != series:
            raise ValueError('filterdef_anim lift: init/stop series '
                             'diverge — dual-store encoding invalid')
        e = _encode_series(series)
        e['prog'] = d + 1                # USF filter progs are 1-based
        if two_tap:
            e['stop_phase'] = e['init_phase']
        if kind == 'res':
            e['target'] = 'res'
        entries.append(e)
    entries.sort(key=lambda e: (e['prog'], e.get('target') or ''))
    return entries
