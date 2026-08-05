"""USF — writer.

Serialize a `UsfFile` model to `.usf` text. The output is deterministic
and round-trip stable: `parse(write(model))` returns an equivalent
model, and `write(parse(text))` is byte-identical to canonicalised text.
"""

from __future__ import annotations

from src.usf.types import (
    UsfFile, PsidMeta, Params, InitVoice, InitState,
    InitSid, InitSidVoice, InitFilter,
    Instrument, PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig,
    FreqSlideConfig, IncBy2Config, SongEndConfig, InitBehaviorConfig,
    MasterVolConfig, SfxConfig,
    MusicSubtune, DigiSubtune, SfxSubtune, DmcSfxSubtune, SfxEngine,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
)


# Fields that should be emitted as hex (`$NN`) rather than decimal.
# The list is conservative — anything that's a byte-level / mask /
# memory-flavored value goes here. Adding a field doesn't break
# round-trip; it just affects how the writer formats it.
_HEX_FIELDS = {
    'linear_pw_or', 'ctrl', 'dur_field', 'pwm_period', 'slide_v',
    'incby2_onset', 'stop_fill', 'sfx_framectr_ofs', 'sfx_state_ofs',
    'instr_base', 'freq_table_base', 'init',
}


def _hex(value: int, width: int = 2) -> str:
    """Format `value` as `$XX...`. `width` is the minimum hex digits."""
    return f'${value:0{width}X}'


def _format_param_value(key: str, val) -> str:
    if isinstance(val, bool):
        return 'true' if val else 'false'
    if isinstance(val, int):
        return _hex(val) if key in _HEX_FIELDS else str(val)
    if isinstance(val, (list, tuple)):
        # Explicit + recursive, so the emitted form is guaranteed to match the
        # grammar's `param_list` rather than depending on Python's repr of a
        # sequence. Nesting is real: GoatTracker V1's `idle_priming` is a list
        # of per-voice lists.
        def _seq(v):
            if isinstance(v, (list, tuple)):
                return '[' + ', '.join(_seq(x) for x in v) + ']'
            return str(int(v))
        return _seq(val)
    if isinstance(val, str) and (' ' in val or not val.isidentifier()):
        return '"' + val + '"'                         # readable string knob
    return str(val)


def _format_init_value(key: str, val) -> str:
    if isinstance(val, InstrumentRef):
        return _format_instr_ref(val)
    if isinstance(val, str):
        return val
    if key in _HEX_FIELDS or key in {'ctrl', 'dur_field', 'pwm_period', 'slide_v'}:
        return _hex(val)
    return str(val)


def _format_instr_ref(ref: InstrumentRef) -> str:
    if ref.id is not None:
        return f'i{ref.id}'
    return f'i:{ref.name}'


def _format_pitch(p: Pitch) -> str:
    return str(p)


# ---------------------------------------------------------------------------
# Block writers
# ---------------------------------------------------------------------------

def _quote(s: str) -> str:
    """Quote a string for the USF grammar (ESCAPED_STRING): backslashes
    and embedded double quotes must be escaped (HVSC titles contain
    quotes, e.g. 'Jingle from the "Lenor" advert')."""
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _write_psid(p: PsidMeta) -> list[str]:
    lines = [
        'psid {',
        f'  title:      {_quote(p.title)}',
        f'  author:     {_quote(p.author)}',
        f'  released:   {_quote(p.released)}',
        f'  clock:      {p.clock}',
        f'  sid:        {p.sid}',
    ]
    # Multi-SID chip models — only when the header states one explicitly
    # (None = Unknown = "same as the first SID", elided).
    if p.sid2 is not None:
        lines.append(f'  sid2:       {p.sid2}')
    if p.sid3 is not None:
        lines.append(f'  sid3:       {p.sid3}')
    if p.start_song != 1:                 # elidability: absent = default 1
        lines.append(f'  start_song: {p.start_song}')
    if p.speed:
        lines.append(f'  speed:      ${p.speed:08X}')
    lines.append('}')
    return lines


def _write_params(p: Params) -> list[str]:
    if not p.fields:
        return ['params {', '}']
    lines = ['params {']
    # Sort by key for determinism
    for k in sorted(p.fields.keys()):
        v = p.fields[k]
        lines.append(f'  {k}: {_format_param_value(k, v)}')
    lines.append('}')
    return lines


def _write_init_voice(v: InitVoice) -> str:
    # DEFAULT-VALUED FIELDS ARE ELIDED (2026-08-03): the parser constructs
    # InitVoice(id=...) and sets only the fields present, so an absent field
    # IS its dataclass default — "absent = don't prime", the trichotomy's own
    # doctrine for priming state. Emitting `ctrl: $00 dur_field: $00 ...` on
    # every voice was noise: it buried the one or two load-bearing values
    # (DMC's note/gate_mask work-file leftovers) under five defaults, and fed
    # the ML corpus five tokens of nothing. Elision is writer-only: the
    # parsed object round-trips identically, so every built .sid is
    # byte-identical by construction (gate: usf_corpus_check + the
    # round-trip equality test below in tests).
    parts = []
    if v.ctrl is not None and v.ctrl != 0:
        parts.append(f'ctrl: {_hex(v.ctrl)}')
    if v.dur_field != 0:
        parts.append(f'dur_field: {_hex(v.dur_field)}')
    if v.pwm_period != 0:
        parts.append(f'pwm_period: {_hex(v.pwm_period)}')
    if v.pwm_dir != 'up':
        parts.append(f'pwm_dir: {v.pwm_dir}')
    if v.instr is not None:
        parts.append(f'instr: {_format_instr_ref(v.instr)}')
    if v.slide_v != 0:
        parts.append(f'slide_v: {_hex(v.slide_v)}')
    if v.note is not None:
        parts.append(f'note: {v.note}')
    if v.gate_mask is not None:
        parts.append(f'gate_mask: {_hex(v.gate_mask)}')
    if v.guard is not None:
        parts.append(f'guard: {_hex(v.guard)}')
    if v.dur_reload is not None:
        parts.append(f'dur_reload: {_hex(v.dur_reload)}')
    if getattr(v, 'glide_note', None) is not None:
        parts.append(f'glide_note: {_hex(v.glide_note)}')
    if getattr(v, 'glide_target', None) is not None:
        parts.append(f'glide_target: {_hex(v.glide_target)}')
    if getattr(v, 'note_active', False):
        parts.append('note_active: 1')
    if getattr(v, 'sliding', False):
        parts.append('sliding: 1')
    if getattr(v, 'freq', None) is not None:
        parts.append(f'freq: {_hex(v.freq, 4)}')
    if getattr(v, 'slide_freq', None) is not None:
        parts.append(f'slide_freq: {_hex(v.slide_freq, 4)}')
    if getattr(v, 'slide_rate', None) is not None:
        parts.append(f'slide_rate: {_hex(v.slide_rate, 4)}')
    if getattr(v, 'pulse_width', None) is not None:
        parts.append(f'pulse_width: {_hex(v.pulse_width, 4)}')
    if not parts:                      # all-defaults voice: keep the line (the
        return f'  voice {v.id} {{ }}'  # object stays in init.voices on parse)
    return f'  voice {v.id} {{ ' + '  '.join(parts) + ' }'


def _write_init_sid_voice(v: InitSidVoice) -> str:
    parts = []
    if v.envelope_prime is not None:
        ad, sr = v.envelope_prime
        parts.append(f'envelope_prime: ({_hex(ad)}, {_hex(sr)})')
    if v.pw_init is not None:
        parts.append(f'pw_init: {_hex(v.pw_init, 4)}')
    if getattr(v, 'ctrl_init', None) is not None:
        parts.append(f'ctrl_init: {_hex(v.ctrl_init)}')
    if getattr(v, 'freq_init', None) is not None:
        parts.append(f'freq_init: {_hex(v.freq_init, 4)}')
    return f'    voice {v.id} {{ ' + '  '.join(parts) + ' }'


def _write_init_sid(sid: InitSid, chip: int = 1) -> list[str]:
    # chip 1 is always the bare `sid {` form; 2/3 name the chip
    lines = ['  sid {' if chip == 1 else f'  sid {chip} {{']
    if sid.master_vol is not None:
        lines.append(f'    master_vol: {_hex(sid.master_vol)}')
    if sid.filter is not None:
        f = sid.filter
        parts = []
        if f.cutoff_lo:
            parts.append(f'cutoff_lo: {_hex(f.cutoff_lo)}')
        if f.cutoff_hi:
            parts.append(f'cutoff_hi: {_hex(f.cutoff_hi)}')
        if f.res_routing:
            parts.append(f'res_routing: {_hex(f.res_routing)}')
        # An all-zero InitFilter carries no priming (identical to no block);
        # emitting `filter {  }` would be rejected by the grammar (it requires
        # at least one field). Omit the block entirely in that case.
        if parts:
            lines.append('    filter { ' + '  '.join(parts) + ' }')
    for v in sorted(sid.voices, key=lambda x: x.id):
        lines.append(_write_init_sid_voice(v))
    lines.append('  }')
    return lines


def _write_environment(env) -> list[str]:
    lines = ['environment {  ; how the host drives play(): CIA rate / per-VBI repeats']
    if env.cia_period:
        lines.append(f'  cia_period: {_hex(env.cia_period, 4)}')
    if env.play_repeat != 1:
        lines.append(f'  play_repeat: {env.play_repeat}')
    lines.append('}')
    return lines


def _write_init(state: InitState) -> list[str]:
    lines = ['init {']
    if getattr(state, 'slide_phase', None) is not None:
        lines.append(f'  slide_phase: {state.slide_phase}')
    if getattr(state, 'speed_ctr_init', 0):
        lines.append(f'  speed_ctr_init: {state.speed_ctr_init}')
    if getattr(state, 'fade_frac_init', 0):
        lines.append(f'  fade_frac_init: {state.fade_frac_init}')
    if getattr(state, 'filter_arm_cutoff', 0):
        lines.append(f'  filter_arm_cutoff: {_hex(state.filter_arm_cutoff)}')
    if getattr(state, 'filter_arm_frames', 0):
        lines.append(f'  filter_arm_frames: {state.filter_arm_frames}')
    if state.sid is not None:
        lines.extend(_write_init_sid(state.sid))
    if getattr(state, 'sid2', None) is not None:
        lines.extend(_write_init_sid(state.sid2, 2))
    if getattr(state, 'sid3', None) is not None:
        lines.extend(_write_init_sid(state.sid3, 3))
    for v in sorted(state.voices, key=lambda x: x.id):
        lines.append(_write_init_voice(v))
    lines.append('}')
    return lines


def _write_pwm(p: PwmConfig) -> 'str | None':
    """Returns the `pwm: ...` line, or None when the config equals the
    constructor default (caller skips the line; the parser's absent-line
    value IS PwmConfig() via Instrument's default_factory, so object
    equality round-trips exactly). Field-level: every field elides at its
    dataclass default (the elidability principle, 2026-08-03 — the always-
    emitted `speed=0 min_hi=0` were census-flagged default noise)."""
    if p == PwmConfig():
        return None
    parts = []
    if p.mode != 'none':
        parts.append(f'mode={p.mode}')
    if p.speed:
        parts.append(f'speed={p.speed}')
    if p.init:
        parts.append(f'init={_hex(p.init, 4)}')
    if p.min_hi:
        parts.append(f'min_hi={p.min_hi}')
    if p.max_hi:
        parts.append(f'max_hi={p.max_hi}')
    # Emit phase1_* only when any of them is non-default (keeps Hubbard
    # USFs visually unchanged on round-trip).
    if p.phase1_dir != 'up' or p.phase1_bound != 0 or p.phase1_step != 0:
        parts.append(f'phase1_dir={p.phase1_dir}')
        parts.append(f'phase1_bound={_hex(p.phase1_bound)}')
        parts.append(f'phase1_step={_hex(p.phase1_step)}')
    if p.lo_or_mask:
        parts.append(f'lo_or_mask={_hex(p.lo_or_mask)}')
    if p.speed_steps:
        parts.append('speed_steps=[' + ', '.join(str(s) for s in p.speed_steps) + ']')
        # split form only: always stated (even 0) — its PRESENCE is the
        # form marker distinguishing true step values from legacy packed
        if p.step_base is not None:
            parts.append(f'step_base={p.step_base}')
    if p.keep_running:
        parts.append('keep_running=true')
    return 'pwm:      ' + ' '.join(parts)


def _write_arp(a: ArpConfig) -> 'str | None':
    """None when the config equals ArpConfig() — the census's biggest
    finding (`arp: offsets=[] period=1` printed in ~11.3k files was the
    no-arpeggio identity). Field-level elision at dataclass defaults."""
    if a == ArpConfig():
        return None
    parts = []
    if a.offsets:
        offs = ', '.join(str(o) for o in a.offsets)
        parts.append(f'offsets=[{offs}]')
    if a.period != 1:
        parts.append(f'period={a.period}')
    if a.interval != 12:
        parts.append(f'interval={a.interval}')
    if a.phase_invert:
        parts.append('phase_invert=true')
    return 'arp:      ' + ' '.join(parts)


def _write_vibrato(v: VibratoConfig) -> 'str | None':
    """None when the config equals VibratoConfig(). NB DMC's inert vibrato
    is `scale=0 onset=0`, which is NOT the constructor default (onset 6) —
    that line shrinks to `vibrato: onset=0` here; making it vanish is an
    EXTRACT-side question (should DMC leave onset at 6 when amplitude==0?)
    parked for the deeper cleanup — it changes the parsed object, so it
    needs the build-MD5 gate, not the writer-safety gate."""
    if v == VibratoConfig():
        return None
    parts = []
    if v.scale:
        parts.append(f'scale={v.scale}')
    if v.onset != 6:
        parts.append(f'onset={v.onset}')
    # Descriptive parameters — emit only when non-default so existing
    # USFs stay visually unchanged for the common (Hubbard) defaults.
    if v.shape != 'triangle':
        parts.append(f'shape={v.shape}')
    if v.period_frames != 8:
        parts.append(f'period_frames={v.period_frames}')
    if v.polarity != 'unipolar':
        parts.append(f'polarity={v.polarity}')
    if v.depth_semitones:
        # Trim trailing zeros for readability (1.5 not 1.500000).
        parts.append(f'depth_semitones={v.depth_semitones:g}')
    # FC v1 additions — emit only when non-default
    if v.amplitude:
        parts.append(f'amplitude={v.amplitude}')
    if v.speed:
        parts.append(f'speed={v.speed}')
    if v.direction != 'up':
        parts.append(f'direction={v.direction}')
    if v.ramp:
        parts.append(f'ramp={v.ramp}')
    return 'vibrato:  ' + ' '.join(parts)


def _write_envelope(e: EnvelopeConfig) -> str | None:
    """Returns the `envelope: ...` line, or None when all fields are
    default (caller skips emission entirely).

    Phase 3c — `gate_off_delta` and `adsr_zero_delta` are dropped from
    the schema. The placeholder `envelope: gate_off_delta=0
    adsr_zero_delta=0` line is gone — engines without release_ctrl
    (Companion family) just omit the envelope line.
    """
    parts = []
    if e.release_ctrl:
        parts.append(f'release_ctrl={_hex(e.release_ctrl)}')
    if e.gate_mode != 'hold':
        parts.append(f'gate_mode={e.gate_mode}')
    if e.gate_open:
        parts.append('gate_open=1')
    if not parts:
        return None
    return 'envelope: ' + ' '.join(parts)


def _write_slide(s: FreqSlideConfig) -> str:
    parts = [f'mode={s.mode}']
    if s.initial_dir != 'up':
        parts.append(f'initial_dir={s.initial_dir}')
    if s.upper_delta:
        parts.append(f'upper_delta={s.upper_delta}')
    if s.lower_delta:
        parts.append(f'lower_delta={s.lower_delta}')
    if s.step:
        parts.append(f'step={_hex(s.step, 4)}')
    if s.high_oct_arp:
        parts.append('high_oct_arp=true')
    if s.half_rate:
        parts.append('half_rate=true')
    return 'slide:    ' + ' '.join(parts)


def _write_incby2(b: IncBy2Config) -> str:
    parts = [f'mode={b.mode}']
    if b.step != 1:
        parts.append(f'step={b.step}')
    if b.onset:
        parts.append(f'onset={b.onset}')
    if b.late_gate:
        parts.append(f'late_gate={b.late_gate}')
    if b.every_frame:
        parts.append('every_frame=true')
    return 'incby2:   ' + ' '.join(parts)


def _write_arp_programs(progs: dict) -> list[str]:
    """Emit `arp_programs { prog N: [o0, o1, ...] }` (FC arp library)."""
    lines = ['arp_programs {']
    for n in sorted(progs):
        offs = ', '.join(str(o) for o in progs[n])
        lines.append(f'  prog {n}: [{offs}]')
    lines.append('}')
    return lines


def _write_pulse_programs(progs: dict) -> list[str]:
    """Emit `pulse_programs { prog N: lo=.. hi=.. [wrap] seg T S [flip] }`."""
    lines = ['pulse_programs {']
    for n in sorted(progs):
        p = progs[n]
        parts = [f'lo={p["lo"]}', f'hi={p["hi"]}']
        if p.get('wrap'):
            parts.append('wrap')
        for thr, step, flip in p['segs']:
            parts.append(f'seg {thr} {step}' + (' flip' if flip else ''))
        lines.append(f'  prog {n}: ' + ' '.join(parts))
    lines.append('}')
    return lines


def _write_filter_programs(progs: dict) -> list[str]:
    """Emit `filter_programs { prog N: init= [onset=] d418= final= end=
    seg T A ... }` — onset only when non-zero (Tel programs omit it)."""
    lines = ['filter_programs {']
    for n in sorted(progs):
        p = progs[n]
        if 'res' in p:           # duration-based shape (DMC)
            parts = [f'res={p["res"]}', f'mode={p["mode"]}',
                     f'init={p["init"]}', f'repeat={p["repeat"]}',
                     f'stop={p["stop"]}']
            for d, f in p['steps']:
                parts.append(f'step ({d}, {f})')
            lines.append(f'  prog {n}: ' + ' '.join(parts))
            continue
        parts = [f'init={p["init"]}']
        if p.get('onset'):
            parts.append(f'onset={p["onset"]}')
        parts += [f'd418={p["d418"]}',
                  f'final={p["final"]}', f'end={p["end"]}']
        for thr, add in p['segs']:
            parts.append(f'seg {thr} {add}')
        lines.append(f'  prog {n}: ' + ' '.join(parts))
    lines.append('}')
    return lines


def _write_filter_mod(mods: dict) -> list[str]:
    """Emit `filter_mod { prog N: start= init_phase= stop_phase=
    step (d, f) ... }` — the song-global looped cutoff LFO."""
    lines = ['filter_mod {  ; song-global looped cutoff LFO (two phase-offset taps)']
    for n in sorted(mods):
        m = mods[n]
        parts = [f'start={m["start"]}', f'init_phase={m["init_phase"]}',
                 f'stop_phase={m["stop_phase"]}']
        for d, f in m['steps']:
            parts.append(f'step ({d}, {f})')
        lines.append(f'  prog {n}: ' + ' '.join(parts))
    lines.append('}')
    return lines


def _write_drum_programs(progs: dict) -> list[str]:
    """Emit `drum_programs { drum N: wave=[..] tone=[..] }`."""
    lines = ['drum_programs {']
    for n in sorted(progs):
        p = progs[n]
        w = ', '.join(str(x) for x in p['wave'])
        t = ', '.join(str(x) for x in p['tone'])
        lines.append(f'  drum {n}: wave=[{w}] tone=[{t}]')
    lines.append('}')
    return lines


def _write_wave_programs(progs: dict) -> list[str]:
    """Emit `wave_programs { prog N: ctrl=[..] freq=[..] }`."""
    lines = ['wave_programs {  ; per-frame waveform + pitch envelopes, by note frame-counter']
    for n in sorted(progs):
        p = progs[n]
        c = ', '.join(str(x) for x in p['ctrl'])
        f = ', '.join(str(x) for x in p['freq'])
        tail = f' loop={p["loop"]}' if 'loop' in p else ''
        lines.append(f'  prog {n}: ctrl=[{c}] freq=[{f}]{tail}')
    lines.append('}')
    return lines


def _wave_name(b: int) -> str:
    """SID waveform bits (bit4 tri, bit5 saw, bit6 pulse, bit7 noise)."""
    w, names = b & 0xF0, []
    if w & 0x80:
        names.append('noise')
    if w & 0x40:
        names.append('pulse')
    if w & 0x20:
        names.append('saw')
    if w & 0x10:
        names.append('triangle')
    return '+'.join(names)


def _instrument_fingerprint(i: Instrument) -> str:
    """A one-line, human-readable timbre/articulation summary — a PURE function
    of the instrument's musical fields (regenerated on every write, so it never
    drifts), read in temporal order attack -> body -> modulation. Describes the
    musical ROLE only, never engine addresses. Emitted as a `;` comment, which
    the reader %ignores, so it is writer-only and can't affect the rebuild."""
    fx = getattr(i, 'effects', None) or frozenset()
    wf = i.waveform or []
    parts = []
    if 'noise_attack' in fx:                       # attack transient first
        parts.append('noise-attack')
    if 'drum' in fx:
        parts.append('drum — percussive, no melodic pitch')
    else:
        seen = []
        for b in wf:                               # body: waveform character
            nm = _wave_name(b)
            if nm and nm not in seen:
                seen.append(nm)
        if len(seen) > 1:
            parts.append('wavetable ' + '/'.join(seen[:3]))
        elif seen:
            parts.append(seen[0])
        if getattr(getattr(i, 'pwm', None), 'mode', 'none') not in ('none', None) \
                and any(b & 0x40 for b in wf):
            parts.append('PWM sweep')
        wfr = i.wave_freq or []
        if len(wfr) > 2 and len(set(wfr)) > 2:
            parts.append('arpeggio')
        ad, sr = (i.adsr or (0, 0))                # articulation from ADSR
        atk, sus = (ad >> 4) & 0xF, (sr >> 4) & 0xF
        if atk <= 1 and sus <= 3:
            parts.append('plucked')
        elif atk >= 8:
            parts.append('soft swell')
        elif sus >= 12:
            parts.append('sustained')
    vib = getattr(i, 'vibrato', None)              # modulation
    if getattr(vib, 'amplitude', 0):
        onset = getattr(vib, 'onset', 0)
        parts.append(f'vibrato (after {onset}f)' if onset else 'vibrato')
    if getattr(getattr(i, 'freq_slide_config', None), 'mode', 'none') \
            not in ('none', None):
        parts.append('portamento')
    if getattr(getattr(i, 'filter_prog', None), 'program', 0):
        parts.append('filtered')
    return ', '.join(parts) if parts else 'tone'


def _write_instrument(i: Instrument) -> list[str]:
    head = f'instrument {i.id}'
    if i.name:
        head += f' {i.name}'
    lines = [head + ' {', f'  ; {_instrument_fingerprint(i)}']
    if i.waveform:
        wave = ' '.join(_hex(b) for b in i.waveform)
        lines.append(f'  waveform: {wave}')
        lines.append(f'  loop:     {i.loop}')
    if i.wave_freq:
        wf = ', '.join(str(v) for v in i.wave_freq)
        lines.append(f'  wave_freq: [{wf}]')
    if getattr(i, 'wave_abs', None):
        wa = ', '.join(str(int(v)) for v in i.wave_abs)
        lines.append(f'  wave_abs: [{wa}]')
    if getattr(i, 'wave_filter', None):
        wfi = ' '.join(_hex(b) for b in i.wave_filter)
        lines.append(f'  wave_filter: {wfi}')
    if getattr(i, 'offtable_freq', None):
        def _slot(v):
            # a slot is a fixed byte or a named live-signal reference
            # (live-signal modulation §3.1); voiceless = a global signal
            if hasattr(v, 'name') and hasattr(v, 'voice'):
                return (f'{v.name}(v{v.voice})' if v.voice is not None
                        else f'{v.name}()')
            return str(int(v))

        def _ofreq(rec):
            s, n, lo, hi = rec[:4]
            if not isinstance(lo, int) or not isinstance(hi, int):
                return f'at({s}, {n}, {_slot(lo)}, {_slot(hi)})'
            kw = 'live' if (len(rec) > 4 and rec[4]) else 'at'
            return f'{kw}({s}, {n}, {lo}, {hi})'
        entries = ' '.join(_ofreq(r) for r in i.offtable_freq)
        lines.append(f'  offtable_freq: {entries}')
    if getattr(i, 'wave_table_pos', None) is not None:
        lines.append(f'  wave_table_pos: {i.wave_table_pos}')
    if getattr(i, 'record_offset', None) is not None:
        lines.append(f'  record_offset: {i.record_offset}')
    if getattr(i, 'wave_start', None) is not None:
        lines.append(f'  wave_start: {i.wave_start}')
    if getattr(i, 'wave_start_on_marker', False):
        lines.append('  wave_start_on_marker: 1')
    # pwm/arp/vibrato follow the envelope precedent: None = the config is
    # its constructor default = the parser's absent-line value — skip.
    pwm_line = _write_pwm(i.pwm)
    if pwm_line is not None:
        lines.append(f'  {pwm_line}')
    lines.append(f'  adsr:     {_hex(i.adsr[0])} {_hex(i.adsr[1])}')
    arp_line = _write_arp(i.arp)
    if arp_line is not None:
        lines.append(f'  {arp_line}')
    vib_line = _write_vibrato(i.vibrato)
    if vib_line is not None:
        lines.append(f'  {vib_line}')
    env_line = _write_envelope(i.envelope)
    if env_line is not None:
        lines.append(f'  {env_line}')
    # Phase 3c — emit the per-inst sub-configs when active. The legacy
    # `fx: freq_slide / inc_by2` flag line is gone — its info now
    # lives in the slide / incby2 blocks below.
    if i.freq_slide_config.mode != 'none':
        lines.append(f'  {_write_slide(i.freq_slide_config)}')
    if i.inc_by2_config.mode != 'none':
        lines.append(f'  {_write_incby2(i.inc_by2_config)}')
    # FC v1 — emit decomposed effect blocks only when active.
    pp = i.pulse_prog
    if pp.program or pp.increment:
        pp_parts = []
        if pp.program:
            pp_parts.append(f'program={pp.program}')
        if pp.increment:
            pp_parts.append(f'increment={pp.increment}')
        lines.append('  pulse_prog: ' + ' '.join(pp_parts))
    for label, env in (('pulse_env', i.pulse_env),
                       ('filter_env', i.filter_env)):
        if env is None:
            continue
        parts = [f'start={_hex(env.start, 4)}']
        if env.loop is not None:
            parts.append(f'repeat={env.loop}')
        for rate, frames in env.phases:
            parts.append(f'seg ({rate}, {_hex(frames, 4)})')
        lines.append(f'  {label}: ' + ' '.join(parts))
    fp = i.filter_prog
    if (fp.program or fp.strange or fp.double_voice or fp.aux_bits
            or fp.keep_running):
        fp_parts = []
        if fp.program:
            fp_parts.append(f'program={fp.program}')
        if fp.keep_running:
            fp_parts.append('keep_running=true')
        if fp.strange:
            fp_parts.append('strange=true')
        if fp.double_voice:
            fp_parts.append('double_voice=true')
        if fp.aux_bits:
            fp_parts.append(f'aux_bits={_hex(fp.aux_bits)}')
        lines.append('  filter_prog: ' + ' '.join(fp_parts))
    if i.effects:
        # Deterministic order matching the bit positions in fx3
        order = ['filter_program', 'pulse_run', 'tone_arp', 'pulse_arp',
                 'drum', 'tonesweep_up', 'wave_arp', 'noise_tick',
                 'noise_attack']
        emitted = [n for n in order if n in i.effects]
        lines.append('  effects: ' + ' '.join(emitted))
    lines.append('}')
    return lines


def _write_orderlist(o: Orderlist) -> str:
    parts = []
    for i, e in enumerate(o.entries):
        rep = o.repeat_at(i)
        vi = o.voiceinc_at(i)
        s = str(e)
        if getattr(o, 'stated', False):
            # stated form: b[~i][*r][+c][!k][^d]; +c emitted iff a command
            # byte exists (incl. +0 / redundant re-statements)
            intro = (o.intro_entries[i]
                     if i < len(getattr(o, 'intro_entries', []) or []) else None)
            if intro is not None:
                s += f'~{intro}'
            if rep != 1:
                s += f'*{rep}'
            mark = (o.stated_marks[i]
                    if i < len(getattr(o, 'stated_marks', []) or []) else None)
            if mark is not None:
                s += f'+{mark}' if mark >= 0 else f'{mark}'
            extra = (o.extra_cmds[i]
                     if i < len(getattr(o, 'extra_cmds', []) or []) else 0)
            if extra:
                s += f'!{extra}'
            vm = (o.stated_vmarks[i]
                  if i < len(getattr(o, 'stated_vmarks', []) or []) else None)
            if vm is not None:
                s += f'^{vm}'
            parts.append(s)
            continue
        tr = o.transpose_at(i)
        if rep != 1:
            s += f'*{rep}'
        if tr:
            s += f'+{tr}' if tr > 0 else f'{tr}'
        if vi:
            s += f'^{vi}'
        parts.append(s)
    if o.loop_to is not None:
        s = f'loop@{o.loop_to}'
        if getattr(o, 'stated', False):
            # stated lists: the pickup is DERIVED (head unmarked inherits
            # the carried value); only a TRAILING stated command needs
            # serializing — `+T` on the terminator IS that command.
            tr = getattr(o, 'stated_trail', None)
            if tr is not None:
                s += (f'+{tr}' if tr >= 0 else f'-{-tr}')
        elif o.loop_transpose is not None:
            s += (f'+{o.loop_transpose}' if o.loop_transpose >= 0
                  else f'-{-o.loop_transpose}')
        parts.append(s)
    elif o.stop:
        parts.append('stop')
    return ' '.join(parts)


def _write_pattern(p: Pattern) -> list[str]:
    length = f' length={p.length}' if p.length is not None else ''
    lines = [f'    pattern {p.id}{length} {{']
    # Column-align pitch / duration / instrument / flags. A row with no
    # duration (stated-inherited) keeps an empty column for alignment.
    for row in p.rows:
        pitch = _format_pitch(row.pitch)
        dur = str(row.duration) if row.duration is not None else ''
        instr = _format_instr_ref(row.instr) if row.instr else ''
        flags = ' '.join(row.fx_flags)
        parts = [pitch.ljust(3), dur.rjust(3)]
        if instr:
            parts.append(instr)
        if flags:
            parts.append(flags)
        lines.append('      ' + '  '.join(parts).rstrip())
    lines.append('    }')
    return lines


def _write_voice(v: VoiceBlock) -> list[str]:
    lines = [f'  voice {v.id} {{']
    kw = 'orderlist stated:' if getattr(v.orderlist, 'stated', False) \
        else 'orderlist:'
    lines.append(f'    {kw} {_write_orderlist(v.orderlist)}')
    for p in sorted(v.patterns, key=lambda x: x.id):
        lines.extend(_write_pattern(p))
    lines.append('  }')
    return lines


def _write_subtune(s) -> list[str]:
    if isinstance(s, MusicSubtune):
        lines = [f'subtune {s.id} music {{']
        lines.append(f'  tempo: {s.tempo}')
        if getattr(s, 'tempo2', None) is not None:
            lines.append(f'  tempo 2: {s.tempo2}')
        if getattr(s, 'tempo3', None) is not None:
            lines.append(f'  tempo 3: {s.tempo3}')
        if getattr(s, 'origin_engine', None):
            lines.append(f'  origin_engine: {s.origin_engine}')
        if s.is_sfx:
            lines.append('  is_sfx: true')
        if s.params is not None and s.params.fields:
            # Indent the per-subtune params block under the subtune.
            for line in _write_params(s.params):
                lines.append('  ' + line)
        if s.init is not None:
            # Indent the per-subtune init block under the subtune.
            for line in _write_init(s.init):
                lines.append('  ' + line)
        # Per-subtune overrides of normally file-level content (a compilation
        # whose packed players tune differently / carry their own idle sweep).
        if getattr(s, 'freq_table', None):
            for line in _write_freq_table(s.freq_table):
                lines.append('  ' + line)
        if getattr(s, 'default_filter', None) is not None:
            lines.append('  ' + _write_swenv('default_filter',
                                             s.default_filter))
        if getattr(s, 'wave_programs', None):
            for line in _write_wave_programs(s.wave_programs):
                lines.append('  ' + line)
        for v in s.voices:
            lines.extend(_write_voice(v))
        # one global block per chip; chip 1 is always the bare form
        for chip, track in ((1, s.global_track),
                            (2, getattr(s, 'global_track2', [])),
                            (3, getattr(s, 'global_track3', []))):
            if not track:
                continue
            lines.append('  global {' if chip == 1 else f'  global {chip} {{')
            for e in track:
                parts = [f'{k}={_hex(v)}' for k, v in
                         (('dyn', e.dyn), ('cutoff', e.cutoff),
                          ('cutoff_lo', getattr(e, 'cutoff_lo', None)),
                          ('res', e.res), ('mode', e.mode), ('route', e.route)) if v is not None]
                lines.append(f'    at {e.step} ' + ' '.join(parts))
            lines.append('  }')
        lines.append('}')
        return lines
    if isinstance(s, DigiSubtune):
        return [f'subtune {s.id} digi {{', f'  sample: {s.sample}', '}']
    if isinstance(s, SfxSubtune):
        lines = [f'subtune {s.id} sfx {{']
        lines.append('  v1: ' + ' '.join(_hex(b) for b in s.v1))
        lines.append('  v2: ' + ' '.join(_hex(b) for b in s.v2))
        lines.append(
            f'  sweep: start={_hex(s.start_index)} end={_hex(s.end_index)} '
            f'rate={s.rate} direction={s.direction}')
        lines.append(f'  v2_offset: {_hex(s.v2_offset)}')
        flags = []
        if s.toggle_v1: flags.append('toggle_v1')
        if s.toggle_v2: flags.append('toggle_v2')
        if s.skip_v1:   flags.append('skip_v1')
        if s.skip_both: flags.append('skip_both')
        if flags:
            lines.append('  flags: ' + ' '.join(flags))
        if s.extended_freq:
            lines.append('  extended_freq {')
            for off in sorted(s.extended_freq):
                lines.append(f'    {_hex(off)}: {_hex(s.extended_freq[off])}')
            lines.append('  }')
        lines.append('}')
        return lines
    if isinstance(s, DmcSfxSubtune):
        return [f'subtune {s.id} dmcsfx {{', f'  song: {s.song}', '}']
    raise TypeError(f'unknown subtune type: {type(s).__name__}')


def _write_dmc_sfx(e: SfxEngine) -> list[str]:
    def _bl(name, data):
        return f'  {name}: ' + ' '.join(_hex(b) for b in data)
    lines = ['dmc_sfx {  ; embedded SFX sequencer: shared tables + per-song trigger records']
    lines.append(f'  init_counter: {e.init_counter}')
    lines.append(f'  live_counter_fidx: {e.live_counter_fidx}')
    lines.append(_bl('filter_lfo', e.filter_lfo))
    lines.append(_bl('wave_table', e.wave_table))
    lines.append(_bl('freq_lo', e.freq_lo))
    lines.append(_bl('freq_hi', e.freq_hi))
    for i, ins in enumerate(e.instruments):
        lines.append(f'  instrument {i} {{')
        lines.append('    ctrl: ' + ' '.join(_hex(b) for b in ins.ctrl))
        lines.append('    freqbase: ' + ' '.join(_hex(b) for b in ins.freqbase))
        lines.append(f'    ad: {_hex(ins.ad)}')
        lines.append(f'    sr: {_hex(ins.sr)}')
        lines.append(f'    pw: {_hex(ins.pw_lo)} {_hex(ins.pw_hi)}')
        lines.append('  }')
    for i, sg in enumerate(e.songs):
        lines.append(f'  song {i} {{')
        lines.append(f'    voice: {sg.voice}')
        lines.append(f'    duration: {sg.duration}')
        lines.append(f'    wavestep: {_hex(sg.wavestep)}')
        lines.append(f'    increment: {_hex(sg.increment)}')
        lines.append(f'    instrument: {sg.instrument}')
        lines.append('  }')
    for i, vi in enumerate(e.voice_init):
        lines.append(f'  voice_init {i} {{')
        lines.append(f'    duration: {vi.duration}')
        lines.append(f'    pitch: {_hex(vi.pitch)}')
        lines.append(f'    increment: {_hex(vi.increment)}')
        lines.append(f'    wavestep: {_hex(vi.wavestep)}')
        lines.append(f'    instrument: {vi.instrument}')
        lines.append('  }')
    lines.append('}')
    return lines


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _write_swenv(kw: str, env) -> str:
    parts = [f'start={_hex(env.start, 4)}']
    if env.loop is not None:
        parts.append(f'repeat={env.loop}')
    for rate, frames in env.phases:
        parts.append(f'seg ({rate}, {_hex(frames, 4)})')
    return f'{kw} {{ ' + ' '.join(parts) + ' }'


def _write_freq_table(bytes_: list[int]) -> list[str]:
    lines = ['freq_table {  ; per-tune tuning table (96-entry musical region + tail)']
    # 16 bytes per line for readability.
    for i in range(0, len(bytes_), 16):
        row = ' '.join(_hex(b) for b in bytes_[i:i + 16])
        lines.append(f'  {row}')
    lines.append('}')
    return lines


def _write_state_layout(d: dict) -> list[str]:
    lines = ['state_layout {  ; which state bytes off-table arp notes sonify']
    if d.get('n_voices') is not None:
        lines.append(f'  n_voices: {d["n_voices"]}')
    for slot in d.get('scalars', []):
        if slot['kind'] == 'const':
            lines.append(
                f'  scalar {slot["offset"]} const {_hex(slot["value"])}')
        else:
            lines.append(
                f'  scalar {slot["offset"]} var {slot["var"]}')
    for slot in d.get('per_voice', []):
        if slot['kind'] == 'const':
            lines.append(
                f'  per_voice {slot["offset"]} const {_hex(slot["value"])}')
        else:
            lines.append(
                f'  per_voice {slot["offset"]} var {slot["var"]}')
    lines.append('}')
    return lines


def _write_sfx(cfg: SfxConfig) -> list[str]:
    """Emit `sfx { ... }`; only non-default fields written. Block
    itself signals SFX presence."""
    parts = []
    if cfg.framectr_ofs != 253:
        parts.append(f'  framectr_ofs: {_hex(cfg.framectr_ofs)}')
    if cfg.state_ofs is not None:
        parts.append(f'  state_ofs: {_hex(cfg.state_ofs)}')
    return ['sfx {  ; tune carries a sound-effect sub-engine', *parts, '}']


def _write_master_vol(cfg: MasterVolConfig) -> list[str]:
    """Emit `master_vol { ... }`; subtrahend_voice always written
    (the field is the trigger for the modulation existing), other
    fields only when non-default."""
    parts = [f'  subtrahend_voice: {cfg.subtrahend_voice}']
    if cfg.base != 0xA0:
        parts.append(f'  base: {_hex(cfg.base)}')
    if cfg.trigger != 'inst_change':
        parts.append(f'  trigger: {cfg.trigger}')
    if cfg.reset_on_loop:
        parts.append('  reset_on_loop: true')
    if cfg.underflow_clamp:
        parts.append('  underflow_clamp: true')
    return ['master_vol {  ; master-volume fade: clamp(base - voice orderlist position)', *parts, '}']


def _write_init_behavior(cfg: InitBehaviorConfig) -> list[str]:
    """Emit `init_behavior { ... }`; only non-default fields written."""
    parts = []
    if cfg.silence_all_voices_on_frame_0:
        parts.append('  silence_all_voices_on_frame_0: true')
    if cfg.no_first_attack_voice:
        parts.append(f'  no_first_attack_voice: {cfg.no_first_attack_voice}')
    if cfg.master_vol_every_frame:
        parts.append(f'  master_vol_every_frame: ${cfg.master_vol_every_frame:02X}')
    if cfg.master_vol_every_note:
        parts.append(f'  master_vol_every_note: ${cfg.master_vol_every_note:02X}')
    # articulation behaviors (C33 typing) — None = canon, elided
    if cfg.gate_off_hold is not None:
        parts.append(f'  gate_off_hold: {cfg.gate_off_hold}')
    if cfg.rest_effects is not None:
        parts.append(f'  rest_effects: {cfg.rest_effects}')
    if cfg.hard_restart is not None:
        parts.append(f'  hard_restart: {cfg.hard_restart}')
    if cfg.cymbal_onset is not None:
        parts.append(f'  cymbal_onset: {cfg.cymbal_onset}')
    if cfg.vibrato_ramp is not None:
        parts.append(f'  vibrato_ramp: {cfg.vibrato_ramp}')
    return ['init_behavior {  ; engine play behavior', *parts, '}']


def _write_song_end(cfg: SongEndConfig) -> list[str]:
    """Emit a `song_end { ... }` block; only fields differing from
    defaults are written so default Hubbard songs don't emit a block."""
    parts = []
    if cfg.stop_marker != 'silence':
        parts.append(f'  stop_marker: {cfg.stop_marker}')
    if cfg.fill_value:
        parts.append(f'  fill_value: {_hex(cfg.fill_value)}')
    if cfg.loop_marker != 'loop':
        parts.append(f'  loop_marker: {cfg.loop_marker}')
    return ['song_end {  ; what the stop/loop markers do at end of orderlist', *parts, '}']


def write(usf: UsfFile) -> str:
    """Serialize a `UsfFile` to canonical `.usf` text."""
    lines: list[str] = []
    lines.extend(_write_psid(usf.psid))
    lines.append('')
    lines.extend(_write_params(usf.params))
    lines.append('')
    lines.extend(_write_init(usf.init))
    if getattr(usf, 'environment', None) is not None:
        lines.append('')
        lines.extend(_write_environment(usf.environment))
    if usf.freq_table is not None:
        lines.append('')
        lines.extend(_write_freq_table(usf.freq_table))
    if getattr(usf, 'offtable_vibdepth', None):
        lines.append('')
        lines.append('offtable_vibdepth {  ; vibrato depths for notes past the table')
        for note, depth in usf.offtable_vibdepth:
            lines.append(f'  at({note}, {depth})')
        lines.append('}')
    if getattr(usf, 'wave_table', None):
        lines.append('')
        lines.append('wave_table {  ; shared position-indexed wave table '
                     '(stated cells only): pos: <ctrl> <freq> | pos: jump n')
        for pos in sorted(usf.wave_table):
            cell = usf.wave_table[pos]
            if cell[0] == 'jump':
                lines.append(f'  {pos}: jump {cell[1]}')
            else:
                lines.append(f'  {pos}: {_hex(cell[1])} {_hex(cell[2])}')
        lines.append('}')
    if usf.state_layout is not None:
        lines.append('')
        lines.extend(_write_state_layout(usf.state_layout))
    if usf.song_end is not None and (
            usf.song_end.stop_marker != 'silence'
            or usf.song_end.fill_value
            or usf.song_end.loop_marker != 'loop'):
        lines.append('')
        lines.extend(_write_song_end(usf.song_end))
    if usf.init_behavior is not None and (
            usf.init_behavior.silence_all_voices_on_frame_0
            or usf.init_behavior.no_first_attack_voice
            or usf.init_behavior.master_vol_every_frame
            or usf.init_behavior.master_vol_every_note
            or usf.init_behavior.gate_off_hold is not None
            or usf.init_behavior.rest_effects is not None
            or usf.init_behavior.hard_restart is not None
            or usf.init_behavior.cymbal_onset is not None
            or usf.init_behavior.vibrato_ramp is not None):
        lines.append('')
        lines.extend(_write_init_behavior(usf.init_behavior))
    if usf.master_vol is not None:
        lines.append('')
        lines.extend(_write_master_vol(usf.master_vol))
    if usf.sfx is not None:
        lines.append('')
        lines.extend(_write_sfx(usf.sfx))
    if getattr(usf, 'dmc_sfx', None) is not None:
        lines.append('')
        lines.extend(_write_dmc_sfx(usf.dmc_sfx))
    for _kw, _env in (('default_filter', getattr(usf, 'default_filter', None)),
                      ('default_pulse', getattr(usf, 'default_pulse', None))):
        if _env is None:
            continue
        lines.append('')
        lines.append(_write_swenv(_kw, _env))
    if usf.arp_programs:
        lines.append('')
        lines.extend(_write_arp_programs(usf.arp_programs))
    if usf.pulse_programs:
        lines.append('')
        lines.extend(_write_pulse_programs(usf.pulse_programs))
    if usf.filter_programs:
        lines.append('')
        lines.extend(_write_filter_programs(usf.filter_programs))
    if usf.filter_mod:
        lines.append('')
        lines.extend(_write_filter_mod(usf.filter_mod))
    if usf.drum_programs:
        lines.append('')
        lines.extend(_write_drum_programs(usf.drum_programs))
    if usf.wave_programs:
        lines.append('')
        lines.extend(_write_wave_programs(usf.wave_programs))
    for name, vals in (('attack_len', usf.attack_len),
                       ('attack_wave', usf.attack_wave),
                       ('wave_arp', usf.wave_arp),
                       ('pulse_arp', usf.pulse_arp)):
        if vals:
            lines.append(f'{name} = [{", ".join(str(v) for v in vals)}]')
    for inst in sorted(usf.instruments, key=lambda x: x.id):
        lines.append('')
        lines.extend(_write_instrument(inst))
    for sub in sorted(usf.subtunes, key=lambda x: x.id):
        lines.append('')
        lines.extend(_write_subtune(sub))
    return '\n'.join(lines) + '\n'


def write_file(usf: UsfFile, path: str) -> None:
    """Serialize a `UsfFile` to a file (UTF-8, LF line endings)."""
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(write(usf))
