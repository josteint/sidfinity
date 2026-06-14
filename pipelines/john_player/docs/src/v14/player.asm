;       Compile with WLA-6510 (http://www.hut.fi/~vhelin/wla.html)


.INCLUDE "mem.inc"

.DEFINE COMPILE_PLAYER  0       ; 0 to compile editor (with normal player)
                                ; 1 to compile normal player only
                                ; 2 to compile packed block data player

.DEFINE reloc           $1000   ; use relocator instead
.DEFINE zeropage        $40



;*****  JOHN PLAYER VERSION 1.4  *******************************************

.DEFINE FreqTab         $035a+reloc
.DEFINE Music           $0400+reloc

.DEFINE VibTab          $0400+reloc
.DEFINE SoundTab        $0420+reloc
.DEFINE FilTab          $0500+reloc
.DEFINE WaveTab         $0540+reloc
.DEFINE ArpTab          $0580+reloc
.DEFINE Sequencer       $05c0+reloc
.DEFINE BlockData       $0600+reloc

.ENUM zeropage
cmdtick         DB
fbase           DB
c1hold          DB
c2hold          DB
c3hold          DB
count           DB
speed           DB
seqpos          DB
step            DB
block           DB
vibpos          DB
mod             DB
modh            DB
.ENDE


.ORG $0
.SECTION "BANKHEADER"                   ; CBM binary load address

.IF COMPILE_PLAYER == 0
        .dw     $0801
.ELSE
        .dw     reloc
.ENDIF
.ENDS


;*****  INITIALIZE PLAYER ($1000)  *****************************************

.ORG    reloc
.SECTION "johnplayer" FORCE

        jmp     Initialize


;*****  PLAYER FRAME ROUTINES ($1003)  *************************************

;-----  channel 1

c1:
        ldy     c1hold                  ; 0 = no hold, other = sound offset
        beq     c1sndp_

        ldx     #$ff
        stx.w   c1gate_+1               ; key down - gate on
        inx
        stx     c1hold                  ; voice reset

        lda     SoundTab,y              ; $00: attack/decay
        sta     $d405
        lda     SoundTab+1,y            ; $01: sustain/release
        sta     $d406
        lda     #$09                    ; testbit+gate to stabilize adsr
        sta     $d404

        lda     SoundTab+2,y            ; $02: sound pos
        sta.w   c1sndp_+1
        lda     SoundTab+3,y            ; $03: sound end
        sta.w   c1snde_+1
        lda     SoundTab+4,y            ; $04: sound loop
        sta.w   c1snd8_+1

        lda     SoundTab+9,y            ; $09: resonance/filt. ch select
        sta     $d417
        lda     SoundTab+10,y           ; $0a: filt. type/master volume
        sta     $d418

        lda     SoundTab+5,y            ; $05: pw init ($00 = no init)
        beq     c1done

        sta.w   c1pwhi_+1
        lda     SoundTab+6,y            ; $06: pw mod rate
        sta.w   c1pwal_+1
        lda     SoundTab+7,y            ; $07: pw mod top
        sta.w   c1ptop_+1
        lda     SoundTab+8,y            ; $08: pw mod bottom
        sta.w   c1pbot_+1

        bpl     c1done                  ; always branch

c1sndp_:
        ldy     #$00                    ; c1 snd pos
        beq     c1done
c1snde_:
        cpy     #$00                    ; c1 snd end
        bne     c1nolp
c1snd8_:
        ldy     #$00                    ; c1 snd loop

c1nolp:
        lda     FilTab,y                ; c1 controls filter
        clc
        adc     fbase                   ; filter base (from note data)
        sta     $d416                   ; set filter cutoff

        lda     WaveTab,y               ; get waveform
c1gate_:
        and     #$fe                    ; gate on/off 
        sta     $d404                   ; set channel waveform

c1pwlo_:
        lda     #$00
c1pwal_:
        adc     #$02
        tax
c1pwhi_:
        lda     #$08
c1pwah_:
        adc     #$00

c1ptop_:
        cmp     #$10                    ; pulse width top limit
        beq     c1pwrev
c1pbot_:
        cmp     #$00                    ; pulse width bottom limit
        bne     c1norev

c1pwrev:
        lda.w   c1pwal_+0               ; reverse pulse direction
        eor     #$80                    ; morph between adc/sbc
        sta.w   c1pwal_+0
        sta.w   c1pwah_+0
        bne     c1pwdone                ; always branch

c1norev:
        stx.w   c1pwlo_+1
        stx     $d402                   ; set c1 pulse width lo
        sta.w   c1pwhi_+1
        sta     $d403                   ; set c1 pulse width hi

c1pwdone:
        lda     ArpTab,y                ; get arpeggio byte
        asl
        bcs     c1abs                   ; absolute freq hi value (for drums)

c1note_:
        adc     #$00                    ; add to channel note
        tax

        lda     FreqTab,x
c1modulatel_:
        cmp     #mod                    ; ($c9=cmp#=vib off/ $65=adc=vib on)
        sta     $d400                   ; set c1 frequency lo
        lda     FreqTab+1,x
c1modulateh_:
        cmp     #modh                   ; ($c9=cmp#=vib off/ $65=adc=vib on)
c1abs:
        sta     $d401                   ; set c1 frequency hi

        iny
        sty.w   c1sndp_+1               ; advance c1 snd pos
c1done:


;-----  channel 2

c2:
        ldy     c2hold                  ; 0 = no hold, other = sound offset
        beq     c2sndp_

        ldx     #$ff
        stx.w   c2gate_+1               ; key down - gate on
        inx
        stx     c2hold                  ; voice reset

        lda     SoundTab,y              ; $00: attack/decay
        sta     $d405+7
        lda     SoundTab+1,y            ; $01: sustain/release
        sta     $d406+7
        lda     #$09
        sta     $d404+7                 ; testbit+gate to stabilize adsr

        lda     SoundTab+2,y            ; $02: sound pos
        sta.w   c2sndp_+1
        lda     SoundTab+3,y            ; $03: sound end
        sta.w   c2snde_+1
        lda     SoundTab+4,y            ; $04: sound loop
        sta.w   c2snd8_+1

        lda     SoundTab+5,y            ; $05: pw init ($00 = no init)
        beq     c2done

        sta.w   c2pwhi_+1
        lda     SoundTab+6,y            ; $06: pw mod rate
        sta.w   c2pwal_+1
        lda     SoundTab+7,y            ; $07: pw mod top
        sta.w   c2ptop_+1
        lda     SoundTab+8,y            ; $08: pw mod bottom
        sta.w   c2pbot_+1

        bpl     c2done                  ; always branch

c2sndp_:
        ldy     #$00                    ; c2 snd pos
        beq     c2done
c2snde_:
        cpy     #$00                    ; c2 snd end
        bne     c2nolp
c2snd8_:
        ldy     #$00                    ; c2 snd loop

c2nolp:
        lda     WaveTab,y               ; get waveform
c2gate_:
        and     #$fe                    ; gate on/off 
        sta     $d404+7                 ; set channel waveform

c2pwlo_:
        lda     #$55
c2pwal_:
        sbc     #$02
        tax
c2pwhi_:
        lda     #$08
c2pwah_:
        sbc     #$00

c2ptop_:
        cmp     #$10                    ; pulse width top limit
        beq     c2pwrev
c2pbot_:
        cmp     #$00                    ; pulse width bottom limit
        bne     c2norev

c2pwrev:
        lda.w   c2pwal_+0               ; reverse pulse direction
        eor     #$80                    ; morph between adc/sbc
        sta.w   c2pwal_+0
        sta.w   c2pwah_+0
        bne     c2pwdone                ; always branch

c2norev:
        stx.w   c2pwlo_+1
        stx     $d402+7                 ; set c2 pulse width lo
        sta.w   c2pwhi_+1
        sta     $d403+7                 ; set c2 pulse width hi

c2pwdone:
        lda     ArpTab,y                ; get arpeggio byte
        asl
        bcs     c2abs                   ; absolute freq hi value (for drums)

c2note_:
        adc     #$00                    ; add to channel note
        tax

        lda     FreqTab,x
c2modulatel_:
        cmp     #mod                    ; ($c9=cmp#=vib off/ $65=adc=vib on)
        sta     $d400+7                 ; set c2 frequency lo
        lda     FreqTab+1,x
c2modulateh_:
        cmp     #modh                   ; ($c9=cmp#=vib off/ $65=adc=vib on)
c2abs:
        sta     $d401+7                 ; set c2 frequency hi

        iny
        sty.w   c2sndp_+1               ; advance c2 snd pos
c2done:


;-----  channel 3

c3:
        ldy     c3hold                  ; 0 = no hold, other = sound offset
        beq     c3sndp_

        ldx     #$ff
        stx.w   c3gate_+1               ; key down - gate on
        inx
        stx     c3hold                  ; voice reset

        lda     SoundTab,y              ; $00: attack/decay
        sta     $d405+14
        lda     SoundTab+1,y            ; $01: sustain/release
        sta     $d406+14
        lda     #$09
        sta     $d404+14                ; testbit+gate to stabilize adsr

        lda     SoundTab+2,y            ; $02: sound pos
        sta.w   c3sndp_+1
        lda     SoundTab+3,y            ; $03: sound end
        sta.w   c3snde_+1
        lda     SoundTab+4,y            ; $04: sound loop
        sta.w   c3snd8_+1

        lda     SoundTab+5,y            ; $05: pw init ($00 = no init)
        beq     c3done

        sta.w   c3pwhi_+1
        lda     SoundTab+6,y            ; $06: pw mod rate
        sta.w   c3pwal_+1
        lda     SoundTab+7,y            ; $07: pw mod top
        sta.w   c3ptop_+1
        lda     SoundTab+8,y            ; $08: pw mod bottom
        sta.w   c3pbot_+1

        bpl     c3done                  ; always branch


c3sndp_:
        ldy     #$00                    ; c3 snd pos
        beq     c3done
c3snde_:
        cpy     #$00                    ; c3 snd end + 1
        bne     c3nolp
c3snd8_:
        ldy     #$00                    ; c3 snd loop

c3nolp:
        lda     WaveTab,y               ; get waveform
c3gate_:
        and     #$fe                    ; gate on/off 
        sta     $d404+14                ; set channel waveform

c3pwlo_:
        lda     #$aa
c3pwal_:
        adc     #$02
        tax
c3pwhi_:
        lda     #$08
c3pwah_:
        adc     #$00

c3ptop_:
        cmp     #$10                    ; pulse width top limit
        beq     c3pwrev
c3pbot_:
        cmp     #$00                    ; pulse width bottom limit
        bne     c3norev

c3pwrev:
        lda.w   c3pwal_+0               ; reverse pulse direction
        eor     #$80                    ; morph between adc/sbc
        sta.w   c3pwal_+0
        sta.w   c3pwah_+0
        bne     c3pwdone                ; always branch

c3norev:
        stx.w   c3pwlo_+1
        stx     $d402+14                ; set c3 pulse width lo
        sta.w   c3pwhi_+1
        sta     $d403+14                ; set c3 pulse width hi

c3pwdone:
        lda     ArpTab,y                ; get arpeggio byte
        asl
        bcs     c3abs                   ; absolute freq hi value (for drums)

c3note_:
        adc     #$00                    ; add to channel note
        tax

        lda     FreqTab,x
c3modulatel_:
        cmp     #mod                    ; ($c9=cmp#=vib off/ $65=adc=vib on)
        sta     $d400+14                ; set c3 frequency lo
        lda     FreqTab+1,x
c3modulateh_:
        cmp     #modh                   ; ($c9=cmp#=vib off/ $65=adc=vib on)
c3abs:
        sta     $d401+14                ; set c3 frequency hi

        iny
        sty.w   c3sndp_+1               ; write back
c3done:


;*****  SEQUENCER  *********************************************************

seq:
        lda     speed
        dec     count
        beq     nextstep

        lsr
        cmp     count
        beq     halfstep

        lda     cmdtick
        beq     nocmdtick


;-----  check and execute command

getcmd:
        ldy     #$00                    ; clear cmdtick
        sty     cmdtick

        lax     (step),y                ; get cmd
        beq     nocmd

        lda.w   cmdjmpL-1,x
        sta.w   docmd_+1

        iny
        lax     (step),y                ; get cmd parameter

.IF COMPILE_PLAYER == 2
        lda     step                    ; advance note pointer
        clc
        adc     #$02
        sta     step
        bcc     _chnoc
        inc     block
_chnoc:

docmd_:
        jmp     setfilter


nocmd:
        inc     step
        bne     _cnonoc
        inc     block
_cnonoc:

.ELSE
        lda     step                    ; advance to next step
        clc
        adc     #$08
        sta     step

docmd_:
        jmp     setfilter


nocmd:
        lda     step                    ; advance to next step
        clc
        adc     #$08
        sta     step
.ENDIF

nocmdtick:


;-----  vibrato

vibrate_:
        lda     #$00
        beq     _vibdone
        clc

        adc     vibpos
        and     #$0f
        sta     vibpos
        tay

        lda.w   VibTab,y
vibwidth_:
        cmp     #$ea

        sta     mod
        lda.w   VibTab+$10,y
        sta     modh
_vibdone:
        rts


;-----  next step, get notes

nextstep:
        sta     count

halfstep:

.IF COMPILE_PLAYER == 2
getnotes:
getc1:
        ldx     #$00                    ; reset channel byte

        ldy     #$00                    ; get c1 note
        lda     (step),y
        beq     getc1done               ; no note
        bpl     c1notie                 ; normal note

        cmp     #$ff                    ; check if 'no notes on line'
        beq     packedreadok

        sta.w   c1gate_+1               ; must be $fe (gate off mask)
        bne     getc1done               ; always branch

c1notie:
        sta.w   c1note_+1               ; set c1 note
        iny
        lda     (step),y                ; get c1 sound
        beq     getc1done               ; tied note, no trig

        sta     c1hold                  ; init sound next frame

        stx     $d406
        stx     $d404                   ; reset channel
getc1done:


getc2:
        iny                             ; get c2 note
        lda     (step),y
        beq     getc2done               ; no note
        bpl     c2notie                 ; normal note

        cmp     #$ff                    ; check if 'no more notes on line'
        beq     packedreadok

        sta.w   c2gate_+1               ; must be $fe (gate off mask)
        bne     getc2done               ; always branch

c2notie:
        sta.w   c2note_+1               ; set c2 note
        iny
        lda     (step),y                ; get c2 sound
        beq     getc2done               ; tied note, no trig
        
        sta     c2hold                  ; init sound next frame

        stx     $d406+7
        stx     $d404+7                 ; reset channel
getc2done:


getc3:
        iny                             ; get c3 note
        lda     (step),y
        beq     getc3done               ; no note
        bpl     c3notie                 ; normal note

        sta.w   c3gate_+1               ; must be $fe (gate off mask)
        bmi     getc3done               ; always branch

c3notie:
        sta.w   c3note_+1               ; set c3 note
        iny
        lda     (step),y                ; get c3 sound
        beq     getc3done               ; tied note, no trig

        sta     c3hold                  ; init sound next frame

        stx     $d406+14
        stx     $d404+14                ; reset channel
getc3done:


packedreadok:
        iny
        sty     cmdtick                 ; (set flag: process cmd next frame)

        tya
        clc
        adc     step                    ; advance note pointer
        sta     step
        bcc     _prnoc
        inc     block
_prnoc:
        rts

.ELSE
getnotes:
getc1:
        ldx     #$00                    ; reset channel byte

        ldy     #$02                    ; get c1 note
        sty     cmdtick                 ; (set flag: process cmd next frame)
        lda     (step),y
        beq     getc1done               ; no note
        bpl     c1notie                 ; normal note

        sta.w   c1gate_+1               ; must be $fe (gate off mask)
        bmi     getc1done               ; always branch

c1notie:
        sta.w   c1note_+1               ; set c1 note
        iny
        lda     (step),y                ; get c1 sound
        beq     getc1done               ; tied note, no trig

        sta     c1hold                  ; init sound next frame

        stx     $d406
        stx     $d404                   ; reset channel
getc1done:


getc2:
        ldy     #$04                    ; get c2 note
        lda     (step),y
        beq     getc2done               ; no note
        bpl     c2notie                 ; normal note

        sta.w   c2gate_+1               ; must be $fe (gate off mask)
        bmi     getc2done               ; always branch

c2notie:
        sta.w   c2note_+1               ; set c2 note
        iny
        lda     (step),y                ; get c2 sound
        beq     getc2done               ; tied note, no trig
        
        sta     c2hold                  ; init sound next frame

        stx     $d406+7
        stx     $d404+7                 ; reset channel
getc2done:


getc3:
        ldy     #$06                    ; get c3 note
        lda     (step),y
        beq     getc3done               ; no note
        bpl     c3notie                 ; normal note

        sta.w   c3gate_+1               ; must be $fe (gate off mask)
        rts

c3notie:
        sta.w   c3note_+1               ; set c3 note
        iny
        lda     (step),y                ; get c3 sound
        beq     getc3done               ; tied note, no trig

        sta     c3hold                  ; init sound next frame

        stx     $d406+14
        stx     $d404+14                ; reset channel
getc3done:
        rts
.ENDIF


;*****  BLOCK COMMANDS  ****************************************************

;       entry points must be located on the same memory page!

setfilter:
        stx     fbase                   ; cmd 3: Flt - set cutoff base
        rts
setspeed:
        stx     speed                   ; cmd 4: Tmp - set speed
        dex                             ; i got rhythm
        stx     count
        rts

offchannel:                             ; cmd 8: Off - channel mod off
        lda     #$c9                    ; $c9=cmp#=vib off
        bmi     _modchange
modchannel:                             ; cmd 7: Mod - channel mod on
        lda     #$65                    ; $65=adc=vib on
_modchange:
        cpx     #$03
        beq     setc3mod
        dex
        beq     setc1mod
        bne     setc2mod

setvibwidth:
        cpx     #$03                    ; cmd 5: Ini - init vibrato
        bcs     _badinit

        lda.w   vibwidthcmd,x           ; set vibrato width
        sta.w   vibwidth_
        lda.w   vibwidthcmd+1,x
        sta.w   vibwidth_+1
        ldx     #$00
        stx     mod
        stx     modh
        stx     vibpos                  ; retrig vibrato
        ;
setvibrate:
;---
        stx.w   vibrate_+1              ; cmd 6: Vib - set vibrato rate
_badinit:
        rts

.IF COMPILE_PLAYER == 2
blockbreak:
nextblock:
        ldy     seqpos
        iny
        iny
_regetblock:
        sty     seqpos

firstblockentry:
        lda     Sequencer,y             ; get block address high byte
        bne     newblock

        lda     Sequencer+1,y           ; sequencer loop
        tay
        bpl     _regetblock

newblock:
        sta     block
        lda     Sequencer+1,y           ; get block address low byte
        sta     step

        rts

.ELSE
blockbreak:
        lda     #$00                    ; cmd 2: Brk - block break
        sta     step

nextblock:
        inc     seqpos                  ; cmd 1: End - normal block

firstblockentry:
        ldy     seqpos

        lda     Sequencer,y             ; get block number
        bne     newblock

        ldx     Sequencer+1,y           ; sequencer loop
        stx     seqpos
        lda     Sequencer,x

newblock:
        clc
        adc     #(BlockData/256)-1
        sta     block
        rts
.ENDIF

setc1mod:
        sta.w   c1modulatel_
        sta.w   c1modulateh_
        rts
setc2mod:
        sta.w   c2modulatel_
        sta.w   c2modulateh_
        rts
setc3mod:
        sta.w   c3modulatel_
        sta.w   c3modulateh_
        rts


;*****  INITIALIZE  ********************************************************

.IF COMPILE_PLAYER == 2

Initialize:
        lda     #$00
        ldx     #$0c
_clr:
        sta     cmdtick,x               ; clear zero page variables
        sta     $d400,x
        sta     $d40b,x
        dex
        bpl     _clr

        tay
        lda     #$0f
        sta     $d418                   ; set volume
        lda     #$0c
        sta     speed                   ; initial song speed
        inc     count                   ; first step next frame

        bne     firstblockentry         ; prepare first block

.ELSE

Initialize:
        lda     #$00
        ldx     #$0c
_clr:
        sta     cmdtick,x               ; clear zero page variables
        sta     $d400,x
        sta     $d40b,x
        dex
        bpl     _clr

        lda     #$0f
        sta     $d418                   ; set volume
        lda     #$0c
        sta     speed                   ; initial song speed
        inc     count                   ; first step next frame

        bne     firstblockentry         ; prepare first block
.ENDIF

vibwidthcmd:                            ; x  vi,x  vi+1,x  width multiplier
        .DB     $c9                     ; 0  cmp#  nop     x1
        .DB     $ea                     ; 1  nop   asl     x2
        asl                             ; 2  asl   asl     x4
        asl
        
cmdjmpL:
        .DB     nextblock&255
        .DB     blockbreak&255
        .DB     setfilter&255
        .DB     setspeed&255
        .DB     setvibwidth&255
        .DB     setvibrate&255
        .DB     modchannel&255
        .DB     offchannel&255
.ENDS


;*****  FREQUENCY TABLE  ***************************************************

.ORG    FreqTab
.SECTION "freqtable" FORCE
        .INCBIN "64freq.bin"

.ENDS


;*****  MUSIC DATA  ********************************************************

.ORG    Music
.SECTION "music" FORCE

.IF COMPILE_PLAYER == 2
        .INCBIN "packtest.bin"
.ELSE
        .INCBIN "presets.bin"
.ENDIF

.ENDS


.IF COMPILE_PLAYER == 0

;*****  EDITOR  ************************************************************

.ORG    $0801
.SECTION "run" FORCE

        .DB     $0b,$08,$01,$00,$9e,$32,$30,$36,$31     ;"1 sys2061"
        .DB     $00,$00,$00

Go:
        jmp     Editor


;-----  save executable player

.DEFINE xpchar          $fb                     ; scroll pos addr
.DEFINE xpfin           $fc                     ; scroll fine addr
.DEFINE xpscry          $40                     ; scroll y-line

        sei
        jsr     $1000

        lda     #$16
        sta     $d018

        ldy     #$00
        sty     $d020
        sty     $d021

_xpinit:
        lda.w   xptoptext,y
        sta     $0400,y
        lda.w   xpbottext,y
        sta     $0700,y
        lda     #$20
        sta     $0500,y
        sta     $0600,y
        lda     #$01
        sta     $d800,y
        lda     #$0f
        sta     $d900,y
        sta     $da00,y
        sta     $db00,y
        iny
        bne     _xpinit

        lda     #$30                    ; 1 second delay before playing
        sta     count

        lda     #$00
        sta     xpchar
        lda     #$07
        sta     xpfin

xpframeloop:
        lda     #$08
        sta     $d016

        lda     xpfin
        ldx     #xpscry
_xpscrtop:
        cpx     $d012
        bne     _xpscrtop

        sta     $d016

        lda     #$08

        ldx     #xpscry+16
_xpscrbot:
        cpx     $d012
        bne     _xpscrbot

        sta     $d016

        dec     xpfin
        bpl     _xpnonewchar

        lda     #$07
        sta     xpfin

        ldy     #$00
_xpleap:
        lda.w   $0401+$28*2,y
        sta.w   $0400+$28*2,y
        iny
        cpy     #$27
        bne     _xpleap

        ldy     xpchar
        lda.w   xpscroller,y
        sta.w   $0427+$28*2

_xpskipspaces:
        iny
        cpy     #$90
        bne     _xpnowrap

        ldy     #$00
_xpnowrap:
        cmp     #$20                    ; last character a space?
        bne     _xpnospace

        lda.w   xpscroller,y            ; multiple spaces -> one space
        cmp     #$20
        beq     _xpskipspaces

_xpnospace:
        sty     xpchar

_xpnonewchar:
        lda     #$0c
        ldx     #$fc
_xpwaitfc:
        cpx     $d012
        bne     _xpwaitfc
        sta     $d020
        jsr     $1003

        lda     #$00
        sta     $d020
        beq     xpframeloop


xpscroller:
        .DSB    $90 $20

xptoptext:
        .DSB    $100 $20

xpbottext:
        .INCBIN "xpbottext.bin"


.ENDS

.INCLUDE "editor.asm"
.ENDIF
