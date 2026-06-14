# Cyberlogic SoundStudio (CSS) — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

Cyberlogic SoundStudio (CSS), a German-scene C64 SID editor — **player code by Oliver
Klee ("Odi")**, **music/data/concept by Sascha Nagie ("celticdesign")**, group **Demons
of Sound**; CSS V4.0, 1991–92. 196 HVSC #84 tunes; 0 migrated. Player base $1000, play
$1003. No public source / format spec / manual. Author split confirmed by the embedded
string `"MUSIC SASCHA NAGIE, PLAYER O.KLEE"`.

**Richest primary source without RE**: Oliver Klee wrote **first-person STIL comments on
~14 HVSC tunes** explicitly naming the CSS tool (filter-byte quirk, the CSS packer, a
low-raster player variant, portamento/arpeggio/PWM effects) — read `STIL.txt` for these.

## File index

| Topic | File | Reliability |
|---|---|---|
| Write model + binary layout + the $6000 cluster split | `cluster_write_model_and_binary.md` | secondary (binary) |
| ↳ early-engine byte map | `src/v_arc_early_bytemap.md` | primary |
| Editor + format + author confirmation | `cluster_editor_and_authors.md` | secondary |
| HVSC corpus / address clusters / scene + STIL quotes | `cluster_corpus_and_scene.md` | primary (DB+STIL) |

(No source/spec was published; structure is from byte-stable binary inspection + the STIL
first-person notes. CSS is self-contained — each SID embeds its own player + data.)

## What's solved

**Binary layout** (self-contained; `$1000` base, 133/196):
- 6-entry jump table at load (+$00 init, +$03 play, +$06/$09/$0C/$0F others); ASCII
  composer+player string at `load+$12`; runtime state `$1032–$10A0` (zeroed on init);
  player code; then data tables; then pattern streams.
- **13 parallel 32-entry instrument tables** `$17D8–$1916`; a **95-entry freq table**
  `$1928/$1987` that **doubles as the pattern-pointer table** (same bytes, dual-indexed).
- Section architecture: 6 metadata arrays `$1C0E–$1C5F` + 3 voice→pattern tables
  (`$19E6`/`$1A9E`/`$1B56`). Pattern streams from `$1D0E`, terminated by `$2A $2A $2A`
  (`"***"`, the `*** END OF MUSIC ***` marker).

**Per-frame write model** (voices **X=2,1,0**, V3 first):
per voice `D401 (freq-hi) → D400 (freq-lo) → D402 (PW-lo) → D403 (PW-hi) → D405 (AD) →
D406 (SR) → D404 (ctrl/gate)` — **freq-hi-before-lo is unusual** (most Hubbard-era players
write lo first; a useful fingerprint). Global once/frame: `D416 → D417 → D418`, with the
**`$D418` value from a per-section table `$1C5E[section]`** (not a fixed global) — likely
the source of the STIL-noted filter/volume quirk.

**Note encoding**: 1 byte/event — **upper nibble = instrument index** (decoded by the
4×`LSR` the sidid sig anchors on, hit at ~$14D5/$14D5 ADSR counter), lower nibble = pitch
step; interleaved with duration + command bytes; patterns delimited within the section
tables.

**Effects** (named in STIL / partly decoded): portamento, arpeggio, PWM; in-stream opcodes
`$80–$FB` (arp/vibrato/tie/porta — exact map OPEN), `$FC/$FD` args (loop/transpose — OPEN).

**The `$6000` cluster (13 SIDs) is TWO unrelated engines**:
1. **SID*Nation IV–XI** (Nagie, 2013–14): the newer `celticdesign` engine relocated to
   $6000 — same write order + sidid, but init extracts instrument via **`LSR`×6** (not ×4).
2. **Timeout series** (The Blue Ninja, 1992): the **early Odi player** relocated; string
   `"MINIPLAYER3.0 91 BY TBN"`; 4-entry jump table — an earlier engine generation.

**Player is NOT frozen** — it evolves per composition. At least two generations: Odi's
original (1991–92) and a 1996 revision (string `"LARS HUTZELMANN'96 PLAYER O.KLEE"`).

## Corpus shape (196 tunes — all PSID v2, all VBL/speed=0, all 4 German composers)

| init / play | Count | Notes |
|---|---|---|
| $1000 / $1003 | 133 | canonical CSS |
| $6000 / $6003 | 13 | TWO engines (celticdesign-2013 + Odi-early-Timeout) |
| $0FF0/$0FF4/$0FF6 / $1003 | 16 | near-$1000 init stub (Nagie packing variant) |
| 14 scattered singletons | 14 | game OSTs (Blue Ninja for Protovision), relocations |

Composers: Sascha Nagie (120, 61%), X-Radical/Frank Schanzenbächer (28), The Blue Ninja/
Lars Hutzelmann (24, extended CSS as a Protovision game engine to ~2005), Odi/Oliver Klee
(24). Span 1991–2021 (two peaks: 1991–93 DOS era, 2013–16 Genesis Project). STIL.txt has 93
entries across these composers; no CSS doc in HVSC DOCUMENTS.

## What remains (migration-phase RE)

Player flow + table layout are mapped; the effect-opcode + section details are the open work:
- **Disassemble one canonical $1000 tune** (the `src/` byte map is a head start) to decode:
  the **`$80–$FB` in-stream effect opcode map** (arp/vibrato/tie/porta), the `$FC/$FD`
  argument semantics, the **section-advance trigger** (`$1035` — voice-1-done vs all-done),
  and the `$1C0E` SMC sentinel (rewrites a CPY operand at runtime — per CORE TENET, emit
  clean code for the same writes, don't reproduce the SMC).
- **The freq/pattern-pointer table dual-use** — confirm the dual indexing in the extractor.
- **Multi-generation handling**: Odi-early (LSR×4, $D418-per-section) vs celticdesign-2013
  (LSR×6) vs the 1996 revision — at least 2-3 layout variants the extractor keys on.
- No CIA in the DB schema — read PSID `speed` directly to confirm all VBL.

## Top leads

1. **`Soundstudio.prg`** (zimmers.net FUNET editors, 26.8 KB, dated 12/11/92 = the CSS
   Preview) + **`css.d64`** from CSDb #170632 — the editor binary; its data-entry code is
   the closest thing to a format spec. Disassemble during migration.
2. **STIL.txt** (local HVSC) — Oliver Klee's 14 first-person CSS comments; re-read for the
   effect catalogue before RE.
3. **Contact celticdesign / Oliver Klee** on CSDb — both still active; could supply the
   effect map or source directly.

Full provenance in each file + `provenance_log.md`.
