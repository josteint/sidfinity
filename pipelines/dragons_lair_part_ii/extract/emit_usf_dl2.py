"""DL2 USF → SongData.lean emitter.

Reads the original SID, runs `dl2_decompile` + `dl2_to_usf`, and writes
`codegen/DragonsLairPartIi/SongData.lean` defining the constant
`dragons_lair_part_iiV3 : USFSong` against the schema in `USF.lean`.

This replaces the Monty-cloned (and incorrect-for-DL2) auto-generated
SongData.lean produced by the inherited `engine_model.py` / `emit_usf.py`.

The verbatim Main.lean does not currently consume this SongData — it
reads `EngineImage.lean` directly. But emitting a structurally-correct
USFSong is a checkpoint on the road to a structural codegen, and the
data round-trips through the type system: if it compiles, the static
shape is valid USF.

Usage:
    python3 -m pipelines.dragons_lair_part_ii.extract.emit_usf_dl2
"""
from __future__ import annotations

from pathlib import Path

from .dl2_decompile import SID_PATH, decompile
from .dl2_to_usf import (
    dl2_to_usf, USFSong, USFInstrument, USFNoteEvent, USFPattern,
    USFSubtune, USFVoice, USFFreqTable,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_PATH = (
    REPO_ROOT
    / "pipelines/dragons_lair_part_ii/codegen/DragonsLairPartIi/SongData.lean"
)


# ---------------------------------------------------------------------------
# Lean-literal helpers
# ---------------------------------------------------------------------------

def fin256(n: int) -> str:
    if not (0 <= n < 256):
        raise ValueError(f"value {n} out of Fin 256 range")
    return f"⟨{n}, by omega⟩"


def lean_str(s: str) -> str:
    # Lean strings: only \" and \\ need escaping for what we put through.
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def emit_freq_table(ft: USFFreqTable) -> str:
    pairs = ", ".join(f"({fin256(lo)}, {fin256(hi)})" for lo, hi in ft.entries)
    return (
        "def dl2FreqTable : USFFreqTable := {\n"
        f"  entries := [{pairs}]\n"
        "}\n"
    )


def emit_instrument(inst: USFInstrument) -> str:
    # Behavior Options are all `none` — see dl2_to_usf for rationale. The
    # 1986-engine effect routing isn't yet mapped onto the 1985 USF
    # behaviors; the raw bytes live in EngineImage.lean for the
    # verbatim emit path.
    waveform_program = "[" + ", ".join(fin256(b) for b in inst.waveformProgram) + "]"
    return (
        f"def dl2I{inst.id} : USFInstrument := {{\n"
        f"  initCtrl := {fin256(inst.initCtrl)}\n"
        f"  initPwLo := {fin256(inst.initPwLo)}\n"
        f"  initPwHi := {fin256(inst.initPwHi)}\n"
        f"  ad := {fin256(inst.ad)}\n"
        f"  sr := {fin256(inst.sr)}\n"
        f"  initFreqMod := .normal\n"
        f"  waveformProgram := {waveform_program}\n"
        f"  waveLoop := {inst.waveLoop}\n"
        f"  waveStepEvery := {inst.waveStepEvery}\n"
        f"  pwMod := none\n"
        f"  vibrato := none\n"
        f"  freqSlide := none\n"
        f"  arpeggio := none\n"
        f"  effectOrder := []\n"
        f"  release := {{ framesBeforeEnd := {inst.releaseFramesBeforeEnd}, "
        f"zeroAdsr := {'true' if inst.releaseZeroAdsr else 'false'}, "
        f"noRelease := {'true' if inst.releaseNoRelease else 'false'} }}\n"
        f"  filterEnabled := {'true' if inst.filterEnabled else 'false'}\n"
        f"  skydive := false\n"
        f"}}\n"
    )


def emit_pattern(pat: USFPattern) -> str:
    """Emit a USFPattern. If notes is empty, this pattern was unreferenced."""
    if not pat.notes:
        # Should not happen for our extraction (we only emit referenced
        # patterns) but kept for safety.
        return f"def dl2P{pat.id} : USFPattern := {{ notes := [] }}\n"
    note_lits: list[str] = []
    for n in pat.notes:
        if n.kind == "tie":
            kind_lit = ".tie"
        elif n.kind.startswith("pitched:"):
            pitch = int(n.kind.split(":", 1)[1])
            kind_lit = f".pitched {fin256(pitch)}"
        elif n.kind == "rest":
            kind_lit = ".rest"
        else:
            raise ValueError(f"unknown note kind {n.kind!r}")
        note_lits.append(
            f"{{ kind := {kind_lit}, durationFrames := {n.durationFrames}, "
            f"instrument := {n.instrument}, porta := {n.porta} }}"
        )
    return (
        f"def dl2P{pat.id} : USFPattern := {{\n"
        f"  notes := [{', '.join(note_lits)}]\n"
        f"}}\n"
    )


def emit_voice(name: str, voice: USFVoice) -> str:
    loop = "none" if voice.loopPoint is None else f"some {voice.loopPoint}"
    orderlist = "[" + ", ".join(str(p) for p in voice.orderlist) + "]"
    return f"def {name} : USFVoice := {{ orderlist := {orderlist}, loopPoint := {loop} }}\n"


def emit_subtune(idx: int, sub: USFSubtune,
                 voice_names: tuple[str, str, str]) -> str:
    voices_lit = ", ".join(voice_names)
    return (
        f"def dl2S{idx} : USFSubtune := {{ voices := [{voices_lit}], "
        f"tempo := {sub.tempo} }}\n"
    )


def emit_song_data(usf: USFSong, n_pattern_slots: int) -> str:
    """Full SongData.lean content."""
    out: list[str] = []
    out.append("-- Auto-generated by extract/emit_usf_dl2.py")
    out.append("-- Rob Hubbard — Dragon's Lair Part II (1986 Software Projects)")
    out.append("--")
    out.append("-- Structural USF mapping derived from the 1986 Hubbard engine.")
    out.append("-- Behavior fields (pwMod / vibrato / freqSlide / arpeggio) are")
    out.append("-- all `none` in this pass — the 1986 engine's fx_flag routing")
    out.append("-- doesn't yet have a clean mapping onto the existing USF")
    out.append("-- behaviors. The verbatim emit path in Main.lean uses")
    out.append("-- EngineImage.lean for byte-perfect output; this file")
    out.append("-- captures the structural shape for future codegen work.")
    out.append("")
    out.append("import DragonsLairPartIi.USF")
    out.append("")

    # Freq table
    out.append(emit_freq_table(usf.freqTable))

    # Instruments
    for inst in usf.instruments:
        out.append(emit_instrument(inst))

    # Patterns — we only emit referenced ones, but the song's patterns
    # list is indexed by id. Build a complete table of n_pattern_slots
    # entries, with referenced patterns named and unused slots inline {}.
    pat_by_id = {p.id: p for p in usf.patterns}
    for pat in usf.patterns:
        out.append(emit_pattern(pat))

    # Voices + subtunes
    for idx, sub in enumerate(usf.subtunes):
        v_names = (f"dl2S{idx}V0", f"dl2S{idx}V1", f"dl2S{idx}V2")
        for v_idx, v in enumerate(sub.voices):
            out.append(emit_voice(v_names[v_idx], v))
        out.append(emit_subtune(idx, sub, v_names))

    # Patterns array (indexed by pattern id 0..n-1)
    pat_entries = []
    for i in range(n_pattern_slots):
        if i in pat_by_id:
            pat_entries.append(f"dl2P{i}")
        else:
            pat_entries.append("{ notes := [] }")
    pat_lit = "[" + ", ".join(pat_entries) + "]"

    # Instrument array
    inst_lit = "[" + ", ".join(f"dl2I{i}" for i in range(len(usf.instruments))) + "]"

    # Subtune array
    sub_lit = "[" + ", ".join(f"dl2S{i}" for i in range(len(usf.subtunes))) + "]"

    out.append("def dragons_lair_part_iiV3 : USFSong := {")
    out.append(f"  freqTable := dl2FreqTable")
    out.append(f"  instruments := {inst_lit}")
    out.append(f"  patterns := {pat_lit}")
    out.append(f"  subtunes := {sub_lit}")
    out.append(f"  voiceOrder := [⟨2, by omega⟩, ⟨1, by omega⟩, ⟨0, by omega⟩]")
    out.append(f"  filter := none")
    out.append(f"  playRate := .vbi")
    # Use the engineQuirks defaults — no 1986-specific quirks
    # representation defined in USF.lean yet.
    out.append(f"  engineQuirks := {{}}")
    out.append(f"  title := {lean_str(usf.title)}")
    out.append(f"  author := {lean_str(usf.author)}")
    out.append(f"  released := {lean_str(usf.released)}")
    out.append("}")
    out.append("")

    return "\n".join(out)


def main() -> int:
    blob = SID_PATH.read_bytes()
    dl2 = decompile(blob)
    usf = dl2_to_usf(dl2)
    n_pattern_slots = len(dl2.pattern_pointers)
    content = emit_song_data(usf, n_pattern_slots)
    OUT_PATH.write_text(content)
    print(f"Wrote {OUT_PATH}")
    print(f"  freqTable:   {len(usf.freqTable.entries)} entries")
    print(f"  instruments: {len(usf.instruments)}")
    print(f"  patterns:    {len(usf.patterns)} referenced / {n_pattern_slots} slots")
    print(f"  subtunes:    {len(usf.subtunes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
