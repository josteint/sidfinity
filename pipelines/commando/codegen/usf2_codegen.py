"""usf2_codegen.py — Phase 4: USF2 -> 6502 player -> .sid.

Builds a playable Commando SID from the clean USF2 representation (the
decoded Score + the InstrumentModels). The 6502 player is a clean
Commando engine — a faithful implementation of song_interp.py's
semantics — assembled by xa65; the USF2 data is serialised into memory
tables after the engine code.

No engineQuirks, no dynamicFreqEntries: the engine knowledge lives here
in the codegen (plumbing); the data stays abstract.

Complete for Commando: the note backbone, all effects (vibrato, PWM,
drum-slide, skydive, inc_by2, arpeggio incl. the off-table cases) and
the structured data layout — shared patterns referenced by per-voice
orderlists. Reproduces the original's instruction stream 100 % over
the whole song.

Usage:
    python3 pipelines/commando/codegen/usf2_codegen.py
    python3 pipelines/commando/codegen/usf2_codegen.py --verify
"""

from __future__ import annotations

import os
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

from pipelines.commando.extract.engine_model import extract  # noqa: E402
from pipelines.commando.extract.inst_generalize import decode_all  # noqa: E402
from pipelines.commando.extract.inst_interp import subtune_resetspd  # noqa: E402

SID_PATH = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_original.sid')
XA = os.path.join(ROOT, 'tools', 'xa65', 'xa', 'xa')
OUT_SID = '/tmp/usf2_commando.sid'

LOAD = 0x1000

# Effects implemented by the 6502 engine so far (verification enables
# exactly this subset in song_interp).
ENGINE_FX = {'skydive', 'arp', 'vibrato', 'pwm', 'arp_offtable'}

# ---------------------------------------------------------------------------
# 6502 engine. A faithful implementation of song_interp.py's frame loop.
# Data labels (sidtab, insttab, pwacc, freqtab, patterns + pataddr,
# per-voice orderlists, statebuf) are appended by the codegen.
#
# instrument table row (16 bytes): init_ctrl, init_pw_lo, init_pw_hi,
# init_ad, init_sr, hr_ctrl, fx_flags, then 9 effect-param bytes.
# fx_flags bit0 = freqSlide (skydive).
# ---------------------------------------------------------------------------

ENGINE = r"""
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

* = $1000
        jmp init
        jmp play

init:
        ldx #2
ini1:   lda #0
        sta v_dur,x
        sta v_pwdir,x
        sta v_pwperiod,x
        sta v_instr,x
        sta v_orderpos,x
        sta v_ended,x
        jsr set_patptr       ; v_patptr,x = first pattern of orderlist X
        dex
        bpl ini1
        lda #0
        sta end_phase
        sta speed_ctr
        lda #$ff
        sta frame_ctr
        ldx #$18
ini2:   lda #0
        sta $d400,x
        dex
        bpl ini2
        lda #$0f
        sta $d418
        rts

play:
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
        dec speed_ctr
        bpl notick
        lda #RESETSPD
        sta speed_ctr
        lda #1
        sta is_tick
        jmp voices
notick: lda #0
        sta is_tick
voices:
        ldx #2
pvloop: jsr proc_voice
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
        rts

proc_voice:
        lda v_ended,x
        bne pv_endret        ; voice hit $FE - it no longer plays
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
pv_endret:
        rts

calc_instoff:
        lda v_instr,x
        and #$3f
        asl
        sta pw_idx           ; inst*2  (index into pwacc)
        asl
        asl
        asl
        sta instoff          ; inst*16 (index into insttab)
        rts

; load_note - advance voice X to its next note. Walks the current
; pattern (5-byte records); the $FF pattern-end marker advances the
; orderlist. The instrument carries across notes/patterns/the loop -
; it is kept in v_instr and only replaced when a note has an
; instrument byte (bit7 clear).
load_note:
ln_read:
        lda v_patlo,x
        sta notep
        lda v_pathi,x
        sta notep+1
        ldy #0
        lda (notep),y        ; pitch, or $FF = pattern end
        cmp #$ff
        bne ln_have
        inc v_orderpos,x     ; pattern ended - next orderlist entry
        jsr set_patptr
        lda v_ended,x        ; set_patptr may have hit the $FE marker
        bne ln_endret
        jmp ln_read
ln_endret:
        rts
ln_have:
        sta f_lo             ; stash byte 0 (pitch) - stored below only
                             ; if this is not a tie note
        iny
        lda (notep),y        ; byte 1 = durfield | no_release<<7
        pha
        and #$1f
        sta v_dur,x
        sta v_durfield,x
        pla
        and #$80
        sta v_norel,x
        iny
        lda (notep),y        ; byte 2 = instrument (b7 no-inst, b6 tie)
        sta pwm_tmp
        and #$40             ; a tie note keeps the live pitch; only a
        bne ln_keeppitch     ; non-tie note sets a new one
        lda f_lo
        sta v_pitch,x
ln_keeppitch:
        lda pwm_tmp
        and #$80
        bne ln_keepinst
        lda pwm_tmp
        and #$3f             ; note carries an instrument - take it
        jmp ln_setinst
ln_keepinst:
        lda v_instr,x
        and #$3f             ; no instrument byte - keep the carried one
ln_setinst:
        sta pwm_tmp+1
        lda pwm_tmp
        and #$40             ; tie bit
        ora pwm_tmp+1
        sta v_instr,x
        ldy #3
        lda (notep),y        ; byte 3 = Hubbard note_idx
        sta v_hubidx,x
        iny
        lda (notep),y        ; byte 4 = drum/porta trigger
        sta v_drumtrig,x
        lda #0
        sta v_tick,x
        lda v_patlo,x        ; advance v_patptr past this 5-byte record
        clc
        adc #5
        sta v_patlo,x
        bcc ln_nowrap
        inc v_pathi,x
ln_nowrap:
        lda v_patlo,x        ; peek the next record for the seq_idx rule
        sta notep
        lda v_pathi,x
        sta notep+1
        ldy #0
        lda (notep),y
        cmp #$ff
        bne ln_seqcur
        jsr next_orderidx    ; last note of pattern - seq_idx pre-increments
        sta v_seqidx,x
        rts
ln_seqcur:
        lda v_orderpos,x
        sta v_seqidx,x
        rts

; set_patptr - point v_patptr,x at the pattern named by orderlist
; entry v_orderpos,x. The $FF terminator wraps v_orderpos to
; orderLoop,x; the $FE terminator ends the voice (v_ended). Clobbers
; A and Y; preserves X.
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
        sta v_ended,x
        rts
sp_have:
        tay                  ; Y = pattern index
        lda pataddr_lo,y
        sta v_patlo,x
        lda pataddr_hi,y
        sta v_pathi,x
        rts

; next_orderidx - the orderlist index the next pattern will occupy:
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
        rts

; note_start - write the note-start register block for voice X.
; common fields (ctrl/ad/sr from insttab, pw from the accumulator) are
; loaded into temps first; then tie vs full diverge.
note_start:
        ldy instoff
        lda insttab+0,y
        sta i_ctrl
        lda insttab+3,y
        sta i_ad
        lda insttab+4,y
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
        ldy sidoff
        sta $d404,y
        jmp ns_pwadsr
ns_full:
        ; freq - pitch 104 (inst 4) reads off-table into ctrl_byte
        lda v_pitch,x
        cmp #104
        beq ns_offtab
        asl
        tay
        lda freqtab,y
        sta f_lo
        lda freqtab+1,y
        sta f_hi
        jmp ns_havefreq
ns_offtab:
        lda v_ctrlbyte+0     ; $54F8 = ctrl_byte[0]
        sta f_lo
        lda v_ctrlbyte+1     ; $54F9 = ctrl_byte[1]
        sta f_hi
ns_havefreq:
        lda f_hi
        sta v_slide,x        ; seed the skydive/drum-slide freq_hi
        lda f_lo
        sta v_slidelo,x      ; seed the drum-slide freq_lo
        lda i_ctrl
        sta v_ctrlbyte,x     ; update ctrl_byte AFTER the off-table read
        ldy sidoff
        lda f_hi
        sta $d401,y
        lda f_lo
        sta $d400,y
        lda i_ctrl
        sta $d404,y
ns_pwadsr:
        ldy sidoff
        lda i_pwlo
        sta $d402,y
        lda i_pwhi
        sta $d403,y
        lda i_ad
        sta $d405,y
        lda i_sr
        sta $d406,y
        rts

; hr_writes - hard-restart block, ctrl=hr_ctrl ad=0 sr=0.
hr_writes:
        ldy instoff
        lda insttab+5,y
        ldy sidoff
        sta $d404,y
        lda #0
        sta $d405,y
        sta $d406,y
        rts

; do_effects - effects in engine order vibrato,pwm,drumslide,skydive,arp.
do_effects:
        lda #0
        sta vib_carry
        jsr fx_vibrato
        jsr fx_pwm
        jsr fx_drumslide
        jsr fx_skydive
        jsr fx_incby2
        jmp fx_arp

; fx_drumslide - per-note portamento ($52B3-$52F9), effect #3. A note
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
fxd_ret: rts

; fx_incby2 - bit1. odd-frame +2 on the shared slide value, write old.
fx_incby2:
        ldy instoff
        lda insttab+6,y
        and #$02
        beq fxi_ret
        lda v_durfield,x
        cmp #3
        bcc fxi_ret
        lda frame_ctr
        and #$01
        beq fxi_ret
        lda v_slide,x
        beq fxi_ret
        ldy sidoff
        lda v_slide,x
        sta $d401,y          ; write OLD slide value
        lda v_slide,x
        clc
        adc #$02
        sta v_slide,x
fxi_ret: rts

; fx_pwm - bit4. linear or bidirectional PWM. The pw accumulators
; (pwacc) are per-instrument shared state - see song_interp._pwm.
fx_pwm:
        ldy instoff
        lda insttab+8,y      ; pwm_mode  0=none 1=linear 2=bidir
        bne fxp_on
        rts
fxp_on:
        cmp #$01
        bne fxp_bidir
        ldy instoff
        lda insttab+9,y      ; linear - pw_lo += speed + vib_carry
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        clc
        adc pwm_tmp
        clc
        adc vib_carry
        sta pwacc,y
        ldy sidoff
        sta $d402,y
        rts
fxp_bidir:
        dec v_pwperiod,x
        bpl fxp_ret          ; period counter not expired
        ldy instoff
        lda insttab+10,y     ; reload period
        sta v_pwperiod,x
        lda v_pwdir,x
        bne fxp_fall
        ldy instoff          ; rising
        lda insttab+9,y      ; step
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
        cmp insttab+12,y     ; hi_bound
        bne fxp_wr
        lda #$01
        sta v_pwdir,x
        jmp fxp_wr
fxp_fall:
        ldy instoff
        lda insttab+9,y      ; step
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
        cmp insttab+11,y     ; lo_bound
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
        rts

; fx_vibrato - bit3. triangle LFO on freq, disassembly $51C1-$522D.
; leaves vib_carry = the 6502 carry the section hands to the PWM add.
fx_vibrato:
        ldy instoff
        lda insttab+6,y
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
        lda insttab+7,y      ; vib_depth
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
        cmp #$06
        bcc fxv_wr           ; dur < 6 -> no add (carry left = 0)
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
        rts

; fx_skydive - bit0. freq_hi slide + ctrl, see song_interp._skydive.
fx_skydive:
        ldy instoff
        lda insttab+6,y
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
        lda insttab+5,y      ; not-start ctrl = hr_ctrl
        bne fxs_w
        lda #$80
fxs_w:  ldy sidoff
        sta $d404,y
        dec v_slide,x
        rts
fxs_ns: lda #$80             ; note-start subphase ctrl = $80
        ldy sidoff
        sta $d404,y
fxs_ret: rts

; fx_arp - bit2 arpeggio. alternate pitch / pitch+12 by frame parity.
; idx under 96 is a normal freq-table lookup. idx 96 and up is
; off-table - in the original the lookup overflows the 96-entry freq
; table into engine state; reproduced cleanly here via statebuf, a
; mirror of the $54E8.. state region assembled on demand.
fx_arp:
        ldy instoff
        lda insttab+6,y
        and #$04
        beq fxa_ret
        lda frame_ctr
        and #$01
        beq fxa_even
        lda v_pitch,x
        clc
        adc #$0c
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
fxa_ret: rts

; build_statebuf - assemble the $54E8.. engine-state mirror that the
; off-table arpeggio indexes. Slots 0-2 (v_sid_off) and the gaps are
; pre-set in the data; this fills the live per-voice slots. The values
; are read live (after PWM has run) - matching song_interp. Preserves
; X and Y so the caller keeps the voice index / statebuf offset.
build_statebuf:
        txa
        pha
        lda sidoff
        sta statebuf+3       ; $54EB scratch = current voice sid offset
        ldx #2
bsb1:   lda v_seqidx,x
        sta statebuf+4,x     ; $54EC seq_idx
        lda v_hubidx,x
        sta statebuf+7,x     ; $54EF note_idx
        lda v_dur,x
        sta statebuf+10,x    ; $54F2 duration
        lda v_ctrlbyte,x
        sta statebuf+16,x    ; $54F8 ctrl_byte
        lda v_pitch,x
        sta statebuf+19,x    ; $54FB pitch
        lda v_instr,x
        and #$3f
        sta statebuf+22,x    ; $54FE instr_num
        lda v_pwdir,x
        sta statebuf+40,x    ; $5510 pw_dir
        lda v_instr,x
        and #$40             ; tie -> bit6
        ora v_durfield,x
        sta statebuf+13,x    ; $54F5 note_byte
        dex
        bpl bsb1
        pla
        tax
        rts

sidtab: .byt 0, 7, 14
"""


# ---------------------------------------------------------------------------
# data serialisation
# ---------------------------------------------------------------------------

def _pattern_notes(pat_notes):
    """The 5-byte note records for one pattern: pitch, durfield,
    instrument, hub_note_idx, drum_trig.

    hub_note_idx (Hubbard's byte offset into the pattern) is
    pattern-intrinsic, so it lives in the shared pattern. The
    instrument byte keeps engine_model's bit7 (no instrument byte) and
    bit6 (tie) — the engine resolves the cross-note/pattern carry, so
    the same shared pattern is correct wherever the orderlist uses it.
    seq_idx is NOT stored: it is the orderlist position, which depends
    on where the pattern sits in the orderlist — the engine tracks it."""
    out = []
    hidx = 0
    for j, n in enumerate(pat_notes):
        nbytes = (1 if n.tie
                  else 2 if (n.instrument & 0x80) else 3)
        base = 0 if j == 0 else hidx
        is_last = j == len(pat_notes) - 1
        hidx = 0 if is_last else base + nbytes
        # byte 1 = durfield (0..31) | no_release in bit7
        durf = ((n.duration - 1) & 0x1F) | (n.drum_trig & 0x80)
        out.append((n.pitch & 0xFF, durf, n.instrument & 0xFF,
                    hidx & 0xFF, n.drum_trig & 0xFF))
    return out


def _fx_flags(m) -> int:
    return ((1 if m.freq_slide else 0) | (2 if m.inc_by2 else 0)
            | (4 if m.arpeggio else 0) | (8 if m.vibrato else 0)
            | (16 if m.pwm else 0))


def _emit_data(score, models, freq_table) -> str:
    """Emit the xa65 data section."""
    lines = []

    # instrument row (16 bytes): init_ctrl, init_pw_lo, init_pw_hi,
    # init_ad, init_sr, hr_ctrl, fx_flags, vib_depth, pwm_mode,
    # pwm_a (speed/step), pwm_period, pwm_lo, pwm_hi, then 3 spare.
    lines.append('insttab:')
    for m in models:
        vib_depth = m.vibrato.depth if m.vibrato else 0
        pwm_mode = pwm_a = pwm_period = pwm_lo = pwm_hi = 0
        if m.pwm:
            if m.pwm.mode == 'linear':
                pwm_mode, pwm_a = 1, m.pwm.speed
            else:
                pwm_mode, pwm_a = 2, m.pwm.step
                pwm_period, pwm_lo, pwm_hi = (m.pwm.period, m.pwm.lo_bound,
                                              m.pwm.hi_bound)
        row = [m.init_ctrl, m.init_pw_lo, m.init_pw_hi, m.init_ad,
               m.init_sr, m.hr_ctrl, _fx_flags(m), vib_depth,
               pwm_mode, pwm_a, pwm_period, pwm_lo, pwm_hi, 0, 0, 0]
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in row))

    # pwacc - per-instrument pw_lo/pw_hi accumulators (shared by every
    # voice playing the instrument), seeded from the table pw values.
    lines.append('pwacc:')
    for m in models:
        lines.append(f'        .byt ${m.init_pw_lo:02X},${m.init_pw_hi:02X}')

    # full table (>=96 entries) — vibrato reads freqtab[pitch+1] which
    # can run one past the 96 musical notes.
    lines.append('freqtab:')
    for f in freq_table:
        lines.append(f'        .byt ${f & 0xFF:02X},${(f >> 8) & 0xFF:02X}')

    # patterns + orderlists — Hubbard's compact layout kept structured:
    # each unique pattern is emitted once, and every voice's orderlist
    # references them by a dense slot index. collect every pattern any
    # voice uses into one dense table.
    pat_order = []                 # dense slot -> note list
    pat_slot = {}                  # orig pattern index -> dense slot
    for v in score.voices:
        for oidx in v.orderlist:
            if oidx not in pat_slot:
                pat_slot[oidx] = len(pat_order)
                pat_order.append(v.patterns.get(oidx, []))

    for slot, pat_notes in enumerate(pat_order):
        lines.append(f'pat{slot}:')
        for (p, d, ins, h, dt) in _pattern_notes(pat_notes):
            lines.append(f'        .byt ${p:02X},${d:02X},${ins:02X},'
                         f'${h:02X},${dt:02X}')
        lines.append('        .byt $FF   ; pattern end')

    npat = len(pat_order)
    lines.append('pataddr_lo: .byt '
                 + ','.join(f'<pat{s}' for s in range(npat)))
    lines.append('pataddr_hi: .byt '
                 + ','.join(f'>pat{s}' for s in range(npat)))

    for vi, v in enumerate(score.voices):
        ob = ','.join(f'${pat_slot[oidx]:02X}' for oidx in v.orderlist)
        # $FF = loop to orderLoop; $FE = end of song (no loop)
        term = '$FE' if v.stop else '$FF'
        lines.append(f'order{vi}: .byt {ob},{term}')
    lines.append('orderLo: .byt <order0,<order1,<order2')
    lines.append('orderHi: .byt >order0,>order1,>order2')
    loops = [v.loop if v.loop >= 0 else 0 for v in score.voices]
    lines.append('orderLoop: .byt ' + ','.join(f'${x:02X}' for x in loops))

    # statebuf - the $54E8.. engine-state mirror the off-table arpeggio
    # indexes. Slots 0-2 are v_sid_off (constant 0,7,14); the rest are
    # filled live by build_statebuf, with the unmapped gap bytes left 0.
    lines.append('statebuf: .byt 0,7,14')
    lines.append('        .byt ' + ','.join(['0'] * 93))
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def build(subtune: int = 0, out_path: str = OUT_SID) -> str:
    song = extract(subtune=subtune)
    models = decode_all(SID_PATH)
    from src.hubbard_emu import load_sid
    _, binary, load = load_sid(SID_PATH)
    resetspd = subtune_resetspd(subtune, binary, load)

    asm = (f'RESETSPD = {resetspd}\n'
           + ENGINE + '\n'
           + _emit_data(song.score, models, song.freq_table) + '\n')

    src = '/tmp/usf2_commando.s'
    obj = '/tmp/usf2_commando.bin'
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        code = f.read()

    # name / author / released come verbatim from the original SID —
    # this is the same tune, so it carries the same identifying
    # metadata (PSID header bytes 22..118).
    with open(SID_PATH, 'rb') as f:
        orig_hdr = f.read(124)

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD + 3)
    h += struct.pack('>H', 1)              # songs — this build holds one subtune
    h += struct.pack('>H', 1)              # startSong
    h += struct.pack('>I', 0)
    h += orig_hdr[22:118]                  # name + author + released (3x32)
    h += struct.pack('>H', 0x0014)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124

    with open(out_path, 'wb') as f:
        f.write(bytes(h) + code)
    return out_path


# ---------------------------------------------------------------------------
# verification — rebuilt SID vs song_interp with a matching effect subset
# ---------------------------------------------------------------------------

def verify(sid_path: str, enabled: set, subtune: int = 0,
           n_frames: int = 1500) -> None:
    from pipelines.commando.extract.inst_program import capture, REG_NAMES
    from pipelines.commando.extract.song_interp import SongInterp

    cap = capture(sid_path, n_frames=n_frames, subtune=subtune)
    si = SongInterp(SID_PATH, subtune)
    si.fx_vibrato = 'vibrato' in enabled
    si.fx_pwm = 'pwm' in enabled
    si.fx_skydive = 'skydive' in enabled
    si.fx_arp = 'arp' in enabled
    # the engine does not yet do the off-table (inst 7) arpeggio
    si.fx_arp_offtable = 'arp_offtable' in enabled

    match = 0
    first = None
    by_voice: dict[tuple, int] = {}
    for k in range(n_frames):
        want = si.step()
        got = cap.raw_frames[k]
        if got == want:
            match += 1
            continue
        if first is None:
            first = (k, want, got)
        diff = set(want) ^ set(got)
        vs = tuple(sorted({['V1', 'V2', 'V3'][o // 7] for o, _ in diff}))
        by_voice[vs] = by_voice.get(vs, 0) + 1

    feats = '+'.join(sorted(enabled)) or 'backbone'
    print(f'vs song_interp [{feats}]: {match}/{n_frames} frames exact '
          f'({100.0 * match / n_frames:.1f}%)')
    for vs, c in sorted(by_voice.items(), key=lambda x: -x[1]):
        print(f'  {",".join(vs)}: {c}')
    if first:
        k, want, got = first

        def fmt(fw):
            return ' '.join(
                f'{["V1","V2","V3"][o // 7]}.{REG_NAMES[o % 7]}={v:02X}'
                for o, v in fw) or '-'
        print(f'  first diff at frame {k}:')
        print(f'    song_interp: {fmt(want)}')
        print(f'    rebuilt SID: {fmt(got)}')


def main(argv: list[str]) -> None:
    path = build()
    print(f'built {path}  ({os.path.getsize(path)} bytes)')
    if '--verify' in argv:
        verify(path, ENGINE_FX)


if __name__ == '__main__':
    main(sys.argv[1:])
