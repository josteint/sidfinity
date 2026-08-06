"""I5 — the byte-faithful stated orderlist (buckets-1/2/3 unification).

The engine re-enters the track byte stream past stated commands carrying
live decode state (the transpose register, the persistent sector position),
while the plain stated form assumes path-independent slot arrival. This
module carries the walker's dispatch semantics IN SLOT SPACE so that the
authored byte structure (slots, marks, dual-role bytes, jumps with their
targets, the loop-landing byte) is the stored content and every
path-dependent fact — re-entry offsets, carried transposes,
sector-position bases — is DERIVED, never stored (mechanism in the
interpreter, content in USF; ledger C32/C34).

Two directions, one shared layout:

  notation_from_walk(v)  — build a TrackNotation from a walked DmcVoice
      (walk-time ground truth: `entry_dual` / `loop_target_pos` are recorded
      by `_walk_track`'s own dispatch, so no raw-byte re-parse can drift).
  replay(nt, facts, ...) — unroll the notation with the engine's real
      dispatch (mark-skip on the loop landing, sector-position carry, the
      C34 one-row law, mid-track jump keys, the mod-256 ring closure) into
      the effective structures the walker yields.

`replay(notation_from_walk(v)) == walk(v)` is the fold's acceptance PROOF
(to_usf checks full equality of entries / transposes / offsets / loop /
stop before emitting the stated form; any mismatch keeps the legacy
representation). The composer runs the same replay at COMPOSE TIME to
materialize the unrolled emission — the emitted player is untouched.

Validated standalone against all fold-residue members' fresh walks before
any schema code (tmp/i5_replay_validate.py; design probe
tmp/i5_notation_probe.py, 41/41 voices round-trip exact).
"""
from dataclasses import dataclass, field

_GUARD = 8192          # mirrors _walk_track's never-settles guard


@dataclass
class TrackNotation:
    """The authored byte structure of one voice's track, in slot space.

    Per physical slot i (one pass of the track):
      entries[i]  — steady pattern id (the eternal decode)
      marks[i]    — the stated transpose command before slot i's sector
                    byte, or None = no command byte (the slot INHERITS the
                    running transpose — over the loop wrap included)
      extras[i]   — extra dead command bytes before the mark (each is a
                    byte the engine executes and the mark overrides)
      dual[i]     — slot i is a post-transpose one-row entry whose byte
                    RE-DISPATCHES as the following element (the C34 run-on
                    dual byte): it contributes NO byte of its own — its
                    byte IS the next slot's command / the terminator
      intros[i]   — pass-0 decode where the carried state makes the first
                    visit differ (None = same as entries[i])
      jump_in[i]  — slot i is entered through a mid-track $FF jump landing
                    at absolute track byte `jump_in[i]` (the start of the
                    slot's command block — a new byte region; None = the
                    slot follows its predecessor contiguously). The value
                    is authored layout, observable through the sonified
                    track-position counter.

    Terminator (exactly one):
      stop        — $FE.
      loop_slot   — the $FF lands at `starts[loop_slot] + loop_skip`
                    (loop_skip = command bytes of that block the landing
                    skips; 0 = today's land-on-the-mark semantics, the
                    elidable default).
      endless     — the LAST slot's sector never terminates (8-bit sectpos
                    wrap): the walk freezes there — intro = the lead rows,
                    steady = the repeating period, self-loop (r128).
      ring        — no terminator byte at all: the 8-bit track position
                    wraps mod 256 and the closure is a live state repeat
                    (position, sticky, transpose). Layout must span
                    exactly 256 bytes.
      inject      — the $FF plays one spurious pseudo-row (the C13
                    loop_note_inject wedge) recorded as the LAST slot
                    (sharing the $FF byte), then wraps to byte 0; the
                    closure key carries the transpose.
    """
    entries: list = field(default_factory=list)
    marks: list = field(default_factory=list)
    extras: list = field(default_factory=list)
    dual: list = field(default_factory=list)
    intros: list = field(default_factory=list)
    jump_in: list = field(default_factory=list)
    loop_slot: int | None = None
    loop_skip: int = 0
    stop: bool = False
    endless: bool = False
    ring: bool = False
    inject: bool = False


@dataclass
class RowFacts:
    """The dispatch-relevant facts of one pattern row (engine-neutral: the
    extract adapts DmcRow, the composer adapts USF rows)."""
    width: int                 # orig fetch byte width (INCs of $1729,x)
    dur: int | None = None     # stated duration command value (dcmd)
    instr: int | None = None   # stated instrument command value (icmd)
    vol: int | None = None     # stated volume command value (vcmd)


def facts_from_dmc_rows(rows) -> list:
    """RowFacts from extract-side DmcRow lists (mirrors the walker's
    `consumed` computation and _Sticky updates)."""
    out = []
    for r in rows:
        base = 3 if r.glide_to is not None else (2 if r.glide_slide else 1)
        w = base + int(r.dcmd) + int(r.icmd) + int(r.vcmd) + (r.softcmd or 0)
        out.append(RowFacts(width=w,
                            dur=r.duration if r.dcmd else None,
                            instr=r.instr if r.icmd else None,
                            vol=r.vol if r.vcmd else None))
    return out


def facts_from_usf_rows(rows, width_fn) -> list:
    """RowFacts from composer-side USF NoteRow objects. `width_fn` is the
    composer's byte-width oracle (composer_asm._row_secwidth) so the two
    stay one implementation. The stated-command placement flags
    (dur_cmd / instr_cmd / vol_cmd) mark which values update the sticky
    state — the byte-faithful fold forces them onto every row of a
    materialized voice so the compose-time replay sees what the walk saw.
    Sticky instrument identity uses the USF instrument-ref id: the closure
    key needs only EQUALITY, which any injective renumbering preserves."""
    out = []
    for r in rows:
        flags = {f.split('=')[0]: (f.split('=')[1] if '=' in f else True)
                 for f in r.fx_flags}
        out.append(RowFacts(
            width=width_fn(r),
            dur=r.duration if 'dur_cmd' in flags else None,
            instr=((r.instr.id if r.instr else 0)
                   if 'instr_cmd' in flags else None),
            vol=(int(flags.get('vol', 0) or 0)
                 if 'vol_cmd' in flags else None)))
    return out


def _ownbyte(nt, i):
    """Does slot i occupy a track byte of its own? (A dual slot's byte is
    the next element's; the inject pseudo-slot's byte is the $FF.)"""
    if nt.dual[i]:
        return False
    if nt.inject and i == len(nt.entries) - 1:
        return False
    return True


def layout(nt: TrackNotation):
    """Byte positions of the notation's authored layout. Returns
    (offs, starts, term_pos): offs[i] = slot i's sector-byte position,
    starts[i] = the first byte of slot i's command block (== offs[i] when
    the block is empty), term_pos = the terminator byte's position."""
    offs, starts = [], []
    c = 0
    for i in range(len(nt.entries)):
        if nt.jump_in[i] is not None:
            c = nt.jump_in[i]
        starts.append(c)
        if nt.marks[i] is not None:
            c += (nt.extras[i] or 0) + 1
        offs.append(c)
        if _ownbyte(nt, i):
            c += 1
    return offs, starts, c


class ReplayError(Exception):
    pass


def replay(nt: TrackNotation, pat_facts: dict, instr_seed: int = 0):
    """Unroll the notation with the engine's real dispatch until state
    closure — the walker's semantics in slot space.

    `pat_facts`: pattern id -> list[RowFacts] for every pattern the
    notation references (steady + intro).

    Returns (entries, transposes, offsets, loop_to, stop) — the exact
    shape `_walk_track` yields (entries as pattern ids; loop_to = the
    unrolled index the closure repeats from; offsets = the authored byte
    position of each visit's sector byte).

    Mirrored walker facts: the sticky (dur, instr, vol) state evolves on
    stated commands only; a dual one-row accumulates its width into the
    persistent sector position ($1729,x — zeroed only by entering a
    normal $7F-terminated sector); every $FF (mid-track jump or the loop)
    keys (target, sticky, pending) in ONE shared table — a state repeat
    at ANY $FF closes the walk at the index recorded when that key first
    appeared; the mark a landing skips is NOT re-executed on later
    passes (the carried transpose plays); a ring track closes on a
    (byte position, sticky, transpose) repeat checked at every dispatch
    once the position has wrapped; the inject $FF keys the transpose too
    and plays its pseudo-row before wrapping to byte 0.

    Raises ReplayError when the notation cannot settle or is malformed —
    callers treat that as a refusal, never a crash."""
    P = len(nt.entries)
    if P == 0:
        raise ReplayError('empty notation')
    for name in ('marks', 'extras', 'dual', 'intros', 'jump_in'):
        if len(getattr(nt, name)) != P:
            raise ReplayError(f'{name} length mismatch')
    offs, starts, term_pos = layout(nt)
    for i in range(P):
        if nt.dual[i]:
            if i + 1 < P:
                # the shared byte is the next slot's single command byte,
                # or the $FF of a mid-track jump the next slot is entered
                # through (a post-transpose $FF one-row, Mythig s2v1)
                ok = (nt.jump_in[i + 1] is not None
                      or (nt.marks[i + 1] is not None
                          and not (nt.extras[i + 1] or 0)))
                if not ok:
                    raise ReplayError('dual byte not shared with next mark')
            elif not (nt.stop or nt.loop_slot is not None or nt.ring):
                raise ReplayError('dual tail without terminator')
    if nt.ring and term_pos != 256:
        raise ReplayError(f'ring layout spans {term_pos} bytes, not 256')

    # linear item stream + byte-position -> item index (the command /
    # terminator face wins on a shared byte: a fresh dispatch there sees
    # the command). `top[j]` = the item is dispatched at the walker's loop
    # top (mod-256 ring closure checks happen exactly there): dead / mark
    # bytes, and a slot byte NOT preceded by a mark (an after-mark sector
    # is consumed in the mark's own dispatch).
    n_slots = P - 1 if nt.inject else P
    items, pos_of, top = [], {}, []

    def _add(item, pos=None, is_top=False):
        if pos is not None:
            pos_of.setdefault(pos, len(items))
        items.append(item)
        top.append((pos, is_top))
    for i in range(n_slots):
        if nt.jump_in[i] is not None:
            # the $FF byte sits where the previous element ended; it is
            # dispatched at the walker's loop top (ring mod checks see it)
            jpos = 0 if i == 0 else \
                offs[i - 1] + (1 if _ownbyte(nt, i - 1) else 0)
            _add(('jump', nt.jump_in[i]), jpos, True)
        if nt.marks[i] is not None:
            for k in range(nt.extras[i] or 0):
                _add(('dead', i), starts[i] + k, True)
            _add(('mark', i), starts[i] + (nt.extras[i] or 0), True)
            _add(('slot', i), offs[i] if _ownbyte(nt, i) else None, False)
        else:
            _add(('slot', i), offs[i] if _ownbyte(nt, i) else None, True)
    _add(('term',), term_pos, False)
    land_item = None
    if nt.loop_slot is not None and not (nt.endless or nt.ring):
        land_pos = starts[nt.loop_slot] + (nt.loop_skip or 0)
        land_item = pos_of.get(land_pos)
        if land_item is None:
            raise ReplayError(f'loop landing at unmapped byte {land_pos}')

    ent_out, tr_out, off_out = [], [], []
    cur = 0                       # transpose register
    dur, instr, vol = 0, instr_seed, 0   # _Sticky mirror
    pending = 0                   # persistent sector position carry
    visits = [0] * P
    wrap_seen = {}                # $FF keys (mid-track jumps + the loop)
    mod_seen = {}                 # ring keys (pos, sticky, transpose)
    wrapped = False

    def _play(i):
        nonlocal dur, instr, vol, pending
        pid = (nt.intros[i] if visits[i] == 0 and nt.intros[i] is not None
               else nt.entries[i])
        visits[i] += 1
        ent_out.append(pid)
        tr_out.append(cur)
        off_out.append(offs[i])
        rows = pat_facts.get(pid)
        if rows is None:
            raise ReplayError(f'pattern {pid} facts missing')
        for r in rows:
            if r.dur is not None:
                dur = r.dur
            if r.instr is not None:
                instr = r.instr
            if r.vol is not None:
                vol = r.vol
        if nt.dual[i] or (nt.inject and i == P - 1):
            pending += sum(r.width for r in rows)   # run-on: $1729 carries
        else:
            pending = 0     # a normal sector consumes the carry at entry
                            # and its $7F end marker resets the position

    idx = 0
    for _ in range(_GUARD):
        it = items[idx]
        kind = it[0]
        if wrapped and top[idx][1]:
            key = (top[idx][0], dur, instr, vol, cur)
            if key in mod_seen:
                return ent_out, tr_out, off_out, mod_seen[key], False
            mod_seen[key] = len(ent_out)
        if kind == 'dead':
            idx += 1
        elif kind == 'mark':
            cur = nt.marks[it[1]]
            idx += 1
        elif kind == 'jump':
            tgt = it[1]
            key = (tgt, dur, instr, vol, pending)
            if key in wrap_seen:
                return ent_out, tr_out, off_out, wrap_seen[key], False
            wrap_seen[key] = len(ent_out)
            j = pos_of.get(tgt)
            if j is None:
                raise ReplayError(f'jump target {tgt} unmapped')
            idx = j
        elif kind == 'slot':
            i = it[1]
            _play(i)
            if nt.endless and i == n_slots - 1:
                # unterminated sector: play the steady period once more
                # (the intro visit was the lead) and freeze there — the
                # walker's self-loop encoding (r128)
                if nt.intros[i] is not None:
                    _play(i)
                return ent_out, tr_out, off_out, len(ent_out) - 1, False
            idx += 1
        else:                                   # term
            if nt.stop:
                return ent_out, tr_out, off_out, None, True
            if nt.ring:
                wrapped = True
                idx = 0
                continue
            if nt.inject:
                key = (dur, instr, vol, pending, cur)
                if key in wrap_seen:
                    return ent_out, tr_out, off_out, wrap_seen[key], False
                wrap_seen[key] = len(ent_out)
                _play(P - 1)
                idx = land_item if land_item is not None else pos_of.get(0)
                if idx is None:
                    raise ReplayError('inject landing unmapped')
                continue
            if nt.loop_slot is None:
                return ent_out, tr_out, off_out, None, True
            # SAME key namespace as the mid-track jumps: the walker keeps
            # one wrap table for every $FF, keyed by the TARGET byte — a
            # terminal wrap can close against a mid-track jump's recorded
            # state when both aim at the same landing (Cornflakes v3)
            land_pos = starts[nt.loop_slot] + (nt.loop_skip or 0)
            key = (land_pos, dur, instr, vol, pending)
            if key in wrap_seen:
                return ent_out, tr_out, off_out, wrap_seen[key], False
            wrap_seen[key] = len(ent_out)
            idx = land_item
    raise ReplayError('replay never settles')


def notation_from_walk(v):
    """Build the TrackNotation from a walked DmcVoice. Returns
    (notation, None) or (None, reason). Refuses shapes the notation does
    not model — the caller keeps the legacy representation for those."""
    n = len(v.entries)
    offs = v.entry_offsets
    if not n or not offs or len(offs) != n:
        return None, 'no_offsets'
    dual_w = getattr(v, 'entry_dual', None)
    dual_w = dual_w if dual_w and len(dual_w) == n else [0] * n
    jf = (v.jump_from if len(getattr(v, 'jump_from', ()) or ()) == n
          else [None] * n)
    inject = any(d == 2 for d in dual_w)
    looped = not v.stop and v.loop_to is not None
    ltp = getattr(v, 'loop_target_pos', None)
    # the endless self-loop tail (walker ground truth, r128): the walk
    # froze in an unterminated sector — lead + period chunks (or period
    # alone) at one track byte, loop_to = the last index
    endless = bool(getattr(v, 'endless_tail', False))
    if endless and (inject or not looped or v.loop_to != n - 1):
        return None, 'endless_shape'
    # first-visit slot linearization; pass 0 must BE the physical track
    slot_of, slots = {}, []
    for o in offs:
        s = slot_of.get(o)
        if s is None:
            s = len(slot_of)
            slot_of[o] = s
        slots.append(s)
    P = len(slot_of)
    if slots[:P] != list(range(P)):
        return None, 'pass0_incomplete'
    # per-slot dual flag + visit agreement
    dual = [bool(dual_w[s]) and dual_w[s] != 2 for s in range(P)]
    for j in range(P, n):
        if (bool(dual_w[j]) and dual_w[j] != 2) != dual[slots[j]]:
            return None, 'dual_visit_disagrees'
    if inject:
        if dual_w[P - 1] != 2:
            return None, 'inject_not_last_slot'
        if any(d == 2 for i, d in enumerate(dual_w) if slots[i] != P - 1):
            return None, 'inject_extra_slot'
    # mid-track jump landings (first visits only; the cycle passes'
    # landings come from the loop and are reproduced by the replay)
    jump_in = [None] * P
    for s in range(1, P):
        if jf[s] is not None:
            jump_in[s] = jf[s]
    # marks / extras from the observed gaps (dual-aware: a run-on dual's
    # byte is itself the first command byte of the next block; a jumped
    # slot's block starts at the landing)
    marks, extras = [], []
    for s in range(P):
        if jump_in[s] is not None:
            prev_end = jump_in[s]
        elif s == 0:
            prev_end = 0
        else:
            prev_end = offs[s - 1] + (0 if dual[s - 1] else 1)
        gap = offs[s] - prev_end
        if gap < 0:
            return None, 'negative_gap'
        if gap == 0:
            inherited = v.transposes[s - 1] if s > 0 else 0
            if v.transposes[s] != inherited:
                return None, 'gap0_transpose'
            marks.append(None)
            extras.append(0)
        else:
            marks.append(v.transposes[s])
            extras.append(gap - 1)
        if s > 0 and dual[s - 1] and jump_in[s] is None and \
                (marks[s] is None or extras[s]):
            return None, 'dual_share_shape'
    # steady / intro per slot: steady = the last visit's decode; only the
    # FIRST visit may differ (the carried-state intro variant)
    entries, intros = [None] * P, [None] * P
    by_slot = [[] for _ in range(P)]
    for j, s in enumerate(slots):
        by_slot[s].append(v.entries[j])
    for s in range(P):
        pids = by_slot[s]
        steady = pids[-1]
        entries[s] = steady
        for k, p in enumerate(pids):
            if p != steady:
                if k > 0:
                    return None, 'later_visit_differs'
                intros[s] = p
    nt = TrackNotation(entries=entries, marks=marks, extras=extras,
                       dual=dual, intros=intros, jump_in=jump_in,
                       endless=endless, inject=inject)
    n_offs, n_starts, term_pos = layout(nt)
    if n_offs != offs[:P]:
        return None, 'layout_disagrees'
    if v.stop or v.loop_to is None:
        nt.stop = True
        if dual[P - 1] and not v.stop:
            return None, 'dual_tail_no_term'
        return nt, None
    if endless:
        nt.loop_slot = P - 1
        return nt, None
    if inject:
        nt.loop_slot, nt.loop_skip = 0, 0     # the wedge wraps to byte 0
        return nt, None
    if term_pos == 256:
        # the authored track fills the whole 8-bit page with NO terminator
        # byte: the position wraps mod 256 and closure is a live state
        # repeat — at the wrap ring (Blue_Max) or at a mid-track $FF's key
        # on the re-pass (Cornflakes)
        nt.ring = True
        return nt, None
    if ltp is None:
        return None, 'no_landing'
    L = None
    for s in range(P):
        if n_starts[s] <= ltp <= n_offs[s]:
            L = s
            break
    if L is None:
        if ltp == term_pos:
            return None, 'landing_on_terminator'
        return None, 'landing_unlocatable'
    nt.loop_slot = L
    nt.loop_skip = ltp - n_starts[L]
    return nt, None


def prove_replay(v, nt=None):
    """The fold's acceptance proof: replay(notation) must equal the walk
    EXACTLY (entries, transposes, byte offsets, loop closure, stop).
    Returns (notation, None) on success or (None, reason)."""
    if nt is None:
        nt, why = notation_from_walk(v)
        if nt is None:
            return None, why
    facts = {}
    for pid in set(nt.entries) | {p for p in nt.intros if p is not None}:
        facts[pid] = facts_from_dmc_rows(v.patterns[pid])
    try:
        ents, trs, offs, loop_to, stop = replay(
            nt, facts, instr_seed=getattr(v, 'instr_seed', 0))
    except ReplayError as e:
        return None, f'replay_error:{e}'
    if ents != list(v.entries):
        return None, 'proof_entries'
    if trs != list(v.transposes):
        return None, 'proof_transposes'
    if offs != list(v.entry_offsets):
        return None, 'proof_offsets'
    if loop_to != v.loop_to or stop != bool(v.stop or v.loop_to is None):
        return None, 'proof_closure'
    return nt, None
