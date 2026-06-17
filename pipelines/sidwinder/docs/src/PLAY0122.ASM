;-------- Taki's Player V01.22 ---------


         *= $1000

         jmp m_init        ;initialize
         jmp irqplr        ;irq player
         jmp mltspd        ;multi-speed

         .byte $20,$2d,$54,$01,$0b,$09  ;" -Taki's Player V01.22-"
         .byte $27,$13,$20,$50,$0c,$01
         .byte $19,$05,$12,$20,$56,$30
         .byte $31,$2e,$32,$32,$2d
         .byte $3d,$3e,$20,$4d,$15,$13  ;"=> Music by Taki"
         .byte $09,$03,$20,$02,$19,$20
         .byte $54,$01,$0b,$09
         .byte $2f,$4e,$01,$14,$15,$12  ;"/Natural beat <="
         .byte $01,$0c,$20,$02,$05,$01
         .byte $14,$20,$3c,$3d

freqhi   .byte $01,$01,$01,$01,$01,$01
         .byte $01,$01,$01,$01,$01,$02
         .byte $02,$02,$02,$02,$02,$02
         .byte $03,$03,$03,$03,$03,$04
         .byte $04,$04,$04,$05,$05,$05
         .byte $06,$06,$06,$07,$07,$08
         .byte $08,$09,$09,$0a,$0a,$0b
         .byte $0c,$0d,$0d,$0e,$0f,$10
         .byte $11,$12,$13,$14,$15,$17
         .byte $18,$1a,$1b,$1d,$1f,$20
         .byte $22,$24,$27,$29,$2b,$2e
         .byte $31,$34,$37,$3a,$3e,$41
         .byte $45,$49,$4e,$52,$57,$5c
         .byte $62,$68,$6e,$75,$7c,$83
         .byte $8b,$93,$9c,$a5,$af,$b9
         .byte $c4,$d0,$dd,$ea,$f8,$00

freqlo   .byte $16,$27,$39,$4b,$5f,$74
         .byte $8a,$a1,$ba,$d4,$f0,$0e
         .byte $2d,$4e,$71,$96,$be,$e7
         .byte $14,$42,$74,$a9,$e0,$1b
         .byte $5a,$9c,$e2,$2d,$7b,$cf
         .byte $27,$85,$e8,$51,$c1,$37
         .byte $b4,$38,$c4,$59,$f7,$9e
         .byte $4e,$0a,$d0,$a2,$81,$6d
         .byte $67,$70,$89,$b2,$ed,$3b
         .byte $9d,$14,$a0,$45,$03,$db
         .byte $cf,$e1,$12,$65,$db,$76
         .byte $3a,$27,$41,$8a,$05,$b5
         .byte $9d,$c1,$24,$c9,$b6,$ed
         .byte $73,$4e,$82,$14,$0a,$6a
         .byte $3b,$82,$48,$93,$6b,$da
         .byte $e7,$9c,$04,$28,$14,$00

irqplr   lda vol_ct
         beq volend
         dec vol_ct        ;vol.ctrl
         bne volend
         lda vol_cr
         sta vol_ct
         lda volume
         clc
         adc vol_ad
         sta volume
         beq volend-5
         cmp #$0f
         bcc volend
         lda #$00
         sta vol_ct

volend   ldx #$00
         jsr player
         ldx #$07
         jsr player
         ldx #$0e

player   lda dur_dc,x
         sta lastdr,x
         bne *+5
         jmp firstf
         tay
         lda finish,x
         sta lastfn,x
         beq wframe+3
         lda gt_dec,x      ;gate timer
         beq wframe
         dec gt_dec,x
         bne wframe
         lda #$fe          ;gate off
         sta gt_msk,x
wframe   lda lastfn,x
         cpy #$02
         bcc lframe
         bne decsnd
         cmp #$80          ;last-1
         bcc decsnd
         lda #$fe
         sta gt_msk,x
         lda #$00
         sta $d405,x
         sta $d406,x
decsnd   dec dur_dc,x
         jmp p_test

lframe   cmp #$c0          ;last
         beq tracks
         lda sct_lo,x
         sta $fb
         lda sct_hi,x
         sta $fc
         ldy sctpos,x
         jmp sector
tracks   lda trk_lo,x
         sta $fb
         lda trk_hi,x
         sta $fc
         ldy trkpos,x
         lda ($fb),y
         cmp #$ff          ;Jmp00
         bne notjmp
         iny
         lda ($fb),y
         tay
         lda ($fb),y

notjmp   cmp #$f8          ;Inc00
         bcc notinc
         sbc #$f7          ;c=1
         asl a
         asl a
         asl a
         sta vol_ct
         sta vol_cr
         lda #$01          ;increase
         sta vol_ad
         iny
         jmp trkcmd

notinc   cmp #$f0          ;Dec00
         bcc notdec
         beq haltvp
nothlt   sbc #$f0          ;c=1
         asl a
         asl a
         asl a
         sta vol_ct
         sta vol_cr
         lda #$ff          ;decrease
         sta vol_ad
         iny
         jmp trkcmd

notdec   cmp #$e0          ;Vol00
         bcc notvol
         and #$0f
         sta volume
haltvp   lda #$00
         sta vol_ct
         iny
trkcmd   lda ($fb),y

notvol   cmp #$80
         bcs nottrp
         cmp #$40          ;Tr+00
         bcc settrp
         eor #$bf          ;Tr-00
         clc
         adc #$01
settrp   sta transp,x
         iny

nottrp   iny               ;Sct00
         tya
         sta trkpos,x
         dey
         lda ($fb),y
         and #$7f
         tay
         lda sctadl,y
         sta sct_lo,x
         sta $fb
         lda sctadh,y
         sta sct_hi,x
         sta $fc
         lda #$00
         sta sctpos,x
         tay

sector   lda ($fb),y
         cmp #$c0          ;Snd.00
         bcc nossnd
         and #$3f
         sta s_nmbr,x
         inc sctpos,x
         iny
         lda ($fb),y
nossnd   cmp #$80          ;Dur.01
         bcc nosdur
         and #$3f
         sta dur_rs,x
         inc sctpos,x
nosdur   dec dur_dc,x
         lda lastfn,x
         cmp #$c0
         beq *+5
         jmp p_test
         rts

firstf   lda sct_lo,x      ;1st frame
         sta $fb
         lda sct_hi,x
         sta $fc
         ldy sctpos,x
         lda ($fb),y
         cmp #$5f          ;---
         beq norest-3
         cmp #$6f          ;+++
         bne norest
         jmp setfin+3

norest   cmp #$60
         bcs *+5
         jmp normal
         inc sctpos,x
         iny
         clc
         adc #$01
         cmp #$70
         bcs nogld0
         and #$0f          ;Gld.01
         sta g_mode,x
         lda ($fb),y
         clc
         adc transp,x
         sta g_note
         tay
         lda freqlo,y
         sta acf_lo
         lda freqhi,y
         sta acf_hi
         inc sctpos,x
         ldy sctpos,x
         lda ($fb),y
         clc
         adc transp,x
         sta acnote,x
         tay
         lda acf_lo
         sec
         sbc freqlo,y
         sta g_addl,x
         lda acf_hi
         sbc freqhi,y
         sta g_addh,x
         cpy g_note
         beq glinit-5
         bcs glinit
         lda g_mode,x
         ora #$80          ;down
         bmi glinit-3

nogld0   and #$0f          ;Gld.11
         sta g_mode,x
         ldy acnote,x
         sty g_note
         lda freqlo,y
         sta acf_lo
         lda freqhi,y
         sta acf_hi
         ldy sctpos,x
         lda ($fb),y
         clc
         adc transp,x
         sta acnote,x
         tay
         lda acf_lo
         sec
         sbc freqlo,y
         sta g_addl,x
         lda acf_hi
         sbc freqhi,y
         sta g_addh,x
         cpy g_note
         bcc setbit
         bne normal-3
         lda #$00
         beq normal-6
setbit   lda g_mode,x
         ora #$80          ;down
         sta g_mode,x
         jmp setfin

normal   adc transp,x      ;c=0
         sta acnote,x
         lda #$00
         sta g_mode,x

glinit   lda #$ff
         sta gt_msk,x
         ldy s_nmbr,x
         lda snd_ad,y
         sta $d405,x
         lda snd_sr,y
         sta $d406,x
         lda snd_gt,y      ;gate off
         sta gt_dec,x
         lda snd_wt,y      ;wave
         sta w_pntr,x
         lda #$00
         sta w_cntr,x

         lda snd_pt,y
         cmp #$ff          ;no pls.rst
         beq tvinit
         sta p_pntr,x
         lda #$00
         sta p_cntr,x
         sta p_wdtl,x
         sta p_wdth,x

tvinit   lda snd_st,y
         cmp #$ff          ;no sld.rst
         beq tfinit
         sta v_pntr,x
         lda #$00
         sta v_cntr,x
         sta v_modl,x
         sta v_modh,x

tfinit   lda snd_ft,y
         cpx #$00
         bne filtrk
         cmp #$ff          ;no flt.rst
         beq setfin
         sta f_pntr
         stx f_cntr
         stx f_freq
         stx f_lres
         stx f_type
filtrk   cmp #$00
         beq nnfres
         lda filter,x
nnfres   sta flt_on,x

setfin   ldy sctpos,x
         lda dur_rs,x
         sta dur_dc,x
         inc sctpos,x
nxtcmd   iny
         lda ($fb),y
         bmi nxtcmd
         cmp #$7f
         bne t_rest
         lda #$c0          ;Finish
         bne setend
t_rest   cmp #$5f
         bne t_hold
         lda #$40          ;---
         bne setend
t_hold   cmp #$6f
         bcs t_zero
         lda #$80          ;notes
         bne setend
t_zero   lda #$00          ;+++
setend   sta finish,x
         lda lastfn,x
         bpl p_test
s_adsr   lda #$09          ;1st frame
         sta $d404,x
         rts


mltspd   ldx #$00          ;multi-speed
         jsr sounds
         ldx #$07
         jsr sounds
         ldx #$0e

sounds   lda lastfn,x
         bpl p_test
         lda lastdr,x
         beq s_adsr

p_test   ldy p_pntr,x      ;pulse fx
         beq w_test        ;pls.off
         lda p_cntr,x
         beq p_nrep
         dec p_cntr,x      ;repeat
         dey
         jmp p_ncmd+6
p_nrep   lda pls_rp,y
         cmp #$ff
         bne p_ncmd
         lda pls_ph,y      ;jump
         sta p_pntr,x
         tay
         lda pls_rp,y
p_ncmd   sta p_cntr,x      ;normal
         inc p_pntr,x
         lda p_wdtl,x
         clc
         adc pls_pl,y
         sta p_wdtl,x
         sta $d402,x
         lda p_wdth,x
         adc pls_ph,y
         sta p_wdth,x
         sta $d403,x

w_test   lda w_cntr,x      ;arpeggio
         beq w_nrep
         dec w_cntr,x
         jmp g_test
w_nrep   ldy w_pntr,x
         lda wve_wf,y
         cmp #$ff
         bne w_ncmd
         lda wve_st,y      ;jump
         sta w_pntr,x
         tay
         lda wve_wf,y
w_ncmd   inc w_pntr,x
         cmp #$90
         bcs w_srep
         sta w_form,x
         bcc w_norm
w_srep   sbc #$90          ;c=1
         sta w_cntr,x
w_norm   lda wve_st,y
         sta w_step,x

g_test   lda g_mode,x      ;glide fx
         beq v_test
         bmi g_down
         tay               ;up
         lda g_addl,x
         clc
         adc gld_al,y
         sta g_addl,x
         lda g_addh,x
         adc gld_ah,y
         sta g_addh,x
         bcc v_test
         bcs g_wend
g_down   and #$0f
         tay
         lda g_addl,x
         sec
         sbc gld_al,y
         sta g_addl,x
         lda g_addh,x
         sbc gld_ah,y
         sta g_addh,x
         bcs v_test
g_wend   lda #$00          ;off
         sta g_mode,x
         sta g_addl,x
         sta g_addh,x

v_test   ldy v_pntr,x      ;slide fx
         beq setsid        ;sld.off
         lda v_cntr,x
         beq v_nrep
         dec v_cntr,x      ;repeat
         dey
         jmp v_ncmd+6
v_nrep   lda sld_rp,y
         cmp #$fe          ;copy
         bcc v_ncmd
         beq v_copy
         lda sld_fh,y      ;jump
         sta v_pntr,x
         tay
         lda sld_rp,y
         cmp #$fe          ;copy
         bcc v_ncmd
v_copy   inc v_pntr,x
         lda sld_fl,y
         sta $d400,x
         lda sld_fh,y
         jmp direct        ;skip add's
v_ncmd   sta v_cntr,x
         inc v_pntr,x
         lda v_modl,x
         clc
         adc sld_fl,y
         sta v_modl,x
         lda v_modh,x
         adc sld_fh,y
         sta v_modh,x

setsid   lda acnote,x
         clc
         adc w_step,x
         tay
         lda g_mode,x
         beq laxity
         lda freqlo,y
         clc
         adc g_addl,x      ;glide
         sta $d400,x
         lda freqhi,y
         adc g_addh,x
         jmp direct
laxity   lda freqlo,y
         clc
         adc v_modl,x      ;slide
         sta $d400,x
         lda freqhi,y
         adc v_modh,x
direct   sta $d401,x
         lda w_form,x
         and gt_msk,x
         sta $d404,x

chkflt   cpx #$00          ;filter fx
         bne sndend
f_test   ldy f_pntr
         beq f_wsid
         lda f_cntr
         beq f_nrep
         dec f_cntr        ;repeat
         dey
         jmp f_ncmd+6
f_nrep   lda flt_rp,y
         cmp #$fe
         bcc f_ncmd
         beq f_nset
         lda flt_fh,y      ;jump
         sta f_pntr
         tay
         lda flt_rp,y
         cmp #$fe
         bcc f_ncmd
f_nset   lda flt_fh,y      ;set type
         sta f_type
         inc f_pntr
         iny
         lda flt_rp,y
f_ncmd   sta f_cntr        ;normal
         inc f_pntr
         lda f_lres
         clc
         adc flt_rl,y
         tax
         and #$f7
         sta f_lres
         sta $d415         ;freq lo
         txa
         and #$08
         cmp #$08          ;carry!
         lda f_freq
         adc flt_fh,y
         sta f_freq
         sta $d416         ;freq hi

f_wsid   lda f_lres        ;resonance
         and #$f0
         ora flt_on        ;filter on
         ora flt_on+$07
         ora flt_on+$0e
         sta $d417
         lda f_type        ;pass type
         ora volume
         sta $d418
sndend   rts


m_init   cmp #$20          ;initialize
         bcs sndend
         tay
         lda tr1adl,y      ;address lo
         sta trk_lo
         lda tr2adl,y
         sta trk_lo+$07
         lda tr3adl,y
         sta trk_lo+$0e
         lda tr1adh,y      ;address hi
         sta trk_hi
         lda tr2adh,y
         sta trk_hi+$07
         lda tr3adh,y
         sta trk_hi+$0e
         lda start1,y      ;startpos.
         sta trkpos
         lda start2,y
         sta trkpos+$07
         lda start3,y
         sta trkpos+$0e
         lda #$0f          ;variables
         sta volume
         ldy #$02
setvar   ldx offset,y
         lda #$03
         sta gt_dec,x
         sta dur_dc,x
         sta dur_rs,x
         lda #$c0
         sta finish,x
         lda sctadl
         sta sct_lo,x
         lda sctadh
         sta sct_hi,x
         lda #$00
         sta transp,x
         sta sctpos,x
         sta p_pntr,x
         sta v_pntr,x
         sta w_pntr,x
         sta s_nmbr,x
         dey
         bpl setvar
         sta f_pntr
         sta vol_ct
         sta vol_cr
         sta vol_ad
         ldy #$18
clrsid   sta $d400,y
         dey
         bpl clrsid
         rts


gt_dec   .byte $00
gt_msk   .byte $fe
lastfn   .byte $00
finish   .byte $00
lastdr   .byte $00
dur_dc   .byte $00
dur_rs   .byte $00,$00,$fe,$00,$00
         .byte $00,$00,$00,$00,$fe
         .byte $00,$00,$00,$00,$00

transp   .byte $00
trk_lo   .byte $00
trk_hi   .byte $00
trkpos   .byte $00
sct_lo   .byte $00
sct_hi   .byte $00
sctpos   .byte $00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00

p_pntr   .byte $00
p_cntr   .byte $00
p_wdtl   .byte $00
p_wdth   .byte $00
g_mode   .byte $00
g_addl   .byte $00
g_addh   .byte $00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00

v_pntr   .byte $00
v_cntr   .byte $00
v_modl   .byte $00
v_modh   .byte $00
w_pntr   .byte $00
w_cntr   .byte $00
w_form   .byte $00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00

w_step   .byte $00
s_nmbr   .byte $00
acnote   .byte $00
g_note   .byte $00
vol_ct   .byte $00
filter   .byte $01
flt_on   .byte $00,$00,$00,$00,$00
         .byte $00,$02,$00,$00,$00
         .byte $00,$00,$00,$04,$00

f_pntr   .byte $00
f_cntr   .byte $00
f_lres   .byte $00
f_freq   .byte $00
f_type   .byte $00
volume   .byte $00

acf_lo   = g_note+$07
acf_hi   = g_note+$0e
vol_cr   = vol_ct+$07
vol_ad   = vol_ct+$0e

offset   .byte $00,$07,$0e


         *= $1700
speeds   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         *= $1720
start1   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         *= $1740
start2   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         *= $1760
start3   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         *= $1780
tr1adl   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         *= $17a0
tr2adl   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         *= $17c0
tr3adl   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         *= $17e0
tr1adh   .byte $28,$29,$2a,$2b
         .byte $2c,$2d,$2e,$2f
         *= $1800
tr2adh   .byte $30,$31,$32,$33
         .byte $34,$35,$36,$37
         *= $1820
tr3adh   .byte $38,$39,$3a,$3b
         .byte $3c,$3d,$3e,$3f
         *= $1840
gld_al   .byte $00,$20,$40,$60,$80,$a0
         .byte $c0,$e0,$00,$20,$40,$60
         .byte $80,$a0,$c0,$e0
gld_ah   .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$01,$01,$01,$01
         .byte $01,$01,$01,$01


         *= $1880

sctadl   .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00

         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00

         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00

         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$00,$00,$00,$00

         *= $18e0

sctadh   .byte $40,$41,$42,$43,$44,$45
         .byte $46,$47,$48,$49,$4a,$4b
         .byte $4c,$4d,$4e,$4f,$50,$51
         .byte $52,$53,$54,$55,$56,$57

         .byte $58,$59,$5a,$5b,$5c,$5d
         .byte $5e,$5f,$60,$61,$62,$63
         .byte $64,$65,$66,$67,$68,$69
         .byte $6a,$6b,$6c,$6d,$6e,$6f

         .byte $70,$71,$72,$73,$74,$75
         .byte $76,$77,$78,$79,$7a,$7b
         .byte $7c,$7d,$7e,$7f,$80,$81
         .byte $82,$83,$84,$85,$86,$87

         .byte $88,$89,$8a,$8b,$8c,$8d
         .byte $8e,$8f,$90,$91,$92,$93
         .byte $94,$95,$96,$97,$98,$99
         .byte $9a,$9b,$9c,$9d,$9e,$9f


snd_ad   = $1940
snd_sr   = $1980
snd_gt   = $19c0
snd_wt   = $1a00
snd_ft   = $1a40
snd_pt   = $1a80
snd_st   = $1ac0

wve_wf   = $1b00
wve_st   = $1c00

flt_rp   = $1d00
flt_fh   = $1e00
flt_rl   = $1f00

pls_rp   = $2000
pls_pl   = $2100
pls_ph   = $2200

sld_rp   = $2300
sld_fl   = $2400
sld_fh   = $2500


;---------------------------------------
;
;
;SndTab: AD SR Gt Wt Ft Pt St
;
;AD      Attack, Decay
;SR      Sustain, Release
;Gt      Gate off counter
;Wt      Waveform pointer
;Ft      Filter pointer
;Pt      Pulse pointer
;St      Slide pointer
;
;
;WveTab: Wf St
;
;Wf      Waveform values
;        $90 Repeat arpeggio (-$8F)
;            & hold waveform
;        $FF Jump (Position: St)
;St      Arpeggio offset
;
;
;FltTab: Rp Fh Rl
;
;Rp      Repeat counter
;        $FE Type (Fh bits 4-6)
;        $FF Jump (Position: Fh)
;Fh      Frequency addition hi
;Rl      Resonance add + freq.add lo
;
;
;PlsTab: Rp Ph Pl
;
;Rp      Repeat counter
;        $FF Jump (Position: Ph)
;Ph      Pulse width addition hi
;Pl      Pulse width addition lo
;
;
;SldTab: Rp Fh Fl
;
;Rp      Repeat counter
;        $FE Copy freq to SID
;        $FF Jump (Position: Fh)
;Fh      Frequency addition hi
;Fl      Frequency addition lo
;
;
;GldTab: Ah Al
;
;Ah      Frequency addition hi
;Al      Frequency addition lo
;
;
;Next Instruction Lookahead
;
;  NextInst  HardRst  GateOff  Finish
;
;   Finish      +        +      $C0
;   Notes       +        +      $80
;    ---        -        +      $40
;    +++        -        -      $00
;   Gld.0*      +        +      $80
;   Gld.1*      -        -      $00
;
;
;Track & Sector Commands
;
; $00-$3F   Tr+00     $00-$5E   Notes
; $40-$7F   Tr-00     $5F        ---
; $80-$DF   Sct00     $60-$7E   Gld.01
; $E0-$EF   Vol00     $6F        +++
; $F0       HltVS     $7F       Finish
; $F1-$F7   Dec00     $80-$BF   Dur.01
; $F8-$FE   Inc00     $C0-$FF   Snd.00
; $FF       Jmp00
;
;
;---------------------------------------

.end
