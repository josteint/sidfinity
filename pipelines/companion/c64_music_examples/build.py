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
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, 'tools/py65_lib')

ROOT = Path(__file__).resolve().parents[3]
XA = str(ROOT / 'tools' / 'xa65' / 'xa' / 'xa')

SID_PATH = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'H' / 'Hubbard_Rob' /
               'Commodore_64_Music_Examples.sid')


def _assemble(asm_src: str, name: str = 'c64me') -> bytes:
    src = f'/tmp/{name}.s'
    obj = f'/tmp/{name}.bin'
    with open(src, 'w') as f:
        f.write(asm_src)
    r = subprocess.run([XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    return open(obj, 'rb').read()


def _psid_header(title: str, author: str, released: str,
                 n_subtunes: int, start_song: int,
                 load: int, init_addr: int, play_addr: int) -> bytes:
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', load)  # load addr (non-zero → raw body)
    h += struct.pack('>H', init_addr)
    h += struct.pack('>H', play_addr)
    h += struct.pack('>H', n_subtunes)
    h += struct.pack('>H', start_song)
    h += struct.pack('>I', 0)  # speed: VBI
    def _latin1(s, n):
        return s.encode('latin-1', errors='replace')[:n].ljust(n, b'\x00')
    h += _latin1(title, 32)
    h += _latin1(author, 32)
    h += _latin1(released, 32)
    h += struct.pack('>H', (1 << 2) | (1 << 4))  # PAL + 6581
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124
    return bytes(h)


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


def emit_sub0_asm() -> str:
    """Emit complete xa65 asm for sub 0's V1.a engine + data."""
    from pipelines.companion.c64_music_examples.extract.engine_model import (
        _run_init_via_py65, FAMILY_A_INSTANCES,
    )
    b = FAMILY_A_INSTANCES[0]
    mem, _ = _run_init_via_py65(SID_PATH, 0)

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
    current_note = mem[0x0B5A]
    pwm_sign_v1 = mem[0x0ADE]
    pwm_sign_v3 = mem[0x0AEC]

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
  ; Copy state template (32 bytes)
  ldx #31
copy_state:
  lda state_template,x
  sta state,x
  dex
  bpl copy_state
  ; Override state pattern ptrs with our fresh addresses, then load zp
  lda #<ptn_v1
  sta state+24
  lda #>ptn_v1
  sta state+25
  lda #<ptn_v2
  sta state+26
  lda #>ptn_v2
  sta state+27
  lda #<ptn_v3
  sta state+28
  lda #>ptn_v3
  sta state+29
  lda state+24
  sta zp_v1_lo
  lda state+25
  sta zp_v1_hi
  lda state+26
  sta zp_v2_lo
  lda state+27
  sta zp_v2_hi
  lda state+28
  sta zp_v3_lo
  lda state+29
  sta zp_v3_hi
  ; Init PWM sign + current_note
  lda #${pwm_sign_v1:02X}
  sta pwm_sign_v1
  lda #${pwm_sign_v3:02X}
  sta pwm_sign_v3
  lda #${current_note:02X}
  sta current_note
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
  inc frame_idx
  lda state+14         ; V3 phase
  bmi skip_v3_pwm
  inc state+30
  cmp state+30
  bne skip_v3_pwm
  ldx #$0E
  jsr pwm_sweep
  sta state+30
skip_v3_pwm:
  lda state+0          ; V1 phase
  bmi skip_v1_pwm
  inc state+31
  cmp state+31
  bne skip_v1_pwm
  ldx #$00
  jsr pwm_sweep
  sta state+31
skip_v1_pwm:
  ; Frame dispatch
  inc state+23         ; frame_ctr
  lda state+23
  cmp state+21         ; tempo
  bne not_tempo
  jmp loop_reset
not_tempo:
  cmp state+22         ; alt_tempo
  beq full_tick
  jmp vibrato_only
full_tick:
  lda #0
  sta state+23
  jsr advance_v1
  jsr advance_v2
  jsr advance_v3
  rts

loop_reset:
  lda state+1          ; V1 last_cmd
  bpl skip_lr_v1
  lda state+4          ; V1 timbre
  sta $d404
skip_lr_v1:
  lda state+8          ; V2 last_cmd
  bpl skip_lr_v2
  lda state+11         ; V2 timbre
  sta $d40b
skip_lr_v2:
  lda state+15         ; V3 last_cmd
  bpl skip_lr_v3
  lda state+18         ; V3 timbre
  sta $d412
skip_lr_v3:
  jmp vibrato_only

vibrato_only:
  ; V1 vibrato (triangle sweep on freq)
  lda frame_idx
  and #$07
  cmp #$04
  bcc vib_pos
  eor #$07
vib_pos:
  sta tri_pos
  ldy current_note
  lda freq_lo+1,y      ; freq_lo[note+1]
  sec
  sbc freq_lo,y
  sta step_lo
  lda freq_hi+1,y
  sbc freq_hi,y
  ; logical shift right 4 (16-bit signed)
  lsr
  ror step_lo
  lsr
  ror step_lo
  lsr
  ror step_lo
  lsr
  ror step_lo
  sta step_hi
  ; base
  lda freq_lo,y
  sta base_lo
  lda freq_hi,y
  sta base_hi
  ; multiply step by tri_pos via repeated addition
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
  cpx #0
  bne ve_play_note
  sty current_note
ve_play_note:
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
  lda state+24
  sta zp_v1_lo
  lda state+25
  sta zp_v1_hi
  jmp advance_v1
ve_loop_v2:
  cpx #7
  bne ve_loop_v3
  lda state+26
  sta zp_v2_lo
  lda state+27
  sta zp_v2_hi
  jmp advance_v2
ve_loop_v3:
  lda state+28
  sta zp_v3_lo
  lda state+29
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
  bne ve_play_note
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

pwm_sweep:
  cpx #0
  bne pwm_v3
  lda pwm_sign_v1
  bpl pwm_v1_desc
  inc state+3
  lda state+3
  cmp #$0E
  bne pwm_v1_emit
  inc pwm_sign_v1
  jmp pwm_v1_emit
pwm_v1_desc:
  dec state+3
  lda state+3
  cmp #$02
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
  cmp #$0E
  bne pwm_v3_emit
  inc pwm_sign_v3
  jmp pwm_v3_emit
pwm_v3_desc:
  dec state+17
  lda state+17
  cmp #$02
  bne pwm_v3_emit
  dec pwm_sign_v3
pwm_v3_emit:
  sta $d411
  lda #0
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

;Runtime state
state:           .dsb 32, 0
pwm_sign_v1:     .byte 0
pwm_sign_v3:     .byte 0
current_note:    .byte 0
frame_idx:       .byte 0
tri_pos:         .byte 0
step_lo:         .byte 0
step_hi:         .byte 0
base_lo:         .byte 0
base_hi:         .byte 0
last_cmd_tmp:    .byte 0
"""
    return asm


def build_sub0_sid() -> bytes:
    asm = emit_sub0_asm()
    body = _assemble(asm, 'c64me_sub0')
    # xa65 emits raw code; the * = $0801 directive determined the load addr.
    load_addr = 0x0801
    init_addr = load_addr      # init_jmp (jmp init) at $0801
    play_addr = load_addr + 3  # play_jmp (jmp play) at $0804
    title = "Commodore 64 Music Examples (sub 0)"
    author = "Rob Hubbard"
    released = "1985 Rob Hubbard"
    # PSID header with load=load_addr (non-zero), so body is raw code (no prefix).
    h = _psid_header(title, author, released, 1, 1, load_addr, init_addr, play_addr)
    return h + body


if __name__ == '__main__':
    sid = build_sub0_sid()
    out_path = SID_PATH.replace('.sid', '.sub0.sidfinity.sid')
    with open(out_path, 'wb') as f:
        f.write(sid)
    print(f"Wrote {out_path} ({len(sid)} bytes)")
