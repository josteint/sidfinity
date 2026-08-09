"""Standalone builder for C64ME — emits a PSID byte-exact against orig.

Bypasses the main composer.py infrastructure. Reads engine state +
pattern bytes via the Python emulators in extract/engine_model.py,
emits a clean xa65-assembled engine + per-subtune data, packages
as PSID, verifies against orig via writelog.

This module currently handles sub 0 (V1.a engine variant) as the
proof-of-concept. Other variants (V1.b/V1.c/V2/Family B) extend the
same pattern with per-variant asm templates.
"""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, 'tools/py65_lib')

ROOT = Path(__file__).resolve().parents[3]

SID_PATH = str(ROOT / 'hvsc85' / 'MUSICIANS' / 'H' / 'Hubbard_Rob' /
               'Commodore_64_Music_Examples.sid')


def _assemble(asm_src: str, name: str = 'c64me') -> bytes:
    """Thin wrapper around the shared `src.composer_runtime.assemble`.
    C64ME's asm doesn't use ':' in comments and doesn't need labels.
    `name` is ignored — shared helper uses TemporaryDirectory."""
    from src.composer_runtime import assemble
    return assemble(asm_src)


def _psid_header(title: str, author: str, released: str,
                 n_subtunes: int, start_song: int,
                 load: int, init_addr: int, play_addr: int) -> bytes:
    """Thin wrapper around src.composer_runtime.build_header."""
    from src.composer_runtime import build_header
    return build_header(
        load=load, init=init_addr, play=play_addr,
        songs=n_subtunes, start_song=start_song, speed=0,  # VBI
        title=title, author=author, released=released)


def _walk_pattern(mem: bytearray, start: int, max_bytes: int = 4000) -> bytes:
    out = []
    addr = start
    for _ in range(max_bytes):
        b = mem[addr]
        out.append(b)
        addr = (addr + 1) & 0xFFFF
        if b in (0x0F, 0x8E):
            break
    return bytes(out)


# Vibrato + loop_reset variant chunks
_VIBRATO_AND_LOOP_RESET_ASM = """\
loop_reset:
  lda state+1
  bpl skip_lr_v1
  lda state+4
  sta $d404
skip_lr_v1:
  lda state+8
  bpl skip_lr_v2
  lda state+11
  sta $d40b
skip_lr_v2:
  lda state+15
  bpl skip_lr_v3
  lda state+18
  sta $d412
skip_lr_v3:
  jmp vibrato_only

vibrato_only:
  lda frame_idx
  and #$07
  cmp #$04
  bcc vib_pos
  eor #$07
vib_pos:
  sta tri_pos
  ldy current_note
  lda freq_lo+1,y
  beq vib_done
  sec
  sbc freq_lo,y
  sta step_lo
  lda freq_hi+1,y
  sbc freq_hi,y
  lsr
  ror step_lo
  lsr
  ror step_lo
  lsr
  ror step_lo
  lsr
  ror step_lo
  sta step_hi
  lda freq_lo,y
  sta base_lo
  lda freq_hi,y
  sta base_hi
  ldy tri_pos
  beq vib_emit
vib_mul:
  clc
  lda base_lo
  adc step_lo
  sta base_lo
  lda base_hi
  adc step_hi
  sta base_hi
  dey
  bne vib_mul
vib_emit:
  lda base_lo
  sta $d400
  lda base_hi
  sta $d401
vib_done:
  inc frame_idx
  rts
"""

# loop_reset without vibrato (sub 2 / sub 3): RTS instead of jmp vibrato
_LOOP_RESET_NO_VIBRATO_ASM = """\
loop_reset:
  lda state+1
  bpl skip_lr_v1
  lda state+4
  sta $d404
skip_lr_v1:
  lda state+8
  bpl skip_lr_v2
  lda state+11
  sta $d40b
skip_lr_v2:
  lda state+15
  bpl skip_lr_v3
  lda state+18
  sta $d412
skip_lr_v3:
  rts
"""


def emit_subtune_asm(subtune: int) -> str:
    """Emit complete xa65 asm for one Family A V1-router subtune.

    Handles dispatch + PWM variant + per-instance state/pattern data
    via FAMILY_A_INSTANCES bindings. Sub 0 = V1.a (vibrato + sweep PWM).
    Sub 2 = V1.b (no vibrato + increment PWM). Sub 3 = V1.c (BNE-loop
    + sweep PWM with $03/$0D bounds).
    """
    from pipelines.companion.c64_music_examples.extract.engine_model import (
        _run_init_via_py65, FAMILY_A_INSTANCES,
    )
    b = FAMILY_A_INSTANCES[subtune]
    mem, _ = _run_init_via_py65(SID_PATH, subtune)

    # Extract state + patterns + freq tables
    state_bytes = list(mem[b.state_base:b.state_base + 32])
    v1_lo = mem[0x1C]; v1_hi = mem[0x1D]
    v2_lo = mem[0x1E]; v2_hi = mem[0x1F]
    v3_lo = mem[0x20]; v3_hi = mem[0x21]
    v1_pat = _walk_pattern(mem, (v1_hi << 8) | v1_lo)
    v2_pat = _walk_pattern(mem, (v2_hi << 8) | v2_lo)
    v3_pat = _walk_pattern(mem, (v3_hi << 8) | v3_lo)
    freq_hi = list(mem[0x0B5F:0x0B5F + 128])
    freq_lo = list(mem[0x0BDF:0x0BDF + 128])
    current_note = mem[b.current_note_addr]
    # PWM sign bytes only meaningful for sweep variant
    if b.pwm_variant == 'sweep':
        pwm_sign_v1 = mem[b.pwm_sign_base]
        pwm_sign_v3 = mem[b.pwm_sign_base + 14]
    else:
        pwm_sign_v1 = pwm_sign_v3 = 0  # unused
    # PWM state offsets within state — sub 3 has them at +24/+25 instead of +30/+31.
    v3_pwm_state_off = b.v3_pwm_ctr_addr - b.state_base
    v1_pwm_state_off = b.v1_pwm_ctr_addr - b.state_base

    def hex_list(bs):
        out = []
        for i in range(0, len(bs), 16):
            chunk = bs[i:i + 16]
            out.append('  .byte ' + ', '.join(f'${b:02X}' for b in chunk))
        return '\n'.join(out)

    # Variant-specific asm chunks.
    if b.pwm_variant == 'sweep':
        pwm_sweep_asm = f"""\
pwm_sweep:
  cpx #0
  bne pwm_v3
  lda pwm_sign_v1
  bpl pwm_v1_desc
  inc state+3
  lda state+3
  cmp #${b.pwm_hi:02X}
  bne pwm_v1_emit
  inc pwm_sign_v1
  jmp pwm_v1_emit
pwm_v1_desc:
  dec state+3
  lda state+3
  cmp #${b.pwm_lo:02X}
  bne pwm_v1_emit
  dec pwm_sign_v1
pwm_v1_emit:
  sta $d403
  lda #0
  rts
pwm_v3:
  lda pwm_sign_v3
  bpl pwm_v3_desc
  inc state+17
  lda state+17
  cmp #${b.pwm_hi:02X}
  bne pwm_v3_emit
  inc pwm_sign_v3
  jmp pwm_v3_emit
pwm_v3_desc:
  dec state+17
  lda state+17
  cmp #${b.pwm_lo:02X}
  bne pwm_v3_emit
  dec pwm_sign_v3
pwm_v3_emit:
  sta $d411
  lda #0
  rts
"""
        pwm_runtime_vars = """\
pwm_sign_v1:     .byte 0
pwm_sign_v3:     .byte 0
"""
        pwm_init_asm = f"""\
  lda #${pwm_sign_v1:02X}
  sta pwm_sign_v1
  lda #${pwm_sign_v3:02X}
  sta pwm_sign_v3
"""
    else:  # 'increment'
        pwm_sweep_asm = f"""\
pwm_sweep:
  cpx #0
  bne pwm_inc_v3
  inc state+3
  lda state+3
  cmp #${b.pwm_hi:02X}
  bne pwm_inc_v1_emit
  lda #${b.pwm_lo:02X}
  sta state+3
pwm_inc_v1_emit:
  sta $d403
  lda #0
  rts
pwm_inc_v3:
  inc state+17
  lda state+17
  cmp #${b.pwm_hi:02X}
  bne pwm_inc_v3_emit
  lda #${b.pwm_lo:02X}
  sta state+17
pwm_inc_v3_emit:
  sta $d411
  lda #0
  rts
"""
        pwm_runtime_vars = ""
        pwm_init_asm = ""

    # current_note is always allocated — voice_event router writes to it on
    # V1 note plays regardless of dispatch variant (even when vibrato never
    # reads it). vibrato_only also references it; whether it's present in
    # the emitted code depends on the dispatch chunk.
    common_runtime_vars = f"current_note:    .byte 0\n"
    common_init_asm = f"  lda #${current_note:02X}\n  sta current_note\n"

    if b.dispatch == 'v0':
        else_branch_asm = "  jmp vibrato_only"
        tempo_branch_asm = "  jmp loop_reset"
        vibrato_section = _VIBRATO_AND_LOOP_RESET_ASM
        vib_runtime_vars = """\
frame_idx:       .byte 0
tri_pos:         .byte 0
step_lo:         .byte 0
step_hi:         .byte 0
base_lo:         .byte 0
base_hi:         .byte 0
"""
        vib_init_asm = ""
    else:  # 'no_vibrato' or 'bne_loop'
        else_branch_asm = "  rts"
        tempo_branch_asm = "  jmp loop_reset"
        vibrato_section = _LOOP_RESET_NO_VIBRATO_ASM
        vib_runtime_vars = ""
        vib_init_asm = ""

    # full_tick end: V1.a engine INCs frame_idx (for vibrato); other variants
    # don't have frame_idx so just rts.
    if b.dispatch == 'v0':
        full_tick_end_asm = "  inc frame_idx\n  rts"
    else:
        full_tick_end_asm = "  rts"

    # Per-subtune init's optional initial master_vol write.
    if b.init_master_vol_first:
        init_master_vol_first_asm = "  lda #$0F\n  sta $d418\n"
    else:
        init_master_vol_first_asm = ""

    asm = f"""\
* = $0801

zp_v1_lo = $1C
zp_v1_hi = $1D
zp_v2_lo = $1E
zp_v2_hi = $1F
zp_v3_lo = $20
zp_v3_hi = $21

init_jmp:
  jmp init
play_jmp:
  jmp play

init:
  sei
{init_master_vol_first_asm}  ; Copy state template (32 bytes)
  ldx #31
copy_state:
  lda state_template,x
  sta state,x
  dex
  bpl copy_state
  ; Init zp pattern ptrs directly to our fresh addresses (no via-state
  ; indirection — sub 3 has PWM ctrs at state+24/+25, not pattern_ptrs)
  lda #<ptn_v1
  sta zp_v1_lo
  lda #>ptn_v1
  sta zp_v1_hi
  lda #<ptn_v2
  sta zp_v2_lo
  lda #>ptn_v2
  sta zp_v2_hi
  lda #<ptn_v3
  sta zp_v3_lo
  lda #>ptn_v3
  sta zp_v3_hi
{pwm_init_asm}{common_init_asm}{vib_init_asm}
  ; Dump state to SID regs (LDX #$14; LDA state,X; STA $D400,X; DEX; BPL)
  ldx #$14
dump_to_sid:
  lda state,x
  sta $d400,x
  dex
  bpl dump_to_sid
  lda #0
  sta $d417
  lda #$0F
  sta $d418
  cli
  rts

play:
  lda state+14
  bmi skip_v3_pwm
  inc state+{v3_pwm_state_off}
  cmp state+{v3_pwm_state_off}
  bne skip_v3_pwm
  ldx #$0E
  jsr pwm_sweep
  sta state+{v3_pwm_state_off}
skip_v3_pwm:
  lda state+0
  bmi skip_v1_pwm
  inc state+{v1_pwm_state_off}
  cmp state+{v1_pwm_state_off}
  bne skip_v1_pwm
  ldx #$00
  jsr pwm_sweep
  sta state+{v1_pwm_state_off}
skip_v1_pwm:
  inc state+23
  lda state+23
  cmp state+21
  bne not_tempo
{tempo_branch_asm}
not_tempo:
  cmp state+22
  beq full_tick
{else_branch_asm}
full_tick:
  lda #0
  sta state+23
  jsr advance_v1
  jsr advance_v2
  jsr advance_v3
{full_tick_end_asm}

{vibrato_section}
; Voice advance subroutines
advance_v1:
  ldy #0
  lda (zp_v1_lo),y
  inc zp_v1_lo
  bne av1_done
  inc zp_v1_hi
av1_done:
  ldx #$00
  jmp voice_event

advance_v2:
  ldy #0
  lda (zp_v2_lo),y
  inc zp_v2_lo
  bne av2_done
  inc zp_v2_hi
av2_done:
  ldx #$07
  jmp voice_event

advance_v3:
  ldy #0
  lda (zp_v3_lo),y
  inc zp_v3_lo
  bne av3_done
  inc zp_v3_hi
av3_done:
  ldx #$0E
  jmp voice_event

; Voice event router
voice_event:
  sta last_cmd_tmp
  cpx #0
  bne ve_store_v2
  sta state+1
  jmp ve_dur_check
ve_store_v2:
  cpx #7
  bne ve_store_v3
  sta state+8
  jmp ve_dur_check
ve_store_v3:
  sta state+15
ve_dur_check:
  lda last_cmd_tmp
  cmp #$09
  bcs ve_hi
  asl
  asl
  asl
  asl
  cpx #0
  bne ve_dur_v2
  sta state+4
  jmp advance_v1
ve_dur_v2:
  cpx #7
  bne ve_dur_v3
  sta state+11
  jmp advance_v2
ve_dur_v3:
  sta state+18
  jmp advance_v3
ve_hi:
  cmp #$0F
  beq ve_done
  tay
  bpl ve_bare_note
  and #$7F
  tay
  jmp ve_special_or_note

ve_bare_note:
ve_play_note:
  cpx #0
  bne ve_play_freq
  sty current_note
ve_play_freq:
  lda freq_hi,y
  sta $d401,x
  lda freq_lo,y
  sta $d400,x
  cpx #0
  bne ve_ctrl_v2
  ldy state+4
  jmp ve_emit_ctrl
ve_ctrl_v2:
  cpx #7
  bne ve_ctrl_v3
  ldy state+11
  jmp ve_emit_ctrl
ve_ctrl_v3:
  ldy state+18
ve_emit_ctrl:
  iny
  tya
  sta $d404,x
ve_done:
  rts

ve_special_or_note:
  cpy #$0E
  bne ve_check_0c
  cpx #0
  bne ve_loop_v2
  lda #<ptn_v1
  sta zp_v1_lo
  lda #>ptn_v1
  sta zp_v1_hi
  jmp advance_v1
ve_loop_v2:
  cpx #7
  bne ve_loop_v3
  lda #<ptn_v2
  sta zp_v2_lo
  lda #>ptn_v2
  sta zp_v2_hi
  jmp advance_v2
ve_loop_v3:
  lda #<ptn_v3
  sta zp_v3_lo
  lda #>ptn_v3
  sta zp_v3_hi
  jmp advance_v3
ve_check_0c:
  cpy #$0C
  bne ve_check_0d
  cpx #0
  bne ve_0c_v2
  lda state+4
  jmp ve_emit_timbre
ve_0c_v2:
  cpx #7
  bne ve_0c_v3
  lda state+11
  jmp ve_emit_timbre
ve_0c_v3:
  lda state+18
ve_emit_timbre:
  sta $d404,x
  rts
ve_check_0d:
  cpy #$0D
  beq ve_0d_path
  jmp ve_play_note
ve_0d_path:
  cpx #0
  bne ve_0d_v2
  lda state+4
  jmp ve_emit_timbre_0d
ve_0d_v2:
  cpx #7
  bne ve_0d_v3
  lda state+11
  jmp ve_emit_timbre_0d
ve_0d_v3:
  lda state+18
ve_emit_timbre_0d:
  sta $d404,x
  rts

{pwm_sweep_asm}
;===== Data =====

state_template:
{hex_list(state_bytes)}

ptn_v1:
{hex_list(list(v1_pat))}
ptn_v2:
{hex_list(list(v2_pat))}
ptn_v3:
{hex_list(list(v3_pat))}

freq_hi:
{hex_list(freq_hi)}
freq_lo:
{hex_list(freq_lo)}

;Runtime state
state:           .dsb 32, 0
{pwm_runtime_vars}{common_runtime_vars}{vib_runtime_vars}last_cmd_tmp:    .byte 0
"""
    return asm


def build_subtune_sid(subtune: int) -> bytes:
    asm = emit_subtune_asm(subtune)
    body = _assemble(asm, f'c64me_sub{subtune}')
    load_addr = 0x0801
    init_addr = load_addr
    play_addr = load_addr + 3
    title = f"Commodore 64 Music Examples (sub {subtune})"
    author = "Rob Hubbard"
    released = "1985 Rob Hubbard"
    h = _psid_header(title, author, released, 1, 1, load_addr, init_addr, play_addr)
    return h + body


def emit_v2_subtune_asm(subtune: int) -> str:
    """Emit complete xa65 asm for one V2-router subtune (subs 4-14).

    Differs from V1 router in:
    - No duration-nybble path (no <$09 case)
    - AD/SR writes on note play (V2-the-voice also gets PW writes)
    - Gate flag at gate_flag var (orig $0384) skips V1 writes when bit 7 set
    - $0D for V3 sets song_end_flag (orig $0383) = $FF
    - Different freq tables ($32D8 hi / $3358 lo in orig)
    - Per-voice state: 7 bytes (last_cmd, PW_lo, PW_hi, ctrl, AD, SR + 1 unused)
    - No vibrato in else branch
    - Increment PWM
    """
    from pipelines.companion.c64_music_examples.extract.engine_model import (
        _run_init_via_py65, FAMILY_A_INSTANCES, V2_FREQ_HI_ADDR, V2_FREQ_LO_ADDR,
    )
    b = FAMILY_A_INSTANCES['shared']
    mem, _ = _run_init_via_py65(SID_PATH, subtune)

    state_bytes = list(mem[b.state_base:b.state_base + 32])
    v1_lo = mem[0x1C]; v1_hi = mem[0x1D]
    v2_lo = mem[0x1E]; v2_hi = mem[0x1F]
    v3_lo = mem[0x20]; v3_hi = mem[0x21]
    v1_pat = _walk_pattern(mem, (v1_hi << 8) | v1_lo)
    v2_pat = _walk_pattern(mem, (v2_hi << 8) | v2_lo)
    v3_pat = _walk_pattern(mem, (v3_hi << 8) | v3_lo)
    freq_hi = list(mem[V2_FREQ_HI_ADDR:V2_FREQ_HI_ADDR + 128])
    freq_lo = list(mem[V2_FREQ_LO_ADDR:V2_FREQ_LO_ADDR + 128])
    gate_flag_init = mem[0x0384]
    song_end_init = mem[0x0383]

    # V2 PWM ctr addresses for sub 4-14: state+30 (V3), state+31 (V1)
    v3_pwm_state_off = 30
    v1_pwm_state_off = 31

    def hex_list(bs):
        out = []
        for i in range(0, len(bs), 16):
            chunk = bs[i:i + 16]
            out.append('  .byte ' + ', '.join(f'${b:02X}' for b in chunk))
        return '\n'.join(out)

    asm = f"""\
* = $0801

zp_v1_lo = $1C
zp_v1_hi = $1D
zp_v2_lo = $1E
zp_v2_hi = $1F
zp_v3_lo = $20
zp_v3_hi = $21

init_jmp:
  jmp init
play_jmp:
  jmp play

init:
  sei
  lda #$0F
  sta $d418
  ldx #31
copy_state:
  lda state_template,x
  sta state,x
  dex
  bpl copy_state
  lda #<ptn_v1
  sta zp_v1_lo
  lda #>ptn_v1
  sta zp_v1_hi
  lda #<ptn_v2
  sta zp_v2_lo
  lda #>ptn_v2
  sta zp_v2_hi
  lda #<ptn_v3
  sta zp_v3_lo
  lda #>ptn_v3
  sta zp_v3_hi
  lda #${gate_flag_init:02X}
  sta gate_flag
  lda #${song_end_init:02X}
  sta song_end
  lda #0
  sta $d417
  lda #$0F
  sta $d418
  lda state+3
  sta $d403
  cli
  rts

play:
  ; V3 PWM
  lda state+14
  bmi skip_v3_pwm
  inc state+{v3_pwm_state_off}
  cmp state+{v3_pwm_state_off}
  bne skip_v3_pwm
  ldx #$0E
  jsr pwm_sweep
  sta state+{v3_pwm_state_off}
skip_v3_pwm:
  ; V1 PWM
  lda state+0
  bmi skip_v1_pwm
  inc state+{v1_pwm_state_off}
  cmp state+{v1_pwm_state_off}
  bne skip_v1_pwm
  ldx #$00
  jsr pwm_sweep
  sta state+{v1_pwm_state_off}
skip_v1_pwm:
  inc state+23
  lda state+23
  cmp state+21
  bne v2_not_tempo
  jmp v2_loop_reset
v2_not_tempo:
  cmp state+22
  beq v2_full_tick
  rts
v2_full_tick:
  lda #0
  sta state+23
  jsr advance_v1
  jsr advance_v2
  jsr advance_v3
  rts

v2_loop_reset:
  lda state+1
  bpl v2_skip_lr_v1
  bit gate_flag
  bmi v2_skip_lr_v1
  lda state+4
  sta $d404
v2_skip_lr_v1:
  lda state+8
  bpl v2_skip_lr_v2
  lda state+11
  sta $d40b
v2_skip_lr_v2:
  lda state+15
  bpl v2_skip_lr_v3
  lda state+18
  sta $d412
v2_skip_lr_v3:
  rts

; V2 PWM sweep (increment-only)
pwm_sweep:
  cpx #0
  bne pwm_inc_v3
  inc state+3
  lda state+3
  cmp #$0E
  bne pwm_inc_v1_emit
  lda #$02
  sta state+3
pwm_inc_v1_emit:
  sta $d403
  lda #0
  rts
pwm_inc_v3:
  inc state+17
  lda state+17
  cmp #$0E
  bne pwm_inc_v3_emit
  lda #$02
  sta state+17
pwm_inc_v3_emit:
  sta $d411
  lda #0
  rts

; Voice advance subroutines
advance_v1:
  ldy #0
  lda (zp_v1_lo),y
  inc zp_v1_lo
  bne av1_done
  inc zp_v1_hi
av1_done:
  ldx #$00
  jmp v2_voice_event

advance_v2:
  ldy #0
  lda (zp_v2_lo),y
  inc zp_v2_lo
  bne av2_done
  inc zp_v2_hi
av2_done:
  ldx #$07
  jmp v2_voice_event

advance_v3:
  ldy #0
  lda (zp_v3_lo),y
  inc zp_v3_lo
  bne av3_done
  inc zp_v3_hi
av3_done:
  ldx #$0E
  jmp v2_voice_event

; V2 voice event router (no duration nybble; AD/SR writes; gate check)
v2_voice_event:
  cpx #0
  bne v2_store_v2
  sta state+1
  jmp v2_dispatch
v2_store_v2:
  cpx #7
  bne v2_store_v3
  sta state+8
  jmp v2_dispatch
v2_store_v3:
  sta state+15
v2_dispatch:
  tay
  bpl v2_note_path
  and #$7F
  tay
  jmp v2_special

v2_note_path:
  bit gate_flag
  bpl v2_play_note
  cpx #0
  beq v2_done
v2_play_note:
  lda freq_hi,y
  sta $d401,x
  lda freq_lo,y
  sta $d400,x
  jsr v2_ad_sr_helper
  cpx #0
  bne v2_ctrl_v2
  ldy state+4
  jmp v2_emit_ctrl
v2_ctrl_v2:
  cpx #7
  bne v2_ctrl_v3
  ldy state+11
  jmp v2_emit_ctrl
v2_ctrl_v3:
  ldy state+18
v2_emit_ctrl:
  iny
  tya
  sta $d404,x
v2_done:
  rts

v2_special:
  cpy #$0E
  bne v2_check_0c
  ; Pattern loop
  cpx #0
  bne v2_loop_v2
  lda #<ptn_v1
  sta zp_v1_lo
  lda #>ptn_v1
  sta zp_v1_hi
  jmp advance_v1
v2_loop_v2:
  cpx #7
  bne v2_loop_v3
  lda #<ptn_v2
  sta zp_v2_lo
  lda #>ptn_v2
  sta zp_v2_hi
  jmp advance_v2
v2_loop_v3:
  lda #<ptn_v3
  sta zp_v3_lo
  lda #>ptn_v3
  sta zp_v3_hi
  jmp advance_v3
v2_check_0c:
  cpy #$0C
  bne v2_check_0d
  bit gate_flag
  bpl v2_0c_write
  cpx #0
  beq v2_done
v2_0c_write:
  cpx #0
  bne v2_0c_v2
  lda state+4
  jmp v2_0c_emit
v2_0c_v2:
  cpx #7
  bne v2_0c_v3
  lda state+11
  jmp v2_0c_emit
v2_0c_v3:
  lda state+18
v2_0c_emit:
  sta $d404,x
  rts
v2_check_0d:
  cpy #$0D
  beq v2_0d_path
  jmp v2_play_note
v2_0d_path:
  bit gate_flag
  bpl v2_0d_write
  cpx #0
  beq v2_0d_check_v3
v2_0d_write:
  cpx #0
  bne v2_0d_v2
  lda state+4
  jmp v2_0d_emit
v2_0d_v2:
  cpx #7
  bne v2_0d_v3
  lda state+11
  jmp v2_0d_emit
v2_0d_v3:
  lda state+18
v2_0d_emit:
  sta $d404,x
v2_0d_check_v3:
  cpx #$0E
  bne v2_0d_done
  lda #$FF
  sta song_end
v2_0d_done:
  rts

; AD/SR helper — writes AD/SR for all voices, plus PW for V2 (X=7)
v2_ad_sr_helper:
  cpx #$07
  bne v2_ad_sr_no_pw
  lda state+2,x
  sta $d402,x
  lda state+3,x
  sta $d403,x
v2_ad_sr_no_pw:
  lda state+5,x
  sta $d405,x
  lda state+6,x
  sta $d406,x
  rts

;===== Data =====

state_template:
{hex_list(state_bytes)}

ptn_v1:
{hex_list(list(v1_pat))}
ptn_v2:
{hex_list(list(v2_pat))}
ptn_v3:
{hex_list(list(v3_pat))}

freq_hi:
{hex_list(freq_hi)}
freq_lo:
{hex_list(freq_lo)}

state:        .dsb 32, 0
gate_flag:    .byte 0
song_end:     .byte 0
"""
    return asm


def build_subtune_sid_v2(subtune: int) -> bytes:
    asm = emit_v2_subtune_asm(subtune)
    body = _assemble(asm, f'c64me_sub{subtune}')
    load_addr = 0x0801
    init_addr = load_addr
    play_addr = load_addr + 3
    title = f"Commodore 64 Music Examples (sub {subtune})"
    author = "Rob Hubbard"
    released = "1985 Rob Hubbard"
    h = _psid_header(title, author, released, 1, 1, load_addr, init_addr, play_addr)
    return h + body


def build_subtune_sid_b(subtune: int) -> bytes:
    """Build sub 1 (Family B engine).

    Pragmatic approach: load at $1100 to fit just before the engine
    at $1119; copy engine code + data verbatim from orig SID. The
    engine internally references hardcoded addresses ($1348 freq,
    $143C/$14CD pattern tables, $1D1D instruments, $1408 state, etc.)
    — placing them at orig addresses lets engine code work as-is
    without fixups.

    State and runtime vars at $1408-$1437 are RAM (cleared at load),
    set up via init code.
    """
    if subtune != 1:
        raise ValueError("build_subtune_sid_b only handles sub 1")
    from pipelines.companion.c64_music_examples.extract.engine_model import (
        _run_init_via_py65,
    )
    mem, _ = _run_init_via_py65(SID_PATH, 1)

    # Build init code at $1100 that:
    # - SEI
    # - sets master_vol $0F + filter $00
    # - initializes state ($1408-$1437) with snapshot values from orig init
    # - CLI; RTS
    # Play address: $1119 (engine entry — same as orig, since we're at same load)

    # Capture state snapshot AFTER orig init runs
    state_snap = bytes(mem[0x1408:0x1438])  # 0x30 bytes
    # Also $0314/$0315 (IRQ vector) and $A2 (frame ctr equiv) and $03E7
    # — these aren't reset to specific values per subtune in orig PSID, so leave.

    # Build init asm at $1100
    init_asm = ['* = $1100', 'init_entry:', '  sei',
                '  lda #$0F', '  sta $d418',
                '  lda #$00', '  sta $d417',
                '  lda #$0F', '  sta $d418']
    # Copy state snapshot byte-by-byte
    for i, v in enumerate(state_snap):
        init_asm.append(f'  lda #${v:02X}')
        init_asm.append(f'  sta ${0x1408 + i:04X}')
    init_asm.append('  cli')
    init_asm.append('  rts')

    # Assemble init code first to get its size
    init_src = '\n'.join(init_asm)
    init_bin = _assemble(init_src, 'c64me_sub1_init')

    # Build full asm: init + raw engine bytes at $1119 + raw data sections
    # We assemble in two pieces, but xa65 single-pass works by using
    # .byte for the engine/data sections.
    # Engine code: $1119-$1347 (varies) + $1348-$1447 freq + $143C-$14DC pattern tables + ...
    # Easiest: dump $1119-$1D9F (covers engine + data + instruments) as a single .byte block.
    # Then padding to ensure addresses match.

    # Find end of useful data: $1D1D + 13*8 = $1D85 (instruments). Add safety to $1DA0.
    DATA_END = 0x1DA0

    # Lower load to $1000 to fit init code + state snapshot data
    full_asm = ['* = $1000']
    full_asm.append('init_entry:')
    full_asm.append('  jmp init_real')
    full_asm.append('play_entry:')
    full_asm.append('  lda $A2')
    full_asm.append('  pha')
    full_asm.append('  lda $086E')
    full_asm.append('  sta $A2')
    full_asm.append('  inc $086E')
    full_asm.append('  jsr $1119')
    full_asm.append('  pla')
    full_asm.append('  sta $A2')
    full_asm.append('  rts')
    full_asm.append('init_real:')
    full_asm.append('  sei')
    full_asm.append('  lda #$00')
    full_asm.append('  sta $086E')
    full_asm.append('  sta $d417')
    full_asm.append('  lda #$0F')
    full_asm.append('  sta $d418')
    full_asm.append('  ldx #$2F')          # copy 48 bytes (state[0x00..0x2F])
    full_asm.append('init_copy:')
    full_asm.append('  lda state_snap,x')
    full_asm.append('  sta $1408,x')
    full_asm.append('  dex')
    full_asm.append('  bpl init_copy')
    full_asm.append('  cli')
    full_asm.append('  rts')
    full_asm.append('state_snap:')
    for i in range(0, len(state_snap), 16):
        chunk = state_snap[i:i+16]
        full_asm.append('  .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    full_asm.append('  .dsb $1119 - *, 0')

    # Dump engine + data $1119-$1D9F
    raw_block = bytes(mem[0x1119:DATA_END])
    for i in range(0, len(raw_block), 16):
        chunk = raw_block[i:i+16]
        full_asm.append('  .byte ' + ', '.join(f'${b:02X}' for b in chunk))

    asm = '\n'.join(full_asm) + '\n'
    body = _assemble(asm, 'c64me_sub1')
    load_addr = 0x1000
    init_addr = load_addr      # init_entry at $1000
    play_addr = load_addr + 3  # play_entry just after init_entry's JMP
    title = "Commodore 64 Music Examples (sub 1)"
    author = "Rob Hubbard"
    released = "1985 Rob Hubbard"
    h = _psid_header(title, author, released, 1, 1, load_addr, init_addr, play_addr)
    return h + body


if __name__ == '__main__':
    import sys
    subtunes = [int(s) for s in sys.argv[1:]] if len(sys.argv) > 1 else [0]
    for st in subtunes:
        if st in (0, 2, 3):
            sid = build_subtune_sid(st)
        elif st == 1:
            sid = build_subtune_sid_b(st)
        else:
            sid = build_subtune_sid_v2(st)
        out_path = SID_PATH.replace('.sid', f'.sub{st}.sidfinity.sid')
        with open(out_path, 'wb') as f:
            f.write(sid)
        print(f"Wrote {out_path} ({len(sid)} bytes)")
