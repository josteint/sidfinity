"""USF v2 → SID codegen.

The *read* side of the USF-only pipeline. Reads `<basename>.usf` and
the sibling `<basename>.sampleN.flac` files; does NOT peek at the
original SID. Produces a SID functionally equivalent to the original
(verified via verify_all: py65 frame-exact for music, writelog
cycle-strict for digi).

Per-engine constants (instrument-table address, freq-table addresses,
the 320-byte freq-table region) live in
`pipelines/hubbard/engine_constants.py` — these are engine *code*
properties, the same across all tunes of one engine. Tune data is
entirely in the USF + sidecar FLACs.
"""

from __future__ import annotations

import os
import struct

from src.usf2 import (
    UsfFile, MusicSubtune, DigiSubtune, parse_file, validate,
)
from pipelines.hubbard.codegen import _Inputs, _emit_sid, LOAD
from pipelines.hubbard.engine_constants import ENGINE_CONSTANTS, DigiCode
from pipelines.hubbard.flac_io import read_sample
from pipelines.hubbard.digi_pack import pack_digi
from pipelines.hubbard.inst_generalize import (
    InstrumentModel, ArpSpec, VibratoSpec, PwmSpec,
)
from pipelines.hubbard.types import (
    Score, Voice, Note, Instrument as HubInstrument,
)


# ---------------------------------------------------------------------------
# USF → InstrumentModel (the inverse of pipelines/chimera/extract/to_usf_v2.
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

    Inverse of `to_usf_v2._row_from_note`:
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
# Freq bytes: 320 bytes that go at freqtab. First 192 = standard PAL
# musical freq table (engine constant). Bytes at +205, +208, +214,
# +229, +232, +239 come from USF init. Remaining engine state may also
# come from the per-engine constant (scratch values etc.) — we let the
# engine constants supply EVERYTHING, then overlay the init values.
# ---------------------------------------------------------------------------

def _freq_bytes_from_usf(usf: UsfFile, engine_const) -> bytes:
    fb = bytearray(engine_const.freq_bytes)
    for v in usf.init.voices:
        i = v.id - 1
        fb[205 + i] = v.dur_field
        fb[208 + i] = v.ctrl
        if v.instr is not None:
            fb[214 + i] = (v.instr.id - 1) & 0xFF
        fb[229 + i] = v.pwm_period
        fb[232 + i] = 0x00 if v.pwm_dir == 'up' else 0xFF
        fb[239 + i] = v.slide_v
    return bytes(fb)


# ---------------------------------------------------------------------------
# USF → _Inputs
# ---------------------------------------------------------------------------

def _inputs_from_usf(usf: UsfFile) -> _Inputs:
    """Build codegen `_Inputs` purely from a parsed UsfFile + the
    per-engine constants. No binary or sid_path access."""
    if usf.engine not in ENGINE_CONSTANTS:
        raise ValueError(
            f'no engine constants registered for engine {usf.engine!r}; '
            f'add to pipelines/hubbard/engine_constants.py')
    ec = ENGINE_CONSTANTS[usf.engine]

    # PSID metadata
    def latin1(s: str) -> bytes:
        return s.encode('latin-1', errors='replace')

    # Engine equates / asm flags
    p = usf.params.fields

    def get(key: str, default):
        return p.get(key, default)

    # Instruments — convert USF → InstrumentModel
    models = [_model_from_usf_instrument(u, get('vib_onset', 6))
              for u in usf.instruments]

    # Music subtunes only (digi handled elsewhere for now)
    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    music_subs.sort(key=lambda s: s.id)
    subtune_ids = tuple(s.id for s in music_subs)
    scores = [_score_from_subtune(s) for s in music_subs]
    resetspds = [s.tempo - 1 for s in music_subs]
    voice_starts = [ec.voice_starts.get(s.id, 2) for s in music_subs]

    freq_bytes = _freq_bytes_from_usf(usf, ec)

    return _Inputs(
        title=latin1(usf.psid.title),
        author=latin1(usf.psid.author),
        released=latin1(usf.psid.released),
        start_song=usf.psid.start_song,
        arp_interval=get('arp_interval', 12),
        arp_period=get('arp_period', 2),
        linear_pw_or=get('linear_pw_or', 0),
        incby2_step=get('incby2_step', 2),
        incby2_every_frame=get('incby2_every_frame', False),
        incby2_onset=get('incby2_onset', 3),
        suppress_first_notestart=get('suppress_first_notestart', False),
        freeze_on_stop=get('freeze_on_stop', False),
        speed_ctr_init=get('speed_ctr_init', 0),
        first_frame_gate_off=get('first_frame_gate_off', False),
        stop_fill=get('stop_fill', None),
        sfx_framectr_ofs=ec.sfx_framectr_ofs,
        sfx_state_ofs=ec.sfx_state_ofs,
        has_sfx=ec.has_sfx,
        subtunes=subtune_ids,
        models=models, scores=scores, resetspds=resetspds,
        voice_starts=voice_starts, freq_bytes=freq_bytes,
        sfx_list=[],                # SFX from USF: TBD (not Chimera)
    )


# ---------------------------------------------------------------------------
# Combined music + digi build (for engines with digi subtunes, e.g. Chimera)
# ---------------------------------------------------------------------------

def _build_digi_region(usf: UsfFile, digi_subs: list[DigiSubtune],
                       digi_code: DigiCode, usf_dir: str) -> tuple[bytes, int]:
    """Build the bytes of the digi region — dispatcher + tables +
    samples + player — placed at their fixed engine addresses.

    Returns (region_bytes, region_base). The region is contiguous from
    `region_base` to `region_base + len(region_bytes)` and covers the
    dispatcher, the bank table, the validation table, the
    `keep_screen`/`pace` slots, all sample byte streams, and the digi
    player. Per-subtune `pace` and `bank` slots are filled from each
    Sample's `extras`.
    """
    # The region spans dispatcher_base..(end of digi player). Build a
    # bytearray that long, write each segment at its address-relative
    # offset.
    base = digi_code.dispatcher_base                       # e.g. $9F80
    end  = digi_code.player_base + len(digi_code.player)   # one past last byte

    # The dispatcher's `jsr $C200` / `jsr $C206` originally targeted the
    # in-original music engine. We retarget to OUR music (built by
    # _emit_sid at LOAD).
    dispatcher = bytearray(digi_code.dispatcher)
    dispatcher[digi_code.music_init_patch_off:
               digi_code.music_init_patch_off + 3] = bytes(
        [0x20, LOAD & 0xFF, (LOAD >> 8) & 0xFF])
    dispatcher[digi_code.music_play_patch_off:
               digi_code.music_play_patch_off + 3] = bytes(
        [0x20, (LOAD + 3) & 0xFF, ((LOAD + 3) >> 8) & 0xFF])

    region = bytearray(end - base)
    region[0:len(dispatcher)] = dispatcher
    # Place the digi player at its base.
    player_off = digi_code.player_base - base
    region[player_off:player_off + len(digi_code.player)] = digi_code.player

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

    # Per-subtune dispatcher tables at $9FE2 (pace) and $9FE4 (bank-hi).
    # The dispatcher does `lda $9FE2,X` and `lda $9FE4,X` where X is the
    # SFX index (subtune - n_music_subtunes).
    pace_base = digi_code.dispatcher_base + 0x62             # $9FE2
    bank_base = digi_code.dispatcher_base + 0x64             # $9FE4
    for s in samples:
        region[pace_base - base + s['st_idx']] = s['pace']
        region[bank_base - base + s['st_idx']] = s['bank']

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

    return bytes(region), base


def _emit_combined_sid(inputs: _Inputs, usf: UsfFile, digi_subs: list,
                       digi_code: DigiCode, out_path: str, usf_dir: str,
                       codec) -> str:
    """Emit a combined RSID containing music engine + digi engine +
    samples. Music at LOAD ($1000 by default), digi at its engine-fixed
    addresses ($9F80 dispatcher + $C000 player for Chimera). Inline-load
    encoded in the binary so the file can be RSID-style with two
    segments and a zero gap.
    """
    # Build the music binary the same way _emit_sid would, but then
    # extract just the data (no PSID header — we build a different one).
    tmp_music = out_path + '.music.tmp'
    _emit_sid(inputs, tmp_music, codec)
    music_blob = open(tmp_music, 'rb').read()
    os.unlink(tmp_music)
    # _emit_sid wrote a PSID. Strip its 124-byte header.
    music_body = music_blob[124:]                  # music bytes at $LOAD

    digi_region, digi_base = _build_digi_region(
        usf, digi_subs, digi_code, usf_dir)

    music_end = LOAD + len(music_body)
    if music_end > digi_base:
        raise ValueError(
            f'music engine at ${LOAD:04X}-${music_end - 1:04X} overlaps '
            f'the digi region starting at ${digi_base:04X}')
    gap = bytes(digi_base - music_end)
    binary = music_body + gap + digi_region

    # RSID v2 header: load=$0000 (inline), init=dispatcher_base, play=0
    n_music = len(inputs.subtunes)
    songs = n_music + len(digi_subs)
    start_song = min(max(inputs.start_song, 1), songs)

    h = bytearray(b'RSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', 0x0000)             # load = inline-encoded
    h += struct.pack('>H', digi_code.dispatcher_base)
    h += struct.pack('>H', 0x0000)             # play = IRQ-driven
    h += struct.pack('>H', songs)
    h += struct.pack('>H', start_song)
    h += struct.pack('>I', 0)
    for s in (inputs.title, inputs.author, inputs.released):
        h += s[:32].ljust(32, b'\x00')
    h += struct.pack('>H', 0x0014)             # flags (PAL + 6581)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124, len(h)

    with open(out_path, 'wb') as f:
        f.write(bytes(h))
        f.write(struct.pack('<H', LOAD))       # inline load addr
        f.write(binary)
    return out_path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_from_usf(usf_path: str, out_path: str, codec=None) -> str:
    """Read `usf_path` + its sample sidecars, produce a SID at `out_path`.
    No access to the original SID — this is the principled path. Routes
    to the music-only or combined music+digi build based on whether the
    USF has any digi subtunes."""
    from pipelines.hubbard.note_codec import BitPackCodec
    if codec is None:
        codec = BitPackCodec()
    usf = parse_file(usf_path)
    usf_dir = os.path.dirname(os.path.abspath(usf_path))
    validate(usf, usf_dir=usf_dir)
    inputs = _inputs_from_usf(usf)

    digi_subs = [s for s in usf.subtunes if isinstance(s, DigiSubtune)]
    digi_subs.sort(key=lambda s: s.id)
    if not digi_subs:
        return _emit_sid(inputs, out_path, codec)

    ec = ENGINE_CONSTANTS[usf.engine]
    if ec.digi is None:
        raise ValueError(
            f'engine {usf.engine!r} has no DigiCode but USF declares '
            f'digi subtunes')
    return _emit_combined_sid(inputs, usf, digi_subs, ec.digi,
                              out_path, usf_dir, codec)
