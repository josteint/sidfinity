# Smaller Players - Batch 2

## DefleMask v12 (245 tunes)

- **Author:** Leonardo Demartino (Delek)
- **Year:** 2013-2016
- **Documentation:** Good - format spec at https://www.deflemask.com/DMF_SPECS.txt
- **Source available:** No (but third-party player exists: https://github.com/chiptunecafe/deflestream64)

Cross-platform multi-system chiptune tracker (Windows/macOS/Linux/iOS/Android). Supports C64 SID (6581 and 8580), plus Genesis, NES, Game Boy, etc. Not a native C64 tool. DMF file format: zlib-compressed binary, 16-byte magic ".DelekDefleMask.", version byte. System IDs: C64 8580=0x07, C64 6581=0x47, both 3 channels. Exports to .SID, .VGM, .WAV, ROM. The 6502 player is embedded in SID exports. SIDId identifies three variants: DefleMask_v1, DefleMask_v2, DefleMask_v12.

## 20CC (245 tunes)

- **Author:** Falco Paul (player code), Edwin van Santen/EVS (compositions)
- **Year:** Late 1980s-early 1990s
- **Documentation:** Poor
- **Source available:** No
- **CSDb:** #10741

Named after the group "20th Century Composers" (Dutch C64 music group). Unique features: auto-swing, beat accenting. Claims "world's fastest music routine" at only four raster lines. Architecture may be based on Future Composer. Proprietary editor format, no public spec. Instructions accessible inside tool (press F7).

## EMS/Odie (197 tunes)

- **Author:** Sean Connolly (Odie) of Cosine/Sonix Systems
- **Year:** 1997+ (V7.03, V9.x, V10.x)
- **Documentation:** Poor
- **Source available:** No
- **CSDb:** #4649

The Electronic Music System. Native C64 SID editor. Described as "good but advanced." Traditional demoscene editor alongside DMC and JCH. Multiple version sub-variants in sidid.

## Cyberlogic SoundStudio (197 tunes)

- **Author:** Oliver Klee & Sascha Nagie
- **Year:** 1991
- **Documentation:** Very poor
- **Source available:** No
- **CSDb:** #170632

German scene music editor. Sascha Nagie associated with "Demons of Sound." Very little public documentation.

## Jeff (192 tunes)

- **Author:** Soren Lund (Jeff) of Cyberzound Productions
- **Year:** 1996+
- **Documentation:** Poor
- **Source available:** No
- **CSDb:** #122334

Custom player routines by prolific SID composer. Multiple group-specific variants: Jeff/Airwalk, Jeff/BullSID, Jeff/FLT, Jeff/XLarge. Also X-SID variant (2007, via Viruz group). Proprietary "Music Editor" format. Interview: https://remix64.com/interviews/interview-soren-jeff-lund.html

## John Player (184 tunes)

- **Author:** Aleksi Eeben (Heatbeat) of CNCD/Cyberiad
- **Year:** 2001-2002
- **Documentation:** Moderate
- **Source available:** Distributed with tool (V1.6, V2.0 beta)
- **CSDb:** #2630

Created because author found other C64 music tools unintuitive. Community described it as "most efficient C64 editor combining user-friendliness and straightforwardness." Versions: V1.0, V1.4, V1.6, V2.0b. Also on Pouet: https://www.pouet.net/prod.php?which=13860

## MusicShop (182 tunes)

- **Author:** Don Williams, published by Broderbund Software
- **Year:** 1984 (MIDI version 1985)
- **Documentation:** Good (user manual archived at Internet Archive)
- **Source available:** No (commercial)
- **CSDb:** #82453
- **Manual:** https://archive.org/stream/The_Music_Shop_Users_Manual

Commercial music composition program. Graphical notation interface (not tracker-style). Independent control of 3 SID voices with envelope, waveform, vibrato, filter. Aimed at serious music composers rather than demoscene.

## Vibrants/Laxity (179 tunes)

- **Author:** Thomas Egeskov Petersen (Laxity) of Vibrants/Bonzai/Maniacs of Noise/MultiStyle Labs
- **Year:** Late 1980s-1990s
- **Documentation:** Poor (editor never publicly documented)
- **Source available:** No (but JCH's derivative players have source)
- **CSDb:** #122333

The Laxity Editor was the predecessor to the JCH Editor. Never intended to go public. Inspired JCH to create his own editor after Laxity told him to stop using it. Modern successor: SID Factory II (https://github.com/Chordian/sidfactory2) by Laxity, JCH, and Michel de Bree.

## OdinTracker (163 tunes)

- **Author:** Zoltan Konyha (Zed)
- **Year:** 2000-2001
- **Documentation:** Moderate (source available)
- **Source available:** Yes (OdinTracker113src.zip on CSDb)
- **CSDb:** #2628, #12577

Native C64 SID tracker with publicly available source code.

## David Whittaker (117 tunes)

- **Author:** David Whittaker (driver based on code by Jason Brooke)
- **Year:** Late 1985+
- **Documentation:** Moderate
- **Source available:** No (but well-studied)

One of the most prolific C64 game music composers. Composed by programming directly in machine code (Supersoft tools), not using a music editor. Uses Music Macro Language (MML). Song table format: `<speed>, <v1_lo>, <v1_hi>, <v2_lo>, <v2_hi>, <v3_lo>, <v3_hi>` (7 bytes per entry). Includes arpeggio tables and envelope data. Composed on Yamaha CX5M/Casio CZ-230S/Roland Jupiter-6 then translated to 6502. Driver ported to NES, Amstrad CPC, Atari ST, Amiga, ZX Spectrum with compatible data structures.
