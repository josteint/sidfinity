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
from dataclasses import dataclass, field

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

@dataclass
class StatebufSlot:
    offset: int
    kind: str            # 'var' | 'var_and' | 'note_byte' | 'const' | 'zp'
    var: str = ''        # zp name for 'var' / 'var_and'
    mask: int = 0xFF     # AND mask for 'var_and'
    value: int = 0       # byte value for 'const'


@dataclass
class StatebufLayout:
    n_voices: int = 3
    scalars: list = field(default_factory=list)     # list[StatebufSlot]
    per_voice: list = field(default_factory=list)   # list[StatebufSlot]


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
    # The classic seed: 0, 7, 14 for V1, V2, V3. Engines override via
    # `scalars` entries with kind='const' (e.g. HR puts sidoff
    # constants at offsets 0 and 1 explicitly).
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
; register, mark the song silent, and abort the frame ($C2DC).
sps_fill:
        stx sub_tmp
        ldx #20
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

; fx_incby2 - bit1. odd-frame slide on v_slide, write OLD value then
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


def _emit_data(scores, models, freq_bytes, resetspds, voice_starts,
               sfx_list, pat_slot, pat_bytes, codec_extra,
               seed_overlap: bool = True,
               state_layout: StatebufLayout = COMMANDO_STATEBUF_LAYOUT,
               seed_offsets: _Optional[dict] = None) -> str:
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
    # `seed_overlap=False` zeros the seed for engines that init their
    # per-voice state at runtime (Human Race's $1A9C init).
    if seed_overlap:
        # The 6 per-voice state vars live inside the freq-table region.
        # Each engine has the same set of vars but at engine-specific
        # offsets — Commando defaults; Hunter Patrol's v_slide is at
        # +238 instead of +239 (one byte earlier within the state).
        so = seed_offsets or {
            'v_ctrl':     208,
            'pwm_period': 229,
            'pwm_dir':    232,
            'v_instr':    214,
            'v_durfield': 205,
            'v_slide':    239,
        }
        ov = ([freq_bytes[so['v_ctrl']     + i] for i in range(3)]
              + [freq_bytes[so['pwm_period'] + i] for i in range(3)]
              + [freq_bytes[so['pwm_dir']    + i] for i in range(3)]
              + [freq_bytes[so['v_instr']    + i] for i in range(3)]
              + [freq_bytes[so['v_durfield'] + i] for i in range(3)]
              + [freq_bytes[so['v_slide']    + i] for i in range(3)])
    else:
        ov = [0] * 18
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

    # per-subtune orderlists ($FF = loop to orderLoop, $FE = end of song).
    # An empty orderlist (e.g. Human Race's unused V3) emits just $FE —
    # set_patptr will see the song-end terminator at the first read and
    # set v_ended on the voice, leaving it silent. $FF here would loop
    # forever (the only entry is the terminator).
    for si, score in enumerate(scores):
        for vi, v in enumerate(score.voices):
            if v.orderlist:
                term = '$FE' if v.stop else '$FF'
                ob = ','.join(f'${pat_slot[oidx]:02X}' for oidx in v.orderlist)
                lines.append(f'order_{si}_{vi}: .byt {ob},{term}')
            else:
                lines.append(f'order_{si}_{vi}: .byt $FE')

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
    lines.append('subVoiceStart: .byt '
                 + ','.join(f'${v:02X}' for v in voice_starts))

    # live per-voice orderlist selection (filled by init)
    lines.append('orderLo: .byt 0,0,0')
    lines.append('orderHi: .byt 0,0,0')
    lines.append('orderLoop: .byt 0,0,0')

    # statebuf - the engine-state mirror the off-table arpeggio indexes.
    # Initial bytes hold any const scalars (Commando's per-voice sidoff
    # 0,7,14 lives here; HR's sidoffs 0,7 likewise). The rest is filled
    # live by build_statebuf, with unmapped gap bytes left at their
    # init value (usually 0).
    lines.append(f'statebuf: .byt {_statebuf_init_bytes(state_layout)}')

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

def _sfx_state_in_freqtab(asm: str, ofs: int) -> str:
    """Relocate the SFX engine state into the freq-table off-table
    region, for engines whose SFX pitch sweep overruns the 96-entry
    table and reads engine state as 'frequency' (Monty: $84FB+).

    The shared SFX player is Commando's — zp state plus a few bytes
    mirrored at Commando's scattered freq-table offsets. This rewires
    it so the SFX-state block sits at ofs..ofs+5 and the post-update
    sweep index is mirrored there each step, so the overrun reads live
    state byte-exact. Commando keeps the original wiring (ofs None)."""
    # 1. init_sfx — write the SFX-state block at this engine's offsets:
    #    +0 disable=0, +1 SFX index, +2 static $ff, +3 sweep index,
    #    +4 step rate, +5 end index.
    o2 = ("        lda #$80\n"
          "        sta freqtab+241      ; the sweep reads $5519 here -"
          " mode byte $80\n"
          "        lda sfx_idx\n"
          "        sta freqtab+255      ; $5527 - the SFX index\n"
          "        lda #$ff\n"
          "        sta freqtab+256      ; $5528 - drum_enable\n"
          "        ldy #14\n"
          "        lda (sfx_rec),y      ; record 14 - sweep start index\n"
          "        sta sfx_index\n")
    n2 = ("        lda #$00\n"
          f"        sta freqtab+{ofs}        ; SFX-disable flag\n"
          "        lda sfx_idx\n"
          f"        sta freqtab+{ofs + 1}        ; SFX index\n"
          "        lda #$ff\n"
          f"        sta freqtab+{ofs + 2}        ; static byte\n"
          "        ldy #16\n"
          "        lda (sfx_rec),y      ; record 16 - step rate\n"
          f"        sta freqtab+{ofs + 4}        ; step counter\n"
          "        ldy #15\n"
          "        lda (sfx_rec),y      ; record 15 - end index\n"
          f"        sta freqtab+{ofs + 5}        ; end index\n"
          "        ldy #14\n"
          "        lda (sfx_rec),y      ; record 14 - sweep start index\n"
          "        sta sfx_index\n"
          f"        sta freqtab+{ofs + 3}        ; sweep index (initial)\n")
    assert o2 in asm, 'sfx fix: init_sfx block not found'
    asm = asm.replace(o2, n2, 1)

    # 2. sfxs_go — mirror the POST-update sweep index to freqtab+ofs+3
    #    before the sweep reads it (the engine advances its index in
    #    memory, then reads the freq table, so the overrun read of the
    #    index byte sees the new value).
    o3 = ("        lda (sfx_rec),y      ; record 17 - flags\n"
          "        sta sfx_flags\n"
          "        and #$04\n")
    n3 = ("        lda (sfx_rec),y      ; record 17 - flags\n"
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
          f"        sta freqtab+{ofs + 3}\n"
          "        lda sfx_flags\n"
          "        and #$04\n")
    assert o3 in asm, 'sfx fix: sfxs_go block not found'
    asm = asm.replace(o3, n3, 1)
    return asm


from dataclasses import dataclass as _dataclass, field as _field
from typing import Optional as _Optional


@_dataclass
class _Inputs:
    """Everything `_emit_sid` needs, decoupled from the source.

    `_inputs_from_config` builds this by reading `config.sid_path`.
    `_inputs_from_usf` (in build_from_usf.py) builds it from a `.usf`
    file plus per-engine constants. Both feed `_emit_sid` which is
    pure: it knows nothing about how the inputs were derived.
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
    )


def _emit_sid(inputs: _Inputs, out_path: str, codec) -> str:
    """Emit a SID file from a fully-prepared `_Inputs`. No I/O of the
    original binary; everything needed is in `inputs`."""
    pat_order, pat_slot = _pattern_pool(inputs.scores)
    pat_bytes, codec_extra = codec.encode(pat_order)

    asm = (f'PWLEN = {2 * len(inputs.models) - 1}\n'
           f'N_MUSIC = {len(inputs.subtunes)}\n'
           f'FRAME_CTR_INIT = {inputs.frame_ctr_init}\n'
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
           + codec.zp_asm + '\n'
           + ENGINE + '\n'
           + codec.note_asm + '\n'
           + _emit_data(inputs.scores, inputs.models, inputs.freq_bytes,
                        inputs.resetspds, inputs.voice_starts,
                        inputs.sfx_list, pat_slot, pat_bytes, codec_extra,
                        seed_overlap=inputs.seed_overlap,
                        state_layout=inputs.state_layout,
                        seed_offsets=inputs.seed_offsets)
           + '\n')

    asm = asm.replace('inc freqtab+253',
                      f'inc freqtab+{inputs.sfx_framectr_ofs}')
    if inputs.sfx_state_ofs is not None:
        asm = _sfx_state_in_freqtab(asm, inputs.sfx_state_ofs)

    # Substitute the per-engine build_statebuf body for the sentinel
    # in the ENGINE template. The layout differs per engine — see
    # StatebufLayout / COMMANDO_STATEBUF_LAYOUT / Human Race's layout.
    asm = asm.replace('; %%BUILD_STATEBUF%%',
                      _emit_build_statebuf(inputs.state_layout))

    # Substitute the optional "late-in-note" gate inside fx_incby2.
    # Hunter Patrol's skydive only fires once the v_dur countdown
    # drops below 9 frames; other engines have no such gate.
    late_gate_asm = ''
    if inputs.incby2_late_gate is not None:
        late_gate_asm = (
            f'        lda v_dur,x\n'
            f'        cmp #{inputs.incby2_late_gate}\n'
            f'        bcs fxi_ret          ; v_dur >= late_gate -> skip')
    asm = asm.replace('; %%INCBY2_LATE_GATE%%', late_gate_asm)

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
    songs = len(inputs.subtunes) + (16 if inputs.has_sfx else 0)
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', LOAD + 3)
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


def build(config, out_path: str = OUT_SID, codec=None) -> str:
    from pipelines.hubbard.note_codec import BitPackCodec
    if codec is None:
        codec = BitPackCodec()
    inputs = _inputs_from_config(config)
    return _emit_sid(inputs, out_path, codec)


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
