; ======================================
; Part of Odin Tracker 1.13 for C64 by Zed on 17 Apr 2001.
;
; Editor's player.
; ======================================

; ======================================
player_istrument_play:
; Run keyjazz. This always tests in channel 0.
; ======================================
;  Input: A: note (0 means no key pressed)
;         Y: instrument
; ======================================
; Test always in channel 0.
        ldx #0
        sta player_keyjazznote
        sty player_keyjazzinst
        cmp #$00
        bne pip_normalnote
        lda #$fe
        sta chn_gateon,x
pip_nonewnote1:
        jmp pip_nonewnote
pip_normalnote:
; If key was released, always start the new note.
        tay
        lda chn_gateon,x
        lsr
        tya
        bcc pip_newnote
; If the same key is held, do not start the sound again.
        cmp player_previouskeyjazznote
        beq pip_nonewnote1
pip_newnote:
; Clear player data.
        lda #$00
        ldy #PLAYERCLEARDATASIZE
pip_clear:
        sta playercleardata-1,y
        dey
        bne pip_clear
        lda #$0f
        sta globalvolume
        lda player_keyjazznote
        sta chn_note,x
        lda player_keyjazzinst
        sta chn_inst,x
        tay
; Copy changeable instrument parameters to channel.
        lda INSTRUMENTS_AD,y            ; Copy AD.
        sta chn_ad,x
        lda INSTRUMENTS_SR,y            ; Copy SR.
        sta chn_sr,x
        lda INSTRUMENTS_WAVETABLESTART,y ; Wave table start index.
        sta chn_waveidx,x
        lda INSTRUMENTS_ARPTABLESTART,y ; Arpeggio table start index.
        sta chn_arpidx,x
        lda INSTRUMENTS_VIBDELAY,y      ; Copy vibrato delay.
        sta chn_vibdelay,x
; Set pulse width.
        lda INSTRUMENTS_PULSEWIDTH,y
        asl
        asl
        asl
        asl
        sta chn_plswidthlo,x
        lda INSTRUMENTS_PULSEWIDTH,y
        lsr
        lsr
        lsr
        lsr
        sta chn_plswidthhi,x
; Set pulse speed.
        lda INSTRUMENTS_PULSESPEED,y
        sta chn_plsspeed,x
; Set pulse limits.
        lda INSTRUMENTS_PULSELIMITS,y
        lsr
        lsr
        lsr
        lsr
        sta chn_plslimitdown,x
        lda INSTRUMENTS_PULSELIMITS,y
        and #$0f
        sta chn_plslimitup,x
; TODO init filter to operate on channel 0 !!!
; The user should be able to set up filter if he needs.
; The code below is not OK, because it always enable filters,
; which is not what we need.
; So for now, no filtering in keyjazz mode. Sorry.
;        lda INSTRUMENTS_FILTERTABLESTART,y  ; Filter table start index.
;        sta filter_idx
;        lda INSTRUMENTS_FILTERTABLEEND,y ; Copy filter table end.
;        sta filter_end
;        lda INSTRUMENTS_FILTERTABLELOOP,y ; Copy filter table loop.
;        sta filter_loop
;        lda #$f1
;        sta filter_input
;        lda #$10
;        sta filter_mode
; Reset vibrato and pulse width modulation.
        lda #$00
        sta chn_plsdir,x
        sta chn_vibpos,x
; Set gate on.
        lda #$ff
        sta chn_gateon,x

pip_nonewnote:
        lda #$00
        sta chn_vibdepth,x
        jsr process_instrument
        ldy chn_finalnote,x
        lda freqtablelo,y
        sta chn_freqlo,x
        lda freqtablehi,y
        sta chn_freqhi,x
; Do vibrato and update vibrato position.
        jsr calcvibrato
        lda chn_vibpos,x
        clc
        adc chn_vibspeed,x
        sta chn_vibpos,x

; Process filter table.
        ldy filter_idx
        lda FILTERTABLE,y
        sta filter_cutoff
; Advance filter table index.
        iny
        cpy filter_end
        bcc pip_filteridxok
        beq pip_filteridxok
        ldy filter_loop
pip_filteridxok:
        sty filter_idx

; Dump everything into the SID chip.
        ldx #$00
        ldy sidregindex,x
        lda chn_plswidthlo,x
        sta $d402,y
        lda chn_plswidthhi,x
        sta $d403,y
        lda chn_finfreqlo,x
        sta $d400,y
        lda chn_finfreqhi,x
        sta $d401,y
        lda chn_waveform,x
        cmp #$ff
        beq pip_channeloff
        and chn_gateon,x
        sta $d404,y
        lda chn_ad,x
        sta $d405,y
        lda chn_sr,x
        sta $d406,y
        jmp pip_channeldone
pip_channeloff:
        lda #$00
        sta $d404,y
        sta $d405,y
        sta $d406,y
pip_channeldone:
        lda filter_cutoff
        sta $d416
        lda filter_input
        sta $d417
        lda globalvolume
        ora filter_mode
        sta $d418
        lda chn_note,x
        sta player_previouskeyjazznote
        rts

; ======================================
player_init:
; Initialize all player variables and reset SID.
; ======================================
; Initialize all player variables.
        jsr player_resetchannels
; Init speed.
        lda #6
        sta speed
; Set global volume to maximum.
        lda #$0f
        sta globalvolume
; Init hard restart counters.
        lda #2
        sta chn_hardrestart+0
        sta chn_hardrestart+1
        sta chn_hardrestart+2

; ======================================
player_stop:
; ======================================
; Shut up SID.
        ldy #$18
ps_resetsidloop:
        lda #$08                        ; Reset SID.
        sta $d400,y
        lda #$00
        sta $d400,y
        dey
        bpl ps_resetsidloop
        rts

; ======================================
player_start:
; Start playing.
; ======================================
;  Input: A: start order number
;         X: start pattern row
;         Y: if nonzero, play single pattern only
;         chn_muted[]
; ======================================
; Set order position.
        sta ordernumber
        sta nextordernumber
        stx firsttrackrow               ; Able to start playing from any row.
        sty player_singlepattern        ; Play single pattern if nonzero.
        lda #$80                        ; Force a pattern jump.
        sta forcenewpattern
; Init speedcounter.
        ldy speed
        dey
        sty speedcounter

; ======================================
player_resetchannels:
; Reset channel data.
; ======================================
        lda #$00
        ldy #PLAYERCLEARDATASIZE
pr_clearloop:
        sta playercleardata-1,y
        dey
        bne pr_clearloop
;;;;        sta sidlogger+1
        rts

; ======================================
player_play:
; Call this in every frame.
; ======================================
; Play 1 tick of music.
; ======================================
; Update the mod3 counter which is used by the arpeggio effect (Axy).
        dec mod3counter
        bpl pp_mod3counterdone
        lda #2
        sta mod3counter
pp_mod3counterdone:
; Speed 0 stops song, but continues effects.
        lda speed
        beq pp_allframes                ; Do stuff that is done in all frames.
; Update speed counter and see if it is time for a new trackrow.
        inc speedcounter
        lda speedcounter
        cmp speed
        bne pp_allframes                ; Do stuff that is done in all frames.
; Start new row.
        lda #$00                        ; Reset speed counter.
        sta speedcounter
        lda forcenewpattern             ; Fetching a new pattern is forced at
        bmi pp_newpatternforced         ; start of tune and by order jump and pattern break.
        inc trackrow                    ; Advance one row.
        lda trackrow                    ; Check if we reached the end of pattern.
        cmp #64
        bmi pp_pattern_ok
pp_newpatternforced:
        jsr start_newpattern            ; !!!! Expand inline!

pp_pattern_ok:
; Create offset into track. trackrow3=3*trackrow
        lda trackrow
        asl
        adc trackrow
        sta trackrow3
; Fetch new lines from tracks.
        ldx #2
pp_fetchnextchn:
        lda chn_trackptrlo,x
        ldy chn_trackptrhi,x
        jsr fetchrow                    ; !!!! Expand inline!
        dex
        bpl pp_fetchnextchn

; The following stuff is executed in every frame.
pp_allframes:
        ldx #2
ppaf_nextchn:
; Play the note currently in chn_note.
; Suppose there is no vibrato.
; Effect and instrument vibrato can override this.
        lda #$00
        sta chn_vibdepth,x
; First check if there is an instrument. If there is none,
; there is no instrument wavetable/arpeggio/vibrato to do.
        lda chn_inst,x
        beq ppaf_noinst
; This is done before effects, so that they can override this.
        jsr process_instrument
ppaf_noinst:
; Now process track effects.
        ldy chn_effect,x
;;;;        beq ppaf_noeffect
        cpy #3
        bne ppaf_notslidetonote
        jsr effect03
        jmp ppaf_dovibrato
ppaf_notslidetonote:
        lda effectpointerslo,y
        sta ppaf_effectcall+1
        lda effectpointershi,y
        sta ppaf_effectcall+2
ppaf_effectcall:
        jsr $ffff                       ; Self modifying code.
; Set freq for note of channel X from freq table.
; Add slide frequency, which is negative when sliding down.
;;;;ppaf_noeffect:
        ldy chn_finalnote,x
        lda freqtablelo,y
        sta chn_notefreqlo,x
        clc
        adc chn_slidefreqlo,x
        sta chn_freqlo,x
        lda freqtablehi,y
        sta chn_notefreqhi,x
        adc chn_slidefreqhi,x
        sta chn_freqhi,x
ppaf_dovibrato:
; Do vibrato and update vibrato position.
        jsr calcvibrato
        lda chn_vibpos,x
        clc
        adc chn_vibspeed,x
        sta chn_vibpos,x
        dex
        bpl ppaf_nextchn

; Process filter table.
        ldy filter_idx
        beq ppaf_filterdone
        lda FILTERTABLE,y
        sta filter_cutoff
; Advance filter table index.
        iny
        cpy filter_end
        bcc ppaf_filteridxok
        beq ppaf_filteridxok
        ldy filter_loop
ppaf_filteridxok:
        sty filter_idx
ppaf_filterdone:

; Do hardrestart stuff.
; !!!! TODO: shit happens if we have to look ahead into the next pattern.
; This should work but it is damn waste of time.
        lda forcenewpattern             ; Fetching a new pattern is forced at
        bmi pphr_newpatternforced       ; start of tune and by order jump and pattern break.
        ldx trackrow
        inx
        txa
        and #$3f
        stx nexttrackrow
        bne pphr_pattern_ok
pphr_newpatternforced:
        lda firsttrackrow               ; For pattern break, this is the next row.
        sta nexttrackrow
        jsr look_newpattern             ; !!!! Expand inline!

pphr_pattern_ok:
; Create offset into track. Y=3*nexttrackrow
        lda nexttrackrow
        asl
        adc nexttrackrow
        tay
        ldx #2
pphr_nextchn:
; Is it time for hardrestart?
        lda speedcounter
        clc
        adc chn_hardrestart,x
        cmp speed
        bcc pphr_nohardrestart
        lda chn_trackptrlo,x
        sta player_trackptr
        lda chn_trackptrhi,x
        sta player_trackptr+1
        lda (player_trackptr),y
        and #$7f
        beq pphr_nohardrestart          ; No note -> no hardrestart.
        cmp #97
        beq pphr_nohardrestart          ; Note off -> no hardrestart.
; We will have a new note, but if we'll also have slide to note (effect 3)
; never do hardrestart.
        lda (player_trackptr),y
        bmi pphr_hardrestart            ; Can't be effect 3 -> do hardrestart.
        iny
        lda (player_trackptr),y
        dey
        and #$e0
        cmp #$60
        beq pphr_nohardrestart          ; This is effect 3 -> no hardrestart.
pphr_hardrestart:
; Clear AD/SR and waveform to zero.
; Maybe some other ways would result in better hardrestart.
; Tell me if you have any good ideas.
        lda #$00
        sta chn_waveform,x
        sta chn_ad,x
        sta chn_sr,x
pphr_nohardrestart:
        dex
        bpl pphr_nextchn

; Dump everything into the SID chip.
        ldx #2
pp_dump2sid:
        ldy sidregindex,x
        lda chn_plswidthlo,x
        sta $d402,y
        lda chn_plswidthhi,x
        sta $d403,y
        lda chn_finfreqlo,x
        sta $d400,y
        lda chn_finfreqhi,x
        sta $d401,y
        lda chn_muted,x
        bne ptds_channeloff
; Channel is not muted. If waveform is $FF, mute with hard restart, though.
        lda chn_waveform,x
        cmp #$ff
        beq ptds_channeloff
        and chn_gateon,x
        sta $d404,y
        lda chn_ad,x
        sta $d405,y
        lda chn_sr,x
        sta $d406,y
        jmp ptds_channeldone
ptds_channeloff:
        lda #$00
        sta $d404,y
        sta $d405,y
        sta $d406,y
ptds_channeldone:
        dex
        bpl pp_dump2sid
; Update filter parameters.
        lda filter_cutoff
        sta $d416
        lda filter_input
        sta $d417
        lda globalvolume
        ora filter_mode
        sta $d418

;;;;sidlogbase = $8000
;;;;xd400      = sidlogbase
;;;;xd401      = sidlogbase+$0100
;;;;xd402      = sidlogbase+$0200
;;;;xd403      = sidlogbase+$0300
;;;;xd404      = sidlogbase+$0400
;;;;xd405      = sidlogbase+$0500
;;;;xd406      = sidlogbase+$0600
;;;;xd407      = sidlogbase+$0700
;;;;xd408      = sidlogbase+$0800
;;;;xd409      = sidlogbase+$0900
;;;;xd40a      = sidlogbase+$0a00
;;;;xd40b      = sidlogbase+$0b00
;;;;xd40c      = sidlogbase+$0c00
;;;;xd40d      = sidlogbase+$0d00
;;;;xd40e      = sidlogbase+$0e00
;;;;xd40f      = sidlogbase+$0f00
;;;;xd410      = sidlogbase+$1000
;;;;xd411      = sidlogbase+$1100
;;;;xd412      = sidlogbase+$1200
;;;;xd413      = sidlogbase+$1300
;;;;xd414      = sidlogbase+$1400
;;;;xd415      = sidlogbase+$1500
;;;;xd416      = sidlogbase+$1600
;;;;xd417      = sidlogbase+$1700
;;;;xd418      = sidlogbase+$1800
;;;;
;;;;sidlogger:
;;;;        ldx #$00
;;;;; Log voice 1.
;;;;        lda chn_finfreqlo+0
;;;;        sta xd400,x
;;;;        lda chn_finfreqhi+0
;;;;        sta xd401,x
;;;;        lda chn_plswidthlo+0
;;;;        sta xd402,x
;;;;        lda chn_plswidthhi+0
;;;;        sta xd403,x
;;;;        lda chn_waveform+0
;;;;        and chn_gateon+0
;;;;        sta xd404,x
;;;;        lda chn_ad+0
;;;;        sta xd405,x
;;;;        lda chn_sr+0
;;;;        sta xd406,x
;;;;; Log voice 2.
;;;;        lda chn_finfreqlo+1
;;;;        sta xd407,x
;;;;        lda chn_finfreqhi+1
;;;;        sta xd408,x
;;;;        lda chn_plswidthlo+1
;;;;        sta xd409,x
;;;;        lda chn_plswidthhi+1
;;;;        sta xd40a,x
;;;;        lda chn_waveform+1
;;;;        and chn_gateon+1
;;;;        sta xd40b,x
;;;;        lda chn_ad+1
;;;;        sta xd40c,x
;;;;        lda chn_sr+1
;;;;        sta xd40d,x
;;;;; Log voice 3.
;;;;        lda chn_finfreqlo+2
;;;;        sta xd40e,x
;;;;        lda chn_finfreqhi+2
;;;;        sta xd40f,x
;;;;        lda chn_plswidthlo+2
;;;;        sta xd410,x
;;;;        lda chn_plswidthhi+2
;;;;        sta xd411,x
;;;;        lda chn_waveform+2
;;;;        and chn_gateon+2
;;;;        sta xd412,x
;;;;        lda chn_ad+2
;;;;        sta xd413,x
;;;;        lda chn_sr+2
;;;;        sta xd414,x
;;;;; Log filter.
;;;;        lda filter_cutoff
;;;;        sta xd416,x
;;;;        lda filter_input
;;;;        sta xd417,x
;;;;        lda globalvolume
;;;;        ora filter_mode
;;;;        sta xd418,x
;;;;        inx
;;;;        beq logdone
;;;;        stx sidlogger+1
;;;;logdone:
        rts

; ======================================
process_instrument:
; Process instrument arpeggio, vibrato, etc.
; ======================================
;  Input: X: channel number
; Output: chn_*, !!!! many
;   Uses: chn_*, !!!! many
; ======================================
; Process instrument vibrato.
        lda chn_vibdelay,x
        bne pi_vibdelayed
        ldy chn_inst,x
        lda INSTRUMENTS_VIBDEPTH_SPEED,y
        and #$f0
        sta chn_vibdepth,x
        lda INSTRUMENTS_VIBDEPTH_SPEED,y
        and #$0f
        sta chn_vibspeed,x
        bpl pi_vibdone                  ; Jump always.
pi_vibdelayed:
        dec chn_vibdelay,x
pi_vibdone:

; Do pulse width modulation.
        lda chn_plsspeed,x
        beq pi_nopulse
        ldy chn_plsdir,x
        beq pi_pulseup
; Decrement pulse width. If lower limit is reached, reverse direction.
        lda chn_plswidthlo,x
        sec
        sbc chn_plsspeed,x
        sta chn_plswidthlo,x
        lda chn_plswidthhi,x
        sbc #0
        cmp chn_plslimitdown,x
        bpl pi_pulsedone
        lda #$00
        sta chn_plsdir,x
        sta chn_plswidthlo,x
        lda chn_plslimitdown,x
        bpl pi_pulsedone                ; Jump always.
; Increment pulse width. If upper limit is reached, reverse direction.
pi_pulseup:
        clc
        adc chn_plswidthlo,x
        sta chn_plswidthlo,x
        lda chn_plswidthhi,x
        adc #0
        cmp chn_plslimitup,x
        bmi pi_pulsedone
        beq pi_pulsedone
        lda #$ff
        sta chn_plsdir,x
        sta chn_plswidthlo,x
        lda chn_plslimitup,x
pi_pulsedone:
        sta chn_plswidthhi,x
pi_nopulse:

; Process wave table.
        ldy chn_waveidx,x
        lda WAVETABLE,y
        sta chn_waveform,x
; Advance wavetable index.
        iny
        tya
        ldy chn_inst,x
        cmp INSTRUMENTS_WAVETABLEEND,y
        bcc pi_waveidxok
        beq pi_waveidxok
        lda INSTRUMENTS_WAVETABLELOOP,y
pi_waveidxok:
        sta chn_waveidx,x

; If slide to note is active, do not do arpeggio.
        lda chn_note,x
        ldy chn_effect,x
        cpy #3
        beq pi_noteready
; Process arpeggio table.
        ldy chn_arpidx,x
        lda ARPEGGIOTABLE,y
; If arpeggio table entry is < $80 then add it to note (relative arpeggio),
; otherwise use entry-$80 (absolute arpeggio)
        bmi pi_arptableabs
        clc
        adc chn_note,x
        adc chn_transpose,x
        jmp pi_arptablenoteok
pi_arptableabs:
        and #$7f
        clc
        adc #1                          ; Add 1 because C-0 is 1
pi_arptablenoteok:
; Advance arpeggio table index.
        sta pi_notetemp+1
        iny
        tya
        ldy chn_inst,x
        cmp INSTRUMENTS_ARPTABLEEND,y
        bcc pi_arpidxok
        beq pi_arpidxok
        lda INSTRUMENTS_ARPTABLELOOP,y
pi_arpidxok:
        sta chn_arpidx,x
pi_notetemp:
        lda #$00                        ; Self modifying code.
pi_noteready:
        sta chn_finalnote,x
        rts

; ======================================
calcvibrato:
; Calc vibrato for channel X.
; ======================================
;  Input: X: channel number
;         chn_freq??
;         chn_vibpos,
;         chn_vibdepth
; Output: chn_finfreq??
;         chn_vibpos
; ======================================
; Get vibrato frequency adder from table using depth.
        lda chn_vibpos,x
        tay
        and #$10
        beq cv_forward
        tya
        eor #$0f
        .byte $24                       ; BIT $ff
cv_forward:
        tya
        and #$0f
        ora chn_vibdepth,x              ; == depth*16
        tay
; vibrato_table,y is now the frequency that has to be
; added to or subtracted from the channel frequency.
        lda chn_vibpos,x
        and #$20
        bne cv_addfreq
; chn_freq-=vibrato_table,y
        lda chn_freqlo,x
        sec
        sbc vibrato_table,y
        sta chn_finfreqlo,x
        lda chn_freqhi,x
        sbc #0
        sta chn_finfreqhi,x
        rts
cv_addfreq:
; chn_notefreq+=vibrato_table,y
        lda chn_freqlo,x
        clc
        adc vibrato_table,y
        sta chn_finfreqlo,x
        lda chn_freqhi,x
        adc #0
        sta chn_finfreqhi,x
        rts

; ======================================
effect01:
; ======================================
; Slide down by param if param<$80, otherwise up by param-$80.
; ======================================
; Calculate slide adder.
        lda chn_effectpar,x
        and #$7f
; Multiply parameter by 16 to get slide adder.
        tay
        asl
        asl
        asl
        asl
        sta player_vibratotemp
        tya
        lsr
        lsr
        lsr
        lsr
        sta player_vibratotemp+1
        ldy chn_effectpar,x
        bmi effect01up
; Slide down - subtract from frequency.
        lda chn_slidefreqlo,x
        sec
        sbc player_vibratotemp
        sta chn_slidefreqlo,x
        lda chn_slidefreqhi,x
        sbc player_vibratotemp+1
        sta chn_slidefreqhi,x
        rts
; Slide up - add to frequency.
effect01up:
        lda chn_slidefreqlo,x
        clc
        adc player_vibratotemp
        sta chn_slidefreqlo,x
        lda chn_slidefreqhi,x
        adc player_vibratotemp+1
        sta chn_slidefreqhi,x
; Dummy entry for effect 0.
effect00:
        rts

; ======================================
effect02:
; ======================================
; Set pulse width.
; Parameter is bits 11..4 of pulse width.
; ======================================
        lda chn_effectpar,x
        asl
        asl
        asl
        asl
        sta chn_plswidthlo,x
        lda chn_effectpar,x
        lsr
        lsr
        lsr
        lsr
        sta chn_plswidthhi,x
        rts

; ======================================
effect03:
; ======================================
; Slide to note. Damn hack.
; ======================================
        lda chn_effectpar,x
; Multiply parameter by 16 to get slide adder.
        tay
        asl
        asl
        asl
        asl
        sta player_vibratotemp
        tya
        lsr
        lsr
        lsr
        lsr
        sta player_vibratotemp+1
        jsr freqcmp
        bcc effect03up
; Slide down.
        lda chn_freqlo,x
        sec
        sbc player_vibratotemp
        sta chn_freqlo,x
        lda chn_freqhi,x
        sbc player_vibratotemp+1
        sta chn_freqhi,x
; Check if we have shot past the destination frequency.
        jsr freqcmp
        bcc effect03stop                ; Reached, stop.
        rts                             ; Still not reached.
; Slide up.
effect03up:
        lda chn_freqlo,x
        clc
        adc player_vibratotemp
        sta chn_freqlo,x
        lda chn_freqhi,x
        adc player_vibratotemp+1
        sta chn_freqhi,x
; Check if we have shot past the destination frequency.
        jsr freqcmp
        bcs effect03stop                ; Reached, stop.
        beq effect03stop                ; Reached, stop.
        rts                             ; Still not reached.
effect03stop:
        lda chn_notefreqlo,x
        sta chn_freqlo,x
        lda chn_notefreqhi,x
        sta chn_freqhi,x
        rts

; ======================================
effect04:
; ======================================
; Vibrato.
; High nybble of parameter is depth, low is speed.
; ======================================
        lda chn_effectpar,x
        and #$f0
        sta chn_vibdepth,x
        lda chn_effectpar,x
        and #$0f
        sta chn_vibspeed,x
        rts

; ======================================
effect05:
; ======================================
; Set pulse speed.
; ======================================
        lda chn_effectpar,x
        sta chn_plsspeed,x
        rts

; ======================================
effect06:
; ======================================
; Set pulse limits.
; ======================================
        lda chn_effectpar,x
        lsr
        lsr
        lsr
        lsr
        sta chn_plslimitdown,x
        lda chn_effectpar,x
        and #$0f
        sta chn_plslimitup,x
        rts

; ======================================
effect07:
; ======================================
; Set Attack/Decay.
; ======================================
        lda chn_effectpar,x
        sta chn_ad,x
        rts

; ======================================
effect08:
; ======================================
; Set Sustain/Release.
; ======================================
        lda chn_effectpar,x
        sta chn_sr,x
        rts

; ======================================
effect09:
; ======================================
; Set waveform.
; ======================================
        lda chn_effectpar,x
        sta chn_waveform,x
        rts

; ======================================
effect0a:
; ======================================
; Arpeggio. (Protracker-like.)
; ======================================
        ldy mod3counter
        beq effect0aadd2                ; Counter at 0 -> use note 2.
        dey
        bne effect0aadd0                ; Counter at 2 -> use base note.
        lda chn_effectpar,x             ; Counter at 1 -> use note 1.
        lsr
        lsr
        lsr
        lsr
        clc
        adc chn_note,x
        bcc effect0adone
effect0aadd0:
        lda chn_note,x
        clc
        bcc effect0adone
effect0aadd2:
        lda chn_effectpar,x
        and #$0f
        clc
        adc chn_note,x
effect0adone:
        adc chn_transpose,x
        sta chn_finalnote,x
        rts

; ======================================
effect0b:
; ======================================
; Jump to order.
; ======================================
        lda chn_effectpar,x
        sta nextordernumber
        lda #$80
        sta forcenewpattern
        rts

; ======================================
effect0c:
; ======================================
; Set filter cutoff frequency.
; Parameter is 8 MSBs of frequency.
; ======================================
        lda chn_effectpar,x
        sta filter_cutoff
        rts

; ======================================
effect0d:
; ======================================
; Pattern break.
; ======================================
        lda chn_effectpar,x
        sta firsttrackrow
        lda #$80
        sta forcenewpattern
        rts

; ======================================
effect0e:
; ======================================
; Filter resonance/input control.
; High nybble is resonance, bit 0,1,2 enable filter for voice 1,2,3.
; ======================================
        lda chn_effectpar,x
        sta filter_input
        rts

; ======================================
effect0f:
; ======================================
; Parameter: $00-$7f: set speed
; Parameter: $80-$8f: set global volume
; Parameter: $90-$9f: set filter mode.
;   bit 0: low pass, bit 2: band pass, bit 3: high pass,
;   bit 3: cut off voice 3's output.
; Parameter: $a0-$af: fine slide down.
; Parameter: $b0-$bf: fine slide up.
; Parameter: $c0-$cf: note cut.
; Parameter: $d0-$df: note delay.                               !!!! TODO
; Parameter: $e0-$ef: select filter controller
; Parameter: $f0-$ff: set hard restart ticks.
; ======================================
        lda chn_effectpar,x
        bpl effect0fspeed
        and #$f0
        tay
        lda chn_effectpar,x
        and #$0f
; Now A is parameter bits 0..3, Y is bits 4..7
        cpy #$80
        beq effect0f80
        cpy #$90
        beq effect0f90
        cpy #$a0
        beq effect0fa0
        cpy #$b0
        beq effect0fb0
        cpy #$c0
        beq effect0fc0
        cpy #$e0
        beq effect0fe0
        cpy #$f0
        beq effect0ff0
; This is note delay (fdx), which is handled by the note delay counter. !!! TODO.
        rts
; Set speed.
effect0fspeed:
        sta speed
        rts
; Set global volume.
effect0f80:
        sta globalvolume
        rts
; Set filter mode.
effect0f90:
        asl
        asl
        asl
        asl
        sta filter_mode
        rts
; Fine slide down.
effect0fa0:
        ldy speedcounter
        bne effect0fb0done
; Multiply parameter by 4 to get slide adder.
        asl
        asl
        sta player_vibratotemp
; Subtract from slidefreq.
        lda chn_slidefreqlo,x
        sec
        sbc player_vibratotemp
        sta chn_slidefreqlo,x
        lda chn_slidefreqhi,x
        sbc #0
        sta chn_slidefreqhi,x
        rts
; Fine slide up.
effect0fb0:
        ldy speedcounter
        bne effect0fb0done
; Multiply parameter by 4 to get slide adder.
        asl
        asl
; Add to slidefreq.
        adc chn_slidefreqlo,x
        sta chn_slidefreqlo,x
        lda chn_slidefreqhi,x
        adc #0
        sta chn_slidefreqhi,x
effect0fb0done:
        rts
; Note cut.
effect0fc0:
        cmp speedcounter
        bne effect0fc0done
        lda #$fe                        ; Release gate.
        sta chn_gateon,x
effect0fc0done:
        rts
; Select filter cutoff controller.
effect0fe0:
        ldy speedcounter
        bne effect0fe0done
        tay
        beq effect0fe0nofilter
        lda INSTRUMENTS_FILTERTABLESTART,y  ; Filter table start index.
        sta filter_idx
        lda INSTRUMENTS_FILTERTABLEEND,y ; Copy filter table end.
        sta filter_end
        lda INSTRUMENTS_FILTERTABLELOOP,y ; Copy filter table loop.
        sta filter_loop
effect0fe0done:
        rts
effect0fe0nofilter:
        sta filter_idx
        sta filter_end
        sta filter_loop
        rts
; Set hardrestart.
effect0ff0:
        sta chn_hardrestart,x
        rts

; ======================================
start_newpattern:
; Get order index -> pattern number -> tracks for channels 1,2,3.
; ======================================
;  Input: ordernumber
; Output: trackrow: = previous firsttrackrow
;         firsttrackrow: always 0
;         forcenewpattern: always 0
; ======================================
; about 93+3*71 clock cycles
        ldy ordernumber                 ; Get index in order table.
        lda player_singlepattern
        bne snp_orderready
        ldy nextordernumber             ; Get index in order table.
        sty ordernumber
        inc nextordernumber
snp_orderready:
; player_patternptr=PATTERNS+6*ORDERLIST[ordernumber]
        ldx #0
        lda ORDERLIST,y            ; Get current pattern.
        asl
        bcc snp_noof1
        inx
        clc
snp_noof1:
        adc ORDERLIST,y
        bcc snp_noof2
        inx
snp_noof2:
        stx player_patternptr+1
        asl
        rol player_patternptr+1
        adc #<PATTERNS
        sta player_patternptr
        lda player_patternptr+1
        adc #>PATTERNS
        sta player_patternptr+1
; Init row positions.
        lda firsttrackrow               ; Usually 0 or set by pattern break.
        sta trackrow
        lda #$00                        ; Default pattern start is row 0.
        sta firsttrackrow
        sta forcenewpattern             ; Do not force new pattern.
; Fetch transpose values and create track pointers for each channel.
        tax
        tay
        jsr start_newtrack              ; Get track for channel 1
        jsr start_newtrack              ; Get track for channel 2
                                        ; Get track for channel 3

; ======================================
start_newtrack:
; Read track number and calculate 192*track_number+tracks.
; Also read track transpose.
; ======================================
;  Input: player_patternptr, player_patternptr+1: pointer to pattern
;         X: channel number
;         Y: 2*channel number
; Output: chn_trackptrlo, chn_trackptrhi, chn_transpose
; ======================================
; about 71 clock cycles
        lda (player_patternptr),y              ; Get track number.
        asl
        adc (player_patternptr),y
        sta player_trackptr+1
        lda #$00
        ror player_trackptr+1
        ror
        lsr player_trackptr+1
        ror
        adc #<TRACKS_BASE
        sta chn_trackptrlo,x
        lda player_trackptr+1
        adc #>TRACKS_BASE
        sta chn_trackptrhi,x
        iny
        lda (player_patternptr),y              ; Get transpose.
        sta chn_transpose,x
        inx
        iny
        rts

; ======================================
look_newpattern:
; Get tracks for next pattern, but don's set track transpose.
; ======================================
;  Input: ordernumber
; ======================================
        ldy nextordernumber             ; Get index in order table.
; player_patternptr=PATTERNS+6*ORDERLIST[nextordernumber]
        ldx #0
        lda ORDERLIST,y            ; Get next pattern.
        asl
        bcc lnp_noof1
        inx
        clc
lnp_noof1:
        adc ORDERLIST,y
        bcc lnp_noof2
        inx
lnp_noof2:
        stx player_patternptr+1
        asl
        rol player_patternptr+1
        adc #<PATTERNS
        sta player_patternptr
        lda player_patternptr+1
        adc #>PATTERNS
        sta player_patternptr+1
; Create track pointers for each channel.
        ldx #0
        ldy #0
        jsr look_newtrack               ; Get track for channel 1
        jsr look_newtrack               ; Get track for channel 2
                                        ; Get track for channel 3

; ======================================
look_newtrack:
; Read track number and calculate 192*track_number+tracks.
; ======================================
;  Input: player_patternptr, player_patternptr+1: pointer to pattern
;         X: channel number
;         Y: 2*channel number
; Output: chn_trackptrlo, chn_trackptrhi
; ======================================
        lda (player_patternptr),y              ; Get track number.
        asl
        adc (player_patternptr),y
        sta player_trackptr+1
        lda #$00
        ror player_trackptr+1
        ror
        lsr player_trackptr+1
        ror
        adc #<TRACKS_BASE
        sta chn_trackptrlo,x
        lda player_trackptr+1
        adc #>TRACKS_BASE
        sta chn_trackptrhi,x
        inx
        iny
        iny
        rts

; ======================================
fetchrow:
; Read next row of a track.
; ======================================
;  Input: Y:A: track pointer
;         X: channel number
;         trackrow3
; Output: chn_note,x
;         chn_inst,x
;         chn_effect,x
;         chn_effectpar,x
; ======================================
        sta player_trackptr
        sty player_trackptr+1
; Read note and high bit of effect.
        ldy trackrow3
        lda (player_trackptr),y
        cmp #$80                        ; Move bit 7 into C, will be rotated into effect number.
        and #$7f
        sta fr_nextnote+1
; Read 3 low bits of effect and instrument number.
        iny
        lda (player_trackptr),y
        ror
        lsr
        lsr
        lsr
        lsr
        sta chn_effect,x
; Read parameter.
        iny
        lda (player_trackptr),y
        sta chn_effectpar,x
; Read instrument.
        dey
        lda (player_trackptr),y
        and #$1f
; Start new instrument if necessary.
        beq fr_nonewinst
        sta chn_inst,x
        tay
; Copy changeable instrument parameters to channel.
        lda INSTRUMENTS_VIBDELAY,y      ; Copy vibrato delay.
        sta chn_vibdelay,x
; Set pulse width.
        lda INSTRUMENTS_PULSEWIDTH,y
        asl
        asl
        asl
        asl
        sta chn_plswidthlo,x
        lda INSTRUMENTS_PULSEWIDTH,y
        lsr
        lsr
        lsr
        lsr
        sta chn_plswidthhi,x
; Set pulse speed.
        lda INSTRUMENTS_PULSESPEED,y
        sta chn_plsspeed,x
; Set pulse limits.
        lda INSTRUMENTS_PULSELIMITS,y
        lsr
        lsr
        lsr
        lsr
        sta chn_plslimitdown,x
        lda INSTRUMENTS_PULSELIMITS,y
        and #$0f
        sta chn_plslimitup,x
; Reset vibrato and pulse width modulation.
        lda #$00
        sta chn_plsdir,x
        sta chn_vibpos,x
fr_nonewinst:
; Start new note if necessary.
fr_nextnote:
        lda #$00                        ; Self modifying code.
        beq fr_nonewnote
        cmp #97
        beq fr_noteoff
; Normal note between C-0 and B-7.
        sta chn_note,x
; If slide to note is active, set chn_notefreq?? only.
        ldy chn_effect,x
        cpy #3
        bne fr_noslidetonote
        clc
        adc chn_transpose,x
        tay
        lda freqtablelo,y
        sta chn_notefreqlo,x
        lda freqtablehi,y
        sta chn_notefreqhi,x
; Restart wave and arpeggio table and vibrato if there is a new note.
fr_noslidetonote:
        ldy chn_inst,x
        lda INSTRUMENTS_AD,y            ; Copy AD.
        sta chn_ad,x
        lda INSTRUMENTS_SR,y            ; Copy SR.
        sta chn_sr,x
        lda INSTRUMENTS_WAVETABLESTART,y ; Wave table start index.
        sta chn_waveidx,x
        lda INSTRUMENTS_ARPTABLESTART,y ; Arpeggio table start index.
        sta chn_arpidx,x
; Reset slide.
        lda #$00
        sta chn_slidefreqlo,x
        sta chn_slidefreqhi,x
; Set gate on.
        lda #$ff
        sta chn_gateon,x
fr_nonewnote:
        rts
; Set gate off.
fr_noteoff:
        lda #$fe
        sta chn_gateon,x
        rts

; ======================================
freqcmp:
; See if chn_freq??<chn_notefreq?? for channel X. Used in slide to note.
; ======================================
;  Input: X: channel number
;         chn_freqlo, chn_freqhi: current frequency
;         chn_notefreqlo, chn_notefreqhi: destination frequency
; Output: FLAGS: C=!(chn_freq??<chn_notefreq??)
; ======================================
        lda chn_freqhi,x
        cmp chn_notefreqhi,x
        bne freqcmp_done
        lda chn_freqlo,x
        cmp chn_notefreqlo,x
freqcmp_done:
        rts

; Pointers to effect procedures.
effectpointershi:       .byte >effect00, >effect01, >effect02, >effect03
                        .byte >effect04, >effect05, >effect06, >effect07
                        .byte >effect08, >effect09, >effect0a, >effect0b
                        .byte >effect0c, >effect0d, >effect0e, >effect0f
effectpointerslo:       .byte <effect00, <effect01, <effect02, <effect03
                        .byte <effect04, <effect05, <effect06, <effect07
                        .byte <effect08, <effect09, <effect0a, <effect0b
                        .byte <effect0c, <effect0d, <effect0e, <effect0f

; Index of SID registers for each channel.
sidregindex:    .byte 0, 7, 14

; Frequencies for all notes.
        include freqtab/freqtab.s

; 1 table for each possible vibrato depth.
; Each table contains 1/4th of a 64 byte sine wave.
; Total 256 bytes.
vibrato_table:
        include vibrato/vibrato.s

; Variables describing the current position in the song.
; These are not zeroed when playing starts.
globalvolume:   .byte 0         ; Global volume that goes to SID.
speed:          .byte 0         ; Speed as set by command F, default: 6
speedcounter:   .byte 0         ; Speed counter counts from 0 to speed-1
trackrow:       .byte 0         ; Index of current trackrow.
firsttrackrow:  .byte 0         ; First pattern row, usually 0 or set by pattern break.
ordernumber:    .byte 0         ; Index into orderlist.
nextordernumber:.byte 0         ; Next index into orderlist, set by order jump.
forcenewpattern:.byte 0         ; Flag set by order jump and pattern break.
player_singlepattern: byte 0    ; If nonzero, play current pattern only.

; Channel data.
chn_muted:      .byte 0,0,0     ; Nonzero means channel is muted.
chn_hardrestart: .byte 0,0,0    ; Number of ticks to shut channel up before new note.
playercleardata:                ; Variables from here are cleared when playing starts.
chn_gateon:     .byte 0,0,0     ; Bit 0 is SID gate bit, bit 7-1 always set.
chn_plsdir:     .byte 0,0,0     ; Nonzero means decrement pulse width.
chn_transpose:  .byte 0,0,0     ; Track transpose read from pattern.
chn_track:      .byte 0,0,0     ; Track index. Unused outside editor.
chn_trackptrlo: .byte 0,0,0     ; Track pointer low byte.
chn_trackptrhi: .byte 0,0,0     ; Track pointer high byte.
chn_note:       .byte 0,0,0     ; Note read from track or old note if track note is 0. C-0 is 1, B-7 is 96.
chn_inst:       .byte 0,0,0     ; Instrument read from track.
chn_effect:     .byte 0,0,0     ; Effect read from track.
chn_effectpar:  .byte 0,0,0     ; Effect parameter read from track.
chn_finalnote:  .byte 0,0,0     ; Note + arpeggio and track transpose.
chn_waveform:   .byte 0,0,0     ; Waveform from wavetable or set waveform effect.
chn_ad:         .byte 0,0,0     ; CFI, modified by set AD effect. (CFI=Copy From Instrument)
chn_sr:         .byte 0,0,0     ; CFI, modified by set SR effect.
chn_plswidthlo: .byte 0,0,0     ; CFI, modified by set pulse width effect and pulse width modulation.
chn_plswidthhi: .byte 0,0,0     ; CFI, modified by set pulse width effect and pulse width modulation.
chn_plsspeed:   .byte 0,0,0     ; CFI, modified by set pulse speed effect.
chn_plslimitdown:.byte 0,0,0    ; CFI, modified by set pulse limits effect.
chn_plslimitup: .byte 0,0,0     ; CFI, modified by set pulse limits effect.
chn_vibdelay:   .byte 0,0,0     ; CFI, count down to 0 then start instrument vibrato.
chn_vibdepth:   .byte 0,0,0     ; CFI, modified by vibrato effect.
chn_vibspeed:   .byte 0,0,0     ; CFI, modified by vibrato effect.
chn_waveidx:    .byte 0,0,0     ; CFI, wave table index, updated every tick.
chn_arpidx:     .byte 0,0,0     ; CFI, arpeggio table index, updated every tick.
chn_notefreqlo: .byte 0,0,0     ; Frequency for note read from pattern.
chn_notefreqhi: .byte 0,0,0     ;
chn_freqlo:     .byte 0,0,0     ; Frequency after (arpeggio) and slide.
chn_freqhi:     .byte 0,0,0     ;   arpeggio is not added when slide to note.
chn_finfreqlo:  .byte 0,0,0     ; Final frequency after (arpeggio) and slide
chn_finfreqhi:  .byte 0,0,0     ;   and vibrato.
chn_vibpos:     .byte 0,0,0     ; Vibrato counter.
chn_slidefreqlo:.byte 0,0,0     ; New note resets this to 0,
chn_slidefreqhi:.byte 0,0,0     ;   slide effect adds/subs chn_slidefreq??.

; Global parameters that are 0 after init.
mod3counter:    .byte 0         ; Mod 3 counter used by arpeggio effect

; Global filter parameters.
filter_idx:     .byte 0         ; Filter table index.
filter_end:     .byte 0         ; Filter table end index.
filter_loop:    .byte 0         ; Filter table loop index.
filter_cutoff:  .byte 0         ; Filter cutoff frequency 8 MSBs.
filter_input:   .byte 0         ; Filter input and resonance.
filter_mode:    .byte 0         ; Filter mode as in $D418.

PLAYERCLEARDATASIZE = *-playercleardata

; Temp variables.
trackrow3:      .byte 0         ; ==3*trackrow
nexttrackrow:   .byte 0         ; Used when checking if hardrestart has to be done.

; Damn keyjazz hack.
player_keyjazznote:             .byte 0
player_keyjazzinst:             .byte 0
player_previouskeyjazznote:     .byte 0

editor_playerend:
