"""Composer — EngineModel → 6502 asm → PSID bytes.

The composer is the asm-codegen layer of the rewrite. It reads an
`EngineModel` (from `pipelines.engine_model`) and emits asm whose
per-frame SID instruction stream matches what the original engine
would produce.

**Principle: feature-by-feature emission, no shape selection.** The
composer inspects each feature on the model and calls the
corresponding emitter. A USF that uses N features gets asm that
implements those N features composed. Adding a new engine = adding
features the composer doesn't yet emit, not adding a shape branch.

Status: Phase 3 — initial scope is the feature set henrys_house uses
(1 active voice, atomic-per-tick encoding, every-tick voice timing,
single-phase tempo, no modulation, fixed-init master vol, single
subtune, $FF=master_vol_reset_and_loop terminator). Future phases
widen the supported feature set engine-family by engine-family.

`can_handle(model)` returns True iff every feature on the model has
an emitter in the composer. USFs with unsupported features fall
through to the legacy shape dispatch in `pipelines/universal_codegen.py`
during the transition.
"""

from __future__ import annotations

import os
import struct
import subprocess

from pipelines.engine_model import (
    EngineModel, PatternConfig, VoiceTiming, TempoDispatch,
    TerminatorVocab, MasterVolConfig, SubtuneSpec, VoiceConfig,
    InstrumentProgram,
)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_XA = os.path.join(_ROOT, 'tools', 'xa65', 'xa', 'xa')
LOAD = 0x1000

_SEMI = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
         'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


# ---------------------------------------------------------------------------
# Feature support check
# ---------------------------------------------------------------------------

# Phase 3 — minimum feature set. As phases land, this widens.
_SUPPORTED_PATTERN_ENCODINGS = {'atomic_per_tick'}
_SUPPORTED_PITCH_FORMATS = {'octave_semi_nibble'}
_SUPPORTED_VOICE_TIMING = {'every_tick'}
_SUPPORTED_TEMPO_DISPATCH = {'single_phase'}
_SUPPORTED_MASTER_VOL = {'fixed_init'}

_SUPPORTED_TERMINATORS = {
    'note', 'rest_gate_off', 'skip', 'master_vol_reset_and_loop',
}


def can_handle(model: EngineModel) -> bool:
    """Does the composer have emitters for every feature in this model?

    Reads each dimension on the model and checks against the supported
    sets. Returns False if any feature is unsupported. USFs that fail
    this check fall through to the legacy shape dispatch.
    """
    if model.pattern.encoding not in _SUPPORTED_PATTERN_ENCODINGS:
        return False
    if model.pattern.pitch_byte_format not in _SUPPORTED_PITCH_FORMATS:
        return False
    if model.voice_timing.mode not in _SUPPORTED_VOICE_TIMING:
        return False
    if model.tempo_dispatch.mode not in _SUPPORTED_TEMPO_DISPATCH:
        return False
    if model.master_vol.mode not in _SUPPORTED_MASTER_VOL:
        return False

    # Optional features: composer doesn't emit any of these yet.
    if model.commands is not None: return False
    if model.inter_voice_quirks: return False
    if model.state_layout is not None: return False
    if model.sfx is not None: return False
    if model.digi is not None: return False
    if model.hardcoded_pw_sweep is not None: return False
    if model.compound is not None: return False

    # Modulation programs — none supported yet
    for inst in model.instruments:
        if (inst.vibrato or inst.pwm_linear or inst.pwm_bidirectional
                or inst.arpeggio or inst.freq_hi_slide
                or inst.odd_frame_slide or inst.per_note_portamento):
            return False

    # Terminator bytes — all entries must map to behaviors we emit
    for byte, behavior in model.terminators.byte_map.items():
        if behavior not in _SUPPORTED_TERMINATORS:
            # Edge: for bowden the $81-$FE skip range maps to 'skip'
            # which IS supported — but bowden also has $FF=loop_substitute_first
            # which isn't, so the overall check still fails.
            return False

    # Voice count — composer supports 1 active voice in Phase 3.
    # Active = any voice with a non-empty pattern in any subtune.
    active = _active_voice_indices(model)
    if len(active) != 1:
        return False

    # Multi-subtune — Phase 3 supports a single subtune. (The legacy
    # 1-voice emitter supports multi via byte tables; we'll add that
    # in a later phase when a multi-subtune 1-voice tune appears.)
    if len(model.subtunes) != 1:
        return False

    return True


# ---------------------------------------------------------------------------
# Active voices
# ---------------------------------------------------------------------------

def _active_voice_indices(model: EngineModel) -> list[int]:
    """0-indexed list of voices that have a non-empty pattern in any
    subtune. Used to size the per-voice runtime state."""
    active = set()
    for sub in model.subtunes:
        for v_idx, pat_bytes in enumerate(sub.voice_patterns):
            if pat_bytes:
                active.add(v_idx)
    # Fallback: read from the model's voice count if voice_patterns
    # hasn't been populated yet (Phase 2 builder leaves it empty).
    if not active and model.voices.count > 0:
        active.add(0)
    return sorted(active)


# ---------------------------------------------------------------------------
# Pattern row encoder — single-voice atomic-per-tick
# ---------------------------------------------------------------------------

def _row_to_byte(row, byte_map: dict[int, str]) -> bytes:
    """One pattern row → one head byte + (duration-1) skip bytes.

    The skip byte value is whichever byte maps to 'skip' in the
    terminator vocab (typically $81). Rest rows emit the byte mapped
    to 'rest_gate_off' (typically $80).
    """
    skip_byte = next(
        (b for b, beh in byte_map.items() if beh == 'skip'), 0x81)
    rest_byte = next(
        (b for b, beh in byte_map.items() if beh == 'rest_gate_off'), 0x80)
    if row.pitch.is_rest:
        head = rest_byte
    else:
        head = (row.pitch.octave << 4) | _SEMI[row.pitch.name]
    return bytes([head]) + bytes([skip_byte] * (row.duration - 1))


def _voice_pattern_bytes(voice_block, byte_map: dict[int, str]) -> bytes:
    """Encode one voice's pattern rows + the $FF loop terminator."""
    if not voice_block.patterns:
        return bytes()
    pat = voice_block.patterns[0]
    body = b''.join(_row_to_byte(r, byte_map) for r in pat.rows)
    # Append the byte that maps to the loop terminator behavior.
    loop_byte = next(
        (b for b, beh in byte_map.items()
         if beh in ('master_vol_reset_and_loop',
                    'loop_reset', 'loop_substitute_first')),
        0xFF)
    return body + bytes([loop_byte])


# ---------------------------------------------------------------------------
# Asm emitters — each emits a fragment for one feature
# ---------------------------------------------------------------------------

def _emit_header() -> list[str]:
    return [f'* = ${LOAD:04X}', '  jmp init', '  jmp play']


def _emit_init_silence_sid() -> list[str]:
    """Standard init — write 0 to $D400-$D418."""
    return [
        '  lda #0',
        '  ldx #0',
        'init_silence:',
        '  sta $d400,x',
        '  inx',
        '  cpx #$19',
        '  bne init_silence',
    ]


def _emit_init_master_vol(mv: MasterVolConfig) -> list[str]:
    return [
        f'  lda #${mv.init_value:02X}',
        '  sta $d418',
    ]


def _emit_init_pos_and_tempo(sub: SubtuneSpec) -> list[str]:
    """Per-voice init position + tempo counter + tempo const."""
    L = []
    if sub.voice_init:
        L.append(f'  lda #${sub.voice_init[0].initial_position:02X}')
        L.append('  sta v_pos')
    else:
        L.append('  lda #0')
        L.append('  sta v_pos')
    L.append(f'  lda #${sub.init_tempo_ctr:02X}')
    L.append('  sta tempo_ctr')
    L.append(f'  lda #${sub.tempo:02X}')
    L.append('  sta tempo_const')
    return L


def _emit_init_timbre_inline(inst: InstrumentProgram) -> list[str]:
    """For the single-voice no-modulation case, the instrument's 5-byte
    timbre is loaded into RAM slots once at init (no per-frame writes)."""
    return [
        f'  lda #${inst.init_pw_lo:02X}',
        '  sta t_pwlo',
        f'  lda #${inst.init_pw_hi:02X}',
        '  sta t_pwhi',
        f'  lda #${inst.init_ctrl:02X}',
        '  sta t_ctrl',
        f'  lda #${inst.init_ad:02X}',
        '  sta t_ad',
        f'  lda #${inst.init_sr:02X}',
        '  sta t_sr',
    ]


def _emit_play_tempo_gate_single() -> list[str]:
    """`inc tempo_ctr; cmp tempo_const; on hit reset + dispatch`."""
    return [
        'play:',
        '  inc tempo_ctr',
        '  lda tempo_ctr',
        '  cmp tempo_const',
        '  beq play_tick',
        '  rts',
        'play_tick:',
        '  lda #0',
        '  sta tempo_ctr',
    ]


def _emit_play_voice_dispatch_1voice() -> list[str]:
    """Single-voice every-tick read: X = v_pos; inc; read orderlist byte."""
    return [
        '  ldx v_pos',
        '  inc v_pos',
        '  lda orderlist_v1,x',
    ]


def _emit_byte_dispatch_1voice(terms: TerminatorVocab,
                                mv: MasterVolConfig) -> list[str]:
    """Decode the byte just read into a behavior.

    The current implementation hard-codes the byte values for the
    supported terminator set ($80 rest, $81 skip, $FF
    master_vol_reset_and_loop) — Phase 3 minimum. Generalizing to
    arbitrary byte mappings is a Phase 4+ enhancement when other
    shapes land.
    """
    return [
        '  cmp #$ff',
        '  bne not_ff',
        # master_vol_reset_and_loop
        f'  lda #${mv.init_value:02X}',
        '  sta $d418',
        '  lda #0',
        '  sta v_pos',
        '  rts',
        'not_ff:',
        '  cmp #$80',
        '  beq pn_rest',
        '  bcs pn_skip',
        # Normal note: pitch byte = (octave<<4)|semi; freq lookup.
        '  tay',
        '  lda freq_hi_tab,y',
        '  sta $d401',
        '  lda freq_lo_tab,y',
        '  sta $d400',
        '  lda t_pwlo',
        '  sta $d402',
        '  lda t_pwhi',
        '  sta $d403',
        '  lda t_ctrl',
        '  sta $d404',
        '  lda t_ad',
        '  sta $d405',
        '  lda t_sr',
        '  sta $d406',
        '  lda t_ctrl',
        '  ora #$01',
        '  sta $d404',
        '  rts',
        'pn_rest:',
        '  lda t_ctrl',
        '  sta $d404',
        '  rts',
        'pn_skip:',
        '  rts',
    ]


def _emit_runtime_vars_1voice() -> list[str]:
    return [
        'v_pos:       .byte 0',
        'tempo_ctr:   .byte 0',
        'tempo_const: .byte 0',
        't_pwlo:      .byte 0',
        't_pwhi:      .byte 0',
        't_ctrl:      .byte 0',
        't_ad:        .byte 0',
        't_sr:        .byte 0',
    ]


def _emit_freq_table(freq_table: bytes) -> list[str]:
    fh = freq_table[:128]
    fl = freq_table[128:256]
    lines = ['freq_hi_tab:']
    for i in range(0, len(fh), 16):
        lines.append('  .byte ' + ', '.join(
            f'${b:02X}' for b in fh[i:i+16]))
    lines.append('freq_lo_tab:')
    for i in range(0, len(fl), 16):
        lines.append('  .byte ' + ', '.join(
            f'${b:02X}' for b in fl[i:i+16]))
    return lines


def _emit_orderlist_1voice(pat_bytes: bytes) -> list[str]:
    L = ['orderlist_v1:']
    for i in range(0, len(pat_bytes), 16):
        L.append('  .byte ' + ', '.join(
            f'${b:02X}' for b in pat_bytes[i:i+16]))
    return L


# ---------------------------------------------------------------------------
# Top-level compose
# ---------------------------------------------------------------------------

def emit_asm(model: EngineModel, voice_patterns_override: list[bytes] | None = None) -> str:
    """Compose the asm source for the given model.

    `voice_patterns_override` lets the caller pass pre-encoded pattern
    bytes (the Phase 2 builder doesn't populate `SubtuneSpec.voice_patterns`
    yet, so the caller encodes them via the model's pattern config).
    """
    if not can_handle(model):
        raise NotImplementedError(
            'composer does not yet support every feature in this model. '
            'See `can_handle()` for the supported set.')

    sub = model.subtunes[0]
    inst = model.instruments[0]

    L: list[str] = []
    L += _emit_header()

    # Init
    L.append('init:')
    L += _emit_init_silence_sid()
    L += _emit_init_master_vol(model.master_vol)
    L += _emit_init_pos_and_tempo(sub)
    L += _emit_init_timbre_inline(inst)
    L.append('  rts')

    # Play
    L += _emit_play_tempo_gate_single()
    L += _emit_play_voice_dispatch_1voice()
    L += _emit_byte_dispatch_1voice(model.terminators, model.master_vol)

    # Runtime + data
    L += _emit_runtime_vars_1voice()
    L += _emit_freq_table(model.freq_table)
    pat_bytes = (voice_patterns_override[0]
                 if voice_patterns_override else
                 sub.voice_patterns[0])
    L += _emit_orderlist_1voice(pat_bytes)

    return '\n'.join(L) + '\n'


def _assemble(asm_src: str, tmp_basename: str = 'composer') -> bytes:
    src = f'/tmp/{tmp_basename}.s'
    obj = f'/tmp/{tmp_basename}.bin'
    with open(src, 'w') as f:
        f.write(asm_src)
    r = subprocess.run([_XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    return open(obj, 'rb').read()


def _psid_header(model: EngineModel, n_subtunes: int, load: int) -> bytes:
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', load)
    h += struct.pack('>H', load)
    h += struct.pack('>H', load + 3)
    h += struct.pack('>H', n_subtunes)
    h += struct.pack('>H', model.psid.start_song)
    h += struct.pack('>I', model.psid.psid_speed)
    def _latin1(s: str, n: int) -> bytes:
        return s.encode('latin-1', errors='replace')[:n].ljust(n, b'\x00')
    h += _latin1(model.psid.title, 32)
    h += _latin1(model.psid.author, 32)
    h += _latin1(model.psid.released, 32)
    clock_bits = {'unknown': 0, 'PAL': 1, 'NTSC': 2, 'both': 3}.get(
        model.psid.clock, 0)
    sid_bits = {6581: 1, 8580: 2}.get(model.psid.sid_model, 1)
    h += struct.pack('>H', (clock_bits << 2) | (sid_bits << 4))
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124
    return bytes(h)


def emit_sid_from_model(model: EngineModel,
                         voice_patterns_override: list[bytes] | None = None
                         ) -> bytes:
    """Compose an EngineModel into a complete PSID byte string."""
    asm = emit_asm(model, voice_patterns_override=voice_patterns_override)
    body = _assemble(asm)
    return _psid_header(model, n_subtunes=len(model.subtunes), load=LOAD) + body


# ---------------------------------------------------------------------------
# Entry from a USF (for build_from_usf to dispatch into)
# ---------------------------------------------------------------------------

def emit_sid_from_usf(usf) -> bytes:
    """Build SID bytes from a USF via the composer path.

    Reads the model, encodes pattern bytes (since the Phase 2 builder
    leaves `voice_patterns` empty), and runs the composer. Raises if
    the model has features the composer doesn't yet handle.
    """
    from pipelines.engine_model import from_usf
    model = from_usf(usf)
    if not can_handle(model):
        raise NotImplementedError(
            'composer cannot handle this USF yet — fall through to legacy')

    # Encode pattern bytes from the USF's MusicSubtune rows. The model's
    # voice_patterns field is empty in Phase 2; we encode on demand here
    # using the model's terminator vocab.
    from src.usf import MusicSubtune
    music = sorted(
        (s for s in usf.subtunes if isinstance(s, MusicSubtune)),
        key=lambda s: s.id)
    ms = music[0]

    # Active voice (there's exactly one — can_handle ensures this).
    active_voice = next(v for v in ms.voices if v.patterns)
    pat_bytes = _voice_pattern_bytes(active_voice, model.terminators.byte_map)

    return emit_sid_from_model(model, voice_patterns_override=[pat_bytes])
