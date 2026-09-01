"""Controls for `compare_split_by_register` — the music+digi split verdict.

The verdict claims two things and each gets a control here:

  1. It DEGENERATES correctly.  With no strict registers it is exactly the
     Mode-1 flat compare; with every register strict it is exactly the
     Mode-2 cycle-strict compare.  A split that did not degenerate would be
     a third verdict rather than a composition of the two the canon has.

  2. It SEPARATES.  A perturbation confined to the digi register must fail
     ONLY the digi side, and a perturbation confined to the music registers
     must fail ONLY the music side.  Without this the "split" could be
     passing both halves of a broken stream, or failing both halves of a
     good one, and no existing test would notice.

Control 2 is run against a REAL capture of a real music+digi member
(a Digi-Organizer member paired with a DMC tune) rather than a synthetic
frame list, so the register populations, the burst shapes and the write
counts are the ones the verdict will actually meet.  Only the perturbation
is synthetic — no composer for these members exists yet, so there is no
rebuild to diff.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pipelines.hubbard.verify_cycle import (          # noqa: E402
    compare_instruction_stream, compare_strict, compare_split_by_register,
    writelog_capture, DIGI_REGS_D418)

# A DMC tune with a Digi-Organizer core, measured `exclusive` on $D418 by
# tools/register_ownership.py (its only $D418 writers are PCs $916B/$918A).
PAIRED = os.path.join(ROOT, 'hvsc85', 'DEMOS', 'G-L',
                      'Lady_with_the_Red_Dress.sid')


@pytest.fixture(scope='module')
def cap():
    if not os.path.exists(PAIRED):
        pytest.skip('HVSC not present')
    frames = writelog_capture(PAIRED, 0, 6.0, force_rsid=True)
    if not frames:
        pytest.skip('capture empty')
    return frames


def _has(frames, regs):
    return any((w[1] & 0x1F) in regs for fr in frames for w in fr)


def test_capture_carries_both_populations(cap):
    """The control member must actually contain music AND digi writes, or
    the separation tests below would pass vacuously."""
    assert _has(cap, DIGI_REGS_D418), 'no $D418 writes — not a digi member'
    assert _has(cap, set(range(0x18))), 'no music writes'


def test_degenerates_to_mode1_with_no_strict_regs(cap):
    got = compare_split_by_register(cap, cap, strict_regs=frozenset())
    want = compare_instruction_stream(cap, cap)
    assert got['music'] == want
    assert got['digi_full'] is True          # empty substream, trivially full
    assert got['is_full'] is True


def test_degenerates_to_mode2_with_all_regs_strict(cap):
    allregs = frozenset(range(0x20))
    got = compare_split_by_register(cap, cap, strict_regs=allregs)
    want = compare_strict(cap, cap)
    assert got['digi'] == want
    assert got['is_full'] is True


def test_identity_is_full(cap):
    assert compare_split_by_register(cap, cap)['is_full'] is True


def _perturb(frames, pred, dcycle=0, dval=0):
    """Copy `frames`, shifting the cycle (or value) of every write matching
    `pred`.  Returns (new_frames, n_changed)."""
    out, n = [], 0
    for fr in frames:
        nf = []
        for cyc, reg, val in fr:
            if pred(reg):
                nf.append((cyc + dcycle, reg, (val + dval) & 0xFF))
                n += 1
            else:
                nf.append((cyc, reg, val))
        out.append(nf)
    return out, n


def test_digi_only_cycle_shift_fails_only_the_digi_side(cap):
    """Move every $D418 write 3 cycles later and nothing else.  Mode 2 must
    reject it (the sample timing IS the waveform); Mode 1 must not even see
    it (it drops cycles by design)."""
    pert, n = _perturb(cap, lambda r: (r & 0x1F) == 0x18, dcycle=3)
    assert n > 100, f'perturbation touched only {n} writes'
    res = compare_split_by_register(cap, pert)
    assert res['digi_full'] is False, 'cycle-strict side missed a cycle shift'
    assert res['music_full'] is True, 'Mode-1 side saw a pure cycle shift'
    assert res['is_full'] is False


def test_music_only_value_change_fails_only_the_music_side(cap):
    """Change one music register's VALUE and nothing else."""
    pert, n = _perturb(cap, lambda r: (r & 0x1F) == 0x01, dval=1)
    if n == 0:
        pytest.skip('control member writes no $D401')
    res = compare_split_by_register(cap, pert)
    assert res['music_full'] is False, 'Mode-1 side missed a value change'
    assert res['digi_full'] is True, 'digi side saw a music-register change'
    assert res['is_full'] is False


def test_music_only_cycle_shift_is_tolerated(cap):
    """Trap B, stated as a test: shifting the MUSIC writes within their
    frame changes nothing about the verdict.  This is the property the
    split exists to preserve — the music half must stay Mode 1 even though
    it now travels beside a cycle-strict half."""
    pert, n = _perturb(cap, lambda r: (r & 0x1F) != 0x18, dcycle=17)
    assert n > 10
    assert compare_split_by_register(cap, pert)['is_full'] is True
