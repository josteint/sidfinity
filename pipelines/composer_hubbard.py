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



# `_Inputs` dataclass + `_inputs_from_config` moved to composer.py
# in Phase 8.20. Re-export for legacy importers (5TT unified writer).
from pipelines.composer import _Inputs, _inputs_from_config  # noqa: F401


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
# USF → domain converters + `_inputs_from_usf` + `_ovseed_from_init_state`
# moved to composer.py in Phase 8.20.

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


# `_inputs_from_usf` moved to composer.py in Phase 8.20.
from pipelines.composer import _inputs_from_usf  # noqa: F401


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
