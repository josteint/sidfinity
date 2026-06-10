---
name: project_fc_fingerprint_and_standard
description: "FC player-version fingerprint DB (tools/fc_fingerprint.py) + the dominant 'vanilla' FC player migration (pipelines/future_composer/standard/). 91% of HVSC FC (3673/4024) is ONE player → highest-leverage target. Standard player is a DIFFERENT ENGINE from the Tel composer (pattern/instrument/effect/write-model all differ). DONE: base + standard PATTERN decoder + instrument-select fix + $40 effect (=wave_arp reuse, no new schema). V1 wave program matches orig exactly. RESUME: the $80 effect (V3, biggest remaining lever — a noise-click attack), then pulse/filter/wave-freq, then the base counter init-phase (the $40 onset is 1 tick late = a per-voice counter-phasing diff). See RESUME HERE."
metadata: 
  node_type: memory
  type: project
  originSessionId: fea5d0c1-61d2-49f9-8e14-4e5916b95622
---

## FC player-version fingerprinting — `tools/fc_fingerprint.py`
Relocation-invariant FC player identification. Traces reachable code from
init+play (reuses `seed_disassembly.trace`), takes the OPCODE skeleton
(relocation changes operands, not opcodes → reloc-invariant), clusters by exact
SHA1 + opcode-4-gram Jaccard. Validated: same engine relocated → 0.94-1.0;
different FC versions → ≤0.64 (Adrenalin engine A vs Cyb II vs Hawkeye).
Run: `PYTHONPATH=tools/py65_lib:tools:src python3 tools/fc_fingerprint.py --corpus`.
NB: the corpus query must use `LIKE '%FutureComposer%'` — `LIKE '%MoN%'` is
case-insensitive and sweeps in SoundMONitor.

## Corpus result (the big finding)
4024 HVSC FutureComposer SIDs → 901 distinct skeletons, 109 families.
**ONE dominant family = 3673/4024 ≈ 91%** (the vanilla FC editor player).
Migrate that ONE player → covers ~91% of the FC catalogue. The migrated
canaries so far (Cyb II, Hawkeye) and Adrenalin's engine A are LARGER
demoscene-CUSTOM variants (outliers, 0.32-0.64 to each other) — i.e. we
migrated the hard custom players first and never the easy vanilla one.

## Adrenalin verdict (fingerprint-confirmed)
Adrenalin's 4 subs span 3 FC variants; all are customized OUTLIERS (engine A
best corpus match 0.78, sub1 0.04). The fingerprint gives NO layout shortcut
for it — it stays manual. Sub 1 IS FC (full disasm: `sub1_disassembly.s`),
just a slim variant at its own addresses. Engine A ≈ Hawkeye (0.64) is its
closest reference. Adrenalin is low catalogue value (4 SIDs) vs the vanilla
player (3673); deprioritized in favour of the standard-player migration.

## Standard ("vanilla") FC player migration — `pipelines/future_composer/standard/`
Representative: `Carter/Jarre_2.sid` (load $1800). `disassembly.s` annotated
with the full data-address map: freq lo/hi $1D64/$1DC4 (96-entry canonical
table), instr records $2188 (8B, id<<3), pattern_ptr $1EA7 (2B interleaved),
seq/orderlist ptrs $1EA1(lo)/$1EA4(hi) (= flat_seq_table 6B record @ $1EA1),
speed $211D, d4point $211E. `config.py` (FC_STANDARD) drives the EXTRACT, which
WORKS (sane FCSong: 96 freq, 10 instr, 5 patterns, 3 seqs).

Effect tables NOW MAPPED (disassembly.s): pulse $1E95 (4-byte/prog),
filter $1E89 (12-byte ($f9),y program), wave/arp $1E66/$1E76, program-ptr
table $1E3E/$40/$42/$44 (sel $2153&$0F), $1E32 (4-byte effect).

**KEY SCOPE FINDING (2026-06-09):** the standard FC effect FORMATS differ
STRUCTURALLY from the Tel variants (Cyb II/Hawkeye) the current extract/composer
were built for — pulse 4-byte vs 8-byte; filter is a 12-byte ($f9),y program.
So this migration is NOT config-only: it needs standard-FC-format DECODERS
(extract) + EMITTERS (composer). First build (core addresses, aux=0) confirmed:
extract yields a sane FCSong but the play stream diverges (shift=None) because
instruments use fx1/2/3 and the standard effect formats aren't implemented. The
init diff is trichotomy-handled.

This REORIENTS the FC composer: it should target the DOMINANT standard format
(91% of HVSC FC), with the Tel variants (Cyb II/Hawkeye/Adrenalin) as special
cases — opposite of how it grew. Ties into [[project_fc_principled_composer]].

## Standard-player BUILD progress (2026-06-09 session 2) — base mostly aligned
Driven write-log-first on Jarre_2 (per-frame compare; shift=None until base
aligns). All changes are GATED config knobs → FC canaries stay 15/15 throughout
(Cyb II/Hawkeye/Adrenalin untouched; and the FC composer composer_asm.py is a
SEPARATE file from Hubbard/Companion's composer.py — zero cross-family risk).

DONE + committed (base):
- Instrument decoder `instr_format='standard'`: real 8-byte layout (+0 PW-hi,
  +2 AD, +3 SR, +5 wave-sel/mode $2153, +6 pulse-default $2154, +7 effect-flags
  $2155 — NOT Tel fx). Zeros Tel fx1/2/3 → killed the SPURIOUS VIBRATO that was
  the first big divergence (root cause was instrument layout, NOT note-timing;
  tempo is correct, $211D=$01).
- `voice_loop_layout='standard'`: nolengset writes freq once (note-load,
  freq-first) + updates lastfreq; nextvoice = PW, CONDITIONAL freq (only if
  changed vs lastfreq), ctrl. Matches vanilla's per-frame model (freq only on
  note/effect). Removed freq-duplication; V2 held frame matches orig exactly.
- `vol_every_frame=$1F`: $D418 written first each frame (vanilla $1833) +
  fm2 $D418 disabled. Frame-1 vol aligns.
- Held-frame order set; rebuild write count dropped 17189->12552 toward orig.

DONE + committed (wave envelope = engine core, the big remaining effect):
- FULL RE in standard/RE_NOTES.md: gated by inst +7 bit4; selector +5 low
  nibble; clock $2142,x (frames-since-note, capped 15); dual tables ctrl[]→$D404
  and freq[]→$D400/01 (+$0D absolute / +$2130 relative mode); SMC ptr tables
  $1E3E/$40/$42/$44.
- DECODER `_decode_std_wave_programs` (std_wave_ptr_addr=$1E3E) — verified
  parses Jarre_2 sel0/sel1.
- USF SCHEMA `UsfFile.wave_programs {sel: ctrl[15]+freq[15]}` (mirrors
  arp/pulse/filter_programs): types+grammar+parser+writer + extract->to_usf
  carry. Round-trips write->parse exactly. (Shared USF change, backward-compat.)

WAVE emitter (stage 2) ALSO DONE + committed (gated, canaries 15/15):
- 2a DATA emission: contiguous-layout allocator lays ctrl[]/freq[] at sel*16
  stride (std_wave_ctrl/std_wave_freq equates). Verified bytes for Jarre_2.
- 2b EFFECT asm: gated `std_wave_chain` (composer_asm.py) — ctrl from
  std_wave_ctrl[(sel<<4)+clk-1], clk=counter2,x reset on note-load; gwo2
  BYPASSES the Tel chain (`gwo2_dispatch` hook); instr decoder un-zeroed so
  fx1=+5/fx2=+6/fx3=+7 carry the standard bytes. Wiring verified.
  (freq part of the wave + the modes NOT yet written — ctrl only so far.)

## ✅ PATTERN DECODER DONE (2026-06-10, commit 1af4a15) — premise CORRECTED:
`_parse_pattern_standard` (engine_model.py), gated `cfg.pattern_format='standard'`
(default 'tel' → canaries 15/15). $18DD-$1957: $C0-$DF=instrument-select(0-31),
$F0-$FE=tie/no-retrigger (next byte=note), $E0-$EF=3-byte glide, $80-$BF=length,
$00-$7F=note, $FF=end. Reuses existing PatEvent vocab → to_usf/composer unchanged.
The 79fdbd3 "wrong notes" finding was a MIS-DIAGNOSIS (incomplete parser trace):
note PITCHES are IDENTICAL Tel-vs-standard for Jarre_2. The real foundational bug
was INSTRUMENT SELECTION — Jarre_2 patterns have zero $70-$7F bytes; they select
via $Cx, which Tel misread as wave-adjust → no instrument ever selected → wrong
instrument's effects corrupted freq. Now pat5→i4, pat6→i1, pat7/8/9→i7; frame 0
matches; first divergence moved to frame 1 = the EFFECT CHAIN.

## ✅ $40 EFFECT DONE (2026-06-10, commit 3fdf1e9): = wave_arp (no new schema —
the $40 effect $1BE0 IS the shipped wave_arp musical concept; reused it:
wavearp_addr=$1E32 + wavearpwait=3 + gated interpreter in std_wave_chain). Plus a
PREREQUISITE fix: the instrument-select encoding (encode_pattern emitted
NoteRow.instr as $70|n = arp-select, but the composer sets wavecount only from
$Cx; new instr_as_wavecount flag emits $C0|n so standard instruments actually
load). V1 (inst4, WAVE PROGRAM) ctrl now matches orig EXACTLY ($11,$81,$41,$40).
RESIDUAL: the $40 onset is 1 tick late (orig 2 frames of $41, reb 3) — a per-VOICE
counter INIT-PHASE diff (V1 wave matches with counter2=0 at note-load, but orig's
V2 acts as if counter is +1; orig advances some voices' counters during
init/pre-roll). Plus a note-duration discrepancy (reb V2 note2 ~2 frames early).
Both are base counter/tempo init-phasing, NOT $40-specific; the $40 VALUES are right.

## ✅ $80 EFFECT DONE (2026-06-10, commit 13beae3): = noise_tick reuse (same fx3
bit as Hawkeye's, 0x80→'noise_tick' pre-existed). noise_tick_style='standard',
body in std_wave_chain after the wave program. counter<2 → freq=$4800 (HI,LO via
conditional-freq) + ctrl=$81; counter>=2 → BASE freq EVERY frame LO,HI + ctrl=
waveform&$FE — the order asymmetry handled by a per-voice nt_flag armed by the
chain, consumed by nextvoice's freq slot (unconditional lo,hi, self-clearing).
V3 attack+restore verified EXACT (values + order). Writes 11544→13494 (orig 17189).

## RESUME HERE (2026-06-10 — remaining effects, biggest lever first):
0. MANDATORY 3 questions: docs=pipelines/future_composer/docs/; disasm=standard/
   disassembly.s; RE=standard/RE_NOTES.md (READ the top sections — turnkey).
1. **PULSE sweep** — orig V2 PW +$40/frame, V3 +$C0/frame = exactly fx2 & $FC
   (inst1=$40, inst7=$C0) = the pulse DEFAULT step ($2154&$FC, the ctr<thr_b
   band). The spliced standard pulse emitter (cut 2026-06-09,
   _splice_standard_pulse_prog) is NOT producing it — selector/default-step
   wiring missing or splice inert. Acc: 16-bit ±= step, dir flips hi<$01/>=$0F.
2. **Vibrato** (V3, +5=$27): orig writes a freq pair ($25AE) BEFORE the $80
   restore overwrites ($25A2) — both in the stream. Map $1A0A-$1B3F.
3. **Filter $D416=$FF every frame from f1** (global reg) — find the driver ($1C00).
4. Wave-program FREQ part + modes (ctrl done); then the base counter INIT-PHASE
   (the $40 onset 1 tick late = per-voice counter phasing from init pre-roll);
   then relocation (load $1800/$4800/... → derive addrs) → ONE config for 3673.
Verdict: verify_featuredriven(FC_STANDARD); localize with find_first_divergence +
tools/voice_writelog.py per voice (mind Trap C — frame numbers ≠ play() calls).

Verdict tool: `verify_featuredriven(FC_STANDARD)` (shift becomes a real int once
the note stream + base align). Diagnostic: per-frame writelog compare on
Carter/Jarre_2.sid vs build_via_asm_featuredriven(FC_STANDARD).
The standard player is a DIFFERENT ENGINE from the Tel composer (pattern fmt,
instrument fmt, effect chain, write model all differ) — not a config variant.
All changes gated → FC canaries (Cyb II/Hawkeye/Adrenalin) stay 15/15; FC
composer (composer_asm.py) is separate from Hubbard/Companion (composer.py).

## Related
[[project_adrenalin]] (the outlier that triggered this pivot),
[[project_fc_principled_composer]], [[project_fingerprint_db]] (the deferred
writelog→params DB — Approach B, not yet built).
