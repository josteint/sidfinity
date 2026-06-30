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

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
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
}


def _encode_sector(rows) -> bytes:
    out = bytearray()
    for row in rows:
        glide = glide_to = None
        for fl in row.fx_flags:
            key = fl.split('=', 1)[0]
            if key in _PREFIX_BYTE:
                out += bytes([_PREFIX_BYTE[key], _flag_val(fl) & 0xFF])
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
    # neither).
    spdctr = mvolfrac = 0
    if sub.params and sub.params.fields:
        spdctr = int(sub.params.fields.get('speed_ctr_init', 0))
        mvolfrac = int(sub.params.fields.get('fade_frac_init', 0))
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
        cia_period=(int(usf.params.fields.get('cia_period', 0))
                    if usf.params and usf.params.fields else 0),
        title=usf.psid.title, author=usf.psid.author,
        released=usf.psid.released,
    )
    # family-4 (Jupiter41) player flag + leftovers (Phase C composer knobs)
    pf = usf.params.fields if usf.params and usf.params.fields else {}
    if int(pf.get('family4', 0)):
        m.family4 = True
        m.f4_filtmode = int(pf.get('f4_filtmode', 0))
        m.f4_fcinit = int(pf.get('f4_fcinit', 0))
        m.f4_idle_notes = [int(pf.get('f4_note%d' % i, 0)) for i in range(3)]

    # ---- re-pack the shared wave table (idle program at index 0, then
    #      each instrument's program) and reassign pointers -------------
    wave = []

    def add_wave(ctrl, freq, loop):
        s = len(wave)
        freq = (list(freq) + [0] * len(ctrl))[:len(ctrl)]
        for c, f in zip(ctrl, freq):
            wave.append((c & 0xFF, f & 0xFF))
        wave.append((0x90, (s + loop) & 0xFF))       # V5 marker: freq = abs target
        return s

    ip = usf.wave_programs.get(0)
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
            pulse.append(((a >> 8) & 0xFF, a & 0xFF))                  # ADD
            pulse.append(((frames >> 8) & 0xFF, frames & 0xFF))        # count
        lp = dp.loop if dp.loop is not None else len(dp.phases) - 1
        pulse.append((0x90, (2 * lp) & 0xFF))                          # loop onto a phase
    else:
        pulse = [(0, 0)]                                               # null pos 0 (891 behavior)

    # ---- filter table position 0 = the V3 DEFAULT (idle) filter program, run
    #      from frame 0 (filterpos starts at 0). The real default_filter sweep
    #      when present, else a (0,0) HOLD (zero-ADD, count==0 = 65536-frame
    #      hold, $90 self-loop) so the composer can run filter_run for V3 every
    #      frame without an out-of-bounds count read. The idle program has NO
    #      start entry (it continues from the init.sid.filter priming cutoff) —
    #      its ADD/count pairs begin at position 0. ----------
    filt = []
    df = usf.default_filter
    if df is not None and df.phases:
        for rate, frames in df.phases:
            a = rate & 0xFFFF
            filt.append(((a >> 8) & 0xFF, a & 0xFF))                # ADD
            filt.append(((frames >> 8) & 0xFF, frames & 0xFF))      # count
        lp = df.loop if df.loop is not None else len(df.phases) - 1
        filt.append((0x90, (2 * lp) & 0xFF))                        # loop onto a phase
    else:
        filt = [(0, 0), (0, 0), (0x90, 0)]                          # hold at pos 0

    def add_env(table, env):
        s = len(table)
        table.append(((env.start >> 8) & 0xFF, env.start & 0xFF))   # init pair
        for rate, frames in env.phases:
            a = rate & 0xFFFF
            table.append(((a >> 8) & 0xFF, a & 0xFF))               # step
            table.append(((frames >> 8) & 0xFF, frames & 0xFF))     # count
        if env.phases:
            lp = env.loop if env.loop is not None else len(env.phases) - 1
            table.append((0x90, (s + 1 + 2 * lp) & 0xFF))      # loop onto a step
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

    for inst in usf.instruments:
        wptr = add_wave(inst.waveform, inst.wave_freq, inst.loop)
        pptr = add_env(pulse, inst.pulse_env) if inst.pulse_env else 0
        fptr = add_env(filt, inst.filter_env) if inst.filter_env else 0
        v = inst.vibrato
        m.instruments.append(V5Instrument(
            id=inst.id, ad=inst.adsr[0], sr=inst.adsr[1],
            wave_ptr=wptr, pulse_ptr=pptr, filter_ptr=fptr,
            vib_delay=v.onset, vib_speed=v.speed, vib_width=v.amplitude,
            offtable_freq=list(getattr(inst, 'offtable_freq', []) or [])))

    m.wave = wave
    m.pulse = pulse
    m.filter = filt
    # pulsepos / filterpos / wavepos are byte-indexed in the engine
    for nm, tbl in (('wave', wave), ('pulse', pulse), ('filter', filt)):
        if len(tbl) > 256:
            raise RuntimeError(f'unsupported:{nm}_table_overflow {len(tbl)}')

    # ---- sectors: content-dedup the patterns of ALL subtunes' voices into
    #      one shared global pool; remap orderlist entries to it -----------
    from pipelines.dmc.v5.extract.engine_model import V5Subtune
    pool, by_bytes, remap = [], {}, {}
    for usub in usf.subtunes:
        for voice in usub.voices:
            for pat in voice.patterns:
                enc = _encode_sector(pat.rows)
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
