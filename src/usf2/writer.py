"""USF v2 — writer.

Serialize a `UsfFile` model to `.usf` text. The output is deterministic
and round-trip stable: `parse(write(model))` returns an equivalent
model, and `write(parse(text))` is byte-identical to canonicalised text.
"""

from __future__ import annotations

from src.usf2.types import (
    UsfFile, PsidMeta, Params, InitVoice, InitState,
    Instrument, PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig,
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
    return [
        'psid {',
        f'  title:      "{p.title}"',
        f'  author:     "{p.author}"',
        f'  released:   "{p.released}"',
        f'  clock:      {p.clock}',
        f'  sid:        {p.sid}',
        f'  start_song: {p.start_song}',
        '}',
    ]


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


def _write_init(state: InitState) -> list[str]:
    lines = ['init {']
    for v in sorted(state.voices, key=lambda x: x.id):
        lines.append(_write_init_voice(v))
    lines.append('}')
    return lines


def _write_pwm(p: PwmConfig) -> str:
    return (f'pwm:      mode={p.mode} speed={p.speed} '
            f'init={_hex(p.init, 4)} min_hi={p.min_hi} max_hi={p.max_hi}')


def _write_arp(a: ArpConfig) -> str:
    offs = ', '.join(str(o) for o in a.offsets)
    return f'arp:      offsets=[{offs}] period={a.period}'


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
    lines.append(f'  vibrato:  scale={i.vibrato.scale}')
    lines.append(
        f'  envelope: gate_off_delta={i.envelope.gate_off_delta} '
        f'adsr_zero_delta={i.envelope.adsr_zero_delta}')
    fx_flags = []
    if i.freq_slide:
        fx_flags.append('freq_slide')
    if i.inc_by2:
        fx_flags.append('inc_by2')
    if fx_flags:
        lines.append(f'  fx:       {" ".join(fx_flags)}')
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
        for v in s.voices:
            lines.extend(_write_voice(v))
        lines.append('}')
        return lines
    if isinstance(s, DigiSubtune):
        return [f'subtune {s.id} digi {{', f'  sample: {s.sample}', '}']
    if isinstance(s, SfxSubtune):
        # SFX schema TBD; emit empty body for now.
        return [f'subtune {s.id} sfx {{', '}']
    raise TypeError(f'unknown subtune type: {type(s).__name__}')


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def write(usf: UsfFile) -> str:
    """Serialize a `UsfFile` to canonical `.usf` text."""
    lines: list[str] = []
    lines.append(f'version: {usf.version}')
    lines.append(f'engine: {usf.engine}')
    lines.append('')
    lines.extend(_write_psid(usf.psid))
    lines.append('')
    lines.extend(_write_params(usf.params))
    lines.append('')
    lines.extend(_write_init(usf.init))
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
