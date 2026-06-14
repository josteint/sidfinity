;       Compile with WLA-6510 (http://www.hut.fi/~vhelin/wla.html)


.DEFINE dest            $f7
.DEFINE desth           $f8
.DEFINE source          $f9
.DEFINE sourceh         $fa

.DEFINE dataend         $0100
.DEFINE dataendh        $0101


;*****  BLOCK PACKER  ******************************************************

BlockPack:
        ldy     #$00
_seeklast:
        lda     Sequencer,y             ; find last step in sequencer
        beq     _lastseq
        iny
        cpy     #$40
        bne     _seeklast

_lastseq:
        iny                             ; space for loop mark
        tya
        asl
        clc
        adc     #$c0
        sta     dest
        lda     #$65
        adc     #$00
        sta     desth                   ; address of first packed block

        lda     #$00
        ldy     #$3f
_clrtmpb:
        sta     $65c0,y                 ; packed player sequencer
        sta     $6000,y                 ; temporary block address map
        sta     $6040,y
        dey
        bpl     _clrtmpb

        ldy     #$00                    ; sequencer position
_packnextblock:
        tya
        pha

        ldx.w   Sequencer,y
        beq     _packendloop
        jsr     PackOneBlock

        pla
        tay
        iny
        jmp     _packnextblock

_packendloop:
        pla
        ldx.w   Sequencer+1,y           ; get loop position
        tya
        asl
        tay
        lda     #$00
        sta     $65c0,y                 ; 'loop'
        txa
        asl                             ; ahem almost forgot this
        sta     $65c1,y                 ; loop position

        ldy     #$00

        ldx     #$00
_songt:
        lda     $3500,x                 ; add song tag
        jsr     _byteout
        inx
        cpx     #$18
        bne     _songt

        ldx     #$00
_tagit:
        lda.w   PackedTag,x             ; add john player tag
        jsr     _byteout
        inx
        cpx     #$18
        bne     _tagit

        lda     dest                    ; end of packed data
        sta.w   dataend
        lda     desth
        sec
        sbc     #$50
        sta.w   dataendh

        rts


PackedTag:
        .DB     " JOHN PLAYER BY A. EEBEN"


;-----  pack one block in sequencer step y, block number in x

PackOneBlock:
        tya
        asl
        tay

        lda     $6000,x                 ; same block packed earlier?
        beq     _notpackedyet

        sta     $65c0,y
        lda     $6040,x
        sta     $65c1,y

        rts


_notpackedyet:
        lda     desth                   ; store packed block address
        clc
        adc     #$b0
        sta     $65c0,y                 ; unusual byte order
        sta     $6000,x
        lda     dest
        sta     $65c1,y
        sta     $6040,x

        txa
        clc
        adc     #(BlockData/256)-1
        sta     sourceh
        ldy     #$00
        sty     source

        ldx     #$20                    ; lines in block

_nextline:
        ldy     #$07
_buf:
        lda     (source),y              ; buffer line
        sta.w   buffer,y

        dey
        bpl     _buf

        iny                             ; zero

        lda     source                  ; advance to next line in block
        clc
        adc     #$08
        sta     source

;----   check if no notes on line

        lda.w   buffer+2
        bne     _notempty
        lda.w   buffer+4
        bne     _notempty
        lda.w   buffer+6
        bne     _notempty

        lda     #$ff                    ; output 'no notes on line'
        jsr     _byteout
        jmp     _cmdout

_notempty:

;----   channel 1

        lda.w   buffer+2                ; c1 note
        beq     _c1onebyte
        bmi     _c1onebyte

        jsr     _byteout                ; output note
        lda.w   buffer+3                ; get sound number

_c1onebyte:
        jsr     _byteout                ; output $00 or $fe or sound number

;----   check if no notes on channels 2 and 3

        lda.w   buffer+4
        bne     _notemptyb
        lda.w   buffer+6
        bne     _notemptyb

        lda     #$ff                    ; output 'no more notes on line'
        jsr     _byteout
        jmp     _cmdout

_notemptyb:

;-----  channel 2

        lda.w   buffer+4                ; c2 note
        beq     _c2onebyte
        bmi     _c2onebyte

        jsr     _byteout                ; output note
        lda.w   buffer+5                ; get sound number

_c2onebyte:
        jsr     _byteout                ; output $00 or $fe or sound number

;-----  channel 3

        lda.w   buffer+6                ; c3 note
        beq     _c3onebyte
        bmi     _c3onebyte

        jsr     _byteout                ; output note
        lda.w   buffer+7                ; get sound number

_c3onebyte:
        jsr     _byteout                ; output $00 or $fe or sound number

;-----  command

_cmdout:
        lda.w   buffer
        beq     _cmdonebyte

        jsr     _byteout                ; output cmd

        cmp     #$02                    ; skip rest of block if 'brk'
        beq     _blockend

        cmp     #$01                    ; no parameter needed for 'end'
        beq     _linedone

        lda.w   buffer+1                ; get cmd parameter

_cmdonebyte:
        jsr     _byteout                ; output 'no cmd' or cmd parameter

_linedone:
        dex
        beq     _blockend
        jmp     _nextline               ; next line in block

_blockend:
        rts


;-----  byte out

_byteout:
        sta     (dest),y

        inc     dest
        bne     _nocd
        inc     dest+1
_nocd:
        rts


buffer:
        .DB     $00,$00,$00,$00,$00,$00,$00,$00


;*****  MUSIC FILE PACKER  *************************************************


.DEFINE rlecode $a7
.DEFINE musicend $36

;-----  pack music from $1400-$35ff to $6000

MusicPack:
        lda     #$4a
        sta     $6000
        lda     #$4f
        sta     $6001
        lda     #$48
        sta     $6002
        lda     #$4e
        sta     $6003

        lda     #$14
        sta     source+1
        lda     #$60
        sta     dest+1
        lda     #$00
        sta     source
        lda     #$04
        sta     dest

_rleseek:
        ldy     #$00
        ldx     #$00
        lda     (source),y

_rlerept:
        cpy     #$ff
        beq     _rlepack
        iny
        cmp     (source),y
        beq     _rlerept

        cmp     #rlecode
        beq     _rlepack        ; escape hit

        cpy     #$04
        bcs     _rlepack        ; pack if more than 4

        sta     (dest,x)        ; write noncomp byte

        inc     source          ; advance source by 1
        bne     _rlna
        inc     source+1
_rlna:
        lda     #$01
        jmp     _rleadvdest

_rlepack:
        pha

        tya
        clc
        adc     source
        sta     source
        bcc     _rlnoca
        inc     source+1
_rlnoca:
        lda     #rlecode
        sta     (dest,x)        ; write esc
        tya

        ldx     #musicend
        cpx     source+1
        bne     _rlenotrim

        sec
        sbc     source          ; trim end of data
_rlenotrim:
        ldy     #$01
        sta     (dest),y        ; write count
        iny
        pla
        sta     (dest),y        ; write bytevalue
        
        lda     #$03

_rleadvdest:
        clc                     ; advance dest by a
        adc     dest
        sta     dest
        bcc     _rlnocb
        inc     dest+1
_rlnocb:
        ldx     #musicend
        cpx     source+1
        bne     _rleseek

_rledone:
        ldy     #$00
        lda     #rlecode
        sta     (dest),y
        iny
        lda     #$00
        sta     (dest),y

        lda     #$02
        clc
        adc     dest
        sta     dest
        bcc     _rlnoce
        inc     dest+1
_rlnoce:
        lda     dest
        sta.w   dataend
        lda     desth
        sta.w   dataendh

        rts


;-----  unpack music from $6000 to $1400

MusicUnpack:
        lda     #$4a                    ; is it really john?
        cmp     $6000
        bne     _bad
        lda     #$4f
        cmp     $6001
        bne     _bad
        lda     #$48
        cmp     $6002
        bne     _bad
        lda     #$4e
        cmp     $6003
        beq     _notbad
_bad:
        rts

_notbad:
        lda     #$60
        sta     source+1
        lda     #$14
        sta     dest+1
        lda     #$04
        sta     source
        ldy     #$00
        sty     dest

_unpackloop:
        ldy     #$00
        lda     (source),y

        cmp     #rlecode
        beq     _unpack

        sta     (dest),y

        inc     source
        bne     _munops
        inc     source+1
_munops:
        inc     dest
        bne     _unpackloop
        inc     dest+1
_munopd:
        jmp     _unpackloop

_unpack:
        iny
        lda     (source),y              ; get count
        beq     _unpackdone

        sta     tmpreg
        iny
        lda     (source),y              ; get bytevalue

        ldy     tmpreg
_reptout:
        dey

        sta     (dest),y
        bne     _reptout

        lda     tmpreg
        clc
        adc     dest
        sta     dest
        bcc     _nocda
        inc     dest+1
_nocda:
        
        lda     #$03
        clc
        adc     source
        sta     source
        bcc     _nocdb
        inc     source+1
_nocdb:
        jmp     _unpackloop

_unpackdone:
        rts

