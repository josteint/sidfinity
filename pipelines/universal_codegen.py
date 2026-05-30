"""Universal codegen — USF → SID, designed for any engine family.

Status: seed. Today it handles five engine families across four shapes:

  Atomic-event shape (1 engine byte per tick):
    - 1-voice tunes (henrys_house)
    - 3-voice tunes with loop substitution + inter-voice carry-leak
      quirk (bowden_canonical)

  Pair-encoded shape (2 engine bytes per row: note + duration):
    - 3-voice tick-counter state-machine tunes (yes_tune family —
      Yes_Tune + Soldier_of_Fortune).

  Command-stream shape (1 byte per tick + embedded $Bx/$Cx/$Dx/$Ex
  command bytes that don't consume a tick):
    - 3-voice tunes with recursive command interpreter, mutable
      tempo / master_vol / instrument palette + song-position sync
      (clever_music — Fairlight + Gyroscope).

  Companion shape (Hubbard's 1984 extension of Bowden's base driver):
    - 3-voice, two-tempo (gate_off_tick + note_load_tick) for
      staccato/legato, hardcoded V3 PW_LO sweep, $80+pitch =
      "play with early release", $8C rest, $8D end-song on V3.
      Up_up_and_Away.sid.

All families support multi-subtune USFs. Init takes A = subtune index
and reads per-subtune data tables (init_pos, tempo, timbres, orderlist
pointers) emitted alongside the engine code.

Each engine family that migrates over teaches the codegen new
primitives.

Architecture
============

A pipeline of small asm-emitting functions composed by a driver. The
driver reads the USF, picks which emitters to chain, and assembles
the result. No `*Kind` dispatch — `applies_to(usf)` and `pick_features`
look at USF *content* (instrument modulation programs, orderlist
shape, fx flags, named mechanism params, SFX subtunes) — never at
engine identity (no `usf.engine` lookups, no data-block-size
fingerprints).

  emit_sid(usf)
    ├─ pick_features(usf)        → feature dict + per-subtune feature list
    ├─ emit_header / emit_init   → preamble + init (A = subtune index)
    ├─ emit_play_loop_*          → tempo gate + per-voice processing
    ├─ emit_note_play_*          → SID register writes per played note
    ├─ emit_loop_terminator_*    → $FF handler
    ├─ emit_runtime_vars + data  → zp / freq table / orderlists
    └─ assemble + PSID header
"""

from __future__ import annotations

import os
import struct
import subprocess

from src.usf import UsfFile, MusicSubtune, SfxSubtune


LOAD = 0x1000

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_XA = os.path.join(_ROOT, 'tools', 'xa65', 'xa', 'xa')

_SEMI = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
         'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


# ---------------------------------------------------------------------------
# Feature detection
# ---------------------------------------------------------------------------

def _is_pair_shape(music) -> bool:
    """Pair-shape engine signal: at least one voice carries a real stop
    terminator (entries non-empty AND `stop=True`). henrys_house uses
    `entries=[], stop=True` as a placeholder for unused voice slots —
    that case does NOT signal pair shape.
    """
    for ms in music:
        for v in ms.voices:
            ol = v.orderlist
            if ol.entries and ol.stop:
                return True
    return False


_CMD_PREFIXES = ('tempo=', 'vol=', 'song_pos=')


def _is_command_stream_shape(music) -> bool:
    """Command-stream signal: at least one row carries an embedded
    engine-command flag (tempo / vol / song_pos) or has an explicit
    `instr` on a rest row (the $Dx SET_INSTRUMENT command in clever
    music's pattern stream).
    """
    for ms in music:
        for v in ms.voices:
            for p in v.patterns:
                for r in p.rows:
                    if r.instr is not None and r.pitch.is_rest:
                        return True
                    for f in r.fx_flags:
                        if f.startswith(_CMD_PREFIXES):
                            return True
    return False


def _is_companion_shape(music) -> bool:
    """Companion-shape signal: any subtune carries a `gate_off_tick`
    parameter — the two-tempo divider that distinguishes Hubbard's
    1984 Companion engine from every other family."""
    for ms in music:
        if ms.params and 'gate_off_tick' in ms.params.fields:
            return True
    return False


def _has_rich_modulation(usf) -> bool:
    """Any instrument carries a per-frame modulation program: vibrato
    LFO, PWM accumulator/sweep, multi-step arpeggio, freq-hi slide,
    or odd-frame slide. The codegen needs to produce per-frame
    register writes for these features; emitter chains without those
    capabilities can't reproduce the SID stream.
    """
    for inst in usf.instruments:
        if inst.vibrato.scale != 0:
            return True
        if inst.pwm.mode in ('linear', 'bidirectional'):
            return True
        if len(inst.arp.offsets) > 1:
            return True
        if inst.freq_slide or inst.inc_by2:
            return True
    return False


def _has_multi_pattern_orderlists(music) -> bool:
    """Any voice references multiple distinct patterns through its
    orderlist (or names a pattern other than id=1). Multi-pattern
    dispatch is a play-loop capability — the simple emitter chains
    only handle a single pattern per voice (orderlist entries=[1])."""
    for ms in music:
        for v in ms.voices:
            entries = v.orderlist.entries
            if len(entries) > 1 or (entries and entries[0] != 1):
                return True
            for p in v.patterns:
                if p.id != 1:
                    return True
    return False


def _has_sfx_subtunes(usf) -> bool:
    return any(isinstance(s, SfxSubtune) for s in usf.subtunes)


def _has_state_layout(usf) -> bool:
    return usf.state_layout is not None


def _is_hubbard85_shape(usf, music) -> bool:
    """Detection by USF content features that the simpler shapes can't
    produce:
      - rich per-instrument modulation programs (vibrato / PWM modes /
        multi-step arpeggio / freq-hi slide / inc_by2),
      - multi-pattern orderlists (a voice walks through several patterns),
      - SFX subtunes (sound-effect records the engine plays alongside),
      - a `state_layout` block (off-table-arp state mirror for engines
        that read past the freq table into runtime state).
    These are musical / structural facts about the USF, not engine-id
    fingerprints — a USF with any of them needs the parametric Hubbard
    '85 emitter chain regardless of which engine produced it.
    """
    return (_has_rich_modulation(usf)
            or _has_multi_pattern_orderlists(music)
            or _has_sfx_subtunes(usf)
            or _has_state_layout(usf))


def pick_features(usf: UsfFile) -> dict:
    """Walk the USF and produce a feature dict the emitters consume.

    Features are descriptive musical / structural facts. Engines with
    overlapping musical content share features; engine-quirk behaviors
    surface as named boolean flags (no opaque kinds).
    """
    music = sorted(
        (s for s in usf.subtunes if isinstance(s, MusicSubtune)),
        key=lambda s: s.id)
    if not music:
        raise NotImplementedError('universal codegen requires at least 1 music subtune')

    # Pattern-shape detection by USF content. Order matters: the
    # hubbard85 detection runs first because it keys on the richest
    # content signals (rich instrument modulation, multi-pattern
    # orderlists, SFX subtunes, state_layout) — features the simpler
    # shapes can't produce. The other detections key on shape-specific
    # mechanism markers (gate_off_tick, tempo=/vol=/song_pos= flags,
    # stop terminators) that are content / named-mechanism facts about
    # the USF, never engine-name lookups.
    if _is_hubbard85_shape(usf, music):
        pattern_shape = 'hubbard85'
    elif _is_companion_shape(music):
        pattern_shape = 'companion'
    elif _is_command_stream_shape(music):
        pattern_shape = 'command_stream'
    elif _is_pair_shape(music):
        pattern_shape = 'pair'
    else:
        pattern_shape = 'atomic'

    if pattern_shape == 'hubbard85':
        # The hubbard85 path runs its own asm/data layout via
        # `_hubbard_emit_sid` and consumes a different feature shape
        # (`_Inputs`, built downstream in `_inputs_from_usf`). The
        # high-level dispatcher returns early without going through
        # the per-emitter chain.
        return {'pattern_shape': pattern_shape}

    if pattern_shape == 'atomic':
        # Voice count from active voices in the first subtune.
        active = [v for v in music[0].voices if v.patterns]
        voice_count = len(active)
        if voice_count not in (1, 3):
            raise NotImplementedError(
                f'universal codegen atomic-shape supports 1- or 3-voice; '
                f'got {voice_count}')
        # - `loop_action`: $FF behavior on atomic shape.
        #     'reinit_master_vol' — write $D418 + reset pos (henrys)
        #     'substitute_first'  — pos = 1, play orderlist[0] (bowden)
        loop_action = 'reinit_master_vol' if voice_count == 1 else 'substitute_first'
        # - `inter_voice_carry_leak`: bowden's 4-vs-5-byte timbre choice
        #   based on the prior voice's note byte. On for atomic 3-voice.
        inter_voice_carry_leak = (voice_count == 3)
    elif pattern_shape == 'pair':
        # Pair shape: yes_tune family — 3 voice slots, some may be silent.
        voice_count = 3
        loop_action = 'reset_and_replay'
        inter_voice_carry_leak = False
    elif pattern_shape == 'command_stream':
        # Command-stream shape: clever_music family — 3 voices,
        # 16-instrument palette, song_pos sync, recursive interp.
        voice_count = 3
        loop_action = 'song_pos_jump'
        inter_voice_carry_leak = False
    else:
        # Companion shape: Hubbard's 1984 Companion engine — 3 voices,
        # locked timbre, two-tempo dispatch, V3 hardcoded PW sweep.
        voice_count = 3
        loop_action = 'companion_end_song'
        inter_voice_carry_leak = False

    instr_by_id = {i.id: i for i in usf.instruments}

    def _timbre_of(instr) -> tuple[int, int, int, int, int]:
        return (
            instr.pwm.init & 0xFF,
            (instr.pwm.init >> 8) & 0xFF,
            instr.waveform[0] if instr.waveform else 0,
            instr.adsr[0],
            instr.adsr[1],
        )

    # Per-subtune feature list.
    subtunes_feat: list[dict] = []
    for ms in music:
        # Per-voice instrument lookup. Prefer the subtune's own init.voices
        # (carries per-subtune timbres for multi-subtune USFs).
        init_voices = (ms.init.voices if (ms.init and ms.init.voices)
                       else usf.init.voices)
        voice_to_instr: dict[int, object] = {1: None, 2: None, 3: None}
        for iv in init_voices:
            if iv.instr is not None:
                voice_to_instr[iv.id] = instr_by_id[iv.instr.id]

        timbres = []
        for vid in (1, 2, 3):
            ins = voice_to_instr[vid] or instr_by_id[next(iter(instr_by_id))]
            timbres.append(_timbre_of(ins))

        pat_rows = {v.id: (v.patterns[0].rows if v.patterns else [])
                    for v in ms.voices}
        sp = ms.params.fields if ms.params else {}

        sf = {
            'id':             ms.id,
            'tempo':          ms.tempo,
            'init_pos':       (sp.get('init_pos_v1', 0),
                               sp.get('init_pos_v2', 0),
                               sp.get('init_pos_v3', 0)),
            'init_tempo_ctr': sp.get('init_tempo_ctr', 0),
            'cia1_timer_a':   sp.get('cia1_timer_a', 0),
            'timbres':        timbres,
            'pattern_rows':   pat_rows,
        }
        if pattern_shape == 'pair':
            # Per-voice pre-encoded pattern bytes + initial state byte.
            #   state 0 = silent (orderlist entries=[]),
            #   state 2 = load-pattern (orderlist entries=[1], terminator
            #             encodes $81 stop or $FF loop).
            pat_bytes: dict[int, bytes] = {}
            init_states: dict[int, int] = {}
            for v in ms.voices:
                pb, st = _pair_voice_bytes_and_state(v)
                pat_bytes[v.id] = pb
                init_states[v.id] = st
            sf['pair_pattern_bytes'] = pat_bytes
            sf['pair_init_states']   = init_states
            sf['gain_init_full']     = int(sp.get('gain_init', 'full') == 'full')
        elif pattern_shape == 'command_stream':
            # Per-voice encoded pattern bytes (notes + skip runs + embedded
            # command bytes), plus the engine-wide instrument palette.
            cmd_pat_bytes: dict[int, bytes] = {}
            for v in ms.voices:
                cmd_pat_bytes[v.id] = _cmd_voice_bytes(v)
            sf['cmd_pattern_bytes'] = cmd_pat_bytes
            sf['init_song_pos']     = sp.get('init_song_pos', 0xE0)
            sf['init_master_vol']   = sp.get('init_master_vol', 0x0A)
        elif pattern_shape == 'companion':
            # Per-voice orderlist bytes ($8D-terminated + per-voice post-
            # terminator padding the engine reads past the end).
            # Companion shape uses InitVoice.ctrl as the per-voice
            # ctrl_noGate byte (NOT the instrument's waveform field
            # like other shapes do).
            init_voices = (ms.init.voices if (ms.init and ms.init.voices)
                           else usf.init.voices)
            iv_by_id = {iv.id: iv for iv in init_voices}
            cmp_timbres = []
            for vid in (1, 2, 3):
                iv = iv_by_id.get(vid)
                ins = (instr_by_id[iv.instr.id]
                       if iv and iv.instr else
                       voice_to_instr[vid])
                cmp_timbres.append((
                    ins.pwm.init & 0xFF,
                    (ins.pwm.init >> 8) & 0xFF,
                    iv.ctrl if iv else 0,
                    ins.adsr[0],
                    ins.adsr[1],
                ))
            cmp_ord: dict[int, bytes] = {}
            for v in ms.voices:
                pad_count = sp.get(f'v{v.id}_pad_count', 0)
                pad_byte  = sp.get(f'v{v.id}_pad_byte', 0)
                cmp_ord[v.id] = (
                    _companion_voice_bytes(v)
                    + bytes([pad_byte] * pad_count))
            sf['cmp_timbres']        = cmp_timbres
            sf['cmp_orderlists']     = cmp_ord
            sf['gate_off_tick']      = sp.get('gate_off_tick', 9)
            sf['note_load_tick']     = sp.get('note_load_tick', 13)
            sf['init_tempo_counter'] = sp.get('init_tempo_counter', 0)
            sf['init_pwm_ctr']       = sp.get('init_pwm_ctr', 0)
            sf['init_pwm_ctr_2']     = sp.get('init_pwm_ctr_2', 0)
            sf['vol_filter']         = sp.get('vol_filter', 0x0F)
            sf['filter_cutoff_hi']   = sp.get('filter_cutoff_hi', 0)
        subtunes_feat.append(sf)

    out = {
        'pattern_shape':         pattern_shape,
        'voice_count':           voice_count,
        'freq_hi':               bytes(usf.freq_table[:128]),
        'freq_lo':               bytes(usf.freq_table[128:]),
        'loop_action':           loop_action,
        'inter_voice_carry_leak': inter_voice_carry_leak,
        'master_vol':            0x0F,
        'subtunes':              subtunes_feat,
    }
    if pattern_shape == 'command_stream':
        # The full instrument palette ($Dx index → 5-byte timbre).
        out['cmd_instruments'] = sorted(usf.instruments, key=lambda i: i.id)
    return out


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


def _cmd_row_bytes(row) -> bytes:
    """Command-stream row → engine bytes.

    Notes/rests emit (head, $81×(duration-1)) — one byte per tick, duration
    represented as skip runs. Command flags (tempo/vol/song_pos) and
    `row.instr` emit a single command byte that doesn't consume a tick
    (the engine's interpreter recurses past it).
    """
    flags = set(row.fx_flags)
    if not row.pitch.is_rest:
        head = (row.pitch.octave << 4) | _SEMI[row.pitch.name]
        return bytes([head]) + bytes([0x81] * (row.duration - 1))
    if row.instr is not None:
        return bytes([0xD0 | ((row.instr.id - 1) & 0x0F)])
    for flag in flags:
        if flag.startswith('tempo='):
            return bytes([0xB0 | (int(flag.split('=')[1]) & 0x0F)])
        if flag.startswith('vol='):
            return bytes([0xC0 | (int(flag.split('=')[1]) & 0x0F)])
        if flag.startswith('song_pos='):
            return bytes([0xE0 | (int(flag.split('=')[1]) & 0x0F)])
        if flag.startswith('fx:raw_'):
            return bytes([int(flag.split('_')[1], 16)])
    return bytes([0x80]) + bytes([0x81] * (row.duration - 1))


def _companion_row_byte(row) -> int:
    """Companion shape row → 1 engine byte.

    Normal pitch → (octave<<4)|semi.
    Rest → $8C.
    fx:early_release flag adds the $80 bit (or → $8C for rest+early).
    """
    early = 'fx:early_release' in row.fx_flags
    if row.pitch.is_rest:
        if not early:
            raise ValueError(
                f'voice has a rest row without fx:early_release — '
                f'companion shape can\'t represent that musically')
        return 0x8C
    pitch_byte = (row.pitch.octave << 4) | _SEMI[row.pitch.name]
    return pitch_byte | (0x80 if early else 0)


def _companion_voice_bytes(vb) -> bytes:
    """One voice's orderlist body + the $8D end-song terminator."""
    if not vb.patterns:
        raise ValueError(f'voice {vb.id} has no patterns')
    pat = vb.patterns[0]
    body = bytes(_companion_row_byte(r) for r in pat.rows)
    return body + bytes([0x8D])


def _companion_template_bytes(sub_feat: dict) -> bytes:
    """The 32-byte init template the engine copies into v_state at init.

    Layout: V1 (pos=0, gate_off_flag=0, pw_lo, pw_hi, ctrl_noGate, ad, sr),
    V2, V3 (same), then gate_off_tick, note_load_tick, init_tempo_counter,
    6 zeros (original engine had self-modifying-code bytes here), then
    init_pwm_ctr, init_pwm_ctr_2.
    """
    out = []
    for v_idx in range(3):
        t = sub_feat['cmp_timbres'][v_idx]
        out += [0, 0, t[0], t[1], t[2], t[3], t[4]]
    out += [
        sub_feat['gate_off_tick'],
        sub_feat['note_load_tick'],
        sub_feat['init_tempo_counter'],
        0, 0, 0, 0, 0, 0,
        sub_feat['init_pwm_ctr'],
        sub_feat['init_pwm_ctr_2'],
    ]
    assert len(out) == 32, len(out)
    return bytes(out)


def _inst_timbre_block(inst) -> bytes:
    """5-byte (pw_lo, pw_hi, ctrl, ad, sr) timbre block — the inst_table
    entry the command-stream engine reads on a $Dx SET_INSTRUMENT."""
    pw_lo = inst.pwm.init & 0xFF
    pw_hi = (inst.pwm.init >> 8) & 0xFF
    ctrl = inst.waveform[0] if inst.waveform else 0
    ad, sr = inst.adsr
    return bytes([pw_lo, pw_hi, ctrl, ad, sr])


def _cmd_voice_bytes(vb) -> bytes:
    """Concatenate one voice's pattern rows into the command-stream byte
    sequence the engine reads."""
    if not vb.patterns:
        raise ValueError(f'voice {vb.id} has no patterns')
    pat = vb.patterns[0]
    return b''.join(_cmd_row_bytes(r) for r in pat.rows)


def _pair_row_bytes(row) -> bytes:
    """(note, duration) pair for one row in pair-shape engines."""
    for f in row.fx_flags:
        if f.startswith('fx:raw_'):
            return bytes([int(f.split('_')[1], 16), row.duration & 0xFF])
    if row.pitch.is_rest:
        return bytes([0x80, row.duration & 0xFF])
    note = (row.pitch.octave << 4) | _SEMI[row.pitch.name]
    return bytes([note, row.duration & 0xFF])


def _pair_voice_bytes_and_state(vb) -> tuple[bytes, int]:
    """Encode one VoiceBlock as pair-shape pattern bytes + init state.

      orderlist entries=[]      → silent voice: $81 sentinel, state=0.
      orderlist entries=[1] stop → state=2, body + $81 stop terminator.
      orderlist entries=[1] loop → state=2, body + $FF loop terminator.
    """
    ol = vb.orderlist
    if not ol.entries:
        return bytes([0x81]), 0x00
    if len(ol.entries) != 1 or ol.entries[0] != 1:
        raise ValueError(
            f'voice {vb.id}: pair shape supports single-pattern orderlist '
            f'([1]); got {ol.entries}')
    pat = vb.patterns[0]
    body = b''.join(_pair_row_bytes(r) for r in pat.rows)
    if ol.stop:
        return body + bytes([0x81]), 0x02
    if ol.loop_to is not None:
        return body + bytes([0xFF]), 0x02
    raise ValueError(
        f'voice {vb.id}: orderlist must terminate with stop or loop@N')


def _orderlist_bytes(sub_feat: dict, vid: int) -> bytes:
    rows = sub_feat['pattern_rows'].get(vid, [])
    if not rows:
        # Inactive voice — emit a single $FF terminator (engine reads it
        # and loops; in practice the voice never starts because its
        # init_pos is set to skip).
        return bytes([0xFF])
    return b''.join(_row_to_bytes(r) for r in rows) + bytes([0xFF])


# ---------------------------------------------------------------------------
# Asm emitters — 3-voice family (bowden_canonical)
# ---------------------------------------------------------------------------

# Zero-page slots for the per-voice orderlist pointers.
ZP_OL_V1_LO, ZP_OL_V1_HI = 0xE0, 0xE1
ZP_OL_V2_LO, ZP_OL_V2_HI = 0xE2, 0xE3
ZP_OL_V3_LO, ZP_OL_V3_HI = 0xE4, 0xE5


def _emit_3voice_init(features: dict, has_cia: bool) -> list[str]:
    """Init: A = subtune index. Reads per-subtune scalar/timbre/orderlist
    pointer tables.

    Init-frame SID writes don't have to match the original engine's exact
    init — `skip_init=True` in the per-frame comparison drops frame 0.
    """
    L: list[str] = [
        'init:',
        '  pha                  ; save A = subtune idx',
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
        '  pla',
        '  tax                  ; X = subtune index',
        # Per-subtune scalar setup.
        '  lda init_v1_pos_tab,x',
        '  sta v1_pos',
        '  lda init_v2_pos_tab,x',
        '  sta v2_pos',
        '  lda init_v3_pos_tab,x',
        '  sta v3_pos',
        '  lda init_tempo_ctr_tab,x',
        '  sta tempo_ctr',
        '  lda tempo_tab,x',
        '  sta tempo_const',
    ]
    # Per-subtune timbre fill — 5 fields × 3 voices, into X-indexed RAM
    # arrays at offsets 0, 7, 14.
    fields = ['pwlo', 'pwhi', 'ctrl', 'ad', 'sr']
    for fname in fields:
        for v, off in enumerate((0, 7, 14)):
            L.append(f'  lda v{v+1}_{fname}_tab,x')
            L.append(f'  sta timbre_{fname}+{off}')
    # Per-subtune orderlist pointers (zp).
    L += [
        '  lda v1_ol_lo_tab,x',
        f'  sta ${ZP_OL_V1_LO:02X}',
        '  lda v1_ol_hi_tab,x',
        f'  sta ${ZP_OL_V1_HI:02X}',
        '  lda v2_ol_lo_tab,x',
        f'  sta ${ZP_OL_V2_LO:02X}',
        '  lda v2_ol_hi_tab,x',
        f'  sta ${ZP_OL_V2_HI:02X}',
        '  lda v3_ol_lo_tab,x',
        f'  sta ${ZP_OL_V3_LO:02X}',
        '  lda v3_ol_hi_tab,x',
        f'  sta ${ZP_OL_V3_HI:02X}',
    ]
    if has_cia:
        L += [
            '  lda cia1_lo_tab,x',
            '  sta $dc04',
            '  lda cia1_hi_tab,x',
            '  sta $dc05',
        ]
    L.append('  rts')
    return L


def _emit_3voice_play(features: dict) -> list[str]:
    """Play loop: gate by tempo_const RAM byte, process V1/V2/V3 in order."""
    leak = features['inter_voice_carry_leak']
    L: list[str] = [
        'play:',
        '  inc tempo_ctr',
        '  lda tempo_ctr',
        '  cmp tempo_const',
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

    The `this_skip_sr` flag suppresses the SR write when set (bowden
    carry-leak: a prior voice's skip note leaves carry=0, making the
    next voice's PW loop short-circuit one iteration — the SR write).
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
        '  sta $d404,x          ; junk write (gate=0) for envelope retrigger',
        '  lda timbre_ad,x',
        '  sta $d405,x',
        '  lda this_skip_sr',
        '  bne pn_no_sr_write',
        '  lda timbre_sr,x',
        '  sta $d406,x',
        'pn_no_sr_write:',
        '  lda timbre_ctrl,x',
        '  ora #$01',
        '  sta $d404,x          ; gate=1, finalises envelope retrigger',
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
    """Per-voice step: read byte, handle $FF substitution, classify byte
    to set `next_skip_sr`, call proc_note."""
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
# Asm emitters — pair-shape (yes_tune family: Yes_Tune + Soldier_of_Fortune)
# ---------------------------------------------------------------------------
#
# Per-voice state at `v_state + X` (X = 0/7/14):
#   +$00  tick_ctr     (decrements; plays next pair when reaches 0)
#   +$01  state        (0=silent, 1=normal, 2=load-pattern)
#   +$02..+$06  timbre (5 bytes: pw_lo, pw_hi, ctrl, ad, sr)
#   +$15  pattern_ptr lo (current position)
#   +$16  pattern_ptr hi
#   +$17  pat_start lo (immutable reset target)
#   +$18  pat_start hi
#
# Pattern bytes: $00-$7F dur (note + duration), $80 dur (rest + duration),
# $81 (stop), $FF (loop to pat_start).

def _emit_pair_init(features: dict) -> list[str]:
    """Init: A = subtune index. Loads per-voice state from per-subtune
    tables; writes $D418=$0F only when gain_init='full'."""
    L: list[str] = [
        'init:',
        '  pha                  ; save A = subtune idx',
        '  tay                  ; Y = subtune index',
        '  lda init_d418_tab,y',
        '  beq init_skip_d418',
        f'  lda #${features["master_vol"]:02X}',
        '  sta $d418',
        'init_skip_d418:',
        '  pla',
        '  tay                  ; Y = subtune index',
    ]
    for v_idx, x in enumerate((0, 7, 14)):
        L.append(f'  ; V{v_idx+1} init from sub-Y tables')
        for j in range(5):
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
        L.append('  lda #$00')
        L.append(f'  sta v_state+${0x00+x:02X}')
    L += [
        '  lda tempo_tab,y',
        '  sta tempo_const',
        '  lda init_tempo_ctr_tab,y',
        '  sta tempo_ctr',
        '  rts',
    ]
    return L


def _emit_pair_play(features: dict) -> list[str]:
    L: list[str] = [
        'play:',
        '  inc tempo_ctr',
        '  lda tempo_ctr',
        '  cmp tempo_const',
        '  bne play_exit',
        '  lda #0',
        '  sta tempo_ctr',
    ]
    for v, x in enumerate((0, 7, 14)):
        L.append(f'  ldx #{x}')
        L.append('  jsr voice_tick')
    L += [
        'play_exit:',
        '  rts',
    ]
    return L


def _emit_pair_voice_tick() -> list[str]:
    return [
        'voice_tick:',
        '  lda v_state+1,x      ; state',
        '  cmp #2',
        '  bne vt_chk1',
        '  lda v_state+$17,x',
        '  sta v_state+$15,x    ; ptr = pat_start',
        '  lda v_state+$18,x',
        '  sta v_state+$16,x',
        '  lda #0',
        '  sta v_state,x        ; tick_ctr = 0',
        '  lda #1',
        '  sta v_state+1,x',
        'vt_chk1:',
        '  lda v_state+1,x',
        '  cmp #1',
        '  beq vt_play',
        '  rts                  ; state != 1 - skip',
        'vt_play:',
        '  lda v_state+$15,x',
        '  sta $fb',
        '  lda v_state+$16,x',
        '  sta $fc',
        '  jmp play_note        ; tail-call (X preserved)',
    ]


def _emit_pair_play_note() -> list[str]:
    return [
        'play_note:',
        '  ldy #0',
        '  lda ($fb),y',
        '  and #$80',
        '  beq pn_normal',
        '  jmp pn_bit7',
        'pn_normal:',
        '  ldy v_state,x        ; tick_ctr',
        '  cpy #0',
        '  bne pn_dec',
        '  jsr pn_emit_note',
        '  jsr pn_advance',
        'pn_dec:',
        '  dec v_state,x',
        '  rts',
        'pn_emit_note:',
        '  ldy #0',
        '  lda ($fb),y',
        '  tay',
        '  lda freq_hi_tab,y',
        '  sta $d401,x',
        '  lda freq_lo_tab,y',
        '  sta $d400,x',
        '  txa',
        '  tay',
        '  clc',
        '  adc #$05',
        '  sta pn_endy',
        'pn_pw_loop:',
        '  lda v_state+2,y',
        '  sta $d402,y',
        '  iny',
        '  cpy pn_endy',
        '  bne pn_pw_loop',
        '  ldy v_state+4,x',
        '  iny',
        '  tya',
        '  sta $d404,x',
        '  rts',
        'pn_advance:',
        '  ldy #1',
        '  lda ($fb),y',
        '  cmp #0',
        '  bne pn_adv_ok',
        '  lda #1',
        'pn_adv_ok:',
        '  sta v_state,x',
        '  lda v_state+$15,x',
        '  clc',
        '  adc #2',
        '  sta v_state+$15,x',
        '  bcc pn_adv_done',
        '  inc v_state+$16,x',
        'pn_adv_done:',
        '  rts',
        'pn_bit7:',
        '  ldy #0',
        '  lda ($fb),y',
        '  cmp #$80',
        '  bne pn_n80',
        # $80 - rest with duration
        '  ldy v_state,x        ; tick_ctr',
        '  cpy #0',
        '  bne pn_dec',
        '  lda v_state+4,x      ; ctrl',
        '  sta $d404,x',
        '  jsr pn_advance',
        '  jmp pn_dec',
        'pn_n80:',
        '  cmp #$ff',
        '  bne pn_nff',
        # $FF - loop
        '  lda v_state+$17,x',
        '  sta v_state+$15,x',
        '  lda v_state+$18,x',
        '  sta v_state+$16,x',
        '  lda #0',
        '  sta v_state,x',
        '  lda v_state+$15,x',
        '  sta $fb',
        '  lda v_state+$16,x',
        '  sta $fc',
        '  jmp play_note',
        'pn_nff:',
        '  cmp #$81',
        '  bne pn_other',
        # $81 - stop voice
        '  lda v_state+4,x',
        '  sta $d404,x',
        '  lda #0',
        '  sta v_state+1,x',
        'pn_other:',
        '  rts',
    ]


# ---------------------------------------------------------------------------
# Asm emitters — command-stream shape (clever_music family)
# ---------------------------------------------------------------------------
#
# Per-voice state at `v_state + X` (X = 0/7/14):
#   +$00  pattern_ptr lo
#   +$01  pattern_ptr hi
#   +$02..+$06  timbre slot (pw_lo, pw_hi, ctrl, ad, sr) — set by $Dx
#
# Per-voice duration counter at `dur_ctr + (X >> 3)` (stride 1: 0/1/2).
# load_note runs when dur_ctr == 1; otherwise dec dur_ctr.
#
# Globals: tempo_const, tempo_ctr, song_pos. tempo_const + master_vol +
# instrument palette are all RAM-mutable mid-stream.

def _emit_cmd_init(features: dict, has_cia: bool) -> list[str]:
    """Init: A = subtune index. Loads per-voice ptr lo/hi from song_table
    (E0..E2 = V1/V2/V3 starts), dur_ctr=1 for all 3 voices, song_pos and
    master_vol from per-subtune tables, tempo + tempo_ctr likewise. CIA1
    timer programmed only if at least one subtune wants it."""
    L: list[str] = [
        'init:',
        '  pha                  ; save A = subtune idx',
        '  lda #0',
        '  ldx #0',
        'init_silence:',
        '  sta $d400,x',
        '  inx',
        '  cpx #$19',
        '  bne init_silence',
        '  pla',
        '  tax                  ; X = subtune index',
        '  lda init_master_vol_tab,x',
        '  sta $d418',
        '  lda song_table+0',
        '  sta v_state+0        ; V1 ptr lo',
        '  lda song_table+1',
        '  sta v_state+1        ; V1 ptr hi',
        '  lda song_table+2',
        '  sta v_state+7        ; V2 ptr lo',
        '  lda song_table+3',
        '  sta v_state+8        ; V2 ptr hi',
        '  lda song_table+4',
        '  sta v_state+14       ; V3 ptr lo',
        '  lda song_table+5',
        '  sta v_state+15       ; V3 ptr hi',
        '  lda #1',
        '  sta dur_ctr+0',
        '  sta dur_ctr+1',
        '  sta dur_ctr+2',
        '  lda init_song_pos_tab,x',
        '  sta song_pos',
        '  lda tempo_tab,x',
        '  sta tempo_const',
        '  lda init_tempo_ctr_tab,x',
        '  sta tempo_ctr',
    ]
    if has_cia:
        L += [
            '  lda cia1_lo_tab,x',
            '  sta $dc04',
            '  lda cia1_hi_tab,x',
            '  sta $dc05',
        ]
    L.append('  rts')
    return L


def _emit_cmd_play() -> list[str]:
    L = [
        'play:',
        '  inc tempo_ctr',
        '  lda tempo_ctr',
        '  cmp tempo_const',
        '  bne play_exit',
        '  lda #0',
        '  sta tempo_ctr',
    ]
    for v, (x, dur_off) in enumerate([(0, 0), (7, 1), (14, 2)]):
        L += [
            f'  ldx #{x}',
            f'  lda dur_ctr+{dur_off}',
            '  cmp #1',
            f'  bne v{v+1}_dec',
            '  jsr load_note',
            f'  jmp v{v+1}_done',
            f'v{v+1}_dec:',
            f'  dec dur_ctr+{dur_off}',
            f'v{v+1}_done:',
        ]
    L += [
        'play_exit:',
        '  rts',
    ]
    return L


def _emit_cmd_load_note() -> list[str]:
    """Recursive command interpreter — X = voice offset (0/7/14).

    Reads one byte; dispatches: $00-$7F NORMAL_NOTE plays, $80 REST gates
    off, $81 SKIP returns, $82 dur SET_DURATION, $Bx tempo, $Cx vol,
    $Dx instr (copy 5 bytes from inst_table), $Ex pattern_jump (when
    Y == song_pos: jump via song_table, advance song_pos $E5→$E0, recurse).
    Most commands recurse to consume the next byte in the same tick.
    """
    return [
        '; load_note expects X as voice offset 0,7,14',
        'load_note:',
        '  ldy #0',
        '  lda v_state+0,x      ; ptr lo',
        '  sta zp_ptr_lo',
        '  lda v_state+1,x      ; ptr hi',
        '  sta zp_ptr_hi',
        '  inc v_state+0,x      ; advance ptr',
        '  bne ln_skip_inc_hi',
        '  inc v_state+1,x',
        'ln_skip_inc_hi:',
        '  lda (zp_ptr_lo),y     ; read byte',
        '  tay',
        '  and #$80',
        '  bne ln_bit7',
        # NORMAL NOTE path
        '  lda freq_hi_tab,y',
        '  sta $d401,x',
        '  lda freq_lo_tab,y',
        '  sta $d400,x',
        '  txa',
        '  tay',
        '  clc',
        '  adc #$05',
        '  sta zp_endy',
        'ln_pw_loop:',
        '  lda v_state+2,y       ; timbre[y]',
        '  sta $d402,y',
        '  iny',
        '  cpy zp_endy',
        '  bne ln_pw_loop',
        '  ldy v_state+4,x       ; ctrl byte',
        '  iny',
        '  tya',
        '  sta $d404,x           ; gate=1',
        '  rts',
        'ln_bit7:',
        '  cpy #$80',
        '  bne ln_not80',
        '  lda v_state+4,x       ; ctrl (gate off)',
        '  sta $d404,x',
        '  rts',
        'ln_not80:',
        '  cpy #$81',
        '  bne ln_not81',
        '  rts',
        'ln_not81:',
        '  cpy #$82',
        '  bne ln_not82',
        # SET_DURATION: gate off, read next byte as new dur
        '  lda v_state+4,x',
        '  sta $d404,x',
        '  lda v_state+0,x',
        '  sta zp_ptr_lo',
        '  lda v_state+1,x',
        '  sta zp_ptr_hi',
        '  inc v_state+0,x',
        '  bne ln82_no_carry',
        '  inc v_state+1,x',
        'ln82_no_carry:',
        '  txa                   ; transform X (0/7/14) → (0/1/2)',
        '  clc',
        '  ror',
        '  clc',
        '  adc #$01',
        '  clc',
        '  ror',
        '  clc',
        '  ror',
        '  stx zp_x_save',
        '  tax',
        '  ldy #0',
        '  lda (zp_ptr_lo),y',
        '  sta dur_ctr,x',
        '  ldx zp_x_save',
        '  rts',
        'ln_not82:',
        # $Ex pattern jump (if Y == song_pos)
        '  cpy song_pos',
        '  bne ln_not_ex',
        '  inc song_pos',
        '  lda song_pos',
        '  cmp #$e6',
        '  bne ln_no_wrap',
        '  lda #$e0',
        '  sta song_pos',
        'ln_no_wrap:',
        '  tya                   ; Y = $Ex',
        '  and #$0f',
        '  clc',
        '  rol                   ; *2 for 16-bit indexing',
        '  tay',
        '  lda song_table,y',
        '  sta v_state+0,x',
        '  iny',
        '  lda song_table,y',
        '  sta v_state+1,x',
        '  jsr load_note         ; recurse with new ptr',
        '  rts',
        'ln_not_ex:',
        # $Dx SET_INSTRUMENT — copy 5 bytes from inst_table
        '  tya',
        '  and #$f0',
        '  cmp #$d0',
        '  bne ln_not_dx',
        '  tya',
        '  and #$0f',
        '  sta zp_tmp',
        '  asl                   ; *2',
        '  asl                   ; *4',
        '  clc',
        '  adc zp_tmp            ; *5',
        '  tay',
        '  stx zp_x_save',
        '  txa',
        '  clc',
        '  adc #2                ; → timbre slot offset from v_state base',
        '  tax',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  inx',
        '  iny',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  inx',
        '  iny',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  inx',
        '  iny',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  inx',
        '  iny',
        '  lda inst_table,y',
        '  sta v_state,x',
        '  ldx zp_x_save',
        '  jsr load_note',
        '  rts',
        'ln_not_dx:',
        # $Cx SET_MASTER_VOL
        '  tya',
        '  and #$f0',
        '  cmp #$c0',
        '  bne ln_not_cx',
        '  tya',
        '  and #$0f',
        '  sta $d418',
        '  jsr load_note',
        '  rts',
        'ln_not_cx:',
        # $Bx SET_TEMPO
        '  tya',
        '  and #$f0',
        '  cmp #$b0',
        '  bne ln_other_bit7',
        '  tya',
        '  and #$0f',
        '  sta tempo_const',
        '  jsr load_note',
        '  rts',
        'ln_other_bit7:',
        # Unrecognized bit-7 byte — engine treats as SKIP_BYTE + recurse
        '  jsr load_note',
        '  rts',
    ]


# ---------------------------------------------------------------------------
# Asm emitters — companion shape (Hubbard's 1984 Companion engine)
# ---------------------------------------------------------------------------
#
# 32-byte template at v_state:
#   bytes 0..6   V1 (pos, gate_off_flag, pw_lo, pw_hi, ctrl_noGate, ad, sr)
#   bytes 7..13  V2 (same layout)
#   bytes 14..20 V3 (same layout)
#   byte 21      gate_off_tick     (early-release timer cap)
#   byte 22      note_load_tick    (next-note timer cap)
#   byte 23      init_tempo_counter
#   bytes 24..29 6 zeros (engine had self-modifying-code bytes here)
#   bytes 30..31 init_pwm_ctr, init_pwm_ctr_2
#
# Globals: g_tempo_ctr (== v_state+23 in original, but here separate),
# g_pwm_ctr (== v_state+30), g_song_alive (1 byte).

def _emit_companion_init() -> list[str]:
    """A = subtune idx. Copies 32-byte template into v_state, loads
    orderlist zp pointers from per-subtune tables, programs filter +
    master vol, marks song alive."""
    return [
        'init:',
        '  sta sub_idx',
        '  ldx sub_idx',
        '  lda tmpl_lo,x',
        '  sta cmp_tcopy+1',
        '  lda tmpl_hi,x',
        '  sta cmp_tcopy+2',
        '  ldx #0',
        'cmp_tcopy:',
        '  lda $FFFF,x          ; OPERAND patched at runtime',
        '  sta v_state,x',
        '  inx',
        '  cpx #32',
        '  bne cmp_tcopy',
        '  ldx sub_idx',
        '  lda ord_v1_lo,x',
        f'  sta ${0xE0:02X}',
        '  lda ord_v1_hi,x',
        f'  sta ${0xE1:02X}',
        '  lda ord_v2_lo,x',
        f'  sta ${0xE2:02X}',
        '  lda ord_v2_hi,x',
        f'  sta ${0xE3:02X}',
        '  lda ord_v3_lo,x',
        f'  sta ${0xE4:02X}',
        '  lda ord_v3_hi,x',
        f'  sta ${0xE5:02X}',
        '  lda sub_fcHi,x',
        '  sta $D416',
        '  lda #0',
        '  sta $D417',
        '  lda sub_vol,x',
        '  sta $D418',
        '  lda #1',
        '  sta g_song_alive',
        '  rts',
    ]


def _emit_companion_play() -> list[str]:
    """Two-tempo play loop:

    PWM block first — global pwm_ctr toggles 0/1 every frame; on the
    1→0 transition, V3.PW_LO += 5 (the original engine relies on
    carry=1 from the CMP, so the effective step is +5 not +4) and
    writes $D410.

    Then the tempo counter increments. If it hits gate_off_tick:
    `maybe_gate_off` per voice (early-release scheduled by bit-7
    save). If it hits note_load_tick: reset counter, advance each
    voice's orderlist by 1, dispatch through proc_note.
    """
    return [
        'play:',
        '  inc g_pwm_ctr',
        '  lda g_pwm_ctr',
        '  cmp #$01',
        '  bne cmp_pwm_done',
        '  lda #0',
        '  sta g_pwm_ctr',
        '  lda v_state+16        ; V3 pw_lo',
        # CMP set carry=1; ADC #4 → +5 effective step.
        '  adc #4',
        '  sta v_state+16',
        '  sta $D410',
        'cmp_pwm_done:',
        '  inc g_tempo_ctr',
        '  lda g_tempo_ctr',
        '  cmp v_state+21        ; gate_off_tick',
        '  bne cmp_not_gate_off',
        '  ldx #0',
        '  jsr cmp_maybe_gate_off',
        '  ldx #7',
        '  jsr cmp_maybe_gate_off',
        '  ldx #14',
        '  jsr cmp_maybe_gate_off',
        '  jmp cmp_play_done',
        'cmp_not_gate_off:',
        '  cmp v_state+22        ; note_load_tick',
        '  bne cmp_play_done',
        '  lda #0',
        '  sta g_tempo_ctr',
        '  ldx #0',
        '  ldy v_state+0',
        '  inc v_state+0',
        f'  lda (${0xE0:02X}),y',
        '  tay',
        '  jsr cmp_proc_note',
        '  ldx #7',
        '  ldy v_state+7',
        '  inc v_state+7',
        f'  lda (${0xE2:02X}),y',
        '  tay',
        '  jsr cmp_proc_note',
        '  ldx #14',
        '  ldy v_state+14',
        '  inc v_state+14',
        f'  lda (${0xE4:02X}),y',
        '  tay',
        '  jsr cmp_proc_note',
        'cmp_play_done:',
        '  rts',
    ]


def _emit_companion_maybe_gate_off() -> list[str]:
    return [
        'cmp_maybe_gate_off:',
        '  lda v_state+1,x       ; gate_off flag',
        '  bmi cmp_do_gate_off',
        '  rts',
        'cmp_do_gate_off:',
        '  lda v_state+4,x       ; ctrl_noGate',
        '  sta $D404,x',
        '  lda #0',
        '  sta v_state+1,x',
        '  rts',
    ]


def _emit_companion_proc_note() -> list[str]:
    """X = voice offset (0/7/14), Y = note byte.

    bit-7 clear → normal note: write freq + timbre + gate-on ctrl.
    bit-7 set  → save flag at v_state+1,x, then check sentinels:
      $0C → rest (gate off)
      $0D → end_or_rest (gate off; if V3, vol=0 + song_alive=0)
      else $80+pitch → play pitch + leave bit-7 flag set so
                       maybe_gate_off fires at next gate_off_tick.
    """
    return [
        'cmp_proc_note:',
        '  tya',
        '  and #$80',
        '  beq cmp_proc_normal',
        '  sta v_state+1,x       ; flag = $80',
        '  tya',
        '  and #$7F',
        '  tay',
        '  cpy #$0C',
        '  beq cmp_proc_rest',
        '  cpy #$0D',
        '  beq cmp_proc_end_or_rest',
        'cmp_proc_normal:',
        '  lda freq_hi_tab,y',
        '  sta $D401,x',
        '  lda freq_lo_tab,y',
        '  sta $D400,x',
        # Skip pw_lo for V3 — V3's PW_LO is driven only by the global sweep.
        '  cpx #14',
        '  beq cmp_skip_pwlo',
        '  lda v_state+2,x',
        '  sta $D402,x',
        'cmp_skip_pwlo:',
        '  lda v_state+3,x',
        '  sta $D403,x',
        '  lda v_state+5,x',
        '  sta $D405,x',
        '  lda v_state+6,x',
        '  sta $D406,x',
        '  lda v_state+4,x       ; ctrl_noGate',
        '  ora #$01              ; gate on',
        '  sta $D404,x',
        '  rts',
        'cmp_proc_rest:',
        '  lda v_state+4,x',
        '  sta $D404,x',
        '  rts',
        'cmp_proc_end_or_rest:',
        '  lda v_state+4,x',
        '  sta $D404,x',
        '  cpx #14',
        '  bne cmp_proc_end_done',
        '  lda #0',
        '  sta g_song_alive',
        '  sta $D418',
        'cmp_proc_end_done:',
        '  rts',
    ]


# ---------------------------------------------------------------------------
# Shared emitters
# ---------------------------------------------------------------------------

def emit_header() -> list[str]:
    return [f'* = ${LOAD:04X}', '  jmp init', '  jmp play']


def _emit_runtime_vars(features: dict) -> list[str]:
    if features['pattern_shape'] == 'companion':
        return [
            'sub_idx:       .byte 0',
            'g_song_alive:  .byte 0',
            # 32-byte template area. g_tempo_ctr and g_pwm_ctr deliberately
            # share memory with v_state+23 (init_tempo_counter) and
            # v_state+30 (init_pwm_ctr) — the template copy at init seeds
            # both runtime counters, which the engine then mutates in place.
            'v_state:       .dsb 32, 0',
            'g_tempo_ctr = v_state+23',
            'g_pwm_ctr   = v_state+30',
        ]
    if features['pattern_shape'] == 'command_stream':
        return [
            'zp_ptr_lo = $FB',
            'zp_ptr_hi = $FC',
            'zp_endy:     .byte 0',
            'zp_x_save:   .byte 0',
            'zp_tmp:      .byte 0',
            # Per-voice state (3 voices × 7 bytes stride).
            'v_state:     .dsb 21, 0',
            # Duration counters (stride 1).
            'dur_ctr:     .dsb 3, 0',
            'tempo_const: .byte 0',
            'tempo_ctr:   .byte 0',
            'song_pos:    .byte 0',
        ]
    if features['pattern_shape'] == 'pair':
        return [
            'pn_endy:     .byte 0',
            'tempo_const: .byte 0',
            'tempo_ctr:   .byte 0',
            # Per-voice state block, X-indexed at offsets 0/7/14.
            # Allocate $20 bytes to cover the largest offset ($18) plus
            # +14 (V3 base).
            'v_state:     .dsb $20, 0',
        ]
    # atomic 3-voice (1-voice atomic shape was retired in Phase 3 of
    # the composer rewrite — the composer owns those USFs now)
    L = [
        'v1_pos:        .byte 0',
        'v2_pos:        .byte 0',
        'v3_pos:        .byte 0',
        'tempo_ctr:     .byte 0',
        'tempo_const:   .byte 0',
    ]
    if features['inter_voice_carry_leak']:
        L += [
            'this_skip_sr:  .byte 0',
            'next_skip_sr:  .byte 0',
        ]
    for fname in ('pwlo', 'pwhi', 'ctrl', 'ad', 'sr'):
        L.append(f'timbre_{fname}: .dsb 15, 0')
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


def _emit_subtune_tables(features: dict) -> list[str]:
    """Per-subtune scalar / timbre / orderlist-pointer byte tables."""
    subs = features['subtunes']
    n = len(subs)
    L: list[str] = []

    def _tab(label: str, values: list[int]) -> None:
        L.append(f'{label}: .byte ' +
                 ', '.join(f'${v & 0xFF:02X}' for v in values))

    if features['pattern_shape'] == 'companion':
        # Per-subtune filter cutoff + master vol byte tables.
        _tab('sub_fcHi',  [s['filter_cutoff_hi'] for s in subs])
        _tab('sub_vol',   [s['vol_filter'] for s in subs])
        # Per-subtune 32-byte template + per-voice orderlist labels.
        # Layout: orderlists adjacent (V1 → V2 → V3 → template) so the
        # engine's "read past $8D" behavior reads predictable bytes from
        # the next block.
        for s in subs:
            sid = s['id']
            L.append(f'ord_s{sid}_v1:')
            ob = s['cmp_orderlists'][1]
            for i in range(0, len(ob), 16):
                L.append('  .byte ' + ', '.join(f'${b:02X}' for b in ob[i:i+16]))
            L.append(f'ord_s{sid}_v2:')
            ob = s['cmp_orderlists'][2]
            for i in range(0, len(ob), 16):
                L.append('  .byte ' + ', '.join(f'${b:02X}' for b in ob[i:i+16]))
            L.append(f'ord_s{sid}_v3:')
            ob = s['cmp_orderlists'][3]
            for i in range(0, len(ob), 16):
                L.append('  .byte ' + ', '.join(f'${b:02X}' for b in ob[i:i+16]))
            tmpl = _companion_template_bytes(s)
            L.append(f'tmpl_s{sid}:')
            L.append('  .byte ' + ', '.join(f'${b:02X}' for b in tmpl[:16]))
            L.append('  .byte ' + ', '.join(f'${b:02X}' for b in tmpl[16:32]))
        L.append('ord_v1_lo: .byte ' + ', '.join(
            f'<ord_s{s["id"]}_v1' for s in subs))
        L.append('ord_v1_hi: .byte ' + ', '.join(
            f'>ord_s{s["id"]}_v1' for s in subs))
        L.append('ord_v2_lo: .byte ' + ', '.join(
            f'<ord_s{s["id"]}_v2' for s in subs))
        L.append('ord_v2_hi: .byte ' + ', '.join(
            f'>ord_s{s["id"]}_v2' for s in subs))
        L.append('ord_v3_lo: .byte ' + ', '.join(
            f'<ord_s{s["id"]}_v3' for s in subs))
        L.append('ord_v3_hi: .byte ' + ', '.join(
            f'>ord_s{s["id"]}_v3' for s in subs))
        L.append('tmpl_lo:   .byte ' + ', '.join(
            f'<tmpl_s{s["id"]}' for s in subs))
        L.append('tmpl_hi:   .byte ' + ', '.join(
            f'>tmpl_s{s["id"]}' for s in subs))
        return L

    _tab('tempo_tab',          [s['tempo'] for s in subs])
    _tab('init_tempo_ctr_tab', [s['init_tempo_ctr'] for s in subs])

    if features['pattern_shape'] == 'command_stream':
        _tab('init_song_pos_tab',  [s['init_song_pos'] for s in subs])
        _tab('init_master_vol_tab', [s['init_master_vol'] for s in subs])
        if any(s['cia1_timer_a'] for s in subs):
            DEFAULT_CIA = 0x4CC7
            cia_vals = [s['cia1_timer_a'] or DEFAULT_CIA for s in subs]
            _tab('cia1_lo_tab', [v & 0xFF for v in cia_vals])
            _tab('cia1_hi_tab', [(v >> 8) & 0xFF for v in cia_vals])
        # Song table: E0/E3 → V1, E1/E4 → V2, E2/E5 → V3, all pointing at
        # the (single) subtune's per-voice pattern starts. Multi-subtune
        # support for command_stream is left for when a real multi-subtune
        # clever_music engine surfaces.
        L += [
            'song_table:',
            '  .byte <ptn_v1, >ptn_v1     ; E0',
            '  .byte <ptn_v2, >ptn_v2     ; E1',
            '  .byte <ptn_v3, >ptn_v3     ; E2',
            '  .byte <ptn_v1, >ptn_v1     ; E3',
            '  .byte <ptn_v2, >ptn_v2     ; E4',
            '  .byte <ptn_v3, >ptn_v3     ; E5',
            'inst_table:',
        ]
        # 16 × 5 byte instrument palette.
        for inst in sorted(features['cmd_instruments'], key=lambda i: i.id):
            L.append('  .byte ' + ', '.join(
                f'${b:02X}' for b in _inst_timbre_block(inst)))
        return L

    if features['pattern_shape'] == 'pair':
        # Pair-shape uses byte-per-timbre-field per-voice tables (yes_tune
        # init reads `v{V}_tb{J}_tab,y`), the per-voice initial state
        # byte, the gain-init gate, and per-voice pat_start address
        # tables.
        for v_idx in range(3):
            for j in range(5):
                _tab(f'v{v_idx+1}_tb{j}_tab',
                     [s['timbres'][v_idx][j] for s in subs])
        for v_idx in range(3):
            _tab(f'v{v_idx+1}_state_tab',
                 [s['pair_init_states'][v_idx + 1] for s in subs])
        _tab('init_d418_tab', [s['gain_init_full'] for s in subs])
        for v_idx in range(3):
            L.append(f'v{v_idx+1}_ps_lo_tab:')
            L.append('  .byte ' + ', '.join(
                f'<ptn_s{i}_v{v_idx+1}' for i in range(n)))
            L.append(f'v{v_idx+1}_ps_hi_tab:')
            L.append('  .byte ' + ', '.join(
                f'>ptn_s{i}_v{v_idx+1}' for i in range(n)))
        return L

    # Atomic shape: init_pos × 3 + per-voice timbre tables + per-voice
    # orderlist address tables.
    _tab('init_v1_pos_tab', [s['init_pos'][0] for s in subs])
    _tab('init_v2_pos_tab', [s['init_pos'][1] for s in subs])
    _tab('init_v3_pos_tab', [s['init_pos'][2] for s in subs])

    n_voices = features['voice_count']
    fields = ['pwlo', 'pwhi', 'ctrl', 'ad', 'sr']
    for v in range(3 if n_voices == 3 else 1):
        for fi, fname in enumerate(fields):
            _tab(f'v{v+1}_{fname}_tab',
                 [s['timbres'][v][fi] for s in subs])

    if n_voices == 3:
        if any(s['cia1_timer_a'] for s in subs):
            DEFAULT_CIA = 0x4CC7   # libsidplayfp's PAL default
            cia_vals = [s['cia1_timer_a'] or DEFAULT_CIA for s in subs]
            _tab('cia1_lo_tab', [v & 0xFF for v in cia_vals])
            _tab('cia1_hi_tab', [(v >> 8) & 0xFF for v in cia_vals])

        for v in range(3):
            L.append(f'v{v+1}_ol_lo_tab:')
            L.append('  .byte ' + ', '.join(
                f'<orderlist_v{v+1}_s{i}' for i in range(n)))
            L.append(f'v{v+1}_ol_hi_tab:')
            L.append('  .byte ' + ', '.join(
                f'>orderlist_v{v+1}_s{i}' for i in range(n)))
    return L


def _emit_orderlists(features: dict) -> list[str]:
    """Emit per-subtune × per-voice orderlist (atomic) or pattern (pair /
    command_stream) blocks. Companion shape emits its data alongside the
    template+dispatch tables in `_emit_subtune_tables`, so this returns
    empty for that shape."""
    if features['pattern_shape'] == 'companion':
        return []
    L: list[str] = []
    if features['pattern_shape'] == 'command_stream':
        # Single-subtune for now — emit unlabelled-by-subtune `ptn_v{V}`
        # blocks. Multi-subtune for clever_music would emit
        # `ptn_s{S}_v{V}` and per-subtune song-tables.
        sub = features['subtunes'][0]
        for vid in (1, 2, 3):
            L.append(f'ptn_v{vid}:')
            pb = sub['cmd_pattern_bytes'][vid]
            for i in range(0, len(pb), 16):
                L.append('  .byte ' + ', '.join(
                    f'${b:02X}' for b in pb[i:i+16]))
        return L
    if features['pattern_shape'] == 'pair':
        for s_idx, sub in enumerate(features['subtunes']):
            for vid in (1, 2, 3):
                L.append(f'ptn_s{s_idx}_v{vid}:')
                pb = sub['pair_pattern_bytes'][vid]
                for i in range(0, len(pb), 16):
                    L.append('  .byte ' + ', '.join(
                        f'${b:02X}' for b in pb[i:i+16]))
        return L
    n_voices = features['voice_count']
    for s_idx, sub in enumerate(features['subtunes']):
        if n_voices == 1:
            # 1-voice: a single `orderlist_v1` label is the entry point;
            # for multi-subtune, init would copy the per-subtune body
            # there. For now (henrys is 1-subtune), emit one block.
            L.append('orderlist_v1:')
            ob = _orderlist_bytes(sub, 1)
            for i in range(0, len(ob), 16):
                L.append('  .byte ' + ', '.join(
                    f'${b:02X}' for b in ob[i:i+16]))
        else:
            for vid in (1, 2, 3):
                L.append(f'orderlist_v{vid}_s{s_idx}:')
                ob = _orderlist_bytes(sub, vid)
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


def emit_sid(usf: UsfFile, usf_dir: str | None = None) -> bytes:
    """Universal entry. Reads USF, picks emitters, returns PSID bytes.

    `usf_dir` is only consulted when the USF carries digi subtunes
    (whose sample sidecars live alongside the .usf on disk). Music-only
    USFs do not need it.
    """
    features = pick_features(usf)
    shape = features['pattern_shape']

    if shape == 'hubbard85':
        return _emit_hubbard85_bytes(usf, usf_dir)

    vc = features['voice_count']

    asm_lines: list[str] = []
    asm_lines += emit_header()
    if shape == 'companion':
        asm_lines += _emit_companion_init()
        asm_lines += _emit_companion_play()
        asm_lines += _emit_companion_maybe_gate_off()
        asm_lines += _emit_companion_proc_note()
    elif shape == 'command_stream':
        has_cia = any(s['cia1_timer_a'] for s in features['subtunes'])
        asm_lines += _emit_cmd_init(features, has_cia)
        asm_lines += _emit_cmd_play()
        asm_lines += _emit_cmd_load_note()
    elif shape == 'pair':
        asm_lines += _emit_pair_init(features)
        asm_lines += _emit_pair_play(features)
        asm_lines += _emit_pair_voice_tick()
        asm_lines += _emit_pair_play_note()
    elif shape == 'atomic' and vc == 3:
        has_cia = any(s['cia1_timer_a'] for s in features['subtunes'])
        asm_lines += _emit_3voice_init(features, has_cia)
        asm_lines += _emit_3voice_play(features)
        asm_lines += _emit_3voice_proc_note(features)
        asm_lines += _emit_3voice_voice_steps(features)
    else:
        # 1-voice atomic USFs (henrys-shape) now go through
        # `pipelines.composer`. If they reach here, the composer
        # rejected the USF for some other reason — raise rather than
        # silently fall through to the 3-voice path.
        raise NotImplementedError(
            f'universal_codegen: no legacy emitter for shape={shape!r} '
            f'voice_count={vc} (composer should have handled this)')
    asm_lines += _emit_runtime_vars(features)
    asm_lines += _emit_freq_table(features)
    asm_lines += _emit_subtune_tables(features)
    asm_lines += _emit_orderlists(features)
    asm = '\n'.join(asm_lines) + '\n'

    body = _assemble(asm)
    n_subs = len(features['subtunes'])
    return _psid_header(usf, n_subs, LOAD) + body


def applies_to(usf: UsfFile) -> bool:
    """Does this USF fit what the universal codegen currently handles?

    Used by `pipelines.build_from_usf.build_from_usf` to route. Looks at
    USF *content* (instrument modulation programs, orderlist shape, SFX
    subtunes, named mechanism params); never at engine identity (engine
    name, freq_table size, or any other engine fingerprint).
    """
    music = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    if not music:
        return False
    if usf.freq_table is None:
        return False
    if not usf.instruments:
        return False
    if _is_hubbard85_shape(usf, music):
        return True
    if _is_companion_shape(music):
        for ms in music:
            if len(ms.voices) != 3:
                return False
        return True
    if _is_command_stream_shape(music):
        for ms in music:
            if len(ms.voices) != 3:
                return False
        return True
    if _is_pair_shape(music):
        for ms in music:
            if len(ms.voices) != 3:
                return False
        return True
    active = [v for v in music[0].voices if v.patterns]
    return len(active) in (1, 3)


# =============================================================================
# Hubbard '85 shape — parametric core for 11 engines + SFX sub-engine
# =============================================================================
#
# Lifted from the former pipelines/codegen.py. ENGINE is the 6502 player
# template; _emit_data lays out the data section; _hubbard_emit_sid is the
# entry point (renamed from the original _hubbard_emit_sid to keep the universal
# `emit_sid` as the single public entry).
#
# os/struct/subprocess + LOAD already imported/defined at the top of this
# file; `_XA` from the universal section is the xa65 binary path (same
# `ROOT/tools/xa65/xa/xa` the lifted code used to compute as `XA`).
import sys as _sys
from dataclasses import dataclass, field

_sys.path.insert(0, _ROOT)
_sys.path.insert(0, os.path.join(_ROOT, 'src'))
_sys.path.insert(0, os.path.join(_ROOT, 'tools', 'py65_lib'))

from pipelines.hubbard.inst_generalize import decode_all  # noqa: E402

# Local alias so the lifted code reads the same; XA was the legacy name.
XA = _XA


# ---------------------------------------------------------------------------
# build_statebuf — engine state-region mirror for off-table arpeggio
# ---------------------------------------------------------------------------
#
# The drum arpeggio (fx bit 2) computes `arp_pitch = v_pitch + 12`
# every frame the pitch passes through the +12 phase. For arp_pitch
# >= 96 the look-up `freq_table[arp_pitch*2]` reads PAST the 96-entry
# table into engine state. This is Hubbard's "off-table arpeggio" —
# a deliberate trick that produces characteristic percussive freqs
# from live engine state.
#
# Each Hubbard '85 engine has its own state-region layout (Commando
# at $54E8, HR at $0DA4, ...). To reproduce the original write set,
# the rebuild's `statebuf` must mirror the same byte at each off-
# table offset. `StatebufLayout` captures the layout as data; one
# shared emitter generates the `build_statebuf` asm.
#
# Reading the layout: each engine's `statebuf+N` should hold whatever
# byte the original engine has at "state-region offset N" when the
# off-table read happens. Slots fall into two camps:
#
#   - `scalars`: written once at the top of build_statebuf (constants
#     or scalar zp vars like `sidoff`).
#   - `per_voice`: written inside a `ldx #n-1; ...; dex; bpl` loop;
#     the slot's `offset` is the base, with offset+X storing the X-th
#     voice's value.

@dataclass
class StatebufSlot:
    offset: int
    kind: str            # 'var' | 'var_and' | 'note_byte' | 'const' | 'zp'
    var: str = ''        # zp name for 'var' / 'var_and'
    mask: int = 0xFF     # AND mask for 'var_and'
    value: int = 0       # byte value for 'const'


@dataclass
class StatebufLayout:
    n_voices: int = 3
    scalars: list = field(default_factory=list)     # list[StatebufSlot]
    per_voice: list = field(default_factory=list)   # list[StatebufSlot]


# Commando's layout — the historic hand-written `build_statebuf` body.
# Action Biker, Devils Galop, Monty and Chimera all share this layout
# (they're the same engine family with the same state-region offsets).
COMMANDO_STATEBUF_LAYOUT = StatebufLayout(
    n_voices=3,
    scalars=[
        StatebufSlot(offset=3, kind='zp', var='sidoff'),
    ],
    per_voice=[
        StatebufSlot(offset=4,  kind='var',     var='v_seqidx'),
        StatebufSlot(offset=7,  kind='var',     var='v_hubidx'),
        StatebufSlot(offset=10, kind='var',     var='v_dur'),
        StatebufSlot(offset=13, kind='note_byte'),
        StatebufSlot(offset=16, kind='var',     var='v_ctrlbyte'),
        StatebufSlot(offset=19, kind='var',     var='v_pitch'),
        StatebufSlot(offset=22, kind='var_and', var='v_instr', mask=0x3f),
        StatebufSlot(offset=40, kind='var',     var='v_pwdir'),
    ],
)


def _emit_build_statebuf(layout: StatebufLayout) -> str:
    """Emit the `build_statebuf:` routine from a StatebufLayout.

    Saves X (the caller's voice index), runs the scalars once, then
    the per-voice loop with X = n_voices-1 down to 0, then restores X.
    """
    lines = ['build_statebuf:', '        txa', '        pha']
    for s in layout.scalars:
        if s.kind == 'const':
            lines.append(f'        lda #${s.value:02X}')
        elif s.kind == 'zp':
            lines.append(f'        lda {s.var}')
        else:
            raise ValueError(f'scalar slot kind {s.kind!r} not supported')
        lines.append(f'        sta statebuf+{s.offset}')

    if layout.per_voice:
        lines.append(f'        ldx #{layout.n_voices - 1}')
        lines.append('bsb1:')
        for s in layout.per_voice:
            if s.kind == 'var':
                lines.append(f'        lda {s.var},x')
                lines.append(f'        sta statebuf+{s.offset},x')
            elif s.kind == 'var_and':
                lines.append(f'        lda {s.var},x')
                lines.append(f'        and #${s.mask:02X}')
                lines.append(f'        sta statebuf+{s.offset},x')
            elif s.kind == 'note_byte':
                lines.append(f'        lda v_instr,x')
                lines.append(f'        and #$40')
                lines.append(f'        ora v_durfield,x')
                lines.append(f'        sta statebuf+{s.offset},x')
            else:
                raise ValueError(f'per-voice slot kind {s.kind!r} not supported')
        lines.append('        dex')
        lines.append('        bpl bsb1')

    lines += ['        pla', '        tax', '        rts']
    return '\n'.join(lines)


def _statebuf_init_bytes(layout: StatebufLayout) -> str:
    """The `statebuf:` data block — 96 bytes, with the per-voice
    sidoff constants seeded where Commando expects them ($00, $07,
    $0E for V1, V2, V3) and zeros for everything else. For engines
    with different scalar constants, those are reflected here."""
    bytes_ = [0] * 96
    # The classic seed: 0, 7, 14 for V1, V2, V3. Engines override via
    # `scalars` entries with kind='const' (e.g. HR puts sidoff
    # constants at offsets 0 and 1 explicitly).
    bytes_[0] = 0
    bytes_[1] = 7
    if layout.n_voices >= 3:
        bytes_[2] = 14
    # Apply any const scalars from the layout.
    for s in layout.scalars:
        if s.kind == 'const' and s.offset < len(bytes_):
            bytes_[s.offset] = s.value
    return ','.join(str(b) for b in bytes_)

# ---------------------------------------------------------------------------
# 6502 engine. A faithful implementation of song_interp.py's frame loop.
# Data labels (sidtab, insttab, pwacc, freqtab, patterns + pataddr,
# per-voice orderlists, statebuf) are appended by the codegen.
#
# instrument table row (16 bytes): init_ctrl, init_pw_lo, init_pw_hi,
# init_ad, init_sr, hr_ctrl, fx_flags, then 9 effect-param bytes.
# fx_flags bit0 = freqSlide (skydive).
# ---------------------------------------------------------------------------

ENGINE = r"""
frame_ctr = $40
speed_ctr = $41
is_tick   = $42
sidoff    = $43
v_dur     = $44
v_instr   = $47
v_pitch   = $4a
v_patlo   = $4d
v_pathi   = $50
v_orderpos = $53
orderp    = $56
notep     = $59
i_ctrl    = $5b
i_pwlo    = $5c
i_pwhi    = $5d
i_ad      = $5e
i_sr      = $5f
f_lo      = $60
f_hi      = $61
instoff   = $62
v_slide   = $63
v_tick    = $66
v_durfield = $69
vib_step  = $6c
vdelta_lo = $6d
vdelta_hi = $6e
vtarg_lo  = $6f
vtarg_hi  = $70
vdepthctr = $71
vib_carry = $72
pw_idx    = $73
v_pwdir   = $74
v_pwperiod = $77
pwm_tmp   = $7a
v_hubidx  = $7c
v_norel   = $7f
v_ctrlbyte = $82
v_drumtrig = $85
v_slidelo  = $88
v_seqidx   = $8b
vfreq      = $8e
v_ended    = $92
end_phase  = $95
cur_resetspd = $96
sub_tmp    = $97
is_sfx     = $98
sfx_idx    = $99
sfx_rec    = $9a
sfx_index  = $9c
sfx_stepctr = $9d
sfx_v1gate = $9e
sfx_v2gate = $9f
sfx_done   = $a0
sfx_started = $a1
sfx_y      = $a2
sfx_flags  = $a3
sfx_tmp    = $a4
v_notesleft = $a5
drum_prio   = $b2
pv_abort    = $b3
v_frozen    = $b4
voice_start = $b7
first_frame = $b8
; Master-volume fade counter — incremented on the configured voice's
; pattern-end (never wraps on song-loop). Read by the bit-7-style
; master VOL write on instrument-change notes:
;   $D418 = clamp(MASTER_VOL_BASE - vol_progress, 0..$0F)
; Only emitted when MASTER_VOL_FADE = 1.
vol_progress = $b9
; Per-subtune engine-param zp slots (used only when the codegen emits
; the per-subtune-params variant — see PER_SUBTUNE_ENGINE_PARAMS).
; `cur_incby2_step` is the slide step added per frame (8-bit signed:
; +2 = $02, -1 = $FF, etc.). `cur_incby2_late_gate` is the v_dur
; threshold below which the fx-bit-1 slide fires; $FF = "no gate".
cur_incby2_step  = $b9
cur_incby2_late_gate = $ba

* = $1000
        jmp init
        jmp play

; init - A = subtune number. A under N_MUSIC is a music subtune; A
; N_MUSIC and up is a sound effect (A-N_MUSIC = the SFX index).
init:
        cmp #N_MUSIC
        bcc init_music
        sec
        sbc #N_MUSIC
        sta sfx_idx
        lda #$01
        sta is_sfx
        jmp init_sfx
init_music:
        sta sub_tmp          ; A = subtune
        lda #$00
        sta is_sfx
        lda #DRUM_PRIO_INIT  ; $178B drum-priority gate
        sta drum_prio
        lda sub_tmp
        asl                  ; subtune*2
        clc
        adc sub_tmp          ; subtune*3 = base index into the 9-entry
        tay                  ; per-subtune orderlist tables
        ldx #0
inisel: lda subOrderLo,y
        sta orderLo,x
        lda subOrderHi,y
        sta orderHi,x
        lda subOrderLoop,y
        sta orderLoop,x
        iny
        inx
        cpx #3
        bne inisel
        ldy sub_tmp          ; this subtune's tempo
        lda subResetspd,y
        sta cur_resetspd
        lda subVoiceStart,y  ; per-subtune voice-loop start
        sta voice_start
        ldx #PWLEN           ; re-seed the PWM accumulators from pwseed
inipw:  lda pwseed,x
        sta pwacc,x
        dex
        bpl inipw
        ldx #2
ini1:   lda #0
        sta v_dur,x
        sta v_pwdir,x
        sta v_pwperiod,x
        sta v_instr,x
        sta v_orderpos,x
        sta v_ended,x
        sta v_frozen,x
        jsr set_patptr       ; v_patptr,x = first pattern of orderlist X
        dex
        bpl ini1
        ; %%OVSEED_COPY%%    ; runtime copy of subOvseed_<sub> -> ovseed
        ldx #2               ; seed the freq-table-overlap variables
iniov:  lda ovseed,x
        sta v_ctrlbyte,x
        lda ovseed+3,x
        sta v_pwperiod,x
        lda ovseed+6,x
        sta v_pwdir,x
        lda ovseed+9,x
        sta v_instr,x
        lda ovseed+12,x
        sta v_durfield,x
        lda ovseed+15,x
        sta v_slide,x
        dex
        bpl iniov
        lda #0
        sta end_phase
        ; %%VOL_PROGRESS_INIT%%   ; engines with MASTER_VOL_FADE reset
                                  ; the vol_progress counter here; for
                                  ; other engines this expands to nothing
                                  ; so the binary doesn't grow (address-
                                  ; shifting changes broke Monty st 0 +
                                  ; SFX subtunes when this was emitted
                                  ; unconditionally).
        lda #SPEED_CTR_INIT
        sta speed_ctr
        lda #1
        sta first_frame
        lda #FRAME_CTR_INIT
        sta frame_ctr
        ldx #$18
ini2:   lda #0
        sta $d400,x
        dex
        bpl ini2
        lda #MASTER_VOL_INIT  ; $D418 init value — most engines write $0F
                              ; here, but engines with MASTER_VOL_FADE
                              ; leave it at $00 because the original
                              ; engine doesn't write $D418 until the
                              ; first instrument-change note.
        sta $d418
        rts

play:
        inc freqtab+253      ; mirror Hubbard's INC $5525 (the SFX
                             ; sweep can read this byte as a frequency)
        lda is_sfx
        beq pl_music
        jmp sfx_play
pl_music:
        lda end_phase
        beq pl_run
        cmp #$01
        bne pl_silent        ; end_phase 2 - song over, write nothing
        lda #$02             ; end_phase 1 - gate every voice off, once
        sta end_phase
        lda #$00
        sta $d404            ; V1 ctrl
        sta $d40b            ; V2 ctrl
        sta $d412            ; V3 ctrl
pl_silent:
        rts
pl_run:
        inc frame_ctr
        lda first_frame
        beq pl_nogate
        lda #0
        sta first_frame
        lda #FIRST_FRAME_GATE_OFF
        beq pl_nogate
        lda #0
        sta $d404
        sta $d40b
        sta $d412
pl_nogate:
        dec speed_ctr
        bpl notick
        lda cur_resetspd
        sta speed_ctr
        lda #1
        sta is_tick
        jmp voices
notick: lda #0
        sta is_tick
voices:
        lda #0
        sta pv_abort
        ldx voice_start
pvloop: jsr proc_voice
        lda pv_abort
        bne pl_done
        lda #$ff
        sta drum_prio
        dex
        bpl pvloop
        ; end-of-song - once all three voices have hit $FE, arm the
        ; one-shot gate-off for the next frame.
        lda v_ended+0
        and v_ended+1
        and v_ended+2
        beq pl_done
        lda end_phase
        bne pl_done
        lda #$01
        sta end_phase
pl_done:
        rts

proc_voice:
        lda v_ended,x
        bne pv_endret        ; voice hit $FE - it no longer plays
        lda v_frozen,x
        bne pv_frozen        ; voice hit $FE under freeze_on_stop
        lda sidtab,x
        sta sidoff
        jsr calc_instoff
        lda is_tick
        beq pv_fx
        dec v_dur,x
        bpl pv_sus
        jsr load_note
        lda v_ended,x        ; load_note may have hit the $FE marker
        bne pv_endret
        lda v_frozen,x       ; load_note may have hit the $FE freeze
        bne pvf_abort
        jsr calc_instoff
        jmp note_start
pv_sus:
        inc v_tick,x
        lda v_dur,x
        bne pv_fx
        lda v_norel,x
        bne pv_fx            ; no_release - skip the hard restart
        jsr hr_writes
pv_fx:
        jmp do_effects
; a $FE-frozen voice. v_dur cycles as a signed byte; while it is
; negative the voice tries to advance, hits $FE and aborts the frame.
; otherwise it sustains, hard-restarts at zero-crossing and runs fx.
pv_frozen:
        lda sidtab,x
        sta sidoff
        jsr calc_instoff
        lda is_tick
        beq pvf_fx
        dec v_dur,x
        lda v_dur,x
        bmi pvf_abort
        inc v_tick,x
        lda v_dur,x
        bne pvf_fx
        lda v_norel,x
        bne pvf_fx
        jsr hr_writes
pvf_fx:
        jmp do_effects
pvf_abort:
        lda #1
        sta pv_abort
        rts
pv_endret:
        rts

calc_instoff:
        lda v_instr,x
        and #$3f
        sta instoff          ; instrument number (column-table index)
        asl
        sta pw_idx           ; inst*2  (index into pwacc)
        rts

; load_note is supplied by the note codec (see note_codec.py) — the
; engine calls it; the codec owns the pattern byte format and its
; decoder. set_patptr / next_orderidx below are codec-agnostic.

; set_patptr - point v_patptr,x at the pattern named by orderlist
; entry v_orderpos,x. The $FF terminator wraps v_orderpos to
; orderLoop,x; the $FE terminator ends the voice (v_ended). Clobbers
; A and Y; preserves X.
set_patptr:
        lda orderLo,x
        sta orderp
        lda orderHi,x
        sta orderp+1
sp_read:
        ldy v_orderpos,x
        lda (orderp),y
        cmp #$fe
        bcc sp_have          ; below $FE - a real pattern index
        beq sp_stop          ; $FE - end of song
        lda orderLoop,x      ; $FF - wrap to the loop point
        sta v_orderpos,x
        jmp sp_read
sp_stop:
        lda #$ff
        ldy #FREEZE_ON_STOP
        bne sps_freeze
        ldy #STOP_IS_FILL
        bne sps_fill
        sta v_ended,x
        rts
sps_freeze:
        sta v_frozen,x
        rts
; sps_fill - the $FE stop_fill end. Writes STOP_FILL to every voice
; register PLUS filter cutoff lo/hi + res-routing ($D400-$D417, 24
; regs), matching Action Biker's $C2E1-$C2E7 `LDX #$17; STA $D400,X`
; loop. $D418 (master VOL) is left alone — the engine's loop stops
; at $D417. `LDX #imm` is 2 bytes regardless of value, so this change
; doesn't shift any other addresses.
sps_fill:
        stx sub_tmp
        ldx #23
        lda #STOP_FILL
sps_fl: sta $d400,x
        dex
        bpl sps_fl
        lda #$02
        sta end_phase
        lda #1
        sta pv_abort
        ldx sub_tmp
        lda #$ff
        sta v_ended,x
        rts
sp_have:
        tay                  ; Y = pattern index
        lda pataddr_lo,y
        sta v_patlo,x
        lda pataddr_hi,y
        sta v_pathi,x
        ; every pattern starts with a 1-byte note count - read it and
        ; step v_patptr past it, then reset the per-voice read cursor.
        lda v_patlo,x
        sta notep
        lda v_pathi,x
        sta notep+1
        ldy #0
        lda (notep),y
        sta v_notesleft,x
        inc v_patlo,x
        bne sp_nc
        inc v_pathi,x
sp_nc:
        lda #0
        sta v_bitcnt,x       ; codec cursor state
        sta v_hubidx,x       ; note_idx restarts at 0 in a new pattern
        rts

; next_orderidx - the orderlist index the next pattern will occupy:
; v_orderpos+1, or orderLoop,x if that entry is the $FF terminator.
; Returns it in A. Preserves X.
next_orderidx:
        lda orderLo,x
        sta orderp
        lda orderHi,x
        sta orderp+1
        lda v_orderpos,x
        clc
        adc #1
        tay                  ; Y = v_orderpos + 1
        lda (orderp),y
        cmp #$fe
        bcc noi_have
        lda orderLoop,x      ; next entry is a terminator ($FE/$FF) - wrap
        rts
noi_have:
        tya
        rts

; note_start - write the note-start register block for voice X.
; common fields (ctrl/ad/sr from insttab, pw from the accumulator) are
; loaded into temps first; then tie vs full diverge.
note_start:
        ldy instoff
        lda it_ctrl,y
        sta i_ctrl
        lda it_ad,y
        sta i_ad
        lda it_sr,y
        sta i_sr
        ldy pw_idx
        lda pwacc,y
        sta i_pwlo
        lda pwacc+1,y
        sta i_pwhi
        lda v_instr,x
        and #$40
        beq ns_full
        ; tie - ctrl gated off, pw, ad, sr; no freq, no slide re-seed.
        lda i_ctrl
        sta v_ctrlbyte,x
        and #$fe
        bit drum_prio
        bpl ns_pwadsr        ; suppressed -> skip the write
        ldy sidoff
        sta $d404,y
        jmp ns_pwadsr
ns_full:
        ; freq - pitch >= 96 reads off-table into the engine state
        ; region. The shared `statebuf` mirrors the per-engine layout
        ; (see StatebufLayout); off-table notes read it the same way
        ; fx_arp does for the +12 / +24 octave cases.
        lda v_pitch,x
        cmp #96
        bcs ns_offtab
        asl
        tay
        lda freqtab,y
        sta f_lo
        lda freqtab+1,y
        sta f_hi
        jmp ns_havefreq
ns_offtab:
        sec
        sbc #96
        cmp #48
        bcs ns_offzero       ; pitch beyond the 48-byte mirrored state
        asl                  ; (pitch-96)*2 = statebuf offset
        tay
        jsr build_statebuf
        ; %%NS_OFFTAB_DECR%%
        lda statebuf+0,y
        sta f_lo
        lda statebuf+1,y
        sta f_hi
        jmp ns_havefreq
ns_offzero:
        lda #0
        sta f_lo
        sta f_hi
ns_havefreq:
        lda f_hi
        sta v_slide,x        ; seed the skydive/drum-slide freq_hi
        lda f_lo
        sta v_slidelo,x      ; seed the drum-slide freq_lo
        lda i_ctrl
        sta v_ctrlbyte,x     ; update ctrl_byte AFTER the off-table read
        bit drum_prio
        bpl ns_pwadsr        ; suppressed -> skip the writes
        ldy sidoff
        lda f_hi
        sta $d401,y
        lda f_lo
        sta $d400,y
        lda i_ctrl
        sta $d404,y
ns_pwadsr:
        bit drum_prio
        bpl ns_pwret         ; suppressed -> skip the writes
        ldy sidoff
        lda i_pwlo
        sta $d402,y
        lda i_pwhi
        sta $d403,y
        lda i_ad
        sta $d405,y
        lda i_sr
        sta $d406,y
ns_pwret:
        rts

; hr_writes - hard-restart block, ctrl=hr_ctrl ad=0 sr=0.
hr_writes:
        ldy instoff
        lda it_hrctrl,y
        ldy sidoff
        sta $d404,y
        lda #0
        sta $d405,y
        sta $d406,y
        rts

; do_effects - effects in engine order vibrato,pwm,drumslide,skydive,arp.
do_effects:
        lda #0
        sta vib_carry
        jsr fx_vibrato
        jsr fx_pwm
        jsr fx_drumslide
        jsr fx_skydive
        jsr fx_incby2
        jmp fx_arp

; fx_drumslide - per-note portamento ($52B3-$52F9), effect #3. A note
; carrying a drum/porta trigger slides the running freq (v_slidelo /
; v_slide = $551D/$551A) by delta=trig&$7E each frame, dir=trig&$01.
; bit7 of the trigger is no_release - mask it off before the run test.
fx_drumslide:
        lda v_drumtrig,x
        and #$7f
        beq fxd_ret
        and #$7e             ; delta
        sta pwm_tmp
        lda v_drumtrig,x
        and #$01
        bne fxd_down
        lda v_slidelo,x      ; slide up
        clc
        adc pwm_tmp
        sta v_slidelo,x
        lda v_slide,x
        adc #$00
        sta v_slide,x
        jmp fxd_wr
fxd_down:
        lda v_slidelo,x      ; slide down
        sec
        sbc pwm_tmp
        sta v_slidelo,x
        lda v_slide,x
        sbc #$00
        sta v_slide,x
fxd_wr:
        ldy sidoff
        lda v_slidelo,x
        sta $d400,y          ; freq_lo
        lda v_slide,x
        sta $d401,y          ; freq_hi
fxd_ret: rts

; fx_incby2 - bit1. odd-frame slide on v_slide, write OLD value then
; step. The optional %%INCBY2_LATE_GATE%% sentinel below is replaced
; at codegen time with a `v_dur >= N -> skip` check for engines like
; Hunter Patrol whose skydive only fires in the tail of long notes.
fx_incby2:
        ldy instoff
        lda it_fx,y
        and #$02
        beq fxi_ret
        lda v_durfield,x
        cmp #INCBY2_ONSET
        bcc fxi_ret
; %%INCBY2_LATE_GATE%%
        lda frame_ctr
        and #$01
        ora #INCBY2_ALWAYS   ; 1 -> runs every frame
        beq fxi_ret
        lda v_slide,x
        beq fxi_ret
        ldy sidoff
        lda v_slide,x
        sta $d401,y          ; write OLD slide value
        lda v_slide,x
        clc
        adc #INCBY2_STEP
        sta v_slide,x
fxi_ret: rts

; fx_pwm - bit4. linear or bidirectional PWM. The pw accumulators
; (pwacc) are per-instrument shared state - see song_interp._pwm.
fx_pwm:
        ldy instoff
        lda it_pwmode,y      ; pwm_mode  0=none 1=linear 2=bidir
        bne fxp_on
        rts
fxp_on:
        cmp #$01
        bne fxp_bidir
        ldy instoff
        lda it_pwa,y      ; linear - pw_lo += speed + vib_carry
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        clc
        adc pwm_tmp
        clc
        adc vib_carry
        ora #LINEAR_PW_OR
        sta pwacc,y
        ldy sidoff
        sta $d402,y
        rts
fxp_bidir:
        dec v_pwperiod,x
        bpl fxp_ret          ; period counter not expired
        ldy instoff
        lda it_pwperiod,y     ; reload period
        sta v_pwperiod,x
        lda v_pwdir,x
        bne fxp_fall
        ldy instoff          ; rising
        lda it_pwa,y      ; step
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        clc
        adc pwm_tmp
        sta pwacc,y
        lda pwacc+1,y
        adc #$00
        and #$0f
        sta pwacc+1,y
        ldy instoff
        cmp it_pwhi,y     ; hi_bound
        bne fxp_wr
        lda #$01
        sta v_pwdir,x
        jmp fxp_wr
fxp_fall:
        ldy instoff
        lda it_pwa,y      ; step
        sta pwm_tmp
        ldy pw_idx
        lda pwacc,y
        sec
        sbc pwm_tmp
        sta pwacc,y
        lda pwacc+1,y
        sbc #$00
        and #$0f
        sta pwacc+1,y
        ldy instoff
        cmp it_pwlo,y     ; lo_bound
        bne fxp_wr
        lda #$00
        sta v_pwdir,x
fxp_wr:
        ldy pw_idx
        lda pwacc+1,y
        sta pwm_tmp
        lda pwacc,y
        sta pwm_tmp+1
        ldy sidoff
        lda pwm_tmp
        sta $d403,y          ; pw_hi
        lda pwm_tmp+1
        sta $d402,y          ; pw_lo
fxp_ret:
        rts

; fx_vibrato - bit3. triangle LFO on freq, disassembly $51C1-$522D.
; leaves vib_carry = the 6502 carry the section hands to the PWM add.
fx_vibrato:
        ldy instoff
        lda it_fx,y
        and #$08
        bne fxv_go
        rts
fxv_go:
        lda frame_ctr
        and #$07
        cmp #$04
        bcc fxv_s1
        eor #$07
fxv_s1: sta vib_step
        ldy instoff
        lda it_vibdepth,y      ; vib_depth
        sta vdepthctr
        jsr vib_loadfreq     ; vfreq = freq16[pitch], freq16[pitch+1]
        sec
        lda vfreq+2          ; freq16[pitch+1] - freq16[pitch]
        sbc vfreq+0
        sta vdelta_lo
        lda vfreq+3
        sbc vfreq+1          ; A = diff_hi
fxv_sh: lsr                  ; shift A,vdelta_lo right depth+1 times
        ror vdelta_lo
        dec vdepthctr
        bpl fxv_sh
        sta vdelta_hi
        lda vfreq+0          ; target = freq16[pitch]
        sta vtarg_lo
        lda vfreq+1
        sta vtarg_hi
        lda v_durfield,x
        ldy instoff
        cmp it_onset,y     ; onset_dur (per-instrument)
        bcc fxv_wr           ; dur < onset -> no add (carry left = 0)
        ldy vib_step
        beq fxv_wr           ; step 0 -> no add (carry left = 1)
fxv_add:
        clc
        lda vtarg_lo
        adc vdelta_lo
        sta vtarg_lo
        lda vtarg_hi
        adc vdelta_hi
        sta vtarg_hi
        dey
        bne fxv_add
fxv_wr:
        lda #0               ; capture carry-out for the PWM ADC
        adc #0
        sta vib_carry
        ldy sidoff
        lda vtarg_lo
        sta $d400,y
        lda vtarg_hi
        sta $d401,y
        rts

; vib_loadfreq - fill vfreq (4 bytes) with freq16[pitch] and
; freq16[pitch+1]. In-table pitches read the freq table; an off-table
; pitch (96 and up) reads the engine-state mirror - the original's
; vibrato overflows the 96-entry freq table the same way.
vib_loadfreq:
        lda v_pitch,x
        cmp #96
        bcs vlf_off
        asl
        tay
        lda freqtab+0,y
        sta vfreq+0
        lda freqtab+1,y
        sta vfreq+1
        lda freqtab+2,y
        sta vfreq+2
        lda freqtab+3,y
        sta vfreq+3
        rts
vlf_off:
        sec
        sbc #96
        asl                  ; (pitch-96)*2 = statebuf offset
        tay
        jsr build_statebuf
        lda statebuf+0,y
        sta vfreq+0
        lda statebuf+1,y
        sta vfreq+1
        lda statebuf+2,y
        sta vfreq+2
        lda statebuf+3,y
        sta vfreq+3
        rts

; fx_skydive - bit0. freq_hi slide + ctrl, see song_interp._skydive.
fx_skydive:
        ldy instoff
        lda it_fx,y
        and #$01
        beq fxs_ret
        lda v_dur,x
        beq fxs_ret          ; duration_ctr == 0
        lda v_slide,x
        beq fxs_ret          ; slide value dead
        ldy sidoff
        lda v_slide,x
        sta $d401,y          ; freq_hi = slide value
        lda v_tick,x
        beq fxs_ns
        ldy instoff
        lda it_hrctrl,y      ; not-start ctrl = hr_ctrl
        bne fxs_w
        lda #$80
fxs_w:  ldy sidoff
        sta $d404,y
        dec v_slide,x
        rts
fxs_ns: lda #$80             ; note-start subphase ctrl = $80
        ldy sidoff
        sta $d404,y
fxs_ret: rts

; fx_arp - bit2 arpeggio. alternate pitch / pitch+12 by frame parity.
; idx under 96 is a normal freq-table lookup. idx 96 and up is
; off-table - in the original the lookup overflows the 96-entry freq
; table into engine state; reproduced cleanly here via statebuf, a
; mirror of the $54E8.. state region assembled on demand.
fx_arp:
        ldy instoff
        lda it_fx,y
        and #$04
        beq fxa_ret
        lda frame_ctr
        and #ARP_MASK
        beq fxa_even
        lda v_pitch,x
        clc
        adc #ARP_OFS
        jmp fxa_idx
fxa_even:
        lda v_pitch,x
fxa_idx:
        cmp #96
        bcc fxa_in
        sec
        sbc #96
        cmp #48
        bcs fxa_ret          ; beyond the mirrored state - reads zero
        asl                  ; (idx-96)*2 = statebuf offset
        tay
        jsr build_statebuf
        lda statebuf+0,y     ; addr   -> freq_lo
        pha
        lda statebuf+1,y     ; addr+1 -> freq_hi
        ldy sidoff
        sta $d401,y          ; freq_hi written first
        pla
        sta $d400,y          ; then freq_lo
        rts
fxa_in:
        asl
        tay
        lda freqtab,y
        sta f_lo
        lda freqtab+1,y
        sta f_hi
        ldy sidoff
        lda f_hi
        sta $d401,y
        lda f_lo
        sta $d400,y
fxa_ret: rts

; build_statebuf - assemble the off-table-arpeggio state mirror.
; Generated per-engine from StatebufLayout (see codegen.py); the
; concrete body is substituted in at codegen time.
; %%BUILD_STATEBUF%%

; ============================ sound effects ===========================
; A SFX is a 2-voice register snapshot plus a freq-table pitch sweep,
; driven by a 32-byte record (sfxdata). See pipelines/hubbard/commando/extract/
; sfx.py for the engine derivation.

; init_sfx - set up sound effect sfx_idx. Builds the record pointer,
; patches the live freq-table bytes the sweep overflows into, and
; resets the sweep state.
init_sfx:
        lda #$00
        sta sfx_rec+1
        lda sfx_idx
        asl
        rol sfx_rec+1
        asl
        rol sfx_rec+1
        asl
        rol sfx_rec+1
        asl
        rol sfx_rec+1
        asl
        rol sfx_rec+1        ; sfx_idx*32 - A is the low byte
        clc
        adc #<sfxdata
        sta sfx_rec
        lda sfx_rec+1
        adc #>sfxdata
        sta sfx_rec+1
        lda #$80
        sta freqtab+241      ; the sweep reads $5519 here - mode byte $80
        lda sfx_idx
        sta freqtab+255      ; $5527 - the SFX index
        lda #$ff
        sta freqtab+256      ; $5528 - drum_enable
        ldy #14
        lda (sfx_rec),y      ; record 14 - sweep start index
        sta sfx_index
        lda #$00
        sta sfx_stepctr
        sta sfx_done
        sta sfx_started
        ldy #4
        lda (sfx_rec),y      ; record 4 - V1 ctrl, the live V1 gate
        sta sfx_v1gate
        ldy #11
        lda (sfx_rec),y      ; record 11 - V2 ctrl, the live V2 gate
        sta sfx_v2gate
        ldx #$18
isfxclr: lda #$00
        sta $d400,x
        dex
        bpl isfxclr
        lda #$0f
        sta $d418
        rts

; sfx_play - one frame of the sound-effect engine. The first frame
; gates the voices off and writes the 14-byte register snapshot;
; thereafter it steps the freq-table sweep.
sfx_play:
        lda sfx_started
        bne sfxp_run
        lda #$01
        sta sfx_started
        lda #$00
        sta $d404            ; play-path clear - gate V1,V2,V3 off
        sta $d40b
        sta $d412
        sta $d404            ; the trigger gates V1,V2 again
        sta $d40b
        ldy #$00
sfxp_cpy: lda (sfx_rec),y    ; records 0..13 - V1+V2 register snapshot
        sta $d400,y
        iny
        cpy #$0e
        bne sfxp_cpy
sfxp_run:
        lda sfx_done
        bne sfxp_ret
        dec sfx_stepctr
        bpl sfxp_ret
        ldy #16
        lda (sfx_rec),y      ; record 16 - step rate
        sta sfx_stepctr
        jsr sfx_step
sfxp_ret:
        rts

; sfx_step - one sweep step. Writes V1/V2 freq from the freq table and
; advances the index; ends the SFX when the index reaches the end.
sfx_step:
        ldy #15
        lda (sfx_rec),y      ; record 15 - end index
        cmp sfx_index
        bne sfxs_go
        lda #$00             ; reached the end - gate off, done
        sta $d404
        sta $d40b
        lda #$01
        sta sfx_done
        rts
sfxs_go:
        lda sfx_index
        asl
        sta sfx_y            ; sfx_y = (index*2) & $FF
        ldy #17
        lda (sfx_rec),y      ; record 17 - flags
        sta sfx_flags
        and #$04
        bne sfxs_gates       ; bit2 - skip both freq writes
        lda sfx_flags
        and #$02
        bne sfxs_v2          ; bit1 - skip the V1 freq write
        ldy sfx_y
        lda freqtab,y
        sta $d400
        lda freqtab+1,y
        sta $d401
sfxs_v2:
        ldy #18
        lda (sfx_rec),y      ; record 18 - V2 byte offset
        sta sfx_tmp
        lda sfx_y
        sec
        sbc sfx_tmp
        tay                  ; Y = (sfx_y - v2offset) & $FF
        lda freqtab,y
        sta $d407
        lda freqtab+1,y
        sta $d408
sfxs_gates:
        ldy #19
        lda (sfx_rec),y      ; record 19 - gate-toggle flags
        sta sfx_tmp
        and #$80
        beq sfxs_g2          ; bit7 - retrigger the V1 gate
        lda sfx_v1gate
        eor #$01
        sta sfx_v1gate
        sta $d404
sfxs_g2:
        lda sfx_tmp
        and #$40
        beq sfxs_adv         ; bit6 - retrigger the V2 gate
        lda sfx_v2gate
        eor #$01
        sta sfx_v2gate
        sta $d40b
sfxs_adv:
        lda sfx_flags
        and #$01
        beq sfxs_down        ; bit0 - 1 sweeps up, 0 sweeps down
        inc sfx_index
        rts
sfxs_down:
        dec sfx_index
        rts

sidtab: .byt 0, 7, 14
"""


# ---------------------------------------------------------------------------
# data serialisation
# ---------------------------------------------------------------------------

def _fx_flags(m) -> int:
    return ((1 if m.freq_slide else 0) | (2 if m.inc_by2 else 0)
            | (4 if m.arpeggio else 0) | (8 if m.vibrato else 0)
            | (16 if m.pwm else 0))


def _pattern_pool(scores):
    """Dense, globally-shared pattern pool. Returns (pat_order, pat_slot):
    pat_order[slot] = note list; pat_slot[orig pattern index] = slot."""
    pat_order, pat_slot = [], {}
    for score in scores:
        for v in score.voices:
            for oidx in v.orderlist:
                if oidx not in pat_slot:
                    pat_slot[oidx] = len(pat_order)
                    pat_order.append(v.patterns.get(oidx, []))
    return pat_order, pat_slot


def _emit_data(scores, models, freq_bytes, resetspds, voice_starts,
               sfx_list, pat_slot, pat_bytes, codec_extra,
               seed_overlap: bool = True,
               state_layout: StatebufLayout = COMMANDO_STATEBUF_LAYOUT,
               seed_offsets: _Optional[dict] = None,
               per_subtune_speed_ctr_init: _Optional[list] = None,
               per_subtune_incby2_step: _Optional[list] = None,
               per_subtune_incby2_late_gate: _Optional[list] = None,
               per_subtune_ovseed: _Optional[list] = None) -> str:
    """Emit the xa65 data section for a multi-subtune build.

    `scores` is one Score per packed music subtune; `sfx_list` is the
    16 sound effects; `codec` is the note packer. Instruments, the freq
    table and the pattern pool are shared; orderlists, loop points and
    tempo are per-subtune, selected by `init` from the subOrder* /
    subResetspd tables."""
    lines = []

    # instrument data — column-major: one table per field, indexed by
    # the instrument NUMBER. Row-major (inst*16) overflowed the 8-bit
    # index past 15 instruments (Monty has 20).
    irows = []
    for m in models:
        vib_depth = m.vibrato.depth if m.vibrato else 0
        vib_onset = m.vibrato.onset_dur if m.vibrato else 6
        pwm_mode = pwm_a = pwm_period = pwm_lo = pwm_hi = 0
        if m.pwm:
            if m.pwm.mode == 'linear':
                pwm_mode, pwm_a = 1, m.pwm.speed
            else:
                pwm_mode, pwm_a = 2, m.pwm.step
                pwm_period, pwm_lo, pwm_hi = (m.pwm.period, m.pwm.lo_bound,
                                              m.pwm.hi_bound)
        irows.append([m.init_ctrl, 0, 0, m.init_ad, m.init_sr, m.hr_ctrl,
                      _fx_flags(m), vib_depth, pwm_mode, pwm_a,
                      pwm_period, pwm_lo, pwm_hi, vib_onset])
    for idx, name in ((0, 'it_ctrl'), (3, 'it_ad'), (4, 'it_sr'),
                      (5, 'it_hrctrl'), (6, 'it_fx'), (7, 'it_vibdepth'),
                      (8, 'it_pwmode'), (9, 'it_pwa'), (10, 'it_pwperiod'),
                      (11, 'it_pwlo'), (12, 'it_pwhi'), (13, 'it_onset')):
        lines.append(f'{name}: .byt '
                     + ','.join(f'${r[idx]:02X}' for r in irows))

    # pwseed - the per-instrument pw_lo/pw_hi seeds. pwacc is the live
    # accumulator (shared by every voice playing the instrument); init
    # copies pwseed -> pwacc so each subtune starts fresh.
    lines.append('pwseed:')
    for m in models:
        lines.append(f'        .byt ${m.init_pw_lo:02X},${m.init_pw_hi:02X}')
    lines.append('pwacc: .byt ' + ','.join(['0'] * (2 * len(models))))

    # the freq table, emitted as raw bytes — the music reads it as
    # 16-bit entries, the SFX sweep walks it byte-wise and overflows
    # past the musical notes into the engine-state region.
    lines.append('freqtab:')
    for i in range(0, len(freq_bytes), 16):
        chunk = freq_bytes[i:i + 16]
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in chunk))

    # the overlap seed — v_ctrl / pwm_period / pwm_dir initial values.
    # The engine's per-voice variables sit past the 96-entry freq table;
    # init copies these load-time bytes into the zero-page mirrors so an
    # off-table read (or a counter's first DEC) sees the right value.
    # `seed_overlap=False` zeros the seed for engines that init their
    # per-voice state at runtime (Human Race's $1A9C init).
    if seed_overlap:
        # The 6 per-voice state vars live inside the freq-table region.
        # Each engine has the same set of vars but at engine-specific
        # offsets — Commando defaults; Hunter Patrol's v_slide is at
        # +238 instead of +239 (one byte earlier within the state).
        so = seed_offsets or {
            'v_ctrl':     208,
            'pwm_period': 229,
            'pwm_dir':    232,
            'v_instr':    214,
            'v_durfield': 205,
            'v_slide':    239,
        }
        ov = ([freq_bytes[so['v_ctrl']     + i] for i in range(3)]
              + [freq_bytes[so['pwm_period'] + i] for i in range(3)]
              + [freq_bytes[so['pwm_dir']    + i] for i in range(3)]
              + [freq_bytes[so['v_instr']    + i] for i in range(3)]
              + [freq_bytes[so['v_durfield'] + i] for i in range(3)]
              + [freq_bytes[so['v_slide']    + i] for i in range(3)])
    else:
        ov = [0] * 18
    lines.append('ovseed: .byt ' + ','.join(f'${b:02X}' for b in ov))

    # patterns — each unique pattern emitted once; orderlists reference
    # them by a dense slot. pattern indices are global, so the pool is
    # shared by all packed subtunes. The note codec serialises each
    # pattern (byte 0 = note count); the format is the codec's choice.
    for slot, blob in enumerate(pat_bytes):
        lines.append(f'pat{slot}:')
        for i in range(0, len(blob), 16):
            chunk = blob[i:i + 16]
            lines.append('        .byt ' + ','.join(f'${b:02X}' for b in chunk))
    if codec_extra:
        lines.append(codec_extra)

    npat = len(pat_bytes)
    lines.append('pataddr_lo: .byt '
                 + ','.join(f'<pat{s}' for s in range(npat)))
    lines.append('pataddr_hi: .byt '
                 + ','.join(f'>pat{s}' for s in range(npat)))

    # per-subtune orderlists ($FF = loop to orderLoop, $FE = end of song).
    # An empty orderlist (e.g. Human Race's unused V3) emits just $FE —
    # set_patptr will see the song-end terminator at the first read and
    # set v_ended on the voice, leaving it silent. $FF here would loop
    # forever (the only entry is the terminator).
    for si, score in enumerate(scores):
        for vi, v in enumerate(score.voices):
            if v.orderlist:
                term = '$FE' if v.stop else '$FF'
                ob = ','.join(f'${pat_slot[oidx]:02X}' for oidx in v.orderlist)
                lines.append(f'order_{si}_{vi}: .byt {ob},{term}')
            else:
                lines.append(f'order_{si}_{vi}: .byt $FE')

    # subOrder* — 3 entries per subtune (one per voice); init copies the
    # selected subtune's row into the live orderLo/Hi/Loop arrays.
    los, his, loops = [], [], []
    for si, score in enumerate(scores):
        for vi, v in enumerate(score.voices):
            los.append(f'<order_{si}_{vi}')
            his.append(f'>order_{si}_{vi}')
            loops.append(f'${(v.loop if v.loop >= 0 else 0):02X}')
    lines.append('subOrderLo: .byt ' + ','.join(los))
    lines.append('subOrderHi: .byt ' + ','.join(his))
    lines.append('subOrderLoop: .byt ' + ','.join(loops))
    lines.append('subResetspd: .byt '
                 + ','.join(f'${r:02X}' for r in resetspds))
    lines.append('subVoiceStart: .byt '
                 + ','.join(f'${v:02X}' for v in voice_starts))

    # Per-subtune engine-param tables — only emitted when any one is
    # provided; the engine then reads from them at init (see _hubbard_emit_sid's
    # `uses_psp` branch). Each list MUST be len(scores).
    if (per_subtune_speed_ctr_init is not None
            or per_subtune_incby2_step is not None
            or per_subtune_incby2_late_gate is not None):
        n = len(scores)
        sci = per_subtune_speed_ctr_init or [0] * n
        ibs = per_subtune_incby2_step or [0] * n
        ibg = per_subtune_incby2_late_gate or [0xFF] * n
        lines.append('subSpeedCtrInit: .byt '
                     + ','.join(f'${b & 0xFF:02X}' for b in sci))
        lines.append('subIncBy2Step: .byt '
                     + ','.join(f'${b & 0xFF:02X}' for b in ibs))
        lines.append('subIncBy2LateGate: .byt '
                     + ','.join(f'${b & 0xFF:02X}' for b in ibg))

    # Per-subtune ovseed (per-voice initial state). When provided, init
    # copies the selected sub's 18-byte ovseed into `ovseed` before the
    # iniov loop runs. This is for unified engines (5 Title Tunes) where
    # the 5 sub-engines have different load-time per-voice state values.
    if per_subtune_ovseed is not None:
        assert all(len(o) == 18 for o in per_subtune_ovseed), \
            'each per_subtune_ovseed entry must be 18 bytes'
        for i, ov_bytes in enumerate(per_subtune_ovseed):
            lines.append(f'subOvseed_{i}: .byt '
                         + ','.join(f'${b & 0xFF:02X}' for b in ov_bytes))
        lines.append('subOvseedLo: .byt '
                     + ','.join(f'<subOvseed_{i}'
                                 for i in range(len(per_subtune_ovseed))))
        lines.append('subOvseedHi: .byt '
                     + ','.join(f'>subOvseed_{i}'
                                 for i in range(len(per_subtune_ovseed))))

    # live per-voice orderlist selection (filled by init)
    lines.append('orderLo: .byt 0,0,0')
    lines.append('orderHi: .byt 0,0,0')
    lines.append('orderLoop: .byt 0,0,0')

    # statebuf - the engine-state mirror the off-table arpeggio indexes.
    # Initial bytes hold any const scalars (Commando's per-voice sidoff
    # 0,7,14 lives here; HR's sidoffs 0,7 likewise). The rest is filled
    # live by build_statebuf, with unmapped gap bytes left at their
    # init value (usually 0).
    lines.append(f'statebuf: .byt {_statebuf_init_bytes(state_layout)}')

    # sound-effect records — 32 bytes each: V1[7], V2[7], start, end,
    # rate, flags (bit0 direction, bit1 skip-V1, bit2 skip-both),
    # v2_byte_offset, gate (bit7/6 toggle V1/V2). See sfx_play.
    lines.append('sfxdata:')
    for sf in sfx_list:
        flags = ((1 if sf.direction == 'up' else 0)
                 | (2 if sf.skip_v1 else 0)
                 | (4 if sf.skip_both else 0))
        gate = ((0x80 if sf.toggle_v1 else 0)
                | (0x40 if sf.toggle_v2 else 0))
        rec = (list(sf.v1) + list(sf.v2)
               + [sf.start_index, sf.end_index, sf.rate, flags,
                  sf.v2_byte_offset, gate])
        rec += [0] * (32 - len(rec))
        lines.append('        .byt ' + ','.join(f'${b:02X}' for b in rec))
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def _sfx_state_in_freqtab(asm: str, ofs: int) -> str:
    """Relocate the SFX engine state into the freq-table off-table
    region, for engines whose SFX pitch sweep overruns the 96-entry
    table and reads engine state as 'frequency' (Monty: $84FB+).

    The shared SFX player is Commando's — zp state plus a few bytes
    mirrored at Commando's scattered freq-table offsets. This rewires
    it so the SFX-state block sits at ofs..ofs+5 and the post-update
    sweep index is mirrored there each step, so the overrun reads live
    state byte-exact. Commando keeps the original wiring (ofs None)."""
    # 1. init_sfx — write the SFX-state block at this engine's offsets:
    #    +0 disable=0, +1 SFX index, +2 static $ff, +3 sweep index,
    #    +4 step rate, +5 end index.
    o2 = ("        lda #$80\n"
          "        sta freqtab+241      ; the sweep reads $5519 here -"
          " mode byte $80\n"
          "        lda sfx_idx\n"
          "        sta freqtab+255      ; $5527 - the SFX index\n"
          "        lda #$ff\n"
          "        sta freqtab+256      ; $5528 - drum_enable\n"
          "        ldy #14\n"
          "        lda (sfx_rec),y      ; record 14 - sweep start index\n"
          "        sta sfx_index\n")
    n2 = ("        lda #$00\n"
          f"        sta freqtab+{ofs}        ; SFX-disable flag\n"
          "        lda sfx_idx\n"
          f"        sta freqtab+{ofs + 1}        ; SFX index\n"
          "        lda #$ff\n"
          f"        sta freqtab+{ofs + 2}        ; static byte\n"
          "        ldy #16\n"
          "        lda (sfx_rec),y      ; record 16 - step rate\n"
          f"        sta freqtab+{ofs + 4}        ; step counter\n"
          "        ldy #15\n"
          "        lda (sfx_rec),y      ; record 15 - end index\n"
          f"        sta freqtab+{ofs + 5}        ; end index\n"
          "        ldy #14\n"
          "        lda (sfx_rec),y      ; record 14 - sweep start index\n"
          "        sta sfx_index\n"
          f"        sta freqtab+{ofs + 3}        ; sweep index (initial)\n")
    assert o2 in asm, 'sfx fix: init_sfx block not found'
    asm = asm.replace(o2, n2, 1)

    # 2. sfxs_go — mirror the POST-update sweep index to freqtab+ofs+3
    #    before the sweep reads it (the engine advances its index in
    #    memory, then reads the freq table, so the overrun read of the
    #    index byte sees the new value).
    o3 = ("        lda (sfx_rec),y      ; record 17 - flags\n"
          "        sta sfx_flags\n"
          "        and #$04\n")
    n3 = ("        lda (sfx_rec),y      ; record 17 - flags\n"
          "        sta sfx_flags\n"
          "        and #$01\n"
          "        beq sfxm_dn\n"
          "        lda sfx_index\n"
          "        clc\n"
          "        adc #$01\n"
          "        jmp sfxm_st\n"
          "sfxm_dn:\n"
          "        lda sfx_index\n"
          "        sec\n"
          "        sbc #$01\n"
          "sfxm_st:\n"
          f"        sta freqtab+{ofs + 3}\n"
          "        lda sfx_flags\n"
          "        and #$04\n")
    assert o3 in asm, 'sfx fix: sfxs_go block not found'
    asm = asm.replace(o3, n3, 1)
    return asm


from dataclasses import dataclass as _dataclass, field as _field
from typing import Optional as _Optional


@_dataclass
class _Inputs:
    """Everything `_hubbard_emit_sid` needs, decoupled from the source.

    `_inputs_from_config` builds this by reading `config.sid_path`.
    `_inputs_from_usf` (in `build_from_usf.py`) builds it from a
    v3 `.usf` file alone — no engine-name lookup. Both feed `_hubbard_emit_sid`
    which is pure: it knows nothing about how the inputs were derived.
    """
    # PSID header metadata
    title: bytes              # exact 32-byte bytes (latin-1) for header
    author: bytes
    released: bytes
    start_song: int           # 1-indexed
    # Engine equates / asm flags
    arp_interval: int
    arp_period: int
    linear_pw_or: int
    incby2_step: int
    incby2_every_frame: bool
    incby2_onset: int
    suppress_first_notestart: bool
    freeze_on_stop: bool
    speed_ctr_init: int
    first_frame_gate_off: bool
    stop_fill: _Optional[int]
    sfx_framectr_ofs: int
    sfx_state_ofs: _Optional[int]
    has_sfx: bool
    # Per-engine data
    subtunes: tuple
    models: list                   # list[InstrumentModel]
    scores: list                   # list[Score]
    resetspds: list                # list[int]
    voice_starts: list             # list[int]
    freq_bytes: bytes              # 320 bytes
    sfx_list: list
    seed_overlap: bool = True
    psid_speed: int = 0       # PSID v2 speed bitmask (bit N = subtune N+1)
    state_layout: StatebufLayout = _field(default_factory=lambda: COMMANDO_STATEBUF_LAYOUT)
    seed_offsets: _Optional[dict] = None     # per-engine ovseed offsets
    frame_ctr_init: int = 0xFF                # initial zp frame_ctr
    incby2_late_gate: _Optional[int] = None   # fx_incby2 v_dur < N gate
    arp_phase_invert: bool = False            # swap base/+OFS sense in fx_arp
    # Engines whose off-table note-start reads pattern-position state
    # (Thing on a Spring) need the current voice's v_hubidx slot in
    # statebuf decremented by 1 to match the engine's v_patpos value
    # at the freq-read moment (which is BEFORE the post-pitch INC).
    # Offset = where v_hubidx lives in the engine's state_layout
    # (Commando default = 7).
    ns_offtab_decr_offset: _Optional[int] = None
    # Whether load_note resets v_hubidx to 0 at the last note of a
    # pattern. Default True (matches Commando family). Thing on a
    # Spring's engine doesn't reset v_patpos until the $C160 read,
    # which fires on the NEXT note-load frame.
    hubidx_wrap_at_patend: bool = True
    # Per-subtune engine-param overrides (5 Title Tunes unified path).
    # When any of these lists is set, the codegen emits per-subtune
    # tables (subSpeedCtrInit / subIncBy2Step / subIncBy2LateGate) and
    # the engine's init loads cur_incby2_step / cur_incby2_late_gate
    # zp slots from them. SPEED_CTR_INIT becomes a table read at init
    # time too. Use `incby2_late_gate=$FF` per sub to mean "no gate".
    # Each list MUST be len(subtunes); the value at index i applies
    # when subtune i plays. When all three are None, the codegen
    # emits the existing compile-time-constant code (no change).
    per_subtune_speed_ctr_init: _Optional[list] = None
    per_subtune_incby2_step: _Optional[list] = None
    per_subtune_incby2_late_gate: _Optional[list] = None
    # Per-subtune ovseed: each entry is 18 bytes — the 6 freq-table-
    # overlap state vars × 3 voices, in v_ctrl/pwm_period/pwm_dir/
    # v_instr/v_durfield/v_slide order. When set, init copies the
    # selected sub's bytes into the `ovseed` data block before the
    # iniov loop. Used by unified-engine builds (5 Title Tunes) where
    # each sub's per-voice load-time state differs.
    per_subtune_ovseed: _Optional[list] = None
    # Master-volume fade — see EngineConfig.master_vol_subtrahend_voice.
    # When set (0/1/2), codegen maintains a vol_progress counter that
    # increments on the named voice's pattern-end (never wraps) and
    # writes $D418 = clamp(master_vol_base - counter, 0..$0F) on every
    # instrument-change note. None disables.
    master_vol_subtrahend_voice: _Optional[int] = None
    master_vol_base: int = 0xA0
    master_vol_trigger: str = 'inst_change'
    tie_preserves_slide: bool = False


def _inputs_from_config(config) -> _Inputs:
    """Build inputs from a legacy `EngineConfig` (reads the binary)."""
    from src.hubbard_emu import load_sid
    _, binary, load = load_sid(config.sid_path)
    models = decode_all(config.sid_path, config.instr_base,
                        config.instr_count, config.arp_interval,
                        config.vib_onset, config.arp_period)
    scores = [config.extract(subtune=s).score for s in config.subtunes]
    resetspds = [config.resetspd(s, binary, load) for s in config.subtunes]
    voice_starts = [config.voice_starts[s] if config.voice_starts else 2
                    for s in config.subtunes]
    freq_bytes = bytes(binary[config.freq_table_base - load + i]
                       for i in range(320))
    sfx_list = config.extract_sfx(config.sid_path)[0] if config.has_sfx else []

    with open(config.sid_path, 'rb') as f:
        orig_hdr = f.read(124)

    psid_speed = int.from_bytes(orig_hdr[0x12:0x16], 'big')

    return _Inputs(
        title=orig_hdr[22:54],
        author=orig_hdr[54:86],
        released=orig_hdr[86:118],
        start_song=(orig_hdr[0x10] << 8) | orig_hdr[0x11],
        psid_speed=psid_speed,
        arp_interval=config.arp_interval,
        arp_period=config.arp_period,
        arp_phase_invert=config.arp_phase_invert,
        linear_pw_or=config.linear_pw_or,
        incby2_step=config.incby2_step,
        incby2_every_frame=config.incby2_every_frame,
        incby2_onset=config.incby2_onset,
        suppress_first_notestart=config.suppress_first_notestart,
        freeze_on_stop=config.freeze_on_stop,
        speed_ctr_init=config.speed_ctr_init,
        first_frame_gate_off=config.first_frame_gate_off,
        stop_fill=config.stop_fill,
        sfx_framectr_ofs=config.sfx_framectr_ofs,
        sfx_state_ofs=config.sfx_state_ofs,
        has_sfx=config.has_sfx,
        seed_overlap=config.seed_overlap,
        frame_ctr_init=config.frame_ctr_init,
        incby2_late_gate=config.incby2_late_gate,
        subtunes=config.subtunes,
        models=models, scores=scores, resetspds=resetspds,
        voice_starts=voice_starts, freq_bytes=freq_bytes,
        sfx_list=sfx_list,
        master_vol_subtrahend_voice=config.master_vol_subtrahend_voice,
        master_vol_base=config.master_vol_base,
        master_vol_trigger=config.master_vol_trigger,
        tie_preserves_slide=config.tie_preserves_slide,
    )


def _hubbard_emit_sid(inputs: _Inputs, out_path: str, codec,
              load_addr: int = LOAD) -> str:
    """Emit a SID file from a fully-prepared `_Inputs`. No I/O of the
    original binary; everything needed is in `inputs`.

    `load_addr` overrides the default $1000 load address — set by the
    compound-PSID build (5 Title Tunes) which packs 5 engines at
    non-overlapping addresses.
    """
    pat_order, pat_slot = _pattern_pool(inputs.scores)
    pat_bytes, codec_extra = codec.encode(pat_order)

    asm = (f'PWLEN = {2 * len(inputs.models) - 1}\n'
           f'N_MUSIC = {len(inputs.subtunes)}\n'
           f'FRAME_CTR_INIT = {inputs.frame_ctr_init}\n'
           f'HUBIDX_WRAP_AT_PATEND = {1 if inputs.hubidx_wrap_at_patend else 0}\n'
           f'ARP_OFS = {inputs.arp_interval}\n'
           f'ARP_MASK = {inputs.arp_period - 1}\n'
           f'LINEAR_PW_OR = {inputs.linear_pw_or}\n'
           f'INCBY2_STEP = {inputs.incby2_step & 0xFF}\n'
           f'INCBY2_ALWAYS = {1 if inputs.incby2_every_frame else 0}\n'
           f'INCBY2_ONSET = {inputs.incby2_onset}\n'
           f'DRUM_PRIO_INIT = {0 if inputs.suppress_first_notestart else 255}\n'
           f'DUR_BITS = {codec.dur_bits}\n'
           f'INST_BITS = {codec.inst_bits}\n'
           f'FREEZE_ON_STOP = {1 if inputs.freeze_on_stop else 0}\n'
           f'SPEED_CTR_INIT = {inputs.speed_ctr_init}\n'
           f'FIRST_FRAME_GATE_OFF = {1 if inputs.first_frame_gate_off else 0}\n'
           f'STOP_IS_FILL = {1 if inputs.stop_fill is not None else 0}\n'
           f'STOP_FILL = {inputs.stop_fill or 0}\n'
           f'MASTER_VOL_INIT = {0x00 if inputs.master_vol_subtrahend_voice is not None else 0x0F}\n'
           + codec.zp_asm + '\n'
           + ENGINE + '\n'
           + codec.note_asm + '\n'
           + _emit_data(inputs.scores, inputs.models, inputs.freq_bytes,
                        inputs.resetspds, inputs.voice_starts,
                        inputs.sfx_list, pat_slot, pat_bytes, codec_extra,
                        seed_overlap=inputs.seed_overlap,
                        state_layout=inputs.state_layout,
                        seed_offsets=inputs.seed_offsets,
                        per_subtune_speed_ctr_init=inputs.per_subtune_speed_ctr_init,
                        per_subtune_incby2_step=inputs.per_subtune_incby2_step,
                        per_subtune_incby2_late_gate=inputs.per_subtune_incby2_late_gate,
                        per_subtune_ovseed=inputs.per_subtune_ovseed)
           + '\n')

    asm = asm.replace('inc freqtab+253',
                      f'inc freqtab+{inputs.sfx_framectr_ofs}')
    if inputs.sfx_state_ofs is not None:
        asm = _sfx_state_in_freqtab(asm, inputs.sfx_state_ofs)

    # Substitute the per-engine build_statebuf body for the sentinel
    # in the ENGINE template. The layout differs per engine — see
    # StatebufLayout / COMMANDO_STATEBUF_LAYOUT / Human Race's layout.
    asm = asm.replace('; %%BUILD_STATEBUF%%',
                      _emit_build_statebuf(inputs.state_layout))

    # When arp_phase_invert, flip the sense of fx_arp's branch: the
    # "frame_ctr & ARP_MASK == 0" path becomes the +ARP_OFS one
    # instead of the base one (One Man and his Droid uses
    # `frame_ctr & $04 == 0` → +12, the inverse of every other engine).
    if inputs.arp_phase_invert:
        asm = asm.replace('beq fxa_even', 'bne fxa_even')

    # Per-subtune engine params (5 Title Tunes unified path). When ANY
    # of the per_subtune_* lists is set, replace the compile-time SPEED
    # CTR / INCBY2 STEP / late-gate code with per-subtune-table reads.
    uses_psp = (
        inputs.per_subtune_speed_ctr_init is not None
        or inputs.per_subtune_incby2_step is not None
        or inputs.per_subtune_incby2_late_gate is not None)

    if uses_psp:
        # SPEED_CTR_INIT load: replace `lda #SPEED_CTR_INIT; sta speed_ctr`
        # with a per-subtune table read. The init block also primes the
        # cur_incby2_* zp slots that fx_incby2 reads at runtime.
        asm = asm.replace(
            '        lda #SPEED_CTR_INIT\n        sta speed_ctr',
            '        ldy sub_tmp\n'
            '        lda subSpeedCtrInit,y\n'
            '        sta speed_ctr\n'
            '        lda subIncBy2Step,y\n'
            '        sta cur_incby2_step\n'
            '        lda subIncBy2LateGate,y\n'
            '        sta cur_incby2_late_gate')
        # Per-subtune ovseed copy — runs BEFORE the iniov loop, so init's
        # per-voice state seeding sees the correct per-subtune bytes.
        ov_copy_asm = ''
        if inputs.per_subtune_ovseed is not None:
            ov_copy_asm = (
                '        ldy sub_tmp\n'
                '        lda subOvseedLo,y\n'
                '        sta sfx_rec\n'
                '        lda subOvseedHi,y\n'
                '        sta sfx_rec+1\n'
                '        ldy #17\n'
                'ovcopy: lda (sfx_rec),y\n'
                '        sta ovseed,y\n'
                '        dey\n'
                '        bpl ovcopy')
        asm = asm.replace('; %%OVSEED_COPY%%', ov_copy_asm)
        # fx_incby2: switch the slide-step `adc #INCBY2_STEP` to use the
        # zp slot loaded above.
        asm = asm.replace(
            '        adc #INCBY2_STEP',
            '        adc cur_incby2_step')
        # Late-gate sentinel: always emit the runtime check; subs with
        # no gate use cur_incby2_late_gate = $FF (v_dur never reaches).
        late_gate_asm = (
            f'        lda v_dur,x\n'
            f'        cmp cur_incby2_late_gate\n'
            f'        bcs fxi_ret          ; v_dur >= late_gate -> skip')
        asm = asm.replace('; %%INCBY2_LATE_GATE%%', late_gate_asm)
    else:
        # Existing per-engine compile-time path (unchanged for the 9
        # already-migrated engines).
        late_gate_asm = ''
        if inputs.incby2_late_gate is not None:
            late_gate_asm = (
                f'        lda v_dur,x\n'
                f'        cmp #{inputs.incby2_late_gate}\n'
                f'        bcs fxi_ret          ; v_dur >= late_gate -> skip')
        asm = asm.replace('; %%INCBY2_LATE_GATE%%', late_gate_asm)
        # Engines without per-subtune ovseed don't copy anything — the
        # codegen-baked `ovseed` constants are read directly.
        asm = asm.replace('; %%OVSEED_COPY%%', '')

    # Off-table note-start: for engines whose off-table reads
    # pattern-position state, decrement the current voice's v_hubidx
    # slot in statebuf by 1 to match the engine's v_patpos at the
    # freq-read moment (orig advances mid-load; ours advances at end).
    # Only Thing on a Spring sets this for now.
    offtab_decr_asm = ''
    if inputs.ns_offtab_decr_offset is not None:
        ofs = inputs.ns_offtab_decr_offset
        # Caller's voice index is in X here (build_statebuf preserves X).
        offtab_decr_asm = (
            f'        sec\n'
            f'        lda statebuf+{ofs},x\n'
            f'        sbc #1\n'
            f'        sta statebuf+{ofs},x')
    asm = asm.replace('; %%NS_OFFTAB_DECR%%', offtab_decr_asm)

    # Master-volume fade: when set, emit (a) a per-voice gate that INCs
    # vol_progress on the configured voice's pattern-end, and (b) the
    # $D418 = clamp(BASE - vol_progress, 0..$0F) write on every
    # instrument-change note. The two sentinels live in note_codec.py's
    # load_note; both expand to empty strings when the feature is off,
    # leaving previously-byte-exact engines unaffected.
    vol_inc_asm = ''
    vol_write_inst_change_asm = ''
    vol_write_every_note_asm = ''
    if inputs.master_vol_subtrahend_voice is not None:
        v = inputs.master_vol_subtrahend_voice
        # Peek-ahead semantics: INC vol_progress when the current voice's
        # v_notesleft has just decremented to 0 — i.e. THIS load was the
        # pattern's last note. Matches the engine's $C15A-$C167 path
        # which INCs $C46D on the same tick the last note is loaded
        # (engine peeks one byte ahead and finds the $FF terminator).
        vol_inc_asm = (
            f'        cpx #{v}\n'
            f'        bne vp_skip\n'
            f'        lda v_notesleft,x\n'
            f'        bne vp_skip\n'
            f'        inc vol_progress\n'
            f'vp_skip:')
        vol_write_template = (
            f'        lda #${inputs.master_vol_base:02X}\n'
            f'        sec\n'
            f'        sbc vol_progress\n'
            f'        cmp #$0f\n'
            f'        bcc {{label}}\n'
            f'        lda #$0f\n'
            f'{{label}}: sta $d418')
        if inputs.master_vol_trigger == 'every_note':
            vol_write_every_note_asm = vol_write_template.format(label='mvw_lt')
        else:
            vol_write_inst_change_asm = vol_write_template.format(label='mvw_lt')
    vol_init_asm = ('        sta vol_progress'
                    if inputs.master_vol_subtrahend_voice is not None
                    else '')
    asm = asm.replace('; %%VOL_PROGRESS_INC%%', vol_inc_asm)
    asm = asm.replace('; %%MASTER_VOL_WRITE%%', vol_write_inst_change_asm)
    asm = asm.replace('; %%MASTER_VOL_EVERY_NOTE%%',
                      vol_write_every_note_asm)
    asm = asm.replace('; %%VOL_PROGRESS_INIT%%', vol_init_asm)

    # tie_preserves_slide selects WHERE the v_drumtrig clear lives in
    # ln_decode. False (default): unconditional at the top (pre-9828b37
    # behaviour — works for Monty / Chimera / others). True: only in the
    # non-tie path (matches Confuzion / BoB's `BVS skip` over the
    # v_slide clear). Both placements emit exactly `sta v_drumtrig,x`
    # (2 bytes) so swapping doesn't shift any addresses.
    if inputs.tie_preserves_slide:
        clear_uncond = ''
        clear_nontie = '        sta v_drumtrig,x'
    else:
        clear_uncond = '        sta v_drumtrig,x'
        clear_nontie = ''
    asm = asm.replace('; %%CLEAR_DRUMTRIG_UNCOND%%', clear_uncond)
    asm = asm.replace('; %%CLEAR_DRUMTRIG_NONTIE%%', clear_nontie)

    # Relocate the engine to the requested load address — the ENGINE
    # template has `* = $1000` hardcoded; rewrite it to load_addr.
    asm = asm.replace('* = $1000', f'* = ${load_addr:04X}')

    src = '/tmp/usf2_commando.s'
    obj = '/tmp/usf2_commando.bin'
    with open(src, 'w') as f:
        f.write(asm)
    r = subprocess.run([XA, src, '-o', obj], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'xa65 failed:\n{r.stdout}\n{r.stderr}')
    with open(obj, 'rb') as f:
        code = f.read()

    # PSID header
    songs = len(inputs.subtunes) + (len(inputs.sfx_list) if inputs.has_sfx else 0)
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', load_addr)
    h += struct.pack('>H', load_addr)
    h += struct.pack('>H', load_addr + 3)
    h += struct.pack('>H', songs)
    h += struct.pack('>H', min(max(inputs.start_song, 1), songs))
    h += struct.pack('>I', inputs.psid_speed)
    # 3 × 32-byte latin-1 fields. Pad/truncate to exactly 32 each.
    for s in (inputs.title, inputs.author, inputs.released):
        h += s[:32].ljust(32, b'\x00')
    h += struct.pack('>H', 0x0014)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124, len(h)

    with open(out_path, 'wb') as f:
        f.write(bytes(h) + code)
    return out_path




# =============================================================================
# Hubbard '85 — USF -> _Inputs adapter + digi region builder
# =============================================================================
#
# Lifted from the former pipelines/build_from_usf.py module-level helpers.
# Stays here next to _hubbard_emit_sid so the shape's full dispatch lives
# in one file. `build_from_usf` (the top-level public entry) stays in
# pipelines/build_from_usf.py and just calls into universal_codegen.emit_sid.

from src.usf import DigiSubtune
from pipelines.hubbard.sfx import SoundEffect
from pipelines.hubbard.engine_constants import (
    DigiCode, chimera_psid_dispatcher, assemble_chimera_digi_player,
)
from pipelines.hubbard.flac_io import read_sample
from pipelines.hubbard.digi_pack import pack_digi
from pipelines.hubbard.inst_generalize import (
    InstrumentModel, ArpSpec, VibratoSpec, PwmSpec,
)
from pipelines.hubbard.types import (
    Score, Voice, Note, Instrument as HubInstrument,
)
# Named handles for the few distinct digi techniques in the SID corpus.
# Each entry maps a tune-level `digi_player: <name>` to its DigiCode
# (which describes where the dispatcher + player live in the rebuild's
# address space). The bytes of the player asm itself stay in
# engine_constants.py — they're 6502 code, not USF data.
def _digi_player_registry():
    from pipelines.hubbard.engine_constants import CHIMERA_DIGI
    return {
        'chimera_1bit': CHIMERA_DIGI,
    }


# ---------------------------------------------------------------------------
# USF → InstrumentModel (the inverse of pipelines/hubbard/chimera/extract/to_usf.
# _convert_instrument)
# ---------------------------------------------------------------------------

def _model_from_usf_instrument(u, vib_onset: int) -> InstrumentModel:
    init_ctrl = u.waveform[0] if u.waveform else 0
    init_pw_lo = u.pwm.init & 0xFF
    init_pw_hi = (u.pwm.init >> 8) & 0xFF

    pwm = None
    pw_lo_kind = 'const'
    pw_hi_kind = 'const'
    if u.pwm.mode == 'linear':
        pwm = PwmSpec(mode='linear', speed=u.pwm.speed,
                      seed_lo=init_pw_lo, seed_hi=init_pw_hi,
                      lo_bound=u.pwm.min_hi, hi_bound=u.pwm.max_hi)
        pw_lo_kind = 'accumulator'
    elif u.pwm.mode == 'bidirectional':
        pwm = PwmSpec(mode='bidirectional',
                      period=u.pwm.speed & 0x1F,
                      step=u.pwm.speed & 0xE0,
                      seed_lo=init_pw_lo, seed_hi=init_pw_hi,
                      lo_bound=u.pwm.min_hi, hi_bound=u.pwm.max_hi)
        pw_lo_kind = pw_hi_kind = 'accumulator'

    # Arpeggio: USF stores [0] when off, full offsets list when on.
    has_arp = len(u.arp.offsets) > 1
    arpeggio = (ArpSpec(intervals=tuple(u.arp.offsets), step_every=1)
                if has_arp else None)

    vibrato = (VibratoSpec(depth=u.vibrato.scale, onset_dur=vib_onset)
               if u.vibrato.scale != 0 else None)

    # Reconstruct the engine's fx_flags byte from the structured fields.
    fx_flags = ((1 if u.freq_slide else 0)
                | (2 if u.inc_by2 else 0)
                | (4 if has_arp else 0)
                | (8 if u.pwm.mode == 'linear' else 0))

    return InstrumentModel(
        inst=u.id - 1,                              # back to 0-indexed
        init_ctrl=init_ctrl,
        init_pw_lo=init_pw_lo,
        init_pw_hi=init_pw_hi,
        init_ad=u.adsr[0],
        init_sr=u.adsr[1],
        hr_ctrl=init_ctrl & 0xFE,
        pw_lo_kind=pw_lo_kind, pw_hi_kind=pw_hi_kind,
        fx_flags=fx_flags,
        freq_slide=u.freq_slide, inc_by2=u.inc_by2,
        arpeggio=arpeggio, vibrato=vibrato, pwm=pwm,
    )


# ---------------------------------------------------------------------------
# USF → Score (the extract-output shape the codegen consumes)
# ---------------------------------------------------------------------------

_NOTE_TO_NUM = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

# A pitch byte the engine treats as "no fresh note." Hubbard '85 uses
# values past the 96-entry musical freq table as off-table / rest. We
# use a sentinel that's safely past 95 and won't collide with arpeggio
# extensions.
_REST_PITCH = 0xFF


def _pitch_to_engine(p) -> int:
    if p.is_rest:
        return _REST_PITCH
    semis = _NOTE_TO_NUM[p.name] + 12 * p.octave
    return semis


def _instr_to_engine_byte(instr_ref, current_instr: int) -> int:
    """Convert a USF NoteRow's `instr` field back to the engine's
    per-note instrument byte. When no ref is present, set the high bit
    ('do not load new instrument'). When a ref is present, emit the
    instrument's 0-indexed id with high bit clear."""
    if instr_ref is None:
        return current_instr | 0x80
    # USF is 1-indexed; engine is 0-indexed.
    return (instr_ref.id - 1) & 0x3F


def _flags_to_engine(fx_flags: tuple) -> tuple[bool, int]:
    """Translate USF fx flag tokens back to (tie_bool, drum_trig_byte).

    Inverse of `to_usf._row_from_note`:
      tie         <- 'tie' token
      drum_trig   <- (0x80 if 'no_release') | porta_amount
    """
    tie = 'tie' in fx_flags
    drum_trig = 0x80 if 'no_release' in fx_flags else 0
    for flag in fx_flags:
        if flag.startswith('porta='):
            drum_trig |= int(flag[len('porta='):]) & 0x7F
    return tie, drum_trig


def _score_from_subtune(sub: MusicSubtune) -> Score:
    voices = []
    for vb in sub.voices:
        orderlist = list(vb.orderlist.entries)
        loop = vb.orderlist.loop_to if vb.orderlist.loop_to is not None else -1
        stop = vb.orderlist.stop
        patterns = {}
        for pat in vb.patterns:
            current_instr = 0
            notes = []
            for row in pat.rows:
                if row.instr is not None:
                    current_instr = row.instr.id - 1
                inst_byte = _instr_to_engine_byte(row.instr, current_instr)
                tie, drum = _flags_to_engine(row.fx_flags)
                notes.append(Note(
                    pitch=_pitch_to_engine(row.pitch),
                    duration=row.duration,
                    instrument=inst_byte,
                    tie=tie,
                    drum_trig=drum,
                ))
            patterns[pat.id] = notes
        voices.append(Voice(orderlist=orderlist, patterns=patterns,
                            loop=loop, stop=stop))
    return Score(tempo=sub.tempo, voices=voices)


# ---------------------------------------------------------------------------
# SfxSubtune → engine SoundEffect — the inverse of `_convert_sfx` in
# to_usf.py. Reassembles the 7-byte v1/v2 voice register lists (the
# freq_lo byte is re-derived from start_index / gate-flags-plus-offset).
# ---------------------------------------------------------------------------

def _soundeffect_from_usf(s: SfxSubtune, idx: int) -> SoundEffect:
    # Reconstruct the engine's gate byte at v2[0] — bit 7 toggle_v1,
    # bit 6 toggle_v2, bits 0-5 v2_offset. This matches `decode_sfx`'s
    # forward decomposition in pipelines/hubbard/sfx.py.
    gate_byte = ((0x80 if s.toggle_v1 else 0)
                 | (0x40 if s.toggle_v2 else 0)
                 | (s.v2_offset & 0x3F))
    v1_full = [s.start_index] + list(s.v1)         # 7 bytes
    v2_full = [gate_byte] + list(s.v2)             # 7 bytes
    return SoundEffect(
        index=idx,
        v1=v1_full,
        v2=v2_full,
        start_index=s.start_index,
        end_index=s.end_index,
        rate=s.rate,
        direction=s.direction,
        skip_v1=s.skip_v1,
        skip_both=s.skip_both,
        v2_byte_offset=s.v2_offset,
        toggle_v1=s.toggle_v1,
        toggle_v2=s.toggle_v2,
    )


# ---------------------------------------------------------------------------
# USF → _Inputs helpers
# ---------------------------------------------------------------------------

def _ovseed_from_init_state(init, instr_count: int) -> bytes:
    """Convert a USF `InitState` back into the 18-byte ovseed
    (the inverse of `_init_state_from_ovseed` in
    pipelines/hubbard/five_title_tunes/unified/write_unified_usf.py).
    Layout: v_ctrl[3] pwm_period[3] pwm_dir[3] v_instr[3]
            v_durfield[3] v_slide[3]."""
    if init is None or not init.voices:
        return bytes(18)
    ovseed = bytearray(18)
    for v in init.voices:
        i = v.id - 1
        if not 0 <= i < 3:
            continue
        ovseed[0 + i] = v.ctrl
        ovseed[3 + i] = v.pwm_period
        ovseed[6 + i] = 0x00 if v.pwm_dir == 'up' else 0xFF
        instr_byte = (v.instr.id - 1) & 0x3F if v.instr is not None else 0
        ovseed[9 + i] = instr_byte
        ovseed[12 + i] = v.dur_field
        ovseed[15 + i] = v.slide_v
    return bytes(ovseed)


# ---------------------------------------------------------------------------
# Combined music + digi build (for engines with digi subtunes, e.g. Chimera)
# ---------------------------------------------------------------------------

def _build_digi_region(usf: UsfFile, digi_subs: list[DigiSubtune],
                       digi_code: DigiCode, usf_dir: str,
                       music_load: int | None = None
                       ) -> tuple[bytes, int, int]:
    """Build the bytes of the digi region — dispatcher + tables +
    samples + player — placed at their fixed engine addresses.

    Returns `(region_bytes, region_base, play_addr)`. `play_addr` is
    the PSID `play` entry inside the dispatcher (used by the header).
    """
    base = digi_code.dispatcher_base                       # e.g. $9F80
    # The Chimera player is assembled lazily from its xa65 asm source
    # (regenerated, not lifted verbatim from the original SID).
    player_bytes = assemble_chimera_digi_player(
        player_base=digi_code.player_base)
    end  = digi_code.player_base + len(player_bytes)       # one past last byte

    # Generate the PSID dispatcher with addresses substituted for our
    # music engine and the digi player. `music_load` is passed by the
    # caller (auto-packing); fall back to digi_code.music_load_addr or
    # LOAD when called from contexts that don't know the music engine
    # address yet.
    if music_load is None:
        music_load = (digi_code.music_load_addr
                      if digi_code.music_load_addr is not None else LOAD)
    disp = chimera_psid_dispatcher(
        music_init=music_load, music_play=music_load + 3,
        digi_player=digi_code.player_base, base=base)
    dispatcher = disp['bytes']
    play_addr = base + disp['play_off']
    pace_table_addr = base + disp['pace_table_off']
    bank_table_addr = base + disp['bank_table_off']

    region = bytearray(end - base)
    region[0:len(dispatcher)] = dispatcher
    # Place the digi player at its base.
    player_off = digi_code.player_base - base
    region[player_off:player_off + len(player_bytes)] = player_bytes

    # Process digi subtunes: each carries a pace + bank in its FLAC's
    # Vorbis comments (via the extractor's `to_sample`).
    samples = []
    for st_idx, sub in enumerate(digi_subs):
        sample_path = os.path.join(usf_dir, sub.sample)
        sample = read_sample(sample_path)
        pace = int(sample.extras['pace'], 16)
        bank = int(sample.extras['bank'], 16)
        src = int(sample.extras['src'], 16)
        end_addr = int(sample.extras['end'], 16)
        keep_screen = sample.extras.get('keep_screen', '0') == '1'
        packed = pack_digi(sample)
        if end_addr - src != len(packed):
            raise ValueError(
                f'subtune {sub.id}: sample claims ${src:04X}-${end_addr:04X} '
                f'({end_addr - src} bytes) but packed bytes are '
                f'{len(packed)}')
        samples.append({
            'st_idx': st_idx, 'pace': pace, 'bank': bank,
            'src': src, 'end': end_addr, 'keep_screen': keep_screen,
            'packed': packed,
            'boundary_vol': sample.extras.get('boundary_vol', '00'),
        })

    # Per-subtune dispatcher tables — the PSID dispatcher's pace_table /
    # bank_table slots reported by `chimera_psid_dispatcher`.
    for s in samples:
        region[pace_table_addr - base + s['st_idx']] = s['pace']
        region[bank_table_addr - base + s['st_idx']] = s['bank']

    # Bank table at $A000 + bank*4 = {src_lo, src_hi, end_lo, end_hi}.
    bt_off = digi_code.bank_table_base - base
    for s in samples:
        e = bt_off + s['bank'] * 4
        region[e + 0] = s['src'] & 0xFF
        region[e + 1] = (s['src'] >> 8) & 0xFF
        region[e + 2] = s['end'] & 0xFF
        region[e + 3] = (s['end'] >> 8) & 0xFF

    # $A103 = sample-table length (number of banks the player accepts).
    region[(digi_code.bank_table_base + 0x103) - base] = len(samples)
    # $A108 = keep-screen flag. Use the first subtune's value (the
    # engine's design assumes it's constant per tune).
    if samples:
        region[(digi_code.bank_table_base + 0x108) - base] = \
            1 if samples[0]['keep_screen'] else 0
        # $A10A = pace placeholder (the dispatcher writes the real one
        # here at runtime). Set to the first subtune's pace.
        region[(digi_code.bank_table_base + 0x10A) - base] = samples[0]['pace']
    # $A10B+ = bank-validation table (the player linearly scans this
    # at startup to confirm the requested bank is registered). Entries
    # are ordered bank-ascending, which matches the original SIDs
    # we've seen — the cycle count of the scan depends on the order,
    # so cycle-strict reproduction requires we match it.
    for i, s in enumerate(sorted(samples, key=lambda x: x['bank'])):
        region[(digi_code.bank_table_base + 0x10B + i) - base] = s['bank']

    # Sample bytes at their claimed addresses.
    for s in samples:
        sb = s['src'] - base
        region[sb:sb + len(s['packed'])] = s['packed']
        # The digi player reads one byte PAST `end` on its last loop
        # iteration ($F9 wrap reads a final vol byte before the bounds
        # check exits) — preserve that byte from the original so the
        # very last $D418 write matches cycle-strict.
        boundary_vol = int(s.get('boundary_vol', '00'), 16)
        if 0 <= s['end'] - base < len(region):
            region[s['end'] - base] = boundary_vol

    return bytes(region), base, play_addr


def _emit_combined_sid(inputs: _Inputs, usf: UsfFile, digi_subs: list,
                       digi_code: DigiCode, out_path: str, usf_dir: str,
                       codec) -> str:
    """Emit a combined PSID containing music engine + digi engine +
    samples. Music at `digi_code.music_load_addr` (or LOAD if None);
    digi at the engine-fixed addresses ($9F80 dispatcher + $C000
    player for Chimera). The combined file uses inline-load encoding
    so the bytes are one contiguous segment between music_load_addr
    and the digi region's end, with a zero-fill gap between them.

    The default music_load=$1000 puts the music engine 36 KB below
    the dispatcher, ballooning the file to ~45 KB. Setting
    music_load_addr close to dispatcher_base (e.g. $9C00 for Chimera)
    shrinks the gap to a few hundred bytes — matching the original
    Chimera SID's ~12 KB footprint.
    """
    # Auto-pack music against dispatcher when music_load_addr is None:
    # measure music size at LOAD, then compute the tight music_load
    # before building the digi region (the dispatcher's JMP MUSIC_INIT
    # must match the final music_load address). Iterate in case the
    # assembled size shifts with the load address (page-crossing
    # penalties etc.); typically converges in 1-2 iterations.
    tmp_music = out_path + '.music.tmp'
    if digi_code.music_load_addr is not None:
        music_load = digi_code.music_load_addr
    else:
        _hubbard_emit_sid(inputs, tmp_music, codec, load_addr=LOAD)
        size = os.path.getsize(tmp_music) - 124
        music_load = digi_code.dispatcher_base - size
        for _ in range(4):
            _hubbard_emit_sid(inputs, tmp_music, codec, load_addr=music_load)
            new_size = os.path.getsize(tmp_music) - 124
            new_load = digi_code.dispatcher_base - new_size
            if new_load == music_load:
                break
            music_load = new_load

    digi_region, digi_base, play_addr = _build_digi_region(
        usf, digi_subs, digi_code, usf_dir, music_load=music_load)

    _hubbard_emit_sid(inputs, tmp_music, codec, load_addr=music_load)
    music_blob = open(tmp_music, 'rb').read()
    os.unlink(tmp_music)
    # _hubbard_emit_sid wrote a PSID. Strip its 124-byte header.
    music_body = music_blob[124:]                  # music bytes at $music_load

    music_end = music_load + len(music_body)
    if music_end > digi_base:
        raise ValueError(
            f'music engine at ${music_load:04X}-${music_end - 1:04X} overlaps '
            f'the digi region starting at ${digi_base:04X}')
    gap = bytes(digi_base - music_end)
    binary = music_body + gap + digi_region

    # PSID v2 header: load=$0000 (inline), init=dispatcher_base,
    # play=play_addr (regenerated PSID dispatcher's play entry).
    # No more RSID; no KERNAL dep at playback.
    n_music = len(inputs.subtunes)
    songs = n_music + len(digi_subs)
    start_song = min(max(inputs.start_song, 1), songs)

    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', 0x0000)             # load = inline-encoded
    h += struct.pack('>H', digi_code.dispatcher_base)
    h += struct.pack('>H', play_addr)
    h += struct.pack('>H', songs)
    h += struct.pack('>H', start_song)
    h += struct.pack('>I', inputs.psid_speed)
    for s in (inputs.title, inputs.author, inputs.released):
        h += s[:32].ljust(32, b'\x00')
    h += struct.pack('>H', 0x0014)             # flags (PAL + 6581)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124, len(h)

    with open(out_path, 'wb') as f:
        f.write(bytes(h))
        f.write(struct.pack('<H', music_load))   # inline load addr
        f.write(binary)
    return out_path


# ---------------------------------------------------------------------------
# USF → _Inputs
# ---------------------------------------------------------------------------

def _inputs_from_usf(usf: UsfFile) -> _Inputs:
    """Build codegen `_Inputs` from a USF — no engine-name lookup."""
    if usf.freq_table is None:
        raise ValueError(
            'Hubbard build requires a freq_table block in the USF')
    if len(usf.freq_table) != 320:
        raise ValueError(
            f'expected 320-byte freq_table, got {len(usf.freq_table)}')

    # Tune-level params with Commando-flavor defaults. Engines that
    # diverge from these set the field in the USF's params block.
    p = usf.params.fields if usf.params else {}

    def get(key, default):
        return p.get(key, default)

    def latin1(s: str) -> bytes:
        return s.encode('latin-1', errors='replace')

    # Vibrato onset is per-instrument; we plumb the top-level value
    # through each InstrumentModel at build time.
    vib_onset = get('vib_onset', 6)

    models = [_model_from_usf_instrument(u, vib_onset)
              for u in usf.instruments]

    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    music_subs.sort(key=lambda s: s.id)
    subtune_ids = tuple(s.id for s in music_subs)
    scores = [_score_from_subtune(s) for s in music_subs]
    resetspds = [s.tempo - 1 for s in music_subs]
    # Per-subtune voice_start (Action Biker skips a voice on sub 0).
    voice_starts = []
    for s in music_subs:
        sp = s.params.fields if s.params else {}
        voice_starts.append(sp.get('voice_start', 2))

    # Per-subtune mechanism mode: 5_Title_Tunes-style compound engines
    # carry per-subtune deltas on each MusicSubtune.params + per-sub
    # init state. Only the keys below flip the mode; per-sub
    # `voice_start` alone is read independently.
    _PER_SUBTUNE_MECHANISM = {
        'speed_ctr_init', 'incby2_step', 'incby2_late_gate', 'tick_divider',
    }
    has_per_subtune = any(
        s.init is not None or
        (s.params is not None and
         _PER_SUBTUNE_MECHANISM & s.params.fields.keys())
        for s in music_subs)
    per_subtune_speed_ctr_init = None
    per_subtune_incby2_step = None
    per_subtune_incby2_late_gate = None
    per_subtune_ovseed = None
    if has_per_subtune:
        per_subtune_speed_ctr_init = []
        per_subtune_incby2_step = []
        per_subtune_incby2_late_gate = []
        per_subtune_ovseed = []
        top_speed_ctr_init = get('speed_ctr_init', 0)
        top_incby2_step = get('incby2_step', 2)
        top_incby2_late_gate = get('incby2_late_gate', None)
        for i, s in enumerate(music_subs):
            sp = s.params.fields if s.params is not None else {}
            per_subtune_speed_ctr_init.append(
                sp.get('speed_ctr_init', top_speed_ctr_init))
            per_subtune_incby2_step.append(
                sp.get('incby2_step', top_incby2_step) & 0xFF)
            late_gate = sp.get('incby2_late_gate', top_incby2_late_gate)
            per_subtune_incby2_late_gate.append(
                (0xFF if late_gate is None else late_gate) & 0xFF)
            per_subtune_ovseed.append(
                _ovseed_from_init_state(s.init, len(usf.instruments)))
            if 'tick_divider' in sp:
                resetspds[i] = sp['tick_divider']

    # SFX subtunes
    sfx_subs = sorted(
        (s for s in usf.subtunes if isinstance(s, SfxSubtune)),
        key=lambda s: s.id)
    sfx_list = [_soundeffect_from_usf(s, idx)
                for idx, s in enumerate(sfx_subs)]

    # Freq bytes: USF carries the canonical region; per-voice init
    # overlay (when the USF still ships an init block) overrides.
    fb = bytearray(usf.freq_table)
    for v in usf.init.voices:
        i = v.id - 1
        fb[205 + i] = v.dur_field
        fb[208 + i] = v.ctrl
        if v.instr is not None:
            fb[214 + i] = (v.instr.id - 1) & 0xFF
        fb[229 + i] = v.pwm_period
        fb[232 + i] = 0x00 if v.pwm_dir == 'up' else 0xFF
        fb[239 + i] = v.slide_v
    freq_bytes = bytes(fb)

    # Optional state_layout (Human Race).
    state_layout = None
    if usf.state_layout is not None:
        # StatebufLayout/Slot are defined above in this same module
        d = usf.state_layout
        scalars = [StatebufSlot(offset=s['offset'], kind=s['kind'],
                                value=s.get('value', 0),
                                var=s.get('var', ''))
                   for s in d['scalars']]
        per_voice = [StatebufSlot(offset=s['offset'], kind=s['kind'],
                                  value=s.get('value', 0),
                                  var=s.get('var', ''))
                     for s in d['per_voice']]
        state_layout = StatebufLayout(
            n_voices=d['n_voices'], scalars=scalars, per_voice=per_voice)

    ns_offtab_decr_offset = get('ns_offtab_decr_offset', None)
    return _Inputs(
        title=latin1(usf.psid.title),
        author=latin1(usf.psid.author),
        released=latin1(usf.psid.released),
        start_song=usf.psid.start_song,
        arp_interval=get('arp_interval', 12),
        arp_period=get('arp_period', 2),
        arp_phase_invert=get('arp_phase_invert', False),
        linear_pw_or=get('linear_pw_or', 0),
        incby2_step=get('incby2_step', 2),
        incby2_every_frame=get('incby2_every_frame', False),
        incby2_onset=get('incby2_onset', 3),
        suppress_first_notestart=get('suppress_first_notestart', False),
        freeze_on_stop=get('freeze_on_stop', False),
        speed_ctr_init=get('speed_ctr_init', 0),
        first_frame_gate_off=get('first_frame_gate_off', False),
        seed_overlap=get('seed_overlap', True),
        psid_speed=usf.psid.speed,
        frame_ctr_init=get('frame_ctr_init', 0xFF),
        incby2_late_gate=get('incby2_late_gate', None),
        stop_fill=get('stop_fill', None),
        sfx_framectr_ofs=get('sfx_framectr_ofs', 253),
        sfx_state_ofs=get('sfx_state_ofs', None),
        has_sfx=get('has_sfx', False),
        subtunes=subtune_ids,
        models=models, scores=scores, resetspds=resetspds,
        voice_starts=voice_starts, freq_bytes=freq_bytes,
        sfx_list=sfx_list,
        per_subtune_speed_ctr_init=per_subtune_speed_ctr_init,
        per_subtune_incby2_step=per_subtune_incby2_step,
        per_subtune_incby2_late_gate=per_subtune_incby2_late_gate,
        per_subtune_ovseed=per_subtune_ovseed,
        master_vol_subtrahend_voice=get('master_vol_subtrahend_voice', None),
        master_vol_base=get('master_vol_base', 0xA0),
        master_vol_trigger=get('master_vol_trigger', 'inst_change'),
        tie_preserves_slide=get('tie_preserves_slide', False),
        hubidx_wrap_at_patend=get('hubidx_wrap_at_patend', True),
        **({'ns_offtab_decr_offset': ns_offtab_decr_offset}
           if ns_offtab_decr_offset is not None else {}),
        **({'state_layout': state_layout} if state_layout is not None else {}),
    )


def _emit_hubbard85_bytes(usf: UsfFile, usf_dir: str | None) -> bytes:
    """Hubbard '85 dispatch: build `_Inputs` from the USF, then either
    `_hubbard_emit_sid` (music-only) or `_emit_combined_sid` (when the
    USF carries digi subtunes). Returns the PSID bytes."""
    from pipelines.hubbard.note_codec import BitPackCodec
    import tempfile
    codec = BitPackCodec()
    inputs = _inputs_from_usf(usf)

    digi_subs = sorted(
        (s for s in usf.subtunes if isinstance(s, DigiSubtune)),
        key=lambda s: s.id)

    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        if not digi_subs:
            _hubbard_emit_sid(inputs, tmp_path, codec)
        else:
            if usf_dir is None:
                raise ValueError(
                    'USF has digi subtunes; emit_sid needs usf_dir to '
                    'locate sample FLAC sidecars')
            name = usf.params.fields.get('digi_player') if usf.params else None
            if name is None:
                raise ValueError(
                    'USF has digi subtunes but no `digi_player` in params')
            registry = _digi_player_registry()
            if name not in registry:
                raise ValueError(
                    f'unknown digi_player {name!r}; '
                    f'register in `_digi_player_registry`')
            _emit_combined_sid(inputs, usf, digi_subs, registry[name],
                                tmp_path, usf_dir, codec)
        return open(tmp_path, 'rb').read()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
