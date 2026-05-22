"""Generate USF v3 Commando data as a Lean file.

Reads the Hubbard SID binary via ``engine_model.extract``, then emits a Lean
source file (``Commando/SongData.lean``) that the Lean codegen consumes to
produce ``commando.sid``.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional

from .engine_model import extract
from pipelines.hubbard.types import ExtractedSong, Instrument, Note

logger = logging.getLogger(__name__)


def hex_byte(n: int) -> str:
    return f"⟨{n & 0xFF}, by omega⟩"


def gen_freq_table(T: list[int]) -> str:
    """Emit 128 entries: standard PAL 0-95, plus engine-extracted 96-127.
    Pitch 104 is special-cased in player (dynamic ctrl byte alias).
    """
    pairs: list[str] = []
    for i in range(128):
        if i < len(T):
            flo = T[i] & 0xFF
            fhi = (T[i] >> 8) & 0xFF
        else:
            flo = 0
            fhi = 0
        # Zero out pitch 104 (decompiler marks it as percussion .dynamicCtrl)
        if i == 104:
            flo = 0
            fhi = 0
        pairs.append(f"({hex_byte(flo)}, {hex_byte(fhi)})")
    return "[" + ", ".join(pairs) + "]"


def gen_instrument(idx: int, inst: Instrument) -> str:
    pw = inst.pwm
    bit0 = inst.has_bit0
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
        vibspec = (
            f"some {{ shape := .triangle, periodFrames := 8, "
            f"semitoneShift := {vib + 1}, onsetFrames := 6, "
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

    eff_parts: list[str] = []
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

    return f"""def cv3I{idx} : USFInstrument := {{
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
    # no_release is encoded in bit 7 of drum_trig (engine_model.py).
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
    return f"def cv3P{idx} : USFPattern := {{ notes := [{', '.join(note_strs)}] }}"


def main(argv: Optional[list[str]] = None) -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if argv is None:
        argv = sys.argv[1:]

    # Subtune list. Default = 3 music subtunes (game, title, intro). Pass
    # comma-separated indices to override, e.g. `emit_usf.py 0,1,2`.
    subtune_indices: list[int] = [0, 1, 2]
    if argv:
        subtune_indices = [int(x) for x in argv[0].split(',')]

    # Extract per subtune. The first subtune supplies the shared freq table
    # and instruments (which are the same across all Hubbard subtunes that
    # share his player engine).
    extracts: list[ExtractedSong] = [extract(subtune=s) for s in subtune_indices]
    song = extracts[0]
    T = song.freq_table
    instruments = song.instruments

    out: list[str] = [
        "-- Auto-generated USF v3 Commando data",
        f"-- Subtunes: {subtune_indices} (0-indexed; PSID subtunes "
        f"{[s + 1 for s in subtune_indices]})",
        "import Commando.USF",
        "",
    ]

    out.append(f"def commandoV3FreqTable : USFFreqTable := {{ entries := {gen_freq_table(T)} }}")
    out.append("")

    for i, inst in enumerate(instruments):
        out.append(gen_instrument(i, inst))
        out.append("")

    # Collect patterns across all subtunes. Each pattern's durationFrames is
    # pre-multiplied by ITS subtune's tempo, so a pattern shared between two
    # subtunes at different tempos would need different durations — we
    # error if that happens. For Commando subtunes 0/1/2 there's no overlap
    # (they each use disjoint pattern ranges).
    all_pats: dict[int, tuple[list[Note], int]] = {}
    for s in extracts:
        tempo = s.score.tempo
        for v in s.score.voices:
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
    for si, s in enumerate(extracts):
        start = voice_global_idx
        for v in s.score.voices:
            ol = '[' + ', '.join(str(p) for p in v.orderlist) + ']'
            loop_pt = v.loop
            # rh_decompile uses -1 to mean "no loop / song stops"; USF schema
            # represents that as `none`.
            loop_str = (
                f'some {loop_pt}' if loop_pt is not None and loop_pt >= 0
                else 'none'
            )
            voice_defs.append(
                f"def cv3V{voice_global_idx} : USFVoice := {{ orderlist := {ol}, loopPoint := {loop_str} }}"
            )
            voice_global_idx += 1
        subtune_voices.append((start, voice_global_idx - start))
    out.extend(voice_defs)
    out.append("")

    # Subtune defs: each USFSubtune wraps 3 voices + tempo.
    subtune_defs: list[str] = []
    for si, ((start, count), s) in enumerate(zip(subtune_voices, extracts)):
        v_refs = ', '.join(f'cv3V{i}' for i in range(start, start + count))
        subtune_defs.append(
            f"def cv3S{si} : USFSubtune := {{ voices := [{v_refs}], tempo := {s.score.tempo} }}"
        )
    out.extend(subtune_defs)
    out.append("")

    # Pattern list (ordered by index, with empty placeholders for missing indices)
    if not all_pats:
        raise ValueError("no patterns extracted — cannot emit USF song data")
    max_pat = max(all_pats.keys()) + 1
    pat_refs: list[str] = []
    for i in range(max_pat):
        if i in all_pats:
            pat_refs.append(f'cv3P{i}')
        else:
            pat_refs.append('{ notes := [] }')

    # Final song
    inst_refs = ', '.join(f'cv3I{i}' for i in range(len(instruments)))
    subtune_refs = ', '.join(f'cv3S{i}' for i in range(len(extracts)))
    pat_list = ', '.join(pat_refs)

    # Engine quirks for Commando (Hubbard player). Encoded as DATA so the
    # universal codegen can emit code mechanically. See docs/usf_v3_engine_quirks.md.
    quirks = """{
    preserveNoteFlags := true
    voiceScratch := [
      { name := "hub_off", initial := ⟨0, by omega⟩ },   -- slot 0
      { name := "seq_idx", initial := ⟨0, by omega⟩ }    -- slot 1
    ]
    noteLoadOps := [
      -- hub_off (slot 0): bit 6 -> +1, bit 7 -> +2, neither -> +3
      .addByFlag 0 [
        (⟨0x40, by omega⟩, ⟨0x40, by omega⟩, ⟨1, by omega⟩),
        (⟨0x80, by omega⟩, ⟨0x80, by omega⟩, ⟨2, by omega⟩),
        (⟨0x00, by omega⟩, ⟨0x00, by omega⟩, ⟨3, by omega⟩)
      ],
      -- Eager pattern-end behaviors (das_model v2nd1):
      -- when next byte is the EOP marker, reset hub_off and inc seq_idx
      .resetIfNextEnds 0,
      .incIfNextEnds   1 ⟨1, by omega⟩
    ]
    patternEndOps := [
      -- Also (redundantly) on next note's advance_order
      .reset 0,
      .increment 1 ⟨1, by omega⟩
    ]
    dynamicFreqEntries := [
      -- ===== Frame-start updates =====
      -- T[100]: V2.hub_off (lo), V3.hub_off (hi)
      { freqSlot := 100,
        loSource := .scratch ⟨1, by omega⟩ 0,
        hiSource := .scratch ⟨2, by omega⟩ 0,
        phase    := .atFrameStart },
      -- T[104]: V1.ctrl (lo), V2.ctrl (hi). Hubbard percussion noise feed.
      { freqSlot := 104,
        loSource := .voiceCtrl ⟨0, by omega⟩,
        hiSource := .voiceCtrl ⟨1, by omega⟩,
        phase    := .atFrameStart },

      -- ===== Between V3 and V2 (= beforeVoice 1) =====
      -- T[98]: V1.seq_idx (lo), V2.seq_idx (hi)
      { freqSlot := 98,
        loSource := .scratch ⟨0, by omega⟩ 1,
        hiSource := .scratch ⟨1, by omega⟩ 1,
        phase    := .beforeVoice ⟨1, by omega⟩ },
      -- T[99]: V3.seq_idx (lo), V1.hub_off (hi)
      { freqSlot := 99,
        loSource := .scratch ⟨2, by omega⟩ 1,
        hiSource := .scratch ⟨0, by omega⟩ 0,
        phase    := .beforeVoice ⟨1, by omega⟩ },
      -- T[105]: V3.ctrl (lo), V1.pitch (hi)
      { freqSlot := 105,
        loSource := .voiceCtrl ⟨2, by omega⟩,
        hiSource := .voicePitch ⟨0, by omega⟩,
        phase    := .beforeVoice ⟨1, by omega⟩ },
      -- T[106]: V2.pitch (lo), V3.pitch (hi)
      { freqSlot := 106,
        loSource := .voicePitch ⟨1, by omega⟩,
        hiSource := .voicePitch ⟨2, by omega⟩,
        phase    := .beforeVoice ⟨1, by omega⟩ },
      -- T[107]: V1.inst (lo), V2.inst (hi)
      --   At this phase V1 hasn't loaded yet so v_inst[V1] is "prev_inst";
      --   V2 may or may not have loaded depending on its own scheduling.
      { freqSlot := 107,
        loSource := .voiceInst ⟨0, by omega⟩,
        hiSource := .voiceInst ⟨1, by omega⟩,
        phase    := .beforeVoice ⟨1, by omega⟩ },

      -- ===== Between V2 and V1 (= beforeVoice 0) =====
      -- T[100]: re-update so V1 sees latest V2.hub_off this frame
      { freqSlot := 100,
        loSource := .scratch ⟨1, by omega⟩ 0,
        hiSource := .scratch ⟨2, by omega⟩ 0,
        phase    := .beforeVoice ⟨0, by omega⟩ },
      -- T[104]: re-update similarly
      { freqSlot := 104,
        loSource := .voiceCtrl ⟨0, by omega⟩,
        hiSource := .voiceCtrl ⟨1, by omega⟩,
        phase    := .beforeVoice ⟨0, by omega⟩ }
    ]
  }"""

    out.append(f"""def commandoV3 : USFSong := {{
  freqTable := commandoV3FreqTable
  instruments := [{inst_refs}]
  patterns := [{pat_list}]
  subtunes := [{subtune_refs}]
  voiceOrder := [⟨2, by omega⟩, ⟨1, by omega⟩, ⟨0, by omega⟩]
  filter := none
  playRate := .vbi
  engineQuirks := {quirks}
  title := "Commando"
  author := "Rob Hubbard"
  released := "1985 Elite"
}}""")

    # Output path is repo-root-relative, computed from this file's location.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    out_path = os.path.join(repo_root, 'pipelines/commando/codegen/Commando/SongData.lean')
    with open(out_path, 'w') as f:
        f.write('\n'.join(out) + '\n')

    last_score = extracts[-1].score
    logger.info(
        "Wrote %d instruments, %d patterns, %d voices to %s",
        len(instruments), len(all_pats), len(last_score.voices), out_path,
    )


if __name__ == '__main__':
    main()
