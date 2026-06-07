---
name: project_fc_principled_composer
description: "FC family principled-composer work (de-verbatim patterns/sequences/aux); plan, key findings, transpose/voiceinc decisions"
metadata: 
  node_type: memory
  type: project
  originSessionId: 34baf59d-942f-49ab-b1d7-123e07963888
---

Bringing the FC composer (`pipelines/future_composer/composer_asm.py`) up
to the USF principle: today its `build_via_asm_featuredriven` emits engine
code from features but the **data tail (patterns + sequences +
pattern_ptr_table + aux tables) is still verbatim-copied from the orig
HVSC binary**. Plan: `docs/principled_fc_composer_plan.md`.

**Verdict tool:** `verify_featuredriven(cfg)` — frame-exact writelog match
(NOT byte-exact; the composer chooses its own layout per CORE TENET).
Baseline (2026-06-06): Hawkeye 12/12, Cyb II 2/2 green. Two canaries.

**Plan correction (load-bearing):** the plan's "Schema: nothing — USF
already carries `Pattern.events`" is WRONG. `to_usf.py` lowers FC patterns
into the *generic* USF representation (`VoiceBlock → Orderlist + Pattern →
NoteRow`, like Hubbard), not FC `Pattern.events` (those exist only at
extract time). So Phase 1 walks the generic USF, and byte-exact is off the
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
[[reference_usf_v2_format]].

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
1. EXTRACTION (the main remaining work): SFX subtunes need POST-INIT memory
   (static $8FC5 is empty; populated at init from the record) — run
   `_run_init_in_py65` per SFX subtune, decode sequences with the corrected
   ranges, extract the SFX patterns (slots 54-63 from $8475 post-init). The
   FCSong `patterns` dict (single global, keyed by fc-id) can't hold
   per-subtune slot-54-63 patterns (fc-id 54 differs per SFX subtune) →
   resolve patterns PER-SUBTUNE so each SFX subtune's voices carry their own
   real patterns. Then the global content-dedup pool in build_pattern_pool
   merges/separates them naturally (98 unique ≤128 ✓).
2. song_init: unify Hawkeye to a flat seq_table for ALL 12 subtunes (drop
   the SMC template + SFX-page copies; CORE TENET lets us). seq_table holds
   12 records × 6 bytes (3 voice seq ptrs); speedbyte per subtune from USF
   tempo; voice_loop_start = is_sfx?0:2 (mode byte). build_music_data already
   builds the global pool + flat seq_table — extend for n_songs subtunes.
3. Set Hawkeye `emit_data_from_usf=True`; verify 12/12.
No per-subtune pattern tables, no SFX-record regeneration, no engine-walker
widening needed — the 128-slot encoding made all that unnecessary.

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
