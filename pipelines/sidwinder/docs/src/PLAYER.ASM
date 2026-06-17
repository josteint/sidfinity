;-  SIDwinder player
;   V01.23
;
;   (C) 1994-1999   Bal zs Tak cs        ( Takinb@sch.bme.hu )
;
;   (C) 1999-2000   Levente H rsfalvi    ( Levente@terrasoft.hu )
;
;   Released on 2000.03.15
;
;   This is a music player routine for the SID chip. It was developed by
;   Taki / Natural Beat and first released to the public in 1999. Later in
;   1999, the C64 TASM source was converted into ASCII text format and
;   slightly modified to fit with the syntax of Table Driven Assembler.
;
;   Player V01.23 is _almost identical to the original V01.22 it is based on.
;   Modifications:
;   - Simple source editing: now all labels are defined relative to the start
;     address of the player.
;   - Added modifications to compile to Plus/4
;     - Selectable SID base address
;     - Plus/4 freq table support (885Khz based frq values)
;   - Conditional asm rows to support editor channel on/off
;   - Changed initialization routine (editor sfx mode support, avoid clicks)
;   - As above, eliminated start(1,2,3) pointer support for player in the
;     packer
;   - Few small modifications in order to make the code a few bytes shorter
;   - The source was released under GPL
;
;
;   This program is free software; you can redistribute it and/or modify
;   it under the terms of the GNU General Public License as published by
;   the Free Software Foundation; either version 2 of the License, or
;   (at your option) any later version.
;
;   This program is distributed in the hope that it will be useful,
;   but WITHOUT ANY WARRANTY; without even the implied warranty of
;   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;   GNU General Public License for more details.
;
;   You should have received a copy of the GNU General Public License
;   along with this program; if not, write to the Free Software
;   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
;
;
;   Compiling needs:
;
;   - Table Driven Assembler 3.0.1 or later (ASM)
;   - ComLink V0.98 or later (linking)
;
;   The source can be compiled to run both on C-64 and Plus/4.
;   (Just define c64 or p4 with the TASM -d option in the command line)
;
;   Link with -th option
;


#ifndef LO
#define LO(x) (x&$ff)
#define HI(x) (x>>8)
#endif

#ifndef c64
#ifndef p4
#define c64
#endif
#endif

#ifndef sid
#define sid $d400
#endif

#ifndef editor
pt       =$fb                 ;poor TASM needs it to be defined at the
#endif                        ;start of the source :-(

pstart   =*

p_init   jmp m_init        ;initialize
p_play   jmp irqplr        ;irq player
p_mult   jmp mltspd        ;multi-speed

         .byte $20,$2d,$20,$20,$53,$49 ;" - SIDwinder"
         .byte $44,$17,$09,$0e,$04,$05
         .byte $12,$20
p_ver    .byte $56,$30,$31,$2e,$32,$33 ;"V01.23  -"
         .byte $20,$20,$2d
         .byte $2d,$4d,$15,$13,$09,$03 ;"- Music by (your handle / group)-"
         .byte $20,$02,$19,$20,$28,$19
         .byte $0f,$15,$12,$20,$08,$01
         .byte $0e,$04,$0c,$05,$20,$2f
         .byte $20,$07,$12,$0f,$15,$10
         .byte $29,$2d

#ifdef c64
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
         .byte $c4,$d0,$dd,$ea,$f8,$ff

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
         .byte $e7,$9c,$04,$28,$14,$ff
#endif

#ifdef p4
freqhi   .byte $01,$01,$01,$01,$01,$01
         .byte $01,$01,$01,$02,$02,$02
         .byte $02,$02,$02,$02,$03,$03
         .byte $03,$03,$03,$04,$04,$04
         .byte $04,$05,$05,$05,$06,$06
         .byte $06,$07,$07,$08,$08,$09
         .byte $09,$0a,$0a,$0b,$0c,$0c
         .byte $0d,$0e,$0f,$10,$11,$12
         .byte $13,$14,$15,$16,$18,$19
         .byte $1b,$1c,$1e,$20,$22,$24
         .byte $26,$28,$2b,$2d,$30,$33
         .byte $36,$39,$3d,$41,$44,$49
         .byte $4d,$51,$56,$5b,$61,$67
         .byte $6d,$73,$7a,$82,$89,$92
         .byte $9a,$a3,$ad,$b7,$c2,$ce
         .byte $da,$e7,$f5,$ff,$ff,$ff

freqlo   .byte $35,$48,$5b,$70,$86,$9d
         .byte $b6,$d0,$eb,$08,$27,$48
         .byte $6b,$90,$b7,$e0,$0c,$3a
         .byte $6b,$9f,$d6,$11,$4f,$90
         .byte $d6,$1f,$6d,$c0,$17,$74
         .byte $d6,$3e,$ac,$21,$9d,$20
         .byte $ab,$3e,$da,$7f,$2e,$e8
         .byte $ac,$7c,$59,$43,$3a,$40
         .byte $56,$7c,$b4,$ff,$5d,$d0
         .byte $58,$f9,$b2,$85,$74,$80
         .byte $ac,$f9,$69,$fd,$b9,$9f
         .byte $b1,$f1,$64,$0a,$e8,$01
         .byte $58,$f2,$d1,$fb,$73,$3e
         .byte $62,$e3,$c7,$14,$d0,$02
         .byte $b1,$e3,$a2,$f5,$e6,$7c
         .byte $c4,$c6,$8e,$ff,$ff,$ff
#endif

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
         sta sid+5,x
         sta sid+6,x
decsnd   dec dur_dc,x
         jmp p_test

lframe   cmp #$c0          ;last
         beq track
         lda sct_lo,x
         sta pt
         lda sct_hi,x
         sta pt+1
         ldy sctpos,x
         jmp sector
track    lda trk_lo,x
         sta pt
         lda trk_hi,x
         sta pt+1
         ldy trkpos,x
         lda (pt),y
         cmp #$ff          ;Jmp00
         bne notjmp
         iny
         lda (pt),y
         tay
         lda (pt),y

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
trkcmd   lda (pt),y

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
         lda (pt),y
         and #$7f
         tay
sctadl1  =*+1
.export sctadl1
         lda sctadl,y
         sta sct_lo,x
         sta pt
sctadh1  =*+1
.export sctadh1
         lda sctadh,y
         sta sct_hi,x
         sta pt+1
         lda #$00
         sta sctpos,x
         tay

sector   lda (pt),y
         cmp #$c0          ;Snd.00
         bcc nossnd
         and #$3f
         sta s_nmbr,x
         inc sctpos,x
         iny
         lda (pt),y
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
         sta pt
         lda sct_hi,x
         sta pt+1
         ldy sctpos,x
         lda (pt),y
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
         and #$0f
         bcs nogld0
         sta g_mode,x      ;Gld.01
         lda (pt),y
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
         lda (pt),y
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

nogld0                     ;Gld.11  (eliminated an AND #$0f - H.L.)
         sta g_mode,x
         ldy acnote,x
         sty g_note
         lda freqlo,y
         sta acf_lo
         lda freqhi,y
         sta acf_hi
         ldy sctpos,x
         lda (pt),y
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
snd_ad1  =*+1
.export snd_ad1
         lda snd_ad,y
         sta sid+5,x
snd_sr1  =*+1
.export snd_sr1
         lda snd_sr,y
         sta sid+6,x
snd_gt1  =*+1
.export snd_gt1
         lda snd_gt,y      ;gate off
         sta gt_dec,x
snd_wt1  =*+1
.export snd_wt1
         lda snd_wt,y      ;wave
         sta w_pntr,x
         lda #$00
         sta w_cntr,x
snd_pt1  =*+1
.export snd_pt1
         lda snd_pt,y
         cmp #$ff          ;no pls.rst
         beq tvinit
         sta p_pntr,x
         lda #$00
         sta p_cntr,x
         sta p_wdtl,x
         sta p_wdth,x

snd_st1  =*+1
.export snd_st1
tvinit   lda snd_st,y
         cmp #$ff          ;no sld.rst
         beq tfinit
         sta v_pntr,x
         lda #$00
         sta v_cntr,x
         sta v_modl,x
         sta v_modh,x

snd_ft1  =*+1
.export snd_ft1
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
         lda (pt),y
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

#ifdef editor              ;channel off; modif by H.L.
         and e_trx,x      ;trkon/off
#endif
         sta sid+4,x
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
pls_rp1  =*+1
.export pls_rp1
p_nrep   lda pls_rp,y
         cmp #$ff
         bne p_ncmd
pls_ph1  =*+1
.export pls_ph1
         lda pls_ph,y      ;jump
         sta p_pntr,x
         tay
pls_rp2  =*+1
.export pls_rp2
         lda pls_rp,y
p_ncmd   sta p_cntr,x      ;normal
         inc p_pntr,x
         lda p_wdtl,x
         clc
pls_pl1  =*+1
.export pls_pl1
         adc pls_pl,y
         sta p_wdtl,x
         sta sid+2,x
         lda p_wdth,x
pls_ph2  =*+1
.export pls_ph2
         adc pls_ph,y
         sta p_wdth,x
         sta sid+3,x

w_test   lda w_cntr,x      ;arpeggio
         beq w_nrep
         dec w_cntr,x
         jmp g_test
w_nrep   ldy w_pntr,x
wve_wf1  =*+1
.export wve_wf1
         lda wve_wf,y
         cmp #$ff
         bne w_ncmd
wve_st1  =*+1
.export wve_st1
         lda wve_st,y      ;jump
         sta w_pntr,x
         tay
wve_wf2 =*+1
.export wve_wf2
         lda wve_wf,y
w_ncmd   inc w_pntr,x
         cmp #$90
         bcs w_srep
         sta w_form,x
         bcc w_norm
w_srep   sbc #$90          ;c=1
         sta w_cntr,x
wve_st2  =*+1
.export wve_st2
w_norm   lda wve_st,y
         sta w_step,x

g_test   lda g_mode,x      ;glide fx
         beq v_test
         bmi g_down
         tay               ;up
         lda g_addl,x
         clc
gld_al1  =*+1
.export gld_al1
         adc gld_al,y
         sta g_addl,x
         lda g_addh,x
gld_ah1  =*+1
.export gld_ah1
         adc gld_ah,y
         sta g_addh,x
         bcc v_test
         bcs g_wend
g_down   and #$0f
         tay
         lda g_addl,x
         sec
gld_al2  =*+1
.export gld_al2
         sbc gld_al,y
         sta g_addl,x
         lda g_addh,x
gld_ah2  =*+1
.export gld_ah2
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
sld_rp1  =*+1
.export sld_rp1
v_nrep   lda sld_rp,y
         cmp #$fe          ;copy
         bcc v_ncmd
         beq v_copy
sld_fh1  =*+1
.export sld_fh1
         lda sld_fh,y      ;jump
         sta v_pntr,x
         tay
sld_rp2  =*+1
.export sld_rp2
         lda sld_rp,y
         cmp #$fe          ;copy
         bcc v_ncmd
v_copy   inc v_pntr,x
sld_fl1  =*+1
.export sld_fl1
         lda sld_fl,y
         sta sid,x
sld_fh2  =*+1
.export sld_fh2
         lda sld_fh,y
         jmp direct        ;skip add's
v_ncmd   sta v_cntr,x
         inc v_pntr,x
         lda v_modl,x
         clc
sld_fl2 =*+1
.export sld_fl2
         adc sld_fl,y
         sta v_modl,x
         lda v_modh,x
sld_fh3  =*+1
.export sld_fh3
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
         sta sid,x
         lda freqhi,y
         adc g_addh,x
         jmp direct
laxity   lda freqlo,y
         clc
         adc v_modl,x      ;slide
         sta sid,x
         lda freqhi,y
         adc v_modh,x
direct   sta sid+1,x
         lda w_form,x
         and gt_msk,x
#ifdef editor              ;channel off; modif by H.L.
         and e_trx,x      ;trkon/off
#endif
         sta sid+4,x

chkflt   cpx #$00          ;filter fx
         bne sndend
f_test   ldy f_pntr
         beq f_wsid
         lda f_cntr
         beq f_nrep
         dec f_cntr        ;repeat
         dey
         jmp f_ncmd+6
flt_rp1  =*+1
.export flt_rp1
f_nrep   lda flt_rp,y
         cmp #$fe
         bcc f_ncmd
         beq f_nset
flt_fh1  =*+1
.export flt_fh1
         lda flt_fh,y      ;jump
         sta f_pntr
         tay
flt_rp2  =*+1
.export flt_rp2
         lda flt_rp,y
         cmp #$fe
         bcc f_ncmd
flt_fh2  =*+1
.export flt_fh2
f_nset   lda flt_fh,y      ;set type
         sta f_type
         inc f_pntr
         iny
flt_rp3  =*+1
.export flt_rp3
         lda flt_rp,y
f_ncmd   sta f_cntr        ;normal
         inc f_pntr
         lda f_lres
         clc
flt_rl1  =*+1
.export flt_rl1
         adc flt_rl,y
         tax
         and #$f7
         sta f_lres
         sta sid+$15         ;freq lo
         txa
         and #$08
         cmp #$08          ;carry!
         lda f_freq
flt_fh3  =*+1
.export flt_fh3
         adc flt_fh,y
         sta f_freq
         sta sid+$16         ;freq hi

f_wsid   lda f_lres        ;resonance
         and #$f0
         ora flt_on        ;filter on
         ora flt_on+$07
         ora flt_on+$0e
         sta sid+$17
         lda f_type        ;pass type
         ora volume
         sta sid+$18
sndend   rts


m_init   cmp #$20          ;initialize
         bcs sndend
         tay
tr1adl1  =*+1
.export tr1adl1
         lda tr1adl,y      ;address lo
         sta trk_lo
tr2adl1  =*+1
.export tr2adl1
         lda tr2adl,y
         sta trk_lo+$07
tr3adl1  =*+1
.export tr3adl1
         lda tr3adl,y
         sta trk_lo+$0e
tr1adh1  =*+1
.export tr1adh1
         lda tr1adh,y      ;address hi
         sta trk_hi
tr2adh1  =*+1
.export tr2adh1
         lda tr2adh,y
         sta trk_hi+$07
tr3adh1  =*+1
.export tr3adh1
         lda tr3adh,y
         sta trk_hi+$0e
#ifndef packer
         lda start1,y      ;startpos.
         sta trkpos
         lda start2,y
         sta trkpos+$07
         lda start3,y
         sta trkpos+$0e
#endif
         lda #0
         ldx #$18
clrsid   sta sid,x
         dex
         bpl clrsid

ctinit   lda #$0f          ;variables
         sta volume
         ldy #$02
setvar   ldx offset,y
         lda #$03
         sta gt_dec,x
         sta dur_dc,x
         sta dur_rs,x
         lda #$c0
         sta finish,x
         lda #$00
#ifdef packer
         sta trkpos,x      ;Modif H.L.
#endif
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
         rts

pend

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

dstart                          ;start of music data (used by packer)

         *= ((*+$ff)&$ff00)

speeds   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00

start1   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00

start2   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00

start3   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00

tr1adl   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00

tr2adl   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00

tr3adl   .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00
         .byte $00,$00,$00,$00

tr1adh   .byte HI(tracks)+$00,HI(tracks)+$01,HI(tracks)+$02,HI(tracks)+$03
         .byte HI(tracks)+$04,HI(tracks)+$05,HI(tracks)+$06,HI(tracks)+$07
         .byte HI(tracks)+$00,HI(tracks)+$01,HI(tracks)+$02,HI(tracks)+$03
         .byte HI(tracks)+$04,HI(tracks)+$05,HI(tracks)+$06,HI(tracks)+$07
         .byte HI(tracks)+$00,HI(tracks)+$01,HI(tracks)+$02,HI(tracks)+$03
         .byte HI(tracks)+$04,HI(tracks)+$05,HI(tracks)+$06,HI(tracks)+$07
         .byte HI(tracks)+$00,HI(tracks)+$01,HI(tracks)+$02,HI(tracks)+$03
         .byte HI(tracks)+$04,HI(tracks)+$05,HI(tracks)+$06,HI(tracks)+$07

tr2adh   .byte HI(tracks)+$08,HI(tracks)+$09,HI(tracks)+$0a,HI(tracks)+$0b
         .byte HI(tracks)+$0c,HI(tracks)+$0d,HI(tracks)+$0e,HI(tracks)+$0f
         .byte HI(tracks)+$08,HI(tracks)+$09,HI(tracks)+$0a,HI(tracks)+$0b
         .byte HI(tracks)+$0c,HI(tracks)+$0d,HI(tracks)+$0e,HI(tracks)+$0f
         .byte HI(tracks)+$08,HI(tracks)+$09,HI(tracks)+$0a,HI(tracks)+$0b
         .byte HI(tracks)+$0c,HI(tracks)+$0d,HI(tracks)+$0e,HI(tracks)+$0f
         .byte HI(tracks)+$08,HI(tracks)+$09,HI(tracks)+$0a,HI(tracks)+$0b
         .byte HI(tracks)+$0c,HI(tracks)+$0d,HI(tracks)+$0e,HI(tracks)+$0f

tr3adh   .byte HI(tracks)+$10,HI(tracks)+$11,HI(tracks)+$12,HI(tracks)+$13
         .byte HI(tracks)+$14,HI(tracks)+$15,HI(tracks)+$16,HI(tracks)+$17
         .byte HI(tracks)+$10,HI(tracks)+$11,HI(tracks)+$12,HI(tracks)+$13
         .byte HI(tracks)+$14,HI(tracks)+$15,HI(tracks)+$16,HI(tracks)+$17
         .byte HI(tracks)+$10,HI(tracks)+$11,HI(tracks)+$12,HI(tracks)+$13
         .byte HI(tracks)+$14,HI(tracks)+$15,HI(tracks)+$16,HI(tracks)+$17
         .byte HI(tracks)+$10,HI(tracks)+$11,HI(tracks)+$12,HI(tracks)+$13
         .byte HI(tracks)+$14,HI(tracks)+$15,HI(tracks)+$16,HI(tracks)+$17

         *= ((*+$ff)&$ff00)

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

sctadh   .byte HI(sectors)+$00,HI(sectors)+$01,HI(sectors)+$02
         .byte HI(sectors)+$03,HI(sectors)+$04,HI(sectors)+$05
         .byte HI(sectors)+$06,HI(sectors)+$07,HI(sectors)+$08
         .byte HI(sectors)+$09,HI(sectors)+$0a,HI(sectors)+$0b
         .byte HI(sectors)+$0c,HI(sectors)+$0d,HI(sectors)+$0e
         .byte HI(sectors)+$0f,HI(sectors)+$10,HI(sectors)+$11
         .byte HI(sectors)+$12,HI(sectors)+$13,HI(sectors)+$14
         .byte HI(sectors)+$15,HI(sectors)+$16,HI(sectors)+$17

         .byte HI(sectors)+$18,HI(sectors)+$19,HI(sectors)+$1a
         .byte HI(sectors)+$1b,HI(sectors)+$1c,HI(sectors)+$1d
         .byte HI(sectors)+$1e,HI(sectors)+$1f,HI(sectors)+$20
         .byte HI(sectors)+$21,HI(sectors)+$22,HI(sectors)+$23
         .byte HI(sectors)+$24,HI(sectors)+$25,HI(sectors)+$26
         .byte HI(sectors)+$27,HI(sectors)+$28,HI(sectors)+$29
         .byte HI(sectors)+$2a,HI(sectors)+$2b,HI(sectors)+$2c
         .byte HI(sectors)+$2d,HI(sectors)+$2e,HI(sectors)+$2f

         .byte HI(sectors)+$30,HI(sectors)+$31,HI(sectors)+$32
         .byte HI(sectors)+$33,HI(sectors)+$34,HI(sectors)+$35
         .byte HI(sectors)+$36,HI(sectors)+$37,HI(sectors)+$38
         .byte HI(sectors)+$39,HI(sectors)+$3a,HI(sectors)+$3b
         .byte HI(sectors)+$3c,HI(sectors)+$3d,HI(sectors)+$3e
         .byte HI(sectors)+$3f,HI(sectors)+$40,HI(sectors)+$41
         .byte HI(sectors)+$42,HI(sectors)+$43,HI(sectors)+$44
         .byte HI(sectors)+$45,HI(sectors)+$46,HI(sectors)+$47

         .byte HI(sectors)+$48,HI(sectors)+$49,HI(sectors)+$4a
         .byte HI(sectors)+$4b,HI(sectors)+$4c,HI(sectors)+$4d
         .byte HI(sectors)+$4e,HI(sectors)+$4f,HI(sectors)+$50
         .byte HI(sectors)+$51,HI(sectors)+$52,HI(sectors)+$53
         .byte HI(sectors)+$54,HI(sectors)+$55,HI(sectors)+$56
         .byte HI(sectors)+$57,HI(sectors)+$58,HI(sectors)+$59
         .byte HI(sectors)+$5a,HI(sectors)+$5b,HI(sectors)+$5c
         .byte HI(sectors)+$5d,HI(sectors)+$5e,HI(sectors)+$5f

gld_al   .byte $00,$20,$40,$60,$80,$a0
         .byte $c0,$e0,$00,$20,$40,$60
         .byte $80,$a0,$c0,$e0
gld_ah   .byte $00,$00,$00,$00,$00,$00
         .byte $00,$00,$01,$01,$01,$01
         .byte $01,$01,$01,$01

snd_ad   .block $40
snd_sr   .block $40
snd_gt   .block $40
snd_wt   .block $40
snd_ft   .block $40
snd_pt   .block $40
snd_st   .block $40

         *= ((*+$ff)&$ff00)

wve_wf   .byte $08,$fe,$ff
         .block ($0100-3)
wve_st   .byte 0,0,0
         .block ($0100-3)

flt_rp   .block $0100
flt_fh   .block $0100
flt_rl   .block $0100

pls_rp   .block $0100
pls_ph   .block $0100
pls_pl   .block $0100

sld_rp   .block $0100
sld_fh   .block $0100
sld_fl   .block $0100

#ifndef tracks
#define tracks pstart+$1800
#endif
#ifndef sectors
#define sectors pstart+$3000
#endif


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

