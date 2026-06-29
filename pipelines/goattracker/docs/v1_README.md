# GoatTracker **V1** documentation index

Research wave 2026-06-29 (`research-player` skill). This indexes the
**V1-specific** docs. The non-`v1_`/non-`v1` files in this dir
(`player_algorithm.md`, `player_variables.md`, `table_algorithms.md`,
`gt2_data_layout.md`, `gt2_player_versions.md`, `research.md`) describe
**GoatTracker 2** and are kept as a Rosetta stone — V1 shares the GT player
lineage but is the older relative.

## TL;DR — what V1 is

The **original GoatTracker 1.x** by Cadaver / Covert Bitops (HVSC engine
`GoatTracker_V1.x`, **1,359 SIDs**; 1,347 single-SID + **12 dual-SID/2SID to
exclude**). Song file ID is **`GTS!`** (NOT GTS3/GTS4 — those are early GT2).
Same 3-voice sequential frame loop + global filter + 1-based table pointers +
deferred first-play init as GT2, but with these **V1-defining differences**:

| Axis | V1 | GT2 (for contrast) |
|---|---|---|
| Arpeggio | **pattern command `0XY`** (root → +X → +Y semitones, runs every tick; X≥8 = half-speed; shares the vibrato counter) — REMOVED in V2 | wave-table only |
| Wave table | **per-instrument, inline** (waveform+note pairs); packer splits to `mt_wavetbl`/`mt_notetbl` | one **global** wave table |
| Pulse | **4 per-instrument scalar params** (init PW, speed, lo-limit, hi-limit), direction-bouncing — no step table | pulse step-table |
| Filter | **table from V1.4+** (64 × 4 bytes: ctrl, type/vol, freq/speed, next-step); step 0 = funktempo hack. V1.25 had NO filter table | filter step-table |
| Speed table | **none** — vibrato/portamento speeds inline in the data byte | explicit speed table |
| Pattern row | **3 bytes, variable** (note-only rows collapse); 8 commands packed into 3 bits of the instr byte | fixed 4-byte rows, 16 commands |
| Instruments | **max 31** (5-bit field) | max 63 |
| Hard restart | global ADSR pack-time param (V1.25 AD/SR=0); **testbit method from V1.5**, per-instrument configurable | per-instrument |

**Audio sub-versions inside the single sidid class** (indistinguishable by
sidid; must be detected from the player binary): **pre-V1.3** (no filter table,
no orderlist transpose/repeat), **V1.3–V1.4** (table filter + transpose/repeat),
**V1.5+** (testbit hard restart, delayed wavetable `$01-$08`, master fader).
Command meanings shifted between V1.25 and V1.53 (e.g. cmd 2 = filter-cutoff-speed
in V1.25 → portamento-down in V1.53).

## Files (V1)

| File | What it covers |
|---|---|
| `v1_github_source.md` (693 ln) | GT2's `gsong.c` GTS! importer decoded byte-by-byte + V1 player-source walkthrough; per-instrument struct, arp, wave, pulse, filter, pattern. **Most complete.** |
| `v1_archive_downloads.md` (541 ln) | Verbatim format specs from the V1.25 + V1.53 readmes; V1.25-vs-V1.53 diffs; player-loop structure; V1-vs-GT2 table. |
| `v1_forums_wikis.md` (546 ln) | Cross-checked semantics from readmes + player asm + scene discussion; **6 OPEN questions flagged for binary RE.** |
| `v1_csdb_covertbitops.md` (322 ln) | CSDb/Covert Bitops version history 1.0→1.6, format lineage GTS! → GTS2 → GTS3 → GTS4 → GTS5, command-set evolution. |
| `v1_hvsc_sidid_versions.md` (330 ln) | sidid fingerprint anatomy, the two 2SID sub-signatures, HVSC counts, sub-version landscape. |

## `docs/src/` — primary source (the ground truth for the migration)

- `v1_player1_v153.s` — **GoatTracker V1.5 standard playroutine** (full 6502, virtual-address map at top). **Primary reference for `disassembly.s` annotation.**
- `v1_player1_125.s` / `v1_player2_125.s` — V1.25 standard + game playroutines (pre-filter-table era).
- `v1_gmusic_v153.s` — V1.5 game playroutine (SFX + relocatemusic).
- `v1_player2_v153.s` — V1.5 relocation stub.
- `v1_readme_125.txt` / `v1_readme_153.txt` — official manuals (format spec in §6).

## Gaps → defer to the migration (binary-RE) phase, NOT more research

- Which player **sub-version** dominates the 1,359 HVSC V1 SIDs (pre-1.3 / 1.3-1.4 / 1.5+) — decide the canary + composer baseline by fingerprinting the binaries.
- The 6 OPEN questions in `v1_forums_wikis.md` (half-speed arp counter exactly, V1.25 arp logic, filter application order, packed wavetable index encoding) — settle them against `v1_player1_v153.s` + a real SID writelog during disassembly.
- Stereo/2SID variant (`gstereo.zip`) — only if the 12 dual-SID tunes come into scope (currently: exclude).
