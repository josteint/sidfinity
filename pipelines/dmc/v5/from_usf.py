"""DMC V5 USF -> model (the inverse of extract/to_usf).

Rebuilds a V5Model from a parsed UsfFile so the composer (which is
model-driven and UNCHANGED) can emit the SID. The shared wave / pulse /
filter tables are RE-PACKED from the per-instrument inline programs and
the pointers reassigned -- the engine's packing mechanism. Per the CORE
TENET the rebuilt tables need not match the original's byte layout; only
the resulting $D400-$D418 write stream must (verified by `verify_v5`).

Sectors are content-deduped into a fresh global pool and orderlist
entries remapped to it; sticky dur/instrument are re-emitted on change
(an equivalent stream, not a byte copy).
"""
from __future__ import annotations

from src.usf.types import UsfFile, Pitch
from pipelines.dmc.v5.extract.engine_model import V5Model, V5Instrument

_FORCE_PAGED = False    # dev knob (tests only): run the paged packer even when
                        # every pool fits, to exercise the machinery on FULL members

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def defused_pool_overflow(usf: UsfFile) -> 'list[str]':
    """Which de-fused pools would exceed the 256-entry byte cursor.

    SIZE-ONLY mirror of `usf_to_model`'s `_build_pools` (same program
    lengths, same overflow-gated identical-program dedup — no layout
    detail). `usf_to_model` asserts this mirror against its real pools on
    EVERY build, so the two cannot drift silently.

    Exists so the EXTRACT can decide the `offtable_live_pos` refusal before
    the .usf is ever written (`write_v5_usf`): whether a member's off-table
    freq read sonifies the live pulsepos/filterpos is extract-side knowledge
    (it needs the player's state-block addresses), and a capture-validity
    fact like that never belongs IN the USF — the USF carries music only.
    """
    over = []

    def _wkey(ctrl, freq, loop):
        n = len(ctrl)
        return (tuple(c & 0xFF for c in ctrl),
                tuple(f & 0xFF for f in (list(freq) + [0] * n)[:n]), loop)

    ip = usf.wave_programs.get(0)
    keys = ([_wkey(ip['ctrl'], ip['freq'], ip.get('loop', 0))]
            if (ip and ip['ctrl']) else [])
    keys += [_wkey(i.waveform, i.wave_freq, i.loop) for i in usf.instruments]
    size = sum(len(k[0]) + 1 for k in keys)
    if size > 256:                       # overflow-gated dedup, like the packer
        size = sum(len(k[0]) + 1 for k in dict.fromkeys(keys))
    if size > 256:
        over.append('wave')

    def _ebytes(env):
        return 2 + 2 * len(env.phases) if env.phases else 4

    for nm, dflt, dflt_empty, envs in (
            ('pulse', usf.default_pulse, 1,
             [i.pulse_env for i in usf.instruments if i.pulse_env]),
            ('filter', usf.default_filter, 3,
             [i.filter_env for i in usf.instruments if i.filter_env])):
        base = (2 * len(dflt.phases) + 1 if dflt is not None and dflt.phases
                else dflt_empty)
        size = base + sum(_ebytes(e) for e in envs)
        if size > 256:
            seen = set()
            size = base
            for e in envs:
                k = (e.start, tuple(e.phases), e.loop)
                if k not in seen:
                    seen.add(k)
                    size += _ebytes(e)
        if size > 256:
            over.append(nm)
    return over
_NOTE_IDX = {n: i for i, n in enumerate(NOTE_NAMES)}


def _note_num(p: Pitch) -> int:
    return p.octave * 12 + _NOTE_IDX[p.name]


def _pitch_str_num(s: str) -> int:
    """'C-4' / 'C#4' (a glide_to flag value) -> raw note index."""
    name = s[0] + ('#' if s[1] == '#' else '')
    return int(s[2:]) * 12 + _NOTE_IDX[name]


def _flag_val(fl: str) -> int:
    v = fl.split('=', 1)[1]
    return int(v.lstrip('$'), 16) if v.startswith('$') else int(v)


# --- sector rows -> raw bytes (event order preserved verbatim) ----------
# Parameter commands are ORDERED prefix flags emitted before the row's
# main byte. Main byte: a note pitch; $FE (`tie`); $F4 (`gate_tie`); or
# $FB/$FA (glide on a note / slide on a hold). The verbatim ordering is
# load-bearing -- the engine's gate-off lookahead reads the raw next byte.
_PREFIX_BYTE = {
    'set_dur': 0xFD, 'set_instr': 0xFC, 'vol': 0xF3, 'frq': 0xF8,
    'fade_in': 0xF7, 'fade_out': 0xF6, 'adr': 0xF2, 'srr': 0xF1,
    'filter': 0xF9,
    # family-4-only prefix command (see engine_model._CMD). $F0 is handled
    # separately in _encode_sector: its two decomposed fields (f0_vib_width /
    # f0_wave_count) recompose into the packed byte.
    'freq_bias': 0xEF,
}


def _encode_sector(rows, ipos: 'dict | None' = None) -> bytes:
    """`ipos` maps instrument USF id -> engine table POSITION for the $FC
    (set_instr) operand. The engine indexes its instrument table by position;
    `set_instr=` values are instrument IDS — for a standalone V5 file ids ARE
    0-based positions (byte-identical), but a heterogeneous merge renumbers
    ids into a shared pool (ledger C31/C35), where the lookup is load-bearing.
    None = identity (ids == positions)."""
    out = bytearray()
    for row in rows:
        glide = glide_to = None
        f0_vw = f0_wc = None
        for fl in row.fx_flags:
            key = fl.split('=', 1)[0]
            if key == 'set_instr' and ipos:
                v = _flag_val(fl)
                out += bytes([_PREFIX_BYTE[key], ipos.get(v, v) & 0xFF])
            elif key in _PREFIX_BYTE:
                out += bytes([_PREFIX_BYTE[key], _flag_val(fl) & 0xFF])
            elif key == 'f0_vib_width':      # family-4 $F0: the two decomposed
                f0_vw = _flag_val(fl)        # fields recompose into one packed
                if f0_wc is not None:        # byte (low 3 bits | count << 4),
                    out += bytes([0xF0, (f0_wc << 4) | (f0_vw & 0x07)])
                    f0_vw = f0_wc = None     # emitted once both are seen (the
            elif key == 'f0_wave_count':     # extract always emits the pair).
                f0_wc = _flag_val(fl)
                if f0_vw is not None:
                    out += bytes([0xF0, (f0_wc << 4) | (f0_vw & 0x07)])
                    f0_vw = f0_wc = None
            elif fl == 'gate_toggle':
                out.append(0xF5)
            elif key == 'glide':
                glide = _flag_val(fl)
            elif key == 'glide_to':
                glide_to = _pitch_str_num(fl.split('=', 1)[1])
        if glide is not None:                # $FB note+glide / $FA hold+slide
            if row.pitch.is_rest:
                out += bytes([0xFA, glide & 0xFF, glide_to & 0xFF])
            else:
                out += bytes([0xFB, glide & 0xFF,
                              _note_num(row.pitch) & 0xFF, glide_to & 0xFF])
        elif 'gate_tie' in row.fx_flags:
            out.append(0xF4)
        elif 'tie' in row.fx_flags:
            out.append(0xFE)
        else:
            out.append(_note_num(row.pitch) & 0xFF)
    out.append(0xFF)
    return bytes(out)


def _encode_orderlist(ol, remap: dict) -> bytes:
    out = bytearray()
    entry_byte = []
    cur_tr = 0
    for i, e in enumerate(ol.entries):
        entry_byte.append(len(out))
        tr = ol.transpose_at(i)
        # Force the transpose at the loop target when the loop RE-ESTABLISHES
        # it (loop_transpose set): the orig has an explicit $FD/$FC there that
        # re-applies the transpose each wrap, even when redundant in pass 1.
        # Without this the loop carries the last entry's transpose -> wrong
        # note on passes 2+.
        force = (ol.loop_transpose is not None and i == ol.loop_to)
        if tr != cur_tr or force:
            if tr >= 0:
                out += bytes([0xFD, tr & 0xFF])      # positive transpose
            else:
                out += bytes([0xFC, (-tr) & 0xFF])   # negative transpose
            cur_tr = tr
        out.append(remap[e] & 0xFF)
    if ol.stop:
        out.append(0xFE)
    elif ol.loop_to is not None:
        tgt = entry_byte[ol.loop_to] if ol.loop_to < len(entry_byte) else 0
        out += bytes([0xFF, tgt & 0xFF])
    else:
        out += bytes([0xFF, 0x00])
    return bytes(out)


def usf_to_model(usf: UsfFile) -> V5Model:
    sub = usf.subtunes[0]
    sid = sub.init.sid if (sub.init and sub.init.sid) else None
    mvol = sid.master_vol if sid and sid.master_vol is not None else 0x0F
    flt = sid.filter if sid else None

    # $1013 speed-counter + $101C fade-frac startup phases (init clears
    # neither) — typed init engine-state priming (§4.5).
    spdctr = int(sub.init.speed_ctr_init or 0) if sub.init else 0
    mvolfrac = int(sub.init.fade_frac_init or 0) if sub.init else 0
    # $100F,x per-voice leftover note the lead-in effects frame(s) idle on.
    notes = [0, 0, 0]
    if sub.init and sub.init.voices:
        for iv in sub.init.voices:
            if iv.note is not None and 1 <= iv.id <= 3:
                notes[iv.id - 1] = iv.note

    m = V5Model(
        freq_lo=list(usf.freq_table[:96]),
        freq_hi=list(usf.freq_table[96:192]),
        speed=sub.tempo, master_vol=mvol,
        lo_filtmode=flt.res_routing if flt else 0,
        lo_fchi=flt.cutoff_hi if flt else 0,
        lo_fclo=flt.cutoff_lo if flt else 0,
        lo_spdctr=spdctr, lo_notes=notes, lo_mvolfrac=mvolfrac,
        cia_period=(int(usf.environment.cia_period)
                    if getattr(usf, 'environment', None) else 0),
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released,
        clock=usf.psid.clock, sid_model=usf.psid.sid,
    )
    # family-4 (Jupiter41) player flag + leftovers (Phase C composer knobs)
    pf = usf.params.fields if usf.params and usf.params.fields else {}
    # TYPED FIRST, params FALLBACK: `play_phases` moved to Environment
    # (trichotomy §4.3 / ledger C33), but stored .usf written before the move
    # still carry it in params{} — reading both keeps every stored artifact
    # building identically (C20 third layer).
    _envph = getattr(getattr(usf, 'environment', None), 'play_phases', '') or ''
    m.play_phases = str(_envph or pf.get('play_phases', '') or '')
    # PLAYER-MECHANISM KNOBS (Principle §8) — each names the behaviour it
    # changes; the composer branches on these, never on a player identity.
    m.noteon_skip_freq_clear = bool(int(pf.get('noteon_skip_freq_clear', 0)))
    m.wave_speed_from_instr = bool(int(pf.get('wave_speed_from_instr', 0)))
    m.volovr_ad_zero = bool(int(pf.get('volovr_ad_zero', 0)))
    m.pulse_ctr_8bit = bool(int(pf.get('pulse_ctr_8bit', 0)))
    m.noteload_no_d418 = bool(int(pf.get('noteload_no_d418', 0)))
    m.filter_v3_only = bool(int(pf.get('filter_v3_only', 0)))
    m.filter_needs_cmd = bool(int(pf.get('filter_needs_cmd', 0)))
    m.filter_d416_only = bool(int(pf.get('filter_d416_only', 0)))
    m.d418_skip_vib_reversal = bool(int(pf.get('d418_skip_vib_reversal', 0)))
    m.wave_step_carry = bool(int(pf.get('wave_step_carry', 0)))
    m.vib_from_instr_bytes = bool(int(pf.get('vib_from_instr_bytes', 0)))
    m.filter_prog_8bit = bool(int(pf.get('filter_prog_8bit', 0)))
    m.play_skip_init = int(pf.get('play_skip_init', 2))
    m.dur_ctr_init = int(pf.get('dur_ctr_init', 1))

    # Share identical (ctrl, freq, loop) programs ONLY when the un-shared pool
    # would overflow the 256-byte single-byte wavepos. Non-overflow members keep
    # their exact un-shared layout: sharing moves programs and rewrites the
    # absolute $90 loop-marker targets, which is POSITION-DEPENDENT — even for
    # byte-identical programs it perturbed a currently-FULL member (CreaMD's
    # Ambient regressed; the divergence is freq, likely the de-fusion adjacency
    # coupling the pulse table also shows). Overflow members can't build at all
    # un-shared, so best-effort sharing there is pure upside, and gating to
    # overflow-only is zero-regression by construction (it never touches a member
    # that already builds). Mirrors the V4 composer_asm pool dedup (ledger C8).
    ip = usf.wave_programs.get(0)
    _idle_n = (len(ip['ctrl']) + 1) if (ip and ip['ctrl']) else 0
    _dedup = _idle_n + sum(len(i.waveform) + 1 for i in usf.instruments) > 256

    def _env_bytes(env):
        return 2 + 2 * len(env.phases) if env.phases else 4

    # ---- pool construction, two-pass (ledger C8 sixth widening — the paged
    #      composer cursor, backlog item 19 option (c)). Pass 1 (paged=False)
    #      is the historical layout, byte-for-byte: every member whose pools
    #      fit 256 entries keeps it. Only when a pool overflows is pass 2 run,
    #      which lays the SAME programs out page-padded: a program (incl. its
    #      $90 marker) never straddles a 256-byte page, so the engine's 8-bit
    #      position stays a valid in-page offset, the $90 marker's `& $FF`
    #      target stays correct, and only the read operands' HI byte (the
    #      page) changes — selected per voice by the composer's SMC patches.
    def _build_pools(paged: bool):
        def _pad(table, proglen, no_zero_off):
            if not paged:
                return
            if proglen > 256:
                # a single program can never span two pages (unreachable:
                # _PHASE_CAP bounds captures at ~97 bytes)
                raise RuntimeError(f'unsupported:prog_too_long {proglen}')
            off = len(table) & 0xFF
            if off and off + proglen > 256:
                table.extend([(0, 0)] * (256 - off))
            if no_zero_off and table and (len(table) & 0xFF) == 0:
                # the engine reads pulse_ptr/filter_ptr LOW byte as its
                # "restart?" flag (0 = no restart) — never place a real
                # program at an in-page offset of 0
                table.append((0, 0))

        # ---- re-pack the shared wave table (idle program at index 0, then
        #      each instrument's program) and reassign pointers -------------
        wave = []
        # Dedup identical (ctrl, freq, loop) wave programs into one pooled
        # copy (see the gate note above): each note re-inits wavepos to the
        # instrument's ptr and reads the same sequence, and the absolute $90
        # target loops to the shared copy's own loop point.
        _wseen: dict = {}

        def add_wave(ctrl, freq, loop):
            n = len(ctrl)
            cb = tuple(c & 0xFF for c in ctrl)
            fb = tuple(f & 0xFF for f in (list(freq) + [0] * n)[:n])
            key = (cb, fb, loop)
            if _dedup and key in _wseen:
                return _wseen[key]
            _pad(wave, n + 1, False)
            s = len(wave)
            for c, f in zip(cb, fb):
                wave.append((c, f))
            wave.append((0x90, (s + loop) & 0xFF))   # V5 marker: freq = abs target
            _wseen[key] = s
            return s

        if ip and ip['ctrl']:
            add_wave(ip['ctrl'], ip['freq'], ip.get('loop', 0))

        # ---- synthesize the de-fused pulse/filter tables from the per-
        #      instrument envelopes (null entry 0, then each envelope's program;
        #      a $90 terminal so the program holds its loop/last phase and
        #      doesn't bleed into the next). The engine walks each instrument's
        #      own copy, so keep-running continuations stay faithful. ----------
        # ---- pulse table position 0 = the per-voice DEFAULT (idle) PW program when
        #      present (pulse_run runs it from pulsepos=0). When ABSENT, keep the
        #      single null (0,0) entry — NOT a 3-entry hold: pulse_run was never
        #      gated, so the single (0,0) with its benign OOB-count read is exactly
        #      the 891-FULL behavior; the 3-entry hold shifts the de-fused table and
        #      regressed 135 members (see RE_NOTES dead-end). The idle has no start
        #      entry (PW continues from the cleared 0). ----------
        pulse = []
        dp = usf.default_pulse
        if dp is not None and dp.phases:
            for rate, frames in dp.phases:
                a = rate & 0xFFFF
                pulse.append(((a >> 8) & 0xFF, a & 0xFF))              # ADD
                pulse.append(((frames >> 8) & 0xFF, frames & 0xFF))    # count
            lp = dp.loop if dp.loop is not None else len(dp.phases) - 1
            pulse.append((0x90, (2 * lp) & 0xFF))                      # loop onto a phase
        else:
            pulse = [(0, 0)]                                           # null pos 0 (891 behavior)

        # ---- filter table position 0 = the V3 DEFAULT (idle) filter program, run
        #      from frame 0 (filterpos starts at 0). The real default_filter sweep
        #      when present, else a (0,0) HOLD (zero-ADD, count==0 = 65536-frame
        #      hold, $90 self-loop) so the composer can run filter_run for V3 every
        #      frame without an out-of-bounds count read. The idle program has NO
        #      start entry (it continues from the init.sid.filter priming cutoff) —
        #      its ADD/count pairs begin at position 0. ----------
        filt = []
        df = usf.default_filter
        if getattr(m, 'filter_prog_8bit', False) and df is not None and df.phases:
            # family-4: 8-bit (add, count) program. add -> filterlo[2k]; count ->
            # filterhi[2k+1]; the other byte of each pair is unread by the 2-step
            # walk, so leave it 0. count 256 -> byte 0 (the engine's 8-bit counter
            # wraps). $90 loops to position 2*lp.
            for add, count in df.phases:
                filt.append((add & 0xFF, 0))
                filt.append((0, count & 0xFF))
            lp = df.loop if df.loop is not None else len(df.phases) - 1
            filt.append((0x90, (2 * lp) & 0xFF))
        elif df is not None and df.phases:
            for rate, frames in df.phases:
                a = rate & 0xFFFF
                filt.append(((a >> 8) & 0xFF, a & 0xFF))            # ADD
                filt.append(((frames >> 8) & 0xFF, frames & 0xFF))  # count
            lp = df.loop if df.loop is not None else len(df.phases) - 1
            filt.append((0x90, (2 * lp) & 0xFF))                    # loop onto a phase
        else:
            filt = [(0, 0), (0, 0), (0x90, 0)]                      # hold at pos 0

        def add_env(table, env):
            s = len(table)
            table.append(((env.start >> 8) & 0xFF, env.start & 0xFF))  # init pair
            for rate, frames in env.phases:
                a = rate & 0xFFFF
                table.append(((a >> 8) & 0xFF, a & 0xFF))           # step
                table.append(((frames >> 8) & 0xFF, frames & 0xFF))  # count
            if env.phases:
                lp = env.loop if env.loop is not None else len(env.phases) - 1
                table.append((0x90, (s + 1 + 2 * lp) & 0xFF))  # loop onto a step
            else:
                # Static env (no sweep): HOLD the start value. A bare `$90 -> start`
                # makes the engine's run-loop re-read the START pair as an ADD step
                # (ramping +start.hi per frame — the dominant V5 pulse/filter bug).
                # Instead sit on a zero-ADD with a count==0 (= 65536-frame wrap), so
                # the value is held; the $90 loops back onto that zero-ADD.
                table.append((0x00, 0x00))            # s+1: zero ADD (held)
                table.append((0x00, 0x00))            # s+2: count 0 -> 65536-frame hold
                table.append((0x90, (s + 1) & 0xFF))  # s+3: loop onto the zero ADD
            return s

        def add_env_f4(table, env):
            # family-4 8-bit (add, count) layout: filterlo[s] = start cutoff (the
            # engine's $1019 = filterlo[byte4] re-init), then the sweep at s+1:
            # filterlo[2k+1] = add, filterhi[2k+2] = count; $90 loops to phase lp.
            # The de-fused per-instrument copy (ledger C8); fptr is the composer's
            # own re-packed index, never serialized.
            s = len(table)
            table.append((env.start & 0xFF, 0))               # filterlo[s] = start
            for add, count in env.phases:
                table.append((add & 0xFF, 0))                 # filterlo = add
                table.append((0, count & 0xFF))               # filterhi = count (256->0)
            if env.phases:
                lp = env.loop if env.loop is not None else len(env.phases) - 1
                table.append((0x90, (s + 1 + 2 * lp) & 0xFF))
            else:
                table.append((0x00, 0x00))                    # zero-ADD hold
                table.append((0x00, 0x00))                    # count 0 -> 256-frame hold
                table.append((0x90, (s + 1) & 0xFF))
            return s

        _f4 = getattr(m, 'pulse_ctr_8bit', False)
        # Overflow-gated identical-pulse-program dedup (mirrors the wave-pool dedup,
        # ledger C8). A family-4 OFF-TABLE pulse program is large (a one-shot ramp
        # captured to _PHASE_CAP ~= 97 bytes), so many instruments sharing a few
        # programs overflow the 256-byte single-byte pulsepos when un-shared (Jupiter41:
        # 16 insts, 5 distinct programs -> 356 bytes un-shared, 209 shared). When the
        # un-shared pool would overflow, share identical (start, phases, loop) programs:
        # byte-identical for the write stream (each note re-inits pulsepos to the program
        # start and reads the same sequence). Gated to overflow-only — non-overflow
        # members keep their exact un-shared layout (pulse sharing is position-dependent
        # like wave, via the absolute $90 markers), so this is zero-regression by
        # construction (never touches a member that already builds).
        _pulse_undedup = len(pulse) + sum(_env_bytes(i.pulse_env)
                                          for i in usf.instruments if i.pulse_env)
        _pulse_dedup = _pulse_undedup > 256
        _pseen: dict = {}

        def add_pulse(env):
            key = (env.start, tuple(env.phases), env.loop)
            if _pulse_dedup and key in _pseen:
                return _pseen[key]
            _pad(pulse, _env_bytes(env), True)
            s = add_env(pulse, env)
            _pseen[key] = s
            return s

        # Overflow-gated FILTER-pool dedup — same as the pulse/wave pools (ledger C8). A
        # correctly-captured off-table filter program is large, so many instruments over
        # few programs overflow the 256-byte filterpos un-shared; share identical programs
        # when the un-shared pool would overflow. Gated to overflow-only -> zero-regression.
        _filter_undedup = len(filt) + sum(_env_bytes(i.filter_env)
                                          for i in usf.instruments if i.filter_env)
        _filter_dedup = _filter_undedup > 256
        _fseen: dict = {}

        def add_filter(env):
            key = (env.start, tuple(env.phases), env.loop)
            if _filter_dedup and key in _fseen:
                return _fseen[key]
            _pad(filt, _env_bytes(env), True)
            s = add_env_f4(filt, env) if _f4 else add_env(filt, env)
            _fseen[key] = s
            return s

        ptrs = []
        for inst in usf.instruments:
            wptr = add_wave(inst.waveform, inst.wave_freq, inst.loop)
            pptr = add_pulse(inst.pulse_env) if inst.pulse_env else 0
            fptr = add_filter(inst.filter_env) if inst.filter_env else 0
            ptrs.append((wptr, pptr, fptr))
        return wave, pulse, filt, ptrs

    wave, pulse, filt, ptrs = _build_pools(paged=False)
    if _FORCE_PAGED:                       # dev knob: exercise pass 2 on a
        wave, pulse, filt, ptrs = _build_pools(paged=True)   # fitting member
        m.instr_pages = [(w >> 8, p >> 8, f >> 8) for (w, p, f) in ptrs]
        m.force_paged = True
    # pulsepos / filterpos / wavepos are byte-indexed in the engine: a pool past
    # 256 entries cannot be addressed by the un-paged layout. Re-lay it out
    # page-padded (pass 2) and record each instrument's page triple for the
    # composer's per-voice page-select SMC. Non-overflow members never reach
    # pass 2 and stay byte-identical. (The offtable_live_pos refusal happens
    # UPSTREAM, at the extract boundary in write_v5_usf — the fact it needs is
    # extract-side and deliberately not in the USF; a live-pos USF handed
    # straight to this function builds paged and lets verify judge it.)
    over = [nm for nm, t in (('wave', wave), ('pulse', pulse),
                             ('filter', filt)) if len(t) > 256]
    mirror = defused_pool_overflow(usf)
    if set(over) != set(mirror):
        # drift tripwire: the size-only mirror the extract's refusal relies on
        # must agree with the real packer, every build
        raise RuntimeError(
            f'defused_pool_overflow mirror drifted: packer={over} mirror={mirror}')
    if over:
        wave, pulse, filt, ptrs = _build_pools(paged=True)
        m.instr_pages = [(w >> 8, p >> 8, f >> 8) for (w, p, f) in ptrs]

    for inst, (wptr, pptr, fptr) in zip(usf.instruments, ptrs):
        v = inst.vibrato
        m.instruments.append(V5Instrument(
            id=inst.id, ad=inst.adsr[0], sr=inst.adsr[1],
            wave_ptr=wptr & 0xFF, pulse_ptr=pptr & 0xFF,
            filter_ptr=fptr & 0xFF,
            vib_delay=v.onset, vib_speed=v.speed, vib_width=v.amplitude,
            offtable_freq=list(getattr(inst, 'offtable_freq', []) or [])))

    m.wave = wave
    m.pulse = pulse
    m.filter = filt

    # ---- sectors: content-dedup the patterns of ALL subtunes' voices into
    #      one shared global pool; remap orderlist entries to it -----------
    from pipelines.dmc.v5.extract.engine_model import V5Subtune
    pool, by_bytes, remap = [], {}, {}
    _ipos = {inst.id: n for n, inst in enumerate(usf.instruments)}
    for usub in usf.subtunes:
        for voice in usub.voices:
            for pat in voice.patterns:
                enc = _encode_sector(pat.rows, _ipos)
                idx = by_bytes.get(enc)
                if idx is None:
                    idx = len(pool)
                    pool.append(enc)
                    by_bytes[enc] = idx
                remap[pat.id] = idx
    m.sectors = [None] * len(pool)
    m.sector_raw = list(pool)

    # ---- per-subtune orderlist records (tempo -> speed, init.sid.master_vol
    #      -> master vol, the 3 voices -> orderlists) -------------------------
    for usub in usf.subtunes:
        usid = usub.init.sid if (usub.init and usub.init.sid) else None
        smvol = (usid.master_vol if usid and usid.master_vol is not None
                 else 0x0F)
        m.subtunes.append(V5Subtune(
            speed=usub.tempo, master_vol=smvol,
            orderlist_raw=[_encode_orderlist(v.orderlist, remap)
                           for v in usub.voices]))
    m.orderlist_raw = m.subtunes[0].orderlist_raw
    m.speed = m.subtunes[0].speed
    m.master_vol = m.subtunes[0].master_vol
    return m
