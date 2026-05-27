"""Split the parent SID, extract each sub-binary, merge into one USFSong
with 5 USFSubtune records, emit SongData.lean.

For documentation of the multi-binary structure see
pipelines/five_title_tunes/README.md.
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO))

from pipelines.five_title_tunes.extract.engine_model import extract
from pipelines.five_title_tunes.extract.merge import merge
from pipelines.five_title_tunes.extract.types import Note, ExtractedSong

logger = logging.getLogger(__name__)

PARENT_SID  = REPO / 'hvsc84/MUSICIANS/H/Hubbard_Rob/5_Title_Tunes.sid'
WORK_SUBS   = REPO / 'pipelines/five_title_tunes/work_subs'
SUB_FT_BASES = [0x0F6A, 0x1C07, 0x2360, 0x2BA0, 0x34C3]
N_SUBS       = 5

OUT_LEAN = REPO / 'pipelines/five_title_tunes/codegen/FiveTitleTunes/SongData.lean'


# ============================================================================
# Lean emission helpers (cloned from Monty's emit_usf with renamed prefix)
# ============================================================================

def hex_byte(n: int) -> str:
    return f"⟨{n & 0xFF}, by omega⟩"


def gen_freq_table(T: list[int]) -> str:
    pairs = []
    for i in range(128):
        if i < len(T):
            lo = T[i] & 0xFF
            hi = (T[i] >> 8) & 0xFF
        else:
            lo = 0
            hi = 0
        pairs.append(f"({hex_byte(lo)}, {hex_byte(hi)})")
    return "[" + ", ".join(pairs) + "]"


def gen_instrument(idx, inst) -> str:
    init_lo = inst.pwm.init_pw & 0xFF
    init_hi = (inst.pwm.init_pw >> 8) & 0x0F
    if inst.pwm.speed == 0:
        pwmod = 'none'
    elif inst.pwm.mode == 'linear':
        pwmod = (f"some {{ mode := .linear {hex_byte(inst.pwm.speed)}, "
                 f"stepEvery := 1, startDelay := 0 }}")
    else:
        pwmod = (f"some {{ mode := .bidirectional {hex_byte(inst.pwm.speed)} "
                 f"{hex_byte(inst.pwm.min_hi)} {hex_byte(inst.pwm.max_hi)}, "
                 f"stepEvery := 1, startDelay := 0 }}")
    if inst.vibrato_scale == 0:
        vibspec = 'none'
    else:
        vibspec = (f"some {{ shape := .triangle, periodFrames := 8, "
                   f"semitoneShift := {inst.vibrato_scale + 1}, onsetFrames := 6, "
                   f"rampUpFrames := 0, unipolar := true }}")
    if inst.has_bit0:
        slidespec = ("some { kind := .monotonic (-1), stepEvery := 1, "
                     "startDelay := 9, stopAtZero := true }")
    else:
        slidespec = 'none'
    if inst.arp_offset > 0:
        arpspec = (f"some {{ intervals := [0, {inst.arp_offset}], "
                   f"stepEvery := 1, phaseSource := .global, startDelay := 0 }}")
    else:
        arpspec = 'none'

    eff_parts = []
    if inst.vibrato_scale > 0: eff_parts.append('.vibrato')
    eff_parts.append('.pwMod')
    if inst.has_bit0: eff_parts.append('.freqSlide')
    if inst.arp_offset > 0: eff_parts.append('.arpeggio')
    eff_parts.append('.gateCheck')
    eff_order = '[' + ', '.join(eff_parts) + ']'

    waveform_lit = '[' + ', '.join(hex_byte(b) for b in inst.waveform.steps) + ']'

    return f"""def ft3I{idx} : USFInstrument := {{
  initCtrl := {hex_byte(inst.waveform.steps[0])}
  initPwLo := {hex_byte(init_lo)}
  initPwHi := {hex_byte(init_hi)}
  ad := {hex_byte(inst.envelope.ad)}
  sr := {hex_byte(inst.envelope.sr)}
  initFreqMod := .normal
  waveformProgram := {waveform_lit}
  waveLoop := {inst.waveform.loop}
  waveStepEvery := 1
  pwMod := {pwmod}
  vibrato := {vibspec}
  freqSlide := {slidespec}
  arpeggio := {arpspec}
  effectOrder := {eff_order}
  release := {{ framesBeforeEnd := 3, zeroAdsr := true, noRelease := false }}
  filterEnabled := false
  skydive := false
}}"""


def gen_note(note: Note, tempo: int) -> str:
    pitch = note.pitch
    no_release = bool(note.drum_trig & 0x80)
    inst = (note.instrument & 0xFF) | (0x20 if no_release else 0)
    tie = note.tie
    frames = note.duration * tempo
    porta = note.drum_trig & 0x7F
    if tie:
        kind = '.tie'
    elif pitch == 104:
        kind = '.percussion .dynamicCtrl'
    elif pitch < 96:
        kind = f'.pitched {hex_byte(pitch)}'
    else:
        kind = '.percussion .dynamicCtrl'
    return (f"{{ kind := {kind}, durationFrames := {frames}, "
            f"instrument := {inst}, porta := {porta} }}")


def gen_pattern(idx: int, notes: list[Note], tempo: int) -> str:
    note_strs = [gen_note(n, tempo) for n in notes]
    return f"def ft3P{idx} : USFPattern := {{ notes := [{', '.join(note_strs)}] }}"


# ============================================================================
# CLI entry
# ============================================================================

def main(argv: Optional[list[str]] = None) -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    # 1. Split the parent into 5 sub PSIDs (if not already done)
    WORK_SUBS.mkdir(parents=True, exist_ok=True)
    if not all((WORK_SUBS / f'sub_{i}.sid').exists() for i in range(N_SUBS)):
        logger.info("splitting parent → 5 sub PSIDs")
        subprocess.run([
            sys.executable, str(REPO / 'tools/split_multi_binary.py'),
            str(PARENT_SID), str(WORK_SUBS),
        ], check=True)

    # 2. Extract each sub
    extracts: list[ExtractedSong] = []
    for i in range(N_SUBS):
        sub_path = WORK_SUBS / f'sub_{i}.sid'
        es = extract(sid_path=str(sub_path), ft_base=SUB_FT_BASES[i],
                     default_pw_min=0x08, default_pw_max=0x0E)
        extracts.append(es)
        logger.info("  sub %d: %d instruments, %d voices, tempo %d",
                    i, len(es.instruments),
                    len(es.score.voices), es.score.tempo)

    # 3. Merge into one ExtractedSong
    merged = merge(extracts)
    subtune_tempos = merged.score.subtune_tempos  # type: ignore[attr-defined]

    # 4. Emit SongData.lean
    out: list[str] = [
        "-- Auto-generated USF v3 5 Title Tunes data (merged from 5 sub-binaries)",
        f"-- 5 subtunes; merged inst count: {len(merged.instruments)} (≤ 32)",
        "import FiveTitleTunes.USF",
        "",
    ]
    out.append(f"def fiveTtV3FreqTable : USFFreqTable := "
               f"{{ entries := {gen_freq_table(merged.freq_table)} }}")
    out.append("")
    for i, inst in enumerate(merged.instruments):
        out.append(gen_instrument(i, inst))
        out.append("")

    # Collect patterns. Each is referenced by potentially multiple voices.
    # Each pattern has a single tempo (the sub it came from).
    pat_tempo: dict[int, int] = {}
    pat_notes: dict[int, list[Note]] = {}
    for sub_idx, es in enumerate(extracts):
        tempo = subtune_tempos[sub_idx]
        for v in merged.score.voices[sub_idx * 3 : sub_idx * 3 + 3]:
            for pat_idx, notes in v.patterns.items():
                if pat_idx not in pat_notes:
                    pat_notes[pat_idx] = notes
                    pat_tempo[pat_idx] = tempo
                # otherwise patterns shared across voices/subs — fine, same tempo

    for idx in sorted(pat_notes.keys()):
        out.append(gen_pattern(idx, pat_notes[idx], pat_tempo[idx]))
        out.append("")

    # Voices (15 total — 5 subs × 3 voices)
    for vi, v in enumerate(merged.score.voices):
        ol = '[' + ', '.join(str(p) for p in v.orderlist) + ']'
        loop_pt = v.loop
        loop_str = (f'some {loop_pt}' if loop_pt is not None and loop_pt >= 0
                    else 'none')
        out.append(f"def ft3V{vi} : USFVoice := "
                   f"{{ orderlist := {ol}, loopPoint := {loop_str} }}")
    out.append("")

    # 5 Subtunes, each wrapping 3 voices + per-sub tempo + HR threshold.
    # HR thresholds were dialed in by ear, comparing rebuilt subtunes
    # against the original sub-binaries one at a time. Each sub-binary
    # in the original has its own HR character (different cmp #N value
    # in its gate-off check), so a single shared threshold misfits some.
    HR_THRESHOLDS = [4, 2, 2, 10, 4]
    for si in range(N_SUBS):
        v_refs = ', '.join(f'ft3V{i}' for i in range(si * 3, si * 3 + 3))
        out.append(f"def ft3S{si} : USFSubtune := "
                   f"{{ voices := [{v_refs}], tempo := {subtune_tempos[si]}, "
                   f"hrThreshold := {HR_THRESHOLDS[si]} }}")
    out.append("")

    # Pattern list (ordered, with empty placeholders for missing indices)
    max_pat = max(pat_notes.keys()) + 1
    pat_refs: list[str] = []
    for i in range(max_pat):
        if i in pat_notes:
            pat_refs.append(f'ft3P{i}')
        else:
            pat_refs.append('{ notes := [] }')

    inst_refs = ', '.join(f'ft3I{i}' for i in range(len(merged.instruments)))
    subtune_refs = ', '.join(f'ft3S{i}' for i in range(N_SUBS))
    pat_list = ', '.join(pat_refs)

    # engineQuirks: same noteLoadOps/patternEndOps as Monty (same Hubbard
    # engine family). Per-sub pwmPeriodInit/pwmDirInit differ across subs
    # — we use sub 0's as the canonical (write-trace divergence on subs
    # 1-4 is expected; ML training value over fidelity).
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
    pwmPeriodInit := [0, 0, 1]
    pwmDirInit := [0, 0, 1]
  }"""

    out.append(f"""def fiveTtV3 : USFSong := {{
  freqTable := fiveTtV3FreqTable
  instruments := [{inst_refs}]
  patterns := [{pat_list}]
  subtunes := [{subtune_refs}]
  voiceOrder := [⟨2, by omega⟩, ⟨1, by omega⟩, ⟨0, by omega⟩]
  filter := none
  playRate := .vbi
  engineQuirks := {quirks}
  title := "5 Title Tunes"
  author := "Rob Hubbard"
  released := "1985 Rob Hubbard"
}}""")

    OUT_LEAN.parent.mkdir(parents=True, exist_ok=True)
    OUT_LEAN.write_text('\n'.join(out) + '\n')
    logger.info("Wrote %d instruments, %d patterns, %d voices, 5 subtunes to %s",
                len(merged.instruments), len(pat_notes),
                len(merged.score.voices), OUT_LEAN)


if __name__ == '__main__':
    main()
