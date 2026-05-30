"""Shared USF → codegen helpers + the digi region builder.

Most of the build now lives in `usf3_build_from_usf.py` (the
engine-name-blind path). The helpers here — USF instrument → engine
InstrumentModel, USF subtune → Score, USF SFX → SoundEffect, ovseed
reconstruction, and the combined music + digi emitter — are shared
between the v3 build and any future build paths.

The public entry point `build_from_usf` is preserved as a thin
wrapper around `build_from_usf3` for back-compat with callers/docs.
"""

from __future__ import annotations

import os
import struct

from src.usf2 import UsfFile, MusicSubtune, DigiSubtune, SfxSubtune
from pipelines.hubbard.sfx import SoundEffect
from pipelines.hubbard.codegen import _Inputs, _emit_sid, LOAD
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


# ---------------------------------------------------------------------------
# USF → InstrumentModel (the inverse of pipelines/hubbard/chimera/extract/to_usf_v2.
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
# SfxSubtune → engine SoundEffect — the inverse of `_convert_sfx` in
# to_usf_v2.py. Reassembles the 7-byte v1/v2 voice register lists (the
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
# USF → _Inputs helpers (shared with usf3_build_from_usf)
# ---------------------------------------------------------------------------

def _ovseed_from_init_state(init, instr_count: int) -> bytes:
    """Convert a USF `InitState` back into the 18-byte ovseed
    (the inverse of `_init_state_from_ovseed` in
    pipelines/hubbard/five_title_tunes/v2/write_unified_usf.py).
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
        _emit_sid(inputs, tmp_music, codec, load_addr=LOAD)
        size = os.path.getsize(tmp_music) - 124
        music_load = digi_code.dispatcher_base - size
        for _ in range(4):
            _emit_sid(inputs, tmp_music, codec, load_addr=music_load)
            new_size = os.path.getsize(tmp_music) - 124
            new_load = digi_code.dispatcher_base - new_size
            if new_load == music_load:
                break
            music_load = new_load

    digi_region, digi_base, play_addr = _build_digi_region(
        usf, digi_subs, digi_code, usf_dir, music_load=music_load)

    _emit_sid(inputs, tmp_music, codec, load_addr=music_load)
    music_blob = open(tmp_music, 'rb').read()
    os.unlink(tmp_music)
    # _emit_sid wrote a PSID. Strip its 124-byte header.
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
# Public API
# ---------------------------------------------------------------------------

def build_from_usf(usf_path: str, out_path: str, codec=None) -> str:
    """Read `usf_path` + its sample sidecars, produce a SID at `out_path`.

    Thin wrapper around `build_from_usf3` — kept as the public entry
    point for back-compat with callers and docs. All Hubbard '85
    .usf files are USF v3 (self-contained, engine-name-blind); v2
    files would have to be re-extracted via the v3 extract path.
    """
    from pipelines.hubbard.usf3_build_from_usf import build_from_usf3
    return build_from_usf3(usf_path, out_path, codec)
