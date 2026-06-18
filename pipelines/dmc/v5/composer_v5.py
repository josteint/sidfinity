"""DMC V5 composer — V5Model -> our own re-authored V5 engine -> xa65 -> PSID.

A clean re-authoring of the family-3/5 V5 player (see disassembly.s): the
per-frame logic mirrors the original (so the $D400-$D418 write stream
matches) but the code is freshly authored with symbolic labels + a
relabeled state block, and the SONG DATA (orderlists, sectors,
instruments, freq, the 3 programmable tables) is emitted from the
extracted model (index-based / relocatable musical content) and read via
labels. Proves the extract captures the music. Verdict: write-log.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header, FLAGS_PAL_6581

LOAD = 0x1000


def _byt(data) -> str:
    out = []
    for i in range(0, len(data), 16):
        out.append('        .byt ' + ', '.join(f'${b & 0xFF:02X}'
                                               for b in data[i:i + 16]))
    return '\n'.join(out) if out else '        .byt $00'


def _emit_data(m) -> str:
    d = []
    # song data (relocatable: notes/indices/values only) ------------------
    # orderlist pointer record: 3 x (lo,hi) -> the orderlist streams, then
    # speed + master vol.
    # ordrec = one 8-byte record per subtune (3 orderlist ptrs + speed +
    # master vol); the init indexes it by song#*8. Single-subtune = 1 record.
    subs = m.subtunes or [m]      # fall back to the top-level fields
    rec = []
    for si, st in enumerate(subs):
        for v in range(3):
            rec.append(f'<ol_{si}_{v}')
            rec.append(f'>ol_{si}_{v}')
        rec.append(f'${st.speed:02X}')
        rec.append(f'${st.master_vol:02X}')
    d.append('ordrec:\n        .byt ' + ', '.join(rec))
    for si, st in enumerate(subs):
        for v in range(3):
            d.append(f'ol_{si}_{v}:\n' + _byt(st.orderlist_raw[v]))
    # sector pointer tables (lo/hi parallel) + sector streams
    d.append('secp_lo:\n        .byt ' +
             ', '.join(f'<sec_{i}' for i in range(len(m.sectors))))
    d.append('secp_hi:\n        .byt ' +
             ', '.join(f'>sec_{i}' for i in range(len(m.sectors))))
    for i, raw in enumerate(m.sector_raw):
        d.append(f'sec_{i}:\n' + _byt(raw))
    # instruments (8 bytes each)
    instr = []
    for ins in m.instruments:
        instr += [ins.ad, ins.sr, ins.wave_ptr, ins.pulse_ptr,
                  ins.filter_ptr, ins.vib_delay, ins.vib_speed, ins.vib_width]
    d.append('instr:\n' + _byt(instr))
    # freq tables
    d.append('freqlo:\n' + _byt(m.freq_lo))
    d.append('freqhi:\n' + _byt(m.freq_hi))
    # the 3 programmable 2-byte tables (split lo/hi parallel arrays)
    d.append('wavectrl:\n' + _byt([c for c, f in m.wave]))
    d.append('wavefreq:\n' + _byt([f for c, f in m.wave]))
    d.append('pulselo:\n' + _byt([lo for lo, hi in m.pulse]))
    d.append('pulsehi:\n' + _byt([hi for lo, hi in m.pulse]))
    d.append('filterlo:\n' + _byt([lo for lo, hi in m.filter] or [0]))
    d.append('filterhi:\n' + _byt([hi for lo, hi in m.filter] or [0]))
    # per-voice leftover note ($100F-$1011): the lead-in effects frame(s)
    # read it before the first fetch (only observable when lo_spdctr>0).
    d.append('initnotes:\n' + _byt((list(m.lo_notes) + [0, 0, 0])[:3]))
    return '\n'.join(d)


# --- engine: faithful re-authoring of disassembly.s (labels + state block).
#     X = voice 0..2; Y (for $D4xx stores) = sidoff,x = 0/7/14.
_ENGINE = r"""
        * = $1000
        jmp init
        jmp playframe

;; ===================== init =====================
init:
        asl                     ; A = song# * 8 (PSID init passes song# in A;
        asl                     ; the orderlist record is the only song-indexed
        asl                     ; thing — sectors/instruments/tables are shared)
        pha                     ; save across the state clear
        ldx #$00                ; clear the state block FIRST (before we
        txa                     ; load the track pointers / speed into it)
ini_st:
        sta state0,x
        inx
        cpx #(state_end - state0)
        bne ini_st
        pla
        tay                     ; Y = song# * 8 (0 for single-subtune)
        ldx #$00
ini_ptr:
        lda ordrec,y
        sta trkptl,x
        lda ordrec+1,y
        sta trkpth,x
        iny
        iny
        inx
        cpx #$03
        bne ini_ptr
        lda ordrec,y            ; +6 = speed
        sta speed
        lda ordrec+1,y          ; +7 = master vol
        sta mvol0
        lda #LEFT_FILTMODE      ; file-image leftovers init doesn't clear
        sta filtmode
        lda #LEFT_FCHI
        sta fchi
        lda #LEFT_FCLO
        sta fclo
        lda #LEFT_SPDCTR        ; init does NOT clear $1013 (speed counter):
        sta spdctr              ; the file-image leftover sets startup phase
        lda #LEFT_MVOLFRAC      ; nor $101C (fade fractional accumulator):
        sta mvolfrac            ; the first fade ramps from this leftover phase
        ldx #$00
        lda #$01
ini_v:
        sta durctr,x
        sta vactive,x
        inx
        cpx #$03
        bne ini_v
        ldx #$00
        lda #$00
ini_v2:
        sta sidoff,x            ; 0,7,14
        clc
        adc #$07
        inx
        cpx #$03
        bne ini_v2
        ldx #$00
ini_nt:
        lda initnotes,x         ; prime per-voice leftover note ($100F,x)
        sta curnote,x
        inx
        cpx #$03
        bne ini_nt
        ldx #$00
        txa
ini_sid:
        sta $d400,x
        inx
        cpx #$18
        bne ini_sid
        lda #$08
        sta $d404
        sta $d40b
        sta $d412
        lda #$02
        sta playskip
        rts

;; ===================== play (per frame) =====================
playframe:
        lda playskip
        beq pf_go
        dec playskip
        rts
pf_go:
        dec spdctr
        bpl pf_voices
        lda speed
        sta spdctr
pf_voices:
        ldx #$00
        jsr voice
        ldx #$01
        jsr voice
        ldx #$02
        jsr voice
        lda fclo
        sta $d415
        lda fchi
        sta $d416
        rts

;; ===================== per-voice tick =====================
voice:
        lda vactive,x
        beq vo_eff
        lda speed
        cmp spdctr              ; tick frame?
        bne vo_eff
        dec durctr,x            ; (orig decs on every tick when active)
        beq vo_fetch
vo_eff:
        jmp run_effects

;; ----- track fetch (orderlist) -----
vo_fetch:
        lda trkptl,x
        sta $f8
        lda trkpth,x
        sta $f9
        ldy trkpos,x
        lda ($f8),y
        bpl tf_sector
        cmp #$ff
        bne tf_chk_fe
        iny
        lda ($f8),y             ; loop position
        sta trkpos,x
        tay
        lda ($f8),y             ; loop-target byte: RE-DISPATCH through the
        jmp tf_chk_fd           ; transpose checks (orig $FF -> $111F), so a
                                ; loop target of $FD/$FC applies its transpose
                                ; (many orderlists loop to a leading $FC/$FD);
                                ; a sector# target falls through to tf_sector.
tf_chk_fe:
        cmp #$fe
        bne tf_chk_fd
        lda #$00
        sta vactive,x           ; voice end -> freewheel
        jmp wave_step
tf_chk_fd:
        cmp #$fd
        bne tf_chk_fc
        iny
        inc trkpos,x
        inc trkpos,x
        lda ($f8),y
        sta transp,x
        iny
        lda ($f8),y
        jmp tf_sector_a
tf_chk_fc:
        cmp #$fc
        bne tf_sector
        iny
        inc trkpos,x
        inc trkpos,x
        lda ($f8),y
        eor #$ff
        clc
        adc #$01
        sta transp,x
        iny
        lda ($f8),y
tf_sector_a:
tf_sector:
        tay
        lda secp_lo,y
        sta $f8
        lda secp_hi,y
        sta $f9
        ;; fall into sector dispatch

;; ----- sector dispatch -----
sector_disp:
        ldy secpos,x
        lda ($f8),y
        bmi sd_cmd
        jmp note_play
sd_cmd:
        cmp #$fd
        bne sd_fc
        iny
        lda ($f8),y
        sta durrel,x
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_fc:
        cmp #$fc
        bne sd_fe
        iny
        lda ($f8),y
        sta instr_n,x
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_fe:
        cmp #$fe
        bne sd_f4
        jmp step_commit
sd_f4:
        cmp #$f4
        bne sd_f5
        lda gatemask,x
        eor #$01
        sta gatemask,x
        jmp step_commit
sd_f5:
        cmp #$f5
        bne sd_f3
        lda gateflag,x
        eor #$ff
        sta gateflag,x
        inc secpos,x
        jmp sector_disp
sd_f3:
        cmp #$f3
        bne sd_fb
        iny
        lda ($f8),y
        sta volovr,x
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_fb:
        cmp #$fb
        bne sd_fa
        iny
        lda ($f8),y
        sta glspeed,x
        iny
        lda ($f8),y
        clc
        adc transp,x
        sta curnote,x
        iny
        lda ($f8),y
        clc
        adc transp,x
        sta gltarget,x
        lda secpos,x
        clc
        adc #$03
        sta secpos,x
        jmp note_on
sd_fa:
        cmp #$fa
        bne sd_f9
        iny
        lda ($f8),y
        sta glspeed,x
        iny
        lda ($f8),y
        clc
        adc transp,x
        sta gltarget,x
        lda secpos,x
        clc
        adc #$02
        sta secpos,x
        jmp step_commit
sd_f9:
        cmp #$f9
        bne sd_f8
        iny
        lda ($f8),y
        pha
        beq sd_f9_z
        asl
        asl
        asl
        asl
        ora #$04
sd_f9_z:
        sta $d417
        pla
        and #$f0
        sta filtmode
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_f8:
        cmp #$f8
        bne sd_f2
        iny
        lda ($f8),y
        sta frqovr
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_f2:
        cmp #$f2
        bne sd_f1
        iny
        lda ($f8),y
        ldy sidoff,x
        sta $d405,y
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_f1:
        cmp #$f1
        bne sd_f7
        iny
        lda ($f8),y
        ldy sidoff,x
        sta $d406,y
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_f7:
        cmp #$f7
        bne sd_f6
        iny
        lda ($f8),y
        sta fadein
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_f6:
        cmp #$f6
        bne sd_done
        iny
        lda ($f8),y
        sta fadeout
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_done:
        rts                     ; (unknown -> ignore, defensive)

;; ----- note play (byte < $80) -----
note_play:
        clc
        adc transp,x
        sta curnote,x
        lda gateflag,x
        beq note_on
        jmp step_commit

;; ----- note on -----
note_on:
        lda instr_n,x
        asl
        asl
        asl
        tay
        lda instr,y             ; AD
        pha
        lda instr+1,y           ; SR
        pha
        ldy sidoff,x
        lda volovr,x
        beq no_sr
        asl
        asl
        asl
        asl
        sta tmp40
        pla
        and #$0f
        ora tmp40
        sta $d406,y
        jmp no_ad
no_sr:
        pla
        sta $d406,y
no_ad:
        pla
        sta $d405,y
        lda durrel,x
        sta durctr,x
        lda #$00
        sta notectr,x
        ldy sidoff,x
        lda #$09
        sta $d404,y
        sta notestart,x
        lda #$00
        sta $d400,y
        sta $d401,y
        inc secpos,x
        jsr step_lookahead
        rts                     ; note_on: no write this frame (note_init2 next)

;; ----- step commit (gate-off step / slide / tied note) -----
step_commit:
        lda durrel,x
        sta durctr,x
        inc secpos,x
        jsr step_lookahead
        jmp wave_step           ; falls into the steady write (matches orig)

step_lookahead:
        ldy secpos,x
        lda ($f8),y
        sta lookahead,x
        cmp #$ff
        bne sl_done
        lda #$00
        sta secpos,x
        sta gateflag,x          ; clear gate flag at sector end (matches orig)
        sta volovr,x            ; ($17e7) cleared at sector end
        inc trkpos,x
sl_done:
        rts

;; ===================== run effects =====================
run_effects:
        lda notestart,x
        bne note_init2
        jmp eff_steady
note_init2:
        lda #$00
        sta notestart,x
        lda filtmode
        ora mvol0
        sta $d418
        lda instr_n,x
        asl
        asl
        asl
        tay
        lda instr+5,y           ; vib delay
        sta vibdel,x
        lda instr+6,y           ; vib speed
        sta vibspd,x
        lda instr+7,y           ; vib width &7
        and #$07
        sta vibwidth
        lda instr+2,y           ; wave ptr
        sta wavepos,x
        lda instr+3,y           ; pulse ptr
        sta pulseflag
        beq ni_nopulse
        sta pulsepos,x
ni_nopulse:
        lda instr+4,y           ; filter ptr
        sta filtflag
        beq ni_nofilt
        sta filterpos           ; FL!=0 restarts the V3 filter at this program;
                                ; FL=0 = no restart (the running idle/instrument
                                ; sweep continues). filter_run runs for V3 every
                                ; frame from filterpos=0 regardless (idle default).
ni_nofilt:
        ;; first wave-table step
        ldy wavepos,x
        inc wavepos,x
        lda wavectrl,y
        sta wavectl,x
        and #$08
        beq ni_w_mel
        lda wavefreq,y
        sta freqhiv,x
        lda #$00
        sta freqlov,x
        jmp ni_pulse
ni_w_mel:
        lda wavefreq,y
        clc
        adc curnote,x
        tay
        lda freqlo,y
        sta freqlov,x
        lda freqhi,y
        sta freqhiv,x
ni_pulse:
        lda #$f7
        sta gatemask,x          ; hard-restart-ish gate prep
        lda pulseflag
        beq ni_pdone
        ldy pulsepos,x
        beq ni_pdone
        lda pulsehi,y           ; orig: pwlo = pulsehi[y]
        sta pwlo,x
        lda pulselo,y           ; orig: pwhi = pulselo[y]
        sta pwhi,x
        lda #$00
        sta pwctr_lo,x
        sta pwctr_hi,x
        inc pulsepos,x
ni_pdone:
        lda filtflag
        beq ni_fdone
        ldy filterpos
        lda frqovr
        beq ni_ftab
        sta fchi
        lda #$00
        sta fclo
        jmp ni_fadv
ni_ftab:
        lda filterlo,y
        sta fchi
        lda filterhi,y
        sta fclo
ni_fadv:
        lda #$00
        sta filtctr_lo
        sta filtctr_hi
        inc filterpos
ni_fdone:
        lda #$00
        sta accl,x
        sta acch,x
        sta vibdbl,x
        sta vibdir,x
        sta vibctr,x
        sta vstep_lo,x
        sta vstep_hi,x
        ;; vib step = base-note freq << width
        ldy curnote,x
        lda freqhi,y
        sta vstep_lo,x
        lda vibwidth
        beq vs_done
        ldy #$00
vs_loop:
        asl vstep_lo,x
        rol vstep_hi,x
        iny
        cpy vibwidth
        bne vs_loop
vs_done:
        jmp gate_logic

;; ----- steady effects: pulse / filter(v3) / glide / vibrato / fade / wave / gate / write
eff_steady:
;; pulse_run: advance PW accum; (add,count) pairs; $90 loop. ALWAYS runs
;; (PU=0 means "no restart", not "no run" — the pulse keeps advancing).
        ldy pulsepos,x
        lda pulselo,y
        cmp #$90
        bne pr_go
        lda pulsehi,y
        sta pulsepos,x
        tay
        lda pulselo,y
pr_go:
        sta schi
        lda pulsehi,y
        sta sclo
        iny
        lda pwlo,x
        clc
        adc sclo
        sta pwlo,x
        lda pwhi,x
        adc schi
        sta pwhi,x
        lda pwctr_lo,x
        clc
        adc #$01
        sta pwctr_lo,x
        lda pwctr_hi,x
        adc #$00
        sta pwctr_hi,x
        cmp pulselo,y
        bne filter_run
        lda pwctr_lo,x
        cmp pulsehi,y
        bne filter_run
        lda #$00
        sta pwctr_lo,x
        sta pwctr_hi,x
        inc pulsepos,x
        inc pulsepos,x
filter_run:
        cpx #$02                ; V3 only
        bne glide_slide
        ;; the orig runs filter_run_v3 for V3 EVERY frame from filterpos=0 —
        ;; filter-table position 0 is the DEFAULT (idle) filter program (a real
        ;; default_filter sweep, or a (0,0) hold). No filt_run_on gate: the idle
        ;; sweep must run from frame 0, before any per-instrument filter note.
        ldy filterpos
        lda filterlo,y
        cmp #$90
        bne fr_go
        lda filterhi,y
        sta filterpos
        tay
        lda filterlo,y
fr_go:
        sta schi
        lda filterhi,y
        sta sclo
        iny
        lda fclo
        clc
        adc sclo
        sta fclo
        lda fchi
        adc schi
        sta fchi
        lda filtctr_lo
        clc
        adc #$01
        sta filtctr_lo
        lda filtctr_hi
        adc #$00
        sta filtctr_hi
        cmp filterlo,y
        bne glide_slide
        lda filtctr_lo
        cmp filterhi,y
        bne glide_slide
        lda #$00
        sta filtctr_lo
        sta filtctr_hi
        inc filterpos
        inc filterpos
glide_slide:
        lda glspeed,x
        bne gs_active
        jmp vibrato
gs_active:
        lda curnote,x
        cmp gltarget,x
        bcs gs_down
        lda accl,x
        clc
        adc glspeed,x
        sta accl,x
        lda acch,x
        adc #$00
        sta acch,x
        lda freqlov,x
        clc
        adc accl,x
        sta glsc_lo
        lda freqhiv,x
        adc acch,x
        sta glsc_hi
        ldy gltarget,x
        cmp freqhi,y
        bne gs_skipvib
        jmp gs_arrive
gs_down:
        lda accl,x
        sec
        sbc glspeed,x
        sta accl,x
        lda acch,x
        sbc #$00
        sta acch,x
        lda freqlov,x
        clc
        adc accl,x
        sta glsc_lo
        lda freqhiv,x
        adc acch,x
        sta glsc_hi
        ldy gltarget,x
        cmp freqhi,y
        bcc gs_arrive
        bne gs_skipvib
        lda glsc_lo
        cmp freqlo,y
        bcs gs_skipvib
gs_arrive:
        lda gltarget,x
        sta curnote,x
        tay
        lda freqlo,y
        sta freqlov,x
        lda freqhi,y
        sta freqhiv,x
        lda #$00
        sta accl,x
        sta acch,x
        sta glspeed,x
        jmp vibrato
gs_skipvib:
        jmp fade
vibrato:
        lda gateflag,x
        beq vib_go
        lda #$00
        sta accl,x
        sta acch,x
        jmp fade
vib_go:
        lda vibspd,x
        bne vib_on
        jmp fade
vib_on:
        lda vibdel,x
        beq vib_run
        dec vibdel,x
        jmp fade
vib_run:
        lda vibdir,x
        bne vib_dn
        lda accl,x
        clc
        adc vstep_lo,x
        sta accl,x
        lda acch,x
        adc vstep_hi,x
        sta acch,x
        inc vibctr,x
        lda vibctr,x
        cmp vibspd,x
        bne fade
        lda #$00
        sta vibctr,x
        inc vibdir,x
        lda vibdbl,x
        bne fade
        asl vstep_lo,x
        rol vstep_hi,x
        inc vibdbl,x
        jmp fade
vib_dn:
        lda accl,x
        sec
        sbc vstep_lo,x
        sta accl,x
        lda acch,x
        sbc vstep_hi,x
        sta acch,x
        inc vibctr,x
        lda vibctr,x
        cmp vibspd,x
        bne fade
        lda #$00
        sta vibctr,x
        dec vibdir,x
fade:
        lda fadeout
        beq fade_in
        lda mvolfrac
        sec
        sbc fadeout
        sta mvolfrac
        lda mvol0
        sbc #$00
        sta mvol0
        bne fade_in
        lda #$00
        sta fadeout
fade_in:
        lda fadein
        beq write_vol
        lda mvolfrac
        clc
        adc fadein
        sta mvolfrac
        lda mvol0
        adc #$00
        sta mvol0
        cmp #$0f
        bne write_vol
        lda #$00
        sta fadein
write_vol:
        lda mvol0
        ora filtmode
        sta $d418
wave_step:
        ldy wavepos,x
        lda wavectrl,y
        cmp #$90
        bne ws_go
        lda wavefreq,y
        sta wavepos,x
        tay
        lda wavectrl,y
ws_go:
        sta wavectl,x
        and #$08
        beq ws_mel
        lda wavefreq,y
        sta freqhiv,x
        lda #$00
        sta freqlov,x
        jmp ws_adv
ws_mel:
        lda wavefreq,y
        clc
        adc curnote,x
        tay
        lda freqlo,y
        sta freqlov,x
        lda freqhi,y
        sta freqhiv,x
ws_adv:
        inc wavepos,x

;; ----- gate logic: lookahead-based gate-off + hard restart -----
gate_logic:
        ldy sidoff,x
        lda lookahead,x
        cmp #$fe
        beq sid_write
        cmp #$f4
        beq sid_write
        cmp #$fa
        beq sid_write
        cmp #$f2
        beq sid_write
        cmp #$f1
        beq sid_write
        cmp #$f5
        beq gl_f5
        lda gateflag,x
        bne sid_write
gl_chk1:
        lda durctr,x
        cmp #$01
        bne gl_chk2
        lda #$00
        sta $d406,y
        jmp sid_write
gl_f5:
        lda gateflag,x
        beq sid_write
        jmp gl_chk1
gl_chk2:
        lda durctr,x
        cmp #$02
        bne sid_write
        lda spdctr
        bne sid_write
        lda #$f6
        sta gatemask,x

;; ----- SID write (per-voice) -----
sid_write:
        ldy sidoff,x
        lda freqlov,x
        clc
        adc accl,x
        sta $d400,y
        lda freqhiv,x
        adc acch,x
        sta $d401,y
        lda pwlo,x
        sta $d402,y
        lda pwhi,x
        sta $d403,y
        lda wavectl,x
        and gatemask,x
        sta $d404,y
        rts
"""


def emit_v5_asm(m) -> str:
    state = """
;; ===================== state block =====================
state0:
vactive:  .dsb 3, 0
sidoff:   .dsb 3, 0
trkptl:   .dsb 3, 0
trkpth:   .dsb 3, 0
trkpos:   .dsb 3, 0
secpos:   .dsb 3, 0
durctr:   .dsb 3, 0
durrel:   .dsb 3, 0
instr_n:  .dsb 3, 0
transp:   .dsb 3, 0
volovr:   .dsb 3, 0
gateflag: .dsb 3, 0
glspeed:  .dsb 3, 0
gltarget: .dsb 3, 0
curnote:  .dsb 3, 0
wavepos:  .dsb 3, 0
pulsepos: .dsb 3, 0
vibdel:   .dsb 3, 0
vibspd:   .dsb 3, 0
notectr:  .dsb 3, 0
notestart: .dsb 3, 0
freqlov:  .dsb 3, 0
freqhiv:  .dsb 3, 0
wavectl:  .dsb 3, 0
gatemask: .dsb 3, 0
lookahead: .dsb 3, 0
pwlo:     .dsb 3, 0
pwhi:     .dsb 3, 0
pwctr_lo: .dsb 3, 0
pwctr_hi: .dsb 3, 0
vibdbl:   .dsb 3, 0
vibdir:   .dsb 3, 0
vibctr:   .dsb 3, 0
accl:     .dsb 3, 0
acch:     .dsb 3, 0
vstep_lo: .dsb 3, 0
vstep_hi: .dsb 3, 0
speed:    .dsb 1, 0
spdctr:   .dsb 1, 0
filtmode: .dsb 1, 0
fchi:     .dsb 1, 0
fclo:     .dsb 1, 0
fadein:   .dsb 1, 0
fadeout:  .dsb 1, 0
vibwidth: .dsb 1, 0
mvol0:    .dsb 1, 0
mvolfrac: .dsb 1, 0
sclo:     .dsb 1, 0
schi:     .dsb 1, 0
glsc_lo:  .dsb 1, 0
glsc_hi:  .dsb 1, 0
filterpos: .dsb 1, 0
filtctr_lo: .dsb 1, 0
filtctr_hi: .dsb 1, 0
frqovr:   .dsb 1, 0
filtflag: .dsb 1, 0
pulseflag: .dsb 1, 0
playskip: .dsb 1, 0
tmp40:    .dsb 1, 0
state_end:
        .byt $00
"""
    consts = (f'LEFT_FILTMODE = ${m.lo_filtmode:02X}\n'
              f'LEFT_FCHI = ${m.lo_fchi:02X}\n'
              f'LEFT_FCLO = ${m.lo_fclo:02X}\n'
              f'LEFT_SPDCTR = ${m.lo_spdctr:02X}\n'
              f'LEFT_MVOLFRAC = ${m.lo_mvolfrac:02X}\n')
    return consts + _ENGINE + '\n' + _emit_data(m) + '\n' + state


def build_v5_sid(m) -> bytes:
    from pipelines.dmc.composer_asm import _sanitize_asm
    code = assemble(_sanitize_asm(emit_v5_asm(m)))
    n_songs = len(m.subtunes) if m.subtunes else 1
    header = build_header(load=0, init=LOAD, play=LOAD + 3, songs=n_songs,
                          start_song=1, speed=0, title=m.title,
                          author=m.author, released=m.released,
                          flags=FLAGS_PAL_6581)
    return header + bytes([LOAD & 0xFF, LOAD >> 8]) + code
