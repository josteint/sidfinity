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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

from pipelines.hubbard.inst_generalize import decode_all  # noqa: E402

XA = os.path.join(ROOT, 'tools', 'xa65', 'xa', 'xa')
OUT_SID = '/tmp/usf2_build.sid'

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

* = $1000
        jmp init
        jmp play

; init - A = subtune number. A under 3 is a music subtune; A 3 and up
; is a sound effect (A-3 = the SFX index).
init:
        cmp #$03
        bcc init_music
        sec
        sbc #$03
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
        ldx #2               ; seed the freq-table-overlap variables
iniov:  lda ovseed,x
        sta v_ctrlbyte,x
        lda ovseed+3,x
        sta v_pwperiod,x
        lda ovseed+6,x
        sta v_pwdir,x
        dex
        bpl iniov
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
        ldx #2
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
        rts

proc_voice:
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
        rts

; load_note is supplied by the note codec (see note_codec.py) — the
; engine calls it; the codec owns the pattern byte format and its
; decoder. set_patptr / next_orderidx below are codec-agnostic.

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
        ldy #FREEZE_ON_STOP
        bne sps_freeze
        sta v_ended,x
        rts
sps_freeze:
        sta v_frozen,x
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
        rts

; hr_writes - hard-restart block, ctrl=hr_ctrl ad=0 sr=0.
hr_writes:
        ldy instoff
        lda it_hrctrl,y
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
        lda it_fx,y
        and #$02
        beq fxi_ret
        lda v_durfield,x
        cmp #3
        bcc fxi_ret
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
fxi_ret: rts

; fx_pwm - bit4. linear or bidirectional PWM. The pw accumulators
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
        rts

; fx_vibrato - bit3. triangle LFO on freq, disassembly $51C1-$522D.
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
        rts

; fx_skydive - bit0. freq_hi slide + ctrl, see song_interp._skydive.
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
fxs_ret: rts

; fx_arp - bit2 arpeggio. alternate pitch / pitch+12 by frame parity.
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
        and #$01
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

; ============================ sound effects ===========================
; A SFX is a 2-voice register snapshot plus a freq-table pitch sweep,
; driven by a 32-byte record (sfxdata). See pipelines/commando/extract/
; sfx.py for the engine derivation.

; init_sfx - set up sound effect sfx_idx. Builds the record pointer,
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
        rts

; sfx_play - one frame of the sound-effect engine. The first frame
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
        rts

; sfx_step - one sweep step. Writes V1/V2 freq from the freq table and
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
        rts

sidtab: .byt 0, 7, 14
"""


# ---------------------------------------------------------------------------
# data serialisation
# ---------------------------------------------------------------------------

def _fx_flags(m) -> int:
    return ((1 if m.freq_slide else 0) | (2 if m.inc_by2 else 0)
            | (4 if m.arpeggio else 0) | (8 if m.vibrato else 0)
            | (16 if m.pwm else 0))


def _pattern_pool(scores):
    """Dense, globally-shared pattern pool. Returns (pat_order, pat_slot):
    pat_order[slot] = note list; pat_slot[orig pattern index] = slot."""
    pat_order, pat_slot = [], {}
    for score in scores:
        for v in score.voices:
            for oidx in v.orderlist:
                if oidx not in pat_slot:
                    pat_slot[oidx] = len(pat_order)
                    pat_order.append(v.patterns.get(oidx, []))
    return pat_order, pat_slot


def _emit_data(scores, models, freq_bytes, resetspds, sfx_list,
               pat_slot, pat_bytes, codec_extra) -> str:
    """Emit the xa65 data section for a multi-subtune build.

    `scores` is one Score per packed music subtune; `sfx_list` is the
    16 sound effects; `codec` is the note packer. Instruments, the freq
    table and the pattern pool are shared; orderlists, loop points and
    tempo are per-subtune, selected by `init` from the subOrder* /
    subResetspd tables."""
    lines = []

    # instrument data — column-major: one table per field, indexed by
    # the instrument NUMBER. Row-major (inst*16) overflowed the 8-bit
    # index past 15 instruments (Monty has 20).
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
                pwm_period, pwm_lo, pwm_hi = (m.pwm.period, m.pwm.lo_bound,
                                              m.pwm.hi_bound)
        irows.append([m.init_ctrl, 0, 0, m.init_ad, m.init_sr, m.hr_ctrl,
                      _fx_flags(m), vib_depth, pwm_mode, pwm_a,
                      pwm_period, pwm_lo, pwm_hi, vib_onset])
    for idx, name in ((0, 'it_ctrl'), (3, 'it_ad'), (4, 'it_sr'),
                      (5, 'it_hrctrl'), (6, 'it_fx'), (7, 'it_vibdepth'),
                      (8, 'it_pwmode'), (9, 'it_pwa'), (10, 'it_pwperiod'),
                      (11, 'it_pwlo'), (12, 'it_pwhi'), (13, 'it_onset')):
        lines.append(f'{name}: .byt '
                     + ','.join(f'${r[idx]:02X}' for r in irows))

    # pwseed - the per-instrument pw_lo/pw_hi seeds. pwacc is the live
    # accumulator (shared by every voice playing the instrument); init
    # copies pwseed -> pwacc so each subtune starts fresh.
    lines.append('pwseed:')
    for m in models:
        lines.append(f'        .byt ${m.init_pw_lo:02X},${m.init_pw_hi:02X}')
    lines.append('pwacc: .byt ' + ','.join(['0'] * (2 * len(models))))

    # the freq table, emitted as raw bytes — the music reads it as
    # 16-bit entries, the SFX sweep walks it byte-wise and overflows
    # past the musical notes into the engine-state region.
    lines.append('freqtab:')
    for i in range(0, len(freq_bytes), 16):
        chunk = freq_bytes[i:i + 16]
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in chunk))

    # the overlap seed — v_ctrl / pwm_period / pwm_dir initial values.
    # The engine's per-voice variables sit past the 96-entry freq table;
    # init copies these load-time bytes into the zero-page mirrors so an
    # off-table read (or a counter's first DEC) sees the right value.
    ov = ([freq_bytes[208 + i] for i in range(3)]      # v_ctrl   $84D0,x
          + [freq_bytes[229 + i] for i in range(3)]    # pwm_period $84E5,x
          + [freq_bytes[232 + i] for i in range(3)])   # pwm_dir  $84E8,x
    lines.append('ovseed: .byt ' + ','.join(f'${b:02X}' for b in ov))

    # patterns — each unique pattern emitted once; orderlists reference
    # them by a dense slot. pattern indices are global, so the pool is
    # shared by all packed subtunes. The note codec serialises each
    # pattern (byte 0 = note count); the format is the codec's choice.
    for slot, blob in enumerate(pat_bytes):
        lines.append(f'pat{slot}:')
        for i in range(0, len(blob), 16):
            chunk = blob[i:i + 16]
            lines.append('        .byt ' + ','.join(f'${b:02X}' for b in chunk))
    if codec_extra:
        lines.append(codec_extra)

    npat = len(pat_bytes)
    lines.append('pataddr_lo: .byt '
                 + ','.join(f'<pat{s}' for s in range(npat)))
    lines.append('pataddr_hi: .byt '
                 + ','.join(f'>pat{s}' for s in range(npat)))

    # per-subtune orderlists ($FF = loop to orderLoop, $FE = end of song)
    for si, score in enumerate(scores):
        for vi, v in enumerate(score.voices):
            ob = ','.join(f'${pat_slot[oidx]:02X}' for oidx in v.orderlist)
            term = '$FE' if v.stop else '$FF'
            lines.append(f'order_{si}_{vi}: .byt {ob},{term}')

    # subOrder* — 3 entries per subtune (one per voice); init copies the
    # selected subtune's row into the live orderLo/Hi/Loop arrays.
    los, his, loops = [], [], []
    for si, score in enumerate(scores):
        for vi, v in enumerate(score.voices):
            los.append(f'<order_{si}_{vi}')
            his.append(f'>order_{si}_{vi}')
            loops.append(f'${(v.loop if v.loop >= 0 else 0):02X}')
    lines.append('subOrderLo: .byt ' + ','.join(los))
    lines.append('subOrderHi: .byt ' + ','.join(his))
    lines.append('subOrderLoop: .byt ' + ','.join(loops))
    lines.append('subResetspd: .byt '
                 + ','.join(f'${r:02X}' for r in resetspds))

    # live per-voice orderlist selection (filled by init)
    lines.append('orderLo: .byt 0,0,0')
    lines.append('orderHi: .byt 0,0,0')
    lines.append('orderLoop: .byt 0,0,0')

    # statebuf - the $54E8.. engine-state mirror the off-table arpeggio
    # indexes. Slots 0-2 are v_sid_off (constant 0,7,14); the rest are
    # filled live by build_statebuf, with the unmapped gap bytes left 0.
    lines.append('statebuf: .byt 0,7,14')
    lines.append('        .byt ' + ','.join(['0'] * 93))

    # sound-effect records — 32 bytes each: V1[7], V2[7], start, end,
    # rate, flags (bit0 direction, bit1 skip-V1, bit2 skip-both),
    # v2_byte_offset, gate (bit7/6 toggle V1/V2). See sfx_play.
    lines.append('sfxdata:')
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
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in rec))
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def build(config, out_path: str = OUT_SID, codec=None) -> str:
    from src.hubbard_emu import load_sid
    from pipelines.hubbard.note_codec import BitPackCodec
    if codec is None:
        codec = BitPackCodec()
    _, binary, load = load_sid(config.sid_path)
    models = decode_all(config.sid_path, config.instr_base,
                        config.instr_count, config.arp_interval,
                        config.vib_onset)
    scores = [config.extract(subtune=s).score for s in config.subtunes]
    resetspds = [config.resetspd(s, binary, load) for s in config.subtunes]
    # the freq table - raw bytes from the engine's freq-table base
    freq_bytes = bytes(binary[config.freq_table_base - load + i]
                       for i in range(320))
    sfx_list = config.extract_sfx(config.sid_path)[0] if config.has_sfx else []

    # asm layout: equates, then the generic engine, then the codec's
    # note reader, then the data section.
    # encode the pattern pool up front — the codec's note_asm needs
    # DUR_BITS, which encode() determines from the data.
    pat_order, pat_slot = _pattern_pool(scores)
    pat_bytes, codec_extra = codec.encode(pat_order)

    asm = (f'PWLEN = {2 * len(models) - 1}\n'
           f'ARP_OFS = {config.arp_interval}\n'
           f'INCBY2_STEP = {config.incby2_step & 0xFF}\n'
           f'INCBY2_ALWAYS = {1 if config.incby2_every_frame else 0}\n'
           f'DRUM_PRIO_INIT = {0 if config.suppress_first_notestart else 255}\n'
           f'DUR_BITS = {codec.dur_bits}\n'
           f'INST_BITS = {codec.inst_bits}\n'
           f'FREEZE_ON_STOP = {1 if config.freeze_on_stop else 0}\n'
           + codec.zp_asm + '\n'
           + ENGINE + '\n'
           + codec.note_asm + '\n'
           + _emit_data(scores, models, freq_bytes, resetspds, sfx_list,
                        pat_slot, pat_bytes, codec_extra)
           + '\n')

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
    with open(config.sid_path, 'rb') as f:
        orig_hdr = f.read(124)

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD + 3)
    h += struct.pack('>H',
                     len(config.subtunes) + (16 if config.has_sfx else 0))
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
    from pipelines.hubbard.inst_program import capture, REG_NAMES
    from pipelines.hubbard.song_interp import SongInterp
    from pipelines.commando.config import COMMANDO

    cap = capture(sid_path, n_frames=n_frames, subtune=subtune)
    si = SongInterp(COMMANDO, subtune)
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
    from pipelines.commando.config import COMMANDO
    path = build(COMMANDO)
    print(f'built {path}  ({os.path.getsize(path)} bytes)')
    if '--verify' in argv:
        verify(path, ENGINE_FX)


if __name__ == '__main__':
    main(sys.argv[1:])
