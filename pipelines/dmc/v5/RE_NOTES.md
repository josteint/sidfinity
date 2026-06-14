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

## ✅✅ USF layer — DONE (2026-06-14): Katusha FULL through USF

Pipeline is now `extract -> to_usf -> UsfFile -> from_usf -> V5Model ->
build_v5_sid` (composer UNCHANGED — model-driven). Katusha verifies
instruction-sequence exact THROUGH USF (trichotomy is_full + state_match,
97955/97955 play; find_first_divergence 98880/98880 = 100%). Verdict:
`pipelines/dmc/v5/verify_v5.py:verify_v5` (build_from_cfg goes through a
real .usf file). Test: `tests/test_dmc_v5_usf.py`.

Files: `extract/to_usf.py` (model_to_usf + write_v5_usf), `from_usf.py`
(usf_to_model), `verify_v5.py`.

REUSED existing USF types:
- AD/SR -> `Instrument.adsr`; vib delay/speed/width -> `VibratoConfig`
  onset/speed/amplitude (inverted in from_usf).
- WAVE program: `_slice_wave` follows the V5 $90 marker (ctrl==$90 -> the
  parallel freq byte is the ABSOLUTE loop target) into
  `Instrument.waveform`/`wave_freq`/`loop` — decodes away wave_ptr.
  `wave_freq` kept RAW (each step's melodic-vs-abs mode is its own ctrl
  bit 3, visible in `waveform`). Idle walk (table[0]) -> `wave_programs[0]`.
- freq table -> `freq_table` (96 lo + 96 hi). speed -> tempo. master_vol +
  $1015/$1016/$1017 leftovers -> `init.sid` (master_vol +
  InitFilter cutoff_lo/cutoff_hi/res_routing).
- Sectors -> `Pattern`/`NoteRow`: notes = pitch rows, gates ($FE) = `tie`
  rows. Orderlists -> `Orderlist` (entries + signed transposes + loop;
  loop byte-offset <-> entry index).

NEW schema (one principled field, spec-synced — types/grammar/parser/
writer/docs/test):
- `Instrument.pulse_sweep` (`PulseSweepConfig`): inline PW envelope
  `start=$NNNN seg (add, frames) ... [loop=N]` — decodes away pulse_ptr.
  Non-restarting instruments (ptr 0) carry `pwm.keep_running=true`; the
  position-persistence the keep-running relies on is ENGINE MECHANISM
  (per-voice pulse position), not stored content.

KEY WRITE-LOG LESSON (cost one fix-round): V5 `gate_logic` reads the
LOOKAHEAD byte — the raw next byte after a note/gate — to decide the
hard-restart gate-off. So sector command BYTE POSITIONS are write-stream-
significant; the `$FC` snd / `$FD` dur commands may NOT be reshuffled
relative to the notes/gates. They are carried as ORDERED PREFIX FLAGS
(`set_dur` / `set_instr`) on the following note/gate row, re-emitted
verbatim. (First attempt stamped instr per-row + re-emitted on change ->
moved a snd from before a gate to after it -> flipped one $D404 gate bit.)

RESIDUE (family-wide, not Katusha): other sector commands
(vol/slide/glide/frq/flt/fade/gate_toggle/adr/srr) raise `unsupported:`
in to_usf; FILTER sweep (voice-3) has no schema yet (Katusha uses none —
filter table is a single null entry); pulse programs that genuinely
advance segments / loop are untested (Katusha's counts are near-infinite
$90xx); sectors are decoded in isolation (Katusha self-establishes
dur/snd per sector — path-resolution like V4 is needed if a member
inherits sticky state across sectors).

## THEN — factory + wide batch (unchanged plan below)

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
