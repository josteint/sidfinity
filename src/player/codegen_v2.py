"""
codegen_v2.py — Instruction-level 6502 code generator for the SIDfinity player.

Unlike blocks.py which selects pre-written blocks, this generates assembly
instruction-by-instruction based on what a specific song needs. Each emit_*
function decides per-instruction what to include.

Target: ~500 bytes for simple songs (Covfefe), ~900 bytes full features.
"""

from dataclasses import dataclass, field
from codegen import detect_features, close_features, \
    FILTER, EFFECTS, VIBRATO, PORTAMENTO, TONEPORTA, CALCULATED_SPEED, REL_LASTNOTE, FREQ_SLIDE, \
    FUNKTEMPO, WAVE_DELAY, WAVE_CMD, PULSE_MOD, TICK0_FX, \
    ORDERLIST_TRANS, ORDERLIST_REPEAT, SET_AD, SET_SR, SET_WAVE, \
    SET_WAVEPTR, SET_PULSEPTR, SET_FILTPTR, SET_FILTCTRL, SET_FILTCUT, \
    SET_MASTERVOL, SET_TEMPO, BUFFERED_WRITES, UNBUFFERED_WRITES, \
    ADSR_AD_FIRST, LOADREGS_AD_FIRST, NEWNOTE_ALL_REGS, VIBRATO_PARAM_FIX, \
    NOHR_INSTR, LEGATO_INSTR, HAS_KEYOFF, HAS_KEYON, HAS_PACKED_REST


@dataclass
class Ctx:
    """Code generation context — tracks emitted assembly and features."""
    features: frozenset
    lines: list = field(default_factory=list)
    byte_est: int = 0

    def has(self, flag):
        return flag in self.features

    def emit(self, text):
        self.lines.append(text)

    def comment(self, text):
        self.emit(f'; {text}')

    def label(self, name):
        self.emit(f'{name}')

    def inst(self, op, arg='', comment=''):
        """Emit one instruction, properly formatted."""
        if comment:
            self.emit(f'                {op:4s} {arg:24s} ; {comment}')
        else:
            if arg:
                self.emit(f'                {op} {arg}')
            else:
                self.emit(f'                {op}')

    def data(self, directive, args):
        self.emit(f'                {directive} {args}')

    def blank(self):
        self.emit('')

    def equate(self, name, value):
        self.emit(f'{name:<16s} = {value}')

    def section(self, title):
        self.blank()
        self.emit(f'; === {title} ===')

    def cmp_gate_timer(self):
        """Emit CMP for gate timer — hardcoded if uniform, variable if mixed."""
        if self.uniform_gate_timer is not None:
            self.inst('cmp', f'#${self.uniform_gate_timer:02x}',
                      comment=f'hardcoded gatetimer={self.uniform_gate_timer}')
        else:
            self.inst('cmp', 'mt_chngatetimer,x')

    def source(self):
        from peephole import peephole_optimize
        self.lines = peephole_optimize(self.lines)
        return '\n'.join(self.lines)


def generate_player(song):
    """Generate xa65 assembly for this specific song. Returns source string."""
    features = detect_features(song)
    ctx = Ctx(features=features)

    # Detect uniform gate timer for hardcoding (saves 2 cycles per check).
    # Clamp gate_timer to max(0, tempo-1): with tempo <= gate_timer, hard restart
    # fires on the first frame of the note, silencing it entirely.
    _max_gt = max(0, song.tempo - 1)
    gt_values = set()
    for inst in song.instruments:
        raw = getattr(inst, '_gate_timer_raw', inst.gate_timer)
        gt_values.add(min(raw & 0x3F, _max_gt))
    ctx.uniform_gate_timer = gt_values.pop() if len(gt_values) == 1 else None

    # Multispeed support
    ctx.multiplier = getattr(song, 'multiplier', 0)
    ctx.cia_timer = getattr(song, '_cia_timer', None)

    emit_preamble(ctx)
    emit_jump_table(ctx)
    emit_init(ctx)
    emit_play_dispatch(ctx)
    emit_full_init(ctx)
    emit_filter(ctx)
    emit_channel_exec(ctx)
    emit_wave_table(ctx)
    if ctx.has(EFFECTS):
        emit_effects(ctx)
    emit_pulse_table(ctx)
    emit_gate_timer(ctx)
    emit_pattern_reader(ctx)
    emit_register_writes(ctx)
    emit_tick0_path(ctx)
    emit_new_note_init(ctx)
    if ctx.has(TICK0_FX):
        emit_tick0_dispatch(ctx)
    emit_variables(ctx)

    return ctx.source()


# =============================================================================
# Preamble — defines, constants, origin
# =============================================================================

def emit_preamble(ctx):
    ctx.emit('; SIDfinity Compact Player (codegen_v2)')
    ctx.blank()
    # Packer-overridable defines
    for name, default in [('base', '$1000'), ('SIDBASE', '$d400'),
                           ('FIRSTNOTE', '0'), ('DEFAULTTEMPO', '6'),
                           ('ADPARAM', '0'), ('SRPARAM', '0'),
                           ('FIRSTNOHRINSTR', '$3f'), ('FIRSTLEGATOINSTR', '$3f')]:
        ctx.emit(f'#ifndef {name}')
        ctx.equate(name, default)
        ctx.emit('#endif')
    ctx.blank()
    # Zero page
    ctx.equate('mt_temp1', '$fc')
    ctx.equate('mt_temp2', '$fd')
    ctx.blank()
    # Constants
    ctx.equate('ENDPATT', '$00')
    ctx.equate('FX', '$40')
    ctx.equate('FXONLY', '$50')
    ctx.equate('NOTE', '$60')
    ctx.equate('REST', '$bd')
    ctx.equate('KEYOFF', '$be')
    ctx.equate('KEYON', '$bf')
    ctx.equate('FPKREST', '$c0')
    if ctx.has(ORDERLIST_REPEAT):
        ctx.equate('REPEAT', '$d0')
    if ctx.has(ORDERLIST_TRANS):
        ctx.equate('TRANSDN', '$e0')
        ctx.equate('TRANS', '$f0')
    ctx.equate('LOOPSONG', '$ff')
    ctx.equate('LOOPTBL', '$ff')
    ctx.blank()
    ctx.emit('                * = base')


# =============================================================================
# Jump table + init
# =============================================================================

def emit_jump_table(ctx):
    ctx.section('jump table')
    ctx.inst('jmp', 'mt_init')
    ctx.inst('jmp', 'mt_play')


def emit_init(ctx):
    ctx.section('mt_init')
    ctx.label('mt_init')
    ctx.inst('sta', 'mt_temp1')
    ctx.inst('asl')
    ctx.inst('clc')
    ctx.inst('adc', 'mt_temp1')
    ctx.inst('sta', 'mt_songidx')
    ctx.inst('lda', '#0')
    ctx.inst('sta', 'mt_initpend')
    ctx.inst('rts')
    ctx.label('mt_songidx')
    ctx.data('.byte', '0')
    ctx.label('mt_initpend')
    ctx.data('.byte', '$80')


# =============================================================================
# Play dispatch
# =============================================================================

def emit_play_dispatch(ctx):
    ctx.section('mt_play')
    ctx.label('mt_play')
    ctx.inst('bit', 'mt_initpend')
    ctx.inst('bmi', 'mp_run')
    ctx.inst('jmp', 'mt_fullinit')
    ctx.label('mp_run')
    # Filter / volume write
    if ctx.has(FILTER):
        ctx.inst('jsr', 'mt_filterexec')
    else:
        # Inline volume write — saves JSR/RTS overhead (12 cycles)
        ctx.label('mt_g_mvol')
        ctx.inst('lda', '#$0f')
        ctx.inst('sta', 'SIDBASE+$18')

    multiplier = getattr(ctx, 'multiplier', 0)
    if multiplier and multiplier > 1:
        # Multispeed: execute all 3 channels N times per frame.
        # The tempo counter decrements each call; with N calls per frame,
        # it takes tempo/N frames to process one tick = correct timing.
        ctx.inst('lda', f'#{multiplier}', comment=f'multispeed {multiplier}x')
        ctx.inst('sta', 'mt_mspeed_cnt')
        ctx.label('mt_mspeed_loop')

    ctx.inst('ldx', '#0')
    ctx.inst('jsr', 'mt_execchn')
    ctx.inst('ldx', '#7')
    ctx.inst('jsr', 'mt_execchn')
    ctx.inst('ldx', '#14')
    if multiplier and multiplier > 1:
        ctx.inst('jsr', 'mt_execchn')
        ctx.inst('dec', 'mt_mspeed_cnt')
        ctx.inst('bne', 'mt_mspeed_loop')
        ctx.inst('rts')
        ctx.label('mt_mspeed_cnt')
        ctx.data('.byte', '0')
    else:
        ctx.inst('jmp', 'mt_execchn')


# =============================================================================
# Full init
# =============================================================================

def emit_full_init(ctx):
    ctx.section('mt_fullinit')
    ctx.label('mt_fullinit')
    ctx.inst('ldy', 'mt_songidx')
    ctx.inst('lda', '#0')
    ctx.inst('ldx', '#41')
    ctx.label('fi_c1')
    ctx.inst('sta', 'mt_chnsongptr,x')
    ctx.inst('dex')
    ctx.inst('bpl', 'fi_c1')
    ctx.inst('ldx', '#41')
    ctx.label('fi_c2')
    ctx.inst('sta', 'mt_chnvibtime,x')
    ctx.inst('dex')
    ctx.inst('bpl', 'fi_c2')
    ctx.inst('ldx', '#$18')
    ctx.label('fi_sid')
    ctx.inst('sta', 'SIDBASE,x')
    ctx.inst('dex')
    ctx.inst('bpl', 'fi_sid')
    # Filter SMC clears
    if ctx.has(FILTER):
        ctx.inst('sta', 'mt_g_fstep+1')
        ctx.inst('sta', 'mt_g_ftime+1')
        ctx.inst('sta', 'mt_g_fcut+1')
        ctx.inst('sta', 'mt_g_fctrl+1')
        ctx.inst('sta', 'mt_g_ftype+1')
    # Volume
    ctx.inst('lda', '#$0f')
    ctx.inst('sta', 'mt_g_mvol+1')
    ctx.inst('sta', 'SIDBASE+$18')
    # Funktempo defaults
    if ctx.has(FUNKTEMPO):
        ctx.inst('lda', '#8')
        ctx.inst('sta', 'mt_funktbl')
        ctx.inst('lda', '#5')
        ctx.inst('sta', 'mt_funktbl+1')
    ctx.inst('lda', '#$80')
    ctx.inst('sta', 'mt_initpend')
    # Per-channel init
    ctx.inst('ldx', '#14')
    ctx.inst('sty', 'mt_temp1')
    ctx.inst('tya')
    ctx.inst('clc')
    ctx.inst('adc', '#2')
    ctx.inst('tay')
    ctx.inst('jsr', 'fi_ch')
    ctx.inst('ldx', '#7')
    ctx.inst('dey')
    ctx.inst('jsr', 'fi_ch')
    ctx.inst('ldx', '#0')
    ctx.inst('dey')
    ctx.label('fi_ch')
    ctx.inst('tya')
    ctx.inst('sta', 'mt_chnsongnum,x')
    ctx.inst('lda', '#DEFAULTTEMPO')
    ctx.inst('sta', 'mt_chntempo,x')
    ctx.inst('lda', '#1')
    ctx.inst('sta', 'mt_chncounter,x')
    ctx.inst('sta', 'mt_chninstr,x')
    ctx.inst('lda', '#$fe')
    ctx.inst('sta', 'mt_chngate,x')
    ctx.inst('lda', '#0')
    ctx.inst('sta', 'mt_chnad,x')
    ctx.inst('sta', 'mt_chnsr,x')
    ctx.inst('rts')


# =============================================================================
# Filter
# =============================================================================

def emit_filter(ctx):
    ctx.section('filter')
    if not ctx.has(FILTER):
        # Volume write is inlined in play dispatch — just emit equates
        ctx.equate('mt_g_fstep', 'mt_g_mvol')
        ctx.equate('mt_g_ftime', 'mt_g_mvol')
        ctx.equate('mt_g_fcut', 'mt_g_mvol')
        ctx.equate('mt_g_fctrl', 'mt_g_mvol')
        ctx.equate('mt_g_ftype', 'mt_g_mvol')
    else:
        # Full filter table stepper
        ctx.label('mt_filterexec')
        ctx.label('mt_g_fstep')
        ctx.inst('ldy', '#0')
        ctx.inst('beq', 'fe_out')
        ctx.label('mt_g_ftime')
        ctx.inst('lda', '#0')
        ctx.inst('bne', 'fe_mod')
        ctx.inst('lda', 'mt_filttimetbl-1,y')
        ctx.inst('beq', 'fe_cut')
        ctx.inst('cmp', '#$80')
        ctx.inst('bcs', 'fe_par')
        ctx.inst('sta', 'mt_g_ftime+1')
        ctx.inst('jmp', 'fe_mod')
        ctx.label('fe_par')
        ctx.inst('asl')
        ctx.inst('sta', 'mt_g_ftype+1')
        ctx.inst('lda', 'mt_filtspdtbl-1,y')
        ctx.inst('sta', 'mt_g_fctrl+1')
        ctx.inst('lda', 'mt_filttimetbl,y')
        ctx.inst('bne', 'fe_adv2')
        ctx.inst('iny')
        ctx.label('fe_cut')
        ctx.inst('lda', 'mt_filtspdtbl-1,y')
        ctx.inst('sta', 'mt_g_fcut+1')
        ctx.inst('jmp', 'fe_adv')
        ctx.label('fe_mod')
        ctx.inst('clc')
        ctx.inst('lda', 'mt_g_fcut+1')
        ctx.inst('adc', 'mt_filtspdtbl-1,y')
        ctx.inst('sta', 'mt_g_fcut+1')
        ctx.inst('dec', 'mt_g_ftime+1')
        ctx.inst('bne', 'fe_out')
        ctx.label('fe_adv')
        ctx.inst('lda', 'mt_filttimetbl,y')
        ctx.label('fe_adv2')
        ctx.inst('cmp', '#LOOPTBL')
        ctx.inst('bne', 'fe_nj')
        ctx.inst('lda', 'mt_filtspdtbl,y')
        ctx.inst('sta', 'mt_g_fstep+1')
        ctx.inst('jmp', 'fe_out')
        ctx.label('fe_nj')
        ctx.inst('iny')
        ctx.inst('sty', 'mt_g_fstep+1')
        ctx.label('fe_out')
        ctx.label('mt_g_fcut')
        ctx.inst('lda', '#0')
        ctx.inst('sta', 'SIDBASE+$16')
        ctx.label('mt_g_fctrl')
        ctx.inst('lda', '#0')
        ctx.inst('sta', 'SIDBASE+$17')
        ctx.label('mt_g_ftype')
        ctx.inst('lda', '#0')
        ctx.label('mt_g_mvol')
        ctx.inst('ora', '#$0f')
        ctx.inst('sta', 'SIDBASE+$18')
        ctx.inst('rts')


# =============================================================================
# Channel execution entry — counter + tempo reload
# =============================================================================

def emit_channel_exec(ctx):
    ctx.section('channel exec')
    ctx.label('mt_execchn')
    ctx.inst('dec', 'mt_chncounter,x')
    ctx.inst('bne', 'ce_not0')
    ctx.inst('jmp', 'ce_t0')
    ctx.label('ce_not0')
    ctx.inst('bpl', 'ce_wave')
    # Underflow reload
    ctx.inst('lda', 'mt_chntempo,x')
    if ctx.has(FUNKTEMPO):
        ctx.inst('cmp', '#2')
        ctx.inst('bcs', 'ce_str')
        ctx.inst('tay')
        ctx.inst('eor', '#1')
        ctx.inst('sta', 'mt_chntempo,x')
        ctx.inst('lda', 'mt_funktbl,y')
        ctx.inst('sec')
        ctx.inst('sbc', '#1')
    ctx.label('ce_str')
    ctx.inst('sta', 'mt_chncounter,x')
    # Fall through to wave table


# =============================================================================
# Wave table
# =============================================================================

def emit_wave_table(ctx):
    ctx.section('wave table')
    ctx.label('ce_wave')
    ctx.inst('ldy', 'mt_chnwaveptr,x')
    ctx.inst('bne', 'ce_wgo')
    ctx.inst('jmp', 'ce_wdone')
    ctx.label('ce_wgo')

    if ctx.has(WAVE_CMD):
        # Need mt_wv_optr for note lookup after advance (WAVE_CMD ce_wpost path).
        # WAVE_DELAY without WAVE_CMD doesn't need this — Y is still valid
        # when the note column is read pre-advance at ce_wadv.
        ctx.inst('sty', 'mt_wv_optr')

    ctx.inst('lda', 'mt_wavetbl-1,y')

    if ctx.has(WAVE_DELAY):
        # Bias format: $00-$0F = delay, $10+ = waveform+bias, $E0+ = cmd
        ctx.inst('cmp', '#$10')
        ctx.inst('bcs', 'ce_wndly')
        ctx.inst('cmp', 'mt_chnwavetime,x')
        ctx.inst('beq', 'ce_wdlyok')
        ctx.inst('inc', 'mt_chnwavetime,x')
        ctx.inst('jmp', 'ce_wdone')
        ctx.label('ce_wdlyok')
        ctx.inst('lda', '#0')
        if ctx.has(WAVE_CMD):
            ctx.inst('sta', 'mt_wv_left')
        ctx.inst('jmp', 'ce_wadv')
        ctx.label('ce_wndly')
        # Subtract bias (carry set from CMP)
        ctx.inst('sbc', '#$10')
        if ctx.has(WAVE_CMD):
            ctx.inst('sta', 'mt_wv_left')
            ctx.inst('cmp', '#$e0')
            ctx.inst('bcs', 'ce_wadv')
        ctx.inst('sta', 'mt_chnwave,x')
    else:
        # No-bias format: $00 = no change, $01-$FE = waveform, $FF = loop marker
        # No CMP/SBC needed — saves 7 cycles per channel
        if ctx.has(WAVE_CMD):
            # Must store to mt_wv_left BEFORE the $00 branch, otherwise
            # a stale command byte causes ce_wpost to dispatch wrong.
            ctx.inst('sta', 'mt_wv_left')
            ctx.inst('beq', 'ce_wadv', comment='$00 = no waveform change')
            ctx.inst('cmp', '#$e0')
            ctx.inst('bcs', 'ce_wadv')
        else:
            ctx.inst('beq', 'ce_wadv', comment='$00 = no waveform change')
        ctx.inst('sta', 'mt_chnwave,x')

    # Advance pointer
    ctx.label('ce_wadv')
    if ctx.has(WAVE_DELAY):
        ctx.inst('lda', '#0')
        ctx.inst('sta', 'mt_chnwavetime,x')
    # Read note column BEFORE advancing — avoids Y save/restore
    if not ctx.has(WAVE_CMD):
        # Simple path: read note at current Y, then advance
        ctx.inst('lda', 'mt_notetbl-1,y', comment='note at current pos')
        ctx.inst('sta', 'mt_wv_optr', comment='stash note value')
    ctx.inst('lda', 'mt_wavetbl,y')
    ctx.inst('cmp', '#LOOPTBL')
    ctx.inst('bne', 'ce_wnj')
    ctx.inst('lda', 'mt_notetbl,y')
    ctx.inst('sta', 'mt_chnwaveptr,x')
    ctx.inst('jmp', 'ce_wpost')
    ctx.label('ce_wnj')
    ctx.inst('iny')
    ctx.inst('tya')
    ctx.inst('sta', 'mt_chnwaveptr,x')

    # Right column — note/freq
    ctx.label('ce_wpost')
    if ctx.has(WAVE_CMD):
        ctx.inst('lda', 'mt_wv_left')
        ctx.inst('cmp', '#$e0')
        ctx.inst('bcs', 'ce_wcmd')
        # WAVE_CMD path still uses saved Y for note
        ctx.inst('ldy', 'mt_wv_optr')
        ctx.inst('lda', 'mt_notetbl-1,y')
    else:
        # Note was stashed in mt_wv_optr before advance
        ctx.inst('lda', 'mt_wv_optr')
    ctx.inst('beq', 'ce_wdone')

    if ctx.has(FREQ_SLIDE):
        # Detect freq_slide: packed right $60-$7F (= .sng $E0-$FF after XOR $80)
        # These values never occur as note indices (max absolute note = 95 = packed $5F)
        ctx.inst('cmp', '#$60')
        ctx.inst('bcc', 'ce_wnote')       # $01-$5F = absolute note
        ctx.inst('cmp', '#$80')
        ctx.inst('bcs', 'ce_wnote')       # $80-$FF = relative note
        # $60-$7F = freq_slide: signed delta = A - $70
        ctx.inst('sec')
        ctx.inst('sbc', '#$70')
        ctx.inst('sta', 'mt_chnfreqslide,x')
        ctx.inst('jmp', 'ce_wdone')       # don't change note, just set slide
        ctx.label('ce_wnote')

    # Note resolution
    ctx.inst('bpl', 'ce_wabs')
    # Relative note (more common — falls through to freq lookup)
    ctx.inst('clc')
    ctx.inst('adc', 'mt_chnnote,x')
    ctx.inst('and', '#$7f')
    if ctx.has(REL_LASTNOTE):
        # Set mt_chnlastnote to the BASE note (mt_chnnote), not the
        # arpeggio-modified note. This enables calculated speed vibrato
        # for Hubbard-style instruments that use relative wave tables.
        # For GT2 arpeggios, the base note is still correct — vibrato
        # should oscillate around the written note, not the arpeggio step.
        ctx.inst('pha')
        ctx.inst('lda', 'mt_chnnote,x')
        ctx.inst('sta', 'mt_chnlastnote,x')
        ctx.inst('pla')
    ctx.inst('jmp', 'ce_wfreq')
    # Absolute note
    ctx.label('ce_wabs')
    ctx.inst('sta', 'mt_chnlastnote,x')
    ctx.label('ce_wfreq')
    ctx.inst('tay')
    ctx.inst('lda', 'mt_freqtbllo,y')
    ctx.inst('sta', 'mt_chnfreqlo,x')
    ctx.inst('lda', 'mt_freqtblhi,y')
    ctx.inst('sta', 'mt_chnfreqhi,x')
    if ctx.has(VIBRATO) or ctx.has(FREQ_SLIDE):
        ctx.inst('lda', '#0')
        if ctx.has(VIBRATO):
            ctx.inst('sta', 'mt_chnvibtime,x')
        if ctx.has(FREQ_SLIDE):
            ctx.inst('sta', 'mt_chnfreqslide,x')
    if ctx.has(WAVE_CMD) or ctx.has(EFFECTS):
        ctx.inst('jmp', 'ce_pulse')
    # else: falls through to ce_wdone → ce_pulse

    # Wave command dispatch
    if ctx.has(WAVE_CMD):
        ctx.label('ce_wcmd')
        ctx.inst('ldy', 'mt_wv_optr')
        ctx.inst('lda', 'mt_notetbl-1,y')
        ctx.inst('sta', 'mt_wv_param')
        ctx.inst('lda', 'mt_wv_left')
        ctx.inst('and', '#$0f')
        ctx.inst('cmp', '#5')
        ctx.inst('bcs', 'ce_wct0')
        if ctx.has(EFFECTS):
            ctx.inst('sta', 'mt_chnfx,x')
            ctx.inst('lda', 'mt_wv_param')
            ctx.inst('sta', 'mt_chnparam,x')
            ctx.inst('jmp', 'ce_runfx')
        else:
            ctx.inst('jmp', 'ce_pulse')
        ctx.label('ce_wct0')
        if ctx.has(TICK0_FX):
            # Don't clobber mt_chnnewfx/mt_chnnewparam — those hold the
            # pending pattern-reader values (e.g. toneporta FX=3).
            # Pass fx index in Y, param in A directly to mt_t0_wave.
            ctx.inst('tay')
            ctx.inst('lda', 'mt_wv_param')
            ctx.inst('jsr', 'mt_t0_wave')
        ctx.inst('jmp', 'ce_pulse')

    # ce_wdone — run effects or go to pulse
    ctx.label('ce_wdone')
    if ctx.has(EFFECTS):
        ctx.inst('lda', 'mt_chncounter,x')
        ctx.inst('bne', 'ce_wdgo')
        ctx.inst('jmp', 'ce_pulse')
        ctx.label('ce_wdgo')
        ctx.label('ce_runfx')
        ctx.inst('ldy', 'mt_chnparam,x')
        ctx.inst('bne', 'ce_rfgo')
        if ctx.has(TONEPORTA):
            # Toneporta with param=0 means "snap to target" — don't skip
            ctx.inst('lda', 'mt_chnfx,x')
            ctx.inst('cmp', '#3')
            ctx.inst('bne', 'ce_rfskip')
            ctx.inst('jmp', 'ce_fx3')
            ctx.label('ce_rfskip')
        ctx.inst('jmp', 'ce_pulse')
        ctx.label('ce_rfgo')
    # else: fall through to ce_pulse (next section)


# =============================================================================
# Effects (only if EFFECTS active)
# =============================================================================

def emit_effects(ctx):
    ctx.section('effects')
    # Speed table load
    if ctx.has(CALCULATED_SPEED):
        # Calculated speed: bit 7 of left byte means "use calculated speed"
        ctx.inst('lda', 'mt_speedlefttbl-1,y')
        ctx.inst('bmi', 'ce_calcspd')
        ctx.inst('sta', 'mt_temp2')
        ctx.inst('lda', 'mt_speedrighttbl-1,y')
        ctx.inst('sta', 'mt_temp1')
        ctx.inst('jmp', 'ce_fxdisp')

        ctx.label('ce_calcspd')
        ctx.inst('and', '#$7f')
        if ctx.has(VIBRATO):
            ctx.inst('sta', 'mt_smc_fxspd+1', comment='SMC: patch CMP operand')
        else:
            ctx.inst('sta', 'mt_fx_spd')
        ctx.inst('lda', 'mt_speedrighttbl-1,y')
        ctx.inst('sta', 'mt_fx_shift')
        ctx.inst('ldy', 'mt_chnlastnote,x')
        ctx.inst('sec')
        ctx.inst('lda', 'mt_freqtbllo+1-FIRSTNOTE,y')
        ctx.inst('sbc', 'mt_freqtbllo-FIRSTNOTE,y')
        ctx.inst('sta', 'mt_temp1')
        ctx.inst('lda', 'mt_freqtblhi+1-FIRSTNOTE,y')
        ctx.inst('sbc', 'mt_freqtblhi-FIRSTNOTE,y')
        ctx.inst('sta', 'mt_temp2')
        ctx.inst('ldy', 'mt_fx_shift')
        ctx.inst('beq', 'ce_fxdisp')
        ctx.label('ce_shft')
        ctx.inst('lsr', 'mt_temp2')
        ctx.inst('ror', 'mt_temp1')
        ctx.inst('dey')
        ctx.inst('bne', 'ce_shft')
    else:
        # No calculated speed: left byte is the speed high byte (no bit 7 flag).
        # No BMI branch — all speed entries are normal speed.
        ctx.inst('lda', 'mt_speedrighttbl-1,y')
        ctx.inst('sta', 'mt_temp1')
        ctx.inst('lda', 'mt_speedlefttbl-1,y')
        ctx.inst('sta', 'mt_temp2')

    # FX dispatch — Z3-verified: CMP #2 / BCC fxadd / BEQ fxsub
    # replaces CMP #1 / BNE / JMP / CMP #2 / BNE / JMP (saves 8 bytes, 8 cycles)
    ctx.label('ce_fxdisp')
    ctx.inst('lda', 'mt_chnfx,x')
    if ctx.has(VIBRATO):
        ctx.inst('beq', 'ce_fx0')
    else:
        ctx.inst('beq', 'ce_fxnop')
    ctx.inst('cmp', '#2')
    ctx.inst('bcc', 'ce_fxadd', comment='FX 1: carry clear → add')
    ctx.inst('beq', 'ce_fxsub', comment='FX 2: zero → sub')
    # FX 3 or 4 (A > 2)
    if ctx.has(TONEPORTA) and ctx.has(VIBRATO):
        ctx.inst('cmp', '#3')
        ctx.inst('beq', 'ce_fx3j')
        ctx.inst('jmp', 'ce_fx4')
        ctx.label('ce_fx3j')
        ctx.inst('jmp', 'ce_fx3')
    elif ctx.has(TONEPORTA):
        ctx.inst('cmp', '#3')
        ctx.inst('beq', 'ce_fx3j')
        ctx.inst('jmp', 'ce_pulse')
        ctx.label('ce_fx3j')
        ctx.inst('jmp', 'ce_fx3')
    elif ctx.has(VIBRATO):
        ctx.inst('jmp', 'ce_fx4')
    else:
        ctx.inst('jmp', 'ce_pulse')

    if not ctx.has(VIBRATO):
        ctx.label('ce_fxnop')
        ctx.inst('jmp', 'ce_pulse')

    if ctx.has(VIBRATO):
        # FX 0 — inst vibrato with delay
        ctx.label('ce_fx0')
        ctx.inst('lda', 'mt_chnvibdelay,x')
        ctx.inst('beq', 'ce_fx4')
        ctx.inst('dec', 'mt_chnvibdelay,x')
        ctx.inst('jmp', 'ce_pulse')
        # FX 4 — vibrato
        ctx.label('ce_fx4')
        ctx.inst('ldy', 'mt_chnparam,x')
        if ctx.has(CALCULATED_SPEED):
            # Calculated speed: BMI splits normal vs calculated paths
            ctx.inst('lda', 'mt_speedlefttbl-1,y')
            ctx.inst('bmi', 'ce_v4c')
            ctx.inst('and', '#$7f')
            ctx.inst('sta', 'mt_smc_fxspd+1', comment='SMC: patch CMP operand')
            ctx.inst('lda', 'mt_speedrighttbl-1,y')
            ctx.inst('sta', 'mt_temp1')
            ctx.inst('lda', '#0')
            ctx.inst('sta', 'mt_temp2')
            ctx.inst('jmp', 'ce_v4r')
            ctx.label('ce_v4c')
            ctx.inst('and', '#$7f')
            ctx.inst('sta', 'mt_smc_fxspd+1', comment='SMC: patch CMP operand')
            ctx.inst('lda', 'mt_speedrighttbl-1,y')
            ctx.inst('pha')
            ctx.inst('ldy', 'mt_chnlastnote,x')
            ctx.inst('sec')
            ctx.inst('lda', 'mt_freqtbllo+1-FIRSTNOTE,y')
            ctx.inst('sbc', 'mt_freqtbllo-FIRSTNOTE,y')
            ctx.inst('sta', 'mt_temp1')
            ctx.inst('lda', 'mt_freqtblhi+1-FIRSTNOTE,y')
            ctx.inst('sbc', 'mt_freqtblhi-FIRSTNOTE,y')
            ctx.inst('sta', 'mt_temp2')
            ctx.inst('pla')
            ctx.inst('tay')
            ctx.inst('beq', 'ce_v4r')
            ctx.label('ce_v4s')
            ctx.inst('lsr', 'mt_temp2')
            ctx.inst('ror', 'mt_temp1')
            ctx.inst('dey')
            ctx.inst('bne', 'ce_v4s')
        else:
            # NOCALCULATEDSPEED: left byte is vibrato speed (full byte, no
            # bit 7 flag). temp1 = right byte, temp2 = 0 always.
            ctx.inst('lda', '#0')
            ctx.inst('sta', 'mt_temp2')
            ctx.inst('lda', 'mt_speedrighttbl-1,y')
            ctx.inst('sta', 'mt_temp1')
            ctx.inst('lda', 'mt_speedlefttbl-1,y')
            ctx.inst('sta', 'mt_smc_fxspd+1', comment='SMC: patch CMP operand')
        ctx.label('ce_v4r')
        ctx.inst('lda', 'mt_chnvibtime,x')
        ctx.inst('bmi', 'ce_v4nc')
        ctx.label('mt_smc_fxspd')
        ctx.inst('cmp', '#0', comment='SMC: operand patched with fx speed')
        ctx.inst('nop', comment='pad: CMP imm is 1 byte shorter than CMP abs')
        ctx.inst('beq', 'ce_v4nc')
        ctx.inst('bcc', 'ce_v4n2')
        ctx.inst('eor', '#$ff')
        # Fall through to ce_v4nc (CLC) — carry is set from CMP above,
        # must clear before ADC. Original GT2 uses the same fall-through.
        ctx.label('ce_v4nc')
        ctx.inst('clc')
        ctx.label('ce_v4n2')
        ctx.inst('adc', '#2')
        ctx.label('ce_v4st')
        ctx.inst('sta', 'mt_chnvibtime,x')
        ctx.inst('lsr')
        ctx.inst('bcs', 'ce_fxsub')

    # Freq add
    ctx.label('ce_fxadd')
    ctx.inst('clc')
    ctx.inst('lda', 'mt_chnfreqlo,x')
    ctx.inst('adc', 'mt_temp1')
    ctx.inst('sta', 'mt_chnfreqlo,x')
    ctx.inst('lda', 'mt_chnfreqhi,x')
    ctx.inst('adc', 'mt_temp2')
    ctx.inst('sta', 'mt_chnfreqhi,x')
    ctx.inst('jmp', 'ce_pulse')

    # Freq sub
    ctx.label('ce_fxsub')
    ctx.inst('sec')
    ctx.inst('lda', 'mt_chnfreqlo,x')
    ctx.inst('sbc', 'mt_temp1')
    ctx.inst('sta', 'mt_chnfreqlo,x')
    ctx.inst('lda', 'mt_chnfreqhi,x')
    ctx.inst('sbc', 'mt_temp2')
    ctx.inst('sta', 'mt_chnfreqhi,x')
    if ctx.has(TONEPORTA):
        ctx.inst('jmp', 'ce_pulse')
        emit_toneporta(ctx)
    # Fall through to ce_pulse (emit_pulse_table is next)


def emit_toneporta(ctx):
    ctx.section('tone portamento')
    ctx.label('ce_fx3')
    ctx.inst('lda', 'mt_chnparam,x')
    ctx.inst('bne', 'ce_fx3go')
    ctx.inst('jmp', 'ce_tpsnap')
    ctx.label('ce_fx3go')
    ctx.inst('ldy', 'mt_chnparam,x')
    if ctx.has(CALCULATED_SPEED):
        # Calculated speed: BMI splits normal vs calculated paths
        ctx.inst('lda', 'mt_speedlefttbl-1,y')
        ctx.inst('bmi', 'ce_tpcs')
        ctx.inst('sta', 'mt_fx_shi')
        ctx.inst('lda', 'mt_speedrighttbl-1,y')
        ctx.inst('sta', 'mt_fx_slo')
        ctx.inst('jmp', 'ce_tpgo')
        ctx.label('ce_tpcs')
        ctx.inst('and', '#$7f')
        ctx.inst('pha')
        ctx.inst('lda', 'mt_speedrighttbl-1,y')
        ctx.inst('pha')
        ctx.inst('ldy', 'mt_chnlastnote,x')
        ctx.inst('sec')
        ctx.inst('lda', 'mt_freqtbllo+1-FIRSTNOTE,y')
        ctx.inst('sbc', 'mt_freqtbllo-FIRSTNOTE,y')
        ctx.inst('sta', 'mt_fx_slo')
        ctx.inst('lda', 'mt_freqtblhi+1-FIRSTNOTE,y')
        ctx.inst('sbc', 'mt_freqtblhi-FIRSTNOTE,y')
        ctx.inst('sta', 'mt_fx_shi')
        ctx.inst('pla')
        ctx.inst('tay')
        ctx.inst('pla')
        ctx.inst('cpy', '#0')
        ctx.inst('beq', 'ce_tpgo')
        ctx.label('ce_tpsh')
        ctx.inst('lsr', 'mt_fx_shi')
        ctx.inst('ror', 'mt_fx_slo')
        ctx.inst('dey')
        ctx.inst('bne', 'ce_tpsh')
    else:
        # NOCALCULATEDSPEED: left byte is speed high byte, no bit 7 flag.
        ctx.inst('lda', 'mt_speedrighttbl-1,y')
        ctx.inst('sta', 'mt_fx_slo')
        ctx.inst('lda', 'mt_speedlefttbl-1,y')
        ctx.inst('sta', 'mt_fx_shi')
    ctx.label('ce_tpgo')
    ctx.inst('lda', 'mt_chnnote,x')
    # SEC / SBC #FIRSTNOTE removed: FIRSTNOTE=0, so SBC #0 is no-op
    ctx.inst('tay')
    ctx.inst('sec')
    ctx.inst('lda', 'mt_chnfreqlo,x')
    ctx.inst('sbc', 'mt_freqtbllo,y')
    ctx.inst('sta', 'mt_temp1')
    ctx.inst('lda', 'mt_chnfreqhi,x')
    ctx.inst('sbc', 'mt_freqtblhi,y')
    ctx.inst('sta', 'mt_temp2')
    ctx.inst('bmi', 'ce_tpup')
    ctx.inst('sec')
    ctx.inst('lda', 'mt_temp1')
    ctx.inst('sbc', 'mt_fx_slo')
    ctx.inst('lda', 'mt_temp2')
    ctx.inst('sbc', 'mt_fx_shi')
    ctx.inst('bmi', 'ce_tpsnap')
    ctx.inst('sec')
    ctx.inst('lda', 'mt_chnfreqlo,x')
    ctx.inst('sbc', 'mt_fx_slo')
    ctx.inst('sta', 'mt_chnfreqlo,x')
    ctx.inst('lda', 'mt_chnfreqhi,x')
    ctx.inst('sbc', 'mt_fx_shi')
    ctx.inst('sta', 'mt_chnfreqhi,x')
    ctx.inst('jmp', 'ce_pulse')
    ctx.label('ce_tpup')
    ctx.inst('clc')
    ctx.inst('lda', 'mt_temp1')
    ctx.inst('adc', 'mt_fx_slo')
    ctx.inst('lda', 'mt_temp2')
    ctx.inst('adc', 'mt_fx_shi')
    ctx.inst('bpl', 'ce_tpsnap')
    ctx.inst('clc')
    ctx.inst('lda', 'mt_chnfreqlo,x')
    ctx.inst('adc', 'mt_fx_slo')
    ctx.inst('sta', 'mt_chnfreqlo,x')
    ctx.inst('lda', 'mt_chnfreqhi,x')
    ctx.inst('adc', 'mt_fx_shi')
    ctx.inst('sta', 'mt_chnfreqhi,x')
    ctx.inst('jmp', 'ce_pulse')
    ctx.label('ce_tpsnap')
    ctx.inst('lda', 'mt_chnnote,x')
    ctx.inst('sta', 'mt_chnlastnote,x')
    # SEC / SBC #FIRSTNOTE removed: FIRSTNOTE=0, SBC #0 is no-op
    ctx.inst('tay')
    ctx.inst('lda', 'mt_freqtbllo,y')
    ctx.inst('sta', 'mt_chnfreqlo,x')
    ctx.inst('lda', 'mt_freqtblhi,y')
    ctx.inst('sta', 'mt_chnfreqhi,x')
    ctx.inst('lda', '#0')
    ctx.inst('sta', 'mt_chnvibtime,x')
    # Fall through to ce_pulse (emit_pulse_table is next)


# =============================================================================
# Pulse table
# =============================================================================

def emit_pulse_table(ctx):
    ctx.section('pulse table')
    ctx.label('ce_pulse')
    if not ctx.has(PULSE_MOD):
        # No pulse — fall through to gate timer
        return

    ctx.inst('ldy', 'mt_chnpulseptr,x')
    ctx.inst('beq', 'ce_pskip')
    ctx.inst('lda', 'mt_chncounter,x')
    ctx.cmp_gate_timer()
    ctx.inst('beq', 'ce_pskip')
    ctx.inst('ora', 'mt_chnpattptr,x')
    ctx.inst('beq', 'ce_pskip')
    ctx.label('ce_pgo')
    ctx.inst('lda', 'mt_chnpulsetime,x')
    ctx.inst('bne', 'ce_pmod')
    ctx.inst('lda', 'mt_pulsetimetbl-1,y')
    ctx.inst('cmp', '#$80')
    ctx.inst('bcs', 'ce_pset')
    ctx.inst('sta', 'mt_chnpulsetime,x')
    ctx.inst('jmp', 'ce_pmod')
    ctx.label('ce_pset')
    ctx.inst('sta', 'mt_chnpulsehi,x')
    ctx.inst('lda', 'mt_pulsespdtbl-1,y')
    ctx.inst('sta', 'mt_chnpulselo,x')
    ctx.inst('jmp', 'ce_padv')
    ctx.label('ce_pmod')
    ctx.inst('lda', 'mt_pulsespdtbl-1,y')
    ctx.inst('clc')
    ctx.inst('bpl', 'ce_pup')
    ctx.inst('dec', 'mt_chnpulsehi,x')
    ctx.label('ce_pup')
    ctx.inst('adc', 'mt_chnpulselo,x')
    ctx.inst('sta', 'mt_chnpulselo,x')
    ctx.inst('bcc', 'ce_pnoc')
    ctx.inst('inc', 'mt_chnpulsehi,x')
    ctx.label('ce_pnoc')
    ctx.inst('dec', 'mt_chnpulsetime,x')
    ctx.inst('bne', 'ce_pwr')
    ctx.label('ce_padv')
    ctx.inst('lda', 'mt_pulsetimetbl,y')
    ctx.inst('cmp', '#LOOPTBL')
    ctx.inst('bne', 'ce_pnj')
    ctx.inst('lda', 'mt_pulsespdtbl,y')
    ctx.inst('sta', 'mt_chnpulseptr,x')
    ctx.inst('jmp', 'ce_pwr')
    ctx.label('ce_pnj')
    ctx.inst('iny')
    ctx.inst('tya')
    ctx.inst('sta', 'mt_chnpulseptr,x')
    ctx.label('ce_pwr')
    if ctx.has(UNBUFFERED_WRITES):
        ctx.inst('lda', 'mt_chnpulselo,x')
        ctx.inst('sta', 'SIDBASE+2,x')
        ctx.inst('lda', 'mt_chnpulsehi,x')
        ctx.inst('sta', 'SIDBASE+3,x')
    ctx.label('ce_pskip')


# =============================================================================
# Gate timer check
# =============================================================================

def emit_gate_timer(ctx):
    ctx.section('gate timer')
    ctx.inst('lda', 'mt_chncounter,x')
    ctx.cmp_gate_timer()
    ctx.inst('beq', 'ce_getnote')
    ctx.inst('jmp', 'ce_ldregs')


# =============================================================================
# Pattern reader
# =============================================================================

def emit_pattern_reader(ctx):
    ctx.section('pattern reader')
    ctx.label('ce_getnote')
    ctx.inst('ldy', 'mt_chnpattnum,x')
    ctx.inst('lda', 'mt_patttbllo,y')
    ctx.inst('sta', 'mt_temp1')
    ctx.inst('lda', 'mt_patttblhi,y')
    ctx.inst('sta', 'mt_temp2')
    ctx.inst('ldy', 'mt_chnpattptr,x')
    # Packed rest continuation
    if ctx.has(HAS_PACKED_REST):
        ctx.inst('lda', 'mt_chnpkrest,x')
        ctx.inst('beq', 'ce_nopkr')
        ctx.inst('jmp', 'ce_pkrc')
        ctx.label('ce_nopkr')
    # Read byte
    ctx.inst('lda', '(mt_temp1),y')
    if ctx.has(HAS_PACKED_REST):
        ctx.inst('cmp', '#FPKREST')
        ctx.inst('bcs', 'ce_pkrn')
    ctx.inst('cmp', '#NOTE')
    ctx.inst('bcs', 'ce_note')
    ctx.inst('cmp', '#FX')
    ctx.inst('bcs', 'ce_fx')
    # Instrument change
    ctx.inst('sta', 'mt_chninstr,x')
    ctx.inst('iny')
    ctx.inst('lda', '(mt_temp1),y')
    ctx.inst('cmp', '#NOTE')
    ctx.inst('bcs', 'ce_note')
    # FX — Covfefe trick: CMP #$50 sets carry, AND #$0F preserves it,
    # BCS later uses it for FXONLY check. No PHA/PLA needed.
    ctx.label('ce_fx')
    ctx.inst('cmp', '#FXONLY', comment='carry set if FXONLY ($50+)')
    ctx.inst('and', '#$0f', comment='AND preserves carry')
    ctx.inst('sta', 'mt_chnnewfx,x')
    ctx.inst('beq', 'ce_fxnp')
    ctx.inst('iny')
    ctx.inst('lda', '(mt_temp1),y')
    ctx.inst('sta', 'mt_chnnewparam,x')
    ctx.label('ce_fxnp')
    ctx.inst('bcs', 'ce_rest', comment='FXONLY: carry still set from CMP')
    ctx.inst('iny')
    ctx.inst('lda', '(mt_temp1),y')
    # Note
    ctx.label('ce_note')
    ctx.inst('cmp', '#REST')
    ctx.inst('beq', 'ce_rest')
    if ctx.has(HAS_KEYOFF) or ctx.has(HAS_KEYON):
        ctx.inst('cmp', '#KEYOFF')
        if ctx.has(HAS_KEYOFF) and ctx.has(HAS_KEYON):
            ctx.inst('bcs', 'ce_koff')  # KEYOFF=$BE, KEYON=$BF: both >= $BE
        elif ctx.has(HAS_KEYOFF):
            ctx.inst('beq', 'ce_koff')
        else:
            # Only KEYON, no KEYOFF
            ctx.inst('cmp', '#KEYON')
            ctx.inst('beq', 'ce_koff')
    # Normal note
    if ctx.has(ORDERLIST_TRANS):
        ctx.inst('clc')
        ctx.inst('adc', 'mt_chntrans,x')
    ctx.inst('sta', 'mt_chnnewnote,x')
    # Toneporta check — skip HR, go straight to rest (like original GT2).
    # mt_chnnewnote stays set; tick-0 emit_new_note_init handles it.
    if ctx.has(TONEPORTA):
        ctx.inst('lda', 'mt_chnnewfx,x')
        ctx.inst('cmp', '#3')
        ctx.inst('beq', 'ce_rest')
    # Legato check
    if ctx.has(LEGATO_INSTR):
        ctx.inst('lda', 'mt_chninstr,x')
        ctx.inst('cmp', '#FIRSTLEGATOINSTR')
        ctx.inst('bcs', 'ce_rest')
    # No-HR check
    if ctx.has(NOHR_INSTR):
        if not ctx.has(LEGATO_INSTR):
            ctx.inst('lda', 'mt_chninstr,x')
        ctx.inst('cmp', '#FIRSTNOHRINSTR')
        ctx.inst('bcs', 'ce_skhr')
    # Hard restart
    if ctx.has(ADSR_AD_FIRST):
        ctx.inst('lda', '#ADPARAM')
        ctx.inst('sta', 'mt_chnad,x')
        ctx.inst('lda', '#SRPARAM')
        ctx.inst('sta', 'mt_chnsr,x')
    else:
        ctx.inst('lda', '#SRPARAM')
        ctx.inst('sta', 'mt_chnsr,x')
        ctx.inst('lda', '#ADPARAM')
        ctx.inst('sta', 'mt_chnad,x')
    if ctx.has(UNBUFFERED_WRITES):
        ctx.inst('lda', 'mt_chnsr,x')
        ctx.inst('sta', 'SIDBASE+6,x')
        ctx.inst('lda', 'mt_chnad,x')
        ctx.inst('sta', 'SIDBASE+5,x')
    ctx.label('ce_skhr')
    ctx.inst('lda', '#$fe')
    ctx.inst('sta', 'mt_chngate,x')
    ctx.inst('jmp', 'ce_rest')
    # Keyoff/keyon
    if ctx.has(HAS_KEYOFF) or ctx.has(HAS_KEYON):
        ctx.label('ce_koff')
        ctx.inst('ora', '#$f0')
        ctx.inst('sta', 'mt_chngate,x')
        ctx.inst('jmp', 'ce_rest')
    # Packed rest
    if ctx.has(HAS_PACKED_REST):
        ctx.label('ce_pkrn')
        ctx.inst('adc', '#0')
        ctx.inst('beq', 'ce_rest')
        ctx.inst('sta', 'mt_chnpkrest,x')
        ctx.inst('jmp', 'ce_ldregs')
        ctx.label('ce_pkrc')
        ctx.inst('clc')
        ctx.inst('adc', '#1')
        ctx.inst('sta', 'mt_chnpkrest,x')
        ctx.inst('beq', 'ce_rest')
        ctx.inst('jmp', 'ce_ldregs')

    # Rest — Covfefe trick: BEQ skips TYA when byte is $00 (ENDPATT),
    # so A=0 falls through to STA (stores 0 = reset pattptr)
    ctx.label('ce_rest')
    ctx.inst('lda', '#0')
    if ctx.has(HAS_PACKED_REST):
        ctx.inst('sta', 'mt_chnpkrest,x')
    ctx.inst('iny')
    ctx.inst('lda', '(mt_temp1),y')
    ctx.inst('beq', 'ce_pattend', comment='ENDPATT: A=0, skip TYA')
    ctx.inst('tya')
    ctx.label('ce_pattend')
    ctx.inst('sta', 'mt_chnpattptr,x')
    # Fall through to ce_ldregs


# =============================================================================
# Register writes
# =============================================================================

def emit_register_writes(ctx):
    ctx.section('register writes')
    ctx.label('ce_ldregs')
    if not ctx.has(UNBUFFERED_WRITES):
        if ctx.has(LOADREGS_AD_FIRST):
            ctx.inst('lda', 'mt_chnad,x')
            ctx.inst('sta', 'SIDBASE+5,x')
            ctx.inst('lda', 'mt_chnsr,x')
            ctx.inst('sta', 'SIDBASE+6,x')
            ctx.inst('lda', 'mt_chnpulselo,x')
            ctx.inst('sta', 'SIDBASE+2,x')
            ctx.inst('lda', 'mt_chnpulsehi,x')
            ctx.inst('sta', 'SIDBASE+3,x')
        else:
            ctx.inst('lda', 'mt_chnpulselo,x')
            ctx.inst('sta', 'SIDBASE+2,x')
            ctx.inst('lda', 'mt_chnpulsehi,x')
            ctx.inst('sta', 'SIDBASE+3,x')
            ctx.inst('lda', 'mt_chnsr,x')
            ctx.inst('sta', 'SIDBASE+6,x')
            ctx.inst('lda', 'mt_chnad,x')
            ctx.inst('sta', 'SIDBASE+5,x')
    if ctx.has(FREQ_SLIDE):
        # Apply per-frame freq_slide before writing to SID.
        # mt_chnfreqslide is a signed delta added to freq_hi each frame.
        ctx.inst('lda', 'mt_chnfreqslide,x')
        ctx.inst('beq', 'ce_noslide')
        ctx.inst('clc')
        ctx.inst('adc', 'mt_chnfreqhi,x')
        ctx.inst('sta', 'mt_chnfreqhi,x')
        ctx.label('ce_noslide')
    ctx.inst('lda', 'mt_chnfreqlo,x')
    ctx.inst('sta', 'SIDBASE,x')
    ctx.inst('lda', 'mt_chnfreqhi,x')
    ctx.inst('sta', 'SIDBASE+1,x')
    ctx.label('ce_ldwav')
    ctx.inst('lda', 'mt_chnwave,x')
    ctx.inst('and', 'mt_chngate,x')
    ctx.inst('sta', 'SIDBASE+4,x')
    ctx.inst('rts')


# =============================================================================
# Tick-0 path
# =============================================================================

def emit_tick0_path(ctx):
    ctx.section('tick-0 path')
    ctx.label('ce_t0')
    ctx.inst('lda', 'mt_chnpattptr,x')
    ctx.inst('bne', 'ce_nonew')
    # Orderlist reader
    ctx.inst('ldy', 'mt_chnsongnum,x')
    ctx.inst('lda', 'mt_songtbllo,y')
    ctx.inst('sta', 'mt_temp1')
    ctx.inst('lda', 'mt_songtblhi,y')
    ctx.inst('sta', 'mt_temp2')
    ctx.inst('ldy', 'mt_chnsongptr,x')
    ctx.inst('lda', '(mt_temp1),y')
    # Loop detection
    ctx.inst('cmp', '#LOOPSONG')
    ctx.inst('bne', 'ce_nolp')
    ctx.inst('iny')
    ctx.inst('lda', '(mt_temp1),y')
    ctx.inst('tay')
    ctx.inst('lda', '(mt_temp1),y')
    ctx.label('ce_nolp')
    # Transpose
    if ctx.has(ORDERLIST_TRANS):
        ctx.inst('cmp', '#TRANSDN')
        ctx.inst('bcc', 'ce_notr')
        ctx.inst('sec')
        ctx.inst('sbc', '#TRANS')
        ctx.inst('sta', 'mt_chntrans,x')
        ctx.inst('iny')
        ctx.inst('lda', '(mt_temp1),y')
        ctx.label('ce_notr')
    # Repeat
    if ctx.has(ORDERLIST_REPEAT):
        ctx.inst('cmp', '#REPEAT')
        ctx.inst('bcc', 'ce_norep')
        ctx.inst('sec')
        ctx.inst('sbc', '#REPEAT')
        ctx.inst('sta', 'mt_wv_optr')
        ctx.inst('inc', 'mt_chnrepeat,x')
        ctx.inst('lda', 'mt_chnrepeat,x')
        ctx.inst('cmp', 'mt_wv_optr')
        ctx.inst('bne', 'ce_nonew')
        ctx.inst('lda', '#0')
        ctx.inst('sta', 'mt_chnrepeat,x')
        ctx.inst('iny')
        ctx.inst('lda', '(mt_temp1),y')
        ctx.label('ce_norep')
    # Store pattern
    ctx.inst('sta', 'mt_chnpattnum,x')
    ctx.inst('iny')
    ctx.inst('tya')
    ctx.inst('sta', 'mt_chnsongptr,x')
    ctx.label('ce_nonew')
    # Gate timer
    ctx.inst('ldy', 'mt_chninstr,x')
    ctx.inst('lda', 'mt_insgatetimer-1,y')
    ctx.inst('sta', 'mt_chngatetimer,x')
    # New note?
    ctx.inst('lda', 'mt_chnnewnote,x')
    ctx.inst('bne', 'ce_newn')
    ctx.inst('beq', 'ce_nnn', comment='unconditional (newnote=0)')


def emit_new_note_init(ctx):
    ctx.section('new note init')
    ctx.label('ce_newn')
    ctx.inst('sec')
    ctx.inst('sbc', '#NOTE')
    ctx.inst('sta', 'mt_chnnote,x')
    ctx.inst('lda', '#0')
    if ctx.has(EFFECTS):
        ctx.inst('sta', 'mt_chnfx,x')
    ctx.inst('sta', 'mt_chnnewnote,x')
    # Y = instrument (from gate timer load above)
    if ctx.has(VIBRATO):
        ctx.inst('lda', 'mt_insvibdelay-1,y')
        ctx.inst('sta', 'mt_chnvibdelay,x')
        ctx.inst('lda', 'mt_insvibparam-1,y')
        ctx.inst('sta', 'mt_chnparam,x')
    # Toneporta skip
    if ctx.has(TONEPORTA):
        ctx.inst('lda', 'mt_chnnewfx,x')
        ctx.inst('cmp', '#3')
        ctx.inst('beq', 'ce_nnn')
    # First-frame waveform (Y still = instrument)
    ctx.inst('lda', 'mt_insfirstwave-1,y')
    ctx.inst('beq', 'ce_skfw')
    ctx.inst('cmp', '#$fe')
    ctx.inst('bcs', 'ce_skfw')
    ctx.inst('sta', 'mt_chnwave,x')
    ctx.label('ce_skfw')
    ctx.inst('lda', '#$ff')
    ctx.inst('sta', 'mt_chngate,x')
    # Pulse ptr (Y still = instrument)
    if ctx.has(PULSE_MOD):
        ctx.inst('lda', 'mt_inspulseptr-1,y')
        ctx.inst('beq', 'ce_npi')
        ctx.inst('sta', 'mt_chnpulseptr,x')
        ctx.inst('lda', '#0')
        ctx.inst('sta', 'mt_chnpulsetime,x')
        ctx.label('ce_npi')
    # Filter ptr (Y still = instrument)
    if ctx.has(FILTER):
        ctx.inst('lda', 'mt_insfiltptr-1,y')
        ctx.inst('beq', 'ce_nfi')
        ctx.inst('sta', 'mt_g_fstep+1')
        ctx.inst('lda', '#0')
        ctx.inst('sta', 'mt_g_ftime+1')
        ctx.label('ce_nfi')
    # Wave ptr (Y still = instrument)
    ctx.inst('lda', 'mt_inswaveptr-1,y')
    ctx.inst('sta', 'mt_chnwaveptr,x')
    ctx.inst('lda', '#0')
    ctx.inst('sta', 'mt_chnwavetime,x')
    # ADSR (Y still = instrument)
    if ctx.has(ADSR_AD_FIRST):
        ctx.inst('lda', 'mt_insad-1,y')
        ctx.inst('sta', 'mt_chnad,x')
        ctx.inst('lda', 'mt_inssr-1,y')
        ctx.inst('sta', 'mt_chnsr,x')
    else:
        ctx.inst('lda', 'mt_inssr-1,y')
        ctx.inst('sta', 'mt_chnsr,x')
        ctx.inst('lda', 'mt_insad-1,y')
        ctx.inst('sta', 'mt_chnad,x')
    if ctx.has(UNBUFFERED_WRITES):
        ctx.inst('lda', 'mt_chnsr,x')
        ctx.inst('sta', 'SIDBASE+6,x')
        ctx.inst('lda', 'mt_chnad,x')
        ctx.inst('sta', 'SIDBASE+5,x')
    # Tick-0 effect
    if ctx.has(TICK0_FX):
        ctx.inst('jsr', 'mt_t0_dispatch')
    # Register writes
    if ctx.has(UNBUFFERED_WRITES):
        ctx.inst('jmp', 'ce_ldwav')
    elif ctx.has(NEWNOTE_ALL_REGS):
        ctx.inst('jmp', 'ce_ldregs')
    else:
        ctx.inst('jmp', 'ce_ldwav')

    # No new note path
    ctx.label('ce_nnn')
    if ctx.has(TICK0_FX):
        ctx.inst('jsr', 'mt_t0_dispatch')
    ctx.inst('jmp', 'ce_wave')


# =============================================================================
# Tick-0 effect dispatch
# =============================================================================

def emit_tick0_dispatch(ctx):
    ctx.section('tick-0 dispatch')
    # Wave command entry: A=param, Y=fx already set by caller.
    # JMP past the memory loads so we don't clobber mt_chnnewfx/param.
    if ctx.has(WAVE_CMD) and ctx.has(TICK0_FX):
        ctx.label('mt_t0_wave')
        ctx.inst('jmp', 'mt_t0_body')
    ctx.label('mt_t0_dispatch')
    ctx.inst('lda', 'mt_chnnewparam,x')
    ctx.inst('ldy', 'mt_chnnewfx,x')
    ctx.label('mt_t0_body')

    # FX 0
    if ctx.has(VIBRATO):
        ctx.inst('beq', 'mt_t0_fx0')
    else:
        ctx.inst('beq', 'mt_t0_rts')

    # FX 1-4
    if ctx.has(EFFECTS):
        ctx.inst('cpy', '#5')
        ctx.inst('bcc', 'mt_t0_fx14')
        if ctx.has(SET_AD):
            ctx.inst('beq', 'mt_t0_fx5')

    # FX 5-F: CMP chain for active effects
    has_fxf = ctx.has(SET_TEMPO) or ctx.has(FUNKTEMPO)
    fx_checks = [
        (6, SET_SR), (7, SET_WAVE), (8, SET_WAVEPTR),
        (9, SET_PULSEPTR), (0xa, SET_FILTPTR), (0xb, SET_FILTCTRL),
        (0xc, SET_FILTCUT), (0xd, SET_MASTERVOL), (0xe, FUNKTEMPO),
    ]
    for num, flag in fx_checks:
        if ctx.has(flag):
            ctx.inst('cpy', f'#${num:x}')
            ctx.inst('beq', f'mt_t0_fx{num:x}')

    # FX F: set tempo — also needed if FUNKTEMPO uses it
    if has_fxf:
        ctx.label('mt_t0_fxf')
        ctx.inst('cmp', '#$80')
        ctx.inst('bcs', 'mt_t0fc')
        ctx.inst('sta', 'mt_chntempo')
        ctx.inst('sta', 'mt_chntempo+7')
        ctx.inst('sta', 'mt_chntempo+14')
        ctx.inst('rts')
        ctx.label('mt_t0fc')
        ctx.inst('and', '#$7f')
        ctx.inst('sta', 'mt_chntempo,x')
        ctx.inst('rts')
    else:
        ctx.inst('rts')

    # FX 0 handler
    if ctx.has(VIBRATO):
        ctx.label('mt_t0_fx0')
        ctx.inst('ldy', 'mt_chninstr,x')
        ctx.inst('lda', 'mt_insvibparam-1,y')
        if ctx.has(VIBRATO_PARAM_FIX):
            ctx.inst('bne', 'mt_t0_fx34')
            ctx.inst('lda', '#0')
    if ctx.has(EFFECTS):
        ctx.label('mt_t0_fx14')
    ctx.label('mt_t0_fx34')
    ctx.inst('sta', 'mt_chnparam,x')
    ctx.inst('lda', 'mt_chnnewfx,x')
    ctx.inst('sta', 'mt_chnfx,x')
    ctx.label('mt_t0_rts')
    ctx.inst('rts')

    # Individual handlers
    if ctx.has(SET_AD):
        ctx.label('mt_t0_fx5')
        ctx.inst('sta', 'mt_chnad,x')
        if ctx.has(UNBUFFERED_WRITES):
            ctx.inst('sta', 'SIDBASE+5,x')  # BW=0: write directly to SID
        ctx.inst('rts')
    if ctx.has(SET_SR):
        ctx.label('mt_t0_fx6')
        ctx.inst('sta', 'mt_chnsr,x')
        if ctx.has(UNBUFFERED_WRITES):
            ctx.inst('sta', 'SIDBASE+6,x')  # BW=0: write directly to SID
        ctx.inst('rts')
    if ctx.has(SET_WAVE):
        ctx.label('mt_t0_fx7')
        ctx.inst('sta', 'mt_chnwave,x')
        ctx.inst('rts')
    if ctx.has(SET_WAVEPTR):
        ctx.label('mt_t0_fx8')
        ctx.inst('sta', 'mt_chnwaveptr,x')
        ctx.inst('lda', '#0')
        ctx.inst('sta', 'mt_chnwavetime,x')
        ctx.inst('rts')
    if ctx.has(SET_PULSEPTR):
        ctx.label('mt_t0_fx9')
        ctx.inst('sta', 'mt_chnpulseptr,x')
        ctx.inst('lda', '#0')
        ctx.inst('sta', 'mt_chnpulsetime,x')
        ctx.inst('rts')
    if ctx.has(SET_FILTPTR):
        ctx.label('mt_t0_fxa')
        ctx.inst('sta', 'mt_g_fstep+1')
        ctx.inst('lda', '#0')
        ctx.inst('sta', 'mt_g_ftime+1')
        ctx.inst('rts')
    if ctx.has(SET_FILTCTRL):
        ctx.label('mt_t0_fxb')
        ctx.inst('sta', 'mt_g_fctrl+1')
        ctx.inst('cmp', '#0')
        ctx.inst('bne', 'mt_t0bx')
        ctx.inst('sta', 'mt_g_fstep+1')
        ctx.label('mt_t0bx')
        ctx.inst('rts')
    if ctx.has(SET_FILTCUT):
        ctx.label('mt_t0_fxc')
        ctx.inst('sta', 'mt_g_fcut+1')
        ctx.inst('rts')
    if ctx.has(SET_MASTERVOL):
        ctx.label('mt_t0_fxd')
        ctx.inst('sta', 'mt_g_mvol+1')
        ctx.inst('rts')
    if ctx.has(FUNKTEMPO):
        ctx.label('mt_t0_fxe')
        ctx.inst('tay')
        ctx.inst('lda', 'mt_speedlefttbl-1,y')
        ctx.inst('sta', 'mt_funktbl')
        ctx.inst('lda', 'mt_speedrighttbl-1,y')
        ctx.inst('sta', 'mt_funktbl+1')
        ctx.inst('lda', '#0')
        ctx.inst('beq', 'mt_t0_fxf')


# =============================================================================
# Variables
# =============================================================================

def emit_variables(ctx):
    ctx.section('variables')
    ctx.label('mt_wv_optr')
    ctx.data('.byte', '0')
    if ctx.has(WAVE_CMD):
        ctx.label('mt_wv_left')
        ctx.data('.byte', '0')
        ctx.label('mt_wv_param')
        ctx.data('.byte', '0')
    else:
        ctx.equate('mt_wv_left', 'mt_wv_optr')
        ctx.equate('mt_wv_param', 'mt_wv_optr')
    if ctx.has(EFFECTS):
        ctx.label('mt_fx_spd')
        ctx.data('.byte', '0')
        ctx.label('mt_fx_shift')
        ctx.data('.byte', '0')
    if ctx.has(TONEPORTA):
        ctx.label('mt_fx_slo')
        ctx.data('.byte', '0')
        ctx.label('mt_fx_shi')
        ctx.data('.byte', '0')
    if ctx.has(FUNKTEMPO):
        ctx.label('mt_funktbl')
        ctx.data('.byte', '8, 5')
    ctx.blank()
    # Channel variables (5 groups, stride 7)
    ctx.label('mt_chnsongptr')
    ctx.data('.dsb', '21,0')
    ctx.equate('mt_chntrans', 'mt_chnsongptr+1')
    ctx.equate('mt_chnrepeat', 'mt_chnsongptr+2')
    ctx.equate('mt_chnpattptr', 'mt_chnsongptr+3')
    ctx.equate('mt_chnpkrest', 'mt_chnsongptr+4')
    ctx.equate('mt_chnnewfx', 'mt_chnsongptr+5')
    ctx.equate('mt_chnnewparam', 'mt_chnsongptr+6')
    ctx.label('mt_chnfx')
    ctx.data('.dsb', '21,0')
    ctx.equate('mt_chnparam', 'mt_chnfx+1')
    ctx.equate('mt_chnnewnote', 'mt_chnfx+2')
    ctx.equate('mt_chnwaveptr', 'mt_chnfx+3')
    ctx.equate('mt_chnwave', 'mt_chnfx+4')
    ctx.equate('mt_chnpulseptr', 'mt_chnfx+5')
    ctx.equate('mt_chnpulsetime', 'mt_chnfx+6')
    ctx.label('mt_chnsongnum')
    ctx.data('.dsb', '21,0')
    ctx.equate('mt_chnpattnum', 'mt_chnsongnum+1')
    ctx.equate('mt_chntempo', 'mt_chnsongnum+2')
    ctx.equate('mt_chncounter', 'mt_chnsongnum+3')
    ctx.equate('mt_chnnote', 'mt_chnsongnum+4')
    ctx.equate('mt_chninstr', 'mt_chnsongnum+5')
    ctx.equate('mt_chngate', 'mt_chnsongnum+6')
    ctx.label('mt_chnvibtime')
    ctx.data('.dsb', '21,0')
    ctx.equate('mt_chnvibdelay', 'mt_chnvibtime+1')
    ctx.equate('mt_chnwavetime', 'mt_chnvibtime+2')
    ctx.equate('mt_chnfreqlo', 'mt_chnvibtime+3')
    ctx.equate('mt_chnfreqhi', 'mt_chnvibtime+4')
    ctx.equate('mt_chnpulselo', 'mt_chnvibtime+5')
    ctx.equate('mt_chnpulsehi', 'mt_chnvibtime+6')
    ctx.label('mt_chnad')
    ctx.data('.dsb', '21,0')
    ctx.equate('mt_chnsr', 'mt_chnad+1')
    ctx.equate('mt_chngatetimer', 'mt_chnad+2')
    ctx.equate('mt_chnlastnote', 'mt_chnad+3')
    if ctx.has(FREQ_SLIDE):
        ctx.equate('mt_chnfreqslide', 'mt_chnad+4')

    # Dummy data labels for standalone assembly
    ctx.blank()
    ctx.emit('#ifndef mt_songtbllo')
    ctx.label('mt_dummy')
    ctx.data('.byte', '0')
    for lbl in ['mt_songtbllo', 'mt_songtblhi', 'mt_patttbllo', 'mt_patttblhi',
                'mt_insad', 'mt_inssr', 'mt_inswaveptr', 'mt_inspulseptr',
                'mt_insfiltptr', 'mt_insvibparam', 'mt_insvibdelay',
                'mt_insgatetimer', 'mt_insfirstwave', 'mt_wavetbl', 'mt_notetbl',
                'mt_pulsetimetbl', 'mt_pulsespdtbl', 'mt_filttimetbl',
                'mt_filtspdtbl', 'mt_speedlefttbl', 'mt_speedrighttbl',
                'mt_freqtbllo', 'mt_freqtblhi']:
        ctx.equate(lbl, 'mt_dummy')
    ctx.emit('#endif')


# =============================================================================
# Test
# =============================================================================

if __name__ == '__main__':
    import sys
    import os
    import json
    import subprocess
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from gt2_to_usf import gt2_to_usf

    with open('src/player/regression_registry.json') as f:
        reg = json.load(f)

    xa = 'tools/xa65/xa/xa'

    for name_frag in ['Covfefe', 'Boo', 'Ghost01', 'Shovel_Funk', 'Blast-A-Load']:
        entry = [e for e in reg if name_frag in e['path']]
        if not entry:
            continue
        path = entry[0]['path']
        if not os.path.exists(path):
            continue
        song = gt2_to_usf(path)
        if not song:
            continue
        src = generate_player(song)
        with open('/tmp/v2_test.s', 'w') as f:
            f.write(src)
        r = subprocess.run([xa, '-XMASM', '-o', '/tmp/v2_test.bin', '/tmp/v2_test.s'],
                          capture_output=True, text=True)
        if r.returncode == 0:
            size = os.path.getsize('/tmp/v2_test.bin')
            features = detect_features(song)
            print(f'{os.path.basename(path):30s} {size:4d} bytes  ({len(features)} features)')
        else:
            err = r.stderr.strip().split('\n')[0][:60]
            print(f'{os.path.basename(path):30s} FAILED: {err}')
