#!/usr/bin/env python3
"""divergence_triage.py — ENGINE-BLIND divergence classifier (prototype).

Given an HVSC original and a rebuild, localize the first writelog
divergence (reusing find_first_divergence) and run a battery of
engine-BLIND writelog-signature detectors that suggest the likely
convergence-ledger class(es) with evidence — collapsing the manual
"which ledger entry is this?" triage step (the slow part per
feedback_measure_mechanism_before_precedent).

Engine-blind BY CONSTRUCTION: the detectors read only the two (reg,val)
write streams — no engine knowledge. Engine-PARAMETRIZED detectors
(off-table freq C6, wedge diff C19, state-as-data C11) plug in through
ENGINE_DETECTORS, a per-engine registry (the divergence_census /
select_regression_portfolio pattern: engine-blind core + one registry
entry per family). With no engine registered, the blind detectors still
run and still help.

Usage:
    # engine-blind (works on ANY SID family):
    python3 tools/divergence_triage.py ORIG.sid REBUILD.sid [--subtune N]
    # + engine-parametrized detectors (registry):
    python3 tools/divergence_triage.py ORIG.sid REBUILD.sid --engine dmc
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from find_first_divergence import describe_reg, _resolve_duration  # noqa: E402
from pipelines.hubbard.verify_cycle import (  # noqa: E402
    writelog_per_irq_capture, writelog_capture)


def _localize(orig, rebuild, subtune, duration):
    """Engine-blind localization of the first (reg,val) divergence, using the
    Trap-C-free PER-IRQ capture (writes bucketed by play() invocation, init
    dropped) so CIA/multispeed members do not spuriously "diverge at position
    0" (the flat per-frame capture's Trap-C artifact — see
    writelog_per_irq_capture). Falls back to the flat capture if per-irq yields
    nothing. Returns the same dict shape find_first_divergence produced."""
    dur = _resolve_duration(orig, subtune, duration)

    def cap(path):
        try:
            fr = writelog_per_irq_capture(path, subtune=subtune, duration=dur)
            if fr:
                return fr, 'per-irq'
        except Exception:
            pass
        return writelog_capture(path, subtune=subtune, duration=dur), 'flat'

    of, omode = cap(orig)
    rf, rmode = cap(rebuild)

    def flatten(frames):
        return [(reg, val, k, c) for k, fr in enumerate(frames)
                for c, reg, val in fr]
    fo, fr = flatten(of), flatten(rf)
    n = min(len(fo), len(fr))
    div = next((i for i in range(n) if fo[i][:2] != fr[i][:2]), None)
    return {
        'duration_s': dur, 'orig_writes': len(fo), 'rebuild_writes': len(fr),
        'match_prefix': div if div is not None else n, 'first_div': div,
        'orig_flat': fo, 'rebuild_flat': fr, 'capture': f'{omode}/{rmode}',
    }


@dataclass
class Signal:
    """One triage hypothesis."""
    klass: str          # ledger id, e.g. 'C24' / 'C28' / 'C16'
    confidence: str     # HIGH | MED | LOW
    summary: str        # one-line human hypothesis
    evidence: str       # the measurement that fired it


_CONF_RANK = {'HIGH': 0, 'MED': 1, 'LOW': 2}


# --------------------------------------------------------------------------
# Engine-BLIND detectors — each reads only the flat (reg,val,frame,cyc)
# streams + the divergence result, and returns a Signal or None.
# --------------------------------------------------------------------------

def _detect_length_tail(r) -> 'Signal | None':
    """No content divergence in the overlap, but the stream LENGTHS differ
    -> a timing/rate class, not a wrong note. Sub-classify by the ratio
    (C24 double-speed / C9 clean-1/N rate / C25 latch-overrun / C12 drift)."""
    if r['first_div'] is not None:
        return None
    lo, lr = r['orig_writes'], r['rebuild_writes']
    if lo == 0 or lr == 0 or lo == lr:
        return None
    hi, lowv = max(lo, lr), min(lo, lr)
    ratio = hi / lowv
    faster = 'rebuild' if lr > lo else 'orig'
    ev = (f'exact prefix over the whole overlap; lengths {lo} vs {lr} '
          f'(ratio {ratio:.3f}, {faster} longer)')
    # near-integer multiple => double/half-speed body (C24) or rate (C9)
    for n in (2, 3, 4, 6):
        if abs(ratio - n) < 0.03:
            return Signal('C24/C9', 'HIGH',
                          f'whole-stream ~{n}x length -> play-repeat / wrong '
                          f'CIA rate ({faster} runs {n}x)', ev)
    if ratio <= 1.02:
        return Signal('C25/C12', 'HIGH',
                      'exact prefix + tiny (<2%) length tail -> CIA latch '
                      'overrun (C25) or delta-drift (C12, scales with song '
                      'length)', ev)
    if ratio <= 1.5:
        return Signal('C9/C25', 'MED',
                      f'exact prefix + {100*(ratio-1):.1f}% length tail -> '
                      'rate/latch class', ev)
    return Signal('length', 'MED',
                  f'exact prefix, length ratio {ratio:.2f} -> a timing/rate '
                  'class (not a wrong note)', ev)


def _split_by_chip(flat):
    chips = {}
    for reg, val, fr, cyc in flat:
        c = reg >> 5
        chips.setdefault(c, []).append((reg & 0x1F, val))
    return chips


def _detect_cross_chip(r) -> 'Signal | None':
    """Multi-SID: the merged chip-tagged stream diverges, but each chip's
    OWN substream matches -> a cross-chip ADJACENCY (C28), physically
    unobservable ordering, i.e. a FALSE divergence."""
    if r['first_div'] is None:
        return None
    multi = any(reg >> 5 for reg, *_ in r['orig_flat'][:2000])
    if not multi:
        return None
    co = _split_by_chip(r['orig_flat'])
    cr = _split_by_chip(r['rebuild_flat'])
    if set(co) != set(cr):
        return None
    for c in co:
        n = min(len(co[c]), len(cr[c]))
        if co[c][:n] != cr[c][:n]:
            return None                     # a real per-chip divergence
    return Signal('C28', 'HIGH',
                  'multi-SID: every chip substream matches individually but '
                  'the merged stream diverges -> cross-chip order (C28), '
                  'physically unobservable; split by reg//0x20 to verify',
                  'per-chip substreams all match; only the interleave differs')


def _div_kind(r) -> 'str | None':
    """'wrong_value' = same register, different value (an effect computed the
    wrong value); 'reorder' = different register (writes in the wrong order or
    a missing/extra emission). These need different detectors."""
    div = r['first_div']
    if div is None:
        return None
    return ('wrong_value'
            if r['orig_flat'][div][0] == r['rebuild_flat'][div][0]
            else 'reorder')


def _detect_write_order(r, window: int = 12) -> 'Signal | None':
    """DIFFERENT register at the divergence -> the diverging (reg,val) is
    either PRESENT nearby in the other stream (reordered -> write-ORDER, C16)
    or ABSENT (a missing/extra EMISSION). A same-register value difference is
    NOT this class (that is a wrong value -> the role detectors)."""
    if _div_kind(r) != 'reorder':
        return None
    div = r['first_div']
    fo, fr = r['orig_flat'], r['rebuild_flat']
    o = fo[div][:2]
    lo_i, hi_i = max(0, div - window), min(len(fr), div + window + 1)
    reb_win = [e[:2] for e in fr[lo_i:hi_i]]
    orig_win = [e[:2] for e in fo[lo_i:min(len(fo), div + window + 1)]]
    r_here = fr[div][:2] if div < len(fr) else None
    if o in reb_win and r_here in orig_win:
        return Signal('C16', 'MED',
                      'diverging writes are all present NEARBY in both streams '
                      '(reordered) -> per-frame write-ORDER differs (C16); '
                      'parametrize the emission order, do not rewrite',
                      f'orig {describe_reg(o[0])}=${o[1]:02X} found within '
                      f'{window} of the rebuild')
    if o not in reb_win:
        return Signal('emission', 'MED',
                      f"orig's {describe_reg(o[0])}=${o[1]:02X} is ABSENT from "
                      "the rebuild's local window -> a MISSING emission "
                      '(effect not fired) rather than a wrong value',
                      f'value not found within {window} writes of the rebuild')
    return None


def _detect_wrong_value_freq(r) -> 'Signal | None':
    """WRONG VALUE on a voice-freq register -> off-table freq read (C6) or, when
    the delta is quantized x16, speed-nibble arming (C22); deeper divergence
    weights C22. Routes to the engine off-table probe (registry) to confirm."""
    if _div_kind(r) != 'wrong_value':
        return None
    reg, oval, *_ = r['orig_flat'][r['first_div']]
    rreg, rval, *_ = r['rebuild_flat'][r['first_div']]
    role = describe_reg(reg)
    if 'freq' not in role:
        return None
    div = r['first_div']
    depth = div / max(1, min(r['orig_writes'], r['rebuild_writes']))
    x16 = (reg & 7) == 0 and abs(oval - rval) % 16 == 0   # freq-lo, delta x16
    deep = depth >= 0.5
    klass = 'C22/C6' if (x16 and deep) else 'C6/C22'
    hint = ('freq-lo delta is a multiple of 16 (a C22 arming tell)' if x16
            else 'run the engine off-table probe to confirm C6')
    return Signal(klass, 'MED',
                  f'wrong VALUE on {role} ({100*depth:.0f}% through) -> '
                  'off-table freq read (C6)' + (' or arming drift (C22)'
                                                if x16 or deep else ''),
                  f'{hint}; orig ${oval:02X} vs rebuild ${rval:02X}')


def _detect_wrong_value_pulse(r) -> 'Signal | None':
    """WRONG VALUE on a pulse-width register (PW lo/hi) -> a pulse-program /
    PWM sweep the composer runs but the orig doesn't (or a different contour):
    the swept-value class (C1), often a 'no program' mis-detection (C3) or a
    wrong instrument's PWM. Very common as an EARLY divergence (first note)."""
    if _div_kind(r) != 'wrong_value':
        return None
    reg, oval, *_ = r['orig_flat'][r['first_div']]
    rval = r['rebuild_flat'][r['first_div']][1]
    role = describe_reg(reg)
    if 'PW' not in role:
        return None
    flat = (oval == 0)                      # orig PW held at 0 = no sweep at all
    return Signal('C1/C3', 'MED',
                  f'wrong VALUE on {role} -> pulse-width contour differs '
                  + ('(orig holds PW=$00 = NO sweep; composer runs a PWM '
                     'that should be absent/flat -> check "no program" '
                     'detection C3 + the voice\'s instrument)'
                     if flat else '(PWM sweep contour C1 or wrong instrument)'),
                  f'orig ${oval:02X} vs rebuild ${rval:02X}'
                  + ('; orig PW flat at 0' if flat else ''))


def _detect_wrong_value_global(r) -> 'Signal | None':
    """WRONG VALUE on a chip-global register ($D415-$D418) -> filter /
    master-vol AUTOMATION (C10), not a per-voice effect."""
    if _div_kind(r) != 'wrong_value':
        return None
    reg = r['orig_flat'][r['first_div']][0] & 0x1F
    if reg in (0x15, 0x16, 0x17, 0x18):
        return Signal('C10', 'LOW',
                      f'divergence on a chip-global reg ({describe_reg(reg)}) '
                      '-> master-vol/filter automation (C10) or filter program '
                      '- check the parametric vs explicit-event choice',
                      f'first divergence is ${reg + 0xD400:04X}')
    return None


BLIND_DETECTORS = [
    _detect_length_tail,
    _detect_cross_chip,
    _detect_wrong_value_freq,
    _detect_wrong_value_pulse,
    _detect_write_order,
    _detect_wrong_value_global,
]


# --------------------------------------------------------------------------
# Engine-PARAMETRIZED registry — one entry per family. Each detector takes
# (orig_path, rebuild_path, subtune, result) and returns a Signal or None.
# These are thin adapters onto the family's existing probes.
# --------------------------------------------------------------------------

def _dmc_offtable(orig, rebuild, subtune, r) -> 'Signal | None':
    """Adapter onto tools/dmc_offtable_probe.py (C6). Only meaningful when the
    divergence is a voice freq lo/hi (the probe bows out otherwise)."""
    if _div_kind(r) != 'wrong_value':
        return None
    role = describe_reg(r['orig_flat'][r['first_div']][0])
    if 'freq' not in role:
        return None
    return Signal('C6?', 'LOW',
                  'engine detector available: run '
                  f'`dmc_offtable_probe.py <member> --subtune {subtune}` to '
                  'confirm/deny an off-table freq read at the divergence',
                  'registry adapter (not auto-run in this prototype)')


ENGINE_DETECTORS = {
    'dmc': [_dmc_offtable],
    # 'future_composer': [...], 'music_assembler': [...] — add per family.
}


# --------------------------------------------------------------------------

def triage(orig, rebuild, subtune=0, duration=None, engine=None) -> list:
    r = _localize(orig, rebuild, subtune, duration)
    signals = []
    if r['first_div'] is None and r['orig_writes'] == r['rebuild_writes']:
        return r, []                        # FULL: no divergence, equal length
    for det in BLIND_DETECTORS:
        s = det(r)
        if s:
            signals.append(s)
    for det in ENGINE_DETECTORS.get(engine, []):
        s = det(orig, rebuild, subtune, r)
        if s:
            signals.append(s)
    signals.sort(key=lambda s: _CONF_RANK[s.confidence])
    return r, signals


def _report(r, signals) -> str:
    out = []
    lo, lr, mp = r['orig_writes'], r['rebuild_writes'], r['match_prefix']
    div = r['first_div']
    if div is None and lo == lr:
        return 'FULL — no divergence, equal length.'
    cap = r.get('capture', '?')
    if div is not None:
        reg, oval, fr, _ = r['orig_flat'][div]
        rreg, rval, *_ = r['rebuild_flat'][div]
        pct = 100 * div / max(lo, lr)
        out.append(f'[capture {cap}] first divergence @ flat {div} '
                   f'({pct:.1f}% through), play {fr}: orig '
                   f'{describe_reg(reg)}=${oval:02X} vs rebuild '
                   f'{describe_reg(rreg)}=${rval:02X}')
    else:
        out.append(f'no content divergence; lengths {lo} vs {lr} '
                   f'(prefix {mp})')
    out.append('')
    if not signals:
        out.append('no signature detector fired — inspect manually '
                   '(find_first_divergence + read the disasm).')
        return '\n'.join(out)
    out.append('LIKELY CLASSES (most confident first):')
    for s in signals:
        out.append(f'  [{s.confidence:4}] {s.klass:8} {s.summary}')
        out.append(f'         evidence: {s.evidence}')
    out.append('')
    ledgers = sorted({k for s in signals for k in s.klass.replace('?', '')
                      .split('/') if k.startswith('C')})
    if ledgers:
        out.append('read: ' + ', '.join(f'docs/ledger/{k}.md' for k in ledgers))
    return '\n'.join(out)


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('orig')
    p.add_argument('rebuild')
    p.add_argument('--subtune', type=int, default=0)
    p.add_argument('--duration', type=float, default=None)
    p.add_argument('--engine', default=None,
                   help='register engine-parametrized detectors (e.g. dmc)')
    args = p.parse_args()
    for f in (args.orig, args.rebuild):
        if not os.path.exists(f):
            print(f'error: not found: {f}', file=sys.stderr)
            return 1
    r, signals = triage(args.orig, args.rebuild, args.subtune,
                        args.duration, args.engine)
    print(_report(r, signals))
    return 0


if __name__ == '__main__':
    sys.exit(main())
