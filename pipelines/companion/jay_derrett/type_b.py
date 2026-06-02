"""Type B engine emit (Equalizer-shape, B1 sub-cluster).

Implements `emit_asm_type_b()` for the Equalizer canonical engine:
- 5-byte instrument programs
- Per-voice PWM modulation: phase 0 ADD $40 until PW hi >= $08,
  then phase 1 signed-delta oscillation
- NOTE handler: resets PW lo, copies saved phase-1 delta to current,
  writes freq + CTRL (twice: w/o gate, then gate retrigger)
- $Dx handler: 5-byte program → phase1 delta (saved+cur), CTRL, AD, SR

My reb uses Y-indexed slab layout (cleaner than orig's per-voice
unrolled mod subs with state-multiplexing through V1's slots).
"""
from __future__ import annotations
import struct
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


@dataclass
class TypeBData:
    """Extracted data for a Type B SID."""
    freq_lo: bytes        # 128 bytes
    freq_hi: bytes        # 128 bytes
    sub_jump_table: bytes # 6 bytes (3 entries × 2)
    inst_programs: list[bytes]  # N × 5-byte programs
    voice_patterns: list[bytes]  # 3 voice byte streams
    voice_initial_offsets: tuple[int, int, int]
    # PSID metadata
    title: str
    author: str
    released: str
    # Captured init state (replicated in reb's init)
    initial_voice_ptrs: tuple[int, int, int]   # absolute orig addrs (remap)
    initial_tempo: int
    initial_tempo_reload: int
    initial_master_vol: int
    initial_dur_counters: tuple[int, int, int]
    initial_cur_ctrl: tuple[int, int, int]
    initial_pw_lo: tuple[int, int, int]
    initial_pw_hi: tuple[int, int, int]
    # PW hi reset values per voice. NOTE handler copies these to PW hi.
    # $Dx handler updates them from inst byte 0.
    initial_pw_hi_reset: tuple[int, int, int]
    # Phase-1 signed delta per voice — static body data ($CA2B/$CA6B/
    # $CAAB), toggled by mod sub's flip. Not changed by NOTE or $Dx.
    initial_phase1_delta: tuple[int, int, int]
    initial_smc: int
    smc_wrap: int             # $E3 for Equalizer (3 sub-jump entries)
    # Per-SID init SID writes (captured via py65 trace) — replayed by reb's
    # init to match orig's pre-play SID state. Sequence of (reg, val) tuples.
    init_sid_writes: list[tuple[int, int]] = None


def emit_asm_type_b(data: TypeBData, load_addr: int = 0x1000) -> str:
    """Emit clean xa65 asm for a Type B (Equalizer-shape) Jay_Derrett SID."""
    lines: list[str] = [f'* = ${load_addr:04X}']
    lines += [
        '',
        '; ==========================================================',
        '; Jay_Derrett Type B engine (Equalizer-shape)',
        '; ==========================================================',
        '',
        '; ZP: $F2/$F3 = pattern ptr',
        '',
        'init_entry: jmp init_code',
        'play_entry: jmp play_code',
        '',
    ]

    # ----- init -----
    lines += ['init_code:']
    for v in range(3):
        lines += [
            f'    lda #<voice{v}_pattern',
            f'    sta voice_ptrs+{v*2}',
            f'    lda #>voice{v}_pattern',
            f'    sta voice_ptrs+{v*2+1}',
        ]
    lines += [
        f'    lda #${data.initial_smc:02X}',
        '    sta self_mod_counter',
        f'    lda #${data.initial_tempo:02X}',
        '    sta tempo_counter',
        f'    lda #${data.initial_tempo_reload:02X}',
        '    sta tempo_reload',
    ]
    # Replay captured orig init SID writes (matches orig's pre-play SID state)
    if data.init_sid_writes:
        for reg, val in data.init_sid_writes:
            lines += [f'    lda #${val:02X}', f'    sta $d4{reg:02X}']
    for v in range(3):
        lines += [
            f'    lda #${data.initial_dur_counters[v]:02X}',
            f'    sta dur_counters+{v}',
            f'    lda #${data.initial_cur_ctrl[v]:02X}',
            f'    sta cur_ctrl+{v}',
            f'    lda #${data.initial_pw_lo[v]:02X}',
            f'    sta voice_pw_lo+{v}',
            f'    lda #${data.initial_pw_hi[v]:02X}',
            f'    sta voice_pw_hi+{v}',
            f'    lda #${data.initial_pw_hi_reset[v]:02X}',
            f'    sta voice_pw_hi_reset+{v}',
            f'    lda #${data.initial_phase1_delta[v]:02X}',
            f'    sta voice_phase1_delta+{v}',
        ]
    lines += ['    rts', '']

    # ----- play -----
    lines += [
        'play_code:',
        '    ; PWM modulation per voice (unrolled — orig has per-voice',
        '    ; hand-coded subs with different control flow per voice).',
        '    jsr pwm_update_v0',
        '    jsr pwm_update_v1',
        '    jsr pwm_update_v2',
        '    ; tempo check',
        '    dec tempo_counter',
        '    beq tempo_expired',
        '    rts',
        'tempo_expired:',
        '    ldx #$00',
        '    jsr process_voice',
        '    ldx #$01',
        '    jsr process_voice',
        '    ldx #$02',
        '    jsr process_voice',
        '    lda tempo_reload',
        '    sta tempo_counter',
        '    rts',
        '',
    ]

    # ----- Per-voice unrolled PWM mod subs -----
    # V0 (V1 in SID): phase 0 entry CMP #$08 / BCS (≥), writes both
    # $D402 + $D403 in BOTH phases.
    lines += [
        'pwm_update_v0:',
        '    lda voice_pw_hi+0',
        '    cmp #$08',
        '    bcs v0_phase1',
        '    ; Phase 0: ADD #$40 to PW lo, carry → INC PW hi, write both',
        '    lda voice_pw_lo+0',
        '    clc',
        '    adc #$40',
        '    sta voice_pw_lo+0',
        '    bcc v0_p0_nocarry',
        '    inc voice_pw_hi+0',
        'v0_p0_nocarry:',
        '    sta $d402',
        '    lda voice_pw_hi+0',
        '    sta $d403',
        '    rts',
        'v0_phase1:',
        '    lda voice_pw_lo+0',
        '    clc',
        '    adc voice_phase1_delta+0',
        '    sta voice_pw_lo+0',
        '    sta $d402',           # phase 1 writes ONLY PW lo (not PW hi)',
        '    beq v0_p1_flip',
        '    rts',
        'v0_p1_flip:',
        '    lda #$00',
        '    sec',
        '    sbc voice_phase1_delta+0',
        '    sta voice_phase1_delta+0',
        '    jmp v0_phase1',
        '',
    ]
    # V1 (V2 in SID, sid_off=7): phase 0 entry CMP #$09 / BEQ (==),
    # phase 1 writes ONLY PW lo ($D409), no PW hi.
    lines += [
        'pwm_update_v1:',
        '    lda voice_pw_hi+1',
        '    cmp #$09',
        '    beq v1_phase1',
        '    ; Phase 0',
        '    lda voice_pw_lo+1',
        '    clc',
        '    adc #$40',
        '    sta voice_pw_lo+1',
        '    bcc v1_p0_nocarry',
        '    inc voice_pw_hi+1',
        'v1_p0_nocarry:',
        '    sta $d409',
        '    lda voice_pw_hi+1',
        '    sta $d40a',
        '    rts',
        'v1_phase1:',
        '    lda voice_pw_lo+1',
        '    clc',
        '    adc voice_phase1_delta+1',
        '    sta voice_pw_lo+1',
        '    sta $d409',
        '    bne v1_p1_done',
        '    lda #$00',
        '    sec',
        '    sbc voice_phase1_delta+1',
        '    sta voice_phase1_delta+1',
        '    jmp v1_phase1',
        'v1_p1_done:',
        '    rts',
        '',
    ]
    # V2 (V3 in SID, sid_off=$E): same as V1 but for V3 ($D410/$D411).
    lines += [
        'pwm_update_v2:',
        '    lda voice_pw_hi+2',
        '    cmp #$09',
        '    beq v2_phase1',
        '    lda voice_pw_lo+2',
        '    clc',
        '    adc #$40',
        '    sta voice_pw_lo+2',
        '    bcc v2_p0_nocarry',
        '    inc voice_pw_hi+2',
        'v2_p0_nocarry:',
        '    sta $d410',
        '    lda voice_pw_hi+2',
        '    sta $d411',
        '    rts',
        'v2_phase1:',
        '    lda voice_pw_lo+2',
        '    clc',
        '    adc voice_phase1_delta+2',
        '    sta voice_pw_lo+2',
        '    sta $d410',
        '    bne v2_p1_done',
        '    lda #$00',
        '    sec',
        '    sbc voice_phase1_delta+2',
        '    sta voice_phase1_delta+2',
        '    jmp v2_phase1',
        'v2_p1_done:',
        '    rts',
        '',
    ]

    # ----- process_voice (set up $F2/F3 + cur_voice, call proc_note) -----
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

    # ----- proc_note — byte vocabulary same as Type A -----
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
        '    bne dispatch1',
        '    jmp pn_ex',
        'dispatch1:',
        '    cmp #$d0',
        '    bne dispatch2',
        '    jmp pn_dx',
        'dispatch2:',
        '    pla',
        '    cmp #$80',
        '    bne dispatch3',
        '    jmp pn_gate_off',
        'dispatch3:',
        '    cmp #$81',
        '    bne dispatch4',
        '    jmp pn_skip',
        'dispatch4:',
        '    cmp #$82',
        '    bne dispatch5',
        '    jmp pn_set_dur',
        'dispatch5:',
        '    pha',
        '    and #$f0',
        '    cmp #$b0',
        '    bne dispatch6',
        '    jmp pn_bx',
        'dispatch6:',
        '    cmp #$c0',
        '    bne dispatch7',
        '    jmp pn_cx',
        'dispatch7:',
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
        f'    cmp #${data.smc_wrap:02X}',
        '    bne pn_read',
        f'    lda #${data.initial_smc:02X}',
        '    sta self_mod_counter',
        '    jmp pn_read',
        '',
        'pn_dx:',
        '    pla',
        '    and #$0f',
        '    ; inst index → byte offset = inst * 5',
        '    sta inst_tmp',
        '    asl',
        '    asl',
        '    clc',
        '    adc inst_tmp',
        '    sta inst_off',         # save inst*5
        '    tay',
        '    ; byte 0 → voice_pw_hi_reset AND current voice_pw_hi (orig',
        '    ; multiplexing: $Dx writes $CA0A which IS the live PW hi',
        '    ; for the current voice via play_code\'s pre/post-proc_note',
        '    ; copy through V1\'s slots).',
        '    lda inst_programs,y',
        '    sta voice_pw_hi_reset,x',
        '    sta voice_pw_hi,x',
        '    ; byte 1 → cur_ctrl[X]',
        '    lda inst_programs+1,y',
        '    sta cur_ctrl,x',
        '    ; byte 2 → SID AD (D405+sid_off), byte 3 → SID SR (D406+sid_off)',
        '    lda inst_programs+2,y',
        '    sta tmp_a',
        '    lda inst_programs+3,y',
        '    sta tmp_b',
        '    ldy voice_sid_off,x',
        '    lda tmp_a',
        '    sta $d405,y',
        '    lda tmp_b',
        '    sta $d406,y',
        '    jmp pn_advance_recurse',
        '',
        'pn_gate_off:',
        '    ; Equalizer $80: writes cur_ctrl,X to $D404,Y directly',
        '    ldy voice_sid_off,x',
        '    lda cur_ctrl,x',
        '    sta $d404,y',
        '    jmp pn_advance_rts',
        '',
        'pn_skip:',
        '    jmp pn_advance_rts',
        '',
        'pn_set_dur:',
        '    inc $f2',
        '    bne pn_sd_no_inc',
        '    inc $f3',
        'pn_sd_no_inc:',
        '    ldy #$00',
        '    lda ($f2),y',
        '    sta dur_counters,x',
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
        '    ; A = note byte. Orig quirk: NOTE always resets V0\'s PW lo',
        '    ; (orig hardcodes STA $CA03 regardless of current voice — V2/V3',
        '    ; PW lo never reset). Current voice gets PW hi reset.',
        '    pha',
        '    lda #$00',
        '    sta voice_pw_lo+0',     # always V0, NOT current voice
        '    lda voice_pw_hi_reset,x',
        '    sta voice_pw_hi,x',
        '    pla',
        '    tay              ; Y = note',
        '    lda freq_lo_table,y',
        '    sta tmp_a',
        '    lda freq_hi_table,y',
        '    sta tmp_b',
        '    ldy voice_sid_off,x',
        '    lda tmp_a',
        '    sta $d400,y',
        '    lda tmp_b',
        '    sta $d401,y',
        '    lda cur_ctrl,x',
        '    sta $d404,y',
        '    ora #$01',
        '    sta $d404,y',
        '    jmp pn_advance_rts',
        '',
        'pn_advance_recurse:',
        '    inc $f2',
        '    bne par_skip',
        '    inc $f3',
        'par_skip:',
        '    jmp pn_read',
        '',
        'pn_advance_rts:',
        '    inc $f2',
        '    bne part_skip',
        '    inc $f3',
        'part_skip:',
        '    rts',
        '',
    ]

    # ----- state region -----
    lines += [
        '; State',
        'cur_voice:        .byte 0',
        'inst_tmp:         .byte 0',
        'inst_off:         .byte 0',
        'tmp_a:            .byte 0',
        'tmp_b:            .byte 0',
        'frame_counter:    .byte 0',
        'tempo_counter:    .byte 0',
        'tempo_reload:     .byte 0',
        'self_mod_counter: .byte 0',
        'dur_counters:     .byte 0, 0, 0',
        'cur_ctrl:         .byte 0, 0, 0',
        'voice_pw_lo:      .byte 0, 0, 0',
        'voice_pw_hi:      .byte 0, 0, 0',
        'voice_phase1_delta:   .byte 0, 0, 0',
        'voice_pw_hi_reset: .byte 0, 0, 0',
        'voice_ptrs:       .byte 0, 0, 0, 0, 0, 0',
        'voice_sid_off:    .byte $00, $07, $0E',
        '',
        'sub_jump_table:',
        '    .byte ' + ', '.join(f'${b:02X}' for b in data.sub_jump_table),
        '',
    ]

    # ----- freq tables -----
    lines.append('freq_lo_table:')
    for i in range(0, 128, 16):
        chunk = data.freq_lo[i:i + 16]
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('freq_hi_table:')
    for i in range(0, 128, 16):
        chunk = data.freq_hi[i:i + 16]
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    # ----- inst programs (5 bytes each, concatenated) -----
    lines.append('inst_programs:')
    for i, prog in enumerate(data.inst_programs):
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in prog[:5]))
    lines.append('')

    # ----- voice patterns -----
    for v, pat in enumerate(data.voice_patterns):
        lines.append(f'voice{v}_pattern:')
        for i in range(0, len(pat), 16):
            chunk = pat[i:i + 16]
            lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# Extraction for Type B SIDs
# ---------------------------------------------------------------------------

# Per-SID hardcoded engine state addresses for B1 sub-cluster.
# Eventually auto-detect; for now hand-extracted from binary RE.
TYPE_B_CONFIGS = {
    'Equalizer': {
        'voice_ptrs_addr': 0xC8AC,
        'dur_counters_addr': 0xC8B2,
        'cur_ctrl_addr': 0xC8B5,
        'tempo_addr': 0xC8AA,
        'tempo_reload_addr': 0xC8AB,
        'freq_lo_addr': 0xC8E1,
        'freq_hi_addr': 0xC961,
        'inst_programs_addr': 0xC8BF,
        'n_inst': 16,
        'sub_jump_table_addr': 0xC8B8,
        'smc_addr': 0xC785,
        'smc_wrap': 0xE3,
        'pw_lo_addrs': (0xCA03, 0xCA05, 0xCA07),
        'pw_hi_addrs': (0xCA04, 0xCA06, 0xCA08),
        'phase1_delta_addrs': (0xCA2B, 0xCA6B, 0xCAAB),
        'pw_hi_reset_addrs': (0xCA0B, 0xCA0D, 0xCA0E),
    },
    'Death_or_Glory': {
        'voice_ptrs_addr': 0x3931,
        'dur_counters_addr': 0x3937,
        'cur_ctrl_addr': 0x393A,        # heuristic — adjust if wrong
        'tempo_addr': 0x392F,
        'tempo_reload_addr': 0x3930,    # heuristic
        'freq_lo_addr': 0x3971,
        'freq_hi_addr': 0x39F1,         # heuristic = freq_lo + $80
        'inst_programs_addr': 0x394A,   # from $Dx handler at $3832
        'n_inst': 16,
        'sub_jump_table_addr': 0x393D,  # heuristic — adjust
        'smc_addr': 0x3812,             # heuristic — at LDA before CMP #$E6 at $3813
        'smc_wrap': 0xE6,               # detected: CMP #$E6
        'pw_lo_addrs': (0x3A93, 0x3A95, 0x3A97),
        'pw_hi_addrs': (0x3A94, 0x3A96, 0x3A98),
        'phase1_delta_addrs': (0x3ABB, 0x3AFB, 0x3B3B),
        'pw_hi_reset_addrs': (0x3A9C, 0x3A9D, 0x3A9E),
    },
}


def extract_type_b(sid_path: str, sid_name: str = None) -> TypeBData:
    """Extract Type B engine data from a SID using TYPE_B_CONFIGS."""
    if sid_name is None:
        sid_name = Path(sid_path).stem
    if sid_name not in TYPE_B_CONFIGS:
        raise ValueError(f'No TYPE_B_CONFIGS entry for {sid_name}')
    cfg = TYPE_B_CONFIGS[sid_name]

    raw = Path(sid_path).read_bytes()
    body = raw[0x7C:]
    load_in = struct.unpack('>H', raw[8:10])[0]
    if load_in == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    else:
        load = load_in
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body

    # Run init via py65 to capture state cells + SID writes
    import sys as _sys
    _sys.path.insert(0, str(ROOT / 'tools' / 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from pipelines.companion.jay_derrett.build import _libsidplayfp_powerup_ram
    init_addr = struct.unpack('>H', raw[10:12])[0]
    mpu = MPU()
    mpu.memory = _libsidplayfp_powerup_ram()
    mpu.memory[load:load + len(body)] = body
    mpu.memory[0x01] = 0x37
    mpu.a = 0; mpu.x = 0; mpu.y = 0; mpu.p = 0x20; mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE; mpu.memory[0x01FE] = 0xFE
    mpu.pc = init_addr
    init_sid_writes: list[tuple[int, int]] = []
    for _ in range(2_000_000):
        if mpu.pc == 0xFEFF: break
        op = mpu.memory[mpu.pc]
        tgt = None
        if op == 0x8D:    # STA abs
            tgt = mpu.memory[mpu.pc + 1] | (mpu.memory[mpu.pc + 2] << 8)
            val = mpu.a
        elif op == 0x9D:  # STA abs,X
            tgt = ((mpu.memory[mpu.pc + 1] | (mpu.memory[mpu.pc + 2] << 8)) + mpu.x) & 0xFFFF
            val = mpu.a
        elif op == 0x99:  # STA abs,Y
            tgt = ((mpu.memory[mpu.pc + 1] | (mpu.memory[mpu.pc + 2] << 8)) + mpu.y) & 0xFFFF
            val = mpu.a
        elif op == 0x8E:  # STX abs
            tgt = mpu.memory[mpu.pc + 1] | (mpu.memory[mpu.pc + 2] << 8)
            val = mpu.x
        elif op == 0x8C:  # STY abs
            tgt = mpu.memory[mpu.pc + 1] | (mpu.memory[mpu.pc + 2] << 8)
            val = mpu.y
        if tgt is not None and 0xD400 <= tgt <= 0xD41F:
            init_sid_writes.append((tgt & 0x1F, val))
        mpu.step()
    post = mpu.memory

    # Voice ptrs (initial)
    vp = cfg['voice_ptrs_addr']
    voice_initial_ptrs = tuple(
        post[vp + v*2] | (post[vp + v*2 + 1] << 8)
        for v in range(3)
    )

    # Freq tables (128 bytes each)
    freq_lo = bytes(post[cfg['freq_lo_addr']:cfg['freq_lo_addr'] + 128])
    freq_hi = bytes(post[cfg['freq_hi_addr']:cfg['freq_hi_addr'] + 128])

    # Sub-jump table (3 entries × 2 = 6 bytes)
    sjt = bytes(post[cfg['sub_jump_table_addr']:cfg['sub_jump_table_addr'] + 6])

    # Instrument programs (n_inst × 5 bytes)
    inst_programs = []
    inst_base = cfg['inst_programs_addr']
    for i in range(cfg['n_inst']):
        prog = bytes(post[inst_base + i*5:inst_base + (i+1)*5])
        inst_programs.append(prog)

    # Voice patterns — use captured ranges. Pattern data goes from each
    # voice's initial ptr to the next sorted boundary (other voice ptrs,
    # play_addr, init_addr, or end of body).
    pat_starts = list(voice_initial_ptrs)
    play_addr = struct.unpack('>H', raw[12:14])[0]
    body_end = load + len(body)
    boundaries = sorted(set(pat_starts + [play_addr, init_addr, body_end]))
    voice_patterns = []
    for v in range(3):
        start = voice_initial_ptrs[v]
        end = next((b for b in boundaries if b > start), body_end)
        voice_patterns.append(bytes(post[start:end]))

    # Init state captures
    dur = tuple(post[cfg['dur_counters_addr'] + v] for v in range(3))
    cur_ctrl = tuple(post[cfg['cur_ctrl_addr'] + v] for v in range(3))
    pw_lo = tuple(post[a] for a in cfg['pw_lo_addrs'])
    pw_hi = tuple(post[a] for a in cfg['pw_hi_addrs'])
    phase1 = tuple(post[a] for a in cfg['phase1_delta_addrs'])
    pw_hi_reset = tuple(post[a] for a in cfg['pw_hi_reset_addrs'])
    tempo = post[cfg['tempo_addr']]
    tempo_reload = post[cfg['tempo_reload_addr']]
    smc = post[cfg['smc_addr']]
    mvol = post[0xD418] or 0x0F

    # PSID metadata
    title = raw[0x16:0x36].rstrip(b'\x00').decode('latin-1')
    author = raw[0x36:0x56].rstrip(b'\x00').decode('latin-1')
    released = raw[0x56:0x76].rstrip(b'\x00').decode('latin-1')

    return TypeBData(
        freq_lo=freq_lo, freq_hi=freq_hi,
        sub_jump_table=sjt,
        inst_programs=inst_programs,
        voice_patterns=voice_patterns,
        voice_initial_offsets=(0, 0, 0),
        title=title, author=author, released=released,
        initial_voice_ptrs=voice_initial_ptrs,
        initial_tempo=tempo,
        initial_tempo_reload=tempo_reload,
        initial_master_vol=mvol,
        initial_dur_counters=dur,
        initial_cur_ctrl=cur_ctrl,
        initial_pw_lo=pw_lo,
        initial_pw_hi=pw_hi,
        initial_pw_hi_reset=pw_hi_reset,
        initial_phase1_delta=phase1,
        initial_smc=smc,
        smc_wrap=cfg['smc_wrap'],
        init_sid_writes=init_sid_writes,
    )


def build_type_b_sid(sid_name: str, load_addr: int = 0x1000) -> bytes:
    """Build a Type B SID as PSID using emit_asm_type_b."""
    from pipelines.companion.jay_derrett.build import _assemble, _wrap_psid
    sid_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   f'{sid_name}.sid')
    data = extract_type_b(sid_path, sid_name)

    # Pass 1: assemble to get label addrs
    asm1 = emit_asm_type_b(data, load_addr)
    bin1, labels1 = _assemble(asm1, f'jd_{sid_name}_pass1')
    voice_pattern_bases = [labels1.get(f'voice{v}_pattern', 0) for v in range(3)]

    # Remap sub_jump_table entries to new voice_pattern_bases
    remapped = bytearray()
    for i in range(0, len(data.sub_jump_table), 2):
        orig = data.sub_jump_table[i] | (data.sub_jump_table[i+1] << 8)
        owner = None
        for v in range(3):
            base = data.initial_voice_ptrs[v]
            end = base + len(data.voice_patterns[v])
            if base <= orig < end:
                owner = v
                break
        if owner is not None:
            offset = orig - data.initial_voice_ptrs[owner]
            new = voice_pattern_bases[owner] + offset
            remapped += bytes([new & 0xFF, (new >> 8) & 0xFF])
        else:
            remapped += b'\x00\x00'
    data.sub_jump_table = bytes(remapped)
    asm2 = emit_asm_type_b(data, load_addr)
    bin2, _ = _assemble(asm2, f'jd_{sid_name}_pass2')

    return _wrap_psid(data.title, data.author, data.released,
                      load_addr, load_addr + 3, load_addr,
                      bin2, n_subtunes=1)


def build_equalizer_sid(load_addr: int = 0x1000) -> bytes:
    return build_type_b_sid('Equalizer', load_addr)


if __name__ == '__main__':
    import sys as _sys
    targets = _sys.argv[1:] if len(_sys.argv) > 1 else ['Equalizer']
    for name in targets:
        out = ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' / f'{name}.sidfinity.sid'
        out.write_bytes(build_type_b_sid(name))
        print(f'Wrote {out}')
