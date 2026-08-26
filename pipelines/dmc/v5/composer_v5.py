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
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header

LOAD = 0x1000


def _byt(data) -> str:
    out = []
    for i in range(0, len(data), 16):
        out.append('        .byt ' + ', '.join(f'${b & 0xFF:02X}'
                                               for b in data[i:i + 16]))
    return '\n'.join(out) if out else '        .byt $00'


def _paged_pools(m) -> set:
    """Which of the 3 programmable pools exceed the engine's 8-bit position
    (ledger C8 sixth widening / backlog item 19c). from_usf's pass-2 packer
    guarantees no program straddles a 256-byte page, so the position stays an
    in-page offset and only the read operands' HI byte (the page) varies —
    selected per voice by the SMC patch stubs `_apply_pool_paging` splices."""
    if getattr(m, 'force_paged', False):   # from_usf._FORCE_PAGED (tests only)
        return {'wave', 'pulse', 'filter'}
    return {nm for nm, t in (('wave', m.wave), ('pulse', m.pulse),
                             ('filter', m.filter)) if len(t) > 256}


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
    # freq tables, extended IN-BOUNDS with the off-table arpeggio frequencies.
    # A melodic wave step reads freqlo,y / freqhi,y with y = (offset + note); when
    # that index runs past the 96-entry tables the orig played an engine-state
    # byte as a frequency. We place the EXPLICIT freq (from each instrument's
    # `offtable_freq`) at that index, so the lookup stays in-bounds — no OOB read,
    # no freq_overrun window, no verbatim blob. (`offtable_freq` is the ML-musical
    # per-(step,note) frequency; idx = wave program's freq at `step` + note.)
    ext_lo = list(m.freq_lo)
    ext_hi = list(m.freq_hi)
    ov = {}
    for ins in m.instruments:
        for offset, note, lo, hi in getattr(ins, 'offtable_freq', []) or []:
            idx = (offset + note) & 0xFF
            if idx > 95:
                ov[idx] = (lo, hi)
    if ov:
        top = max(ov)
        ext_lo += [0] * (top + 1 - len(ext_lo))
        ext_hi += [0] * (top + 1 - len(ext_hi))
        for idx, (lo, hi) in ov.items():
            ext_lo[idx] = lo
            ext_hi[idx] = hi
    d.append('freqlo:\n' + _byt(ext_lo))
    d.append('freqhi:\n' + _byt(ext_hi))
    # the 3 programmable 2-byte tables (split lo/hi parallel arrays). A PAGED
    # pool's arrays are page-aligned so `>label + page` addresses page k of the
    # pool exactly (the SMC stubs store that sum into the read operands).
    paged = _paged_pools(m)
    _align = ('        .dsb (256 - (* & 255)) & 255, $00'
              '   ; page-align (paged pool)\n')

    def _pool(nm, lab, data):
        return (_align if nm in paged else '') + f'{lab}:\n' + _byt(data)
    d.append(_pool('wave', 'wavectrl', [c for c, f in m.wave]))
    d.append(_pool('wave', 'wavefreq', [f for c, f in m.wave]))
    d.append(_pool('pulse', 'pulselo', [lo for lo, hi in m.pulse]))
    d.append(_pool('pulse', 'pulsehi', [hi for lo, hi in m.pulse]))
    d.append(_pool('filter', 'filterlo', [lo for lo, hi in m.filter] or [0]))
    d.append(_pool('filter', 'filterhi', [hi for lo, hi in m.filter] or [0]))
    if paged:
        pages = getattr(m, 'instr_pages', None)
        if pages is None or len(pages) != len(m.instruments):
            raise RuntimeError(
                'paged pools without instr_pages — build the model through '
                'from_usf.usf_to_model (its pass-2 packer records the pages)')
        pg = []
        for (w, p, f) in pages:
            pg += [w, p, f, 0, 0, 0, 0, 0]     # stride 8 = the instr record
        d.append('instpg:\n' + _byt(pg))       # indexed by instr_n*8 (Y)
    # per-voice leftover note ($100F-$1011): the lead-in effects frame(s)
    # read it before the first fetch. ONE source — the extract reads it from
    # whichever address that member's player keeps it at (the Jupiter41
    # variant uses $1012-$1014), so the composer no longer asks which player
    # this was (Principle §8).
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
        bne sd_ef
        iny
        lda ($f8),y
        sta fadeout
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_ef:
        cmp #$ef                ; family-4 $EF nn: per-voice freq-lo BIAS
        bne sd_f0               ; ($1842,x), added in the wave-step (frqbias)
        iny
        lda ($f8),y
        sta frqbias,x
        inc secpos,x
        inc secpos,x
        jmp sector_disp
sd_f0:
        cmp #$f0                ; family-4 $F0 nn: per-note vib width (nn&7).
        bne sd_done             ; (the wave/freq re-load part is deferred; the
        iny                     ; command is byte-synced so the walk stays in
        lda ($f8),y             ; step and the member builds.)
        and #$07
        sta vibwidth
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
        ;; WAVESPD
        lda #$00                ; wave-speed reload (family-3: advance every frame)
        sta wavespd,x
        sta wavespc,x
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
        lda wavespc,x           ; wave-speed counter: hold N frames per step
        beq ws_adv_now          ; 0 -> advance now (family-3: speed always 0)
        dec wavespc,x
        jmp ws_done
ws_adv_now:
        inc wavepos,x
        lda wavespd,x
        sta wavespc,x
ws_done:

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


_POOL_TABLES = {'wave': ('wavectrl', 'wavefreq'),
                'pulse': ('pulselo', 'pulsehi'),
                'filter': ('filterlo', 'filterhi')}


def _apply_pool_paging(engine: str, state: str, m) -> 'tuple[str, str]':
    """Splice the paged-pool machinery into the FINAL engine text (after all
    mechanism-knob replaces, so variant-substituted read sites are seen).

    Ledger C8 sixth widening (backlog item 19c): a pool past 256 entries keeps
    its 8-bit per-voice position as an IN-PAGE offset (from_usf's packer never
    lets a program straddle a page) and the page moves into the read operands'
    HI byte. The three voices can sit on different pages at once, so the
    operands are SMC-patched per voice: at note_init2 (the new instrument's
    pages, from the stride-8 `instpg` table while Y still holds instr_n*8) and
    at each read block's entry (eff_steady / wave_step / filter_run) from the
    per-voice `wavepg,x`/`pulsepg,x` (filterpos is GLOBAL and V3-only, so one
    `filtpg` byte set only when a program is SET). All three registers live in
    the cleared state block, so a re-init lands every voice back on page 0 and
    the entry stubs re-patch before the first read.
    """
    paged = _paged_pools(m)
    # per-voice page registers inside state0..state_end (init clears -> page 0)
    st_anchor = 'pulsepos: .dsb 3, 0'
    if st_anchor not in state:
        raise RuntimeError('paged pools: state-block anchor moved')
    state = state.replace(
        st_anchor,
        st_anchor + '\n'
        'wavepg:   .dsb 3, 0\n'
        'pulsepg:  .dsb 3, 0\n'
        'filtpg:   .dsb 1, 0')
    tbl_of = {}                       # array label -> pool name
    for nm, labels in _POOL_TABLES.items():
        if nm in paged:
            for la in labels:
                tbl_of[la] = nm
    site_re = re.compile(r'^\s+(lda|cmp)\s+(' + '|'.join(tbl_of) + r'),y\b')
    # read-site region -> which page register serves it
    region_of = {'wave': {'note_init2': 'NI', 'wave_step': 'WS'},
                 'pulse': {'note_init2': 'NI', 'eff_steady': 'PR'},
                 'filter': {'note_init2': 'NI', 'filter_run': 'FR'}}
    anchors = {'note_init2:', 'eff_steady:', 'filter_run:', 'glide_slide:',
               'wave_step:', 'gate_logic:'}
    region = None
    out, groups, n = [], {}, 0        # groups: (grp, array label) -> [labels]
    for line in engine.split('\n'):
        stripped = line.strip()
        if stripped in anchors:
            region = stripped[:-1]
        mm = site_re.match(line)
        if mm:
            arr = mm.group(2)
            grp = region_of[tbl_of[arr]].get(region)
            if grp is None:
                raise RuntimeError(
                    f'paged pool {tbl_of[arr]}: read site in unexpected '
                    f'region {region!r}: {stripped!r}')
            lab = f'zpg{n}'
            n += 1
            groups.setdefault((grp, arr), []).append(lab)
            out.append(f'{lab}:')
        out.append(line)
    engine = '\n'.join(out)

    def patch(grp, pool, pgsrc):
        """Store `>array + page` into every (grp, array) site's operand HI
        byte. The page registers hold the raw PAGE NUMBER (0..n), so each
        array group adds its own base hi byte — the arrays are page-aligned,
        so `>array + page` addresses page `page` of that array exactly."""
        s, found = '', False
        for arr in _POOL_TABLES[pool]:
            labs = groups.get((grp, arr), [])
            if not labs:
                continue
            found = True
            s += (f'        lda {pgsrc}\n        clc\n'
                  f'        adc #>{arr}\n'
                  + ''.join(f'        sta {la}+2\n' for la in labs))
        return s, found

    # --- note_init2: patch the ni read sites for the NEW instrument --------
    # (Y still holds instr_n*8 here — instpg is stride-8 like the record)
    ni = ''
    if 'wave' in paged:
        s, _ = patch('NI', 'wave', 'wavepg,x')
        ni += '        lda instpg,y\n        sta wavepg,x\n' + s
    if 'pulse' in paged:
        s, _ = patch('NI', 'pulse', 'pulsepg,x')
        ni += '        lda instpg+1,y\n        sta pulsepg,x\n' + s
    if 'filter' in paged:
        # FL=0 = "no restart": the running program (and its page) continues
        s, _ = patch('NI', 'filter', 'filtpg')
        ni += ('        lda filtflag\n        beq zpgnof\n'
               '        lda instpg+2,y\n        sta filtpg\n'
               + s + 'zpgnof:\n')
    ni_anchor = '        ;; first wave-table step\n'
    if ni_anchor not in engine:
        raise RuntimeError('paged pools: note_init2 anchor moved')
    engine = engine.replace(ni_anchor, ni_anchor + ni, 1)
    # --- steady read blocks: re-patch at entry (any voice may have jumped
    #     here without passing note_init2 this frame) -----------------------
    if 'pulse' in paged:
        s, found = patch('PR', 'pulse', 'pulsepg,x')
        if not found:
            raise RuntimeError('paged pulse pool: no pulse_run read sites')
        engine = engine.replace('eff_steady:\n', 'eff_steady:\n' + s, 1)
    if 'wave' in paged:
        s, found = patch('WS', 'wave', 'wavepg,x')
        if not found:
            raise RuntimeError('paged wave pool: no wave_step read sites')
        engine = engine.replace('wave_step:\n', 'wave_step:\n' + s, 1)
    if 'filter' in paged:
        s, found = patch('FR', 'filter', 'filtpg')
        if not found:
            raise RuntimeError('paged filter pool: no filter_run read sites')
        i = engine.index('filter_run:')
        j = engine.index('        ldy filterpos', i)
        engine = engine[:j] + s + engine[j:]
    return engine, state


def emit_v5_asm(m, origin: int = 0x1000) -> str:
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
wavespd:  .dsb 3, 0
wavespc:  .dsb 3, 0
frqbias:  .dsb 3, 0
pulsepos: .dsb 3, 0
vibdel:   .dsb 3, 0
vibspd:   .dsb 3, 0
vibrev:   .dsb 3, 0
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
filtbase: .dsb 1, 0
filtactive: .dsb 1, 0
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
    # Filter mode + starting cutoff: ONE source each. The extract reads them
    # from whichever address the member's player keeps them at, so these are
    # plain leftovers here rather than a per-player choice (Principle §8).
    consts = (f'LEFT_FILTMODE = ${m.lo_filtmode:02X}\n'
              f'LEFT_FCHI = ${m.lo_fchi:02X}\n'
              f'LEFT_FCLO = ${m.lo_fclo:02X}\n'
              f'LEFT_SPDCTR = ${m.lo_spdctr:02X}\n'
              f'LEFT_MVOLFRAC = ${m.lo_mvolfrac:02X}\n')
    # origin: the asm is fully label-based; the single `* = $1000` is the
    # only origin-dependent line (a heterogeneous compilation splices this
    # engine at an arbitrary address, ledger C31/C35 — same knob as
    # compose_dmc_asm's `origin`).
    engine = _ENGINE.replace('* = $1000', '* = $%04X' % origin)
    # family-4 (Jupiter41) WRITE-ORDER knob (ledger C16): family-4's note-on
    # writes ONLY SR/AD/CTRL on the TICK frame — it does NOT write FREQ=$0000
    # (the wave-step on the NEXT frame writes the real freq). The family-3
    # note-on writes FREQ=$0000 here; drop those 2 writes for family-4 so the
    # note-on emission order matches (note-on pass = SR/AD/CTRL only).
    # ---- PLAYER-MECHANISM KNOBS (Principle §8) -------------------
    # These branches used to sit inside one `if m.family4:` gate — a flag
    # naming the ORIGINATING PLAYER, read by emitters, which is exactly the
    # shape §8 forbids. Each is now guarded by the MECHANISM it changes, so a
    # future player exhibiting any one of them can set it alone, and the
    # composer never learns which engine the music came from. The Jupiter41
    # variant simply sets all thirteen (see the extract).
    if int(getattr(m, 'play_skip_init', 2)) != 2:
        # PLAY-SKIP: family-3's play opens `LDA $1842 / BEQ / DEC $1842 / JMP
        # exit`, and its canon init ends `LDA #$02 / STA $1842` — so the first
        # two play() calls of a family-3 tune do nothing at all. family-4's play
        # ($1095) has NO such counter: it goes straight into the DEC $1016
        # 2-phase toggle. Emitting family-3's skip here put two silent frames in
        # front of every family-4 rebuild, i.e. the whole tune ran 40 ms late.
        #
        # The flat write-stream verdict CANNOT see this — an empty frame
        # contributes nothing to the concatenated stream, so both streams still
        # line up. It is a real defect that no gate catches, which is exactly
        # why it is worth fixing rather than leaving. (It is also why the fix is
        # invisible in the FULL counts: the phase seed above is what moves them.)
        #
        # NB no USF field is needed: the skip count is DERIVABLE from the player
        # variant, which the USF already carries. family-4 -> 0, family-3 -> the
        # canon 2.
        engine = engine.replace(
            '        lda #$02\n        sta playskip',
            '        lda #$00                ; family-4 play has no $1842 skip\n'
            '        sta playskip')
    if getattr(m, 'noteon_skip_freq_clear', False):
        engine = engine.replace(
            '        sta notestart,x\n        lda #$00\n'
            '        sta $d400,y\n        sta $d401,y\n        inc secpos,x',
            '        sta notestart,x\n        inc secpos,x')
    if int(getattr(m, 'dur_ctr_init', 1)) != 1:
        # family-4 init seeds the per-voice DURATION counter to 2 ($17E5,x=2);
        # the family-3 default is 1. The 2-phase ticks on even frames so the
        # first note-on lands at frame 2 (durctr 2->1->0). Preserve vactive=$01.
        engine = engine.replace(
            '        sta durctr,x\n        sta vactive,x',
            '        pha\n        lda #$02\n        sta durctr,x\n'
            '        pla\n        sta vactive,x')
    if getattr(m, 'wave_speed_from_instr', False):
        # family-4 wave-SPEED counter: the instrument's byte 6 ($2293,y) >> 4 is
        # the wave-step advance period ($1845/$1848 in the orig). family-3 has no
        # speed (advances every frame). Without this the wave program sweeps every
        # frame instead of holding each step N frames (the steady-note divergence).
        engine = engine.replace(
            '        ;; WAVESPD\n        lda #$00'
            '                ; wave-speed reload (family-3: advance every frame)\n'
            '        sta wavespd,x\n        sta wavespc,x',
            '        ;; WAVESPD\n        lda instr+6,y\n        lsr\n        lsr\n'
            '        lsr\n        lsr\n        sta wavespd,x\n        sta wavespc,x')
    if getattr(m, 'wave_speed_from_instr', False):
        # family-4 note-init first-step must use the SAME speed-gated advance as
        # the per-frame ws_adv: family-3 unconditionally advances (`inc wavepos`)
        # after the first step, but family-4's first step IS a real wave step
        # under the speed counter. Without this, a speed-0 instrument emits its
        # first wave value TWICE (note_init2 reads pos N without advancing, then
        # eff_steady re-reads pos N) — the V2 drum's extra DD00 frame. With it:
        # speed 0 advances now (one DD00), speed>0 holds (V1's 6-frame note).
        engine = engine.replace(
            '        ldy wavepos,x\n        inc wavepos,x\n        lda wavectrl,y',
            '        ldy wavepos,x\n'
            '        lda wavespc,x\n        beq ni_ws_adv\n        dec wavespc,x\n'
            '        jmp ni_ws_done\n'
            'ni_ws_adv:\n        inc wavepos,x\n        lda wavespd,x\n'
            '        sta wavespc,x\n'
            'ni_ws_done:\n        lda wavectrl,y')
    if getattr(m, 'volovr_ad_zero', False):
        # family-4 vol-override note-on ($1352) writes AD=$00 (not the instrument
        # AD): the SR carries the vol level (volovr<<4 | instr_SR&$0f) and the AD
        # is forced to $00. family-3 keeps the instrument AD. Force AD=$00 on the
        # vol-override path; the non-override path is unchanged.
        engine = engine.replace(
            '        ora tmp40\n        sta $d406,y\n        jmp no_ad',
            '        ora tmp40\n        sta $d406,y\n        pla\n        lda #$00\n'
            '        sta $d405,y\n        jmp ni_voldone')
    if getattr(m, 'volovr_ad_zero', False):
        engine = engine.replace(
            '        sta $d405,y\n        lda durrel,x',
            '        sta $d405,y\nni_voldone:\n        lda durrel,x')
    if getattr(m, 'pulse_ctr_8bit', False):
        # family-4 pulse_run uses an 8-bit step counter ($1830 vs $23BC[pos+1]),
        # not the family-3 16-bit counter (pulselo[pos+1]:pulsehi[pos+1]). With the
        # 16-bit check, family-4's nonzero pulselo[pos+1] ($23A3) makes pwctr_hi(0)
        # != pulselo[pos+1] so the pulse never advances (PW frozen at the 0-add
        # step — V3's PWM sweep never starts). Use an 8-bit counter for family-4.
        engine = engine.replace(
            '        lda pwctr_lo,x\n        clc\n        adc #$01\n'
            '        sta pwctr_lo,x\n        lda pwctr_hi,x\n        adc #$00\n'
            '        sta pwctr_hi,x\n        cmp pulselo,y\n        bne filter_run\n'
            '        lda pwctr_lo,x\n        cmp pulsehi,y\n        bne filter_run',
            '        inc pwctr_lo,x\n        lda pwctr_lo,x\n'
            '        cmp pulsehi,y\n        bne filter_run')
    if getattr(m, 'noteload_no_d418', False):
        # family-4's note-LOAD writes only SR/AD/CTRL (C16) — NOT $D418. The orig's
        # note-load (TICK) doesn't touch $D418; the per-voice write_vol path emits it
        # for the non-loading voices. note_init2's $D418 is an extra write for fam-4.
        engine = engine.replace(
            '        lda filtmode\n        ora mvol0\n        sta $d418\n'
            '        lda instr_n,x',
            '        lda instr_n,x')
    if getattr(m, 'filter_v3_only', False):
        # family-4 keeps V3 on the DEFAULT filter program (filterpos walks from 0,
        # swept continuously by filter_run); the orig never runs a per-instrument
        # filter init for V3 (it stays idle / inst 0). Force filtflag=0 so the
        # note-on never resets filterpos/fchi from an instrument byte4 — otherwise
        # the rebuild jumps filterpos to a byte4 value and corrupts the sweep.
        # family-4: V3 plays inst-0 notes that RE-INIT the filter (note-on sets
        # filterpos=filter_ptr, fchi=filterlo[filter_ptr]=the start cutoff, then
        # INC; filter_run sweeps from there). filter_ptr is now the composer's
        # OWN re-packed index (from the per-instrument 8-bit SweepEnvelope capture),
        # so `lda instr+4,y` reads the right program. The orig's filter init ($1411)
        # is V3-ONLY (CPX #$02) — so filtflag = byte4 only for V3; V1/V2 get 0 (their
        # notes must NOT touch the global filter state).
        engine = engine.replace(
            '        lda instr+4,y           ; filter ptr\n        sta filtflag',
            '        lda instr+4,y           ; filter ptr (V3-only)\n'
            '        cpx #$02\n        beq f4_flt_v3\n        lda #$00\n'
            'f4_flt_v3:\n        sta filtflag\n'
            '        lda filtflag            ; restore Z (cpx clobbered it) for'
            ' the\n                                ; following `beq ni_nofilt`')
    if getattr(m, 'filter_needs_cmd', False):
        # family-4: the V3 filter sweep is gated by $1857 (set by $F9), so it does
        # NOT run until the first $F9 fires (~frame 2-3). The composer otherwise
        # sweeps from frame 0 → the whole sweep is ~2 frames early. Set filtactive
        # in sd_f9 ($F9) and gate the V3 filter_run on it.
        engine = engine.replace(
            '        and #$f0\n        sta filtmode\n        inc secpos,x',
            '        and #$f0\n        sta filtmode\n        lda #$01\n'
            '        sta filtactive\n        inc secpos,x')
    if getattr(m, 'filter_needs_cmd', False):
        engine = engine.replace(
            '        cpx #$02                ; V3 only\n        bne glide_slide',
            '        cpx #$02                ; V3 only\n        bne glide_slide\n'
            '        lda filtactive\n        beq glide_slide')
    if getattr(m, 'filter_d416_only', False):
        # family-4 FILTER (C-2): $D416-only = fchi($1019 sweep) + filtbase($1853);
        # no per-frame $D415 (init clear leaves it $00). $F8 sets the filter base
        # ($1853) not frqovr; $F9 (sd_f9, already family-4-shaped) sets $D417 res +
        # filtmode. The filter_run uses an 8-bit counter (like the pulse) and only
        # the fchi byte gets the $23D5 add (no fclo carry into fchi).
        engine = engine.replace(
            '        iny\n        lda ($f8),y\n        sta frqovr',
            '        iny\n        lda ($f8),y\n        sta filtbase')
    if getattr(m, 'filter_d416_only', False):
        engine = engine.replace(
            '        lda fclo\n        sta $d415\n        lda fchi\n'
            '        sta $d416\n        rts',
            '        lda fchi\n        clc\n        adc filtbase\n'
            '        sta $d416\n        rts')
    if getattr(m, 'filter_d416_only', False):
        engine = engine.replace(
            '        lda fclo\n        clc\n        adc sclo\n        sta fclo\n'
            '        lda fchi\n        adc schi\n        sta fchi\n'
            '        lda filtctr_lo\n        clc\n        adc #$01\n'
            '        sta filtctr_lo\n        lda filtctr_hi\n        adc #$00\n'
            '        sta filtctr_hi\n        cmp filterlo,y\n        bne glide_slide\n'
            '        lda filtctr_lo\n        cmp filterhi,y\n        bne glide_slide\n'
            '        lda #$00\n        sta filtctr_lo\n        sta filtctr_hi\n'
            '        inc filterpos\n        inc filterpos',
            '        lda fchi\n        clc\n        adc schi\n        sta fchi\n'
            '        inc filtctr_lo\n        lda filtctr_lo\n'
            '        cmp filterhi,y\n        bne glide_slide\n'
            '        lda #$00\n        sta filtctr_lo\n'
            '        inc filterpos\n        inc filterpos')
    if getattr(m, 'wave_step_carry', False):
        # family-4 melodic wave-step propagates the CARRY from (wavefreq+curnote)
        # into freqlo via `adc frqbias,x` with NO clc (the orig's $1688 lacks one):
        # when wavefreq+curnote >= 256 the freq is +1. frqbias is the $EF freq-lo
        # bias (default 0; $EF decode deferred — Jupiter41 doesn't use it). Hits
        # BOTH the per-frame ws_mel and the note-init ni_w_mel (identical blocks).
        engine = engine.replace(
            '        adc curnote,x\n        tay\n'
            '        lda freqlo,y\n        sta freqlov,x\n'
            '        lda freqhi,y\n        sta freqhiv,x',
            '        adc curnote,x\n        tay\n'
            '        lda freqlo,y\n        adc frqbias,x\n        sta freqlov,x\n'
            '        lda freqhi,y\n        adc #$00\n        sta freqhiv,x')
    if getattr(m, 'vib_from_instr_bytes', False):
        # family-4 vibrato (note-on $138F; state machine $157C): onset delay = byte5
        # ($1806), period = byte6 & $0F ($1809 — the UP/DOWN step count; byte6's HIGH
        # nibble is the wave speed), width = byte7 & $07. Same byte map as family-3
        # EXCEPT vibspd masks to byte6's low nibble (family-3 uses the whole byte).
        engine = engine.replace(
            '        lda instr+6,y           ; vib speed\n'
            '        sta vibspd,x',
            '        lda instr+6,y           ; family-4: vib period = byte6 & $0F\n'
            '        and #$0f\n        sta vibspd,x')
    if getattr(m, 'd418_skip_vib_reversal', False):
        # family-4: the orig skips the per-voice $D418 write ONLY on a vib REVERSAL
        # frame — the oscillating path WRITES $D418 every frame ($15B0 BNE $1612)
        # EXCEPT when the counter hits the bound and the direction flips ($158F jumps
        # to $1654, bypassing $1651). Set a `vibrev` flag on reversal (cleared each
        # frame at vib_on entry) and skip $D418 when vibspd!=0 && vibrev!=0.
        engine = engine.replace(
            'vib_on:\n        lda vibdel,x',
            'vib_on:\n        lda #$00\n        sta vibrev,x\n        lda vibdel,x')
    if getattr(m, 'd418_skip_vib_reversal', False):
        # only the UP reversal unconditionally skips $D418 ($158F→$1654); the DOWN
        # reversal skips ONLY when step-doubling is on ($15FB: BEQ $1612 writes when
        # $1812=byte7>>4 == 0). Jupiter41's vib instruments have no step-doubling, so
        # set vibrev on the UP reversal only (the `inc vibdir,x` path).
        engine = engine.replace(
            '        sta vibctr,x\n        inc vibdir,x',
            '        sta vibctr,x\n        inc vibrev,x\n        inc vibdir,x')
    if getattr(m, 'd418_skip_vib_reversal', False):
        engine = engine.replace(
            'write_vol:\n        lda mvol0\n        ora filtmode\n        sta $d418',
            'write_vol:\n        lda vibspd,x\n        beq f4wv_w\n'
            '        lda vibrev,x\n        bne f4wv_skip\n'
            'f4wv_w:\n        lda mvol0\n        ora filtmode\n        sta $d418\n'
            'f4wv_skip:')
    # CIA multispeed: when the original drives play() via a CIA1 timer (PSID
    # speed bit set), program the SAME timer A latch in our init so libsidplayfp
    # calls OUR play() at the identical rate. cia_period 0 = VBI (no-op).
    cia_period = int(getattr(m, 'cia_period', 0)) & 0xFFFF
    if cia_period:
        consts += f'CIA_PERIOD = ${cia_period:04X}\n'
        cia_init = ('        lda #<CIA_PERIOD\n'
                    '        sta $dc04                ; CIA1 timer A lo (play rate)\n'
                    '        lda #>CIA_PERIOD\n'
                    '        sta $dc05                ; CIA1 timer A hi\n'
                    '        lda #$11\n'
                    '        sta $dc0e                ; start timer A, continuous\n')
        engine = engine.replace(
            '        sta playskip\n        rts',
            '        sta playskip\n' + cia_init + '        rts')
    # paged pools (C8 sixth widening) — LAST, so the site scan sees the final
    # (knob-substituted) engine text. No paged pool => both strings unchanged.
    if _paged_pools(m):
        engine, state = _apply_pool_paging(engine, state, m)
    return consts + engine + '\n' + _emit_data(m) + '\n' + state


def _apply_play_phases(asm: str, m) -> str:
    """Ledger C18: splice a per-call PHASE dispatcher in front of the play body.

    A V5 wrapper member's play vector runs the FULL play only every Nth call and
    an EFFECTS-ONLY pass on the others (the original's third jump-table entry:
    canon `run_effects` per voice, no tick, no fetch, no $D415/$D416 tail). The
    tune's real tempo is that divided rate — without this the rebuild runs the
    full play on every IRQ, so it is N× too fast AND one tick out of phase from
    the very first frame.

    The schedule is OBSERVED per member (factory `_observe_play_phases`), never
    derived from the wrapper's code — the shapes vary far too much (SMC operand
    counter, modulo gate, CMP gate, CIA-latch swing) and the C18 card is explicit
    that observation is the method.

    Token vocabulary matches v4's `play_phases` exactly, so the two families
    speak one language: `P` = full play, `F<voices>` = per-voice effects only,
    `S` = a call that writes nothing.

    No schedule => the asm is returned UNCHANGED, so every canon member stays
    byte-identical.
    """
    sched = str(getattr(m, 'play_phases', '') or '')
    tokens = [t for t in sched.split('_') if t]
    if len(tokens) < 2:
        return asm
    ok = all(t == 'P' or t == 'S'
             or (t[0] == 'F' and t[1:] and set(t[1:]) <= set('123'))
             for t in tokens)
    if not ok:
        return asm
    kinds = []
    for t in tokens:
        if t not in kinds:
            kinds.append(t)
    disp, routines = '', ''
    for k, t in enumerate(kinds):
        disp += f'        cmp #{k}\n        beq ph_r{k}\n'
        if t == 'P':
            body = '        jmp playframe                ; P = full play\n'
        elif t == 'S':
            body = '        rts                          ; S = silent call\n'
        else:                                    # F<voices>: effects only
            body = ''
            for v in t[1:]:
                body += (f'        ldx #{int(v) - 1}\n'
                         '        jsr run_effects\n')
            body += '        rts\n'
        routines += f'ph_r{k}:\n{body}'
    n_ph = len(tokens)
    tab = ','.join(str(kinds.index(t)) for t in tokens)
    wrapper = (
        'playphases:\n'
        '        ldy phasectr\n'
        '        iny\n'
        f'        cpy #{n_ph}\n'
        '        bne ph_set\n'
        '        ldy #$00\n'
        'ph_set:\n'
        '        sty phasectr\n'
        '        lda phasetab,y\n'
        + disp
        + '        rts                          ; (unreachable)\n'
        + routines
        + f'phasetab: .byt {tab}\n'
        # seeded to n-1 so the FIRST call increments to 0 = tokens[0], i.e. the
        # schedule starts exactly where the observation started (call 0).
        + f'phasectr: .byt {n_ph - 1}\n\n')
    # Point the jump table at the wrapper and define it just before the play
    # body. The PSID header keeps play = LOAD+3, so nothing else moves.
    #
    # ⚠ ASSERT BOTH ANCHORS. A `str.replace` that finds nothing returns the
    # string unchanged, so a renamed label here would silently produce a build
    # with the wrapper DEFINED BUT NEVER REACHED — it assembles, it verifies as
    # a partial, and it looks exactly like the bug still being unfixed. The
    # session that added this had already been bitten by the same shape twice
    # (a `.get('first_diff')` that always returned None; a `_worker_init` that
    # was never called), so fail loudly instead.
    jt_before = asm.count('        jmp playframe\n')
    body_before = asm.count('playframe:\n')
    if jt_before < 1 or body_before < 1:
        raise RuntimeError(
            f'play_phases: engine asm anchors moved (jump-table entries '
            f'{jt_before}, body labels {body_before}) — the phase wrapper '
            f'would be emitted but never entered')
    asm = asm.replace('        jmp playframe\n', '        jmp playphases\n', 1)
    return asm.replace('playframe:\n', wrapper + 'playframe:\n', 1)


def build_v5_sid(m) -> bytes:
    from pipelines.dmc.composer_asm import _sanitize_asm
    code = assemble(_sanitize_asm(_apply_play_phases(emit_v5_asm(m), m)))
    n_songs = len(m.subtunes) if m.subtunes else 1
    # CIA multispeed: set the PSID speed bit for every subtune so libsidplayfp
    # drives play() via the CIA1 timer A our init programs (cia_period 0 = VBI).
    speed = ((1 << n_songs) - 1) if int(getattr(m, 'cia_period', 0)) else 0
    # Header clock/SID-model flags from the model (extracted orig header):
    # write-log-blind but audible — a 6581 build of an 8580 tune sounds wrong.
    clock = {'PAL': 1, 'NTSC': 2, 'both': 3}.get(getattr(m, 'clock', 'PAL'), 0)
    sidm = {6581: 1, 8580: 2, 'both': 3}.get(getattr(m, 'sid_model', 6581), 0)
    header = build_header(load=0, init=LOAD, play=LOAD + 3, songs=n_songs,
                          start_song=1, speed=speed, title=m.title,
                          author=m.author, released=m.released,
                          flags=(clock << 2) | (sidm << 4))
    return header + bytes([LOAD & 0xFF, LOAD >> 8]) + code
