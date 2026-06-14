.DEFINE textpos         $f7
.DEFINE textposh        $f8
.DEFINE screen          $f9
.DEFINE screenh         $fa
.DEFINE finescroll      $fd
.DEFINE scrolladd       $fe
.DEFINE flip            $ff

.DEFINE textstart       $9800
.DEFINE textend         $9800+$28*(257-26)


;*****  QUICK HELP VIEWER  *************************************************

Help:
        sei

        lda     #$0e
        sta     finescroll
        lda     #$00
        sta     $d020
        sta     $d021
        sta     scrolladd
        sta     textpos
        lda     #$04
        sta     flip

        lda     #textstart/256
        sta     textposh

        jsr     drawscreen

helploop:
        jsr     SCNKEY

        ldx     #$fc
_hlwait:
        cpx     $d012
        bne     _hlwait

        jsr     setscreen

        lda     $c5

        cmp     #$3f                    ; run/stop
        beq     _exithelp
        cmp     #$3c                    ; space
        beq     _exithelp
        cmp     #$03                    ; f7
        beq     _exithelp

        cmp     #$07                    ; cursor up/down
        bne     _nomove

        lda     $028d
        and     #$01
        beq     _moveup

        lda     scrolladd
        cmp     #$0c
        beq     _keydown
        inc     scrolladd
        jmp     _keydown

_moveup:
        lda     scrolladd
        cmp     #$f4
        beq     _keydown
        dec     scrolladd
        jmp     _keydown

_nomove:
        lda     scrolladd               ; slow down scroller if no key
        beq     _keydown
        bmi     _inctoslow
        dec     scrolladd
        jmp     _keydown
_inctoslow:
        inc     scrolladd

_keydown:

        jsr     scrollhelp
        jmp     helploop

_exithelp:
        lda     #$00                    ; clear keyboard buffer
        sta     $c6

        rts


;-----  scroll screen

scrollhelp:
        lda     scrolladd
        clc
        adc     finescroll
        sta     finescroll

        bmi     _leapup

        cmp     #$10
        bcc     _noleap

        and     #$0f
        sta     finescroll

        lda     textpos                 ; check text top
        cmp     #textstart&255
        bne     _nottopoftext
        lda     textposh
        cmp     #textstart/256
        beq     _topoftext

_nottopoftext:
        lda     textpos                 ; leap
        sec
        sbc     #$28
        sta     textpos
        lda     textposh
        sbc     #$00
        sta     textposh

        jmp     drawscreen              ; rts there
        
_topoftext:
        lda     #$0e                    ; hard stop at top
        sta     finescroll
        lda     #$00
        sta     scrolladd

_noleap:
        rts

_leapup:
        and     #$0f
        sta     finescroll

        lda     textpos                 ; check text end
        cmp     #textend&255
        bne     _notbotoftext
        lda     textposh
        cmp     #textend/256
        beq     _botoftext

_notbotoftext:
        lda     #$28                    ; leap
        clc
        adc     textpos
        sta     textpos
        lda     #$00
        adc     textposh
        sta     textposh

        jsr     drawscreen

        rts

_botoftext:
        lda     #$00                    ; hard stop at end
        sta     finescroll
        sta     scrolladd

        rts


;-----  set scroll register and visible screen buffer

setscreen:
        lda     #$36
        ldx     flip
        cpx     #$04
        bne     _not4

        lda     #$16
_not4:
        sta     $d018
        lda     finescroll
        rol
        lda     finescroll
        ror
        clc
        adc     #$10
        sta     $d011

        rts


;-----  draw new screen buffer

drawscreen:
        lda     #$00
        sta     screen
        lda     flip
        eor     #$08
        sta     flip
        sta     screenh

        lda     textposh
        pha

        lda     #$36
        sta     $01

        ldy     #$00
        ldx     #$04
_scrlp:
        lda     (textpos),y
        sta     (screen),y
        iny
        lda     (textpos),y
        sta     (screen),y
        iny
        lda     (textpos),y
        sta     (screen),y
        iny
        lda     (textpos),y
        sta     (screen),y
        iny
        bne     _scrlp

        inc     textpos+1
        inc     screen+1
        dex
        bne     _scrlp

        lda     #$37
        sta     $01

        pla
        sta     textposh

        rts

