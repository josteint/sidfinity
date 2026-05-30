"""Universal codegen — USF → SID, designed for any engine family.

Status: seed. Today it handles two engine families:
  - Single-voice atomic-event tunes (henrys_house)
  - Three-voice atomic-event tunes with per-voice loop semantics + an
    inter-voice carry-leak quirk (bowden_canonical)

Each engine family that migrates over teaches it new primitives. When
`pipelines/codegen.py` (the Hubbard '85 legacy codegen) can also be
expressed here, it retires.

Architecture
============

A pipeline of small asm-emitting functions composed by a driver. The
driver reads the USF, picks which emitters to chain, and assembles
the result. No `*Kind` dispatch — `applies_to(usf)` and `pick_features`
look at USF *content* (voice count, freq_table size, presence of
fx flags, etc.), never at `usf.engine`.

  emit_sid(usf)
    ├─ pick_features(usf)        → feature dict
    ├─ emit_header / emit_init   → preamble + init
    ├─ emit_play_loop_*          → tempo gate + per-voice processing
    ├─ emit_note_play_*          → SID register writes per played note
    ├─ emit_loop_terminator_*    → $FF handler
    ├─ emit_runtime_vars + data  → zp / freq table / orderlists
    └─ assemble + PSID header

What's deliberately unified:
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

    Features are descriptive musical / structural facts. Engines with
    overlapping musical content share features; engine-quirk behaviors
    surface as named boolean flags (no opaque kinds).
    """
    music = sorted(
        (s for s in usf.subtunes if isinstance(s, MusicSubtune)),
        key=lambda s: s.id)
    if len(music) != 1:
        raise NotImplementedError(
            f'universal codegen currently handles 1 subtune; got {len(music)}')
    ms = music[0]

    active = [v for v in ms.voices if v.patterns]
    voice_count = len(active)
    if voice_count not in (1, 3):
        raise NotImplementedError(
            f'universal codegen currently supports 1- or 3-voice tunes; '
            f'got {voice_count}')

    if usf.freq_table is None or len(usf.freq_table) != 256:
        raise NotImplementedError(
            f'universal codegen currently expects 256-byte freq_table '
            f'(128 hi + 128 lo); got {usf.freq_table and len(usf.freq_table)}')

    instr_by_id = {i.id: i for i in usf.instruments}

    # Per-voice timbre, indexed by 0/1/2 = V1/V2/V3.
    # For 1-voice tunes, V1's instrument lives at index 0; V2/V3 unused.
    voice_to_instr = {1: None, 2: None, 3: None}
    init_voices = (ms.init.voices if (ms.init and ms.init.voices)
                   else usf.init.voices)
    for iv in init_voices:
        if iv.instr is not None:
            voice_to_instr[iv.id] = instr_by_id[iv.instr.id]
    timbres = []
    for vid in (1, 2, 3):
        ins = voice_to_instr[vid] or instr_by_id[1]   # fallback for inactive
        timbres.append((
            ins.pwm.init & 0xFF,
            (ins.pwm.init >> 8) & 0xFF,
            ins.waveform[0] if ins.waveform else 0,
            ins.adsr[0],
            ins.adsr[1],
        ))

    # Per-voice pattern (the byte stream).
    pat_rows = {}
    for v in ms.voices:
        pat_rows[v.id] = v.patterns[0].rows if v.patterns else []

    # Per-voice init position + init tempo counter — subtune-level params.
    sp = ms.params.fields if ms.params else {}
    init_pos = (sp.get('init_pos_v1', 0),
                sp.get('init_pos_v2', 0),
                sp.get('init_pos_v3', 0))
    init_tempo_ctr = sp.get('init_tempo_ctr', 0)

    # Engine-quirk flags: derived from USF structure where possible.
    # - `loop_action`: what happens when the engine reads the loop
    #   terminator byte. Two known styles so far:
    #     'reinit_master_vol' — write $D418=$0F + reset pos to 0; no note plays (henrys)
    #     'substitute_first'  — pos = 1, then play orderlist[0] this tick (bowden)
    #   Detected by voice count for now: 1-voice → reinit_master_vol;
    #   3-voice → substitute_first. As more engines arrive, this widens.
    loop_action = 'reinit_master_vol' if voice_count == 1 else 'substitute_first'

    # - `inter_voice_carry_leak`: bowden's quirky 4-vs-5-byte timbre choice
    #   based on whether the prior voice played a skip ($81-$FE) byte.
    #   Engine-mechanism feature; off for henrys. On for 3-voice.
    inter_voice_carry_leak = (voice_count == 3)

    return {
        'tempo':             ms.tempo,
        'voice_count':       voice_count,
        'freq_hi':           bytes(usf.freq_table[:128]),
        'freq_lo':           bytes(usf.freq_table[128:]),
        'timbres':           timbres,
        'pattern_rows':      pat_rows,
        'init_pos':          init_pos,
        'init_tempo_ctr':    init_tempo_ctr,
        'loop_action':       loop_action,
        'inter_voice_carry_leak': inter_voice_carry_leak,
        'master_vol':        0x0F,
    }


# ---------------------------------------------------------------------------
# Pattern row → engine byte
# ---------------------------------------------------------------------------

def _pitch_byte(name: str, octave: int) -> int:
    return (octave << 4) | _SEMI[name]


def _row_to_bytes(row) -> bytes:
    """Atomic 1-tick events.

    `fx:hold` flag → $81 (skip — engine keeps prior state, no SID writes).
    Otherwise: 1 head byte + (duration-1) $81 skips.
    """
    if 'fx:hold' in row.fx_flags:
        return bytes([0x81])
    if not row.pitch.is_rest:
        head = _pitch_byte(row.pitch.name, row.pitch.octave)
    else:
        head = 0x80
        for f in row.fx_flags:
            if f.startswith('fx:raw_'):
                head = int(f.split('_')[1], 16)
                break
    return bytes([head]) + bytes([0x81] * (row.duration - 1))


def _orderlist_bytes(features: dict, vid: int) -> bytes:
    rows = features['pattern_rows'].get(vid, [])
    if not rows:
        # Inactive voice — emit a single $FF terminator (engine reads it
        # and loops; in practice the voice never starts because its
        # init_pos / state is set to skip).
        return bytes([0xFF])
    return b''.join(_row_to_bytes(r) for r in rows) + bytes([0xFF])


# ---------------------------------------------------------------------------
# Asm emitters — 1-voice family (henrys_house)
# ---------------------------------------------------------------------------

def _emit_1voice_init(features: dict) -> list[str]:
    return [
        'init:',
        f'  lda #${features["master_vol"]:02X}',
        '  sta $d418',
        '  lda #0',
        '  sta v_pos',
        '  sta tempo_ctr',
        '  rts',
    ]


def _emit_1voice_play(features: dict) -> list[str]:
    t = features['timbres'][0]
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
        '  lda orderlist_v1,x',
        '  cmp #$ff',
        '  bne not_ff',
        # Loop: reinit master_vol + reset position.
        f'  lda #${features["master_vol"]:02X}',
        '  sta $d418',
        '  lda #0',
        '  sta v_pos',
        '  rts',
        'not_ff:',
        '  cmp #$80',
        '  beq pn_rest',
        '  bcs pn_skip',
        '  tay',
        '  lda freq_hi_tab,y',
        '  sta $d401',
        '  lda freq_lo_tab,y',
        '  sta $d400',
        f'  lda #${t[0]:02X}',
        '  sta $d402',
        f'  lda #${t[1]:02X}',
        '  sta $d403',
        f'  lda #${t[2]:02X}',
        '  sta $d404',
        f'  lda #${t[3]:02X}',
        '  sta $d405',
        f'  lda #${t[4]:02X}',
        '  sta $d406',
        f'  lda #${(t[2] + 1) & 0xFF:02X}',
        '  sta $d404',
        '  rts',
        'pn_rest:',
        f'  lda #${t[2]:02X}',
        '  sta $d404',
        '  rts',
        'pn_skip:',
        '  rts',
    ]


# ---------------------------------------------------------------------------
# Asm emitters — 3-voice family (bowden_canonical)
# ---------------------------------------------------------------------------

# Zero-page slots for the per-voice orderlist pointers.
ZP_OL_V1_LO, ZP_OL_V1_HI = 0xE0, 0xE1
ZP_OL_V2_LO, ZP_OL_V2_HI = 0xE2, 0xE3
ZP_OL_V3_LO, ZP_OL_V3_HI = 0xE4, 0xE5


def _emit_3voice_init(features: dict) -> list[str]:
    """Init silences SID, sets master vol, programs per-voice init
    positions + tempo counter. Init-frame writes don't have to match
    the original engine's exact init — `skip_init=True` in the
    per-frame comparison drops frame 0.
    """
    pos = features['init_pos']
    return [
        'init:',
        # Silence SID — canonical init.
        '  lda #0',
        '  ldx #0',
        'init_silence:',
        '  sta $d400,x',
        '  inx',
        '  cpx #$19',
        '  bne init_silence',
        f'  lda #${features["master_vol"]:02X}',
        '  sta $d418',
        # Per-voice init positions and tempo counter.
        f'  lda #${pos[0]:02X}',
        '  sta v1_pos',
        f'  lda #${pos[1]:02X}',
        '  sta v2_pos',
        f'  lda #${pos[2]:02X}',
        '  sta v3_pos',
        f'  lda #${features["init_tempo_ctr"]:02X}',
        '  sta tempo_ctr',
        # Orderlist pointers — zp slots used by the indirect (zp),Y reads.
        '  lda #<orderlist_v1',
        f'  sta ${ZP_OL_V1_LO:02X}',
        '  lda #>orderlist_v1',
        f'  sta ${ZP_OL_V1_HI:02X}',
        '  lda #<orderlist_v2',
        f'  sta ${ZP_OL_V2_LO:02X}',
        '  lda #>orderlist_v2',
        f'  sta ${ZP_OL_V2_HI:02X}',
        '  lda #<orderlist_v3',
        f'  sta ${ZP_OL_V3_LO:02X}',
        '  lda #>orderlist_v3',
        f'  sta ${ZP_OL_V3_HI:02X}',
        '  rts',
    ]


def _emit_3voice_play(features: dict) -> list[str]:
    """Play loop: gate by tempo, then process V1, V2, V3 in order.

    Models bowden's `next_skip_sr` carry-leak: a voice that plays a
    skip note ($81-$FE) sets a flag that causes the NEXT voice to
    write only 4 timbre bytes (omitting SR) instead of 5. This is the
    engine's quirky 6502 carry-bit behavior — we model it via an
    explicit flag rather than recreating the carry leak directly.
    """
    leak = features['inter_voice_carry_leak']
    L: list[str] = [
        'play:',
        '  inc tempo_ctr',
        '  lda tempo_ctr',
        f'  cmp #{features["tempo"]}',
        '  bne play_exit',
        '  lda #0',
        '  sta tempo_ctr',
    ]
    if leak:
        L.append('  sta next_skip_sr     ; V1 starts each tick with 5-byte timbre')
    L += [
        '  jsr voice1_step',
        '  jsr voice2_step',
        '  jsr voice3_step',
        'play_exit:',
        '  rts',
    ]
    return L


def _emit_3voice_proc_note(features: dict) -> list[str]:
    """proc_note — X = voice offset (0/7/14), A = byte to dispatch.

    For each voice we write its own timbre (stored in 5 parallel
    15-byte arrays indexed by X). The `this_skip_sr` flag suppresses
    the SR write when set (bowden carry-leak).
    """
    return [
        'proc_note:',
        '  cmp #$80',
        '  beq pn_rest',
        '  bcs pn_skip',
        '  tay',
        '  lda freq_hi_tab,y',
        '  sta $d401,x',
        '  lda freq_lo_tab,y',
        '  sta $d400,x',
        '  lda timbre_pwlo,x',
        '  sta $d402,x',
        '  lda timbre_pwhi,x',
        '  sta $d403,x',
        '  lda timbre_ctrl,x',
        '  sta $d404,x',
        '  lda timbre_ad,x',
        '  sta $d405,x',
        '  lda this_skip_sr',
        '  bne pn_no_sr_write',
        '  lda timbre_sr,x',
        '  sta $d406,x',
        'pn_no_sr_write:',
        '  lda timbre_ctrl,x',
        '  ora #$01',
        '  sta $d404,x',
        '  rts',
        'pn_rest:',
        '  lda timbre_ctrl,x',
        '  sta $d404,x',
        '  rts',
        'pn_skip:',
        '  rts',
    ]


def _emit_3voice_voice_step(vn: int, pos_label: str, zp_lo: int,
                             voice_off: int, force_4_on_loop: bool,
                             leak: bool) -> list[str]:
    """Per-voice step routine: read byte, handle $FF substitution (loop),
    classify byte to set `next_skip_sr`, call proc_note.

    `force_4_on_loop` is True for V1/V2 (bowden's loop dispatcher clears
    carry → next voice uses 4-byte timbre); False for V3 (X==$0E keeps
    carry set → 5-byte timbre).
    """
    L: list[str] = [
        f'voice{vn}_step:',
        f'  ldy {pos_label}',
        f'  inc {pos_label}',
        f'  lda (${zp_lo:02X}),y',
        f'  cmp #$ff',
        f'  bne v{vn}_normal',
        # $FF substitution: pos = 1, play orderlist[0] this tick.
        '  lda #1',
        f'  sta {pos_label}',
        '  ldy #0',
        f'  lda (${zp_lo:02X}),y',
    ]
    if leak:
        L += [
            f'  ldy #{1 if force_4_on_loop else 0}',
            '  sty this_skip_sr',
            f'  jmp v{vn}_classify',
        ]
    else:
        L.append(f'  jmp v{vn}_call')
    L.append(f'v{vn}_normal:')
    if leak:
        L += [
            '  ldy next_skip_sr',
            '  sty this_skip_sr',
            f'v{vn}_classify:',
            '  pha',
            '  cmp #$81',
            f'  bcc v{vn}_not_skip',
            '  cmp #$ff',
            f'  beq v{vn}_not_skip',
            '  ldy #1',
            '  sty next_skip_sr',
            f'  jmp v{vn}_call',
            f'v{vn}_not_skip:',
            '  ldy #0',
            '  sty next_skip_sr',
            f'v{vn}_call:',
            '  pla',
        ]
    L += [
        f'  ldx #{voice_off}',
        '  jmp proc_note',
    ]
    return L


def _emit_3voice_voice_steps(features: dict) -> list[str]:
    leak = features['inter_voice_carry_leak']
    L: list[str] = []
    for vn, (pos_label, zp_lo, voice_off, force_4_on_loop) in enumerate([
        ('v1_pos', ZP_OL_V1_LO, 0, True),
        ('v2_pos', ZP_OL_V2_LO, 7, True),
        ('v3_pos', ZP_OL_V3_LO, 14, False),
    ], start=1):
        L += _emit_3voice_voice_step(vn, pos_label, zp_lo, voice_off,
                                      force_4_on_loop, leak)
    return L


# ---------------------------------------------------------------------------
# Shared emitters
# ---------------------------------------------------------------------------

def emit_header() -> list[str]:
    return [f'* = ${LOAD:04X}', '  jmp init', '  jmp play']


def _emit_runtime_vars(features: dict) -> list[str]:
    if features['voice_count'] == 1:
        return [
            'v_pos:       .byte 0',
            'tempo_ctr:   .byte 0',
        ]
    # 3-voice
    L = [
        'v1_pos:        .byte 0',
        'v2_pos:        .byte 0',
        'v3_pos:        .byte 0',
        'tempo_ctr:     .byte 0',
    ]
    if features['inter_voice_carry_leak']:
        L += [
            'this_skip_sr:  .byte 0',
            'next_skip_sr:  .byte 0',
        ]
    # Per-voice timbre arrays — 5 parallel 15-byte tables. Populated
    # at compile time from the per-voice timbres.
    t1, t2, t3 = features['timbres']
    fields = [
        ('pwlo', 0, t1[0], t2[0], t3[0]),
        ('pwhi', 1, t1[1], t2[1], t3[1]),
        ('ctrl', 2, t1[2], t2[2], t3[2]),
        ('ad',   3, t1[3], t2[3], t3[3]),
        ('sr',   4, t1[4], t2[4], t3[4]),
    ]
    for fname, _fi, v1, v2, v3 in fields:
        # X-indexed at 0, 7, 14 — pad with zeros between voice slots.
        row = [0] * 15
        row[0]  = v1
        row[7]  = v2
        row[14] = v3
        L.append(f'timbre_{fname}: .byte ' +
                 ', '.join(f'${b:02X}' for b in row))
    return L


def _emit_freq_table(features: dict) -> list[str]:
    fh = features['freq_hi']
    fl = features['freq_lo']
    lines = ['freq_hi_tab:']
    for i in range(0, len(fh), 16):
        lines.append('  .byte ' + ', '.join(f'${b:02X}' for b in fh[i:i+16]))
    lines.append('freq_lo_tab:')
    for i in range(0, len(fl), 16):
        lines.append('  .byte ' + ', '.join(f'${b:02X}' for b in fl[i:i+16]))
    return lines


def _emit_orderlists(features: dict) -> list[str]:
    """Emit orderlist data — one labelled block per voice."""
    L: list[str] = []
    n_voices = 3       # always emit 3 labels; inactive voices get $FF stub
    for vid in (1, 2, 3):
        L.append(f'orderlist_v{vid}:')
        ob = _orderlist_bytes(features, vid)
        for i in range(0, len(ob), 16):
            L.append('  .byte ' + ', '.join(
                f'${b:02X}' for b in ob[i:i+16]))
    return L


# ---------------------------------------------------------------------------
# Driver
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
    vc = features['voice_count']

    asm_lines: list[str] = []
    asm_lines += emit_header()
    if vc == 1:
        asm_lines += _emit_1voice_init(features)
        asm_lines += _emit_1voice_play(features)
    else:
        asm_lines += _emit_3voice_init(features)
        asm_lines += _emit_3voice_play(features)
        asm_lines += _emit_3voice_proc_note(features)
        asm_lines += _emit_3voice_voice_steps(features)
    asm_lines += _emit_runtime_vars(features)
    asm_lines += _emit_freq_table(features)
    asm_lines += _emit_orderlists(features)
    asm = '\n'.join(asm_lines) + '\n'

    body = _assemble(asm)
    n_subs = sum(1 for s in usf.subtunes if isinstance(s, MusicSubtune))
    return _psid_header(usf, n_subs, LOAD) + body


def applies_to(usf: UsfFile) -> bool:
    """Does this USF fit what the universal codegen currently handles?

    Used by `pipelines.build_from_usf.build_from_usf` to route. Looks at
    USF *content* (voice count, freq_table size, subtune count); never
    at `usf.engine`. Widens as more features arrive.
    """
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if len(music) != 1:
        return False
    ms = music[0]
    active = [v for v in ms.voices if v.patterns]
    if len(active) not in (1, 3):
        return False
    if usf.freq_table is None or len(usf.freq_table) != 256:
        return False
    if not usf.instruments:
        return False
    return True
