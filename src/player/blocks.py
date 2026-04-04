"""
blocks.py — Block library for the SIDfinity per-song code generator.

Each block is a unit of xa65 assembly extracted from sidfinity_player.s.
The code is verbatim from the proven player — no rewriting needed.
The optimization comes from SELECTING which blocks to include.

Block naming convention:
  - Core blocks (always present): prefixed with nothing
  - Feature blocks: named after the feature they implement
  - Alternative blocks: suffixed with the mode (e.g., _buffered, _unbuffered)
"""

try:
    from .codegen import Block, FILTER, EFFECTS, VIBRATO, PORTAMENTO, TONEPORTA, \
        CALCULATED_SPEED, FUNKTEMPO, WAVE_DELAY, WAVE_CMD, PULSE_MOD, TICK0_FX, \
        ORDERLIST_TRANS, ORDERLIST_REPEAT, SET_AD, SET_SR, SET_WAVE, SET_WAVEPTR, \
        SET_PULSEPTR, SET_FILTPTR, SET_FILTCTRL, SET_FILTCUT, SET_MASTERVOL, \
        SET_TEMPO, BUFFERED_WRITES, UNBUFFERED_WRITES, ADSR_AD_FIRST, \
        LOADREGS_AD_FIRST, NEWNOTE_ALL_REGS, VIBRATO_PARAM_FIX, \
        NOHR_INSTR, LEGATO_INSTR
except ImportError:
    from codegen import Block, FILTER, EFFECTS, VIBRATO, PORTAMENTO, TONEPORTA, \
        CALCULATED_SPEED, FUNKTEMPO, WAVE_DELAY, WAVE_CMD, PULSE_MOD, TICK0_FX, \
        ORDERLIST_TRANS, ORDERLIST_REPEAT, SET_AD, SET_SR, SET_WAVE, SET_WAVEPTR, \
        SET_PULSEPTR, SET_FILTPTR, SET_FILTCTRL, SET_FILTCUT, SET_MASTERVOL, \
        SET_TEMPO, BUFFERED_WRITES, UNBUFFERED_WRITES, ADSR_AD_FIRST, \
        LOADREGS_AD_FIRST, NEWNOTE_ALL_REGS, VIBRATO_PARAM_FIX, \
        NOHR_INSTR, LEGATO_INSTR


# =============================================================================
# The preamble — defines, constants, ZP. Not a block (always emitted first).
# =============================================================================

PREAMBLE = """\
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
"""

# =============================================================================
# The dummy data labels — for standalone assembly only.
# The packer strips this block and provides real labels.
# =============================================================================

DUMMY_DATA = """\
#ifndef mt_songtbllo
mt_dummy        .byte 0
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
"""


def build_blocks(features):
    """Build the list of all blocks, parameterized by active features.

    This function returns ALL blocks. The caller uses select_blocks()
    to filter to only the ones needed for a specific song.

    Args:
        features: frozenset of active feature flags (used to emit
                  the correct variant for behavioral blocks)
    """
    blocks = []

    # =========================================================================
    # JUMP TABLE + INIT  (always present, order_group=10)
    # =========================================================================
    blocks.append(Block(
        name='jump_table',
        code="""\
; ---- jump table  base+0=init  base+3=play ------------------------------------
                jmp mt_init
                jmp mt_play""",
        provides={'mt_init_jmp', 'mt_play_jmp'},
        requires={'mt_init', 'mt_play'},
        byte_estimate=6,
        order_group=10,
        fall_through_to='init',
    ))

    blocks.append(Block(
        name='init',
        code="""\
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
mt_initpend     .byte $80""",
        provides={'mt_init', 'mt_songidx', 'mt_initpend'},
        byte_estimate=16,
        order_group=10,
        fall_through_to='play_dispatch',
    ))

    # =========================================================================
    # PLAY DISPATCH  (always present, order_group=11)
    # =========================================================================
    filter_call = '                jsr mt_filterexec' if FILTER in features else ''
    blocks.append(Block(
        name='play_dispatch',
        code=f"""\
; =============================================================================
; mt_play   call once per frame
; =============================================================================
mt_play
                bit mt_initpend
                bmi mp_run
                jmp mt_fullinit
mp_run
{filter_call}
                ldx #0
                jsr mt_execchn
                ldx #7
                jsr mt_execchn
                ldx #14
                jmp mt_execchn""",
        provides={'mt_play', 'mp_run'},
        requires={'mt_initpend', 'mt_fullinit', 'mt_execchn'} |
                 ({'mt_filterexec'} if FILTER in features else set()),
        byte_estimate=25,
        order_group=11,
    ))

    # =========================================================================
    # FULL INIT  (always present, order_group=12)
    # =========================================================================
    # Build the init code — varies based on features
    init_filter_clears = """\
                sta mt_g_fstep+1
                sta mt_g_ftime+1
                sta mt_g_fcut+1
                sta mt_g_fctrl+1
                sta mt_g_ftype+1""" if FILTER in features else """\
                sta mt_g_fstep+1"""

    init_ad_sr = """\
                lda #0
                sta mt_chnad,x
                sta mt_chnsr,x""" if BUFFERED_WRITES in features else ''

    blocks.append(Block(
        name='full_init',
        code=f"""\
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

{init_filter_clears}

                lda #$0f
                sta mt_g_mvol+1
                sta SIDBASE+$18
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
{init_ad_sr}
                rts""",
        provides={'mt_fullinit', 'fi_ch', 'fi_c1', 'fi_c2', 'fi_sid'},
        requires={'mt_songidx', 'mt_initpend', 'mt_chnsongptr', 'mt_chnvibtime',
                  'mt_g_mvol', 'mt_funktbl', 'mt_chnsongnum', 'mt_chntempo',
                  'mt_chncounter', 'mt_chninstr', 'mt_chngate'},
        byte_estimate=80,
        order_group=12,
    ))

    # =========================================================================
    # FILTER EXEC  (order_group=13)
    # =========================================================================
    if FILTER in features:
        blocks.append(Block(
            name='filter_exec',
            code="""\
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
                rts""",
            provides={'mt_filterexec', 'mt_g_fstep', 'mt_g_ftime', 'mt_g_fcut',
                      'mt_g_fctrl', 'mt_g_ftype', 'mt_g_mvol',
                      'fe_out', 'fe_mod', 'fe_par', 'fe_cut', 'fe_adv', 'fe_adv2', 'fe_nj'},
            needs={FILTER},
            byte_estimate=72,
            order_group=13,
        ))
    else:
        blocks.append(Block(
            name='filter_minimal',
            code="""\
; NOFILTER: minimal — just write volume
mt_filterexec
mt_g_mvol       lda #$0f
                sta SIDBASE+$18
mt_g_fstep = mt_g_mvol
mt_g_ftime = mt_g_mvol
mt_g_fcut  = mt_g_mvol
mt_g_fctrl = mt_g_mvol
mt_g_ftype = mt_g_mvol
                rts""",
            provides={'mt_filterexec', 'mt_g_fstep', 'mt_g_ftime', 'mt_g_fcut',
                      'mt_g_fctrl', 'mt_g_ftype', 'mt_g_mvol'},
            excludes={FILTER},
            byte_estimate=8,
            order_group=13,
        ))

    # =========================================================================
    # CHANNEL EXECUTION ENTRY  (always present, order_group=20)
    # =========================================================================
    # Funktempo logic only included if FUNKTEMPO is active
    if FUNKTEMPO in features:
        funktempo_code = """\
                ; funktempo
                tay
                eor #1
                sta mt_chntempo,x
                lda mt_funktbl,y
                sec
                sbc #1"""
    else:
        funktempo_code = ''

    # If no funktempo, we can simplify the counter reload
    if FUNKTEMPO in features:
        counter_reload = f"""\
                ; counter underflow - reload tempo
                lda mt_chntempo,x
                cmp #2
                bcs ce_str
{funktempo_code}
ce_str          sta mt_chncounter,x"""
    else:
        counter_reload = """\
                ; counter underflow - reload tempo
                lda mt_chntempo,x
                sta mt_chncounter,x"""

    blocks.append(Block(
        name='channel_entry',
        code=f"""\
; =============================================================================
; Channel execution   X = 0, 7, or 14
; =============================================================================
mt_execchn
                dec mt_chncounter,x
                bne ce_not0
                jmp ce_t0
ce_not0         bpl ce_wave

{counter_reload}""",
        provides={'mt_execchn', 'ce_not0', 'ce_str'},
        requires={'mt_chncounter', 'mt_chntempo', 'ce_t0', 'ce_wave'},
        byte_estimate=25,
        order_group=20,
        fall_through_to='wave_exec',
    ))

    # =========================================================================
    # WAVE TABLE EXECUTION  (always present, order_group=21)
    # =========================================================================
    # The wave delay handling is conditional
    if WAVE_DELAY in features:
        wave_delay_code = """\
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

ce_wndly"""
    else:
        wave_delay_code = """\
                ; no wave delay — all bytes are waveforms or commands
ce_wndly"""

    blocks.append(Block(
        name='wave_exec',
        code=f"""\
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

{wave_delay_code}
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
                jmp ce_pulse""",
        provides={'ce_wave', 'ce_wgo', 'ce_wndly', 'ce_wadv', 'ce_wnj',
                  'ce_wpost', 'ce_wabs', 'ce_wfreq', 'ce_wdlyok'},
        requires={'mt_chnwaveptr', 'mt_wavetbl', 'mt_notetbl', 'mt_chnwave',
                  'mt_chnwavetime', 'mt_wv_optr', 'mt_wv_left', 'mt_chnnote',
                  'mt_chnlastnote', 'mt_chnfreqlo', 'mt_chnfreqhi', 'mt_freqtbllo',
                  'mt_freqtblhi', 'mt_chnvibtime', 'ce_wdone', 'ce_pulse', 'ce_wcmd'},
        byte_estimate=95,
        order_group=21,
    ))

    # =========================================================================
    # WAVE COMMAND DISPATCH  (order_group=22)
    # =========================================================================
    if WAVE_CMD in features or TICK0_FX in features:
        if EFFECTS in features:
            wave_cmd_04 = """\
                ; commands 0-4 - continuous effects
                sta mt_chnfx,x
                lda mt_wv_param
                sta mt_chnparam,x
                jmp ce_runfx"""
        else:
            wave_cmd_04 = """\
                jmp ce_pulse"""

        if TICK0_FX in features:
            wave_cmd_5f = """\
ce_wct0
                ; commands 5-F - tick0 effects via wave table
                sta mt_chnnewfx,x
                lda mt_wv_param
                sta mt_chnnewparam,x
                jsr mt_t0_dispatch
                jmp ce_pulse"""
        else:
            wave_cmd_5f = """\
ce_wct0
                jmp ce_pulse"""

        blocks.append(Block(
            name='wave_cmd',
            code=f"""\
                ; wave command dispatch
ce_wcmd
                ldy mt_wv_optr
                lda mt_notetbl-1,y
                sta mt_wv_param

                lda mt_wv_left
                and #$0f
                cmp #5
                bcs ce_wct0

{wave_cmd_04}

{wave_cmd_5f}""",
            provides={'ce_wcmd', 'ce_wct0'},
            requires={'mt_wv_optr', 'mt_notetbl', 'mt_wv_param', 'mt_wv_left',
                      'ce_pulse'} |
                     ({'ce_runfx'} if EFFECTS in features else set()) |
                     ({'mt_t0_dispatch'} if TICK0_FX in features else set()),
            needs={WAVE_CMD} if WAVE_CMD in features else {TICK0_FX},
            byte_estimate=30,
            order_group=22,
        ))
    else:
        # No wave commands at all — wcmd just goes to pulse
        blocks.append(Block(
            name='wave_cmd_stub',
            code="""\
ce_wcmd
                jmp ce_pulse""",
            provides={'ce_wcmd'},
            requires={'ce_pulse'},
            byte_estimate=3,
            order_group=22,
        ))

    # =========================================================================
    # EFFECTS (ce_wdone through ce_fxsub)  (order_group=23)
    # =========================================================================
    if EFFECTS in features:
        # Build the effects block — this is the largest optional section
        calc_speed = """\
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
                bne ce_shft""" if CALCULATED_SPEED in features else """\
ce_calcspd
                and #$7f
                sta mt_temp2
                lda mt_speedrighttbl-1,y
                sta mt_temp1"""

        vib_delay = """\
; ---- effect 0 - instrument vibrato with delay ----
ce_fx0          lda mt_chnvibdelay,x
                beq ce_fx4
                dec mt_chnvibdelay,x
                jmp ce_pulse""" if VIBRATO in features else ''

        vibrato = """\
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
                bcs ce_fxsub""" if VIBRATO in features else ''

        # FX dispatch needs to reference the right labels
        fx_dispatch_entries = []
        if VIBRATO in features:
            fx_dispatch_entries.append('                beq ce_fx0')
        else:
            fx_dispatch_entries.append('                beq ce_fxnop')
        fx_dispatch_entries.append("""\
                cmp #1
                bne ce_fxd2
                jmp ce_fxadd
ce_fxd2         cmp #2
                bne ce_fxd3
                jmp ce_fxsub""")
        if TONEPORTA in features and VIBRATO in features:
            fx_dispatch_entries.append("""\
ce_fxd3         cmp #3
                beq ce_fx3j
                jmp ce_fx4
ce_fx3j         jmp ce_fx3""")
        elif TONEPORTA in features:
            fx_dispatch_entries.append("""\
ce_fxd3         cmp #3
                beq ce_fx3j
                jmp ce_pulse
ce_fx3j         jmp ce_fx3""")
        elif VIBRATO in features:
            fx_dispatch_entries.append("""\
ce_fxd3         jmp ce_fx4""")
        else:
            fx_dispatch_entries.append("""\
ce_fxd3         jmp ce_pulse""")

        fx_dispatch = '\n'.join(fx_dispatch_entries)

        if not (VIBRATO in features):
            vib_nop = """\
ce_fxnop        jmp ce_pulse"""
        else:
            vib_nop = ''

        toneporta = ""  # TODO: add full tone porta block if TONEPORTA in features

        if TONEPORTA in features:
            toneporta = """\
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
                jmp ce_pulse"""

        blocks.append(Block(
            name='effects',
            code=f"""\
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

{calc_speed}

ce_fxdisp       lda mt_chnfx,x
{fx_dispatch}

{vib_nop}
{vib_delay}
{vibrato}

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

{toneporta}""",
            provides={'ce_wdone', 'ce_wdgo', 'ce_runfx', 'ce_rfgo', 'ce_calcspd',
                      'ce_fxdisp', 'ce_fxadd', 'ce_fxsub', 'ce_shft'} |
                     ({'ce_fx0', 'ce_fx4', 'ce_v4c', 'ce_v4r', 'ce_v4nc', 'ce_v4n2',
                       'ce_v4st', 'ce_v4s'} if VIBRATO in features else {'ce_fxnop'}) |
                     ({'ce_fx3', 'ce_fx3j', 'ce_fx3go', 'ce_tpcs', 'ce_tpgo', 'ce_tpup',
                       'ce_tpsnap', 'ce_tpsh'} if TONEPORTA in features else set()) |
                     ({'ce_fxd2', 'ce_fxd3'}),
            requires={'ce_pulse', 'mt_speedlefttbl', 'mt_speedrighttbl', 'mt_chnparam',
                      'mt_chnfx', 'mt_chnfreqlo', 'mt_chnfreqhi', 'mt_chncounter'},
            needs={EFFECTS},
            byte_estimate=300,
            order_group=23,
        ))
    else:
        # No effects — ce_wdone just goes to pulse
        blocks.append(Block(
            name='effects_stub',
            code="""\
ce_wdone
                jmp ce_pulse""",
            provides={'ce_wdone'},
            requires={'ce_pulse'},
            excludes={EFFECTS},
            byte_estimate=3,
            order_group=23,
        ))

    # =========================================================================
    # PULSE TABLE  (order_group=30)
    # =========================================================================
    if PULSE_MOD in features:
        pulse_inline = """\
                ; BW=0: write pulse directly to SID
                lda mt_chnpulselo,x
                sta SIDBASE+2,x
                lda mt_chnpulsehi,x
                sta SIDBASE+3,x""" if UNBUFFERED_WRITES in features else ''

        blocks.append(Block(
            name='pulse_exec',
            code=f"""\
; =============================================================================
; Pulse table execution
; =============================================================================
ce_pulse
                ldy mt_chnpulseptr,x
                beq ce_pskip

                ; gate timer check
                lda mt_chncounter,x
                cmp mt_chngatetimer,x
                beq ce_pskip

                ; pulse optimization
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

ce_pwr
{pulse_inline}
ce_pskip
                jmp ce_pskip_gate""",
            provides={'ce_pulse', 'ce_pskip', 'ce_pgo', 'ce_pmod', 'ce_pset',
                      'ce_pup', 'ce_pnoc', 'ce_padv', 'ce_pnj', 'ce_pwr'},
            requires={'mt_chnpulseptr', 'mt_chncounter', 'mt_chngatetimer',
                      'mt_chnpattptr', 'mt_chnpulsetime', 'mt_pulsetimetbl',
                      'mt_pulsespdtbl', 'mt_chnpulsehi', 'mt_chnpulselo'},
            needs={PULSE_MOD},
            byte_estimate=75,
            order_group=30,
        ))
    else:
        blocks.append(Block(
            name='pulse_stub',
            code="""\
ce_pulse
ce_pskip
                jmp ce_pskip_gate""",
            provides={'ce_pulse', 'ce_pskip'},
            excludes={PULSE_MOD},
            byte_estimate=0,
            order_group=30,
        ))

    # =========================================================================
    # GATE TIMER CHECK + REGISTER WRITES  (order_group=31)
    # =========================================================================
    if BUFFERED_WRITES in features:
        if LOADREGS_AD_FIRST in features:
            ldregs_body = """\
                ; BW=1 Group A/C: AD SR pulse freq wave
                lda mt_chnad,x
                sta SIDBASE+5,x
                lda mt_chnsr,x
                sta SIDBASE+6,x
                lda mt_chnpulselo,x
                sta SIDBASE+2,x
                lda mt_chnpulsehi,x
                sta SIDBASE+3,x"""
        else:
            ldregs_body = """\
                ; BW=1 Group B/D: pulse SR AD freq wave
                lda mt_chnpulselo,x
                sta SIDBASE+2,x
                lda mt_chnpulsehi,x
                sta SIDBASE+3,x
                lda mt_chnsr,x
                sta SIDBASE+6,x
                lda mt_chnad,x
                sta SIDBASE+5,x"""
    else:
        ldregs_body = """\
                ; BW=0: freq + wave only"""

    # =========================================================================
    # GATE CHECK + PATTERN READER + REGISTER WRITES  (order_group=31)
    # These must be one block because ce_noend falls through to ce_ldregs
    # =========================================================================
    # Build hard restart code based on ADSR order and buffered/unbuffered
    if ADSR_AD_FIRST in features:
        hr_adsr = """\
                lda #ADPARAM
                sta mt_chnad,x
                lda #SRPARAM
                sta mt_chnsr,x"""
    else:
        hr_adsr = """\
                lda #SRPARAM
                sta mt_chnsr,x
                lda #ADPARAM
                sta mt_chnad,x"""

    hr_inline = """\
                ; BW=0: write ADSR directly to SID
                lda mt_chnsr,x
                sta SIDBASE+6,x
                lda mt_chnad,x
                sta SIDBASE+5,x""" if UNBUFFERED_WRITES in features else ''

    blocks.append(Block(
        name='gate_pattern_regs',
        code=f"""\
; =============================================================================
; Gate timer check
; =============================================================================
ce_pskip_gate
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

                ; hard restart
{hr_adsr}
{hr_inline}

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
                bne ce_noend
                sta mt_chnpattptr,x
                beq ce_ldregs
ce_noend        tya
                sta mt_chnpattptr,x

; =============================================================================
; Register writes
; =============================================================================
ce_ldregs
{ldregs_body}
                lda mt_chnfreqlo,x
                sta SIDBASE,x
                lda mt_chnfreqhi,x
                sta SIDBASE+1,x
ce_ldwav
                lda mt_chnwave,x
                and mt_chngate,x
                sta SIDBASE+4,x
                rts""",
        provides={'ce_getnote', 'ce_nopkr', 'ce_fx', 'ce_fxnp', 'ce_note',
                  'ce_koff', 'ce_kon', 'ce_skhr', 'ce_pkrn', 'ce_pkrc',
                  'ce_rest', 'ce_noend', 'ce_ldregs', 'ce_ldwav', 'ce_pskip_gate'},
        requires={'mt_patttbllo', 'mt_patttblhi', 'mt_chnpattnum', 'mt_chnpattptr',
                  'mt_chnpkrest', 'mt_chninstr', 'mt_chnnewfx', 'mt_chnnewparam',
                  'mt_chntrans', 'mt_chnnewnote', 'mt_chngate', 'mt_chnad', 'mt_chnsr',
                  'mt_chncounter', 'mt_chngatetimer', 'mt_chnfreqlo', 'mt_chnfreqhi',
                  'mt_chnwave'},
        byte_estimate=180,
        order_group=31,
    ))

    # =========================================================================
    # TICK-0 PATH  (order_group=40)
    # =========================================================================
    # Orderlist features
    if ORDERLIST_TRANS in features or ORDERLIST_REPEAT in features:
        ol_trans = """\
                cmp #TRANSDN
                bcc ce_notr
                sec
                sbc #TRANS
                sta mt_chntrans,x
                iny
                lda (mt_temp1),y
ce_notr""" if ORDERLIST_TRANS in features else ''

        ol_repeat = """\
                cmp #REPEAT
                bcc ce_norep
                sec
                sbc #REPEAT
                sta mt_wv_optr
                inc mt_chnrepeat,x
                lda mt_chnrepeat,x
                cmp mt_wv_optr
                bne ce_nonew
                lda #0
                sta mt_chnrepeat,x
                iny
                lda (mt_temp1),y
ce_norep""" if ORDERLIST_REPEAT in features else ''
        ol_features = f"{ol_trans}\n{ol_repeat}"
    else:
        ol_features = ''

    # New note init — ADSR writes vary by mode
    if UNBUFFERED_WRITES in features:
        newnote_adsr_inline = """\
                ; BW=0: write ADSR directly to SID
                lda mt_chnsr,x
                sta SIDBASE+6,x
                lda mt_chnad,x
                sta SIDBASE+5,x"""
    else:
        newnote_adsr_inline = ''

    if ADSR_AD_FIRST in features:
        newnote_adsr = """\
                lda mt_insad-1,y
                sta mt_chnad,x
                lda mt_inssr-1,y
                sta mt_chnsr,x"""
    else:
        newnote_adsr = """\
                lda mt_inssr-1,y
                sta mt_chnsr,x
                lda mt_insad-1,y
                sta mt_chnad,x"""

    # New note exit — depends on write mode
    if UNBUFFERED_WRITES in features:
        newnote_exit = '                jmp ce_ldwav'
    elif NEWNOTE_ALL_REGS in features:
        newnote_exit = '                jmp ce_ldregs'
    else:
        newnote_exit = '                jmp ce_ldwav'

    t0_dispatch_call = '                jsr mt_t0_dispatch' if TICK0_FX in features else ''

    blocks.append(Block(
        name='tick0_path',
        code=f"""\
; =============================================================================
; Tick 0 path
; =============================================================================
ce_t0

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
{ol_features}
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

                ; Y = instrument index from gate timer load
                lda mt_insvibdelay-1,y
                sta mt_chnvibdelay,x
                lda mt_insvibparam-1,y
                sta mt_chnparam,x

                ; toneporta skip
                lda mt_chnnewfx,x
                cmp #3
                beq ce_nnn

                ; first-frame waveform (Y still = instrument)
                lda mt_insfirstwave-1,y
                beq ce_skfw
                cmp #$fe
                bcs ce_skfw
                sta mt_chnwave,x
ce_skfw
                lda #$ff
                sta mt_chngate,x

                ; pulse ptr (Y still = instrument)
                lda mt_inspulseptr-1,y
                beq ce_npi
                sta mt_chnpulseptr,x
                lda #0
                sta mt_chnpulsetime,x
ce_npi
                ; filter ptr (Y still = instrument)
                lda mt_insfiltptr-1,y
                beq ce_nfi
                sta mt_g_fstep+1
                lda #0
                sta mt_g_ftime+1
ce_nfi
                ; wave ptr (Y still = instrument)
                lda mt_inswaveptr-1,y
                sta mt_chnwaveptr,x
                lda #0
                sta mt_chnwavetime,x

                ; ADSR (Y still = instrument)
{newnote_adsr}
{newnote_adsr_inline}

                ; tick-0 effect
{t0_dispatch_call}

                ; register writes for new-note frame
{newnote_exit}

ce_nnn
{t0_dispatch_call}
                jmp ce_wave""",
        provides={'ce_t0', 'ce_nolp', 'ce_nonew', 'ce_newn', 'ce_skfw',
                  'ce_npi', 'ce_nfi', 'ce_nnn', 'ce_notr', 'ce_norep'},
        requires={'mt_chnpattptr', 'mt_chnsongnum', 'mt_songtbllo', 'mt_songtblhi',
                  'mt_chnsongptr', 'mt_chninstr', 'mt_insgatetimer', 'mt_chngatetimer',
                  'mt_chnnewnote', 'mt_chnnote', 'mt_chnfx', 'mt_insvibdelay',
                  'mt_insvibparam', 'mt_chnvibdelay', 'mt_chnparam', 'mt_chnnewfx',
                  'mt_insfirstwave', 'mt_chnwave', 'mt_chngate', 'mt_inspulseptr',
                  'mt_chnpulseptr', 'mt_chnpulsetime', 'mt_insfiltptr', 'mt_g_fstep',
                  'mt_g_ftime', 'mt_inswaveptr', 'mt_chnwaveptr', 'mt_chnwavetime',
                  'mt_insad', 'mt_inssr', 'mt_chnad', 'mt_chnsr',
                  'ce_ldregs', 'ce_ldwav', 'ce_wave', 'mt_chnpattnum', 'mt_chntrans'} |
                 ({'mt_t0_dispatch'} if TICK0_FX in features else set()),
        byte_estimate=150,
        order_group=40,
    ))

    # =========================================================================
    # TICK-0 DISPATCH  (order_group=41)
    # =========================================================================
    if TICK0_FX in features:
        # Build CMP chain — only include entries for active FX
        dispatch_lines = []
        dispatch_lines.append('mt_t0_dispatch')
        dispatch_lines.append('                lda mt_chnnewparam,x')
        dispatch_lines.append('                ldy mt_chnnewfx,x')
        dispatch_lines.append('                beq mt_t0_fx0')
        dispatch_lines.append('                cpy #5')
        dispatch_lines.append('                bcc mt_t0_fx14')

        # FX 5-F: only include comparisons for active handlers
        fx_checks = [
            (5, SET_AD, 'mt_t0_fx5'),
            (6, SET_SR, 'mt_t0_fx6'),
            (7, SET_WAVE, 'mt_t0_fx7'),
            (8, SET_WAVEPTR, 'mt_t0_fx8'),
            (9, SET_PULSEPTR, 'mt_t0_fx9'),
            (0xa, SET_FILTPTR, 'mt_t0_fxa'),
            (0xb, SET_FILTCTRL, 'mt_t0_fxb'),
            (0xc, SET_FILTCUT, 'mt_t0_fxc'),
            (0xd, SET_MASTERVOL, 'mt_t0_fxd'),
            (0xe, FUNKTEMPO, 'mt_t0_fxe'),
        ]
        for num, flag, label in fx_checks:
            if flag in features:
                dispatch_lines.append(f'                beq {label}' if num == 5 else
                                      f'                cpy #${num:x}\n                beq {label}')

        dispatch_lines.append('                ; FX F: set tempo (fall through)')

        # FX F handler
        dispatch_lines.append("""\
mt_t0_fxf       cmp #$80
                bcs mt_t0fc
                sta mt_chntempo
                sta mt_chntempo+7
                sta mt_chntempo+14
                rts
mt_t0fc         and #$7f
                sta mt_chntempo,x
                rts""")

        # FX 0 handler
        vib_fix = """\
                bne mt_t0_fx34
                lda #0""" if VIBRATO_PARAM_FIX in features else ''
        dispatch_lines.append(f"""\
mt_t0_fx0       ldy mt_chninstr,x
                lda mt_insvibparam-1,y
{vib_fix}
mt_t0_fx14
mt_t0_fx34
                sta mt_chnparam,x
                lda mt_chnnewfx,x
                sta mt_chnfx,x
                rts""")

        # Individual handlers
        if SET_AD in features:
            dispatch_lines.append('mt_t0_fx5       sta mt_chnad,x\n                rts')
        if SET_SR in features:
            dispatch_lines.append('mt_t0_fx6       sta mt_chnsr,x\n                rts')
        if SET_WAVE in features:
            dispatch_lines.append('mt_t0_fx7       sta mt_chnwave,x\n                rts')
        if SET_WAVEPTR in features:
            dispatch_lines.append("""\
mt_t0_fx8       sta mt_chnwaveptr,x
                lda #0
                sta mt_chnwavetime,x
                rts""")
        if SET_PULSEPTR in features:
            dispatch_lines.append("""\
mt_t0_fx9       sta mt_chnpulseptr,x
                lda #0
                sta mt_chnpulsetime,x
                rts""")
        if SET_FILTPTR in features:
            dispatch_lines.append("""\
mt_t0_fxa       sta mt_g_fstep+1
                lda #0
                sta mt_g_ftime+1
                rts""")
        if SET_FILTCTRL in features:
            dispatch_lines.append("""\
mt_t0_fxb       sta mt_g_fctrl+1
                cmp #0
                bne mt_t0bx
                sta mt_g_fstep+1
mt_t0bx         rts""")
        if SET_FILTCUT in features:
            dispatch_lines.append('mt_t0_fxc       sta mt_g_fcut+1\n                rts')
        if SET_MASTERVOL in features:
            dispatch_lines.append('mt_t0_fxd       sta mt_g_mvol+1\n                rts')
        if FUNKTEMPO in features:
            dispatch_lines.append("""\
mt_t0_fxe       tay
                lda mt_speedlefttbl-1,y
                sta mt_funktbl
                lda mt_speedrighttbl-1,y
                sta mt_funktbl+1
                lda #0
                beq mt_t0_fxf""")

        blocks.append(Block(
            name='t0_dispatch',
            code='\n'.join(dispatch_lines),
            provides={'mt_t0_dispatch', 'mt_t0_fx0', 'mt_t0_fx14', 'mt_t0_fx34',
                      'mt_t0_fxf', 'mt_t0fc'} |
                     ({f'mt_t0_fx{n}' for n, flag, _ in fx_checks if flag in features}),
            requires={'mt_chnnewparam', 'mt_chnnewfx', 'mt_chninstr', 'mt_insvibparam',
                      'mt_chnparam', 'mt_chnfx', 'mt_chntempo'},
            needs={TICK0_FX},
            byte_estimate=80,
            order_group=41,
        ))

    # =========================================================================
    # VARIABLES  (always present, order_group=90)
    # =========================================================================
    scratch_vars = """\
; ---- scratch variables ----
mt_wv_optr      .byte 0
mt_wv_left      .byte 0
mt_wv_param     .byte 0"""

    if EFFECTS in features:
        scratch_vars += """
mt_fx_spd       .byte 0
mt_fx_shift     .byte 0"""
    if TONEPORTA in features:
        scratch_vars += """
mt_fx_slo       .byte 0
mt_fx_shi       .byte 0"""

    group5 = """\
; Group 5 - ADSR/gate timer/lastnote  (21 bytes)
mt_chnad        .dsb 21,0
mt_chnsr        = mt_chnad+1
mt_chngatetimer = mt_chnad+2
mt_chnlastnote  = mt_chnad+3"""

    blocks.append(Block(
        name='variables',
        code=f"""\
; =============================================================================
; Variables
; =============================================================================
{scratch_vars}

; ---- funktempo table ----
mt_funktbl      .byte 8, 5

; ---- channel variables (stride 7, 3 channels) ----
; Group 1 - sequencer
mt_chnsongptr   .dsb 21,0
mt_chntrans     = mt_chnsongptr+1
mt_chnrepeat    = mt_chnsongptr+2
mt_chnpattptr   = mt_chnsongptr+3
mt_chnpkrest    = mt_chnsongptr+4
mt_chnnewfx     = mt_chnsongptr+5
mt_chnnewparam  = mt_chnsongptr+6

; Group 2 - note/wave/pulse
mt_chnfx        .dsb 21,0
mt_chnparam     = mt_chnfx+1
mt_chnnewnote   = mt_chnfx+2
mt_chnwaveptr   = mt_chnfx+3
mt_chnwave      = mt_chnfx+4
mt_chnpulseptr  = mt_chnfx+5
mt_chnpulsetime = mt_chnfx+6

; Group 3 - song/tempo/note
mt_chnsongnum   .dsb 21,0
mt_chnpattnum   = mt_chnsongnum+1
mt_chntempo     = mt_chnsongnum+2
mt_chncounter   = mt_chnsongnum+3
mt_chnnote      = mt_chnsongnum+4
mt_chninstr     = mt_chnsongnum+5
mt_chngate      = mt_chnsongnum+6

; Group 4 - vibrato/freq/pulse shadows
mt_chnvibtime   .dsb 21,0
mt_chnvibdelay  = mt_chnvibtime+1
mt_chnwavetime  = mt_chnvibtime+2
mt_chnfreqlo    = mt_chnvibtime+3
mt_chnfreqhi    = mt_chnvibtime+4
mt_chnpulselo   = mt_chnvibtime+5
mt_chnpulsehi   = mt_chnvibtime+6

{group5}""",
        provides={'mt_wv_optr', 'mt_wv_left', 'mt_wv_param', 'mt_funktbl',
                  'mt_chnsongptr', 'mt_chntrans', 'mt_chnrepeat', 'mt_chnpattptr',
                  'mt_chnpkrest', 'mt_chnnewfx', 'mt_chnnewparam',
                  'mt_chnfx', 'mt_chnparam', 'mt_chnnewnote', 'mt_chnwaveptr',
                  'mt_chnwave', 'mt_chnpulseptr', 'mt_chnpulsetime',
                  'mt_chnsongnum', 'mt_chnpattnum', 'mt_chntempo', 'mt_chncounter',
                  'mt_chnnote', 'mt_chninstr', 'mt_chngate',
                  'mt_chnvibtime', 'mt_chnvibdelay', 'mt_chnwavetime',
                  'mt_chnfreqlo', 'mt_chnfreqhi', 'mt_chnpulselo', 'mt_chnpulsehi',
                  'mt_chnad', 'mt_chnsr', 'mt_chngatetimer', 'mt_chnlastnote'} |
                 ({'mt_fx_spd', 'mt_fx_shift'} if EFFECTS in features else set()) |
                 ({'mt_fx_slo', 'mt_fx_shi'} if TONEPORTA in features else set()),
        byte_estimate=100,
        order_group=90,
    ))

    return blocks
