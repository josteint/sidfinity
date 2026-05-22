"""DL2 → USF mapping.

Takes the structured `DragonsLairPartII` produced by `dl2_decompile` and
returns a Python representation of `USFSong` matching the Lean schema in
`codegen/DragonsLairPartIi/USF.lean`. The output is consumed by
`emit_usf_dl2.py` to write `SongData.lean`.

Mapping notes
─────────────
- Freq table: 1 sentinel pair + 96 (lo,hi) entries → `USFFreqTable.entries`
  (97 entries; downstream pitch N indexes entry N+1).

- Instruments: each DL2 instrument is two 8-byte records (`$C530`+i and
  `$C610`+i). The "static" fields (init PW, ctrl waveform, AD, SR) map
  cleanly to `USFInstrument.{initCtrl, initPwLo, initPwHi, ad, sr}`.
  The 1986-engine-specific effect routing (fx_flags byte + dual PWM +
  alt-waveform-by-frame-count) does NOT map cleanly onto the existing
  Hubbard-1985 USF behaviors. Those Option fields are therefore left
  `None` in this pass — the engine bytes are preserved verbatim in the
  in-tree `EngineImage.lean` and a future structural codegen will
  pattern-match fx_flags into the USF behaviors as we work them out.

- Note events: one `USFNoteEvent` per decoded pattern row. The 1-byte
  TIE row (duration.bit6 set) becomes `USFNoteKind.tie`; 2/3-byte rows
  become `USFNoteKind.pitched`. The 5 notes with bit 7 set ("legato /
  no-retrigger" — engine skips PW + AD/SR re-init) are marked with
  pitch = note & $7F; the bit-7 flag is preserved alongside via the
  `quirks` channel for the codegen but is NOT a separate `USFNoteKind`
  variant.

- Sticky instrument: pattern rows without an explicit instrument
  inherit the previous row's instrument WITHIN the pattern. The first
  row of each pattern (if no explicit instr) gets the default $1B (27),
  which is the engine's "silent default" instrument set by first-frame
  init. This is per-pattern only — the engine's real model is per-voice
  state carried across patterns, but resolving that requires a runtime
  trace; per-pattern is the conservative static approximation.

- Voice orderlists: terminator byte ($FE or $FF) maps to `loopPoint`:
    $FF wrap → `loopPoint = Some 0`
    $FE end  → `loopPoint = None`

- Subtunes: 10 entries, each with 3 voices. Tempo is approximated as
  the per-subtune speed_reload from $C4ED+A; the engine's actual tempo
  is "speed × (phase+1)" with phase as a sub-frame divider.

- voiceOrder = [2, 1, 0]: DL2 processes V3 → V2 → V1 (X counts down
  from 2 in the per-voice loop).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .dl2_decompile import (
    DragonsLairPartII, Pattern, PatternRow, Subtune, Instrument,
    DEFAULT_INSTR,
)


# ============================================================================
# Python mirrors of the Lean USF.lean structures.
# Names/casing kept Lean-side to make the emitter trivial.
# ============================================================================

@dataclass
class USFFreqTable:
    entries: list[tuple[int, int]]   # (lo, hi)


@dataclass
class USFInstrument:
    id: int
    initCtrl: int
    initPwLo: int
    initPwHi: int
    ad: int
    sr: int
    initFreqMod: str = "normal"        # "normal" | "dynamicVoiceCtrl"
    waveformProgram: list[int] = field(default_factory=list)
    waveLoop: int = 0
    waveStepEvery: int = 0
    pwMod: dict | None = None
    vibrato: dict | None = None
    freqSlide: dict | None = None
    arpeggio: dict | None = None
    effectOrder: list[str] = field(default_factory=list)
    releaseFramesBeforeEnd: int = 0
    releaseZeroAdsr: bool = False
    releaseNoRelease: bool = False
    filterEnabled: bool = False
    # DL2-specific raw bytes preserved for the structural codegen + audit.
    # (Not part of the Lean USFInstrument schema — emitted as a side-table.)
    raw_table1: list[int] = field(default_factory=list)
    raw_table2: list[int] = field(default_factory=list)


@dataclass
class USFNoteEvent:
    kind: str        # "tie" | "pitched:<N>" | "rest"
    durationFrames: int
    instrument: int
    porta: int = 0
    # DL2 audit fields (not in Lean USFNoteEvent schema):
    raw_bytes: list[int] = field(default_factory=list)
    bit7_no_retrigger: bool = False    # raw note byte had bit 7 set


@dataclass
class USFPattern:
    id: int
    notes: list[USFNoteEvent]


@dataclass
class USFVoice:
    orderlist: list[int]              # pattern indices (terminator stripped)
    loopPoint: int | None             # `Some N` ⇒ Nat in Lean; None ⇒ no loop


@dataclass
class USFSubtune:
    psid_index: int
    internal_index: int
    voices: list[USFVoice]
    tempo: int                        # speed_reload (frames per tick approximation)
    # DL2-specific:
    raw_speed_reload: int
    raw_phase_reload: int


@dataclass
class USFSong:
    freqTable: USFFreqTable
    instruments: list[USFInstrument]
    patterns: list[USFPattern]
    subtunes: list[USFSubtune]
    voiceOrder: list[int]             # 3 entries, each 0..2
    filter: dict | None
    playRate: str                     # "vbi" or "cia:<n>"
    title: str
    author: str
    released: str


# ============================================================================
# Conversion
# ============================================================================

def _convert_freq_table(song: DragonsLairPartII) -> USFFreqTable:
    return USFFreqTable(entries=list(song.freq_table))


def _convert_instrument(inst: Instrument) -> USFInstrument:
    return USFInstrument(
        id=inst.id,
        initCtrl=inst.ctrl_wave,
        initPwLo=inst.pulse_lo,
        initPwHi=inst.pulse_hi,
        ad=inst.ad,
        sr=inst.sr,
        # Behavior Options stay None — the 1986 engine's fx_flag routing
        # doesn't map cleanly onto the Hubbard-1985 USF behaviors. We
        # preserve the raw bytes so the structural codegen has every
        # value the player needs.
        waveformProgram=[inst.ctrl_wave],     # 1-step "program" (constant ctrl)
        waveLoop=0,
        waveStepEvery=0,
        effectOrder=[],
        raw_table1=[
            inst.pulse_lo, inst.pulse_hi, inst.ctrl_wave,
            inst.ad, inst.sr, inst.pulse_mod_cfg,
            inst.arp_offset, inst.fx_flags,
        ],
        raw_table2=[
            inst.alt_wave_A, inst.vibrato_src, inst.noise_wave,
            inst.reserved, inst.release_wave, inst.pulse_speed_packed,
            inst.filter_res, inst.filter_delta,
        ],
    )


def _convert_pattern(pat: Pattern) -> USFPattern:
    notes: list[USFNoteEvent] = []
    current_instrument = DEFAULT_INSTR
    for row in pat.rows:
        if row.instrument is not None:
            current_instrument = row.instrument
        if row.tie:
            notes.append(USFNoteEvent(
                kind="tie",
                durationFrames=row.duration,
                instrument=current_instrument,
                raw_bytes=list(row.raw_bytes),
            ))
            continue
        # 2- or 3-byte row — both have a note. Mask off bit 7 for the
        # pitch index; preserve the flag for the codegen.
        assert row.note is not None
        pitch = row.note & 0x7F
        no_retrigger = bool(row.note & 0x80)
        notes.append(USFNoteEvent(
            kind=f"pitched:{pitch}",
            durationFrames=row.duration,
            instrument=current_instrument,
            raw_bytes=list(row.raw_bytes),
            bit7_no_retrigger=no_retrigger,
        ))
    return USFPattern(id=pat.id, notes=notes)


def _convert_subtune(sub: Subtune) -> USFSubtune:
    voices: list[USFVoice] = []
    for stream in sub.voice_orderlist:
        if not stream:
            voices.append(USFVoice(orderlist=[], loopPoint=None))
            continue
        terminator = stream[-1]
        body = stream[:-1]
        if terminator == 0xFF:
            loop = 0
        elif terminator == 0xFE:
            loop = None
        else:
            # Unexpected — orderlist didn't end with a marker. Treat as
            # implicit end-of-song so we don't drop bytes silently.
            body = stream
            loop = None
        voices.append(USFVoice(orderlist=body, loopPoint=loop))
    return USFSubtune(
        psid_index=sub.psid_index,
        internal_index=sub.internal_index,
        voices=voices,
        tempo=max(1, sub.speed_reload),
        raw_speed_reload=sub.speed_reload,
        raw_phase_reload=sub.phase_reload,
    )


def dl2_to_usf(song: DragonsLairPartII) -> USFSong:
    return USFSong(
        freqTable=_convert_freq_table(song),
        instruments=[_convert_instrument(i) for i in song.instruments],
        patterns=[_convert_pattern(p) for p in song.patterns],
        subtunes=[_convert_subtune(s) for s in song.subtunes],
        voiceOrder=[2, 1, 0],
        filter=None,
        playRate="vbi",
        title=song.title,
        author=song.author,
        released=song.released,
    )


def main() -> int:
    """Quick smoke test: extract, convert, print structural summary."""
    from .dl2_decompile import SID_PATH, decompile
    blob = SID_PATH.read_bytes()
    dl2 = decompile(blob)
    usf = dl2_to_usf(dl2)
    print("USFSong (after dl2_to_usf conversion):")
    print(f"  freqTable.entries: {len(usf.freqTable.entries)} (sentinel + 96 notes)")
    print(f"  instruments:      {len(usf.instruments)}")
    print(f"  patterns:         {len(usf.patterns)}")
    print(f"  subtunes:         {len(usf.subtunes)}")
    print(f"  voiceOrder:       {usf.voiceOrder}")
    print(f"  playRate:         {usf.playRate}")
    print(f"  title:            {usf.title!r}")
    print()
    print(f"Sample instrument [1] (table1+table2 raw):")
    i1 = usf.instruments[1]
    print(f"  initCtrl=${i1.initCtrl:02X} PW=${i1.initPwHi:02X}{i1.initPwLo:02X} "
          f"AD=${i1.ad:02X} SR=${i1.sr:02X}")
    print(f"  raw_table1: {[f'${b:02X}' for b in i1.raw_table1]}")
    print(f"  raw_table2: {[f'${b:02X}' for b in i1.raw_table2]}")
    print()
    print(f"Sample pattern [{usf.patterns[0].id}] (first 5 notes):")
    for n in usf.patterns[0].notes[:5]:
        print(f"  kind={n.kind!r:<14} dur={n.durationFrames:>2} "
              f"inst={n.instrument:>2} bit7={n.bit7_no_retrigger}")
    print()
    print(f"Subtune PSID#1 voice 1:")
    s1 = usf.subtunes[0]
    print(f"  internal A={s1.internal_index} tempo={s1.tempo} "
          f"speed=${s1.raw_speed_reload:02X} phase=${s1.raw_phase_reload:02X}")
    print(f"  V1 orderlist({len(s1.voices[0].orderlist)}): "
          f"{[hex(p) for p in s1.voices[0].orderlist[:10]]}... "
          f"loop={s1.voices[0].loopPoint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
