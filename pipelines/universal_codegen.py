"""Universal codegen — USF → SID, designed for any engine family.

Status: seed. Today it handles single-voice atomic-event tunes
(henrys_house). It'll grow one engine family at a time until the
Hubbard '85 codegen (`pipelines/codegen.py`) can retire.

Architecture
============

This is a *pipeline of small asm-emitting functions*, composed by a
driver based on USF features. The driver reads the USF, picks which
emitters to chain, and assembles the result. Each emitter is a small
Python function that returns a list of asm lines.

  emit_sid(usf)
    ├─ pick_features(usf)        → feature dict
    ├─ emit_init(features)       → init asm
    ├─ emit_play(features)       → play-loop asm
    ├─ emit_note_dispatch(...)   → byte-decode asm
    ├─ emit_note_play(...)       → SID register writes for a played note
    ├─ emit_rest(...)            → SID writes for a rest
    ├─ emit_loop(...)            → loop terminator handler
    ├─ emit_runtime_vars(...)    → zp / runtime byte storage
    ├─ emit_freq_table(features) → freq table data
    ├─ emit_orderlist(features)  → pattern bytes
    └─ assemble + write PSID

A new engine that needs a primitive we don't have yet (e.g. multi-voice
loop, mid-pattern tempo command, different freq-table layout) adds an
emitter or a feature flag here. The architecture stays parametric.

What stays unified
==================
- PSID header writing
- xa65 invocation
- LOAD address conventions
- USF data access (subtunes, instruments, patterns)
"""

from __future__ import annotations

import os
import struct
import subprocess

from src.usf import UsfFile, MusicSubtune


LOAD = 0x1000

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_XA = os.path.join(_ROOT, 'tools', 'xa65', 'xa', 'xa')

_SEMI = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
         'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


# ---------------------------------------------------------------------------
# Feature detection
# ---------------------------------------------------------------------------

def pick_features(usf: UsfFile) -> dict:
    """Walk the USF and produce a feature dict the emitters consume.

    Today it's a flat dict; as we add engines, features that aren't
    used by a given tune just stay unset and emitters check before
    using them. No `*Kind` tokens — features are descriptive musical /
    structural facts about the tune.
    """
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if len(music) != 1:
        raise NotImplementedError(
            f'universal codegen currently handles 1 subtune; got {len(music)}')
    ms = music[0]

    active_voices = [v for v in ms.voices if v.patterns]
    if len(active_voices) != 1:
        raise NotImplementedError(
            f'universal codegen currently handles 1 active voice; '
            f'got {len(active_voices)}')

    if usf.freq_table is None or len(usf.freq_table) != 256:
        raise NotImplementedError(
            f'universal codegen currently expects a 256-byte freq_table '
            f'(128 hi + 128 lo); got {usf.freq_table and len(usf.freq_table)}')

    if len(usf.instruments) != 1:
        raise NotImplementedError(
            f'universal codegen currently handles 1 instrument; '
            f'got {len(usf.instruments)}')

    inst = usf.instruments[0]
    timbre = (
        inst.pwm.init & 0xFF,
        (inst.pwm.init >> 8) & 0xFF,
        inst.waveform[0] if inst.waveform else 0,
        inst.adsr[0],
        inst.adsr[1],
    )

    voice = active_voices[0]
    pattern = voice.patterns[0]

    return {
        'tempo':         ms.tempo,
        'freq_hi':       bytes(usf.freq_table[:128]),
        'freq_lo':       bytes(usf.freq_table[128:]),
        'timbre':        timbre,
        'pattern_rows':  pattern.rows,
        'orderlist_loops': voice.orderlist.loop_to is not None,
        'master_vol':    0x0F,
    }


# ---------------------------------------------------------------------------
# Pattern row → engine byte
# ---------------------------------------------------------------------------

def _pitch_byte(name: str, octave: int) -> int:
    return (octave << 4) | _SEMI[name]


def _row_to_bytes(row) -> bytes:
    """Atomic 1-tick events. duration N → 1 head byte + (N-1) $81 skips."""
    if not row.pitch.is_rest:
        head = _pitch_byte(row.pitch.name, row.pitch.octave)
    else:
        head = 0x80
        for f in row.fx_flags:
            if f.startswith('fx:raw_'):
                head = int(f.split('_')[1], 16)
                break
    return bytes([head]) + bytes([0x81] * (row.duration - 1))


# ---------------------------------------------------------------------------
# Asm emitters
# ---------------------------------------------------------------------------

def emit_header() -> list[str]:
    return [f'* = ${LOAD:04X}', '  jmp init', '  jmp play']


def emit_init(features: dict) -> list[str]:
    """Init writes the master-vol byte to $D418 and zeroes the position +
    tempo counters. Engines whose original init does more or less are
    handled by `skip_init=True` in the per-frame comparison.
    """
    return [
        'init:',
        f'  lda #${features["master_vol"]:02X}',
        '  sta $d418',
        '  lda #0',
        '  sta v_pos',
        '  sta tempo_ctr',
        '  rts',
    ]


def emit_play(features: dict) -> list[str]:
    """Play loop: every `tempo`th frame is a music tick. On a tick,
    advance the voice position and dispatch the byte we just read.
    """
    return [
        'play:',
        '  inc tempo_ctr',
        '  ldx tempo_ctr',
        f'  cpx #{features["tempo"]}',
        '  beq play_tick',
        '  rts',
        'play_tick:',
        '  lda #0',
        '  sta tempo_ctr',
        '  ldx v_pos',
        '  inc v_pos',
        '  lda orderlist,x',
    ]


def emit_dispatch_atomic_1byte(features: dict) -> list[str]:
    """One byte per pattern event:
       $00-$7F note,  $80 rest,  $81 skip,  $FF loop terminator.
    """
    return [
        '  cmp #$ff',
        '  bne not_ff',
        # Loop terminator — re-init the master vol + reset position.
        f'  lda #${features["master_vol"]:02X}',
        '  sta $d418',
        '  lda #0',
        '  sta v_pos',
        '  rts',
        'not_ff:',
        '  ldx #0',           # voice offset 0 (single-voice for now)
        '  cmp #$80',
        '  beq pn_rest',
        '  bcs pn_skip',
        '  tay',
        '  jmp pn_note',
        'pn_skip:',
        '  rts',
    ]


def emit_note_play(features: dict) -> list[str]:
    """Write freq + 5-byte timbre + gated ctrl for the voice at X."""
    t = features['timbre']
    return [
        'pn_note:',
        '  lda freq_hi_tab,y',
        '  sta $d401',
        '  lda freq_lo_tab,y',
        '  sta $d400',
        f'  lda #${t[0]:02X}',
        '  sta $d402',
        f'  lda #${t[1]:02X}',
        '  sta $d403',
        f'  lda #${t[2]:02X}',
        '  sta $d404',         # ctrl gate-off (envelope retrigger)
        f'  lda #${t[3]:02X}',
        '  sta $d405',
        f'  lda #${t[4]:02X}',
        '  sta $d406',
        f'  lda #${(t[2] + 1) & 0xFF:02X}',
        '  sta $d404',         # ctrl gate-on
        '  rts',
    ]


def emit_rest(features: dict) -> list[str]:
    t = features['timbre']
    return [
        'pn_rest:',
        f'  lda #${t[2]:02X}',
        '  sta $d404',
        '  rts',
    ]


def emit_runtime_vars(features: dict) -> list[str]:
    return [
        'v_pos:       .byte 0',
        'tempo_ctr:   .byte 0',
    ]


def emit_freq_table(features: dict) -> list[str]:
    lines = ['freq_hi_tab:']
    fh = features['freq_hi']
    fl = features['freq_lo']
    for i in range(0, len(fh), 16):
        lines.append('  .byte ' + ', '.join(f'${b:02X}' for b in fh[i:i+16]))
    lines.append('freq_lo_tab:')
    for i in range(0, len(fl), 16):
        lines.append('  .byte ' + ', '.join(f'${b:02X}' for b in fl[i:i+16]))
    return lines


def emit_orderlist(features: dict) -> list[str]:
    """Encode the voice's pattern as the engine's byte stream.

    Loop terminator: $FF when the voice's orderlist loops; otherwise
    nothing extra (the engine never reaches the end).
    """
    body = b''.join(_row_to_bytes(r) for r in features['pattern_rows'])
    if features['orderlist_loops']:
        body += bytes([0xFF])
    lines = ['orderlist:']
    for i in range(0, len(body), 16):
        lines.append('  .byte ' + ', '.join(f'${b:02X}' for b in body[i:i+16]))
    return lines


# ---------------------------------------------------------------------------
# Driver — pick + chain emitters, assemble, wrap in PSID header
# ---------------------------------------------------------------------------

def _assemble(asm_src: str, tmp_basename: str = 'universal_codegen') -> bytes:
    src = f'/tmp/{tmp_basename}.s'
    obj = f'/tmp/{tmp_basename}.bin'
    with open(src, 'w') as f:
        f.write(asm_src)
    r = subprocess.run([_XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    return open(obj, 'rb').read()


def _psid_header(usf: UsfFile, n_subtunes: int, load: int) -> bytes:
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', load)
    h += struct.pack('>H', load)
    h += struct.pack('>H', load + 3)
    h += struct.pack('>H', n_subtunes)
    h += struct.pack('>H', usf.psid.start_song)
    h += struct.pack('>I', usf.psid.speed)
    def _latin1(s: str, n: int) -> bytes:
        return s.encode('latin-1', errors='replace')[:n].ljust(n, b'\x00')
    h += _latin1(usf.psid.title, 32)
    h += _latin1(usf.psid.author, 32)
    h += _latin1(usf.psid.released, 32)
    clock_bits = {'unknown': 0, 'PAL': 1, 'NTSC': 2, 'both': 3}.get(
        usf.psid.clock, 0)
    sid_bits = {6581: 1, 8580: 2}.get(usf.psid.sid, 1)
    h += struct.pack('>H', (clock_bits << 2) | (sid_bits << 4))
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124
    return bytes(h)


def emit_sid(usf: UsfFile) -> bytes:
    """Universal entry. Reads USF, picks emitters, returns PSID bytes."""
    features = pick_features(usf)

    asm_lines: list[str] = []
    asm_lines += emit_header()
    asm_lines += emit_init(features)
    asm_lines += emit_play(features)
    asm_lines += emit_dispatch_atomic_1byte(features)
    asm_lines += emit_note_play(features)
    asm_lines += emit_rest(features)
    asm_lines += emit_runtime_vars(features)
    asm_lines += emit_freq_table(features)
    asm_lines += emit_orderlist(features)
    asm = '\n'.join(asm_lines) + '\n'

    body = _assemble(asm)

    n_subs = sum(1 for s in usf.subtunes if isinstance(s, MusicSubtune))
    header = _psid_header(usf, n_subs, LOAD)
    return header + body


def applies_to(usf: UsfFile) -> bool:
    """Quick check: does this USF fit the features the universal codegen
    currently handles? Used by `pipelines.build_from_usf.build_from_usf`
    to decide whether to route here or fall back to the Hubbard codegen.

    As more features are supported, this check widens.
    """
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if len(music) != 1:
        return False
    ms = music[0]
    active = [v for v in ms.voices if v.patterns]
    if len(active) != 1:
        return False
    if usf.freq_table is None or len(usf.freq_table) != 256:
        return False
    if len(usf.instruments) != 1:
        return False
    return True
