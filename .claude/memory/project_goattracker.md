---
name: project_goattracker
description: "GoatTracker family migration state — V1 (original 1.x) is the active target; research done, disassembly next"
metadata: 
  node_type: memory
  type: project
  originSessionId: c0742216-af17-42da-9a5c-fa8ae0d40172
---

GoatTracker = 2nd-largest HVSC family after DMC: **8,670 SIDs** (7,311 V2 +
1,359 V1). Family-doc state `OK`. **Active focus: V1** (the *original*
GoatTracker 1.x by Cadaver, NOT GoatTracker 2 — user-directed 2026-06-29).

**Status: RESEARCH + RE_NOTES + disassembly-annotation DONE; extractor next.**
`pipelines/goattracker/v1/` has `disassembly.s` (annotated, canary Joker) +
`RE_NOTES.md` (full engine semantics + data layout + extraction plan). No
extractor/composer/config yet. **Layout VALIDATED against Joker**: instruments
@ $1553 (8-byte stride), wavetbl $157a / notetbl $158a, patttbl lo/hi $159b/$159e
— matches v1_player1_v153.s exactly. **Representation DECIDED** (ledger C14):
per-row commands → `NoteRow.fx_flags` strings (FC precedent), NO schema change;
arp is a per-row musical fx, not a new kind.

## V1 at a glance (the migration target)
- 1,359 SIDs; **1,347 single-SID** + 12 dual-SID/2SID (exclude). **95.6%
  single-subtune.** **78% load $1000**, rest relocated ($0ff6/$0ffa/$3000/
  $c000…) → needs a relocation factory (FC/DMC pattern).
- **ONE dominant player body** (the 639 "distinct" 48-byte prefixes are mostly
  the per-tune freq table; the player-code stub is near-universal) → single
  composer covers most, like FC standard.
- GoatTracker player **lineage**: stride-7 channel state, global filter written
  at frame start ($D416/$D417/$D418), 1-based table pointers, multispeed via
  self-modified `LDY` operand, **deferred first-play init** (init stashes
  subtune×2 into the play routine; real setup runs on first play()). The V2 docs
  (`player_algorithm.md` etc.) are a **Rosetta stone**, not authoritative.
- **V1-defining diffs vs V2** (full table in `docs/v1_README.md`): arpeggio
  pattern command `0XY` (root→+X→+Y semis, every tick, X≥8=half-speed, shares
  vibrato counter; REMOVED in V2); per-instrument **inline** wave table;
  **4-scalar per-instrument pulse** (no step table); **filter table from V1.4+**
  (64×4 bytes; V1.25 none); **no speed table**; 3-byte variable pattern rows,
  8 commands packed in 3 bits; max 31 instruments; testbit hard restart from V1.5.
- Song file ID is **`GTS!`** — the old research.md "GTS3/GTS4" claim was WRONG
  (GTS3/4 are early GT2); corrected 2026-06-29.
- **Audio sub-versions inside one sidid class** (binary-detect, not sidid):
  pre-V1.3 / V1.3-1.4 / V1.5+; cmd meanings shifted V1.25↔V1.53.

## Key assets (all under pipelines/goattracker/docs/)
- **Primary 6502 player source** in `docs/src/`: `v1_player1_v153.s` (V1.5 std —
  the disassembly reference), `v1_player1_125.s` (V1.25), `v1_gmusic_v153.s`,
  `v1_readme_125/153.txt` (manuals). Plus GT2's `gsong.c` GTS! importer
  (`deprecated/gt2_pipeline/GoatTracker_2.77/src/gsong.c`).
- Index: `docs/v1_README.md`; provenance: `docs/v1_provenance_log.md`.

## Next steps (extractor phase — start here)
1. **Extractor** (`v1/extract/engine_model.py` + `to_usf.py` + `config.py`):
   dataflow-read the table bases from the player's `lda <tbl>,Y` operands at
   fixed offsets relative to play (robust across V1.5 tunes), + song globals
   (gatetimer, HR AD/SR) from patched immediates. Parse instruments (8B),
   wave/note programs (per-inst slice via inst.wave + loop), filter table, song
   table→orderlists, pattern table→patterns. Emit USF. See RE_NOTES §2,§8.
2. **Composer**: adapt the free-licensed `v1_player1_v153.s` into our xa65
   engine, emit data tables from USF. (Each family has its own composer; this is
   fine — engine-blindness is about not content-sniffing WITHIN one composer.)
3. **Verify** canary writelog (instruction-sequence exact,
   [[feedback_verification_modes]]); then reloc factory + stratified-subset
   iteration; full batch at closeout (the [[project_fc_fingerprint_and_standard]]
   playbook). Mirror DMC infra: composer_asm.py + v4/factory.py + extract/.

See [[feedback_check_existing_engine_docs]], [[feedback_residue_triage_order]],
[[project_fc_fingerprint_and_standard]] (the closest analog: one vanilla player +
reloc factory + wide batch).
