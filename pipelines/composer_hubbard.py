"""composer/hubbard85 — the lifted Hubbard '85 parametric core.

Status: Phase 8.1 — moved here from `pipelines/universal_codegen.py`
(which is being retired). The composer's hubbard85 dispatch calls
`_emit_hubbard85_bytes` from this module. Future phases (8.2+)
decompose the ENGINE asm template + helpers into composer-style
feature emitters parametric on EngineModel features; as that
happens, this module shrinks.

The Hubbard '85 codegen handles:
  - 11 Hubbard '85 engines (Commando family + Human Race + Hunter
    Patrol + Battle of Britain + Confuzion + Devils Galop + Monty +
    Action Biker + Thing on a Spring + One Man and his Droid + Chimera)
  - SFX sub-engine (16 sound-effect records)
  - Digi region (Chimera 1-bit wavetoggle)
  - 5_Title_Tunes compound build (5 packed sub-engines + dispatcher)
  - Full modulation pipeline: vibrato, PWM linear/bidir, multi-step
    arpeggio (incl. off-table via state_layout), freq-hi slide,
    odd-frame slide, drum-slide, master-vol fade, hard-restart writes,
    drum-prio gate, no-release flag, tie + drum_trig per-note effects.
"""

from __future__ import annotations

import os
import struct
import subprocess
import sys as _sys
from dataclasses import dataclass, field
from typing import Optional as _Optional

from src.usf import UsfFile, MusicSubtune, SfxSubtune, DigiSubtune

LOAD = 0x1000

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sys.path.insert(0, _ROOT)
_sys.path.insert(0, os.path.join(_ROOT, 'src'))
_sys.path.insert(0, os.path.join(_ROOT, 'tools', 'py65_lib'))

_XA = os.path.join(_ROOT, 'tools', 'xa65', 'xa', 'xa')
XA = _XA   # legacy name; some lifted code still references it

from pipelines.hubbard.inst_generalize import decode_all  # noqa: E402

# State-layout mirror moved to composer.py in Phase 8.2. composer.py
# owns the feature emitters; composer_hubbard imports them back here
# so the lifted ENGINE template still substitutes the build_statebuf
# routine via `%%BUILD_STATEBUF%%`. The dataclasses live in
# `engine_model.py` as `StateLayoutMirror`/`StateSlot`, aliased
# `StatebufLayout`/`StatebufSlot` for the lifted code's legacy naming.
from pipelines.composer import (
    COMMANDO_STATEBUF_LAYOUT, _emit_build_statebuf, _statebuf_init_bytes,
)
from pipelines.engine_model import StatebufLayout, StatebufSlot


# ---------------------------------------------------------------------------
# build_statebuf — engine state-region mirror for off-table arpeggio
# ---------------------------------------------------------------------------
#
# The drum arpeggio (fx bit 2) computes `arp_pitch = v_pitch + 12`
# every frame the pitch passes through the +12 phase. For arp_pitch
# >= 96 the look-up `freq_table[arp_pitch*2]` reads PAST the 96-entry
# table into engine state. This is Hubbard's "off-table arpeggio" —
# a deliberate trick that produces characteristic percussive freqs
# from live engine state.
#
# Each Hubbard '85 engine has its own state-region layout (Commando
# at $54E8, HR at $0DA4, ...). To reproduce the original write set,
# the rebuild's `statebuf` must mirror the same byte at each off-
# table offset. `StatebufLayout` captures the layout as data; one
# shared emitter generates the `build_statebuf` asm.
#
# Reading the layout: each engine's `statebuf+N` should hold whatever
# byte the original engine has at "state-region offset N" when the
# off-table read happens. Slots fall into two camps:
#
#   - `scalars`: written once at the top of build_statebuf (constants
#     or scalar zp vars like `sidoff`).
#   - `per_voice`: written inside a `ldx #n-1; ...; dex; bpl` loop;
#     the slot's `offset` is the base, with offset+X storing the X-th
#     voice's value.


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

* = $1000
        jmp init
        jmp play

; init - A = subtune number. A under N_MUSIC is a music subtune; A
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

; %%FX_DRUMSLIDE%%

; %%FX_INCBY2%%

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
fxa_ret: rts

; build_statebuf - assemble the off-table-arpeggio state mirror.
; Generated per-engine from StatebufLayout (see codegen.py); the
; concrete body is substituted in at codegen time.
; %%BUILD_STATEBUF%%

; ============================ sound effects ===========================
; A SFX is a 2-voice register snapshot plus a freq-table pitch sweep,
; driven by a 32-byte record (sfxdata). See pipelines/hubbard/commando/extract/
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


def _emit_data(scores, models, freq_bytes, resetspds, voice_starts,
               sfx_list, pat_slot, pat_bytes, codec_extra,
               seed_overlap: bool = True,
               state_layout: StatebufLayout = COMMANDO_STATEBUF_LAYOUT,
               seed_offsets: _Optional[dict] = None,
               per_subtune_speed_ctr_init: _Optional[list] = None,
               per_subtune_incby2_step: _Optional[list] = None,
               per_subtune_incby2_late_gate: _Optional[list] = None,
               per_subtune_ovseed: _Optional[list] = None) -> str:
    """Emit the xa65 data section for a multi-subtune build.

    `scores` is one Score per packed music subtune; `sfx_list` is the
    16 sound effects; `codec` is the note packer. Instruments, the freq
    table and the pattern pool are shared; orderlists, loop points and
    tempo are per-subtune, selected by `init` from the subOrder* /
    subResetspd tables."""
    lines = []

    # All data-section emitters now live in composer.py (Phase 8.6-8.8).
    from pipelines.composer import (
        _emit_hubbard_instrument_table, _emit_hubbard_pwseed_pwacc,
        _emit_hubbard_freq_table_data, _emit_hubbard_ovseed,
        _emit_hubbard_pattern_pool, _emit_hubbard_orderlists,
        _emit_hubbard_per_subtune_tables, _emit_hubbard_psp_tables,
        _emit_hubbard_per_subtune_ovseed, _emit_hubbard_live_order_arrays,
        _emit_hubbard_statebuf_data, _emit_hubbard_sfx_records,
    )
    lines.extend(_emit_hubbard_instrument_table(models))
    lines.extend(_emit_hubbard_pwseed_pwacc(models))
    lines.extend(_emit_hubbard_freq_table_data(freq_bytes))
    lines.extend(_emit_hubbard_ovseed(freq_bytes, seed_overlap, seed_offsets))

    # patterns — each unique pattern emitted once; orderlists reference
    # them by a dense slot. pattern indices are global, so the pool is
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


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------



from dataclasses import dataclass as _dataclass, field as _field
from typing import Optional as _Optional


@_dataclass
class _Inputs:
    """Everything `_hubbard_emit_sid` needs, decoupled from the source.

    `_inputs_from_config` builds this by reading `config.sid_path`.
    `_inputs_from_usf` (in `build_from_usf.py`) builds it from a
    v3 `.usf` file alone — no engine-name lookup. Both feed `_hubbard_emit_sid`
    which is pure: it knows nothing about how the inputs were derived.
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
    """Build inputs from a legacy `EngineConfig` (reads the binary)."""
    from src.hubbard_emu import load_sid
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


def _hubbard_emit_sid(inputs: _Inputs, out_path: str, codec,
              load_addr: int = LOAD) -> str:
    """Emit a SID file from a fully-prepared `_Inputs`. No I/O of the
    original binary; everything needed is in `inputs`.

    `load_addr` overrides the default $1000 load address — set by the
    compound-PSID build (5 Title Tunes) which packs 5 engines at
    non-overlapping addresses.
    """
    pat_order, pat_slot = _pattern_pool(inputs.scores)
    pat_bytes, codec_extra = codec.encode(pat_order)

    asm = (f'PWLEN = {2 * len(inputs.models) - 1}\n'
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
           + codec.zp_asm + '\n'
           + ENGINE + '\n'
           + codec.note_asm + '\n'
           + _emit_data(inputs.scores, inputs.models, inputs.freq_bytes,
                        inputs.resetspds, inputs.voice_starts,
                        inputs.sfx_list, pat_slot, pat_bytes, codec_extra,
                        seed_overlap=inputs.seed_overlap,
                        state_layout=inputs.state_layout,
                        seed_offsets=inputs.seed_offsets,
                        per_subtune_speed_ctr_init=inputs.per_subtune_speed_ctr_init,
                        per_subtune_incby2_step=inputs.per_subtune_incby2_step,
                        per_subtune_incby2_late_gate=inputs.per_subtune_incby2_late_gate,
                        per_subtune_ovseed=inputs.per_subtune_ovseed)
           + '\n')

    from pipelines.composer import (
        _emit_sfx_framectr_offset_substitution,
        _emit_per_subtune_dispatch,
        _emit_load_addr_substitution,
        _apply_sfx_state_in_freqtab,
        _emit_hubbard_fx_drumslide,
        _emit_hubbard_fx_incby2,
    )
    # fx routine chunk substitutions (Phase 8.9+). Each fx routine
    # moved out of the ENGINE template into composer.py; the template
    # has a `; %%FX_<NAME>%%` sentinel that we substitute back here.
    # The substitutions must run BEFORE the smaller nested sentinels
    # (like `%%INCBY2_LATE_GATE%%` which lives inside fx_incby2).
    asm = asm.replace('; %%FX_DRUMSLIDE%%', _emit_hubbard_fx_drumslide())
    asm = asm.replace('; %%FX_INCBY2%%', _emit_hubbard_fx_incby2())
    old, new = _emit_sfx_framectr_offset_substitution(inputs.sfx_framectr_ofs)
    asm = asm.replace(old, new)
    asm = _apply_sfx_state_in_freqtab(asm, inputs.sfx_state_ofs)

    # Substitute the per-engine build_statebuf body for the sentinel
    # in the ENGINE template. The layout differs per engine — see
    # StatebufLayout / COMMANDO_STATEBUF_LAYOUT / Human Race's layout.
    asm = asm.replace('; %%BUILD_STATEBUF%%',
                      _emit_build_statebuf(inputs.state_layout))

    # Small sentinel-feature emitters — Phase 8.4 moved them into
    # composer.py. composer_hubbard.py is the adapter: wraps `_Inputs`
    # fields into the right shape and applies the substitutions.
    from pipelines.engine_model import FadeProgressive
    from pipelines.composer import (
        _emit_arp_phase_invert_substitution,
        _emit_clear_drumtrig,
        _emit_incby2_late_gate,
        _emit_master_vol_fade,
        _emit_ns_offtab_decr,
        _emit_ovseed_copy,
    )

    # arp_phase_invert — direct text replace in fx_arp's branch.
    sub = _emit_arp_phase_invert_substitution(inputs.arp_phase_invert)
    if sub is not None:
        asm = asm.replace(sub[0], sub[1])

    # Per-subtune engine params (5_Title_Tunes unified path). When ANY
    # of the per_subtune_* lists is set, replace the compile-time SPEED
    # CTR / INCBY2 STEP / late-gate code with per-subtune-table reads.
    uses_psp = (
        inputs.per_subtune_speed_ctr_init is not None
        or inputs.per_subtune_incby2_step is not None
        or inputs.per_subtune_incby2_late_gate is not None)

    # 5_Title_Tunes per-subtune mechanism dispatch — replaces the
    # SPEED_CTR_INIT load + INCBY2_STEP add with per-subtune table reads.
    for old, new in _emit_per_subtune_dispatch(uses_psp).items():
        asm = asm.replace(old, new)
    if uses_psp:
        asm = asm.replace('; %%OVSEED_COPY%%', _emit_ovseed_copy(
            inputs.per_subtune_ovseed is not None))
        asm = asm.replace('; %%INCBY2_LATE_GATE%%',
                          _emit_incby2_late_gate(None, per_subtune_zp_var=True))
    else:
        asm = asm.replace('; %%OVSEED_COPY%%', _emit_ovseed_copy(False))
        asm = asm.replace('; %%INCBY2_LATE_GATE%%',
                          _emit_incby2_late_gate(inputs.incby2_late_gate))

    # ns_offtab_decr — Thing on a Spring's statebuf v_hubidx decrement.
    asm = asm.replace('; %%NS_OFFTAB_DECR%%',
                      _emit_ns_offtab_decr(inputs.ns_offtab_decr_offset))

    # Master-volume fade — four sentinel substitutions.
    fade = (
        FadeProgressive(
            subtrahend_voice_idx=inputs.master_vol_subtrahend_voice,
            base=inputs.master_vol_base,
            trigger=inputs.master_vol_trigger,
        )
        if inputs.master_vol_subtrahend_voice is not None else None)
    for sentinel, fragment in _emit_master_vol_fade(fade).items():
        asm = asm.replace(sentinel, fragment)

    # tie_preserves_slide — pair of substitutions positioning the
    # `sta v_drumtrig,x` clear.
    for sentinel, fragment in _emit_clear_drumtrig(
            inputs.tie_preserves_slide).items():
        asm = asm.replace(sentinel, fragment)

    # Relocate the engine to the requested load address (composer's
    # emitter handles the substitution; compound PSIDs (5TT) place
    # each packed sub-engine at a different address).
    old, new = _emit_load_addr_substitution(load_addr)
    asm = asm.replace(old, new)

    src = '/tmp/usf2_commando.s'
    obj = '/tmp/usf2_commando.bin'
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([XA, src, '-o', obj], capture_output=True, text=True)
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




# =============================================================================
# Hubbard '85 — USF -> _Inputs adapter + digi region builder
# =============================================================================
#
# Lifted from the former pipelines/build_from_usf.py module-level helpers.
# Stays here next to _hubbard_emit_sid so the shape's full dispatch lives
# in one file. `build_from_usf` (the top-level public entry) stays in
# pipelines/build_from_usf.py and just calls into universal_codegen.emit_sid.

from pipelines.hubbard.sfx import SoundEffect
from pipelines.hubbard.engine_constants import (
    DigiCode, chimera_psid_dispatcher, assemble_chimera_digi_player,
)
from pipelines.hubbard.flac_io import read_sample
from pipelines.hubbard.digi_pack import pack_digi
from pipelines.hubbard.inst_generalize import (
    InstrumentModel, ArpSpec, VibratoSpec, PwmSpec,
)
from pipelines.hubbard.types import (
    Score, Voice, Note, Instrument as HubInstrument,
)
# Named handles for the few distinct digi techniques in the SID corpus.
# Each entry maps a tune-level `digi_player: <name>` to its DigiCode
# (which describes where the dispatcher + player live in the rebuild's
# address space). The bytes of the player asm itself stay in
# engine_constants.py — they're 6502 code, not USF data.
def _digi_player_registry():
    from pipelines.hubbard.engine_constants import CHIMERA_DIGI
    return {
        'chimera_1bit': CHIMERA_DIGI,
    }


# ---------------------------------------------------------------------------
# USF → InstrumentModel (the inverse of pipelines/hubbard/chimera/extract/to_usf.
# _convert_instrument)
# ---------------------------------------------------------------------------

def _model_from_usf_instrument(u, vib_onset: int) -> InstrumentModel:
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


# ---------------------------------------------------------------------------
# USF → Score (the extract-output shape the codegen consumes)
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


def _score_from_subtune(sub: MusicSubtune) -> Score:
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


# ---------------------------------------------------------------------------
# SfxSubtune → engine SoundEffect — the inverse of `_convert_sfx` in
# to_usf.py. Reassembles the 7-byte v1/v2 voice register lists (the
# freq_lo byte is re-derived from start_index / gate-flags-plus-offset).
# ---------------------------------------------------------------------------

def _soundeffect_from_usf(s: SfxSubtune, idx: int) -> SoundEffect:
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


# ---------------------------------------------------------------------------
# USF → _Inputs helpers
# ---------------------------------------------------------------------------

def _ovseed_from_init_state(init, instr_count: int) -> bytes:
    """Convert a USF `InitState` back into the 18-byte ovseed
    (the inverse of `_init_state_from_ovseed` in
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


# ---------------------------------------------------------------------------
# Combined music + digi build (for engines with digi subtunes, e.g. Chimera)
# ---------------------------------------------------------------------------

def _build_digi_region(usf: UsfFile, digi_subs: list[DigiSubtune],
                       digi_code: DigiCode, usf_dir: str,
                       music_load: int | None = None
                       ) -> tuple[bytes, int, int]:
    """Build the bytes of the digi region — dispatcher + tables +
    samples + player — placed at their fixed engine addresses.

    Returns `(region_bytes, region_base, play_addr)`. `play_addr` is
    the PSID `play` entry inside the dispatcher (used by the header).
    """
    base = digi_code.dispatcher_base                       # e.g. $9F80
    # The Chimera player is assembled lazily from its xa65 asm source
    # (regenerated, not lifted verbatim from the original SID).
    player_bytes = assemble_chimera_digi_player(
        player_base=digi_code.player_base)
    end  = digi_code.player_base + len(player_bytes)       # one past last byte

    # Generate the PSID dispatcher with addresses substituted for our
    # music engine and the digi player. `music_load` is passed by the
    # caller (auto-packing); fall back to digi_code.music_load_addr or
    # LOAD when called from contexts that don't know the music engine
    # address yet.
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
        sample_path = os.path.join(usf_dir, sub.sample)
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


def _emit_combined_sid(inputs: _Inputs, usf: UsfFile, digi_subs: list,
                       digi_code: DigiCode, out_path: str, usf_dir: str,
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
    # _hubbard_emit_sid wrote a PSID. Strip its 124-byte header.
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


# ---------------------------------------------------------------------------
# USF → _Inputs
# ---------------------------------------------------------------------------

def _inputs_from_usf(usf: UsfFile) -> _Inputs:
    """Build codegen `_Inputs` from a USF — no engine-name lookup."""
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
        # StatebufLayout/Slot are defined above in this same module
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


def _emit_hubbard85_bytes(usf: UsfFile, usf_dir: str | None) -> bytes:
    """Hubbard '85 dispatch: build `_Inputs` from the USF, then either
    `_hubbard_emit_sid` (music-only) or `_emit_combined_sid` (when the
    USF carries digi subtunes). Returns the PSID bytes."""
    from pipelines.hubbard.note_codec import BitPackCodec
    import tempfile
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
