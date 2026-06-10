---
name: project_fc_fingerprint_and_standard
description: "FC player-version fingerprint DB (tools/fc_fingerprint.py) + the dominant 'vanilla' FC player migration (pipelines/future_composer/standard/). 91% of HVSC FC (3673/4024) is ONE player → highest-leverage target. ✅ JARRE_2 SUB 0 FULL (2026-06-10): play 17164/17164 + trichotomy audio✓ — the standard player's first verified tune. Full effect chain done (pattern decoder, instrument-select, $40=wave_arp, $80=noise_tick, pulse sweep, wave ctrl+freq, vibrato, $D416 default, tick gate-off, note-duration +1, universal_reset init). RESUME: ear-test + RELOCATION → one config for the 3673-SID family rollout. See RESUME HERE."
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

## ✅ PULSE SWEEP DONE (2026-06-10, commit 23c9f22): top of std_wave_chain,
gated pulse_prog_format=='standard'. CORRECTED bands: ctr<=thr_a→step1;
thr_a<ctr<=thr_b→step2; ctr>thr_b→DEFAULT=fx2&$FC; selector=fx2&7 (overlapping
fields); fx2&7==0 → explicit default branch (orig does an OOB table read at -4
that resolves to default — composer doesn't reproduce the mechanism). Acc=
d402/d403 shadows + dir=pulsetest (both pre-existing, note-load-init'd, tie-
skipped — NO new state). Gated 4-byte pulsetabel emission at (n-1)*4. Deleted
the inert Tel-chain splice. V2 exact; V3 exact until the early-note residual.
Match prefix 1→11 writes; f1 matches through V3+V2+V1-PW.

## ✅ WAVE-FREQ + $D416 + TICK GATE-OFF DONE (2026-06-10, 4c0a355 + e18bda0):
**FRAMES 1-3 EXACT, match prefix 46.** Wave freq: relative mode = semitone ARP
(note idx + val → table, lo,hi $1D42); absolute = val+$0D hi,lo ($1CD8); clk>=15
skips ctrl+freq (shadows hold, idx 0..13); wave insts never reach $80. fw_mode
3-state freq-write dispatch in nextvoice. $D416=$FF: bit0-clear insts write iff
voice==filtvoice latch (0 → V1 wins); chain-armed filt_pend, written between PW
and freq. Tick GATE-OFF ($19FA): standard h10 = on tick frames w/ counter2!=0,
ctrl shadow = waveform&$FE before the chain. **RE-DIAGNOSIS: the 'counter
init-phase / $40-onset-late' theory was WRONG — it was the missing gate-off.**

## ✅✅ JARRE_2 SUB 0 FULL (2026-06-10) — THE STANDARD PLAYER'S FIRST VERIFIED
TUNE: play 17164/17164, trichotomy state ✓, audio✓ (canonical init boundary).
The last three pieces: (1) VIBRATO ($1A36-$1AE8: triangle, fx1 = depth bits
3-6 + speed bits 0-2, step = semitone delta >> speed replicated 1:1 incl. the
`hi += counter2` and lone-LSR quirks, direct lo,hi write when counter2>=4,
shadows untouched; svib_* state, NOT reset per note); (2) NOTE-DURATION fix
in the EXTRACT (standard plays raw+1 ticks per $8x → PatSetLength(raw+1), USF
carries the actual tick count — this was the "~2-frames-early" residual);
(3) INIT = init_style='universal_reset' (orig init is a pure clean zeroing,
NO priming → empty USF init{} + default cfg knobs match end-of-init state;
the Tel default init's $16=$FF/$17/$18=$1F signature was leaking before).

## FAMILY ROLLOUT phase 1 DONE (2026-06-10): ear-test PASSED (user).
`fc_standard_config(sid_path)` = relocation factory (fixed layout confirmed:
2760/4024 SIDs have the freq table at load+$564; 2639 share the full shape).
**PRATO = 2nd verified member (181601/181601, audio✓)** via 3 family fixes:
pulse programs BY REFERENCE (n=fx2&7, reads may pass the nominal table —
capture by value); the STALE-TAIL variant (one static byte orig $2046: $DC →
vibrato-skipped insts write stale global $217C/D every frame;
cfg.std_vibrato_stale_tail, factory-probed; 1.57%→92.87% on its own);
instrument growth (patterns select ids 0-31; extract grows to max referenced,
composer sizes from USF). Verify fixes: fractional Songlengths; trichotomy
Check-A default = host state ($D418=$0F pre-init) → deferred-init members
(Prato init = ZERO SID writes, $210E=$2C variant) verify.

## ✅ $Ex GLIDE DONE (2026-06-10): USF grammar grew glide_up/glide_down
(16-bit rate) + glide_onset (directional portamento — new point shape in the
same parameter space as Tel's glide=N); PatGlide carries (direction, speed,
onset); standard encode; gated composer $Ex parse handler (sgl_* state,
threshold = variable not SMC); chain block between vibrato and pulse
(MUTATES lonotesto/hinotesto so $80-restore sees glided freq; d400/d401 +
lastfreq track intent). PLUS the MIRROR-WRITE variant: orig $1B3F operand
$55 (20 members) makes the glide-up hi write land on SID-mirrored regs
((op+d4point)&$1F); cfg.std_glide_hi_reg, factory-probed, emitted as
sta $D400+reg,y (mirror-equivalent). Entrail prefix 17376→18948.

## ✅ FILTER bit-SET path DONE (2026-06-10): mapped into the EXISTING Tel
filter_programs envelope (same musical concept) grown along the musical
axis — variable seg count (3 Tel / 4 standard) + optional onset= in the
USF grammar. filter_prog_format='standard' decoder (12 bytes at
filterbytes_addr=$1E89, reloc'd) → progs[0]; gated 12-byte emission +
std_filter equate; chain block with the descending band scan, flt_sto
cutoff shadow ($2169), filt_ctr ($2172: $B0 seed after ok2, reset at
seq-$FF), $D417/$D416 via filt_pend17/filt_pend (D417 FIRST). Entrail
prefix 18948→49752. The full standard effect chain is now: vibrato →
glide → pulse → $40 → FILTER → wave → $80. Canaries 16/16.

## ✅✅ ENTRAIL FULL (2026-06-10): play 127162/127162, audio✓ — 3rd member.
Two bugs: (1) the GLIDE EMISSION ORDER (composer parser checks only
$8x-or-note after $Cx → [len][instr][$Ex] misread the $Ex as a length;
encode now emits [instr][len-unconditional][$Ex]); (2) the **fx3-bit2 +$04
ARPEGGIO** ($1D1E — the LAST chain effect): per-note ctr (3 at fetch)
cycles 2→1→0; freq = freqtab[noho+arp3[ctr]] lo,hi direct per frame; arp3
= orig $1E86-88 (slot 0 baked → cfg.std_arp3_init factory-probed; slots
1-2 rewritten by every vibrato-skipped inst's $2030 path = fx1 nibbles or
$0C/$18 — THAT's what $2030 does); $80+bit2 insts write BOTH pairs →
fw_mode=3 double dispatch. Cracked by the NEW TOOL (below): "no semantic-
state divergence + writelog divergence" = an unemitted effect.

## ✅ NEW TOOL: event-aligned state diff (Trap-C-free)
`state_diff.py --on-write D418 --align-value 1F` + `state_map_gen --sid`
(per-member maps) + `standard/state_map.py` annotation (stream cursors
intentionally unmapped — the composer re-encodes streams). Also: the
composer's standard layout now INCs counter2×3 at frame top before the
$D418 write (orig $182A order; RAM-only, stream-neutral) so the state
trigger-snapshots align exactly. Benign known diffs: baked $1AF8 glide
threshold (dead until the first $Ex). Documented in CLAUDE.md +
INVESTIGATION_BACKLOG.

## RESUME HERE (2026-06-10 — widen the rollout):
0. MANDATORY 3 questions; RE=standard/RE_NOTES.md (top: full chain incl.
   +$04 arp, variant census, latent glide-3rd-byte caveat).
1. The 9 remaining sample failures (fail at position ~1 — check their
   probe bytes / oddball $2046 builds first; triage write-log-first; the
   event-aligned state differ is the second tool to reach for).
2. Then the 2639-member batch bucketed by first-divergence signature;
   fix the biggest buckets first.
Verdict: verify_featuredriven(fc_standard_config(sid)); localize with
find_first_divergence + state_diff --on-write D418 --align-value 1F.

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
