"""Codegen for Chris Murray's Henrys_House — a single-voice Companion
variant. Engine semantics:

  - 1 voice (V1 only — engine has no V2/V3 logic)
  - Tempo hardcoded to 8 (CPX #$08 in tempo gate, not a memory cell)
  - Note encoding identical to bowden_canonical: $00-$7F NORMAL_NOTE,
    $80 REST, $81 SKIP, $FF LOOP_RESTART
  - $FF handler resets V1pos=0 (NOT the bowden_canonical's "pos=1 + play
    orderlist[0] in same tick"); next tick reads orderlist[0]
  - Same 5-byte timbre dump + gated ctrl as bowden / clever_music

Per-tune data: 1 voice's orderlist + 5-byte timbre. Freq table is
shared with the Clever Music engine (identical bytes).
"""

from __future__ import annotations

import os
import struct
import subprocess

from src.usf import (
    UsfFile, PsidMeta, Params, InitState, InitVoice, Instrument,
    PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig, MusicSubtune,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
    write_file, validate, parse_file,
)
from pipelines.companion.clever_music.engine_constants import (
    CLEVER_FREQ_HI, CLEVER_FREQ_LO, pitch_to_note_byte, note_byte_to_pitch,
)


XA = os.environ.get('XA', 'tools/xa65/xa/xa')

LOAD = 0x1000
INIT_VEC = LOAD
PLAY_VEC = LOAD + 3


# ---------------------------------------------------------------------------
# Extract (SID → USF)
# ---------------------------------------------------------------------------

def _run_init(sid_path: str):
    """Run init via py65 to capture per-tune state + init SID writes."""
    import sys as _sys
    _sys.path.insert(0, 'tools/py65_lib')
    from py65.devices.mpu6502 import MPU

    class _Mem(bytearray):
        sid_writes: list  # type: ignore

        def __new__(cls, size):
            obj = super().__new__(cls, size)
            obj.sid_writes = []
            return obj

        def __setitem__(self, idx, val):
            if isinstance(idx, int) and 0xD400 <= idx <= 0xD418:
                self.sid_writes.append((idx - 0xD400, val))
            super().__setitem__(idx, val)

    raw = open(sid_path, 'rb').read()
    body = raw[124:]
    load_in = struct.unpack('>H', raw[8:10])[0]
    if load_in == 0:
        load = struct.unpack('<H', body[:2])[0]
        body = body[2:]
    else:
        load = load_in
    init_addr = struct.unpack('>H', raw[10:12])[0]
    mpu = MPU()
    mpu.memory = _Mem(0x10000)
    mpu.memory[load:load + len(body)] = body
    mpu.memory.sid_writes.clear()
    mpu.a = 0; mpu.x = 0; mpu.y = 0; mpu.p = 0x20; mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE; mpu.memory[0x01FE] = 0xFE
    mpu.memory.sid_writes.clear()
    mpu.pc = init_addr
    for _ in range(50000):
        if not load <= mpu.pc < load + len(body):
            break
        mpu.step()
    return bytearray(mpu.memory), list(mpu.memory.sid_writes), raw, load


def _extract_pattern_rows(body: bytes) -> list[NoteRow]:
    """Decode the pattern's byte body into a list of NoteRows.

    Engine bytes: $00-$7F = note, $80 = rest (writes gate-off),
    $81 = skip (no write — continues whatever the voice was doing).
    A run of one head byte ($00-$7F or $80) followed by $81s is
    musically a single event of the head's kind whose duration is
    the run length. So we collapse runs into rows whose `duration`
    is the tick count.
    """
    rows: list[NoteRow] = []
    for b in body:
        if b == 0x81:
            if rows:
                rows[-1].duration += 1
            else:
                # Pattern beginning with $81 — engine does nothing this
                # tick. Encode as a rest tick we extend later.
                rows.append(NoteRow(pitch=Pitch.rest(), duration=1))
        elif b == 0x80:
            rows.append(NoteRow(pitch=Pitch.rest(), duration=1))
        elif b & 0x80:
            # Pattern body should never hit this (only $80/$81/note);
            # $FF is the terminator handled separately. Keep a raw
            # escape for defence in depth.
            rows.append(NoteRow(pitch=Pitch.rest(), duration=1,
                                fx_flags=(f'fx:raw_{b:02x}',)))
        else:
            name, octave = note_byte_to_pitch(b)
            rows.append(NoteRow(pitch=Pitch(name=name, octave=octave),
                                duration=1))
    return rows


# Known data offsets in Henrys_House's binary (relative to load $ACC0).
# Discovered by hand-disasm; documented in project memory.
HH_TIMBRE_ADDR = 0xAEA1     # 5 bytes
HH_ORDERLIST = 0xADC0       # ends at $FF
HH_FREQ_HI = 0xACC0
HH_FREQ_LO = 0xAD40


def build_usf(sid_path: str) -> UsfFile:
    mem, init_sid, raw, load = _run_init(sid_path)

    # Extract orderlist (up to and including $FF)
    ol_start = HH_ORDERLIST
    ol_end = ol_start + 256
    ol_slice = bytes(mem[ol_start:ol_end])
    ff = ol_slice.find(0xFF)
    if ff < 0:
        raise ValueError('no $FF terminator in orderlist')
    orderlist = ol_slice[:ff + 1]

    # Extract timbre
    tb = bytes(mem[HH_TIMBRE_ADDR:HH_TIMBRE_ADDR + 5])
    pw = (tb[1] << 8) | tb[0]
    instrument = Instrument(
        id=1,
        waveform=[tb[2]],
        loop=0,
        pwm=PwmConfig(mode='none', speed=0, init=pw, min_hi=0, max_hi=0),
        adsr=(tb[3], tb[4]),
        arp=ArpConfig(offsets=[0], period=1),
        vibrato=VibratoConfig(scale=0),
        envelope=EnvelopeConfig(),
    )

    rows = _extract_pattern_rows(orderlist[:-1])         # exclude $FF terminator
    total_ticks = sum(r.duration for r in rows)
    voice = VoiceBlock(
        id=1,
        orderlist=Orderlist(entries=[1], loop_to=0),
        patterns=[Pattern(id=1, length=total_ticks, rows=rows)],
    )
    # Grammar requires 3 voices per subtune; pad with empty placeholders
    # that the codegen ignores (henrys_house is single-voice).
    placeholder = lambda i: VoiceBlock(
        id=i,
        orderlist=Orderlist(entries=[], stop=True),
        patterns=[],
    )

    music = MusicSubtune(
        id=0,
        tempo=8,                     # hardcoded in the engine
        voices=[voice, placeholder(2), placeholder(3)],
        params=Params(fields={}),
    )

    # PSID meta
    title = raw[0x16:0x36].rstrip(b'\x00').decode('latin-1')
    author = raw[0x36:0x56].rstrip(b'\x00').decode('latin-1')
    released = raw[0x56:0x76].rstrip(b'\x00').decode('latin-1')
    flags = int.from_bytes(raw[0x76:0x78], 'big')
    clock = {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[(flags >> 2) & 0x03]
    sid_model = {0: 6581, 1: 6581, 2: 8580, 3: 6581}[(flags >> 4) & 0x03]
    psid = PsidMeta(
        title=title, author=author, released=released,
        clock=clock, sid=sid_model,
        start_song=int.from_bytes(raw[0x10:0x12], 'big'),
        speed=int.from_bytes(raw[0x12:0x16], 'big'),
    )

    return UsfFile(
        engine='henrys_house',
        psid=psid,
        params=Params(),
        init=InitState(voices=[InitVoice(id=1, instr=InstrumentRef(id=1))]),
        instruments=[instrument],
        subtunes=[music],
    )


def write_usf(sid_path: str, out_path: str | None = None) -> str:
    if out_path is None:
        base, _ = os.path.splitext(sid_path)
        out_path = base + '.usf'
    usf = build_usf(sid_path)
    validate(usf)
    write_file(usf, out_path)
    try:
        from src.sid_db import record_usf
        record_usf(out_path)
    except Exception:
        pass
    return out_path


# ---------------------------------------------------------------------------
# Codegen (USF → SID)
# ---------------------------------------------------------------------------

def _row_to_bytes(row: NoteRow) -> bytes:
    """Serialise one NoteRow back to its engine byte sequence.

    A row's `duration` D = 1 head byte + (D-1) $81 skips. The head
    byte is the pitched-note byte for a note row, $80 for a rest, or
    the raw byte for the (defensive) fx:raw_NN fallback.
    """
    if not row.pitch.is_rest:
        head = pitch_to_note_byte(row.pitch.name, row.pitch.octave)
    else:
        head = 0x80
        for f in row.fx_flags:
            if f.startswith('fx:raw_'):
                head = int(f.split('_')[1], 16)
                break
    return bytes([head]) + bytes([0x81] * (row.duration - 1))


def emit_asm(usf: UsfFile) -> str:
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if len(music) != 1:
        raise ValueError(f'henrys_house expects 1 music subtune')
    ms = music[0]
    if not ms.voices:
        raise ValueError(f'henrys_house needs at least one voice')
    instr = next((i for i in usf.instruments if i.id == 1), None)
    if instr is None:
        raise ValueError('missing instrument 1')

    # Extract timbre bytes
    pw_lo = instr.pwm.init & 0xFF
    pw_hi = (instr.pwm.init >> 8) & 0xFF
    ctrl = instr.waveform[0] if instr.waveform else 0
    ad, sr = instr.adsr
    timbre = [pw_lo, pw_hi, ctrl, ad, sr]

    # Extract pattern bytes
    pat = ms.voices[0].patterns[0]
    pat_body = b''.join(_row_to_bytes(r) for r in pat.rows)
    pattern_bytes = pat_body + bytes([0xFF])

    tempo = ms.tempo

    L: list[str] = []
    L.append(f'* = ${LOAD:04X}')
    L.append('  jmp init')
    L.append('  jmp play')

    L.append('init:')
    # Only writes $D418=$0F (matches Henrys_House init)
    L.append('  lda #$0f')
    L.append('  sta $d418')
    L.append('  lda #0')
    L.append('  sta v_pos')
    L.append('  sta tempo_ctr')
    L.append('  rts')

    L.append('play:')
    L.append('  inc tempo_ctr')
    L.append('  ldx tempo_ctr')
    L.append(f'  cpx #{tempo}')
    L.append('  beq play_tick')
    L.append('  rts')
    L.append('play_tick:')
    L.append('  lda #0')
    L.append('  sta tempo_ctr')
    L.append('  ldx v_pos')
    L.append('  inc v_pos')
    L.append('  lda orderlist,x')
    L.append('  cmp #$ff')
    L.append('  bne not_ff')
    # $FF handler — write D418=$0F (matches Henrys_House restart-init
    # side effect) and reset v_pos. NO note plays this tick.
    L.append('  lda #$0f')
    L.append('  sta $d418')
    L.append('  lda #0')
    L.append('  sta v_pos')
    L.append('  rts')
    L.append('not_ff:')
    L.append('  ldx #0          ; voice offset 0 for proc_note')
    # proc_note (inline-style)
    L.append('  cmp #$80')
    L.append('  beq pn_rest')
    L.append('  bcs pn_skip')
    L.append('  tay')
    L.append('  lda freq_hi_tab,y')
    L.append('  sta $d401')
    L.append('  lda freq_lo_tab,y')
    L.append('  sta $d400')
    L.append(f'  lda #${timbre[0]:02X}')
    L.append('  sta $d402')
    L.append(f'  lda #${timbre[1]:02X}')
    L.append('  sta $d403')
    L.append(f'  lda #${timbre[2]:02X}')
    L.append('  sta $d404           ; junk ctrl (gate=0) for envelope retrigger')
    L.append(f'  lda #${timbre[3]:02X}')
    L.append('  sta $d405')
    L.append(f'  lda #${timbre[4]:02X}')
    L.append('  sta $d406')
    L.append(f'  lda #${(timbre[2] + 1) & 0xFF:02X}')
    L.append('  sta $d404           ; gate=1')
    L.append('  rts')
    L.append('pn_rest:')
    L.append(f'  lda #${timbre[2]:02X}')
    L.append('  sta $d404')
    L.append('  rts')
    L.append('pn_skip:')
    L.append('  rts')

    # Runtime variables
    L.append('v_pos:       .byte 0')
    L.append('tempo_ctr:   .byte 0')

    # Freq tables (shared with Clever Music)
    L.append('freq_hi_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in CLEVER_FREQ_HI[i:i+16]))
    L.append('freq_lo_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in CLEVER_FREQ_LO[i:i+16]))

    L.append('orderlist:')
    for i in range(0, len(pattern_bytes), 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in pattern_bytes[i:i+16]))

    return '\n'.join(L) + '\n'


def assemble(asm_src: str) -> bytes:
    src = '/tmp/henrys_house_codegen.s'
    obj = '/tmp/henrys_house_codegen.bin'
    with open(src, 'w') as f:
        f.write(asm_src)
    r = subprocess.run([XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    return open(obj, 'rb').read()


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


def build_from_usf(usf_path: str, out_path: str | None = None) -> str:
    usf = parse_file(usf_path)
    if usf.engine != 'henrys_house':
        raise ValueError(f"expected engine 'henrys_house', got {usf.engine!r}")
    if out_path is None:
        base, _ = os.path.splitext(usf_path)
        out_path = base + '.sidfinity.sid'
    with open(out_path, 'wb') as f:
        f.write(emit_sid(usf))
    try:
        from src.sid_db import record_rebuild
        record_rebuild(out_path)
    except Exception:
        pass
    return out_path
