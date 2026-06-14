.DEFINE CHRIN           $ffcf
.DEFINE CHROUT          $ffd2
.DEFINE SAVE            $ffd8
.DEFINE LOAD            $ffd5
.DEFINE SETLFS          $ffba
.DEFINE SETNAM          $ffbd
.DEFINE OPEN            $ffc0
.DEFINE CLOSE           $ffc3
.DEFINE CHKIN           $ffc6
.DEFINE READST          $ffb7
.DEFINE CLALL           $ffe7
.DEFINE STOP            $ffe1

.DEFINE TALK            $ffb4
.DEFINE TKSA            $ff96
.DEFINE UNTLK           $ffab
.DEFINE ACPTR           $ffa5

.DEFINE LISTEN          $ffb1
.DEFINE SECOND          $ff93
.DEFINE UNLSN           $ffae

.DEFINE DECOUT          $bdd1           ; BASIC ROM, print number in $62-$63


;-----  dir

DiskDir:
        sta     tmpreg                  ; set up file
        lda     #36
        sta.w   Filename                ; "$"
        lda     #$01                    ; filename length
        ldy     #$00                    ; secondary address
        jsr     SetupFile

        jsr     OPEN
        bcs     _derror

        ldx     #$01                    ; input from channel 1
        jsr     CHKIN
        bcs     _derror

        jsr     CHRIN                   ; skip header
        jsr     CHRIN

_dirlp:
        jsr     _dirline
        bcc     _dirlp                  ; carry clear if not eof

_dclose:
        lda     #$01                    ; close file
        jsr     CLOSE
        jsr     CLALL                   ; input back to keyboard
        rts

_derror:
        jsr     _dclose
        rts

_dirline:
        jsr     CHRIN                   ; skip obsolete bytes
        jsr     CHRIN

        jsr     READST                  ; check end of file
        bne     _dirend

        jsr     STOP                    ; check stop key
        beq     _dirend

        jsr     CHRIN                   ; get and print blocks
        sta     $63
        jsr     CHRIN
        sta     $62
        jsr     DECOUT

        lda     #32
        jsr     CHROUT

_dirnamelp:
        jsr     CHRIN
        jsr     CHROUT
        bne     _dirnamelp

        lda     #13
        jsr     CHROUT

_direndline:
        clc
        rts

_dirend:
        sec
        rts


;-----  disk status

DiskStatus:
        lda     #$00                    ; clear st
        sta     $90

        lda     $ba
        jsr     LISTEN                  ; check if device is present
        jsr     UNLSN

        jsr     READST
        and     #$83
        bne     _dserr

        ldy     #$0f                    ; secondary address (command)
        lda     #$00                    ; no filename
        jsr     SetupFile

        jsr     OPEN
        bcs     _derror

        ldx     #$01                    ; input from channel 1
        jsr     CHKIN

_derrout:
        jsr     CHRIN                   ; get and print disk status message
        beq     _derror
        jsr     CHROUT
        cmp     #13
        bne     _derrout

        jmp     _dclose

_dserr:
        ldy     #$00
_errl:
        lda.w   nodevice,y
        jsr     CHROUT
        iny
        cmp     #13
        bne     _errl
        rts

nodevice:
        .DB     "DEVICE NOT PRESENT",13


;-----  set up file, a = filename length, y = secondary address

SetupFile:
        pha
        lda     #$01                    ; file number
        ldx     $ba                     ; current device
        jsr     SETLFS

        pla
        ldx     #Filename&255
        ldy     #Filename/256
        jsr     SETNAM

        rts

Filename:
        .DSB    $11 $20


;-----  save file, a = filename length
;       from (source) to ($0100)

SaveFile:
        ldy     #$00
        jsr     SetupFile

        lda     #source
        ldx     $0100
        ldy     $0101

        jsr     SAVE

        rts


;-----  load file, a = filename length

LoadFile:
        ldy     #$00                    ; secondary address (reloc)
        jsr     SetupFile

        lda     #$00                    ; load flag
        ldx     #$00
        ldy     #$60                    ; load to $6000

        jsr     LOAD
        rts
