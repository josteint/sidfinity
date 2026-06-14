# DMC V5 — RE notes (Phase A complete)

Rep: `DEMOS/G-L/Katusha.sid` (family-3, 1461 + family-5 sibling 34 = the
dominant V5 player). Phase A (full disassembly + annotation) DONE
2026-06-14 → `pipelines/dmc/v5/disassembly.s`. Scope + plan in
`pipelines/dmc/v5/SCOPE.md`; format research in
`pipelines/dmc/docs/dmc_v5_{format_notes,docs_original}.md` +
`dmc_sector_commands.md`.

## ✅ Resolved in Phase A (all in disassembly.s header)

- **Sector command byte map** (the flagged unknown): notes `<$80`;
  commands `$F1-$FE` (SRR/ADR/VOL/gate×2/FD-/FD+/FRQ/FLT/SLD/GLD/SND/DUR/
  GATE) + `$FF` END. Track (orderlist): `$FC/$FD` transpose, `$FE`
  voice-end, `$FF pp` loop.
- **8-byte instrument** order confirmed from runtime: AD, SR, WV, PU, FL,
  vib-delay, vib-speed, vib-width(&$07).
- **3 programmable 2-byte tables** (wave/pulse/filter), `$90`=loop;
  filter is **voice-3 only** (`CPX #$02` @ $1496). Vib step = base-note
  freq << width. Full 11-bit filter cutoff ($D415 lo + $D416 hi).
- **Per-voice write order** (sid_write $16E6): freq lo/hi, PW lo/hi, ctrl
  (AND gate mask). Global $D415/$D416 once per play; $D418 in fade;
  $D417 at FLT cmd. Hard restart via gate-mask $F6 + SR=0 (gate_logic).

## Phase B (extract) — operand sites for dataflow

The packer places the data tables per song (like V4 — these addresses
are operand-patched; Katusha's values are the disassembly's). The extract
reads the base of each table by dataflow from these CODE sites (operand
lo-byte address = the listed PC + 1):

| table | Katusha addr | read sites (PC) |
|---|---|---|
| orderlist ptr | $1878 | $1046, $1059 (init) |
| sector ptr lo/hi | $196E / $1972 | $114E / $1153 |
| instrument | $1976 | $12CB/$12CF (note_on), $134F.. (note_init2) |
| freq lo/hi | $170F / $176F | $13A5/$13AB, $168C/$1692, $153B/$1541 |
| wave ctrl/freq | $199E / $19AB | $1385/$165E, $19AB reads alongside |
| pulse lo/hi | $19B8 / $19BF | $13C0/$13C9, $143C/$1450 |
| filter lo/hi | $19C6 / $19C7 | $13EF/$13F5, $149D/$14B1 |

NB confirm whether WV/PU/FL instrument pointers are entry indices or
need ×2 — the player uses them as ENTRY indices into the 2-byte tables
(reads `$199E,y` / `$19AB,y` with y = the pointer, not ×2). So pointers
are entry indices; the table arrays are split lo/hi (parallel), not
interleaved 2-byte records.

## Phase B/C open items

1. Packed memory map for ARBITRARY members (Katusha's table addresses are
   operand-patched — generalize via the dataflow sites above; build a
   `dmc_v5_config` factory like V4/family-2).
2. USF schema: the 3 programmable tables (content-by-reference), fade
   (FD+/-), ADR/SRR live register-sets, full filter cutoff, vib-step=
   freq<<width. Reuse `_offtable_check` pattern.
3. NEW V5 composer (the V4 composer does NOT apply). Write-log-first on
   Katusha. Verdict: `verify_dmc` (engine-neutral, reuse as-is).
4. **family-4 branch (686, Jupiter41, play +$95):** distinct (~0.31
   Jaccard) — diff its disasm against family-3's once family-3 is FULL.

## ✅ Phase B (extract) — DONE + validated (2026-06-14)

`pipelines/dmc/v5/config.py` (DMCV5Config, the operand sites above) +
`extract/engine_model.py` (`extract(cfg) -> V5Model`). Lifts Katusha to
a complete structured model — freq tables, 5 instruments (8-byte),
wave(13)/pulse(7)/filter(1) tables, speed/mastervol, 3 orderlists (with
loop), 4 sectors decoded into event streams. Region sizes from address
deltas (instr|wave_ctrl|wave_freq|pulse_lo|pulse_hi|filter_lo|filter_hi).
The sector-command decode (Phase-A byte map) is implemented + validated:
sectors lift to sensible `dur/snd/note/gate/...` event streams.

Validated on Katusha:
  sector 0: dur 04, snd 00, a note+gate melody
  sector 1/2: dur 02, snd 01/02 fast arps
  sector 3: dur 04, snd 03 melody with rests

## ✅✅ Phase C (composer) — Katusha FULL (2026-06-14)

`pipelines/dmc/v5/composer_v5.py` — a clean re-authored V5 engine
(labeled routines + relabeled state block) driven by the extracted song
data (orderlists/sectors/instruments/freq/tables emitted via labels;
index-based, relocatable). Katusha verifies instruction-sequence exact
at full songlength (trichotomy is_full + state_match, 97955/97955 play
writes; find_first_divergence 98880/98880 = 100%).

The write-log loop (key fixes, each via find_first_divergence + py65):
1. init clears state BEFORE loading track pointers (was wiping them).
2. prime file-image leftovers $1015/$1016/$1017 (filtmode/cutoff).
3. voice tick decs durctr every tick (removed an extra guard).
4. step_commit (gate-off/slide/tied-note) falls through to wave_step +
   writes the steady frame (note_on instead rts's — note_init2 next).
5. pulse_run ALWAYS advances — PU=0 = "no restart", NOT "no run" (the
   running-pulse-program semantics). This was the last fix to 100%.

NOTE — composer keeps the V5 state at the original absolute addresses +
data via labels; it's a faithful clean re-author (the per-frame logic
must match to match the write stream). NOT yet through USF (prototype
extract->model->composer); the USF layer + schema co-design is a
follow-up (the model IS the musical content, so serialization is
mechanical).

## NEXT — USF layer (designed 2026-06-14; implement next)

The composer currently reads V5Model directly (prototype). To satisfy
"always through USF", add `extract -> to_usf -> UsfFile -> from_usf ->
V5Model -> build_v5_sid` (composer UNCHANGED — it keeps reading a model).
Design (re-read docs/usf_representation_principle.md before coding):

REUSE existing USF types (no new schema):
- AD/SR -> `Instrument.adsr`; vib delay/speed/width -> `VibratoConfig`
  (onset / period / depth — parametric).
- Per-instrument WAVE program: decode the wave-table slice from the
  instrument's wave_ptr (follow $90 loops, like V4 `_slice_wave`) into
  `waveform`/`wave_freq`/`loop`. DECODES AWAY the wave_ptr (§7 forbids
  the `*Ptr` shape). Drum = test-bit ($08) entries -> abs freq-hi
  (`effects: drum` per step or the FC dual-table convention).
- Sectors -> `Pattern`/`NoteRow`: note = pitch; the 14 commands ->
  `fx_flags` (dur/snd/gate/gate_tie/fade_in/fade_out/frq/flt/adr/srr/
  vol/slide/glide). Orderlists -> `VoiceBlock.orderlist` (+ transposes,
  loop). speed -> tempo; master_vol + $1015/$1016/$1017 leftovers ->
  `init.sid` priming (filter mode + cutoff lo/hi).
- freq table -> `freq_table` (per-tune tuning).

NEW musical-content fields (principled per Rule 2 — sweep = content,
interpreter stays in engine; NOT a kind-index):
- per-instrument PULSE sweep program: decode the pulse-table slice from
  pulse_ptr (start pair + (add,count) segments + $90 loop) into an inline
  step list. Decodes away pulse_ptr.
- per-instrument FILTER sweep program: same shape (voice-3-only).
  Decodes away filter_ptr.
  Candidate schema: extend `PulseProgConfig`/`FilterProgConfig` or add a
  small `sweep { start, steps:[(add,frames)], loop }` form. Run the §9
  4 tests + grep (`*Ptr`, `*Kind`) before committing.

`from_usf` rebuilds the V5Model (re-pack per-instrument programs into the
shared wave/pulse/filter tables + reassign pointers — the inverse of the
decode; the composer reads the model). Verify Katusha FULL through USF
(should reproduce the current 100%). THEN the factory + wide batch below.

## THEN — factory + wide batch
`dmc_v5_config` factory (jump-table detect init+$40/play+$A1, the
operand sites above, carved reference) + reuse tools/dmc_family_batch.py
over family-3/5 (1495). Then the family-4 branch (686, play +$95).

## (historical) Phase C plan

A NEW hand-authored V5 engine (the V4 `composer_asm.py` does NOT apply —
8-byte instruments, table-based pulse/filter, full filter cutoff, the
14-command sector model). Must be RE-AUTHORED clean (the tenet forbids
emitting verbatim/relocated player bytes). USF schema co-designed
write-log-first: the 3 programmable tables (content-by-reference), fade,
ADR/SRR, full cutoff, vib-step=freq<<width. Verdict: `verify_dmc`
(engine-neutral, reuse). Then factory + wide batch (family-3/5, 1495),
then the family-4 branch.
