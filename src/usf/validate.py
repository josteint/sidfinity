"""USF — semantic validators (layers 2-4 of the spec).

Layer 1 (grammar) lives in the parser. These passes run AFTER parsing
and BEFORE codegen. They produce precise, actionable error messages.
"""

from __future__ import annotations

import os

from src.usf.types import (
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
    """Layer 3 — duration consistency.

    A pattern that DECLARES `length=` must be fully stated (every row
    carries a duration) and the durations must sum to it. A pattern
    with stated-inherited rows (any duration absent) must NOT declare a
    length (its total is entry-context-dependent); the voice must
    resolve cleanly under the shared inheritance interpreter
    (src/usf/resolve.py) — same walk the composers run."""
    from src.usf.resolve import needs_resolution, resolve_voice
    for sub in usf.subtunes:
        if not isinstance(sub, MusicSubtune):
            continue
        init_by_id = {v.id: v for v in (sub.init.voices if sub.init else [])}
        for voice in sub.voices:
            for pat in voice.patterns:
                stated = [r.duration for r in pat.rows]
                if pat.length is not None:
                    if any(d is None for d in stated):
                        raise UsfValidationError(
                            f'subtune {sub.id} voice {voice.id} pattern '
                            f'{pat.id}: declares length={pat.length} but '
                            f'has stated-inherited rows (omit length=)')
                    actual = sum(stated)
                    if actual != pat.length:
                        raise UsfValidationError(
                            f'subtune {sub.id} voice {voice.id} pattern '
                            f'{pat.id}: durations sum to {actual}, declared '
                            f'length={pat.length}')
            if needs_resolution(voice):
                try:
                    resolve_voice(voice, init_by_id.get(voice.id))
                except Exception as e:
                    raise UsfValidationError(
                        f'subtune {sub.id} voice {voice.id}: stated-row '
                        f'resolution failed: {e}') from e


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


def _check_origin_engine(usf: UsfFile) -> None:
    """`origin_engine` is a MOVE-1 SCAFFOLD and this is its ratchet.

    It is permitted EXACTLY when one file demonstrably requires more than one
    COMPOSER. Two rules make that self-policing:

      * all-or-nothing — if any music subtune names an engine, every one must,
        so a file never half-declares where its subtunes come from;
      * at least two DISTINCT values — a file whose subtunes all name the SAME
        engine needs exactly one composer, so the tag states nothing and is
        refused.

    The second rule is what keeps the pressure on. Without it the field would
    become the cheap answer to any awkward migration, which is precisely how
    the composer-side leak of principle §8 kept re-emerging. 5 Title Tunes is
    the bar: five independent Hubbard '85 sub-engines in one file, unified
    under ONE composer via per-subtune params, no tag — and the unified build
    is 38% the size of the compound one.

    At Move 1 there is one engine-blind composer, so no file can satisfy
    "requires more than one" and the construct is dead by construction.
    """
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    named = [s for s in music if getattr(s, 'origin_engine', None)]
    if not named:
        return
    missing = [s.id for s in music if not getattr(s, 'origin_engine', None)]
    if missing:
        raise UsfValidationError(
            'origin_engine: subtune(s) %s do not name an engine while others '
            'do — it is all-or-nothing (a file must not half-declare where '
            'its subtunes come from)' % ', '.join(str(i) for i in missing))
    distinct = {s.origin_engine for s in named}
    if len(distinct) < 2:
        raise UsfValidationError(
            "origin_engine: every subtune names %r, so this file needs ONE "
            "composer and the field states nothing. It is permitted only when "
            "a file demonstrably requires more than one composer (see "
            "docs/the_principle.md §8); a same-family multi-engine file is "
            "unified under one composer via per-subtune params instead — "
            "5_Title_Tunes is the precedent." % distinct.pop())


def validate(usf: UsfFile, usf_dir: str | None = None) -> None:
    """Run layers 2-4. If `usf_dir` is None, the sidecar check is skipped
    (useful for in-memory tests that don't need on-disk FLACs)."""
    _check_refs(usf)
    _check_lengths(usf)
    _check_origin_engine(usf)
    if usf_dir is not None:
        _check_sidecars(usf, usf_dir)
