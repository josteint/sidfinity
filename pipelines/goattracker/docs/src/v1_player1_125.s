;ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
;บMusicroutine 11.1 by Lasse ”rni, September 2001.                            บ
;ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ

                processor 6502
                org $1000

        ; "Virtual addresses" just for relocation

mt_instad       = $4000
mt_instsr       = $4001
mt_instpulse    = $4002
mt_instpulsespd = $4003
mt_instpulselow = $4004
mt_instpulsehigh = $4005
mt_instfilter   = $4006
mt_instwave     = $4007

mt_wavetbl    = $5000
mt_notetbl    = $5100

mt_songtbllo    = $6000
mt_songtblhi    = $7000
mt_patttbllo    = $8000
mt_patttblhi    = $9000

        ; Defines for the music data.
        ; Patterndata 1st byte: repeat prefix or note

C0              = $00
CIS0            = $01
D0              = $02
DIS0            = $03
E0              = $04
F0              = $05
FIS0            = $06
G0              = $07
GIS0            = $08
A0              = $09
B0              = $0a
H0              = $0b
C1              = $0c
CIS1            = $0d
D1              = $0e
DIS1            = $0f
E1              = $10
F1              = $11
FIS1            = $12
G1              = $13
GIS1            = $14
A1              = $15
B1              = $16
H1              = $17
C2              = $18
CIS2            = $19
D2              = $1a
DIS2            = $1b
E2              = $1c
F2              = $1d
FIS2            = $1e
G2              = $1f
GIS2            = $20
A2              = $21
B2              = $22
H2              = $23
C3              = $24
CIS3            = $25
D3              = $26
DIS3            = $27
E3              = $28
F3              = $29
FIS3            = $2a
G3              = $2b
GIS3            = $2c
A3              = $2d
B3              = $2e
H3              = $2f
C4              = $30
CIS4            = $31
D4              = $32
DIS4            = $33
E4              = $34
F4              = $35
FIS4            = $36
G4              = $37
GIS4            = $38
A4              = $39
B4              = $3a
H4              = $3b
C5              = $3c
CIS5            = $3d
D5              = $3e
DIS5            = $3f
E5              = $40
F5              = $41
FIS5            = $42
G5              = $43
GIS5            = $44
A5              = $45
B5              = $46
H5              = $47
C6              = $48
CIS6            = $49
D6              = $4a
DIS6            = $4b
E6              = $4c
F6              = $4d
FIS6            = $4e
G6              = $4f
GIS6            = $50
A6              = $51
B6              = $52
H6              = $53
C7              = $54
CIS7            = $55
D7              = $56
DIS7            = $57
E7              = $58
F7              = $59
FIS7            = $5a
G7              = $5b
GIS7            = $5c
A7              = $5d
KEYOFF          = $5e           ;Keyoff clears the gatebit
REST            = $5f
NOCMD           = $60           ;Instrument & command byte do not exist
FIRSTPACKEDREST = $c0
PACKEDREST      = $00
ENDPATT         = $ff

        ; Patterndata 2nd byte: Instrument number and command ORed with each
        ; other

INST0           = $00           ;There's a maximum of 32 instruments
INST1           = $08
INST2           = $10
INST3           = $18
INST4           = $20
INST5           = $28
INST6           = $30
INST7           = $38
INST8           = $40
INST9           = $48
INST10          = $50
INST11          = $58
INST12          = $60
INST13          = $68
INST14          = $70
INST15          = $78
INST16          = $80
INST17          = $88
INST18          = $90
INST19          = $98
INST20          = $a0
INST21          = $a8
INST22          = $b0
INST23          = $b8
INST24          = $c0
INST25          = $c8
INST26          = $d0
INST27          = $d8
INST28          = $e0
INST29          = $e8
INST30          = $f0
INST31          = $f8

CMD_ARPEGGIO    = $00
CMD_PORTAMENTO  = $01
CMD_SETCUTOFFADD = $02
CMD_TONEPORTA   = $03
CMD_VIBRATO     = $04
CMD_SETFILTER   = $05
CMD_SETSUSTAIN  = $06
CMD_SETTEMPO    = $07

        ; Sequencedata: Values $00-$fe are pattern numbers and $ff loops song
        ; (followed by restart point)

LOOPSONG        = $ff

        ; Used zeropage temp variables

mt_temp1        = $fc
mt_temp2        = $fd
mt_temp3        = $fe

                jmp init
                jmp play
setvolume:      sta mt_volume+1
                rts

init:           sta playflag+1
                rts

play:           ldx #$00
playflag:       lda #$00
                bmi mt_play
                asl
                adc playflag+1
                tay
mt_initloop:    lda mt_songtbllo,y
                sta mt_chnsongadrlo,x
                lda mt_songtblhi,y
                sta mt_chnsongadrhi,x
                iny
                lda #$00
                sta mt_chnsongptr,x
                sta mt_chnwavetbl,x
                sta mt_chnpulsedir,x
                sta $d404,x
                lda #$05
                sta mt_chntick,x
                sta mt_chntempo,x
                sta mt_chnnewnote,x
                lda #ENDPATT
                sta mt_chnpattptr,x
                sta playflag+1
                lda mt_chnnext,x
                tax
                bne mt_initloop
                sta $d415
                sta mt_filtctrl+1
                sta mt_filtcutoffadd+1
                rts

mt_play:        clc
mt_filtcutoff:  lda #$00
mt_filtcutoffadd:adc #$00
                sta mt_filtcutoff+1
                sta $d416
mt_filtctrl:    lda #$00
                sta $d417
mt_filttype:    lda #$00
mt_volume:      ora #$0f
                sta $d418
mt_chnloop:     ldy mt_chntick,x
                beq mt_newnotes
                bpl mt_noreload
                ldy mt_chntempo,x
mt_noreload:    dey
                tya
                sta mt_chntick,x
                lda mt_chnpattptr,x             ;Check for pattern end
                cmp #ENDPATT
                bcs mt_nextpatt
mt_nonextpatt:  jmp mt_effects
mt_nextpatt:    inc mt_chnpattptr,x
                ldy mt_chnsongptr,x
                lda mt_chnsongadrlo,x
                sta mt_temp1
                lda mt_chnsongadrhi,x
                sta mt_temp2
                lda (mt_temp1),y
                cmp #LOOPSONG
                bcc mt_noloopsong
                iny
                lda (mt_temp1),y
                tay
                lda (mt_temp1),y
mt_noloopsong:  sta mt_chnpattnum,x
                iny
                tya
                sta mt_chnsongptr,x
                lda mt_chnnewnote,x
                bne mt_nextpatt_nonewnote
                jmp mt_newnoteinit
mt_nextpatt_nonewnote:
                jmp mt_pulseok2

mt_packedrest:  inc mt_chnnewnote,x
                bpl mt_newpackedrest
                lda mt_chnnewnote,x
                cmp #$ff
                bne mt_packedrestnotover
mt_packedrestover:
                tya
                sta mt_chnpattptr,x
                lda #$01
mt_newpackedrest:
                sta mt_chnnewnote,x
mt_packedrestnotover:
                ldy mt_chncommand,x
                bpl mt_rest

mt_newnotes:    lda #$ff
                sta mt_chntick,x
                ldy mt_chnpattnum,x
                lda mt_patttbllo,y
                sta mt_temp1
                lda mt_patttblhi,y
                sta mt_temp2
                ldy mt_chnpattptr,x
                lda (mt_temp1),y
                iny
                cmp #NOCMD                      ;Do command+databytes exist?
                bcc mt_cmd
                cmp #FIRSTPACKEDREST
                bcs mt_packedrest
                sbc #NOCMD-1
                sta mt_temp3
                bcs mt_nocmd
mt_cmd:         sta mt_temp3
                lda (mt_temp1),y
                and #$f8
                beq mt_skipinst                 ;Instrument number 0 lets
                sta mt_chninstnum,x             ;the instrument stay the same
mt_skipinst:    lda (mt_temp1),y
                and #$07
                sta mt_chncommand,x
                iny
                lda (mt_temp1),y
                sta mt_chncmddata,x
                iny
mt_nocmd:       lda (mt_temp1),y
                cmp #ENDPATT
                beq mt_endpatt
                tya
mt_endpatt:     sta mt_chnpattptr,x
                ldy mt_chncommand,x
                lda mt_temp3
                cmp #KEYOFF                   ;Keyoff or rest?
                beq mt_keyoff
                bcs mt_rest
mt_normalnote:  sta mt_chnnote,x
                cpy #CMD_TONEPORTA            ;Or toneportamento?
                beq mt_rest
                lda #$00
                sta mt_chnnewnote,x           ;Otherwise, normal new note
                sta $d405,x                   ;and hard restart!
                sta $d406,x
mt_keyoff:      lda mt_chnwave,x              ;Keyoff: reset gatebit
                and #$fe
                sta $d404,x
mt_rest:        lda mt_tick0cmdtbllo,y
                sta mt_tick0jump+1
                lda mt_chncmddata,x
mt_tick0jump:   jmp mt_setfilter

mt_newnoteinit: lda #$01
                sta mt_chnnewnote,x
                lda #$fe
                sta mt_chnarpcount,x
                sta mt_chnvibcount,x
                ldy mt_chninstnum,x
                lda mt_instfilter,y
                beq mt_nofilterchange
                sta mt_filtcutoff+1
                asl
                asl
                asl
                asl
                sta mt_filttype+1
mt_nofilterchange:
                lda mt_instpulse,y
                beq mt_skippulse
                sta mt_chnpulse,x
                sta $d402,x
                sta $d403,x
                lda #$80
                bne mt_skippulse2
mt_skippulse:   lda mt_chnpulsedir,x
                ora #$80
mt_skippulse2:  sta mt_chnpulsedir,x
                jmp mt_nextchn

mt_effects:     lda mt_chnnewnote,x
                beq mt_newnoteinit
                ldy mt_chninstnum,x
mt_pulsemod:    lda mt_chnpulsedir,x
                bpl mt_noadsrinit
                and #$7f
                sta mt_chnpulsedir,x
                stx mt_temp1
                ldx mt_instwave,y
                lda mt_wavetbl,x
                ldx mt_temp1
                sta mt_chnwave,x
                sta $d404,x
                lda mt_instad,y
                sta $d405,x
                lda mt_instsr,y
                sta $d406,x
                lda mt_instwave,y
                tay
                bne mt_skipwave

mt_noadsrinit:  lsr
                lda mt_chnpulse,x
                bcs mt_pulsesub
                adc mt_instpulsespd,y
                adc #$00
                sta mt_chnpulse,x
                sta $d402,x
                sta $d403,x
                and #$0f
                cmp mt_instpulsehigh,y
                bcc mt_pulseok2
                lda #$01
                bne mt_pulseok
mt_pulsesub:    sbc mt_instpulsespd,y
                sbc #$00
                sta mt_chnpulse,x
                sta $d402,x
                sta $d403,x
                and #$0f
                cmp mt_instpulselow,y
                bcs mt_pulseok2
                lda #$00
mt_pulseok:     sta mt_chnpulsedir,x
mt_pulseok2:    ldy mt_chnwavetbl,x
                bne mt_dowavetbl
                ldy mt_chncommand,x             ;Do only continuous effects
                beq mt_arpeggio                 ;Arpeggio is most common so
                lda mt_contcmdtbllo-1,y         ;optimize for it
                sta mt_contjump+1
                lda mt_chncmddata,x
mt_contjump:    jmp mt_portamento

mt_dowavetbl:   lda mt_wavetbl,y
                beq mt_skipwave
                sta mt_chnwave,x
                sta $d404,x
mt_skipwave:    lda mt_notetbl,y
                bmi mt_wavetblabs
                clc
                adc mt_chnnote,x
mt_wavetblabs:  and #$7f
                sta mt_temp1
                lda mt_wavetbl+1,y
                cmp #$ff
                bcc mt_nowaveend
                lda mt_notetbl+1,y
                beq mt_nowaveloop
                ldy mt_chninstnum,x
                adc mt_instwave,y             ;Carry is cleared
                adc #$fe
                bne mt_nowaveloop
mt_nowaveend:   iny
                tya
mt_nowaveloop:  sta mt_chnwavetbl,x
                ldy mt_temp1
                bpl mt_arpfreq


mt_arpeggio:    ldy mt_chncmddata,x
                beq mt_nextchn
                bpl mt_fastarp
                lda mt_chntick,x
                and #$01
                bne mt_nextchn
mt_fastarp:     tya
                ldy mt_chnarpcount,x
                bmi mt_arp1
                bne mt_arp2
mt_arp0:        ldy mt_chnnote,x
                lda #$ff
                bne mt_arpfreq2
mt_arp2:        and #$0f
                clc
                adc mt_chnnote,x
                tay
                lda #$00
                beq mt_arpfreq2
mt_arp1:        and #$70
                lsr
                lsr
                lsr
                lsr
                adc mt_chnnote,x
                tay
                lda #$01
mt_arpfreq2:    sta mt_chnarpcount,x
mt_arpfreq:     lda mt_freqtbllo,y
                sta mt_chnfreqlo,x
                sta $d400,x
                lda mt_freqtblhi,y
                sta mt_chnfreqhi,x
                sta $d401,x
mt_cmddonothing:
mt_nextchn:     lda mt_chnnext,x
                beq mt_alldone
                tax
                jmp mt_chnloop
mt_alldone:     rts

        ;Effects. All entrypoints must reside on the same page!

mt_starttoneportamento:
                lda #$fe
                sta mt_chnvibcount,x
                bne mt_cmddonothing

mt_setfilter:   sta mt_filtctrl+1
                jmp mt_cmddonothing

mt_setcutoffadd:sta mt_filtcutoffadd+1
                jmp mt_cmddonothing

mt_setsustain:  sta $d406,x
                jmp mt_cmddonothing

mt_settempo:    bmi mt_settempoone
                sta mt_chntempo
                sta mt_chntempo+7
                sta mt_chntempo+14
                bpl mt_cmddonothing
mt_settempoone: and #$7f
                sta mt_chntempo,x
                bpl mt_cmddonothing

mt_portamento:  asl
                sta mt_temp1
                bcc mt_freqadd
                bcs mt_freqsub

mt_vibrato:     sta mt_temp1
                and #$0e
                sta mt_temp2
                lda mt_chnvibcount,x
                bmi mt_novibdir2
                cmp mt_temp2
                bcc mt_novibdir
                eor #$ff
                jmp mt_vibdone
mt_novibdir2:   clc
mt_novibdir:    adc #$02
mt_vibdone:     sta mt_chnvibcount,x
                lsr
                bcc mt_freqadd
                bcs mt_freqsub

mt_toneportamento:
                ldy mt_chnnote,x
                asl
                sta mt_temp1
                bcs mt_tpdown
mt_tpup:        lda mt_chnfreqhi,x
                cmp mt_freqtblhi,y
                beq mt_tpupchecklow
                bcc mt_freqadd
                bcs mt_tpfound
mt_tpupchecklow:lda mt_chnfreqlo,x
                cmp mt_freqtbllo,y
                bcc mt_freqadd
                bcs mt_tpfound
mt_tpdown:      lda mt_chnfreqhi,x
                cmp mt_freqtblhi,y
                beq mt_tpdownchecklow
                bcs mt_freqsub
                bcc mt_tpfound
mt_tpdownchecklow:lda mt_chnfreqlo,x
                cmp mt_freqtbllo,y
                beq mt_tpfound
                bcs mt_freqsub
mt_tpfound:     jmp mt_arpfreq

mt_freqadd:     lda mt_chnfreqlo,x
                sta $d400,x
                adc mt_temp1
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                sta $d401,x
                adc #$00
                sta mt_chnfreqhi,x
mt_freqdone:    lda mt_chnnext,x
                bne mt_nextchn2
mt_alldone2:    rts

mt_freqsub:     lda mt_chnfreqlo,x
                sta $d400,x
                sbc mt_temp1
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                sta $d401,x
                sbc #$00
                sta mt_chnfreqhi,x
mt_freqdone2:   lda mt_chnnext,x
                beq mt_alldone2
mt_nextchn2:    tax
                jmp mt_chnloop

mt_freqtblhi:   dc.b $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$02
                dc.b $02,$02,$02,$02,$02,$02,$03,$03,$03,$03,$03,$04
                dc.b $04,$04,$04,$05,$05,$05,$06,$06,$06,$07,$07,$08
                dc.b $08,$09,$09,$0a,$0a,$0b,$0c,$0c,$0d,$0e,$0f,$10
                dc.b $11,$12,$13,$14,$15,$17,$18,$19,$1b,$1d,$1e,$20
                dc.b $22,$24,$26,$29,$2b,$2e,$30,$33,$36,$3a,$3d,$41
                dc.b $45,$49,$4d,$52,$57,$5c,$61,$67,$6d,$74,$7b,$82
                dc.b $8a,$92,$9b,$a4,$ae,$b8,$c3,$cf,$db,$e8,$f6,$ff

mt_freqtbllo:   dc.b $15,$25,$36,$49,$5c,$71,$87,$9f,$b7,$d1,$ed,$0a
                dc.b $2a,$4a,$6d,$92,$b9,$e3,$0f,$3e,$6f,$a3,$db,$15
                dc.b $54,$95,$db,$25,$73,$c7,$1e,$7c,$de,$47,$b6,$2b
                dc.b $a8,$2b,$b7,$4b,$e7,$8e,$3d,$f8,$bd,$8e,$6c,$57
                dc.b $50,$57,$6e,$96,$cf,$1c,$7b,$f0,$7b,$1d,$d8,$ae
                dc.b $a0,$af,$dd,$2d,$9f,$38,$f7,$e0,$f6,$3b,$b1,$5d
                dc.b $40,$5e,$bb,$5a,$3f,$70,$ef,$c1,$ed,$76,$63,$ba
                dc.b $80,$bc,$76,$b4,$7f,$e0,$de,$83,$da,$ed,$c7,$ff

mt_tick0cmdtbllo:dc.b <mt_cmddonothing
                dc.b <mt_cmddonothing
                dc.b <mt_setcutoffadd
                dc.b <mt_starttoneportamento
                dc.b <mt_cmddonothing
                dc.b <mt_setfilter
                dc.b <mt_setsustain
                dc.b <mt_settempo

mt_contcmdtbllo:dc.b <mt_portamento
                dc.b <mt_cmddonothing
                dc.b <mt_toneportamento
                dc.b <mt_vibrato
                dc.b <mt_cmddonothing
                dc.b <mt_cmddonothing
                dc.b <mt_cmddonothing

mt_chnnote:     dc.b 0
mt_chnfreqlo:   dc.b 0
mt_chnfreqhi:   dc.b 0
mt_chnnewnote:  dc.b 0
mt_chncommand:  dc.b 0
mt_chncmddata:  dc.b 0
mt_chninstnum:  dc.b INST1

                dc.b 0,0,0,0,0,0,INST1
                dc.b 0,0,0,0,0,0,INST1

mt_chnwave:     dc.b 8
mt_chnwavetbl:  dc.b 0
mt_chnpulse:    dc.b 0
mt_chnpulsedir: dc.b 0
mt_chnarpcount: dc.b 0
mt_chnvibcount: dc.b 0
mt_chnsongptr:  dc.b 0

                dc.b 8,0,0,0,0,0,0
                dc.b 8,0,0,0,0,0,0

mt_chnsongadrlo:dc.b 0
mt_chnsongadrhi:dc.b 0
mt_chnpattptr:  dc.b 0
mt_chnpattnum:  dc.b 0
mt_chntick:     dc.b 0
mt_chntempo:    dc.b 0
mt_chnnext:     dc.b 7

                dc.b 0,0,0,0,0,0,14
                dc.b 0,0,0,0,0,0,0

