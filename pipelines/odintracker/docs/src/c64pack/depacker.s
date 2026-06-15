; ======================================
; Depack routine.
;
; Includes packed data at the end of the file.
; Set LOADADDRESS and STARTADDRESS as required.
; ======================================

DEPACKER        = $0100                 ; Fits in the stack.
LOADADDRESS     = $0810
STARTADDRESS    = $0810

dest    = $2d           ; When finished, points to end of program.
src     = $fb
string  = $fd

        processor 6502

        org $0801
; Basic tokens for the line '2001 SYS2064ZED'
        .byte $0B,$08,$D1,$07,$9E,$32,$30,$36,$34,$5a,$45,$44,$00,$00

        org $0810

; Detect SIO type.
; Output of old SID (6581) does not exceed $7f for waveform $30, while
; output of new SID (8580) does. That's what we inspect here.
        lda #$00
        tay
        ldx #$18
siddetect_clear:
        sta $d400,x
        dex
        bpl siddetect_clear
        lda #$02
        sta $d40f                       ; Voice 3 freq high byte.
        lda #$30
        sta $d412                       ; Voice 3 control register.
        inx
; X==0 and Y==0 here.
siddetect_loop:
        lda $d41b                       ; Voice 3 output.
        bmi siddetect_newfound          ; New SID generates output.
        dex
        bne siddetect_loop
        dey
        bne siddetect_loop
; Output didn't go over $80 in the 65536 step loop -> old SID.
        lda #<oldsidtext
        ldy #>oldsidtext
        bne siddetect_found             ; Jumps always.
siddetect_newfound:
        lda #<newsidtext
        ldy #>newsidtext
siddetect_found:
        jsr $ab1e
        lda #<foundtext
        ldy #>foundtext
        jsr $ab1e

        sei
        lda #$34
        sta $01
        ldy #DEPACKLEN
copydepacker:
        lda depackstart-1,y
        sta DEPACKER-1,y
        dey
        bne copydepacker

; Copy to top of mem. src and dest are reversed in their meaning!
        sty src
        sty src+1
        ldx #DATAPAGES
copyup_loop:
        dec copyup_innerloop+2
        dec src+1
copyup_innerloop:
        lda datastart+256*DATAPAGES,y
        sta (src),y
        iny
        bne copyup_innerloop
        dex
        bne copyup_loop
        lda #<LOADADDRESS
        sta dest
        lda #>LOADADDRESS
        sta dest+1
        jmp DEPACKER

oldsidtext:
        .byte $4f,$4c,$44,$20,$28,$36,$35,$38,$31,$00   ; old (6581
newsidtext:
        .byte $4e,$45,$57,$20,$28,$38,$35,$38,$30,$00   ; new (8580
foundtext:
        .byte $29,$20,$53,$49,$44,$20,$46,$4f,$55,$4e,$44,$2e,$00       ; ) sid found.

; Depacker.
depackstart:
        rorg DEPACKER

depackloop:
        jsr getbyte
        lsr
        beq depackready
        bcs compressedblock

; Uncompressed block.
        tax
uncompressedloop:
        jsr getbyte
        jsr putbyte
        dex
        bne uncompressedloop
        beq depackloop

; RLE or string block.
compressedblock:
        lsr
        tax
        bcs stringblock

; RLE block.
        jsr getbyte
rleloop:
        jsr putbyte
        dex
        bne rleloop
        beq depackloop

stringblock:
        jsr getbyte
        clc
        adc dest
        sta string
        php
        jsr getbyte
        plp
        adc dest+1
        sta string+1
stringblockloop:
        lda (string),y
        inc string
        bne getstringbyteok
        inc string+1
getstringbyteok:
        jsr putbyte
        dex
        bne stringblockloop
        beq depackloop

; Read packed byte.
getbyte:
        lda (src),y
        inc src
        bne getbyteok
        inc src+1
getbyteok:
        rts

; Write unpacked byte.
putbyte:
        sta (dest),y
        inc dest
        bne putbyteok
        inc dest+1
putbyteok:
        rts

depackready:
        lda #$37
        sta $01
; Clear screen from right to left. Clever, eh?
        ldy #39
spalsh_nextframe:
        lda #$fa
splash_waitraster:
        cmp $d012
        bne splash_waitraster
        lda #$00
        sta src
        sta string
        lda #$04
        sta src+1
        lda #$d8
        sta string+1
        ldx #25
spalsh_nextline:
        lda #$a0
        sta (src),y
        lda $d020
        sta (string),y
        lda src
        clc
        adc #40
        sta src
        sta string
        lda src+1
        adc #0
        sta src+1
        adc #$d4
        sta string+1
        dex
        bne spalsh_nextline
        dey
        bpl spalsh_nextframe
; Start user's code.
        ldx #$ff
        txs
        cli
        jmp STARTADDRESS

        rend

DEPACKLEN       = *-depackstart

datastart:
        incbin packed.bin
dataend:
DATAPAGES       = >(dataend-datastart+$ff)
