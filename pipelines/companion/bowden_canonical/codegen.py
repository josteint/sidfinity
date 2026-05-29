"""6502 codegen for the Bowden-canonical Companion engine.

Generates a clean xa65 assembly source that reproduces the original
engine's per-frame SID instruction stream from USF v2 data. The
generated code is structurally different from the original engine
binary (no carry-leak tricks, no self-modifying offsets) — it just
needs to produce the same FINAL per-frame register state for each
$D400-$D418 register, which `verify_all` checks via md5 of py65
snapshots.

Layout (all contiguous starting at LOAD=$1000; xa65 doesn't honour
forward `* =` gaps, so labels fall naturally and we use JMP
trampolines at the top to give PSID stable entry points):

  $1000  JMP init    (3 bytes)
  $1003  JMP play    (3 bytes)
  $1006  init body
         play body
         proc_note
         voice1_step / voice2_step / voice3_step
         data (timbres, freq tables, orderlists)

Engine semantics (see extract/engine_model.py for the full analysis):

  - 3 voices walking flat orderlists of (oct<<4)|semi pitch bytes
  - $80 = rest (gate off, no other writes)
  - $FF = loop to position 1 of own orderlist, immediately play [0]
  - Per-voice fixed 5-byte timbre (pw_lo, pw_hi, ctrl, ad, sr)
  - Global tempo: frames per tick
  - V1 init_pos = 0 (zeroed by init); V2/V3 init_pos are tune data
"""

from __future__ import annotations

import os
import subprocess
import struct

from src.usf2 import (
    UsfFile, MusicSubtune, Instrument, parse_file,
)
from pipelines.companion.bowden_canonical.engine_constants import (
    freq_tables, pitch_to_note_byte,
)


XA = os.environ.get('XA', 'tools/xa65/xa/xa')

LOAD = 0x1000
INIT_VEC = LOAD          # JMP init
PLAY_VEC = LOAD + 3      # JMP play


def _note_byte_from_row(row) -> int:
    if row.pitch.is_rest:
        return 0x80
    return pitch_to_note_byte(row.pitch.name, row.pitch.octave)


def _orderlist_bytes(voice_block) -> bytes:
    """Convert a USF voice block's pattern 1 into the engine's
    $FF-terminated byte sequence."""
    if not voice_block.patterns:
        raise ValueError(f'voice {voice_block.id} has no patterns')
    pat = voice_block.patterns[0]
    return bytes(_note_byte_from_row(r) for r in pat.rows) + bytes([0xFF])


def _timbre_block(instr: Instrument) -> bytes:
    """USF Instrument → 5-byte timbre (pw_lo, pw_hi, ctrl, ad, sr)."""
    pw_lo = instr.pwm.init & 0xFF
    pw_hi = (instr.pwm.init >> 8) & 0xFF
    ctrl = instr.waveform[0] if instr.waveform else 0
    ad, sr = instr.adsr
    return bytes([pw_lo, pw_hi, ctrl, ad, sr])


def emit_asm(usf: UsfFile) -> str:
    """Emit xa65 assembly source — fully contiguous from LOAD."""
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if len(music) != 1:
        raise ValueError(f'bowden_canonical expects 1 music subtune, got {len(music)}')
    ms = music[0]
    if len(ms.voices) != 3:
        raise ValueError(f'expected 3 voices, got {len(ms.voices)}')

    instr_by_id = {i.id: i for i in usf.instruments}
    voice_instr_ids = [iv.instr.id for iv in (ms.init.voices if ms.init
                                              else usf.init.voices)]
    timbres = [_timbre_block(instr_by_id[iid]) for iid in voice_instr_ids]

    orderlists = [_orderlist_bytes(vb) for vb in ms.voices]

    p = ms.params.fields if ms.params else {}
    init_v1 = p.get('init_pos_v1', 0)
    init_v2 = p.get('init_pos_v2', 0)
    init_v3 = p.get('init_pos_v3', 0)
    init_tempo_ctr = p.get('init_tempo_ctr', 0)

    tempo = ms.tempo

    freq_hi, freq_lo = freq_tables()

    L = []
    L.append(f'* = ${LOAD:04X}')

    # Trampolines — PSID dispatches into these at INIT_VEC / PLAY_VEC.
    L.append('  jmp init')
    L.append('  jmp play')

    # ---- init ----
    L.append('init:')
    L.append('  lda #0')
    L.append('  ldx #0')
    L.append('init_silence:')
    L.append('  sta $d400,x')
    L.append('  inx')
    L.append('  cpx #$19')
    L.append('  bne init_silence')
    L.append('  lda #$0f')
    L.append('  sta $d418')
    L.append('  lda #$09')
    L.append('  sta $d405')
    L.append('  lda #0')
    L.append('  sta $d406')
    L.append('  lda #$09')
    L.append('  sta $d40c')
    L.append('  lda #0')
    L.append('  sta $d40d')
    L.append(f'  lda #{init_v1}')
    L.append('  sta v1_pos')
    L.append(f'  lda #{init_v2}')
    L.append('  sta v2_pos')
    L.append(f'  lda #{init_v3}')
    L.append('  sta v3_pos')
    L.append(f'  lda #{init_tempo_ctr}')
    L.append('  sta tempo_ctr')
    L.append('  rts')

    # ---- play ----
    L.append('play:')
    L.append('  inc tempo_ctr')
    L.append('  lda tempo_ctr')
    L.append('  cmp tempo_const')
    L.append('  bne play_exit')
    L.append('  lda #0')
    L.append('  sta tempo_ctr')
    L.append('  jsr voice1_step')
    L.append('  jsr voice2_step')
    L.append('  jsr voice3_step')
    L.append('play_exit:')
    L.append('  rts')

    # ---- proc_note: A = note byte, X = voice offset (0/7/14) ----
    L.append('; proc_note expects A as the note byte and X as voice offset 0,7,14')
    L.append('; voice_step sets X (via LDX immediate) AFTER loading A, which clears')
    L.append('; the N flag, so we test A explicitly with CMP rather than BMI.')
    L.append('; The original engine emits a 5-byte timbre dump (pw_lo, pw_hi,')
    L.append('; ctrl-junk, ad, sr) on regular ticks, but only 4 bytes (no sr) when')
    L.append('; V1 or V2 hits its $FF loop terminator and proc_note is called')
    L.append('; recursively on orderlist[0] — the loop dispatcher leaves carry=0')
    L.append('; from CPX #$0E, which shortens the engine PW loop by one iteration.')
    L.append('; We emit two variants — proc_note (5-byte) and proc_note_4 (4-byte).')
    L.append('proc_note:')
    L.append('  cmp #$80')
    L.append('  beq pn_rest')
    L.append('  tay')
    L.append('  lda freq_hi_tab,y')
    L.append('  sta $d401,x')
    L.append('  lda freq_lo_tab,y')
    L.append('  sta $d400,x')
    L.append('  lda timbre_pwlo,x')
    L.append('  sta $d402,x')
    L.append('  lda timbre_pwhi,x')
    L.append('  sta $d403,x')
    L.append('  lda timbre_ctrl,x')
    L.append('  sta $d404,x          ; junk write (gate=0) — DELIBERATE retrigger')
    L.append('  lda timbre_ad,x')
    L.append('  sta $d405,x')
    L.append('  lda timbre_sr,x')
    L.append('  sta $d406,x')
    L.append('  lda timbre_ctrl,x')
    L.append('  ora #$01')
    L.append('  sta $d404,x          ; gate=1, finalises the envelope retrigger')
    L.append('  rts')
    L.append('pn_rest:')
    L.append('  lda timbre_ctrl,x')
    L.append('  sta $d404,x')
    L.append('  rts')
    L.append('proc_note_4:')
    L.append('  cmp #$80')
    L.append('  beq pn_rest')
    L.append('  tay')
    L.append('  lda freq_hi_tab,y')
    L.append('  sta $d401,x')
    L.append('  lda freq_lo_tab,y')
    L.append('  sta $d400,x')
    L.append('  lda timbre_pwlo,x')
    L.append('  sta $d402,x')
    L.append('  lda timbre_pwhi,x')
    L.append('  sta $d403,x')
    L.append('  lda timbre_ctrl,x')
    L.append('  sta $d404,x          ; junk write (gate=0)')
    L.append('  lda timbre_ad,x')
    L.append('  sta $d405,x          ; NB no sr write (carry=0 path)')
    L.append('  lda timbre_ctrl,x')
    L.append('  ora #$01')
    L.append('  sta $d404,x          ; gate=1')
    L.append('  rts')

    # ---- per-voice step routines ----
    # V1/V2 take a 4-byte-timbre path on $FF substitution; V3 stays 5-byte.
    # (See proc_note above for the carry-leak explanation.)
    for v, (pos_label, orderlist_label, voice_off, pn4_on_loop) in enumerate([
        ('v1_pos', 'orderlist_v1', 0, True),
        ('v2_pos', 'orderlist_v2', 7, True),
        ('v3_pos', 'orderlist_v3', 14, False),
    ]):
        vn = v + 1
        L.append(f'voice{vn}_step:')
        L.append(f'  ldx {pos_label}')
        L.append(f'  inc {pos_label}')
        L.append(f'  lda {orderlist_label},x')
        L.append('  cmp #$ff')
        L.append(f'  bne v{vn}_play')
        # $FF substitution path
        L.append('  lda #1')
        L.append(f'  sta {pos_label}')
        L.append(f'  lda {orderlist_label}')
        L.append(f'  ldx #{voice_off}')
        if pn4_on_loop:
            L.append('  jmp proc_note_4    ; carry=0 path emits 4-byte timbre')
        else:
            L.append('  jmp proc_note      ; V3 keeps full 5-byte timbre')
        L.append(f'v{vn}_play:')
        L.append(f'  ldx #{voice_off}')
        L.append('  jmp proc_note')

    # ---- runtime variables (RAM) ----
    L.append('v1_pos:    .byte 0')
    L.append('v2_pos:    .byte 0')
    L.append('v3_pos:    .byte 0')
    L.append('tempo_ctr: .byte 0')
    L.append(f'tempo_const: .byte {tempo}')

    # ---- timbre table — 5 parallel arrays of 15 bytes (X up to 14) ----
    fields = ['pwlo', 'pwhi', 'ctrl', 'ad', 'sr']
    for fi, fname in enumerate(fields):
        slot = [0] * 15
        for v in range(3):
            slot[v * 7] = timbres[v][fi]
        bytes_str = ', '.join(f'${b:02X}' for b in slot)
        L.append(f'timbre_{fname}: .byte {bytes_str}')

    # ---- freq tables ----
    L.append('freq_hi_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in freq_hi[i:i+16]))

    L.append('freq_lo_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in freq_lo[i:i+16]))

    # ---- orderlists ----
    for v, label in enumerate(['orderlist_v1', 'orderlist_v2', 'orderlist_v3']):
        L.append(f'{label}:')
        ol = orderlists[v]
        for i in range(0, len(ol), 16):
            L.append('  .byte ' + ', '.join(f'${b:02X}' for b in ol[i:i+16]))

    return '\n'.join(L) + '\n'


def assemble(asm_src: str) -> bytes:
    """Run xa65, return the assembled flat binary (no load-address header)."""
    src_path = '/tmp/bowden_codegen.s'
    obj_path = '/tmp/bowden_codegen.bin'
    with open(src_path, 'w') as f:
        f.write(asm_src)
    r = subprocess.run([XA, src_path, '-o', obj_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    return open(obj_path, 'rb').read()


def emit_sid(usf: UsfFile) -> bytes:
    """Emit a complete PSID file for the given USF."""
    asm = emit_asm(usf)
    body = assemble(asm)

    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    n_songs = len(music)

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', LOAD)
    h += struct.pack('>H', INIT_VEC)
    h += struct.pack('>H', PLAY_VEC)
    h += struct.pack('>H', n_songs)
    h += struct.pack('>H', usf.psid.start_song)
    h += struct.pack('>I', usf.psid.speed)

    def latin1(s: str, n: int) -> bytes:
        return s.encode('latin-1', errors='replace')[:n].ljust(n, b'\x00')

    h += latin1(usf.psid.title, 32)
    h += latin1(usf.psid.author, 32)
    h += latin1(usf.psid.released, 32)

    clock_bits = {'unknown': 0, 'PAL': 1, 'NTSC': 2, 'both': 3}.get(usf.psid.clock, 0)
    sid_bits = {6581: 1, 8580: 2}.get(usf.psid.sid, 1)
    flags = (clock_bits << 2) | (sid_bits << 4)
    h += struct.pack('>H', flags)
    h += struct.pack('>BBH', 0, 0, 0)

    assert len(h) == 124, len(h)
    return bytes(h) + body
