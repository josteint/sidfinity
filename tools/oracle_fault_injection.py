#!/usr/bin/env python3
"""oracle_fault_injection.py — measure what the write-stream verdict CANNOT see.

We have a great deal of evidence that the verdict is SOUND (a FULL member
really does reproduce the original's writes) and none at all about its
STRENGTH: what could be wrong with a rebuild and still pass? Trap B's boundary
in the_core_tenet.md is one known blind spot, and it was found BY EAR, on
Techno-Rap, after a confident FULL had been recorded.

This makes the question mechanical. Take a real member's ground-truth capture,
apply a catalogue of single, well-understood mutations to a copy, and ask the
comparator whether it notices. The output is a KILL RATE and, more usefully, a
named list of mutations that survive.

That converts "cycles within a frame are observation, not signal" from an
axiom the project asserts into a claim it has measured. NIST SP 800-142 names
the oracle problem as the chief practical limit of combinatorial testing; we
are unusual in having an exact oracle, so it is worth knowing its edges.

⚠ A SURVIVING MUTATION IS NOT AUTOMATICALLY A BUG. Some are deliberate:
within-frame CYCLE POSITION is explicitly not signal (Trap B), so a mutation
that only moves cycles SHOULD survive. What matters is whether each survivor
is one we INTENDED to be invisible. The report separates them.

Usage:
    python3 tools/oracle_fault_injection.py                       # defaults
    python3 tools/oracle_fault_injection.py --sid DEMOS/G-L/Katusha.sid
    python3 tools/oracle_fault_injection.py --duration 8
"""
from __future__ import annotations

import argparse
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.tslog import ts, phase                                   # noqa: E402
from pipelines.hubbard.verify_cycle import (                      # noqa: E402
    writelog_per_irq_capture, compare_instruction_stream)


# ---------------------------------------------------------------------------
# Mutations. Each takes the per-IRQ chunk list and returns a mutated copy.
# `intended_invisible` marks the ones the Core Tenet deliberately does not
# treat as signal — surviving those is correct behaviour, not a gap.
# ---------------------------------------------------------------------------

def _first_nonempty(chunks, start=1):
    for i in range(start, len(chunks)):
        if chunks[i]:
            return i
    return None


def m_drop_one_d418(ch):
    """Drop a single $D418 write (master volume / filter mode)."""
    out = copy.deepcopy(ch)
    for i in range(1, len(out)):
        for j, w in enumerate(out[i]):
            if w[-2] == 0x18:
                del out[i][j]
                return out
    return None


def m_drop_one_write(ch):
    """Drop one arbitrary write from the middle of the song."""
    out = copy.deepcopy(ch)
    i = _first_nonempty(out, len(out) // 2)
    if i is None:
        return None
    del out[i][0]
    return out


def m_duplicate_one_write(ch):
    out = copy.deepcopy(ch)
    i = _first_nonempty(out, len(out) // 2)
    if i is None:
        return None
    out[i].insert(0, out[i][0])
    return out


def m_swap_within_frame(ch):
    """Swap two adjacent writes INSIDE one play() call."""
    out = copy.deepcopy(ch)
    for i in range(1, len(out)):
        if len(out[i]) >= 2 and out[i][0][-2:] != out[i][1][-2:]:
            out[i][0], out[i][1] = out[i][1], out[i][0]
            return out
    return None


def m_swap_across_frames(ch):
    """Move one write from the end of a frame to the start of the next."""
    out = copy.deepcopy(ch)
    for i in range(1, len(out) - 1):
        if out[i] and out[i + 1]:
            w = out[i].pop()
            out[i + 1].insert(0, w)
            return out
    return None


def m_value_off_by_one(ch):
    """Change one written VALUE by 1 (a note a hair out of tune)."""
    out = copy.deepcopy(ch)
    i = _first_nonempty(out, len(out) // 2)
    if i is None:
        return None
    w = list(out[i][0])
    w[-1] = (w[-1] + 1) & 0xFF
    out[i][0] = tuple(w)
    return out


def m_wrong_register(ch):
    """Send one write to the neighbouring register."""
    out = copy.deepcopy(ch)
    i = _first_nonempty(out, len(out) // 2)
    if i is None:
        return None
    w = list(out[i][0])
    w[-2] = (w[-2] + 1) % 0x19
    out[i][0] = tuple(w)
    return out


def m_shift_voice_one_frame(ch):
    """Delay every V2 write ($D407-$D40D) by one play() call.

    The single most musically severe mutation here: one voice plays 20 ms
    late against the other two for the whole song.
    """
    out = copy.deepcopy(ch)
    carry = []
    for i in range(1, len(out)):
        keep = [w for w in out[i] if not (0x07 <= w[-2] <= 0x0D)]
        move = [w for w in out[i] if 0x07 <= w[-2] <= 0x0D]
        out[i] = carry + keep
        carry = move
    return out


def m_leading_blank_frames(ch, n=2):
    """Insert n silent play() calls at the front — the whole tune runs late.

    MEASURED BLIND SPOT (2026-08-22): this is exactly what the v5 composer did
    to every family-4 member by emitting family-3's `playskip = 2`. An empty
    play() contributes nothing to the concatenated stream, so the flat verdict
    is structurally incapable of noticing.
    """
    out = copy.deepcopy(ch)
    return [out[0]] + [[] for _ in range(n)] + out[1:]


def m_truncate_tail(ch, k=40):
    """Lose the last k writes (a song that stops slightly early)."""
    out = copy.deepcopy(ch)
    removed = 0
    for i in range(len(out) - 1, 0, -1):
        while out[i] and removed < k:
            out[i].pop()
            removed += 1
        if removed >= k:
            break
    return out


def m_shuffle_frame_order(ch):
    """Reverse the write order of one whole play() call."""
    out = copy.deepcopy(ch)
    for i in range(1, len(out)):
        if len(out[i]) >= 3:
            out[i] = list(reversed(out[i]))
            return out
    return None


def m_cycle_jitter(ch):
    """Move every write's CYCLE within its frame, changing nothing else.

    INTENDED INVISIBLE: the Core Tenet's Trap B says within-frame cycle
    position is observation, not signal. If this one is ever caught, the
    comparator is stricter than the doctrine.
    """
    out = copy.deepcopy(ch)
    for i in range(1, len(out)):
        out[i] = [(max(0, w[0] // 2),) + tuple(w[1:]) if len(w) >= 3 else w
                  for w in out[i]]
    return out


MUTATIONS = [
    ('drop_one_d418', m_drop_one_d418, False),
    ('drop_one_write', m_drop_one_write, False),
    ('duplicate_one_write', m_duplicate_one_write, False),
    ('swap_within_frame', m_swap_within_frame, False),
    ('swap_across_frames', m_swap_across_frames, False),
    ('value_off_by_one', m_value_off_by_one, False),
    ('wrong_register', m_wrong_register, False),
    ('shift_voice_one_frame', m_shift_voice_one_frame, False),
    ('leading_blank_frames', m_leading_blank_frames, False),
    ('truncate_tail_40', m_truncate_tail, False),
    ('reverse_one_frame', m_shuffle_frame_order, False),
    ('cycle_jitter', m_cycle_jitter, True),
]


def judge(base, mutant) -> bool:
    """True iff the verdict CATCHES the mutation (i.e. no longer FULL).

    Uses the same two-sided comparison the DMC v5 verdict applies: end-of-init
    chip state (Check A) plus the flattened play stream (Check B).
    """
    def st(ch):
        return {reg: val for (_c, reg, val) in (ch[0] if ch else [])}
    if st(base) != st(mutant):
        return True
    r = compare_instruction_stream(base[1:], mutant[1:])
    la, lb = r['len_all_a'], r['len_all_b']
    ok = (r['match_all'] == min(la, lb)
          and abs(la - lb) <= max(128, max(la, lb) // 200))
    return not ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sid', default='DEMOS/G-L/Katusha.sid',
                    help='HVSC-relative member to capture (any will do)')
    ap.add_argument('--subtune', type=int, default=0)
    ap.add_argument('--duration', type=float, default=12.0)
    a = ap.parse_args()
    orig = os.path.join(ROOT, 'hvsc85', a.sid)
    if not os.path.exists(orig):
        ts(f'no such member: {orig}')
        return 2

    with phase(f'capture {a.sid} sub {a.subtune} for {a.duration}s'):
        base = writelog_per_irq_capture(orig, subtune=a.subtune,
                                        duration=a.duration, keep_init=True)
    n_w = sum(len(c) for c in base)
    ts(f'{len(base)} play() chunks, {n_w} writes')
    ts('sanity: an unmutated copy must pass -> '
       f'{"FAIL (BUG)" if judge(base, copy.deepcopy(base)) else "passes"}')

    caught, survived, skipped = [], [], []
    with phase(f'{len(MUTATIONS)} mutations'):
        for name, fn, intended in MUTATIONS:
            mut = fn(base)
            if mut is None:
                skipped.append(name)
                ts(f'  {name:24s} SKIPPED (no applicable site)')
                continue
            hit = judge(base, mut)
            tag = 'CAUGHT ' if hit else ('survived (intended)' if intended
                                         else 'SURVIVED')
            ts(f'  {name:24s} {tag}')
            (caught if hit else survived).append((name, intended))

    real = [n for n, i in survived if not i]
    ts('')
    ts(f'KILL RATE: {len(caught)}/{len(caught) + len(survived)} '
       f'({100 * len(caught) / max(1, len(caught) + len(survived)):.0f}%)')
    if real:
        ts(f'UNINTENDED SURVIVORS ({len(real)}) — the oracle is blind to these:')
        for n in real:
            ts(f'    {n}')
    else:
        ts('No unintended survivors.')
    for n, i in survived:
        if i:
            ts(f'(by design, survived: {n} — Trap B says cycles are not signal)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
