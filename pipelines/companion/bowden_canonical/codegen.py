"""6502 codegen for the Bowden-canonical Companion engine.

Generates a clean xa65 assembly source that reproduces the original
engine's per-frame SID instruction stream from USF v2 data. Single-
or multi-subtune. Init takes A as the subtune index and configures
runtime state (orderlist pointers, timbre table, tempo, voice
positions) from per-subtune data tables.

Layout (all contiguous starting at LOAD=$1000):

  $1000   JMP init     (3 bytes — PSID entry)
  $1003   JMP play     (3 bytes — PSID entry)
  $1006+  init body (per-subtune dispatch)
          play body
          proc_note + proc_note_4 + voice steps
          runtime variables + timbre table
          freq tables (engine constant)
          per-subtune data tables (init_pos, tempo, timbre, orderlist ptrs)
          per-subtune orderlists (each up to 256 bytes per voice)

Engine semantics — see extract/engine_model.py for the analysis.

Multi-subtune support: voice_step routines use indirect (zp),Y
addressing to read orderlist bytes, so each subtune can point V1/V2/V3
at independently-located orderlist data via zp pointers programmed
by init.
"""

from __future__ import annotations

import os
import subprocess
import struct

from src.usf import UsfFile, MusicSubtune, Instrument
from pipelines.companion.bowden_canonical.engine_constants import (
    freq_tables, pitch_to_note_byte,
)


XA = os.environ.get('XA', 'tools/xa65/xa/xa')

LOAD = 0x1000
INIT_VEC = LOAD
PLAY_VEC = LOAD + 3

# Zero-page pointers for per-voice orderlist (set by init).
ZP_ORD_V1_LO = 0xE0
ZP_ORD_V1_HI = 0xE1
ZP_ORD_V2_LO = 0xE2
ZP_ORD_V2_HI = 0xE3
ZP_ORD_V3_LO = 0xE4
ZP_ORD_V3_HI = 0xE5


def _note_byte_from_row(row) -> int:
    if 'fx:hold' in row.fx_flags:
        return 0x81
    if row.pitch.is_rest:
        return 0x80
    return pitch_to_note_byte(row.pitch.name, row.pitch.octave)


def _orderlist_bytes(voice_block) -> bytes:
    if not voice_block.patterns:
        raise ValueError(f'voice {voice_block.id} has no patterns')
    pat = voice_block.patterns[0]
    return bytes(_note_byte_from_row(r) for r in pat.rows) + bytes([0xFF])


def _timbre_block(instr: Instrument) -> bytes:
    pw_lo = instr.pwm.init & 0xFF
    pw_hi = (instr.pwm.init >> 8) & 0xFF
    ctrl = instr.waveform[0] if instr.waveform else 0
    ad, sr = instr.adsr
    return bytes([pw_lo, pw_hi, ctrl, ad, sr])


def emit_asm(usf: UsfFile) -> str:
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if not music:
        raise ValueError('no music subtunes')
    music.sort(key=lambda s: s.id)
    n_sub = len(music)

    instr_by_id = {i.id: i for i in usf.instruments}

    # Per-subtune data
    per_sub: list[dict] = []
    for ms in music:
        if len(ms.voices) != 3:
            raise ValueError(f'subtune {ms.id}: expected 3 voices')
        voice_iids = [iv.instr.id for iv in (ms.init.voices if ms.init
                                              else usf.init.voices)]
        timbres = [_timbre_block(instr_by_id[iid]) for iid in voice_iids]
        orderlists = [_orderlist_bytes(vb) for vb in ms.voices]
        p = ms.params.fields if ms.params else {}
        per_sub.append({
            'tempo': ms.tempo,
            'init_pos': (p.get('init_pos_v1', 0),
                         p.get('init_pos_v2', 0),
                         p.get('init_pos_v3', 0)),
            'init_tempo_ctr': p.get('init_tempo_ctr', 0),
            'cia1_timer_a': p.get('cia1_timer_a', 0),
            'timbres': timbres,
            'orderlists': orderlists,
        })

    freq_hi, freq_lo = freq_tables()

    L: list[str] = []
    L.append(f'* = ${LOAD:04X}')

    # PSID trampolines
    L.append('  jmp init')
    L.append('  jmp play')

    # ---- init (A = subtune index) ----
    L.append('init:')
    # Silence SID
    L.append('  pha                  ; save A')
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
    L.append('  pla                  ; restore A as subtune index')
    L.append('  tax                  ; X = subtune index (byte tables)')
    # Per-subtune scalar setup
    L.append('  lda init_v1_pos_tab,x')
    L.append('  sta v1_pos')
    L.append('  lda init_v2_pos_tab,x')
    L.append('  sta v2_pos')
    L.append('  lda init_v3_pos_tab,x')
    L.append('  sta v3_pos')
    L.append('  lda init_tempo_ctr_tab,x')
    L.append('  sta tempo_ctr')
    L.append('  lda tempo_tab,x')
    L.append('  sta tempo_const')
    # Per-subtune timbre table fill (15 bytes × 5 fields written into
    # runtime timbre arrays at offsets 0, 7, 14)
    fields = ['pwlo', 'pwhi', 'ctrl', 'ad', 'sr']
    for fname in fields:
        for v, off in enumerate((0, 7, 14)):
            L.append(f'  lda v{v+1}_{fname}_tab,x')
            L.append(f'  sta timbre_{fname}+{off}')
    # Per-subtune orderlist pointers (3 voices × 2 bytes)
    L.append('  lda v1_ol_lo_tab,x')
    L.append(f'  sta ${ZP_ORD_V1_LO:02X}')
    L.append('  lda v1_ol_hi_tab,x')
    L.append(f'  sta ${ZP_ORD_V1_HI:02X}')
    L.append('  lda v2_ol_lo_tab,x')
    L.append(f'  sta ${ZP_ORD_V2_LO:02X}')
    L.append('  lda v2_ol_hi_tab,x')
    L.append(f'  sta ${ZP_ORD_V2_HI:02X}')
    L.append('  lda v3_ol_lo_tab,x')
    L.append(f'  sta ${ZP_ORD_V3_LO:02X}')
    L.append('  lda v3_ol_hi_tab,x')
    L.append(f'  sta ${ZP_ORD_V3_HI:02X}')
    # CIA1 timer A — if any subtune programs it, emit a per-subtune
    # lookup and write. Default-zero subtunes write 0/0 which leaves
    # libsidplayfp's default psiddrv programming intact (subtle: actually
    # a zero write would set the timer to fire immediately, which is
    # wrong — so we only emit the writes when at least one subtune has
    # a non-default value, and we use the default value for the others
    # — see _cia_default below).
    if any(s['cia1_timer_a'] for s in per_sub):
        L.append('  lda cia1_lo_tab,x')
        L.append('  sta $dc04')
        L.append('  lda cia1_hi_tab,x')
        L.append('  sta $dc05')
    L.append('  rts')

    # ---- play ----
    L.append('play:')
    L.append('  inc tempo_ctr')
    L.append('  lda tempo_ctr')
    L.append('  cmp tempo_const')
    L.append('  bne play_exit')
    L.append('  lda #0')
    L.append('  sta tempo_ctr')
    L.append('  sta next_skip_sr     ; V1 starts each tick with 5-byte timbre')
    L.append('  jsr voice1_step')
    L.append('  jsr voice2_step')
    L.append('  jsr voice3_step')
    L.append('play_exit:')
    L.append('  rts')

    # Unified proc_note. The this_skip_sr byte controls whether the
    # final SR write happens — set by voice_step to model the original
    # engine's carry-leak between voices: a voice that plays a skip
    # note ($81-$FE) leaves carry=0 from the engine's `CPY #$FF / BNE`
    # at $C0E9, which makes the NEXT voice's `ADC #$04` add only 4
    # instead of 5 and short-circuits its PW loop by one iteration —
    # the SR write. Voice $FF substitution similarly forces 4-byte for
    # V1/V2 via the loop dispatcher's `CPX #$0E` clearing carry; V3's
    # $FF dispatch leaves carry=1 (X == $0E) and keeps 5-byte.
    L.append('proc_note:')
    L.append('  cmp #$80')
    L.append('  beq pn_rest')
    L.append('  bcs pn_skip')
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
    L.append('  sta $d404,x          ; junk write (gate=0) for envelope retrigger')
    L.append('  lda timbre_ad,x')
    L.append('  sta $d405,x')
    L.append('  lda this_skip_sr')
    L.append('  bne pn_no_sr_write')
    L.append('  lda timbre_sr,x')
    L.append('  sta $d406,x')
    L.append('pn_no_sr_write:')
    L.append('  lda timbre_ctrl,x')
    L.append('  ora #$01')
    L.append('  sta $d404,x          ; gate=1, finalises envelope retrigger')
    L.append('  rts')
    L.append('pn_rest:')
    L.append('  lda timbre_ctrl,x')
    L.append('  sta $d404,x')
    L.append('  rts')
    L.append('pn_skip:')
    L.append('  rts')

    # ---- per-voice step routines ----
    # Each voice:
    #   1. Reads its note byte; handles $FF substitution
    #   2. Sets THIS call's skip_sr (4-vs-5-byte timbre choice)
    #      - normal flow: copy from prior voice's next_skip_sr
    #      - $FF substitution: V1/V2 force 1, V3 forces 0
    #   3. Classifies the effective note to update next_skip_sr for
    #      the following voice
    #   4. Calls proc_note
    for v, (pos_label, zp_lo, voice_off, force_4_on_loop) in enumerate([
        ('v1_pos', ZP_ORD_V1_LO, 0, True),
        ('v2_pos', ZP_ORD_V2_LO, 7, True),
        ('v3_pos', ZP_ORD_V3_LO, 14, False),
    ]):
        vn = v + 1
        L.append(f'voice{vn}_step:')
        L.append(f'  ldy {pos_label}')
        L.append(f'  inc {pos_label}')
        L.append(f'  lda (${zp_lo:02X}),y')
        L.append(f'  cmp #$ff')
        L.append(f'  bne v{vn}_normal')
        # $FF substitution path
        L.append(f'  lda #1')
        L.append(f'  sta {pos_label}')
        L.append(f'  ldy #0')
        L.append(f'  lda (${zp_lo:02X}),y   ; A = effective note (orderlist[0])')
        L.append(f'  ldy #{1 if force_4_on_loop else 0}')
        L.append(f'  sty this_skip_sr      ; force {"4-byte" if force_4_on_loop else "5-byte"} for V{vn} loop')
        L.append(f'  jmp v{vn}_classify')
        L.append(f'v{vn}_normal:')
        # Normal-path: inherit this_skip_sr from prior voice's next_skip_sr
        L.append(f'  ldy next_skip_sr')
        L.append(f'  sty this_skip_sr')
        L.append(f'v{vn}_classify:')
        # A = effective note; set next_skip_sr based on whether
        # it's a skip ($81-$FE).
        L.append(f'  pha')
        L.append(f'  cmp #$81')
        L.append(f'  bcc v{vn}_not_skip')
        L.append(f'  cmp #$ff')
        L.append(f'  beq v{vn}_not_skip')
        L.append(f'  ldy #1')
        L.append(f'  sty next_skip_sr')
        L.append(f'  jmp v{vn}_call')
        L.append(f'v{vn}_not_skip:')
        L.append(f'  ldy #0')
        L.append(f'  sty next_skip_sr')
        L.append(f'v{vn}_call:')
        L.append(f'  pla')
        L.append(f'  ldx #{voice_off}')
        L.append(f'  jmp proc_note')

    # ---- runtime variables ----
    L.append('v1_pos:        .byte 0')
    L.append('v2_pos:        .byte 0')
    L.append('v3_pos:        .byte 0')
    L.append('tempo_ctr:     .byte 0')
    L.append('tempo_const:   .byte 0')
    L.append('this_skip_sr:  .byte 0')
    L.append('next_skip_sr:  .byte 0')

    # Runtime timbre table — 5 parallel 15-byte arrays. Filled at init.
    for fname in fields:
        L.append(f'timbre_{fname}: .dsb 15, 0')

    # ---- freq tables (engine constant) ----
    L.append('freq_hi_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in freq_hi[i:i+16]))
    L.append('freq_lo_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in freq_lo[i:i+16]))

    # ---- per-subtune data tables (byte tables indexed by subtune) ----
    def _byte_tab(label: str, values: list[int]) -> None:
        L.append(f'{label}: .byte ' + ', '.join(f'${v:02X}' for v in values))

    _byte_tab('tempo_tab', [s['tempo'] for s in per_sub])
    _byte_tab('init_v1_pos_tab', [s['init_pos'][0] for s in per_sub])
    _byte_tab('init_v2_pos_tab', [s['init_pos'][1] for s in per_sub])
    _byte_tab('init_v3_pos_tab', [s['init_pos'][2] for s in per_sub])
    _byte_tab('init_tempo_ctr_tab', [s['init_tempo_ctr'] for s in per_sub])
    if any(s['cia1_timer_a'] for s in per_sub):
        # PAL default = $4CC7 (libsidplayfp's standard ~50Hz). Subtunes
        # without a captured CIA write fall back to this so the rebuild
        # plays at the same default rate sidplayfp would have used
        # without explicit programming.
        DEFAULT_CIA = 0x4CC7
        cia_vals = [s['cia1_timer_a'] or DEFAULT_CIA for s in per_sub]
        _byte_tab('cia1_lo_tab', [v & 0xFF for v in cia_vals])
        _byte_tab('cia1_hi_tab', [(v >> 8) & 0xFF for v in cia_vals])

    # Per-subtune timbre fields (3 voices × 5 fields × N subtunes)
    for v in range(3):
        for fi, fname in enumerate(fields):
            _byte_tab(f'v{v+1}_{fname}_tab',
                      [s['timbres'][v][fi] for s in per_sub])

    # Per-subtune orderlist address tables (hi/lo per voice)
    # We'll forward-reference labels orderlist_v<v>_s<i>.
    for v in range(3):
        L.append(f'v{v+1}_ol_lo_tab:')
        L.append('  .byte ' + ', '.join(
            f'<orderlist_v{v+1}_s{i}' for i in range(n_sub)))
        L.append(f'v{v+1}_ol_hi_tab:')
        L.append('  .byte ' + ', '.join(
            f'>orderlist_v{v+1}_s{i}' for i in range(n_sub)))

    # ---- per-subtune orderlists ----
    for s_idx, s in enumerate(per_sub):
        for v in range(3):
            L.append(f'orderlist_v{v+1}_s{s_idx}:')
            ol = s['orderlists'][v]
            for i in range(0, len(ol), 16):
                L.append('  .byte ' + ', '.join(
                    f'${b:02X}' for b in ol[i:i+16]))

    return '\n'.join(L) + '\n'


def assemble(asm_src: str) -> bytes:
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
