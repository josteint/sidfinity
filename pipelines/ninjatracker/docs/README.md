# NinjaTracker player — research docs index

**Engine family:** `ninjatracker` (sidid labels **NinjaTracker_V1.x** / **NinjaTracker_V2.x**)
— a minimal native C64 tracker by **Lasse Öörni ("Cadaver")** of **Covert Bitops**, the
same author as GoatTracker. Designed for **minimum rastertime** (game music; V1 ≤ ~11
rasterlines, V2 leaner still). **111 HVSC SIDs** (18 V1 + 93 V2), mostly Cadaver's own
games (Metal Warrior 4, Hessian, Steel Ranger) and modern commercial C64 titles by Sarah
Jane Avory (Zeta Wing, Sam's Journey, Briley Witch Chronicles) and others.

Research sweep: **2026-06-16** (research-player skill; all six clusters completed). State
→ **OK**. **This is a best-case engine: full player source is public and saved locally —
the format is essentially completely specified, no reverse-engineering needed.**

## Headline — the holy grail is in `src/`

The player source ships with the distribution (cadaver.github.io / Covert Bitops) and the
GoatTracker→NinjaTracker converter is open. Both are saved under `src/`:

| `src/` file | what it is |
|---|---|
| **`nt2play_v204.s`** (710 ln) | **V2.04 player source** — the canonical V2 engine (DASM, Cadaver 6/2013). Exact playback logic, table interpreters, hard-restart, relocation fixups. |
| **`ntplay_v1.s`** (596 ln) | **V1.1 player source** — the (incompatible) V1 engine. |
| **`gt2nt2.c`** (1926 ln) | **GT2→NT2 converter** — *writes* the NT2 binary, so it is the authoritative byte-layout spec (section order, header, RLE). |
| `nt2player_editor_v204.s`, `nt2songdata_v204.s`, `nt2var_v204.s` | editor-embedded player, song-data save layout, memory map / relocation tables. |
| `nt2play_gt2nt2.s` | the player variant bundled with the converter. |
| `readme_v204.txt`, `readme_v1.txt`, `readgam_v1.txt`, `readme_gt2nt2.txt` | distribution docs — editor keybindings + format/usage notes. |
| `sidid_signatures.txt` | sidid.cfg blocks for V1 + V2 (they share no bytes — V2 is a full rewrite). |
| `archive_*` duplicates | same sources fetched independently by the archive cluster (distinct provenance headers); the un-prefixed files above are canonical. |

Analysis/summary docs (the cluster outputs):

| file | content |
|---|---|
| **`format_spec.md`** | **Synthesized byte-level spec** — `.sng` on-disk format (magic `N2`, `$BF` RLE), gamemusic binary (6-byte size header + packed sections), pattern/orderlist/table/command encodings, hard-restart model, V1↔V2 differences. Start here. |
| `csdb_findings.md` | Full release history (V1.0 2002 #7206 → V2.04 2013 #119721), converter releases, CSDb limits/notes. |
| `github_findings.md` | Where each source was obtained; relocation/fixup model; V1↔V2 source-level deltas. |
| `forum_findings.md` | Table/pattern encodings, hard-restart sequence, player API, GT2→NT2 conversion incompatibilities. |
| `hvsc_findings.md` | PSID-header survey of all 111 SIDs (V1 vs V2 clusters), sidid V1/V2 anchors, STIL. |
| `archive_findings.md` | Covert Bitops homepage history, release/changelog, doc text. |
| `research.md` | Original stub (pre-existing; kept). |

## Format at a glance (confirm against the source — it's all there)

- **API:** `nt_newmusic(A=lo,X=hi)` relocates (patches **21 self-mod fixups**), `nt_playsong(A=subtune)`, `nt_music()` per frame. V2 uses only **2 zero-page bytes**; V1 uses 5.
- **Gamemusic binary:** 6-byte header `{wavetbl, pulsetbl, filttbl, cmd, legatocmd, patttbl}` sizes, then packed sections. Player code is NOT stored with the music.
- **Patterns:** `raw = (note_index<<1) | has_new_cmd`; sentinels `$00` end, `$01` cmd-only, `$04` keyon, `$08` keyoff, notes `$18`–`$BE` = C-1..B-7; optional duration byte `≥$C0` (3–65 frames). Command `$01–$7F` normal / `$81–$FF` legato (skips hard-restart + gate keyon).
- **Orderlist:** `$00` loop, `$01–$7F` pattern#, `$80–$BF` transpose down, `$C0–$FF` transpose up.
- **Tables (2-column in V2):** Wave left byte `$00–$8F` waveform+arp / `$90–$BF` delay / `$C0–$DF` vibrato / `$E0–$FE` slide (stops at target) / `$FF` jump. Pulse/filter: high bit = signed-modulate vs absolute-set, `$FF` jump.
- **Commands (= instruments):** AD, SR, wave-ptr, pulse-ptr, filt-ptr. Hard-restart (V2.03+) = 2 frames + 1 silent frame ("hifi").
- **Limits:** ≤16 subtunes (some HVSC tunes use far more via re-init — Soul_Force 43), 127 patterns, 127 commands, 255 table entries. All HVSC tunes **VBL/50 Hz** (no CIA). `play=init+3` canonical; relocation first-class. Two `play=$0000` data-only members need special handling.
- **V1 vs V2 are distinct engines** (full rewrite): V1 = 5 ZP bytes, 3-column tables/patterns, opposite transpose sign, no commands/legato/filter-table/hard-restart; V2 added all of those + 2-column tables + 21-fixup relocation.

## Gap analysis

- **Nothing material is missing for the migration.** Player source (V1 + V2) + the
  format-writing converter + distribution docs are all in `src/`. The migration can read
  byte offsets and per-frame SID behaviour directly from `nt2play_v204.s` / `ntplay_v1.s`
  and validate the binary layout against `gt2nt2.c`.
- **Minor confirm-from-binaries items:** the two `play=$0000` data-only SIDs; the handful
  of tunes exceeding 16 subtunes (re-init mechanism); exact V1 SFX byte order (`{PW,AD,SR}`
  vs V2 `{SR,AD,PW}`) — all answerable from the saved sources.
- **No online gaps.** No further web research warranted.
