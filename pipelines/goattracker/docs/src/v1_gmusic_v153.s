;-------------------------------------------------------------------------------
; GoatTracker V1.5 gamemusic playroutine.
;
; NOTE: This playroutine source code does not fall under the GPL license!
; Use it freely for any purpose, commercial or noncommercial.
;
; You'll have to supply the address of the musicdata yourself, and call
; RELOCATEMUSIC every time a new music module has been loaded to that address.
;
; You also have to create the sound effect tables yourself, see example2.s for
; details. Remember that higher sound effect numbers have higher priority.
;
; It's recommended to place the playroutine at a page start. That's because the
; effect code contains selfmodifying jumps that only modify the low-byte.
; There's a conditional DASM define to catch a page-cross error, though.
;-------------------------------------------------------------------------------

                processor 6502

          ;Address of music data
;mt_musicdata    =

          ;2 consecutive zeropage addresses required
;mt_zpbase       =

          ;Memory defines

mt_instad       = mt_musicdata-4           ;These are known
mt_instsr       = mt_musicdata-3
mt_instpulse    = mt_musicdata-2
mt_instpulsespd = mt_musicdata-1
mt_instpulselow = mt_musicdata
mt_instpulsehigh = mt_musicdata+1
mt_instfilter   = mt_musicdata+2
mt_instwave     = mt_musicdata+3

mt_wavetbl      = mt_musicdata+4           ;These are yet unknown
mt_notetbl      = mt_musicdata+4
mt_songtbllo    = mt_musicdata+4
mt_songtblhi    = mt_musicdata+4
mt_patttbllo    = mt_musicdata+4
mt_patttblhi    = mt_musicdata+4
mt_filttbl      = mt_musicdata+4

        ; Constants for musicdata relocation

REL_ADDONE      = 0
REL_INSTRSIZE   = 1
REL_WAVESIZE    = 2
REL_SONGSIZE    = 3
REL_PATTSIZE    = 4
REL_SUBONE      = $80
REL_END         = $ff

        ; Special note values

KEYOFF          = $5e           ;Keyoff clears the gatebit
REST            = $5f
NOCMD           = $60           ;Instrument & command byte do not exist
FIRSTPACKEDREST = $c0
PACKEDREST      = $00
ENDPATT         = $ff

        ; Instrument numbers in patterndata

INST1           = $08

        ; Orderlist commands

REPEAT          = $d0
TRANSDOWN       = $e0
TRANSUP         = $f0
LOOPSONG        = $ff

;-------------------------------------------------------------------------------
; MUSIC
;
; Plays one frame of music + sound effects. Do not call this if music is being
; loaded or if RELOCATEMUSIC hasn't been called yet after loading new music
; data!
;-------------------------------------------------------------------------------

music:
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
mt_initsongnum: ldy #$00
                bmi mt_noinit
                sty mt_chnsongnum
                iny
                sty mt_chnsongnum+7
                iny
                sty mt_chnsongnum+14
                txa
                ldx #21
mt_initfirst:   sta mt_chnwave-1,x              ;Reset sequencer variables
                dex
                bne mt_initfirst
                sta $d415                       ;Reset cutoff lowbyte
                jsr mt_setfiltersub             ;Set filter 0
                jsr mt_initloop
                ldx #$07
                jsr mt_initloop
                ldx #$0e
mt_initloop:    lda #$05                        ;Reset tempo
                sta mt_chntempo,x
                lda #$04                        ;Initial tick (gatetimer+2)
                sta mt_chntick,x
                lda #ENDPATT                    ;Force fetch of new pattern
                sta mt_chnpattptr,x
                sta mt_chnnewnote,x
                sta mt_initsongnum+1
                jmp mt_loadregs                 ;Load regs/handle SFX

mt_noinit:      jsr mt_chnloop
                ldx #$07
                jsr mt_chnloop
                ldx #$0e
mt_chnloop:     dec mt_chntick,x                ;Tick 0 or not?
                beq mt_tick0
mt_tickn:       bpl mt_noreload                 ;Reload tempo if necessary
                lda mt_chntempo,x
                cmp #$02
                bcs mt_nofunk
                tay
                eor #$01
                sta mt_chntempo,x
mt_filttblaccess2c:
                lda mt_filttbl+2,y
mt_nofunk:      sta mt_chntick,x
mt_noreload:    ldy mt_chnwaveptr,x             ;Execute wavetable?
                bne mt_ticknwave
                sty mt_zpbase+1                 ;Clear speed highbyte
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
                lda mt_instpulse,y            
                and #$0f
                sta mt_chnpulse,x
mt_skippulse:   lda mt_instwave,y
                sta mt_chnwaveptr,x
                lda mt_instad,y
                sta mt_chnad,x
                lda mt_chnfx,x          ;Sustain override?
                cmp #$06
                beq mt_skipsustain
                lda mt_instsr,y
                sta mt_chnsr,x
mt_skipsustain: lda mt_instfilter,y
                beq mt_nofilterchange
                jsr mt_setfiltersub
mt_nofilterchange:
                lda #$09                ;First frame waveform (testbit)
                sta mt_chnwave,x
                jmp mt_loadregs

mt_tick0nonew:  ldy mt_chnwaveptr,x
                beq mt_pulseexec

mt_waveexec:    lda mt_chnsfx,x         ;If sound effect executing,
                bne mt_pulseexec        ;skip wavetable
mt_wavetblaccess:
                lda mt_wavetbl,y
                cmp #$08                        ;0-7 used as delay
                bcs mt_nowavedelay              ;+ no wave change
                cmp mt_chnarpcount,x
                beq mt_skipwave
                inc mt_chnarpcount,x
                bne mt_pulseexec
mt_nowavedelay: sta mt_chnwave,x
mt_skipwave:
mt_notetblaccess:
                lda mt_notetbl,y
                bmi mt_wavetblabs
                clc
                adc mt_chnnote,x
mt_wavetblabs:  and #$7f
                sta mt_zpbase
mt_wavetblplusaccess:
                lda mt_wavetbl+1,y
                cmp #$ff
                bcc mt_nowaveend
mt_notetblplusaccess:
                lda mt_notetbl+1,y
                beq mt_nowaveloop
                ldy mt_chninstnum,x
                adc mt_instwave,y             ;Carry is cleared
                adc #$fe
                bne mt_nowaveloop
mt_nowaveend:   iny
                tya
mt_nowaveloop:  sta mt_chnwaveptr,x
                ldy mt_zpbase
mt_arpfreqresetvib:lda #$00		;Reset arpeggio/vibrato/delayed wave exec.
		sta mt_chnarpcount,x	;each time a frequency is loaded
mt_arpfreq:     lda mt_freqtbllo,y
                sta mt_chnfreqlo,x
                lda mt_freqtblhi,y
                sta mt_chnfreqhi,x
mt_pulseexec:
                lda mt_chntick,x
                cmp #$02                ;cmp gatetimer
                beq mt_getnewnotes      ;Get new notes
                lda mt_chnpattptr,x
                cmp #ENDPATT
                bne mt_normalpulse
                jmp mt_sequencer        ;Sequencer advance

mt_normalpulse: ldy mt_chninstnum,x
                lda mt_instpulsespd,y
                and #$fe
                beq mt_pulseok
                sta mt_zpbase
                lda mt_chnpulsedir,x
                lsr
                bcs mt_pulsesub
mt_pulseadd:    asl
                adc mt_zpbase
                pha
                lda mt_chnpulse,x
                adc #$00
                sta mt_chnpulse,x
                cmp mt_instpulsehigh,y
                jmp mt_pulsedone
mt_pulsesub:    asl
                sec
                sbc mt_zpbase
                pha
                lda mt_chnpulse,x
                sbc #$00
                sta mt_chnpulse,x
                cmp mt_instpulselow,y
mt_pulsedone:   pla
                adc #$00
                sta mt_chnpulsedir,x
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
mt_patttblloaccess:
                lda mt_patttbllo,y
                clc
                adc #<mt_musicdata
                sta mt_zpbase
mt_patttblhiaccess:
                lda mt_patttblhi,y
                adc #>mt_musicdata
                sta mt_zpbase+1
                ldy mt_chnpattptr,x
                lda (mt_zpbase),y
                iny
                cmp #NOCMD                      ;Do command+databytes exist?
                bcc mt_cmd
                cmp #FIRSTPACKEDREST
                bcs mt_packedrest
                sbc #NOCMD-1
                sta mt_notenum+1
                bcs mt_nocmd
mt_cmd:         sta mt_notenum+1
                lda (mt_zpbase),y
                sta mt_chnnewfx,x
                iny
                lda (mt_zpbase),y
                sta mt_chnnewfxparam,x
                iny
mt_nocmd:       lda (mt_zpbase),y
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
                lda #$0f                      ;Hardrestart AD parameter
                sta mt_chnad,x
                lda #$00                      ;Hardrestart SR parameter
                sta mt_chnsr,x
mt_nohardrestart:
mt_keyoff:      lda #$fe
                sta mt_chngate,x
mt_rest:

mt_loadregs:    lda mt_chnsfx,x
                bne mt_dosfx
                lda mt_chnpulsedir,x
                sta $d402,x
                lda mt_chnpulse,x
                sta $d403,x
                lda mt_chnad,x
                sta $d405,x
                lda mt_chnsr,x
                sta $d406,x
mt_loadregs2:   lda mt_chnfreqlo,x
                sta $d400,x
                lda mt_chnfreqhi,x
                sta $d401,x
mt_loadregs3:   lda mt_chnwave,x
                and mt_chngate,x
                sta $d404,x
                rts

        ;Sound FX code

mt_dosfx:       lda #$fe
                sta mt_chngate,x
                lda #$00
                sta mt_chnwaveptr,x
                ldy mt_chnsfxnum,x
                lda mt_sfxtbllo,y
                sta mt_zpbase
                lda mt_sfxtblhi,y
                sta mt_zpbase+1
                ldy mt_chnsfx,x
                inc mt_chnsfx,x
                cpy #$03
                beq mt_dosfx_frame0
                bcs mt_dosfx_framen
                lda #$0f                   ;Forced hardrestart of channel,
                sta $d405,x                ;before sound begins
                lda #$00
                sta $d406,x
                jmp mt_loadregs2

mt_dosfx_frame0:ldy #$01
                lda (mt_zpbase),y              ;Load ADSR
                sta $d405,x
                iny
                lda (mt_zpbase),y
                sta $d406,x
                iny
                lda (mt_zpbase),y              ;Load pulse
                sta $d402,x
                sta $d403,x
                lda #$09                       ;Testbit
mt_dosfx_storewave:
                sta $d404,x
                sta mt_chnwave,x
mt_dosfx_nowavechange:
                rts

mt_dosfx_framen:lda (mt_zpbase),y
                bne mt_dosfx_noend
mt_dosfx_end:   sta mt_chnwave,x
                sta mt_chnsfx,x
                jmp mt_loadregs3
mt_dosfx_noend: tay
                lda mt_freqtbllo-$80,y            ;Get frequency
                sta $d400,x
                sta mt_chnfreqlo,x
                lda mt_freqtblhi-$80,y
                sta $d401,x
                sta mt_chnfreqhi,x
                ldy mt_chnsfx,x
                lda (mt_zpbase),y             ;Then take a look at the coming
                beq mt_dosfx_nowavechange     ;byte
                cmp #$82                      ;Is it a waveform or a note?
                bcs mt_dosfx_nowavechange
                inc mt_chnsfx,x
                bcc mt_dosfx_storewave

mt_sequencer:   ldy mt_chnsongnum,x
mt_songtblloaccess:
                lda mt_songtbllo,y
                clc
                adc #<mt_musicdata
                sta mt_zpbase
mt_songtblhiaccess:
                lda mt_songtblhi,y
                adc #>mt_musicdata
                sta mt_zpbase+1
                lda mt_chnrepeat,x
                beq mt_norepeatnow
                dec mt_chnrepeat,x
                jmp mt_seqdone2
mt_norepeatnow: ldy mt_chnsongptr,x
mt_seqloop:     lda (mt_zpbase),y
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
                lda (mt_zpbase),y
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

        ;Tick n commands

mt_ticknportaup:jsr mt_makespeed
                bcc mt_freqadd

mt_ticknportadown:
                jsr mt_makespeed
                sec
                bcs mt_freqsub

mt_ticknvibrato:tay
                and #$f0                ;Clear low bits of speed
                sta mt_zpbase
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

mt_tickntpup:   lda mt_zpbase+1                    ;Now compare toneportamento
                cmp mt_tickntptemphi+1          ;speed to the offset
                bne mt_tickntpup_nolowbyte
                lda mt_zpbase
                cmp mt_tickntptemplo+1
mt_tickntpup_nolowbyte:
                bcs mt_tickntpfound             ;If speed greater, we're done
mt_freqadd:     lda mt_chnfreqlo,x
                adc mt_zpbase
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                adc mt_zpbase+1
                sta mt_chnfreqhi,x
                jmp mt_pulseexec

mt_tickntpdown:
mt_tickntptemplo:
                lda #$00                        ;Add speed to the negative
                adc mt_zpbase                    ;offset
mt_tickntptemphi:
                lda #$00
                adc mt_zpbase+1
                bpl mt_tickntpfound             ;If goes positive, we're done
                sec
mt_freqsub:     lda mt_chnfreqlo,x
                sbc mt_zpbase
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                sbc mt_zpbase+1
                sta mt_chnfreqhi,x
mt_arpzero:     jmp mt_pulseexec

mt_tickntpfound:lda #$00                        ;Stop the speed to save
mt_tickntpfound2:
                sta mt_chnfxparam,x             ;rastertime on subsequent frames
                jmp mt_arpfreqresetvib

mt_ticknarp:    beq mt_arpzero
                jmp mt_arpeggio

mt_setfiltersub:tay
mt_filttblaccess0:
                lda mt_filttbl,y
                beq mt_sfsmod
                sta mt_d417reg+1
mt_filttblaccess1:
                lda mt_filttbl+1,y
                sta mt_d418reg+1
mt_filttblaccess2:
                lda mt_filttbl+2,y
                beq mt_sfscutoffskip
                sta mt_d416reg+1
mt_sfscutoffskip:
                lda #$00
                beq mt_sfscommon
mt_filttblaccess2b:
mt_sfsmod:      lda mt_filttbl+2,y
                sta mt_filtcutoffadd+1
mt_filttblaccess1b:
                lda mt_filttbl+1,y
mt_sfscommon:   sta mt_filttime+1
                tya
                beq mt_sfsnonext
mt_filttblaccess3:
                lda mt_filttbl+3,y
mt_sfsnonext:   sta mt_filtstep+1
                rts

mt_makespeed:   asl
                rol mt_zpbase+1
                asl
                rol mt_zpbase+1
                sta mt_zpbase
                rts


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
mt_settempoone: cmp #$f0
                bcs mt_setfader
                and #$7f
                sta mt_chntempo,x
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

                if (mt_ticknportaup & $ff00)!=(mt_ticknarp & $ff00)
                err
                endif

                if (mt_tick0arp & $ff00)!=(mt_tick0tempo & $ff00)
                err
                endif

;-------------------------------------------------------------------------------
; PLAYTUNE
;
; Initializes a tune specified by A (0 = first subtune).
;-------------------------------------------------------------------------------

playtune:       sta init_adc+1
                asl
init_adc:       adc #$00
                sta mt_initsongnum+1
                rts

;-------------------------------------------------------------------------------
; PLAYSFX
;
; Plays a sound effect indicated by A (0 = first sound effect). X is the
; channel number (0-2). Modifies X & Y!
;-------------------------------------------------------------------------------

playsfx:        ldy mt_sfxchntbl,x              ;Convert to SID reg. index
                ldx mt_chnsfx,y                 ;Channel already playing an
                beq psfx_chnok                  ;effect?
                cmp mt_chnsfxnum,y              ;Then, must check priority
                bcc psfx_done
psfx_chnok:     sta mt_chnsfxnum,y
                lda #$01
                sta mt_chnsfx,y
psfx_done:      rts

;-------------------------------------------------------------------------------
; RELOCATEMUSIC
;
; Modifies playroutine addresses to reflect the current song(s) loaded. This
; uses the same zeropage addresses as MUSIC (the playroutine itself), so don't
; call it while this is running!
;-------------------------------------------------------------------------------

relocatemusic:  lda #<(mt_musicdata+4)
                sta mt_rello
                lda #>(mt_musicdata+4)
                sta mt_relhi
                ldx #$00
rel_loop:       lda reladrtbllo,x
                sta mt_zpbase
                lda reladrtblhi,x
                sta mt_zpbase+1
                clc
                ldy reladdtbl,x
                bmi rel_subone
                bne rel_noaddone
rel_addone:     lda #$01
                bne rel_ok
rel_noaddone:   lda mt_musicdata-1,y
rel_ok:         adc mt_rello
                sta mt_rello
                ldy #$00
                sta (mt_zpbase),y
                lda mt_relhi
                adc #$00
                sta mt_relhi
rel_storecommon:iny
                sta (mt_zpbase),y
                inx
                bne rel_loop
rel_subone:     cpy #REL_END
                beq rel_done
                ldy #$00
                lda mt_rello
                sbc #$00                        ;Carry = 0
                sta (mt_zpbase),y
                lda mt_relhi
                sbc #$00
                bne rel_storecommon
rel_done:       rts

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

reladrtbllo:    dc.b <(mt_wavetblplusaccess+1)
                dc.b <(mt_wavetblaccess+1)
                dc.b <(mt_notetblplusaccess+1)
                dc.b <(mt_notetblaccess+1)
                dc.b <(mt_songtblloaccess+1)
                dc.b <(mt_songtblhiaccess+1)
                dc.b <(mt_patttblloaccess+1)
                dc.b <(mt_patttblhiaccess+1)
                dc.b <(mt_filttblaccess0+1)
                dc.b <(mt_filttblaccess1+1)
                dc.b <(mt_filttblaccess2+1)
                dc.b <(mt_filttblaccess1b+1)
                dc.b <(mt_filttblaccess3+1)
                dc.b <(mt_filttblaccess2b+1)
                dc.b <(mt_filttblaccess2c+1)

reladrtblhi:    dc.b >(mt_wavetblplusaccess+1)
                dc.b >(mt_wavetblaccess+1)
                dc.b >(mt_notetblplusaccess+1)
                dc.b >(mt_notetblaccess+1)
                dc.b >(mt_songtblloaccess+1)
                dc.b >(mt_songtblhiaccess+1)
                dc.b >(mt_patttblloaccess+1)
                dc.b >(mt_patttblhiaccess+1)
                dc.b >(mt_filttblaccess0+1)
                dc.b >(mt_filttblaccess1+1)
                dc.b >(mt_filttblaccess2+1)
                dc.b >(mt_filttblaccess1b+1)
                dc.b >(mt_filttblaccess3+1)
                dc.b >(mt_filttblaccess2b+1)
                dc.b >(mt_filttblaccess2c+1)

reladdtbl:      dc.b REL_INSTRSIZE
                dc.b REL_SUBONE
                dc.b REL_WAVESIZE
                dc.b REL_SUBONE
                dc.b REL_WAVESIZE
                dc.b REL_SONGSIZE
                dc.b REL_SONGSIZE
                dc.b REL_PATTSIZE
                dc.b REL_PATTSIZE
                dc.b REL_ADDONE
                dc.b REL_ADDONE
                dc.b REL_SUBONE
                dc.b REL_ADDONE
                dc.b REL_SUBONE
                dc.b REL_SUBONE
                dc.b REL_END

mt_sfxchntbl:   dc.b 0,7,14

mt_rello        = mt_chnwave
mt_relhi        = mt_chnwave+1

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
mt_chnad:       dc.b 0
mt_chnsr:       dc.b 0
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
mt_chnsfx:      dc.b 0
mt_chnsfxnum:   dc.b 0
                dc.b 0,0,0,0,0,0,0
                dc.b 0,0,0,0,0,0,0


