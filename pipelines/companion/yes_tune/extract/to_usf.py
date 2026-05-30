"""Yes_Tune family — SID → USF extract.

Engine semantics (from $6240 disasm of Yes_Tune.sid):

  Per-voice state at $6200+X (X=0/7/14):
    +$00  tick_ctr     (decrements; plays next pair when reaches 0)
    +$01  state        (0=skipped, 1=normal, 2=load-pattern)
    +$02..+$06  timbre (5 bytes: pw_lo, pw_hi, ctrl, ad, sr)
    +$04  ctrl byte (= timbre[+2])
    +$15  pattern_ptr lo (current position)
    +$16  pattern_ptr hi
    +$17  pat_start lo (immutable reset target)
    +$18  pat_start hi

  Global:
    $622A  tempo_ctr
    $622B  tempo
    $6100..$617F  freq_hi (128 bytes)
    $6180..$61FF  freq_lo

  Pattern is a sequence of either 2-byte pairs or 1-byte commands:
    $00-$7F dur  NORMAL_NOTE — play freq + 5-byte timbre + gated ctrl,
                 then tick_ctr = dur, advance ptr by 2
    $80 dur      REST — write ctrl (gate off), advance ptr by 2
    $81          STOP_VOICE — write ctrl (gate off), state = 0 (silent)
    $FF          LOOP — reset ptr to pat_start, recurse play_note

The build path is the universal `pipelines.build_from_usf.build_from_usf`.
This file only does the SID→USF direction.

USF representation:
  Normal note → row Pitch + duration N
  $80 rest    → row Pitch.rest() + duration N
  $81 stop    → voice orderlist terminator `stop`
  $FF loop    → voice orderlist terminator `loop @ 0`

  Per-voice runtime initial state lives entirely in the orderlist
  shape: a silent voice has `orderlist: stop` with no patterns
  (engine state=0); a normal voice has `orderlist: 1 stop` or
  `orderlist: 1 loop@0` depending on which terminator byte the
  engine reads at end-of-pattern (state=2).

  Subtune gain-init (whether the engine writes $D418=$0F during
  init) lives in `params { gain_init: full | preserve }`.

  Muted-pitch percussion triggers ($2C..$2F, $4C..$4F) in SFX
  subtunes still use `fx:raw_NN` — these are freq=0 entries in
  the freq table that gate the envelope without an audible pitch;
  a clean musical primitive ("trigger / drum / mute") requires a
  Pitch-type extension and is deferred.
"""

from __future__ import annotations

import os
import struct

from src.usf import (
    UsfFile, PsidMeta, Params, InitState, InitVoice, Instrument,
    PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig, MusicSubtune,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
    write_file, validate,
)
from pipelines.companion.clever_music.engine_constants import (
    CLEVER_FREQ_HI, CLEVER_FREQ_LO, note_byte_to_pitch,
)


def _run_init(sid_path: str, subtune: int = 0):
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
    mpu.a = subtune; mpu.x = 0; mpu.y = 0; mpu.p = 0x20; mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE; mpu.memory[0x01FE] = 0xFE
    mpu.memory.sid_writes.clear()
    mpu.pc = init_addr
    for _ in range(200000):
        if not load <= mpu.pc < load + len(body): break
        mpu.step()
    return bytearray(mpu.memory), list(mpu.memory.sid_writes), raw


def _detect_layout(mem: bytearray, play_addr: int) -> dict:
    """Detect per-tune engine addresses by scanning the play loop.

    Yes_Tune-style engines share this play loop structure:
      ...tempo gate...
      LDA $VOICE_BASE+1,X    ; state byte
      CMP #$02
      ...
      LDA $VOICE_BASE+$15,X  ; pattern ptr lo
      LDY $VOICE_BASE+$16,X  ; pattern ptr hi
      JSR play_note
    where VOICE_BASE is engine-relative.

    Returns dict with voice_base, freq_hi, freq_lo, tempo_ctr, tempo.
    """
    pc = play_addr
    end = play_addr + 0x100
    voice_state_addr = None
    inc_target = None  # tempo_ctr
    cmp_target = None  # tempo
    while pc < end - 4:
        if mem[pc] == 0xBD and mem[pc + 3] == 0xC9 and mem[pc + 4] == 0x02:
            voice_state_addr = mem[pc + 1] | (mem[pc + 2] << 8)
            break
        if mem[pc] == 0xEE and inc_target is None:
            inc_target = mem[pc + 1] | (mem[pc + 2] << 8)
        if mem[pc] == 0xCC and cmp_target is None:
            cmp_target = mem[pc + 1] | (mem[pc + 2] << 8)
        pc += 1
    if voice_state_addr is None:
        raise ValueError(f'no LDA abs,X / CMP #$02 pattern in play loop')
    voice_base = voice_state_addr - 1
    freq_hi = voice_base - 0x100
    freq_lo = voice_base - 0x80
    return dict(
        voice_base=voice_base,
        freq_hi=freq_hi,
        freq_lo=freq_lo,
        tempo_ctr=inc_target,
        tempo=cmp_target,
    )


def _extract_pattern(mem: bytearray, start: int) -> bytes:
    """Walk pattern bytes from `start` until $FF or $81 terminator,
    inclusive of the terminator byte."""
    out = bytearray()
    i = 0
    while i < 4096:
        b = mem[start + i]
        out.append(b)
        if b == 0xFF or b == 0x81:
            return bytes(out)
        if b < 0x80 or b == 0x80:
            out.append(mem[start + i + 1])
            i += 2
        else:
            i += 1
    raise ValueError(f'no $FF/$81 terminator within 4KB of ${start:04X}')


def _row_from_pair(note: int, dur: int) -> NoteRow:
    if note == 0x80:
        return NoteRow(pitch=Pitch.rest(), duration=dur)
    if note < 0x80:
        semi = note & 0x0F
        if semi < 12:
            name, octave = note_byte_to_pitch(note)
            return NoteRow(pitch=Pitch(name=name, octave=octave), duration=dur)
        return NoteRow(pitch=Pitch.rest(), duration=dur,
                       fx_flags=(f'fx:raw_{note:02x}',))
    raise ValueError(f'unexpected pair note=${note:02X}')


def _build_voice_rows(pattern_bytes: bytes) -> tuple[list[NoteRow], str | None]:
    rows = []
    terminator: str | None = None
    i = 0
    while i < len(pattern_bytes):
        b = pattern_bytes[i]
        if b == 0x81:
            terminator = 'stop'
            break
        if b == 0xFF:
            terminator = 'loop'
            break
        if b < 0x80 or b == 0x80:
            dur = pattern_bytes[i + 1]
            rows.append(_row_from_pair(b, dur))
            i += 2
        else:
            i += 1
    return rows, terminator


def _n_subtunes(sid_path: str) -> int:
    raw = open(sid_path, 'rb').read()
    return int.from_bytes(raw[14:16], 'big')


def build_usf(sid_path: str) -> UsfFile:
    n_sub = _n_subtunes(sid_path)
    mem0, init_sid0, raw = _run_init(sid_path, subtune=0)
    play_addr = struct.unpack('>H', raw[12:14])[0]
    layout = _detect_layout(mem0, play_addr)
    VB = layout['voice_base']
    TEMPO_CTR = layout['tempo_ctr']
    TEMPO = layout['tempo']

    music_subtunes = []
    instruments = []
    instrument_id = 0
    for s_idx in range(n_sub):
        mem, _, _ = _run_init(sid_path, subtune=s_idx)
        voices = []
        sub_init_voices = []
        for v, x in enumerate((0, 7, 14)):
            pat_start = mem[VB + 0x17 + x] | (mem[VB + 0x18 + x] << 8)
            timbre = bytes(mem[VB + 0x02 + x:VB + 0x02 + x + 5])
            engine_state = mem[VB + 1 + x]    # 0 = silent, 2 = load-pattern

            instrument_id += 1
            pw = (timbre[1] << 8) | timbre[0]
            instruments.append(Instrument(
                id=instrument_id, waveform=[timbre[2]], loop=0,
                pwm=PwmConfig(mode='none', speed=0, init=pw, min_hi=0, max_hi=0),
                adsr=(timbre[3], timbre[4]),
                arp=ArpConfig(offsets=[0], period=1),
                vibrato=VibratoConfig(scale=0),
                envelope=EnvelopeConfig(),
            ))
            sub_init_voices.append(
                InitVoice(id=v + 1, instr=InstrumentRef(id=instrument_id)))

            if engine_state == 0:
                voices.append(VoiceBlock(
                    id=v + 1,
                    orderlist=Orderlist(entries=[], stop=True),
                    patterns=[],
                ))
                continue
            if engine_state != 2:
                raise ValueError(
                    f'subtune {s_idx} voice {v+1}: unexpected engine '
                    f'state ${engine_state:02X} (expected $00 or $02)')

            pat_bytes = _extract_pattern(mem, pat_start)
            rows, terminator = _build_voice_rows(pat_bytes)
            if terminator is None:
                raise ValueError(
                    f'subtune {s_idx} voice {v+1}: pattern at ${pat_start:04X} '
                    f'has no $81/$FF terminator')
            total_ticks = sum(r.duration for r in rows)
            if terminator == 'stop':
                ol = Orderlist(entries=[1], stop=True)
            else:
                ol = Orderlist(entries=[1], loop_to=0)
            voices.append(VoiceBlock(
                id=v + 1,
                orderlist=ol,
                patterns=[Pattern(id=1, length=total_ticks, rows=rows)],
            ))

        _, init_sid, _ = _run_init(sid_path, subtune=s_idx)
        wrote_d418_full = any(r == 0x18 and v == 0x0F for r, v in init_sid)
        sub_fields = {
            'gain_init': 'full' if wrote_d418_full else 'preserve',
            'init_tempo_ctr': mem[TEMPO_CTR],
        }
        music_subtunes.append(MusicSubtune(
            id=s_idx, tempo=mem[TEMPO], voices=voices,
            init=InitState(voices=sub_init_voices),
            params=Params(fields=sub_fields),
        ))

    title = raw[0x16:0x36].rstrip(b'\x00').decode('latin-1')
    author = raw[0x36:0x56].rstrip(b'\x00').decode('latin-1')
    released = raw[0x56:0x76].rstrip(b'\x00').decode('latin-1')
    flags = int.from_bytes(raw[0x76:0x78], 'big')
    clock = {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[(flags >> 2) & 0x03]
    sid_model = {0: 6581, 1: 6581, 2: 8580, 3: 6581}[(flags >> 4) & 0x03]
    psid = PsidMeta(title=title, author=author, released=released,
                    clock=clock, sid=sid_model,
                    start_song=int.from_bytes(raw[0x10:0x12], 'big'),
                    speed=int.from_bytes(raw[0x12:0x16], 'big'))

    top_init = InitState(voices=[
        InitVoice(id=v + 1, instr=InstrumentRef(id=v + 1)) for v in range(3)
    ])

    freq_table = list(CLEVER_FREQ_HI) + list(CLEVER_FREQ_LO)
    return UsfFile(
        engine='yes_tune', psid=psid,
        params=Params(), init=top_init,
        instruments=instruments, subtunes=music_subtunes,
        freq_table=freq_table,
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
