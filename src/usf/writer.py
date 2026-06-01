"""USF v2 — writer.

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
    MusicSubtune, DigiSubtune, SfxSubtune,
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

def _write_psid(p: PsidMeta) -> list[str]:
    lines = [
        'psid {',
        f'  title:      "{p.title}"',
        f'  author:     "{p.author}"',
        f'  released:   "{p.released}"',
        f'  clock:      {p.clock}',
        f'  sid:        {p.sid}',
        f'  start_song: {p.start_song}',
    ]
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
    parts = []
    if v.ctrl is not None:
        parts.append(f'ctrl: {_hex(v.ctrl)}')
    parts.append(f'dur_field: {_hex(v.dur_field)}')
    parts.append(f'pwm_period: {_hex(v.pwm_period)}')
    parts.append(f'pwm_dir: {v.pwm_dir}')
    if v.instr is not None:
        parts.append(f'instr: {_format_instr_ref(v.instr)}')
    parts.append(f'slide_v: {_hex(v.slide_v)}')
    return f'  voice {v.id} {{ ' + '  '.join(parts) + ' }'


def _write_init_sid_voice(v: InitSidVoice) -> str:
    parts = []
    if v.envelope_prime is not None:
        ad, sr = v.envelope_prime
        parts.append(f'envelope_prime: ({_hex(ad)}, {_hex(sr)})')
    if v.pw_init is not None:
        parts.append(f'pw_init: {_hex(v.pw_init, 4)}')
    return f'    voice {v.id} {{ ' + '  '.join(parts) + ' }'


def _write_init_sid(sid: InitSid) -> list[str]:
    lines = ['  sid {']
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
        lines.append('    filter { ' + '  '.join(parts) + ' }')
    for v in sorted(sid.voices, key=lambda x: x.id):
        lines.append(_write_init_sid_voice(v))
    lines.append('  }')
    return lines


def _write_init(state: InitState) -> list[str]:
    lines = ['init {']
    if state.sid is not None:
        lines.extend(_write_init_sid(state.sid))
    for v in sorted(state.voices, key=lambda x: x.id):
        lines.append(_write_init_voice(v))
    lines.append('}')
    return lines


def _write_pwm(p: PwmConfig) -> str:
    parts = [f'mode={p.mode}', f'speed={p.speed}',
             f'init={_hex(p.init, 4)}',
             f'min_hi={p.min_hi}', f'max_hi={p.max_hi}']
    # Emit phase1_* only when any of them is non-default (keeps Hubbard
    # USFs visually unchanged on round-trip).
    if p.phase1_dir != 'up' or p.phase1_bound != 0 or p.phase1_step != 0:
        parts.append(f'phase1_dir={p.phase1_dir}')
        parts.append(f'phase1_bound={_hex(p.phase1_bound)}')
        parts.append(f'phase1_step={_hex(p.phase1_step)}')
    if p.lo_or_mask:
        parts.append(f'lo_or_mask={_hex(p.lo_or_mask)}')
    return 'pwm:      ' + ' '.join(parts)


def _write_arp(a: ArpConfig) -> str:
    offs = ', '.join(str(o) for o in a.offsets)
    parts = [f'offsets=[{offs}]', f'period={a.period}']
    # Emit interval / phase_invert only when non-default — keeps
    # existing USFs unchanged on round-trip.
    if a.interval != 12:
        parts.append(f'interval={a.interval}')
    if a.phase_invert:
        parts.append('phase_invert=true')
    return 'arp:      ' + ' '.join(parts)


def _write_vibrato(v: VibratoConfig) -> str:
    parts = [f'scale={v.scale}']
    if v.onset != 6:
        parts.append(f'onset={v.onset}')
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


def _write_instrument(i: Instrument) -> list[str]:
    head = f'instrument {i.id}'
    if i.name:
        head += f' {i.name}'
    lines = [head + ' {']
    if i.waveform:
        wave = ' '.join(_hex(b) for b in i.waveform)
        lines.append(f'  waveform: {wave}')
        lines.append(f'  loop:     {i.loop}')
    lines.append(f'  {_write_pwm(i.pwm)}')
    lines.append(f'  adsr:     {_hex(i.adsr[0])} {_hex(i.adsr[1])}')
    lines.append(f'  {_write_arp(i.arp)}')
    lines.append(f'  {_write_vibrato(i.vibrato)}')
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
    lines.append('}')
    return lines


def _write_orderlist(o: Orderlist) -> str:
    parts = [str(e) for e in o.entries]
    if o.loop_to is not None:
        parts.append(f'loop@{o.loop_to}')
    elif o.stop:
        parts.append('stop')
    return ' '.join(parts)


def _write_pattern(p: Pattern) -> list[str]:
    lines = [f'    pattern {p.id} length={p.length} {{']
    # Column-align pitch / duration / instrument / flags.
    for row in p.rows:
        pitch = _format_pitch(row.pitch)
        dur = str(row.duration)
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
    lines.append(f'    orderlist: {_write_orderlist(v.orderlist)}')
    for p in sorted(v.patterns, key=lambda x: x.id):
        lines.extend(_write_pattern(p))
    lines.append('  }')
    return lines


def _write_subtune(s) -> list[str]:
    if isinstance(s, MusicSubtune):
        lines = [f'subtune {s.id} music {{']
        lines.append(f'  tempo: {s.tempo}')
        if s.params is not None and s.params.fields:
            # Indent the per-subtune params block under the subtune.
            for line in _write_params(s.params):
                lines.append('  ' + line)
        if s.init is not None:
            # Indent the per-subtune init block under the subtune.
            for line in _write_init(s.init):
                lines.append('  ' + line)
        for v in s.voices:
            lines.extend(_write_voice(v))
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
        lines.append('}')
        return lines
    raise TypeError(f'unknown subtune type: {type(s).__name__}')


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _write_freq_table(bytes_: list[int]) -> list[str]:
    lines = ['freq_table {']
    # 16 bytes per line for readability.
    for i in range(0, len(bytes_), 16):
        row = ' '.join(_hex(b) for b in bytes_[i:i + 16])
        lines.append(f'  {row}')
    lines.append('}')
    return lines


def _write_state_layout(d: dict) -> list[str]:
    lines = ['state_layout {']
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


def _write_init_behavior(cfg: InitBehaviorConfig) -> list[str]:
    """Emit `init_behavior { ... }`; only non-default fields written."""
    parts = []
    if cfg.silence_all_voices_on_frame_0:
        parts.append('  silence_all_voices_on_frame_0: true')
    if cfg.no_first_attack_voice:
        parts.append(f'  no_first_attack_voice: {cfg.no_first_attack_voice}')
    return ['init_behavior {', *parts, '}']


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
    return ['song_end {', *parts, '}']


def write(usf: UsfFile) -> str:
    """Serialize a `UsfFile` to canonical `.usf` text."""
    lines: list[str] = []
    lines.extend(_write_psid(usf.psid))
    lines.append('')
    lines.extend(_write_params(usf.params))
    lines.append('')
    lines.extend(_write_init(usf.init))
    if usf.freq_table is not None:
        lines.append('')
        lines.extend(_write_freq_table(usf.freq_table))
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
            or usf.init_behavior.no_first_attack_voice):
        lines.append('')
        lines.extend(_write_init_behavior(usf.init_behavior))
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
