"""DMC V4 model → USF.

Maps the path-resolved DmcModel onto the engine-neutral USF schema:

- sectors → per-voice patterns (NoteRow: pitch/duration/instr +
  `vol=N` / `noretrig` / `gate_toggle` / `glide=N` / `glide_to=P` flags)
- tracks → orderlists with signed per-entry transposes + loop/stop
- instruments → adsr / pwm (bidirectional + speed_steps) / vibrato
  (onset + amplitude + ramp) / envelope.gate_mode / slide ('run',
  half_rate) / filter_prog / waveform + wave_freq + loop / effects
- filter definitions → the duration-based filter_programs shape
- per-subtune speed → tempo; master vol + the $D417 routing-shadow
  leftover → per-subtune init.sid priming (trichotomy: priming, not
  reset — the play loop's $D417 writes read this state)

The freq table IS carried (per-tune tuning content — members ship
edited or wholly different temperaments). The per-note vibrato-depth
curve stays a fixed engine constant (mechanism, identical family-wide).
"""
from __future__ import annotations

import os
import re

from src.usf.types import (
    Environment,
    UsfFile, PsidMeta, Params, InitState, InitSid, InitFilter, InitVoice,
    Instrument, PwmConfig, VibratoConfig, EnvelopeConfig,
    FreqSlideConfig, FilterProgConfig, ArpConfig,
    MusicSubtune, VoiceBlock, Orderlist, Pattern, NoteRow, Pitch,
    InstrumentRef, DmcSfxSubtune,
)
from src.usf.writer import write_file
from pipelines.dmc.v4.config import DMCV4Config
from pipelines.dmc.v4.extract.engine_model import (
    extract, DmcModel, DmcRow, NOTE_NAMES,
)


def _pitch(note: int) -> Pitch:
    return Pitch(name=NOTE_NAMES[note % 12], octave=note // 12)


# Sector-position window idx (per-voice $1729-$172B), for the row-command gate.
_SECTPOS_IDX = {(0x1729 + k) - 0x16A7 for k in range(3)} \
    | {(0x1729 + k) - 0x1647 for k in range(3)}


def _offtable_live_idx() -> set:
    """The window indices a canon-geometry off-table read is served LIVE from —
    the single source of truth lives in the composer (offtable_live_idx), shared
    so extract's per-read `live` stamp and the composer's redirect derivation
    can't disagree on geometry."""
    from pipelines.dmc.composer_asm import offtable_live_idx
    return offtable_live_idx()


def _stamp_live(recs, canon: bool) -> list:
    """Tag each off-table read `(off, note, lo, hi)` whose canon-geometry
    window landing sonifies a live-varying value.

    Phase 3 (live-signal modulation §3): each live slot becomes a NAMED
    `LiveSignal` reference — the lo slot for the flo-window landing
    ($1647+idx), the hi slot for the fhi-window landing ($16A7+idx) —
    replacing the bare 5-tuple `live` flag. Replacing a slot drops its
    captured byte — dense signals' captures were noise, and the SPARSE
    glide seeds (the one load-bearing case, ledger C11) now travel as
    typed init.voice_state priming (glide_note/glide_target — draft §8
    option (a), the trichotomy §4.5 home). The SIDFINITY_SIG_OLDFORM A/B
    lever was retired at the phase-5 corpus sync (2026-07-29) — the v4
    corpus is mass-written in the signal form; the legacy `live` 5-tuple
    remains parseable only for the not-yet-migrated v5/family-2 stored
    files. Static reads stay plain 4-tuples so non-off-table engines are
    byte-identical."""
    from src.usf.types import LiveSignal
    from pipelines.dmc.composer_asm import signal_for_addr
    live_idx = _offtable_live_idx()
    out = []
    for rec in recs:
        off, note, lo, hi = rec[:4]
        idx = (off + note) & 0xFF
        if canon and idx in live_idx:
            slo = signal_for_addr(0x1647 + idx)
            shi = signal_for_addr(0x16A7 + idx)
            out.append((off, note,
                        LiveSignal(*slo) if slo else lo,
                        LiveSignal(*shi) if shi else hi))
        else:
            out.append((off, note, lo, hi))
    return out


def _row_to_usf(r: DmcRow, cmd_flags: bool = False) -> NoteRow:
    flags = []
    if r.vol:
        flags.append(f'vol={r.vol}')
    if cmd_flags:
        # stated-command placement (arrangement, §8): emitted only for members
        # whose off-table freq reads sonify the sector-position counter
        # ($1729-$172B) — the composer derives each row's orig byte width
        # (base + stated commands) to keep a live sectpos,x shadow.
        if r.dcmd:
            flags.append('dur_cmd' if int(r.dcmd) <= 1
                         else f'dur_cmd={int(r.dcmd)}')
        if r.icmd:
            flags.append('instr_cmd' if int(r.icmd) <= 1
                         else f'instr_cmd={int(r.icmd)}')
        if r.vcmd:
            flags.append('vol_cmd' if int(r.vcmd) <= 1
                         else f'vol_cmd={int(r.vcmd)}')
        if r.softcmd:
            flags.append(f'soft_cmd={r.softcmd}')
    if getattr(r, 'tempo', None) is not None:
        flags.append(f'tempo={r.tempo}')
    if r.gate_toggle:
        flags.append('gate_toggle')
    if r.soft or r.glide_slide:
        flags.append('noretrig')
    if r.glide_speed or r.glide_slide or r.glide_to is not None:
        # glide/slide rows ALWAYS carry glide=N, including speed 0 (ledger
        # C22 — the encoding must be injective over engine ops). Mode 1: a
        # $Dx slide with a zero speed nibble is the engine's "set target,
        # no note load, hold" — suppressing glide=0 rendered it identically
        # to a plain soft note and the composer LOADED the note early
        # (Apocalypsa: octave drop 10 frames before the orig). Mode 0: a
        # $Cx glide with a zero speed nibble is the engine's GLIDE-CANCEL
        # ($1136 stores 0 to glsp) — suppressing it rendered a plain note,
        # so a previous row's armed glide kept ramping the freq accumulator
        # in the rebuild (Grave_Story_intro +$10/frame; the ×16-quantized
        # deep freq drift class, family-1 round 19).
        flags.append(f'glide={r.glide_speed}')
    if r.glide_to is not None:
        flags.append(f'glide_to={_pitch(r.glide_to)}')
    if getattr(r, 'runon', False):
        # run-on row: no $7F end-marker follows in the source stream — the
        # engine's sector position is NOT reset after this row (feeds the
        # composer's sectpos-shadow base threading).
        flags.append('runon')
    if r.note is None:
        return NoteRow(pitch=Pitch.rest(), duration=r.duration,
                       fx_flags=tuple(flags))
    return NoteRow(pitch=_pitch(r.note), duration=r.duration,
                   instr=InstrumentRef(id=r.instr + 1),
                   fx_flags=tuple(flags))


def _row_to_usf_stated(r: DmcRow, cmd_flags: bool) -> NoteRow:
    """STATED row form (D6 piece 2): duration / instrument / volume are
    carried only where the sector stream states the command byte — value
    presence is the byte fact; an absent value INHERITS the previously
    played row's, per src/usf/resolve.py. One physical sector is
    therefore ONE pattern regardless of entry sticky state (the `~intro`
    decode variants dissolve). `cmd_flags` (sectpos-sonified members
    only — arrangement, §8, the same gate as the effective form) keeps
    the dur_cmd/instr_cmd/vol_cmd/soft_cmd placement flags: on stated
    rows they are redundant with value presence, but they keep the
    composer's sectpos byte-width math on ONE unambiguous source
    (fallback voices carry flags without presence semantics — presence-
    based widths there would miscount)."""
    flags = []
    if r.vcmd:
        flags.append(f'vol={r.vol}')
    if cmd_flags:
        if r.dcmd:
            flags.append('dur_cmd' if int(r.dcmd) <= 1
                         else f'dur_cmd={int(r.dcmd)}')
        if r.icmd:
            flags.append('instr_cmd' if int(r.icmd) <= 1
                         else f'instr_cmd={int(r.icmd)}')
        if r.vcmd:
            flags.append('vol_cmd' if int(r.vcmd) <= 1
                         else f'vol_cmd={int(r.vcmd)}')
        if r.softcmd:
            flags.append(f'soft_cmd={r.softcmd}')
    if getattr(r, 'tempo', None) is not None:
        flags.append(f'tempo={r.tempo}')
    if r.gate_toggle:
        flags.append('gate_toggle')
    if r.soft or r.glide_slide:
        flags.append('noretrig')
    if r.glide_speed or r.glide_slide or r.glide_to is not None:
        flags.append(f'glide={r.glide_speed}')
    if r.glide_to is not None:
        flags.append(f'glide_to={_pitch(r.glide_to)}')
    if getattr(r, 'runon', False):
        flags.append('runon')       # no $7F follows: sectpos not reset
    dur = r.duration if r.dcmd else None
    instr = InstrumentRef(id=r.instr + 1) if r.icmd else None
    pitch = Pitch.rest() if r.note is None else _pitch(r.note)
    return NoteRow(pitch=pitch, duration=dur, instr=instr,
                   fx_flags=tuple(flags))


def _stated_voice_form(v, ents, intros, loop_slot, soft_flags):
    """Fold a walked voice's EFFECTIVE pattern pool into the stated form.

    Returns (patterns_rows, entries, needs_instr_seed) — the deduped
    stated pattern pool (list of row-lists, ids = list index), the
    remapped physical entries, and whether a leading note row consumes
    the engine's init instrument (the walk's `v.instr_seed` — the $1015,x
    work-file leftover, 0 when cleared/dead; emitted as per-subtune
    `init { voice N { instr: i<seed+1> } }` priming so the USF stays
    the complete spec) — or None when the stated form fails to reproduce
    the walk's effective decode (caller keeps the effective representation
    wholesale; no member downgrades).

    Verification is the C32 discipline: re-run the SHARED resolver
    (src/usf/resolve.py) over the stated notation (intro pass + steady
    cycle, sticky threading) and require the resolved effective
    (duration, instrument, volume) of every row in BOTH passes to equal
    the walk's ground truth.
    """
    stated = [[_row_to_usf_stated(r, soft_flags) for r in rows]
              for rows in v.patterns]

    def _key(rows):
        return tuple((r.pitch.name, r.pitch.octave, r.duration,
                      r.instr.id if r.instr else None, r.fx_flags)
                     for r in rows)

    remap, pool = {}, []
    key_to_id = {}
    for pid, rows in enumerate(stated):
        k = _key(rows)
        nid = key_to_id.get(k)
        if nid is None:
            nid = len(pool)
            key_to_id[k] = nid
            pool.append(rows)
        remap[pid] = nid
    # the intro variant must MERGE with its steady slot (probe: 100% of
    # variants are sticky-channel carry; anything else falls back)
    for sl, ip in enumerate(intros):
        if ip is not None and remap[ip] != remap[ents[sl]]:
            return None
    entries = [remap[p] for p in ents]

    # consistency: shared-resolver re-derivation vs the walk's decode
    from src.usf.resolve import StickyState, resolve_rows
    st = StickyState(dur=0, instr_id=None, vol=0)
    needs_instr_seed = False
    vol_inherit_active = False

    def _check_pass(slot_range, eff_pids):
        nonlocal needs_instr_seed, vol_inherit_active
        for sl, pid_eff in zip(slot_range, eff_pids):
            rows = pool[entries[sl]]
            resolved = resolve_rows(rows, st)
            eff = v.patterns[pid_eff]
            if len(resolved) != len(eff):
                return False
            for rr, dr in zip(resolved, eff):
                if rr.duration != dr.duration or rr.vol != dr.vol:
                    return False
                if dr.vol and not any(f.startswith('vol=')
                                      for f in rr.row.fx_flags):
                    vol_inherit_active = True
                if rr.instr_id is None:
                    if dr.instr != v.instr_seed:
                        return False
                    needs_instr_seed = True
                elif rr.instr_id != dr.instr + 1:
                    return False
        return True

    n = len(ents)
    pass0 = [intros[sl] if intros[sl] is not None else ents[sl]
             for sl in range(n)]
    if not _check_pass(range(n), pass0):
        return None
    if loop_slot is not None:
        if not _check_pass(range(loop_slot, n),
                           [ents[sl] for sl in range(loop_slot, n)]):
            return None
    # DISCRIMINABILITY guard: the composer detects stated-row voices by
    # dur/instr inheritance (vol alone can't discriminate stated from
    # effective). A voice with NO dur/instr inheritance but ACTIVE vol
    # inheritance (a flagless row whose effective volume is nonzero)
    # would be misread as effective — keep such a voice on the effective
    # representation wholesale.
    has_marker = any(
        r.duration is None or (not r.pitch.is_rest and r.instr is None)
        for rows in pool for r in rows)
    if vol_inherit_active and not has_marker:
        return None
    return pool, entries, needs_instr_seed


def _instrument_to_usf(inst, wavepos_layout: bool = False,
                       canon: bool = True,
                       wave_norm: bool = False) -> Instrument:
    effects = set()
    if inst.drum:
        effects.add('drum')
    if inst.noise_attack:
        effects.add('noise_attack')
    wave_freq = inst.wave_freq
    if not inst.drum:
        # melodic: per-step semitone offsets, signed
        wave_freq = [b - 256 if b >= 128 else b for b in wave_freq]
    slide = FreqSlideConfig()
    vib = VibratoConfig(onset=inst.vib_delay, amplitude=inst.vib_width,
                        ramp=0 if inst.dual else inst.vib_ramp)
    if inst.dual:
        slide = FreqSlideConfig(mode='run', step=inst.slide_step,
                                initial_dir=inst.slide_dir, half_rate=True)
    return Instrument(
        id=inst.id + 1,
        # normal form: the wave content lives in the file-level wave_table;
        # this instrument is a pointer (the composer re-derives the
        # resolved copies through the shared resolver)
        waveform=[] if wave_norm else list(inst.wave_ctrl),
        loop=0 if wave_norm else inst.wave_loop,
        wave_freq=[] if wave_norm else wave_freq,
        wave_start=inst.wave_start if wave_norm else None,
        adsr=(inst.ad, inst.sr),
        offtable_freq=_stamp_live(inst.offtable_freq, canon),
        # editor wave-table position (arrangement) — only for members whose
        # off-table reads sonify a live wave position (see DmcModel)
        wave_table_pos=inst.wave_pool_pos if wavepos_layout else None,
        # editor "start at the loop marker" idiom — the first-read chase writes
        # $171F=n; carried only when an off-table read sonifies that scratch
        wave_start_on_marker=inst.wave_start_on_marker,
        pwm=PwmConfig(mode='bidirectional',
                      init=inst.pw_init_hi << 8,
                      min_hi=inst.pw_bound_a, max_hi=inst.pw_bound_b,
                      speed_steps=list(inst.pw_steps),
                      keep_running=inst.pw_keep_running),
        arp=ArpConfig(offsets=[]),
        vibrato=vib,
        envelope=EnvelopeConfig(gate_mode=inst.gate_mode,
                                gate_open=inst.gate_open),
        freq_slide_config=slide,
        filter_prog=FilterProgConfig(
            program=(inst.filter_def + 1) if inst.filter_on else 0,
            keep_running=inst.filter_keep_running),
        effects=frozenset(effects),
    )


def _fold_stated_orderlist(v):
    """Fold _walk_track's state-closure unroll into the PHYSICAL stated
    form (the de-unroll, 2026-07-18): one pass of physical entries with
    per-entry STATED transpose-command marks (directly observed from the
    track's byte offsets — a command byte is either there or not; no
    fitting), per-slot INTRO-pass decode variants where the loop-carried
    sector state makes the first decode differ, and a physical loop slot.
    The composer re-derives the unrolled emission (full pass + cycle),
    the effective transposes of both passes, and the byte-offset counter
    values the off-table reads sonify — all from this form; the fitted
    otrk_pad/otrk_period/otrk_rcmd params are gone.

    Returns (entries, marks, extras, intros, loop_slot_or_None) or None
    when the walk output doesn't fit the universal 2-pass rho structure
    (→ caller keeps the legacy representation + otrk_legacy flag)."""
    n = len(v.entries)
    offs = v.entry_offsets
    if not offs or len(offs) != n:
        return None

    def _marks_for(prefix_lo, prefix_hi):
        """Derive (mark, extra) per slot in [prefix_lo, prefix_hi) from
        the observed byte offsets; None on inconsistency."""
        marks, extras = [], []
        for i in range(prefix_lo, prefix_hi):
            prev_end = (offs[i - 1] + 1) if i > prefix_lo else 0
            gap = offs[i] - prev_end     # command bytes before this sector
            if gap < 0:
                return None
            if gap == 0:
                # no command byte: transpose must be inherited unchanged
                inherited = v.transposes[i - 1] if i > prefix_lo else 0
                if v.transposes[i] != inherited:
                    return None
                marks.append(None)
                extras.append(0)
            else:
                marks.append(v.transposes[i])
                extras.append(gap - 1)
        return marks, extras

    if v.stop or v.loop_to is None:
        r = _marks_for(0, n)
        if r is None:
            return None
        marks, extras = r
        return list(v.entries), marks, extras, [None] * n, None

    # rho structure: pass0 = slots 0..B-1 (whole physical track), then the
    # cycle (loop target .. end) walked once more until state closure.
    B = n
    for i in range(1, n):
        if offs[i] <= offs[i - 1]:
            B = i
            break
    if B == n or v.loop_to != B:
        return None
    r = _marks_for(0, B)
    if r is None:
        return None
    marks, extras = r
    # align cycle entries to physical slots by byte offset (exact identity)
    off_to_slot = {offs[i]: i for i in range(B)}
    slots = [off_to_slot.get(offs[j]) for j in range(B, n)]
    if any(sl is None for sl in slots):
        return None
    S = slots[0]
    if slots != list(range(S, S + len(slots))) or S + len(slots) != B:
        return None
    # steady decode = cycle pass; intro decode = pass0 where it differs.
    # An intro/loop variant pair may differ ONLY in carried (unstated)
    # instr/vol — the class the composer's stated encoding ERASES, so both
    # passes produce the same encoded pattern and one physical slot serves
    # them. A pair differing in STATED content or duration (the mid-sector
    # loop re-entry that SKIPS the sector's leading command bytes: the $FF
    # loop inherits the sector position, Creo/Dance's `...$A0 $FF` tail)
    # encodes differently per pass — one slot cannot carry both, so refuse
    # and let the legacy unrolled representation carry the member.
    def _stated_equal(a, b):
        if len(a) != len(b):
            return False
        for r, s in zip(a, b):
            if (r.duration, r.note, r.soft, r.gate_toggle, r.glide_speed,
                    r.glide_to, r.glide_slide, r.dcmd, r.icmd, r.vcmd,
                    r.softcmd) != \
               (s.duration, s.note, s.soft, s.gate_toggle, s.glide_speed,
                    s.glide_to, s.glide_slide, s.dcmd, s.icmd, s.vcmd,
                    s.softcmd):
                return False
            if r.icmd and r.instr != s.instr:
                return False
            if r.vcmd and r.vol != s.vol:
                return False
        return True

    entries = list(v.entries[:B])
    intros = [None] * B
    # ENDLESS-TAIL admission (r128): a voice ending in an unterminated
    # (mod-256 wrapped) sector walks to [.., lead, period] at ONE track
    # byte — a SELF-LOOP slot whose pass-0 decode (lead) genuinely differs
    # from its steady decode (period) in stated content. Scoped to exactly
    # that shape: cycle length 1, equal observed offsets, loop_to = the
    # tail slot — the Creo/Dance mid-sector-reentry refusal below stands
    # for every longer cycle. The composer plays the intro entry once and
    # loops on the steady entry at the SAME otrk value (the orig's frozen
    # wrap position).
    self_loop_tail = (len(slots) == 1 and S == B - 1
                      and offs[B] == offs[B - 1])
    for j in range(B, n):
        sl = slots[j - B]
        if v.entries[j] != entries[sl]:
            if not self_loop_tail and \
               not _stated_equal(v.patterns[entries[sl]],
                                 v.patterns[v.entries[j]]):
                return None
            intros[sl] = entries[sl]        # intro variant = pass-0 decode
            entries[sl] = v.entries[j]      # base = steady decode
    # verify the derived effective transposes reproduce BOTH walked passes:
    # pass0 from cur=0, cycle continuing from pass0's end value
    cur = 0
    eff0 = []
    for i in range(B):
        if marks[i] is not None:
            cur = marks[i]
        eff0.append(cur)
    if eff0 != list(v.transposes[:B]):
        return None
    cur = eff0[-1]
    for j in range(B, n):
        sl = slots[j - B]
        if marks[sl] is not None:
            cur = marks[sl]
        if cur != v.transposes[j]:
            return None
    return entries, marks, extras, intros, S


def _otrk_model(v):
    """The otrk phase scalars (pad, period): the engine's track counter
    ($1726,x) counts BYTES of the orig encoding, where a transpose command
    byte is editor-placed — usually on change, but sometimes redundantly
    (measured: a leading constant, {+1: 146} of 540 tracks). The composer
    derives per-entry offsets as transpose-CHANGE count + PAD (the
    dual_phase-style phase scalar), resetting every PERIOD entries — the
    physical track length the loop-unrolling walk obscured (offsets are
    periodic because each pass re-reads the same bytes). Returns (pad,
    period) only when the model reproduces the walked ground-truth offsets
    EXACTLY; None = keep the plain derivation (piecewise mid-track
    redundancy — the documented residue tail)."""
    n = len(v.entries)
    if not v.entry_offsets or len(v.entry_offsets) != n:
        return None
    # physical period = first offset reset (loop-unrolled walks); else n
    period = n
    for i in range(1, n):
        if v.entry_offsets[i] <= v.entry_offsets[i - 1]:
            period = i
            break
    pad = v.entry_offsets[0]      # leading redundant-command count
    # cur = the transpose the LEADING command already set (pad accounts for its
    # byte); starting at 0 double-counts a leading transpose command when the
    # first entry is transposed (So_easy V1: entry 0 transpose 1 -> the model
    # re-added the byte pad already covers -> spurious legacy fallback).
    cur0 = v.transposes[0] if v.transposes else 0
    off, cur = pad, cur0
    for i in range(n):
        if i and i % period == 0:
            off, cur = pad, cur0  # pass boundary: orig re-reads from start
        t = v.transposes[i] if v.transposes else 0
        if t != cur:
            off, cur = off + 1, t
        if v.entry_offsets[i] != off:
            return None
        off += 1
    return pad, period


def _otrk_rcmd_model(v):
    """When the plain (pad, period) model is off ONLY because the composer
    placed extra REDUNDANT transpose commands mid-track — a `transpose to X`
    where X is already the current value, an explicit reset the composer WROTE
    (their arrangement), which the on-change model doesn't predict — recover
    the exact offsets by carrying those command POSITIONS. Returns
    (pad, period, rcmd) where rcmd is a bitmask of the redundant-command
    positions WITHIN the period (bit p = a redundant transpose command
    precedes physical entry p). This is the composer's ARRANGEMENT (where they
    notated transpose commands) — named musical content per the representation
    principle §8 (the composer needs it to reproduce the off-table sonification
    of $1726); the byte-OFFSET is DERIVED from it, never stored. None = even
    this can't model it (a non-unit jump / decrease = genuine legacy residue)."""
    n = len(v.entries)
    if not v.entry_offsets or len(v.entry_offsets) != n:
        return None
    period = n
    for i in range(1, n):
        if v.entry_offsets[i] <= v.entry_offsets[i - 1]:
            period = i
            break
    pad = v.entry_offsets[0]
    cur0 = v.transposes[0] if v.transposes else 0
    rcmd = 0
    off, cur, red = pad, cur0, 0
    for i in range(n):
        p = i % period
        if p == 0:
            off, cur, red = pad, cur0, 0
        t = v.transposes[i] if v.transposes else 0
        if t != cur:
            off, cur = off + 1, t
        actual = v.entry_offsets[i]
        expected = off + red
        if actual == expected + 1:
            red += 1
            rcmd |= (1 << p)
        elif actual != expected:
            return None
        off += 1
    return pad, period, rcmd if rcmd else None


def _emit_otrk_fields(m) -> dict:
    fields = {}
    for song in m.songs:
        for vi, v in enumerate(song.voices):
            # de-unrolled (stated-form) voices carry their track notation
            # per-entry — no fitted params needed. The fitted models below
            # survive ONLY as the fallback for walks that don't fold (so no
            # member's behavior can regress from the de-unroll).
            if _fold_stated_orderlist(v) is not None:
                continue
            r = _otrk_model(v)
            if r is not None:
                pad, period = r
                if pad:
                    fields[f'otrk_pad_s{song.id}_v{vi + 1}'] = pad
                if period < len(v.entries):
                    fields[f'otrk_period_s{song.id}_v{vi + 1}'] = period
                continue
            # the composer's redundant transpose-command PLACEMENT (arrangement)
            r2 = _otrk_rcmd_model(v)
            if r2 is not None and r2[2] is not None:
                pad, period, rcmd = r2
                if pad:
                    fields[f'otrk_pad_s{song.id}_v{vi + 1}'] = pad
                if period < len(v.entries):
                    fields[f'otrk_period_s{song.id}_v{vi + 1}'] = period
                fields[f'otrk_rcmd_s{song.id}_v{vi + 1}'] = rcmd
                continue
            # non-unit jump / decrease: genuine residue -> entry+1 approximation
            fields[f'otrk_legacy_s{song.id}_v{vi + 1}'] = 1
    return fields


def model_to_usf(m: DmcModel, wave_norm: bool = False) -> UsfFile:
    # Wave-table normal form (§4) is OPT-IN per writer: only the audited
    # single-player writer (write_dmc_usf) passes wave_norm=True. Every
    # other caller — the 2SID/compilation/heterogeneous merges and any
    # view-projection that reconstructs a UsfFile from parts — keeps the
    # resolved-copy form, so an unaudited path can never orphan pointer
    # instruments from their file-level table (the zero_wave_table crash
    # the phase-2 regression caught, twice: the 2SID merge and MA's
    # heterogeneous _project). The model must ALSO have passed extract()'s
    # re-derivation assert (wave_table_norm set). (The SIDFINITY_WT_OLDFORM
    # A/B lever was retired at the phase-5 corpus sync, 2026-07-29.)
    _norm = getattr(m, 'wave_table_norm', None) if wave_norm else None
    # Sparse-glide SEEDS (phase 3a, draft §8 option (a)): the work-file
    # leftovers of glide_note/glide_target ($1744/$1747), previously
    # smuggled as the captured value slots of live off-table records (the
    # composer's igla/iglb window-fill). Computed by mirroring that fill —
    # instruments in emission order, later records win — and emitted as
    # init.voice_state priming under the signal form.
    _gseed = ([0, 0, 0], [0, 0, 0])
    _fill = {}
    for k in sorted(m.instruments):
        for rec in (m.instruments[k].offtable_freq or []):
            off, note, lo, hi = rec[:4]
            idx = (off + note) & 0xFF
            if idx >= 96:
                _fill[idx - 96] = hi          # hi window pos
            if idx >= 192:
                _fill[idx - 192] = lo         # lo window pos
    for x in range(3):
        _gseed[0][x] = _fill.get(61 + x, 0)   # gla ($1744+x)
        _gseed[1][x] = _fill.get(64 + x, 0)   # glb ($1747+x)
    pad_fields = _emit_otrk_fields(m)
    # row command flags (dur_cmd/instr_cmd/vol_cmd/soft_cmd) feed the composer's sectpos
    # shadow — emit them iff a canon-geometry off-table read sonifies the sector
    # position window (matches the composer's derived sectpos_on).
    cmd_flags = m.offtable_canon and any(
        (off + note) & 0xFF in _SECTPOS_IDX
        for ins in m.instruments.values()
        for off, note, *_ in ins.offtable_freq)
    # duration-reload leftover priming ($173E-$1740): emitted ONLY when an
    # off-table freq read actually lands on the durreload rows (see the
    # file-level block below for the full rationale). Computed here because the
    # per-subtune priming below is gated on the same condition.
    _DURREL_WIN = {151, 152, 153, 247, 248, 249}
    reads_durrel = any(((off + note) & 0xFF) in _DURREL_WIN
                       for inst in m.instruments.values()
                       for off, note, _lo, _hi in
                       (getattr(inst, 'offtable_freq', []) or []))
    durrel = (m.durrel_init if reads_durrel and any(m.durrel_init)
              else (0, 0, 0))
    subtunes = []
    for song in m.songs:
        voices = []
        seed_voices = []
        for vi, v in enumerate(song.voices):
            folded = _fold_stated_orderlist(v)
            stated_form = None
            if folded is not None:
                ents, marks, extras, intros, loop_slot = folded
                stated_form = _stated_voice_form(v, ents, intros, loop_slot,
                                                 cmd_flags)
            if folded is not None and stated_form is not None:
                # STATED rows (D6 piece 2): one pattern per physical
                # sector; the `~intro` decode variants are re-derived by
                # the composer's resolution interpreter, not stored.
                pool, entries, instr_seed = stated_form
                if instr_seed:
                    # the engine's init sticky instrument: the $1015,x
                    # work-file leftover the walk was seeded with (0 for
                    # the common cleared/dead-seed case -> i1)
                    seed_voices.append(InitVoice(
                        id=vi + 1,
                        instr=InstrumentRef(id=v.instr_seed + 1)))
                pats = []
                for i, rows in enumerate(pool):
                    full = all(r.duration is not None for r in rows)
                    pats.append(Pattern(
                        id=i,
                        length=(sum(r.duration for r in rows)
                                if full else None),
                        rows=rows))
                ol = Orderlist(entries=entries, loop_to=loop_slot,
                               stop=loop_slot is None, stated=True)
                ol.stated_marks = marks
                ol.extra_cmds = (extras if any(extras) else [])
                # derived intro-pass effective transposes (parser parity)
                eff, cur = [], 0
                for mk in marks:
                    if mk is not None:
                        cur = mk
                    eff.append(cur)
                ol.transposes = eff if any(eff) else []
            elif folded is not None:
                # stated ORDERLIST, effective rows (the stated-row fold
                # failed its re-derivation — keep the walk's decode
                # wholesale: materialized intro variants + effective pool)
                ents, marks, extras, intros, loop_slot = folded
                pats = [Pattern(id=i,
                                length=sum(r.duration for r in rows),
                                rows=[_row_to_usf(r, cmd_flags)
                                      for r in rows])
                        for i, rows in enumerate(v.patterns)]
                ol = Orderlist(entries=ents, loop_to=loop_slot,
                               stop=loop_slot is None, stated=True)
                ol.stated_marks = marks
                ol.extra_cmds = (extras if any(extras) else [])
                ol.intro_entries = (intros if any(x is not None
                                                 for x in intros) else [])
                eff, cur = [], 0
                for mk in marks:
                    if mk is not None:
                        cur = mk
                    eff.append(cur)
                ol.transposes = eff if any(eff) else []
            else:
                pats = [Pattern(id=i,
                                length=sum(r.duration for r in rows),
                                rows=[_row_to_usf(r, cmd_flags)
                                      for r in rows])
                        for i, rows in enumerate(v.patterns)]
                ol = Orderlist(entries=list(v.entries),
                               transposes=(list(v.transposes)
                                           if any(v.transposes) else []),
                               loop_to=v.loop_to, stop=v.stop)
            voices.append(VoiceBlock(id=vi + 1, orderlist=ol, patterns=pats))
        # per-subtune idle priming (compilations only — one packed player per
        # subtune, each with its own uncleared work-file leftovers). Merged
        # into the SAME InitVoice as the resolver seed above, since the
        # composer looks these up by voice id.
        if song.idle_notes is not None:
            s_dur = (song.durrel_init
                     if reads_durrel and any(song.durrel_init or ())
                     else (0, 0, 0))
            by_id = {iv.id: iv for iv in seed_voices}
            for vi in range(3):
                if not (song.idle_notes[vi] or song.idle_masks[vi] or s_dur[vi]):
                    continue
                iv = by_id.get(vi + 1)
                repl = dict(note=song.idle_notes[vi] or None,
                            gate_mask=song.idle_masks[vi] or None,
                            dur_reload=s_dur[vi] or None)
                if iv is None:
                    seed_voices.append(InitVoice(id=vi + 1, **repl))
                else:
                    for k, val in repl.items():
                        setattr(iv, k, val)
        # per-subtune shadow when the member has one (a compilation: each
        # subtune runs its own player's leftover), else the model-level value
        shadow = (song.d417_shadow if song.d417_shadow is not None
                  else m.d417_shadow)
        sub_init = InitState(
            voices=seed_voices,
            # per-subtune slide-clock phase (compilation players disagreeing
            # on the $1019 leftover); None = inherit the file-level value
            slide_phase=getattr(song, 'dual_phase', None),
            sid=InitSid(
                master_vol=song.master_vol,
                filter=InitFilter(res_routing=shadow) if shadow else None))
        subtunes.append(MusicSubtune(
            id=song.id, tempo=song.speed, voices=voices, init=sub_init,
            # per-subtune composer-param overrides (compilations whose packed
            # players disagree on a wedge knob — ledger C31); None otherwise
            params=(Params(fields=dict(song.params)) if song.params else None)))

    # (the file-level `durrel` gate — flo idx 247-249 / fhi idx 151-153, so the
    # composer's live `durrel` shadow gets the pre-first-event value for voices
    # that haven't fetched yet — is computed above the subtune loop, which
    # shares it for the per-subtune priming.)

    # filter_mod: the factory probe encodes the song-global cutoff LFO as
    # 'prog|start|init_phase|stop_phase|d:f,...' — decode into the typed
    # block (musical content, not a params knob).
    filter_mod = {}
    fm = m.extra_params.pop('filter_mod', None)
    if fm:
        for seg in fm.split(';'):        # multi-tap probe joins progs by ';'
            prog, start, ip, sp, steps = seg.split('|')
            filter_mod[int(prog)] = {
                'start': int(start), 'init_phase': int(ip),
                'stop_phase': int(sp),
                'steps': [(int(d), int(f)) for d, f in
                          (t.split(':') for t in steps.split(','))]}
    return UsfFile(
        psid=PsidMeta(title=m.title, author=m.author, released=m.released,
                      clock=m.clock, sid=m.sid_model,
                      start_song=m.start_song,
                      # per-subtune play-dispatch environment (a file can mix
                      # a CIA multispeed song with vblank ones); masked to the
                      # walked subtunes
                      speed=m.speed_mask & ((1 << m.n_subtunes) - 1)),
        params=Params(fields={
            # otrk phase-offset scalars (see _otrk_pad)
            **pad_fields,
            # family-2 build knobs (factory-probed; empty for canon)
            **m.extra_params}),
        # NB idle_guards deliberately NOT emitted yet — the composer's guard
        # freewheel schedule for stopped voices is unverified vs the orig
        # (see composer_asm DMC_OFFTABLE_STATE note); priming would change
        # gate-logic behaviour for every member with $1786-8 leftovers.
        # slide_phase: engine-state priming (trichotomy §4.5) — initial
        # phase bit of the global half-rate slide clock (work-file
        # leftover; shifts WHICH frames dual-effect voices update on).
        init=InitState(voices=[
            InitVoice(id=v + 1,
                      note=m.idle_notes[v] or None,
                      gate_mask=m.idle_masks[v] or None,
                      dur_reload=durrel[v] or None,
                      glide_note=_gseed[0][v] or None,
                      glide_target=_gseed[1][v] or None)
            for v in range(3)
            if m.idle_notes[v] or m.idle_masks[v] or durrel[v]
            or _gseed[0][v] or _gseed[1][v]],
            slide_phase=(m.dual_phase or 0) or None),
        # environment (trichotomy §4.3): CIA multispeed latch /
        # whole-play() per-VBI repeats. None = single-speed vblank.
        environment=(Environment(cia_period=m.cia_period or 0,
                                 play_repeat=m.play_repeat or 1)
                     if (m.cia_period or m.play_repeat > 1) else None),
        instruments=[_instrument_to_usf(m.instruments[k], m.wavepos_layout,
                                        m.offtable_canon,
                                        wave_norm=_norm is not None)
                     for k in sorted(m.instruments)],
        subtunes=subtunes,
        filter_programs={d + 1: dict(v) for d, v in m.filter_defs.items()},
        filter_mod=filter_mod,
        # tuning is per-tune musical content (members ship edited or
        # wholly different temperaments): 96 lo + 96 hi bytes.
        freq_table=list(m.freq_lo) + list(m.freq_hi),
        # Wave-table NORMAL FORM (§4): the stated shared table; instruments
        # carry `wave_start` pointers and the resolved copies (waveform /
        # wave_freq / loop + the idle wave_programs[0]) are ABSENT — the
        # composer re-derives them through the shared resolver. None =
        # resolved-copy form (fallback members + merge paths).
        wave_table=_norm,
        # the idle wave program: what a voice's effects walk before its
        # first note (the engine's cleared cache starts the wave table
        # at index 0, independent of any instrument's start); under the
        # normal form it is resolve_wave_table(wave_table, 0).
        wave_programs=({} if _norm is not None else
                       {0: {'ctrl': list(m.idle_wave[0]),
                            'freq': list(m.idle_wave[1]),
                            'loop': m.idle_wave[2]}}),
        # off-table vibrato-depth reads (note>95) — the vibdepth analog of
        # offtable_freq; composer places these past the vibdepth table.
        offtable_vibdepth=sorted(m.offtable_vibdepth.items()),
    )


def write_dmc_usf(cfg: DMCV4Config, out_dir: str,
                  hvsc_root: str = 'hvsc84') -> str:
    m = extract(cfg, hvsc_root=hvsc_root)
    usf = model_to_usf(m, wave_norm=True)
    base = os.path.splitext(os.path.basename(cfg.sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out


def _offset_note_refs(rows, di: int):
    """Return rows with every instrument reference (note.instr + a
    `set_instr=N` fx flag) shifted by `di` — used to move a chip's
    instruments into a disjoint id range in the merged multi-SID USF."""
    import dataclasses
    out = []
    for r in rows:
        instr = r.instr
        if instr is not None and getattr(instr, 'id', None) is not None:
            instr = dataclasses.replace(instr, id=instr.id + di)
        flags = []
        for f in r.fx_flags:
            if f.startswith('set_instr='):
                flags.append(f'set_instr={int(f.split("=")[1]) + di}')
            else:
                flags.append(f)
        out.append(dataclasses.replace(r, instr=instr, fx_flags=flags))
    return out


# Per-chip id strides in the MERGED multi-SID USF: chip c's instruments +
# filter programs are shifted by c*STRIDE so a fixed-arithmetic split
# recovers each chip's standalone sub-USF exactly (ids well above any real
# DMC per-player count — instruments and 17-record filter windows). Only
# appear in multi-SID files; single-chip USFs are unchanged.
MULTISID_INSTR_STRIDE = 100
MULTISID_FILTER_STRIDE = 100

# A params key ending in `_v<N>` is PER-VOICE (the otrk phase scalars), so it
# renumbers with its voice when chips are merged into one multi-SID USF.
_VOICE_KEY = re.compile(r'^(.*_v)(\d+)$')

# Params that are PER-CHIP by construction in a multi-SID member — they
# describe the WRAPPER's treatment of one chip's player, not the shared
# player code, so they merge into one ';'-separated list in chip order and
# split back per chip. (`play_phases`/`noteinit_deferred`: Surgeon's
# Cow_Anus_Fucked runs ONE chip per call, so chip 1 observes `P_S` while
# chip 2 observes `S_P` — a disagreement that is the correct answer, not the
# non-first-chip wedge the player-wide assert is there to catch.)
MULTISID_PER_CHIP_KEYS = ('multisid_keep_regs', 'play_phases',
                          'noteinit_deferred')


def merge_2sid_usf(models, sid2_model=None, sid3_model=None,
                   active=None) -> UsfFile:
    """Merge per-chip DmcModels (one per SID chip) into ONE multi-SID USF:
    voices number through the chips (1-3 = chip 1, 4-6 = chip 2, ...), each
    chip's instruments + filter programs live in a disjoint id range (chip
    c shifted by c*STRIDE), and per-chip priming rides init.sid /
    init.sid2 / init.sid3. freq_table + idle wave are shared (verified
    identical across a member's chips). Chip I/O addresses are NOT carried —
    the composer standardises them (chip 2 = $D420, chip 3 = $D440).
    Multi-subtune members merge subtune-wise: the chips share one subtune
    list (each chip's player is handed the same A=subtune), so subtune s of
    the merged USF carries chip c's subtune s on voices c*3+1..c*3+3, with
    that subtune's own per-chip tempo (`tempo 2/3`) and priming
    (`sid 2/3`)."""
    import dataclasses
    # Phase 4 (live-signal modulation): a wavepos-CARRIER chip needs the
    # stated wave_table + per-instrument wave_start pointers in the merged
    # file, or the composer cannot emit its pool positionally. The schema
    # has ONE file-level wave_table and the chips' tables generally differ,
    # so the norm form is carried for the carrier chip(s) ONLY (the others
    # stay resolved-copy; their instruments carry no pointers, so the
    # foreign table is inert for them). Multiple carrier chips are admitted
    # only when their stated tables agree — otherwise fall back wholesale
    # (honest residue; flagged for the phase-5 per-chip-table decision).
    _WPI = {(0x177A + k) - 0x16A7 for k in range(3)}

    def _wp_carrier(m):
        return getattr(m, 'wave_table_norm', None) is not None and any(
            (o + n) & 0xFF in _WPI
            for ins in m.instruments.values()
            for o, n, _lo, _hi in (ins.offtable_freq or []))
    carriers = [ci for ci, m in enumerate(models) if _wp_carrier(m)]
    if carriers and all(models[c].wave_table_norm ==
                        models[carriers[0]].wave_table_norm
                        for c in carriers):
        usfs = [model_to_usf(m, wave_norm=(ci in carriers))
                for ci, m in enumerate(models)]
        merged_wave_table = usfs[carriers[0]].wave_table
    else:
        usfs = [model_to_usf(m) for m in models]
        merged_wave_table = None
    # the merged idle program must stay stated even when chip 1 went norm
    # form (its wave_programs are empty then) — take the first non-empty
    merged_wave_progs = next(
        (u.wave_programs for u in usfs if u.wave_programs.get(0)),
        usfs[0].wave_programs)
    if active is None:
        # no observation: the chips are one tune driven by the same subtune
        # number, so their subtune lists must line up 1:1
        n_sub = len(usfs[0].subtunes)
        assert all(len(u.subtunes) == n_sub for u in usfs), \
            'multi-SID chips disagree on the subtune count'
        active = [{ci: si for ci in range(len(usfs))} for si in range(n_sub)]
    else:
        n_sub = len(active)
        for si, chips in enumerate(active):
            for ci, song in chips.items():
                assert song < len(usfs[ci].subtunes), (
                    f'subtune {si} routes chip {ci + 1} to song {song}, '
                    f'but it has {len(usfs[ci].subtunes)}')
    # shared musical content must coincide across chips (they're one tune)
    assert all(u.freq_table == usfs[0].freq_table for u in usfs), \
        'multi-SID chips disagree on the freq table'

    # per-chip params, in three classes:
    #  - MULTISID_PER_CHIP_KEYS are per-chip by construction (which of THIS
    #    chip's stores the relocation left pointing at chip 1 (C19); how the
    #    wrapper schedules THIS chip's player (C18)) and merge into one
    #    ';'-separated list in chip order;
    #  - PER-VOICE keys (`..._v<N>`, e.g. the otrk phase scalars) renumber
    #    with their voice, exactly like the voice blocks;
    #  - everything else is a player-wide knob that must AGREE across the
    #    chips — they are copies of one player, so a disagreement means a
    #    wedge on a non-first chip, which this merge would otherwise drop on
    #    the floor (it carries usfs[0]'s params).
    per_chip = {k: [u.params.fields.get(k, '') for u in usfs]
                for k in MULTISID_PER_CHIP_KEYS}
    per_voice = {}
    common = []
    for ci, u in enumerate(usfs):
        chip_common = {}
        for k, v in u.params.fields.items():
            if k in MULTISID_PER_CHIP_KEYS:
                continue
            mv = _VOICE_KEY.match(k)
            if mv:
                per_voice[f'{mv.group(1)}{int(mv.group(2)) + ci * 3}'] = v
            else:
                chip_common[k] = v
        common.append(chip_common)
    assert all(c == common[0] for c in common), \
        f'multi-SID chips disagree on player params: {common}'
    merged_params = dict(common[0])
    merged_params.update(per_voice)
    for k, vals in per_chip.items():
        if any(vals):
            merged_params[k] = ';'.join(str(v) for v in vals)

    merged_instruments = []
    merged_filters = {}
    init_voices = []
    for ci, u in enumerate(usfs):
        ioff = ci * MULTISID_INSTR_STRIDE
        foff = ci * MULTISID_FILTER_STRIDE
        for inst in u.instruments:
            fp = inst.filter_prog
            if fp and fp.program:
                fp = dataclasses.replace(fp, program=fp.program + foff)
            merged_instruments.append(
                dataclasses.replace(inst, id=inst.id + ioff, filter_prog=fp))
        for prog, dfn in u.filter_programs.items():
            merged_filters[prog + foff] = dfn
        # per-voice idle priming (top-level init.voices), voices renumbered
        for iv in u.init.voices:
            init_voices.append(dataclasses.replace(iv, id=ci * 3 + iv.id))

    merged_subtunes = []
    file_chip_sids = []     # subtune 1's per-chip priming (file-level init)
    for si in range(n_sub):
        all_voices = []
        seed_voices = []    # per-SUBTUNE resolver seeds (stated rows)
        chip_sids = []      # per-chip InitSid priming
        tempos = []
        for ci, u in enumerate(usfs):
            ioff = ci * MULTISID_INSTR_STRIDE
            if ci not in active[si]:
                # the dispatch wrapper does not call this chip's player for
                # this subtune: no voices, no tempo, no priming — the chip
                # is simply not part of this subtune
                tempos.append(None)
                chip_sids.append(None)
                continue
            # the wrapper picks the SONG each chip plays (need not be si)
            sub = u.subtunes[active[si][ci]]
            # tempo/priming stay positional (one slot per chip) so the split
            # inverts by chip index
            tempos.append(sub.tempo)
            # per-chip SID priming (master vol + $D417 routing shadow) rides
            # the subtune init.sid in the per-chip USF
            chip_sids.append(sub.init.sid if sub.init else None)
            # voices renumbered through the chips; note refs shifted
            for v in sub.voices:
                pats = [dataclasses.replace(
                    p, rows=_offset_note_refs(p.rows, ioff))
                    for p in v.patterns]
                all_voices.append(dataclasses.replace(
                    v, id=ci * 3 + v.id, patterns=pats))
            # per-SUBTUNE engine-state priming (the stated-row resolver seeds,
            # e.g. `instr: i1`) rides the subtune init in the per-chip USF —
            # a DISTINCT level from the file-level idle voices above; keep it
            # on the merged subtune so _split_chip_usf recovers it per chip
            if sub.init:
                for iv in sub.init.voices:
                    seed_voices.append(
                        dataclasses.replace(iv, id=ci * 3 + iv.id))
        if si == 0:
            file_chip_sids = chip_sids
        sub_init = InitState(
            voices=seed_voices,
            sid=chip_sids[0],
            sid2=chip_sids[1] if len(chip_sids) > 1 else None,
            sid3=chip_sids[2] if len(chip_sids) > 2 else None)
        # the subtune's base tempo is the first SOUNDING chip's (chip 1 may
        # not be part of this subtune); a chip carries `tempo N` only when
        # it sounds AND differs from the base
        base_tempo = next(t for t in tempos if t is not None)
        merged_subtunes.append(MusicSubtune(
            id=si + 1, tempo=base_tempo, voices=all_voices,
            init=sub_init,
            tempo2=tempos[1] if len(tempos) > 1 and tempos[1] is not None
            and tempos[1] != base_tempo else None,
            tempo3=tempos[2] if len(tempos) > 2 and tempos[2] is not None
            and tempos[2] != base_tempo else None))

    base = usfs[0]
    init = InitState(
        voices=init_voices,
        sid=file_chip_sids[0],
        sid2=file_chip_sids[1] if len(file_chip_sids) > 1 else None,
        sid3=file_chip_sids[2] if len(file_chip_sids) > 2 else None)
    psid = dataclasses.replace(base.psid, sid2=sid2_model, sid3=sid3_model)
    return dataclasses.replace(
        base, psid=psid, init=init,
        params=dataclasses.replace(base.params, fields=merged_params),
        instruments=merged_instruments,
        filter_programs=merged_filters,
        wave_table=merged_wave_table,
        wave_programs=merged_wave_progs,
        subtunes=merged_subtunes)


def write_dmc_2sid_usf(cfgs, out_dir: str, hvsc_root: str = 'hvsc84') -> str:
    from pipelines.dmc.v4.factory import (_sid_header_multi,
                                          multisid_active_chips)
    models = [extract(c, hvsc_root=hvsc_root) for c in cfgs]
    path = os.path.join(hvsc_root, cfgs[0].sid_path)
    _, _, _, m2, m3 = _sid_header_multi(path)
    # which chips the dispatch wrapper actually calls per subtune (observed,
    # C18); None on observation failure = every chip plays every subtune
    active = multisid_active_chips(path, [c.base for c in cfgs],
                                   len(models[0].songs))
    usf = merge_2sid_usf(models, sid2_model=m2, sid3_model=m3, active=active)
    base = os.path.splitext(os.path.basename(cfgs[0].sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out


def heterogeneous_to_usf(dmc_model, sfx_engine, subtune_kinds,
                         start_song: int) -> UsfFile:
    """Combine a DMC merged model + a dmc_sfx SfxEngine into one heterogeneous
    UsfFile: the DMC music subtunes and the dmcsfx subtunes interleaved in PSID
    order, plus the shared `dmc_sfx` block."""
    import dataclasses
    dmc_usf = model_to_usf(dmc_model)
    dmc_subs = dmc_usf.subtunes                    # ids 1..n_dmc, DMC order
    final = []
    for k, (kind, idx) in enumerate(subtune_kinds):
        if kind == 'dmc':
            final.append(dataclasses.replace(dmc_subs[idx], id=k + 1))
        else:
            final.append(DmcSfxSubtune(id=k + 1, song=idx))
    psid = dataclasses.replace(dmc_usf.psid, start_song=start_song)
    return dataclasses.replace(dmc_usf, subtunes=final, dmc_sfx=sfx_engine,
                               psid=psid)


def write_dmc_compilation_usf(sid_path: str, spec: dict, out_dir: str,
                              hvsc_root: str = 'hvsc84') -> str:
    """COMPILATION member (ledger C31): extract every packed player and merge.

    HOMOGENEOUS (all DMC players): merge into one unified single-player DmcModel
    (freq/vibdepth shared, instruments renumbered into one pool, songs reordered
    by PSID subtune), serialized with the ordinary model_to_usf path.
    HETEROGENEOUS (DMC players + a dmc_sfx sub-player, e.g. Canyon_Tank_Duel):
    the DMC subtunes merge as usual, the dmc_sfx player becomes a typed
    SfxEngine (`dmc_sfx` block) + dmcsfx subtunes; the composer emits both
    engines behind a per-subtune dispatcher."""
    from pipelines.dmc.v4.compilation import (extract_compilation,
                                              extract_heterogeneous,
                                              sfx_player_indices)
    if sfx_player_indices(sid_path, spec, hvsc_root):
        dmc_model, sfx_engine, kinds, start = extract_heterogeneous(
            sid_path, spec, hvsc_root=hvsc_root)
        usf = heterogeneous_to_usf(dmc_model, sfx_engine, kinds, start)
    else:
        m = extract_compilation(sid_path, spec, hvsc_root=hvsc_root)
        usf = model_to_usf(m)
    base = os.path.splitext(os.path.basename(sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out
