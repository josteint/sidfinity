"""Composer — EngineModel → 6502 asm → PSID bytes.

The composer is the asm-codegen layer of the rewrite. It reads an
`EngineModel` (from `pipelines.engine_model`) and emits asm whose
per-frame SID instruction stream matches what the original engine
would produce.

Architecture
------------
**One codegen path, parametric on features.** Voice count is just a
number — the play loop iterates over the active voices (voices with
non-empty patterns). There is no "1-voice vs 3-voice" branch; if a
voice has a pattern, it gets a `voice_step` routine and a `jsr` in
the play body. If it doesn't, it gets nothing.

Each feature on the model triggers asm conditionally:
* `inter_voice_quirks` containing `carry_leak_4_vs_5_byte_timbre`
  adds the `this_skip_sr` / `next_skip_sr` runtime vars + the
  4-vs-5-byte timbre branch in `proc_note` + the classify logic in
  each `voice_step`.
* `terminators.byte_map[0xFF]` selects what the `$FF` byte does
  (`master_vol_reset_and_loop` vs `loop_substitute_first` vs
  `loop_reset`).
* etc.

Status: Phase 4. Supported feature set widens engine-family by
engine-family. `can_handle(model)` returns True iff every feature
the model carries has an emitter in the composer; USFs with
unsupported features fall through to the legacy shape dispatch in
`pipelines/universal_codegen.py`.
"""

from __future__ import annotations

import os
import struct
import subprocess

from pipelines.engine_model import (
    EngineModel, MasterVolConfig, SubtuneSpec, InstrumentProgram,
    InterVoiceQuirk,
)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_XA = os.path.join(_ROOT, 'tools', 'xa65', 'xa', 'xa')
LOAD = 0x1000

_SEMI = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
         'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

# X-indexed voice offsets — the SID's per-voice register stride is 7,
# so V1=0, V2=7, V3=14. This is engine mechanism the SID hardware
# defines, not engine identity.
_VOICE_OFFSET = {0: 0, 1: 7, 2: 14}

# zp slot allocation for per-voice orderlist pointers (indirect (zp),Y reads).
_ZP_OL_BASE = 0xE0   # V1: $E0/$E1, V2: $E2/$E3, V3: $E4/$E5


# ---------------------------------------------------------------------------
# Feature support check
# ---------------------------------------------------------------------------

_SUPPORTED_PATTERN_ENCODINGS = {
    'atomic_per_tick', 'note_dur_pair', 'atomic_per_period',
}
_SUPPORTED_PITCH_FORMATS = {'octave_semi_nibble'}
_SUPPORTED_VOICE_TIMING = {
    'every_tick', 'tick_counter_decrement', 'dur_counter_decrement',
}
_SUPPORTED_TEMPO_DISPATCH = {'single_phase', 'two_phase'}
_SUPPORTED_MASTER_VOL = {'fixed_init', 'per_subtune_init', 'mutable_commands'}

_SUPPORTED_TERMINATORS = {
    'note', 'rest_gate_off', 'skip',
    'master_vol_reset_and_loop',
    'loop_substitute_first',
    'loop_reset',
    'song_end_voice',
    'set_duration_next_byte',
    'early_release_flag',
    'end_song_on_voice_n',
}

_SUPPORTED_INTER_VOICE_QUIRKS = {
    'carry_leak_4_vs_5_byte_timbre',
}

_SUPPORTED_EMBEDDED_COMMANDS = {
    'set_tempo', 'set_master_vol', 'set_instrument', 'pattern_jump',
    'skip_byte_recurse',
}


def _needs_hubbard85_path(usf, model: EngineModel) -> bool:
    """Return True iff the USF carries features the simpler composer
    emitters can't produce — currently routed through the lifted
    Hubbard '85 parametric core in `universal_codegen.py`.

    Content signals (each independent — composer reads which features
    the music uses, not which engine produced it):
      * any instrument has a per-frame modulation program (vibrato,
        PWM modes, multi-step arpeggio, freq-hi slide, odd-frame slide,
        per-note portamento)
      * any voice references multiple patterns through its orderlist
        (composer's simpler shapes only handle a single pattern per
        voice)
      * the USF carries SFX or digi subtunes
      * the USF carries a `state_layout` block (off-table arpeggio
        state mirror)

    A USF that doesn't trip any of these uses the composer's
    feature-emitter chain directly.
    """
    # Per-instrument modulation programs
    for inst in model.instruments:
        if (inst.vibrato or inst.pwm_linear or inst.pwm_bidirectional
                or inst.arpeggio or inst.freq_hi_slide
                or inst.odd_frame_slide or inst.per_note_portamento):
            return True
    # Multi-pattern orderlists
    from src.usf import MusicSubtune
    for s in usf.subtunes:
        if not isinstance(s, MusicSubtune):
            continue
        for v in s.voices:
            entries = v.orderlist.entries
            if len(entries) > 1 or any(e != 1 for e in entries):
                return True
            for p in v.patterns:
                if p.id != 1:
                    return True
    # SFX / digi / state_layout — model carries them as Optional features
    if model.sfx is not None:
        return True
    if model.digi is not None:
        return True
    if model.state_layout is not None:
        return True
    return False


def can_handle(model: EngineModel) -> bool:
    """Does the composer have emitters for every feature in this model?"""
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

    # Optional features the composer doesn't emit yet
    if model.commands is not None:
        for cmd in model.commands.nibble_map.values():
            if cmd not in _SUPPORTED_EMBEDDED_COMMANDS:
                return False
    if model.state_layout is not None: return False
    if model.sfx is not None: return False
    if model.digi is not None: return False
    if model.compound is not None: return False
    # `hardcoded_pw_sweep` is supported only in the two-phase tempo
    # (companion) path; reject when combined with other tempo dispatch.
    if model.hardcoded_pw_sweep is not None:
        if model.tempo_dispatch.mode != 'two_phase':
            return False

    for inst in model.instruments:
        if (inst.vibrato or inst.pwm_linear or inst.pwm_bidirectional
                or inst.arpeggio or inst.freq_hi_slide
                or inst.odd_frame_slide or inst.per_note_portamento):
            return False

    for quirk in model.inter_voice_quirks:
        if quirk.name not in _SUPPORTED_INTER_VOICE_QUIRKS:
            return False

    for byte, behavior in model.terminators.byte_map.items():
        if behavior not in _SUPPORTED_TERMINATORS:
            return False

    return True


# ---------------------------------------------------------------------------
# Active voices — voices the orderlist actually uses
# ---------------------------------------------------------------------------

def _active_voice_indices(model: EngineModel, usf=None) -> list[int]:
    """0-indexed list of voices that have a non-empty pattern in any
    subtune. The play loop iterates over these; no fixed voice count.

    If `usf` is provided, also looks at the USF directly (the Phase 2
    builder doesn't fill in `voice_patterns` on the model).
    """
    active = set()
    for sub in model.subtunes:
        for v_idx, pat_bytes in enumerate(sub.voice_patterns):
            if pat_bytes:
                active.add(v_idx)
    if usf is not None and not active:
        from src.usf import MusicSubtune
        for s in usf.subtunes:
            if not isinstance(s, MusicSubtune):
                continue
            for v in s.voices:
                if v.patterns:
                    active.add(v.id - 1)
    return sorted(active)


def _has_carry_leak(model: EngineModel) -> bool:
    return any(q.name == 'carry_leak_4_vs_5_byte_timbre'
               for q in model.inter_voice_quirks)


# ---------------------------------------------------------------------------
# Pattern row encoder
# ---------------------------------------------------------------------------

def _skip_byte(byte_map: dict[int, str]) -> int:
    return next((b for b, beh in byte_map.items() if beh == 'skip'), 0x81)


def _rest_byte(byte_map: dict[int, str]) -> int:
    return next((b for b, beh in byte_map.items() if beh == 'rest_gate_off'),
                0x80)


def _loop_byte(byte_map: dict[int, str]) -> int:
    return next(
        (b for b, beh in byte_map.items()
         if beh in ('master_vol_reset_and_loop', 'loop_reset',
                    'loop_substitute_first')),
        0xFF)


def _row_to_byte(row, byte_map: dict[int, str]) -> bytes:
    skip = _skip_byte(byte_map)
    rest = _rest_byte(byte_map)
    # `fx:hold` rows mean "sustain the prior note" — emit a single skip
    # byte (no SID writes). Rest rows emit the rest_gate_off byte.
    if 'fx:hold' in row.fx_flags:
        return bytes([skip])
    if row.pitch.is_rest:
        head = rest
    else:
        head = (row.pitch.octave << 4) | _SEMI[row.pitch.name]
    return bytes([head]) + bytes([skip] * (row.duration - 1))


def _voice_pattern_bytes(voice_block, byte_map: dict[int, str]) -> bytes:
    if not voice_block.patterns:
        return bytes([_loop_byte(byte_map)])
    pat = voice_block.patterns[0]
    body = b''.join(_row_to_byte(r, byte_map) for r in pat.rows)
    return body + bytes([_loop_byte(byte_map)])


# ---------------------------------------------------------------------------
# Pair-shape encoders — note + duration byte pairs
# ---------------------------------------------------------------------------

def _pair_row_bytes(row) -> bytes:
    """One pattern row → (note, duration) 2-byte pair.

    `fx:raw_NN` flag carries a verbatim byte (yes_tune SoF SFX subtunes
    use this for muted-pitch percussion triggers). Otherwise: note byte
    is (octave<<4)|semi for pitched, $80 for rest.
    """
    for f in row.fx_flags:
        if f.startswith('fx:raw_'):
            return bytes([int(f.split('_')[1], 16), row.duration & 0xFF])
    if row.pitch.is_rest:
        return bytes([0x80, row.duration & 0xFF])
    note = (row.pitch.octave << 4) | _SEMI[row.pitch.name]
    return bytes([note, row.duration & 0xFF])


def _pair_voice_bytes_and_state(voice_block) -> tuple[bytes, int]:
    """Encode one voice's pattern as pair-shape bytes + init state byte.

    State byte values: 0 = silent voice (engine skips it forever),
    2 = load-pattern (init→state=1 on first tick→play normally).

      orderlist `entries=[]` + stop      → state=0, sentinel $81 byte
      orderlist `entries=[1]` + stop=True → state=2, body + $81 (stop)
      orderlist `entries=[1]` + loop_to=0 → state=2, body + $FF (loop)
    """
    ol = voice_block.orderlist
    if not ol.entries:
        return bytes([0x81]), 0x00
    if len(ol.entries) != 1 or ol.entries[0] != 1:
        raise NotImplementedError(
            f'pair-shape voice supports a single-pattern orderlist ([1]); '
            f'got {ol.entries}')
    pat = voice_block.patterns[0]
    body = b''.join(_pair_row_bytes(r) for r in pat.rows)
    if ol.stop:
        return body + bytes([0x81]), 0x02
    if ol.loop_to is not None:
        return body + bytes([0xFF]), 0x02
    raise NotImplementedError(
        f'pair-shape voice orderlist must terminate with stop or loop@N')


# ---------------------------------------------------------------------------
# Asm emitters — each composable from features on the model
# ---------------------------------------------------------------------------

def _emit_header() -> list[str]:
    return [f'* = ${LOAD:04X}', '  jmp init', '  jmp play']


def _emit_init(model: EngineModel, active: list[int]) -> list[str]:
    """Init: A = subtune index. Reads per-subtune state from byte tables
    indexed by X; loads per-voice timbre, position, orderlist pointer,
    plus tempo + master vol."""
    L = [
        'init:',
        '  pha                  ; save A = subtune idx',
        # Silence SID.
        '  lda #0',
        '  ldx #0',
        'init_silence:',
        '  sta $d400,x',
        '  inx',
        '  cpx #$19',
        '  bne init_silence',
        # Master vol (single value across subtunes for fixed_init mode).
        f'  lda #${model.master_vol.init_value:02X}',
        '  sta $d418',
        '  pla',
        '  tax                  ; X = subtune index',
    ]
    # Per-voice initial position.
    for v in active:
        L.append(f'  lda init_v{v+1}_pos_tab,x')
        L.append(f'  sta v{v+1}_pos')
    L += [
        '  lda init_tempo_ctr_tab,x',
        '  sta tempo_ctr',
        '  lda tempo_tab,x',
        '  sta tempo_const',
    ]
    # Per-voice timbre fill — X-indexed (offset 0/7/14 in the timbre arrays).
    for fname in ('pwlo', 'pwhi', 'ctrl', 'ad', 'sr'):
        for v in active:
            L.append(f'  lda v{v+1}_{fname}_tab,x')
            L.append(f'  sta timbre_{fname}+{_VOICE_OFFSET[v]}')
    # Orderlist zp pointers.
    for v in active:
        zp_lo = _ZP_OL_BASE + 2 * v
        L.append(f'  lda v{v+1}_ol_lo_tab,x')
        L.append(f'  sta ${zp_lo:02X}')
        L.append(f'  lda v{v+1}_ol_hi_tab,x')
        L.append(f'  sta ${zp_lo + 1:02X}')
    # CIA1 timer A if any subtune programs one.
    if any(s.cia1_timer_a for s in model.subtunes):
        L += [
            '  lda cia1_lo_tab,x',
            '  sta $dc04',
            '  lda cia1_hi_tab,x',
            '  sta $dc05',
        ]
    L.append('  rts')
    return L


def _emit_play(model: EngineModel, active: list[int]) -> list[str]:
    """Play loop: tempo gate, then iterate over active voices."""
    L = [
        'play:',
        '  inc tempo_ctr',
        '  lda tempo_ctr',
        '  cmp tempo_const',
        '  bne play_exit',
        '  lda #0',
        '  sta tempo_ctr',
    ]
    if _has_carry_leak(model):
        # Reset the carry-leak flag each tick — V1 always starts with
        # 5-byte timbre (no prior voice this tick).
        L.append('  sta next_skip_sr')
    for v in active:
        L.append(f'  jsr voice{v+1}_step')
    L.append('play_exit:')
    L.append('  rts')
    return L


def _emit_proc_note(model: EngineModel) -> list[str]:
    """Shared per-voice note dispatcher. X = voice offset (0/7/14),
    A = byte to dispatch.

    The byte values for `rest` / `skip` come from the model's
    terminator vocab. The carry-leak quirk conditionally skips the SR
    write."""
    byte_map = model.terminators.byte_map
    rest = _rest_byte(byte_map)
    skip = _skip_byte(byte_map)
    carry_leak = _has_carry_leak(model)

    L = [
        'proc_note:',
        f'  cmp #${rest:02X}',
        '  beq pn_rest',
    ]
    # If the byte_map has the `skip` byte just above `rest`, we use
    # `bcs` after the `beq`. The current shapes all satisfy this.
    L += [
        '  bcs pn_skip',
        '  tay',
        '  lda freq_hi_tab,y',
        '  sta $d401,x',
        '  lda freq_lo_tab,y',
        '  sta $d400,x',
        '  lda timbre_pwlo,x',
        '  sta $d402,x',
        '  lda timbre_pwhi,x',
        '  sta $d403,x',
        '  lda timbre_ctrl,x',
        '  sta $d404,x          ; gate=0 (envelope retrigger)',
        '  lda timbre_ad,x',
        '  sta $d405,x',
    ]
    if carry_leak:
        L += [
            '  lda this_skip_sr',
            '  bne pn_no_sr_write',
            '  lda timbre_sr,x',
            '  sta $d406,x',
            'pn_no_sr_write:',
        ]
    else:
        L += [
            '  lda timbre_sr,x',
            '  sta $d406,x',
        ]
    L += [
        '  lda timbre_ctrl,x',
        '  ora #$01             ; gate=1',
        '  sta $d404,x',
        '  rts',
        'pn_rest:',
        '  lda timbre_ctrl,x',
        '  sta $d404,x',
        '  rts',
        'pn_skip:',
        '  rts',
    ]
    _ = skip   # captured into byte stream during pattern encode
    return L


def _emit_voice_step(model: EngineModel, v: int) -> list[str]:
    """Per-voice step: read next byte, handle the $FF terminator,
    classify (if carry-leak), then `jmp proc_note` with X = voice
    offset.

    Voice index `v` is 0-indexed. The voice's zp orderlist pointer
    lives at $E0+2*v / $E0+2*v+1.
    """
    byte_map = model.terminators.byte_map
    loop = _loop_byte(byte_map)
    loop_behavior = byte_map.get(loop, 'loop_reset')
    skip = _skip_byte(byte_map)
    carry_leak = _has_carry_leak(model)
    zp_lo = _ZP_OL_BASE + 2 * v
    voice_off = _VOICE_OFFSET[v]
    vn = v + 1

    L = [
        f'voice{vn}_step:',
        f'  ldy v{vn}_pos',
        f'  inc v{vn}_pos',
        f'  lda (${zp_lo:02X}),y',
        f'  cmp #${loop:02X}',
        f'  bne v{vn}_normal',
    ]

    # Loop-byte handler — varies by what behavior the byte maps to.
    if loop_behavior == 'master_vol_reset_and_loop':
        # henrys: write $D418 + reset pos, no further byte read this tick
        L += [
            f'  lda #${model.master_vol.init_value:02X}',
            '  sta $d418',
            '  lda #0',
            f'  sta v{vn}_pos',
            '  rts',
        ]
    elif loop_behavior == 'loop_substitute_first':
        # bowden: pos=1, replay byte 0 this tick. The carry-leak quirk
        # picks 4 or 5-byte timbre via this_skip_sr — V1/V2 force 4-byte,
        # V3 leaves 5-byte (engine carry-leak from CPX #$0E in original).
        L += [
            '  lda #1',
            f'  sta v{vn}_pos',
            '  ldy #0',
            f'  lda (${zp_lo:02X}),y',
        ]
        if carry_leak:
            force_4 = (v < 2)
            L += [
                f'  ldy #{1 if force_4 else 0}',
                '  sty this_skip_sr',
                f'  jmp v{vn}_classify',
            ]
        else:
            L.append(f'  jmp v{vn}_call')
    elif loop_behavior == 'loop_reset':
        # yes_tune-style: reset pos to 0 + recurse (not used yet in
        # composer's supported set, but defined for forward compat)
        L += [
            '  lda #0',
            f'  sta v{vn}_pos',
            f'  jmp v{vn}_normal',
        ]
    else:
        raise NotImplementedError(f'composer: unhandled loop behavior {loop_behavior!r}')

    L.append(f'v{vn}_normal:')
    if carry_leak:
        L += [
            '  ldy next_skip_sr',
            '  sty this_skip_sr',
            f'v{vn}_classify:',
            '  pha',
            f'  cmp #${skip:02X}',
            f'  bcc v{vn}_not_skip',
            f'  cmp #${loop:02X}',
            f'  beq v{vn}_not_skip',
            '  ldy #1',
            '  sty next_skip_sr',
            f'  jmp v{vn}_call',
            f'v{vn}_not_skip:',
            '  ldy #0',
            '  sty next_skip_sr',
            f'v{vn}_call:',
            '  pla',
        ]
    L += [
        f'  ldx #{voice_off}',
        '  jmp proc_note',
    ]
    return L


def _emit_runtime_vars(model: EngineModel, active: list[int]) -> list[str]:
    L = []
    for v in active:
        L.append(f'v{v+1}_pos:        .byte 0')
    L += [
        'tempo_ctr:     .byte 0',
        'tempo_const:   .byte 0',
    ]
    if _has_carry_leak(model):
        L += [
            'this_skip_sr:  .byte 0',
            'next_skip_sr:  .byte 0',
        ]
    # Timbre arrays — X-indexed at 0, 7, 14. The maximum X any voice
    # uses is _VOICE_OFFSET[max(active)]; size the array to cover it
    # plus the 5-byte stride.
    max_off = max((_VOICE_OFFSET[v] for v in active), default=0)
    arr_len = max_off + 5
    for fname in ('pwlo', 'pwhi', 'ctrl', 'ad', 'sr'):
        L.append(f'timbre_{fname}: .dsb {arr_len}, 0')
    return L


# ---------------------------------------------------------------------------
# Cmd-stream encoder — atomic-per-tick + embedded command bytes
# ---------------------------------------------------------------------------

def _cmd_row_bytes(row) -> bytes:
    """Cmd-stream row → engine bytes.

    Notes/rests: head + (duration-1) × skip bytes ($81 skip; $80 rest).
    Embedded commands (single byte, no skip extension — they don't
    consume a tick): `tempo=N` → $B0|N, `vol=N` → $C0|N, `instr_ref`
    on rest row → $D0|(id-1), `song_pos=N` → $E0|N. `fx:raw_NN` → raw.
    """
    flags = set(row.fx_flags)
    if not row.pitch.is_rest:
        head = (row.pitch.octave << 4) | _SEMI[row.pitch.name]
        return bytes([head]) + bytes([0x81] * (row.duration - 1))
    if row.instr is not None:
        return bytes([0xD0 | ((row.instr.id - 1) & 0x0F)])
    for flag in flags:
        if flag.startswith('tempo='):
            return bytes([0xB0 | (int(flag.split('=')[1]) & 0x0F)])
        if flag.startswith('vol='):
            return bytes([0xC0 | (int(flag.split('=')[1]) & 0x0F)])
        if flag.startswith('song_pos='):
            return bytes([0xE0 | (int(flag.split('=')[1]) & 0x0F)])
        if flag.startswith('fx:raw_'):
            return bytes([int(flag.split('_')[1], 16)])
    return bytes([0x80]) + bytes([0x81] * (row.duration - 1))


def _cmd_voice_bytes(voice_block) -> bytes:
    """Concatenate one voice's pattern rows. No terminator — the engine
    loops via $Ex pattern_jump commands that match song_pos."""
    if not voice_block.patterns:
        raise NotImplementedError(
            'cmd-stream voice requires at least one pattern')
    pat = voice_block.patterns[0]
    return b''.join(_cmd_row_bytes(r) for r in pat.rows)


# ---------------------------------------------------------------------------
# Companion-shape encoders — atomic-per-period + early-release flag + $8D end
# ---------------------------------------------------------------------------

def _companion_row_byte(row) -> int:
    """One pattern row → 1 engine byte.

    Normal pitch → (octave<<4)|semi.
    fx:early_release on pitch → $80 | pitch_byte.
    fx:early_release on rest → $8C.
    Rest without early_release → not representable in companion shape.
    """
    early = 'fx:early_release' in row.fx_flags
    if row.pitch.is_rest:
        if not early:
            raise NotImplementedError(
                'companion shape: rest row without fx:early_release '
                'is not representable')
        return 0x8C
    pitch_byte = (row.pitch.octave << 4) | _SEMI[row.pitch.name]
    return pitch_byte | (0x80 if early else 0)


def _companion_voice_bytes(voice_block, pad_count: int, pad_byte: int) -> bytes:
    """One voice's pattern bytes + $8D end-song terminator + post-
    terminator padding (engine reads past $8D into adjacent memory)."""
    if not voice_block.patterns:
        raise NotImplementedError('companion voice requires a pattern')
    pat = voice_block.patterns[0]
    body = bytes(_companion_row_byte(r) for r in pat.rows)
    return body + bytes([0x8D]) + bytes([pad_byte] * pad_count)


def _companion_template_bytes(per_voice_timbres: list[tuple],
                                gate_off_tick: int, note_load_tick: int,
                                init_tempo_counter: int,
                                init_pwm_ctr: int, init_pwm_ctr_2: int
                                ) -> bytes:
    """The 32-byte init template the engine copies into v_state at init.

    Layout:
      bytes 0..6   V1 (pos=0, gate_off_flag=0, pw_lo, pw_hi,
                       ctrl_noGate, ad, sr)
      bytes 7..13  V2 (same)
      bytes 14..20 V3 (same)
      byte 21      gate_off_tick
      byte 22      note_load_tick
      byte 23      init_tempo_counter
      bytes 24..29 6 zeros
      bytes 30..31 init_pwm_ctr, init_pwm_ctr_2
    """
    out = []
    for v_idx in range(3):
        t = per_voice_timbres[v_idx]
        # pos=0, gate_off_flag=0, then 5-byte timbre (pw_lo, pw_hi,
        # ctrl_noGate, ad, sr)
        out += [0, 0, t[0], t[1], t[2], t[3], t[4]]
    out += [
        gate_off_tick, note_load_tick, init_tempo_counter,
        0, 0, 0, 0, 0, 0,
        init_pwm_ctr, init_pwm_ctr_2,
    ]
    assert len(out) == 32, len(out)
    return bytes(out)


# ---------------------------------------------------------------------------
# Asm emitters — pair-shape (tick_counter_decrement voice timing)
# ---------------------------------------------------------------------------
#
# Per-voice state at `v_state + X` (X = 0/7/14):
#   +$00  tick_ctr        (decrements; plays next pair when reaches 0)
#   +$01  state           (0=silent, 1=playing, 2=load-pattern)
#   +$02..+$06  timbre    (pw_lo, pw_hi, ctrl, ad, sr)
#   +$15  pattern_ptr lo  (current position)
#   +$16  pattern_ptr hi
#   +$17  pat_start lo    (immutable reset target)
#   +$18  pat_start hi
#
# Pattern bytes:
#   $00-$7F + dur : NORMAL_NOTE — play freq + 5-byte timbre + gated ctrl,
#                   tick_ctr = dur, ptr += 2
#   $80 + dur     : REST — write ctrl gate-off, tick_ctr = dur, ptr += 2
#   $81           : STOP_VOICE — write ctrl gate-off, state = 0
#   $FF           : LOOP — reset ptr to pat_start, recurse play_note

def _emit_pair_init(model: EngineModel) -> list[str]:
    """Init: A = subtune index. Reads per-subtune state from byte tables.
    Master vol: written conditionally based on per-subtune `gain_init`
    flag (full = write $0F, preserve = skip the write)."""
    mv_init = model.master_vol.init_value
    L = [
        'init:',
        '  pha                  ; save A = subtune idx',
        '  tay                  ; Y = subtune index',
        '  lda init_d418_tab,y',
        '  beq init_skip_d418',
        f'  lda #${mv_init:02X}',
        '  sta $d418',
        'init_skip_d418:',
        '  pla',
        '  tay                  ; Y = subtune index',
    ]
    for v_idx, x in enumerate((0, 7, 14)):
        for j in range(5):
            L.append(f'  lda v{v_idx+1}_tb{j}_tab,y')
            L.append(f'  sta v_state+${0x02+x+j:02X}')
        L.append(f'  lda v{v_idx+1}_ps_lo_tab,y')
        L.append(f'  sta v_state+${0x15+x:02X}')
        L.append(f'  sta v_state+${0x17+x:02X}')
        L.append(f'  lda v{v_idx+1}_ps_hi_tab,y')
        L.append(f'  sta v_state+${0x16+x:02X}')
        L.append(f'  sta v_state+${0x18+x:02X}')
        L.append(f'  lda v{v_idx+1}_state_tab,y')
        L.append(f'  sta v_state+${0x01+x:02X}')
        L.append('  lda #$00')
        L.append(f'  sta v_state+${0x00+x:02X}')
    L += [
        '  lda tempo_tab,y',
        '  sta tempo_const',
        '  lda init_tempo_ctr_tab,y',
        '  sta tempo_ctr',
        '  rts',
    ]
    return L


def _emit_pair_play() -> list[str]:
    """Play: tempo gate + dispatch to shared voice_tick with each X."""
    L = [
        'play:',
        '  inc tempo_ctr',
        '  lda tempo_ctr',
        '  cmp tempo_const',
        '  bne play_exit',
        '  lda #0',
        '  sta tempo_ctr',
    ]
    for x in (0, 7, 14):
        L.append(f'  ldx #{x}')
        L.append('  jsr voice_tick')
    L += ['play_exit:', '  rts']
    return L


def _emit_pair_voice_tick() -> list[str]:
    """Shared voice_tick — X = voice offset. State machine: 0 silent,
    1 playing, 2 load-pattern."""
    return [
        'voice_tick:',
        '  lda v_state+1,x      ; state',
        '  cmp #2',
        '  bne vt_chk1',
        # load pattern
        '  lda v_state+$17,x',
        '  sta v_state+$15,x',
        '  lda v_state+$18,x',
        '  sta v_state+$16,x',
        '  lda #0',
        '  sta v_state,x        ; tick_ctr = 0',
        '  lda #1',
        '  sta v_state+1,x',
        'vt_chk1:',
        '  lda v_state+1,x',
        '  cmp #1',
        '  beq vt_play',
        '  rts                  ; state != 1 - skip',
        'vt_play:',
        '  lda v_state+$15,x',
        '  sta $fb',
        '  lda v_state+$16,x',
        '  sta $fc',
        '  jmp play_note',
    ]


def _emit_pair_play_note() -> list[str]:
    """Per-tick play_note: bit-7 dispatch on the byte at pattern_ptr.
    Normal note: tick_ctr==0 → emit freq + 5-byte timbre + gated ctrl,
    then advance ptr by 2 bytes. Otherwise dec tick_ctr.
    $80 dur: rest. $81: stop voice. $FF: loop to pat_start."""
    return [
        'play_note:',
        '  ldy #0',
        '  lda ($fb),y',
        '  and #$80',
        '  beq pn_normal',
        '  jmp pn_bit7',
        'pn_normal:',
        '  ldy v_state,x        ; tick_ctr',
        '  cpy #0',
        '  bne pn_dec',
        '  jsr pn_emit_note',
        '  jsr pn_advance',
        'pn_dec:',
        '  dec v_state,x',
        '  rts',
        'pn_emit_note:',
        '  ldy #0',
        '  lda ($fb),y',
        '  tay',
        '  lda freq_hi_tab,y',
        '  sta $d401,x',
        '  lda freq_lo_tab,y',
        '  sta $d400,x',
        '  txa',
        '  tay',
        '  clc',
        '  adc #$05',
        '  sta pn_endy',
        'pn_pw_loop:',
        '  lda v_state+2,y',
        '  sta $d402,y',
        '  iny',
        '  cpy pn_endy',
        '  bne pn_pw_loop',
        '  ldy v_state+4,x      ; ctrl byte',
        '  iny',
        '  tya',
        '  sta $d404,x          ; gate=1',
        '  rts',
        'pn_advance:',
        '  ldy #1',
        '  lda ($fb),y',
        '  cmp #0',
        '  bne pn_adv_ok',
        '  lda #1',
        'pn_adv_ok:',
        '  sta v_state,x',
        '  lda v_state+$15,x',
        '  clc',
        '  adc #2',
        '  sta v_state+$15,x',
        '  bcc pn_adv_done',
        '  inc v_state+$16,x',
        'pn_adv_done:',
        '  rts',
        'pn_bit7:',
        '  ldy #0',
        '  lda ($fb),y',
        '  cmp #$80',
        '  bne pn_n80',
        # $80 — rest with duration
        '  ldy v_state,x',
        '  cpy #0',
        '  bne pn_dec',
        '  lda v_state+4,x      ; ctrl',
        '  sta $d404,x',
        '  jsr pn_advance',
        '  jmp pn_dec',
        'pn_n80:',
        '  cmp #$ff',
        '  bne pn_nff',
        # $FF — loop to pat_start, recurse play_note
        '  lda v_state+$17,x',
        '  sta v_state+$15,x',
        '  lda v_state+$18,x',
        '  sta v_state+$16,x',
        '  lda #0',
        '  sta v_state,x',
        '  lda v_state+$15,x',
        '  sta $fb',
        '  lda v_state+$16,x',
        '  sta $fc',
        '  jmp play_note',
        'pn_nff:',
        '  cmp #$81',
        '  bne pn_other',
        # $81 — stop voice
        '  lda v_state+4,x',
        '  sta $d404,x',
        '  lda #0',
        '  sta v_state+1,x',
        'pn_other:',
        '  rts',
    ]


def _emit_pair_runtime_vars() -> list[str]:
    return [
        'pn_endy:     .byte 0',
        'tempo_const: .byte 0',
        'tempo_ctr:   .byte 0',
        # Per-voice state block — 3 voices × stride 7 plus the $15-$18
        # offsets push the largest used offset to V3+$18 = 14+24 = 38.
        # Allocate $20 ($28 actually = 40) to be safe.
        'v_state:     .dsb $28, 0',
    ]


def _emit_pair_per_subtune_tables(model: EngineModel,
                                   per_subtune_voice_timbres: list[list[tuple]],
                                   per_subtune_voice_init_states: list[list[int]]
                                   ) -> list[str]:
    """Per-subtune byte tables for pair shape.

    Tables:
      tempo_tab          — per-subtune tempo_const
      init_tempo_ctr_tab — per-subtune initial tempo counter
      init_d418_tab      — per-subtune gain_init (1=full / 0=preserve)
      v<N>_tb<J>_tab     — per-subtune per-voice timbre (5 fields × 3 voices)
      v<N>_state_tab     — per-subtune per-voice initial state byte (0/2)
      v<N>_ps_lo/hi_tab  — per-subtune per-voice pat_start address
    """
    subs = model.subtunes
    L = []
    n_sub = len(subs)

    def _tab(label: str, vals: list[int]) -> None:
        L.append(f'{label}: .byte ' +
                 ', '.join(f'${v & 0xFF:02X}' for v in vals))

    _tab('tempo_tab',          [s.tempo for s in subs])
    _tab('init_tempo_ctr_tab', [s.init_tempo_ctr for s in subs])

    # gain_init flag — 1 = write $D418 at init, 0 = skip (preserve
    # whatever vol was already set). The model builder sets
    # `master_vol_init = None` for `gain_init: preserve` and to the
    # actual byte value for `gain_init: full` (or `vol_filter: N`).
    init_d418 = [0 if s.master_vol_init is None else 1 for s in subs]
    _tab('init_d418_tab', init_d418)

    # Per-voice timbres (5 fields × 3 voices).
    for v_idx in range(3):
        for j in range(5):
            _tab(f'v{v_idx+1}_tb{j}_tab',
                 [per_subtune_voice_timbres[s_idx][v_idx][j]
                  for s_idx in range(n_sub)])

    # Per-voice initial state byte (0 = silent, 2 = load-pattern).
    for v_idx in range(3):
        _tab(f'v{v_idx+1}_state_tab',
             [per_subtune_voice_init_states[s_idx][v_idx]
              for s_idx in range(n_sub)])

    # Per-voice pat_start address tables — reference per-subtune
    # per-voice orderlist labels.
    for v_idx in range(3):
        L.append(f'v{v_idx+1}_ps_lo_tab: .byte ' + ', '.join(
            f'<orderlist_v{v_idx+1}_s{i}' for i in range(n_sub)))
        L.append(f'v{v_idx+1}_ps_hi_tab: .byte ' + ', '.join(
            f'>orderlist_v{v_idx+1}_s{i}' for i in range(n_sub)))
    return L


# ---------------------------------------------------------------------------
# Asm emitters — cmd-stream shape (dur_counter_decrement + embedded
# commands $Bx/$Cx/$Dx/$Ex/$82 + recursive interpreter)
# ---------------------------------------------------------------------------
#
# Per-voice state at `v_state + X` (X = 0/7/14):
#   +$00  pattern_ptr lo
#   +$01  pattern_ptr hi
#   +$02..+$06  timbre (5 bytes: pw_lo, pw_hi, ctrl, ad, sr)
#
# Per-voice `dur_ctr` at stride 1: dur_ctr+0/+1/+2 for V1/V2/V3.

def _emit_cmd_init(model: EngineModel, has_cia: bool) -> list[str]:
    """Init: A = subtune index. Silence SID, write per-subtune master
    vol, load song_table[0..5] into V1/V2/V3 ptrs, dur_ctr=1 × 3,
    song_pos + tempo + tempo_ctr from per-subtune tables."""
    L = [
        'init:',
        '  pha                  ; save A = subtune idx',
        '  lda #0',
        '  ldx #0',
        'init_silence:',
        '  sta $d400,x',
        '  inx',
        '  cpx #$19',
        '  bne init_silence',
        '  pla',
        '  tax                  ; X = subtune index',
        '  lda init_master_vol_tab,x',
        '  sta $d418',
        '  lda song_table+0',
        '  sta v_state+0',
        '  lda song_table+1',
        '  sta v_state+1',
        '  lda song_table+2',
        '  sta v_state+7',
        '  lda song_table+3',
        '  sta v_state+8',
        '  lda song_table+4',
        '  sta v_state+14',
        '  lda song_table+5',
        '  sta v_state+15',
        '  lda #1',
        '  sta dur_ctr+0',
        '  sta dur_ctr+1',
        '  sta dur_ctr+2',
        '  lda init_song_pos_tab,x',
        '  sta song_pos',
        '  lda tempo_tab,x',
        '  sta tempo_const',
        '  lda init_tempo_ctr_tab,x',
        '  sta tempo_ctr',
    ]
    if has_cia:
        L += [
            '  lda cia1_lo_tab,x',
            '  sta $dc04',
            '  lda cia1_hi_tab,x',
            '  sta $dc05',
        ]
    L.append('  rts')
    return L


def _emit_cmd_play() -> list[str]:
    """Play loop: tempo gate, then per-voice dur_ctr check + load_note."""
    L = [
        'play:',
        '  inc tempo_ctr',
        '  lda tempo_ctr',
        '  cmp tempo_const',
        '  bne play_exit',
        '  lda #0',
        '  sta tempo_ctr',
    ]
    for v, (x, dur_off) in enumerate([(0, 0), (7, 1), (14, 2)]):
        L += [
            f'  ldx #{x}',
            f'  lda dur_ctr+{dur_off}',
            '  cmp #1',
            f'  bne v{v+1}_dec',
            '  jsr load_note',
            f'  jmp v{v+1}_done',
            f'v{v+1}_dec:',
            f'  dec dur_ctr+{dur_off}',
            f'v{v+1}_done:',
        ]
    L += ['play_exit:', '  rts']
    return L


def _emit_cmd_load_note() -> list[str]:
    """Recursive command interpreter. X = voice offset.

    Reads one byte, dispatches:
      $00-$7F NORMAL_NOTE → play freq + 5-byte timbre + gated ctrl
      $80 REST → ctrl gate-off
      $81 SKIP → return
      $82 dur SET_DURATION → gate off + dur_ctr = next byte, return
      $Bx SET_TEMPO → tempo_const = low nibble, recurse
      $Cx SET_MASTER_VOL → $D418 = low nibble, recurse
      $Dx SET_INSTRUMENT → copy 5 bytes from inst_table, recurse
      $Ex PATTERN_JUMP (matches song_pos) → jump via song_table,
                                            advance song_pos, recurse
      other bit-7 → SKIP_BYTE + recurse
    """
    return [
        '; load_note expects X as voice offset 0,7,14',
        'load_note:',
        '  ldy #0',
        '  lda v_state+0,x',
        '  sta zp_ptr_lo',
        '  lda v_state+1,x',
        '  sta zp_ptr_hi',
        '  inc v_state+0,x',
        '  bne ln_skip_inc_hi',
        '  inc v_state+1,x',
        'ln_skip_inc_hi:',
        '  lda (zp_ptr_lo),y',
        '  tay',
        '  and #$80',
        '  bne ln_bit7',
        # NORMAL NOTE
        '  lda freq_hi_tab,y',
        '  sta $d401,x',
        '  lda freq_lo_tab,y',
        '  sta $d400,x',
        '  txa',
        '  tay',
        '  clc',
        '  adc #$05',
        '  sta zp_endy',
        'ln_pw_loop:',
        '  lda v_state+2,y',
        '  sta $d402,y',
        '  iny',
        '  cpy zp_endy',
        '  bne ln_pw_loop',
        '  ldy v_state+4,x',
        '  iny',
        '  tya',
        '  sta $d404,x',
        '  rts',
        'ln_bit7:',
        '  cpy #$80',
        '  bne ln_not80',
        '  lda v_state+4,x',
        '  sta $d404,x',
        '  rts',
        'ln_not80:',
        '  cpy #$81',
        '  bne ln_not81',
        '  rts',
        'ln_not81:',
        '  cpy #$82',
        '  bne ln_not82',
        # SET_DURATION
        '  lda v_state+4,x',
        '  sta $d404,x',
        '  lda v_state+0,x',
        '  sta zp_ptr_lo',
        '  lda v_state+1,x',
        '  sta zp_ptr_hi',
        '  inc v_state+0,x',
        '  bne ln82_no_carry',
        '  inc v_state+1,x',
        'ln82_no_carry:',
        '  txa',
        '  clc',
        '  ror',
        '  clc',
        '  adc #$01',
        '  clc',
        '  ror',
        '  clc',
        '  ror',
        '  stx zp_x_save',
        '  tax',
        '  ldy #0',
        '  lda (zp_ptr_lo),y',
        '  sta dur_ctr,x',
        '  ldx zp_x_save',
        '  rts',
        'ln_not82:',
        # $Ex PATTERN_JUMP (when Y == song_pos)
        '  cpy song_pos',
        '  bne ln_not_ex',
        '  inc song_pos',
        '  lda song_pos',
        '  cmp #$e6',
        '  bne ln_no_wrap',
        '  lda #$e0',
        '  sta song_pos',
        'ln_no_wrap:',
        '  tya',
        '  and #$0f',
        '  clc',
        '  rol',
        '  tay',
        '  lda song_table,y',
        '  sta v_state+0,x',
        '  iny',
        '  lda song_table,y',
        '  sta v_state+1,x',
        '  jsr load_note',
        '  rts',
        'ln_not_ex:',
        # $Dx SET_INSTRUMENT — copy 5 bytes from inst_table
        '  tya',
        '  and #$f0',
        '  cmp #$d0',
        '  bne ln_not_dx',
        '  tya',
        '  and #$0f',
        '  sta zp_tmp',
        '  asl',
        '  asl',
        '  clc',
        '  adc zp_tmp',
        '  tay',
        '  stx zp_x_save',
        '  txa',
        '  clc',
        '  adc #2',
        '  tax',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  inx',
        '  iny',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  inx',
        '  iny',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  inx',
        '  iny',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  inx',
        '  iny',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  ldx zp_x_save',
        '  jsr load_note',
        '  rts',
        'ln_not_dx:',
        # $Cx SET_MASTER_VOL
        '  tya',
        '  and #$f0',
        '  cmp #$c0',
        '  bne ln_not_cx',
        '  tya',
        '  and #$0f',
        '  sta $d418',
        '  jsr load_note',
        '  rts',
        'ln_not_cx:',
        # $Bx SET_TEMPO
        '  tya',
        '  and #$f0',
        '  cmp #$b0',
        '  bne ln_other_bit7',
        '  tya',
        '  and #$0f',
        '  sta tempo_const',
        '  jsr load_note',
        '  rts',
        'ln_other_bit7:',
        # Unrecognized bit-7 — SKIP_BYTE + recurse
        '  jsr load_note',
        '  rts',
    ]


def _emit_cmd_runtime_vars() -> list[str]:
    return [
        'zp_ptr_lo = $FB',
        'zp_ptr_hi = $FC',
        'zp_endy:     .byte 0',
        'zp_x_save:   .byte 0',
        'zp_tmp:      .byte 0',
        'v_state:     .dsb 21, 0',
        'dur_ctr:     .dsb 3, 0',
        'tempo_const: .byte 0',
        'tempo_ctr:   .byte 0',
        'song_pos:    .byte 0',
    ]


def _emit_cmd_inst_table(model: EngineModel) -> list[str]:
    """Engine-wide 16-instrument palette — 16 × 5-byte rows.

    Instruments < 16 are real entries; pad to 16 with zeros."""
    L = ['inst_table:']
    insts_sorted = sorted(model.instruments, key=lambda i: i.id)
    for inst in insts_sorted:
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in [
            inst.init_pw_lo, inst.init_pw_hi, inst.init_ctrl,
            inst.init_ad, inst.init_sr,
        ]))
    # Pad to 16 entries with zeros.
    for _ in range(16 - len(insts_sorted)):
        L.append('  .byte $00, $00, $00, $00, $00')
    return L


def _emit_cmd_song_table() -> list[str]:
    """Song table — 6 entries × 2 bytes. E0/E3 → V1, E1/E4 → V2,
    E2/E5 → V3. For single-subtune cmd-stream USFs, the entries
    point at ptn_v1/v2/v3 directly."""
    return [
        'song_table:',
        '  .byte <ptn_v1, >ptn_v1     ; E0',
        '  .byte <ptn_v2, >ptn_v2     ; E1',
        '  .byte <ptn_v3, >ptn_v3     ; E2',
        '  .byte <ptn_v1, >ptn_v1     ; E3',
        '  .byte <ptn_v2, >ptn_v2     ; E4',
        '  .byte <ptn_v3, >ptn_v3     ; E5',
    ]


def _emit_cmd_per_subtune_tables(model: EngineModel,
                                  has_cia: bool) -> list[str]:
    """Per-subtune byte tables for cmd-stream shape."""
    subs = model.subtunes
    L = []

    def _tab(label, vals):
        L.append(f'{label}: .byte ' +
                 ', '.join(f'${v & 0xFF:02X}' for v in vals))

    _tab('tempo_tab',          [s.tempo for s in subs])
    _tab('init_tempo_ctr_tab', [s.init_tempo_ctr for s in subs])
    _tab('init_song_pos_tab',  [s.init_song_pos if s.init_song_pos is not None
                                 else 0xE0 for s in subs])
    # init_master_vol: per-subtune; falls back to model.master_vol.init_value
    # when SubtuneSpec.master_vol_init is None.
    default_mv = model.master_vol.init_value
    _tab('init_master_vol_tab',
         [s.master_vol_init if s.master_vol_init is not None else default_mv
          for s in subs])
    if has_cia:
        DEFAULT_CIA = 0x4CC7
        cia_vals = [s.cia1_timer_a or DEFAULT_CIA for s in subs]
        _tab('cia1_lo_tab', [v & 0xFF for v in cia_vals])
        _tab('cia1_hi_tab', [(v >> 8) & 0xFF for v in cia_vals])
    return L


def _emit_cmd_orderlists(per_subtune_voice_patterns: list[dict[int, bytes]]
                          ) -> list[str]:
    """Cmd-stream pattern data — single-subtune today (Fairlight,
    Gyroscope). Emits ptn_v1, ptn_v2, ptn_v3 labels (no subtune suffix)."""
    L = []
    if len(per_subtune_voice_patterns) != 1:
        raise NotImplementedError(
            'cmd-stream multi-subtune not supported yet')
    voices = per_subtune_voice_patterns[0]
    for vid in (1, 2, 3):
        L.append(f'ptn_v{vid}:')
        pb = voices.get(vid - 1, bytes())
        for i in range(0, len(pb), 16):
            L.append('  .byte ' + ', '.join(
                f'${b:02X}' for b in pb[i:i+16]))
    return L


# ---------------------------------------------------------------------------
# Asm emitters — companion shape (two-phase tempo + V3 PW sweep +
# early-release flag + 32-byte init template)
# ---------------------------------------------------------------------------
#
# Per-subtune 32-byte template at v_state:
#   bytes 0..6   V1 (pos, gate_off_flag, 5-byte timbre)
#   bytes 7..13  V2 (same)
#   bytes 14..20 V3 (same)
#   byte 21      gate_off_tick      (early-release timer cap)
#   byte 22      note_load_tick     (next-note timer cap)
#   byte 23      init_tempo_counter
#   bytes 24..29 6 zeros
#   bytes 30..31 init_pwm_ctr, init_pwm_ctr_2
#
# `g_tempo_ctr` and `g_pwm_ctr` alias v_state+23 and v_state+30 so the
# template copy at init also seeds the runtime counters.

def _emit_companion_init() -> list[str]:
    """A = subtune idx. Copies 32-byte template into v_state from
    per-subtune tmpl_s{N} (selected via tmpl_lo/hi tables). Loads
    orderlist zp pointers; programs filter + master vol; marks song
    alive."""
    return [
        'init:',
        '  sta sub_idx',
        '  ldx sub_idx',
        '  lda tmpl_lo,x',
        '  sta cmp_tcopy+1',
        '  lda tmpl_hi,x',
        '  sta cmp_tcopy+2',
        '  ldx #0',
        'cmp_tcopy:',
        '  lda $FFFF,x          ; OPERAND patched at runtime',
        '  sta v_state,x',
        '  inx',
        '  cpx #32',
        '  bne cmp_tcopy',
        '  ldx sub_idx',
        '  lda ord_v1_lo,x',
        f'  sta ${0xE0:02X}',
        '  lda ord_v1_hi,x',
        f'  sta ${0xE1:02X}',
        '  lda ord_v2_lo,x',
        f'  sta ${0xE2:02X}',
        '  lda ord_v2_hi,x',
        f'  sta ${0xE3:02X}',
        '  lda ord_v3_lo,x',
        f'  sta ${0xE4:02X}',
        '  lda ord_v3_hi,x',
        f'  sta ${0xE5:02X}',
        '  lda sub_fcHi,x',
        '  sta $D416',
        '  lda #0',
        '  sta $D417',
        '  lda sub_vol,x',
        '  sta $D418',
        '  lda #1',
        '  sta g_song_alive',
        '  rts',
    ]


def _emit_companion_play(model: EngineModel) -> list[str]:
    """Two-tempo play loop. PWM block first (toggling pwm_ctr +
    Vn PW_LO sweep on 1→0 transition), then tempo counter. On
    gate_off_tick → maybe_gate_off × 3; on note_load_tick → reset
    + advance + proc_note × 3."""
    sweep = model.hardcoded_pw_sweep
    # `g_pwm_ctr` aliases v_state+30. The legacy engine writes the
    # swept register via the carry-leak +5 pattern (CMP sets carry,
    # ADC #4 effectively adds 5). Mirror that for byte-exact match.
    L = [
        'play:',
        '  inc g_pwm_ctr',
        '  lda g_pwm_ctr',
        '  cmp #$01',
        '  bne cmp_pwm_done',
        '  lda #0',
        '  sta g_pwm_ctr',
    ]
    if sweep is not None:
        # Swept voice's pw_lo offset in v_state = (voice_idx * 7) + 2 + 0
        # = voice_idx * 7 + 2. For V3 (idx=2): 14 + 2 = 16.
        pw_lo_off = sweep.voice_idx * 7 + 2
        sid_reg = 0xD400 + sweep.voice_idx * 7 + 0x02  # voice pw_lo reg
        # The original engine's `ADC #4` after `CMP #$01` adds 5
        # (carry from CMP). Use the delta_per_phase - 1 to mirror that.
        adc_imm = sweep.delta_per_phase - 1
        L += [
            f'  lda v_state+{pw_lo_off}',
            f'  adc #{adc_imm}',
            f'  sta v_state+{pw_lo_off}',
            f'  sta ${sid_reg:04X}',
        ]
    L += [
        'cmp_pwm_done:',
        '  inc g_tempo_ctr',
        '  lda g_tempo_ctr',
        '  cmp v_state+21        ; gate_off_tick',
        '  bne cmp_not_gate_off',
        '  ldx #0',
        '  jsr cmp_maybe_gate_off',
        '  ldx #7',
        '  jsr cmp_maybe_gate_off',
        '  ldx #14',
        '  jsr cmp_maybe_gate_off',
        '  jmp cmp_play_done',
        'cmp_not_gate_off:',
        '  cmp v_state+22        ; note_load_tick',
        '  bne cmp_play_done',
        '  lda #0',
        '  sta g_tempo_ctr',
        '  ldx #0',
        '  ldy v_state+0',
        '  inc v_state+0',
        f'  lda (${0xE0:02X}),y',
        '  tay',
        '  jsr cmp_proc_note',
        '  ldx #7',
        '  ldy v_state+7',
        '  inc v_state+7',
        f'  lda (${0xE2:02X}),y',
        '  tay',
        '  jsr cmp_proc_note',
        '  ldx #14',
        '  ldy v_state+14',
        '  inc v_state+14',
        f'  lda (${0xE4:02X}),y',
        '  tay',
        '  jsr cmp_proc_note',
        'cmp_play_done:',
        '  rts',
    ]
    return L


def _emit_companion_maybe_gate_off() -> list[str]:
    return [
        'cmp_maybe_gate_off:',
        '  lda v_state+1,x       ; gate_off flag',
        '  bmi cmp_do_gate_off',
        '  rts',
        'cmp_do_gate_off:',
        '  lda v_state+4,x       ; ctrl_noGate',
        '  sta $D404,x',
        '  lda #0',
        '  sta v_state+1,x',
        '  rts',
    ]


def _emit_companion_proc_note(model: EngineModel) -> list[str]:
    """X = voice offset (0/7/14), Y = note byte.

    bit-7 clear → normal note: freq + 5-byte timbre + gate-on.
    bit-7 set:
      - save bit-7 flag at v_state+1,x (gate-off scheduled)
      - mask low 7
      - $0C → rest (gate off)
      - $0D → end_or_rest (gate off; on the end-song voice also
              writes $D418=0 + clears g_song_alive)
      - else $80+pitch → play pitch + leave flag set so
                         maybe_gate_off fires at next gate_off_tick.
    """
    # End-song voice index from terminator vocab; companion writes
    # vol=0 + song_alive=0 on V3's $8D ($0D after stripping bit-7).
    end_song_voice = model.terminators.end_song_voice_idx
    end_song_x = (end_song_voice or 0) * 7 if end_song_voice is not None else None
    sweep = model.hardcoded_pw_sweep
    sweep_voice_x = sweep.voice_idx * 7 if sweep else None

    L = [
        'cmp_proc_note:',
        '  tya',
        '  and #$80',
        '  beq cmp_proc_normal',
        '  sta v_state+1,x       ; flag = $80',
        '  tya',
        '  and #$7F',
        '  tay',
        '  cpy #$0C',
        '  beq cmp_proc_rest',
        '  cpy #$0D',
        '  beq cmp_proc_end_or_rest',
        'cmp_proc_normal:',
        '  lda freq_hi_tab,y',
        '  sta $D401,x',
        '  lda freq_lo_tab,y',
        '  sta $D400,x',
    ]
    # Skip pw_lo for the swept voice — its PW_LO is driven only by
    # the global sweep.
    if sweep_voice_x is not None:
        L += [
            f'  cpx #{sweep_voice_x}',
            '  beq cmp_skip_pwlo',
            '  lda v_state+2,x',
            '  sta $D402,x',
            'cmp_skip_pwlo:',
        ]
    else:
        L += [
            '  lda v_state+2,x',
            '  sta $D402,x',
        ]
    L += [
        '  lda v_state+3,x',
        '  sta $D403,x',
        '  lda v_state+5,x',
        '  sta $D405,x',
        '  lda v_state+6,x',
        '  sta $D406,x',
        '  lda v_state+4,x       ; ctrl_noGate',
        '  ora #$01              ; gate on',
        '  sta $D404,x',
        '  rts',
        'cmp_proc_rest:',
        '  lda v_state+4,x',
        '  sta $D404,x',
        '  rts',
        'cmp_proc_end_or_rest:',
        '  lda v_state+4,x',
        '  sta $D404,x',
    ]
    if end_song_x is not None:
        L += [
            f'  cpx #{end_song_x}',
            '  bne cmp_proc_end_done',
            '  lda #0',
            '  sta g_song_alive',
            '  sta $D418',
            'cmp_proc_end_done:',
            '  rts',
        ]
    else:
        L.append('  rts')
    return L


def _emit_companion_runtime_vars() -> list[str]:
    return [
        'sub_idx:       .byte 0',
        'g_song_alive:  .byte 0',
        # 32-byte template area. g_tempo_ctr and g_pwm_ctr alias
        # v_state+23 (init_tempo_counter slot) and v_state+30
        # (init_pwm_ctr slot) so the template copy at init seeds
        # both runtime counters.
        'v_state:       .dsb 32, 0',
        'g_tempo_ctr = v_state+23',
        'g_pwm_ctr   = v_state+30',
    ]


def _emit_companion_per_subtune_blocks(model: EngineModel,
                                        per_subtune_voice_orderlists: list[list[bytes]],
                                        per_subtune_voice_timbres: list[list[tuple]]
                                        ) -> list[str]:
    """Per-subtune blocks (orderlist × 3 + template) + dispatch tables.

    Layout follows the legacy companion engine: each subtune emits
    `ord_s{N}_v1`, `ord_s{N}_v2`, `ord_s{N}_v3`, `tmpl_s{N}` in
    sequence (so the engine's "read past $8D" overruns predictable
    bytes from the next voice's orderlist or the template).
    """
    L = []
    subs = model.subtunes
    n_sub = len(subs)

    for s_idx, sub in enumerate(subs):
        L.append(f'; ----- subtune {sub.id} block -----')
        # V1/V2/V3 orderlists
        for v_idx in range(3):
            L.append(f'ord_s{sub.id}_v{v_idx+1}:')
            ob = per_subtune_voice_orderlists[s_idx][v_idx]
            for i in range(0, len(ob), 16):
                L.append('  .byte ' + ', '.join(
                    f'${b:02X}' for b in ob[i:i+16]))
        # Per-subtune template — built from voice timbres + timing/PWM
        init_pwm = sub.init_pwm_state or (0, 0)
        tmpl = _companion_template_bytes(
            per_subtune_voice_timbres[s_idx],
            sub.gate_off_tick or 0,
            sub.note_load_tick or 0,
            sub.init_tempo_ctr,
            init_pwm[0], init_pwm[1])
        L.append(f'tmpl_s{sub.id}:')
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in tmpl[:16]))
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in tmpl[16:32]))

    # Dispatch tables (one entry per subtune)
    L.append('; ----- dispatch tables -----')
    L.append('ord_v1_lo: .byte ' + ', '.join(
        f'<ord_s{subs[i].id}_v1' for i in range(n_sub)))
    L.append('ord_v1_hi: .byte ' + ', '.join(
        f'>ord_s{subs[i].id}_v1' for i in range(n_sub)))
    L.append('ord_v2_lo: .byte ' + ', '.join(
        f'<ord_s{subs[i].id}_v2' for i in range(n_sub)))
    L.append('ord_v2_hi: .byte ' + ', '.join(
        f'>ord_s{subs[i].id}_v2' for i in range(n_sub)))
    L.append('ord_v3_lo: .byte ' + ', '.join(
        f'<ord_s{subs[i].id}_v3' for i in range(n_sub)))
    L.append('ord_v3_hi: .byte ' + ', '.join(
        f'>ord_s{subs[i].id}_v3' for i in range(n_sub)))
    L.append('tmpl_lo:   .byte ' + ', '.join(
        f'<tmpl_s{subs[i].id}' for i in range(n_sub)))
    L.append('tmpl_hi:   .byte ' + ', '.join(
        f'>tmpl_s{subs[i].id}' for i in range(n_sub)))
    # Per-subtune filter cutoff + master vol byte tables.
    L.append('sub_fcHi:  .byte ' + ', '.join(
        f'${(s.filter_cutoff_hi or 0):02X}' for s in subs))
    L.append('sub_vol:   .byte ' + ', '.join(
        f'${(s.master_vol_init or 0):02X}' for s in subs))
    return L


# ---------------------------------------------------------------------------

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


def _emit_per_subtune_tables(model: EngineModel, active: list[int],
                              per_subtune_voice_timbres: list[list[tuple]]
                              ) -> list[str]:
    """Per-subtune byte tables: tempo, init_tempo_ctr, init_v{N}_pos,
    v{N}_{field}_tab × 5 fields. Plus optional cia1_lo/hi.

    `per_subtune_voice_timbres[s][v]` is a 5-tuple
    (pw_lo, pw_hi, ctrl, ad, sr) for voice v in subtune s.
    """
    subs = model.subtunes
    L = []

    def _tab(label: str, vals: list[int]) -> None:
        L.append(f'{label}: .byte ' +
                 ', '.join(f'${v & 0xFF:02X}' for v in vals))

    _tab('tempo_tab',          [s.tempo for s in subs])
    _tab('init_tempo_ctr_tab', [s.init_tempo_ctr for s in subs])
    for v in active:
        _tab(f'init_v{v+1}_pos_tab',
             [s.voice_init[v].initial_position if v < len(s.voice_init) else 0
              for s in subs])
    fields = ['pwlo', 'pwhi', 'ctrl', 'ad', 'sr']
    for v in active:
        for fi, fname in enumerate(fields):
            _tab(f'v{v+1}_{fname}_tab',
                 [per_subtune_voice_timbres[s_idx][v][fi]
                  for s_idx in range(len(subs))])
    if any(s.cia1_timer_a for s in subs):
        DEFAULT_CIA = 0x4CC7
        cia_vals = [s.cia1_timer_a or DEFAULT_CIA for s in subs]
        _tab('cia1_lo_tab', [v & 0xFF for v in cia_vals])
        _tab('cia1_hi_tab', [(v >> 8) & 0xFF for v in cia_vals])
    n_sub = len(subs)
    for v in active:
        L.append(f'v{v+1}_ol_lo_tab: .byte ' + ', '.join(
            f'<orderlist_v{v+1}_s{i}' for i in range(n_sub)))
        L.append(f'v{v+1}_ol_hi_tab: .byte ' + ', '.join(
            f'>orderlist_v{v+1}_s{i}' for i in range(n_sub)))
    return L


def _emit_orderlists(active: list[int],
                      per_subtune_voice_patterns: list[dict[int, bytes]]) -> list[str]:
    """Emit per-subtune × per-voice orderlist data blocks."""
    L = []
    for s_idx, voice_pats in enumerate(per_subtune_voice_patterns):
        for v in active:
            L.append(f'orderlist_v{v+1}_s{s_idx}:')
            pb = voice_pats.get(v, bytes())
            if not pb:
                pb = bytes([0xFF])
            for i in range(0, len(pb), 16):
                L.append('  .byte ' + ', '.join(
                    f'${b:02X}' for b in pb[i:i+16]))
    return L


# ---------------------------------------------------------------------------
# Top-level compose
# ---------------------------------------------------------------------------

def emit_asm(model: EngineModel,
             active: list[int],
             per_subtune_voice_timbres: list[list[tuple]],
             per_subtune_voice_patterns: list[dict[int, bytes]],
             per_subtune_voice_init_states: list[list[int]] | None = None,
             ) -> str:
    """Emit asm composed from the model's features.

    Dispatch on `voice_timing.mode` — different timing modes produce
    structurally different play loops (every-tick atomic dispatch vs
    per-voice tick-counter state machine). This is feature-driven
    dispatch on a real USF feature, not engine identification.
    """
    if not can_handle(model):
        raise NotImplementedError(
            'composer does not yet support every feature in this model. '
            'See `can_handle()`.')

    L: list[str] = []
    L += _emit_header()

    if model.voice_timing.mode == 'every_tick':
        if model.tempo_dispatch.mode == 'two_phase':
            # Companion shape: two-tempo dispatch (gate_off_tick +
            # note_load_tick) + hardcoded V3 PW sweep + early-release
            # flag + 32-byte init template per subtune. Voices read
            # next byte only when the global tempo_ctr hits
            # note_load_tick; no per-voice counter.
            L += _emit_companion_init()
            L += _emit_companion_play(model)
            L += _emit_companion_maybe_gate_off()
            L += _emit_companion_proc_note(model)
            L += _emit_companion_runtime_vars()
            L += _emit_freq_table(model.freq_table)
            # Convert per-subtune-voice-patterns dict to ordered list
            per_subtune_voice_orderlists = [
                [per_subtune_voice_patterns[s_idx].get(v, bytes([0x8D]))
                 for v in range(3)]
                for s_idx in range(len(model.subtunes))]
            L += _emit_companion_per_subtune_blocks(
                model, per_subtune_voice_orderlists,
                per_subtune_voice_timbres)
        else:
            # Atomic-byte-per-tick (single-phase tempo): per-voice
            # voice_step routines + shared proc_note + RAM-mutable
            # per-voice positions.
            L += _emit_init(model, active)
            L += _emit_play(model, active)
            L += _emit_proc_note(model)
            for v in active:
                L += _emit_voice_step(model, v)
            L += _emit_runtime_vars(model, active)
            L += _emit_freq_table(model.freq_table)
            L += _emit_per_subtune_tables(model, active, per_subtune_voice_timbres)
            L += _emit_orderlists(active, per_subtune_voice_patterns)

    elif model.voice_timing.mode == 'tick_counter_decrement':
        # Per-voice tick-counter state machine: shared voice_tick called
        # with X = voice offset; recursive play_note dispatches on byte
        # values; per-voice state block at v_state[X].
        if per_subtune_voice_init_states is None:
            raise ValueError(
                'pair shape requires per_subtune_voice_init_states')
        L += _emit_pair_init(model)
        L += _emit_pair_play()
        L += _emit_pair_voice_tick()
        L += _emit_pair_play_note()
        L += _emit_pair_runtime_vars()
        L += _emit_freq_table(model.freq_table)
        L += _emit_pair_per_subtune_tables(
            model, per_subtune_voice_timbres, per_subtune_voice_init_states)
        # The pair shape always emits all 3 voice slots' orderlists
        # (silent voices get a $81 sentinel from the encoder).
        L += _emit_orderlists([0, 1, 2], per_subtune_voice_patterns)

    elif model.voice_timing.mode == 'dur_counter_decrement':
        # Per-voice dur-counter with a recursive command interpreter.
        # Distinguished from a hypothetical other dur-counter shape by
        # the presence of `commands` (embedded $Bx/$Cx/$Dx/$Ex bytes)
        # and atomic_per_tick pattern encoding.
        if model.commands is None:
            raise NotImplementedError(
                'dur_counter_decrement without commands not supported '
                '(would be Hubbard\'s bitpack codec — Phase 8)')
        has_cia = any(s.cia1_timer_a for s in model.subtunes)
        L += _emit_cmd_init(model, has_cia)
        L += _emit_cmd_play()
        L += _emit_cmd_load_note()
        L += _emit_cmd_runtime_vars()
        L += _emit_freq_table(model.freq_table)
        L += _emit_cmd_inst_table(model)
        L += _emit_cmd_song_table()
        L += _emit_cmd_per_subtune_tables(model, has_cia)
        L += _emit_cmd_orderlists(per_subtune_voice_patterns)

    else:
        raise NotImplementedError(
            f'composer: voice_timing.mode {model.voice_timing.mode!r} '
            f'not supported yet')

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


# ---------------------------------------------------------------------------
# USF entry — encodes pattern bytes + per-voice timbres from the USF,
# then composes asm via emit_asm.
# ---------------------------------------------------------------------------

def emit_sid_from_usf(usf, usf_dir: str | None = None) -> bytes:
    from pipelines.engine_model import from_usf
    model = from_usf(usf)

    # Hubbard '85 dispatch: the bitpack codec + full modulation pipeline
    # + SFX/digi sub-engines are large enough that they're currently
    # served by the lifted parametric core in `universal_codegen.py`
    # (`_emit_hubbard85_bytes`). The composer detects hubbard85 USFs by
    # USF content (rich instrument modulation, multi-pattern orderlists,
    # SFX subtunes, state_layout block — all features the simpler
    # composer emitters can't produce) and delegates.
    #
    # Future phases (8.1+) will decompose the Hubbard '85 ENGINE asm
    # into per-feature composer emitters parametric on EngineModel
    # features — one feature at a time, byte-exact-regression at each
    # step. For now: composer is the single entry; the implementation
    # for hubbard85 still lives in universal_codegen.py.
    if _needs_hubbard85_path(usf, model):
        from pipelines.universal_codegen import _emit_hubbard85_bytes
        return _emit_hubbard85_bytes(usf, usf_dir)

    if not can_handle(model):
        raise NotImplementedError(
            'composer cannot handle this USF yet — fall through to legacy')

    active = _active_voice_indices(model, usf=usf)
    if not active:
        raise NotImplementedError('USF has no active voices')

    # Per-subtune, per-voice timbres. Each subtune carries its own
    # `init.voices` which references instruments — usually subtune-
    # specific (e.g. Melonmania's subtunes use different instruments).
    # The ctrl byte's source depends on the model's `voices.ctrl_source`:
    # 'instrument_waveform' (most shapes) or 'init_voice_field'
    # (companion — ctrl_noGate is the per-voice InitVoice.ctrl byte).
    from src.usf import MusicSubtune
    music = sorted(
        (s for s in usf.subtunes if isinstance(s, MusicSubtune)),
        key=lambda s: s.id)
    instr_by_id = {i.id: i for i in usf.instruments}
    ctrl_from_init = (model.voices.ctrl_source == 'init_voice_field')

    per_subtune_voice_timbres: list[list[tuple]] = []
    for ms in music:
        init_voices = (ms.init.voices if (ms.init and ms.init.voices)
                       else usf.init.voices)
        iv_by_id = {iv.id: iv for iv in init_voices}
        timbres = []
        for v_idx in range(3):
            iv = iv_by_id.get(v_idx + 1)
            if iv and iv.instr:
                inst = instr_by_id[iv.instr.id]
                ctrl_byte = (iv.ctrl if ctrl_from_init
                             else (inst.waveform[0] if inst.waveform else 0))
                timbres.append((
                    inst.pwm.init & 0xFF,
                    (inst.pwm.init >> 8) & 0xFF,
                    ctrl_byte,
                    inst.adsr[0],
                    inst.adsr[1],
                ))
            else:
                timbres.append((0, 0, 0, 0, 0))
        per_subtune_voice_timbres.append(timbres)

    # Encode each subtune's per-voice pattern bytes — encoding depends
    # on the model's pattern shape (atomic vs pair vs cmd-stream vs
    # companion).
    per_subtune_voice_patterns: list[dict[int, bytes]] = []
    per_subtune_voice_init_states: list[list[int]] = []
    is_pair = (model.voice_timing.mode == 'tick_counter_decrement')
    is_cmd = (model.voice_timing.mode == 'dur_counter_decrement')
    is_companion = (model.voice_timing.mode == 'every_tick'
                    and model.tempo_dispatch.mode == 'two_phase')
    for ms in music:
        pat_dict: dict[int, bytes] = {}
        init_states = [0, 0, 0]
        sp = ms.params.fields if ms.params else {}
        for v in ms.voices:
            if is_pair:
                pb, st = _pair_voice_bytes_and_state(v)
                pat_dict[v.id - 1] = pb
                init_states[v.id - 1] = st
            elif is_cmd:
                pat_dict[v.id - 1] = _cmd_voice_bytes(v)
            elif is_companion:
                pad_count = sp.get(f'v{v.id}_pad_count', 0)
                pad_byte = sp.get(f'v{v.id}_pad_byte', 0)
                pat_dict[v.id - 1] = _companion_voice_bytes(
                    v, pad_count, pad_byte)
            else:
                pat_dict[v.id - 1] = _voice_pattern_bytes(
                    v, model.terminators.byte_map)
        per_subtune_voice_patterns.append(pat_dict)
        per_subtune_voice_init_states.append(init_states)

    asm = emit_asm(
        model, active,
        per_subtune_voice_timbres, per_subtune_voice_patterns,
        per_subtune_voice_init_states=(
            per_subtune_voice_init_states if is_pair else None))
    body = _assemble(asm)
    return _psid_header(model, n_subtunes=len(music), load=LOAD) + body
