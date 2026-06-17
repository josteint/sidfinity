;-  SIDwinder packer + relocator
;   V01.23
;
;   This program packs songs created in SIDwinder editor V01.2x
;   and produces 'executable' sound files by linking the sound datas
;   together with the SIDwinder player routine (V01.23).
;
;   Released on 2000.03.15
;
;   (C) 2000        Levente H rsfalvi    ( Levente@terrasoft.hu )
;
;   Portions (I/O routines)
;   (C) 1994-1999   Bal zs Tak cs        ( Takinb@sch.bme.hu )
;
;
;   The source supports compiling to both C-64 and Plus/4 (or C-16/60K).
;
;   Features include:
;   V01.23:
;
;   - 'Full' sound file parsing for used/unused areas (then eliminating
;     all unnecessary data to shorten packed file)
;   - File relocation to selectable start address
;   - Selectable SID chip base address
;   - Selectable used zeropage word (used by player)
;   - Selectable frequency table (C64 or Plus/4 SID, 985Khz or 885Khz based)
;   - Maybe needless to say - the packer now loads the data file format of
;     SIDwinder (instead of the 'memory image')
;
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
;   - player.asm           SIDwinder player source file
;
;   The source can be compiled to run both on C-64 and Plus/4.
;   (Just define c64 or p4 with the TASM -d option in the command line)
;
;   Link with -thx option
;


#define packer

#define LO(x) (x&$ff)
#define HI(x) (x>>8)

#ifndef p4
#define c64
#endif

#define sid $d400          ;Let the packer use $d400 whether compiled
                           ;to +4

;system specific definitions
#ifdef c64
#define set37 lda #$37 \ sta x01
#define set35 lda #$35 \ sta x01

;         *= $0810
         *= $080e
         .word *+2

#define tracks $e000
#define sectors $7000

#define screen $0400
#define vic $d000
#define color $d800

#define colr $0f

sector_l   =$6000
tracks_l   =$1800

zp1      = $2b
zp2      = $2c
zp3      = $2d
zp4      = $2e
zp5      = $2f
zp6      = $30
zp7      = $31
zp8      = $32
zp9      = $33
zp10     = $34
zp11     = $35
zp12     = $36
zp13     = $37
zp14     = $38
zp15     = $39
zp16     = $3a
loadcnt  = $3b

x01        =$01
xCB        =$CB
xD3        =$D3
x0277      =$0277
x0286      =$0286
x028D      =$028D
x0291      =$0291


xD011      =vic+$11
xD020      =vic+$20
xD021      =vic+$21

iBDCD      =$BDCD
iE544      =$E544
iFCE2      =$fce2

#endif

#ifdef p4
#define set37 sta $ff3e
#define set35 sta $ff3f

#define tracks $e000
#define sectors $7000

;         *= $1010
         *= $100E
         .word *+2

#define screen $0c00
#define color $0800

#define colr $51

sector_l   =$6000
tracks_l   =$1800

zp1      = $d0
zp2      = $d1
zp3      = $d2
zp4      = $d3
zp5      = $d4
zp6      = $d5
zp7      = $d6
zp8      = $d7
zp9      = $d8
zp10     = $d9
zp11     = $da
zp12     = $db
zp13     = $dc
zp14     = $dd
zp15     = $de
zp16     = $df

loadcnt  = $e5


xCB        =$C6
xD3        =$ca
x0277      =$0527
x0286      =$053b
x0543      =$0543
x028D      =$0543
x0291      =$0547

xD011      =$ff06
xD020      =$ff19
xD021      =$ff15
xFF08      =$ff08

iBDCD      =$a45f
iE544      =$d888
iFCE2      =$fff6
#endif


;system independent definitions

sptr       =$fc
st         =$90

iFF81      =$FF81
iFFBA      =$FFBA
iFFBD      =$FFBD
iFFC0      =$FFC0
iFFC3      =$FFC3
iFFC6      =$FFC6
iFFC9      =$FFC9
iFFCC      =$FFCC
iFFCF      =$FFCF
iFFD2      =$FFD2


         jsr iFF81
         lda #$1b
         sta xD011
         lda #$00
         sta xD020
         sta xD021
         lda #$80
         sta x0291
         lda #colr
         sta x0286
         lda #14           ;Small/capital set
         jsr iFFD2


         lda #0            ;clear everything
#ifdef p4
         sta $f9           ;Fix PuCrunch's fault...
#endif
         tax
l1       sta wve_wf,x
         sta wve_st,x
         sta flt_rp,x
         sta flt_fh,x
         sta flt_rl,x
         sta pls_rp,x
         sta pls_pl,x
         sta pls_ph,x
         sta sld_rp,x
         sta sld_fl,x
         sta sld_fh,x
         sta wveuse,x
         sta fltuse,x
         sta plsuse,x
         sta slduse,x
         inx
         bne l1
         ldx #$3f
l2       sta snduse,x
         sta snd_ad,x
         sta snd_sr,x
         sta snd_gt,x
         sta snd_wt,x
         sta snd_ft,x
         sta snd_pt,x
         sta snd_st,x
         sta gld_al,x
         dex
         bpl l2
         ldx #$5f
l4       sta tr1use,x
         sta start1,x
         sta tr1adl,x
         dex
         bpl l4
         ldx #$1f
l5       sta glduse,x
         dex
         bpl l5
         ldx #(HI(sector_l)-1)
l6       sta sctuse,x
         dex
         bpl l6
         lda #LO(tracks)
         sta zp1
         lda #HI(tracks)
         sta zp2
         ldy #0
         lda #$80
l3       sta (zp1),y
         iny
         bne l3
         inc zp2
         lda zp2
         cmp #HI(tracks+tracks_l)
         bne l3-2
         lda #LO(sectors)
         sta zp1
         lda #HI(sectors)
         sta zp2
         lda #$5f
l7       sta (zp1),y
         iny
         bne l7
         inc zp2
         ldx zp2
         cpx #HI(sectors+sector_l)
         bne l7

         jsr iE544
         jsr primm

;               0123456789012345678901234567890123456789
         .text "   ***   SIDwinder packer V01.23   ***"
         .byte 13
         .text "        ( For SIDwinder V01.2x  )"
         .byte 13,13
         .text "     (C) 2000 by Levente Harsfalvi"
         .byte 13
         .text "           (TLC of Coroners)"
         .byte 13
         .text " Released together with the V01.23 pack"
         .byte 13,13,0
         jsr primm
         .text "This program is free software (GPL). For"
         .text "further details, please refer to the"
         .byte 13
         .text "documentation file."
         .byte 13,13,13,0

fn       jsr primm
         .text "Enter filename (or $): "
         .byte 0
         jsr input
         lda #13
         jsr iFFD2
         lda ibufl
         beq fn
         ldy ibufl
         dey
         cpy #15
         bcc *+4
         ldy #15
         sty zp3
_bel     lda ibuf,y
         sta filnam,y
         dey
         bpl _bel

         inc zp3           ;Filename length
         lda filnam
         cmp #'$'
         bne fn2
         lda #13
         jsr iFFD2
         jsr m_dirr
         jmp fn

fn2      jsr primm
         .byte 13
         .text "Please wait, loading..."
         .byte 13,13,0

         jsr m_load
         bcs fn
;               0123456789012345678901234567890123456789

         jsr primm
         .byte 13
         .text "Below please enter hex numbers without"
         .byte 13
         .text "prefix!"
         .byte 13,0

ns1      jsr primm
         .byte 13
         .text "Number of subsongs (01-20): "
         .byte 0
         jsr inputh
         bcs ns1
         cpy #0
         bne ns1
         cpx #$21
         bcs ns1
         stx subsongs
         stx m_init+1

ns2      jsr primm
         .byte 13
         .text "Start address in memory: "
         .byte 0
         jsr inputh
         bcs ns2
         stx start
         sty start+1
         txa
         sec
         sbc #LO(pstart)
         sta reloc
         tya
         sbc #HI(pstart)
         sta reloc+1

ns7      jsr primm
         .byte 13
         .text "Reserved zeropage word for the player"
         .byte 13
         .byte "(if in doubt enter fb): "
         .byte 0
         jsr inputh
         bcs ns7
         txa
         sec
         sbc #pt
         sta zreloc

ns3      jsr primm
         .byte 13
         .text "SID baseaddress (d400, fd40 etc.): "
         .byte 0
         jsr inputh
         bcs ns3
         txa
         sec
         sbc #LO(sid)
         sta sreloc
         tya
         sbc #HI(sid)
         sta sreloc+1

ns4      jsr primm
         .byte 13
         .text "(C)64 or (P)lus/4 freq table? "
         .byte 0
         jsr input
         lda ibufl
         beq ns4
         lda ibuf
#ifdef c64
         cmp #'P'
#endif
#ifdef p4
         cmp #'C'
#endif
         bne ns6
         ldx #0
ns5      lda freqtab,x
         sta freqhi,x
         inx
         cpx #$c0
         bne ns5

ns6      jsr primm
         .byte 13,13
         .text "Enter your identity field (32 chars)!"
         .byte 13
         .text "Pos -- 12345678901234567890123456789012"
         .byte 13
         .text "Field: "
         .byte 0
         jsr input
         ldy #31
         lda #$20
_ihx     sta pstart+$20,y
         dey
         bpl _ihx
         ldy ibufl
         dey
         cpy #32
         bcc _bex
         ldy #31
_bex     lda ibuf,y        ;Petscii to screencode conv on the fly
         cmp #$c0          ;Capitals
         bcc _sci1
         and #$7f
         bcs _sci2
_sci1    cmp #$41
         bcc _sci2
         and #$3f
_sci2    sta pstart+$20,y
         dey
         bpl _bex


         jsr primm
         .byte 13,13
         .text "Packing, please be patient..."
         .byte 13,13,0

         sei
         set35
         jsr prusetb       ;prepare usage tables
         jsr trax          ;eliminate all start pointers, sort track tables
                           ;and index them into ascending order, calculate
                           ;length of track tables
         jsr collsct       ;Collect used sectors (sectorlengths) into sctuse
                           ;+ collect info on snd/gld use
         jsr packsct       ;...then pack sectors into one block
         jsr packscta      ;and also, their start pointers...
         jsr packgld       ;now pack the glide table and update commands
         jsr packsnd       ;pack sndtable

         jsr collwt        ;Collect used arpeggio table elements
         jsr packwt

         jsr collft        ;Collect used filter table elements
         jsr packft

         jsr collpt        ;Collect used pulse table elements
         jsr packpt

         jsr collst        ;Collect used slide/vib table elements
         jsr packst
                           ;...Now link the whole thing together

         lda #LO(dstart)   ;Initials...
         sta zp1
         sta tmpsta        ;Store the track pointer table start temporarily
         lda #HI(dstart)
         sta zp2
         sta tmpsta+1

                           ;First tr1adl+tr1adh
         lda zp1
         clc
         adc reloc
         sta tr1adl1
         lda zp2
         adc reloc+1
         sta tr1adl1+1
         lda subsongs
         ldx #LO(tr1adl)
         ldy #HI(tr1adl)
         jsr copy

         lda zp1
         clc
         adc reloc
         sta tr2adl1
         lda zp2
         adc reloc+1
         sta tr2adl1+1
         lda subsongs
         ldx #LO(tr2adl)
         ldy #HI(tr2adl)
         jsr copy

         lda zp1
         clc
         adc reloc
         sta tr3adl1
         lda zp2
         adc reloc+1
         sta tr3adl1+1
         lda subsongs
         ldx #LO(tr3adl)
         ldy #HI(tr3adl)
         jsr copy

         lda zp1
         clc
         adc reloc
         sta tr1adh1
         lda zp2
         adc reloc+1
         sta tr1adh1+1
         lda subsongs
         ldx #LO(tr1adh)
         ldy #HI(tr1adh)
         jsr copy

         lda zp1
         clc
         adc reloc
         sta tr2adh1
         lda zp2
         adc reloc+1
         sta tr2adh1+1
         lda subsongs
         ldx #LO(tr2adh)
         ldy #HI(tr2adh)
         jsr copy

         lda zp1
         clc
         adc reloc
         sta tr3adh1
         lda zp2
         adc reloc+1
         sta tr3adh1+1
         lda subsongs
         ldx #LO(tr3adh)
         ldy #HI(tr3adh)
         jsr copy

                           ;trxadx completed... addresses still need fixing
         lda zp1
         sta tmpscta
         lda zp2
         sta tmpscta+1     ;store sct pointer table start address

         lda zp1           ;Now sctadl
         clc
         adc reloc
         sta sctadl1
         lda zp2
         adc reloc+1
         sta sctadl1+1
         lda sctalen
         ldx #LO(sctadl)
         ldy #HI(sctadl)
         jsr copy

         lda zp1
         clc
         adc reloc
         sta sctadh1
         lda zp2
         adc reloc+1
         sta sctadh1+1
         lda sctalen
         ldx #LO(sctadh)
         ldy #HI(sctadh)
         jsr copy

         dec reloc
         lda reloc
         cmp #$ff
         bne foo1
         dec reloc+1
foo1
         lda zp1           ;Copy glide tables...
         clc
         adc reloc
         sta gld_al1
         sta gld_al2
         lda zp2
         adc reloc+1
         sta gld_al1+1
         sta gld_al2+1
         lda gldlen
         ldx #LO(gld_al)
         ldy #HI(gld_al)
         jsr copy

         lda zp1
         clc
         adc reloc
         sta gld_ah1
         sta gld_ah2
         lda zp2
         adc reloc+1
         sta gld_ah1+1
         sta gld_ah2+1
         lda gldlen
         ldx #LO(gld_ah)
         ldy #HI(gld_ah)
         jsr copy

         inc reloc
         bne foo2
         inc reloc+1
foo2
         lda zp1           ;Snd_ad
         clc
         adc reloc
         sta snd_ad1
         lda zp2
         adc reloc+1
         sta snd_ad1+1
         lda sndlen
         ldx #LO(snd_ad)
         ldy #HI(snd_ad)
         jsr copy

         lda zp1           ;Snd_sr
         clc
         adc reloc
         sta snd_sr1
         lda zp2
         adc reloc+1
         sta snd_sr1+1
         lda sndlen
         ldx #LO(snd_sr)
         ldy #HI(snd_sr)
         jsr copy

         lda zp1           ;Snd_gt
         clc
         adc reloc
         sta snd_gt1
         lda zp2
         adc reloc+1
         sta snd_gt1+1
         lda sndlen
         ldx #LO(snd_gt)
         ldy #HI(snd_gt)
         jsr copy

         lda zp1           ;Snd_wt
         clc
         adc reloc
         sta snd_wt1
         lda zp2
         adc reloc+1
         sta snd_wt1+1
         lda sndlen
         ldx #LO(snd_wt)
         ldy #HI(snd_wt)
         jsr copy

         lda zp1           ;Snd_ft
         clc
         adc reloc
         sta snd_ft1
         lda zp2
         adc reloc+1
         sta snd_ft1+1
         lda sndlen
         ldx #LO(snd_ft)
         ldy #HI(snd_ft)
         jsr copy

         lda zp1           ;Snd_pt
         clc
         adc reloc
         sta snd_pt1
         lda zp2
         adc reloc+1
         sta snd_pt1+1
         lda sndlen
         ldx #LO(snd_pt)
         ldy #HI(snd_pt)
         jsr copy

         lda zp1           ;Snd_st
         clc
         adc reloc
         sta snd_st1
         lda zp2
         adc reloc+1
         sta snd_st1+1
         lda sndlen
         ldx #LO(snd_st)
         ldy #HI(snd_st)
         jsr copy

         lda zp1           ;wve_wf
         clc
         adc reloc
         sta wve_wf1
         sta wve_wf2
         lda zp2
         adc reloc+1
         sta wve_wf1+1
         sta wve_wf2+1
         lda wvelen
         ldx #LO(wve_wf)
         ldy #HI(wve_wf)
         jsr copy

         lda zp1           ;wve_st
         clc
         adc reloc
         sta wve_st1
         sta wve_st2
         lda zp2
         adc reloc+1
         sta wve_st1+1
         sta wve_st2+1
         lda wvelen
         ldx #LO(wve_st)
         ldy #HI(wve_st)
         jsr copy

         lda zp1           ;flt_rp
         clc
         adc reloc
         sta flt_rp1
         sta flt_rp2
         sta flt_rp3
         lda zp2
         adc reloc+1
         sta flt_rp1+1
         sta flt_rp2+1
         sta flt_rp3+1
         lda fltlen
         ldx #LO(flt_rp)
         ldy #HI(flt_rp)
         jsr copy

         lda zp1           ;flt_fh
         clc
         adc reloc
         sta flt_fh1
         sta flt_fh2
         sta flt_fh3
         lda zp2
         adc reloc+1
         sta flt_fh1+1
         sta flt_fh2+1
         sta flt_fh3+1
         lda fltlen
         ldx #LO(flt_fh)
         ldy #HI(flt_fh)
         jsr copy

         lda zp1           ;flt_rl
         clc
         adc reloc
         sta flt_rl1
         lda zp2
         adc reloc+1
         sta flt_rl1+1
         lda fltlen
         ldx #LO(flt_rl)
         ldy #HI(flt_rl)
         jsr copy

         lda zp1           ;pls_rp
         clc
         adc reloc
         sta pls_rp1
         sta pls_rp2
         lda zp2
         adc reloc+1
         sta pls_rp1+1
         sta pls_rp2+1
         lda plslen
         ldx #LO(pls_rp)
         ldy #HI(pls_rp)
         jsr copy

         lda zp1           ;pls_ph
         clc
         adc reloc
         sta pls_ph1
         sta pls_ph2
         lda zp2
         adc reloc+1
         sta pls_ph1+1
         sta pls_ph2+1
         lda plslen
         ldx #LO(pls_ph)
         ldy #HI(pls_ph)
         jsr copy

         lda zp1           ;pls_pl
         clc
         adc reloc
         sta pls_pl1
         lda zp2
         adc reloc+1
         sta pls_pl1+1
         lda plslen
         ldx #LO(pls_pl)
         ldy #HI(pls_pl)
         jsr copy

         lda zp1           ;sld_rp
         clc
         adc reloc
         sta sld_rp1
         sta sld_rp2
         lda zp2
         adc reloc+1
         sta sld_rp1+1
         sta sld_rp2+1
         lda sldlen
         ldx #LO(sld_rp)
         ldy #HI(sld_rp)
         jsr copy

         lda zp1           ;sld_fh
         clc
         adc reloc
         sta sld_fh1
         sta sld_fh2
         sta sld_fh3
         lda zp2
         adc reloc+1
         sta sld_fh1+1
         sta sld_fh2+1
         sta sld_fh3+1
         lda sldlen
         ldx #LO(sld_fh)
         ldy #HI(sld_fh)
         jsr copy

         lda zp1           ;sld_fl
         clc
         adc reloc
         sta sld_fl1
         sta sld_fl2
         lda zp2
         adc reloc+1
         sta sld_fl1+1
         sta sld_fl2+1
         lda sldlen
         ldx #LO(sld_fl)
         ldy #HI(sld_fl)
         jsr copy

                           ;Finished with all tables. Happy.
                           ;Now fix the trax address tables
                           ;pointed by tmpsta
         lda tmpsta
         sta zp3
         sta zp5
         lda tmpsta+1
         sta zp4
         sta zp6
         ldy #2
to3      lda zp5           ;Quick and dirty way to add 3*subsongs to
         clc               ;zp5/zp6
         adc subsongs
         sta zp5
         lda zp6
         adc #0
         sta zp6
         dey
         bpl to3

         lda zp1
         sec
         sbc trstal
         sta zp7
         lda zp2
         sbc trstah
         sta zp8
         lda zp7
         clc
         adc reloc
         sta zp7
         lda zp8
         adc reloc+1
         sta zp8

         ldx #2            ;After calculating, fix the pointers...
trfl     ldy #0
trfl2    lda (zp3),y
         clc
         adc zp7
         sta (zp3),y
         lda (zp5),y
         adc zp8
         sta (zp5),y
         iny
         cpy subsongs
         bne trfl2
         lda subsongs
         clc
         adc zp3
         sta zp3
         lda zp4
         adc #0
         sta zp4
         lda subsongs
         clc
         adc zp5
         sta zp5
         lda zp6
         adc #0
         sta zp6
         dex
         bpl trfl

         lda trendl+2      ;Copy trax tables...
         sec
         sbc trstal
         sta zp5
         lda trendh+2
         sbc trstah
         sta zp6
         ldx trstal
         ldy trstah
         jsr copyl

         lda tmpscta       ;The same with the sectors
         sta zp3
         lda tmpscta+1
         sta zp4
         lda tmpscta
         clc
         adc sctalen
         sta zp5
         lda tmpscta+1
         adc #0
         sta zp6
         lda zp1
         sec
         sbc sctsta
         sta zp7
         lda zp2
         sbc sctsta+1
         sta zp8
         lda zp7
         clc
         adc reloc
         sta zp7
         lda zp8
         adc reloc+1
         sta zp8

         ldy #0            ;Fix them...
scl      lda (zp3),y
         clc
         adc zp7
         sta (zp3),y
         lda (zp5),y
         adc zp8
         sta (zp5),y
         iny
         cpy sctalen
         bne scl

         lda sctend        ;Copy sectorsl
         sec
         sbc sctsta
         sta zp5
         lda sctend+1
         sbc sctsta+1
         sta zp6
         ldx sctsta
         ldy sctsta+1
         jsr copyl
                           ;Huh, done all copying stuff.
                           ;Now relocating the code...
         lda pstart+1      ;First the three jumps right in the start of
         clc               ;the player...
         adc reloc
         sta pstart+1
         lda pstart+2
         adc reloc+1
         sta pstart+2

         lda pstart+4
         clc
         adc reloc
         sta pstart+4
         lda pstart+5
         adc reloc+1
         sta pstart+5

         lda pstart+7
         clc
         adc reloc
         sta pstart+7
         lda pstart+8
         adc reloc+1
         sta pstart+8

         jsr reloc_c       ;...then the rest of the code.

         jsr reloc_s       ;Redirect SID to the new baseaddress

         jsr reloc_z       ;Redirect zeropage address...

         set37
         cli

         jsr primm
         .byte 13
         .text "Done."
         .byte 13,13,0

fns      jsr primm
         .byte 13
         .text "Enter filename: "
         .byte 0
         jsr input
         lda #13
         jsr iFFD2
         lda ibufl
         beq fns
         ldy ibufl
         dey
         cpy #15
         bcc _b2
         ldy #15
_b2      sty zp3           ;temp
_bels    lda ibuf,y
         sta filnam,y
         dey
         bpl _bels
         inc zp3
         ldy zp3
         ldx #0
_fs3     lda suff,x
         sta filnam,y
         inx
         iny
         cpx #4
         bne _fs3
         sty zp3

fns2     jsr m_sav
         bcs fns

         jmp iFCE2         ;Phew, done... 8-$


;----------------- Copy routines

copy     sta zp15          ;store bytes to be copied
         cmp #0
         beq clle
         stx zp3
         sty zp4
         ldy #0
cloop    lda (zp3),y
         sta (zp1),y
         iny
         cpy zp15
         bne cloop
         lda zp1
         clc
         adc zp15
         sta zp1
         lda zp2
         adc #0
         sta zp2
         rts

copyl    stx zp3           ;Copy long blocks
         sty zp4           ;dest in zp1/zp2, src x/y, len zp5/zp6
         ldy #0            ;Updates zp1/zp2
         lda zp5
         ora zp6
         beq clle          ;0 len, exit
         lda zp5
         eor #$ff
         sta zp5
         lda zp6
         eor #$ff
         sta zp6
         lda zp5
         clc
         adc #1
         sta zp5
         lda zp6
         adc #$00
         sta zp6
clloop   lda (zp3),y
         sta (zp1),y
         inc zp1
         bne cl1
         inc zp2
cl1      inc zp3
         bne cl2
         inc zp4
cl2      inc zp5
         bne clloop
         inc zp6
         bne clloop
clle     rts

;---------------------- Relocation -----------------

reloc_c  lda #LO((pstart+$0100))
         sta zp3
         lda #HI((pstart+$0100))
         sta zp4
r1       ldy #0
         lda (zp3),y
         tax
         lda comms,x
         tax
         cmp #3
         bne r_next
rf1      iny
         lda (zp3),y
         sta zp5
         iny
         lda (zp3),y
         sta zp6
         lda zp5
         sec
         sbc #LO(pstart)
         lda zp6
         sbc #HI(pstart)
         bcc r_next
         lda zp5
         sec
         sbc #LO(dstart)
         lda zp6
         sbc #HI(dstart)
         bcs r_next        ;Does it point into the code or the vars?
         dey
         lda zp5
         clc
         adc reloc
         sta (zp3),y
         iny
         lda zp6
         adc reloc+1
         sta (zp3),y

r_next   txa
         clc
         adc zp3
         sta zp3
         lda zp4
         adc #0
         sta zp4
         lda zp3
         cmp #LO(pend)
         bne r1
         lda zp4
         cmp #HI(pend)
         bne r1
         rts

reloc_s  lda #LO((pstart+$0100))        ;SID baseadd fix
         sta zp3
         lda #HI((pstart+$0100))
         sta zp4
rs1      ldy #0
         lda (zp3),y
         tax
         lda comms,x
         tax
         cmp #3
         bne rs_next
rfs1     iny
         lda (zp3),y
         and #$c0
         cmp #LO(sid)
         bne rs_next
         iny
         lda (zp3),y
         cmp #HI(sid)
         bne rs_next
         dey
         lda (zp3),y
         clc
         adc sreloc
         sta (zp3),y
         iny
         lda (zp3),y
         adc sreloc+1
         sta (zp3),y

rs_next  txa
         clc
         adc zp3
         sta zp3
         lda zp4
         adc #0
         sta zp4
         lda zp3
         cmp #LO(pend)
         bne rs1
         lda zp4
         cmp #HI(pend)
         bne rs1
         rts

reloc_z  lda #LO((pstart+$0100))        ;Zeropage word address fix
         sta zp3
         lda #HI((pstart+$0100))
         sta zp4
rz1      ldy #0
         lda (zp3),y
         tax
         lda comms,x
         tax
         cmp #2
         bne rz_next
rfz1     lda (zp3),y
         cmp #$85
         beq rfz3
         cmp #$b1
         bne rz_next
rfz3     iny
         lda (zp3),y
         cmp #pt
         beq rfz2
         cmp #pt+1
         bne rz_next
rfz2     clc
         adc zreloc
         sta (zp3),y

rz_next  txa
         clc
         adc zp3
         sta zp3
         lda zp4
         adc #0
         sta zp4
         lda zp3
         cmp #LO(pend)
         bne rz1
         lda zp4
         cmp #HI(pend)
         bne rz1
         rts


;              0 1 2 3 4 5 6 7 8 9 a b c d e f
comms    .byte 1,2,1,1,1,2,2,1,1,2,1,1,1,3,3,1     ;00
         .byte 2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1     ;10
         .byte 3,2,1,1,2,2,2,1,1,2,1,1,3,3,3,1     ;20
         .byte 2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1     ;30
         .byte 1,2,1,1,1,2,2,1,1,2,1,1,3,3,3,1     ;40
         .byte 2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1     ;50
         .byte 1,2,1,1,1,2,2,1,1,2,1,1,3,3,3,1     ;60
         .byte 2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1     ;70
         .byte 1,2,1,1,2,2,2,1,1,1,1,1,3,3,3,1     ;80

;              0 1 2 3 4 5 6 7 8 9 a b c d e f
         .byte 2,2,1,1,2,2,2,1,1,3,1,1,1,3,1,1     ;90
         .byte 2,2,2,1,2,2,1,1,1,2,1,1,3,3,3,1     ;a0
         .byte 2,2,1,1,2,2,2,1,1,3,1,1,3,3,3,1     ;b0
         .byte 2,2,1,1,2,2,2,1,1,2,1,1,3,3,3,1     ;c0
         .byte 2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1     ;d0
         .byte 2,2,1,1,2,2,2,1,1,2,1,1,3,3,3,1     ;e0
         .byte 2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1     ;f0


;------------------- Scanning + packing

prusetb  ldx #$ff
pr1      lda wve_wf,x
         ora wve_st,x
         bne pr2
         dex               ;Hope nobody wants to try it out on a song
         bne pr1           ;with no waveform settings at all...
pr2      lda #1
         sta wveuse,x

         ldx #$ff
pr3      lda flt_rp,x
         ora flt_fh,x
         ora flt_rl,x
         bne pr4
         dex
         bne pr3
pr4      lda #1
         sta fltuse,x

         ldx #$ff
pr5      lda pls_rp,x
         ora pls_ph,x
         ora pls_pl,x
         bne pr6
         dex
         bne pr5
pr6      lda #1
         sta plsuse,x

         ldx #$ff
pr7      lda sld_rp,x
         ora sld_fh,x
         ora sld_fl,x
         bne pr8
         dex
         bne pr7
pr8      lda #1
         sta plsuse,x
         rts

trax     ldx #$00
pl1      lda tr1adl,x
         clc
         adc start1,x
         sta tr1adl,x
         inx
         cpx #$60
         bne pl1
         lda #$00
         dex
pl2      txa
         and #$1f
         sta tr1id,x
         dex
         bpl pl2
         lda #LO(tr1id)
         sta zp1
         lda #HI(tr1id)
         sta zp2
         lda #LO(tr1adl)
         sta zp3
         lda #HI(tr1adl)
         sta zp4
         lda #LO(tr1adh)
         sta zp5
         lda #HI(tr1adh)
         sta zp6
         jsr sort_trad     ;Let's make an index table on starting addr
         lda #LO(tr1use)
         sta zp7
         lda #HI(tr1use)
         sta zp8
         lda #LO(start1)
         sta zp9
         lda #HI(start1)
         sta zp10
         jsr cl_trl        ;Calculate lengths, update jumps
         lda #0
         sta zp9           ;1st track
         lda #LO(tracks)
         sta trstal
         lda #HI(tracks)
         sta trstah
         jsr packtrk       ;...Then pack the thing and update pointers

         lda #LO(tr2id)
         sta zp1
         lda #HI(tr2id)
         sta zp2
         lda #LO(tr2adl)
         sta zp3
         lda #HI(tr2adl)
         sta zp4
         lda #LO(tr2adh)
         sta zp5
         lda #HI(tr2adh)
         sta zp6
         jsr sort_trad
         lda #LO(tr2use)
         sta zp7
         lda #HI(tr2use)
         sta zp8
         lda #LO(start2)
         sta zp9
         lda #HI(start2)
         sta zp10
         jsr cl_trl        ;Calculate lengths, update jumps
         lda #1
         sta zp9           ;2nd track
         lda trendl
         sta trstal+1
         lda trendh
         sta trstah+1
         jsr packtrk

         lda #LO(tr3id)
         sta zp1
         lda #HI(tr3id)
         sta zp2
         lda #LO(tr3adl)
         sta zp3
         lda #HI(tr3adl)
         sta zp4
         lda #LO(tr3adh)
         sta zp5
         lda #HI(tr3adh)
         sta zp6
         jsr sort_trad
         lda #LO(tr3use)
         sta zp7
         lda #HI(tr3use)
         sta zp8
         lda #LO(start3)
         sta zp9
         lda #HI(start3)
         sta zp10
         jsr cl_trl        ;Calculate lengths, update jumps
         lda #2
         sta zp9           ;3rd track
         lda trendl+1
         sta trstal+2
         lda trendh+1
         sta trstah+2
         jsr packtrk
         rts



sort_trad
         ldy #0            ;I
         sty zp7

stl      ldy zp7           ;trackaddr sorter main loop
         sty zp11          ;supposed minindex
         iny
         sty zp8           ;J
stl2     ldy zp8           ;inner loop
         lda (zp1),y
         tay
         sta zp12
         lda (zp3),y
         sta zp9
         lda (zp5),y
         sta zp10
         ldy zp11
         lda (zp1),y
         tay
         sta zp13
         lda zp12          ;This small code in the middle provides
         sec               ;that whenever two pointers equal, they
         sbc zp13          ;can still be sorted in order
         lda zp9
         sbc (zp3),y
         lda zp10
         sbc (zp5),y
         bcs s_inc
         ldy zp8
         sty zp11          ;gotcha!

s_inc    inc zp8
         lda zp8
         cmp #$20
         bne stl2
         ldy zp11
         lda (zp1),y
         tax
         ldy zp7
         lda (zp1),y
         ldy zp11
         sta (zp1),y
         ldy zp7
         txa
         sta (zp1),y
         iny
         sty zp7
         cpy #$1f
         bne stl
         rts

cl_trl   ldy #0            ;Check how many bytes they occupy
         sty zp11          ;Let's call zp11 'I'
aml      ldy zp11
         iny
         cpy #$20
         bne aj1
         lda #LO((tracks+tracks_l))
         pha
         lda #HI((tracks+tracks_l))
         pha
         jmp aj2
aj1      lda (zp1),y
         tay
         lda (zp5),y
         pha
         lda (zp3),y
         pha
aj2      ldy zp11
         lda (zp1),y
         tay
         pla
         sec
         sbc (zp3),y
         sta zp12          ;Distance between two track tables
         pla
         sbc (zp5),y
         sta zp13
         lda (zp3),y
         sta zp14
         lda (zp5),y
         sta zp15          ;Pointer to track table
         ldy #0
         lda zp13          ;Avoid shooting ourselves on the foot,
         bne alp           ;when the pointers equal.
         lda zp12
         beq ano
alp      lda (zp14),y
         cmp #$ff
         beq ajmp          ;gotcha!
         iny
         cpy zp12
         bne alp
         beq ano
ajmp     iny
         sty zp16
         lda (zp14),y
         pha
         ldy zp11
         lda (zp1),y
         tay
         pla
         sec
         sbc (zp9),y
         ldy zp16
         sta (zp14),y
         ldy zp11
         lda (zp1),y
         tay
         inc zp16
         lda zp16
         sta (zp7),y
ano      inc zp11
         lda zp11
         cmp #$20
         bne aml

         lda #$1e          ;Let's sort it a bit...
         sta zp11          ;so all not zeroes go to the first possible
a22lb    ldy zp11          ;place... (sum sort of a bubble algoritm)
         lda (zp1),y
         sta zp15
         tay
         lda (zp5),y
         pha
         lda (zp3),y
         pha
         ldy zp11
         iny
         lda (zp1),y
         sta zp16
         tay
         pla
         sec
         sbc (zp3),y
         sta zp12
         pla
         sbc (zp5),y
         ora zp12
         bne anemnyert
         ldy zp16
         lda (zp7),y
         tax
         ldy zp15
         lda (zp7),y
         pha
         txa
         sta (zp7),y
         pla
         ldy zp16
         sta (zp7),y
anemnyert
         dec zp11
         bpl a22lb
         rts

packtrk  lda #0            ;pack the tracktables like hell...
         sta zp10
         ldx zp9
         lda trstal,x
         sta zp11
         lda trstah,x
         sta zp12

tpl      ldy zp10
         lda (zp1),y
         cmp subsongs
         bcs tpe
         tay
         sta zp13
         lda (zp3),y
         sta zp14
         lda (zp5),y
         sta zp15
         lda (zp7),y
         sta zp16          ;ugh, hope enough zero page pointers...
         beq tp2           ;Don't copy anything if 0 bytes used
         ldy #0
tp1      lda (zp14),y
         sta (zp11),y
         iny
         cpy zp16
         bne tp1
tp2      ldy zp13          ;...but update the track table pointer...
         lda zp11
         sta (zp3),y
         lda zp12
         sta (zp5),y
         lda zp11
         clc
         adc (zp7),y
         sta zp11
         lda zp12
         adc #0
         sta zp12
tpe      inc zp10
         lda zp10
         cmp #$20
         bne tpl

         ldx zp9
         lda zp11
         sta trendl,x
         lda zp12
         sta trendh,x
         rts

collsct  lda trstal        ;The whole routine is built with the fact in mind
         sta zp1           ;that all track tables are packed tight together,
         lda trstah        ;thus this bunch has _one start and _one end
         sta zp2           ;address...
col      ldy #0
         lda (zp1),y
         cmp #$ff
         bne co1           ;Track jump command; increase pointer and re-enter
         inc zp1           ;(Krestology turn-disk part rulez ;-)  )...
         bne notsct
         inc zp2
         jmp notsct
co1      cmp #$80          ;Below sct00
         bcc notsct
         cmp #$e0          ;Above stc5f
         bcs notsct
         and #$7f
         tax
         ldy sctuse,x
         bne notsct        ;...Why examining again, if used?
         pha               ;Save it for later use...
         jsr exsct         ;Examine sector. Check length (return in AC),
                           ;mark used instruments and glides in snduse and
                           ;glduse.
         tay
         pla
         tax
         tya               ;Damned 6502 design...
         sta sctuse,x
notsct   inc zp1
         bne co2
         inc zp2
co2      lda zp1
         cmp trendl+2      ;until end of the packed tracktable
         bne col
         lda zp2
         cmp trendh+2
         bne col
         rts

exsct    tay
         lda sctadl,y
         sta zp3
         lda sctadh,y
         sta zp4
         ldy #0
exsl     lda (zp3),y
         cmp #$7f          ;FINISH
         bne nemf
         iny
         tya
         rts
nemf     cmp #$c0
         bcc nemsnd
         and #$3f          ;just found an sndxx instruction...
         tax
         lda #$01
         ora snduse,x
         sta snduse,x
         bne exse
nemsnd   cmp #$60
         bcc exse
         cmp #$80
         bcs exse
         cmp #$6f
         beq exse
         clc               ;Found sum GLD.?x
         adc #$01          ;Phew, Taki remapped the command to 01.
         and #$0f
         tax
         lda glduse,x
         ora #$01
         sta glduse,x
exse     iny
         bne exsl
         lda #0            ;There was no FINISH in this sector
         rts

packsct  lda #0            ;Pack them together...
         sta zp1           ;I
         lda #LO(sectors)
         sta zp2
         sta sctsta
         lda #HI(sectors)
         sta zp3
         sta sctsta+1
pcsl     ldx zp1
         lda sctuse,x
         beq nextsct
         sta zp4
         lda sctadl,x
         sta zp5
         lda sctadh,x
         sta zp6
         ldy #0
pcil     lda (zp5),y
         sta (zp2),y
         iny
         cpy zp4
         bne pcil
         lda zp2
         sta sctadl,x
         lda zp3
         sta sctadh,x
         lda zp2
         clc
         adc sctuse,x
         sta zp2
         lda zp3
         adc #$00
         sta zp3
nextsct  inc zp1
         lda zp1
         cmp #HI(sector_l)
         bne pcsl
         lda zp2
         sta sctend
         lda zp3
         sta sctend+1
         rts

packscta ldx #0            ;Pack sector address table
         stx zp1
psa      lda sctuse,x
         bne psx
         lda #0
         sta zp5
psal2    lda sctadl+1,x
         sta sctadl,x
         lda sctadh+1,x
         sta sctadh,x
         lda sctuse+1,x
         sta sctuse,x
         ora zp5
         sta zp5
         inx
         cpx #HI(sector_l)-1
         bne psal2
         lda #0
         sta sctuse+HI(sector_l)-1
         lda zp1
         jsr upd_scta      ;update sector numbers in the tracks
         ldx zp1
         lda zp5
         bne psa
         beq psa4
psx      inc zp1
         ldx zp1
         cpx #HI(sector_l)-1
         bne psa
psa4     stx sctalen
         rts

upd_scta sta zp4
         lda trstal
         sta zp2
         lda trstah
         sta zp3
         ldy #0
sal      lda (zp2),y
         cmp #$80
         bcc nsa
         cmp #$e0
         bcs nsa
         tax
         sec
         sbc #$80
         cmp zp4
         bcc nsa
         dex
         txa
         sta (zp2),y
nsa      inc zp2
         bne nsx
         inc zp3
nsx      lda zp2
         cmp trendl+2
         bne sal
         lda zp3
         cmp trendh+2
         bne sal
         rts


packgld  ldx #1            ;quite slow method but works...
         stx zp1
pgl      lda glduse,x
         bne gnx
         lda #0
         sta zp5
pgl2     lda gld_al+1,x
         sta gld_al,x
         lda gld_ah+1,x
         sta gld_ah,x
         lda glduse+1,x
         sta glduse,x
         ora zp5
         sta zp5
         inx
         cpx #$0f
         bne pgl2
         lda #0
         sta glduse+$0f
         lda zp1
         jsr upd_gl        ;update glide commands in the sectors
         ldx zp1
         lda zp5
         bne pgl
         beq pgl4
gnx      inc zp1
         ldx zp1
         cpx #$0f
         bne pgl
pgl4     stx gldlen

         ldx #0            ;copy the thing one byte down (eliminate one
pgl3     lda gld_al+1,x    ;loose table element (the first))
         sta gld_al,x
         lda gld_ah+1,x
         sta gld_ah,x
         lda glduse+1,x
         sta glduse,x
         inx
         cpx #$0f
         bne pgl3
         dec gldlen
         rts

upd_gl   sta zp4
         lda #LO(sectors)
         sta zp2
         lda #HI(sectors)
         sta zp3
         ldy #0
ugl      lda (zp2),y
         cmp #$60
         bcc ngl
         cmp #$7f
         bcs ngl
         cmp #$6f
         beq ngl
         tax
         and #$0f
         cmp zp4
         bcc ngl
         dex
         txa
         sta (zp2),y
ngl      iny
         cpy sctend
         bne ugl
         inc zp3
         lda zp3
         cmp sctend+1
         bne ugl
         rts

packsnd  ldx #0            ;Same applies to the sndpack algorithm...
         stx zp1
psd      lda snduse,x
         bne snx
         lda #0
         sta zp5
psd2     lda snd_ad+1,x
         sta snd_ad,x
         lda snd_sr+1,x
         sta snd_sr,x
         lda snd_gt+1,x
         sta snd_gt,x
         lda snd_wt+1,x
         sta snd_wt,x
         lda snd_ft+1,x
         sta snd_ft,x
         lda snd_pt+1,x
         sta snd_pt,x
         lda snd_st+1,x
         sta snd_st,x
         lda snduse+1,x
         sta snduse,x
         ora zp5
         sta zp5
         inx
         cpx #$3f
         bne psd2
         lda #0
         sta snduse+$3f
         lda zp1
         jsr upd_sd        ;update Sndxx commands in the sectors
         ldx zp1
         lda zp5
         bne psd
         stx sndlen
         rts
snx      inc zp1
         ldx zp1
         cpx #$3f
         bne psd
         inx
         stx sndlen
         rts

upd_sd   sta zp4
         lda #LO(sectors)
         sta zp2
         lda #HI(sectors)
         sta zp3
         ldy #0
usl      lda (zp2),y
         cmp #$c0
         bcc nsd
         tax
         and #$3f
         cmp zp4
         bcc nsd
         dex
         txa
         sta (zp2),y
nsd      iny
         cpy sctend
         bne usl
         inc zp3
         lda zp3
         cmp sctend+1
         bne usl
         rts

collwt   ldx #0            ;Search all instruments and trace the arpeggio
cwl      ldy snd_wt,x      ;table for used bytes
         lda wveuse,y
         bne wused         ;Used area, no reason to scan once more

scwl     ora #$01
         sta wveuse,y
         lda wve_wf,y
         cmp #$ff
         bne scw1
         lda wve_st,y
         tay
         .byte $24
scw1     iny
         cpy #0
         beq wused
         lda wveuse,y
         beq scwl

wused    inx
         cpx sndlen
         bne cwl
         rts

packwt   ldx #0
         stx zp1
pwt      lda wveuse,x
         bne wtx
         lda #0
         sta zp5
pwt2     lda wve_wf+1,x
         sta wve_wf,x
         lda wve_st+1,x
         sta wve_st,x
         lda wveuse+1,x
         sta wveuse,x
         ora zp5
         sta zp5
         inx
         cpx #$ff
         bne pwt2
         lda #0
         sta wveuse+$ff
         lda zp1
         jsr upd_wt
         ldx zp1
         lda zp5
         bne pwt
         stx wvelen
         rts
wtx      inc zp1
         ldx zp1
         cpx #$ff
         bne pwt
         inx
         stx wvelen
         rts

upd_wt   sta zp4
         ldy #0
uwl      ldx snd_wt,y
         cpx zp4
         bcc nwd
         dex
         txa
         sta snd_wt,y
nwd      iny
         cpy sndlen
         bne uwl

         ldy #0
uwl2     lda wve_wf,y
         cmp #$ff
         bne nwj
         ldx wve_st,y
         cpx zp4
         bcc nwj
         dex
         txa
         sta wve_st,y
nwj      iny
         cpy wvelen
         bne uwl2
         rts

collft   ldx #0            ;Search all instruments and trace the filter
                           ;table for used bytes
         lda #1            ;Let's treat it as used...
         sta fltuse
cfl      ldy snd_ft,x
         beq fused         ;0 is special
         cpy #$ff
         beq fused         ;so is $ff
         lda fltuse,y
         bne fused         ;Used area, no reason to scan once more

scfl     ora #$01
         sta fltuse,y
         lda flt_rp,y
         cmp #$ff          ;jump ahead...
         bne scf1
         lda flt_fh,y
         tay
         .byte $24
scf1     iny
         cpy #0
         beq fused
         lda fltuse,y
         beq scfl

fused    inx
         cpx sndlen
         bne cfl
         rts

packft   ldx #0
         stx zp1
pft      lda fltuse,x
         bne ftx
         lda #0
         sta zp5
pft2     lda flt_rp+1,x
         sta flt_rp,x
         lda flt_fh+1,x
         sta flt_fh,x
         lda flt_rl+1,x
         sta flt_rl,x
         lda fltuse+1,x
         sta fltuse,x
         ora zp5
         sta zp5
         inx
         cpx #$ff
         bne pft2
         lda #0
         sta fltuse+$ff
         lda zp1
         jsr upd_ft
         ldx zp1
         lda zp5
         bne pft
         stx fltlen
         rts
ftx      inc zp1
         ldx zp1
         cpx #$ff
         bne pft
         inx
         stx fltlen
         rts

upd_ft   sta zp4
         ldy #0
ufl      ldx snd_ft,y
         cpx zp4
         bcc nfd
         dex
         txa
         sta snd_ft,y
nfd      iny
         cpy sndlen
         bne ufl

         ldy #0
ufl2     lda flt_rp,y
         cmp #$ff
         bne nfj
         ldx flt_fh,y
         cpx zp4
         bcc nfj
         dex
         txa
         sta flt_fh,y
nfj      iny
         cpy fltlen
         bne ufl2
         rts

collpt   ldx #0            ;Search all instruments and trace the pulse
                           ;table for used bytes
         lda #1            ;Let's treat it as used...
         sta plsuse
cpl      ldy snd_pt,x
         beq pused         ;0 is special
         cpy #$ff
         beq pused         ;so is $ff
         lda plsuse,y
         bne pused         ;Used area, no reason to scan once more

scpl     ora #$01
         sta plsuse,y
         lda pls_rp,y
         cmp #$ff          ;jump ahead...
         bne scp1          ;Not you, Scorpy!  ;-)
         lda pls_ph,y
         tay
         .byte $24
scp1     iny
         cpy #0
         beq pused
         lda plsuse,y
         beq scpl

pused    inx
         cpx sndlen
         bne cpl
         rts

packpt   ldx #0
         stx zp1
ppt      lda plsuse,x
         bne ptx
         lda #0
         sta zp5
ppt2     lda pls_rp+1,x
         sta pls_rp,x
         lda pls_ph+1,x
         sta pls_ph,x
         lda pls_pl+1,x
         sta pls_pl,x
         lda plsuse+1,x
         sta plsuse,x
         ora zp5
         sta zp5
         inx
         cpx #$ff
         bne ppt2
         lda #0
         sta slduse+$ff
         lda zp1
         jsr upd_pt
         ldx zp1
         lda zp5
         bne ppt
         stx plslen
         rts
ptx      inc zp1
         ldx zp1
         cpx #$ff
         bne ppt
         inx
         stx plslen
         rts

upd_pt   sta zp4
         ldy #0
upl      ldx snd_pt,y
         cpx zp4
         bcc npd
         dex
         txa
         sta snd_pt,y
npd      iny
         cpy sndlen
         bne upl

         ldy #0
upl2     lda pls_rp,y
         cmp #$ff
         bne npj
         ldx pls_ph,y
         cpx zp4
         bcc npj
         dex
         txa
         sta pls_ph,y
npj      iny
         cpy plslen
         bne upl2
         rts

collst   ldx #0            ;Search all instruments and trace the slide
                           ;table for used bytes
         lda #1            ;Let's treat it as used...
         sta slduse
csl      ldy snd_st,x
         beq sused         ;0 is special
         cpy #$ff
         beq sused         ;so is $ff
         lda slduse,y
         bne sused         ;Used area, no reason to scan once more

scsl     ora #$01
         sta slduse,y
         lda sld_rp,y
         cmp #$ff          ;jump ahead...
         bne scs1
         lda sld_fh,y
         tay
         .byte $24
scs1     iny
         cpy #0
         beq sused
         lda slduse,y
         beq scsl

sused    inx
         cpx sndlen
         bne csl
         rts

packst   ldx #0
         stx zp1
pst      lda slduse,x
         bne sltx
         lda #0
         sta zp5
pst2     lda sld_rp+1,x
         sta sld_rp,x
         lda sld_fh+1,x
         sta sld_fh,x
         lda sld_fl+1,x
         sta sld_fl,x
         lda slduse+1,x
         sta slduse,x
         ora zp5
         sta zp5
         inx
         cpx #$ff
         bne pst2
         lda #0
         sta slduse+$ff
         lda zp1
         jsr upd_st
         ldx zp1
         lda zp5
         bne pst
         stx sldlen
         rts
sltx     inc zp1
         ldx zp1
         cpx #$ff
         bne pst
         inx
         stx sldlen
         rts

upd_st   sta zp4
         ldy #0
usld     ldx snd_st,y
         cpx zp4
         bcc nsld
         dex
         txa
         sta snd_st,y
nsld     iny
         cpy sndlen
         bne usld

         ldy #0
usl2     lda sld_rp,y
         cmp #$ff
         bne nsj
         ldx sld_fh,y
         cpx zp4
         bcc nsj
         dex
         txa
         sta sld_fh,y
nsj      iny
         cpy sldlen
         bne usl2
         rts

;------------- Screen and keyboard ---------

primm    tsx
         inx
         lda $0100,x
         clc
         adc #$01
         sta sptr
         inx
         lda $0100,x
         adc #$00
         sta sptr+1
         ldy #0
_p_l1    lda (sptr),y
         beq _pend
         cmp #$40
         bcc _ok
         eor #$20
_ok      jsr iFFD2
         iny
         bne _p_l1

_pend    tya
         dex
         clc
         adc sptr
         sta $0100,x
         lda sptr+1
         adc #0
         inx
         sta $0100,x
         rts

input
         ldx #39
         lda #$20
_il      sta ibuf,x
         dex
         bpl _il
         ldy #0
_i3      jsr iFFCF
         cmp #$0d
         beq _i2
         sta ibuf,y
         iny
         cpy #40
         bne _i3
_i2      sty ibufl
         rts

ibufl    .byte 0
ibuf     .block 40
hbuf     .block 4
hdigs    .byte 0
htem     .word 0

inputh   jsr input
         lda ibufl
         cmp #$05
         bcc _ih1          ;too long, quit
         rts
_ih1     ldx #3
         lda #0
_ih2     sta hbuf,x
         dex
         bpl _ih2
         sta hdigs
         ldx #0
_ih3     lda ibuf,x
         cmp #$30
         bcs _ih4
         sec
         rts               ;digit below $30, quit
_ih4     cmp #$3a
         bcc _ihf          ;between $30 and $39, cool
         cmp #$47
         bcc _ih5          ;above 'F', quit
         rts
_ih5     sec
         sbc #$07          ;let it be less by 7
_ihf     sec
         sbc #$30
         pha
         lda hbuf+2
         sta hbuf+3
         lda hbuf+1
         sta hbuf+2
         lda hbuf
         sta hbuf+1
         pla
         sta hbuf
         inc hdigs
         inx
         cpx ibufl
         bne _ih3
         lda #0
         sta htem
         sta htem+1
         ldx hdigs
         dex
_ih6     asl htem
         rol htem+1
         asl htem
         rol htem+1
         asl htem
         rol htem+1
         asl htem
         rol htem+1
         lda hbuf,x
         ora htem
         sta htem
         dex
         bpl _ih6
         ldx htem
         ldy htem+1
         rts

m_load
         lda #$01
         ldx #$08
         ldy #$00
         jsr iFFBA
         lda #$10
         ldx #LO(filnam)
         ldy #HI(filnam)
         jsr iFFBD
         jsr iFFC0
         lda st
         beq *+5
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
m_unid   jsr iFFCC
         lda #$01
         jsr iFFC3
         jsr primm
         .byte 13
         .text "Unidentified module"
         .byte 13,13,0
         sec
         rts

m_ldat   ldx #$00
         jsr basinp
         cmp p_ver,x       ;V01.2x
         bne m_unid
m2       inx
         cpx #$05
         bne m_ldat+2
         jsr basinp
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
         sta loadcnt       ;length
         ldx #$00
m_lp05   jsr basinp
         sta wve_wf,x
         jsr basinp
         sta wve_st,x
         inx
         cpx loadcnt
         bne m_lp05
         cpx #$00
         beq *+13
         lda #$00
         sta wve_wf,x
         sta wve_st,x
         inx
         bne *-7
         jsr basinp        ;flttab
         sta loadcnt       ;length
m_lp06   jsr basinp
         sta flt_rp,x
         jsr basinp
         sta flt_fh,x
         jsr basinp
         sta flt_rl,x
         inx
         cpx loadcnt
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
         sta loadcnt       ;length
m_lp07   jsr basinp
         sta pls_rp,x
         jsr basinp
         sta pls_pl,x
         jsr basinp
         sta pls_ph,x
         inx
         cpx loadcnt
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
         sta loadcnt       ;length
m_lp08   jsr basinp
         sta sld_rp,x
         jsr basinp
         sta sld_fl,x
         jsr basinp
         sta sld_fh,x
         inx
         cpx loadcnt
         bne m_lp08
         cpx #$00
         beq *+16
         lda #$00
         sta sld_rp,x
         sta sld_fl,x
         sta sld_fh,x
         inx
         bne *-10
         lda #HI(tracks)   ;tracks
         sta m_ptr1+2
         sta m_ptr2+2
m_lp09   jsr basinp
         sta loadcnt       ;length
m_lp0a   jsr basinp
m_ptr1   sta tracks,x
         inx
         cpx loadcnt
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
         sta loadcnt       ;length
m_lp0c   jsr iFFCF
         sta xD020
         sty xD020
m_ptr3   sta sectors,x
         bit st
         bvs m_fend
         ldy st
         bne m_fend8
         inx
         cpx loadcnt
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
         cmp #HI(sector_l+sectors)
         bne m_lp0b
m_fend   set37
         jsr iFFCC
         lda #$01
         jsr iFFC3
m_fend8  jmp derror

basout   jsr iFFD2
         jmp *+6
basinp   jsr iFFCF
         sta xD020
         sty xD020
         ldy st
         bne *+3
         rts

         pla
         pla
derror   lda st
         pha
         jsr iFFCC
         lda #$01
         jsr iFFC3
         pla
         bpl rdrive
i37C2    jsr primm
         .byte 13
         .text "Device 8 not present"
         .byte 13,13,0
         sec
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

i37E1
         lda #0
         sta _rct
         ldx #$01
         jsr iFFC6
         ldx #$00
_rdc1    jsr iFFCF
         ora _rct
         sta _rct
         jsr iFFD2         ;00,
         inx
         cpx #$02
         bne _rdc1
         jsr iFFCF
         jsr iFFD2
         jsr iFFCF
         cmp #$20          ;1st spc
         bne *+5
rdloop   jsr iFFCF
         cmp #$2c
         beq rdcomm
         jsr iFFD2
         inx
         cpx #$13
         bne rdloop
         jsr iFFCF
         cmp #$2c
         beq rdcomm
         bne *-12
rdcomm   jsr iFFD2
         inx
         ldy #$05
         jsr iFFCF
         jsr iFFD2
         inx
         dey
         bne *-8
         jsr iFFCF
         jsr iFFCC
         lda #$01
         jsr iFFC3
         lda #13
         jsr iFFD2
         lda _rct
         cmp #$30
         bne _rd2
         clc
         rts
_rd2     sec
         rts

_rct     .byte 0

m_dirr   lda #$01
         ldx #$08
         ldy #$00
         jsr iFFBA
         lda #1
         ldx #LO(filnam)
         ldy #HI(filnam)
         jsr iFFBD
         jsr iFFC0         ;open
         lda st
         beq *+5
         jmp derror

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
         lda #13
         jsr iFFD2
         jmp iFFD2

m_sav    lda #$01
         ldx #$08
         ldy #$01
         jsr iFFBA
         lda zp3
         ldx #LO(filnam)
         ldy #HI(filnam)
         jsr iFFBD
         jsr iFFC0
         lda st
         beq *+5
         jmp derror
         jsr primm
         .byte 13
         .text "Please wait, saving..."
         .byte 13,0
         ldx #$01
         jsr iFFC9

         ldy #0
         lda start
         jsr basout
         lda start+1
         jsr basout
         lda #LO(pstart)
         sta zp3
         lda #HI(pstart)
         sta zp4
savl     ldy #0
         lda (zp3),y
         jsr basout
         inc zp3
         bne _s2
         inc zp4
_s2      lda zp3
         cmp zp1
         bne savl
         lda zp4
         cmp zp2
         bne savl

         jsr iFFCC
         lda #$01
         jsr iFFC3
         jmp derror


subsongs .byte 0           ;Number of subsongs
reloc    .word 0           ;Relocation value of the code (signed)
sreloc   .word 0           ;The above, with the SID base address
zreloc   .byte 0           ;Above, used zeropage pointer address
start    .word 0
tr1id    .block 32
tr2id    .block 32
tr3id    .block 32

glduse   .block 16
snduse   .block 64
tr1use   .block 32
tr2use   .block 32
tr3use   .block 32
trstal   .byte 0,0,0
trstah   .byte 0,0,0
trendl   .byte 0,0,0
trendh   .byte 0,0,0
sctsta   .word 0
sctend   .word 0
sctalen  .byte 0
gldlen   .byte 0
sndlen   .byte 0
wvelen   .byte 0
fltlen   .byte 0
plslen   .byte 0
sldlen   .byte 0


sctuse   .block HI(sector_l)
wveuse   .block 256
fltuse   .block 256
plsuse   .block 256
slduse   .block 256

tmpsta   .word 0
tmpscta  .word 0
dfnam    .text "               "
filnam   .text "                    "
suff     .text ",P,W"

#ifdef c64                              ;Plus/4 freqtab
freqtab  .byte $01,$01,$01,$01,$01,$01
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

         .byte $35,$48,$5b,$70,$86,$9d
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
#ifdef p4
freqtab  .byte $01,$01,$01,$01,$01,$01
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

         .byte $16,$27,$39,$4b,$5f,$74
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

           *= (* & $ff00) + $0100

#include player.asm

.end
