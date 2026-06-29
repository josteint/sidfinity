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

## Next steps (extractor phase)
1. **Extractor binary→model DONE + validated** (`v1/extract/engine_model.py`):
   `parse_sid` + `detect_layout` (anchor/cluster table-base + globals detection,
   variant-tolerant) + `extract` → `V1Song` (orderlists, patterns, instruments
   + wave programs, filter table). Validated on Joker/Imdunk/Menace47. KEY decode
   fixes already in: instbase via B9-operand clustering (PHA/PLA variants break
   single anchors); note-without-cmd = `b-$60` (carry-clear sbc, NOT b-$5f);
   filttbl anchor `A8 B9 ?? ?? F0`; song(diff-3)/patt pair by code-order. Run
   `python3 pipelines/goattracker/v1/extract/engine_model.py` for the smoke dump.
   NOTE: Xetris-class (load $4000, older/gamemusic variant) fails the $fc/$fd
   pair anchor → factory concern for later.
   **NEXT: `to_usf.py`** (model→UsfFile): per-row cmds→fx_flags (C14), inst→
   PwmConfig/waveform/wave_freq/loop + FilterProgConfig, note $5E=keyoff/$5F=rest,
   duration from tempo. Then `config.py`.
2. **Composer** (`v1/composer.py`): data-emission + xa65 + PSID harness DONE
   (assembles, builds a 2592-byte SID for Joker; `build_v1_sid`/`compose_v1_asm`).
   Data layout chosen: separate per-field instrument arrays (instad/instsr/...
   indexed by 1-based id, NO *8), wave arrays in GT shape (wctrl/wnote + $FF
   marker + relative loop tgt=loop+2 so waveexec is a faithful v153 transcription),
   freq table = baked constant, song/pattern pointer tables (per-voice slot base).
   `_encode_pattern`/`_fx_to_cmd` invert to_usf. **ENGINE IS STUBBED** (`_ENGINE`
   = init/play rts) — the clean v153 transcription is the NEXT focused task:
   filter exec (always writes $D416/17/18), 3-voice loop (X=0/7/14), deferred
   first-play init via RAM flag, tick/funktempo, tick0 seq+newnote, waveexec,
   continuous fx (arp/porta/toneporta/vibrato), pulse bounce, gatetimer+HR,
   loadregs. RAM globals (no SMC), rts-trick cmd dispatch, constants
   GATETIMER/HR_AD/HR_SR/DEFTEMPO. Reproduce write OUTPUTS incl. $D404=$09 testbit.
3. **Verify**: build canary -> `writelog_capture` both -> `compare_instruction_stream`
   ([[feedback_verification_modes]]); iterate first-divergence. Then grammar
   extension for arp/vibrato fx (text round-trip), factory, wide batch.
Then reloc factory + stratified-subset iteration; full batch at closeout (the
[[project_fc_fingerprint_and_standard]] playbook). Mirror DMC infra:
composer_asm.py + v4/factory.py + extract/. Harness refs: `src.composer_runtime.
xa65.assemble`, `.psid.build_header`, `pipelines.hubbard.verify_cycle`.

See [[feedback_check_existing_engine_docs]], [[feedback_residue_triage_order]],
[[project_fc_fingerprint_and_standard]] (the closest analog: one vanilla player +
reloc factory + wide batch).
