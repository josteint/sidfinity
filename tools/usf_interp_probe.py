#!/usr/bin/env python3
"""§9 test 3 — the interpolation probe (the Principle's ML-readiness gate,
operationalized 2026-08-04; cleanup plan E3/P3; WIDENED 2026-08-05, I1).

"Take two real instances of the effect, average their parameters … The
result should be a plausible instance." The strong form is judgmental; this
probe mechanizes the WEAK form: the composer must be able to REALIZE the
midpoint of two real instrument configs — build without refusal and produce
a live write stream. A failure is a named finding: the parameter space is
not freely interpolable under the current encoding (§4 basis defect or an
encoding-coupling constraint worth documenting). Findings are surfaced,
never auto-failed — some couplings are legitimate engine structure (then
they become case law here or in the ledger).

The I1 widening (all axes of cleanup-plan item I1):
- CROSS-FILE pairs (--cross): instrument A's config midpointed with an
  instrument from a DIFFERENT member of the same engine corpus — a
  stronger test than same-file siblings.
- More effect families: adsr (NIBBLE-wise — the AD/SR bytes pack four
  4-bit DOF; byte-midpoints would silently test nothing), element-wise
  wave_freq (melodic per-step semitone offsets), alongside the original
  pwm / vibrato / freq_slide.
- More engines (--engines dmc,fc,hubbard): FC standard (file-based
  builder) + the Hubbard '85/Companion corpus (build_from_usf) beside
  DMC f1. §9 test 4 (cross-engine reuse) gets probed for free: the same
  interp functions run against every engine's instances of the shared
  schema. (MA has no stored corpus yet — mass-write deliberately
  deferred; Basic_Program is a trace-lift without this instrument model;
  GT V1 has 1 stored member. All three join when their corpora exist.)

Usage:
    python3 tools/usf_interp_probe.py [--engines dmc,fc,hubbard]
        [--members N] [--pairs N] [--cross N] [--seed S]
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


# config-object interps: (Instrument attr, fn(cfg_a, cfg_b) -> cfg_mid)
CONFIGS = [('pwm', _interp_pwm), ('vibrato', _interp_vib),
           ('freq_slide_config', _interp_slide)]


def _interp_adsr(inst, other):
    """AD/SR bytes pack four 4-bit DOF (attack|decay, sustain|release) —
    midpoint each NIBBLE (a byte-midpoint mixes neighbours' nibbles and
    would test nothing: any byte is realizable)."""
    def nibmid(p, q):
        return ((_mid(p >> 4, q >> 4)) << 4) | _mid(p & 0x0F, q & 0x0F)
    a, b = inst.adsr
    c, d = other.adsr
    inst.adsr = (nibmid(a, c), nibmid(b, d))


def _interp_wave_freq(inst, other):
    """Element-wise midpoint of the per-step semitone-offset list (melodic
    wave programs; only when both carry same-length non-empty lists)."""
    wa, wb = inst.wave_freq, other.wave_freq
    if wa and wb and len(wa) == len(wb):
        inst.wave_freq = [_mid(p, q) for p, q in zip(wa, wb)]


# instrument-level interps: mutate inst in place from other
INST_FIELDS = [('adsr', _interp_adsr), ('wave_freq', _interp_wave_freq)]


# ---------------------------------------------------------------------------
# Engine corpus registry: member list source + USF->SID builder
# ---------------------------------------------------------------------------

def _dmc_members():
    from src.batch_results import load_latest
    rows = load_latest(os.path.join(ROOT, 'tmp',
                                    'dmc_f1_fullbatch_verify.jsonl'))
    return [p for p in sorted(rows)
            if os.path.exists(os.path.join(ROOT, 'hvsc84',
                                           p[:-4] + '.usf'))]


def _dmc_build(rel, usf_text):
    from src.usf.parser import parse
    from pipelines.dmc.composer_asm import build_dmc_sid
    return build_dmc_sid(parse(usf_text))


def _fc_members():
    from src.batch_results import load_latest
    rows = load_latest(os.path.join(ROOT, 'tmp', 'fc_std_wide_results.jsonl'),
                       path_key='sid')
    return [p for p, r in sorted(rows.items())
            if r.get('status') == 'full'
            and os.path.exists(os.path.join(ROOT, 'hvsc84',
                                            p[:-4] + '.usf'))]


def _fc_build(rel, usf_text):
    from pipelines.future_composer.standard.config import fc_standard_config
    from pipelines.future_composer.composer_asm import (
        build_via_asm_featuredriven)
    with tempfile.NamedTemporaryFile('w', suffix='.usf',
                                     delete=False) as f:
        f.write(usf_text)
        tmp = f.name
    try:
        return build_via_asm_featuredriven(
            fc_standard_config('hvsc84/' + rel), usf_path=tmp)
    finally:
        os.unlink(tmp)


def _hubbard_members():
    from src import sid_db
    out = []
    for (path,) in sid_db.query(
            "SELECT path FROM sids WHERE engine IN ('Rob_Hubbard',"
            " 'Companion')"):
        if os.path.exists(os.path.join(ROOT, 'hvsc84', path[:-4] + '.usf')):
            out.append(path)
    return sorted(out)


def _hubbard_build(rel, usf_text):
    from pipelines.build_from_usf import build_from_usf
    with tempfile.NamedTemporaryFile('w', suffix='.usf', delete=False) as f:
        f.write(usf_text)
        tmpu = f.name
    tmps = tmpu[:-4] + '.sid'
    try:
        build_from_usf(tmpu, tmps)
        with open(tmps, 'rb') as f:
            return f.read()
    finally:
        os.unlink(tmpu)
        if os.path.exists(tmps):
            os.unlink(tmps)


ENGINES = {
    'dmc': (_dmc_members, _dmc_build),
    'fc': (_fc_members, _fc_build),
    'hubbard': (_hubbard_members, _hubbard_build),
}


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


def _insts_of(u):
    if isinstance(u.instruments, dict):
        return dict(u.instruments)
    return {i.id: i for i in (u.instruments or [])}


def _parse_member(rel):
    from src.usf.parser import parse_file
    up = os.path.join(ROOT, 'hvsc84', rel[:-4] + '.usf')
    try:
        return parse_file(up)
    except Exception:
        return None


def _probe_one(engine, build, rel, u, inst_id, donor_inst, rng,
               findings, stats):
    """Midpoint ONE randomly-chosen effect family of instrument `inst_id`
    in member `rel` against `donor_inst`; build + liveness-check."""
    from src.usf.writer import write
    from src.usf.parser import parse
    kind = rng.choice(CONFIGS + INST_FIELDS)
    name, fn = kind
    mut = copy.deepcopy(u)
    minsts = _insts_of(mut)
    target = minsts[inst_id]
    try:
        if kind in CONFIGS:
            xa = getattr(target, name, None)
            xb = getattr(donor_inst, name, None)
            if xa is None or xb is None:
                return
            setattr(target, name, fn(xa, xb))
        else:
            fn(target, donor_inst)
    except Exception as e:
        stats['tried'] += 1
        findings.append((engine, rel, name, 'interp', repr(e)[:90]))
        return
    stats['tried'] += 1
    try:
        text = write(mut)
        parse(text)                    # canonical round trip first
        sid = build(rel, text)
    except Exception as e:
        findings.append((engine, rel, name, 'build-refusal',
                         repr(e)[:120]))
        return
    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
        f.write(sid)
        tmp = f.name
    alive = _stream_alive(tmp)
    os.unlink(tmp)
    if alive:
        stats['ok'] += 1
    else:
        findings.append((engine, rel, name, 'dead-stream', ''))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--engines', default='dmc,fc,hubbard')
    ap.add_argument('--members', type=int, default=25,
                    help='members sampled per engine (same-file pool)')
    ap.add_argument('--pairs', type=int, default=2,
                    help='same-file pairs per member')
    ap.add_argument('--cross', type=int, default=20,
                    help='cross-file pairs per engine')
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    findings = []
    stats = {'tried': 0, 'ok': 0}
    for engine in args.engines.split(','):
        members_fn, build = ENGINES[engine]
        members = members_fn()
        if not members:
            print(f'  ({engine}: no corpus, skipped)')
            continue
        picked = rng.sample(members, min(args.members, len(members)))
        # same-file pairs
        parsed = {}
        for m in picked:
            u = _parse_member(m)
            if u is None:
                continue
            parsed[m] = u
            insts = _insts_of(u)
            ids = sorted(insts)
            if len(ids) < 2:
                continue
            for _ in range(args.pairs):
                a, b = rng.sample(ids, 2)
                _probe_one(engine, build, m, u, a, insts[b], rng,
                           findings, stats)
        # cross-file pairs: donor instrument from a DIFFERENT member
        pool = [m for m in parsed if _insts_of(parsed[m])]
        for _ in range(args.cross):
            if len(pool) < 2:
                break
            ma, mb = rng.sample(pool, 2)
            ua, ub = parsed[ma], parsed[mb]
            ia = rng.choice(sorted(_insts_of(ua)))
            ib = rng.choice(sorted(_insts_of(ub)))
            _probe_one(engine, build, ma, ua, ia,
                       _insts_of(ub)[ib], rng, findings, stats)

    print(f"interp probe: {stats['tried']} midpoints tried, "
          f"{stats['ok']} realized live, {len(findings)} finding(s)")
    from collections import Counter
    c = Counter((f[0], f[2], f[3]) for f in findings)
    for (eng, cfg, kind), n in c.most_common():
        ex = next(f for f in findings
                  if f[0] == eng and f[2] == cfg and f[3] == kind)
        print(f'  ⚠ {eng}/{cfg}/{kind}: {n}x   e.g. {ex[1]}: {ex[4]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
