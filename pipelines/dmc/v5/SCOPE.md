# DMC V5 line — migration scope (2026-06-14)

Scoping assessment for the DMC V5 player line (2181 SIDs). NOT yet
migrated. Research docs exist: `pipelines/dmc/docs/dmc_v5_format_notes.md`
(8-byte instrument + 2-byte tables, parameter-level), `dmc_sector_commands.md`
(the ~14 V5 sector commands, byte encoding UNKNOWN), `dmc_v5_docs_original.txt`
(first-party V5.0 docs), `tnd_dmc_tutorial.txt` §3.

## Verdict: V5 is a DISTINCT engine (not a V4 sub-build)

Family-2 reused the V4 composer (same engine, relocated tables + probed
knobs). **V5 cannot** — it is a different player with a different data
model. It needs its OWN extract + composer. It DOES share the DMC
*architecture* (duration-based, 3 voices, track→sector→note dispatch,
`$FF` sector terminator, speed counter), so the migration *pattern* (and
all the verify/factory/batch infrastructure) carries over.

Jaccard to V4 canonical: 0.136 (vs family-2's 0.732). Different engine.

## Census (2181 = 20% of DMC)

| Family | SIDs | rep | player | relationship |
|---|---|---|---|---|
| 3 | 1461 | Katusha | init $1040 / play $10A1 | the dominant V5 player |
| 5 | 34 | Femmin3 | (sibling) | 0.832 to family-3 = same player |
| 4 | 686 | Jupiter41 | init $1040 / play **$1095** | 0.310 to family-3 = **distinct branch** |

So TWO RE targets: **family-3/5 (1495)** dominant + **family-4 (686)**
a distinct branch (same init offset, different play offset + ~0.31
Jaccard → significant code differences; likely a different V5 version).

## V5 engine differences from V4 (from docs + Katusha RE)

- **8-byte instrument** (AD, SR, WV-ptr, PU-ptr, FL-ptr, vib delay,
  vib speed, vib width) vs V4's 11-byte. Editor layout $4000+8n, ids
  $00-$1F.
- **Three programmable 2-byte tables** (wave / pulse / filter), one
  entry consumed per frame, `$90 nn` = loop to absolute position nn
  ("direct-pointer"). V4 had inline pulse-speed bytes + a fixed vib
  table; V5 makes pulse + filter fully programmable.
  - wave entry: byte0 = SID ctrl (bit3/$08 test = drum/hi-freq mode →
    byte1 goes straight to freq-hi); byte1 = semitone arp offset (or
    literal freq-hi in drum mode).
  - pulse entry pairs: start (12-bit), then (16-bit add, frame-count)
    pairs; PU=0 = no restart.
  - filter: like pulse, all 16 bits; FL=0 = no restart.
- **Full 11-bit filter cutoff**: play body writes BOTH `$D415` (lo) and
  `$D416` (hi) — V4 only wrote `$D416`. **Filtering only voice 3** (per
  docs). $D415←$1017, $D416←$1016 once per play() (Katusha $10CA-$10D3).
- **~14 sector commands** (DUR, SND, FD+/FD- fade, GLD 2-note, SLD
  1-note, ADR set-AD, SRR set-SR, FRQ filter-base, FLT type|res, VOL,
  GATE, SWITCH-tie, END) vs V4's ~8. Byte encoding UNKNOWN (the docs
  give the command SET, not the bytes) — must RE from the dispatch.
- **Drum** = wave-entry test bit, not an instrument fx flag. **Tie** =
  SWITCH command. **Fade** (FD+/-) is new (no V4 analogue).
- Sector terminator `$FF` (like family-2, unlike canon V4's `$7F`).

## Katusha player map (family-3, the RE seed)

- entry: 2-entry jump table — init `JMP $1040`, play `JMP $10A1`.
- play `$10A1`: push $F8/$F9; speed-delay $1842; speed counter
  $1013 vs reload $1012; `JSR $10DD` ×3 (voices); then `$D415←$1017`,
  `$D416←$1016` (filter); pull $F8/$F9; rts.
- voice `$10DD`: tick (dur ctr $17DB,x) → fetch or `JMP $1332` (effects).
- track dispatch `$10FF`: `$FF` end/loop (next byte = loop pos), `$FE`
  voice-end (clear $1006,x), `$FD`/`$FC` transpose ±(→$17E4,x), then
  sector# → ptr table $196E/$1972,y.
- sector dispatch `$115B`: byte < $80 → `JMP $12B5` (note); ≥ $80 →
  commands (`$FD` at $1162 sets $17DE,x, ...). **THE command byte map is
  the main RE task.**
- SID write sites traced (reg → PCs): the per-voice freq/pw/ctrl at
  $12xx-$13xx + $16xx; $D417 once ($123E); $D418 ($1345/$1658).
- reachable code $1040-$170E (~713 instrs; comparable size to V4).

## Migration plan (phased — a FULL engine migration, multi-session)

- **Phase A — RE family-3/5 player.** Generate + annotate
  `pipelines/dmc/v5/disassembly.s` (Katusha seed). Map: init, play,
  per-voice, the 3 table interpreters, **the sector command byte map**
  (the flagged unknown — derive from the $115B+ dispatch), the write
  order, the packed memory map (instrument block / tables / tracks /
  sector ptrs after the $2E00 packer).
- **Phase B — V5 extract + USF schema.** Binary→V5 model (dataflow
  operands like V4). USF additions: the 3 programmable 2-byte tables
  (content-by-reference, like FC aux), fade commands, full filter
  cutoff, ADR/SRR sector register-sets. Reuse `_offtable_check` pattern.
- **Phase C — V5 composer.** OUR V5 engine (new — the V4 composer does
  NOT apply). Write-log-first on Katusha → FULL. Verdict: `verify_dmc`
  (the trichotomy/per-IRQ infra is engine-neutral, reuse as-is).
- **Phase D — factory + wide batch** over family-3/5 (1495). New
  `dmc_v5_config` factory (carved V5 reference, probed knobs) + reuse
  `tools/dmc_family_batch.py` (--members the V5 list).
- **Phase E — family-4 branch (686).** A second RE pass (0.310 Jaccard
  = real differences; likely a V5 version variant — diff its disasm
  against family-3's, like family-2 vs V4).

## Effort + yield estimate

- Comparable to the V4 migration (which took multiple sessions): a full
  RE + new extract + new composer + schema + factory, ×2 branches.
- The sector-command byte encoding (Phase A) is the principal unknown;
  everything else is documented at the parameter level.
- Yield: if V5 reaches the ~55-65% FULL the V4 families hit (the
  off-table architectural limit applies here too), that's ~1200-1400
  more FULL → DMC total ~6200-6400 (~58-60% of all 10,676 DMC).
- Reusable as-is: verify (`pipelines/dmc/verify.py`, trichotomy/per-IRQ),
  the factory + wide-batch pattern, `dmc_mass_write.py`, the USF
  pipeline, the regression harness.

## Recommended first step

Phase A on Katusha: seed + annotate the disassembly and crack the sector
command byte map. That single artifact unblocks the extract + composer
and de-risks the rest.
