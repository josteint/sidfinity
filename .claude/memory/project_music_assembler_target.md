---
name: project_music_assembler_target
description: "Music_Assembler — the largest un-migrated HVSC family with completed research (6,351 SIDs, engine_docs OK). Why it is the designated next family, and the DMC member that already depends on it."
metadata: 
  node_type: memory
  type: project
  originSessionId: fc3f0dc2-7e5f-4a76-bce6-958991c22a69
  modified: 2026-07-22T15:29:07.054Z
---

STATUS (2026-07-22, round 2): **THROUGH USF, wide batch 3,915 / 6,351 FULL
(61.6%; 71.2% of the 5,502 members with a locatable player).** The pipeline is
SID -> USF -> SID. Regression portfolio (16 members) + the Freespace_2075
cross-family canary are wired as tier 1 in `tools/regression.py`; the family
batch is `tools/masm_family_batch.py` (tier 2, code_hash-gated).
Freespace_2075 (the DMC+MA heterogeneous member) is now DETECTED, counted FULL
by the DMC batch, and STORABLE as one `.usf` (ledger C35 `origin_engine`).
NOT yet done: the MA family's own corpus mass-write/sync (deliberate — 33%
residue is too high to store).

## ✅ #85 SWEEP (2026-08-19, overnight): 4,021/6,489 FULL (62.0%), 0 regressions
Full family re-verify under current code. +138 members vs the Jul-22
baseline (tmp/masm_wide_results.pre85sweep.jsonl): 104 new FULL, 19
partial, 15 unsupported, 2 gains, 0 gone. Corpus mass-write still
deliberately NOT done (standing decision).

## Round 2 (2026-07-22) — USF round trip + ledger C6

Three landed changes, each with its own commit:

1. **C34 (new ledger entry) — post-preset dispatch.** The byte after a preset
   select is consumed by the preset handler itself (`$C0EC: INY / LDA ($FA),Y
   / CMP #$60 / BCS <rest handler>`), which skips the `$A0` hold sub-split AND
   the end-of-pattern test. So `$A0..$FF` there is a REST and `$FF` there is a
   rest of duration `$1F`, not a terminator. 6% of members. **The write-stream
   verdict is structurally blind to this** — re-emitting the mis-decoded byte
   round-trips through the same handler — so it was only findable by reading
   the handler. It corrupted USF CONTENT only (a `tie` where the music rests).

2. **SID -> USF -> SID.** No per-engine block; the mapping is in
   `extract/to_usf.py`'s header (presets -> instruments, arpeggios -> the
   instrument's WAVE PROGRAM, sequences -> note rows with C14 fx_flags,
   orderlists -> Orderlist's own transposes/repeats). 10 new schema fields,
   all on the musical axis. Also fixed: the composer honoured no orderlist
   loop TARGET, so the `$FD nn` variant (260 members) silently wrapped to
   entry 0 — it needs no USF flag, since we emit our own advance.

3. **Ledger C6 off-table freq — the round's big lever, sample 12/60 -> 41/60.**
   See the C6 entry for the three transferable lessons (freqhi sits BELOW
   freqlo so hi reads land in PLAYER CODE; the reach walk must carry running
   instrument AND running note across sequence boundaries; off-table reach
   predicts the verdict almost exactly — 43/48 partials had it, 11/12 FULLs
   did not).

**METHOD WORTH REUSING — the knock-out sweep** (now recorded in ledger C7).
Rather than mint a typed init field per work-file leftover, zero each of the
24 and diff the emitted WRITE STREAM over a member sample: 10 never moved it.
Then EXPLAIN the dead set from the engine — init leaves `durctr` at 0, so every
voice FETCHES on frame 0 and that fetch overwrites gmask/curnote/presetx/arppos
before any read; what survives is exactly a voice idling mid-note. That
explanation is what makes the drop safe rather than sample-lucky. 10 fields
not added.

### Residue (from the authoritative batch, not a sample)

1,587 partials, by first diverging register:

| | | |
|---:|---:|---|
| 370 | 23.3% | length_only (state + prefix match, lengths differ) |
| 323 | 20.4% | global `$D416` — filter cutoff |
| 181 | 11.4% | global `$D418` — master volume, which the composer writes only at init |
| 223 | 14.1% | `freq_lo` (V1 82 / V2 65 / V3 76) |
| 79 | 5.0% | no first diff recorded |
| ~140 | 8.8% | per-voice `ctrl` |
| 102 | 6.4% | per-voice `sr` |

849 unsupported: **742 no player located** (the predicted version tail —
V1.1/V1.4 Triad, VoiceTracker, DoubleTracker/Ten Tracker), 55 arpeggio and 50
sequence non-termination, 2 track-pointer.

NEXT LEVERS, in dependency order (`feedback_residue_triage_order`): the two
chip-global buckets are half the residue and neither is modelled at all —
`$D418` is not written after init (likely a C10 per-song master-volume
automation or a player variant), and `$D416` is the filter sweep. Then
`length_only`, which is a rate/song-end class, not a content class.

## Census result (tools/masm_census.py, 2026-07-22)

| | |
|---|---:|
| locate OK | 5,618 (88.5%) |
| no player found | 733 (11.5%) |
| signature offset from base | `+$91` on **all** 5,618 |
| PSID vectors `init=base+$48/play=base+$21` | 2,746 |
| PSID vectors `init=base+$00/play=base+$03` | 2,561 |
| other vector convention | 311 |
| song speed 2 / 3 / 1 / other | 3,296 / 990 / 819 / 513 |
| single-subtune members | 5,509 |
| player materialised by init (packed, C26) | 9 |

The 733 misses are the predicted version tail (V1.1 / V1.4 Triad,
VoiceTracker derivative, multispeed DoubleTracker/Ten Tracker) — not yet
triaged. `tmp/masm_census.jsonl` holds the per-member rows.

## Decode check (tools/masm_decode_check.py, 2026-07-22)

| | |
|---|---:|
| decode clean | 5,455 (97.1% of located) |
| suspect (note index past the freq table) | 102 |
| decode error | 52 |
| notes / rests / holds / presets | 1,284,997 / 115,961 / 37,237 / 289,945 |
| slide / filter / legato events | 18,230 / 57,304 / 15,896 |
| presets decoded (median 8/member, max 32) | 46,660 |
| presets with vibrato / pulse-slide / arpeggio | 22,771 / 22,670 / 35,759 |
| arpeggios decoded (median 6/member, max 15) | 31,369 |
| arpeggio steps (mean 4.4/arp) | 140,151 |
| arp steps absolute / relative | 50,394 / 89,757 |

The 102 "suspect" members overrun the 96-entry freq table by 1-12 notes after
transpose — the classic OFF-TABLE READ pattern (ledger C6/C2), to be handled
the way DMC's `offtable_freq` is, NOT a decode bug. The 52 errors are mostly
sequence pointers resolving to $0000.

## The preset (instrument) table — every field grounded by its READ SITE

`extract/presets.py`. 8 bytes/preset; base located from the player's own
operand (anchored on `LDA p+0,Y / STA zp / LDA p+1,Y / LDY voicebase,X /
STA $D406,Y`). Verified against the docs' own byte dump for Sid_Slam p0 —
`0E 08 09 08 84 0F 60 31`, byte-identical.

| +n | read at | meaning |
|---|---|---|
| +0 / +1 | $C235 / $C23A | AD -> $D405, SR -> $D406 |
| +2 | $C252 | waveform/ctrl -> $D404 (note-init frame writes the PREVIOUS ctrl gate-cleared = the hard restart) |
| +3 | $C258 | pulse width init (seeds BOTH pulse work slots) |
| +4 | $C324 | pulse slide step, per frame, gated on +7 bit $40 |
| +5 | $C277 (`LSR A`x3 = delay), $C310 (`AND #$0F` = rate) | vibrato delay + rate |
| +6 | $C2ED / $C300 | vibrato DEPTH (+/- per half-cycle) |
| +7 | $C288 | Fx flags (bit $10 vibrato, $20, $40 pulse slide) + arpeggio index in the low nibble |

METHOD NOTE: scan for a field's read site across ALL `abs,Y` addressing forms.
A `LDA`-only ($B9) scan misses +6 entirely — it is reached by `SBC`/`ADC`
($F9/$79) — which nearly produced a wrong "the docs are wrong, +6 is unused"
claim. The docs ARE wrong here, but differently: the Fx+arpeggio byte is +7,
not +6, and +6 is the vibrato depth.

## Freespace_2075 — now DETECTED, CLASSIFIED and counted FULL by the DMC batch

**2026-07-22 (round 3).** Previously the audio was proven but the member was
outside the pipeline: `detect_compilation` returned **None** for it (the memory's
earlier "detection half is done" was wrong/stale), so the DMC batch reported
`error: track at $836F never settles` — it fell through to the single-player
path and tried to read an MA player as DMC.

Two things blocked detection, both in the landing test of `_observe_dispatch`:

1. the predicate only accepted a **DMC three-JMP head**; MA's base is
   `78 20 48 47 A9 18 ...` (SEI / JSR / IRQ install). The reloc-invariant MA
   anchor is init's fixed prefix at **base+$48**.
2. more subtly, the wrapper enters MA **at base+$48 (its init), never at the
   page-aligned base**, so the `not (pc & 0xFF)` alignment test could never
   fire. The alignment has to be applied to the DERIVED base. MA also carries
   no song number in A there (the accumulator holds copy-loop leftovers,
   $40/$47) — each packed MA player is one tune, so song = 0.

Implemented as a **second observation pass** (`_observe_dispatch_2pass`): the
DMC-only pass runs first and wins whenever it resolves, so broadening is
zero-regression by construction — only members currently detecting as NOTHING
can change. Censused over 300 random DMC members + Freespace: exactly **1**
member changes. The spec now carries `kinds` (`['dmc','masm','masm']`) recorded
AT THE LANDING, where the engine is actually known, rather than re-derived
later from an image that does not even contain a relocated player.

`heterogeneous.py` is now **spec-driven**: the hand-specified `copies` dict and
the 3-subtune-shaped dispatcher are gone — memory comes from a snapshot at the
landing, and the dispatcher is generated for N subtunes. The DMC family batch
routes these via `build_path='hetero_masm'` and reports the member **full**.

**CLOSED — it is now storable as ONE `.usf`** (31,245 bytes) and rebuilds
FULL on all three subtunes from that single stored artifact. The pieces:

- `origin_engine` per subtune (ledger C35) names which COMPOSER builds it.
  Read only by `build_from_usf`'s dispatch, never by an emitter.
- per-subtune `freq_table` + `default_filter` — the two normally file-level
  fields the packed players disagree on (DMC and MA tune differently; the two
  MA players carry different idle cutoff sweeps). NOT scaffolds: they stay
  meaningful under one unified composer.
- one merged instrument pool (9 + 13 + 13 = 35); `build_from_usf` projects a
  single-engine VIEW per subtune, so each composer sees exactly the file it
  would have seen alone.

THREE TRAPS, all silent, all cost real time:

1. **Grouping by ENGINE instead of by PLAYER.** Two subtunes can name the same
   FAMILY yet be different players; merging Freespace's two MA players into
   one view built one tune from the other's data. One composer instance PER
   SUBTUNE is correct by construction (a shared player just gets composed
   twice — image size, never correctness).
2. **Deriving the instrument slice from ROW REFERENCES — ledger C31's merge
   trap, which I walked straight into.** DMC's instrument i1 is referenced by
   no row of its only dispatched song, but init clears the note-init cache to
   0 so an idle voice runs RECORD 0's pulse/wave mechanism. Dropping it
   diverges at write 28. Blocks must TILE the id space (split at each
   subtune's lowest referenced id, first block starting at 1), never equal the
   referenced set.
3. **File-level init ownership.** The first player keeps the merged file's
   params/init slot; a later player's file-level params/init are parked on its
   subtune and lifted back at projection. Getting it backwards overwrote DMC's
   per-voice note/gate_mask priming with the subtune's thinner init and
   diverged at write 26 — with `state_match` still True, so it looked like a
   content bug rather than a plumbing one.

`dmc_mass_write` stores it (build_path `hetero_masm`), and both C20 audits
cover it: the fifth-layer invariant `build(stored .usf) == stored .sid` holds,
and `_rebuild_from_usf` dispatches on `origin_engine`.

## Freespace_2075: the original bring-up — ALL 3 SUBTUNES FULL

`heterogeneous.py`. A scan of all 163 DMC f1 partials found **exactly one**
member carrying an MA player: `Bayliss_Richard/Freespace_2075` (sub 0 = DMC v4
at $1000; subs 1-2 = MA players the round-85 RELOCATING wrapper copies
$2000->$4700 and $2800->$3700). The rebuild composes all three engines behind
a dispatcher at the PSID vectors — the dmc_sfx shape from ledger C31.

**Verified FULL on all three subtunes**: 225,157 / 127,969 / 35,179 writes
exact, state_match=True on each.

Two reusable pieces came out of it:
- `compose_asm(m, origin=, prefix=)` relocates an MA engine and prefixes every
  label, so SEVERAL MA engines can share one image.
- **`preset_table()`/`arp_tables()` searched the WHOLE 64K.** With >1 MA player
  present they returned the FIRST player's table for every player — an address
  not materialised for the others, so every preset field read back ZERO (right
  note frequencies, but SR/AD/ctrl/PW all $00). Both now take the `lo`/`hi`
  block bounds `locate()` already had. This is the bug that made sub 2 diverge
  at write 3.

NOT YET WIRED: `detect_compilation` does not classify MA sub-players and the
member does not round-trip through USF (built straight from the models), so
the DMC family batch still reports it partial. The AUDIO is proven; the
pipeline integration is not done.

## The composer — `composer_asm.py`, `verify.py` (2026-07-22)

Extract -> model -> composed 6502 -> write stream vs HVSC
(`compare_instruction_stream` in TRICHOTOMY mode: we emit our own init, so a
flat compare diverges at write 0 — ledger C21). Nothing is copied from the
image; sequences are RE-EMITTED from decoded events and all addresses are
assembler-resolved.

**INIT PRIMING is load-bearing** (trichotomy 4.5): the player's init clears
ONLY the 16-byte work block (base+$81..$90) and loads each track's first
orderlist entry — every OTHER per-voice byte keeps its file-image leftover,
audible from frame 1. `noteflg` (base+$141) carries bit6 "note already
initialised", so a voice whose first event is a REST (which never writes
noteflg) SKIPS its note-init. Decisive check: the leftover pwlo/pwhi and nfrq
ARE the original's frame-1 writes for V1/V2. `MasmModel.prime` carries these.

**Three tables are ENGINE CONSTANTS** (byte-identical across 58 members, so
mechanism, not content): voice bases $00/$07/$0E, vibrato direction
$00,$01,$01,$00, filter routing $F1/$F3/$F7 (= the manual's "the triggering
track and all lower tracks").

**Two bugs that cost the most time**, both fixed by reading the original's
$C177 rather than reasoning: `rattle` must init to **$FF** not 0 (it is EOR'd
with $FF per frame, so 0 inverts the rattling-slide phase), and `vibfr` must
be cleared at note start. Plus a self-inflicted one: PSID inline-load encoding
takes header load=0 WITH the inline prefix — passing both load=$1000 and the
prefix shifts the image two bytes and the player never runs (zero writes).

**DOMINANT RESIDUE = ledger C6** (off-table freq lookup). The first-divergence
census over 60 members is overwhelmingly freq-lo (33 of 40 partials);
localising one (Iron_Cat/Vibrations) shows the orig writing freq $D415 — an
OPERAND byte, not a frequency: the arpeggio note offset is masked to 7 bits
(0..127) and runs past the 96-entry freq table, so the original plays the
bytes that follow it. Same 102 members `masm_decode_check` flags as
`note_past_freq_table`. Cure is C6's canonical one (per-(instrument, offset,
note) records), NOT a contiguous window copy.

## The arpeggio table — `extract/arps.py`

Selected by preset+7's low nibble (0 = none); 16-entry lo/hi pointer tables
located from the runner's own operands ($C3E5). Read off the runner
($C3E5-$C436):

- **A STEP IS 3 BYTES**: `(waveform, note, filter_lp)`. The terminator is the
  FOURTH byte, PEEKED — it occupies the first slot of what would be the next
  step. `$FE` = STOP (and it clears the arp nibble in the voice's Fx byte, so
  the arpeggio stops running), `$FF` = LOOP to offset 0.
- `waveform` is ANDed with the voice's GATE MASK, which the sequence decoder
  sets to $FF on a note and $FE on a rest — that is how a rest releases the
  gate while an arpeggio keeps running.
- `note` bit7 = ABSOLUTE note index; otherwise it is an OFFSET added to the
  playing note. Result masked to 7 bits, used as the freq-table index.
- `filter_lp` 0 = leave the filter alone.

Corpus confirmations: max arpeggios per member is **15**, exactly the 4-bit
index cap; both bit-7 classes are heavily used (50,394 absolute vs 89,757
relative), so the distinction is real and not a misreading; mean 4.4 steps per
arpeggio. Decoded arps read as instrument macros — e.g. Sid_Slam's arp 1 is
`noise abs 95 -> pulse abs 31 -> triangle abs 31`, a percussion transient.

## Corrections to the research docs (verified at scale, not assumed)

Both are annotated at the head of
`pipelines/music_assembler/docs/spec_player_RE_grounded.md`:

- **Seq pointer LO is `$C675`, HI is `$C669`** — the doc's data-table row has
  them swapped (its own disassembly and byte dumps say otherwise). Checked on
  300 sampled members: 296 resolve as located, **0** need the swap.
- **The sequence opcode map has two ranges BACKWARDS in BOTH specs.**
  `$80..$9F` is **PRESET** (id = byte & $1F, 32 presets — the player does
  `ASL A`x3 = id*8), and `$A0..$FF` is **HOLD**; the docs say the opposite and
  claim `$A0..$AF` preset with a low NIBBLE. A preset byte carries no duration.
  The note flags byte is bit-flagged: bits 0-4 duration, bit 5 SLIDE (+2
  bytes), bit 7 FILTER (+2 bytes), bit 6 legato — not the docs' 3-bit opcode.
  TWO independent corpus confirmations: the max note index after transpose
  across all clean members is **95**, exactly the 96-entry freq table's last
  slot; and the max preset id in use is **32**, exactly the cap implied by
  `byte & $1F` — the docs' `$A0..$AF` low-nibble reading caps at 16, so the
  corpus itself rules it out. The 46,660 decoded presets' waveform bytes are
  also dominated by genuine SID control values ($09 hard-reset, $41 pulse+gate,
  $11 tri, $21 saw, $81 noise), which a mislocated table would not produce.
- **`$FD nn` = loop the orderlist to ENTRY nn**, and it is a PLAYER VARIANT
  (260 members): the second `INY` of the orderlist step at base+$1A1 becomes a
  `JSR` to a stub testing `CMP #$FD`. Detected positively (ledger C13);
  decoding it unconditionally would misread a base-build member's data.
  Handling it took decode errors from 270 to 52.
- **The base anchor is init's fixed prefix at base+$48**
  (`A9 1F 8D 18 D4 A9 F0 8D 17 D4`), NOT `signature - $91` and NOT
  `seqnum - $8D` — those offsets are build-dependent and cost ~50 members plus
  4 false positives when used as the primary anchor. With the init anchor the
  signature offset collapses to a single value (`+$91`) family-wide, which
  also supersedes README.md's `+$91/+$B5/+$70/+$191` spread.

## Why it is next

By CLAUDE.md's stated rule — *next family = the largest un-migrated family
whose `engine_docs` state is OK* — Music_Assembler IS the next family:

| family | SIDs | state |
|---|---:|---|
| dmc | 10,676 | migrated |
| goattracker | 8,670 | migrated |
| **music_assembler** | **6,351** | **OK, un-migrated ← next** |
| future_composer | 4,024 | migrated |
| soundmonitor | 3,625 | OK, un-migrated |
| jch_newplayer | 3,611 | OK, un-migrated |

## What is already known about its shape

From `docs/the_trichotomy.md` §2 (the init survey), Music_Assembler is the
"barely anything" init bucket and its signature is unusually sharp:

- init writes exactly **3 bytes**: `$D417 = $F0`, `$D418 = $1F`. Nothing else.
- It therefore **relies on the previous tune's chip state** for voice ctrl,
  freq, pulse width — our universal reset makes the rebuild *more* defined
  than the original here (trichotomy §5.3: Check A still passes, because the
  host stub starts from a clean reset).
- The player is compact (~1 KB of code) and its data model is DMC-like in
  outline: 2-byte track entries, `$FF` end-of-track / `$FE` stop markers,
  instrument select at `$60 + 5-bit id`, per-voice state arrays indexed by X,
  sector-pointer lo/hi tables, a freq table read as `freqlo[y]`/`freqhi[y]`.
  **Do NOT mistake that outline for DMC** — 0 of 11 DMC canon locate-sites
  match, and `dataflow.locate` returns None on it.

## The dependency that surfaced it

`MUSICIANS/B/Bayliss_Richard/Freespace_2075.sid` (DMC f1 partial) is a
HETEROGENEOUS C31 compilation: subtune 0 runs a DMC v4 player at `$1000`
(**FULL** today), while subtunes 1-2 run **Music_Assembler** players that the
init wrapper relocates into RAM (`$2000→$4700`, `$2800→$3700`). Its C31
detection half is done (round 85, commit 4985aa13); the member cannot go FULL
until an MA extractor exists and is wired as an MA sub-player — the
`dmc_sfx` precedent in ledger C31 (Canyon_Tank_Duel) is the pattern to follow.

Identification method + the trap that nearly hid it: [[project_dmc]] round 85
and the C31 recognition card (an opcode skeleton spanning a player's
SMC/scratch bytes reported "1 carrier in HVSC" for a 6,349-member family).

## Before starting

Run CLAUDE.md's three MANDATORY questions — `pipelines/music_assembler/docs/`
exists and must be read first; there is no `disassembly.s` or `RE_NOTES.md`
yet, so seed one with `tools/seed_disassembly.py` and annotate before coding.
