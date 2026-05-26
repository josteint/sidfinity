"""Companion engine codegen — byte-exact rebuild of Up_up_and_Away.sid.

Emits a 6502 player that matches the per-frame SID register write
stream of Hubbard's Companion-extended engine. The register stream
is what verify_all checks; binary layout differs from the original
(we load at $1000 by default) but per-frame writes match.

Engine model (see src/Companion/docs/engine_model_derived.md):
  - 3 voices, locked timbre per voice (loaded from per-subtune template)
  - Two tempo dividers per subtune: gate_off_tick + note_load_tick
  - Global V3 PW_LO += 4 every other frame (hardcoded sweep)
  - Note byte $00..$7F: pitch (octave<<4)|semitone, plays + gates on
  - Note byte $80+pitch (low 7 != $0C/$0D): play pitch + schedule
    early release
  - Note byte $8C: rest (gate off, no pitch change)
  - Note byte $8D: same; if voice == V3, end song (vol = 0)
"""

from __future__ import annotations

import os
import struct
import subprocess

from pipelines.companion.config import CFG
from pipelines.companion.extract import extract_all, SubtuneData

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XA = os.path.join(ROOT, 'tools', 'xa65', 'xa', 'xa')

LOAD = 0x1000


# Engine asm template — load at $1000, init=$1000, play=$1003.
# Uses zp $E0..$E5 for per-voice orderlist base pointers, and $C6C0+
# for state block (32 bytes) to roughly mirror the original layout.
ENGINE = r"""
; ZP variables for orderlist pointers (one per voice).
ord_lo_v1 = $E0
ord_hi_v1 = $E1
ord_lo_v2 = $E2
ord_hi_v2 = $E3
ord_lo_v3 = $E4
ord_hi_v3 = $E5
sub_idx   = $E6           ; current subtune (0..4)

; State block (32 bytes, mirrors original $C6C0..$C6DF layout).
v_state    = $C6C0
g_tempo_ctr  = $C6D7      ; +23 within v_state
g_pwm_ctr    = $C6DE      ; +30 within v_state
g_song_alive = $C7A1

* = $1000
        jmp init
        jmp play

; ----- init -----
init:   sta sub_idx
        ; Each subtune's 32-byte template lives adjacent to its V3
        ; orderlist (per-subtune block layout). We dispatch by the
        ; subtune-indexed tmpl_lo/tmpl_hi tables.
        ldx sub_idx
        lda tmpl_lo,x
        sta tcopy_src+1
        lda tmpl_hi,x
        sta tcopy_src+2
        ldx #0
tcopy_src: lda $FFFF,x      ; OPERAND patched above to template base ($FFFF placeholder forces 3-byte absolute encoding so the patch lands on the operand bytes — xa65 would shrink $00xx to 2-byte zp,x form)
        sta v_state,x
        inx
        cpx #32
        bne tcopy_src

        ; Load per-subtune orderlist base pointers into zp.
        ldx sub_idx
        lda ord_v1_lo,x
        sta ord_lo_v1
        lda ord_v1_hi,x
        sta ord_hi_v1
        lda ord_v2_lo,x
        sta ord_lo_v2
        lda ord_v2_hi,x
        sta ord_hi_v2
        lda ord_v3_lo,x
        sta ord_lo_v3
        lda ord_v3_hi,x
        sta ord_hi_v3

        ; SID filter setup.
        lda sub_fcHi,x
        sta $D416
        lda #0
        sta $D417
        lda sub_vol,x
        sta $D418

        ; Mark song alive.
        lda #1
        sta g_song_alive
        rts

; ----- play -----
play:   ; Global PWM counter (toggles 0/1 each frame; on 1→0 transition,
        ; V3.PW_LO += 4 and write SID).
        inc g_pwm_ctr
        lda g_pwm_ctr
        cmp #$01
        bne pwm_done
        lda #0
        sta g_pwm_ctr
        lda v_state+16        ; V3 pw_lo (state offset 14+2)
        ; NOTE — no `clc`. The CMP above leaves C=1 (since A==#$01);
        ; the original engine relies on this and adds 5 per sweep step.
        adc #4
        sta v_state+16
        sta $D410             ; V3_PW_LO
pwm_done:

        ; NOTE — no song_alive check. The original engine doesn't
        ; check $C7A1 in its play loop; it keeps processing notes
        ; even after V3's $8D fires (the song just goes silent
        ; because vol = 0 was written). To match per-frame writes
        ; we have to do the same.
        inc g_tempo_ctr
        lda g_tempo_ctr
        cmp v_state+21        ; gate_off_tick
        bne not_gate_off
        ldx #0
        jsr maybe_gate_off
        ldx #7
        jsr maybe_gate_off
        ldx #14
        jsr maybe_gate_off
        jmp play_done

not_gate_off:
        cmp v_state+22        ; note_load_tick
        bne play_done
        ; Reset counter, advance each voice's orderlist by 1.
        lda #0
        sta g_tempo_ctr
        ; V1
        ldx #0
        ldy v_state+0
        inc v_state+0
        lda (ord_lo_v1),y
        tay
        jsr proc_note
        ; V2
        ldx #7
        ldy v_state+7
        inc v_state+7
        lda (ord_lo_v2),y
        tay
        jsr proc_note
        ; V3
        ldx #14
        ldy v_state+14
        inc v_state+14
        lda (ord_lo_v3),y
        tay
        jsr proc_note
play_done:
        rts

; ----- maybe_gate_off — X = voice offset (0/7/14) -----
maybe_gate_off:
        lda v_state+1,x
        bmi do_gate_off
        rts
do_gate_off:
        lda v_state+4,x       ; ctrl_noGate
        sta $D404,x           ; V_CTRL = ctrl with gate=0
        lda #0
        sta v_state+1,x
        rts

; ----- proc_note — X = voice offset (0/7/14), Y = note byte -----
proc_note:
        tya
        and #$80
        beq proc_normal
        ; Bit 7 set — save flag, check sentinels.
        sta v_state+1,x       ; flag = $80
        tya
        and #$7F
        tay
        cpy #$0C
        beq proc_rest
        cpy #$0D
        beq proc_end_or_rest
        ; Else fall through — Y = pitch (low 7), play normally.
proc_normal:
        lda freq_hi,y
        sta $D401,x           ; V_FREQ_HI
        lda freq_lo,y
        sta $D400,x           ; V_FREQ_LO
        ; Skip pw_lo for V3 — V3's PW_LO is driven only by the global sweep.
        cpx #14
        beq skip_pwlo
        lda v_state+2,x
        sta $D402,x           ; V_PW_LO
skip_pwlo:
        lda v_state+3,x
        sta $D403,x           ; V_PW_HI
        lda v_state+5,x
        sta $D405,x           ; V_AD
        lda v_state+6,x
        sta $D406,x           ; V_SR
        lda v_state+4,x       ; ctrl_noGate
        ora #$01              ; gate on
        sta $D404,x           ; V_CTRL
        rts
proc_rest:
        lda v_state+4,x       ; ctrl_noGate (gate=0)
        sta $D404,x
        rts
proc_end_or_rest:
        lda v_state+4,x
        sta $D404,x
        cpx #14
        bne pend_done
        lda #0
        sta g_song_alive
        sta $D418             ; vol = 0
pend_done:
        rts
"""


def _emit_data(subtunes: list[SubtuneData], freq_hi: bytes, freq_lo: bytes) -> str:
    """Emit the data section.

    Layout — chosen so the engine's "keep reading past $8D" behavior
    reproduces the original byte stream from the per-subtune block
    layout alone (no per-voice trailing bytes needed in the USF):

        freq_hi (128) + freq_lo (128)
        sub_<i>_v1_ord  ──┐  reading past V1's $8D falls into V2
        sub_<i>_v2_ord  ──┤  reading past V2's $8D falls into V3
        sub_<i>_v3_ord  ──┤  reading past V3's $8D falls into template
        tmpl_<i>        ──┘  template is the per-voice init bytes
        ... repeat for each subtune ...
        dispatch tables (orderlist + template addresses, filter, vol)
    """
    lines = []

    lines.append('freq_hi:')
    for i in range(0, 128, 16):
        chunk = freq_hi[i:i + 16]
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in chunk))
    lines.append('freq_lo:')
    for i in range(0, 128, 16):
        chunk = freq_lo[i:i + 16]
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in chunk))

    def hex16(bs):
        out = []
        for i in range(0, len(bs), 16):
            chunk = bs[i:i + 16]
            out.append('        .byt ' + ','.join(f'${b & 0xFF:02X}' for b in chunk))
        return out

    for s in subtunes:
        tmpl = bytes([
            s.v1_state.pos, s.v1_state.gate_off_flag,
            s.v1_state.pw_lo, s.v1_state.pw_hi,
            s.v1_state.ctrl_noGate, s.v1_state.ad, s.v1_state.sr,
            s.v2_state.pos, s.v2_state.gate_off_flag,
            s.v2_state.pw_lo, s.v2_state.pw_hi,
            s.v2_state.ctrl_noGate, s.v2_state.ad, s.v2_state.sr,
            s.v3_state.pos, s.v3_state.gate_off_flag,
            s.v3_state.pw_lo, s.v3_state.pw_hi,
            s.v3_state.ctrl_noGate, s.v3_state.ad, s.v3_state.sr,
            s.gate_off_tick, s.note_load_tick, s.init_tempo_counter,
            # 6 zero bytes — original engine kept self-modifying-code
            # orderlist address bytes here; we use zp pointers, so 0.
            0, 0, 0, 0, 0, 0,
            s.init_pwm_ctr, s.init_pwm_ctr_2,
        ])
        assert len(tmpl) == 32

        def pad(p):
            return [p.byte] * p.count if p.count else []

        lines.append(f'; ----- subtune {s.index} block -----')
        lines.append(f'ord_s{s.index}_v1:')
        lines.extend(hex16(bytes(s.orderlist_v1) + bytes(pad(s.v1_padding))))
        lines.append(f'ord_s{s.index}_v2:')
        lines.extend(hex16(bytes(s.orderlist_v2) + bytes(pad(s.v2_padding))))
        lines.append(f'ord_s{s.index}_v3:')
        lines.extend(hex16(bytes(s.orderlist_v3) + bytes(pad(s.v3_padding))))
        lines.append(f'tmpl_s{s.index}:')
        lines.extend(hex16(tmpl))

    lines.append('; ----- dispatch tables -----')
    lines.append('ord_v1_lo: .byt ' + ','.join(f'<ord_s{i}_v1' for i in range(5)))
    lines.append('ord_v1_hi: .byt ' + ','.join(f'>ord_s{i}_v1' for i in range(5)))
    lines.append('ord_v2_lo: .byt ' + ','.join(f'<ord_s{i}_v2' for i in range(5)))
    lines.append('ord_v2_hi: .byt ' + ','.join(f'>ord_s{i}_v2' for i in range(5)))
    lines.append('ord_v3_lo: .byt ' + ','.join(f'<ord_s{i}_v3' for i in range(5)))
    lines.append('ord_v3_hi: .byt ' + ','.join(f'>ord_s{i}_v3' for i in range(5)))
    lines.append('tmpl_lo:   .byt ' + ','.join(f'<tmpl_s{i}'   for i in range(5)))
    lines.append('tmpl_hi:   .byt ' + ','.join(f'>tmpl_s{i}'   for i in range(5)))
    lines.append('sub_fcHi:  .byt ' + ','.join(f'${s.filter_cutoff_hi:02X}' for s in subtunes))
    lines.append('sub_vol:   .byt ' + ','.join(f'${s.vol_filter:02X}' for s in subtunes))

    return '\n'.join(lines) + '\n'


def build_sid(out_path: str) -> str:
    """Build the Companion rebuild SID."""
    subtunes, freq_hi, freq_lo = extract_all()
    asm = ENGINE + '\n' + _emit_data(subtunes, freq_hi, freq_lo) + '\n'

    src = '/tmp/companion_build.s'
    obj = '/tmp/companion_build.bin'
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        code = f.read()

    # PSID header
    with open(CFG.sid_path, 'rb') as f:
        parent_hdr = f.read(124)

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD + 3)
    h += struct.pack('>H', 5)               # num_songs
    h += struct.pack('>H', 1)               # start_song
    h += struct.pack('>I', 0)               # speed
    h += parent_hdr[22:54]                  # title
    h += parent_hdr[54:86]                  # author
    h += parent_hdr[86:118]                 # released
    h += struct.pack('>H', 0x0014)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124

    with open(out_path, 'wb') as f:
        f.write(bytes(h) + code)
    return out_path


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/companion_uupa.sid'
    p = build_sid(out)
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
