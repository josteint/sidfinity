"""Cluster B engine variant emit (Counterforce-shape: 15-byte program).

Cluster B SIDs (Jay_Derrett family):
- Direct dispatch: Counterforce, Destruct
- IRQ dispatch: Osmium, Thundercross, Trigger_Happy
- Trampoline: Road_Warrior
- Trampoline_indirect: Stratton

Cluster B's slab layout (24 bytes within a stride-26 slab):

  +$00  flag           (bit 0 enables LFO toggle; NH uses bit 7)
  +$01  PW hi
  +$02  phase 0 limit
  +$03  phase 0 lo delta
  +$04  (unused/reserved)
  +$05  phase 0 direction (0=ADD, non-zero=SUB)
  +$06  phase 1 direction
  +$07  phase 1 max
  +$08  phase 1 min
  +$09  phase 1 lo delta
  +$0A  (unused/reserved)
  +$0B  CTRL byte (gate-on waveform)
  +$0C  AD
  +$0D  SR
  +$0E  gate-off CTRL (waveform with gate cleared)
  +$0F..$13  (unused/reserved)
  +$14  off-slide freq lo (= freq for THIS note)
  +$15  off-slide freq hi
  +$16  normal freq lo (= freq for note + $10 — typically octave shift)
  +$17  normal freq hi

The inst loader copies the 15-byte program to slab offsets $00..$0E
then COMPUTES the four freq cells from the NOTE byte:
  - $14/$15 from freq_table[note]
  - $16/$17 from freq_table[note + $10]

The modulation block outputs:
  - Freq: LFO-toggle between off-slide ($14/$15) and normal ($16/$17)
    based on (flag bit 0) AND (frame_counter bit 0). bit-0 of flag = 0
    means "always off-slide" (no vibrato).
  - PW hi: from slab offset $01
  - PW lo: from external voice_pwm_lo accumulator
  - CTRL: voice_state+$0B | voice_state+$0E

No slide-update for freq — freq stays constant between NOTE events.
PWM update runs every frame.
"""

from __future__ import annotations
from pathlib import Path


def emit_asm_cluster_b(data, load_addr: int, quirks) -> str:
    """Emit clean xa65 asm for a Cluster B (CF-shape) Jay_Derrett SID.

    `data` is the ExtractedData from build.py's extract_data().
    `quirks` is an EngineQuirks bag from build.py.

    Slot offsets per cluster B's slab layout (see module docstring)."""
    lines: list[str] = [f'* = ${load_addr:04X}']
    lines += [
        '',
        '; ============================================================',
        '; Jay_Derrett Cluster B engine (Counterforce-shape)',
        '; ============================================================',
        '',
        '; ZP: $F2/$F3 pattern ptr',
        '',
        'init_entry:',
        '    jmp init_code',
        'play_entry:',
        '    jmp play_code',
        '',
    ]

    # ----- init code -----
    lines += [
        'init_code:',
        '    lda #<voice0_pattern',
        '    sta voice_ptrs',
        '    lda #>voice0_pattern',
        '    sta voice_ptrs+1',
        '    lda #<voice1_pattern',
        '    sta voice_ptrs+2',
        '    lda #>voice1_pattern',
        '    sta voice_ptrs+3',
        '    lda #<voice2_pattern',
        '    sta voice_ptrs+4',
        '    lda #>voice2_pattern',
        '    sta voice_ptrs+5',
        f'    lda #${quirks.initial_smc:02X}',
        '    sta self_mod_counter',
        f'    lda #${quirks.initial_tempo:02X}',
        '    sta tempo_counter',
        f'    lda #${quirks.initial_tempo_reload:02X}',
        '    sta tempo_reload',
        f'    lda #${quirks.initial_master_vol:02X}',
        '    sta $d418',
        f'    lda #${quirks.initial_dur_counters[0]:02X}',
        '    sta dur_counters',
        f'    lda #${quirks.initial_dur_counters[1]:02X}',
        '    sta dur_counters+1',
        f'    lda #${quirks.initial_dur_counters[2]:02X}',
        '    sta dur_counters+2',
    ]
    pwm = quirks.initial_pwm_lo
    for v, val in enumerate(pwm):
        if val:
            lines += [f'    lda #${val:02X}', f'    sta voice_pwm_lo+{v}']
    phase = quirks.initial_pwm_phase
    for v, val in enumerate(phase):
        if val:
            lines += [f'    lda #${val:02X}', f'    sta voice_pwm_phase+{v}']
    cur_inst = quirks.initial_cur_inst
    for v, val in enumerate(cur_inst):
        if val:
            lines += [f'    lda #${val:02X}', f'    sta cur_inst+{v}']
    cur_ctrl = quirks.initial_cur_ctrl
    for v, val in enumerate(cur_ctrl):
        if val:
            lines += [f'    lda #${val:02X}', f'    sta cur_ctrl+{v}']
    fc = quirks.initial_frame_counter
    if fc:
        lines += [f'    lda #${fc:02X}', '    sta frame_counter']
    if data.init_voice_state is not None and any(data.init_voice_state):
        n = len(data.init_voice_state)
        lines += [
            f'    ldx #${n-1:02X}',
            'init_copy_state_loop:',
            '    lda init_voice_state_data,x',
            '    sta voice_state,x',
            '    dex',
            '    bpl init_copy_state_loop',
        ]
    lines += [
        '    rts',
        '',
    ]
    if data.init_voice_state is not None and any(data.init_voice_state):
        lines.append('init_voice_state_data:')
        for i in range(0, len(data.init_voice_state), 16):
            chunk = data.init_voice_state[i:i + 16]
            lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
        lines.append('')

    # ----- play code -----
    lines += [
        'play_code:',
        '    inc frame_counter',
        '    dec tempo_counter',
        '    bne play_modulation',
        '    ldx #$00',
        '    jsr process_voice',
        '    ldx #$01',
        '    jsr process_voice',
        '    ldx #$02',
        '    jsr process_voice',
        '    lda tempo_reload',
        '    sta tempo_counter',
        'play_modulation:',
        '    ldx #$00',
        '    jsr modulate_voice',
        '    ldx #$01',
        '    jsr modulate_voice',
        '    ldx #$02',
        '    jsr modulate_voice',
        '    rts',
        '',
    ]

    # ----- process_voice — set up $F2/F3 + cur_voice/cur_voice_y -----
    lines += [
        'process_voice:',
        '    stx cur_voice',
        '    txa',
        '    asl',
        '    tay',
        '    lda voice_ptrs,y',
        '    sta $f2',
        '    lda voice_ptrs+1,y',
        '    sta $f3',
        '    ldx cur_voice',
        '    lda voice_y_table,x',
        '    sta cur_voice_y',
        '    jsr proc_note',
        '    ldx cur_voice',
        '    txa',
        '    asl',
        '    tay',
        '    lda $f2',
        '    sta voice_ptrs,y',
        '    lda $f3',
        '    sta voice_ptrs+1,y',
        '    rts',
        '',
    ]

    # ----- proc_note (byte vocab identical to Cluster A) -----
    lines += [
        'proc_note:',
        '    ldx cur_voice',
        '    dec dur_counters,x',
        '    beq pn_proceed',
        '    rts',
        'pn_proceed:',
        '    inc dur_counters,x',
        'pn_read:',
        '    ldy #$00',
        '    lda ($f2),y',
        '    pha',
        '    and #$f0',
        '    cmp #$e0',
        '    beq pn_ex',
        '    cmp #$d0',
        '    beq pn_dx',
        '    pla',
        '    cmp #$80',
        '    beq pn_gate_off',
        '    cmp #$81',
        '    beq pn_skip',
        '    cmp #$82',
        '    beq pn_set_dur',
        '    pha',
        '    and #$f0',
        '    cmp #$b0',
        '    beq pn_bx',
        '    cmp #$c0',
        '    beq pn_cx',
        '    pla',
        '    jmp pn_note',
        '',
        'pn_ex:',
        '    pla',
        '    cmp self_mod_counter',
        '    beq pn_ex_match',
        '    jmp pn_advance_recurse',
        'pn_ex_match:',
        '    and #$0f',
        '    asl',
        '    tay',
        '    lda sub_jump_table,y',
        '    sta $f2',
        '    lda sub_jump_table+1,y',
        '    sta $f3',
        '    inc self_mod_counter',
        '    lda self_mod_counter',
        f'    cmp #${quirks.smc_wrap:02X}',
        '    bne pn_read',
        f'    lda #${quirks.initial_smc:02X}',
        '    sta self_mod_counter',
        '    lda #$00',
        '    sta voice_state+$0B+$34',     # CF: V3 CTRL slot (offset $0B in slab)
        '    sta voice_state+$0E+$34',     # CF: V3 gate-off slot (offset $0E)
        '    jmp pn_read',
        '',
        'pn_dx:',
        '    pla',
        '    and #$0f',
        '    sta cur_inst,x',
        '    inc cur_inst,x',
        '    jmp pn_advance_recurse',
        '',
        'pn_gate_off:',
        '    ldy cur_voice_y',
        '    lda voice_state+$0B,y',       # CF: CTRL at +$0B
        '    sta voice_state+$0E,y',       # CF: gate-off at +$0E
        '    jmp pn_advance_rts',
        '',
        'pn_skip:',
        '    jmp pn_advance_rts',
        '',
        'pn_set_dur:',
        '    inc $f2',
        '    bne pn_sd_no_inc_hi',
        '    inc $f3',
        'pn_sd_no_inc_hi:',
        '    ldy #$00',
        '    lda ($f2),y',
        '    sta dur_counters,x',
    ]
    if quirks.set_dur_clears_v3:
        lines += [
            '    lda #$00',
            '    sta voice_state+$0B+$34',
            '    sta voice_state+$0E+$34',
        ]
    lines += [
        '    jmp pn_advance_rts',
        '',
        'pn_bx:',
        '    pla',
        '    and #$0f',
        '    sta tempo_reload',
        '    dec tempo_reload',
        '    jmp pn_advance_recurse',
        '',
        'pn_cx:',
        '    pla',
        '    and #$0f',
        '    sta $d418',
        '    jmp pn_advance_recurse',
        '',
        'pn_note:',
        '    pha',
        '    ldx cur_voice',
        '    ldy voice_sid_off,x',
        '    lda cur_ctrl,x',
        '    sta $d404,y',
        '    pla',
        '    jsr instrument_load',
        '    jmp pn_advance_rts',
        '',
        'pn_advance_recurse:',
        '    inc $f2',
        '    bne pn_ar_skip',
        '    inc $f3',
        'pn_ar_skip:',
        '    jmp pn_read',
        '',
        'pn_advance_rts:',
        '    inc $f2',
        '    bne pn_arts_skip',
        '    inc $f3',
        'pn_arts_skip:',
        '    rts',
        '',
    ]

    # ----- instrument_load (Cluster B specific) -----
    lines += [
        'instrument_load:',
        '    ; A = note; X = cur_voice; cur_voice_y = Y_stride',
        '    pha',
        '    lda cur_inst,x',
        '    asl',
        '    tay',
        '    lda inst_src_table,y',
        '    sta inst_copy_src+1',
        '    lda inst_src_table+1,y',
        '    sta inst_copy_src+2',
        '    ldy #$0e',                    # CF: 15 bytes (LDY #$0E, DEY-loop)
        '    ldx cur_voice_y',
        '    txa',
        '    clc',
        '    adc #<voice_state',
        '    sta inst_copy_dst+1',
        '    lda #>voice_state',
        '    adc #$00',
        '    sta inst_copy_dst+2',
        'inst_copy_loop:',
        'inst_copy_src:',
        '    lda $ffff,y',
        'inst_copy_dst:',
        '    sta $ffff,y',
        '    dey',
        '    bpl inst_copy_loop',
        '    ; Apply note to freq cells',
        '    pla',
        '    pha',
        '    tax',
        '    ldy cur_voice_y',
        '    ; Off-slide freq (THIS note) at $14/$15',
        '    lda freq_lo_table,x',
        '    sta voice_state+$14,y',
        '    lda freq_hi_table,x',
        '    sta voice_state+$15,y',
        '    ; Normal freq (note+$10) at $16/$17',
        '    pla',
        '    clc',
        '    adc #$10',
        '    tax',
        '    lda freq_lo_table,x',
        '    sta voice_state+$16,y',
        '    lda freq_hi_table,x',
        '    sta voice_state+$17,y',
        '    ; Set cur_ctrl from voice_state+$0B',
        '    lda voice_state+$0B,y',
        '    ldx cur_voice',
        '    sta cur_ctrl,x',
        '    ; Clear PWM phase + lo accum',
        '    lda #$00',
        '    sta voice_pwm_phase,x',
        '    sta voice_pwm_lo,x',
        '    ; Write AD/SR (slab offsets $0C/$0D)',
        '    ldy voice_sid_off,x',
        '    ldx cur_voice_y',
        '    lda voice_state+$0C,x',
        '    sta $d405,y',
        '    lda voice_state+$0D,x',
        '    sta $d406,y',
        '    rts',
        '',
    ]

    # ----- modulate_voice (Cluster B specific) -----
    lines += [
        'modulate_voice:',
        '    stx cur_voice',
        '    lda voice_y_table,x',
        '    sta cur_voice_y',
        '    ldy voice_sid_off,x',
        '    sty cur_sid_off',
        '    ; LFO toggle: bit 0 of flag enables vibrato',
        '    ldy cur_voice_y',
        '    lda voice_state,y',
        '    lsr',
        '    bcc mod_off_slide_freq',      # bit 0 = 0 → always off-slide
        '    lda frame_counter',
        '    lsr',
        '    bcc mod_normal_freq',         # even frame → normal',
        '    ; odd frame → off-slide (fall-through)',
        'mod_off_slide_freq:',
        '    ldx cur_sid_off',
        '    lda voice_state+$14,y',
        '    sta $d400,x',
        '    lda voice_state+$15,y',
        '    sta $d401,x',
        '    jmp mod_pw_out',
        'mod_normal_freq:',
        '    ldx cur_sid_off',
        '    lda voice_state+$16,y',
        '    sta $d400,x',
        '    lda voice_state+$17,y',
        '    sta $d401,x',
        'mod_pw_out:',
        '    ; PW hi from slab+$01',
        '    lda voice_state+$01,y',
        '    sta $d403,x',
        '    ldx cur_voice',
        '    lda voice_pwm_lo,x',
        '    ldx cur_sid_off',
        '    sta $d402,x',
        '    ; CTRL = slab+$0B | slab+$0E',
        '    lda voice_state+$0B,y',
        '    ora voice_state+$0E,y',
        '    sta $d404,x',
        '    ; PWM update',
        '    jsr pwm_update_cb',
        '    rts',
        '',
    ]

    # ----- pwm_update_cb (Cluster B specific) -----
    lines += [
        'pwm_update_cb:',
        '    ldx cur_voice',
        '    lda voice_pwm_phase,x',
        '    bne pwm_cb_phase1',
        '    ; Phase 0',
        '    ldy cur_voice_y',
        '    lda voice_state+$05,y',       # phase 0 dir
        '    bne pwm_cb_0_sub',
        '    ; Phase 0 ADD',
        '    lda voice_pwm_lo,x',
        '    clc',
        '    adc voice_state+$03,y',       # phase 0 lo delta
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$01,y',       # PW hi
        '    adc #$00',
        '    sta voice_state+$01,y',
        '    cmp voice_state+$02,y',       # phase 0 limit
        '    bcs pwm_cb_advance',
        '    rts',
        'pwm_cb_0_sub:',
        '    lda voice_pwm_lo,x',
        '    sec',
        '    sbc voice_state+$03,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$01,y',
        '    sbc #$00',
        '    sta voice_state+$01,y',
        '    cmp voice_state+$02,y',
        '    beq pwm_cb_advance',
        '    bcs pwm_cb_done',
        'pwm_cb_advance:',
        '    inc voice_pwm_phase,x',
        'pwm_cb_done:',
        '    rts',
        '',
        'pwm_cb_phase1:',
        '    ldy cur_voice_y',
        '    lda voice_state+$06,y',       # phase 1 dir
        '    bne pwm_cb_1_sub',
        '    ; Phase 1 ADD',
        '    lda voice_pwm_lo,x',
        '    clc',
        '    adc voice_state+$09,y',       # phase 1 lo delta
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$01,y',
        '    adc #$00',
        '    sta voice_state+$01,y',
        '    cmp voice_state+$07,y',       # phase 1 max
        '    bcc pwm_cb_1_done',
        '    lda #$01',
        '    sta voice_state+$06,y',       # flip to SUB
        '    rts',
        'pwm_cb_1_sub:',
        '    lda voice_pwm_lo,x',
        '    sec',
        '    sbc voice_state+$09,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$01,y',
        '    sbc #$00',
        '    sta voice_state+$01,y',
        '    cmp voice_state+$08,y',       # phase 1 min
        '    beq pwm_cb_1_flip',
        '    bcs pwm_cb_1_done',
        'pwm_cb_1_flip:',
        '    lda #$00',
        '    sta voice_state+$06,y',       # flip to ADD
        'pwm_cb_1_done:',
        '    rts',
        '',
    ]

    # ----- State region -----
    lines += [
        '; State region',
        'cur_voice:        .byte 0',
        'cur_voice_y:      .byte 0',
        'cur_sid_off:      .byte 0',
        'frame_counter:    .byte 0',
        'tempo_counter:    .byte 0',
        'tempo_reload:     .byte 0',
        'self_mod_counter: .byte 0',
        'dur_counters:     .byte 0, 0, 0',
        'cur_inst:         .byte 0, 0, 0',
        'cur_ctrl:         .byte 0, 0, 0',
        'voice_ptrs:       .byte 0, 0, 0, 0, 0, 0',
        'voice_pwm_phase:  .byte 0, 0, 0',
        'voice_pwm_lo:     .byte 0, 0, 0',
        'voice_state:      .dsb 26 * 3, 0',
        'voice_y_table:    .byte $00, $1A, $34',
        'voice_sid_off:    .byte ' + ', '.join(f'${b:02X}' for b in data.voice_offsets),
        '',
        'sub_jump_table:',
        '    .byte ' + ', '.join(f'${b:02X}' for b in data.sub_jump_table),
        '',
    ]

    # ----- Freq tables -----
    lines.append('freq_lo_table:')
    for i in range(0, 128, 16):
        chunk = data.freq_lo[i:i + 16]
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('freq_hi_table:')
    for i in range(0, 128, 16):
        chunk = data.freq_hi[i:i + 16]
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    # ----- Instrument source table + programs (15 bytes each for CF) -----
    lines.append('inst_src_table:')
    for i in range(len(data.inst_programs)):
        lines.append(f'    .byte <inst_prog_{i}, >inst_prog_{i}')
    lines.append('')
    for i, prog in enumerate(data.inst_programs):
        lines.append(f'inst_prog_{i}:')
        # CF programs are 15 bytes; if data has 24, take first 15
        prog_15 = prog[:15]
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in prog_15))
    lines.append('')

    # ----- Voice patterns -----
    for v, pat in enumerate(data.voice_patterns):
        lines.append(f'voice{v}_pattern:')
        for i in range(0, len(pat), 16):
            chunk = pat[i:i + 16]
            lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    return '\n'.join(lines) + '\n'
