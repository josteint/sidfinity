# 20CC — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

20CC, a C64 SID music editor by **Falco Paul** (player code) with compositions by
**Edwin van Santen (EVS)** — the Dutch group "20th Century Composers" (Leiden, founded
17 June 1988). 209 HVSC #84 tunes; 0 migrated. Player base $1000, play $1003. EVS
claimed the **"world's fastest music routine"** (4 raster lines). No public source, but
the editor's **in-tool F7 instructions** were recovered verbatim (`src/`).

## ⚠ FC-inspired, NOT a Future Composer fork — settled

The stub's "may be based on Future Composer" is **functional resemblance only**. The
editor's own F7 text says *"All functions are almost the same as Future Composer, **but
this is NOT the same!**"* Concrete binary differences (from the FC comparison):
- **Vibrato**: 20CC uses a **bit-rotation loop** (LSR/ROR of the ZP freq pair ×Y); FC
  uses signed-delta addition.
- **Wave-table dispatch**: 20CC Variant A uses a hi-2-bit scheme ($00/$40/$80/$C0); FC
  uses $40/$60 thresholds.
- **Filter**: 20CC writes filter only on note-load; FC runs a per-frame filter program.
- **Instrument coupling**: 20CC Variant B embeds the instrument in the note pitch — FC
  never does this.
- 20CC has its own sidid signature (no "based on FC" flag); the 4-raster-line player is
  incompatible with FC's weight; the disks ship an FC *relocator* as a separate tool.

Verdict: **independent design** (Falco Paul "reverse engineered" others' routines and
built his own). The FC pipeline does NOT transfer wholesale — but the editing paradigm
(tracks → blocks → 8-byte instruments) and shared MoN-lineage conventions (96-note split
freq table, `STA $D4xx,Y` Y-indexed voices, X=2,1,0 loop, `$FF` end-marker) are familiar.

## File index

| Topic | File | Reliability |
|---|---|---|
| Write model + binary structure + 2 variants + FC byte-comparison | `cluster_write_model_and_fc_link.md` | secondary (binary) |
| ↳ hex map of a canonical Variant-A SID | `src/I_Wanna_Dance_hexmap.md` | primary |
| Editor + feature model + author + provenance | `cluster_editor_and_author.md` | secondary |
| ↳ verbatim F7 in-tool instructions | `src/20CC_Composer_Instructions.txt` | primary (the only surviving feature doc) |
| HVSC corpus / address clusters / scene | `cluster_corpus_and_scene.md` | primary (DB) |

(No formal format spec / source was published; structure is from byte-stable binary
inspection + the F7 help text.)

## What's solved

**Two binary variants** (one player, two builds):
- **Variant A — 174/209** (majority): `load/init=$1000, play=$1003`; state workspace
  `$1006–$106F`; ~2 KB player. (sidid sig7 — vibrato pattern.)
- **Variant B — 35/209** (later): `load/init=$0FFA, play=$1081`; ASCII credit string
  often at `$100C`; matches the sidid primary sig (`D0 ED C9 E0 B0 10 29 1F 7D`, note-range
  check + hard-restart). **Variant B embeds the instrument number in the note pitch**
  (`note & $1F` = instrument; `$E0–$FF` = commands) — a distinct extraction path.

**Per-frame write model** (voice order **X=2,1,0**; voice offsets `$146D = {00,07,0E}`;
all per-voice writes `STA $D4xx,Y`):
1. `$D401,Y` freq-hi; 2. `$D400,Y` freq-lo; 3. `$D402,Y` PW-lo; 4. `$D403,Y` PW-hi;
5. **`$D418` absolute written 3× per frame** (once per voice loop — likely the beat-accent
mechanism); 6. `$D404,Y` ctrl/gate (on new-note load, or `frame_counter==2` for hard
restart). On **instrument load only**: `$D405`/`$D406` (AD/SR), `$D416`/`$D417` (filter).
**Vibrato = bit-rotation loop** (not signed-delta). Freq = 96-note split table (`$1485`
lo / `$14E5` hi).

**Data hierarchy** (TWO levels, simpler than FC's three):
1. **Sequence stream** (per-voice, ptr table `$1545`, 6 bytes/subtune): `$00–$3F`
   loop/restart, `$40–$5F` repeat count, `$60–$7F` set waveform index, `$80–$BF` set
   **arp/swing param** (the auto-swing/beat-accent), `$C0–$FE` set filter/portamento,
   `$FF` end/advance.
2. **Wave-programs** ("patterns", 8 ptrs `$154B`): hi-2-bit dispatch — `$00–$3F`
   (dur, instrument) full inst load; `$40–$7F` (dur, ?) pulse rate; `$80–$BF` (dur, note);
   `$C0–$FE` (dur, freq-lo, freq-hi) direct freq override; `$FF` end.

**Instruments**: 8-byte records at `$15FB`, index = inst×8. Byte[4]=`$FF` suppresses the
filter write; else `STA $D416`. Editor exposes: `wave_on|wave_off|effect|ADSR|pulse|effect|
settings|filter` with settings `$81`=beat-accent, `$40`=appreq (arp?).

**Editor model** (F7 text): 3 tracks of block-indices/commands (`$80-$BF` transpose,
`$C0-$DF`/`$E0-$FD` sound ±, `$FE` stop, `$FF` restart); ≤32 blocks; block = ordered
`DUR.xx`(first) / `SND.xx` / `GLD:xx,y` / note / `END`. Player features (Falco interview):
2×/3×/4× speed, hard+soft osc restart, sample play, advanced PWM, voice-3 feedback to
filter, auto-swing, beat accenting.

## Corpus shape (209 tunes — all PSID v2, 87% single-subtune)

The address spread is build/relocation, dominated by canonical $FFF/$1000:

| Cluster | init | play | Count | Users |
|---|---|---|---|---|
| A canonical | $FFF/$1000 | $1003 | 120 | EVS, Falco, MCA, Merman, JVD, Schutten |
| A3/A4 | $FEC/$FFA | $106C/$1081 | 11 | EVS 1990 / HeatWave early |
| B ($1670) | $166A | $1676 | 15 | HeatWave EA series + Exile |
| C ($E0xx) | $E000 | $E003 | 4 | Ouwehand Dutch Breeze, Siebold |
| D ($F900) | $F900 | $F903 | 2 | EVS Dolphinforce (1988, earliest) |
| E scattered | various | various | 68 | game scores, audit |

Span 1988–2025; peaks 1991 (40) and 2000 (18, Merman batch). Composers: the 20CC group
(52), MCA/Michiel van den Bos (20), Reyn Ouwehand (19, Falco helped personally), Schutten/
Junebug (18), Merman/Andrew Fisher (18), HeatWave (14). No HVSC DOCUMENTS/STIL mention.

## What remains (migration-phase RE)

Player flow + data hierarchy are mapped; the effect-algorithm details are the open work:
- **Disassemble a canonical Variant-A tune** (recommended: `MUSICIANS/0-9/20CC/van_Santen_Edwin/
  Vlindertjes.sid`, play $106C; the `src/` hex map is a head start) to pin: the **auto-swing**
  + **beat-accent** algorithms (which registers, how much — the `$D418`-×3 and `$80–$BF`
  seq param), the `appreq`/`$40` and `$81` settings semantics, the `GLD` glide params, and
  the exact track-command ranges.
- **Variant B's instrument-in-note-pitch** packing — a second extraction path (35 SIDs).
- **Audit the 68 scattered-address tunes** (mostly Ouwehand game scores) before counting them.
- No CIA confirmed → flat Mode-1 path (but 2×/3×/4× multispeed exists — verify whether any
  carry PSID `speed`≠0 → `--writelog-per-irq`).

## Top leads

1. ~~F7 in-tool feature docs~~ — **OBTAINED** (`src/20CC_Composer_Instructions.txt`).
2. **Falco Paul's pages/interviews** — he's a reachable scene/internet figure; may have more
   player-internals detail (the "fastest routine" writeup).
3. CSDb #10741 editor disk (already partly fetched) + the bundled FC relocator — for the
   exact instrument/effect byte semantics.

Full provenance in each file + `provenance_log.md`.
