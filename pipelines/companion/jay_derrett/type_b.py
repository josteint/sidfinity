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
    initial_phase1_delta: tuple[int, int, int]
    initial_smc: int
    smc_wrap: int             # $E3 for Equalizer (3 sub-jump entries)


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
        f'    lda #${data.initial_master_vol:02X}',
        '    sta $d418',
    ]
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
            f'    lda #${data.initial_phase1_delta[v]:02X}',
            f'    sta voice_phase1_delta_cur+{v}',
            f'    sta voice_phase1_delta_saved+{v}',
        ]
    lines += ['    rts', '']

    # ----- play -----
    lines += [
        'play_code:',
        '    ; PWM modulation per voice (always runs before tempo check)',
        '    ldx #$00',
        '    jsr pwm_update_voice',
        '    ldx #$01',
        '    jsr pwm_update_voice',
        '    ldx #$02',
        '    jsr pwm_update_voice',
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

    # ----- PWM update per voice -----
    lines += [
        'pwm_update_voice:',
        '    ; X = voice idx',
        '    ldy voice_sid_off,x',
        '    lda voice_pw_hi,x',
        '    cmp #$08',
        '    bcs pwm_phase1',
        '    ; Phase 0: PW lo += $40, carry → PW hi += 1',
        '    lda voice_pw_lo,x',
        '    clc',
        '    adc #$40',
        '    sta voice_pw_lo,x',
        '    bcc pwm0_no_carry',
        '    inc voice_pw_hi,x',
        'pwm0_no_carry:',
        '    sta $d402,y',
        '    lda voice_pw_hi,x',
        '    sta $d403,y',
        '    rts',
        'pwm_phase1:',
        '    lda voice_pw_lo,x',
        '    clc',
        '    adc voice_phase1_delta_cur,x',
        '    sta voice_pw_lo,x',
        '    sta $d402,y',
        '    bne pwm1_done',
        '    ; result == 0 → flip sign of delta, retry',
        '    lda #$00',
        '    sec',
        '    sbc voice_phase1_delta_cur,x',
        '    sta voice_phase1_delta_cur,x',
        '    jmp pwm_phase1',
        'pwm1_done:',
        '    lda voice_pw_hi,x',
        '    sta $d403,y',
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
        '    tay',
        '    ; byte 0 → phase1 delta (saved + cur)',
        '    lda inst_programs,y',
        '    sta voice_phase1_delta_saved,x',
        '    sta voice_phase1_delta_cur,x',
        '    ; byte 1 → cur_ctrl',
        '    lda inst_programs+1,y',
        '    sta cur_ctrl,x',
        '    ; byte 2 → AD; byte 3 → SR (direct SID writes)',
        '    ldy voice_sid_off,x',
        '    lda inst_programs+2,y',
        '    ; Need different Y for inst_programs vs voice_sid_off!',
        '    ; Re-derive inst byte offset',
        '    txa',
        '    pha',
        '    lda inst_tmp',
        '    asl',
        '    asl',
        '    clc',
        '    adc inst_tmp',
        '    tay',
        '    lda inst_programs+2,y',
        '    ldx cur_voice',
        '    ldy voice_sid_off,x',
        '    sta $d405,y',
        '    pla',
        '    tax',
        '    lda inst_tmp',
        '    asl',
        '    asl',
        '    clc',
        '    adc inst_tmp',
        '    tay',
        '    lda inst_programs+3,y',
        '    ldx cur_voice',
        '    ldy voice_sid_off,x',
        '    sta $d406,y',
        '    ldx cur_voice',
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
        '    ; A = note byte. Reset PW lo, copy saved delta to cur,',
        '    ; write freq, write CTRL twice (gate retrigger).',
        '    pha',
        '    lda #$00',
        '    sta voice_pw_lo,x',
        '    lda voice_phase1_delta_saved,x',
        '    sta voice_phase1_delta_cur,x',
        '    pla',
        '    pha',
        '    tay              ; Y = note',
        '    lda freq_lo_table,y',
        '    ldy voice_sid_off,x',
        '    sta $d400,y',
        '    pla',
        '    tax              ; X = note',
        '    lda freq_hi_table,x',
        '    ldx cur_voice',
        '    ldy voice_sid_off,x',
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
        'frame_counter:    .byte 0',
        'tempo_counter:    .byte 0',
        'tempo_reload:     .byte 0',
        'self_mod_counter: .byte 0',
        'dur_counters:     .byte 0, 0, 0',
        'cur_ctrl:         .byte 0, 0, 0',
        'voice_pw_lo:      .byte 0, 0, 0',
        'voice_pw_hi:      .byte 0, 0, 0',
        'voice_phase1_delta_cur:   .byte 0, 0, 0',
        'voice_phase1_delta_saved: .byte 0, 0, 0',
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

def extract_type_b(sid_path: str) -> TypeBData:
    """Extract Type B engine data from a SID. Currently Equalizer-specific
    (hardcoded addresses); will be generalized after auto-detection works."""
    # Equalizer specifics — replace with auto-detect later
    EQUALIZER = {
        'name': 'Equalizer',
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
        # PWM cells: V1 at $CA03/$CA04, V2 at $CA05/$CA06, V3 at $CA07/$CA08
        'pw_lo_addrs': (0xCA03, 0xCA05, 0xCA07),
        'pw_hi_addrs': (0xCA04, 0xCA06, 0xCA08),
        # Phase-1 saved delta cells: V1 $CA0B, V2 $CA0D, V3 $CA0E
        'phase1_saved_addrs': (0xCA0B, 0xCA0D, 0xCA0E),
    }
    cfg = EQUALIZER

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

    # Run init via py65 to capture state cells
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
    for _ in range(2_000_000):
        if mpu.pc == 0xFEFF: break
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

    # Voice patterns — use captured ranges. For Equalizer, voice ptrs
    # at $C000, $C233, $C46C; pattern data goes from each ptr to the
    # next, or to play_addr ($C6B4).
    pat_starts = list(voice_initial_ptrs)
    play_addr = struct.unpack('>H', raw[12:14])[0]
    boundaries = sorted(pat_starts + [play_addr])
    voice_patterns = []
    for v in range(3):
        start = voice_initial_ptrs[v]
        end = next(b for b in boundaries if b > start)
        voice_patterns.append(bytes(post[start:end]))

    # Init state captures
    dur = tuple(post[cfg['dur_counters_addr'] + v] for v in range(3))
    cur_ctrl = tuple(post[cfg['cur_ctrl_addr'] + v] for v in range(3))
    pw_lo = tuple(post[a] for a in cfg['pw_lo_addrs'])
    pw_hi = tuple(post[a] for a in cfg['pw_hi_addrs'])
    phase1 = tuple(post[a] for a in cfg['phase1_saved_addrs'])
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
        initial_phase1_delta=phase1,
        initial_smc=smc,
        smc_wrap=cfg['smc_wrap'],
    )


def build_equalizer_sid(load_addr: int = 0x1000) -> bytes:
    """Build Equalizer as PSID using emit_asm_type_b."""
    from pipelines.companion.jay_derrett.build import _assemble, _wrap_psid
    sid_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   'Equalizer.sid')
    data = extract_type_b(sid_path)

    # Pass 1: assemble to get label addrs
    asm1 = emit_asm_type_b(data, load_addr)
    bin1, labels1 = _assemble(asm1, 'jd_equalizer_pass1')
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
    bin2, _ = _assemble(asm2, 'jd_equalizer_pass2')

    return _wrap_psid(data.title, data.author, data.released,
                      load_addr, load_addr + 3, load_addr,
                      bin2, n_subtunes=1)


if __name__ == '__main__':
    out = ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' / 'Equalizer.sidfinity.sid'
    out.write_bytes(build_equalizer_sid())
    print(f'Wrote {out}')
