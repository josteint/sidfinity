;-- 80 chars wide ASCII viewer for C64 and C-16 / C-116 / Plus/4
;   Initial release
;
;   This is just a small, quick-and-dirty routine to display and / or
;   print ASCII texts on the Commodore computer.
;   (It runs even on a stock unexpanded C-16)
;
;   Released on 2000.03.15
;
;   (C) 2000        Levente H rsfalvi    ( Levente@terrasoft.hu )
;
;   Portions (I/O routines)
;   (C) 1994-1999   Bal zs Tak cs        ( Takinb@sch.bme.hu )
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
;   - vchars.bin        4x8 charset
;
;   The source can be compiled to run both on C-64 and Plus/4.
;   (Just define c64 or p4 with the TASM -d option in the command line)
;
;   Link with -thx option
;


#define LO(x) (x&$ff)
#define HI(x) (x>>8)

#ifndef p4
#define c64
#endif

;system specific definitions
#ifdef c64
#define set37 lda #$37 \ sta x01
#define set35 lda #$35 \ sta x01

;         *= $0810
         *= $080e
         .word *+2

i_vchars = $1d00
         .export i_vchars

#define screen $0400
#define bitmap $2000
#define vic $d000
#define color $d800

#define colr $0f

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

x01        =$01
xC6        =$C6
xCB        =$CB
xD3        =$D3
x0277      =$0277
x0286      =$0286
x0289      =$0289
x028D      =$028D
x0291      =$0291


xD011      =vic+$11
xD018      =vic+$18
xD020      =vic+$20
xD021      =vic+$21

iBDCD      =$BDCD
iE544      =$E544
iFCE2      =$fce2

#endif

#ifdef p4
#define set37 sta $ff3e
#define set35 sta $ff3f

;         *= $1010
         *= $100E
         .word *+2

i_vchars = $1d00
         .export i_vchars

#define screen $0c00
#define bitmap $2000
#define color $0800

#define colr $51

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

xCB        =$C6
xC6        =$EF
xD3        =$ca
x0277      =$0527
x0286      =$053b
x0543      =$0543
x0289      =$053f
x028D      =$0543
x0291      =$0547

xD011      =$ff06
xD018      =$ff12               ;not quite the same, but will do here...
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


cint       =$FF81
setlfs     =$FFBA
setnam     =$FFBD
open       =$FFC0
close      =$FFC3
chkin      =$FFC6
chkout     =$FFC9
clrchn     =$FFCC
chrin      =$FFCF
chrout     =$FFD2
getkey     =$FFE4


         lda #0
         sta xD020
         sta xD021
         lda #1
         sta x0289
         lda #$80
         sta x0291
         lda #colr
         sta x0286
         lda #14                        ;Small/capital set
         jsr chrout

#ifdef p4
         lda #0
         sta $f9                     ;Fix PuCrunch's fault...
#endif
fn0      jsr iE544
fn       jsr primm
         .text "Enter filename (or $)!: "
         .byte 0
         jsr input
         lda #13
         jsr chrout
         lda ibufl
         beq fn
         ldy ibufl
         dey
         cpy #16
         bcc _bel-2
         ldy #15
         sty zp1
_bel     lda ibuf,y
         sta filnam,y
         dey
         bpl _bel

         ldx #0
         ldy zp1
         iny
fnl1     lda suff,x
         sta filnam,y
         inx
         iny
         cpx #4
         bne fnl1
         sty namelen

         lda filnam
         cmp #'$'
         bne fn2
         lda #13
         jsr chrout
         jsr m_dirr
         jmp fn

fn2      jsr fopen
         ldx #1
         jsr chkin
         jsr chrin
         lda st
         beq fn23
         jsr derror
         jmp fn

fn23     jsr clrchn
         jsr fclose

fn3      jsr primm
         .byte 13
         .text "(V)iew or (P)rint? "
         .byte 0
         jsr input
         lda #13
         jsr chrout
         lda ibuf
         cmp #'V'
         beq fn4
         cmp #'P'
         beq fn5
         bne fn3

fn4      jsr view
         jsr iE544
         lda #14                        ;Small/capital set
         jsr chrout
         jmp fn

fn5      jsr primm
         .text "Prepare printer and press Return!..."
         .byte 13,0
         jsr input
         jsr fopen
         bcc fn6
         jmp fn
fn6
         jsr print

         jmp fn0

;------------- Print the file... ----------

print    jsr fopen
         jsr popen
         lda #0
         sta zp2                ;Column - for tabs
         ldx #2
         jsr chkout
         lda #17
         jsr chrout             ;Charset setting before _any text
         jsr clrchn

pl0      ldx #1
         jsr chkin
         ldy #0
pl1      jsr chrin
         cmp #13                ;Keeping $0d bytes is not necessary,
         beq pl4                ;$0a signs EOL better
                                ;The CBM printer expects $0d - all $0a's are
                                ;converted to $0d in the same step with the
                                ;PETSCII conversion (it is in the conversion
                                ;table)
         cmp #$80               ;Nonstandard ASCII... maybe an accented char?
         bcc p10
         jsr look_ac            ;Look for accented - and substitute.
p10      tax
         lda a2p,x
         sta buffer,y
         iny
         beq pl1e
pl4      bit st
         bvc pl1
pl1e     sty zp1
         lda st
         sta zp4
         jsr clrchn

         ldx #2
         jsr chkout
         ldy #0
pl2      lda buffer,y
         cmp #9                 ;Tab
         bne p7
         lda zp2                ;Column
         sta zp3                ;Store it temporarily
         clc
         adc #$08
         and #$f8
         sta zp2
         sec
         sbc zp3
         pha
p8       lda #' '
         jsr chrout
         pla
         sec
         sbc #1
         pha
         bne p8
         pla
         jmp p3

p7       jsr chrout
         cmp #13                ;CR?
         bne p5
         lda #0
         sta zp2                ;Yes, ero column
         lda #17                ;Charset code again...
         jsr chrout
         jmp p6
p5       inc zp2
p3       lda zp2
         cmp #80
         bne p6
         lda #0                 ;current line was longer than 80 chars
         sta zp2
         lda #13                ;--> send CR to the printer (wrap)
         jsr chrout
         lda #17                ;...and don't forget the set select code
         jsr chrout

p6       lda st
         bne pe
         iny
         cpy zp1
         bne pl2

         jsr clrchn
         lda zp4                ;Stored status byte (from load buffer)
         bne p9
         jmp pl0

p9       ldx #2                 ;Flush printers buffer
         jsr chkout
         lda #13
         jsr chrout
         jsr clrchn

pe       jsr pclose
         jmp fclose

look_ac  ldx #17
la1      cmp acc,x
         beq la2
         dex
         bpl la1
         lda #$20
         rts
la2      lda acc_s,x
         rts

view     jsr fopen
#ifdef c64
         lda #$18
#endif
#ifdef p4
         lda #$c8
#endif
         sta xD018
         lda #$3b
         sta xD011
         jsr clrscr
         jsr nextpg
         lda #0
         sta xC6
vl       lda xC6
         beq vl
         lda #0
         sta xC6
         lda x0277
         cmp #$0d
         bne v2
         bit st
         bvs vl
         jsr nextpg
         jmp vl
v2       cmp #$13
         bne v3
         jsr fclose
         jmp view
v3       cmp #$20
         bne v4
         bit st
         bvs vl
         jsr scroll
         lda #24
         sta zp1
         ldx #1
         jsr chkin
         jsr nextrow
         jsr clrchn
         jmp vl
v4
#ifdef c64
         cmp #$5f                       ;<--
#endif
#ifdef p4
         cmp #$1b                       ;ESC
#endif
         bne vl

ve       jsr fclose
#ifdef c64
         lda #$15
#endif
#ifdef p4
         lda #$c4
#endif
         sta xD018
         lda #$1b
         sta xD011
         jmp iE544

nextpg   ldx #1
         jsr chkin
         jsr clrmap
         lda #0
         sta zp1                ;Row 0

nxl      jsr nextrow
         inc zp1
         lda zp1
         cmp #25
         beq nxpe
         bit st
         bvc nxl

nxpe     jmp clrchn

nextrow  lda #0
         sta zp2                ;Column 0
         jsr clc_add
nxcl2    jsr chrin
         cmp #$20
         bcs c_ch1              ;Maybe a character?
         cmp #$0a               ;Linefeed?
         beq nxr_e              ;...End
         cmp #$09               ;Tab
         bne nxc2               ;Next character...
         lda zp2
         clc
         adc #$08
         and #$f8
         sta zp2
         jsr clc_add
         jmp nxc2

c_ch1    cmp #$80
         bcc nxc3
         jsr look_ac
nxc3     sec
         sbc #$20               ;...Quite simple chr conv (see chrset...)
         ldx #0
         stx zp5
         stx zp6
         asl a
         asl a
         rol zp6
         asl a
         rol zp6
         sta zp5
         lda zp6
         clc
         adc #HI(i_vchars)
         sta zp6
         lda zp2
         and #$01
         bne nxc1
         lda #$f0               ;Mask for next char
         .byte $2c
nxc1     lda #$0f
         sta msk
         ldy #7
nxcl1    lda (zp5),y            ;Charset byte
msk      = *+1
         and #0
         ora (zp3),y            ;Bitmap byte
         sta (zp3),y
         dey
         bpl nxcl1
         inc zp2
         lda zp2
         and #$01
         bne nxc2
         lda zp3
         clc
         adc #8
         sta zp3
         bne nxc2
         inc zp4
nxc2     lda zp2
         cmp #80
         beq nxr_e
         bit st
         bvc nxcl2
nxr_e    rts

clc_add  lda zp2
         asl a
         asl a
         sta cla_l
         lda #0
         rol a
         sta cla_h
         ldx zp1
         lda rwadl,x
         clc
cla_l    = *+1
         adc #0
         sta zp3
         lda rwadh,x
cla_h    = *+1
         adc #0
         adc #HI(bitmap)
         sta zp4
         rts

scroll   lda #LO(bitmap)
         sta ad2+1
         lda #HI(bitmap)
         sta ad2+2
         lda #LO((bitmap+$0140))
         sta ad1+1
         lda #HI((bitmap+$0140))
         sta ad1+2
         ldx #0
ad1      lda $FACE,x
ad2      sta $FACE,x
         inx
         bne ad1
         inc ad1+2
         inc ad2+2
         lda ad2+2
         cmp #HI((bitmap+$1e00))
         bne ad1
         lda #0
s1       sta bitmap+$1e00,x
         inx
         bne s1
         ldx #$3f
s2       sta bitmap+$1f00,x
         dex
         bpl s2
         rts

clrscr   lda #((colr << 4)&$f0)
         ldy #0
cl2      sta screen,y
         sta screen+$100,y
         sta screen+$200,y
         sta screen+$300,y
         iny
         bne cl2

#ifdef p4
         lda #$05
cl3      sta color,y
         sta color+$100,y
         sta color+$200,y
         sta color+$300,y
         iny
         bne cl3
#endif
clrmap   lda #LO(bitmap)
         sta cl1+1
         lda #HI(bitmap)
         sta cl1+2
         ldy #0
         tya
cl1      sta $FACE,y
         iny
         bne cl1
         inc cl1+2
         lda cl1+2
         cmp #HI((bitmap+$2000))
         bne cl1-1
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
_ok      jsr chrout
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

input    ldx #39
         lda #$20
_il      sta ibuf,x
         dex
         bpl _il
         ldy #0
_i3      jsr chrin
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


;---------- I/O -----------------

fopen    lda #$01
         ldx #$08
         ldy #$02
         jsr setlfs
         lda #$14
         ldx #LO(filnam)
         ldy #HI(filnam)
         jsr setnam
         jsr open
         lda st
         beq *+4
         sec
         rts
         clc
         rts

fclose   jsr clrchn
         lda #$01
         jmp close

popen    lda #$02
         ldx #$04
         ldy #$00
         jsr setlfs
         lda #0
         jsr setnam
         jsr open
         clc
         lda st
         bne *+3
         rts
         jmp derror

pclose   lda #$02
         jmp close

derror   lda st
         pha
         jsr clrchn
         lda #$01
         jsr close
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
         JSR setlfs
         LDA #$00
         TAX
         TAY
         JSR setnam
         JSR open

i37E1
         lda #0
         sta _rct
         ldx #$01
         jsr chkin
         ldx #$00
_rdc1    jsr chrin
         ora _rct
         sta _rct
         jsr chrout       ;00,
         inx
         cpx #$02
         bne _rdc1
         jsr chrin
         jsr chrout
         jsr chrin
         cmp #$20          ;1st spc
         bne *+5
rdloop   jsr chrin
         cmp #$2c
         beq rdcomm
         jsr chrout
         inx
         cpx #$13
         bne rdloop
         jsr chrin
         cmp #$2c
         beq rdcomm
         bne *-12
rdcomm   jsr chrout
         inx
         ldy #$05
         jsr chrin
         jsr chrout
         inx
         dey
         bne *-8
         jsr chrin
         jsr clrchn
         lda #$01
         jsr close
         lda #13
         jsr chrout
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
         jsr setlfs
         lda #1
         ldx #LO(filnam)
         ldy #HI(filnam)
         jsr setnam
         jsr open         ;open
         lda st
         beq *+5
         jmp derror

         ldx #$01
         jsr chkin         ;chkin
         jsr chrin         ;load addr
         jsr chrin
m_newl   lda #$06
         sta xD3
         jsr chrin
         ldx st
         bmi m_endd
         bne m_derr
         jsr chrin
         beq m_endd
         jsr chrin         ;blocks
         ldx st
         bmi m_endd
         bne m_derr
         tax
         jsr chrin
         jsr iBDCD         ;out
         lda #$20
         jsr chrout
m_line   jsr chrin
         beq m_lend
         ldx st
         bmi m_endd
         bne m_derr
         jsr chrout
         jmp m_line
m_lend   lda #$0d
         jsr chrout
         lda x028D
         and #$04
         bne *-5
         lda xCB
         cmp #$3f
         bne m_newl
         jmp m_endd

m_derr   jsr clrchn
         lda #$01
         jsr close
         lda #$01
         ldx #$08
         ldy #$0f
         jsr setlfs
         lda #$00
         tax
         tay
         jsr setnam
         jsr open
         ldx #$01
         jsr chkin
         lda #$0d
         jsr chrout
         jsr chrout
         lda #$06
         sta xD3
         jsr chrin
         jsr chrout
         cmp #$0d
         bne *-8

m_endd   jsr clrchn         ;clrch
         lda #$01
         jsr close         ;close
         lda #13
         jsr chrout
         jmp chrout


filnam   .text "                    "
suff     .text ",P,R"
namelen  .byte 0

acc      .text "öüóõúéáíûÖÜÓÕÚÉÁÍÛ"             ;Accented chars
acc_s    .text "ouooueaiuOUOOUEAIU"             ;And their substitutes

a2p      .byte $20,$20,$20,$20,$20,$20,$20,$20  ;ASCII to PETSCII
         .byte $20,$09,$0d,$20,$20,$0d,$20,$20  ;conversion table
         .byte $20,$20,$20,$20,$20,$20,$20,$20  ;10
         .byte $20,$20,$20,$20,$20,$20,$20,$20
         .byte $20,$21,$22,$23,$24,$25,$26,$27  ;20
         .byte $28,$29,$2a,$2b,$2c,$2d,$2e,$2f
         .byte $30,$31,$32,$33,$34,$35,$36,$37  ;30
         .byte $38,$39,$3a,$3b,$3c,$3d,$3e,$3f
         .byte $40,$61,$62,$63,$64,$65,$66,$67  ;40
         .byte $68,$69,$6a,$6b,$6c,$6d,$6e,$6f
         .byte $70,$71,$72,$73,$74,$75,$76,$77  ;50
         .byte $78,$79,$7a,$5b,$5f,$5d,$5e,$a4      ;a4 = '_'
         .byte $27,$41,$42,$43,$44,$45,$46,$47  ;60
         .byte $48,$49,$4a,$4b,$4c,$4d,$4e,$4f
         .byte $50,$51,$52,$53,$54,$55,$56,$57  ;70
         .byte $58,$59,$5a,$b3,$7d,$ab,$20,$20

rwadl    .byte $00,$40,$80,$c0,$00,$40,$80,$c0  ;Row address low
         .byte $00,$40,$80,$c0,$00,$40,$80,$c0
         .byte $00,$40,$80,$c0,$00,$40,$80,$c0
         .byte $00

rwadh    .byte $00,$01,$02,$03,$05,$06,$07,$08  ;High
         .byte $0a,$0b,$0c,$0d,$0f,$10,$11,$12
         .byte $14,$15,$16,$17,$19,$1a,$1b,$1c
         .byte $1e

buffer   .block 256

         .end
