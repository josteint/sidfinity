"""composer/hubbard85 — the lifted Hubbard '85 parametric core.

Status: Phase 8.1 — moved here from `pipelines/universal_codegen.py`
(which is being retired). The composer's hubbard85 dispatch calls
`_emit_hubbard85_bytes` from this module. Future phases (8.2+)
decompose the ENGINE asm template + helpers into composer-style
feature emitters parametric on EngineModel features; as that
happens, this module shrinks.

The Hubbard '85 codegen handles:
  - 11 Hubbard '85 engines (Commando family + Human Race + Hunter
    Patrol + Battle of Britain + Confuzion + Devils Galop + Monty +
    Action Biker + Thing on a Spring + One Man and his Droid + Chimera)
  - SFX sub-engine (16 sound-effect records)
  - Digi region (Chimera 1-bit wavetoggle)
  - 5_Title_Tunes compound build (5 packed sub-engines + dispatcher)
  - Full modulation pipeline: vibrato, PWM linear/bidir, multi-step
    arpeggio (incl. off-table via state_layout), freq-hi slide,
    odd-frame slide, drum-slide, master-vol fade, hard-restart writes,
    drum-prio gate, no-release flag, tie + drum_trig per-note effects.
"""

from __future__ import annotations

import os
import struct
import subprocess
import sys as _sys
from dataclasses import dataclass, field
from typing import Optional as _Optional

from src.usf import UsfFile, MusicSubtune, SfxSubtune, DigiSubtune

LOAD = 0x1000

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sys.path.insert(0, _ROOT)
_sys.path.insert(0, os.path.join(_ROOT, 'src'))
_sys.path.insert(0, os.path.join(_ROOT, 'tools', 'py65_lib'))

_XA = os.path.join(_ROOT, 'tools', 'xa65', 'xa', 'xa')
XA = _XA   # legacy name; some lifted code still references it

from pipelines.hubbard.inst_generalize import decode_all  # noqa: E402

# State-layout mirror moved to composer.py in Phase 8.2. composer.py
# owns the feature emitters; composer_hubbard imports them back here
# so the lifted ENGINE template still substitutes the build_statebuf
# routine via `%%BUILD_STATEBUF%%`. The dataclasses live in
# `engine_model.py` as `StateLayoutMirror`/`StateSlot`, aliased
# `StatebufLayout`/`StatebufSlot` for the lifted code's legacy naming.
from pipelines.composer import (
    COMMANDO_STATEBUF_LAYOUT, _emit_build_statebuf, _statebuf_init_bytes,
)
from pipelines.engine_model import StatebufLayout, StatebufSlot


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


# The ENGINE asm template + the data section + the pattern-pool helper
# all live in composer.py now (Phase 8.16 moved the template; Phase 8.17
# moved `_emit_data` + `_pattern_pool` and replaced the template-driven
# substitution path with direct chunk concatenation via
# `_compose_hubbard_engine_asm`). This module is now just the
# orchestrator wrapping that composer call with the outer text-replace
# passes, the xa65 invocation, and PSID header packaging.


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------



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
    # Composer-native asm composition. `_compose_hubbard_engine_asm`
    # threads every per-engine knob (load_addr, sfx_framectr_ofs,
    # arp_phase_invert, ns_offtab_decr_offset, sfx_state_ofs,
    # incby2_late_gate, has_per_subtune_ovseed, has_master_vol_fade,
    # uses_per_subtune_dispatch) into the chunk emitters directly.
    # Only the codec.note_asm passes remain as outer text-replaces —
    # they target text the codec emits (the master_vol fade's
    # peek-ahead + $D418 writes, and tie_preserves_slide's drum-trig
    # clear positioning).
    from pipelines.composer import (
        _compose_hubbard_engine_asm,
        _pattern_pool,
    )
    pat_order, pat_slot = _pattern_pool(inputs.scores)
    pat_bytes, codec_extra = codec.encode(pat_order)
    asm = _compose_hubbard_engine_asm(
        inputs, codec, pat_slot, pat_bytes, codec_extra,
        load_addr=load_addr)

    from pipelines.engine_model import FadeProgressive
    from pipelines.composer import (
        _emit_clear_drumtrig,
        _emit_master_vol_fade,
    )

    # Master-volume fade — VOL_PROGRESS_INIT was pushed into init
    # (Phase 8.19); the remaining three sentinels live in the codec's
    # note_asm. The init-side substitution becomes a no-op (no
    # `; %%VOL_PROGRESS_INIT%%` text remains in the engine body), but
    # the dict still has it harmlessly.
    fade = (
        FadeProgressive(
            subtrahend_voice_idx=inputs.master_vol_subtrahend_voice,
            base=inputs.master_vol_base,
            trigger=inputs.master_vol_trigger,
        )
        if inputs.master_vol_subtrahend_voice is not None else None)
    for sentinel, fragment in _emit_master_vol_fade(fade).items():
        asm = asm.replace(sentinel, fragment)

    # tie_preserves_slide — pair of substitutions positioning the
    # `sta v_drumtrig,x` clear (lives in the codec's note_asm).
    for sentinel, fragment in _emit_clear_drumtrig(
            inputs.tie_preserves_slide).items():
        asm = asm.replace(sentinel, fragment)

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

    from pipelines.composer import _build_digi_region
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
            from pipelines.composer import _digi_player_registry
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
