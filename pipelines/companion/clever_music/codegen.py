"""6502 codegen for the Clever Music Companion engine.

Generates an xa65 assembly source that reproduces the original engine's
per-frame SID instruction stream from USF v2 data. The output mirrors
the original engine's instruction structure closely (real PW loop with
the same cycle count, recursive load_note with full bit-7 dispatch)
so the rebuild matches at the cycle level, not just write-set.

Layout (LOAD=$1000, contiguous):

  $1000  JMP init    (PSID)
  $1003  JMP play    (PSID)
  $1006  init        (CIA1 timer setup, silence SID, init state vars)
  play body
  proc_note (per-voice voice_step calls load_note)
  load_note (recursive command interpreter)
  runtime state vars (v_pos, v_timbre, v_dur_ctr, tempo, tempo_ctr, song_pos)
  freq tables (engine constant)
  per-tune data (instrument table, song_table, per-voice pattern data)

Per-voice state struct (stride 7, X=0/7/14):
  +0/+1  pattern_ptr lo/hi
  +2..+6 timbre (pw_lo, pw_hi, ctrl, ad, sr)
Duration counters: stride 1 (separate byte array V1/V2/V3).
"""

from __future__ import annotations

import os
import struct
import subprocess

from src.usf2 import UsfFile, MusicSubtune, parse_file, Pitch, NoteRow
from pipelines.companion.clever_music.engine_constants import (
    CLEVER_FREQ_HI, CLEVER_FREQ_LO, pitch_to_note_byte,
)

XA = os.environ.get('XA', 'tools/xa65/xa/xa')

LOAD = 0x1000
INIT_VEC = LOAD
PLAY_VEC = LOAD + 3

# Runtime variable addresses (chosen contiguously, addresses will be
# resolved by xa65 labels in the emitted assembly).


def _row_to_byte(row: NoteRow) -> int:
    """Inverse of `_row_from_byte` in to_usf_v2."""
    flags = set(row.fx_flags)
    if not row.pitch.is_rest:
        # NORMAL_NOTE
        return pitch_to_note_byte(row.pitch.name, row.pitch.octave)
    if 'fx:hold' in flags:
        return 0x81
    if 'fx:set_dur' in flags:
        return 0x82
    if row.instr is not None:
        # SET_INSTRUMENT
        return 0xD0 | ((row.instr.id - 1) & 0x0F)
    for flag in flags:
        if flag.startswith('fx:tempo_'):
            return 0xB0 | (int(flag.split('_')[1]) & 0x0F)
        if flag.startswith('fx:vol_'):
            return 0xC0 | (int(flag.split('_')[1]) & 0x0F)
        if flag.startswith('fx:jump_'):
            return 0xE0 | (int(flag.split('_')[1]) & 0x0F)
        if flag.startswith('fx:raw_'):
            return int(flag.split('_')[1], 16)
    # Default rest = $80
    return 0x80


def _timbre_block(instr) -> bytes:
    pw_lo = instr.pwm.init & 0xFF
    pw_hi = (instr.pwm.init >> 8) & 0xFF
    ctrl = instr.waveform[0] if instr.waveform else 0
    ad, sr = instr.adsr
    return bytes([pw_lo, pw_hi, ctrl, ad, sr])


def emit_asm(usf: UsfFile) -> str:
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if len(music) != 1:
        raise ValueError(f'clever_music expects 1 music subtune, got {len(music)}')
    ms = music[0]
    if len(usf.instruments) != 16:
        raise ValueError(f'expected 16 instruments, got {len(usf.instruments)}')
    instruments = sorted(usf.instruments, key=lambda i: i.id)

    p = ms.params.fields if ms.params else {}
    init_tempo_ctr = p.get('init_tempo_ctr', 0)
    init_song_pos = p.get('init_song_pos', 0xE0)
    cia1 = p.get('cia1_timer_a', 0)
    tempo = ms.tempo

    # Per-voice pattern bytes (decode each row to its engine byte)
    voice_patterns = []
    for vb in ms.voices:
        if not vb.patterns:
            raise ValueError(f'voice {vb.id} has no patterns')
        pat = vb.patterns[0]
        voice_patterns.append(bytes(_row_to_byte(r) for r in pat.rows))

    L: list[str] = []
    L.append(f'* = ${LOAD:04X}')

    # PSID trampolines
    L.append('  jmp init')
    L.append('  jmp play')

    # ---- init ----
    L.append('init:')
    L.append('  pha                       ; subtune index (we ignore - single subtune)')
    # Silence SID matching original engine - $D400..$D418 = 0, then $D418=$0A
    L.append('  lda #0')
    L.append('  ldx #0')
    L.append('init_silence:')
    L.append('  sta $d400,x')
    L.append('  inx')
    L.append('  cpx #$19')
    L.append('  bne init_silence')
    L.append('  lda #$0a')                # default master vol $0A (Clever Music init writes this)
    L.append('  sta $d418')
    # Set per-voice state from song_table
    L.append('  lda song_table+0')
    L.append('  sta v_state+0             ; V1 ptr lo')
    L.append('  lda song_table+1')
    L.append('  sta v_state+1             ; V1 ptr hi')
    L.append('  lda song_table+2')
    L.append('  sta v_state+7             ; V2 ptr lo')
    L.append('  lda song_table+3')
    L.append('  sta v_state+8             ; V2 ptr hi')
    L.append('  lda song_table+4')
    L.append('  sta v_state+14            ; V3 ptr lo')
    L.append('  lda song_table+5')
    L.append('  sta v_state+15            ; V3 ptr hi')
    L.append('  lda #1')
    L.append('  sta dur_ctr+0')
    L.append('  sta dur_ctr+1')
    L.append('  sta dur_ctr+2')
    L.append(f'  lda #${init_song_pos:02X}')
    L.append('  sta song_pos')
    L.append(f'  lda #{tempo}')
    L.append('  sta tempo_const')
    L.append(f'  lda #{init_tempo_ctr}')
    L.append('  sta tempo_ctr')
    if cia1:
        L.append(f'  lda #${cia1 & 0xFF:02X}')
        L.append('  sta $dc04')
        L.append(f'  lda #${(cia1 >> 8) & 0xFF:02X}')
        L.append('  sta $dc05')
    L.append('  pla')
    L.append('  rts')

    # ---- play ----
    L.append('play:')
    L.append('  inc tempo_ctr')
    L.append('  lda tempo_ctr')
    L.append('  cmp tempo_const')
    L.append('  bne play_exit')
    L.append('  lda #0')
    L.append('  sta tempo_ctr')
    # Per voice — V1 X=0, V2 X=7, V3 X=14; dur_ctr at +0/+1/+2
    for v, (x, dur_off) in enumerate([(0, 0), (7, 1), (14, 2)]):
        L.append(f'  ldx #{x}')
        L.append(f'  lda dur_ctr+{dur_off}')
        L.append('  cmp #1')
        L.append(f'  bne v{v+1}_dec')
        L.append('  jsr load_note')
        L.append(f'  jmp v{v+1}_done')
        L.append(f'v{v+1}_dec:')
        L.append(f'  dec dur_ctr+{dur_off}')
        L.append(f'v{v+1}_done:')
    L.append('play_exit:')
    L.append('  rts')

    # ---- load_note (X = voice offset 0/7/14) ----
    # Mirror the engine structure closely. Self-modify a zp pointer
    # for indirect addressing via (zp),Y.
    L.append('; load_note expects X as voice offset 0,7,14')
    L.append('load_note:')
    L.append('  ldy #0')
    L.append('  lda v_state+0,x          ; ptr lo')
    L.append('  sta zp_ptr_lo')
    L.append('  lda v_state+1,x          ; ptr hi')
    L.append('  sta zp_ptr_hi')
    L.append('  inc v_state+0,x          ; advance ptr')
    L.append('  bne ln_skip_inc_hi')
    L.append('  inc v_state+1,x')
    L.append('ln_skip_inc_hi:')
    L.append('  lda (zp_ptr_lo),y         ; read byte')
    L.append('  tay')
    L.append('  and #$80')
    L.append('  bne ln_bit7')
    # NORMAL NOTE path — mirror engine's loop structure for cycle parity
    L.append('  lda freq_hi_tab,y')
    L.append('  sta $d401,x')
    L.append('  lda freq_lo_tab,y')
    L.append('  sta $d400,x')
    L.append('  txa')
    L.append('  tay')
    L.append('  clc')
    L.append('  adc #$05')
    L.append('  sta zp_endy')
    L.append('ln_pw_loop:')
    L.append('  lda v_state+2,y           ; timbre[y]')
    L.append('  sta $d402,y')
    L.append('  iny')
    L.append('  cpy zp_endy')
    L.append('  bne ln_pw_loop')
    L.append('  ldy v_state+4,x           ; ctrl byte')
    L.append('  iny')
    L.append('  tya')
    L.append('  sta $d404,x               ; gate=1')
    L.append('  rts')
    # bit-7 path
    L.append('ln_bit7:')
    L.append('  cpy #$80')
    L.append('  bne ln_not80')
    L.append('  lda v_state+4,x           ; ctrl (gate off)')
    L.append('  sta $d404,x')
    L.append('  rts')
    L.append('ln_not80:')
    L.append('  cpy #$81')
    L.append('  bne ln_not81')
    L.append('  rts')
    L.append('ln_not81:')
    L.append('  cpy #$82')
    L.append('  bne ln_not82')
    # SET_DURATION: gate off, read next byte as new dur
    L.append('  lda v_state+4,x')
    L.append('  sta $d404,x')
    L.append('  lda v_state+0,x')
    L.append('  sta zp_ptr_lo')
    L.append('  lda v_state+1,x')
    L.append('  sta zp_ptr_hi')
    L.append('  inc v_state+0,x')
    L.append('  bne ln82_no_carry')
    L.append('  inc v_state+1,x')
    L.append('ln82_no_carry:')
    L.append('  txa                       ; transform X (0/7/14) → (0/1/2)')
    L.append('  clc')
    L.append('  ror')
    L.append('  clc')
    L.append('  adc #$01')
    L.append('  clc')
    L.append('  ror')
    L.append('  clc')
    L.append('  ror')
    L.append('  stx zp_x_save')
    L.append('  tax')
    L.append('  ldy #0')
    L.append('  lda (zp_ptr_lo),y')
    L.append('  sta dur_ctr,x')
    L.append('  ldx zp_x_save')
    L.append('  rts')
    L.append('ln_not82:')
    # $Ex pattern jump (if Y == song_pos)
    L.append('  cpy song_pos')
    L.append('  bne ln_not_ex')
    L.append('  inc song_pos')
    L.append('  lda song_pos')
    L.append('  cmp #$e6')
    L.append('  bne ln_no_wrap')
    L.append('  lda #$e0')
    L.append('  sta song_pos')
    L.append('ln_no_wrap:')
    L.append('  tya                       ; Y = $Ex')
    L.append('  and #$0f')
    L.append('  clc')
    L.append('  rol                     ; *2 for 16-bit indexing')
    L.append('  tay')
    L.append('  lda song_table,y')
    L.append('  sta v_state+0,x')
    L.append('  iny')
    L.append('  lda song_table,y')
    L.append('  sta v_state+1,x')
    L.append('  jsr load_note             ; recurse (re-enter with new ptr)')
    L.append('  rts')
    L.append('ln_not_ex:')
    # $Dx SET_INSTRUMENT
    L.append('  tya')
    L.append('  and #$f0')
    L.append('  cmp #$d0')
    L.append('  bne ln_not_dx')
    L.append('  tya')
    L.append('  and #$0f')
    L.append('  clc')
    L.append('  rol                     ; *2')
    L.append('  asl                     ; *4')
    L.append('  adc #0                    ; carry remains for *5')
    L.append('  ; actually need *5; easier with shift+add')
    L.append('  ; reset and use simple multiply')
    L.append('  tya')
    L.append('  and #$0f')
    L.append('  sta zp_tmp')
    L.append('  asl                     ; *2')
    L.append('  asl                     ; *4')
    L.append('  clc')
    L.append('  adc zp_tmp                ; *5')
    L.append('  tay')
    L.append('  stx zp_x_save')
    L.append('  txa                       ; X = voice offset')
    L.append('  clc')
    L.append('  adc #2                    ; → timbre slot offset from v_state base')
    L.append('  tax')
    L.append('  lda inst_table,y          ; copy 5 bytes')
    L.append('  sta v_state,x')
    L.append('  inx')
    L.append('  iny')
    L.append('  lda inst_table,y')
    L.append('  sta v_state,x')
    L.append('  inx')
    L.append('  iny')
    L.append('  lda inst_table,y')
    L.append('  sta v_state,x')
    L.append('  inx')
    L.append('  iny')
    L.append('  lda inst_table,y')
    L.append('  sta v_state,x')
    L.append('  inx')
    L.append('  iny')
    L.append('  lda inst_table,y')
    L.append('  sta v_state,x')
    L.append('  ldx zp_x_save')
    L.append('  jsr load_note')
    L.append('  rts')
    L.append('ln_not_dx:')
    # $Cx SET_MASTER_VOL
    L.append('  tya')
    L.append('  and #$f0')
    L.append('  cmp #$c0')
    L.append('  bne ln_not_cx')
    L.append('  tya')
    L.append('  and #$0f')
    L.append('  sta $d418')
    L.append('  jsr load_note')
    L.append('  rts')
    L.append('ln_not_cx:')
    # $Bx SET_TEMPO
    L.append('  tya')
    L.append('  and #$f0')
    L.append('  cmp #$b0')
    L.append('  bne ln_other_bit7')
    L.append('  tya')
    L.append('  and #$0f')
    L.append('  sta tempo_const')
    L.append('  jsr load_note')
    L.append('  rts')
    L.append('ln_other_bit7:')
    # Unrecognized bit-7 byte — engine treats as SKIP_BYTE + recurse
    L.append('  jsr load_note')
    L.append('  rts')

    # ---- runtime state ----
    # zp_ptr_lo/hi MUST be in zero page for (zp),Y indirect addressing.
    L.append('zp_ptr_lo = $FB')
    L.append('zp_ptr_hi = $FC')
    L.append('zp_endy:     .byte 0')
    L.append('zp_x_save:   .byte 0')
    L.append('zp_tmp:      .byte 0')

    # Per-voice state (3 voices × 7 bytes stride: ptr_lo, ptr_hi, pw_lo, pw_hi, ctrl, ad, sr)
    L.append('v_state: .dsb 21, 0')

    # Duration counters (stride 1)
    L.append('dur_ctr: .dsb 3, 0')

    # Globals
    L.append('tempo_const: .byte 0')
    L.append('tempo_ctr:   .byte 0')
    L.append('song_pos:    .byte 0')

    # Freq tables (engine constant)
    L.append('freq_hi_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in CLEVER_FREQ_HI[i:i+16]))
    L.append('freq_lo_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in CLEVER_FREQ_LO[i:i+16]))

    # Instrument table (16 × 5 = 80 bytes)
    L.append('inst_table:')
    for inst in instruments:
        block = _timbre_block(inst)
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in block))

    # Song table — 6 entries (12 bytes). Maps E0..E5 to voice pattern starts.
    # E0/E3 → V1, E1/E4 → V2, E2/E5 → V3.
    L.append('song_table:')
    L.append('  .byte <ptn_v1, >ptn_v1     ; E0')
    L.append('  .byte <ptn_v2, >ptn_v2     ; E1')
    L.append('  .byte <ptn_v3, >ptn_v3     ; E2')
    L.append('  .byte <ptn_v1, >ptn_v1     ; E3')
    L.append('  .byte <ptn_v2, >ptn_v2     ; E4')
    L.append('  .byte <ptn_v3, >ptn_v3     ; E5')

    # Per-voice pattern data
    for v, pat in enumerate(voice_patterns):
        L.append(f'ptn_v{v+1}:')
        for i in range(0, len(pat), 16):
            L.append('  .byte ' + ', '.join(f'${b:02X}' for b in pat[i:i+16]))

    return '\n'.join(L) + '\n'


def assemble(asm_src: str) -> bytes:
    src_path = '/tmp/clever_music_codegen.s'
    obj_path = '/tmp/clever_music_codegen.bin'
    with open(src_path, 'w') as f:
        f.write(asm_src)
    r = subprocess.run([XA, src_path, '-o', obj_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    return open(obj_path, 'rb').read()


def emit_sid(usf: UsfFile) -> bytes:
    asm = emit_asm(usf)
    body = assemble(asm)

    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', INIT_VEC)
    h += struct.pack('>H', PLAY_VEC)
    h += struct.pack('>H', len(music))
    h += struct.pack('>H', usf.psid.start_song)
    h += struct.pack('>I', usf.psid.speed)

    def latin1(s, n): return s.encode('latin-1', errors='replace')[:n].ljust(n, b'\x00')
    h += latin1(usf.psid.title, 32)
    h += latin1(usf.psid.author, 32)
    h += latin1(usf.psid.released, 32)

    clock_bits = {'unknown': 0, 'PAL': 1, 'NTSC': 2, 'both': 3}.get(usf.psid.clock, 0)
    sid_bits = {6581: 1, 8580: 2}.get(usf.psid.sid, 1)
    flags = (clock_bits << 2) | (sid_bits << 4)
    h += struct.pack('>H', flags)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124
    return bytes(h) + body
