;-  SIDwinder editor
;   V01.23
;
;   An ultimate piece of SID music editors for C64 and Plus/4 + SID-card
;
;
;   (C) 1994-1999   Bal zs Tak cs        ( Takinb@sch.bme.hu )
;
;   (C) 1999-2000   Levente H rsfalvi    ( Levente@terrasoft.hu )
;
;   Released on 2000.03.15
;
;   This editor was developed by Taki / Natural Beat. He also composed a
;   lot of songs in (several versions of) his editor + player. In 1999, he
;   decided to officially release the 01.2x series to the public with the
;   SIDwinder V01.22 software package.
;
;   In the autumn of 1999, the (meanwhile lost) sources of the editor were
;   reanimated from the sources of a previous (V01.20) version and the
;   reverse engineered code of the V01.22 editor.
;
;   V01.23 is just a slightly refined version of the V01.22 editor.
;
;   - The editor now compiles to and runs on Plus/4 (with SID card at $fd40)
;   - The memory map was re-arranged (screen masks under $d000, track tables
;     at $e000 etc.) in order to make more memory for the editor code.
;   - The memory mapping code was heavily modified (now the code runs with
;     all ROMs switched off.
;   - The irq routine was re-coded (partly because of the facts above).
;   - Eliminated support for memory image load/save.
;   - Track on/off no longer uses space in the arpeggio table (was
;     implemented with SID key-bit masking instead)
;   - New code for SFX/liveplay mode
;   - SFX mode no longer uses sector $5f
;   - New code for sector play mode
;   - Up to 16x player speed (supported by the editor)
;   - When playing, the sound parameters are traced even in 16x speed mode.
;   - Rewritten raster-irq positioning and rastertime calculation routines.
;   - Ins at position 0 of the track tables bug fixed
;   - Some other small bugfixes and modifications
;   - First version officially released under GPL
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
;   Compiling needs:
;
;   - Table Driven Assembler 3.0.1 or later (ASM)
;   - ComLink V0.98 or later (linking)
;
;   - player.asm           SIDwinder player source file
;   - chars.bin            Character set
;   - masks.bin            Screen masks
;   - sectors.bin          Sector data initialization (binary image)
;   - tracks.bin           Track data initialization (binary image)
;
;   The source can be compiled to run both on C-64 and Plus/4.
;   (Just define c64 or p4 with the TASM -d option in the command line)
;
;   Link with -thx option
;


#define editor
#define LO(x) (x&$ff)
#define HI(x) (x>>8)

#ifndef p4
#define c64
#endif

;-------------- Definitions for C64 -----------


#ifdef c64
#define st01 lda x01 \ sta $34
#define ist01 lda x01 \ sta $38
#define set37 lda #$37 \ sta x01
#define set35 lda #$35 \ sta x01
#define set34 lda #$34 \ sta x01
#define rst01 lda $34 \ sta x01
#define irst01 lda $38 \ sta x01


;Static includes...

i_chars  = $0800
         .export i_chars   ;Load the characterset, please...

i_masks  = $d000
         .export i_masks   ;Screen masks

i_tracks = $e000
         .export i_tracks  ;Default track tables

i_sectors = $7000
         .export i_sectors ;Default sector data


         *= $07fe
         .word $0800       ;Old trick; let's generate a load address...
         *=$0c00

#define tracks $e000
#define sectors $7000

#define screen $0400
#define cia1 $dc00
#define vic $d000
#define sid $d400
#define color $d800
#define masks $d000
#define sctbuf $5700

#define irqc $01
#define colr $0f
#define bord $04           ;purple, like good old S¢sperec ;-)
#define hilite $01
#define elso_r $35


sector_l   =$6000
tracks_l   =$1800

zp1      = $2b             ;1st col
zp2      = $2c
zp3      = $2d             ;2nd col
zp4      = $2e
zp5      = $2f             ;3rd col
zp6      = $30
zp7      = $31             ;sct.len
zp8      = $32
zp9      = $33             ;corner pos
;$34 occ. by st01
call_ct  = $35             ;Player call counter
;$38 occ. by ist01

x01        =$01
xC6        =$C6
xCB        =$CB
xD3        =$D3
xFD        =$FD
xFE        =$FE
x0277      =$0277
x0286      =$0286
x0289      =$0289
x028A      =$028A
x028D      =$028D
x0291      =$0291


xD011      =vic+$11
xD012      =vic+$12
xD018      =vic+$18
xD019      =vic+$19
xD01A      =vic+$1A
xD020      =vic+$20
xD021      =vic+$21

xDC00      =cia1
xDC01      =cia1+1
xDC0D      =cia1+$0D
tmr0       =cia1+$04

iBDCD      =$BDCD
iE544      =$E544
iEA87      =$ea87
#endif

;-------------- Definitions for Plus/4 ---------

#ifdef p4
#define st01 lda $ff13 \ and #$01 \ sta $de
#define ist01 lda $ff13 \ and #$01 \ sta $df
#define set37 sta $ff3e
#define set35 sta $ff3f
#define set34 sta $ff3f
#define rst01 lda $de \ beq *+7 \ sta $ff3e \ bne *+5 \ sta $ff3f
#define irst01 lda $df \ beq *+7 \ sta $ff3e \ bne *+5 \ sta $ff3f

#define tracks $e000
#define sectors $7000

;Static includes...

i_chars  = $f800
         .export i_chars   ;Load the characterset, please...

i_masks  = $d000
         .export i_masks   ;Screen masks

i_tracks = $e000
         .export i_tracks  ;Default track tables

i_sectors = $7000
         .export i_sectors ;Default sector data


;         *= $1010
         *= $100E
         .word $1010

#define screen $0c00
#define sid $fd40
#define color $0800
#define masks $d000
#define sctbuf $5700

#define irqc $02
#define colr $51
#define bord $24
#define hilite $71
#define elso_r $06

sector_l   =$6000
tracks_l   =$1800

zp1      = $d0             ;1st col
zp2      = $d1
zp3      = $d2             ;2nd col
zp4      = $d3
zp5      = $d4             ;3rd col
zp6      = $d5
zp7      = $d6             ;sct.len
zp8      = $d7
zp9      = $d8             ;corner pos
call_ct  = $db             ;Player call counter


xC6        =$ef
xCB        =$C6
xD3        =$ca
xFD        =$d9
xFE        =$da
x0277      =$0527
x0286      =$053b
x0289      =$053f
x028A      =$0540
x0543      =$0543
x028D      =$x0543
x0291      =$0547

tmr0       =$ff00
xD011      =$ff06
xD012      =$ff0b
xFF12      =$ff12
xFF13      =$ff13
xD019      =$ff09
xD01A      =$ff0a
xD020      =$ff19
xD021      =$ff15
xFF08      =$ff08
xFF0A      =$ff0a
xFF1C      =$ff1c
xFF1D      =$ff1d
xFD30      =$fd30

iBDCD      =$a45f
iE544      =$d888
iEA87      =$db11

#endif


;-------------- System independent definitions  ---
st         =$90
pt         =$fb
x0314      =$0314
x0315      =$0315
x0318      =$0318
x0319      =$0319

x0400      =screen
x0429      =screen+$29
x042F      =screen+$2f
x0430      =screen+$30
x0439      =screen+$39
x043C      =screen+$3C
x0442      =screen+$42
x044C      =screen+$4c
x0479      =screen+$79
x047E      =screen+$7E
x047F      =screen+$7F
x0480      =screen+$80
x0482      =screen+$82
x048B      =screen+$8b
x0495      =screen+$95
x0496      =screen+$96
x0497      =screen+$97
x0498      =screen+$98
x0499      =screen+$99
x049A      =screen+$9A
x0500      =screen+$100
x0542      =screen+$0142
x054D      =screen+$014d
x055B      =screen+$015b
x05BE      =screen+$01be
x0600      =screen+$0200
x0629      =screen+$0229
x069E      =screen+$029e
x06D2      =screen+$02d2
x06DD      =screen+$02dd
x06EB      =screen+$02eb
x06F1      =screen+$02f1
x0700      =screen+$0300
x0719      =screen+$0319
x071A      =screen+$031A
x071C      =screen+$031C
x071D      =screen+$031D
x07A5      =screen+$03A5
x07B7      =screen+$03B7

xD878      =color+$78
xD87C      =color+$7C
xD87D      =color+$7D
xD87E      =color+$7E
xD87F      =color+$7F
xD880      =color+$80
xD882      =color+$82
xD883      =color+$83
xD885      =color+$85
xD886      =color+$86
xD887      =color+$87
xD888      =color+$88
xD889      =color+$89
xD88E      =color+$8E
xD88F      =color+$8F
xD890      =color+$90
xD891      =color+$91
xD892      =color+$92
xD898      =color+$98
xD899      =color+$99
xD89A      =color+$9A
xD89B      =color+$9B
xD89C      =color+$9C
xD89D      =color+$9D
xD940      =color+$140
xD945      =color+$145
xD946      =color+$146
xD950      =color+$150
xD951      =color+$151
xD95E      =color+$15E
xD95F      =color+$15F
xDA9E      =color+$29E
xDA9F      =color+$29F
xDAD0      =color+$2D0
xDAD5      =color+$2D5
xDAD6      =color+$2D6
xDADD      =color+$2DD
xDADE      =color+$2DE
xDADF      =color+$2DF
xDAE0      =color+$2E0
xDAE1      =color+$2E1
xDAE2      =color+$2E2
xDAE3      =color+$2E3
xDAE4      =color+$2E4
xDAE5      =color+$2E5
xDAEE      =color+$2EE
xDAEF      =color+$2EF
xDB69      =color+$369

iFF81      =$FF81
iFF90      =$FF90
iFFBA      =$FFBA
iFFBD      =$FFBD
iFFC0      =$FFC0
iFFC3      =$FFC3
iFFC6      =$FFC6
iFFC9      =$FFC9
iFFCC      =$FFCC
iFFCF      =$FFCF
iFFD2      =$FFD2
iFFD5      =$FFD5
iFFD8      =$FFD8

xE000      =masks
xE100      =masks+$0100
xE200      =masks+$0200
xE300      =masks+$0300
xE400      =masks+$0400
xE500      =masks+$0500
xE600      =masks+$0600
xE700      =masks+$0700
xFACE      =$FACE

xFFFA      =$fffa
xFFFB      =$fffb
xFFFE      =$fffe
xFFFF      =$ffff


         jmp m_entp

call_1   ist01
         set35
         lda #irqc
         sta xD019
         ldx call_ct
         lda call_pl+1,x
         sta xD012
#ifdef c64
         lda call_ph+1,x
         ora #$1b
         sta xD011
#endif
#ifdef p4
         lda $ff0a
         and #$fe
         ora call_ph+1,x
         sta $ff0a
#endif
         cpx #$00
         bne c1_1
         jsr jp1003
         jmp c1_2
c1_1     jsr jp1006
c1_2
         ldx call_ct
         cpx e_acts
         beq c1_3
         inx
         .byte $2C
c1_3     ldx #0
         stx call_ct
         irst01
         cpx #0
         beq c1_5
         jmp iEA81
c1_5     jmp iEA31

callno   lda #irqc         ;stopped
         sta xD019
         lda #elso_r
         sta xD012
         jmp iEA31

jp1003   LDA e_radd
         sta e_rlast
         ldx #bord
         lda #$0a
jp31     cmp tmr0
         bcc jp31
         stx xD020
#ifdef c64
         LDA xD012
#endif
#ifdef p4
         lda xFF1D
#endif
         STA e_ract
         lda f2sig
         ora f4sig
         beq nof4
         ldx #0
         jsr player
         lda f2sig
         bne nof4+3             ;Sector play mode, don't touch sctpos
         lda #3
         cmp sctpos             ;prevent it to loop...
         bcs nof4+3
         sta sctpos
         bcc nof4+3
nof4     JSR p_play
#ifdef c64
         LDA xD012
#endif
#ifdef p4
         lda xFF1D
#endif
         ldx #0
         stx xD020
         SEC
         SBC e_ract
         STA e_radd

         lda e_rlast
         cmp e_rmax
         bcc notrec
         sta e_rmax
notrec   lda #1
         sta e_strob
         rts

jp1006            ;multi
         ldx #bord
         lda #$0a
jp61     cmp tmr0
         bcc jp61
         stx xD020
#ifdef c64
         LDA xD012
#endif
#ifdef p4
         lda xFF1D
#endif
         sta e_ract
         lda f2sig
         ora f4sig
         beq no2f4
         ldx #0
         jsr sounds
         jmp *+6
no2f4    jsr p_mult

#ifdef c64
         LDX xD012
         lda xD011
         ldx #0
         stx xD020
         asl A
         rol A
         and #$01
         tay
         txa
#endif
#ifdef p4
         lda xFF1D
         ldy $ff1c
         ldx #0
         stx xD020
#endif
         sty anyad                      ;damn it, too few registers...
         ldy call_ct
         ldx call_ph,y
         beq jp_1
anyad    =*+1
         ldy #0
         bne jp_1
         clc
         adc #LO(312)                   ;sum correction in certain cases

jp_1     sec
         sbc e_ract
         clc
         adc e_radd
         sta e_radd
         rts

wr_irq   lda #LO(x06F1)
         sta irqpnt+1
         lda #HI(x06F1)
         sta irqpnt+2
         ldx #$03          ;max.rtime
         lda e_rmax
         jsr irqout
         lda e_rlast
         ldx #$00          ;act.rtime
         jsr irqout

         dec e_clkt        ;time
         bne notsec
         lda #$32          ;50 frames
         sta e_clkt
         lda #LO(x0719)
         sta irqpnt+1
         lda #HI(x0719)
         sta irqpnt+2
         lda e_secs
         sed
         clc
         adc #$01          ;inc secs
         cmp #$60
         beq yesmin
         sta e_secs
         cld
         jmp yessec
yesmin   lda #$00          ;1 min
         sta e_secs
         lda e_mins
         clc
         adc #$01          ;inc mins
         cmp #$60
         bne notmin
         lda #$00          ;1 hour
notmin   sta e_mins
         cld
         ldx #$00
         jsr irqout
         lda e_secs
yessec   ldx #$03
         jsr irqout
notsec   lda #LO(x05BE)
         sta irqpnt+1
         lda #HI(x05BE)
         sta irqpnt+2
         lda trkpos        ;trk
         sec
         sbc #$01
         ldx #$00
         jsr irqout
         lda trkpos+$07
         sec
         sbc #$01
         ldx #$03
         jsr irqout
         lda trkpos+$0e
         sec
         sbc #$01
         ldx #$06
         jsr irqout
         lda dur_rs        ;dur
         clc
         adc #$01
         ldx #$0f
         jsr irqout
         lda dur_rs+$07
         clc
         adc #$01
         ldx #$12
         jsr irqout
         lda dur_rs+$0e
         clc
         adc #$01
         ldx #$15
         jsr irqout
         lda sctpos        ;sct
         ldx #$28
         jsr irqout
         lda sctpos+$07
         ldx #$2b
         jsr irqout
         lda sctpos+$0e
         ldx #$2e
         jsr irqout
         lda dur_dc        ;act
         ldx #$37
         jsr irqout
         lda dur_dc+$07
         ldx #$3a
         jsr irqout
         lda dur_dc+$0e
         ldx #$3d
         jsr irqout
         lda s_nmbr        ;snd
         ldx #$50
         jsr irqout
         lda s_nmbr+$07
         ldx #$53
         jsr irqout
         lda s_nmbr+$0e
         ldx #$56
         jsr irqout
         lda gt_dec        ;off
         ldx #$5f
         jsr irqout
         lda gt_dec+$07
         ldx #$62
         jsr irqout
         lda gt_dec+$0e
         ldx #$65
         jmp irqout

setspd   ldy e_tune
         lda speeds,y
         php
         sei
         sta e_acts
         tax
         clc
         adc #$01
         sta call_ct                    ;use it temporarily
         ldy #0
         sty call_ph
         sty call_ph+1
         lda #elso_r
         sta call_pl
         sta xD012
         iny
         cpy call_ct
         beq s_end
         lda call_add,x
         clc
         adc call_pl-1,y
         sta call_pl,y
         iny
         cpy call_ct
         beq s_end
s_lp     lda call_add+$10,x
         clc
         adc call_pl-1,y
         sta call_pl,y
         pha
         lda call_ph-1,y
         adc #$00
         sta call_ph,y
         pla
         sec
         sbc #LO(312)
         pha
         lda call_ph,y
         sbc #HI(312)
         pla
         bcc s_1
         sta call_pl,y
         lda #0
         sta call_ph,y
s_1      iny
         cpy call_ct
         bne s_lp

s_end    lda #elso_r
         sta call_pl,y
         lda #0
         sta call_ph,y
         sta call_ct
#ifdef c64
s_2      lda call_ph,y
         lsr A
         ror A
         sta call_ph,y
         dey
         bpl s_2
#endif
#ifdef c64
         lda #$1b
         sta xD011
#endif
#ifdef p4
         lda $ff0a
         and #$fe
         sta $ff0a
#endif
         lda #elso_r
         sta xD012
         plp
         rts

getkey   lda #$00
         sta xC6

g1       lda xC6
         bne g2
         lda e_strob
         beq g3
         lda #0
         sta e_strob
         txa
         pha
         tya
         pha
         jsr wr_irq
         pla
         tay
         pla
         tax
g3       lda scnstrob
         beq g1
         lda #0
         sta scnstrob
         txa
         pha
         tya
         pha
         jsr scnkey
         pla
         tay
         pla
         tax
         jmp g1

g2       lda x0277
         cmp #$0d          ;return
         beq accept
         cmp #$11          ;c.down
         beq accept
         cmp #$13          ;home
         beq accept
         cmp #$14          ;delete
         beq accept
         cmp #$1d          ;c.right
         beq accept
         cmp #$91          ;c.up
         beq accept
         cmp #$94          ;insert
         beq accept
         cmp #$9d          ;c.left
         beq accept
         cmp #$c4          ;sh.d
         beq accept
         cmp #$c6          ;sh.f        ;Modif H.L.
         beq accept
         cmp #$c7          ;sh.g
         beq accept
         cmp #$c8          ;sh.h
         beq accept
         cmp #$c9          ;sh.i
         beq accept
         cmp #$ca          ;sh.j
         beq accept
         cmp #$d3          ;sh.s
         beq accept
         cmp #$d6          ;sh.v
         beq accept
         cmp #$db          ;sh.+
         beq accept
         cmp #$dd          ;sh.-
         beq accept
         cmp #$20
         bcc gj
         cmp #$8e
         bcs gj
         cmp #$60
         bcc accept
         cmp #$85
         bcc gj
accept   rts
gj       jmp getkey

irqout   ldy x0429
         cpy #$54
         bne irqpnt+3
         pha               ;hex #
         lsr a
         lsr a
         lsr a
         lsr a
         dex
         jsr irqcnv
         pla
         and #$0f
irqcnv   ora #$30
         inx
         cmp #$3a
         bcc irqpnt

         clc
         adc #$07
irqpnt   sta xFACE,x
         rts

numout   pha               ;hex #
         lsr a
         lsr a
         lsr a
         lsr a
         dex
         jsr numcnv
         pla
         and #$0f
numcnv   ora #$30
         inx
         cmp #$3a
         bcc numpnt
         clc
         adc #$07
numpnt   sta xFACE,x
         rts

fncout   sta fncnum+1      ;function
         lda x0429
         cmp #$54
         beq fncend
         tya
         pha
fncnum   ldy #$00
         lda fncadl,y
         sta fncpnt+1
         lda fncadh,y
         sta fncpnt+2
         ldy #$11
fncpnt   lda xFACE,y
         sta x043C,y
         dey
         bpl fncpnt
         pla
         tay
fncend   rts

colsnd   tya               ;snd.
         pha
         ldy #$27
         lda #colr
collp1   sta xD878,y
         dey
         bpl collp1
         pla
         tay
         rts

colafp   tya               ;arp+flt+pls
         pha
         ldy #$ff
         lda #colr
collp2   sta xD940,y
         dey
         bne collp2
         pla
         tay
         rts

coltrs   tya               ;trk+sct
         pha
         ldy #$ff
         lda #colr
collp3   sta xD878,y
         dey
         bne collp3
         pla
         tay
         rts

colsta   tya               ;trst.
         pha
         ldy #$07
         lda #colr
collp4   sta xDA9E,y
         dey
         bpl collp4
         ldy #$04
collp5   sta xDB69,y
         dey
         bpl collp5
         pla
         tay
         rts

colgld   tya               ;gld+more
         pha
         ldy #$ff
         lda #colr
collp6   sta xDAD0,y
         dey
         bne collp6
         pla
         tay
         rts

sndtab   txa               ;tables
         pha
         tya
         pha
         lda zp9
         pha
         lda #LO(x042F)
         sta numpnt+1
         lda #HI(x042F)
         sta numpnt+2
         ldy e_sndn
         ldx #$00
         tya               ;#
         jsr numout
         lda #LO(x0482)
         sta numpnt+1
         lda #HI(x0482)
         sta numpnt+2
         ldx #$00
         lda snd_ad,y      ;ad
         jsr numout
         ldx #$03
         lda snd_sr,y      ;sr
         jsr numout
         ldx #$06
         lda snd_gt,y      ;gt
         jsr numout
         ldx #$09
         lda snd_wt,y      ;wt
         jsr numout
         ldx #$0c
         lda snd_ft,y      ;ft
         jsr numout
         ldx #$0f
         lda snd_pt,y      ;pt
         jsr numout
         ldx #$12
         lda snd_st,y      ;st
         jsr numout
         lda e_test        ;note
         ldy #$08
notest   dey
         cmp octave,y
         bcc notest
         sbc octave,y      ;c=1
         asl a
         tax
         lda twelve,x
         sta x047E
         lda twelve+1,x
         sta x047F
         iny
         tya
         ora #$30
         sta x0480
         pla
         sta zp9
         pla
         tay
         pla
         tax
         rts

chk_fa   lda zp9
         cmp #$fb
         bcc *+6
         lda #$fa
         sta zp9
         rts

wvetab   jsr chk_fa
         lda #LO(wve_wf)
         clc
         adc zp9
         sta zp1
         lda #HI(wve_wf)
         sta zp2
         lda #LO(wve_st)
         clc
         adc zp9
         sta zp3
         lda #HI(wve_st)
         sta zp4
         lda #$00
         sta zp5
         sta zp6
         lda #LO(x0542)
         sta numpnt+1
         lda #HI(x0542)
         sta numpnt+2
         jmp tblout

flttab   jsr chk_fa
         lda #LO(flt_rp)
         clc
         adc zp9
         sta zp1
         lda #HI(flt_rp)
         sta zp2
         lda #LO(flt_fh)
         clc
         adc zp9
         sta zp3
         lda #HI(flt_fh)
         sta zp4
         lda #LO(flt_rl)
         clc
         adc zp9
         sta zp5
         lda #HI(flt_rl)
         sta zp6
         lda #LO(x054D)
         sta numpnt+1
         lda #HI(x054D)
         sta numpnt+2
         jmp tblout

plstab   jsr chk_fa
         lda #LO(pls_rp)
         clc
         adc zp9
         sta zp1
         lda #HI(pls_rp)
         sta zp2
         lda #LO(pls_ph)
         clc
         adc zp9
         sta zp3
         lda #HI(pls_ph)
         sta zp4
         lda #LO(pls_pl)
         clc
         adc zp9
         sta zp5
         lda #HI(pls_pl)
         sta zp6
         lda #LO(x055B)
         sta numpnt+1
         lda #HI(x055B)
         sta numpnt+2
         jmp tblout

gldtab   lda #LO(gld_ah)
         clc
         adc zp9
         sta zp1
         lda #HI(gld_ah)
         adc #$00
         sta zp2
         lda #LO(gld_al)
         clc
         adc zp9
         sta zp3
         lda #HI(gld_al)
         adc #$00
         sta zp4
         lda #$00
         sta zp5
         sta zp6
         lda #LO(x06D2)
         sta numpnt+1
         lda #HI(x06D2)
         sta numpnt+2
         jmp tblout

sldtab   jsr chk_fa
         lda #LO(sld_rp)
         clc
         adc zp9
         sta zp1
         lda #HI(sld_rp)
         sta zp2
         lda #LO(sld_fh)
         clc
         adc zp9
         sta zp3
         lda #HI(sld_fh)
         sta zp4
         lda #LO(sld_fl)
         clc
         adc zp9
         sta zp5
         lda #HI(sld_fl)
         sta zp6
         lda #LO(x06DD)
         sta numpnt+1
         lda #HI(x06DD)
         sta numpnt+2
         jmp tblout

trstab   LDA zp9
         CMP #$1B
         BCC i119F
         LDA #$1A
         STA zp9

i119F    lda #LO(start1)
         clc
         adc zp9
         sta zp1
         lda #HI(start1)
         adc #$00
         sta zp2
         lda #LO(start2)
         clc
         adc zp9
         sta zp3
         lda #HI(start2)
         adc #$00
         sta zp4
         lda #LO(start3)
         clc
         adc zp9
         sta zp5
         lda #HI(start3)
         adc #$00
         sta zp6
         lda #LO(x06EB)
         sta numpnt+1
         lda #HI(x06EB)
         sta numpnt+2

tblout   txa               ;write
         pha
         tya
         pha
         ldy #$05
loop01   ldx x_line,y
         tya
         clc
         adc zp9
         jsr numout
         inx
         inx
         lda (zp1),y
         jsr numout
         inx
         inx
         lda (zp3),y
         jsr numout
         lda zp6
         beq twocol
         inx
         inx
         lda (zp5),y
         jsr numout
twocol   dey
         bpl loop01
         pla
         tay
         pla
         tax
         rts

sctout   txa               ;sector
         pha
         tya
         pha
         lda #LO(x044C)
         sta numpnt+1
         lda #HI(x044C)
         sta numpnt+2
         lda e_sctn
         ldx #$00
         jsr numout
         ldx e_sctn
         lda sctadl,x
         clc
         adc zp9
         sta zp1
         lda sctadh,x
         adc #$00
         sta zp2
         lda #LO(x0495)
         sta numpnt+1
         lda #HI(x0495)
         sta numpnt+2
         ldy #$05          ;sct.out
loop02   ldx x_line,y
         tya
         pha
         clc
         adc zp9
         jsr numout
         inx
         inx
         lda (zp1),y
         cmp #$c0
         bcc _nossnd
         and #$3f
         pha
         lda #LO(sc_snd)
         ldy #HI(sc_snd)
seclin   sta sndwrt+1
         sty sndwrt+2
         ldy #$00
sndwrt   lda xFACE,y
         sta x0495,x       ;sector
         inx
         iny
         cpy #$04
         bne sndwrt
         pla
         jsr numout
loop03   pla
         tay
         dey
         bpl loop02
         pla
         tay
         pla
         tax
         rts
_nossnd  cmp #$80
         bcc _nosdur
         sbc #$7f
         pha
         lda #LO(sc_dur)
         ldy #HI(sc_dur)
         jmp seclin
_nosdur  cmp #$7f
         bne _nosend
         lda #LO(sc_end)
         ldy #HI(sc_end)
fullin   sta fullwt+1
         sty fullwt+2
         ldy #$00
fullwt   lda xFACE,y
         sta x0495,x
         inx
         iny
         cpy #$06
         bne fullwt
         jmp loop03
_nosend  cmp #$6f
         bne nohold
         lda #LO(sc_hld)
         ldy #HI(sc_hld)
         jmp fullin
nohold   cmp #$5f
         bne _norest
         lda #LO(sc_rst)
         ldy #HI(sc_rst)
         jmp fullin
_norest  cmp #$60
         bcc nosgld
         and #$1f
         clc
         adc #$01
         pha
         lda #LO(sc_gld)
         ldy #HI(sc_gld)
         jmp seclin
nosgld   ldy #$08
         dey
         cmp octave,y
         bcc nosgld+2
         sbc octave,y      ;c=1
         asl a
         pha
         iny
         tya
         ora #$30
         sta x0498,x
         lda #$20
         sta x0495,x
         sta x0499,x
         sta x049A,x
         pla
         tay
         lda twelve,y
         sta x0496,x
         lda twelve+1,y
         sta x0497,x
         jmp loop03

sctlen   txa               ;length
         pha
         tya
         pha
         ldy e_sctn
         lda sctadl,y
         sta zp7
         lda sctadh,y
         sta zp8
         lda #LO(x0629)
         sta numpnt+1
         lda #HI(x0629)
         sta numpnt+2
         ldy #$00
         sty len_lo
         sty len_hi
         sty actdur
         beq sctcmd
skip_2   iny
         beq sctend
skip_1   iny
         beq sctend
sctcmd   lda (zp7),y
         cmp #$60
         bcs nonote
adddur   lda len_lo
         clc
         adc actdur
         sta len_lo
         bcc skip_1
         inc len_hi
         jmp skip_1
nonote   cmp #$6f
         beq adddur
         bcc skip_2
         cmp #$7f
         beq sctend
         BCC skip_1

         cmp #$c0
         bcs skip_1
         sec
         sbc #$7f
         sta actdur
         jmp skip_1
sctend   ldx #$02
         lda len_lo
         jsr numout
         ldx #$00
         lda len_hi
         jsr numout
         pla
         tay
         pla
         tax
         rts

tr1out   txa               ;tracks
         pha
         tya
         pha
         jsr chk_fa
         lda #LO(x0479)
         sta trkwrt+4
         sta numpnt+1
         lda #HI(x0479)
         sta numpnt+2
         ldy e_tune
         lda tr1adl,y
         clc
         adc zp9
         sta zp7
         lda tr1adh,y
         adc #$00
         sta zp8
         jmp trkout

tr2out   txa
         pha
         tya
         pha
         jsr chk_fa
         lda #LO(x0482)
         sta trkwrt+4
         sta numpnt+1
         lda #HI(x0482)
         sta numpnt+2
         ldy e_tune
         lda tr2adl,y
         clc
         adc zp9
         sta zp7
         lda tr2adh,y
         adc #$00
         sta zp8
         jmp trkout

tr3out   txa
         pha
         tya
         pha
         jsr chk_fa
         lda #LO(x048B)
         sta trkwrt+4
         sta numpnt+1
         lda #HI(x048B)
         sta numpnt+2
         ldy e_tune
         lda tr3adl,y
         clc
         adc zp9
         sta zp7
         lda tr3adh,y
         adc #$00
         sta zp8

trkout   ldy #$00
         ldx x_line,y
         tya
         pha
         clc
         adc zp9
         jsr numout
         inx
         inx
         lda (zp7),y
         cmp #$40
         bcs nottup
         pha
         lda #LO(tr_tup)
         ldy #HI(tr_tup)
trklin   sta trkwrt+1
         sty trkwrt+2
         ldy #$00
trkwrt   lda xFACE,y
         sta x0400,x
         inx
         iny
         cpy #$05
         bne trkwrt
         pla
         cmp #$ff
         beq nonumb
         dex
         dex
         jsr numout
nonumb   pla
         tay
         iny
         cpy #$06
         bne trkout+2
         dec zp7           ;top space
         ldy #$00
         lda (zp7),y
         inc zp7
         cmp #$ff
         bne nextra
         lda trkwrt+4
         sta cextra+1
         ldx #$07
         lda #$20
cextra   sta x0400,x
         dex
         bpl cextra
nextra   pla
         tay
         pla
         tax
         rts
nottup   cmp #$80
         bcs nottdn
         and #$3f
         pha
         lda #LO(tr_tdn)
         ldy #HI(tr_tdn)
         jmp trklin
nottdn   cmp #$e0
         bcs notsct
         and #$7f
         pha
         lda #LO(tr_sct)
         ldy #HI(tr_sct)
         jmp trklin
notsct   cmp #$f0
         beq _haltvp
         bcs _notvol
         and #$0f
         pha
         lda #LO(tr_vol)
         ldy #HI(tr_vol)
         jmp trklin
_haltvp  lda #$ff
         pha
         lda #LO(tr_hlt)
         ldy #HI(tr_hlt)
         jmp trklin
_notvol  cmp #$f8
         bcs _notdec
         and #$0f
         pha
         lda #LO(tr_dec)
         ldy #HI(tr_dec)
         jmp trklin
_notdec  cmp #$ff
         bcs _notinc
         sec
         sbc #$f7
         pha
         lda #LO(tr_inc)
         ldy #HI(tr_inc)
         jmp trklin
_notinc  cpy #$05
         beq skpclr
         txa
         pha
         clc
         adc trkwrt+4
         sta afterj+1
         lda trkwrt+5
         adc #$00
         sta afterj+2
         ldx #$25
         lda #$20
afterj   sta xFACE,x
         inx
         cpx #$2d
         bne afterj
         pla
         tax
         pla               ;y=y+1
         clc
         adc #$01
         pha
skpclr   iny
         lda (zp7),y
         pha
         lda #LO(tr_jmp)
         ldy #HI(tr_jmp)
         jmp trklin

f1_key   sei               ;play
         txa
         pha
         tya
         pha
         lda #$00
         sta e_radd
         sta e_ract
         sta e_rmax
         sta e_secs
         sta e_mins
         sta f2sig
         sta f4sig
         lda #$32
         sta e_clkt
         lda x0429
         cmp #$54
         bne *+16          ;_sounds s.
         lda #$30
         sta x0719         ;clock
         sta x071A
         sta x071C
         sta x071D
         jsr setspd
         lda #LO(call_1)
         sta x0314
         lda #HI(call_1)
         sta x0315
         lda #LO(sctadl)
         sta sctadl1
         lda #HI(sctadl)
         sta sctadl1+1
         lda #LO(sctadh)
         sta sctadh1
         lda #HI(sctadh)
         sta sctadh1+1
;         lda #$ff
;         sta e_trx+8
;         sta e_trx+1+$0e
         lda e_tune
         jsr p_init
         pla
         tay
         pla
         tax
         lda #$00
         cli
         rts

f2_key   sei               ;sector
         txa
         pha
         tya
         pha
         lda #$00
         sta trkpos
         sta trkpos+$07
         sta trkpos+$0e
         sta f4sig
         sta e_radd
         sta e_ract
         sta e_rmax
         sta e_secs
         sta e_mins
         lda #$32
         sta e_clkt
         sta f2sig
         lda x0429
         cmp #$54
         bne *+16          ;_sounds s.
         lda #$30
         sta x0719         ;clock
         sta x071A
         sta x071C
         sta x071D
         jsr setspd
         lda #LO(call_1)
         sta x0314
         lda #HI(call_1)
         sta x0315
         lda #LO(sctadl)
         sta sctadl1
         lda #HI(sctadl)
         sta sctadl1+1
         lda #LO(sctadh)
         sta sctadh1
         lda #HI(sctadh)
         sta sctadh1+1
         lda e_sctn
         ora #$80
         sta ttrack+1
         lda #LO(ttrack)      ;mod.init
         sta trk_lo
         lda #HI(ttrack)
         sta trk_hi
         lda #0
         sta sid+$0b
         sta sid+$12
         sta sid+5
         sta sid+6
         jsr ctinit
         pla
         tay
         pla
         tax
         lda #$00
         cli
         rts

f3_key   sei               ;stop
         lda #LO(callno)
         sta x0314
         lda #HI(callno)
         sta x0315
         lda #$80
         sta ttrack+1
         lda #elso_r
         sta xD012
#ifdef c64
         lda #$1b
         sta xD011
#endif
#ifdef p4
         lda #$02
         sta $ff0a
#endif
         lda #$00
         sta sid+$18
         cli
         rts

f4_key   sei               ;sfx
         txa
         pha
         tya
         pha
         lda #$00
         sta trkpos
         sta f2sig
         sta e_radd
         sta e_ract
         sta e_rmax
         sta e_secs
         sta e_mins
         lda #$32
         sta e_clkt
         sta f4sig
         lda x0429
         cmp #$54
         bne *+16          ;sounds screen
         lda #$30
         sta x0719         ;clock
         sta x071A
         sta x071C
         sta x071D
         jsr setspd
         lda #LO(call_1)
         sta x0314
         lda #HI(call_1)
         sta x0315
         jsr ctinit
         lda #0
         sta sid+$0b
         sta sid+$12
         sta sid+5                      ;ADSR regs may be not zero -->
         sta sid+6                      ;hard restart
         lda #LO(d_sctad)
         sta sctadl1
         lda #HI(d_sctad)               ;Trick the player to read the dummy
         sta sctadl1+1                  ;sector address 'table'
         lda #LO((d_sctad+1))
         sta sctadh1
         lda #HI((d_sctad+1))
         sta sctadh1+1
         lda e_sndn        ;snd.#
         ora #$c0
         sta dummy_s
         lda e_test        ;note
         sta dummy_s+2
         lda #LO(ttrack)      ;mod.init
         sta trk_lo
         lda #HI(ttrack)
         sta trk_hi
         lda #irqc
         sta xD019
         pla
         tay
         pla
         tax
         lda #$00
         cli
         rts

spaces   lda x0314         ;sfx on?
         cmp #LO(callno)
         beq spcend
         lda f4sig
         beq spcend
         sei
         txa
         pha
         tya
         pha
         jsr ctinit
         lda #$00
         sta trkpos
         lda e_sndn        ;snd.#
         ora #$c0
         sta dummy_s
         lda e_test        ;note
         sta dummy_s+2
         lda #LO(ttrack)      ;mod.init
         sta trk_lo
         lda #HI(ttrack)
         sta trk_hi
         lda #0
         sta sid+$0b
         sta sid+$12
         sta sid+5                      ;ADSR regs may be not zero -->
         sta sid+6                      ;hard restart
         pla
         tay
         pla
         tax
spcend   lda #$00
         cli
         rts

f5_key   lda x0314
         cmp #LO(callno)
         bne f5_end
         sei
         txa
         pha
         tya
         pha
         jsr setspd
         lda #LO(call_1)
         sta x0314
         lda #HI(call_1)
         sta x0315
         lda f_type
         ora volume
         sta sid+$18
         pla
         tay
         pla
         tax
f5_end   lda #$00
         cli
         rts

f7_key   lda x0314
         cmp #LO(callno)
         beq f5_end
         sei
         txa
         pha
         tya
         pha
f7_fwd   ldx #$00
         dex
         bne *-1
         dex
         bne *-1
         jsr fast_f
         lda #$fe
#ifdef c64
         sta xDC00
         lda xDC01
#endif
#ifdef p4
         sta xFD30
         sta xFF08
         lda xFF08
#endif
         and #$08
         beq f7_fwd
#ifdef c64
         bit xD011
         bpl *-3
         bit xD011
         bmi *-3
#endif
#ifdef p4
         lda #$01
         bit xFF1C
         beq *-3
         bit xFF1C
         bne *-3
#endif
         lda #irqc
         sta xD019
         pla
         tay
         pla
         tax
         lda #$00
         cli
         rts

fast_f   dec e_clkt        ;time
         bne fast_e
         lda #$32          ;50 frames
         sta e_clkt
         lda #LO(x0719)
         sta irqpnt+1
         lda #HI(x0719)
         sta irqpnt+2
         lda e_secs
         sed
         clc
         adc #$01          ;inc secs
         cmp #$60
         beq fast_m
         sta e_secs
         cld
         jmp fast_s
fast_m   lda #$00          ;1 min
         sta e_secs
         lda e_mins
         clc
         adc #$01          ;inc mins
         cmp #$60
         bne fast_n
         lda #$00          ;1 hour
fast_n   sta e_mins
         cld
         ldx #$00
         jsr irqout
         lda e_secs
fast_s   ldx #$03
         jsr irqout
fast_e   jmp p_play

f6_key   dec e_tune
         jmp *+6
f8_key   inc e_tune
         txa
         pha
         lda zp9
         pha
         lda e_tune
         and #$1f
         sta e_tune
         tax
         jsr startw
         lda start1,x
         sta e_tr1p
         sta zp9
         jsr tr1out
         lda start2,x
         sta e_tr2p
         sta zp9
         jsr tr2out
         lda start3,x
         sta e_tr3p
         sta zp9
         jsr tr3out
         pla
         sta zp9
         pla
         tax
         lda #$01
         rts

onoff1   lda e_trx         ;trk1 on
         eor #$ff          ;toggle
         sta e_trx
         txa               ;lot of modif by H.L. in order to make the chn-off
         pha               ;function arpeggio free...
         lda x0429
         cmp #$54
         bne on_e
         ldx e_trx
         bne *+5
         lda #$18
         .byte $2c
         lda #$7a
         sta x0430
on_e     pla
         tax
         lda #$00
         rts
onoff2   lda e_trx+7
         eor #$ff
         sta e_trx+7
         txa
         pha
         lda x0429
         cmp #$54
         bne on_e
         ldx e_trx+7
         bne *+5
         lda #$18
         .byte $2c
         lda #$7a
         sta x0439
         bne on_e

onoff3   lda e_trx+$0e
         eor #$ff
         sta e_trx+$0e
         txa
         pha
         lda x0429
         cmp #$54
         bne on_e
         ldx e_trx+$0e
         bne *+5
         lda #$18
         .byte $2c
         lda #$7a
         sta x0442
         bne on_e

_sounds  jsr sndtab        ;screen
         ldy e_sndn
         lda snd_wt,y
         sta zp9
         jsr wvetab
         lda snd_ft,y
         sta zp9
         jsr flttab
         lda snd_pt,y
         sta zp9
         jsr plstab
         lda e_gldp
         sta zp9
         jsr gldtab
         lda snd_st,y
         sta zp9
         jsr sldtab
         lda e_tune
         sta zp9
         jmp trstab

startw   txa               ;corner
         pha
         lda #LO(x069E)
         sta numpnt+1
         lda #HI(x069E)
         sta numpnt+2
         ldx e_tune
         lda start1,x      ;trst
         ldx #$00
         jsr numout
         ldx e_tune
         lda start2,x
         ldx #$03
         jsr numout
         ldx e_tune
         lda start3,x
         ldx #$06
         jsr numout
         lda e_rmax
         ldx #$56
         jsr numout
         lda e_mins        ;time
         ldx #$7b
         jsr numout
         lda e_secs
         ldx #$7e
         jsr numout
         lda e_tune        ;tune#
         ldx #$cb
         jsr numout
         ldx e_tune
         lda speeds,x
         ldx #$ce
         jsr numout
         pla
         tax
         rts

keychk   cmp #$2c          ;trk.sw.
         bne *+5
         jmp onoff1
         cmp #$2e
         bne *+5
         jmp onoff2
         cmp #$2f
         bne *+5
         jmp onoff3
         cmp #$85          ;f-keys
         bne *+5
         jmp f1_key
         cmp #$86
         bne *+5
         jmp f3_key
         cmp #$87
         bne *+5
         jmp f5_key
         cmp #$88
         bne *+5
         jmp f7_key
         cmp #$89
         bne *+5
         jmp f2_key
         cmp #$8a
         bne *+5
         jmp f4_key
         cmp #$8b
         bne *+12
         lda x0429
         cmp #$53
         beq keyfnd
         jmp f6_key
         cmp #$8c
         bne *+14
         lda x0429
         cmp #$53
         beq keyfnd
         jmp f8_key
keyfnd   lda #$00
         rts

w_edit   ldy e_sndn        ;wvetab
         lda snd_wt,y
         sta zp9
         ldy #$00
         ldx #$00
w_edi2   lda #zp1
         sta w_zpge+1
         sta w_zpgf+1
         lda e_msg1
         jsr fncout
w_loop   jsr colafp
         lda #hilite
         sta xD945,x
         sta xD946,x
         jsr wvetab
w_newc   jsr getkey        ;new char
         cmp #$0d
         bne w_down
         cpy #$05
         bne w_rint
         ldx x_line,y
         lda zp9
         cmp #$fa
         beq w_edi2
         inc zp9
         jmp w_edi2
w_rint   iny
         ldx x_line,y
         jmp w_edi2
w_down   cmp #$11
         bne w_home
         cpy #$05
         bne w_dint
         lda zp9           ;scroll
         cmp #$fa
         beq w_newc
         inc zp9
         jmp w_loop
w_dint   iny               ;down
         txa
         clc
         adc #$28
         tax
         jmp w_loop
w_home   cmp #$13
         bne w_delc
         ldy #$00
         sty zp9
         jmp w_edi2-2
w_delc   cmp #$14          ;delete
         bne w_rght
         sei
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$ff
         beq w_dele
         ldx #$3f          ;mod.pntr
w_dcmp   cmp snd_wt,x
         bcs w_dlow
         dec snd_wt,x
w_dlow   dex
         bpl w_dcmp
         sta e_orad
         ldx #$00
w_djst   lda wve_wf,x
         cmp #$ff
         bne w_djnx
         lda e_orad
         cmp wve_st,x
         bcs w_djnx
         dec wve_st,x
w_djnx   inx
         bne w_djst
         jsr sndtab
         lda #$ff
         sec
         sbc zp9
         sta w_dcpy+1
w_delp   iny
         lda (zp1),y
         dey
         sta (zp1),y
         iny
         lda (zp3),y
         dey
         sta (zp3),y
         iny
w_dcpy   cpy #$00
         bne w_delp
w_dele   lda #$00
         sta (zp1),y
         sta (zp3),y
         lda #irqc
         sta xD019
         pla
         tay
         pla
         tax
         cli
         jmp w_loop
w_rght   cmp #$1d
         bne w_uppp
         lda w_zpge+1
         cmp #zp3
         bne *+5
         jmp w_newc
         inc w_zpge+1
         inc w_zpge+1
         inc w_zpgf+1
         inc w_zpgf+1
         inx
         inx
         inx
         stx e_orad
         lda w_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp w_loop
w_uppp   cmp #$91
         bne w_inst
         cpy #$00
         bne w_uint
         lda zp9           ;scroll
         bne *+5
         jmp w_newc
         dec zp9
         jmp w_loop
w_uint   dey               ;down
         txa
         sec
         sbc #$28
         tax
         jmp w_loop
w_inst   cmp #$94
         bne w_left
         sei
         txa
         pha
         sty w_icpy+1
         tya
         clc
         adc zp9
         cmp #$ff
         beq w_inse
         ldx #$3f
w_icmp   cmp snd_wt,x      ;mod.pntr
         beq w_ilow-3
         bcs w_ilow
         inc snd_wt,x
w_ilow   dex
         bpl w_icmp
         sta e_orad
         ldx #$00
w_ijst   lda wve_wf,x
         cmp #$ff
         bne w_ijnx
         lda e_orad
         cmp wve_st,x
         beq w_ijnx-3
         bcs w_ijnx
         inc wve_st,x
w_ijnx   inx
         bne w_ijst
         jsr sndtab
         lda #$ff
         sec
         sbc zp9
         tay
w_islp   dey
         lda (zp1),y
         iny
         sta (zp1),y
         dey
         lda (zp3),y
         iny
         sta (zp3),y
         dey
w_icpy   cpy #$00
         bne w_islp
w_inse   lda #$00
         sta (zp1),y
         sta (zp3),y
         lda #irqc
         sta xD019
         pla
         tax
         cli
         jmp w_loop
w_left   cmp #$9d
         bne w_inot
         lda w_zpge+1
         cmp #zp1
         bne *+5
         jmp w_newc
         dec w_zpge+1
         dec w_zpge+1
         dec w_zpgf+1
         dec w_zpgf+1
         dex
         dex
         dex
         stx e_orad
         lda w_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp w_loop
w_inot   cmp #$db          ;sh.+
         bne w_dnot
         lda e_test
         cmp #$5e
         beq *+8
         inc e_test
         jsr sndtab
         jmp w_newc
w_dnot   cmp #$dd
         bne w_spax
         lda e_test
         beq *+8
         dec e_test
         jsr sndtab
         jmp w_newc
w_spax   cmp #$20          ;test
         bne w_gsnd
         jsr spaces
         jmp w_newc
w_gsnd   cmp #$28          ;exit
         bcs w_isnd
         and #$07
         tay
         jmp colafp
w_isnd   cmp #$2d          ;snd.#
         beq w_dsnd
         cmp #$2b
         bne w_scrn
         inc e_sndn
         jmp *+6
w_dsnd   dec e_sndn
         lda e_sndn
         and #$3f
         sta e_sndn
         jsr _sounds
         jmp w_edit
w_scrn   cmp #$5f          ;to editor
         bne w_tr1x
         ldy #$00
         jmp colafp
w_tr1x   jsr keychk
         bne w_sret
         jmp w_newc
w_sret   cmp #$8d
         bne w_numb
         ldy #$01
         jmp colafp
w_numb   cmp #$30
         bcc w_back
         cmp #$3a
         bcc w_back+3
         cmp #$41
         bcc w_back
         cmp #$47
         bcc w_back+3
w_back   jmp w_newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
w_zpge   lda (zp1),y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
w_zpgf   sta (zp1),y
         jmp w_newc-3

f_edit   ldy e_sndn        ;flttab
         lda snd_ft,y
         sta zp9
         ldy #$00
         ldx #$00
f_edi2   lda #zp1
         sta f_zpge+1
         sta f_zpgf+1
         lda e_msg1
         jsr fncout
f_loop   jsr colafp
         lda #hilite
         sta xD950,x
         sta xD951,x
         jsr flttab
f_newc   jsr getkey        ;new char
         cmp #$0d
         bne f_down
         cpy #$05
         bne f_rint
         ldx x_line,y
         lda zp9
         cmp #$fa
         beq f_edi2
         inc zp9
         jmp f_edi2
f_rint   iny
         ldx x_line,y
         jmp f_edi2
f_down   cmp #$11
         bne f_home
         cpy #$05
         bne f_dint
         lda zp9           ;scroll
         cmp #$fa
         beq f_newc
         inc zp9
         jmp f_loop
f_dint   iny               ;down
         txa
         clc
         adc #$28
         tax
         jmp f_loop
f_home   cmp #$13
         bne f_delc
         ldy #$00
         sty zp9
         jmp f_edi2-2
f_delc   cmp #$14          ;delete
         bne f_rght
         sei
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$ff
         beq f_dele
         ldx #$3f          ;mod.pntr
f_dcmp   cmp snd_ft,x
         bcs f_dlow
         dec snd_ft,x
f_dlow   dex
         bpl f_dcmp
         sta e_orad
         ldx #$00
f_djst   lda flt_rp,x
         cmp #$ff
         bne f_djnx
         lda e_orad
         cmp flt_fh,x
         bcs f_djnx
         dec flt_fh,x
f_djnx   inx
         bne f_djst
         jsr sndtab
         lda #$ff
         sec
         sbc zp9
         sta f_dcpy+1
f_delp   iny
         lda (zp1),y
         dey
         sta (zp1),y
         iny
         lda (zp3),y
         dey
         sta (zp3),y
         iny
         lda (zp5),y
         dey
         sta (zp5),y
         iny
f_dcpy   cpy #$00
         bne f_delp
f_dele   lda #$00
         sta (zp1),y
         sta (zp3),y
         sta (zp5),y
         lda #irqc
         sta xD019
         pla
         tay
         pla
         tax
         cli
         jmp f_loop
f_rght   cmp #$1d
         bne f_uppp
         lda f_zpge+1
         cmp #zp5
         bne *+5
         jmp f_newc
         inc f_zpge+1
         inc f_zpge+1
         inc f_zpgf+1
         inc f_zpgf+1
         inx
         inx
         inx
         stx e_orad
         lda f_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp f_loop
f_uppp   cmp #$91
         bne f_inst
         cpy #$00
         bne f_uint
         lda zp9           ;scroll
         bne *+5
         jmp f_newc
         dec zp9
         jmp f_loop
f_uint   dey               ;down
         txa
         sec
         sbc #$28
         tax
         jmp f_loop
f_inst   cmp #$94
         bne f_left
         sei
         txa
         pha
         sty f_icpy+1
         tya
         clc
         adc zp9
         cmp #$ff
         beq f_inse
         ldx #$3f
f_icmp   cmp snd_ft,x      ;mod.pntr
         beq f_ilow-3
         bcs f_ilow
         inc snd_ft,x
f_ilow   dex
         bpl f_icmp
         sta e_orad
         ldx #$00
f_ijst   lda flt_rp,x
         cmp #$ff
         bne f_ijnx
         lda e_orad
         cmp flt_fh,x
         beq f_ijnx-3
         bcs f_ijnx
         inc flt_fh,x
f_ijnx   inx
         bne f_ijst
         jsr sndtab
         lda #$ff
         sec
         sbc zp9
         tay
f_islp   dey
         lda (zp1),y
         iny
         sta (zp1),y
         dey
         lda (zp3),y
         iny
         sta (zp3),y
         dey
         lda (zp5),y
         iny
         sta (zp5),y
         dey
f_icpy   cpy #$00
         bne f_islp
f_inse   lda #$00
         sta (zp1),y
         sta (zp3),y
         sta (zp5),y
         lda #irqc
         sta xD019
         pla
         tax
         cli
         jmp f_loop
f_left   cmp #$9d
         bne f_inot
         lda f_zpge+1
         cmp #zp1
         bne *+5
         jmp f_newc
         dec f_zpge+1
         dec f_zpge+1
         dec f_zpgf+1
         dec f_zpgf+1
         dex
         dex
         dex
         stx e_orad
         lda f_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp f_loop
f_inot   cmp #$db          ;sh.+
         bne f_dnot
         lda e_test
         cmp #$5e
         beq *+8
         inc e_test
         jsr sndtab
         jmp f_newc
f_dnot   cmp #$dd
         bne f_spax
         lda e_test
         beq *+8
         dec e_test
         jsr sndtab
         jmp f_newc
f_spax   cmp #$20          ;test
         bne f_gsnd
         jsr spaces
         jmp f_newc
f_gsnd   cmp #$28          ;exit
         bcs f_isnd
         and #$07
         tay
         jmp colafp
f_isnd   cmp #$2d          ;snd.#
         beq f_dsnd
         cmp #$2b
         bne f_scrn
         inc e_sndn
         jmp *+6
f_dsnd   dec e_sndn
         lda e_sndn
         and #$3f
         sta e_sndn
         jsr _sounds
         jmp f_edit
f_scrn   cmp #$5f          ;to editor
         bne f_tr1x
         ldy #$00
         jmp colafp
f_tr1x   jsr keychk
         bne f_sret
         jmp f_newc
f_sret   cmp #$8d
         bne f_numb
         ldy #$01
         jmp colafp
f_numb   cmp #$30
         bcc f_back
         cmp #$3a
         bcc f_back+3
         cmp #$41
         bcc f_back
         cmp #$47
         bcc f_back+3
f_back   jmp f_newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
f_zpge   lda (zp1),y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
f_zpgf   sta (zp1),y
         jmp f_newc-3

p_edit   ldy e_sndn        ;plstab
         lda snd_pt,y
         sta zp9
         ldy #$00
         ldx #$00
p_edi2   lda #zp1
         sta p_zpge+1
         sta p_zpgf+1
         lda e_msg1
         jsr fncout
p_loop   jsr colafp
         lda #hilite
         sta xD95E,x
         sta xD95F,x
         jsr plstab
p_newc   jsr getkey        ;new char
         cmp #$0d
         bne p_down
         cpy #$05
         bne p_rint
         ldx x_line,y
         lda zp9
         cmp #$fa
         beq p_edi2
         inc zp9
         jmp p_edi2
p_rint   iny
         ldx x_line,y
         jmp p_edi2
p_down   cmp #$11
         bne p_home
         cpy #$05
         bne p_dint
         lda zp9           ;scroll
         cmp #$fa
         beq p_newc
         inc zp9
         jmp p_loop
p_dint   iny               ;down
         txa
         clc
         adc #$28
         tax
         jmp p_loop
p_home   cmp #$13
         bne p_delc
         ldy #$00
         sty zp9
         jmp p_edi2-2
p_delc   cmp #$14          ;delete
         bne p_rght
         sei
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$ff
         beq p_dele
         ldx #$3f          ;mod.pntr
p_dcmp   cmp snd_pt,x
         bcs p_dlow
         dec snd_pt,x
p_dlow   dex
         bpl p_dcmp
         sta e_orad
         ldx #$00
p_djst   lda pls_rp,x
         cmp #$ff
         bne p_djnx
         lda e_orad
         cmp pls_ph,x
         bcs p_djnx
         dec pls_ph,x
p_djnx   inx
         bne p_djst
         jsr sndtab
         lda #$ff
         sec
         sbc zp9
         sta p_dcpy+1
p_delp   iny
         lda (zp1),y
         dey
         sta (zp1),y
         iny
         lda (zp3),y
         dey
         sta (zp3),y
         iny
         lda (zp5),y
         dey
         sta (zp5),y
         iny
p_dcpy   cpy #$00
         bne p_delp
p_dele   lda #$00
         sta (zp1),y
         sta (zp3),y
         sta (zp5),y
         lda #irqc
         sta xD019
         pla
         tay
         pla
         tax
         cli
         jmp p_loop
p_rght   cmp #$1d
         bne p_uppp
         lda p_zpge+1
         cmp #zp5
         bne *+5
         jmp p_newc
         inc p_zpge+1
         inc p_zpge+1
         inc p_zpgf+1
         inc p_zpgf+1
         inx
         inx
         inx
         stx e_orad
         lda p_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp p_loop
p_uppp   cmp #$91
         bne p_inst
         cpy #$00
         bne p_uint
         lda zp9           ;scroll
         bne *+5
         jmp p_newc
         dec zp9
         jmp p_loop
p_uint   dey               ;down
         txa
         sec
         sbc #$28
         tax
         jmp p_loop
p_inst   cmp #$94
         bne p_left
         sei
         txa
         pha
         sty p_icpy+1
         tya
         clc
         adc zp9
         cmp #$ff
         beq p_inse
         ldx #$3f
p_icmp   cmp snd_pt,x      ;mod.pntr
         beq p_ilow-3
         bcs p_ilow
         inc snd_pt,x
p_ilow   dex
         bpl p_icmp
         sta e_orad
         ldx #$00
p_ijst   lda pls_rp,x
         cmp #$ff
         bne p_ijnx
         lda e_orad
         cmp pls_ph,x
         beq p_ijnx-3
         bcs p_ijnx
         inc pls_ph,x
p_ijnx   inx
         bne p_ijst
         jsr sndtab
         lda #$ff
         sec
         sbc zp9
         tay
p_islp   dey
         lda (zp1),y
         iny
         sta (zp1),y
         dey
         lda (zp3),y
         iny
         sta (zp3),y
         dey
         lda (zp5),y
         iny
         sta (zp5),y
         dey
p_icpy   cpy #$00
         bne p_islp
p_inse   lda #$00
         sta (zp1),y
         sta (zp3),y
         sta (zp5),y
         lda #irqc
         sta xD019
         pla
         tax
         cli
         jmp p_loop
p_left   cmp #$9d
         bne p_inot
         lda p_zpge+1
         cmp #zp1
         bne *+5
         jmp p_newc
         dec p_zpge+1
         dec p_zpge+1
         dec p_zpgf+1
         dec p_zpgf+1
         dex
         dex
         dex
         stx e_orad
         lda p_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp p_loop
p_inot   cmp #$db          ;sh.+
         bne p_dnot
         lda e_test
         cmp #$5e
         beq *+8
         inc e_test
         jsr sndtab
         jmp p_newc
p_dnot   cmp #$dd
         bne p_spax
         lda e_test
         beq *+8
         dec e_test
         jsr sndtab
         jmp p_newc
p_spax   cmp #$20          ;test
         bne p_gsnd
         jsr spaces
         jmp p_newc
p_gsnd   cmp #$28          ;exit
         bcs p_isnd
         and #$07
         tay
         jmp colafp
p_isnd   cmp #$2d          ;snd.#
         beq p_dsnd
         cmp #$2b
         bne p_scrn
         inc e_sndn
         jmp *+6
p_dsnd   dec e_sndn
         lda e_sndn
         and #$3f
         sta e_sndn
         jsr _sounds
         jmp p_edit
p_scrn   cmp #$5f          ;to editor
         bne p_tr1x
         ldy #$00
         jmp colafp
p_tr1x   jsr keychk
         bne p_sret
         jmp p_newc
p_sret   cmp #$8d
         bne p_numb
         ldy #$01
         jmp colafp
p_numb   cmp #$30
         bcc p_back
         cmp #$3a
         bcc p_back+3
         cmp #$41
         bcc p_back
         cmp #$47
         bcc p_back+3
p_back   jmp p_newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
p_zpge   lda (zp1),y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
p_zpgf   sta (zp1),y
         jmp p_newc-3

g_edit   lda e_gldp        ;gldtab
         sta zp9
         ldy #$00
         ldx #$00
g_edi2   lda #zp1
         sta g_zpge+1
         sta g_zpgf+1
         lda e_msg1
         jsr fncout
g_loop   jsr colgld
         lda #hilite
         sta xDAD5,x
         sta xDAD6,x
         jsr gldtab
g_newc   jsr getkey        ;new char
         cmp #$0d
         bne _g_down
         cpy #$05
         bne g_rint
         ldx x_line,y
         lda zp9
         cmp #$0a
         beq g_edi2
         inc zp9
         jmp g_edi2
g_rint   iny
         ldx x_line,y
         jmp g_edi2
_g_down  cmp #$11
         bne g_home
         cpy #$05
         bne g_dint
         lda zp9           ;scroll
         cmp #$0a
         beq g_newc
         inc zp9
         jmp g_loop
g_dint   iny               ;down
         txa
         clc
         adc #$28
         tax
         jmp g_loop
g_home   cmp #$13
         bne g_delc
         ldy #$00
         sty zp9
         jmp g_edi2-2
g_delc   cmp #$14          ;delete
         bne g_rght
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$0f
         beq g_dele
         lda #$0f
         sec
         sbc zp9
         sta g_dcpy+1
g_delp   iny
         lda (zp1),y
         dey
         sta (zp1),y
         iny
         lda (zp3),y
         dey
         sta (zp3),y
         iny
g_dcpy   cpy #$00
         bne g_delp
g_dele   lda #$00
         sta (zp1),y
         sta (zp3),y
         pla
         tay
         pla
         tax
         jmp g_loop
g_rght   cmp #$1d
         bne g_uppp
         lda g_zpge+1
         cmp #zp3
         bne *+5
         jmp g_newc
         inc g_zpge+1
         inc g_zpge+1
         inc g_zpgf+1
         inc g_zpgf+1
         inx
         inx
         inx
         stx e_orad
         lda g_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp g_loop
g_uppp   cmp #$91
         bne g_inst
         cpy #$00
         bne g_uint
         lda zp9           ;scroll
         bne *+5
         jmp g_newc
         dec zp9
         jmp g_loop
g_uint   dey               ;down
         txa
         sec
         sbc #$28
         tax
         jmp g_loop
g_inst   cmp #$94
         bne g_left
         txa
         pha
         sty g_icpy+1
         tya
         clc
         adc zp9
         cmp #$0f
         beq g_inse
         lda #$0f
         sec
         sbc zp9
         tay
g_islp   dey
         lda (zp1),y
         iny
         sta (zp1),y
         dey
         lda (zp3),y
         iny
         sta (zp3),y
         dey
g_icpy   cpy #$00
         bne g_islp
g_inse   lda #$00
         sta (zp1),y
         sta (zp3),y
         pla
         tax
         jmp g_loop
g_left   cmp #$9d
         bne g_spax
         lda g_zpge+1
         cmp #zp1
         bne *+5
         jmp g_newc
         dec g_zpge+1
         dec g_zpge+1
         dec g_zpgf+1
         dec g_zpgf+1
         dex
         dex
         dex
         stx e_orad
         lda g_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp g_loop
g_spax   cmp #$20          ;test
         bne g_gsnd
         jsr spaces
         jmp g_newc
g_gsnd   cmp #$28          ;exit
         bcs g_scrn
         and #$07
         tay
         lda zp9
         sta e_gldp
         jmp colgld
g_scrn   cmp #$5f          ;to editor
         bne g_tr1x
         ldy #$00
         lda zp9
         sta e_gldp
         jmp colgld
g_tr1x   jsr keychk
         bne g_numb
         jmp g_newc
g_numb   cmp #$30
         bcc g_back
         cmp #$3a
         bcc g_back+3
         cmp #$41
         bcc g_back
         cmp #$47
         bcc g_back+3
g_back   jmp g_newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
g_zpge   lda (zp1),y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
g_zpgf   sta (zp1),y
         jmp g_newc-3

v_edit   ldy e_sndn        ;sldtab
         lda snd_st,y
         sta zp9
         ldy #$00
         ldx #$00
v_edi2   lda #zp1
         sta v_zpge+1
         sta v_zpgf+1
         lda e_msg1
         jsr fncout
v_loop   jsr colgld
         lda #hilite
         sta xDAE0,x
         sta xDAE1,x
         jsr sldtab
v_newc   jsr getkey        ;new char
         cmp #$0d
         bne v_down
         cpy #$05
         bne v_rint
         ldx x_line,y
         lda zp9
         cmp #$fa
         beq v_edi2
         inc zp9
         jmp v_edi2
v_rint   iny
         ldx x_line,y
         jmp v_edi2
v_down   cmp #$11
         bne v_home
         cpy #$05
         bne v_dint
         lda zp9           ;scroll
         cmp #$fa
         beq v_newc
         inc zp9
         jmp v_loop
v_dint   iny               ;down
         txa
         clc
         adc #$28
         tax
         jmp v_loop
v_home   cmp #$13
         bne v_delc
         ldy #$00
         sty zp9
         jmp v_edi2-2
v_delc   cmp #$14          ;delete
         bne v_rght
         sei
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$ff
         beq v_dele
         ldx #$3f          ;mod.pntr
v_dcmp   cmp snd_st,x
         bcs v_dlow
         dec snd_st,x
v_dlow   dex
         bpl v_dcmp
         sta e_orad
         ldx #$00
v_djst   lda sld_rp,x
         cmp #$ff
         bne v_djnx
         lda e_orad
         cmp sld_fh,x
         bcs v_djnx
         dec sld_fh,x
v_djnx   inx
         bne v_djst
         jsr sndtab
         lda #$ff
         sec
         sbc zp9
         sta v_dcpy+1
v_delp   iny
         lda (zp1),y
         dey
         sta (zp1),y
         iny
         lda (zp3),y
         dey
         sta (zp3),y
         iny
         lda (zp5),y
         dey
         sta (zp5),y
         iny
v_dcpy   cpy #$00
         bne v_delp
v_dele   lda #$00
         sta (zp1),y
         sta (zp3),y
         sta (zp5),y
         lda #irqc
         sta xD019
         pla
         tay
         pla
         tax
         cli
         jmp v_loop
v_rght   cmp #$1d
         bne v_uppp
         lda v_zpge+1
         cmp #zp5
         bne *+5
         jmp v_newc
         inc v_zpge+1
         inc v_zpge+1
         inc v_zpgf+1
         inc v_zpgf+1
         inx
         inx
         inx
         stx e_orad
         lda v_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp v_loop
v_uppp   cmp #$91
         bne v_inst
         cpy #$00
         bne v_uint
         lda zp9           ;scroll
         bne *+5
         jmp v_newc
         dec zp9
         jmp v_loop
v_uint   dey               ;down
         txa
         sec
         sbc #$28
         tax
         jmp v_loop
v_inst   cmp #$94
         bne v_left
         sei
         txa
         pha
         sty v_icpy+1
         tya
         clc
         adc zp9
         cmp #$ff
         beq v_inse
         ldx #$3f
v_icmp   cmp snd_st,x      ;mod.pntr
         beq v_ilow-3
         bcs v_ilow
         inc snd_st,x
v_ilow   dex
         bpl v_icmp
         sta e_orad
         ldx #$00
v_ijst   lda sld_rp,x
         cmp #$ff
         bne v_ijnx
         lda e_orad
         cmp sld_fh,x
         beq v_ijnx-3
         bcs v_ijnx
         inc sld_fh,x
v_ijnx   inx
         bne v_ijst
         jsr sndtab
         lda #$ff
         sec
         sbc zp9
         tay
v_islp   dey
         lda (zp1),y
         iny
         sta (zp1),y
         dey
         lda (zp3),y
         iny
         sta (zp3),y
         dey
         lda (zp5),y
         iny
         sta (zp5),y
         dey
v_icpy   cpy #$00
         bne v_islp
v_inse   lda #$00
         sta (zp1),y
         sta (zp3),y
         sta (zp5),y
         lda #irqc
         sta xD019
         pla
         tax
         cli
         jmp v_loop
v_left   cmp #$9d
         bne v_inot
         lda v_zpge+1
         cmp #zp1
         bne *+5
         jmp v_newc
         dec v_zpge+1
         dec v_zpge+1
         dec v_zpgf+1
         dec v_zpgf+1
         dex
         dex
         dex
         stx e_orad
         lda v_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp v_loop
v_inot   cmp #$db          ;sh.+
         bne v_dnot
         lda e_test
         cmp #$5e
         beq *+8
         inc e_test
         jsr sndtab
         jmp v_newc
v_dnot   cmp #$dd
         bne v_spax
         lda e_test
         beq *+8
         dec e_test
         jsr sndtab
         jmp v_newc
v_spax   cmp #$20          ;test
         bne v_gsnd
         jsr spaces
         jmp v_newc
v_gsnd   cmp #$28          ;exit
         bcs v_isnd
         and #$07
         tay
         jmp colgld
v_isnd   cmp #$2d          ;snd.#
         beq v_dsnd
         cmp #$2b
         bne v_scrn
         inc e_sndn
         jmp *+6
v_dsnd   dec e_sndn
         lda e_sndn
         and #$3f
         sta e_sndn
         jsr _sounds
         jmp v_edit
v_scrn   cmp #$5f          ;to editor
         bne v_tr1x
         ldy #$00
         jmp colgld
v_tr1x   jsr keychk
         bne v_sret
         jmp v_newc
v_sret   cmp #$8d
         bne v_numb
         ldy #$01
         jmp colgld
v_numb   cmp #$30
         bcc v_back
         cmp #$3a
         bcc v_back+3
         cmp #$41
         bcc v_back
         cmp #$47
         bcc v_back+3
v_back   jmp v_newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
v_zpge   lda (zp1),y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
v_zpgf   sta (zp1),y
         jmp v_newc-3

r_edit   lda e_tune        ;trstab
         sta zp9
         ldy #$00
         ldx #$00
r_edi2   lda #zp1
         sta r_zpge+1
         sta r_zpgf+1
         lda e_msg1
         jsr fncout
r_loop   jsr colgld
         lda #hilite
         sta xDAEE,x
         sta xDAEF,x
         jsr trstab
r_newc   jsr getkey        ;new char
         cmp #$0d
         bne r_down
         cpy #$05
         bne r_rint
         ldx x_line,y
         lda zp9
         cmp #$1a
         beq r_edi2
         inc zp9
         jmp r_edi2
r_rint   iny
         ldx x_line,y
         jmp r_edi2
r_down   cmp #$11
         bne r_home
         cpy #$05
         bne r_dint
         lda zp9           ;scroll
         cmp #$1a
         beq r_newc
         inc zp9
         jmp r_loop
r_dint   iny               ;down
         txa
         clc
         adc #$28
         tax
         jmp r_loop
r_home   cmp #$13
         bne r_delc
         ldy #$00
         sty zp9
         jmp r_edi2-2
r_delc   cmp #$14          ;delete
         bne r_rght
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$1f
         beq r_dele
         lda #$1f
         sec
         sbc zp9
         sta r_dcpy+1
r_delp   iny
         lda (zp1),y
         dey
         sta (zp1),y
         iny
         lda (zp3),y
         dey
         sta (zp3),y
         iny
         lda (zp5),y
         dey
         sta (zp5),y
         iny
r_dcpy   cpy #$00
         bne r_delp
r_dele   lda #$00
         sta (zp1),y
         sta (zp3),y
         sta (zp5),y
         pla
         tay
         pla
         tax
         jmp r_loop
r_rght   cmp #$1d
         bne r_uppp
         lda r_zpge+1
         cmp #zp5
         bne *+5
         jmp r_newc
         inc r_zpge+1
         inc r_zpge+1
         inc r_zpgf+1
         inc r_zpgf+1
         inx
         inx
         inx
         stx e_orad
         lda r_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp r_loop
r_uppp   cmp #$91
         bne r_inst
         cpy #$00
         bne r_uint
         lda zp9           ;scroll
         bne *+5
         jmp r_newc
         dec zp9
         jmp r_loop
r_uint   dey               ;down
         txa
         sec
         sbc #$28
         tax
         jmp r_loop
r_inst   cmp #$94
         bne r_left
         txa
         pha
         sty r_icpy+1
         tya
         clc
         adc zp9
         cmp #$1f
         beq r_inse
         lda #$1f
         sec
         sbc zp9
         tay
r_islp   dey
         lda (zp1),y
         iny
         sta (zp1),y
         dey
         lda (zp3),y
         iny
         sta (zp3),y
         dey
         lda (zp5),y
         iny
         sta (zp5),y
         dey
r_icpy   cpy #$00
         bne r_islp
r_inse   lda #$00
         sta (zp1),y
         sta (zp3),y
         sta (zp5),y
         pla
         tax
         jmp r_loop
r_left   cmp #$9d
         bne r_inot
         lda r_zpge+1
         cmp #zp1
         bne *+5
         jmp r_newc
         dec r_zpge+1
         dec r_zpge+1
         dec r_zpgf+1
         dec r_zpgf+1
         dex
         dex
         dex
         stx e_orad
         lda r_zpge+1
         sec
         sbc #zp1
         lsr a
         tax
         lda e_msg1,x
         jsr fncout
         ldx e_orad
         jmp r_loop
r_inot   cmp #$db          ;sh.+
         bne r_dnot
         lda e_test
         cmp #$5e
         beq *+8
         inc e_test
         jsr sndtab
         jmp r_newc
r_dnot   cmp #$dd
         bne r_spax
         lda e_test
         beq *+8
         dec e_test
         jsr sndtab
         jmp r_newc
r_spax   cmp #$20          ;test
         bne r_gsnd
         jsr spaces
         jmp r_newc
r_gsnd   cmp #$28          ;exit
         bcs r_isnd
         and #$07
         tay
         jmp colgld
r_isnd   cmp #$2d          ;snd.#
         beq r_dsnd
         cmp #$2b
         bne r_scrn
         inc e_sndn
         jmp *+6
r_dsnd   dec e_sndn
         lda e_sndn
         and #$3f
         sta e_sndn
         lda zp9
         pha
         jsr _sounds
         pla
         jmp r_edit+3
r_scrn   cmp #$5f          ;to editor
         bne r_tr1x
         ldy #$00
         jmp colgld
r_tr1x   jsr keychk
         bne r_numb
         jmp r_newc
r_numb   cmp #$30
         bcc r_back
         cmp #$3a
         bcc r_back+3
         cmp #$41
         bcc r_back
         cmp #$47
         bcc r_back+3
r_back   jmp r_newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
r_zpge   lda (zp1),y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
r_zpgf   sta (zp1),y
         jmp r_newc-3


i_edit   jsr _sounds
         jsr sndtab
i_loop   lda e_spos
         asl a
         asl a
         asl a
         asl a
         asl a
         asl a
         php
         clc
         adc #LO(snd_ad)
         sta zp1
         lda #HI(snd_ad)
         adc #$00
         plp
         adc #$00
         sta zp2
         lda e_spos
         asl a
         clc
         adc e_spos
         tax
         ldy e_sndn
         lda e_spos
         jsr fncout
i_wcol   jsr colsnd
         lda #hilite
         sta xD882,x
         sta xD883,x
i_newc   jsr getkey
         cmp #$0d
         bne i_down
         lda snd_ad,y
         sta snd_tmp
         lda snd_sr,y
         sta snd_tmp+1
         lda snd_gt,y
         sta snd_tmp+2
         lda snd_wt,y
         sta snd_tmp+3
         lda snd_ft,y
         sta snd_tmp+4
         lda snd_pt,y
         sta snd_tmp+5
         lda snd_st,y
         sta snd_tmp+6
         jmp i_wcol
i_down   cmp #$11
         bne i_home
         lda (zp1),y
         clc
         adc #$01
         sta (zp1),y
         jmp i_edit
i_home   cmp #$13
         bne i_rght
         lda #$00
         sta e_sndn
         sta e_spos
         jmp i_edit
i_rght   cmp #$1d
         bne i_uppp
         lda e_spos
         cmp #$06
         beq i_newc
         inc e_spos
         jmp i_loop
i_uppp   cmp #$91
         bne i_left
         lda (zp1),y
         sec
         sbc #$01
         sta (zp1),y
         jmp i_edit
i_left   cmp #$9d
         bne i_inot
         lda e_spos
         beq i_newc
         dec e_spos
         jmp i_loop
i_inot   cmp #$db          ;sh.+
         bne i_dnot
         lda e_test
         cmp #$5e
         beq *+8
         inc e_test
         jsr sndtab
         jmp i_newc
i_dnot   cmp #$dd
         bne i_spax
         lda e_test
         beq *+8
         dec e_test
         jsr sndtab
         jmp i_newc
i_spax   cmp #$20          ;test
         bcc *-5
         bne i_gsnd
         jsr spaces
         jmp i_newc
i_gsnd   cmp #$28          ;exit
         bcs i_isnd
         and #$07
         tay
         jmp colsnd
i_isnd   cmp #$2d          ;snd.#
         beq i_dsnd
         cmp #$2b
         bne i_sbuf
         inc e_sndn
         jmp *+6
i_dsnd   dec e_sndn
         lda e_sndn
         and #$3f
         sta e_sndn
         jmp i_edit
i_sbuf   cmp #$5e
         bne i_scrn
         lda snd_tmp
         sta snd_ad,y
         lda snd_tmp+1
         sta snd_sr,y
         lda snd_tmp+2
         sta snd_gt,y
         lda snd_tmp+3
         sta snd_wt,y
         lda snd_tmp+4
         sta snd_ft,y
         lda snd_tmp+5
         sta snd_pt,y
         lda snd_tmp+6
         sta snd_st,y
         jmp i_edit
i_scrn   cmp #$5f          ;to editor
         bne i_tr1x
         ldy #$00
         jmp colsnd
i_tr1x   jsr keychk
         bne i_sret
i2768    jmp i_newc
i_sret   cmp #$8d
         bne i_numb
         ldy e_spos
         cpy #$03
         bcc i_sret-3
         cpy #$06
         beq *+3
         dey
         jmp colsnd
i_numb   cmp #$30
         bcc i_sret-3
         cmp #$3a
         bcc i_cont
         cmp #$41
         bcc i_sret-3
         cmp #$47
         bcs i2768
i_cont   cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
         lda (zp1),y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
         sta (zp1),y
         jmp i_edit

;--------------ed2

jmpnum   iny
         lda (zp7),y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
         sta (zp7),y
         dey
         rts
incnum   lda e_orad
         beq incend
         cmp #$08
         bcs incend
         adc #$f7
         sta (zp7),y
incend   rts
decnum   lda e_orad
         beq incend
         cmp #$08
         bcs incend
         adc #$f0
         sta (zp7),y
         rts
volnum   lda e_orad
         clc
         adc #$e0
         sta (zp7),y
         rts
sctnum   asl a
         asl a
         asl a
         asl a
         and #$7f
         cmp #$60
         bcc *+4
         and #$3f
         ora #$80
         ora e_orad
         sta (zp7),y
         rts
trdnum   asl a
         asl a
         asl a
         asl a
         and #$30
         ora #$40
         ora e_orad
         sta (zp7),y
         rts
trunum   asl a
         asl a
         asl a
         asl a
         and #$30
         ora e_orad
         sta (zp7),y
         rts

t1edit   lda e_tr1p        ;track1
         sta zp9
         ldy #$00
t1loop   jsr coltrs
         ldx x_line,y
         lda #hilite
         sta xD87C,x
         sta xD87D,x
         sta xD87E,x
         sta xD87F,x
         sta xD880,x
         jsr tr1out
t1newc   jsr getkey
         cmp #$20
         beq t1newc
         cmp #$0d
         beq t1down
         cmp #$11
         bne t1home
t1down   cpy #$05
         bne t1dint
         lda zp9           ;scroll
         cmp #$fa
         bcs t1newc
         inc zp9
         jmp t1loop
t1dint   iny               ;down
         jmp t1loop
t1home   cmp #$13
         bne t1delc
         ldy e_tune
         lda start1,y
         sta zp9
         jmp t1edit+5
t1delc   cmp #$14          ;delete
         bne t1rght
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$ff
         beq t1dele
         ldx #$1f          ;mod.pntr
t1dcmp   cmp start1,x
         bcs t1dlow
         dec start1,x
t1dlow   dex
         bpl t1dcmp
         sta e_orad
         tya
         tax
         ldy #$00
t1djst   lda (zp7),y
         cmp #$ff          ;jmp?
         bne t1djnx
         iny
         lda e_orad
         cmp (zp7),y
         bcs t1djnx-4
         lda (zp7),y
         sec
         sbc #$01
         sta (zp7),y
         cpy #$ff
         beq *+7
t1djnx   iny
         cpy #$ff
         bne t1djst
         txa
         tay
         jsr startw
         lda #$ff
         sec
         sbc zp9
         sta t1dcpy+1
t1delp   iny
         lda (zp7),y
         dey
         sta (zp7),y
         iny
t1dcpy   cpy #$00
         bne t1delp
t1dele   lda #$80
         sta (zp7),y
         pla
         tay
         pla
         tax
         jmp t1loop
t1rght   cmp #$1d
         bne t1uppp
         lda zp9
         sta e_tr1p
         lda e_tr2p
         sta zp9
         jmp t2loop
t1uppp   cmp #$91
         bne t1inst
         cpy #$00
         bne t1uint
         lda zp9           ;scroll
         bne *+5
         jmp t1newc
         dec zp9
         jmp t1loop
t1uint   dey               ;down
         jmp t1loop
t1inst   cmp #$94
         bne t1gsnd
         txa
         pha
         sty t1icpy+1
         tya
         clc
         adc zp9
         cmp #$ff
         beq t1inse
         ldx #$1f
t1icmp   cmp start1,x      ;mod.pntr
         bcs t1ilow
         inc start1,x
t1ilow   dex
         bpl t1icmp
         sta e_orad
         ldy #$00
t1ijst   lda (zp7),y
         cmp #$ff          ;jmp?
         bne t1ijnx
         iny
         lda e_orad
         cmp (zp7),y
         beq *+4
         bcs t1ijnx-4
         lda (zp7),y
         clc
         adc #$01
         sta (zp7),y
         cpy #$ff
         beq *+7
t1ijnx   iny
         cpy #$ff
         bne t1ijst
         jsr startw
         lda #$ff
         sec
         sbc zp9
         tay
t1islp   dey
         lda (zp7),y
         iny
         sta (zp7),y
         dey
t1icpy   cpy #$00
         bne t1islp
t1inse   lda #$80
         sta (zp7),y
         pla
         tax
         jmp t1loop
t1gsnd   cmp #$28          ;exit
         bcs t1font
         and #$07
         tay
         lda zp9
         sta e_tr1p
         jmp coltrs
t1font   cmp #$5c
         bne t1scrn
         tya
         clc
         adc zp9
         ldx e_tune
         sta start1,x
         sta zp9
         jsr chk_fa
         sta e_tr1p
         jsr startw
         jmp t1edit
t1scrn   cmp #$5f          ;to editor
         bne t1tr1x
         ldy #$00
         lda zp9
         sta e_tr1p
         jmp coltrs
t1tr1x   jsr keychk
         beq *+9
         cmp #$01
         bne t1sret
         jmp t1edit
         jmp t1newc
t1sret   cmp #$8d
         bne t1lett
         lda #$01
         sta e_ltrk
         lda (zp7),y
         cmp #$80
         bcc t1sre1
         cmp #$e0
         bcs t1sre1
         and #$7f
         sta e_sctn
t1sre1   ldy #$04
         lda zp9
         sta e_tr1p
         jmp coltrs
t1lett   cmp #$c4          ;sh.d
         bne *+6
         lda #$f1
         bne t1lcmd
         cmp #$c8          ;sh.h
         bne *+6
         lda #$f0
         bne t1lcmd
         cmp #$c9          ;sh.i
         bne *+6
         lda #$f8
         bne t1lcmd
         cmp #$ca          ;sh.j
         bne *+6
         lda #$ff
         bne t1lcmd
         cmp #$d3          ;sh.s
         bne *+6
         lda #$80
         bne t1lcmd
         cmp #$d6          ;sh.v
         bne *+6
         lda #$e0
         bne t1lcmd
         cmp #$2b          ;+
         beq *+6
         cmp #$db          ;sh.+
         bne *+6
         lda #$00
         beq t1lcmd
         cmp #$2d          ;-
         beq *+6
         cmp #$dd          ;sh.-
         bne t1numb
         lda #$40
t1lcmd   sta (zp7),y
         jmp t1newc-3
t1numb   cmp #$30          ;number
         bcc t1back
         cmp #$3a
         bcc t1back+3
         cmp #$41
         bcc t1back
         cmp #$47
         bcc t1back+3
t1back   jmp t1newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
         lda (zp7),y
         cmp #$ff          ;jmp
         bne *+8
         jsr jmpnum
         jmp t1newc-3
         cmp #$f8          ;inc
         bcc *+8
         jsr incnum
         jmp t1newc-3
         cmp #$f0          ;hlt
         beq t1back
         bcc *+8
         jsr decnum        ;dec
         jmp t1newc-3
         cmp #$e0          ;vol
         bcc *+8
         jsr volnum
         jmp t1newc-3
         cmp #$80          ;sct
         bcc *+8
         jsr sctnum
         jmp t1newc-3
         cmp #$40          ;tr-
         bcc *+8
         jsr trdnum
         jmp t1newc-3
         jsr trunum        ;tr+
         jmp t1newc-3

t2edit   lda e_tr2p        ;track2
         sta zp9
         ldy #$00
t2loop   jsr coltrs
         ldx x_line,y
         lda #hilite
         sta xD885,x
         sta xD886,x
         sta xD887,x
         sta xD888,x
         sta xD889,x
         jsr tr2out
t2newc   jsr getkey
         cmp #$20
         beq t2newc
         cmp #$0d
         beq t2down
         cmp #$11
         bne t2home
t2down   cpy #$05
         bne t2dint
         lda zp9           ;scroll
         cmp #$fa
         bcs t2newc
         inc zp9
         jmp t2loop
t2dint   iny               ;down
         jmp t2loop
t2home   cmp #$13
         bne t2delc
         ldy e_tune
         lda start2,y
         sta zp9
         jmp t2edit+5
t2delc   cmp #$14          ;delete
         bne t2rght
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$ff
         beq t2dele
         ldx #$1f          ;mod.pntr
t2dcmp   cmp start2,x
         bcs t2dlow
         dec start2,x
t2dlow   dex
         bpl t2dcmp
         sta e_orad
         tya
         tax
         ldy #$00
t2djst   lda (zp7),y
         cmp #$ff          ;jmp?
         bne t2djnx
         iny
         lda e_orad
         cmp (zp7),y
         bcs t2djnx-4
         lda (zp7),y
         sec
         sbc #$01
         sta (zp7),y
         cpy #$ff
         beq *+7
t2djnx   iny
         cpy #$ff
         bne t2djst
         txa
         tay
         jsr startw
         lda #$ff
         sec
         sbc zp9
         sta t2dcpy+1
t2delp   iny
         lda (zp7),y
         dey
         sta (zp7),y
         iny
t2dcpy   cpy #$00
         bne t2delp
t2dele   lda #$80
         sta (zp7),y
         pla
         tay
         pla
         tax
         jmp t2loop
t2rght   cmp #$1d
         bne t2uppp
         lda zp9
         sta e_tr2p
         lda e_tr3p
         sta zp9
         jmp t3loop
t2uppp   cmp #$91
         bne t2inst
         cpy #$00
         bne t2uint
         lda zp9           ;scroll
         bne *+5
         jmp t2newc
         dec zp9
         jmp t2loop
t2uint   dey               ;down
         jmp t2loop
t2inst   cmp #$94
         bne t2left
         txa
         pha
         sty t2icpy+1
         tya
         clc
         adc zp9
         cmp #$ff
         beq t2inse
         ldx #$1f
t2icmp   cmp start2,x      ;mod.pntr
         bcs t2ilow
         inc start2,x
t2ilow   dex
         bpl t2icmp
         sta e_orad
         ldy #$00
t2ijst   lda (zp7),y
         cmp #$ff          ;jmp?
         bne t2ijnx
         iny
         lda e_orad
         cmp (zp7),y
         beq *+4
         bcs t2ijnx-4
         lda (zp7),y
         clc
         adc #$01
         sta (zp7),y
         cpy #$ff
         beq *+7
t2ijnx   iny
         cpy #$ff
         bne t2ijst
         jsr startw
         lda #$ff
         sec
         sbc zp9
         tay
t2islp   dey
         lda (zp7),y
         iny
         sta (zp7),y
         dey
t2icpy   cpy #$00
         bne t2islp
t2inse   lda #$80
         sta (zp7),y
         pla
         tax
         jmp t2loop
t2left   cmp #$9d
         bne t2gsnd
         lda zp9
         sta e_tr2p
         lda e_tr1p
         sta zp9
         jmp t1loop
t2gsnd   cmp #$28          ;exit
         bcs t2font
         and #$07
         tay
         lda zp9
         sta e_tr2p
         jmp coltrs
t2font   cmp #$5c
         bne t2scrn
         tya
         clc
         adc zp9
         ldx e_tune
         sta start2,x
         sta zp9
         jsr chk_fa
         sta e_tr2p
         jsr startw
         jmp t2edit
t2scrn   cmp #$5f          ;to editor
         bne t2tr1x
         ldy #$00
         lda zp9
         sta e_tr2p
         jmp coltrs
t2tr1x   jsr keychk
         beq *+9
         cmp #$01
         bne t2sret
         jmp t2edit
         jmp t2newc
t2sret   cmp #$8d
         bne t2lett
         lda #$02
         sta e_ltrk
         lda (zp7),y
         cmp #$80
         bcc t2sre1
         cmp #$e0
         bcs t2sre1
         and #$7f
         sta e_sctn
t2sre1   ldy #$04
         lda zp9
         sta e_tr2p
         jmp coltrs
t2lett   cmp #$c4          ;sh.d
         bne *+6
         lda #$f1
         bne t2lcmd
         cmp #$c8          ;sh.h
         bne *+6
         lda #$f0
         bne t2lcmd
         cmp #$c9          ;sh.i
         bne *+6
         lda #$f8
         bne t2lcmd
         cmp #$ca          ;sh.j
         bne *+6
         lda #$ff
         bne t2lcmd
         cmp #$d3          ;sh.s
         bne *+6
         lda #$80
         bne t2lcmd
         cmp #$d6          ;sh.v
         bne *+6
         lda #$e0
         bne t2lcmd
         cmp #$2b          ;+
         beq *+6
         cmp #$db          ;sh.+
         bne *+6
         lda #$00
         beq t2lcmd
         cmp #$2d          ;-
         beq *+6
         cmp #$dd          ;sh.-
         bne t2numb
         lda #$40
t2lcmd   sta (zp7),y
         jmp t2newc-3
t2numb   cmp #$30          ;number
         bcc t2back
         cmp #$3a
         bcc t2back+3
         cmp #$41
         bcc t2back
         cmp #$47
         bcc t2back+3
t2back   jmp t2newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
         lda (zp7),y
         cmp #$ff          ;jmp
         bne *+8
         jsr jmpnum
         jmp t2newc-3
         cmp #$f8          ;inc
         bcc *+8
         jsr incnum
         jmp t2newc-3
         cmp #$f0          ;hlt
         beq t2back
         bcc *+8
         jsr decnum        ;dec
         jmp t2newc-3
         cmp #$e0          ;vol
         bcc *+8
         jsr volnum
         jmp t2newc-3
         cmp #$80          ;sct
         bcc *+8
         jsr sctnum
         jmp t2newc-3
         cmp #$40          ;tr-
         bcc *+8
         jsr trdnum
         jmp t2newc-3
         jsr trunum        ;tr+
         jmp t2newc-3

t3edit   lda e_tr3p        ;track3
         sta zp9
         ldy #$00
t3loop   jsr coltrs
         ldx x_line,y
         lda #hilite
         sta xD88E,x
         sta xD88F,x
         sta xD890,x
         sta xD891,x
         sta xD892,x
         jsr tr3out
t3newc   jsr getkey
         cmp #$1d
         beq t3newc
         cmp #$20
         beq t3newc
         cmp #$0d
         beq t3down
         cmp #$11
         bne t3home
t3down   cpy #$05
         bne t3dint
         lda zp9           ;scroll
         cmp #$fa
         bcs t3newc
         inc zp9
         jmp t3loop
t3dint   iny               ;down
         jmp t3loop
t3home   cmp #$13
         bne t3delc
         ldy e_tune
         lda start3,y
         sta zp9
         jmp t3edit+5
t3delc   cmp #$14          ;delete
         bne t3uppp
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$ff
         beq t3dele
         ldx #$1f          ;mod.pntr
t3dcmp   cmp start3,x
         bcs t3dlow
         dec start3,x
t3dlow   dex
         bpl t3dcmp
         sta e_orad
         tya
         tax
         ldy #$00
t3djst   lda (zp7),y
         cmp #$ff          ;jmp?
         bne t3djnx
         iny
         lda e_orad
         cmp (zp7),y
         bcs t3djnx-4
         lda (zp7),y
         sec
         sbc #$01
         sta (zp7),y
         cpy #$ff
         beq *+7
t3djnx   iny
         cpy #$ff
         bne t3djst
         txa
         tay
         jsr startw
         lda #$ff
         sec
         sbc zp9
         sta t3dcpy+1
t3delp   iny
         lda (zp7),y
         dey
         sta (zp7),y
         iny
t3dcpy   cpy #$00
         bne t3delp
t3dele   lda #$80
         sta (zp7),y
         pla
         tay
         pla
         tax
         jmp t3loop
t3uppp   cmp #$91
         bne t3inst
         cpy #$00
         bne t3uint
         lda zp9           ;scroll
         bne *+5
         jmp t3newc
         dec zp9
         jmp t3loop
t3uint   dey               ;down
         jmp t3loop
t3inst   cmp #$94
         bne t3left
         txa
         pha
         sty t3icpy+1
         tya
         clc
         adc zp9
         cmp #$ff
         beq t3inse
         ldx #$1f
t3icmp   cmp start3,x      ;mod.pntr
         bcs t3ilow
         inc start3,x
t3ilow   dex
         bpl t3icmp
         sta e_orad
         ldy #$00
t3ijst   lda (zp7),y
         cmp #$ff          ;jmp?
         bne t3ijnx
         iny
         lda e_orad
         cmp (zp7),y
         beq *+4
         bcs t3ijnx-4
         lda (zp7),y
         clc
         adc #$01
         sta (zp7),y
         cpy #$ff
         beq *+7
t3ijnx   iny
         cpy #$ff
         bne t3ijst
         jsr startw
         lda #$ff
         sec
         sbc zp9
         tay
t3islp   dey
         lda (zp7),y
         iny
         sta (zp7),y
         dey
t3icpy   cpy #$00
         bne t3islp
t3inse   lda #$80
         sta (zp7),y
         pla
         tax
         jmp t3loop
t3left   cmp #$9d
         bne t3gsnd
         lda zp9
         sta e_tr3p
         lda e_tr2p
         sta zp9
         jmp t2loop
t3gsnd   cmp #$28          ;exit
         bcs t3font
         and #$07
         tay
         lda zp9
         sta e_tr3p
         jmp coltrs
t3font   cmp #$5c
         bne t3scrn
         tya
         clc
         adc zp9
         ldx e_tune
         sta start3,x
         sta zp9
         jsr chk_fa
         sta e_tr3p
         jsr startw
         jmp t3edit
t3scrn   cmp #$5f          ;to editor
         bne t3tr1x
         ldy #$00
         lda zp9
         sta e_tr3p
         jmp coltrs
t3tr1x   jsr keychk
         beq *+9
         cmp #$01
         bne t3sret
         jmp t3edit
         jmp t3newc
t3sret   cmp #$8d
         bne t3lett
         lda #$03
         sta e_ltrk
         lda (zp7),y
         cmp #$80
         bcc t3sre1
         cmp #$e0
         bcs t3sre1
         and #$7f
         sta e_sctn
t3sre1   ldy #$04
         lda zp9
         sta e_tr3p
         jmp coltrs
t3lett   cmp #$c4          ;sh.d
         bne *+6
         lda #$f1
         bne t3lcmd
         cmp #$c8          ;sh.h
         bne *+6
         lda #$f0
         bne t3lcmd
         cmp #$c9          ;sh.i
         bne *+6
         lda #$f8
         bne t3lcmd
         cmp #$ca          ;sh.j
         bne *+6
         lda #$ff
         bne t3lcmd
         cmp #$d3          ;sh.s
         bne *+6
         lda #$80
         bne t3lcmd
         cmp #$d6          ;sh.v
         bne *+6
         lda #$e0
         bne t3lcmd
         cmp #$2b          ;+
         beq *+6
         cmp #$db          ;sh.+
         bne *+6
         lda #$00
         beq t3lcmd
         cmp #$2d          ;-
         beq *+6
         cmp #$dd          ;sh.-
         bne t3numb
         lda #$40
t3lcmd   sta (zp7),y
         jmp t3newc-3
t3numb   cmp #$30          ;number
         bcc t3back
         cmp #$3a
         bcc t3back+3
         cmp #$41
         bcc t3back
         cmp #$47
         bcc t3back+3
t3back   jmp t3newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
         lda (zp7),y
         cmp #$ff          ;jmp
         bne *+8
         jsr jmpnum
         jmp t3newc-3
         cmp #$f8          ;inc
         bcc *+8
         jsr incnum
         jmp t3newc-3
         cmp #$f0          ;hlt
         beq t3back
         bcc *+8
         jsr decnum        ;dec
         jmp t3newc-3
         cmp #$e0          ;vol
         bcc *+8
         jsr volnum
         jmp t3newc-3
         cmp #$80          ;sct
         bcc *+8
         jsr sctnum
         jmp t3newc-3
         cmp #$40          ;tr-
         bcc *+8
         jsr trdnum
         jmp t3newc-3
         jsr trunum        ;tr+
         jmp t3newc-3

s__snd   asl a
         asl a
         asl a
         asl a
         ora #$c0
         ora e_orad
         sta (zp1),y
         and #$3f
         sta e_sndn
         rts
s__dur   sec
         sbc #$7f
         asl a
         asl a
         asl a
         asl a
         ora e_orad
         sec
         sbc #$01
         and #$3f
         clc
         adc #$80
         sta (zp1),y
         rts
s__gld   sec
         sbc #$5f
         asl a
         asl a
         asl a
         asl a
         ora e_orad
         sec
         sbc #$01
         and #$1f
         clc
         adc #$60
         sta (zp1),y
         rts

s_edit   ldy #$00
         sty zp9
s_loop   jsr coltrs
         ldx x_line,y
         lda #hilite
         sta xD898,x
         sta xD899,x
         sta xD89A,x
         sta xD89B,x
         sta xD89C,x
         sta xD89D,x
s_csnd   jsr sctout
         lda (zp1),y
         cmp #$c0
         bcc *+7
         and #$3f
         sta e_sndn
         jsr sctlen
s_newc   jsr getkey
         cmp #$1d
         beq s_newc
         cmp #$20
         beq s_newc
         cmp #$0d
         bne s_down
         tya
         pha
         jsr coltrs
         ldy #$00
         lda zp2
         sta s_pbuf+2
s_pbuf   lda sectors,y
         sta sctbuf,y
         iny
         bne s_pbuf
         pla
         tay
         jmp s_loop
s_down   cmp #$11
         bne s_home
         cpy #$05
         bne s_dint
         lda zp9           ;scroll
         cmp #$fa
         beq s_newc
         inc zp9
         jmp s_loop
s_dint   iny               ;down
         jmp s_loop
s_home   cmp #$13
         beq s_edit
         cmp #$14
         bne s_uppp
         txa
         pha
         tya
         pha
         clc
         adc zp9
         cmp #$ff
         beq s_dele
         lda #$ff
         sec
         sbc zp9
         sta s_dcpy+1
s_delp   iny
         lda (zp1),y
         dey
         sta (zp1),y
         iny
s_dcpy   cpy #$00
         bne s_delp
s_dele   lda #$5f
         sta (zp1),y
         pla
         tay
         pla
         tax
         jmp s_loop
s_uppp   cmp #$91
         bne s_inst
         cpy #$00
         bne s_uint
         lda zp9           ;scroll
         bne *+5
         jmp s_newc
         dec zp9
         jmp s_loop
s_uint   dey               ;down
         jmp s_loop
s_inst   cmp #$94
         bne s_gsnd
         txa
         pha
         sty s_icpy+1
         tya
         clc
         adc zp9
         cmp #$ff
         beq s_inse
         lda #$ff
         sec
         sbc zp9
         tay
s_islp   dey
         lda (zp1),y
         iny
         sta (zp1),y
         dey
s_icpy   cpy #$00
         bne s_islp
s_inse   lda #$5f
         sta (zp1),y
         pla
         tax
         jmp s_loop
s_gsnd   cmp #$28          ;exit
         bcs s_dsct
         and #$07
         tay
         jmp coltrs
s_dsct   cmp #$3a
         bne s_isct
         lda e_sctn
         beq *+5
         dec e_sctn
         jmp s_loop
s_isct   cmp #$3b
         bne s_trup
         lda e_sctn
         cmp #$5f
         beq *+5
         inc e_sctn
         jmp s_loop
s_trup   cmp #$db
         bne s_trdn
         tya
         pha
         ldy #$00
s_tulo   lda (zp1),y
         cmp #$5e
         bcs *+6
         adc #$01
         sta (zp1),y
         iny
         bne s_tulo
         pla
         tay
         jmp s_loop
s_trdn   cmp #$dd
         bne s_arrw
         tya
         pha
         ldy #$00
s_tdlo   lda (zp1),y
         beq *+11
         cmp #$5f
         bcs *+7
         sec
         sbc #$01
         sta (zp1),y
         iny
         bne s_tdlo
         pla
         tay
         jmp s_loop
s_arrw   cmp #$5e
         bne s_scrn
         tya
         pha
         jsr coltrs
         ldy #$00
         lda zp2
         sta s_cbuf+5
s_cbuf   lda sctbuf,y
         sta sectors,y
         iny
         bne s_cbuf
         pla
         tay
         jmp s_loop
s_scrn   cmp #$5f          ;to editor
         bne s_tr1x
         ldy #$00
         jmp coltrs
s_tr1x   jsr keychk
         beq *+9
         cmp #$01
         bne s_sret
         jmp s_edit
         jmp s_newc
s_sret   cmp #$8d
         bne s_lett
         ldy e_ltrk
         jmp coltrs
s_lett   cmp #$c4          ;sh.d
         bne *+6
         lda #$80
         bne s_lcmd
         cmp #$c6          ;sh.f              ;Modif by H.L.
         bne *+6
         lda #$7f
         bne s_lcmd
         cmp #$c7          ;sh.g
         bne *+6
         lda #$60
         bne s_lcmd
         cmp #$c8          ;sh.h
         bne *+6
         lda #$6f
         bne s_lcmd
         cmp #$d3          ;sh.s
         bne *+6
         lda #$c0
         bne s_lcmd
         cmp #$2d          ;-
         bne s_numb
         lda #$5f
s_lcmd   sta (zp1),y
         jmp s_csnd
s_numb   sta e_orad
         lda (zp1),y       ;cmd?
         cmp #$60
         bcc s_note
         cmp #$6f
         beq s_note
         cmp #$7f
         beq s_note
         lda e_orad
         cmp #$30          ;number
         bcc s_back
         cmp #$3a
         bcc s_back+3
         cmp #$41
         bcc s_back
         cmp #$47
         bcc s_back+3
s_back   jmp s_newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
         lda (zp1),y
         cmp #$c0          ;snd.
         bcc *+8
         jsr s__snd
         jmp s_csnd
         cmp #$80          ;dur.
         bcc *+8
         jsr s__dur
         jmp s_csnd
         sta actdur
         lda e_orad        ;0?
         beq *+8
         lda actdur
         jsr s__gld        ;gld.
         jmp s_csnd
s_note   lda e_orad
         cmp #$31
         bcc s_back
         cmp #$39
         bcs s_keys
         and #$0f
         sec
         sbc #$01
         sta e_octv
         lda (zp1),y
s_nsbc   cmp #$0c
         bcc s_pure
         sec
         sbc #$0c
         jmp s_nsbc
s_keys   cmp #$41          ;c-
         bne *+6
         lda #$00
         beq s_pure
         cmp #$57          ;c#
         bne *+6
         lda #$01
         bne s_pure
         cmp #$53          ;d-
         bne *+6
         lda #$02
         bne s_pure
         cmp #$45          ;d#
         bne *+6
         lda #$03
         bne s_pure
         cmp #$44          ;e-
         bne *+6
         lda #$04
         bne s_pure
         cmp #$46          ;f-
         bne *+6
         lda #$05
         bne s_pure
         cmp #$54          ;f#
         bne *+6
         lda #$06
         bne s_pure
         cmp #$47          ;g-
         bne *+6
         lda #$07
         bne s_pure
         cmp #$59          ;g#
         bne *+6
         lda #$08
         bne s_pure
         cmp #$48          ;a-
         bne *+6
         lda #$09
         bne s_pure
         cmp #$55          ;a#
         bne *+6
         lda #$0a
         bne s_pure
         cmp #$4a          ;b-
         bne *+6
         lda #$0b
         bne s_pure
         cmp #$4b          ;c'
         beq *+5
         jmp s_newc
         lda #$0c
s_pure   ldx e_octv
         clc
         adc octave,x
         cmp #$5f
         bcc *+4
         lda #$5e
         sta (zp1),y
         sta e_test
         jsr spaces
         jmp s_loop

q_edit   ldx #$00
q_loop   ldy e_tune
         jsr f8_key+3
         jsr colsta
         lda #hilite
         sta xDA9E,x
         sta xDA9F,x
q_newc   jsr getkey
         cmp #$0d
         bne q_down
         txa
         bmi q_edit
         ldx #$cb
         jmp q_loop
q_down   cmp #$11
         bne q_home
         txa
         bmi q_newc
         bne q_dwn2
         lda start1,y
         clc
         adc #$01
         sta start1,y
         jmp q_loop
q_dwn2   cpx #$03
         bne q_dwn3
         lda start2,y
         clc
         adc #$01
         sta start2,y
         jmp q_loop
q_dwn3   lda start3,y
         clc
         adc #$01
         sta start3,y
         jmp q_loop
q_home   cmp #$13
         beq q_edit
         cmp #$1d          ;right
         bne q_uppp
         cpx #$06
         beq q_newc
         cpx #$ce
         beq q_newc
         inx
         inx
         inx
         jmp q_loop
q_uppp   cmp #$91
         bne q_left
         txa
         bpl *+5
q_new2   jmp q_newc
         bne q_upp2
         lda start1,y
         sec
         sbc #$01
         sta start1,y
         jmp q_loop
q_upp2   cpx #$03
         bne q_upp3
         lda start2,y
         sec
         sbc #$01
         sta start2,y
         jmp q_loop
q_upp3   lda start3,y
         sec
         sbc #$01
         sta start3,y
         jmp q_loop
q_left   cmp #$9d
         bne q_gsnd
         txa
         beq q_new2
         cpx #$cb
         beq q_new2
         dex
         dex
         dex
         jmp q_loop
q_gsnd   cmp #$21
         bcc q_new2
         cmp #$28          ;exit
         bcs q_scrn
         and #$07
         tay
         jmp colsta
q_scrn   cmp #$5f          ;to editor
         bne q_tr1x
         ldy #$00
         jmp colsta
q_tr1x   jsr keychk
         beq *+9
         cmp #$01
         bne q_numb
         jmp q_loop
         jmp q_newc
q_numb   cmp #$30
         bcc q_back
         cmp #$3a
         bcc q_back+3
         cmp #$41
         bcc q_back
         cmp #$47
         bcc q_back+3
q_back   jmp q_newc
         cmp #$40
         bcc *+5
         sec
         sbc #$07
         and #$0f
         sta e_orad
         txa
         bpl q_setn
         cpx #$cb
         beq q_inde
         lda e_orad
         cmp #$10
         bcs q_back
         ldy e_tune
         sta speeds,y
         jmp q_loop
q_inde   tya
         asl a
         asl a
         asl a
         asl a
         and #$1f
         ora e_orad
         sta e_tune
         tay
         jmp q_loop
q_setn   bne q_set2
         lda start1,y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
         sta start1,y
         jmp q_loop
q_set2   cpx #$03
         bne q_set3
         lda start2,y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
         sta start2,y
         jmp q_loop
q_set3   lda start3,y
         asl a
         asl a
         asl a
         asl a
         ora e_orad
         sta start3,y
         jmp q_loop

;--------------end of ed2

;--------------ed3
m_nent   ldx #$18
         lda #$20
         sta filnam,x
         sta x07A5,x
         dex
         bpl *-7
         ldx #$00
         lda #$7f
         sta x07A5,x
n_newc   jsr getkey
         cmp #$0d
         bne *+8
         lda #$20
         sta x07A5,x
         rts
         cmp #$14
         bne n_keys
         cpx #$00
         beq n_newc
         lda #$20
         sta x07A5,x
         dex
         sta filnam,x
         jmp n_newc-5
n_keys   cpx #$18
         beq n_newc
         cmp #$20
         bcc n_newc
         cmp #$40
         beq n_newc
         cmp #$5b
         bcs n_newc
         sta filnam,x
         sta x07A5,x
         inx
         jmp n_newc-5

m_load   jsr m_nent
         cpx #$00
         bne *+3
         rts
;memory paging; modif by H.L.

         set37
         lda #$01
         ldx #$08
         ldy #$00
         jsr iFFBA
         lda #$10
         ldx #LO(filnam)
         ldy #HI(filnam)
         jsr iFFBD
         jsr iFFC0
         bcc *+5
         jmp derror
         ldx #$01
         jsr iFFC6
         ldy #$00
         jsr basinp
         cmp #$00
         bne m_unid
         jsr basinp
         cmp #$70
         beq m_ldat        ;load data
m_unid   ldx #$18
         lda msg_pl,x
         sta x07A5,x
         dex
         bpl *-7
         jsr iFFCC
         lda #$01
         jsr iFFC3
         set35
         rts

m_ldat   ldx #$00
         jsr basinp
         cmp p_ver,x       ;V01.2x (only the first 5 chars!!!)
         bne m_unid
m_id     inx
         cpx #$05
         bne m_ldat+2
         jsr basinp        ;Skip minor version number byte
         ldx #$18          ;loading..
         lda msg_ld,x
         sta x07A5,x
         dex
         bpl *-7
         ldx #$00
m_lp01   jsr basinp        ;spd+trst
         sta speeds,x
         inx
         cpx #$80
         bne m_lp01
         ldx #$00
m_lp02   jsr basinp        ;gldtab
         sta gld_al,x
         inx
         cpx #$20
         bne m_lp02
         ldx #$00
m_lp03   jsr basinp        ;_sounds
         sta snd_ad,x
         inx
         bne m_lp03
m_lp04   jsr basinp
         sta snd_ft,x
         inx
         cpx #$c0
         bne m_lp04
         jsr basinp        ;wavetab
         sta e_orad        ;length
         ldx #$00
m_lp05   jsr basinp
         sta wve_wf,x
         jsr basinp
         sta wve_st,x
         inx
         cpx e_orad
         bne m_lp05
         cpx #$00
         beq *+13
         lda #$00
         sta wve_wf,x
         sta wve_st,x
         inx
         bne *-7
         jsr basinp        ;flttab
         sta e_orad        ;length
m_lp06   jsr basinp
         sta flt_rp,x
         jsr basinp
         sta flt_fh,x
         jsr basinp
         sta flt_rl,x
         inx
         cpx e_orad
         bne m_lp06
         cpx #$00
         beq *+16
         lda #$00
         sta flt_rp,x
         sta flt_fh,x
         sta flt_rl,x
         inx
         bne *-10
         jsr basinp        ;plstab
         sta e_orad        ;length
m_lp07   jsr basinp
         sta pls_rp,x
         jsr basinp
         sta pls_pl,x
         jsr basinp
         sta pls_ph,x
         inx
         cpx e_orad
         bne m_lp07
         cpx #$00
         beq *+16
         lda #$00
         sta pls_rp,x
         sta pls_pl,x
         sta pls_ph,x
         inx
         bne *-10
         jsr basinp        ;sldtab
         sta e_orad        ;length
m_lp08   jsr basinp
         sta sld_rp,x
         jsr basinp
         sta sld_fl,x
         jsr basinp
         sta sld_fh,x
         inx
         cpx e_orad
         bne m_lp08
         cpx #$00
         beq *+16
         lda #$00
         sta sld_rp,x
         sta sld_fl,x
         sta sld_fh,x
         inx
         bne *-10
         lda #HI(tracks)          ;tracks
         sta m_ptr1+2
         sta m_ptr2+2
m_lp09   jsr basinp
         sta e_orad        ;length
m_lp0a   jsr basinp
m_ptr1   sta tracks,x
         inx
         cpx e_orad
         bne m_lp0a
         cpx #$00
         beq *+16
         lda #$80
m_ptr2   sta tracks,x
         inx
         bne *-10
         inc m_ptr1+2
         inc m_ptr2+2
         lda m_ptr2+2
         cmp #HI(tracks+tracks_l)
         bne m_lp09
         lda #HI(sectors)
         sta m_ptr3+2      ;sectors
         sta m_ptr4+2
m_lp0b   jsr iFFCF
         bit st
         bvs m_fend
         ldy st
         bne m_fend8
         sta e_orad        ;length
m_lp0c   jsr iFFCF
         sta xD020
         sty xD020
m_ptr3   sta sectors,x
         bit st
         bvs m_fend
         ldy st
         bne m_fend8
         inx
         cpx e_orad
         bne m_lp0c
         cpx #$00
         beq *+16
         lda #$5f
m_ptr4   sta sectors,x
         inx
         bne *-10
         inc m_ptr3+2
         inc m_ptr4+2
         lda m_ptr4+2
         cmp #HI((sector_l+sectors))
         bne m_lp0b
m_fend   set37
         jsr iFFCC
         lda #$01
         jsr iFFC3
m_fend8  jmp derror

m_svdt   jsr m_nent     ;save data
         cpx #$00
         bne *+3
         rts
         set37
         lda #$01
         ldx #$08
         ldy #$01
         jsr iFFBA
         lda #$10
         ldx #LO(filnam)
         ldy #HI(filnam)
         jsr iFFBD
         jsr iFFC0
         bcc *+5
         jmp derror
         ldx #$18
         lda msg_sv,x      ;saving..
         sta x07A5,x
         dex
         bpl *-7
         ldx #$01
         jsr iFFC9
         set35           ;!!!
         lda #$00
         tay
         jsr basout
         lda #$70
         jsr basout
         ldx #$00
         lda p_ver,x       ;V01.23
         jsr basout
         inx
         cpx #$06
         bne *-9
         ldx #$00
m_lp0d   lda speeds,x       ;spd+trst
         jsr basout
         inx
         cpx #$80
         bne m_lp0d
         ldx #$00
m_lp0e   lda gld_al,x       ;gldtab
         jsr basout
         inx
         cpx #$20
         bne m_lp0e
         ldx #$00
m_lp0f   lda snd_ad,x       ;_sounds
         jsr basout
         inx
         bne m_lp0f
m_lp10   lda snd_ft,x
         jsr basout
         inx
         cpx #$c0
         bne m_lp10
         ldx #$00          ;wavetab
         dex
         beq *+7
         lda wve_wf,x
         beq *-6
         inx               ;length
         txa
         sta e_orad
         jsr basout
         ldx #$00
m_lp11   lda wve_wf,x
         jsr basout
         lda wve_st,x
         jsr basout
         inx
         cpx e_orad
         bne m_lp11
         ldx #$00          ;flttab
         dex
         beq *+7
         lda flt_rp,x
         beq *-6
         inx               ;length
         txa
         sta e_orad
         jsr basout
         ldx #$00
m_lp12   lda flt_rp,x
         jsr basout
         lda flt_fh,x
         jsr basout
         lda flt_rl,x
         jsr basout
         inx
         cpx e_orad
         bne m_lp12
         ldx #$00          ;plstab
         dex
         beq *+7
         lda pls_rp,x
         beq *-6
         inx               ;length
         txa
         sta e_orad
         jsr basout
         ldx #$00
m_lp13   lda pls_rp,x
         jsr basout
         lda pls_pl,x
         jsr basout
         lda pls_ph,x
         jsr basout
         inx
         cpx e_orad
         bne m_lp13
         ldx #$00          ;sldtab
         dex
         beq *+7
         lda sld_rp,x
         beq *-6
         inx               ;length
         txa
         sta e_orad
         jsr basout
         ldx #$00
m_lp14   lda sld_rp,x
         jsr basout
         lda sld_fl,x
         jsr basout
         lda sld_fh,x
         jsr basout
         inx
         cpx e_orad
         bne m_lp14
         lda #HI(tracks)          ;tracks
         sta m_ptr5+2
         sta m_ptr6+2
m_lp15   ldx #$00
         dex
         beq *+9
m_ptr5   lda tracks,x
         cmp #$ff
         bne *-8
         inx
         inx
         txa
         sta e_orad        ;length
         jsr basout
         ldx #$00
m_ptr6   lda tracks,x
         jsr basout
         inx
         cpx e_orad
         bne m_ptr6
         inc m_ptr5+2
         inc m_ptr6+2
         lda m_ptr6+2
         cmp #HI(tracks+tracks_l)
         bne m_lp15
         lda #HI(sectors)
         sta m_ptr7+2      ;sectors
         sta m_ptr8+2
         ldx #$ff
m_ptr7   lda sectors,x
         cmp #$5f
         bne m_lp16
         dex
         cpx #$ff
         bne m_ptr7
         jmp m_fend
m_lp16   inx
         txa
         sta e_orad        ;length
         jsr basout
         ldx #$00
m_ptr8   lda sectors,x
         jsr basout
         inx
         cpx e_orad
         bne m_ptr8
         inc m_ptr7+2
         inc m_ptr8+2
         lda m_ptr8+2
         cmp #HI((sector_l+sectors))
         bne m_ptr7-2
         jmp m_fend

basout   pha
         st01
         set37
         pla
         jsr iFFD2
         rst01
         jmp *+6
basinp   jsr iFFCF
         sta xD020
         sty xD020
         ldy st
         bne *+3
         rts
         set37
         pla
         pla
derror   lda st
         pha
         jsr iFFCC
         lda #$01
         jsr iFFC3
         pla
         bpl rdrive
i37C2    ldx #$18
         lda msg_np,x
         sta x07A5,x
         dex
         bpl *-7
         set35
         rts

rdrive   LDA #$01
         LDX #$08
         LDY #$0F
         JSR iFFBA
         LDA #$00
         TAX
         TAY
         JSR iFFBD
         JSR iFFC0

i37E1    ldx #$18
         lda #$20
         sta x07A5,x
         dex
         bpl *-4
         ldx #$01
         jsr iFFC6
         ldx #$00
         jsr iFFCF
         sta x07A5,x       ;00,
         inx
         cpx #$03
         bne *-9
         jsr iFFCF
         cmp #$20          ;1st spc
         bne *+5
rdloop   jsr iFFCF
         cmp #$2c
         beq rdcomm
         sta x07A5,x
         inx
         cpx #$13
         bne rdloop
         jsr iFFCF
         cmp #$2c
         beq rdcomm
         lda #$2a
         sta x07B7         ;*
         bne *-12
rdcomm   sta x07A5,x
         inx
         ldy #$05
         jsr iFFCF
         sta x07A5,x
         inx
         dey
         bne *-8
         jsr iFFCF
         jsr iFFCC
         lda #$01
         jsr iFFC3
         set35
         rts

m_dirr   set37
         lda #$01
         ldx #$08
         ldy #$00
         jsr iFFBA
         lda e_orad
         ldx #LO(filnam)
         ldy #HI(filnam)
         jsr iFFBD
         jsr iFFC0         ;open
         bcc *+5
         jmp derror
         jsr iE544
#ifdef c64
         lda #$15
         sta xD018
#endif
#ifdef p4
         lda #$c4
         sta xFF12
         lda #$d1
         sta xFF13
#endif
         lda #$00
         sta xD021
         ldx #$01
         jsr iFFC6         ;chkin
         jsr iFFCF         ;load addr
         jsr iFFCF
m_newl   lda #$06
         sta xD3
         jsr iFFCF
         ldx st
         bmi m_endd
         bne m_derr
         jsr iFFCF
         beq m_endd
         jsr iFFCF         ;blocks
         ldx st
         bmi m_endd
         bne m_derr
         tax
         jsr iFFCF
         jsr iBDCD         ;out
         lda #$20
         jsr iFFD2
m_line   jsr iFFCF
         beq m_lend
         ldx st
         bmi m_endd
         bne m_derr
         jsr iFFD2
         jmp m_line
m_lend   lda #$0d
         jsr iFFD2
         lda x028D
         and #$04
         bne *-5
         lda xCB
         cmp #$3f
         bne m_newl
         jmp m_endd

m_derr   jsr iFFCC
         lda #$01
         jsr iFFC3
         lda #$01
         ldx #$08
         ldy #$0f
         jsr iFFBA
         lda #$00
         tax
         tay
         jsr iFFBD
         jsr iFFC0
         ldx #$01
         jsr iFFC6
         lda #$0d
         jsr iFFD2
         jsr iFFD2
         lda #$06
         sta xD3
         jsr iFFCF
         jsr iFFD2
         cmp #$0d
         bne *-8

m_endd   jsr iFFCC         ;clrch
         lda #$01
         jsr iFFC3         ;close
         jsr getkey
#ifdef c64
         lda #$0b
#endif
#ifdef p4
         lda #$11
#endif
         sta xD021
         jsr iE544

scn_ed   sei
#ifdef c64
         lda #$13
         sta xD018
#endif
#ifdef p4
         lda #$c0
         sta xFF12
         lda #$f8
         sta xFF13
#endif
         set34
         ldx #$00
loop05   lda xE000,x
         sta x0400,x
         lda xE100,x
         sta x0500,x
         lda xE200,x
         sta x0600,x
         lda xE300,x
         sta x0700,x
         inx
         bne loop05
#ifdef c64
         set35
#endif
         ldx e_trx
         bne *+5
         lda #$18
         .byte $2c
         lda #$7a
         sta x0430
         ldx e_trx+7
         bne *+5
         lda #$18
         .byte $2c
         lda #$7a
         sta x0439
         ldx e_trx+$0e
         bne *+5
         lda #$18
         .byte $2c
         lda #$7a
         sta x0442
         lda e_tr1p
         sta zp9
         jsr tr1out
         lda e_tr2p
         sta zp9
         jsr tr2out
         lda e_tr3p
         sta zp9
         jsr tr3out
         lda #$00
         sta zp9
         jsr sctout
         jsr sctlen
         lda e_gldp
         sta zp9
         jsr gldtab
         jsr startw
         lda #irqc
         sta xD019
         cli
         rts

scn_sd   sei
         set34
         ldx #$00
loop06   lda xE400,x
         sta x0400,x
         lda xE500,x
         sta x0500,x
         lda xE600,x
         sta x0600,x
         lda xE700,x
         sta x0700,x
         inx
         bne loop06
#ifdef c64
         set35
#endif
         lda #irqc
         sta xD019
         cli
         rts

m_dcom   jsr m_nent
         cpx #$00
         bne *+3
         rts
         lda filnam
         cmp #$24
         bne m_dcmd
         stx e_orad
         jmp m_dirr
m_dcmd   txa
         pha
         set37
         lda #$01
         ldx #$08
         ldy #$0f
         jsr iFFBA
         pla
         ldx #LO(filnam)
         ldy #HI(filnam)
         jsr iFFBD
         jsr iFFC0
         LDA st
         BMI i39D9
         JMP i37E1
i39D9    JSR iFFCC
         LDA #$01
         JSR iFFC3
         JMP i37C2

d_edit   ldy #$00
         ldx e_tune
         lda start1,x
         sta e_tr1p
         sta zp9
         jsr tr1out
         lda start2,x
         sta e_tr2p
         sta zp9
         jsr tr2out
         lda start3,x
         sta e_tr3p
         sta zp9
         jsr tr3out
         lda #$00
         sta zp9
         jsr sctout
         jsr sctlen
         lda e_gldp
         sta zp9
         jsr gldtab
         jsr startw
d_loop   jsr colgld
         ldx x_line,y
         lda #hilite
         sta xDADD,x
         sta xDADE,x
         sta xDADF,x
         sta xDAE0,x
         sta xDAE1,x
         sta xDAE2,x
         sta xDAE3,x
         sta xDAE4,x
         sta xDAE5,x
d_newc   jsr getkey
         cmp #$0d
         bne d_down
         jsr f3_key
         tya
         pha
         bne *+8
         jsr m_load
         jmp d_jend
         cpy #$01
         bne *+8
         jsr m_svdt
         jmp d_jend
         cpy #$02
         bne d1
         jmp d_jend
d1       jsr m_dcom
d_jend   pla
         tay
         jmp d_edit+2
d_down   cmp #$11
         bne d_home
         cpy #$03
         beq d_newc
         iny
         jmp d_loop
d_home   cmp #$13
         bne d_uppp
         ldy #$00
         jmp d_loop
d_uppp   cmp #$91
         bne d_gsnd
         tya
         beq d_newc
         dey
         jmp d_loop
d_gsnd   cmp #$21          ;exit
         bcc d_newc
         cmp #$28
         bcs d_scrn
         and #$07
         tay
         jmp colgld
d_scrn   cmp #$5f          ;to editor
         bne d_tr1x
         ldy #$00
         jmp colgld
d_tr1x   jsr keychk
         bne *+5
         jmp d_newc
         jmp d_edit+2

irq      pha
         txa
         pha
         tya
         pha
         cld
         jmp ($0314)

iEA31    lda #$01
         sta scnstrob
iEA81    pla
         tay
         pla
         tax
         pla
nmi      rti

scnkey   st01
         set37
         jsr iEA87
#ifdef p4                       ;shows, how to remap the F-keys and <-- key
                                ;in a quick and dirty way ;-)
                                ;($055f... must be initialized first)
         lda xC6
         bne _r1                ;there was a keypress (not f-key)
         lda $055d              ;f-key strobe
         beq _re                ;none. end.
         clc
         adc #$84               ;C-64 F keys keyboard buffer code
         sta x0277
         lda #0
         sta $055d              ;f-key served.
         inc xC6                ;valid key found!!!
         bne _re

_r1      lda x0277
         cmp #$1b
         bne _re
         lda #$5f               ;ESC <---> <-- done.
         sta x0277
_re
#endif
         rst01
         rts

m_entp   jsr iFF81
         sei
         set35
         ldx #$ff
         txs
         cld
#ifdef p4                       ;init f-keys
         ldx #$3f
         lda #$20
_i1      sta $0567,x
         dex
         bpl _i1
         ldx #$01
         stx $055f+0
         inx
         stx $055f+1
         inx
         stx $055f+2
         inx
         stx $055f+7
         inx
         stx $055f+3
         inx
         stx $055f+4
         inx
         stx $055f+5
         inx
         stx $055f+6
         lda #0                 ;PuCrunch uses this location; must
         sta $f9                ;be cleared before any I/O
#endif
         lda #LO(callno)
         sta x0314
         lda #HI(callno)
         sta x0315
#ifdef c64
         lda #LO(nmi)
         sta xFFFA
         sta x0318
         lda #HI(nmi)
         sta xFFFB
         sta x0319
#endif
         lda #LO(irq)
         sta xFFFE
         lda #HI(irq)
         sta xFFFF
         set37
#ifdef c64
         lda #$7f
         sta xDC0D
         lda #$01
         sta xD01A
#endif
#ifdef p4
         lda #$02
         sta xFF0A
         lda #$01
#endif
         sta x0289
         lda #$80
         sta x028A
         sta x0291
         lda #$1b
         sta xD011
         lda #elso_r
         sta xD012
         lda #$00
         sta xD020
         jsr iFF90
#ifdef c64
         lda #$0b
#endif
#ifdef p4
         lda #$11
#endif
         sta xD021
         lda #colr
         sta x0286
#ifdef p4
         ldx #$d0               ;Sum timing; the routine waits for a border
in1      cpx $ff1d              ;scanline (---> no bad line), delays, then
         bne in1                ;sets timer for exactly 57 cycles (--> one
         inx                    ;line time). The raster routine can then
in2      cpx $ff1d              ;check if the beam is at the right position
         bne in2                ;when changing the border color (in order to
         ldx #$12               ;do it without flickering      (H.L.)
in3      dex
         bne in3
         lda #57
         sta tmr0
         lda #0
         sta tmr0+1
#endif
#ifdef c64
         lda #$00
         sta $dc0e
         ldx #$fe               ;Same applies to the C64 routine...
in1      cpx xD012
         bne in1
         inx
in2      cpx xD012
         bne in2
         ldx #$08               ;Value fixed on C64
in3      dex
         bne in3
         nop
         nop
         lda #63-1              ;63 cycles
         sta tmr0
         lda #0
         sta tmr0+1
         lda #$91
         sta $dc0e
#endif
         jsr iE544

         jsr scn_ed
         jsr t1edit
looped   cpy #$00
         beq loopsd-6
         cpy #$01
         bne *+5
         jsr t1edit
         cpy #$02
         bne *+5
         jsr t2edit
         cpy #$03
         bne *+5
         jsr t3edit
         cpy #$04
         bne *+5
         jsr s_edit
         cpy #$05
         bne *+5
         jsr g_edit
         cpy #$06
         bne *+5
         jsr d_edit
         cpy #$07
         bne looped
         jsr q_edit
         jmp looped

         jsr scn_sd
         jsr i_edit
loopsd   cpy #$00
         beq looped-6
         cpy #$01
         bne *+5
         jsr i_edit
         cpy #$02
         bne *+14
         lda #$07
         ldx #$08
         ldy #$00
         jsr msgset
         jsr w_edit
         cpy #$03
         bne *+14
         lda #$09
         ldx #$0b
         ldy #$0c
         jsr msgset
         jsr f_edit
         cpy #$04
         bne *+14
         lda #$09
         ldx #$0e
         ldy #$0d
         jsr msgset
         jsr p_edit
         cpy #$05
         bne *+14
         lda #$0b
         ldx #$0a
         ldy #$00
         jsr msgset
         jsr g_edit
         cpy #$06
         bne *+14
         lda #$09
         ldx #$0b
         ldy #$0a
         jsr msgset
         jsr v_edit
         cpy #$07
         bne loopsd
         lda #$0f
         ldx #$10
         ldy #$11
         jsr msgset
         jsr r_edit
         jmp loopsd

msgset   sta e_msg1
         stx e_msg2
         sty e_msg3
         rts

;--------------end of ed3

;edit by H.L.  ($56f8...*+7 --> snd_tmp)
snd_tmp  .byte 0,0,0,0,0,0,0

len_lo   .byte $00
len_hi   .byte $00
actdur   .byte $00
e_tune   .byte $00         ;tune#
e_acts   .byte $00         ;speed
e_sctn   .byte $00         ;sct.#
e_ltrk   .byte $01         ;last trk
e_octv   .byte $00         ;octave
e_tr1p   .byte $00         ;trk.pos
e_tr2p   .byte $00
e_tr3p   .byte $00
e_msg1   .byte $00         ;message
e_msg2   .byte $00
e_msg3   .byte $00
e_gldp   .byte $00         ;gld.pos
e_sndn   .byte $00         ;snd.#
e_spos   .byte $00         ;sretpos
e_test   .byte $00         ;t.note
e_radd   .byte $00
e_ract   .byte $00
e_rmax   .byte $00
e_clkt   .byte $00         ;timing
e_secs   .byte $00         ;clock sec
e_mins   .byte $00         ;clock min
e_orad   .byte $00         ;ora-reg
e_rlast  .byte 0
e_strob  .byte 0
scnstrob .byte 0
f2sig    .byte 0           ;signs if play sector mode is active
f4sig    .byte 0           ;signs if liveplay mode is active

e_trx    .byte $ff,0,0,0,0,0,0          ;trk on/off; must be like the
         .byte $ff,0,0,0,0,0,0          ;order of sid-regs...
         .byte $ff,0,0,0,0,0,0          ;

call_pl  .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
call_ph  .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0

call_add  .byte 0,156,104,78,62,52,45,39,35,31,28,26,26,26,26,26
          .byte 0,156,104,78,62,52,45,39,35,31,28,26,24,22,20,19

fncadl   .byte LO(fnctxt+$00),LO(fnctxt+$12)
         .byte LO(fnctxt+$24),LO(fnctxt+$36)
         .byte LO(fnctxt+$48),LO(fnctxt+$5a)
         .byte LO(fnctxt+$6c),LO(fnctxt+$7e)
         .byte LO(fnctxt+$90),LO(fnctxt+$a2)
         .byte LO(fnctxt+$b4),LO(fnctxt+$c6)
         .byte LO(fnctxt+$d8),LO(fnctxt+$ea)
         .byte LO(fnctxt+$fc),LO(fnctxt+$0e)
         .byte LO(fnctxt+$0120),LO(fnctxt+$0132)

fncadh   .byte HI(fnctxt+$00),HI(fnctxt+$12)
         .byte HI(fnctxt+$24),HI(fnctxt+$36)
         .byte HI(fnctxt+$48),HI(fnctxt+$5a)
         .byte HI(fnctxt+$6c),HI(fnctxt+$7e)
         .byte HI(fnctxt+$90),HI(fnctxt+$a2)
         .byte HI(fnctxt+$b4),HI(fnctxt+$c6)
         .byte HI(fnctxt+$d8),HI(fnctxt+$ea)
         .byte HI(fnctxt+$fc),HI(fnctxt+$010e)
         .byte HI(fnctxt+$0120),HI(fnctxt+$0132)


dummy_s  .byte $c0,$bf,$5f,$5f,$5f,$7f            ;Dummy sector, sfx mode
d_sctad  .byte LO(dummy_s),HI(dummy_s)            ;and address for the above

ttrack   .byte $00,$80,$ff,$01                    ;The same, track

x_line   .byte $00,$28,$50,$78
         .byte $a0,$c8,$00,$00
octave   .byte $00,$0c,$18,$24
         .byte $30,$3c,$48,$54
twelve   .byte $43,$2d,$43,$23,$44,$2d  ;"C-C#D-D#E-F-F#G-G#A-A#B-"
         .byte $44,$23,$45,$2d,$46,$2d
         .byte $46,$23,$47,$2d,$47,$23
         .byte $41,$2d,$41,$23,$42,$2d

sc_snd   .byte $53, $0E, $04, $2E, $20, $20  ;"Snd.  "
sc_dur   .byte $44, $15, $12, $2E, $20, $20  ;"Dur.  "
sc_gld   .byte $47, $0C, $04, $2E, $20, $20  ;"Gld.  "
sc_end   .byte $46, $09, $0E, $09, $13, $08  ;"Finish"
sc_hld   .byte $20, $2B, $2B, $2B, $20, $20  ;" +++  "
sc_rst   .byte $2D, $2D, $2D, $2D, $2D, $2D  ;"------"

tr_tup   .byte $54, $12, $2B, $20, $20  ;"Tr+  "
tr_tdn   .byte $54, $12, $2D, $20, $20  ;"Tr-  "
tr_sct   .byte $2E, $2E, $2E, $20, $20  ;"...  "
tr_vol   .byte $56, $0F, $0C, $20, $20  ;"Vol  "
tr_hlt   .byte $48, $0C, $14, $56, $53  ;"HltVS"
tr_dec   .byte $44, $05, $03, $20, $20  ;"Dec  "
tr_inc   .byte $49, $0E, $03, $20, $20  ;"Inc  "
tr_jmp   .byte $4A, $0D, $10, $20, $20  ;"Jmp  "

fnctxt   .byte $41,$14,$14,$01,$03,$0b  ;"Attack + Decay    "
         .byte $20,$2b,$20,$44,$05,$03
         .byte $01,$19,$20,$20,$20,$20
         .byte $53,$15,$13,$14,$01,$09  ;"Sustain + Release "
         .byte $0e,$20,$2b,$20,$52,$05
         .byte $0c,$05,$01,$13,$05,$20
         .byte $47,$01,$14,$05,$20,$0f  ;"Gate off counter  "
         .byte $06,$06,$20,$03,$0f,$15
         .byte $0e,$14,$05,$12,$20,$20
         .byte $41,$12,$10,$05,$07,$07  ;"Arpeggio pointer  "
         .byte $09,$0f,$20,$10,$0f,$09
         .byte $0e,$14,$05,$12,$20,$20
         .byte $46,$09,$0c,$14,$05,$12  ;"Filter pointer    "
         .byte $20,$10,$0f,$09,$0e,$14
         .byte $05,$12,$20,$20,$20,$20
         .byte $50,$15,$0c,$13,$05,$20  ;"Pulse pointer     "
         .byte $10,$0f,$09,$0e,$14,$05
         .byte $12,$20,$20,$20,$20,$20
         .byte $53,$0c,$09,$04,$05,$20  ;"Slide pointer     "
         .byte $10,$0f,$09,$0e,$14,$05
         .byte $12,$20,$20,$20,$20,$20
         .byte $57,$01,$16,$05,$06,$0f  ;"Waveform / Command"
         .byte $12,$0d,$20,$2f,$20,$43
         .byte $0f,$0d,$0d,$01,$0e,$04
         .byte $41,$12,$10,$05,$07,$07  ;"Arpeggio offset   "
         .byte $09,$0f,$20,$0f,$06,$06
         .byte $13,$05,$14,$20,$20,$20
         .byte $52,$05,$10,$05,$01,$14  ;"Repeat / Command  "
         .byte $20,$2f,$20,$43,$0f,$0d
         .byte $0d,$01,$0e,$04,$20,$20
         .byte $46,$12,$05,$11,$15,$05  ;"Frequency low     "
         .byte $0e,$03,$19,$20,$0c,$0f
         .byte $17,$20,$20,$20,$20,$20
         .byte $46,$12,$05,$11,$15,$05  ;"Frequency high    "
         .byte $0e,$03,$19,$20,$08,$09
         .byte $07,$08,$20,$20,$20,$20
         .byte $52,$05,$13,$0f,$0e,$01  ;"Resonance + F.low "
         .byte $0e,$03,$05,$20,$2b,$20
         .byte $46,$2e,$0c,$0f,$17,$20
         .byte $50,$15,$0c,$13,$05,$20  ;"Pulse width low   "
         .byte $17,$09,$04,$14,$08,$20
         .byte $0c,$0f,$17,$20,$20,$20
         .byte $50,$15,$0c,$13,$05,$20  ;"Pulse width high  "
         .byte $17,$09,$04,$14,$08,$20
         .byte $08,$09,$07,$08,$20,$20
         .byte $54,$12,$01,$03,$0b,$20  ;"Track 1 startpos. "
         .byte $31,$20,$13,$14,$01,$12
         .byte $14,$10,$0f,$13,$2e,$20
         .byte $54,$12,$01,$03,$0b,$20  ;"Track 2 startpos. "
         .byte $32,$20,$13,$14,$01,$12
         .byte $14,$10,$0f,$13,$2e,$20
         .byte $54,$12,$01,$03,$0b,$20  ;"Track 3 startpos. "
         .byte $33,$20,$13,$14,$01,$12
         .byte $14,$10,$0f,$13,$2e,$20

filnam   .text "            "
         .text "            "
         .text " "
msg_ld   .byte $50,$0c,$05,$01,$13,$05  ;"Please wait,"
         .byte $20,$17,$01,$09,$14,$2c
         .byte $20,$0c,$0f,$01,$04,$09  ;" loading...  "
         .byte $0e,$07,$2e,$2e,$2e,$20
         .byte $20
msg_sv   .byte $50,$0c,$05,$01,$13,$05  ;"Please wait,"
         .byte $20,$17,$01,$09,$14,$2c
         .byte $20,$13,$01,$16,$09,$0e  ;" saving...   "
         .byte $07,$2e,$2e,$2e,$20,$20
         .byte $20
msg_np   .byte $44,$05,$16,$09,$03,$05  ;"Device 8 not"
         .byte $20,$38,$20,$0e,$0f,$14
         .byte $20,$10,$12,$05,$13,$05  ;" present     "
         .byte $0e,$14,$20,$20,$20,$20
         .byte $20
msg_pl   .byte $49,$0e,$03,$0f,$0d,$10  ;"Incompatible"
         .byte $01,$14,$09,$02,$0c,$05
         .byte $20,$10,$0c,$01,$19,$05  ;" player      "
         .byte $12,$20,$20,$20,$20,$20
         .byte $20

;---------------------------------------

         *=$5800
#include player.asm

.end
