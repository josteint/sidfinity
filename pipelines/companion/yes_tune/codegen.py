"""Yes_Tune — combined extract + USF + codegen for a single SID.

Engine semantics (from $6240 disasm):

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

  Play loop tick:
    For each voice:
      if state == 2: load_pattern (ptr=pat_start, tick=0), state = 1
      if state == 1:
        if tick_ctr == 0: play current pair (note+timbre+gate)
        else: DEC tick_ctr
      else: skip

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
import subprocess

from src.usf2 import (
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
    # Walk play_addr+0 to play_addr+0x80 looking for the LDA-CMP-#$02 pattern.
    pc = play_addr
    end = play_addr + 0x100
    voice_state_addr = None
    inc_target = None  # tempo_ctr
    cmp_target = None  # tempo
    while pc < end - 4:
        if mem[pc] == 0xBD and mem[pc + 3] == 0xC9 and mem[pc + 4] == 0x02:
            # LDA abs,X (BD) followed by CMP #$02 (C9 02)
            voice_state_addr = mem[pc + 1] | (mem[pc + 2] << 8)
            break
        # Also opportunistically find INC abs / CPY abs for tempo
        if mem[pc] == 0xEE and inc_target is None:
            inc_target = mem[pc + 1] | (mem[pc + 2] << 8)
        if mem[pc] == 0xCC and cmp_target is None:  # CPY abs
            cmp_target = mem[pc + 1] | (mem[pc + 2] << 8)
        pc += 1
    if voice_state_addr is None:
        raise ValueError(f'no LDA abs,X / CMP #$02 pattern in play loop')
    # voice_state_addr = voice_base + 1
    voice_base = voice_state_addr - 1
    # Freq tables are voice_base - $100 (hi) and voice_base - $80 (lo).
    # ("- $100" because freq_hi is at $X600 when voice_base is $X700.)
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
            # 2-byte pair (note+dur or rest+dur)
            out.append(mem[start + i + 1])
            i += 2
        else:
            # other bit-7 — undocumented, treat as 1-byte
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
        # Non-musical semitones (12-15) — preserve via fx:raw flag
        return NoteRow(pitch=Pitch.rest(), duration=dur,
                       fx_flags=(f'fx:raw_{note:02x}',))
    raise ValueError(f'unexpected pair note=${note:02X}')


def _build_voice_rows(pattern_bytes: bytes) -> tuple[list[NoteRow], str | None]:
    """Decode pattern bytes into note rows + the engine terminator kind.

    The terminator byte ($81 or $FF) doesn't appear in the row list;
    it becomes the voice's orderlist terminator. Returns ('stop',
    'loop' or None for an unterminated pattern body — only the latter
    case means we read past the end without finding a terminator,
    which would be a malformed engine state).
    """
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
                # Voice is silent throughout the subtune. The engine
                # never reads its pattern data; we drop it from USF.
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
            else:  # 'loop'
                ol = Orderlist(entries=[1], loop_to=0)
            voices.append(VoiceBlock(
                id=v + 1,
                orderlist=ol,
                patterns=[Pattern(id=1, length=total_ticks, rows=rows)],
            ))

        # Subtune-level musical params:
        #   gain_init:    'full' if init writes $D418=$0F (music subtunes),
        #                 'preserve' if init leaves $D418 untouched (SFX
        #                 subtunes ride whatever master vol was already set).
        #   init_tempo_ctr: starting phase of the tempo counter — where
        #                 in the rhythmic cycle the song begins.
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

    # PSID meta
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
    return UsfFile(
        version=2, engine='yes_tune', psid=psid,
        params=Params(), init=top_init,
        instruments=instruments, subtunes=music_subtunes,
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
# Codegen
# ---------------------------------------------------------------------------

def _row_to_pattern_bytes(row: NoteRow) -> bytes:
    """Emit the 2-byte (note, duration) pair for one pattern row.

    The pattern terminator ($81/$FF) is emitted by the caller from the
    voice's orderlist shape, not from row flags.
    """
    for f in row.fx_flags:
        if f.startswith('fx:raw_'):
            return bytes([int(f.split('_')[1], 16), row.duration & 0xFF])
    if row.pitch.is_rest:
        return bytes([0x80, row.duration & 0xFF])
    note = pitch_to_note_byte(row.pitch.name, row.pitch.octave)
    return bytes([note, row.duration & 0xFF])


def _voice_pattern_bytes_and_state(vb: VoiceBlock) -> tuple[bytes, int]:
    """For one VoiceBlock, return (pattern-data bytes, engine-state byte).

    Empty orderlist + stop  → silent voice: sentinel pattern $81,
                              state $00. The engine never reads this
                              pattern because state=0 makes voice_tick
                              skip it; the sentinel byte is just so
                              the pat_start pointer points at *something*.
    orderlist `1 stop`      → state $02, pattern bytes + $81.
    orderlist `1 loop@0`    → state $02, pattern bytes + $FF.
    """
    ol = vb.orderlist
    if not ol.entries:
        # Silent voice. Engine never reads its pattern; emit a $81
        # sentinel so pat_start points at a valid stop byte.
        return bytes([0x81]), 0x00
    if len(ol.entries) != 1 or ol.entries[0] != 1:
        raise ValueError(
            f'voice {vb.id}: yes_tune only supports a single-pattern '
            f'orderlist ([1]); got {ol.entries}')
    pat = vb.patterns[0]
    body = b''.join(_row_to_pattern_bytes(r) for r in pat.rows)
    if ol.stop:
        return body + bytes([0x81]), 0x02
    if ol.loop_to is not None:
        return body + bytes([0xFF]), 0x02
    raise ValueError(
        f'voice {vb.id}: orderlist must terminate with stop or loop@N')


def emit_asm(usf: UsfFile) -> str:
    music = sorted([s for s in usf.subtunes if isinstance(s, MusicSubtune)],
                   key=lambda s: s.id)
    if not music: raise ValueError('no music subtunes')
    n_sub = len(music)

    # Per-subtune data: timbres (3 voices × 5 bytes), tempo, init_tempo_ctr
    instruments_by_id = {i.id: i for i in usf.instruments}

    per_sub = []
    voice_patterns = []  # (subtune_idx, voice_idx) → bytes
    for s_idx, ms in enumerate(music):
        if len(ms.voices) != 3: raise ValueError('expected 3 voices')
        p = ms.params.fields if ms.params else {}
        timbres = []
        for v in range(3):
            iid = ms.init.voices[v].instr.id
            inst = instruments_by_id[iid]
            timbres.append([
                inst.pwm.init & 0xFF, (inst.pwm.init >> 8) & 0xFF,
                inst.waveform[0] if inst.waveform else 0,
                inst.adsr[0], inst.adsr[1],
            ])
        # Per-voice pattern bytes + engine state derived from the
        # orderlist shape (silent = state 0; stop/loop = state 2).
        states = []
        for vb in ms.voices:
            pat_bytes, st = _voice_pattern_bytes_and_state(vb)
            voice_patterns.append(pat_bytes)
            states.append(st)
        gain_init = p.get('gain_init', 'full')
        per_sub.append({
            'tempo': ms.tempo,
            'init_tempo_ctr': p.get('init_tempo_ctr', 0),
            'timbres': timbres,
            'init_state': tuple(states),
            'gain_init_full': int(gain_init == 'full'),
        })

    L: list[str] = []
    L.append(f'* = ${LOAD:04X}')
    L.append('  jmp init')
    L.append('  jmp play')

    L.append('init:')
    # Engine init does NOT silence the SID. May write $D418=$0F for
    # music subtunes; SFX subtunes skip that write. Driven by per-
    # subtune init_d418_tab.
    L.append('  pha                  ; save A = subtune index')
    L.append('  tay                  ; Y = subtune index for table lookup')
    L.append('  lda init_d418_tab,y')
    L.append('  beq init_skip_d418')
    L.append('  lda #$0f')
    L.append('  sta $d418')
    L.append('init_skip_d418:')
    L.append('  pla')
    L.append('  tay                  ; Y = subtune index')
    # Per-voice setup — loaded from per-subtune tables indexed by Y.
    # Each voice has timbre, pat_start, and initial state=2.
    for v_idx, x in enumerate((0, 7, 14)):
        L.append(f'  ; V{v_idx+1} init from sub-Y tables')
        for j in range(5):  # timbre 5 bytes
            L.append(f'  lda v{v_idx+1}_tb{j}_tab,y')
            L.append(f'  sta v_state+${0x02+x+j:02X}')
        L.append(f'  lda v{v_idx+1}_ps_lo_tab,y')
        L.append(f'  sta v_state+${0x15+x:02X}')
        L.append(f'  sta v_state+${0x17+x:02X}')
        L.append(f'  lda v{v_idx+1}_ps_hi_tab,y')
        L.append(f'  sta v_state+${0x16+x:02X}')
        L.append(f'  sta v_state+${0x18+x:02X}')
        L.append(f'  lda v{v_idx+1}_state_tab,y')
        L.append(f'  sta v_state+${0x01+x:02X}')
        L.append(f'  lda #$00')
        L.append(f'  sta v_state+${0x00+x:02X}')
    L.append('  lda tempo_tab,y')
    L.append('  sta tempo_const')
    L.append('  lda init_tempo_ctr_tab,y')
    L.append('  sta tempo_ctr')
    L.append('  rts')

    # play
    L.append('play:')
    L.append('  inc tempo_ctr')
    L.append('  lda tempo_ctr')
    L.append('  cmp tempo_const')
    L.append('  bne play_exit')
    L.append('  lda #0')
    L.append('  sta tempo_ctr')
    # Per voice
    for v, x in enumerate((0, 7, 14)):
        L.append(f'  ldx #{x}')
        L.append(f'  jsr voice_tick')
    L.append('play_exit:')
    L.append('  rts')

    # voice_tick(X = voice offset)
    L.append('voice_tick:')
    L.append('  lda v_state+1,x      ; state')
    L.append('  cmp #2')
    L.append('  bne vt_chk1')
    # state == 2: load pattern + state := 1
    L.append('  lda v_state+$17,x')
    L.append('  sta v_state+$15,x    ; ptr = pat_start')
    L.append('  lda v_state+$18,x')
    L.append('  sta v_state+$16,x')
    L.append('  lda #0')
    L.append('  sta v_state,x        ; tick_ctr = 0')
    L.append('  lda #1')
    L.append('  sta v_state+1,x')
    L.append('vt_chk1:')
    L.append('  lda v_state+1,x')
    L.append('  cmp #1')
    L.append('  beq vt_play')
    L.append('  rts                  ; state != 1 - skip')
    L.append('vt_play:')
    # Set zp ptr from v_state+$15/$16
    L.append('  lda v_state+$15,x')
    L.append('  sta $fb')
    L.append('  lda v_state+$16,x')
    L.append('  sta $fc')
    L.append('  jmp play_note        ; tail-call (X preserved)')

    # play_note (X = voice offset, $fb/$fc = pattern ptr)
    L.append('play_note:')
    L.append('  ldy #0')
    L.append('  lda ($fb),y')
    L.append('  and #$80')
    L.append('  beq pn_normal')
    L.append('  jmp pn_bit7')
    L.append('pn_normal:')
    L.append('  ldy v_state,x        ; tick_ctr')
    L.append('  cpy #0')
    L.append('  bne pn_dec')
    L.append('  jsr pn_emit_note')
    L.append('  jsr pn_advance')
    L.append('pn_dec:')
    L.append('  dec v_state,x')
    L.append('  rts')
    L.append('pn_emit_note:')
    L.append('  ldy #0')
    L.append('  lda ($fb),y')
    L.append('  tay')
    L.append('  lda freq_hi_tab,y')
    L.append('  sta $d401,x')
    L.append('  lda freq_lo_tab,y')
    L.append('  sta $d400,x')
    L.append('  txa')
    L.append('  tay')
    L.append('  clc')
    L.append('  adc #$05')
    L.append('  sta pn_endy')
    L.append('pn_pw_loop:')
    L.append('  lda v_state+2,y')
    L.append('  sta $d402,y')
    L.append('  iny')
    L.append('  cpy pn_endy')
    L.append('  bne pn_pw_loop')
    L.append('  ldy v_state+4,x')
    L.append('  iny')
    L.append('  tya')
    L.append('  sta $d404,x')
    L.append('  rts')
    L.append('pn_advance:')
    L.append('  ldy #1')
    L.append('  lda ($fb),y')
    L.append('  cmp #0')
    L.append('  bne pn_adv_ok')
    L.append('  lda #1')
    L.append('pn_adv_ok:')
    L.append('  sta v_state,x')
    L.append('  lda v_state+$15,x')
    L.append('  clc')
    L.append('  adc #2')
    L.append('  sta v_state+$15,x')
    L.append('  bcc pn_adv_done')
    L.append('  inc v_state+$16,x')
    L.append('pn_adv_done:')
    L.append('  rts')

    # bit-7 path
    L.append('pn_bit7:')
    L.append('  ldy #0')
    L.append('  lda ($fb),y')
    L.append('  cmp #$80')
    L.append('  bne pn_n80')
    # $80 - rest with duration
    L.append('  ldy v_state,x        ; tick_ctr')
    L.append('  cpy #0')
    L.append('  bne pn_dec')
    L.append('  lda v_state+4,x      ; ctrl')
    L.append('  sta $d404,x')
    L.append('  jsr pn_advance')
    L.append('  jmp pn_dec')
    L.append('pn_n80:')
    L.append('  cmp #$ff')
    L.append('  bne pn_nff')
    # $FF - loop
    L.append('  lda v_state+$17,x')
    L.append('  sta v_state+$15,x')
    L.append('  lda v_state+$18,x')
    L.append('  sta v_state+$16,x')
    L.append('  lda #0')
    L.append('  sta v_state,x')
    L.append('  lda v_state+$15,x')
    L.append('  sta $fb')
    L.append('  lda v_state+$16,x')
    L.append('  sta $fc')
    L.append('  jmp play_note')
    L.append('pn_nff:')
    L.append('  cmp #$81')
    L.append('  bne pn_other')
    # $81 - stop voice
    L.append('  lda v_state+4,x')
    L.append('  sta $d404,x')
    L.append('  lda #0')
    L.append('  sta v_state+1,x')
    L.append('pn_other:')
    L.append('  rts')

    # Runtime vars
    L.append('pn_endy:     .byte 0')
    L.append('tempo_const: .byte 0')
    L.append('tempo_ctr:   .byte 0')
    L.append('; v_state per-voice block, X-indexed (3 voices at X=0,7,14)')
    # We need v_state+X at offsets 0..$18 for all 3 voices. Allocate 0x20 bytes.
    L.append('v_state:     .dsb $20, 0')

    # Freq tables
    L.append('freq_hi_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in CLEVER_FREQ_HI[i:i+16]))
    L.append('freq_lo_tab:')
    for i in range(0, 128, 16):
        L.append('  .byte ' + ', '.join(f'${b:02X}' for b in CLEVER_FREQ_LO[i:i+16]))

    # Per-subtune data tables (indexed by Y = subtune)
    def _byte_tab(label, vals):
        L.append(f'{label}: .byte ' + ', '.join(f'${v:02X}' for v in vals))
    _byte_tab('tempo_tab', [s['tempo'] for s in per_sub])
    _byte_tab('init_tempo_ctr_tab', [s['init_tempo_ctr'] for s in per_sub])
    # 3 voices × 5 timbre fields per subtune
    for v_idx in range(3):
        for j in range(5):
            _byte_tab(f'v{v_idx+1}_tb{j}_tab',
                      [s['timbres'][v_idx][j] for s in per_sub])
    # Per-voice initial state byte
    for v_idx in range(3):
        _byte_tab(f'v{v_idx+1}_state_tab',
                  [s['init_state'][v_idx] for s in per_sub])
    _byte_tab('init_d418_tab', [s['gain_init_full'] for s in per_sub])
    # Per-subtune pat_start (lo/hi) tables — reference ptn_sN_vV labels
    for v_idx in range(3):
        L.append(f'v{v_idx+1}_ps_lo_tab:')
        L.append('  .byte ' + ', '.join(
            f'<ptn_s{s}_v{v_idx+1}' for s in range(n_sub)))
        L.append(f'v{v_idx+1}_ps_hi_tab:')
        L.append('  .byte ' + ', '.join(
            f'>ptn_s{s}_v{v_idx+1}' for s in range(n_sub)))

    # Per-subtune per-voice pattern data
    pat_idx = 0
    for s_idx in range(n_sub):
        for v_idx in range(3):
            pat = voice_patterns[pat_idx]
            pat_idx += 1
            L.append(f'ptn_s{s_idx}_v{v_idx+1}:')
            for i in range(0, len(pat), 16):
                L.append('  .byte ' + ', '.join(
                    f'${b:02X}' for b in pat[i:i+16]))

    return '\n'.join(L) + '\n'


def assemble(asm_src: str) -> bytes:
    src = '/tmp/yes_tune_codegen.s'
    obj = '/tmp/yes_tune_codegen.bin'
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
    if usf.engine != 'yes_tune':
        raise ValueError(f"expected engine 'yes_tune', got {usf.engine!r}")
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
