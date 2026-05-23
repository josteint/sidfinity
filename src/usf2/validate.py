"""USF v2 — semantic validators (layers 2-4 of the spec).

Layer 1 (grammar) lives in the parser. These passes run AFTER parsing
and BEFORE codegen. They produce precise, actionable error messages.
"""

from __future__ import annotations

import os

from src.usf2.types import (
    UsfFile, MusicSubtune, DigiSubtune, SfxSubtune, InstrumentRef,
)


class UsfValidationError(Exception):
    """A consistency check failed. Message names the location precisely."""
    pass


def _check_refs(usf: UsfFile) -> None:
    """Layer 2 — every InstrumentRef resolves; every orderlist entry
    references a defined pattern."""
    inst_ids = {i.id for i in usf.instruments}
    inst_names = {i.name for i in usf.instruments if i.name}

    def resolve(ref: InstrumentRef, where: str) -> None:
        if ref.id is not None:
            if ref.id not in inst_ids:
                raise UsfValidationError(
                    f'{where}: instrument id i{ref.id} not defined')
        else:
            if ref.name not in inst_names:
                raise UsfValidationError(
                    f'{where}: instrument name i:{ref.name} not defined')

    # init voices' instr refs
    for v in usf.init.voices:
        if v.instr is not None:
            resolve(v.instr, f'init voice {v.id}')

    # subtunes
    for sub in usf.subtunes:
        if isinstance(sub, MusicSubtune):
            for voice in sub.voices:
                pat_ids = {p.id for p in voice.patterns}
                for pos, entry in enumerate(voice.orderlist.entries):
                    if entry not in pat_ids:
                        raise UsfValidationError(
                            f'subtune {sub.id} voice {voice.id} orderlist '
                            f'position {pos}: pattern {entry} not defined')
                if voice.orderlist.loop_to is not None:
                    lp = voice.orderlist.loop_to
                    if lp < 0 or lp >= len(voice.orderlist.entries):
                        raise UsfValidationError(
                            f'subtune {sub.id} voice {voice.id}: '
                            f'loop@{lp} out of range '
                            f'(orderlist has {len(voice.orderlist.entries)} entries)')
                for pat in voice.patterns:
                    for ri, row in enumerate(pat.rows):
                        if row.instr is not None:
                            resolve(
                                row.instr,
                                f'subtune {sub.id} voice {voice.id} '
                                f'pattern {pat.id} row {ri}')


def _check_lengths(usf: UsfFile) -> None:
    """Layer 3 — each pattern's row durations sum to declared length."""
    for sub in usf.subtunes:
        if not isinstance(sub, MusicSubtune):
            continue
        for voice in sub.voices:
            for pat in voice.patterns:
                actual = sum(r.duration for r in pat.rows)
                if actual != pat.length:
                    raise UsfValidationError(
                        f'subtune {sub.id} voice {voice.id} pattern '
                        f'{pat.id}: durations sum to {actual}, declared '
                        f'length={pat.length}')


def _check_sidecars(usf: UsfFile, usf_dir: str) -> None:
    """Layer 4 — every digi subtune's `sample:` exists in `usf_dir`."""
    for sub in usf.subtunes:
        if not isinstance(sub, DigiSubtune):
            continue
        path = os.path.join(usf_dir, sub.sample)
        if not os.path.isfile(path):
            raise UsfValidationError(
                f'subtune {sub.id}: sample file {sub.sample!r} not found '
                f'next to the .usf (looked in {usf_dir})')


def validate(usf: UsfFile, usf_dir: str | None = None) -> None:
    """Run layers 2-4. If `usf_dir` is None, the sidecar check is skipped
    (useful for in-memory tests that don't need on-disk FLACs)."""
    _check_refs(usf)
    _check_lengths(usf)
    if usf_dir is not None:
        _check_sidecars(usf, usf_dir)
