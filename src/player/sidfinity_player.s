; =============================================================================
; SIDfinity 6502 Player
; =============================================================================
; Assembler  xa65         Build  xa -o out.bin sidfinity_player.s
; Behaviour  GT2 V2.68 Group B, buffered writes
;   All SID register writes deferred to ce_ldregs -- pulse SR AD freq wave.
;   Matches GT2 BUFFEREDWRITES=1 write order to avoid pulse-ahead timing.
; =============================================================================

; ---- assemble-standalone defaults (packer overrides with -D) -----------------
#ifndef base
base             = $1000
#endif
#ifndef SIDBASE
SIDBASE          = $d400
#endif
#ifndef FIRSTNOTE
FIRSTNOTE        = 0
#endif
#ifndef DEFAULTTEMPO
DEFAULTTEMPO     = 6
#endif
#ifndef ADPARAM
ADPARAM          = 0
#endif
#ifndef SRPARAM
SRPARAM          = 0
#endif
#ifndef FIRSTNOHRINSTR
FIRSTNOHRINSTR   = $3f
#endif
#ifndef FIRSTLEGATOINSTR
FIRSTLEGATOINSTR = $3f
#endif

; ---- dummy data labels so standalone assembly resolves all references ---------
#ifndef mt_songtbllo
mt_songtbllo     = mt_dummy
mt_songtblhi     = mt_dummy
mt_patttbllo     = mt_dummy
mt_patttblhi     = mt_dummy
mt_insad         = mt_dummy
mt_inssr         = mt_dummy
mt_inswaveptr    = mt_dummy
mt_inspulseptr   = mt_dummy
mt_insfiltptr    = mt_dummy
mt_insvibparam   = mt_dummy
mt_insvibdelay   = mt_dummy
mt_insgatetimer  = mt_dummy
mt_insfirstwave  = mt_dummy
mt_wavetbl       = mt_dummy
mt_notetbl       = mt_dummy
mt_pulsetimetbl  = mt_dummy
mt_pulsespdtbl   = mt_dummy
mt_filttimetbl   = mt_dummy
mt_filtspdtbl    = mt_dummy
mt_speedlefttbl  = mt_dummy
mt_speedrighttbl = mt_dummy
mt_freqtbllo     = mt_dummy
mt_freqtblhi     = mt_dummy
#endif

; ---- zero page ---------------------------------------------------------------
mt_temp1         = $fc
mt_temp2         = $fd

; ---- constants ---------------------------------------------------------------
ENDPATT  = $00
FX       = $40
FXONLY   = $50
NOTE     = $60
REST     = $bd
KEYOFF   = $be
KEYON    = $bf
FPKREST  = $c0

REPEAT   = $d0
TRANSDN  = $e0
TRANS    = $f0
LOOPSONG = $ff
LOOPTBL  = $ff

; #############################################################################
                * = base
; #############################################################################

; ---- jump table  base+0=init  base+3=play ------------------------------------
                jmp mt_init
                jmp mt_play

; =============================================================================
; mt_init   A = subtune (0-based)
; =============================================================================
mt_init
                sta mt_temp1
                asl
                clc
                adc mt_temp1
                sta mt_songidx
                lda #0
                sta mt_initpend
                rts

mt_songidx      .byte 0
mt_initpend     .byte $80

; =============================================================================
; mt_play   call once per frame
; =============================================================================
mt_play
                bit mt_initpend
                bmi mp_run
                jmp mt_fullinit
mp_run
                jsr mt_filterexec
                ldx #0
                jsr mt_execchn
                ldx #7
                jsr mt_execchn
                ldx #14
                jmp mt_execchn

; =============================================================================
; Full init
; =============================================================================
mt_fullinit
                ldy mt_songidx

                lda #0
                ldx #41
fi_c1           sta mt_chnsongptr,x
                dex
                bpl fi_c1
                ldx #41
fi_c2           sta mt_chnvibtime,x
                dex
                bpl fi_c2
                ldx #$18
fi_sid          sta SIDBASE,x
                dex
                bpl fi_sid

                sta mt_g_fstep+1
                sta mt_g_ftime+1
                sta mt_g_fcut+1
                sta mt_g_fctrl+1
                sta mt_g_ftype+1

                lda #$0f
                sta mt_g_mvol+1
                sta SIDBASE+$18     ; set volume immediately (match GT2 init)
                lda #8
                sta mt_funktbl
                lda #5
                sta mt_funktbl+1
                lda #$80
                sta mt_initpend

                ; per-channel init  Y = song*3
                ldx #14
                sty mt_temp1
                tya
                clc
                adc #2
                tay
                jsr fi_ch
                ldx #7
                dey
                jsr fi_ch
                ldx #0
                dey

fi_ch           tya
                sta mt_chnsongnum,x
                lda #DEFAULTTEMPO
                sta mt_chntempo,x
                lda #1
                sta mt_chncounter,x
                sta mt_chninstr,x
                lda #$fe
                sta mt_chngate,x
                lda #0
                sta mt_chnad,x
                sta mt_chnsr,x
                rts

; =============================================================================
; Filter table exec (global, once per frame)
; =============================================================================
mt_filterexec
mt_g_fstep      ldy #0
                beq fe_out
mt_g_ftime      lda #0
                bne fe_mod

                lda mt_filttimetbl-1,y
                beq fe_cut
                cmp #$80
                bcs fe_par
                sta mt_g_ftime+1
                jmp fe_mod

fe_par          asl
                sta mt_g_ftype+1
                lda mt_filtspdtbl-1,y
                sta mt_g_fctrl+1
                lda mt_filttimetbl,y
                bne fe_adv2
                iny
fe_cut          lda mt_filtspdtbl-1,y
                sta mt_g_fcut+1
                jmp fe_adv

fe_mod          clc
                lda mt_g_fcut+1
                adc mt_filtspdtbl-1,y
                sta mt_g_fcut+1
                dec mt_g_ftime+1
                bne fe_out

fe_adv          lda mt_filttimetbl,y
fe_adv2         cmp #LOOPTBL
                bne fe_nj
                lda mt_filtspdtbl,y
                sta mt_g_fstep+1
                jmp fe_out
fe_nj           iny
                sty mt_g_fstep+1

fe_out
mt_g_fcut       lda #0
                sta SIDBASE+$16
mt_g_fctrl      lda #0
                sta SIDBASE+$17
mt_g_ftype      lda #0
mt_g_mvol       ora #$0f
                sta SIDBASE+$18
                rts

; =============================================================================
; Channel execution   X = 0, 7, or 14
; =============================================================================
mt_execchn
                dec mt_chncounter,x
                bne ce_not0
                jmp ce_t0
ce_not0         bpl ce_wave

                ; counter underflow - reload tempo
                lda mt_chntempo,x
                cmp #2
                bcs ce_str
                ; funktempo
                tay
                eor #1
                sta mt_chntempo,x
                lda mt_funktbl,y
                sec
                sbc #1
ce_str          sta mt_chncounter,x

; =============================================================================
; Wave table execution  (runs every frame)
; =============================================================================
ce_wave
                ldy mt_chnwaveptr,x
                bne ce_wgo
                jmp ce_wdone
ce_wgo

                sty mt_wv_optr

                lda mt_wavetbl-1,y

                ; delay $00-$0F
                cmp #$10
                bcs ce_wndly
                cmp mt_chnwavetime,x
                beq ce_wdlyok
                inc mt_chnwavetime,x
                jmp ce_wdone
ce_wdlyok
                lda #0
                sta mt_wv_left
                jmp ce_wadv

ce_wndly
                sbc #$10
                sta mt_wv_left
                cmp #$e0
                bcs ce_wadv
                sta mt_chnwave,x

ce_wadv
                lda #0
                sta mt_chnwavetime,x
                lda mt_wavetbl,y
                cmp #LOOPTBL
                bne ce_wnj
                lda mt_notetbl,y
                sta mt_chnwaveptr,x
                jmp ce_wpost
ce_wnj          iny
                tya
                sta mt_chnwaveptr,x

ce_wpost
                lda mt_wv_left
                cmp #$e0
                bcs ce_wcmd

                ; right column - note/freq
                ldy mt_wv_optr
                lda mt_notetbl-1,y
                beq ce_wdone

                bpl ce_wabs
                ; relative
                clc
                adc mt_chnnote,x
                and #$7f
                jmp ce_wfreq
ce_wabs         sta mt_chnlastnote,x
ce_wfreq
                sec
                sbc #FIRSTNOTE
                tay
                lda mt_freqtbllo,y
                sta mt_chnfreqlo,x
                lda mt_freqtblhi,y
                sta mt_chnfreqhi,x
                lda #0
                sta mt_chnvibtime,x
                jmp ce_pulse

                ; wave command dispatch
ce_wcmd
                ldy mt_wv_optr
                lda mt_notetbl-1,y
                sta mt_wv_param

                lda mt_wv_left
                and #$0f
                cmp #5
                bcs ce_wct0

                ; commands 0-4 - continuous effects
                sta mt_chnfx,x
                lda mt_wv_param
                sta mt_chnparam,x
                jmp ce_runfx

ce_wct0
                ; commands 5-F - tick0 effects
                tay
                lda mt_t0tbl_lo,y
                sta ce_wcjsr+1
                lda mt_t0tbl_hi,y
                sta ce_wcjsr+2
                lda mt_wv_param
ce_wcjsr        jsr mt_t0_nop
                jmp ce_pulse

; wave done - no freq change, run continuous effects
ce_wdone
                lda mt_chncounter,x
                bne ce_wdgo
                jmp ce_pulse
ce_wdgo

ce_runfx        ldy mt_chnparam,x
                bne ce_rfgo
                jmp ce_pulse
ce_rfgo

                ; load speed table entry
                lda mt_speedlefttbl-1,y
                bmi ce_calcspd

                ; normal speed
                sta mt_temp2
                lda mt_speedrighttbl-1,y
                sta mt_temp1
                jmp ce_fxdisp

ce_calcspd
                and #$7f
                sta mt_fx_spd

                lda mt_speedrighttbl-1,y
                sta mt_fx_shift

                ldy mt_chnlastnote,x
                sec
                lda mt_freqtbllo+1-FIRSTNOTE,y
                sbc mt_freqtbllo-FIRSTNOTE,y
                sta mt_temp1
                lda mt_freqtblhi+1-FIRSTNOTE,y
                sbc mt_freqtblhi-FIRSTNOTE,y
                sta mt_temp2

                ldy mt_fx_shift
                beq ce_fxdisp
ce_shft         lsr mt_temp2
                ror mt_temp1
                dey
                bne ce_shft

ce_fxdisp       lda mt_chnfx,x
                beq ce_fx0
                cmp #1
                bne ce_fxd2
                jmp ce_fxadd
ce_fxd2         cmp #2
                bne ce_fxd3
                jmp ce_fxsub
ce_fxd3         cmp #3
                beq ce_fx3j
                jmp ce_fx4

ce_fx3j         jmp ce_fx3

; ---- effect 0 - instrument vibrato with delay ----
ce_fx0          lda mt_chnvibdelay,x
                beq ce_fx4
                dec mt_chnvibdelay,x
                jmp ce_pulse

; ---- effect 4 - vibrato ----
ce_fx4
                ; reload speed params specifically for vibrato
                ldy mt_chnparam,x
                lda mt_speedlefttbl-1,y
                bmi ce_v4c

                ; normal vibrato
                and #$7f
                sta mt_fx_spd
                lda mt_speedrighttbl-1,y
                sta mt_temp1
                lda #0
                sta mt_temp2
                jmp ce_v4r

ce_v4c
                ; calculated vibrato
                and #$7f
                sta mt_fx_spd
                lda mt_speedrighttbl-1,y
                pha
                ldy mt_chnlastnote,x
                sec
                lda mt_freqtbllo+1-FIRSTNOTE,y
                sbc mt_freqtbllo-FIRSTNOTE,y
                sta mt_temp1
                lda mt_freqtblhi+1-FIRSTNOTE,y
                sbc mt_freqtblhi-FIRSTNOTE,y
                sta mt_temp2
                pla
                tay
                beq ce_v4r
ce_v4s          lsr mt_temp2
                ror mt_temp1
                dey
                bne ce_v4s

ce_v4r
                ; phase logic
                lda mt_chnvibtime,x
                bmi ce_v4nc

                cmp mt_fx_spd
                beq ce_v4nc
                bcc ce_v4n2
                ; flip direction
                eor #$ff
                adc #2
                jmp ce_v4st

ce_v4nc         clc
ce_v4n2         adc #2
ce_v4st         sta mt_chnvibtime,x

                lsr
                bcs ce_fxsub

; ---- freq add ----
ce_fxadd        clc
                lda mt_chnfreqlo,x
                adc mt_temp1
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                adc mt_temp2
                sta mt_chnfreqhi,x
                jmp ce_pulse

; ---- freq sub ----
ce_fxsub        sec
                lda mt_chnfreqlo,x
                sbc mt_temp1
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                sbc mt_temp2
                sta mt_chnfreqhi,x
                jmp ce_pulse

; ---- effect 3 - tone portamento ----
ce_fx3
                lda mt_chnparam,x
                bne ce_fx3go
                jmp ce_tpsnap
ce_fx3go

                ; load speed
                ldy mt_chnparam,x
                lda mt_speedlefttbl-1,y
                bmi ce_tpcs

                sta mt_fx_shi
                lda mt_speedrighttbl-1,y
                sta mt_fx_slo
                jmp ce_tpgo

ce_tpcs
                and #$7f
                pha
                lda mt_speedrighttbl-1,y
                pha
                ldy mt_chnlastnote,x
                sec
                lda mt_freqtbllo+1-FIRSTNOTE,y
                sbc mt_freqtbllo-FIRSTNOTE,y
                sta mt_fx_slo
                lda mt_freqtblhi+1-FIRSTNOTE,y
                sbc mt_freqtblhi-FIRSTNOTE,y
                sta mt_fx_shi
                pla
                tay
                pla
                cpy #0
                beq ce_tpgo
ce_tpsh         lsr mt_fx_shi
                ror mt_fx_slo
                dey
                bne ce_tpsh

ce_tpgo
                ; offset = current - target
                lda mt_chnnote,x
                sec
                sbc #FIRSTNOTE
                tay

                sec
                lda mt_chnfreqlo,x
                sbc mt_freqtbllo,y
                sta mt_temp1
                lda mt_chnfreqhi,x
                sbc mt_freqtblhi,y
                sta mt_temp2

                bmi ce_tpup

                ; going down
                sec
                lda mt_temp1
                sbc mt_fx_slo
                lda mt_temp2
                sbc mt_fx_shi
                bmi ce_tpsnap

                sec
                lda mt_chnfreqlo,x
                sbc mt_fx_slo
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                sbc mt_fx_shi
                sta mt_chnfreqhi,x
                jmp ce_pulse

ce_tpup
                ; going up
                clc
                lda mt_temp1
                adc mt_fx_slo
                lda mt_temp2
                adc mt_fx_shi
                bpl ce_tpsnap

                clc
                lda mt_chnfreqlo,x
                adc mt_fx_slo
                sta mt_chnfreqlo,x
                lda mt_chnfreqhi,x
                adc mt_fx_shi
                sta mt_chnfreqhi,x
                jmp ce_pulse

ce_tpsnap
                lda mt_chnnote,x
                sta mt_chnlastnote,x
                sec
                sbc #FIRSTNOTE
                tay
                lda mt_freqtbllo,y
                sta mt_chnfreqlo,x
                lda mt_freqtblhi,y
                sta mt_chnfreqhi,x
                lda #0
                sta mt_chnvibtime,x
                jmp ce_pulse

; =============================================================================
; Pulse table execution
; =============================================================================
ce_pulse
                ldy mt_chnpulseptr,x
                beq ce_pskip

                ; gate timer check — skip pulse on gatetimer frame (GT2 behavior:
                ; with PULSEOPTIMIZATION, gate timer fires before pulse execution)
                lda mt_chncounter,x
                cmp mt_chngatetimer,x
                beq ce_pskip

                ; pulse optimization — skip when counter=0 AND pattptr=0
                ora mt_chnpattptr,x
                beq ce_pskip
ce_pgo
                lda mt_chnpulsetime,x
                bne ce_pmod

                ; new step
                lda mt_pulsetimetbl-1,y
                cmp #$80
                bcs ce_pset
                sta mt_chnpulsetime,x
                jmp ce_pmod

ce_pset         sta mt_chnpulsehi,x
                lda mt_pulsespdtbl-1,y
                sta mt_chnpulselo,x
                jmp ce_padv

ce_pmod         lda mt_pulsespdtbl-1,y
                clc
                bpl ce_pup
                dec mt_chnpulsehi,x
ce_pup          adc mt_chnpulselo,x
                sta mt_chnpulselo,x
                bcc ce_pnoc
                inc mt_chnpulsehi,x
ce_pnoc
                dec mt_chnpulsetime,x
                bne ce_pwr

ce_padv         lda mt_pulsetimetbl,y
                cmp #LOOPTBL
                bne ce_pnj
                lda mt_pulsespdtbl,y
                sta mt_chnpulseptr,x
                jmp ce_pwr
ce_pnj          iny
                tya
                sta mt_chnpulseptr,x

ce_pwr                                  ; pulse shadow updated above;
                                        ; actual SID write deferred to ce_ldregs
ce_pskip

; =============================================================================
; Gate timer check
; =============================================================================
                lda mt_chncounter,x
                cmp mt_chngatetimer,x
                beq ce_getnote
                jmp ce_ldregs

; =============================================================================
; Pattern reader
; =============================================================================
ce_getnote
                ldy mt_chnpattnum,x
                lda mt_patttbllo,y
                sta mt_temp1
                lda mt_patttblhi,y
                sta mt_temp2
                ldy mt_chnpattptr,x

                ; packed rest continuation
                lda mt_chnpkrest,x
                beq ce_nopkr
                jmp ce_pkrc
ce_nopkr

                lda (mt_temp1),y
                cmp #FPKREST
                bcs ce_pkrn
                cmp #NOTE
                bcs ce_note
                cmp #FX
                bcs ce_fx

                ; instrument change
                sta mt_chninstr,x
                iny
                lda (mt_temp1),y
                cmp #NOTE
                bcs ce_note

ce_fx           pha
                and #$0f
                sta mt_chnnewfx,x
                beq ce_fxnp
                iny
                lda (mt_temp1),y
                sta mt_chnnewparam,x
ce_fxnp         pla
                cmp #FXONLY
                bcs ce_rest
                iny
                lda (mt_temp1),y

ce_note         cmp #REST
                beq ce_rest
                cmp #KEYOFF
                beq ce_koff
                cmp #KEYON
                beq ce_kon

                ; normal note
                clc
                adc mt_chntrans,x
                sta mt_chnnewnote,x

                ; toneporta check
                lda mt_chnnewfx,x
                cmp #3
                beq ce_rest

                ; legato check
                lda mt_chninstr,x
                cmp #FIRSTLEGATOINSTR
                bcs ce_rest

                ; no-HR check
                cmp #FIRSTNOHRINSTR
                bcs ce_skhr

                ; hard restart (Group B) -- shadow only; SID write at ce_ldregs
                lda #SRPARAM
                sta mt_chnsr,x
                lda #ADPARAM
                sta mt_chnad,x

ce_skhr         lda #$fe
                sta mt_chngate,x
                jmp ce_rest

ce_koff         ora #$f0
                sta mt_chngate,x
                jmp ce_rest
ce_kon          ora #$f0
                sta mt_chngate,x
                jmp ce_rest

ce_pkrn
                adc #0
                beq ce_rest
                sta mt_chnpkrest,x
                jmp ce_ldregs

ce_pkrc
                clc
                adc #1
                sta mt_chnpkrest,x
                beq ce_rest
                jmp ce_ldregs

ce_rest         lda #0
                sta mt_chnpkrest,x
                iny
                lda (mt_temp1),y
                cmp #ENDPATT
                bne ce_noend
                lda #0
                sta mt_chnpattptr,x
                jmp ce_ldregs
ce_noend        tya
                sta mt_chnpattptr,x

; =============================================================================
; Register writes -- GT2 BUFFEREDWRITES order: pulse SR AD freq wave
; =============================================================================
ce_ldregs
                lda mt_chnpulselo,x
                sta SIDBASE+2,x
                lda mt_chnpulsehi,x
                sta SIDBASE+3,x
                lda mt_chnsr,x
                sta SIDBASE+6,x
                lda mt_chnad,x
                sta SIDBASE+5,x
                lda mt_chnfreqlo,x
                sta SIDBASE,x
                lda mt_chnfreqhi,x
                sta SIDBASE+1,x
ce_ldwav
                lda mt_chnwave,x
                and mt_chngate,x
                sta SIDBASE+4,x
                rts

; =============================================================================
; Tick 0 path
; =============================================================================
ce_t0
                ; setup tick-0 effect dispatch
                ldy mt_chnnewfx,x
                lda mt_t0tbl_lo,y
                sta ce_t0j1+1
                sta ce_t0j2+1
                lda mt_t0tbl_hi,y
                sta ce_t0j1+2
                sta ce_t0j2+2

                ; need new pattern?
                lda mt_chnpattptr,x
                bne ce_nonew

                ; read orderlist
                ldy mt_chnsongnum,x
                lda mt_songtbllo,y
                sta mt_temp1
                lda mt_songtblhi,y
                sta mt_temp2
                ldy mt_chnsongptr,x
                lda (mt_temp1),y

                cmp #LOOPSONG
                bne ce_nolp
                iny
                lda (mt_temp1),y
                tay
                lda (mt_temp1),y
ce_nolp
                cmp #TRANSDN
                bcc ce_notr
                sec
                sbc #TRANS
                sta mt_chntrans,x
                iny
                lda (mt_temp1),y
ce_notr
                cmp #REPEAT
                bcc ce_norep
                sec
                sbc #REPEAT
                sta mt_wv_optr      ; temp storage (not in use here)
                inc mt_chnrepeat,x
                lda mt_chnrepeat,x
                cmp mt_wv_optr
                bne ce_nonew
                lda #0
                sta mt_chnrepeat,x
                iny
                lda (mt_temp1),y
ce_norep
                sta mt_chnpattnum,x
                iny
                tya
                sta mt_chnsongptr,x

ce_nonew
                ; load gate timer
                ldy mt_chninstr,x
                lda mt_insgatetimer-1,y
                sta mt_chngatetimer,x

                ; new note?
                lda mt_chnnewnote,x
                bne ce_newn
                jmp ce_nnn
ce_newn

                ; ===== new note init =====
                sec
                sbc #NOTE
                sta mt_chnnote,x
                lda #0
                sta mt_chnfx,x
                sta mt_chnnewnote,x

                ldy mt_chninstr,x
                lda mt_insvibdelay-1,y
                sta mt_chnvibdelay,x
                lda mt_insvibparam-1,y
                sta mt_chnparam,x

                ; toneporta skip
                lda mt_chnnewfx,x
                cmp #3
                beq ce_nnn

                ; first-frame waveform
                ldy mt_chninstr,x
                lda mt_insfirstwave-1,y
                beq ce_skfw
                cmp #$fe
                bcs ce_skfw
                sta mt_chnwave,x
ce_skfw
                lda #$ff
                sta mt_chngate,x

                ; pulse ptr
                ldy mt_chninstr,x
                lda mt_inspulseptr-1,y
                beq ce_npi
                sta mt_chnpulseptr,x
                lda #0
                sta mt_chnpulsetime,x
ce_npi
                ; filter ptr
                ldy mt_chninstr,x
                lda mt_insfiltptr-1,y
                beq ce_nfi
                sta mt_g_fstep+1
                lda #0
                sta mt_g_ftime+1
ce_nfi
                ; wave ptr
                ldy mt_chninstr,x
                lda mt_inswaveptr-1,y
                sta mt_chnwaveptr,x
                lda #0
                sta mt_chnwavetime,x

                ; ADSR (Group B) -- shadow only; SID write deferred to ce_ldregs
                ldy mt_chninstr,x
                lda mt_inssr-1,y
                sta mt_chnsr,x
                lda mt_insad-1,y
                sta mt_chnad,x

                ; tick-0 effect
                lda mt_chnnewparam,x
ce_t0j1         jsr mt_t0_nop

                ; buffered writes -- write all regs at once
                jmp ce_ldregs

ce_nnn
                lda mt_chnnewparam,x
ce_t0j2         jsr mt_t0_nop
                jmp ce_wave

; =============================================================================
; Tick-0 effect handlers
; =============================================================================

mt_t0_nop
                ldy mt_chninstr,x
                lda mt_insvibparam-1,y
                jmp mt_t0_34

mt_t0_12
                pha
                lda #0
                sta mt_chnvibtime,x
                pla

mt_t0_34
                sta mt_chnparam,x
                lda mt_chnnewfx,x
                sta mt_chnfx,x
                rts

mt_t0_5         sta mt_chnad,x
                rts
mt_t0_6         sta mt_chnsr,x
                rts
mt_t0_7         sta mt_chnwave,x
                rts
mt_t0_8         sta mt_chnwaveptr,x
                pha
                lda #0
                sta mt_chnwavetime,x
                pla
                rts
mt_t0_9         sta mt_chnpulseptr,x
                pha
                lda #0
                sta mt_chnpulsetime,x
                pla
                rts
mt_t0_a         sta mt_g_fstep+1
                pha
                lda #0
                sta mt_g_ftime+1
                pla
                rts
mt_t0_b         sta mt_g_fctrl+1
                cmp #0
                bne mt_t0b2
                sta mt_g_fstep+1
mt_t0b2         rts
mt_t0_c         sta mt_g_fcut+1
                rts
mt_t0_d         sta mt_g_mvol+1
                rts
mt_t0_e         tay
                lda mt_speedlefttbl-1,y
                sta mt_funktbl
                lda mt_speedrighttbl-1,y
                sta mt_funktbl+1
                lda #0

mt_t0_f         cmp #$80
                bcs mt_t0fc
                sta mt_chntempo
                sta mt_chntempo+7
                sta mt_chntempo+14
                rts
mt_t0fc         and #$7f
                sta mt_chntempo,x
                rts

; =============================================================================
; Jump tables
; =============================================================================
mt_t0tbl_lo
                .byte <mt_t0_nop
                .byte <mt_t0_12
                .byte <mt_t0_12
                .byte <mt_t0_34
                .byte <mt_t0_34
                .byte <mt_t0_5
                .byte <mt_t0_6
                .byte <mt_t0_7
                .byte <mt_t0_8
                .byte <mt_t0_9
                .byte <mt_t0_a
                .byte <mt_t0_b
                .byte <mt_t0_c
                .byte <mt_t0_d
                .byte <mt_t0_e
                .byte <mt_t0_f

mt_t0tbl_hi
                .byte >mt_t0_nop
                .byte >mt_t0_12
                .byte >mt_t0_12
                .byte >mt_t0_34
                .byte >mt_t0_34
                .byte >mt_t0_5
                .byte >mt_t0_6
                .byte >mt_t0_7
                .byte >mt_t0_8
                .byte >mt_t0_9
                .byte >mt_t0_a
                .byte >mt_t0_b
                .byte >mt_t0_c
                .byte >mt_t0_d
                .byte >mt_t0_e
                .byte >mt_t0_f

; =============================================================================
; Scratch variables
; =============================================================================
mt_wv_optr      .byte 0
mt_wv_left      .byte 0
mt_wv_param     .byte 0
mt_fx_spd       .byte 0
mt_fx_shift     .byte 0
mt_fx_slo       .byte 0
mt_fx_shi       .byte 0

; =============================================================================
; Funktempo table
; =============================================================================
mt_funktbl      .byte 8, 5

; =============================================================================
; Channel variables -- 5 groups, stride 7, 3 channels
; =============================================================================
; Group 1 - sequencer  (21 bytes)
mt_chnsongptr   .dsb 21,0
mt_chntrans     = mt_chnsongptr+1
mt_chnrepeat    = mt_chnsongptr+2
mt_chnpattptr   = mt_chnsongptr+3
mt_chnpkrest    = mt_chnsongptr+4
mt_chnnewfx     = mt_chnsongptr+5
mt_chnnewparam  = mt_chnsongptr+6

; Group 2 - note/wave/pulse  (21 bytes)
mt_chnfx        .dsb 21,0
mt_chnparam     = mt_chnfx+1
mt_chnnewnote   = mt_chnfx+2
mt_chnwaveptr   = mt_chnfx+3
mt_chnwave      = mt_chnfx+4
mt_chnpulseptr  = mt_chnfx+5
mt_chnpulsetime = mt_chnfx+6

; Group 3 - song/tempo/note  (21 bytes)
mt_chnsongnum   .dsb 21,0
mt_chnpattnum   = mt_chnsongnum+1
mt_chntempo     = mt_chnsongnum+2
mt_chncounter   = mt_chnsongnum+3
mt_chnnote      = mt_chnsongnum+4
mt_chninstr     = mt_chnsongnum+5
mt_chngate      = mt_chnsongnum+6

; Group 4 - vibrato/freq/pulse shadows  (21 bytes)
mt_chnvibtime   .dsb 21,0
mt_chnvibdelay  = mt_chnvibtime+1
mt_chnwavetime  = mt_chnvibtime+2
mt_chnfreqlo    = mt_chnvibtime+3
mt_chnfreqhi    = mt_chnvibtime+4
mt_chnpulselo   = mt_chnvibtime+5
mt_chnpulsehi   = mt_chnvibtime+6

; Group 5 - ADSR/gate timer/lastnote  (21 bytes)
mt_chnad        .dsb 21,0
mt_chnsr        = mt_chnad+1
mt_chngatetimer = mt_chnad+2
mt_chnlastnote  = mt_chnad+3

; =============================================================================
; Dummy data byte (for standalone assembly)
; =============================================================================
mt_dummy        .byte 0
