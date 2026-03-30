# Smaller Players - Batch 1

## Loadstar SongSmith (314 tunes)

- **Author:** Unknown (distributed via Loadstar magazine)
- **Year:** ~1980s
- **Documentation:** Very poor
- **Source available:** No
- **Notes:** User-friendly tool aimed at hobbyist composers. Loadstar was a disk-based magazine running 24+ years and 250 issues. Used by non-scene composers (e.g., Debby Cruz). Original program may exist in "Loadstar Compleat" archive on itch.io.

## Laxity NewPlayer V21 (314 tunes)

- **Author:** Thomas Egeskov Petersen (Laxity) of Vibrants/Maniacs of Noise
- **Year:** 2006
- **Documentation:** Good (part of JCH ecosystem)
- **Source available:** Yes (JCH released player source)
- **CSDb:** #26563

Derivative of JCH NewPlayer system. The JCH Editor has a modular architecture where different "player" engines can be merged in. Laxity's V21 (version 21.G4 Final) is one such derivative. Uses JCH Editor format with separate instrument, sequence, and pattern data. Features wavetable-style instrument programming, multiple speed support, filter control, extremely efficient rastertime. Versioning: "21.G4" = player version 21, variant G4. Q-series variants for multispeed songs.

## CheeseCutter 2.x (306 tunes)

- **Author:** Timo Taipalus (Abaddon) of Triad
- **Year:** 2009-2017
- **Documentation:** Good
- **Source available:** Yes - https://github.com/theyamo/CheeseCutter (GPL)
- **CSDb:** Multiple releases v0.4.0 through v2.9.0

Cross-platform SID tracker written in D language. Player code in `src/c64/custplay.acme` (ACME assembler). Proprietary `.ct` file format (packed song data). Can export to .sid/.prg. Supports both single-SID and stereo 2SID. Uses reSID/reSID-FP for accurate emulation. Can flag out unused effect code to reduce player size.

## Electrosound (301 tunes)

- **Author:** Orpheus Ltd. (Steve Mellin)
- **Year:** 1985
- **Documentation:** Moderate
- **Source available:** No (commercial)

Commercial C64 music editor (14.95 GBP). Up to 10 instruments, 20 sequences with up to 240 notes each. Per instrument: all SID registers plus modulations on pitch, pulse width, cutoff frequency, key up/down. Per modulator: delay, speed, depth, direction (up/down/vibrato/shuffle), restart. Per sequence: tempo and 3 instruments. Considered most user-friendly of its era but poorly coded (slowest known player on C64). Tuned at 423.9 Hz (not A=440). Driver does not loop.

## Ubik's Musik (293 tunes)

- **Author:** Dave Korn (Ubik), published by Firebird
- **Year:** 1987
- **Documentation:** Moderate
- **Source available:** No (commercial)
- **CSDb:** #39950

26 songs and 32 instruments per file. Three vertical columns (one per voice) displaying sequence numbers with repeat counts. Compiled tunes are standalone PRG (~7KB) with player at $C600. First editor to support logarithmic vibratos, waveform swaps, wavetable drums (8 fixed sounds). Possibly first to support echoes (sustain level changes on every note). Game programmers could play song on 2 voices + SFX on 3rd. Closest to Hubbard's driver capabilities at release. Drawback: high rastertime usage.

## TFX (269 tunes)

- **Author:** Ray of Area Team/Unreal
- **Year:** 1995-1996
- **Documentation:** Very poor
- **Source available:** No
- **CSDb:** #110111 (v1.0), #38900 (v1.2)

Polish scene music editor. Multiple versions (1.0, 1.2, 2.4). Available as .d64/.prg. Very little public documentation despite respectable tune count.

## SidTracker64 (264 tunes)

- **Author:** Daniel Larsson (Pernod)
- **Year:** 2015
- **Documentation:** Good (App Store, reviews)
- **Source available:** No (commercial iOS app)

Modern iPad app for C64 music creation. Native `.s64` format, exports to .sid, .prg, .m4a. Accurate SID emulation. MIDI keyboard/controller input. Audiobus 2 and Inter-App Audio support. Waveform switching per pattern step. Taken seriously by C64 music community (264 tunes in HVSC).

## AMP - Advanced Music Programmer (246 tunes)

- **Author:** Andrew Miller (Burton) of Euratom/Quality
- **Year:** 1989-1991
- **Documentation:** Poor
- **Source available:** No
- **CSDb:** #35519

German-scene music editor distributed through Magic Disk 64 magazine. Proprietary format. Most prolific user: Markus Mueller (Cool One, Delta v2, etc.).
