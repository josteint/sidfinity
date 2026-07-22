---
name: project_fc_principled_composer
description: "FC family principled-composer work (de-verbatim patterns/sequences/aux) — ✅ COMPLETE: §9 fully closed, whole FC build orig-free (model-USF buildable), both canaries (Cyb II 2/2 + Hawkeye 12/12) de-verbatim, PSID header synthesized. Kept for the key findings + transpose/voiceinc decisions."
metadata: 
  node_type: memory
  type: project
  originSessionId: 34baf59d-942f-49ab-b1d7-123e07963888
  modified: 2026-07-22T08:27:00.084Z
---

## ⚠️ 2026-07-22 — ORIG-FREE ≠ USF-COMPLETE (measured; OPEN, needs a decision)

The "§9 closed / orig-free" claim is about BUILD TIME: the composer no longer
reads the original binary. It does NOT mean the `.usf` is the complete build
specification. Audit of `fc_standard` (400 sampled FULL members, every `cfg.*`
field `composer_asm.py` reads — 72 of them):

- 31 fields are FAMILY CONSTANTS → engine mechanism, Principle-permitted.
- 9 are layout addresses → feed the data-base float; write-stream-neutral.
- `subtune_layout` varies (2 values) but is EXTRACT-only: flipping it and
  rebuilding from the same stored `.usf` is byte-identical (verified 3×).
- **3 vary per member AND change the emitted bytes (verified by flipping each
  and rebuilding from the same stored `.usf`):**
  - `std_arp3_init` — 20 distinct values, e.g. `(0,12,24)` (an octave arp) vs
    `(0,0,1)`. Baked initial 3-byte offset table at orig $1E86-$1E88. This one
    is arguably musical CONTENT, not mechanism.
  - `std_glide_hi_reg` — 2 values ($01 normal / $55 the hacked mirror-register
    operand at orig $1B3F, ~20 members).
  - `std_vibrato_stale_tail` — 2 values (orig $2046 variant $EB vs $DC).

None appear in the `.usf` — a standard member's `params {}` block is EMPTY.
They are C19-class player WEDGES, which the CORE TENET explicitly sanctions as
per-engine config ("config fields parametrise differences between engines'
write-log streams"). **The asymmetry worth noting: DMC carries its wedge knobs
IN the USF (`params.fields`) — which is why `hold_gateoff` had to reach the
stored `.usf` — while FC keeps the equivalent knobs in Python only.**

CONSEQUENCE for the C20-fifth-layer audit: `fc_mass_write._rebuild_from_usf`
must hand the builder a freshly-derived cfg, so the FC audit verifies
`stored .usf + cfg -> stored .sid`, NOT `stored .usf -> stored .sid`. It is a
genuinely weaker invariant than DMC's, and by necessity — closing the gap
means carrying these three in the USF. **Not done: that is a schema decision
(§8 vs the sanctioned per-engine-config category), so it is the user's call,
not a unilateral fix.** ML angle: a model generating a USF cannot express
"this tune's 3-step arp is (0,12,24)".

Bringing the FC composer (`pipelines/future_composer/composer_asm.py`) up
to the USF principle: today its `build_via_asm_featuredriven` emits engine
code from features but the **data tail (patterns + sequences +
pattern_ptr_table + aux tables) is still verbatim-copied from the orig
HVSC binary**. Plan: `deprecated/old_docs/principled_fc_composer_plan.md`.

**Verdict tool:** `verify_featuredriven(cfg)` — frame-exact writelog match
(NOT instruction-sequence exact; the composer chooses its own layout per CORE TENET).
Baseline (2026-06-06): Hawkeye 12/12, Cyb II 2/2 green. Two canaries.

**Plan correction (load-bearing):** the plan's "Schema: nothing — USF
already carries `Pattern.events`" is WRONG. `to_usf.py` lowers FC patterns
into the *generic* USF representation (`VoiceBlock → Orderlist + Pattern →
NoteRow`, like Hubbard), not FC `Pattern.events` (those exist only at
extract time). So Phase 1 walks the generic USF, and instruction-sequence exact is off the
table — writelog-exact is the verdict.

**Phase 1 + Phase 2 are coupled** — the sequence references patterns by id
through `pattern_ptr_table`; re-emitting a fresh pattern pool requires
re-emitting sequences too. Doing them as one merged unit (decided
2026-06-06).

**Representation principle for FC sequence-level techniques (USER
DIRECTIVE 2026-06-07):** do NOT fold/bake/flatten anything that's
*lossy*; represent the technique explicitly in USF and defer
folding choices to the grand-unification/tokenization stage (a factored
USF is a reversible superset — you can flatten at tokenize time but never
un-bake). Lossless normalizations (e.g. repeat run-length) are free to
keep whatever's convenient. Distinguish: lossy fold = destroys motif
identity (transpose-into-pitch, voiceinc-into-wave_adjust); lossless =
RLE-reversible (repeat expansion).

**USF orderlist now carries all three FC sequence modifiers explicitly**
(commits 4f040eb transpose + the voiceinc/repeats follow-up). `Orderlist`
gained `transposes` / `voiceincs` / `repeats` (each optional, parallel to
`entries`, empty=identity). Serialized syntax per entry: **`a[*b][+c][^d]`**
— operand (pattern id) first, then homogeneous `<op><param>` modifiers:
*b=repeats(plays), +c=transpose(semitones, FC non-negative 0-31),
^d=voiceinc. Operators are plain single chars (clean under LALR). See
[[reference_usf_format]].

- **transpose** = pitch transpose (FC `$80-$FF` toneadd, `& $1F`, added to
  freq-table index; non-negative). Baking it inflates pool past FC's
  64-pattern limit ($00-$3F pattern-jump byte → max 64 slots).
- **voiceinc** = "sound transpose" (FC14 Amiga spec's name). FC `$60-$7F`,
  `& $0F`. Consumed ONLY at `$C0-$DF` wave-adjust: `wavecount =
  (pattern_byte & $1F) + voiceinc`. Offsets the instrument waveform-program
  scan index. NOT baked (per directive) — kept explicit.
- **repeat** = FC `$40-$5F` `& $3F`; `repeats[i]` = play count (FC count+1).
  Kept RLE (lossless); also needed so per-voice sequence stays < 256 bytes
  (tabcount is a 1-byte index).

**Pattern pool = base motifs.** With BOTH transpose+voiceinc un-folded,
patterns dedup by **fc_id alone** → pool = base FC patterns (54 Hawkeye /
31 Cyb II), ≤64 ✓. (For reference: baked-transpose pool would be 137.)

**FC sequence byte dispatch** (composer_asm walker): `$00-$3F` pattern
jump (byte = pattern id), `$40-$5F` set repeat, `$60-$7F` set voiceinc,
`$80-$FF` set transpose (toneadd), `$FE`/`$FF` end/wrap. NOTE these ranges
differ from `engine_model._parse_sequence`'s SEQ_*_RANGE constants — trust
the disasm/walker.

**Remaining merged Phase 1+2 work:**
1. Extract (`to_usf.py`): DONE — patterns are pure motifs (no transpose,
   no voiceinc folded; raw wave_adjust); dedup by fc_id; orderlist carries
   transposes/voiceincs/repeats. `verify_featuredriven` still green (composer
   still uses verbatim tail, so USF content is a no-op for the verdict until
   step 2).
2. Composer: **Cyb II DONE — fully green 2/2 via USF-derived data tail.**
   `pipelines/future_composer/data_emit.py` = `encode_pattern` /
   `encode_sequence` / `build_pattern_pool` / `build_music_data`. When
   `cfg.emit_data_from_usf=True`, the featuredriven composer builds a fresh
   music-data block (seqtabel + pattern_ptr_table + pattern streams + seq
   streams) at `code_end+shift`, past the verbatim tail, and redirects the
   engine pointers (pattern_ptr_table equate + song-init seqtabel addr) at
   it; verbatim tail still emits (aux tables stay live, old music data dead).
3. **Hawkeye IN PROGRESS** (smc_template_with_sfx, featuredriven_addr_shift
   $40, 6 music + 6 SFX subtunes). Still verbatim (flag off). RE COMPLETE,
   implementation is a sizable multi-session effort — see Hawkeye SFX RE below.

### Hawkeye SFX RE (complete; 2026-06-07)
Hawkeye = 6 music subtunes (0-5) + 6 SFX subtunes (6-11). SFX are REAL
note sequences (not register-snapshot SFX like Hubbard's SfxSubtune), but
stored as **self-contained per-SFX records** at $9200/$9400/.../$9C00
(page = $92 + sfx_idx*2). `$918F` dispatcher (init) for an SFX subtune
copies from the record:
  - record+$00 (6 bytes) → $7B2C: V0/V1/V2 seq pointers (V0=$8FC5 shared;
    V1=V2 mirrored, e.g. $9015).
  - record+$06 (20 bytes) → pattern_ptr_table+$6C ($8475): 10 SFX pattern
    pointers = pool **slots 54-63**.
  - record+$1A (255 bytes) → $8FC5: the seq + pattern DATA (runtime area).
  Then forces X=6 and tail-calls music init.
SFX sequences decode CLEANLY with the correct walker ranges (V0 jumps to
SFX patterns 54-61; V1/V2 jump to SHARED music patterns 0,10,11,12 + WRAP).
The "overlap" (V1 seq addr $9015 == SFX pattern-54 addr) is orig's
space-saving — in USF/our pool pattern-54 and the V1 sequence are SEPARATE,
so it doesn't complicate our representation.

**The blocker — 98 > 64 — SOLVED by repartitioning our sequence encoding.**
The 64 limit was FC's 1-byte $00-$3F jump partition; our composer emits its
own bytes + walker, so we widened it (user directive 2026-06-07: be elegant,
don't inherit FC's limit, no per-subtune-table-in-init hack, unify). New
USF-derived sequence partition (`encode_sequence` + the walker's
`h3_command_dispatch`, gated on `emit_data_from_usf`):
  `$00-$7F` jump (128 patterns) / `$80-$9F` transpose / `$A0-$BF` repeat /
  `$C0-$CF` voiceinc / `$FE`/`$FF` end/wrap.
128 = the clean 1-byte ceiling because the walker indexes
`pattern_ptr_table` with 8-bit `asl;tay;lda table,y` (id*2 ≤ 255); >128
would need a carry-branch (easy, deferred). 128 covers Hawkeye's 98. This
gives ONE global pattern pool, NO per-subtune tables, and song_init stays
dumb. The verbatim path keeps FC's $00-$3F partition (else branch) so orig
bytes still parse. DONE + Cyb II re-verified 2/2, Hawkeye verbatim 12/12.
(The earlier per-subtune-SFX-record-regeneration plan is SUPERSEDED.)

**Remaining for Hawkeye 12/12 (the elegant path, given the blocker is gone):**
The COMPOSER is now uniform — one global pool (≤128), dumb song_init, flat
seq_table. So Hawkeye just needs its real data fed through. Steps:
1. EXTRACTION (DONE): `Subtune` now carries per-subtune `seqs` + `patterns`,
   resolved in that subtune's memory context (`extract()` runs
   `_run_init_in_py65` for SFX subtunes since static $8FC5 is empty; music
   uses the static image). `to_usf._voice_to_usf(voice_id, seq, patterns)`
   + `_subtune_to_usf` read the per-subtune data (not the SID-global dicts,
   which collide for SFX). Result: Hawkeye SFX subtunes now carry REAL
   sequences/patterns (was 256-byte garbage); global content-dedup pool = 99
   (≤128 ✓); all 136 Hawkeye patterns round-trip; Cyb II still 2/2.
2. song_init: DONE — `_emit_song_init_smc` has an `emit_data_from_usf` flat
   branch (all 12 subtunes read the flat seq_table; speedbyte per-subtune;
   voice_loop_start = orig mode constants music/SFX, read from $7AFF in
   compose). compose_fc_asm_featuredriven: preserve_end gated off when
   emit_data_from_usf (no SMC templates read), reads song_init_modes from
   orig mode table, build_music_data already gets all 12 subtunes.
3. Set Hawkeye `emit_data_from_usf=True`; verify 12/12. **BLOCKED — see below.**

### Hawkeye composer: SILENCE BLOCKER SOLVED (banking) — now 7/12
**Root cause (FIXED, commit 9a67de3):** Hawkeye's emit_data music_data +
state live in $A000-$BFFF, but Hawkeye's CODE is below $A000, so libsidplayfp
keeps BASIC ROM mapped at $A000-$BFFF by default — the engine read ROM
instead of its data (py65 has flat RAM → played; libsidplayfp = ground
truth → silent). [[feedback_c64_banking_relocation]]. Found via lock-step
py65-vs-libsidplayfp PC diff + memwatch(RAM)≠CPU-read mismatch.
FIX: `playirq` sets `$01=$36` (BASIC out → RAM at $A000-$BFFF; KERNAL + I/O
in) EVERY frame (the PSID driver resets $01 before each play, so song-init
alone doesn't hold). Gated on `emit_data_from_usf` via the `bank_ram`
substitution — verbatim engines keep data below $A000 and setting $01 there
BREAKS them (broke verbatim Hawkeye until gated). Result: Hawkeye emit_data
0/12 → **7/12** (subs 2,3,4,7,8,10,11 instruction-sequence exact). Cyb II 2/2, Hawkeye
verbatim 12/12.

**Hawkeye emit_data now 10/12** after two more fixes:
- **noretrig (commit 7b06383):** FC `$F0` (PatNoGlide) sets the engine's
  newnote flag = skip ADSR/wave reload (legato). to_usf was dropping it;
  now a `noretrig` fx_flag (grammar/parser), set on PatNoGlide, emitted as
  `$F0` first in encode_pattern. Fixed sub 5 (its ADSR divergence).
- **note-length off-by-one (commit 3d93480):** extract did
  `cur_length = max(1, setlen-1)` which collapsed setlen 1 vs 2 to the same
  duration AND made the encoder emit setlen=duration+1, so notes played one
  step too long → sequence desync. Correct: `duration = raw setlen value`
  (engine nootleng = value-1); encoder emits `$80|duration`. Instruction-sequence exact
  round-trip, unchanged for setlen>=2 (Cyb II 2/2). Fixed subs 0,1,6,9.

**HAWKEYE 12/12 — music layer principled (emit_data_from_usf=True in config;
aux effect-program tables still verbatim — see the gap note below).**
The last 2 (SFX 7,10) were a NOTE-LENGTH PERSISTENCE bug (caught after a
Trap-A slip — don't judge by per-frame register snapshots; the write-log is
the verdict). FC's `nootleng` PERSISTS across patterns: orig patterns whose
first note has no setlen inherit the previous pattern's length. The composer
forced a setlen with a default duration → wrong timing. FIX: thread the
persisted length through the voice's sequence in to_usf — `_build_pattern_rows`
takes `init_length` and returns `final_length`; `_voice_to_usf` carries it
across jumps and dedups patterns by `(fc_id, init_length)`. The composer
always emits an explicit setlen, so rebuilt patterns are self-contained
(different bytes from orig, identical write-log). Verified 12/12 + Cyb II 2/2.

**MUSIC layer principled for both canaries: Cyb II 2/2 + Hawkeye 12/12 —
patterns/sequences/orderlist/freq/instrument-records/pattern_ptr_table/
seq_table all from USF.** BUT this is NOT yet as principled as
Hubbard/Companion: the composer STILL verbatim-copies the aux EFFECT-PROGRAM
tables from the orig binary at compose time (`build_via_asm_featuredriven`
does `orig = f.read()`), and both canaries USE all of them — `drumtabel`
(drum programs), `filterbytes` (filter programs), `pulsetabel` (pulse
programs), `arplo`/`arphi` (arp programs), `vibtabwait` (vibrato onset),
`wavearp`/`pulsearp`. So §9 completeness FAILS for FC (a model-generated FC
USF can't build — needs orig for the aux tables). Hubbard's USF→SID path
(`_inputs_from_usf`) builds from `usf.*` alone (only orig read = the PSID
header metadata). Closing this = the plan's Phase 3/4/5 (decompose each aux
table into musical USF fields with schema discipline). IN PROGRESS.

### Aux-table de-verbatim progress
- **vibtabwait — DONE (commit 4418bb9).** Per-instrument vibrato onset; no
  schema needed (reused `VibratoConfig.onset`). Extract reads vibtabwait[id]
  → FCInstrument.vib_onset → `_inst_to_usf` sets vibrato.onset; composer
  emits the table as a USF-derived section (label-less; equate names it).
- **arp library (arplo/arphi + programs) — DONE.** New top-level USF block
  `arp_programs { prog N: [o0,o1,...] }` (signed semitone offsets; count =
  len-1, derived). Mechanism: pattern `$7x` → N (carried as note instr ref)
  → `arplo[N]/arphi[N]` → program `[count, off0..]`; fx_tone_arp cycles the
  offsets. arp_count = `arphi_addr - arplo_addr`; program data follows arphi;
  composer lays programs out + computes pointers (label-less sections, equates
  name them). Extract `_decode_arp_programs` reads them signed. Schema across
  types/grammar/parser/writer + docs/usf_format.md. Cyb II 2/2, Hawkeye 12/12,
  corpus roundtrips.
- **pulsetabel (pulse-sweep programs) — DONE.** New top-level USF block
  `pulse_programs { prog N: lo= hi= [wrap] seg T S [flip] x3 }`. Program N =
  instrument's fx2&7; 8 bytes at (N-1)*8: b0=(wrap<<7)|lo nibble, b1=hi, then
  3×(b=thr|flip<<7, step). fx_pulse_prog ramps PW between bounds, switching
  step at each threshold. Only REFERENCED programs stored (kmax = max
  inst.fx2&7; unused slots are dead data). Engine ignores b0 bits 4-6 so the
  (wrap,lo) decomposition is writelog-faithful. Schema across all USF files +
  docs. Cyb II 2/2, Hawkeye 12/12.
- **filterbytes (filter cutoff-envelope programs) — DONE.** New top-level USF
  block `filter_programs { prog N: init= d418= final= end= seg T A x3 }`.
  filterbytes is a 2-byte-ptr table → 10-byte programs fb[0..9]: fb0=init
  cutoff, fb1-3=segment adds, fb4=final, fb5=$D418, fb6-8=seg thresholds,
  fb9=end threshold. fx_filter_prog walks counter2 vs thresholds → cutoff to
  $D416, routing to $D418. GOTCHA: extract ALL programs (count = (first_ptr -
  filterbytes_addr)/2), NOT just instrument-referenced — SFX subtunes (6-11)
  reference a program no music instrument uses; refs-only gave Hawkeye 6/12
  (SFX read garbage $FF), full-table extract → 12/12. Cyb II 2/2.
- **drumtabel (percussion programs) — DONE.** New top-level USF block
  `drum_programs { drum N: wave=[..] tone=[..] }` (parallel per-step lists).
  drumtabel = 4 bytes/drum: dwa ptr (waveform prog [len, w1..]) + dto ptr
  (tone prog [t0..]). fx_drum plays (dwa[counter2], dto[counter2-1]) per
  frame → $D404 waveform + pitch offset. Stored as wave/tone steps (len-1
  each; leading length byte = len+1 derived). Extract ALL drums (count =
  (first_dwa - base)/4) — SFX reference drums no music inst does (Hawkeye
  has 7, music uses 0/1/3). Compose lays dwa+dto out + computes drumtabel
  ptrs. Cyb II 2/2, Hawkeye 12/12.
- **flat aux tables — DONE.** startlen/starttabel → `attack_len`/`attack_wave`
  (per-wavecount note-attack; size = starttabel-startlen gap). wavearp/pulsearp
  → `wave_arp` (4, counter2&3) / `pulse_arp` (8, counter2&7). All flat top-level
  USF lists, emitted at their engine addrs. Cyb II 2/2, Hawkeye 12/12.
- **GRAMMAR SPEEDUP (important):** the start rule had accumulated ~13 sequential
  optional blocks (`X? Y? Z? ...`) — LALR table construction blew up to 29s+ and
  then HUNG (>40s) when the 4 flat decls were added. Fix: grouped all FC aux
  blocks (arp/pulse/filter/drum/attack/arp-cycles) into one repeated
  `fc_aux_block*` rule → load 29s → **1.1s**. If adding more top-level optional
  blocks, ALWAYS use a repeated group rule, never a long `X?` chain.
- **ALL live aux tables now USF-derived.** Remaining verbatim (per re-audit):
  aux GAPS (Cyb II 95b, Hawkeye 320b) + TAIL (Cyb II 1600b, Hawkeye 5644b =
  dead old seq/patterns; engine reads music_data). NEXT for §9: zero-fill test
  (replace _emit_verbatim_region with zeros, verify writelog unchanged → all
  dead → remove `orig=f.read()`); if it breaks, a gap holds an unidentified
  live table. NOTE Hawkeye builds with shift=$40 (aux addrs shifted).
### VERBATIM AUDIT RESULT (zero-fill test) — §9 status
Replaced `_emit_verbatim_region` with zero-fill, re-verified:
- **Cyb II: 2/2 with ALL verbatim zeroed → FULLY de-verbatim.** Every byte the
  composer still reads from orig is DEAD. The `orig=f.read()` can be dropped for
  Cyb II (it only needs the PSID header, like Hubbard). Cyb II is the first
  fully-principled FC SID end to end.
- **Hawkeye: 0/12 zeroed (with instr_count=16) → was a MISATTRIBUTION.** Per-gap
  bisection corrected it: zeroing gap1 ($83FC..$848B = SMC templates + the
  pointer table) → **12/12** (gap1 is DEAD — the SMC pointer-table is NOT read
  in the emit_data path; my first audit was wrong). The real live region was
  gap2 ($868C..$8704) = **instrument records 16-30**: Hawkeye has 31 instruments
  (0-30 span instr_records_addr..vibtabwait_addr, $860C..$8704 = 31×8), but
  instr_count was set to 16, so 16-30 stayed verbatim and ALL subtunes read
  them. FIX: instr_count 16 → 31 (Hawkeye config). Now Hawkeye is **12/12 with
  ALL verbatim zeroed → fully de-verbatim**, same as Cyb II.
- **BOTH canaries now fully de-verbatim.**
  LESSON: don't trust a coarse zero-fill audit — bisect per-region; and an
  instr_count that's too small silently hides instruments as verbatim.

### §9 CLOSED for the FC emit_data path — no musical data copied from orig
The composer now copies ZERO musical bytes from orig on the emit_data path:
- Inter-section gaps + the old seq/pattern tail are ZERO-FILLED (`.dsb n,0`),
  not copied verbatim (they're dead — proven by the zero-fill audit).
- `song_init_modes` comes from `FCConfig.song_init_modes` (default (2,0),
  Hawkeye's actual value), not mem[$7AFF].
- `_fixup_verbatim_pointers` skipped for emit_data (nothing verbatim to fix).
- SMC-template preserve already skipped for emit_data.
Verified with REAL builds (zero-filled verbatim): Cyb II 2/2, Hawkeye 12/12,
full regression green. The only remaining orig read is the PSID header
(load_addr / init+play vectors / title) + body size — metadata, exactly like
Hubbard's `_inputs_from_usf` reading its 124-byte header. All MUSICAL content
(patterns, sequences, tables, instruments, every aux program) is USF-derived.
### §9 FULLY CLOSED — the whole build is orig-free (model-USF buildable)
Done (commits cda5658 + this one):
- **music_data placement refactor:** music_data is built AFTER the section
  layout and placed at `music_base = max(section end)` — right after the last
  USF section — instead of `code_end+shift`. The section loop zero-fills gaps
  and ends exactly there, so no verbatim tail. Removes the orig-body-size
  (code_end) dependency.
- **load_addr from cfg** (`FCConfig.load_addr`; Hawkeye $7AE0, Cyb II $A600):
  `compose_fc_asm_featuredriven` reads NO orig on the emit_data path (proven:
  composes with a bogus sid_path).
- **PSID header synthesized** from `usf.psid` + cfg (`_make_psid_header`):
  byte-IDENTICAL to HVSC's header for both canaries; flags from clock+sid,
  init=load_addr, play=load_addr+3, songs=len(usf.subtunes), inline-load form.
  `build_via_asm_featuredriven` uses it for emit_data → the FULL build runs
  from USF alone (proven: builds Hawkeye with a bogus .sid, producing output
  identical to the orig-header build).
Result: a model-generated FC USF can build a complete, instruction-sequence exact SID with NO
orig file at all. Both canaries fully principled, equal to Hubbard/Companion
(actually a step beyond — Hubbard still reads its 124-byte header). §9 met in
full for the FC emit_data path.

  (older note) CONFIRMED per-SID effect-PROGRAM data, NOT engine constants:
  arp/pulse/filter program bytes DIFFER between Cyb II and Hawkeye (only a
  shared default prefix matches). So each needs real work: RE the program
  format → design a musical USF representation (schema-addition discipline;
  programs = offset/value sequences = data tables per Rule 2, decompose where
  structure is clear) → extract → compose-from-USF → verify instruction-sequence exact
  writelog. Each is a mini-project (~1 table/session). The arp table is 8
  pointers (arplo/arphi) into overlapping 4-byte-spaced windows of a shared
  program stream; the note's $7x arp-select (currently mapped to row.instr)
  picks the window. §9 completeness passes only once ALL are USF-derived and
  the composer's `orig = f.read()` is removed.

Cyb II+shift filter bug remains separately latent (Hawkeye builds at shift=0,
so emit_data doesn't need the shift; the banking fix made shift irrelevant).

### (historical) Hawkeye composer BLOCKER: py65 plays, libsidplayfp silent
With `emit_data_from_usf=True` (via dc.replace; NOT yet set in config),
Hawkeye builds fine and **py65 plays it CORRECTLY** (frame 1: V3=$02CC,
V2=$1A9C — matches orig). But **siddump/libsidplayfp (GROUND TRUTH) plays it
essentially SILENT** (1 stray write in 60 frames; verify match=51 = init only,
reb_len >> orig). This is the classic [[feedback_py65_misses_dispatch_bugs]]
/ [[feedback_ground_truth]] split — a CPU/dispatch EXECUTION divergence, NOT
a data bug. Verified CORRECT in libsidplayfp via --memwatch: seq_table
@$9D60 (5C C4 59 A7 A7 A8), seqloclo @$AD9B populated post-init (5C..A7..),
pattern slot0 @$9E6E, speedbyte=$03, testbyte=0. So data + song_init are
right in BOTH emulators; only execution differs.
RULED OUT (all via libsidplayfp --memwatch — EVERYTHING the engine reads is
correct at runtime in libsidplayfp): speedbyte=$03 (@$AD01), snelheid=$03
(@$8435), seq_table (@$9D60), seqloclo populated (@$AD9B = 5C..A7..),
sequences (@$A75C=$90), patterns (@$9E6E). Also ruled out: C64 banking
($A000+ is RAM — Cyb II at $AE3F + Hawkeye's own $AD9B prove it), the
128-slot walker (Cyb II emit_data green with it), addr_shift (shift=0 gives
the SAME match=51 silence). So ALL DATA is correct in libsidplayfp yet it
plays silent while py65 plays perfectly — a pure CPU/execution divergence.

**pc-trace tool**: `tools/siddump FILE --subtune N --pc-trace OUTFILE
START_FRAME END_FRAME` (START/END are FRAME numbers; writes PCs+regs+flags
to OUTFILE — can be HUGE, 1.6GB for a frame; capture in bg + kill early).
Each line: `PC flags A X Y SP DR PR NV-BDIZC opcode`. The A/regs are the
PRE-instruction state. D-flag is clear (not decimal mode).

**pc-trace status / the alignment trap**: lock-step py65-vs-libsidplayfp
PC+A diffs kept pointing at false divergences (e.g. "speedbyte=$00" at
$7B89) because (a) py65 is ONE play() call but the libsidplayfp trace spans
init + driver + many frames, so anchoring on "first $7AE3/$7B89" picked
non-corresponding contexts, and (b) the trace A-column is pre-instruction.
The libsidplayfp driver idle-loops at $04A5 (normal). There is NO runaway
loop (the $82xx hotspot is just the 3-voice DEX/BMI SID-write loop).

NEXT (clean lock-step): anchor the libsidplayfp trace on the FIRST play
cycle AFTER init completes (find first $7AE0 init pass, then the following
$7AE3), and make the py65 harness enter play with libsidplayfp's exact
entry registers/flags. Compare POST-instruction state step-by-step for the
true first execution divergence. The data being 100% correct means the bug
is in how some instruction EXECUTES (candidates: an undocumented opcode
xa65 emitted that the two CPUs handle differently; a stack/flag-on-entry
dependence in playirq; a self-modify the new song_init introduced).

**Shift bisection result (separate bug):** Cyb II is green at shift=0 but
forcing featuredriven_addr_shift=$40 breaks it — diverges DEEP (match=54208)
at a $D416 FILTER write (orig $A0 vs reb $E0). So the shift path mishandles
the filterbytes aux table (verbatim + _fixup_verbatim_pointers). This is
NOT Hawkeye's silence blocker (Hawkeye fails at shift=0 too), but it must be
fixed OR avoided for a clean Hawkeye. Hawkeye emit_data BUILDS with shift=0
(engine fits load+6..first_data_addr since preserve_end=0), so dropping the
shift for the emit_data path side-steps the filter bug — do that once the
silence bug is fixed.
The composer infra is COMMITTED but DORMANT — Hawkeye config does NOT set
emit_data_from_usf, so it stays on the verbatim path (12/12). Cyb II 2/2,
Hawkeye-verbatim 12/12 confirmed after the song_init restructure.

**DONE this session:** fixed `SEQ_TRANSPOSE_RANGE` $80-$BF → $80-$FD
(engine_model.py): the walker treats all $80-$FD as transpose; the old
bound mis-parsed SFX high-transpose bytes ($C0-$FD) as pattern jumps. Safe
(music transpose ≤$97; canaries stay green).

**FC byte encodings (data_emit.py):** pattern: $F1 v filter / $E0 d p glide
(bypasses wave/len/instr; reached only via `skip` re-dispatch, so a length
byte must precede it) / $C0|w wave-inst (w=raw delta; voiceinc added at
runtime) / $80|(L+1) length ($80-chain for L>62) / $70|i instr-arp (i=id-1)
/ pitch / $FF end. sequence: $00-$3F jump(=pool slot) / $40|r repeat(plays-1)
/ $60|v voiceinc / $80|t transpose / $FE stop / $FF wrap.

**Two bugs Cyb II surfaced (both masked by the old verbatim path):**
- **max_patterns truncation**: `max_patterns=33` dropped referenced pattern
  33 (a dup of 29) → extraction one short → empty pattern emitted. Fixed to
  34. max_patterns must cover the max REFERENCED id, not "entries seen".
- **voiceinc/toneadd loop persistence**: `$60/$80` set persistent per-voice
  state that survives the `$FF` wrap and emit NO SID write — a value set near
  a loop's end leaks invisibly into the next loop's early patterns. Fix in
  `encode_sequence`: init cur_t=cur_v=-1 so the first entry always re-emits
  both, re-establishing loop-start state every wrap. (Manifested as wrong
  instrument = inst+voiceinc on loop 2; localized via find_first_divergence
  + instrument-table lookup since voiceinc itself emits no write.)

First target was **Cyb II**. See CORE TENET + [[feedback_deconstruct_not_reproduce]].
