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

_SUPPORTED_PATTERN_ENCODINGS = {'atomic_per_tick', 'note_dur_pair'}
_SUPPORTED_PITCH_FORMATS = {'octave_semi_nibble'}
_SUPPORTED_VOICE_TIMING = {'every_tick', 'tick_counter_decrement'}
_SUPPORTED_TEMPO_DISPATCH = {'single_phase'}
_SUPPORTED_MASTER_VOL = {'fixed_init', 'per_subtune_init'}

_SUPPORTED_TERMINATORS = {
    'note', 'rest_gate_off', 'skip',
    'master_vol_reset_and_loop',
    'loop_substitute_first',
    'loop_reset',
    'song_end_voice',
}

_SUPPORTED_INTER_VOICE_QUIRKS = {
    'carry_leak_4_vs_5_byte_timbre',
}


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
    if model.commands is not None: return False
    if model.state_layout is not None: return False
    if model.sfx is not None: return False
    if model.digi is not None: return False
    if model.hardcoded_pw_sweep is not None: return False
    if model.compound is not None: return False

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
        # Atomic-byte-per-tick: per-voice voice_step routines + shared
        # proc_note + RAM-mutable per-voice positions.
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

def emit_sid_from_usf(usf) -> bytes:
    from pipelines.engine_model import from_usf
    model = from_usf(usf)
    if not can_handle(model):
        raise NotImplementedError(
            'composer cannot handle this USF yet — fall through to legacy')

    active = _active_voice_indices(model, usf=usf)
    if not active:
        raise NotImplementedError('USF has no active voices')

    # Per-subtune, per-voice timbres. Each subtune carries its own
    # `init.voices` which references instruments — usually subtune-
    # specific (Melonmania's subtunes use different instruments).
    from src.usf import MusicSubtune
    music = sorted(
        (s for s in usf.subtunes if isinstance(s, MusicSubtune)),
        key=lambda s: s.id)
    instr_by_id = {i.id: i for i in usf.instruments}

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
                timbres.append((
                    inst.pwm.init & 0xFF,
                    (inst.pwm.init >> 8) & 0xFF,
                    inst.waveform[0] if inst.waveform else 0,
                    inst.adsr[0],
                    inst.adsr[1],
                ))
            else:
                timbres.append((0, 0, 0, 0, 0))
        per_subtune_voice_timbres.append(timbres)

    # Encode each subtune's per-voice pattern bytes + (for pair shape)
    # per-voice initial state bytes.
    per_subtune_voice_patterns: list[dict[int, bytes]] = []
    per_subtune_voice_init_states: list[list[int]] = []
    is_pair = (model.voice_timing.mode == 'tick_counter_decrement')
    for ms in music:
        pat_dict: dict[int, bytes] = {}
        init_states = [0, 0, 0]
        for v in ms.voices:
            if is_pair:
                pb, st = _pair_voice_bytes_and_state(v)
                pat_dict[v.id - 1] = pb
                init_states[v.id - 1] = st
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
