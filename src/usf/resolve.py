"""USF stated-row resolution — the shared duration/instrument/volume
inheritance interpreter (stated-duration pattern rows, D6 piece 2).

A NoteRow's duration / instrument / `vol=` flag are STATED notation: a
value is present where the source stream states a command; an absent
value INHERITS the previously played row's value, in orderlist play
order, across pattern boundaries, carrying over the loop wrap. This
module is the one resolution semantics both composers and the Layer-3
validator consume (engine-blind: it reads only USF content).

Seeds (the state before the first played row) come from the subtune's
`init { voice N { dur_field / instr } }` engine-state priming
(trichotomy §4.5); absent fields default to dur 0 / instr None /
vol 0.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.usf.types import NoteRow, VoiceBlock, InitVoice


def _stated_vol(row: NoteRow) -> Optional[int]:
    for f in row.fx_flags:
        if f.startswith('vol='):
            return int(f.split('=', 1)[1])
    return None


@dataclass
class ResolvedRow:
    """One played row with its inheritance resolved. `row` is the
    source NoteRow (statedness intact); the scalars are EFFECTIVE."""
    row: NoteRow
    duration: int
    instr_id: Optional[int]     # None = never stated and no seed
    vol: int


class StickyState:
    """The inheritance state threaded through play order."""

    def __init__(self, dur: int = 0, instr_id: Optional[int] = None,
                 vol: int = 0):
        self.dur, self.instr_id, self.vol = dur, instr_id, vol

    @classmethod
    def from_init_voice(cls, iv: Optional[InitVoice]) -> 'StickyState':
        if iv is None:
            return cls()
        return cls(dur=iv.dur_field or 0,
                   instr_id=iv.instr.id if iv.instr else None,
                   vol=0)


def resolve_rows(rows: list[NoteRow], st: StickyState) -> list[ResolvedRow]:
    """Resolve one pattern-instance's rows, mutating `st`."""
    out = []
    for r in rows:
        if r.duration is not None:
            st.dur = r.duration
        if r.instr is not None and r.instr.id is not None:
            st.instr_id = r.instr.id
        v = _stated_vol(r)
        if v is not None:
            st.vol = v
        out.append(ResolvedRow(row=r, duration=st.dur,
                               instr_id=st.instr_id, vol=st.vol))
    return out


def needs_resolution(voice: VoiceBlock) -> bool:
    """True iff any row omits a duration (the stated-inherited form)."""
    return any(r.duration is None
               for p in voice.patterns for r in p.rows)


def resolve_voice(voice: VoiceBlock,
                  init_voice: Optional[InitVoice] = None,
                  n_passes: int = 2):
    """Resolve a voice's full play order.

    Returns a list of PASSES; each pass is a list of per-orderlist-entry
    resolved row lists. Pass 0 covers every entry from the top; passes
    1..n-1 cover the loop cycle (`loop_to`..end), threading the sticky
    state continuously (the wrap carry). A `stop` orderlist yields one
    pass. Entry repeats (`*r`) thread state through each play but the
    per-entry result lists the FIRST play's resolution (subsequent plays
    inherit through the pattern's own tail at runtime).
    """
    ol = voice.orderlist
    pat_by_id = {p.id: p for p in voice.patterns}
    st = StickyState.from_init_voice(init_voice)
    passes = []
    if not ol.entries:
        return passes
    reps = list(getattr(ol, 'repeats', None) or [])
    for pno in range(n_passes if ol.loop_to is not None else 1):
        start = 0 if pno == 0 else ol.loop_to
        cur = []
        for i in range(start, len(ol.entries)):
            rows = pat_by_id[ol.entries[i]].rows
            first = resolve_rows(rows, st)
            for _ in range((reps[i] if i < len(reps) else 1) - 1):
                resolve_rows(rows, st)      # thread state through replays
            cur.append(first)
        passes.append(cur)
    return passes
