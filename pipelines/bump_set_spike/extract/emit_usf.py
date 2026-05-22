"""Generate USF v3 BumpSetSpike on the Run data as a Lean file.

Pipeline structure identical to the Commando emit_usf; only the SID source
path, freq table base, and Lean output paths differ.

Discovered freq_table_addr for BumpSetSpike: $8400 (via src/sidxray/discover.py).
"""

from __future__ import annotations

import logging
import os
import sys

from .engine_model import extract
from .types import ExtractedSong, Instrument, Note

logger = logging.getLogger(__name__)


def hex_byte(n: int) -> str:
    return f"⟨{n & 0xFF}, by omega⟩"


def gen_freq_table(T: list[int]) -> str:
    """Emit 128 entries: standard PAL 0-95, plus engine-extracted 96-127.

    Note: Commando's gen_commando_v3.py zeros pitch 104 because Commando
    uses freq-table slot 104 as a hidden register (dynamic ctrl byte
    alias updated each frame via engineQuirks.dynamicFreqEntries).
    BumpSetSpike does NOT do this — its pitch 104 is a real freq lookup
    ($4141 in the original SID). We keep the real value here.
    """
    pairs = []
    for i in range(128):
        if i < len(T):
            flo = T[i] & 0xFF
            fhi = (T[i] >> 8) & 0xFF
        else:
            flo = 0
            fhi = 0
        pairs.append(f"({hex_byte(flo)}, {hex_byte(fhi)})")
    return "[" + ", ".join(pairs) + "]"


def gen_instrument(idx: int, inst: Instrument) -> str:
    pw = inst.pwm
    bit0 = inst.has_bit0
    sky = inst.has_skydive
    arp_off = inst.arp_offset
    vib = inst.vibrato_scale
    waveform = inst.waveform.steps
    loop = inst.waveform.loop
    init_pw = pw.init_pw
    init_lo = init_pw & 0xFF
    init_hi = (init_pw >> 8) & 0x0F

    if pw.speed == 0:
        pwmod = 'none'
    elif pw.mode == 'linear':
        pwmod = (
            f"some {{ mode := .linear {hex_byte(pw.speed)}, "
            f"stepEvery := 1, startDelay := 0 }}"
        )
    else:
        pwmod = (
            f"some {{ mode := .bidirectional {hex_byte(pw.speed)} "
            f"{hex_byte(pw.min_hi)} {hex_byte(pw.max_hi)}, "
            f"stepEvery := 1, startDelay := 0 }}"
        )

    if vib == 0:
        vibspec = 'none'
    else:
        # Bump Set Spike's vib byte (instrument byte 5) is packed:
        #   bits 6:3 = frame_limit  → LFO period = 2 * frame_limit (counter walks 0..limit..0)
        #   bits 2:0 = shift count  → delta = (freq[note] - freq[note-1]) >> shift
        # See disassembly $B1D4..$B1E0. Earlier (Monty/Commando) extracts used
        # `vib + 1` as semitoneShift directly, which is correct only when the
        # data byte is a raw shift count — for Bump Set Spike that produces
        # a 28-bit shift → delta=0 → vibrato silent.
        frame_limit = (vib >> 3) & 0x0F
        shift = vib & 0x07
        period_frames = 2 * frame_limit if frame_limit > 0 else 8
        vibspec = (
            f"some {{ shape := .triangle, periodFrames := {period_frames}, "
            f"semitoneShift := {shift}, onsetFrames := 6, "
            f"rampUpFrames := 0, unipolar := true }}"
        )

    if bit0:
        slidespec = (
            "some { kind := .monotonic (-1), stepEvery := 1, "
            "startDelay := 9, stopAtZero := true }"
        )
    else:
        slidespec = 'none'

    if arp_off > 0:
        arpspec = (
            f"some {{ intervals := [0, {arp_off}], stepEvery := 1, "
            f"phaseSource := .global, startDelay := 0 }}"
        )
    else:
        arpspec = 'none'

    eff_parts = []
    if vib > 0:
        eff_parts.append('.vibrato')
    eff_parts.append('.pwMod')
    if bit0:
        eff_parts.append('.freqSlide')
    if arp_off > 0:
        eff_parts.append('.arpeggio')
    eff_parts.append('.gateCheck')
    eff_order = '[' + ', '.join(eff_parts) + ']'

    waveform_lit = '[' + ', '.join(hex_byte(b) for b in waveform) + ']'

    return f"""def mv3I{idx} : USFInstrument := {{
  initCtrl := {hex_byte(waveform[0])}
  initPwLo := {hex_byte(init_lo)}
  initPwHi := {hex_byte(init_hi)}
  ad := {hex_byte(inst.envelope.ad)}
  sr := {hex_byte(inst.envelope.sr)}
  initFreqMod := .normal
  waveformProgram := {waveform_lit}
  waveLoop := {loop}
  waveStepEvery := 1
  pwMod := {pwmod}
  vibrato := {vibspec}
  freqSlide := {slidespec}
  arpeggio := {arpspec}
  effectOrder := {eff_order}
  release := {{ framesBeforeEnd := 3, zeroAdsr := true, noRelease := false }}
  filterEnabled := false
}}"""


def gen_note(note: Note, tempo: int) -> str:
    pitch = note.pitch
    dur = note.duration
    inst_raw = note.instrument
    # das_model: bits 6 AND 7 are flags. Preserve them - they're needed at
    # runtime for hub_off counter (+1 for bit6 legato, +2 for bit7 tie, +3
    # for full new note). The actual instrument index is bits 0-5.
    # Pattern byte stores the RAW value; codegen masks for table indexing.
    # no_release is encoded in bit 7 of drum_trig (das_model_gen.py:197).
    # Hubbard's no_release flag suppresses HR at the end of THIS note; the
    # next note inherits the still-on gate so the SID envelope doesn't
    # retrigger across the boundary. We piggyback the flag on bit 5 of the
    # raw instrument byte (bits 0-3 are the index, 6/7 are the legato/tie
    # flags). Codegen masks it out for table lookup and uses it to skip HR.
    no_release = bool(note.drum_trig & 0x80)
    inst = (inst_raw & 0xFF) | (0x20 if no_release else 0)
    tie = note.tie
    # Frame count = dur * tempo (frames per tick). Tempo varies per subtune
    # in Hubbard games — comes from speed_table[subtune]+1.
    frames = dur * tempo
    # Portamento byte: drum_trig has porta speed << 1 in bits 1-6 and
    # direction in bit 0; bit 7 was the no_release flag (extracted above).
    # Strip bit 7, leave the porta payload.
    porta = note.drum_trig & 0x7F
    if tie:
        kind = '.tie'
    elif pitch == 104:
        kind = '.percussion .dynamicCtrl'
    elif pitch < 96:
        kind = f'.pitched {hex_byte(pitch)}'
    else:
        # Other extended pitches — for now treat as dynamicCtrl too
        # (Hubbard's pitch 100, 116 etc.)
        kind = '.percussion .dynamicCtrl'
    return (
        f"{{ kind := {kind}, durationFrames := {frames}, "
        f"instrument := {inst}, porta := {porta} }}"
    )


def gen_pattern(idx: int, notes: list[Note], tempo: int) -> str:
    note_strs = [gen_note(n, tempo) for n in notes]
    return f"def mv3P{idx} : USFPattern := {{ notes := [{', '.join(note_strs)}] }}"


BUMP_SET_SPIKE_SID = '/home/jtr/sidfinity/data/C64Music/MUSICIANS/H/Hubbard_Rob/Bump_Set_Spike.sid'
# Freq table base, verified by reading the binary: lo[0]=$16, hi[0]=$01
# (note 0 = $0116). Table is interleaved (lo, hi) over 96 semitones at $B3FF.
BUMP_SET_SPIKE_FT_BASE = 0xB3FF


def main(argv: list[str] | None = None) -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if argv is None:
        argv = sys.argv[1:]

    # Subtune list. Default = subtune 0 only (the title music PSID
    # start_song points at). Pass comma-separated indices to override.
    subtune_indices: list[int] = [0]
    if argv:
        subtune_indices = [int(x) for x in argv[0].split(',')]

    # Extract per subtune from BumpSetSpike (not Commando). Discovery-derived
    # ft_base override. PWM bounds are HARDCODED in Hubbard's player
    # (cmp #$08 / cmp #$0E in pulsework — see ACME disassembly), not
    # per-instrument. The earlier $0B observation was just the warm-up
    # phase before V2 stepped all the way down to $08 (around frame 51).
    extracts: list[ExtractedSong] = [
        extract(
            subtune=s,
            sid_path=BUMP_SET_SPIKE_SID,
            ft_base=BUMP_SET_SPIKE_FT_BASE,
            default_pw_min=0x08,
            default_pw_max=0x0E,
        )
        for s in subtune_indices
    ]
    first = extracts[0]
    T = first.freq_table
    instruments = first.instruments

    out = [
        "-- Auto-generated USF v3 BumpSetSpike on the Run data",
        f"-- Subtunes: {subtune_indices} (0-indexed; PSID subtunes "
        f"{[s + 1 for s in subtune_indices]})",
        "import BumpSetSpike.USF",
        "",
    ]

    out.append(
        f"def bump_set_spikeV3FreqTable : USFFreqTable := "
        f"{{ entries := {gen_freq_table(T)} }}"
    )
    out.append("")

    for i, inst in enumerate(instruments):
        out.append(gen_instrument(i, inst))
        out.append("")

    # Collect patterns across all subtunes. Each pattern's durationFrames is
    # pre-multiplied by ITS subtune's tempo, so a pattern shared between two
    # subtunes at different tempos would need different durations — we
    # error if that happens. For Commando subtunes 0/1/2 there's no overlap
    # (they each use disjoint pattern ranges).
    all_pats: dict[int, tuple[list[Note], int]] = {}  # pat_idx -> (notes, tempo)
    for es in extracts:
        tempo = es.score.tempo
        for v in es.score.voices:
            for pat_idx, pat_notes in v.patterns.items():
                if pat_idx in all_pats:
                    _existing_notes, existing_tempo = all_pats[pat_idx]
                    if existing_tempo != tempo:
                        raise ValueError(
                            f"pattern {pat_idx} shared between subtunes with "
                            f"different tempos ({existing_tempo} vs {tempo}); "
                            f"need tick-based durations to handle this"
                        )
                else:
                    all_pats[pat_idx] = (pat_notes, tempo)

    for idx in sorted(all_pats.keys()):
        notes, tempo = all_pats[idx]
        out.append(gen_pattern(idx, notes, tempo))
        out.append("")

    # Per-subtune voices (orderlists). Each subtune contributes 3 voices.
    voice_defs: list[str] = []
    voice_global_idx = 0
    subtune_voices: list[tuple[int, int]] = []  # (start_idx, count) per subtune
    for es in extracts:
        start = voice_global_idx
        for v in es.score.voices:
            ol = '[' + ', '.join(str(p) for p in v.orderlist) + ']'
            loop_pt = v.loop
            # rh_decompile uses -1 to mean "no loop / song stops"; USF schema
            # represents that as `none`.
            loop_str = (
                f'some {loop_pt}' if loop_pt is not None and loop_pt >= 0
                else 'none'
            )
            voice_defs.append(
                f"def mv3V{voice_global_idx} : USFVoice := "
                f"{{ orderlist := {ol}, loopPoint := {loop_str} }}"
            )
            voice_global_idx += 1
        subtune_voices.append((start, voice_global_idx - start))
    out.extend(voice_defs)
    out.append("")

    # Subtune defs: each USFSubtune wraps 3 voices + tempo.
    subtune_defs: list[str] = []
    for si, ((start, count), es) in enumerate(zip(subtune_voices, extracts)):
        v_refs = ', '.join(f'mv3V{i}' for i in range(start, start + count))
        subtune_defs.append(
            f"def mv3S{si} : USFSubtune := "
            f"{{ voices := [{v_refs}], tempo := {es.score.tempo} }}"
        )
    out.extend(subtune_defs)
    out.append("")

    # Pattern list (ordered by index, with empty placeholders for missing indices)
    max_pat = max(all_pats.keys()) + 1
    pat_refs: list[str] = []
    for i in range(max_pat):
        if i in all_pats:
            pat_refs.append(f'mv3P{i}')
        else:
            pat_refs.append('{ notes := [] }')

    # Final song
    inst_refs = ', '.join(f'mv3I{i}' for i in range(len(instruments)))
    subtune_refs = ', '.join(f'mv3S{i}' for i in range(len(extracts)))
    pat_list = ', '.join(pat_refs)

    # Engine quirks for BumpSetSpike. Same Hubbard engine as Commando, so:
    #   - voiceScratch / noteLoadOps / patternEndOps stay: these encode
    #     Hubbard's variable-length pattern decoding (hub_off counter
    #     advances 1/2/3 bytes per note based on flags). Removing them
    #     breaks pattern-byte advancement on ALL Hubbard SIDs.
    #   - dynamicFreqEntries DROPPED: these are Commando-specific
    #     (use freq-table slots 98..107 as hidden registers for
    #     per-voice state). BumpSetSpike doesn't do this; keeping them would
    #     overwrite BumpSetSpike's real freq value at slot 104 ($4141) with
    #     ctrl bytes every frame.
    quirks = """{
    preserveNoteFlags := true
    voiceScratch := [
      { name := "hub_off", initial := ⟨0, by omega⟩ },
      { name := "seq_idx", initial := ⟨0, by omega⟩ }
    ]
    noteLoadOps := [
      .addByFlag 0 [
        (⟨0x40, by omega⟩, ⟨0x40, by omega⟩, ⟨1, by omega⟩),
        (⟨0x80, by omega⟩, ⟨0x80, by omega⟩, ⟨2, by omega⟩),
        (⟨0x00, by omega⟩, ⟨0x00, by omega⟩, ⟨3, by omega⟩)
      ],
      .resetIfNextEnds 0,
      .incIfNextEnds   1 ⟨1, by omega⟩
    ]
    patternEndOps := [
      .reset 0,
      .increment 1 ⟨1, by omega⟩
    ]
    dynamicFreqEntries := []
  }"""

    out.append(f"""def bump_set_spikeV3 : USFSong := {{
  freqTable := bump_set_spikeV3FreqTable
  instruments := [{inst_refs}]
  patterns := [{pat_list}]
  subtunes := [{subtune_refs}]
  voiceOrder := [⟨2, by omega⟩, ⟨1, by omega⟩, ⟨0, by omega⟩]
  filter := none
  playRate := .vbi
  engineQuirks := {quirks}
  title := "BumpSetSpike on the Run"
  author := "Rob Hubbard"
  released := "1985 Gremlin Graphics"
}}""")

    # Output path is repo-root-relative, computed from this file's location.
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..')
    )
    out_path = os.path.join(
        repo_root, 'pipelines/bump_set_spike/codegen/BumpSetSpike/SongData.lean'
    )
    with open(out_path, 'w') as f:
        f.write('\n'.join(out) + '\n')

    logger.info(
        "Wrote %d instruments, %d patterns, %d voices to %s",
        len(instruments), len(all_pats), len(first.score.voices), out_path,
    )


if __name__ == '__main__':
    main()
