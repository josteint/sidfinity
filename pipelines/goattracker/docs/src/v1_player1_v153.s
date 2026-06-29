;-------------------------------------------------------------------------------
; GoatTracker V1.5 standard playroutine.
;
; NOTE: This playroutine source code does not fall under the GPL license!
; Use it freely for any purpose, commercial or noncommercial.
;-------------------------------------------------------------------------------

                processor 6502
                org $1000

        ; "Virtual addresses" for relocation

mt_instad       = $4000
mt_instsr       = $4001
mt_instpulse    = $4002
mt_instpulsespd = $4003
mt_instpulselow = $4004
mt_instpulsehigh = $4005
mt_instfilter   = $4006
mt_instwave     = $4007
mt_wavetbl      = $4100
mt_notetbl      = $4200
mt_songtbllo    = $4300
mt_songtblhi    = $4400
mt_patttbllo    = $4500
mt_patttblhi    = $4600
mt_filttbl      = $4700

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

        ; Orderlist commands

REPEAT          = $d0
TRANSDOWN       = $e0
TRANSUP         = $f0
LOOPSONG        = $ff

        ; Used zeropage temp variables

mt_temp1        = $fc
mt_temp2        = $fd

                jmp init
                jmp play

init:           sta init_adc+1
                asl
init_adc:       adc #$00
                sta mt_chnloop+1
                rts

mt_tick0tbl:    dc.b <mt_tick0arp
                dc.b <mt_tick0idle
                dc.b <mt_tick0idle
                dc.b <mt_tick0toneport
                dc.b <mt_tick0idle
                dc.b <mt_tick0filter
                dc.b <mt_tick0sr
                dc.b <mt_tick0tempo

mt_tickntbl:    dc.b <mt_ticknarp
                dc.b <mt_ticknportaup
                dc.b <mt_ticknportadown
                dc.b <mt_tickntoneport
                dc.b <mt_ticknvibrato
                dc.b <mt_ticknidle
                dc.b <mt_ticknidle
                dc.b <mt_ticknidle

mt_message:     ds.b 32,0

play:           lda mt_temp1                    ;Store zeropage
                pha
                lda mt_temp2
                pha
mt_filttime:    ldy #$00                        ;Start with filter exec.
                bne mt_filtmod
mt_filtstep:    lda #$00
                beq mt_filtskip
                jsr mt_setfiltersub
                jmp mt_filtskip
mt_filtmod:     dec mt_filttime+1
                lda mt_d416reg+1
                clc
mt_filtcutoffadd:adc #$00
                sta mt_d416reg+1
mt_filtskip:
mt_d416reg:     lda #$00
                sta $d416
mt_d417reg:     lda #$00
                sta $d417
mt_d418reg:     lda #$0f
mt_volume:      and #$ff
                sta $d418

                ldx #$00
mt_chnloop:     lda #$00
                bmi mt_noinit
                sta mt_chnsongnum,x
                inc mt_chnloop+1
                txa                             ;First channel init?
                bne mt_initnotfirst
                ldx #21
mt_initfirst:   sta mt_chnwave-1,x              ;Reset sequencer variables
                dex
                bne mt_initfirst
                sta $d415                       ;Reset cutoff lowbyte
                jsr mt_setfiltersub             ;Set filter 0
mt_initnotfirst:lda #$05                        ;Reset tempo
                sta mt_chntempo,x
                dc.b $ff,$00                    ;Initial tick (gatetimer+2)
                sta mt_chntick,x
                lda #ENDPATT                    ;Force fetch of new pattern
                sta mt_chnpattptr,x
                sta mt_chnnewnote,x
                jmp mt_loadregs

mt_noinit:      dec mt_chntick,x                ;Tick 0 or not?
                beq mt_tick0
mt_tickn:       bpl mt_noreload                 ;Reload tempo if necessary
                lda mt_chntempo,x
                cmp #$02
                bcs mt_nofunk
                tay
                eor #$01
                sta mt_chntempo,x
                lda mt_filttbl+2,y              ;Use filter0 for funktempo
mt_nofunk:      sta mt_chntick,x
mt_noreload:    ldy mt_chnwaveptr,x             ;Execute wavetable?
                bne mt_ticknwave
                sty mt_temp2                    ;Clear speed highbyte
                ldy mt_chnfx,x
                lda mt_tickntbl,y
                sta mt_ticknjump+1
                lda mt_chnfxparam,x
mt_ticknjump:   jmp mt_ticknportaup
mt_ticknwave:   jmp mt_waveexec

mt_tick0:       lda mt_chnnewfx,x
                tay
                and #$f8
                beq mt_skipinst                 ;Instrument number 0 lets
                sta mt_chninstnum,x             ;the instrument stay the same
mt_skipinst:    tya
                and #$07
                sta mt_chnfx,x
                tay
                lda mt_tick0tbl,y
                sta mt_tick0jump+1
                lda mt_chnnewfxparam,x
                sta mt_chnfxparam,x
mt_tick0jump:   jmp mt_tick0tempo               ;Exec tick 0 cmd.
mt_tick0done:   lda mt_chnnewnote,x
                bmi mt_tick0nonew

mt_newnoteinit: sta mt_chnnote,x
                lda #$ff
                sta mt_chnnewnote,x
                sta mt_chngate,x
                ldy mt_chninstnum,x
                lda mt_instpulse,y
                beq mt_skippulse
                and #$f0
                sta mt_chnpulsedir,x
                sta $d402,x
                lda mt_instpulse,y
                and #$0f
                sta mt_chnpulse,x
                sta $d403,x
mt_skippulse:   lda mt_instwave,y
                sta mt_chnwaveptr,x
                lda mt_instad,y
                sta $d405,x
                lda mt_chnfx,x          ;Sustain override?
                cmp #$06
                beq mt_skipsustain
                lda mt_instsr,y
                sta $d406,x
mt_skipsustain: lda #$09                ;First frame waveform (testbit)
                sta mt_chnwave,x
                sta $d404,x
                lda mt_instfilter,y
                beq mt_nofilterchange
                jsr mt_setfiltersub
mt_nofilterchange:
                jmp mt_nextchn

mt_tick0nonew:  ldy mt_chnwaveptr,x
                beq mt_pulseexec

mt_waveexec:    lda mt_wavetbl,y
                cmp #$08                        ;0-7 used as delay
                bcs mt_nowavedelay              ;+ no wave change
                cmp mt_chnarpcount,x
                beq mt_skipwave
                inc mt_chnarpcount,x
                bne mt_pulseexec
mt_nowavedelay: sta mt_chnwave,x
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
mt_nowaveloop:  sta mt_chnwaveptr,x
                ldy mt_temp1
mt_arpfreqresetvib:lda #$00		;Reset arpeggio/vibrato/delayed wave exec.
                sta mt_chnarpcount,x	;each time a frequency is loaded
mt_arpfreq:     lda mt_freqtbllo,y
                sta mt_chnfreqlo,x
                lda mt_freqtblhi,y
                sta mt_chnfreqhi,x
mt_pulseexec:
                lda mt_chntick,x
                dc.b $ff,$00            ;cmp gatetimer
                beq mt_getnewnotes      ;Get new notes
                lda mt_chnpattptr,x
                cmp #ENDPATT
                bne mt_normalpulse
                jmp mt_sequencer        ;Sequencer advance

mt_normalpulse: ldy mt_chninstnum,x
                lda mt_instpulsespd,y
                and #$fe
                beq mt_pulseok
                sta mt_temp1
                lda mt_chnpulsedir,x
                lsr
                bcs mt_pulsesub
mt_pulseadd:    asl
                adc mt_temp1
                pha
                lda mt_chnpulse,x
                adc #$00
                sta mt_chnpulse,x
                cmp mt_instpulsehigh,y
                jmp mt_pulsedone
mt_pulsesub:    asl
                sec
                sbc mt_temp1
                pha
                lda mt_chnpulse,x
                sbc #$00
                sta mt_chnpulse,x
                cmp mt_instpulselow,y
mt_pulsedone:   sta $d403,x
                pla
                adc #$00
                sta mt_chnpulsedir,x
                sta $d402,x
mt_pulseok:     jmp mt_loadregs

mt_packedrest:  ldy mt_chnpackrest,x
                bne mt_packedrestcommon
                sta mt_chnpackrest,x
mt_packedrestcommon:
                inc mt_chnpackrest,x
                bne mt_packedrestcont
                inc mt_chnpattptr,x
mt_packedrestcont:
                jmp mt_rest

mt_getnewnotes: ldy mt_chnpattnum,x
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
                sta mt_notenum+1
                bcs mt_nocmd
mt_cmd:         sta mt_notenum+1
                lda (mt_temp1),y
                sta mt_chnnewfx,x
                iny
                lda (mt_temp1),y
                sta mt_chnnewfxparam,x
                iny
mt_nocmd:       lda (mt_temp1),y
                cmp #ENDPATT
                beq mt_endpatt
                tya
mt_endpatt:     sta mt_chnpattptr,x
mt_notenum:     lda #$00
                cmp #KEYOFF                   ;Keyoff or rest?
                beq mt_keyoff
                bcs mt_rest
mt_normalnote:  adc mt_chntrans,x
                sta mt_chnnewnote,x
                lda mt_chnnewfx,x
                and #$07
                cmp #$03                      ;Toneportamento?
                beq mt_rest
                ldy mt_chninstnum,x
                lda mt_instpulsespd,y         ;Pulsespd bit 0: hardrestart
                lsr                           ;flag
                bcs mt_nohardrestart
                dc.b $ff,$00                  ;Hardrestart AD parameter
                sta $d405,x
                dc.b $ff,$00                  ;Hardrestart SR parameter
                sta $d406,x
mt_nohardrestart:
mt_keyoff:      lda #$fe
                sta mt_chngate,x
mt_rest:

mt_loadregs:    lda mt_chnfreqlo,x
                sta $d400,x
                lda mt_chnfreqhi,x
                sta $d401,x
                lda mt_chnwave,x
                and mt_chngate,x
                sta $d404,x
mt_nextchn:     cpx #14
                bcs mt_alldone
                txa
                adc #$07
                tax
                jmp mt_chnloop
mt_alldone:     lda #$ff
                sta mt_chnloop+1
                pla
                sta mt_temp2                    ;Restore zeropage
                pla
                sta mt_temp1
                rts

mt_sequencer:   ldy mt_chnsongnum,x
                lda mt_songtbllo,y
                sta mt_temp1
                lda mt_songtblhi,y
                sta mt_temp2
                lda mt_chnrepeat,x
                beq mt_norepeatnow
                dec mt_chnrepeat,x
                jmp mt_seqdone2
mt_norepeatnow: ldy mt_chnsongptr,x
mt_seqloop:     lda (mt_temp1),y
                iny
                cmp #REPEAT
                bcc mt_seqdone
                cmp #TRANSDOWN
                bcs mt_trans
mt_repeat:      sbc #REPEAT-1
                sta mt_chnrepeat,x
                bcs mt_seqloop
mt_trans:       cmp #LOOPSONG
                bcc mt_nosongloop
                lda (mt_temp1),y
                tay
                jmp mt_seqloop
mt_nosongloop:  sbc #TRANSUP-1
                sta mt_chntrans,x
                jmp mt_seqloop
mt_seqdone:     sta mt_chnpattnum,x
                tya
                sta mt_chnsongptr,x
mt_seqdone2:    inc mt_chnpattptr,x
                jmp mt_loadregs

mt_setfiltersub:tay
                lda mt_filttbl,y
                beq mt_sfsmod
                sta mt_d417reg+1
                lda mt_filttbl+1,y
                sta mt_d418reg+1
                lda mt_filttbl+2,y
                beq mt_sfscutoffskip
                sta mt_d416reg+1
mt_sfscutoffskip:
                lda #$00
                beq mt_sfscommon
mt_sfsmod:      lda mt_filttbl+2,y
                sta mt_filtcutoffadd+1
                lda mt_filttbl+1,y
mt_sfscommon:   sta mt_filttime+1
                tya
                beq mt_sfsnonext
                lda mt_filttbl+3,y
mt_sfsnonext:   sta mt_filtstep+1
                rts

        ;Tick n commands

mt_ticknportaup:jsr mt_makespeed
                bcc mt_freqadd

mt_ticknportadown:
                jsr mt_makespeed
                sec
                bcs mt_freqsub

mt_ticknvibrato:tay
                and #$f0                ;Clear low bits of speed
                sta mt_temp1
                tya
                and #$0f
                sta mt_vibratocmp+1
                lda mt_chnarpcount,x
                bmi mt_vibratonodir
mt_vibratocmp:  cmp #$00
                bcc mt_vibratonodir2
                beq mt_vibratonodir
                eor #$ff
mt_vibratonodir:
                clc
mt_vibratonodir2:
                adc #$02
mt_vibdone:     sta mt_chnarpcount,x
                lsr
                bcc mt_freqadd
                bcs mt_freqsub
mt_ticknidle:   jmp mt_pulseexec

mt_tickntoneport:
                ldy mt_chnnote,x                  ;(handled on tick 0)
                cmp #$00
                beq mt_tickntpfound2            ;Speed $00 = tie note
                jsr mt_makespeed
                lda mt_freqtbllo,y              ;Calculate offset to the
                sec                             ;right frequency
                sbc mt_chnfreqlo,x
                sta mt_tickntptemplo+1
                lda mt_freqtblhi,y
                sbc mt_chnfreqhi,x
                sta mt_tickntptemphi+1
                bmi mt_tickntpdown              ;If negative, have to go down

mt_tickntpup:   lda mt_temp2                    ;Now compare toneportamento
                cmp mt_tickntptemphi+1          ;speed to the offset
                bne mt_tickntpup_nolowbyte
                lda mt_temp1
                cmp mt_tickntptemplo+1
mt_tickntpup_nolowbyte:
                bcs mt_tickntpfound             ;If speed greater, we're done
mt_freqadd:     lda mt_chnfreqlo,x
                adc mt_temp1
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                adc mt_temp2
                sta mt_chnfreqhi,x
                jmp mt_pulseexec

mt_tickntpdown:
mt_tickntptemplo:
                lda #$00                        ;Add speed to the negative
                adc mt_temp1                    ;offset
mt_tickntptemphi:
                lda #$00
                adc mt_temp2
                bpl mt_tickntpfound             ;If goes positive, we're done
                sec
mt_freqsub:     lda mt_chnfreqlo,x
                sbc mt_temp1
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                sbc mt_temp2
                sta mt_chnfreqhi,x
mt_arpzero:     jmp mt_pulseexec

mt_tickntpfound:lda #$00                        ;Stop the speed to save
mt_tickntpfound2:
                sta mt_chnfxparam,x             ;rastertime on subsequent frames
                jmp mt_arpfreqresetvib

mt_ticknarp:    beq mt_arpzero
                jmp mt_arpeggio

        ;Tick 0 effects

mt_tick0arp:    beq mt_tick0idle                ;If parameter zero..
                lda mt_chnnewnote,x             ;Do not exec if newnote going on
                bpl mt_tick0idle
                ldy mt_chnwaveptr,x             ;Do not exec arpeggio if there's
                beq mt_arpeggio                 ;waveform going on
mt_tick0idle:   jmp mt_tick0done

mt_tick0toneport:
                lda mt_chnnewnote,x
                bmi mt_tick0idle
                sta mt_chnnote,x
                lda #$ff                        ;Reset newnote
                sta mt_chnnewnote,x             ;(use legato instead)
                jmp mt_tick0done

mt_tick0filter: jsr mt_setfiltersub
                jmp mt_tick0done

mt_tick0sr:     sta $d406,x
                jmp mt_tick0done

mt_tick0tempo:  bmi mt_settempoone
                sta mt_chntempo
                sta mt_chntempo+7
                sta mt_chntempo+14
                jmp mt_tick0done
mt_settempoone: cmp #$ef
                beq mt_timingmark
                bcs mt_setfader
                and #$7f
                sta mt_chntempo,x
                jmp mt_tick0done
mt_timingmark:  inc mt_timecounter
                jmp mt_tick0done
mt_setfader:    sta mt_volume+1
                jmp mt_tick0done

mt_arpeggio:    asl
                lda mt_chnarpcount,x
                pha
                adc #$01
                cmp #$06
                bcc mt_arpnotover
                lda #$00
mt_arpnotover:  sta mt_chnarpcount,x
                pla
                lsr
                cmp #$01
                bcc mt_arp1
                bne mt_arp0
mt_arp2:        lda mt_chnfxparam,x
                and #$0f
                bpl mt_arpfreq2
mt_arp0:        lda #$00
                bpl mt_arpfreq2
mt_arp1:        lda mt_chnfxparam,x
                and #$70
                lsr
                lsr
                lsr
                lsr
mt_arpfreq2:    clc
                adc mt_chnnote,x
                tay
mt_arpdone:     jmp mt_arpfreq


mt_makespeed:   asl
                rol mt_temp2
                asl
                rol mt_temp2
                sta mt_temp1
                rts

                if (mt_ticknportaup & $ff00)!=(mt_ticknarp & $ff00)
                err
                endif

                if (mt_tick0arp & $ff00)!=(mt_tick0tempo & $ff00)
                err
                endif

mt_timecounter: dc.b 0

mt_chnwave:     dc.b 0
mt_chnwaveptr:  dc.b 0
mt_chnpackrest: dc.b 0
mt_chnrepeat:   dc.b 0
mt_chntrans:    dc.b 0
mt_chnsongptr:  dc.b 0
mt_chnpattptr:  dc.b 0
                dc.b 0,0,0,0,0,0,0
                dc.b 0,0,0,0,0,0,0

mt_chnfreqlo:   dc.b 0
mt_chnfreqhi:   dc.b 0
mt_chnpulse:    dc.b 0
mt_chnpulsedir: dc.b 0
mt_chnunused3:  dc.b 0
mt_chnunused4:  dc.b 0
mt_chngate:     dc.b 0
                dc.b 0,0,0,0,0,0,0
                dc.b 0,0,0,0,0,0,0

mt_chnnewfx:    dc.b 0
mt_chnnewfxparam:dc.b 0
mt_chnfx:       dc.b 0
mt_chnfxparam:  dc.b 0
mt_chnnote:     dc.b 0
mt_chnnewnote:  dc.b 0
mt_chninstnum:  dc.b INST1

                dc.b 0,0,0,0,0,0,INST1
                dc.b 0,0,0,0,0,0,INST1

mt_chnarpcount: dc.b 0
mt_chnsongnum:  dc.b 0
mt_chnpattnum:  dc.b 0
mt_chntick:     dc.b 0
mt_chntempo:    dc.b 0
mt_chnunused1:  dc.b 0
mt_chnunused2:  dc.b 0
                dc.b 0,0,0,0,0,0,0
                dc.b 0,0,0,0,0,0,0

mt_freqtblhi:   dc.b $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$02
                dc.b $02,$02,$02,$02,$02,$02,$03,$03,$03,$03,$03,$04
                dc.b $04,$04,$04,$05,$05,$05,$06,$06,$06,$07,$07,$08
                dc.b $08,$09,$09,$0a,$0a,$0b,$0c,$0d,$0d,$0e,$0f,$10
                dc.b $11,$12,$13,$14,$15,$17,$18,$1a,$1b,$1d,$1f,$20
                dc.b $22,$24,$27,$29,$2b,$2e,$31,$34,$37,$3a,$3e,$41
                dc.b $45,$49,$4e,$52,$57,$5c,$62,$68,$6e,$75,$7c,$83
                dc.b $8b,$93,$9c,$a5,$af,$b9,$c4,$d0,$dd,$ea,$f8,$ff

mt_freqtbllo:   dc.b $17,$27,$39,$4b,$5f,$74,$8a,$a1,$ba,$d4,$f0,$0e
                dc.b $2d,$4e,$71,$96,$be,$e8,$14,$43,$74,$a9,$e1,$1c
                dc.b $5a,$9c,$e2,$2d,$7c,$cf,$28,$85,$e8,$52,$c1,$37
                dc.b $b4,$39,$c5,$5a,$f7,$9e,$4f,$0a,$d1,$a3,$82,$6e
                dc.b $68,$71,$8a,$b3,$ee,$3c,$9e,$15,$a2,$46,$04,$dc
                dc.b $d0,$e2,$14,$67,$dd,$79,$3c,$29,$44,$8d,$08,$b8
                dc.b $a1,$c5,$28,$cd,$ba,$f1,$78,$53,$87,$1a,$10,$71
                dc.b $42,$89,$4f,$9b,$74,$e2,$f0,$a6,$0e,$33,$20,$ff

