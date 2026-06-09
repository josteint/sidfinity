---
name: project_fc_fingerprint_and_standard
description: "FC player-version fingerprint DB (tools/fc_fingerprint.py) + the dominant 'vanilla' FC player migration (pipelines/future_composer/standard/). Fingerprinting found 91% of HVSC FC (3673/4024) is ONE player → highest-leverage FC target. Standard-player extract works; build needs aux effect tables mapped next."
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

REMAINING (stage 2 — the large composer build, write-log iteration):
- WAVE emitter: extend the data-layout packing engine (composer_asm.py ~3368)
  to emit the dual tables + SMC ptr tables; add the gated envelope asm
  (per-frame ctrl+freq via counter2,x capped 15 + selector + mode); carry the
  standard +5/+7 bytes (un-zero fx1/fx3 + gate the Tel effect chain off, OR new
  per-voice state) so the wave effect can read sel/enable; build + iterate the
  ctrl + freq sub-streams. THIS drives V3 ctrl $81 + freq $4800.
- PULSE emitter already written (gated `_standard_pulse_prog_body`); needs the
  real selector byte wired (NOT fx2=$2154 = default-step).
- FILTER emitter ($1E89 12-byte) — spec'd in RE_NOTES.
- THEN relocation handling (load $1800/$4800/... → derive addrs) so ONE config
  covers all 3673.
The standard player is a STRUCTURALLY different engine from the Tel composer
(conditional freq writes, per-frame wave-program ctrl, vol-first) — the effect
chain is a focused multi-stage build, blueprinted in standard/RE_NOTES.md.

## Related
[[project_adrenalin]] (the outlier that triggered this pivot),
[[project_fc_principled_composer]], [[project_fingerprint_db]] (the deferred
writelog→params DB — Approach B, not yet built).
