# JC64dis (ice00/jc64) — HardTrack hand-annotation? NEGATIVE

> **Provenance.** Fetched live 2026-06-13 from ice00/jc64 (Java C64 emulator +
> disassembler, the project that ships hand-annotated `.dis` files for many C64
> music players). Inspected `doc/example/` directory listing and
> `doc/example/List.txt`.

## Task 2 result: JC64dis ships NO HardTrack `.dis` annotation

`doc/example/` contains ~90 hand-annotated `.dis` disassemblies of C64 music
players/editors and demo/digi/image samples. **None of them is HardTrack.**
Confirmed via both the directory listing and the catalogue file `List.txt`
(neither mentions the string "HardTrack").

Music-player `.dis` files that ARE present (relevant comparators — these are
the engine families JC64dis chose to annotate, none from the Polish
tracker scene):

- SoundMonitor (`SoundMonitor_shades.dis`)
- Music Assembler (`MusicAssembler.dis`, `musicAssembler_.dis`)
- Rockmonitor II & V (`Rockmonitor2.dis`, `Rockmonitor5.dis`)
- Future Composer
- Voice Tracker (`VoiceTracker.dis`), TenTracker (`TenTracker.dis`)
- Sequencer / SID Sequencer, SounDemon, SoundMaster, Power Music, Modulator,
  D.A.I.S.Y., Ariston, Yip Megasound, Barry Leitch player,
  Rob Hubbard's Companion player, Rob_Hubbard_CM, PeterLiepa, Synthicat
- subdirs: `demo/`, `digi/`, `image/`

**No HardTrack, no Elysium/Parados, no Polish-scene tracker** is among them.
There is no JC64dis annotation to capture or reuse.

## Implication

JC64dis is useful here only as a *disassembler tool* (its `.dis` format and the
Java disassembler engine), not as a source of a pre-existing HardTrack
annotation. SIDfinity's own hand-annotated `disassembly.s` for the
representative HardTrack SID — informed by the Elysium SDK source in
`src/sdk/extracted/` — will be the first structural annotation of this
engine.

## Sources

- https://github.com/ice00/jc64 — `doc/example/` directory + `doc/example/List.txt`
