"""Clean xa65 composer for Jay_Derrett SIDs.

Phase 2 deliverable: emit clean asm + freshly-laid-out data for a
Jay_Derrett SID, producing byte-exact SID writes against the orig.

The engine logic is rewritten cleanly (not verbatim packed). Data
tables (freq lo/hi, sub-jump table, instrument sources + programs,
voice pattern bytes) are inlined from the orig SID body — these
ARE the SID's musical content, not the engine mechanism.

Iteration 1: Ninja_Hamster only (1 subtune, direct play, smallest
layout). Other Type A dispatch shapes added in subsequent iterations.

The emitted layout uses a configurable base load address (default
$1000). The composer is parametric over the EngineParams (defined
in emulator.py) — the parameters describe the orig binary's
addresses for extraction; the composer uses fresh chosen addresses
for its own layout.
"""

from __future__ import annotations

import json
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path

from pipelines.companion.jay_derrett.emulator import (
    JayDerrettEmulator, NINJA_HAMSTER, EngineParams,
)

ROOT = Path(__file__).resolve().parents[3]
XA = str(ROOT / 'tools' / 'xa65' / 'xa' / 'xa')


# ---------------------------------------------------------------------------
# Extraction helpers — pull data from the orig SID's memory image
# ---------------------------------------------------------------------------

@dataclass
class ExtractedData:
    """Data extracted from orig SID (the musical content)."""
    freq_lo: bytes        # 256 bytes (covers note + $10 wraparound)
    freq_hi: bytes        # 256 bytes
    sub_jump_table: bytes # 20 bytes (10 entries × 2)
    voice_offsets: bytes  # 3 bytes (0, 7, 14)
    inst_src_table: bytes # 19 × 2 = 38 bytes (src addr lo/hi pairs)
    inst_programs: list[bytes]  # 19 × 24-byte programs
    voice_patterns: list[bytes]  # 3 byte-streams
    voice_initial_offsets: tuple[int, int, int]  # ptr offset into v's pattern
    initial_tempo: int
    initial_master_vol: int
    # PSID metadata
    title: str
    author: str
    released: str


def extract_data(sid_path: str, params: EngineParams = NINJA_HAMSTER
                 ) -> ExtractedData:
    """Run the emulator-equivalent SID load + pull engine data tables.
    The data is the SID's musical content — this is principled extraction
    (not engine bytes)."""
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

    # Freq tables — 256 bytes each (engine uses note+$10 which can
    # overflow into the next 128 bytes; orig data layout has them
    # contiguous so the read still hits valid bytes)
    freq_lo = bytes(mem[params.inst_slide_lo_table:params.inst_slide_lo_table + 256])
    freq_hi = bytes(mem[params.inst_slide_hi_table:params.inst_slide_hi_table + 256])

    sub_jump = bytes(mem[params.sub_jump_table:params.sub_jump_table + 20])
    voice_offs = bytes(mem[params.voice_offsets:params.voice_offsets + 3])

    # Instrument source table — 19 × 2 byte ptrs at $C8FB+
    n_inst = 19
    inst_src = bytes(mem[params.inst_src_table:params.inst_src_table + n_inst * 2])

    # Instrument programs — 24 bytes each, pointed to by inst_src
    inst_progs = []
    for i in range(n_inst):
        src_lo = inst_src[i * 2]
        src_hi = inst_src[i * 2 + 1]
        src_addr = src_lo | (src_hi << 8)
        prog = bytes(mem[src_addr:src_addr + 24])
        inst_progs.append(prog)

    # Voice patterns — bytes from each voice's initial ptr to "end".
    # The orig pattern data is laid out contiguously $C000-$C451.
    # We extract each voice's range from initial_ptr to next voice's
    # initial_ptr (or end of pattern region).
    voice_patterns = []
    pat_starts = [params.voice_initial_ptrs[v] for v in range(3)]
    # End of pattern region: just before the first code instruction
    pat_end = params.play_addr  # play starts right after data
    boundaries = list(pat_starts) + [pat_end]
    boundaries.sort()
    for v in range(3):
        start = params.voice_initial_ptrs[v]
        # Find next boundary > start
        end = next(b for b in boundaries if b > start)
        voice_patterns.append(bytes(mem[start:end]))
    # Offsets of each voice's initial ptr within its pattern slice = 0
    voice_initial_offsets = (0, 0, 0)

    # PSID metadata
    title = raw[0x16:0x36].rstrip(b'\x00').decode('latin-1')
    author = raw[0x36:0x56].rstrip(b'\x00').decode('latin-1')
    released = raw[0x56:0x76].rstrip(b'\x00').decode('latin-1')

    return ExtractedData(
        freq_lo=freq_lo,
        freq_hi=freq_hi,
        sub_jump_table=sub_jump,
        voice_offsets=voice_offs,
        inst_src_table=inst_src,
        inst_programs=inst_progs,
        voice_patterns=voice_patterns,
        voice_initial_offsets=voice_initial_offsets,
        initial_tempo=params.initial_tempo,
        initial_master_vol=params.initial_master_vol,
        title=title,
        author=author,
        released=released,
    )


# ---------------------------------------------------------------------------
# Composer — emit clean xa65 asm for the Jay_Derrett engine
# ---------------------------------------------------------------------------

def emit_asm(data: ExtractedData, load_addr: int = 0x1000) -> str:
    """Generate xa65 source for a clean Jay_Derrett rebuild.

    Layout (one contiguous block from load_addr):
      load+0    init_entry: JMP init_code
      load+3    play_entry: JMP play_code
      load+6    engine code (init, play, proc_note, instrument_loader,
                modulation_block)
      ...       state region, tables, instruments, pattern data

    The engine logic mirrors the orig's semantics but is freshly
    written. Data tables are inlined from `data` (musical content)."""

    lines = [f'* = ${load_addr:04X}']
    lines += [
        '',
        '; ============================================================',
        '; Jay_Derrett engine — clean rebuild',
        '; ============================================================',
        '',
        '; ZP usage:',
        ';   $F2/$F3  pattern ptr (per voice; loaded/saved per call)',
        '',
        '; Entry points',
        'init_entry:',
        '    jmp init_code',
        'play_entry:',
        '    jmp play_code',
        '',
    ]

    # ----- State region forward decls -----
    # We label everything; xa65 resolves addresses.
    # State variables, all at the end of the file as .byte / .dsb.
    # Placed BEFORE data tables to keep them in a single dense block.

    # ----- init code -----
    lines += [
        'init_code:',
        '    ; Voice 0 ptr',
        '    lda #<voice0_pattern',
        '    sta voice_ptrs',
        '    lda #>voice0_pattern',
        '    sta voice_ptrs+1',
        '    ; Voice 1 ptr',
        '    lda #<voice1_pattern',
        '    sta voice_ptrs+2',
        '    lda #>voice1_pattern',
        '    sta voice_ptrs+3',
        '    ; Voice 2 ptr',
        '    lda #<voice2_pattern',
        '    sta voice_ptrs+4',
        '    lda #>voice2_pattern',
        '    sta voice_ptrs+5',
        '    ; Self-mod counter starts at $E0',
        '    lda #$e0',
        '    sta self_mod_counter',
        '    ; Tempo counter + reload',
        f'    lda #${data.initial_tempo:02X}',
        '    sta tempo_counter',
        '    sta tempo_reload',
        '    ; Master vol',
        f'    lda #${data.initial_master_vol:02X}',
        '    sta $d418',
        '    ; Duration counters = 1 (process first byte every tick)',
        '    lda #$01',
        '    sta dur_counters',
        '    sta dur_counters+1',
        '    sta dur_counters+2',
        '    ; Initial PWM lo accumulator: V1=$FF (mirrors orig\'s reliance',
        '    ; on libsidplayfp powerup RAM at $CB01); V2/V3 stay $00.',
        '    lda #$ff',
        '    sta voice_pwm_lo',
        '    rts',
        '',
    ]

    # ----- play code -----
    lines += [
        'play_code:',
        '    inc frame_counter',
        '    dec tempo_counter',
        '    bne play_modulation     ; tempo not expired; skip voice processing',
        '    ; Process all 3 voices',
        '    ldx #$00',
        '    jsr process_voice',
        '    ldx #$01',
        '    jsr process_voice',
        '    ldx #$02',
        '    jsr process_voice',
        '    ; Reload tempo counter',
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

    # ----- process_voice: set up zp ptr, X stride, Y stride; JSR proc_note -----
    # X comes in as voice index (0/1/2).
    # We need: $F2/$F3 = voice's pattern ptr
    #         X stride for compact state (just X = voice idx)
    #         Y stride for runtime state slab (Y_table[X])
    lines += [
        'process_voice:',
        '    ; Save X (voice idx)',
        '    stx cur_voice',
        '    ; Load voice ptr into $F2/$F3',
        '    txa',
        '    asl',                  # X * 2 for ptr index
        '    tay',
        '    lda voice_ptrs,y',
        '    sta $f2',
        '    lda voice_ptrs+1,y',
        '    sta $f3',
        '    ; Y_state = voice_y_table[X]',
        '    ldx cur_voice',
        '    lda voice_y_table,x',
        '    sta cur_voice_y',
        '    ; Call proc_note',
        '    jsr proc_note',
        '    ; Save ptr back',
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

    # ----- proc_note -----
    lines += [
        'proc_note:',
        '    ; DEC duration counter; if non-zero, RTS',
        '    ldx cur_voice',
        '    dec dur_counters,x',
        '    beq pn_proceed',
        '    rts',
        'pn_proceed:',
        '    ; Reset duration to 1',
        '    inc dur_counters,x',
        'pn_read:',
        '    ldy #$00',
        '    lda ($f2),y         ; read pattern byte',
        '    pha                 ; save A',
        '    and #$f0            ; high nibble check',
        '    cmp #$e0            ; $Ex? (pattern-jump)',
        '    beq pn_ex',
        '    cmp #$d0            ; $Dx? (set instrument)',
        '    beq pn_dx',
        '    pla                 ; restore A',
        '    cmp #$80            ; gate-off?',
        '    beq pn_gate_off',
        '    cmp #$81            ; skip?',
        '    beq pn_skip',
        '    cmp #$82            ; set duration?',
        '    beq pn_set_dur',
        '    pha                 ; save A again',
        '    and #$f0',
        '    cmp #$b0            ; $Bx? (set tempo)',
        '    beq pn_bx',
        '    cmp #$c0            ; $Cx? (set master vol)',
        '    beq pn_cx',
        '    pla                 ; restore A — it\'s a NOTE',
        '    jmp pn_note',
        '',
        '; --- $Ex: pattern-jump dispatch (counter-matched) ---',
        'pn_ex:',
        '    pla                 ; restore byte',
        '    cmp self_mod_counter',
        '    beq pn_ex_match',
        '    ; No match — advance ptr + recurse',
        '    jmp pn_advance_recurse',
        'pn_ex_match:',
        '    and #$0f            ; low nibble',
        '    asl',
        '    tay',
        '    lda sub_jump_table,y',
        '    sta $f2',
        '    lda sub_jump_table+1,y',
        '    sta $f3',
        '    inc self_mod_counter',
        '    lda self_mod_counter',
        '    cmp #$e9',
        '    bne pn_read         ; not yet wrap, recurse with new ptr',
        '    ; Wrap: reset counter + silence voice 2 (orig clears',
        '    ; $C975 + $C978 which are voice 2 CTRL + gate-off CTRL slots).',
        '    lda #$e0',
        '    sta self_mod_counter',
        '    lda #$00',
        '    sta voice_state+$14+$34',
        '    sta voice_state+$17+$34',
        '    jmp pn_read',
        '',
        '; --- $Dx: set instrument ---',
        'pn_dx:',
        '    pla                 ; restore byte',
        '    and #$0f            ; low nibble',
        '    sta cur_inst,x      ; store at cur_inst[voice]',
        '    inc cur_inst,x      ; +1 quirk',
        '    jmp pn_advance_recurse',
        '',
        '; --- $80: gate off ---',
        'pn_gate_off:',
        '    ldy cur_voice_y',
        '    lda voice_state+$14,y       ; CTRL slot (gate-on)',
        '    sta voice_state+$17,y       ; copy to gate-off CTRL slot',
        '    jmp pn_advance_rts',
        '',
        '; --- $81: skip ---',
        'pn_skip:',
        '    jmp pn_advance_rts',
        '',
        '; --- $82 N: set duration ---',
        'pn_set_dur:',
        '    ; Advance past $82, read N, store, advance past N',
        '    inc $f2',
        '    bne pn_sd_no_inc_hi',
        '    inc $f3',
        'pn_sd_no_inc_hi:',
        '    ldy #$00',
        '    lda ($f2),y',
        '    sta dur_counters,x',
        '    jmp pn_advance_rts',
        '',
        '; --- $Bx: set tempo ---',
        'pn_bx:',
        '    pla',
        '    and #$0f',
        '    sta tempo_reload',
        '    dec tempo_reload    ; (STA then DEC matches orig)',
        '    jmp pn_advance_recurse',
        '',
        '; --- $Cx: set master vol ---',
        'pn_cx:',
        '    pla',
        '    and #$0f',
        '    sta $d418',
        '    jmp pn_advance_recurse',
        '',
        '; --- NOTE handler ---',
        'pn_note:',
        '    ; A = note byte (preserved from earlier PLA)',
        '    pha                 ; save note',
        '    ; Write CTRL to $D404+sid_off',
        '    ldx cur_voice',
        '    ldy voice_sid_off,x',
        '    lda cur_ctrl,x',
        '    sta $d404,y',
        '    ; Call instrument loader with A = note',
        '    pla                 ; restore note',
        '    jsr instrument_load',
        '    jmp pn_advance_rts',
        '',
        '; --- helpers ---',
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

    # ----- instrument_load (sub_C86E) -----
    lines += [
        'instrument_load:',
        '    ; Args: A = note byte; X = cur_voice; cur_voice_y = Y_stride',
        '    pha                 ; save note',
        '    ; Get inst from cur_inst[X]',
        '    lda cur_inst,x',
        '    asl                 ; inst * 2',
        '    tay',
        '    ; src_addr = inst_src_table[inst*2..+1]',
        '    lda inst_src_table,y',
        '    sta inst_copy_src+1',
        '    lda inst_src_table+1,y',
        '    sta inst_copy_src+2',
        '    ; Copy 24 bytes from src to voice_state[cur_voice_y]',
        '    ldy #$17            ; 23 → loop down to 0',
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
        '    lda $ffff,y         ; self-mod operand (src)',
        'inst_copy_dst:',
        '    sta $ffff,y         ; self-mod operand (dst)',
        '    dey',
        '    bpl inst_copy_loop',
        '    ; Apply note → freq lookup',
        '    pla                 ; restore note',
        '    pha                 ; save again',
        '    tax                 ; X = note',
        '    ldy cur_voice_y',
        '    lda freq_lo_table,x',
        '    sta voice_state+$01,y',
        '    clc',
        '    adc voice_state+$03,y',
        '    sta voice_state+$03,y',
        '    lda freq_hi_table,x',
        '    sta voice_state+$02,y',
        '    clc',
        '    adc voice_state+$04,y',
        '    sta voice_state+$04,y',
        '    lda voice_state+$01,y',
        '    sec',
        '    sbc voice_state+$05,y',
        '    sta voice_state+$05,y',
        '    lda voice_state+$02,y',
        '    sbc voice_state+$06,y',
        '    sta voice_state+$06,y',
        '    ; note + $10 → freq off-slide override',
        '    pla',
        '    clc',
        '    adc #$10',
        '    tax',
        '    lda freq_lo_table,x',
        '    sta voice_state+$18,y',
        '    lda freq_hi_table,x',
        '    sta voice_state+$19,y',
        '    ; Set CTRL byte from voice_state+$14',
        '    lda voice_state+$14,y',
        '    ldx cur_voice',
        '    sta cur_ctrl,x',
        '    ; Clear PWM phase + lo accum for this voice',
        '    lda #$00',
        '    sta voice_pwm_phase,x',
        '    sta voice_pwm_lo,x',
        '    ; Write AD/SR',
        '    ldy voice_sid_off,x',
        '    ldx cur_voice_y',
        '    lda voice_state+$15,x',
        '    sta $d405,y',
        '    lda voice_state+$16,x',
        '    sta $d406,y',
        '    rts',
        '',
    ]

    # ----- modulate_voice (sub_C6EE) -----
    lines += [
        'modulate_voice:',
        '    ; X = voice idx (0/1/2)',
        '    stx cur_voice',
        '    lda voice_y_table,x',
        '    sta cur_voice_y',
        '    ldy voice_sid_off,x',
        '    sty cur_sid_off',
        '    ; Output freq (with bit-7 LFO toggle)',
        '    ldy cur_voice_y',
        '    lda voice_state,y',
        '    bpl mod_freq_normal     ; bit 7 clear → normal freq',
        '    ; bit 7 set: check frame counter LSB',
        '    lda frame_counter',
        '    lsr',
        '    bcc mod_freq_offslide   ; carry clear → off-slide freq',
        'mod_freq_normal:',
        '    ldx cur_sid_off',
        '    lda voice_state+$01,y',
        '    sta $d400,x',
        '    lda voice_state+$02,y',
        '    sta $d401,x',
        '    jmp mod_pw_out',
        'mod_freq_offslide:',
        '    ldx cur_sid_off',
        '    lda voice_state+$18,y',
        '    sta $d400,x',
        '    lda voice_state+$19,y',
        '    sta $d401,x',
        'mod_pw_out:',
        '    ; PW out: $D403 = voice_state+$0A,y ; $D402 = voice_pwm_lo[v]',
        '    lda voice_state+$0A,y',
        '    sta $d403,x',
        '    ldx cur_voice',
        '    lda voice_pwm_lo,x',
        '    ldx cur_sid_off',
        '    sta $d402,x',
        '    ; CTRL out: $D404 = voice_state+$14,y | voice_state+$17,y',
        '    lda voice_state+$14,y',
        '    ora voice_state+$17,y',
        '    sta $d404,x',
        '    ; Slide update — flag bit 0 selects direction',
        '    lda voice_state,y',
        '    lsr',
        '    bcs mod_slide_down',
        '    jsr slide_up',
        '    jmp mod_pwm_update',
        'mod_slide_down:',
        '    jsr slide_down',
        'mod_pwm_update:',
        '    jsr pwm_update',
        '    rts',
        '',
    ]

    # ----- slide_up / slide_down -----
    lines += [
        '; slide_up: in cur_voice_y; modifies voice_state[$01,$02] and flag',
        'slide_up:',
        '    ldy cur_voice_y',
        '    lda voice_state+$01,y',
        '    clc',
        '    adc voice_state+$07,y       ; delta lo',
        '    sta voice_state+$01,y',
        '    lda voice_state+$02,y',
        '    adc voice_state+$08,y       ; delta hi',
        '    sta voice_state+$02,y',
        '    lda voice_state+$01,y',
        '    cmp voice_state+$03,y       ; max lo',
        '    lda voice_state+$02,y',
        '    sbc voice_state+$04,y       ; max hi',
        '    bcc slu_continue            ; below max — keep sliding',
        '    ; Reached max',
        '    lda voice_state,y',
        '    and #$02',
        '    beq slu_check_continuous',
        '    ; Bit 1 set: swap direction (EOR #$01 on flag) + reset to max',
        '    lda voice_state,y',
        '    eor #$01',
        '    sta voice_state,y',
        '    lda voice_state+$03,y',
        '    sta voice_state+$01,y',
        '    lda voice_state+$04,y',
        '    sta voice_state+$02,y',
        '    rts',
        'slu_check_continuous:',
        '    lda voice_state,y',
        '    and #$04',
        '    bne slu_continuous',
        '    ; Bit 2 clear: one-shot — zero deltas',
        '    lda #$00',
        '    sta voice_state+$07,y',
        '    sta voice_state+$08,y',
        '    rts',
        'slu_continuous:',
        '    ; Bit 2 set: reset to min',
        '    lda voice_state+$05,y',
        '    sta voice_state+$01,y',
        '    lda voice_state+$06,y',
        '    sta voice_state+$02,y',
        'slu_continue:',
        '    rts',
        '',
        'slide_down:',
        '    ldy cur_voice_y',
        '    lda voice_state+$01,y',
        '    sec',
        '    sbc voice_state+$07,y       ; delta lo',
        '    sta voice_state+$01,y',
        '    lda voice_state+$02,y',
        '    sbc voice_state+$08,y       ; delta hi',
        '    sta voice_state+$02,y',
        '    lda voice_state+$01,y',
        '    cmp voice_state+$05,y       ; min lo',
        '    lda voice_state+$02,y',
        '    sbc voice_state+$06,y       ; min hi',
        '    bcs sld_continue            ; above min — keep sliding',
        '    ; Reached min',
        '    lda voice_state,y',
        '    and #$02',
        '    beq sld_check_continuous',
        '    ; Bit 1 set: swap direction + reset to min',
        '    lda voice_state,y',
        '    eor #$01',
        '    sta voice_state,y',
        '    lda voice_state+$05,y',
        '    sta voice_state+$01,y',
        '    lda voice_state+$06,y',
        '    sta voice_state+$02,y',
        '    rts',
        'sld_check_continuous:',
        '    lda voice_state,y',
        '    and #$04',
        '    bne sld_continuous',
        '    lda #$00',
        '    sta voice_state+$07,y',
        '    sta voice_state+$08,y',
        '    rts',
        'sld_continuous:',
        '    lda voice_state+$03,y',
        '    sta voice_state+$01,y',
        '    lda voice_state+$04,y',
        '    sta voice_state+$02,y',
        'sld_continue:',
        '    rts',
        '',
    ]

    # ----- pwm_update -----
    lines += [
        'pwm_update:',
        '    ldx cur_voice',
        '    lda voice_pwm_phase,x',
        '    bne pwm_phase1',
        '    ; --- Phase 0 ---',
        '    ldy cur_voice_y',
        '    lda voice_state+$0E,y       ; direction flag',
        '    bne pwm0_sub',
        '    ; Phase 0 ADD',
        '    lda voice_pwm_lo,x',
        '    clc',
        '    adc voice_state+$0C,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$0A,y',
        '    adc #$00',
        '    sta voice_state+$0A,y',
        '    cmp voice_state+$0B,y',
        '    bcs pwm0_advance',
        '    rts',
        'pwm0_sub:',
        '    lda voice_pwm_lo,x',
        '    sec',
        '    sbc voice_state+$0C,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$0A,y',
        '    sbc #$00',
        '    sta voice_state+$0A,y',
        '    cmp voice_state+$0B,y',
        '    beq pwm0_advance',
        '    bcs pwm0_done',
        'pwm0_advance:',
        '    inc voice_pwm_phase,x',
        'pwm0_done:',
        '    rts',
        '',
        'pwm_phase1:',
        '    ldy cur_voice_y',
        '    lda voice_state+$0F,y       ; phase 1 direction flag',
        '    bne pwm1_sub',
        '    ; Phase 1 ADD',
        '    lda voice_pwm_lo,x',
        '    clc',
        '    adc voice_state+$12,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$0A,y',
        '    adc #$00',
        '    sta voice_state+$0A,y',
        '    cmp voice_state+$10,y',
        '    bcc pwm1_done',
        '    lda #$01',
        '    sta voice_state+$0F,y',
        '    rts',
        'pwm1_sub:',
        '    lda voice_pwm_lo,x',
        '    sec',
        '    sbc voice_state+$12,y',
        '    sta voice_pwm_lo,x',
        '    lda voice_state+$0A,y',
        '    sbc #$00',
        '    sta voice_state+$0A,y',
        '    cmp voice_state+$11,y',
        '    beq pwm1_flip',
        '    bcs pwm1_done',
        'pwm1_flip:',
        '    lda #$00',
        '    sta voice_state+$0F,y',
        'pwm1_done:',
        '    rts',
        '',
    ]

    # ----- State region -----
    lines += [
        '; ============================================================',
        '; State region',
        '; ============================================================',
        '',
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
        '',
        '; Per-voice runtime state slabs (3 × $1A = 78 bytes)',
        '; Voice 0: $00, voice 1: $1A, voice 2: $34',
        'voice_state:      .dsb 26 * 3, 0',
        '',
        '; Voice Y-stride table',
        'voice_y_table:    .byte $00, $1A, $34',
        '',
        '; Voice SID register offsets',
        'voice_sid_off:    .byte ' + ', '.join(f'${b:02X}' for b in data.voice_offsets),
        '',
    ]

    # ----- Sub-jump table -----
    lines += [
        'sub_jump_table:',
        '    .byte ' + ', '.join(f'${b:02X}' for b in data.sub_jump_table),
        '',
    ]
    # NOTE: sub_jump_table entries point at absolute addresses in orig.
    # They reference pattern data inside the voice patterns. We MUST
    # remap them to point at our relocated pattern data. Compute the
    # mapping below — for now, emit raw and patch in the bytes table.
    # Actually we'll do this at runtime — see below.

    # ----- Freq tables (256 bytes each: 128 lo + 128 hi) -----
    # The engine indexes with X = note + $10 which can reach $8F, so we
    # need 256 bytes accessible from freq_lo_table base. Use the orig's
    # contiguous layout: freq_lo (128) then freq_hi (128) — engine reads
    # at offset $80+ into freq_lo land in freq_hi region (legitimately).
    lines += [
        'freq_lo_table:',
    ]
    for i in range(0, 128, 16):
        chunk = data.freq_lo[i:i + 16]
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines += [
        'freq_hi_table:',
    ]
    for i in range(0, 128, 16):
        chunk = data.freq_hi[i:i + 16]
        lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    # ----- Instrument source table -----
    # Orig has $C8FB pointing at instrument programs scattered through
    # the SID body. We re-emit a clean table pointing at our local
    # `inst_program_N` labels.
    lines += [
        'inst_src_table:',
    ]
    for i in range(len(data.inst_programs)):
        lines.append(f'    .byte <inst_prog_{i}, >inst_prog_{i}')
    lines.append('')

    # ----- Instrument programs (24 bytes each) -----
    for i, prog in enumerate(data.inst_programs):
        lines.append(f'inst_prog_{i}:')
        for j in range(0, 24, 8):
            chunk = prog[j:j + 8]
            lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    # ----- Voice patterns -----
    for v, pat in enumerate(data.voice_patterns):
        lines.append(f'voice{v}_pattern:')
        for i in range(0, len(pat), 16):
            chunk = pat[i:i + 16]
            lines.append('    .byte ' + ', '.join(f'${b:02X}' for b in chunk))
    lines.append('')

    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# Sub-jump-table relocation
# ---------------------------------------------------------------------------

def _remap_sub_jump_table(data: ExtractedData, params: EngineParams,
                           voice_pattern_bases: list[int]) -> bytes:
    """The orig sub_jump_table entries are absolute addresses into
    voice pattern data. Since we relocate the patterns to our own
    addresses, the table entries must be remapped.

    For each entry's orig address, find which orig voice's pattern
    range it falls in, compute the offset, then add the new voice's
    base address."""
    orig_voice_bases = list(params.voice_initial_ptrs)
    # Determine each voice's pattern length (we have these in data)
    voice_ends = [orig_voice_bases[v] + len(data.voice_patterns[v])
                  for v in range(3)]
    remapped = bytearray()
    for i in range(0, len(data.sub_jump_table), 2):
        orig_lo = data.sub_jump_table[i]
        orig_hi = data.sub_jump_table[i + 1]
        orig_addr = orig_lo | (orig_hi << 8)
        # Find which voice owns this orig_addr
        owner = None
        for v in range(3):
            if orig_voice_bases[v] <= orig_addr < voice_ends[v]:
                owner = v
                break
        if owner is None:
            # Entry references something outside the pattern region —
            # leave as-is (might be padding). Emit zeros.
            remapped += b'\x00\x00'
            continue
        offset = orig_addr - orig_voice_bases[owner]
        new_addr = voice_pattern_bases[owner] + offset
        remapped += bytes([new_addr & 0xFF, (new_addr >> 8) & 0xFF])
    return bytes(remapped)


# ---------------------------------------------------------------------------
# Two-pass assembly to resolve addresses
# ---------------------------------------------------------------------------

def _sanitize_asm(s: str) -> str:
    """xa65 is picky about characters in comments. Strip non-ASCII and
    re-process comments to avoid `$NN:` syntax that confuses the parser."""
    import re
    s = (s.replace('—', '-')
          .replace('–', '-')
          .replace('→', '->')
          .replace('×', 'x')
          .replace('‘', "'").replace('’', "'")
          .encode('ascii', errors='replace').decode('ascii'))
    # Strip `$XX:` patterns from comments (xa65 sometimes mis-parses these).
    out_lines = []
    for line in s.split('\n'):
        comment_idx = line.find(';')
        if comment_idx >= 0:
            code = line[:comment_idx]
            comment = line[comment_idx:]
            # Replace `$XX:` with `XX_` in comments
            comment = re.sub(r'\$([0-9A-Fa-fXx]+):', r'\1_', comment)
            line = code + comment
        out_lines.append(line)
    return '\n'.join(out_lines)


def _assemble(asm_src: str, name: str = 'jd') -> tuple[bytes, dict[str, int]]:
    src = f'/tmp/{name}.s'
    obj = f'/tmp/{name}.bin'
    lbl = f'/tmp/{name}.labels'
    asm_src = _sanitize_asm(asm_src)
    with open(src, 'w') as f:
        f.write(asm_src)
    r = subprocess.run([XA, '-M', src, '-o', obj, '-l', lbl],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    labels = {}
    if Path(lbl).exists():
        for line in open(lbl):
            # xa65 labels file format: name, 0xaddr, 0, 0xext
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                try:
                    labels[parts[0]] = int(parts[1], 16)
                except ValueError:
                    pass
    return open(obj, 'rb').read(), labels


def build_ninja_hamster_sid(load_addr: int = 0x1000) -> bytes:
    """Build a clean Ninja_Hamster PSID."""
    sid_path = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
                   'Ninja_Hamster.sid')
    data = extract_data(sid_path, NINJA_HAMSTER)

    # Pass 1: emit asm + assemble to find voice_pattern label addresses
    asm1 = emit_asm(data, load_addr)
    bin1, labels1 = _assemble(asm1, 'jd_pass1')
    voice_pattern_bases = [
        labels1.get(f'voice{v}_pattern', 0) for v in range(3)
    ]

    # Pass 2: emit again with sub_jump_table remapped
    remapped_sjt = _remap_sub_jump_table(data, NINJA_HAMSTER,
                                          voice_pattern_bases)
    # Replace data.sub_jump_table with remapped version
    data.sub_jump_table = remapped_sjt
    asm2 = emit_asm(data, load_addr)
    bin2, _ = _assemble(asm2, 'jd_pass2')

    # Build PSID header
    title = data.title
    author = data.author
    released = data.released
    init_addr = load_addr
    play_addr = load_addr + 3

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', load_addr)
    h += struct.pack('>H', init_addr)
    h += struct.pack('>H', play_addr)
    h += struct.pack('>H', 1)            # 1 subtune
    h += struct.pack('>H', 1)            # start_song
    h += struct.pack('>I', 0)            # speed (50Hz)
    def _latin1(s, n):
        return s.encode('latin-1', errors='replace')[:n].ljust(n, b'\x00')
    h += _latin1(title, 32)
    h += _latin1(author, 32)
    h += _latin1(released, 32)
    h += struct.pack('>H', (1 << 2) | (1 << 4))  # flags: musPlayer + PAL
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124
    return bytes(h) + bin2


if __name__ == '__main__':
    sid = build_ninja_hamster_sid()
    out = str(ROOT / 'hvsc84' / 'MUSICIANS' / 'D' / 'Derrett_Jay' /
              'Ninja_Hamster.sidfinity.sid')
    Path(out).write_bytes(sid)
    print(f'Wrote {out} ({len(sid)} bytes)')
