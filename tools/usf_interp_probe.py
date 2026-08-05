#!/usr/bin/env python3
"""§9 test 3 — the interpolation probe (the Principle's ML-readiness gate,
operationalized 2026-08-04; cleanup plan E3/P3).

"Take two real instances of the effect, average their parameters … The
result should be a plausible instance." The strong form is judgmental; this
probe mechanizes the WEAK form: the composer must be able to REALIZE the
midpoint of two real same-file instrument configs — build without refusal
and produce a live write stream. A failure is a named finding: the
parameter space is not freely interpolable under the current encoding
(§4 basis defect or an encoding-coupling constraint worth documenting).
Findings are surfaced, never auto-failed — some couplings are legitimate
engine structure (then they become case law here or in the ledger).

DMC-focused v1: interpolates PwmConfig (init/min_hi/max_hi + element-wise
speed_steps), VibratoConfig (onset/amplitude/ramp), FreqSlideConfig (step).
Integer midpoints. One mutated instrument per build.

Usage:
    python3 tools/usf_interp_probe.py [--members N] [--pairs N] [--seed S]
"""
from __future__ import annotations

import argparse
import copy
import os
import random
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))


def _mid(a: int, b: int) -> int:
    return (int(a) + int(b)) // 2


def _interp_pwm(x, y):
    z = copy.deepcopy(x)
    z.init = _mid(x.init, y.init)
    z.min_hi = _mid(x.min_hi, y.min_hi)
    z.max_hi = _mid(x.max_hi, y.max_hi)
    if x.speed_steps and y.speed_steps and \
            len(x.speed_steps) == len(y.speed_steps):
        if x.step_base is not None and y.step_base is not None:
            # split form (2026-08-05): steps and base are independent
            # 0-15 DOF — interpolate both freely (the P3 nibble-coupling
            # finding is CLOSED; no shared-base constraint remains)
            z.speed_steps = [_mid(a, b) for a, b in
                             zip(x.speed_steps, y.speed_steps)]
            z.step_base = _mid(x.step_base, y.step_base)
        elif x.step_base is None and y.step_base is None:
            # legacy packed form: interpolation must hold the base nibble
            # fixed (the P3 case law) — midpoint the hi nibbles only,
            # keep x's base
            base = x.speed_steps[0] & 0x0F
            z.speed_steps = [
                ((_mid(a >> 4, b >> 4)) << 4) | base
                for a, b in zip(x.speed_steps, y.speed_steps)]
    return z


def _interp_vib(x, y):
    z = copy.deepcopy(x)
    z.onset = _mid(x.onset, y.onset)
    z.amplitude = _mid(x.amplitude, y.amplitude)
    z.ramp = _mid(x.ramp, y.ramp)
    return z


def _interp_slide(x, y):
    z = copy.deepcopy(x)
    if getattr(x, 'step', None) is not None and \
            getattr(y, 'step', None) is not None:
        z.step = _mid(x.step, y.step)
    return z


CONFIGS = [('pwm', _interp_pwm), ('vibrato', _interp_vib),
           ('freq_slide_config', _interp_slide)]


def _stream_alive(sid_path: str) -> bool:
    """The built SID produces writes over 3 s (realizability, not fidelity)."""
    try:
        out = subprocess.run(
            ['siddump', sid_path, '--subtune', '1', '--duration', '3',
             '--writelog'],
            capture_output=True, text=True, timeout=120).stdout
        return sum(1 for ln in out.splitlines() if '|W:' in ln) > 0
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--members', type=int, default=25)
    ap.add_argument('--pairs', type=int, default=2)
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()

    from src.batch_results import load_latest
    from src.usf.parser import parse_file
    from src.usf.writer import write
    from src.usf.parser import parse
    from pipelines.dmc.composer_asm import build_dmc_sid

    rows = load_latest(os.path.join(ROOT, 'tmp',
                                    'dmc_f1_fullbatch_verify.jsonl'))
    members = [p for p in sorted(rows)
               if os.path.exists(os.path.join(
                   ROOT, 'hvsc84', p[:-4] + '.usf'))]
    rng = random.Random(args.seed)
    picked = rng.sample(members, min(args.members, len(members)))

    tried = ok = 0
    findings = []
    for m in picked:
        up = os.path.join(ROOT, 'hvsc84', m[:-4] + '.usf')
        try:
            u = parse_file(up)
        except Exception:
            continue
        insts = {k: v for k, v in (u.instruments or {}).items()} \
            if isinstance(u.instruments, dict) else \
            {i.id: i for i in (u.instruments or [])}
        ids = sorted(insts)
        if len(ids) < 2:
            continue
        for _ in range(args.pairs):
            a, b = rng.sample(ids, 2)
            cfg_name, fn = rng.choice(CONFIGS)
            xa = getattr(insts[a], cfg_name, None)
            xb = getattr(insts[b], cfg_name, None)
            if xa is None or xb is None:
                continue
            mut = copy.deepcopy(u)
            minsts = mut.instruments if isinstance(mut.instruments, dict) \
                else {i.id: i for i in mut.instruments}
            try:
                setattr(minsts[a] if isinstance(mut.instruments, dict)
                        else next(i for i in mut.instruments if i.id == a),
                        cfg_name, fn(xa, xb))
            except Exception as e:
                findings.append((m, cfg_name, 'interp', repr(e)[:90]))
                continue
            tried += 1
            try:
                mu = parse(write(mut))       # canonical round trip first
                sid = build_dmc_sid(mu)
            except Exception as e:
                findings.append((m, cfg_name, 'build-refusal',
                                 repr(e)[:120]))
                continue
            with tempfile.NamedTemporaryFile(suffix='.sid',
                                             delete=False) as f:
                f.write(sid)
                tmp = f.name
            alive = _stream_alive(tmp)
            os.unlink(tmp)
            if alive:
                ok += 1
            else:
                findings.append((m, cfg_name, 'dead-stream', ''))
    print(f'interp probe: {tried} midpoints tried, {ok} realized live, '
          f'{len(findings)} finding(s)')
    from collections import Counter
    c = Counter((f[1], f[2]) for f in findings)
    for (cfg, kind), n in c.most_common():
        ex = next(f for f in findings if f[1] == cfg and f[2] == kind)
        print(f'  ⚠ {cfg}/{kind}: {n}x   e.g. {ex[0]}: {ex[3]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
