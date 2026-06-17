musiczpbase     = $fb                       ;5 zeropage addresses required

;-------------------------------------------------------------------------------
; RELOCATEMUSIC
;
; Modifies playroutine addresses to reflect the current song(s) loaded. This
; uses the same zeropage addresses as MUSIC (the playroutine itself), so don't
; call it while this is running!
;
; Parameters: A,X:Musicdata address
; Returns: -
; Modifies: A,X,Y,zeropage temp registers (default: $fb-$ff)
;-------------------------------------------------------------------------------

;musicdata+0 = songtable len (1/2)
;musicdata+1 = patttable len (1/2)
;musicdata+2 = wavetable len
;musicdata+3 = pulsetable len
;musicdata+4 = filttable len

REL_UNCHANGED_MINUS = $00
REL_UNCHANGED       = $01
REL_SONGTBL_MINUS   = $02
REL_SONGTBL         = $03
REL_PATTTBL_MINUS   = $04
REL_PATTTBL         = $05
REL_WAVETBL_MINUS   = $06
REL_WAVETBL         = $07
REL_PULSETBL_MINUS  = $08
REL_PULSETBL        = $09
REL_FILTTBL_MINUS   = $0a
REL_FILTTBL         = $0b
REL_END             = $80

relocatemusic:  sta musicaddresslo
                sta rel_lda+1
                clc
                adc #$05
                sta musiczpbase
                txa
                sta musicaddresshi
                sta rel_lda+2
                adc #$00
                sta musiczpbase+1
                ldx #$00
                stx $d415                         ;Reset cutoff lowbyte
rel_loop:       lda reladrtbllo,x
                sta musiczpbase+2
                lda reladrtblhi,x
                sta musiczpbase+3
                lda reladdtbl,x
                bmi rel_done
                lsr
                php
                beq rel_unchanged
                tay
                dey
                lda musiczpbase
                clc
rel_lda:        adc musicarea,y
                sta musiczpbase
                lda musiczpbase+1
                adc #$00
                sta musiczpbase+1
rel_unchanged:  plp
                ldy #$01
                lda musiczpbase
                sbc #$00
                sta (musiczpbase+2),y
                iny
                lda musiczpbase+1
                sbc #$00
                sta (musiczpbase+2),y
                inx
                bne rel_loop
rel_done:       rts

;-------------------------------------------------------------------------------
; PLAYTUNE
;
; Plays a tune
;
; Parameters: A:Song number
; Returns: -
; Modifies: A,X,Y
;-------------------------------------------------------------------------------

playtune:       sta playtune_adc+1
                asl
playtune_adc:   adc #$00
                sta vinitsongnum+1
                rts

;-------------------------------------------------------------------------------
; PLAYSFX
;
; Plays a sound effect.
;
; Parameters: A,X:Sound effect number
;             Y:Channel index (0,7,14)
; Returns: -
; Modifies: A,X,Y
;-------------------------------------------------------------------------------

playsfx:        pha
                lda #$01
                sta vchnsfx,y
                pla
                sta vchnsfxptrlo,y
                txa
                sta vchnsfxptrhi,y
                rts

;-------------------------------------------------------------------------------
; MUSIC
;
; Ninjatracker playroutine (call from interrupt each frame)
;
; Parameters: -
; Returns: -
; Modifies: A,X,Y,zeropage temp registers (default: $fb-$ff)
;-------------------------------------------------------------------------------

music:          ldx #$00
vinitsongnum:   ldy #$00
                bmi vchnloop
                txa
                ldx #21
vclearloop:     sta vchnsongpos-1,x
                dex
                bne vclearloop
                sta musiczpbase+3
                lda #$01
                sta musiczpbase+2
                lda #$ff
                sta vinitsongnum+1
                jsr vinitchn
                ldx #$07
                jsr vinitchn
                ldx #$0e
vinitchn:       tya
                sta vchnsongnum,x
                iny
                dec vchncounter,x
                rts

vfreqmod:       inc vchnwavedelay,x
                bne vfreqmod_ok
                lda vchnwavestored,x
                sta vchnwavepos,x
vfreqmod_ok:    lda vchnfreqlo,x
                clc
                adc vchnfreqmodlo,x
                sta vchnfreqlo,x
                sta $d400,x
                lda vchnfreqhi,x
                adc vchnfreqmodhi,x
                jmp vsetfreqhi

vchnloop:       ldy musiczpbase+2
                beq vfiltdone
                dec musiczpbase+3
                bmi vfirstfilt
                bne vfiltadd
vfiltnextminusaccess1:
vnextfilt:      lda vfiltnexttbl-1,y
                sta musiczpbase+2
                tay
vfilttimeminusaccess1:
vfirstfilt:     lda vfilttimetbl-1,y
                bmi vsetfilt
                sta musiczpbase+3
                bpl vfiltdone
vsetfilt:       and #$70
vmastervolume:  ora #$0f
                sta $d418
                lda #$01
                sta musiczpbase+3
vfilttimeminusaccess2:
                lda vfilttimetbl-1,y
vresonance:     ora #$f0
                sta $d417
vfiltaddminusaccess1:
                lda vfiltaddtbl-1,y
                bne vstorefilt
vfiltadd:       lda musiczpbase+4
                clc
vfiltaddminusaccess2:
                adc vfiltaddtbl-1,y
vstorefilt:     sta musiczpbase+4
                sta $d416
vfiltdone:
                jsr vchnexec
                ldx #$07
                jsr vchnexec
                ldx #$0e
vchnexec:       ldy vchnsfx,x
                beq vnosfx
                jmp vsfxexec
vnosfx:         ldy vchnwavepos,x
                beq vfreqmod
vwavetblminusaccess1:
                lda vwavetbl-1,y
                beq vhrnote
                cmp #$02
                beq vsetsr
                bcc vlegatonote
                cmp #$90
                bcc vwavechange
                beq vnowavechange

vnewfreqmod:    sta vchnwavedelay,x
vnexttblminusaccess1:
                lda vnexttbl-1,y
                sta vchnwavestored,x
vnotetblminusaccess1:
                lda vnotetbl-1,y
                asl
                sta vchnfreqmodlo,x
                lda #$00
                sta vchnwavepos,x
                bcc vfreqmodpos
                lda #$ff
vfreqmodpos:    asl vchnfreqmodlo,x
                rol
                sta vchnfreqmodhi,x
                jmp vwavedone

vhrnote:        jsr vhardres2
vnexttblminusaccess2:
vlegatonote:    lda vnexttbl-1,y
                beq vskipfilt
                sta musiczpbase+2
                lda #$00
                sta musiczpbase+3
vnotetblminusaccess2:
vskipfilt:      lda vnotetbl-1,y
                beq vskippulse
                sta vchnpulsepos,x
                lda #$00
                sta vchnpulsetime,x
vskippulse:     inc vchnwavepos,x
                jmp vreloadcounter

vwavetblaccess1:
vsetsr:         lda vwavetbl,y
                sta $d404,x
vnotetblminusaccess3:
                lda vnotetbl-1,y
                sta $d405,x
vnexttblminusaccess3:
                lda vnexttbl-1,y
                sta $d406,x
                iny
                bne vnowavechange
vwavechange:    sta $d404,x
vnexttblminusaccess4:
vnowavechange:  lda vnexttbl-1,y
                sta vchnwavepos,x
vnotetblminusaccess4:
                lda vnotetbl-1,y
                asl
                bcs vabsnote
                adc vchnnote,x
vabsnote:       tay
                lda vfreqtbl-26,y
                sta vchnfreqlo,x
                sta $d400,x
                lda vfreqtbl-25,y
vsetfreqhi:     sta $d401,x
                sta vchnfreqhi,x
vwavedone:      inc vchncounter,x
                bne vnonewnote

vgetnewnote:    ldy vchnpattnum,x
vpatttblloaccess:
                lda vpatttbllo,y
                clc
                adc musicaddresslo
                sta musiczpbase
vpatttblhiaccess:
                lda vpatttblhi,y
                adc musicaddresshi
                sta musiczpbase+1
                ldy vchnpattpos,x
                lda (musiczpbase),y
                cmp #$c0                        ;Duration?
                bcc vnoduration
                sta vchnduration,x
                iny
                lda (musiczpbase),y
vnoduration:    cmp #$60
                bcs vnotewithwave
                cmp #$5b
                bcc vnotewithoutwave
                beq vrest
vcommand:       and #$07
                cmp #$07
                sta vcmdsta+1
                iny
                lda (musiczpbase),y
                bcs vcmdfilt
vcmdsta:        sta $d400,x
                bcc vrest
vcmdfilt:       sta musiczpbase+2
                lda #$00
                sta musiczpbase+3
                beq vrest
vnotewithoutwave:
                adc vchntrans,x
                asl
                sta vchnnote,x
                lda vchnwavepreset,x
                bne vsetpos
vnotewithwave:  beq vwaveonly
                sbc #$61
                adc vchntrans,x               ;Adds one too much (C=1)
                asl
                sta vchnnote,x
vwaveonly:      iny
                lda (musiczpbase),y
                sta vchnwavepreset,x
vsetpos:        sta vchnwavepos,x
vrest:          iny
                lda (musiczpbase),y
                beq vendpatt
                tya
vendpatt:       sta vchnpattpos,x
                rts

vnonewnote:     bmi vpulseexec
vreloadcounter: lda vchnpattpos,x
                bne vnonewpatt
                ldy vchnsongnum,x
vsongtblloaccess:
                lda vsongtbllo,y
                clc
                adc musicaddresslo
                sta musiczpbase
vsongtblhiaccess:
                lda vsongtblhi,y
                adc musicaddresshi
                sta musiczpbase+1
                ldy vchnsongpos,x
                lda (musiczpbase),y
                bpl vnotrans
                sta vchntrans,x
                iny
                lda (musiczpbase),y
vnotrans:       sta vchnpattnum,x
                iny
                lda (musiczpbase),y
                beq vsongloop
vnoloop:        tya
                bne vloopcommon
vsongloop:      iny
                lda (musiczpbase),y
vloopcommon:    sta vchnsongpos,x

vnonewpatt:     lda vchnduration,x
                sta vchncounter,x
                rts

vpulseexec:     ldy vchnpulsepos,x
                beq vnextchn
                dec vchnpulsetime,x
                beq vnextpulse
                bmi vfirstpulse
vpulseadd:      clc
vpulseaddminusaccess1:
                lda vpulseaddtbl-1,y
                adc vchnpulse,x
                adc #$00
                jmp vstorepulse
vpulsenextminusaccess1:
vnextpulse:     lda vpulsenexttbl-1,y
                sta vchnpulsepos,x
                tay
vpulsetimeminusaccess1:
vfirstpulse:    lda vpulsetimetbl-1,y
                bpl vnewpulsemod
                lda #$01
                sta vchnpulsetime,x
vpulseaddminusaccess2:
                lda vpulseaddtbl-1,y
vstorepulse:    sta vchnpulse,x
vstorepulse2:   sta $d402,x
                sta $d403,x
vnextchn:       rts

vnewpulsemod:   sta vchnpulsetime,x
                rts

vsfxexec:       lda vchnsfxptrlo,x
                sta musiczpbase
                lda vchnsfxptrhi,x
                sta musiczpbase+1
                cpy #$03
                bcs vsfxexec_initdone
                jsr vhardres
                tay
                lda (musiczpbase),y
                jsr vstorepulse2
                iny
                inc vchnsfx,x
                bne vsfxexec_done
vsfxexec_initdone:
                lda (musiczpbase),y
                bne vsfxexec_noend
vsfxexec_end:   jsr vhardres2
                sta vchnsfx,x
                sta vchnwavepos,x
                sta vchnwavestored,x
                jmp vwavedone
vsfxexec_noend: asl
                sta vsfxexec_resty+1
                iny
                lda (musiczpbase),y                ;Then take a look at the coming
                beq vsfxexec_nowavechange     ;byte
                cmp #$82                      ;Is it a waveform or a note?
                bcs vsfxexec_nowavechange
                iny
vsfxexec_wavechange:
                sta $d404,x
vsfxexec_nowavechange:
                tya
                sta vchnsfx,x
vsfxexec_resty: ldy #$00
                lda vfreqtbl-24,y             ;Get frequency
                sta $d400,x
                lda vfreqtbl-23,y
                sta $d401,x
                ldy #$01
                lda (musiczpbase),y
                sta $d405,x
                iny
                lda (musiczpbase),y
                sta $d406,x
vsfxexec_done:  jmp vwavedone

vhardres:       lda #$00
vhardres2:      sta $d404,x
                sta $d405,x
                sta $d406,x
                rts

        ;Tables

vfreqtbl:       dc.w $022a,$024a,$026d,$0292,$02b9,$02e3,$030f,$033e,$036f,$03a3,$03db,$0415
                dc.w $0454,$0495,$04db,$0525,$0573,$05c7,$061e,$067c,$06de,$0747,$07b6,$082b
                dc.w $08a8,$092b,$09b7,$0a4b,$0ae7,$0b8e,$0c3d,$0cf8,$0dbd,$0e8e,$0f6c,$1057
                dc.w $1150,$1257,$136e,$1496,$15cf,$171c,$187b,$19f0,$1b7b,$1d1d,$1ed8,$20ae
                dc.w $22a0,$24af,$26dd,$292d,$2b9f,$2e38,$30f7,$33e0,$36f6,$3a3b,$3db1,$415d
                dc.w $4540,$495e,$4dbb,$525a,$573f,$5c70,$61ef,$67c1,$6ded,$7476,$7b63,$82ba
                dc.w $8a80,$92bc,$9b76,$a4b4,$ae7f,$b8e0,$c3de,$cf83,$dbda,$e8ed,$f6c7,$ffff

reladrtbllo:    dc.b <vsongtblloaccess
                dc.b <vsongtblhiaccess
                dc.b <vpatttblloaccess
                dc.b <vpatttblhiaccess
                dc.b <vwavetblminusaccess1
                dc.b <vwavetblaccess1
                dc.b <vnotetblminusaccess1
                dc.b <vnotetblminusaccess2
                dc.b <vnotetblminusaccess3
                dc.b <vnotetblminusaccess4
                dc.b <vnexttblminusaccess1
                dc.b <vnexttblminusaccess2
                dc.b <vnexttblminusaccess3
                dc.b <vnexttblminusaccess4
                dc.b <vpulsetimeminusaccess1
                dc.b <vpulseaddminusaccess1
                dc.b <vpulseaddminusaccess2
                dc.b <vpulsenextminusaccess1
                dc.b <vfilttimeminusaccess1
                dc.b <vfilttimeminusaccess2
                dc.b <vfiltaddminusaccess1
                dc.b <vfiltaddminusaccess2
                dc.b <vfiltnextminusaccess1

reladrtblhi:    dc.b >vsongtblloaccess
                dc.b >vsongtblhiaccess
                dc.b >vpatttblloaccess
                dc.b >vpatttblhiaccess
                dc.b >vwavetblminusaccess1
                dc.b >vwavetblaccess1
                dc.b >vnotetblminusaccess1
                dc.b >vnotetblminusaccess2
                dc.b >vnotetblminusaccess3
                dc.b >vnotetblminusaccess4
                dc.b >vnexttblminusaccess1
                dc.b >vnexttblminusaccess2
                dc.b >vnexttblminusaccess3
                dc.b >vnexttblminusaccess4
                dc.b >vpulsetimeminusaccess1
                dc.b >vpulseaddminusaccess1
                dc.b >vpulseaddminusaccess2
                dc.b >vpulsenextminusaccess1
                dc.b >vfilttimeminusaccess1
                dc.b >vfilttimeminusaccess2
                dc.b >vfiltaddminusaccess1
                dc.b >vfiltaddminusaccess2
                dc.b >vfiltnextminusaccess1

reladdtbl:      dc.b REL_UNCHANGED
                dc.b REL_SONGTBL
                dc.b REL_SONGTBL
                dc.b REL_PATTTBL
                dc.b REL_PATTTBL_MINUS
                dc.b REL_UNCHANGED
                dc.b REL_WAVETBL_MINUS
                dc.b REL_UNCHANGED_MINUS
                dc.b REL_UNCHANGED_MINUS
                dc.b REL_UNCHANGED_MINUS
                dc.b REL_WAVETBL_MINUS
                dc.b REL_UNCHANGED_MINUS
                dc.b REL_UNCHANGED_MINUS
                dc.b REL_UNCHANGED_MINUS
                dc.b REL_WAVETBL_MINUS
                dc.b REL_PULSETBL_MINUS
                dc.b REL_UNCHANGED_MINUS
                dc.b REL_PULSETBL_MINUS
                dc.b REL_PULSETBL_MINUS
                dc.b REL_UNCHANGED_MINUS
                dc.b REL_FILTTBL_MINUS
                dc.b REL_UNCHANGED_MINUS
                dc.b REL_FILTTBL_MINUS
                dc.b REL_END

        ;Variables

musicaddresslo: dc.b 0
musicaddresshi: dc.b 0

        ;Channel variables

vchnsongpos:    dc.b 0
vchnpattnum:    dc.b 0
vchnpattpos:    dc.b 0
vchntrans:      dc.b 0
vchncounter:    dc.b 0
vchnwavepos:    dc.b 0
vchnwavestored: dc.b 0

                dc.b 0,0,0,0,0,0,0
                dc.b 0,0,0,0,0,0,0

vchnwavepreset: dc.b 0
vchnwavedelay:  dc.b 0
vchnsongnum:    dc.b 0
vchnpulse:      dc.b 0
vchnpulsepos:   dc.b 0
vchnpulsetime:  dc.b 0
vchnnote:       dc.b 0

                dc.b 0,0,0,0,0,0,0
                dc.b 0,0,0,0,0,0,0

vchnduration:   dc.b 0
vchnfreqlo:     dc.b 0
vchnfreqhi:     dc.b 0
vchnfreqmodlo:  dc.b 0
vchnfreqmodhi:  dc.b 0
vchnsfx:        dc.b 0
vchnunused:     dc.b 0

                dc.b 0,0,0,0,0,0,0
                dc.b 0,0,0,0,0,0,0

vchnsfxptrlo    = vchnfreqmodlo
vchnsfxptrhi    = vchnfreqmodhi

        ;Dummy addresses, will be changed as music is loaded

vsongtbllo:
vsongtblhi:
vpatttbllo:
vpatttblhi:
vwavetbl:
vnotetbl:
vnexttbl:
vpulsetimetbl:
vpulseaddtbl:
vpulsenexttbl:
vfilttimetbl:
vfiltaddtbl:
vfiltnexttbl:
musicarea:
