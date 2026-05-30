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
    InterVoiceQuirk, FadeProgressive,
    StateLayoutMirror, StateSlot, StatebufLayout, StatebufSlot,
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


# ---------------------------------------------------------------------------
# State-layout mirror — off-table arpeggio state buffer
# ---------------------------------------------------------------------------
#
# Pitch values ≥ 96 in some engines (Hubbard '85 family) read past the
# 96-entry musical freq table into engine state. The rebuild mirrors
# this by maintaining a 96-byte `statebuf` block whose bytes match the
# engine's runtime state at the off-table read offsets. The layout
# (which engine var lives at which statebuf offset) is captured as a
# `StateLayoutMirror` (a.k.a. `StatebufLayout` — same dataclass) on
# the engine model.
#
# This is one of the cleanest features in the Hubbard '85 codegen
# — already a function emitter that consumes a layout dataclass and
# returns asm. Phase 8.2 moved it from `composer_hubbard.py` into
# composer territory; the lifted code imports back from here.

# Commando's layout — the historic hand-written `build_statebuf` body.
# Action Biker, Devils Galop, Monty and Chimera all share this layout
# (they're the same engine family with the same state-region offsets).
COMMANDO_STATEBUF_LAYOUT = StatebufLayout(
    n_voices=3,
    scalars=[
        StatebufSlot(offset=3, kind='zp', var='sidoff'),
    ],
    per_voice=[
        StatebufSlot(offset=4,  kind='var',     var='v_seqidx'),
        StatebufSlot(offset=7,  kind='var',     var='v_hubidx'),
        StatebufSlot(offset=10, kind='var',     var='v_dur'),
        StatebufSlot(offset=13, kind='note_byte'),
        StatebufSlot(offset=16, kind='var',     var='v_ctrlbyte'),
        StatebufSlot(offset=19, kind='var',     var='v_pitch'),
        StatebufSlot(offset=22, kind='var_and', var='v_instr', mask=0x3f),
        StatebufSlot(offset=40, kind='var',     var='v_pwdir'),
    ],
)


def _emit_build_statebuf(layout: StatebufLayout) -> str:
    """Emit the `build_statebuf:` routine from a StatebufLayout.

    Saves X (the caller's voice index), runs the scalars once, then
    the per-voice loop with X = n_voices-1 down to 0, then restores X.
    """
    lines = ['build_statebuf:', '        txa', '        pha']
    for s in layout.scalars:
        if s.kind == 'const':
            lines.append(f'        lda #${s.value:02X}')
        elif s.kind == 'zp':
            lines.append(f'        lda {s.var}')
        else:
            raise ValueError(f'scalar slot kind {s.kind!r} not supported')
        lines.append(f'        sta statebuf+{s.offset}')

    if layout.per_voice:
        lines.append(f'        ldx #{layout.n_voices - 1}')
        lines.append('bsb1:')
        for s in layout.per_voice:
            if s.kind == 'var':
                lines.append(f'        lda {s.var},x')
                lines.append(f'        sta statebuf+{s.offset},x')
            elif s.kind == 'var_and':
                lines.append(f'        lda {s.var},x')
                lines.append(f'        and #${s.mask:02X}')
                lines.append(f'        sta statebuf+{s.offset},x')
            elif s.kind == 'note_byte':
                lines.append(f'        lda v_instr,x')
                lines.append(f'        and #$40')
                lines.append(f'        ora v_durfield,x')
                lines.append(f'        sta statebuf+{s.offset},x')
            else:
                raise ValueError(f'per-voice slot kind {s.kind!r} not supported')
        lines.append('        dex')
        lines.append('        bpl bsb1')

    lines += ['        pla', '        tax', '        rts']
    return '\n'.join(lines)


def _statebuf_init_bytes(layout: StatebufLayout) -> str:
    """The `statebuf:` data block — 96 bytes, with the per-voice
    sidoff constants seeded where Commando expects them ($00, $07,
    $0E for V1, V2, V3) and zeros for everything else. For engines
    with different scalar constants, those are reflected here."""
    bytes_ = [0] * 96
    bytes_[0] = 0
    bytes_[1] = 7
    if layout.n_voices >= 3:
        bytes_[2] = 14
    # Apply any const scalars from the layout.
    for s in layout.scalars:
        if s.kind == 'const' and s.offset < len(bytes_):
            bytes_[s.offset] = s.value
    return ','.join(str(b) for b in bytes_)


# ---------------------------------------------------------------------------
# Master-volume fade — progressive $D418 decrement on configured voice's
# pattern-end
# ---------------------------------------------------------------------------
#
# A handful of Hubbard '85 engines (TOAS family) decrement $D418 over
# the course of the song. The `vol_progress` counter increments on the
# configured voice's pattern-end (peek-ahead via v_notesleft); the
# engine writes `$D418 = clamp(base - vol_progress, 0..$0F)` on a
# trigger (either every note-start or only on instrument-change rows).
#
# The lifted ENGINE template has four sentinel comments where this
# feature substitutes asm fragments:
#   ; %%VOL_PROGRESS_INIT%%     init: zero the counter
#   ; %%VOL_PROGRESS_INC%%      load_note: peek-ahead increment
#   ; %%MASTER_VOL_WRITE%%      instrument-change write of $D418
#   ; %%MASTER_VOL_EVERY_NOTE%% every-note write of $D418
#
# Composer's emitter returns the four fragments as a dict (sentinel →
# asm). When `fade is None`, every fragment is the empty string —
# leaving the template unchanged for engines that don't use the fade.

_VOL_FADE_SENTINELS = (
    '; %%VOL_PROGRESS_INC%%',
    '; %%MASTER_VOL_WRITE%%',
    '; %%MASTER_VOL_EVERY_NOTE%%',
)


# ---------------------------------------------------------------------------
# Small sentinel-substitution feature emitters (Phase 8.4)
# ---------------------------------------------------------------------------
#
# Each of these features in the lifted Hubbard '85 ENGINE template is a
# tiny asm fragment substituted via a `; %%FEATURE%%` sentinel comment
# (or a direct text replacement for `arp_phase_invert`). The composer
# owns the emitters; composer_hubbard.py calls them during template
# substitution.

def _emit_ns_offtab_decr(decr_offset: int | None) -> str:
    """Off-table-note-start statebuf decrement (Thing on a Spring).

    The engine reads pattern-position state mid-load, while our note
    codec advances v_hubidx at end-of-load. To match, decrement the
    current voice's v_hubidx slot in statebuf by 1 before the freq
    read. The offset says which statebuf slot to decrement (the
    v_hubidx position in `StateLayoutMirror`).
    """
    if decr_offset is None:
        return ''
    return (
        f'        sec\n'
        f'        lda statebuf+{decr_offset},x\n'
        f'        sbc #1\n'
        f'        sta statebuf+{decr_offset},x'
    )


def _emit_incby2_late_gate(threshold: int | None,
                            per_subtune_zp_var: bool = False) -> str:
    """fx_incby2 late-gate: only fire when `v_dur < threshold`.

    Two variants:
      * compile-time constant (`threshold` is an int) — used by Hunter
        Patrol and similar.
      * per-subtune table read via `cur_incby2_late_gate` zp slot
        (5_Title_Tunes path).

    When neither applies (`threshold=None`, `per_subtune_zp_var=False`),
    returns the empty string — the engine's incby2 fx fires
    unconditionally on the configured frame phase.
    """
    if not per_subtune_zp_var and threshold is None:
        return ''
    cmp_line = ('        cmp cur_incby2_late_gate' if per_subtune_zp_var
                else f'        cmp #{threshold}')
    return (
        '        lda v_dur,x\n'
        f'{cmp_line}\n'
        '        bcs fxi_ret          ; v_dur >= late_gate -> skip'
    )


def _emit_clear_drumtrig(tie_preserves_slide: bool) -> dict[str, str]:
    """Position the `sta v_drumtrig,x` clear in `ln_decode`.

    Two placements possible (both emit the same 2 bytes so no address
    shifting):
      * unconditional (default) — pre-9828b37 behaviour. Works for
        Monty / Chimera / others.
      * only on the non-tie path — matches Confuzion / BoB's
        `BVS skip` over the v_slide clear.
    """
    clear = '        sta v_drumtrig,x'
    if tie_preserves_slide:
        return {
            '; %%CLEAR_DRUMTRIG_UNCOND%%': '',
            '; %%CLEAR_DRUMTRIG_NONTIE%%': clear,
        }
    return {
        '; %%CLEAR_DRUMTRIG_UNCOND%%': clear,
        '; %%CLEAR_DRUMTRIG_NONTIE%%': '',
    }


def _emit_ovseed_copy(has_per_subtune_ovseed: bool) -> str:
    """5_Title_Tunes per-subtune ovseed copy. Runs at the top of `init`
    before the iniov loop reads ovseed; copies the selected subtune's
    18-byte ovseed block into the `ovseed` data label so iniov sees
    the right per-voice state seed.

    Empty string when the engine doesn't use per-subtune ovseed
    (every Hubbard '85 engine outside 5TT).
    """
    if not has_per_subtune_ovseed:
        return ''
    return (
        '        ldy sub_tmp\n'
        '        lda subOvseedLo,y\n'
        '        sta sfx_rec\n'
        '        lda subOvseedHi,y\n'
        '        sta sfx_rec+1\n'
        '        ldy #17\n'
        'ovcopy: lda (sfx_rec),y\n'
        '        sta ovseed,y\n'
        '        dey\n'
        '        bpl ovcopy'
    )


def _fx_flags_byte(m) -> int:
    """Pack an InstrumentModel's modulation presence flags into the
    engine's fx_flags byte.

    Bit 0 = freq_slide (skydive), 1 = inc_by2 (odd-frame slide),
    2 = arpeggio (multi-step), 3 = vibrato, 4 = PWM (any mode).
    The engine reads `it_fx,inst` and ANDs against these bits to
    decide which fx routines to run for the playing note.
    """
    return ((1 if m.freq_slide else 0) | (2 if m.inc_by2 else 0)
            | (4 if m.arpeggio else 0) | (8 if m.vibrato else 0)
            | (16 if m.pwm else 0))


def _emit_hubbard_instrument_table(models) -> list[str]:
    """Hubbard '85's column-major instrument table.

    12 `it_*` tables, each indexed by instrument number. Row-major
    (`inst * 16`) would overflow the 8-bit index past 15 instruments
    (Monty has 20); column-major keeps every index within byte range.

    Fields (in `irow` order — only the indexed columns appear in the
    final emitted tables):
       0  init_ctrl                       → it_ctrl
       1,2  reserved (0, 0)
       3  init_ad                         → it_ad
       4  init_sr                         → it_sr
       5  hr_ctrl                         → it_hrctrl
       6  fx_flags byte                   → it_fx
       7  vibrato depth                   → it_vibdepth
       8  pwm mode (0=none,1=linear,2=bidir) → it_pwmode
       9  pwm `a` (speed for linear, step for bidir) → it_pwa
       10 pwm period (bidir only)         → it_pwperiod
       11,12 pwm lo/hi bounds (bidir)     → it_pwlo/it_pwhi
       13 vibrato onset_dur               → it_onset
    """
    irows = []
    for m in models:
        vib_depth = m.vibrato.depth if m.vibrato else 0
        vib_onset = m.vibrato.onset_dur if m.vibrato else 6
        pwm_mode = pwm_a = pwm_period = pwm_lo = pwm_hi = 0
        if m.pwm:
            if m.pwm.mode == 'linear':
                pwm_mode, pwm_a = 1, m.pwm.speed
            else:
                pwm_mode, pwm_a = 2, m.pwm.step
                pwm_period, pwm_lo, pwm_hi = (
                    m.pwm.period, m.pwm.lo_bound, m.pwm.hi_bound)
        irows.append([m.init_ctrl, 0, 0, m.init_ad, m.init_sr, m.hr_ctrl,
                      _fx_flags_byte(m), vib_depth, pwm_mode, pwm_a,
                      pwm_period, pwm_lo, pwm_hi, vib_onset])
    lines = []
    for idx, name in ((0, 'it_ctrl'), (3, 'it_ad'), (4, 'it_sr'),
                      (5, 'it_hrctrl'), (6, 'it_fx'), (7, 'it_vibdepth'),
                      (8, 'it_pwmode'), (9, 'it_pwa'), (10, 'it_pwperiod'),
                      (11, 'it_pwlo'), (12, 'it_pwhi'), (13, 'it_onset')):
        lines.append(f'{name}: .byt ' +
                     ','.join(f'${r[idx]:02X}' for r in irows))
    return lines


def _emit_hubbard_pwseed_pwacc(models) -> list[str]:
    """Per-instrument PW seed + live accumulator.

    `pwseed`: the load-time pw_lo / pw_hi for each instrument.
    `pwacc`: same shape, zero-initialized at link time — init copies
    `pwseed → pwacc` so each subtune starts the PWM accumulators
    fresh. The PWM fx routines read/write `pwacc`.
    """
    lines = ['pwseed:']
    for m in models:
        lines.append(f'        .byt ${m.init_pw_lo:02X},${m.init_pw_hi:02X}')
    lines.append('pwacc: .byt ' + ','.join(['0'] * (2 * len(models))))
    return lines


# Default seed offsets — Commando family's per-voice state-overlap
# positions within the freq table region. Hunter Patrol overrides
# `v_slide` to 238 (one byte earlier); other engines stay on these
# defaults.
_DEFAULT_SEED_OFFSETS = {
    'v_ctrl':     208,
    'pwm_period': 229,
    'pwm_dir':    232,
    'v_instr':    214,
    'v_durfield': 205,
    'v_slide':    239,
}


def _emit_hubbard_ovseed(freq_bytes: bytes,
                          seed_overlap: bool,
                          seed_offsets: dict | None = None) -> list[str]:
    """Overlap seed — 18 bytes of per-voice initial state.

    The engine's six per-voice state variables (`v_ctrl`,
    `pwm_period`, `pwm_dir`, `v_instr`, `v_durfield`, `v_slide`)
    live PAST the 96-entry musical freq table, in the overlap
    region. `init` copies these load-time bytes into zero-page
    mirrors so an off-table read or first counter DEC sees the
    right value.

    `seed_overlap=False` zeros the seed (Human Race inits per-voice
    state at runtime via its `$1A9C` init — no load-time overlap).
    """
    if seed_overlap:
        so = seed_offsets or _DEFAULT_SEED_OFFSETS
        ov = (
            [freq_bytes[so['v_ctrl']     + i] for i in range(3)]
            + [freq_bytes[so['pwm_period'] + i] for i in range(3)]
            + [freq_bytes[so['pwm_dir']    + i] for i in range(3)]
            + [freq_bytes[so['v_instr']    + i] for i in range(3)]
            + [freq_bytes[so['v_durfield'] + i] for i in range(3)]
            + [freq_bytes[so['v_slide']    + i] for i in range(3)]
        )
    else:
        ov = [0] * 18
    return ['ovseed: .byt ' + ','.join(f'${b:02X}' for b in ov)]


# ---------------------------------------------------------------------------
# Hubbard '85 fx routine asm chunks
# ---------------------------------------------------------------------------
#
# Each fx routine is a labeled subroutine in the ENGINE template. The
# Phase 8.2-8.8 work moved sentinel substitutions + data emitters into
# composer; Phase 8.9+ starts extracting the inline routines.
#
# Each routine becomes a string constant that the ENGINE template
# substitutes via a `; %%FX_<NAME>%%` sentinel. The byte stream is
# unchanged (same asm text, just sourced from composer); the
# extraction sets up future parameterization (e.g. emit fx_drumslide
# only when at least one instrument carries the drum_trig per-note
# fx flag).

_HUBBARD_FX_DRUMSLIDE_ASM = """; fx_drumslide - per-note portamento ($52B3-$52F9), effect #3. A note
; carrying a drum/porta trigger slides the running freq (v_slidelo /
; v_slide = $551D/$551A) by delta=trig&$7E each frame, dir=trig&$01.
; bit7 of the trigger is no_release - mask it off before the run test.
fx_drumslide:
        lda v_drumtrig,x
        and #$7f
        beq fxd_ret
        and #$7e             ; delta
        sta pwm_tmp
        lda v_drumtrig,x
        and #$01
        bne fxd_down
        lda v_slidelo,x      ; slide up
        clc
        adc pwm_tmp
        sta v_slidelo,x
        lda v_slide,x
        adc #$00
        sta v_slide,x
        jmp fxd_wr
fxd_down:
        lda v_slidelo,x      ; slide down
        sec
        sbc pwm_tmp
        sta v_slidelo,x
        lda v_slide,x
        sbc #$00
        sta v_slide,x
fxd_wr:
        ldy sidoff
        lda v_slidelo,x
        sta $d400,y          ; freq_lo
        lda v_slide,x
        sta $d401,y          ; freq_hi
fxd_ret: rts"""


def _emit_hubbard_fx_drumslide() -> str:
    """fx_drumslide routine — per-note portamento (effect #3).

    A note carrying a drum/porta trigger slides the running freq each
    frame by delta = trig & $7E, dir = trig & $01. bit-7 of the
    trigger is no_release (masked off before the run test).

    Today: always emitted (the ENGINE template's `do_effects:` chain
    unconditionally calls `jsr fx_drumslide`). Future: emit only when
    any instrument uses drum_trig.
    """
    return _HUBBARD_FX_DRUMSLIDE_ASM


_HUBBARD_FX_INCBY2_ASM = """; fx_incby2 - bit1. odd-frame slide on v_slide, write OLD value then
; step. The optional %%INCBY2_LATE_GATE%% sentinel below is replaced
; at codegen time with a `v_dur >= N -> skip` check for engines like
; Hunter Patrol whose skydive only fires in the tail of long notes.
fx_incby2:
        ldy instoff
        lda it_fx,y
        and #$02
        beq fxi_ret
        lda v_durfield,x
        cmp #INCBY2_ONSET
        bcc fxi_ret
; %%INCBY2_LATE_GATE%%
        lda frame_ctr
        and #$01
        ora #INCBY2_ALWAYS   ; 1 -> runs every frame
        beq fxi_ret
        lda v_slide,x
        beq fxi_ret
        ldy sidoff
        lda v_slide,x
        sta $d401,y          ; write OLD slide value
        lda v_slide,x
        clc
        adc #INCBY2_STEP
        sta v_slide,x
fxi_ret: rts"""


def _emit_hubbard_fx_incby2(incby2_late_gate: int | None = None,
                            uses_per_subtune_dispatch: bool = False) -> str:
    """fx_incby2 routine — fx-flag bit 1, odd-frame freq-hi slide.

    Engine reads `v_slide`, writes the OLD value to freq_hi, then
    steps it by `INCBY2_STEP` (xa65 equate). Gated by `v_durfield >=
    INCBY2_ONSET` and either odd-frame parity OR `INCBY2_ALWAYS`
    (Human Race).

    Two cross-cutting knobs resolved here:
      - `incby2_late_gate`: optional `v_dur < N` late-gate (Hunter
        Patrol) injected at the `; %%INCBY2_LATE_GATE%%` sentinel.
      - `uses_per_subtune_dispatch`: 5_Title_Tunes path. When True,
        the late-gate reads from the `cur_incby2_late_gate` zp slot
        (per-subtune table) and the step ADC reads from
        `cur_incby2_step` instead of the compile-time `INCBY2_STEP`
        equate.
    """
    asm = _HUBBARD_FX_INCBY2_ASM
    if uses_per_subtune_dispatch:
        asm = asm.replace('; %%INCBY2_LATE_GATE%%',
                          _emit_incby2_late_gate(None, per_subtune_zp_var=True))
        asm = asm.replace('        adc #INCBY2_STEP',
                          '        adc cur_incby2_step')
    else:
        asm = asm.replace('; %%INCBY2_LATE_GATE%%',
                          _emit_incby2_late_gate(incby2_late_gate))
    return asm


_HUBBARD_FX_PWM_ASM = """; fx_pwm - bit4. linear or bidirectional PWM. The pw accumulators
; (pwacc) are per-instrument shared state - see song_interp._pwm.
fx_pwm:
        ldy instoff
        lda it_pwmode,y      ; pwm_mode  0=none 1=linear 2=bidir
        bne fxp_on
        rts
fxp_on:
        cmp #$01
        bne fxp_bidir
        ldy instoff
        lda it_pwa,y      ; linear - pw_lo += speed + vib_carry
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        clc
        adc pwm_tmp
        clc
        adc vib_carry
        ora #LINEAR_PW_OR
        sta pwacc,y
        ldy sidoff
        sta $d402,y
        rts
fxp_bidir:
        dec v_pwperiod,x
        bpl fxp_ret          ; period counter not expired
        ldy instoff
        lda it_pwperiod,y     ; reload period
        sta v_pwperiod,x
        lda v_pwdir,x
        bne fxp_fall
        ldy instoff          ; rising
        lda it_pwa,y      ; step
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        clc
        adc pwm_tmp
        sta pwacc,y
        lda pwacc+1,y
        adc #$00
        and #$0f
        sta pwacc+1,y
        ldy instoff
        cmp it_pwhi,y     ; hi_bound
        bne fxp_wr
        lda #$01
        sta v_pwdir,x
        jmp fxp_wr
fxp_fall:
        ldy instoff
        lda it_pwa,y      ; step
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        sec
        sbc pwm_tmp
        sta pwacc,y
        lda pwacc+1,y
        sbc #$00
        and #$0f
        sta pwacc+1,y
        ldy instoff
        cmp it_pwlo,y     ; lo_bound
        bne fxp_wr
        lda #$00
        sta v_pwdir,x
fxp_wr:
        ldy pw_idx
        lda pwacc+1,y
        sta pwm_tmp
        lda pwacc,y
        sta pwm_tmp+1
        ldy sidoff
        lda pwm_tmp
        sta $d403,y          ; pw_hi
        lda pwm_tmp+1
        sta $d402,y          ; pw_lo
fxp_ret:
        rts"""


def _emit_hubbard_fx_pwm() -> str:
    """fx_pwm routine — fx-flag bit 4. Linear (pw_lo += speed +
    vib_carry) or bidirectional (period-counter + step + bounds)
    PWM. PWM accumulators in `pwacc` are per-instrument shared
    state."""
    return _HUBBARD_FX_PWM_ASM


_HUBBARD_FX_VIBRATO_ASM = """; fx_vibrato - bit3. triangle LFO on freq, disassembly $51C1-$522D.
; leaves vib_carry = the 6502 carry the section hands to the PWM add.
fx_vibrato:
        ldy instoff
        lda it_fx,y
        and #$08
        bne fxv_go
        rts
fxv_go:
        lda frame_ctr
        and #$07
        cmp #$04
        bcc fxv_s1
        eor #$07
fxv_s1: sta vib_step
        ldy instoff
        lda it_vibdepth,y      ; vib_depth
        sta vdepthctr
        jsr vib_loadfreq     ; vfreq = freq16[pitch], freq16[pitch+1]
        sec
        lda vfreq+2          ; freq16[pitch+1] - freq16[pitch]
        sbc vfreq+0
        sta vdelta_lo
        lda vfreq+3
        sbc vfreq+1          ; A = diff_hi
fxv_sh: lsr                  ; shift A,vdelta_lo right depth+1 times
        ror vdelta_lo
        dec vdepthctr
        bpl fxv_sh
        sta vdelta_hi
        lda vfreq+0          ; target = freq16[pitch]
        sta vtarg_lo
        lda vfreq+1
        sta vtarg_hi
        lda v_durfield,x
        ldy instoff
        cmp it_onset,y     ; onset_dur (per-instrument)
        bcc fxv_wr           ; dur < onset -> no add (carry left = 0)
        ldy vib_step
        beq fxv_wr           ; step 0 -> no add (carry left = 1)
fxv_add:
        clc
        lda vtarg_lo
        adc vdelta_lo
        sta vtarg_lo
        lda vtarg_hi
        adc vdelta_hi
        sta vtarg_hi
        dey
        bne fxv_add
fxv_wr:
        lda #0               ; capture carry-out for the PWM ADC
        adc #0
        sta vib_carry
        ldy sidoff
        lda vtarg_lo
        sta $d400,y
        lda vtarg_hi
        sta $d401,y
        rts

; vib_loadfreq - fill vfreq (4 bytes) with freq16[pitch] and
; freq16[pitch+1]. In-table pitches read the freq table; an off-table
; pitch (96 and up) reads the engine-state mirror - the original's
; vibrato overflows the 96-entry freq table the same way.
vib_loadfreq:
        lda v_pitch,x
        cmp #96
        bcs vlf_off
        asl
        tay
        lda freqtab+0,y
        sta vfreq+0
        lda freqtab+1,y
        sta vfreq+1
        lda freqtab+2,y
        sta vfreq+2
        lda freqtab+3,y
        sta vfreq+3
        rts
vlf_off:
        sec
        sbc #96
        asl                  ; (pitch-96)*2 = statebuf offset
        tay
        jsr build_statebuf
        lda statebuf+0,y
        sta vfreq+0
        lda statebuf+1,y
        sta vfreq+1
        lda statebuf+2,y
        sta vfreq+2
        lda statebuf+3,y
        sta vfreq+3
        rts"""


def _emit_hubbard_fx_vibrato() -> str:
    """fx_vibrato + vib_loadfreq routines — fx-flag bit 3, triangle
    LFO on freq. Includes the `vib_loadfreq` support routine that
    fills `vfreq` from freq table (or statebuf mirror for off-table
    pitches). Leaves `vib_carry` set so fx_pwm's linear-mode ADC
    picks up the carry-out from the vibrato addition."""
    return _HUBBARD_FX_VIBRATO_ASM


_HUBBARD_FX_SKYDIVE_ASM = """; fx_skydive - bit0. freq_hi slide + ctrl, see song_interp._skydive.
fx_skydive:
        ldy instoff
        lda it_fx,y
        and #$01
        beq fxs_ret
        lda v_dur,x
        beq fxs_ret          ; duration_ctr == 0
        lda v_slide,x
        beq fxs_ret          ; slide value dead
        ldy sidoff
        lda v_slide,x
        sta $d401,y          ; freq_hi = slide value
        lda v_tick,x
        beq fxs_ns
        ldy instoff
        lda it_hrctrl,y      ; not-start ctrl = hr_ctrl
        bne fxs_w
        lda #$80
fxs_w:  ldy sidoff
        sta $d404,y
        dec v_slide,x
        rts
fxs_ns: lda #$80             ; note-start subphase ctrl = $80
        ldy sidoff
        sta $d404,y
fxs_ret: rts"""


def _emit_hubbard_fx_skydive() -> str:
    """fx_skydive routine — fx-flag bit 0. freq_hi slide + ctrl
    write. Decrements `v_slide` each frame; the ctrl write
    re-asserts hr_ctrl (or $80 for first-tick) so the envelope holds
    while the slide drifts."""
    return _HUBBARD_FX_SKYDIVE_ASM


_HUBBARD_FX_ARP_ASM = """; fx_arp - bit2 arpeggio. alternate pitch / pitch+12 by frame parity.
; idx under 96 is a normal freq-table lookup. idx 96 and up is
; off-table - in the original the lookup overflows the 96-entry freq
; table into engine state; reproduced cleanly here via statebuf, a
; mirror of the $54E8.. state region assembled on demand.
fx_arp:
        ldy instoff
        lda it_fx,y
        and #$04
        beq fxa_ret
        lda frame_ctr
        and #ARP_MASK
        beq fxa_even
        lda v_pitch,x
        clc
        adc #ARP_OFS
        jmp fxa_idx
fxa_even:
        lda v_pitch,x
fxa_idx:
        cmp #96
        bcc fxa_in
        sec
        sbc #96
        cmp #48
        bcs fxa_ret          ; beyond the mirrored state - reads zero
        asl                  ; (idx-96)*2 = statebuf offset
        tay
        jsr build_statebuf
        lda statebuf+0,y     ; addr   -> freq_lo
        pha
        lda statebuf+1,y     ; addr+1 -> freq_hi
        ldy sidoff
        sta $d401,y          ; freq_hi written first
        pla
        sta $d400,y          ; then freq_lo
        rts
fxa_in:
        asl
        tay
        lda freqtab,y
        sta f_lo
        lda freqtab+1,y
        sta f_hi
        ldy sidoff
        lda f_hi
        sta $d401,y
        lda f_lo
        sta $d400,y
fxa_ret: rts"""


def _emit_hubbard_fx_arp(arp_phase_invert: bool = False) -> str:
    """fx_arp routine — fx-flag bit 2, multi-step arpeggio.

    Alternates `v_pitch` / `v_pitch + ARP_OFS` (ARP_OFS = engine
    knob, typically 12) by `frame_ctr & ARP_MASK` parity. Pitches
    >= 96 read off-table via `build_statebuf` (state mirror — Hubbard
    family's "off-table arpeggio" trick).

    `arp_phase_invert=True` flips the active phase from
    `frame_ctr & ARP_MASK == 0 → base` (the Commando family default)
    to `... == 0 → +ARP_OFS` (One Man and his Droid). Implemented by
    flipping the `beq fxa_even` branch sense.
    """
    if not arp_phase_invert:
        return _HUBBARD_FX_ARP_ASM
    return _HUBBARD_FX_ARP_ASM.replace('beq fxa_even', 'bne fxa_even', 1)


_HUBBARD_NOTE_START_ASM = """; note_start - new-note setup. Tie ($40) skips freq, slide, off-table.
; Full notes look up freq16[pitch]; pitch >= 96 reads the engine's
; state mirror via build_statebuf (see StatebufLayout). drum_prio
; suppresses voice 0 SID writes on the first frame.
note_start:
        ldy instoff
        lda it_ctrl,y
        sta i_ctrl
        lda it_ad,y
        sta i_ad
        lda it_sr,y
        sta i_sr
        ldy pw_idx
        lda pwacc,y
        sta i_pwlo
        lda pwacc+1,y
        sta i_pwhi
        lda v_instr,x
        and #$40
        beq ns_full
        ; tie - ctrl gated off, pw, ad, sr; no freq, no slide re-seed.
        lda i_ctrl
        sta v_ctrlbyte,x
        and #$fe
        bit drum_prio
        bpl ns_pwadsr        ; suppressed -> skip the write
        ldy sidoff
        sta $d404,y
        jmp ns_pwadsr
ns_full:
        ; freq - pitch >= 96 reads off-table into the engine state
        ; region. The shared `statebuf` mirrors the per-engine layout
        ; (see StatebufLayout); off-table notes read it the same way
        ; fx_arp does for the +12 / +24 octave cases.
        lda v_pitch,x
        cmp #96
        bcs ns_offtab
        asl
        tay
        lda freqtab,y
        sta f_lo
        lda freqtab+1,y
        sta f_hi
        jmp ns_havefreq
ns_offtab:
        sec
        sbc #96
        cmp #48
        bcs ns_offzero       ; pitch beyond the 48-byte mirrored state
        asl                  ; (pitch-96)*2 = statebuf offset
        tay
        jsr build_statebuf
        ; %%NS_OFFTAB_DECR%%
        lda statebuf+0,y
        sta f_lo
        lda statebuf+1,y
        sta f_hi
        jmp ns_havefreq
ns_offzero:
        lda #0
        sta f_lo
        sta f_hi
ns_havefreq:
        lda f_hi
        sta v_slide,x        ; seed the skydive/drum-slide freq_hi
        lda f_lo
        sta v_slidelo,x      ; seed the drum-slide freq_lo
        lda i_ctrl
        sta v_ctrlbyte,x     ; update ctrl_byte AFTER the off-table read
        bit drum_prio
        bpl ns_pwadsr        ; suppressed -> skip the writes
        ldy sidoff
        lda f_hi
        sta $d401,y
        lda f_lo
        sta $d400,y
        lda i_ctrl
        sta $d404,y
ns_pwadsr:
        bit drum_prio
        bpl ns_pwret         ; suppressed -> skip the writes
        ldy sidoff
        lda i_pwlo
        sta $d402,y
        lda i_pwhi
        sta $d403,y
        lda i_ad
        sta $d405,y
        lda i_sr
        sta $d406,y
ns_pwret:
        rts"""


def _emit_hubbard_note_start(ns_offtab_decr_offset: int | None = None) -> str:
    """note_start routine — the new-note SID-register writes.

    Loads `i_ctrl/i_ad/i_sr/i_pwlo/i_pwhi` from the instrument table,
    looks up the freq (or builds the off-table statebuf for pitches
    >= 96), seeds the slide registers, and writes the frequency / ctrl /
    pulsewidth / AD / SR registers to the SID — all gated by
    `drum_prio` so voice 0's first frame can be suppressed on engines
    that use it.

    `ns_offtab_decr_offset` resolves the nested
    `; %%NS_OFFTAB_DECR%%` sentinel — None = no decrement (default),
    int = statebuf slot to decrement (Thing on a Spring's pattern-
    position state mid-load adjustment).
    """
    return _HUBBARD_NOTE_START_ASM.replace(
        '; %%NS_OFFTAB_DECR%%',
        _emit_ns_offtab_decr(ns_offtab_decr_offset), 1)


_HUBBARD_HR_WRITES_ASM = """; hr_writes - hard-restart block, ctrl=hr_ctrl ad=0 sr=0.
hr_writes:
        ldy instoff
        lda it_hrctrl,y
        ldy sidoff
        sta $d404,y
        lda #0
        sta $d405,y
        sta $d406,y
        rts"""


def _emit_hubbard_hr_writes() -> str:
    """hr_writes routine — the per-note hard-restart writes.

    Writes `ctrl = it_hrctrl`, `ad = 0`, `sr = 0` to the voice's
    SID registers — the standard Hubbard '85 hard-restart sequence
    issued one frame before `note_start` runs for a new note.
    """
    return _HUBBARD_HR_WRITES_ASM


_HUBBARD_SET_PATPTR_ASM = """; set_patptr - advance to the pattern at v_orderpos in voice X's
; orderlist. Reads the orderlist byte, handles $FE (end-of-song)
; and $FF (wrap-to-loop-point); on a real pattern index, loads the
; address into v_patlo/v_pathi, reads the leading note-count byte,
; and resets the per-voice codec cursor.
set_patptr:
        lda orderLo,x
        sta orderp
        lda orderHi,x
        sta orderp+1
sp_read:
        ldy v_orderpos,x
        lda (orderp),y
        cmp #$fe
        bcc sp_have          ; below $FE - a real pattern index
        beq sp_stop          ; $FE - end of song
        lda orderLoop,x      ; $FF - wrap to the loop point
        sta v_orderpos,x
        jmp sp_read
sp_stop:
        lda #$ff
        ldy #FREEZE_ON_STOP
        bne sps_freeze
        ldy #STOP_IS_FILL
        bne sps_fill
        sta v_ended,x
        rts
sps_freeze:
        sta v_frozen,x
        rts
; sps_fill - the $FE stop_fill end. Writes STOP_FILL to every voice
; register PLUS filter cutoff lo/hi + res-routing ($D400-$D417, 24
; regs), matching Action Biker's $C2E1-$C2E7 `LDX #$17; STA $D400,X`
; loop. $D418 (master VOL) is left alone — the engine's loop stops
; at $D417. `LDX #imm` is 2 bytes regardless of value, so this change
; doesn't shift any other addresses.
sps_fill:
        stx sub_tmp
        ldx #23
        lda #STOP_FILL
sps_fl: sta $d400,x
        dex
        bpl sps_fl
        lda #$02
        sta end_phase
        lda #1
        sta pv_abort
        ldx sub_tmp
        lda #$ff
        sta v_ended,x
        rts
sp_have:
        tay                  ; Y = pattern index
        lda pataddr_lo,y
        sta v_patlo,x
        lda pataddr_hi,y
        sta v_pathi,x
        ; every pattern starts with a 1-byte note count - read it and
        ; step v_patptr past it, then reset the per-voice read cursor.
        lda v_patlo,x
        sta notep
        lda v_pathi,x
        sta notep+1
        ldy #0
        lda (notep),y
        sta v_notesleft,x
        inc v_patlo,x
        bne sp_nc
        inc v_pathi,x
sp_nc:
        lda #0
        sta v_bitcnt,x       ; codec cursor state
        sta v_hubidx,x       ; note_idx restarts at 0 in a new pattern
        rts"""


def _emit_hubbard_set_patptr() -> str:
    """set_patptr routine — orderlist dispatch + new-pattern setup.

    Walks the per-voice orderlist (handling $FE end-of-song with the
    freeze-vs-stop_fill flavor knobs, and $FF wrap-to-loop), then on
    a real pattern index loads the pattern address, reads the leading
    note-count byte, and resets the codec cursor.

    References the assembler `.alias` equates FREEZE_ON_STOP /
    STOP_IS_FILL / STOP_FILL (emitted at the top of the engine
    binary from `inputs.freeze_on_stop` / `inputs.stop_fill`).
    """
    return _HUBBARD_SET_PATPTR_ASM


_HUBBARD_NEXT_ORDERIDX_ASM = """; next_orderidx - the orderlist index the next pattern will occupy:
; v_orderpos+1, or orderLoop,x if that entry is the $FF terminator.
; Returns it in A. Preserves X.
next_orderidx:
        lda orderLo,x
        sta orderp
        lda orderHi,x
        sta orderp+1
        lda v_orderpos,x
        clc
        adc #1
        tay                  ; Y = v_orderpos + 1
        lda (orderp),y
        cmp #$fe
        bcc noi_have
        lda orderLoop,x      ; next entry is a terminator ($FE/$FF) - wrap
        rts
noi_have:
        tya
        rts"""


def _emit_hubbard_next_orderidx() -> str:
    """next_orderidx routine — peek at where the next pattern lives.

    Returns the orderlist index the next pattern will occupy:
    v_orderpos+1, or orderLoop,x if that entry is the $FF terminator.
    Used by master_vol_trigger=`every_note` engines that derive their
    fade phase from the upcoming orderlist position.
    """
    return _HUBBARD_NEXT_ORDERIDX_ASM


_HUBBARD_DO_EFFECTS_ASM = """; do_effects - effects in engine order vibrato,pwm,drumslide,skydive,arp.
do_effects:
        lda #0
        sta vib_carry
        jsr fx_vibrato
        jsr fx_pwm
        jsr fx_drumslide
        jsr fx_skydive
        jsr fx_incby2
        jmp fx_arp"""


def _emit_hubbard_do_effects() -> str:
    """do_effects orchestrator — fx chain in engine-canonical order.

    Calls fx_vibrato, fx_pwm, fx_drumslide, fx_skydive, fx_incby2
    in sequence, tail-calls fx_arp. The leading `vib_carry = 0`
    clears the cross-effect carry that fx_vibrato sets and fx_pwm
    consumes.
    """
    return _HUBBARD_DO_EFFECTS_ASM


_HUBBARD_INIT_ASM = """; init - A = subtune number. A under N_MUSIC is a music subtune; A
; N_MUSIC and up is a sound effect (A-N_MUSIC = the SFX index).
init:
        cmp #N_MUSIC
        bcc init_music
        sec
        sbc #N_MUSIC
        sta sfx_idx
        lda #$01
        sta is_sfx
        jmp init_sfx
init_music:
        sta sub_tmp          ; A = subtune
        lda #$00
        sta is_sfx
        lda #DRUM_PRIO_INIT  ; $178B drum-priority gate
        sta drum_prio
        lda sub_tmp
        asl                  ; subtune*2
        clc
        adc sub_tmp          ; subtune*3 = base index into the 9-entry
        tay                  ; per-subtune orderlist tables
        ldx #0
inisel: lda subOrderLo,y
        sta orderLo,x
        lda subOrderHi,y
        sta orderHi,x
        lda subOrderLoop,y
        sta orderLoop,x
        iny
        inx
        cpx #3
        bne inisel
        ldy sub_tmp          ; this subtune's tempo
        lda subResetspd,y
        sta cur_resetspd
        lda subVoiceStart,y  ; per-subtune voice-loop start
        sta voice_start
        ldx #PWLEN           ; re-seed the PWM accumulators from pwseed
inipw:  lda pwseed,x
        sta pwacc,x
        dex
        bpl inipw
        ldx #2
ini1:   lda #0
        sta v_dur,x
        sta v_pwdir,x
        sta v_pwperiod,x
        sta v_instr,x
        sta v_orderpos,x
        sta v_ended,x
        sta v_frozen,x
        jsr set_patptr       ; v_patptr,x = first pattern of orderlist X
        dex
        bpl ini1
        ; %%OVSEED_COPY%%    ; runtime copy of subOvseed_<sub> -> ovseed
        ldx #2               ; seed the freq-table-overlap variables
iniov:  lda ovseed,x
        sta v_ctrlbyte,x
        lda ovseed+3,x
        sta v_pwperiod,x
        lda ovseed+6,x
        sta v_pwdir,x
        lda ovseed+9,x
        sta v_instr,x
        lda ovseed+12,x
        sta v_durfield,x
        lda ovseed+15,x
        sta v_slide,x
        dex
        bpl iniov
        lda #0
        sta end_phase
        ; %%VOL_PROGRESS_INIT%%   ; engines with MASTER_VOL_FADE reset
                                  ; the vol_progress counter here; for
                                  ; other engines this expands to nothing
                                  ; so the binary doesn't grow (address-
                                  ; shifting changes broke Monty st 0 +
                                  ; SFX subtunes when this was emitted
                                  ; unconditionally).
        lda #SPEED_CTR_INIT
        sta speed_ctr
        lda #1
        sta first_frame
        lda #FRAME_CTR_INIT
        sta frame_ctr
        ldx #$18
ini2:   lda #0
        sta $d400,x
        dex
        bpl ini2
        lda #MASTER_VOL_INIT  ; $D418 init value — most engines write $0F
                              ; here, but engines with MASTER_VOL_FADE
                              ; leave it at $00 because the original
                              ; engine doesn't write $D418 until the
                              ; first instrument-change note.
        sta $d418
        rts"""


def _emit_hubbard_init(has_per_subtune_ovseed: bool = False,
                       has_master_vol_fade: bool = False,
                       uses_per_subtune_dispatch: bool = False) -> str:
    """init routine — engine entry.

    A=subtune selects music (A < N_MUSIC) vs SFX (A >= N_MUSIC, with
    A - N_MUSIC = SFX index). Music init re-seeds the per-subtune
    orderlist tables / tempo / voice_start / PWM accumulators / per-
    voice state, then primes the frame counter, master VOL, and SID
    registers.

    Three cross-cutting knobs resolved here:
      - `has_per_subtune_ovseed`: 5_Title_Tunes path. Injects the
        runtime ovseed-copy block at `; %%OVSEED_COPY%%` (selects
        the active sub's 18-byte ovseed → the ovseed data label).
      - `has_master_vol_fade`: when True, injects `sta vol_progress`
        at `; %%VOL_PROGRESS_INIT%%` to zero the fade counter at
        each subtune start.
      - `uses_per_subtune_dispatch`: 5_Title_Tunes path. When True,
        replaces the compile-time `lda #SPEED_CTR_INIT / sta speed_ctr`
        block with the per-subtune table-read variant (also loads
        cur_incby2_step + cur_incby2_late_gate from per-subtune
        tables).
    """
    asm = _HUBBARD_INIT_ASM
    asm = asm.replace('; %%OVSEED_COPY%%',
                      _emit_ovseed_copy(has_per_subtune_ovseed))
    asm = asm.replace('; %%VOL_PROGRESS_INIT%%',
                      '        sta vol_progress' if has_master_vol_fade else '')
    if uses_per_subtune_dispatch:
        asm = asm.replace(
            '        lda #SPEED_CTR_INIT\n        sta speed_ctr',
            '        ldy sub_tmp\n'
            '        lda subSpeedCtrInit,y\n'
            '        sta speed_ctr\n'
            '        lda subIncBy2Step,y\n'
            '        sta cur_incby2_step\n'
            '        lda subIncBy2LateGate,y\n'
            '        sta cur_incby2_late_gate')
    return asm


_HUBBARD_PLAY_ASM = """play:
        inc freqtab+253      ; mirror Hubbard's INC $5525 (the SFX
                             ; sweep can read this byte as a frequency)
        lda is_sfx
        beq pl_music
        jmp sfx_play
pl_music:
        lda end_phase
        beq pl_run
        cmp #$01
        bne pl_silent        ; end_phase 2 - song over, write nothing
        lda #$02             ; end_phase 1 - gate every voice off, once
        sta end_phase
        lda #$00
        sta $d404            ; V1 ctrl
        sta $d40b            ; V2 ctrl
        sta $d412            ; V3 ctrl
pl_silent:
        rts
pl_run:
        inc frame_ctr
        lda first_frame
        beq pl_nogate
        lda #0
        sta first_frame
        lda #FIRST_FRAME_GATE_OFF
        beq pl_nogate
        lda #0
        sta $d404
        sta $d40b
        sta $d412
pl_nogate:
        dec speed_ctr
        bpl notick
        lda cur_resetspd
        sta speed_ctr
        lda #1
        sta is_tick
        jmp voices
notick: lda #0
        sta is_tick
voices:
        lda #0
        sta pv_abort
        ldx voice_start
pvloop: jsr proc_voice
        lda pv_abort
        bne pl_done
        lda #$ff
        sta drum_prio
        dex
        bpl pvloop
        ; end-of-song - once all three voices have hit $FE, arm the
        ; one-shot gate-off for the next frame.
        lda v_ended+0
        and v_ended+1
        and v_ended+2
        beq pl_done
        lda end_phase
        bne pl_done
        lda #$01
        sta end_phase
pl_done:
        rts"""


def _emit_hubbard_play(sfx_framectr_ofs: int = 253) -> str:
    """play routine — the per-frame engine entry.

    Bumps `freqtab+sfx_framectr_ofs` (the SFX-readable frame counter
    — default 253 / Commando family; Monty and One Man and his Droid
    override to 250). Dispatches to the SFX path on SFX subtunes;
    otherwise runs the music end-of-song handler, increments
    `frame_ctr`, optionally gates voices off on the first frame,
    runs the speed counter, and drives the voice loop from
    `voice_start`.
    """
    if sfx_framectr_ofs == 253:
        return _HUBBARD_PLAY_ASM
    return _HUBBARD_PLAY_ASM.replace(
        'inc freqtab+253', f'inc freqtab+{sfx_framectr_ofs}', 1)


_HUBBARD_PROC_VOICE_ASM = """proc_voice:
        lda v_ended,x
        bne pv_endret        ; voice hit $FE - it no longer plays
        lda v_frozen,x
        bne pv_frozen        ; voice hit $FE under freeze_on_stop
        lda sidtab,x
        sta sidoff
        jsr calc_instoff
        lda is_tick
        beq pv_fx
        dec v_dur,x
        bpl pv_sus
        jsr load_note
        lda v_ended,x        ; load_note may have hit the $FE marker
        bne pv_endret
        lda v_frozen,x       ; load_note may have hit the $FE freeze
        bne pvf_abort
        jsr calc_instoff
        jmp note_start
pv_sus:
        inc v_tick,x
        lda v_dur,x
        bne pv_fx
        lda v_norel,x
        bne pv_fx            ; no_release - skip the hard restart
        jsr hr_writes
pv_fx:
        jmp do_effects
; a $FE-frozen voice. v_dur cycles as a signed byte; while it is
; negative the voice tries to advance, hits $FE and aborts the frame.
; otherwise it sustains, hard-restarts at zero-crossing and runs fx.
pv_frozen:
        lda sidtab,x
        sta sidoff
        jsr calc_instoff
        lda is_tick
        beq pvf_fx
        dec v_dur,x
        lda v_dur,x
        bmi pvf_abort
        inc v_tick,x
        lda v_dur,x
        bne pvf_fx
        lda v_norel,x
        bne pvf_fx
        jsr hr_writes
pvf_fx:
        jmp do_effects
pvf_abort:
        lda #1
        sta pv_abort
        rts
pv_endret:
        rts

calc_instoff:
        lda v_instr,x
        and #$3f
        sta instoff          ; instrument number (column-table index)
        asl
        sta pw_idx           ; inst*2  (index into pwacc)
        rts"""


def _emit_hubbard_proc_voice() -> str:
    """proc_voice routine — per-voice tick handler + calc_instoff.

    Bundled with `calc_instoff` (the 6-line instrument-offset helper
    that proc_voice calls multiple times — they belong together). On
    a tick, either advances the duration counter, loads the next note,
    or hard-restarts at zero-crossing; on a non-tick frame runs only
    the effect chain. Handles both the normal path and the
    freeze_on_stop $FE-frozen path.
    """
    return _HUBBARD_PROC_VOICE_ASM


_HUBBARD_INIT_SFX_ASM = """; init_sfx - set up sound effect sfx_idx. Builds the record pointer,
; patches the live freq-table bytes the sweep overflows into, and
; resets the sweep state.
init_sfx:
        lda #$00
        sta sfx_rec+1
        lda sfx_idx
        asl
        rol sfx_rec+1
        asl
        rol sfx_rec+1
        asl
        rol sfx_rec+1
        asl
        rol sfx_rec+1
        asl
        rol sfx_rec+1        ; sfx_idx*32 - A is the low byte
        clc
        adc #<sfxdata
        sta sfx_rec
        lda sfx_rec+1
        adc #>sfxdata
        sta sfx_rec+1
        lda #$80
        sta freqtab+241      ; the sweep reads $5519 here - mode byte $80
        lda sfx_idx
        sta freqtab+255      ; $5527 - the SFX index
        lda #$ff
        sta freqtab+256      ; $5528 - drum_enable
        ldy #14
        lda (sfx_rec),y      ; record 14 - sweep start index
        sta sfx_index
        lda #$00
        sta sfx_stepctr
        sta sfx_done
        sta sfx_started
        ldy #4
        lda (sfx_rec),y      ; record 4 - V1 ctrl, the live V1 gate
        sta sfx_v1gate
        ldy #11
        lda (sfx_rec),y      ; record 11 - V2 ctrl, the live V2 gate
        sta sfx_v2gate
        ldx #$18
isfxclr: lda #$00
        sta $d400,x
        dex
        bpl isfxclr
        lda #$0f
        sta $d418
        rts"""


def _emit_hubbard_init_sfx(sfx_state_ofs: int | None = None) -> str:
    """init_sfx routine — SFX dispatch entry.

    Computes the 32-byte SFX record address (`sfxdata + sfx_idx*32`),
    seeds the SFX state mirror in the freq-table off-table region,
    captures the live V1/V2 ctrl gates, clears the SID, and writes
    $0F to $D418.

    `sfx_state_ofs is None` (Commando family) → seeds the default
    +241 / +255 / +256 layout. `sfx_state_ofs=int` (Monty + One Man
    and his Droid) → relocates the 6-byte state block to
    freqtab[ofs..ofs+5] and uses the layout
    {disable, sfx_idx, $ff, sweep_idx, step_rate, end_idx}.
    """
    if sfx_state_ofs is None:
        return _HUBBARD_INIT_SFX_ASM
    old = ("        lda #$80\n"
           "        sta freqtab+241      ; the sweep reads $5519 here -"
           " mode byte $80\n"
           "        lda sfx_idx\n"
           "        sta freqtab+255      ; $5527 - the SFX index\n"
           "        lda #$ff\n"
           "        sta freqtab+256      ; $5528 - drum_enable\n"
           "        ldy #14\n"
           "        lda (sfx_rec),y      ; record 14 - sweep start index\n"
           "        sta sfx_index\n")
    new = ("        lda #$00\n"
           f"        sta freqtab+{sfx_state_ofs}        ; SFX-disable flag\n"
           "        lda sfx_idx\n"
           f"        sta freqtab+{sfx_state_ofs + 1}        ; SFX index\n"
           "        lda #$ff\n"
           f"        sta freqtab+{sfx_state_ofs + 2}        ; static byte\n"
           "        ldy #16\n"
           "        lda (sfx_rec),y      ; record 16 - step rate\n"
           f"        sta freqtab+{sfx_state_ofs + 4}        ; step counter\n"
           "        ldy #15\n"
           "        lda (sfx_rec),y      ; record 15 - end index\n"
           f"        sta freqtab+{sfx_state_ofs + 5}        ; end index\n"
           "        ldy #14\n"
           "        lda (sfx_rec),y      ; record 14 - sweep start index\n"
           "        sta sfx_index\n"
           f"        sta freqtab+{sfx_state_ofs + 3}        ; sweep index (initial)\n")
    return _HUBBARD_INIT_SFX_ASM.replace(old, new, 1)


_HUBBARD_SFX_PLAY_ASM = """; sfx_play - one frame of the sound-effect engine. The first frame
; gates the voices off and writes the 14-byte register snapshot;
; thereafter it steps the freq-table sweep.
sfx_play:
        lda sfx_started
        bne sfxp_run
        lda #$01
        sta sfx_started
        lda #$00
        sta $d404            ; play-path clear - gate V1,V2,V3 off
        sta $d40b
        sta $d412
        sta $d404            ; the trigger gates V1,V2 again
        sta $d40b
        ldy #$00
sfxp_cpy: lda (sfx_rec),y    ; records 0..13 - V1+V2 register snapshot
        sta $d400,y
        iny
        cpy #$0e
        bne sfxp_cpy
sfxp_run:
        lda sfx_done
        bne sfxp_ret
        dec sfx_stepctr
        bpl sfxp_ret
        ldy #16
        lda (sfx_rec),y      ; record 16 - step rate
        sta sfx_stepctr
        jsr sfx_step
sfxp_ret:
        rts"""


def _emit_hubbard_sfx_play() -> str:
    """sfx_play routine — per-frame SFX driver.

    On the first frame, gates V1/V2/V3 off then writes the 14-byte
    V1+V2 register snapshot from the SFX record. On subsequent
    frames, advances the step counter and invokes sfx_step when it
    rolls over to drive the pitch sweep.
    """
    return _HUBBARD_SFX_PLAY_ASM


_HUBBARD_SFX_STEP_ASM = """; sfx_step - one sweep step. Writes V1/V2 freq from the freq table and
; advances the index; ends the SFX when the index reaches the end.
sfx_step:
        ldy #15
        lda (sfx_rec),y      ; record 15 - end index
        cmp sfx_index
        bne sfxs_go
        lda #$00             ; reached the end - gate off, done
        sta $d404
        sta $d40b
        lda #$01
        sta sfx_done
        rts
sfxs_go:
        lda sfx_index
        asl
        sta sfx_y            ; sfx_y = (index*2) & $FF
        ldy #17
        lda (sfx_rec),y      ; record 17 - flags
        sta sfx_flags
        and #$04
        bne sfxs_gates       ; bit2 - skip both freq writes
        lda sfx_flags
        and #$02
        bne sfxs_v2          ; bit1 - skip the V1 freq write
        ldy sfx_y
        lda freqtab,y
        sta $d400
        lda freqtab+1,y
        sta $d401
sfxs_v2:
        ldy #18
        lda (sfx_rec),y      ; record 18 - V2 byte offset
        sta sfx_tmp
        lda sfx_y
        sec
        sbc sfx_tmp
        tay                  ; Y = (sfx_y - v2offset) & $FF
        lda freqtab,y
        sta $d407
        lda freqtab+1,y
        sta $d408
sfxs_gates:
        ldy #19
        lda (sfx_rec),y      ; record 19 - gate-toggle flags
        sta sfx_tmp
        and #$80
        beq sfxs_g2          ; bit7 - retrigger the V1 gate
        lda sfx_v1gate
        eor #$01
        sta sfx_v1gate
        sta $d404
sfxs_g2:
        lda sfx_tmp
        and #$40
        beq sfxs_adv         ; bit6 - retrigger the V2 gate
        lda sfx_v2gate
        eor #$01
        sta sfx_v2gate
        sta $d40b
sfxs_adv:
        lda sfx_flags
        and #$01
        beq sfxs_down        ; bit0 - 1 sweeps up, 0 sweeps down
        inc sfx_index
        rts
sfxs_down:
        dec sfx_index
        rts"""


def _emit_hubbard_sfx_step(sfx_state_ofs: int | None = None) -> str:
    """sfx_step routine — one pitch-sweep step.

    Reads V1+V2 freq from the freq table at the current sweep index
    (overflowing into engine-state-mirror bytes for off-table
    sweeps), retriggers V1/V2 gates per the per-step flags, and
    advances the sweep index up or down. When the index reaches the
    end marker, gates V1/V2 off and marks `sfx_done`.

    `sfx_state_ofs is None` (Commando family) → no mirror update.
    `sfx_state_ofs=int` → mirrors the post-update sweep index to
    `freqtab[ofs+3]` before the sweep reads it (so the overrun
    read sees the live value). Used by Monty + One Man and his
    Droid; the index mirror is injected at the top of `sfxs_go`.
    """
    if sfx_state_ofs is None:
        return _HUBBARD_SFX_STEP_ASM
    old = ("        lda (sfx_rec),y      ; record 17 - flags\n"
           "        sta sfx_flags\n"
           "        and #$04\n")
    new = ("        lda (sfx_rec),y      ; record 17 - flags\n"
           "        sta sfx_flags\n"
           "        and #$01\n"
           "        beq sfxm_dn\n"
           "        lda sfx_index\n"
           "        clc\n"
           "        adc #$01\n"
           "        jmp sfxm_st\n"
           "sfxm_dn:\n"
           "        lda sfx_index\n"
           "        sec\n"
           "        sbc #$01\n"
           "sfxm_st:\n"
           f"        sta freqtab+{sfx_state_ofs + 3}\n"
           "        lda sfx_flags\n"
           "        and #$04\n")
    return _HUBBARD_SFX_STEP_ASM.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Hubbard '85 engine asm composition — direct concatenation.
#
# The labelled routine chunks (init, play, proc_voice, set_patptr,
# next_orderidx, note_start, hr_writes, do_effects, fx_{drumslide,
# incby2, pwm, vibrato, skydive, arp}, build_statebuf, init_sfx,
# sfx_play, sfx_step) each live in their own `_HUBBARD_<NAME>_ASM`
# constant above. The composition function below concatenates them
# with the static framing (zp equates, entry stub, section banners,
# sidtab) to produce the engine asm body.
#
# Phases 8.9-8.14 lifted each chunk out of a substitution template;
# Phase 8.16 moved the template skeleton itself; Phase 8.17 replaced
# the template-driven path with direct chunk concatenation here.
# The remaining cross-chunk text-replace passes (sfx_framectr,
# arp_phase_invert, master_vol_fade, ...) still run as outer passes
# in composer_hubbard; later phases push them down.
# ---------------------------------------------------------------------------


_HUBBARD_ZP_EQUATES_ASM = r"""
frame_ctr = $40
speed_ctr = $41
is_tick   = $42
sidoff    = $43
v_dur     = $44
v_instr   = $47
v_pitch   = $4a
v_patlo   = $4d
v_pathi   = $50
v_orderpos = $53
orderp    = $56
notep     = $59
i_ctrl    = $5b
i_pwlo    = $5c
i_pwhi    = $5d
i_ad      = $5e
i_sr      = $5f
f_lo      = $60
f_hi      = $61
instoff   = $62
v_slide   = $63
v_tick    = $66
v_durfield = $69
vib_step  = $6c
vdelta_lo = $6d
vdelta_hi = $6e
vtarg_lo  = $6f
vtarg_hi  = $70
vdepthctr = $71
vib_carry = $72
pw_idx    = $73
v_pwdir   = $74
v_pwperiod = $77
pwm_tmp   = $7a
v_hubidx  = $7c
v_norel   = $7f
v_ctrlbyte = $82
v_drumtrig = $85
v_slidelo  = $88
v_seqidx   = $8b
vfreq      = $8e
v_ended    = $92
end_phase  = $95
cur_resetspd = $96
sub_tmp    = $97
is_sfx     = $98
sfx_idx    = $99
sfx_rec    = $9a
sfx_index  = $9c
sfx_stepctr = $9d
sfx_v1gate = $9e
sfx_v2gate = $9f
sfx_done   = $a0
sfx_started = $a1
sfx_y      = $a2
sfx_flags  = $a3
sfx_tmp    = $a4
v_notesleft = $a5
drum_prio   = $b2
pv_abort    = $b3
v_frozen    = $b4
voice_start = $b7
first_frame = $b8
; Master-volume fade counter — incremented on the configured voice's
; pattern-end (never wraps on song-loop). Read by the bit-7-style
; master VOL write on instrument-change notes:
;   $D418 = clamp(MASTER_VOL_BASE - vol_progress, 0..$0F)
; Only emitted when MASTER_VOL_FADE = 1.
vol_progress = $b9
; Per-subtune engine-param zp slots (used only when the codegen emits
; the per-subtune-params variant — see PER_SUBTUNE_ENGINE_PARAMS).
; `cur_incby2_step` is the slide step added per frame (8-bit signed:
; +2 = $02, -1 = $FF, etc.). `cur_incby2_late_gate` is the v_dur
; threshold below which the fx-bit-1 slide fires; $FF = "no gate".
cur_incby2_step  = $b9
cur_incby2_late_gate = $ba
"""


def _emit_hubbard_entry_stub(load_addr: int = LOAD) -> str:
    """Engine entry stub at `load_addr`. Two-instruction trampoline
    that PSID `init` / `play` vectors point at: JMP init / JMP play.

    The default `load_addr=$1000` matches the standalone build; the
    digi-aware combined build (`_emit_combined_sid`) and any future
    compound packer can place each sub-engine at a non-default
    address by passing `load_addr` through `_compose_hubbard_engine_asm`.
    """
    return (f'* = ${load_addr:04X}\n'
            f'        jmp init\n'
            f'        jmp play')


_HUBBARD_LOAD_NOTE_COMMENT = (
    "; load_note is supplied by the note codec (see note_codec.py) — the\n"
    "; engine calls it; the codec owns the pattern byte format and its\n"
    "; decoder. set_patptr / next_orderidx below are codec-agnostic.")


_HUBBARD_SET_PATPTR_HEADER = (
    "; set_patptr - point v_patptr,x at the pattern named by orderlist\n"
    "; entry v_orderpos,x. The $FF terminator wraps v_orderpos to\n"
    "; orderLoop,x; the $FE terminator ends the voice (v_ended). Clobbers\n"
    "; A and Y; preserves X.")


_HUBBARD_BUILD_STATEBUF_HEADER = (
    "; build_statebuf - assemble the off-table-arpeggio state mirror.\n"
    "; Generated per-engine from StatebufLayout (see codegen.py); the\n"
    "; concrete body is substituted in at codegen time.")


_HUBBARD_SFX_BANNER = (
    "; ============================ sound effects ===========================\n"
    "; A SFX is a 2-voice register snapshot plus a freq-table pitch sweep,\n"
    "; driven by a 32-byte record (sfxdata). See pipelines/hubbard/commando/extract/\n"
    "; sfx.py for the engine derivation.")


_HUBBARD_SIDTAB_ASM = "sidtab: .byt 0, 7, 14"


def _compose_hubbard_engine_body(
        state_layout: StatebufLayout,
        load_addr: int = LOAD,
        sfx_framectr_ofs: int = 253,
        arp_phase_invert: bool = False,
        ns_offtab_decr_offset: int | None = None,
        sfx_state_ofs: int | None = None,
        incby2_late_gate: int | None = None,
        has_per_subtune_ovseed: bool = False,
        has_master_vol_fade: bool = False,
        uses_per_subtune_dispatch: bool = False) -> str:
    """Compose the Hubbard '85 engine asm body by direct concatenation
    of named chunks — the composer-native replacement for template +
    `; %%SENTINEL%%` substitution.

    Output is the same text the old template-substitution path
    produced (modulo whitespace), but every chunk is positioned
    explicitly here rather than via sentinel placeholders.

    Per-engine variation enters here as explicit parameters:
      - `state_layout` — `build_statebuf` body (off-table arpeggio mirror)
      - `load_addr` — entry stub address (default $1000)
      - `sfx_framectr_ofs` — play's `inc freqtab+N` slot
      - `arp_phase_invert` — fx_arp branch polarity
      - `ns_offtab_decr_offset` — note_start statebuf decrement
      - `sfx_state_ofs` — init_sfx + sfx_step SFX-state relocation
      - `incby2_late_gate` — fx_incby2 `v_dur < N` late gate
      - `has_per_subtune_ovseed` — init's runtime ovseed copy
      - `has_master_vol_fade` — init's `sta vol_progress`
      - `uses_per_subtune_dispatch` — 5_Title_Tunes mechanism tables
        (init's SPEED_CTR_INIT block + fx_incby2's INCBY2_STEP add)

    The remaining cross-chunk passes (`; %%VOL_PROGRESS_INC%%` /
    `; %%MASTER_VOL_*%%` / `; %%CLEAR_DRUMTRIG_*%%`) all live in the
    codec's note_asm rather than the engine body, so they're handled
    by outer passes in `composer_hubbard._hubbard_emit_sid` until the
    codec itself migrates.
    """
    parts = [
        _HUBBARD_ZP_EQUATES_ASM,
        '',
        _emit_hubbard_entry_stub(load_addr),
        '',
        _emit_hubbard_init(has_per_subtune_ovseed=has_per_subtune_ovseed,
                           has_master_vol_fade=has_master_vol_fade,
                           uses_per_subtune_dispatch=uses_per_subtune_dispatch),
        '',
        _emit_hubbard_play(sfx_framectr_ofs),
        '',
        _emit_hubbard_proc_voice(),
        '',
        _HUBBARD_LOAD_NOTE_COMMENT,
        '',
        _HUBBARD_SET_PATPTR_HEADER,
        _emit_hubbard_set_patptr(),
        '',
        _emit_hubbard_next_orderidx(),
        '',
        _emit_hubbard_note_start(ns_offtab_decr_offset),
        '',
        _emit_hubbard_hr_writes(),
        '',
        _emit_hubbard_do_effects(),
        '',
        _emit_hubbard_fx_drumslide(),
        '',
        _emit_hubbard_fx_incby2(
            incby2_late_gate=incby2_late_gate,
            uses_per_subtune_dispatch=uses_per_subtune_dispatch),
        '',
        _emit_hubbard_fx_pwm(),
        '',
        _emit_hubbard_fx_vibrato(),
        '',
        _emit_hubbard_fx_skydive(),
        '',
        _emit_hubbard_fx_arp(arp_phase_invert),
        '',
        _HUBBARD_BUILD_STATEBUF_HEADER,
        _emit_build_statebuf(state_layout),
        '',
        _HUBBARD_SFX_BANNER,
        '',
        _emit_hubbard_init_sfx(sfx_state_ofs),
        '',
        _emit_hubbard_sfx_play(),
        '',
        _emit_hubbard_sfx_step(sfx_state_ofs),
        '',
        _HUBBARD_SIDTAB_ASM,
    ]
    return '\n'.join(parts)


def _emit_hubbard_asm_equates(inputs, codec) -> str:
    """Header equates derived from `_Inputs` + the note codec.

    These are the compile-time constants the engine asm references —
    sizes (PWLEN, N_MUSIC), engine knobs (ARP_OFS, ARP_MASK,
    LINEAR_PW_OR, INCBY2_*), behaviour flags (DRUM_PRIO_INIT,
    FREEZE_ON_STOP, FIRST_FRAME_GATE_OFF, STOP_IS_FILL, STOP_FILL),
    init values (FRAME_CTR_INIT, SPEED_CTR_INIT, MASTER_VOL_INIT)
    and the codec's bitfield widths (DUR_BITS, INST_BITS).
    """
    return (
        f'PWLEN = {2 * len(inputs.models) - 1}\n'
        f'N_MUSIC = {len(inputs.subtunes)}\n'
        f'FRAME_CTR_INIT = {inputs.frame_ctr_init}\n'
        f'HUBIDX_WRAP_AT_PATEND = {1 if inputs.hubidx_wrap_at_patend else 0}\n'
        f'ARP_OFS = {inputs.arp_interval}\n'
        f'ARP_MASK = {inputs.arp_period - 1}\n'
        f'LINEAR_PW_OR = {inputs.linear_pw_or}\n'
        f'INCBY2_STEP = {inputs.incby2_step & 0xFF}\n'
        f'INCBY2_ALWAYS = {1 if inputs.incby2_every_frame else 0}\n'
        f'INCBY2_ONSET = {inputs.incby2_onset}\n'
        f'DRUM_PRIO_INIT = {0 if inputs.suppress_first_notestart else 255}\n'
        f'DUR_BITS = {codec.dur_bits}\n'
        f'INST_BITS = {codec.inst_bits}\n'
        f'FREEZE_ON_STOP = {1 if inputs.freeze_on_stop else 0}\n'
        f'SPEED_CTR_INIT = {inputs.speed_ctr_init}\n'
        f'FIRST_FRAME_GATE_OFF = {1 if inputs.first_frame_gate_off else 0}\n'
        f'STOP_IS_FILL = {1 if inputs.stop_fill is not None else 0}\n'
        f'STOP_FILL = {inputs.stop_fill or 0}\n'
        f'MASTER_VOL_INIT = {0x00 if inputs.master_vol_subtrahend_voice is not None else 0x0F}\n'
    )


def _pattern_pool(scores):
    """Dense, globally-shared pattern pool. Returns (pat_order, pat_slot):
    pat_order[slot] = note list; pat_slot[orig pattern index] = slot.

    All N music subtunes share one global pool — pattern indices are
    re-numbered into a dense [0..M) range. Each unique pattern appears
    once in the emitted asm regardless of how many voices/subtunes
    reference it.
    """
    pat_order, pat_slot = [], {}
    for score in scores:
        for v in score.voices:
            for oidx in v.orderlist:
                if oidx not in pat_slot:
                    pat_slot[oidx] = len(pat_order)
                    pat_order.append(v.patterns.get(oidx, []))
    return pat_order, pat_slot


def _emit_hubbard_data(scores, models, freq_bytes, resetspds, voice_starts,
                       sfx_list, pat_slot, pat_bytes, codec_extra,
                       seed_overlap: bool = True,
                       state_layout: StatebufLayout = None,
                       seed_offsets=None,
                       per_subtune_speed_ctr_init=None,
                       per_subtune_incby2_step=None,
                       per_subtune_incby2_late_gate=None,
                       per_subtune_ovseed=None) -> str:
    """Emit the xa65 data section for a multi-subtune build.

    `scores` is one Score per packed music subtune; `sfx_list` is the
    16 sound effects; the pattern pool / orderlist / per-subtune
    tables (resetspd / voice_start / ovseed / mechanism overrides)
    are emitted in the order the engine init code reads them.
    Instruments, the freq table and the pattern pool are shared;
    orderlists, loop points and tempo are per-subtune, selected by
    `init` from the subOrder* / subResetspd tables.
    """
    if state_layout is None:
        state_layout = COMMANDO_STATEBUF_LAYOUT
    lines = []
    lines.extend(_emit_hubbard_instrument_table(models))
    lines.extend(_emit_hubbard_pwseed_pwacc(models))
    lines.extend(_emit_hubbard_freq_table_data(freq_bytes))
    lines.extend(_emit_hubbard_ovseed(freq_bytes, seed_overlap, seed_offsets))
    # patterns — each unique pattern emitted once; orderlists reference
    # them by a dense slot. Pattern indices are global, so the pool is
    # shared by all packed subtunes. The note codec serialises each
    # pattern (byte 0 = note count); the format is the codec's choice.
    lines.extend(_emit_hubbard_pattern_pool(pat_bytes, codec_extra))
    lines.extend(_emit_hubbard_orderlists(scores, pat_slot))
    lines.extend(_emit_hubbard_per_subtune_tables(
        scores, resetspds, voice_starts))
    lines.extend(_emit_hubbard_psp_tables(
        len(scores),
        per_subtune_speed_ctr_init,
        per_subtune_incby2_step,
        per_subtune_incby2_late_gate))
    lines.extend(_emit_hubbard_per_subtune_ovseed(per_subtune_ovseed))
    lines.extend(_emit_hubbard_live_order_arrays())
    lines.extend(_emit_hubbard_statebuf_data(state_layout))
    lines.extend(_emit_hubbard_sfx_records(sfx_list))
    return '\n'.join(lines)


def _resolve_codec_note_asm(codec, inputs) -> str:
    """Resolve the codec's note_asm sentinels from `_Inputs`.

    The codec emits its decoder as a class-level `note_asm` string
    that carries five `; %%<SENTINEL>%%` placeholders — three for
    the master-vol fade ($D418 write on instrument-change /
    every-note, and the peek-ahead vol_progress INC at last note of
    pattern) and two for tie_preserves_slide's drum-trig clear
    position. The codec itself doesn't know about these features —
    they're engine-level concerns — so the composer resolves them
    here when composing the engine asm.
    """
    asm = codec.note_asm
    fade = (
        FadeProgressive(
            subtrahend_voice_idx=inputs.master_vol_subtrahend_voice,
            base=inputs.master_vol_base,
            trigger=inputs.master_vol_trigger,
        )
        if inputs.master_vol_subtrahend_voice is not None else None)
    for sentinel, fragment in _emit_master_vol_fade(fade).items():
        asm = asm.replace(sentinel, fragment)
    for sentinel, fragment in _emit_clear_drumtrig(
            inputs.tie_preserves_slide).items():
        asm = asm.replace(sentinel, fragment)
    return asm


def _compose_hubbard_engine_asm(inputs, codec, pat_slot, pat_bytes,
                                codec_extra, load_addr: int = LOAD) -> str:
    """Compose the full Hubbard '85 engine asm — equates + codec zp +
    engine body + codec note-codec + data section.

    This is the composer-native replacement for the template +
    `_emit_data` pipeline that lived in
    `composer_hubbard._hubbard_emit_sid`. Returns FULLY-RESOLVED asm
    ready for xa65 — every sentinel and text-replace target is
    resolved by either the chunk emitters or `_resolve_codec_note_asm`.

    Per-engine variation is threaded into the body via explicit
    parameters drawn from `_Inputs`; the codec's note_asm sentinels
    are resolved by `_resolve_codec_note_asm` from the same `_Inputs`.
    """
    uses_psp = (
        inputs.per_subtune_speed_ctr_init is not None
        or inputs.per_subtune_incby2_step is not None
        or inputs.per_subtune_incby2_late_gate is not None)
    body = _compose_hubbard_engine_body(
        inputs.state_layout,
        load_addr=load_addr,
        sfx_framectr_ofs=inputs.sfx_framectr_ofs,
        arp_phase_invert=inputs.arp_phase_invert,
        ns_offtab_decr_offset=inputs.ns_offtab_decr_offset,
        sfx_state_ofs=inputs.sfx_state_ofs,
        incby2_late_gate=inputs.incby2_late_gate,
        has_per_subtune_ovseed=inputs.per_subtune_ovseed is not None,
        has_master_vol_fade=inputs.master_vol_subtrahend_voice is not None,
        uses_per_subtune_dispatch=uses_psp)
    data = _emit_hubbard_data(
        inputs.scores, inputs.models, inputs.freq_bytes,
        inputs.resetspds, inputs.voice_starts,
        inputs.sfx_list, pat_slot, pat_bytes, codec_extra,
        seed_overlap=inputs.seed_overlap,
        state_layout=inputs.state_layout,
        seed_offsets=inputs.seed_offsets,
        per_subtune_speed_ctr_init=inputs.per_subtune_speed_ctr_init,
        per_subtune_incby2_step=inputs.per_subtune_incby2_step,
        per_subtune_incby2_late_gate=inputs.per_subtune_incby2_late_gate,
        per_subtune_ovseed=inputs.per_subtune_ovseed)
    return (
        _emit_hubbard_asm_equates(inputs, codec)
        + codec.zp_asm + '\n'
        + body + '\n'
        + _resolve_codec_note_asm(codec, inputs) + '\n'
        + data + '\n'
    )


# ---------------------------------------------------------------------------
# Hubbard '85 _Inputs dataclass + USF / config adapters.
# Moved here from composer_hubbard.py in Phase 8.20 — these are the
# typed surface `_compose_hubbard_engine_asm` consumes; they belong
# next to the composition layer.
# ---------------------------------------------------------------------------

from dataclasses import dataclass as _dataclass, field as _field
from typing import Optional as _Optional


@_dataclass
class _Inputs:
    """Everything `_compose_hubbard_engine_asm` needs, decoupled from
    the source.

    `_inputs_from_usf` (the production path) builds this from a USF
    file alone — no engine-name lookup. `_inputs_from_config` is the
    legacy adapter for `EngineConfig` (binary-reading); used today by
    the 5_Title_Tunes unified-USF re-extractor. Both feed
    `_compose_hubbard_engine_asm` which is pure — it knows nothing
    about how the inputs were derived.
    """
    # PSID header metadata
    title: bytes              # exact 32-byte bytes (latin-1) for header
    author: bytes
    released: bytes
    start_song: int           # 1-indexed
    # Engine equates / asm flags
    arp_interval: int
    arp_period: int
    linear_pw_or: int
    incby2_step: int
    incby2_every_frame: bool
    incby2_onset: int
    suppress_first_notestart: bool
    freeze_on_stop: bool
    speed_ctr_init: int
    first_frame_gate_off: bool
    stop_fill: _Optional[int]
    sfx_framectr_ofs: int
    sfx_state_ofs: _Optional[int]
    has_sfx: bool
    # Per-engine data
    subtunes: tuple
    models: list                   # list[InstrumentModel]
    scores: list                   # list[Score]
    resetspds: list                # list[int]
    voice_starts: list             # list[int]
    freq_bytes: bytes              # 320 bytes
    sfx_list: list
    seed_overlap: bool = True
    psid_speed: int = 0       # PSID v2 speed bitmask (bit N = subtune N+1)
    state_layout: StatebufLayout = _field(default_factory=lambda: COMMANDO_STATEBUF_LAYOUT)
    seed_offsets: _Optional[dict] = None     # per-engine ovseed offsets
    frame_ctr_init: int = 0xFF                # initial zp frame_ctr
    incby2_late_gate: _Optional[int] = None   # fx_incby2 v_dur < N gate
    arp_phase_invert: bool = False            # swap base/+OFS sense in fx_arp
    # Engines whose off-table note-start reads pattern-position state
    # (Thing on a Spring) need the current voice's v_hubidx slot in
    # statebuf decremented by 1 to match the engine's v_patpos value
    # at the freq-read moment (which is BEFORE the post-pitch INC).
    # Offset = where v_hubidx lives in the engine's state_layout
    # (Commando default = 7).
    ns_offtab_decr_offset: _Optional[int] = None
    # Whether load_note resets v_hubidx to 0 at the last note of a
    # pattern. Default True (matches Commando family). Thing on a
    # Spring's engine doesn't reset v_patpos until the $C160 read,
    # which fires on the NEXT note-load frame.
    hubidx_wrap_at_patend: bool = True
    # Per-subtune engine-param overrides (5 Title Tunes unified path).
    # When any of these lists is set, the codegen emits per-subtune
    # tables (subSpeedCtrInit / subIncBy2Step / subIncBy2LateGate) and
    # the engine's init loads cur_incby2_step / cur_incby2_late_gate
    # zp slots from them. SPEED_CTR_INIT becomes a table read at init
    # time too. Use `incby2_late_gate=$FF` per sub to mean "no gate".
    # Each list MUST be len(subtunes); the value at index i applies
    # when subtune i plays. When all three are None, the codegen
    # emits the existing compile-time-constant code (no change).
    per_subtune_speed_ctr_init: _Optional[list] = None
    per_subtune_incby2_step: _Optional[list] = None
    per_subtune_incby2_late_gate: _Optional[list] = None
    # Per-subtune ovseed: each entry is 18 bytes — the 6 freq-table-
    # overlap state vars × 3 voices, in v_ctrl/pwm_period/pwm_dir/
    # v_instr/v_durfield/v_slide order. When set, init copies the
    # selected sub's bytes into the `ovseed` data block before the
    # iniov loop. Used by unified-engine builds (5 Title Tunes) where
    # each sub's per-voice load-time state differs.
    per_subtune_ovseed: _Optional[list] = None
    # Master-volume fade — see EngineConfig.master_vol_subtrahend_voice.
    # When set (0/1/2), codegen maintains a vol_progress counter that
    # increments on the named voice's pattern-end (never wraps) and
    # writes $D418 = clamp(master_vol_base - counter, 0..$0F) on every
    # instrument-change note. None disables.
    master_vol_subtrahend_voice: _Optional[int] = None
    master_vol_base: int = 0xA0
    master_vol_trigger: str = 'inst_change'
    tie_preserves_slide: bool = False


def _inputs_from_config(config) -> _Inputs:
    """Build inputs from a legacy `EngineConfig` (reads the binary).

    Used today only by the 5_Title_Tunes unified-USF re-extractor.
    The production build path is USF → `_inputs_from_usf` → asm.
    """
    from src.hubbard_emu import load_sid
    from pipelines.hubbard.inst_generalize import decode_all
    _, binary, load = load_sid(config.sid_path)
    models = decode_all(config.sid_path, config.instr_base,
                        config.instr_count, config.arp_interval,
                        config.vib_onset, config.arp_period)
    scores = [config.extract(subtune=s).score for s in config.subtunes]
    resetspds = [config.resetspd(s, binary, load) for s in config.subtunes]
    voice_starts = [config.voice_starts[s] if config.voice_starts else 2
                    for s in config.subtunes]
    freq_bytes = bytes(binary[config.freq_table_base - load + i]
                       for i in range(320))
    sfx_list = config.extract_sfx(config.sid_path)[0] if config.has_sfx else []

    with open(config.sid_path, 'rb') as f:
        orig_hdr = f.read(124)

    psid_speed = int.from_bytes(orig_hdr[0x12:0x16], 'big')

    return _Inputs(
        title=orig_hdr[22:54],
        author=orig_hdr[54:86],
        released=orig_hdr[86:118],
        start_song=(orig_hdr[0x10] << 8) | orig_hdr[0x11],
        psid_speed=psid_speed,
        arp_interval=config.arp_interval,
        arp_period=config.arp_period,
        arp_phase_invert=config.arp_phase_invert,
        linear_pw_or=config.linear_pw_or,
        incby2_step=config.incby2_step,
        incby2_every_frame=config.incby2_every_frame,
        incby2_onset=config.incby2_onset,
        suppress_first_notestart=config.suppress_first_notestart,
        freeze_on_stop=config.freeze_on_stop,
        speed_ctr_init=config.speed_ctr_init,
        first_frame_gate_off=config.first_frame_gate_off,
        stop_fill=config.stop_fill,
        sfx_framectr_ofs=config.sfx_framectr_ofs,
        sfx_state_ofs=config.sfx_state_ofs,
        has_sfx=config.has_sfx,
        seed_overlap=config.seed_overlap,
        frame_ctr_init=config.frame_ctr_init,
        incby2_late_gate=config.incby2_late_gate,
        subtunes=config.subtunes,
        models=models, scores=scores, resetspds=resetspds,
        voice_starts=voice_starts, freq_bytes=freq_bytes,
        sfx_list=sfx_list,
        master_vol_subtrahend_voice=config.master_vol_subtrahend_voice,
        master_vol_base=config.master_vol_base,
        master_vol_trigger=config.master_vol_trigger,
        tie_preserves_slide=config.tie_preserves_slide,
    )


# ---------------------------------------------------------------------------
# USF → domain converters (USF → InstrumentModel / Score / SoundEffect)
# ---------------------------------------------------------------------------

_NOTE_TO_NUM = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

# A pitch byte the engine treats as "no fresh note." Hubbard '85 uses
# values past the 96-entry musical freq table as off-table / rest. We
# use a sentinel that's safely past 95 and won't collide with arpeggio
# extensions.
_REST_PITCH = 0xFF


def _pitch_to_engine(p) -> int:
    if p.is_rest:
        return _REST_PITCH
    semis = _NOTE_TO_NUM[p.name] + 12 * p.octave
    return semis


def _instr_to_engine_byte(instr_ref, current_instr: int) -> int:
    """Convert a USF NoteRow's `instr` field back to the engine's
    per-note instrument byte. When no ref is present, set the high bit
    ('do not load new instrument'). When a ref is present, emit the
    instrument's 0-indexed id with high bit clear."""
    if instr_ref is None:
        return current_instr | 0x80
    # USF is 1-indexed; engine is 0-indexed.
    return (instr_ref.id - 1) & 0x3F


def _flags_to_engine(fx_flags: tuple) -> tuple[bool, int]:
    """Translate USF fx flag tokens back to (tie_bool, drum_trig_byte).

    Inverse of `to_usf._row_from_note`:
      tie         <- 'tie' token
      drum_trig   <- (0x80 if 'no_release') | porta_amount
    """
    tie = 'tie' in fx_flags
    drum_trig = 0x80 if 'no_release' in fx_flags else 0
    for flag in fx_flags:
        if flag.startswith('porta='):
            drum_trig |= int(flag[len('porta='):]) & 0x7F
    return tie, drum_trig


def _model_from_usf_instrument(u, vib_onset: int):
    """USF Instrument → engine InstrumentModel (the inverse of
    pipelines/hubbard/chimera/extract/to_usf._convert_instrument)."""
    from pipelines.hubbard.inst_generalize import (
        InstrumentModel, ArpSpec, VibratoSpec, PwmSpec,
    )

    init_ctrl = u.waveform[0] if u.waveform else 0
    init_pw_lo = u.pwm.init & 0xFF
    init_pw_hi = (u.pwm.init >> 8) & 0xFF

    pwm = None
    pw_lo_kind = 'const'
    pw_hi_kind = 'const'
    if u.pwm.mode == 'linear':
        pwm = PwmSpec(mode='linear', speed=u.pwm.speed,
                      seed_lo=init_pw_lo, seed_hi=init_pw_hi,
                      lo_bound=u.pwm.min_hi, hi_bound=u.pwm.max_hi)
        pw_lo_kind = 'accumulator'
    elif u.pwm.mode == 'bidirectional':
        pwm = PwmSpec(mode='bidirectional',
                      period=u.pwm.speed & 0x1F,
                      step=u.pwm.speed & 0xE0,
                      seed_lo=init_pw_lo, seed_hi=init_pw_hi,
                      lo_bound=u.pwm.min_hi, hi_bound=u.pwm.max_hi)
        pw_lo_kind = pw_hi_kind = 'accumulator'

    # Arpeggio: USF stores [0] when off, full offsets list when on.
    has_arp = len(u.arp.offsets) > 1
    arpeggio = (ArpSpec(intervals=tuple(u.arp.offsets), step_every=1)
                if has_arp else None)

    vibrato = (VibratoSpec(depth=u.vibrato.scale, onset_dur=vib_onset)
               if u.vibrato.scale != 0 else None)

    # Reconstruct the engine's fx_flags byte from the structured fields.
    fx_flags = ((1 if u.freq_slide else 0)
                | (2 if u.inc_by2 else 0)
                | (4 if has_arp else 0)
                | (8 if u.pwm.mode == 'linear' else 0))

    return InstrumentModel(
        inst=u.id - 1,                              # back to 0-indexed
        init_ctrl=init_ctrl,
        init_pw_lo=init_pw_lo,
        init_pw_hi=init_pw_hi,
        init_ad=u.adsr[0],
        init_sr=u.adsr[1],
        hr_ctrl=init_ctrl & 0xFE,
        pw_lo_kind=pw_lo_kind, pw_hi_kind=pw_hi_kind,
        fx_flags=fx_flags,
        freq_slide=u.freq_slide, inc_by2=u.inc_by2,
        arpeggio=arpeggio, vibrato=vibrato, pwm=pwm,
    )


def _score_from_subtune(sub):
    """USF MusicSubtune → engine Score (the inverse of `to_usf`'s
    per-subtune voice/pattern conversion)."""
    from pipelines.hubbard.types import Score, Voice, Note
    voices = []
    for vb in sub.voices:
        orderlist = list(vb.orderlist.entries)
        loop = vb.orderlist.loop_to if vb.orderlist.loop_to is not None else -1
        stop = vb.orderlist.stop
        patterns = {}
        for pat in vb.patterns:
            current_instr = 0
            notes = []
            for row in pat.rows:
                if row.instr is not None:
                    current_instr = row.instr.id - 1
                inst_byte = _instr_to_engine_byte(row.instr, current_instr)
                tie, drum = _flags_to_engine(row.fx_flags)
                notes.append(Note(
                    pitch=_pitch_to_engine(row.pitch),
                    duration=row.duration,
                    instrument=inst_byte,
                    tie=tie,
                    drum_trig=drum,
                ))
            patterns[pat.id] = notes
        voices.append(Voice(orderlist=orderlist, patterns=patterns,
                            loop=loop, stop=stop))
    return Score(tempo=sub.tempo, voices=voices)


def _soundeffect_from_usf(s, idx: int):
    """USF SfxSubtune → engine SoundEffect (the inverse of
    `_convert_sfx` in to_usf.py). Reassembles the 7-byte v1/v2 voice
    register lists; the freq_lo byte is re-derived from start_index /
    gate-flags-plus-offset."""
    from pipelines.hubbard.sfx import SoundEffect
    # Reconstruct the engine's gate byte at v2[0] — bit 7 toggle_v1,
    # bit 6 toggle_v2, bits 0-5 v2_offset. This matches `decode_sfx`'s
    # forward decomposition in pipelines/hubbard/sfx.py.
    gate_byte = ((0x80 if s.toggle_v1 else 0)
                 | (0x40 if s.toggle_v2 else 0)
                 | (s.v2_offset & 0x3F))
    v1_full = [s.start_index] + list(s.v1)         # 7 bytes
    v2_full = [gate_byte] + list(s.v2)             # 7 bytes
    return SoundEffect(
        index=idx,
        v1=v1_full,
        v2=v2_full,
        start_index=s.start_index,
        end_index=s.end_index,
        rate=s.rate,
        direction=s.direction,
        skip_v1=s.skip_v1,
        skip_both=s.skip_both,
        v2_byte_offset=s.v2_offset,
        toggle_v1=s.toggle_v1,
        toggle_v2=s.toggle_v2,
    )


def _ovseed_from_init_state(init, instr_count: int) -> bytes:
    """USF `InitState` → 18-byte ovseed (the inverse of
    `_init_state_from_ovseed` in
    pipelines/hubbard/five_title_tunes/unified/write_unified_usf.py).
    Layout: v_ctrl[3] pwm_period[3] pwm_dir[3] v_instr[3]
            v_durfield[3] v_slide[3]."""
    if init is None or not init.voices:
        return bytes(18)
    ovseed = bytearray(18)
    for v in init.voices:
        i = v.id - 1
        if not 0 <= i < 3:
            continue
        ovseed[0 + i] = v.ctrl
        ovseed[3 + i] = v.pwm_period
        ovseed[6 + i] = 0x00 if v.pwm_dir == 'up' else 0xFF
        instr_byte = (v.instr.id - 1) & 0x3F if v.instr is not None else 0
        ovseed[9 + i] = instr_byte
        ovseed[12 + i] = v.dur_field
        ovseed[15 + i] = v.slide_v
    return bytes(ovseed)


def _inputs_from_usf(usf) -> _Inputs:
    """Build codegen `_Inputs` from a USF — no engine-name lookup."""
    from src.usf import MusicSubtune, SfxSubtune
    if usf.freq_table is None:
        raise ValueError(
            'Hubbard build requires a freq_table block in the USF')
    if len(usf.freq_table) != 320:
        raise ValueError(
            f'expected 320-byte freq_table, got {len(usf.freq_table)}')

    # Tune-level params with Commando-flavor defaults. Engines that
    # diverge from these set the field in the USF's params block.
    p = usf.params.fields if usf.params else {}

    def get(key, default):
        return p.get(key, default)

    def latin1(s: str) -> bytes:
        return s.encode('latin-1', errors='replace')

    # Vibrato onset is per-instrument; we plumb the top-level value
    # through each InstrumentModel at build time.
    vib_onset = get('vib_onset', 6)

    models = [_model_from_usf_instrument(u, vib_onset)
              for u in usf.instruments]

    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    music_subs.sort(key=lambda s: s.id)
    subtune_ids = tuple(s.id for s in music_subs)
    scores = [_score_from_subtune(s) for s in music_subs]
    resetspds = [s.tempo - 1 for s in music_subs]
    # Per-subtune voice_start (Action Biker skips a voice on sub 0).
    voice_starts = []
    for s in music_subs:
        sp = s.params.fields if s.params else {}
        voice_starts.append(sp.get('voice_start', 2))

    # Per-subtune mechanism mode: 5_Title_Tunes-style compound engines
    # carry per-subtune deltas on each MusicSubtune.params + per-sub
    # init state. Only the keys below flip the mode; per-sub
    # `voice_start` alone is read independently.
    _PER_SUBTUNE_MECHANISM = {
        'speed_ctr_init', 'incby2_step', 'incby2_late_gate', 'tick_divider',
    }
    has_per_subtune = any(
        s.init is not None or
        (s.params is not None and
         _PER_SUBTUNE_MECHANISM & s.params.fields.keys())
        for s in music_subs)
    per_subtune_speed_ctr_init = None
    per_subtune_incby2_step = None
    per_subtune_incby2_late_gate = None
    per_subtune_ovseed = None
    if has_per_subtune:
        per_subtune_speed_ctr_init = []
        per_subtune_incby2_step = []
        per_subtune_incby2_late_gate = []
        per_subtune_ovseed = []
        top_speed_ctr_init = get('speed_ctr_init', 0)
        top_incby2_step = get('incby2_step', 2)
        top_incby2_late_gate = get('incby2_late_gate', None)
        for i, s in enumerate(music_subs):
            sp = s.params.fields if s.params is not None else {}
            per_subtune_speed_ctr_init.append(
                sp.get('speed_ctr_init', top_speed_ctr_init))
            per_subtune_incby2_step.append(
                sp.get('incby2_step', top_incby2_step) & 0xFF)
            late_gate = sp.get('incby2_late_gate', top_incby2_late_gate)
            per_subtune_incby2_late_gate.append(
                (0xFF if late_gate is None else late_gate) & 0xFF)
            per_subtune_ovseed.append(
                _ovseed_from_init_state(s.init, len(usf.instruments)))
            if 'tick_divider' in sp:
                resetspds[i] = sp['tick_divider']

    # SFX subtunes
    sfx_subs = sorted(
        (s for s in usf.subtunes if isinstance(s, SfxSubtune)),
        key=lambda s: s.id)
    sfx_list = [_soundeffect_from_usf(s, idx)
                for idx, s in enumerate(sfx_subs)]

    # Freq bytes: USF carries the canonical region; per-voice init
    # overlay (when the USF still ships an init block) overrides.
    fb = bytearray(usf.freq_table)
    for v in usf.init.voices:
        i = v.id - 1
        fb[205 + i] = v.dur_field
        fb[208 + i] = v.ctrl
        if v.instr is not None:
            fb[214 + i] = (v.instr.id - 1) & 0xFF
        fb[229 + i] = v.pwm_period
        fb[232 + i] = 0x00 if v.pwm_dir == 'up' else 0xFF
        fb[239 + i] = v.slide_v
    freq_bytes = bytes(fb)

    # Optional state_layout (Human Race).
    state_layout = None
    if usf.state_layout is not None:
        d = usf.state_layout
        scalars = [StatebufSlot(offset=s['offset'], kind=s['kind'],
                                value=s.get('value', 0),
                                var=s.get('var', ''))
                   for s in d['scalars']]
        per_voice = [StatebufSlot(offset=s['offset'], kind=s['kind'],
                                  value=s.get('value', 0),
                                  var=s.get('var', ''))
                     for s in d['per_voice']]
        state_layout = StatebufLayout(
            n_voices=d['n_voices'], scalars=scalars, per_voice=per_voice)

    ns_offtab_decr_offset = get('ns_offtab_decr_offset', None)
    return _Inputs(
        title=latin1(usf.psid.title),
        author=latin1(usf.psid.author),
        released=latin1(usf.psid.released),
        start_song=usf.psid.start_song,
        arp_interval=get('arp_interval', 12),
        arp_period=get('arp_period', 2),
        arp_phase_invert=get('arp_phase_invert', False),
        linear_pw_or=get('linear_pw_or', 0),
        incby2_step=get('incby2_step', 2),
        incby2_every_frame=get('incby2_every_frame', False),
        incby2_onset=get('incby2_onset', 3),
        suppress_first_notestart=get('suppress_first_notestart', False),
        freeze_on_stop=get('freeze_on_stop', False),
        speed_ctr_init=get('speed_ctr_init', 0),
        first_frame_gate_off=get('first_frame_gate_off', False),
        seed_overlap=get('seed_overlap', True),
        psid_speed=usf.psid.speed,
        frame_ctr_init=get('frame_ctr_init', 0xFF),
        incby2_late_gate=get('incby2_late_gate', None),
        stop_fill=get('stop_fill', None),
        sfx_framectr_ofs=get('sfx_framectr_ofs', 253),
        sfx_state_ofs=get('sfx_state_ofs', None),
        has_sfx=get('has_sfx', False),
        subtunes=subtune_ids,
        models=models, scores=scores, resetspds=resetspds,
        voice_starts=voice_starts, freq_bytes=freq_bytes,
        sfx_list=sfx_list,
        per_subtune_speed_ctr_init=per_subtune_speed_ctr_init,
        per_subtune_incby2_step=per_subtune_incby2_step,
        per_subtune_incby2_late_gate=per_subtune_incby2_late_gate,
        per_subtune_ovseed=per_subtune_ovseed,
        master_vol_subtrahend_voice=get('master_vol_subtrahend_voice', None),
        master_vol_base=get('master_vol_base', 0xA0),
        master_vol_trigger=get('master_vol_trigger', 'inst_change'),
        tie_preserves_slide=get('tie_preserves_slide', False),
        hubidx_wrap_at_patend=get('hubidx_wrap_at_patend', True),
        **({'ns_offtab_decr_offset': ns_offtab_decr_offset}
           if ns_offtab_decr_offset is not None else {}),
        **({'state_layout': state_layout} if state_layout is not None else {}),
    )


# ---------------------------------------------------------------------------
# Hubbard '85 build dispatch — top-level entry that goes from a USF to
# the PSID bytes. Phase 8.21 moved these in from composer_hubbard.py,
# which is now deletable.
# ---------------------------------------------------------------------------


def _hubbard_emit_sid(inputs: _Inputs, out_path: str, codec,
                      load_addr: int = LOAD) -> str:
    """Emit a SID file from a fully-prepared `_Inputs`. No I/O of the
    original binary; everything needed is in `inputs`.

    `load_addr` overrides the default $1000 load address — set by the
    combined music+digi build (Chimera) which may pack the music
    engine closer to the digi region's dispatcher.

    `_compose_hubbard_engine_asm` produces FULLY-RESOLVED asm: every
    per-engine knob is threaded into the chunk emitters; the codec's
    note_asm sentinels are resolved by `_resolve_codec_note_asm`.
    This function just xa65-assembles the result and wraps it in a
    PSID v2 header.
    """
    pat_order, pat_slot = _pattern_pool(inputs.scores)
    pat_bytes, codec_extra = codec.encode(pat_order)
    asm = _compose_hubbard_engine_asm(
        inputs, codec, pat_slot, pat_bytes, codec_extra,
        load_addr=load_addr)

    src = '/tmp/usf2_commando.s'
    obj = '/tmp/usf2_commando.bin'
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([_XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        code = f.read()

    # PSID header
    songs = len(inputs.subtunes) + (len(inputs.sfx_list) if inputs.has_sfx else 0)
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', load_addr)
    h += struct.pack('>H', load_addr)
    h += struct.pack('>H', load_addr + 3)
    h += struct.pack('>H', songs)
    h += struct.pack('>H', min(max(inputs.start_song, 1), songs))
    h += struct.pack('>I', inputs.psid_speed)
    # 3 × 32-byte latin-1 fields. Pad/truncate to exactly 32 each.
    for s in (inputs.title, inputs.author, inputs.released):
        h += s[:32].ljust(32, b'\x00')
    h += struct.pack('>H', 0x0014)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124, len(h)

    with open(out_path, 'wb') as f:
        f.write(bytes(h) + code)
    return out_path


def _emit_combined_sid(inputs: _Inputs, usf, digi_subs: list,
                       digi_code, out_path: str, usf_dir: str,
                       codec) -> str:
    """Emit a combined PSID containing music engine + digi engine +
    samples. Music at `digi_code.music_load_addr` (or LOAD if None);
    digi at the engine-fixed addresses ($9F80 dispatcher + $C000
    player for Chimera). The combined file uses inline-load encoding
    so the bytes are one contiguous segment between music_load_addr
    and the digi region's end, with a zero-fill gap between them.

    The default music_load=$1000 puts the music engine 36 KB below
    the dispatcher, ballooning the file to ~45 KB. Setting
    music_load_addr close to dispatcher_base (e.g. $9C00 for Chimera)
    shrinks the gap to a few hundred bytes — matching the original
    Chimera SID's ~12 KB footprint.
    """
    # Auto-pack music against dispatcher when music_load_addr is None:
    # measure music size at LOAD, then compute the tight music_load
    # before building the digi region (the dispatcher's JMP MUSIC_INIT
    # must match the final music_load address). Iterate in case the
    # assembled size shifts with the load address (page-crossing
    # penalties etc.); typically converges in 1-2 iterations.
    tmp_music = out_path + '.music.tmp'
    if digi_code.music_load_addr is not None:
        music_load = digi_code.music_load_addr
    else:
        _hubbard_emit_sid(inputs, tmp_music, codec, load_addr=LOAD)
        size = os.path.getsize(tmp_music) - 124
        music_load = digi_code.dispatcher_base - size
        for _ in range(4):
            _hubbard_emit_sid(inputs, tmp_music, codec, load_addr=music_load)
            new_size = os.path.getsize(tmp_music) - 124
            new_load = digi_code.dispatcher_base - new_size
            if new_load == music_load:
                break
            music_load = new_load

    digi_region, digi_base, play_addr = _build_digi_region(
        usf, digi_subs, digi_code, usf_dir, music_load=music_load)

    _hubbard_emit_sid(inputs, tmp_music, codec, load_addr=music_load)
    music_blob = open(tmp_music, 'rb').read()
    os.unlink(tmp_music)
    # `_hubbard_emit_sid` wrote a PSID; strip its 124-byte header.
    music_body = music_blob[124:]                  # music bytes at $music_load

    music_end = music_load + len(music_body)
    if music_end > digi_base:
        raise ValueError(
            f'music engine at ${music_load:04X}-${music_end - 1:04X} overlaps '
            f'the digi region starting at ${digi_base:04X}')
    gap = bytes(digi_base - music_end)
    binary = music_body + gap + digi_region

    # PSID v2 header: load=$0000 (inline), init=dispatcher_base,
    # play=play_addr (regenerated PSID dispatcher's play entry).
    # No more RSID; no KERNAL dep at playback.
    n_music = len(inputs.subtunes)
    songs = n_music + len(digi_subs)
    start_song = min(max(inputs.start_song, 1), songs)

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', 0x0000)             # load = inline-encoded
    h += struct.pack('>H', digi_code.dispatcher_base)
    h += struct.pack('>H', play_addr)
    h += struct.pack('>H', songs)
    h += struct.pack('>H', start_song)
    h += struct.pack('>I', inputs.psid_speed)
    for s in (inputs.title, inputs.author, inputs.released):
        h += s[:32].ljust(32, b'\x00')
    h += struct.pack('>H', 0x0014)             # flags (PAL + 6581)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124, len(h)

    with open(out_path, 'wb') as f:
        f.write(bytes(h))
        f.write(struct.pack('<H', music_load))   # inline load addr
        f.write(binary)
    return out_path


def _emit_hubbard85_bytes(usf, usf_dir) -> bytes:
    """Hubbard '85 dispatch: build `_Inputs` from the USF, then either
    `_hubbard_emit_sid` (music-only) or `_emit_combined_sid` (when the
    USF carries digi subtunes). Returns the PSID bytes."""
    import tempfile
    from src.usf import DigiSubtune
    from pipelines.hubbard.note_codec import BitPackCodec
    codec = BitPackCodec()
    inputs = _inputs_from_usf(usf)

    digi_subs = sorted(
        (s for s in usf.subtunes if isinstance(s, DigiSubtune)),
        key=lambda s: s.id)

    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        if not digi_subs:
            _hubbard_emit_sid(inputs, tmp_path, codec)
        else:
            if usf_dir is None:
                raise ValueError(
                    'USF has digi subtunes; emit_sid needs usf_dir to '
                    'locate sample FLAC sidecars')
            name = usf.params.fields.get('digi_player') if usf.params else None
            if name is None:
                raise ValueError(
                    'USF has digi subtunes but no `digi_player` in params')
            registry = _digi_player_registry()
            if name not in registry:
                raise ValueError(
                    f'unknown digi_player {name!r}; '
                    f'register in `_digi_player_registry`')
            _emit_combined_sid(inputs, usf, digi_subs, registry[name],
                                tmp_path, usf_dir, codec)
        return open(tmp_path, 'rb').read()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _emit_hubbard_pattern_pool(pat_bytes: list[bytes],
                                 codec_extra: str | None) -> list[str]:
    """Pattern pool — `pat0`, `pat1`, ... per unique pattern, plus the
    `pataddr_lo` / `pataddr_hi` lookup tables that map a dense pattern
    slot to its address. `codec_extra` is optional codec-side data
    appended after the patterns (e.g. lookup tables for some codecs)."""
    lines = []
    for slot, blob in enumerate(pat_bytes):
        lines.append(f'pat{slot}:')
        for i in range(0, len(blob), 16):
            chunk = blob[i:i + 16]
            lines.append('        .byt ' +
                         ','.join(f'${b:02X}' for b in chunk))
    if codec_extra:
        lines.append(codec_extra)
    npat = len(pat_bytes)
    lines.append('pataddr_lo: .byt ' + ','.join(
        f'<pat{s}' for s in range(npat)))
    lines.append('pataddr_hi: .byt ' + ','.join(
        f'>pat{s}' for s in range(npat)))
    return lines


def _emit_hubbard_orderlists(scores, pat_slot: dict) -> list[str]:
    """Per-subtune × per-voice orderlists `order_S_V:`.

    `$FF` = loop to `orderLoop` (per-voice loop point); `$FE` = end
    of song. An empty orderlist emits just `$FE` (e.g. Human Race's
    unused V3 — set_patptr sees the song-end terminator at first
    read and silences the voice).
    """
    lines = []
    for si, score in enumerate(scores):
        for vi, v in enumerate(score.voices):
            if v.orderlist:
                term = '$FE' if v.stop else '$FF'
                ob = ','.join(
                    f'${pat_slot[oidx]:02X}' for oidx in v.orderlist)
                lines.append(f'order_{si}_{vi}: .byt {ob},{term}')
            else:
                lines.append(f'order_{si}_{vi}: .byt $FE')
    return lines


def _emit_hubbard_per_subtune_tables(scores, resetspds, voice_starts) -> list[str]:
    """Per-subtune dispatch tables: `subOrderLo/Hi/Loop` (3 entries
    per subtune — one per voice), `subResetspd` (per-subtune tempo),
    `subVoiceStart` (which voice the dispatch loop starts at —
    Action Biker skips V3 on sub 0)."""
    los, his, loops = [], [], []
    for si, score in enumerate(scores):
        for vi, v in enumerate(score.voices):
            los.append(f'<order_{si}_{vi}')
            his.append(f'>order_{si}_{vi}')
            loops.append(f'${(v.loop if v.loop >= 0 else 0):02X}')
    return [
        'subOrderLo: .byt ' + ','.join(los),
        'subOrderHi: .byt ' + ','.join(his),
        'subOrderLoop: .byt ' + ','.join(loops),
        'subResetspd: .byt ' + ','.join(f'${r:02X}' for r in resetspds),
        'subVoiceStart: .byt ' + ','.join(f'${v:02X}' for v in voice_starts),
    ]


def _emit_hubbard_psp_tables(n_scores: int,
                              per_subtune_speed_ctr_init: list | None,
                              per_subtune_incby2_step: list | None,
                              per_subtune_incby2_late_gate: list | None
                              ) -> list[str]:
    """5_Title_Tunes per-subtune mechanism byte tables — only emitted
    when any one is non-None. The engine's init reads `subSpeedCtrInit`,
    `subIncBy2Step`, `subIncBy2LateGate` indexed by subtune (see the
    `uses_psp` path in `_emit_per_subtune_dispatch`).
    """
    if (per_subtune_speed_ctr_init is None
            and per_subtune_incby2_step is None
            and per_subtune_incby2_late_gate is None):
        return []
    sci = per_subtune_speed_ctr_init or [0] * n_scores
    ibs = per_subtune_incby2_step or [0] * n_scores
    ibg = per_subtune_incby2_late_gate or [0xFF] * n_scores
    return [
        'subSpeedCtrInit: .byt ' + ','.join(f'${b & 0xFF:02X}' for b in sci),
        'subIncBy2Step: .byt ' + ','.join(f'${b & 0xFF:02X}' for b in ibs),
        'subIncBy2LateGate: .byt ' + ','.join(f'${b & 0xFF:02X}' for b in ibg),
    ]


def _emit_hubbard_per_subtune_ovseed(per_subtune_ovseed: list | None
                                      ) -> list[str]:
    """5TT per-subtune ovseed blocks + address lookup tables.

    Each subtune has its own 18-byte ovseed copied at init via the
    ovseed-copy loop (composer's `_emit_ovseed_copy`). The address
    tables let init resolve which sub's bytes to copy.
    """
    if per_subtune_ovseed is None:
        return []
    assert all(len(o) == 18 for o in per_subtune_ovseed), \
        'each per_subtune_ovseed entry must be 18 bytes'
    lines = []
    for i, ov_bytes in enumerate(per_subtune_ovseed):
        lines.append(f'subOvseed_{i}: .byt ' +
                     ','.join(f'${b & 0xFF:02X}' for b in ov_bytes))
    n = len(per_subtune_ovseed)
    lines.append('subOvseedLo: .byt ' + ','.join(
        f'<subOvseed_{i}' for i in range(n)))
    lines.append('subOvseedHi: .byt ' + ','.join(
        f'>subOvseed_{i}' for i in range(n)))
    return lines


def _emit_hubbard_live_order_arrays() -> list[str]:
    """Live per-voice orderlist selection — filled by init from
    `subOrder*`. Zero-initialized at link time."""
    return [
        'orderLo: .byt 0,0,0',
        'orderHi: .byt 0,0,0',
        'orderLoop: .byt 0,0,0',
    ]


def _emit_hubbard_statebuf_data(layout: StatebufLayout) -> list[str]:
    """`statebuf:` data block label — uses `_statebuf_init_bytes` for
    the bytes themselves."""
    return [f'statebuf: .byt {_statebuf_init_bytes(layout)}']


def _emit_hubbard_sfx_records(sfx_list) -> list[str]:
    """SFX records — 32 bytes each: V1[7], V2[7], start, end, rate,
    flags (bit0 direction, bit1 skip-V1, bit2 skip-both),
    v2_byte_offset, gate (bit7/6 toggle V1/V2). See `sfx_play`.
    Padded to 32 bytes with zeros.
    """
    lines = ['sfxdata:']
    for sf in sfx_list:
        flags = ((1 if sf.direction == 'up' else 0)
                 | (2 if sf.skip_v1 else 0)
                 | (4 if sf.skip_both else 0))
        gate = ((0x80 if sf.toggle_v1 else 0)
                | (0x40 if sf.toggle_v2 else 0))
        rec = (list(sf.v1) + list(sf.v2)
               + [sf.start_index, sf.end_index, sf.rate, flags,
                  sf.v2_byte_offset, gate])
        rec += [0] * (32 - len(rec))
        lines.append('        .byt ' +
                     ','.join(f'${b:02X}' for b in rec))
    return lines


def _emit_hubbard_freq_table_data(freq_bytes: bytes) -> list[str]:
    """Emit Hubbard '85's `freqtab:` data block.

    Hubbard uses ONE label `freqtab` for both halves of the table
    (the music reads 16-bit entries — freq_hi and freq_lo at
    interleaved offsets; the SFX sweep walks byte-wise and overflows
    past the 96-entry musical region into the engine-state region —
    the overlap is why this is a single contiguous block of typically
    320 bytes).

    Note this is the Hubbard-shape freq table emitter; the simpler
    companion-strain emitter `_emit_freq_table` splits into
    `freq_hi_tab` + `freq_lo_tab` (a 128+128 layout the simpler
    engines use). Composer keeps both — they target structurally
    different engines.
    """
    lines = ['freqtab:']
    for i in range(0, len(freq_bytes), 16):
        chunk = freq_bytes[i:i + 16]
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in chunk))
    return lines


def _digi_player_registry() -> dict:
    """Map `digi_player` USF param values to their `DigiCode`.

    Each entry binds a tune-level `digi_player: <name>` token to a
    concrete `DigiCode` (dispatcher base, player base, music-load
    hint, bank-table base, ...). Composer reads this when a USF has
    digi subtunes — see `_emit_combined_sid` and the dispatch in
    `composer_hubbard._emit_hubbard85_bytes`.
    """
    from pipelines.hubbard.engine_constants import CHIMERA_DIGI
    return {
        'chimera_1bit': CHIMERA_DIGI,
    }


def _build_digi_region(usf, digi_subs, digi_code, usf_dir: str,
                       music_load=None):
    """Build the bytes of the digi region — dispatcher + tables +
    samples + player — placed at their fixed engine addresses.

    Returns `(region_bytes, region_base, play_addr)`. `play_addr` is
    the PSID `play` entry inside the dispatcher (used by the header).
    """
    import os as _os
    from pipelines.hubbard.engine_constants import (
        assemble_chimera_digi_player, chimera_psid_dispatcher,
    )
    from pipelines.hubbard.flac_io import read_sample
    from pipelines.hubbard.digi_pack import pack_digi

    base = digi_code.dispatcher_base                       # e.g. $9F80
    # The Chimera player is assembled lazily from its xa65 asm source
    # (regenerated, not lifted verbatim from the original SID).
    player_bytes = assemble_chimera_digi_player(
        player_base=digi_code.player_base)
    end  = digi_code.player_base + len(player_bytes)       # one past last byte

    # Generate the PSID dispatcher with addresses substituted for our
    # music engine and the digi player. `music_load` is passed by the
    # caller (auto-packing); fall back to digi_code.music_load_addr or
    # the composer's default LOAD ($1000) when called from contexts
    # that don't know the music engine address yet.
    if music_load is None:
        music_load = (digi_code.music_load_addr
                      if digi_code.music_load_addr is not None else LOAD)
    disp = chimera_psid_dispatcher(
        music_init=music_load, music_play=music_load + 3,
        digi_player=digi_code.player_base, base=base)
    dispatcher = disp['bytes']
    play_addr = base + disp['play_off']
    pace_table_addr = base + disp['pace_table_off']
    bank_table_addr = base + disp['bank_table_off']

    region = bytearray(end - base)
    region[0:len(dispatcher)] = dispatcher
    # Place the digi player at its base.
    player_off = digi_code.player_base - base
    region[player_off:player_off + len(player_bytes)] = player_bytes

    # Process digi subtunes: each carries a pace + bank in its FLAC's
    # Vorbis comments (via the extractor's `to_sample`).
    samples = []
    for st_idx, sub in enumerate(digi_subs):
        sample_path = _os.path.join(usf_dir, sub.sample)
        sample = read_sample(sample_path)
        pace = int(sample.extras['pace'], 16)
        bank = int(sample.extras['bank'], 16)
        src = int(sample.extras['src'], 16)
        end_addr = int(sample.extras['end'], 16)
        keep_screen = sample.extras.get('keep_screen', '0') == '1'
        packed = pack_digi(sample)
        if end_addr - src != len(packed):
            raise ValueError(
                f'subtune {sub.id}: sample claims ${src:04X}-${end_addr:04X} '
                f'({end_addr - src} bytes) but packed bytes are '
                f'{len(packed)}')
        samples.append({
            'st_idx': st_idx, 'pace': pace, 'bank': bank,
            'src': src, 'end': end_addr, 'keep_screen': keep_screen,
            'packed': packed,
            'boundary_vol': sample.extras.get('boundary_vol', '00'),
        })

    # Per-subtune dispatcher tables — the PSID dispatcher's pace_table /
    # bank_table slots reported by `chimera_psid_dispatcher`.
    for s in samples:
        region[pace_table_addr - base + s['st_idx']] = s['pace']
        region[bank_table_addr - base + s['st_idx']] = s['bank']

    # Bank table at $A000 + bank*4 = {src_lo, src_hi, end_lo, end_hi}.
    bt_off = digi_code.bank_table_base - base
    for s in samples:
        e = bt_off + s['bank'] * 4
        region[e + 0] = s['src'] & 0xFF
        region[e + 1] = (s['src'] >> 8) & 0xFF
        region[e + 2] = s['end'] & 0xFF
        region[e + 3] = (s['end'] >> 8) & 0xFF

    # $A103 = sample-table length (number of banks the player accepts).
    region[(digi_code.bank_table_base + 0x103) - base] = len(samples)
    # $A108 = keep-screen flag. Use the first subtune's value (the
    # engine's design assumes it's constant per tune).
    if samples:
        region[(digi_code.bank_table_base + 0x108) - base] = \
            1 if samples[0]['keep_screen'] else 0
        # $A10A = pace placeholder (the dispatcher writes the real one
        # here at runtime). Set to the first subtune's pace.
        region[(digi_code.bank_table_base + 0x10A) - base] = samples[0]['pace']
    # $A10B+ = bank-validation table (the player linearly scans this
    # at startup to confirm the requested bank is registered). Entries
    # are ordered bank-ascending, which matches the original SIDs
    # we've seen — the cycle count of the scan depends on the order,
    # so cycle-strict reproduction requires we match it.
    for i, s in enumerate(sorted(samples, key=lambda x: x['bank'])):
        region[(digi_code.bank_table_base + 0x10B + i) - base] = s['bank']

    # Sample bytes at their claimed addresses.
    for s in samples:
        sb = s['src'] - base
        region[sb:sb + len(s['packed'])] = s['packed']
        # The digi player reads one byte PAST `end` on its last loop
        # iteration ($F9 wrap reads a final vol byte before the bounds
        # check exits) — preserve that byte from the original so the
        # very last $D418 write matches cycle-strict.
        boundary_vol = int(s.get('boundary_vol', '00'), 16)
        if 0 <= s['end'] - base < len(region):
            region[s['end'] - base] = boundary_vol

    return bytes(region), base, play_addr


def _emit_master_vol_fade(fade: 'FadeProgressive | None') -> dict[str, str]:
    """Return the codec-side sentinel→asm fragments for the master-vol fade.

    Three sentinels live in the note codec's note_asm:
      - `; %%VOL_PROGRESS_INC%%` — peek-ahead INC at the configured
        voice's pattern-end (last note of a pattern).
      - `; %%MASTER_VOL_WRITE%%` — clamp-and-write $D418 on
        instrument-change notes (default trigger).
      - `; %%MASTER_VOL_EVERY_NOTE%%` — same write on every note
        (Thing on a Spring's trigger='every_note' variant).

    `fade is None` → all three sentinels expand to empty strings.
    The init-side `; %%VOL_PROGRESS_INIT%%` is resolved by
    `_emit_hubbard_init(has_master_vol_fade=...)` directly.
    """
    if fade is None:
        return {s: '' for s in _VOL_FADE_SENTINELS}

    v = fade.subtrahend_voice_idx
    # Peek-ahead semantics: INC vol_progress when the current voice's
    # v_notesleft has just decremented to 0 (i.e. THIS load was the
    # pattern's last note). Matches the engine's $C15A-$C167 path
    # which INCs the counter on the same tick the last note is loaded.
    inc_asm = (
        f'        cpx #{v}\n'
        f'        bne vp_skip\n'
        f'        lda v_notesleft,x\n'
        f'        bne vp_skip\n'
        f'        inc vol_progress\n'
        f'vp_skip:'
    )
    write_template = (
        f'        lda #${fade.base:02X}\n'
        f'        sec\n'
        f'        sbc vol_progress\n'
        f'        cmp #$0f\n'
        f'        bcc {{label}}\n'
        f'        lda #$0f\n'
        f'{{label}}: sta $d418'
    )
    write_asm = write_template.format(label='mvw_lt')
    return {
        '; %%VOL_PROGRESS_INC%%':      inc_asm,
        '; %%MASTER_VOL_WRITE%%':      (
            write_asm if fade.trigger != 'every_note' else ''),
        '; %%MASTER_VOL_EVERY_NOTE%%': (
            write_asm if fade.trigger == 'every_note' else ''),
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
