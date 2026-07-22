---
name: project_music_assembler_target
description: "Music_Assembler — the largest un-migrated HVSC family with completed research (6,351 SIDs, engine_docs OK). Why it is the designated next family, and the DMC member that already depends on it."
metadata: 
  node_type: memory
  type: project
  originSessionId: fc3f0dc2-7e5f-4a76-bce6-958991c22a69
  modified: 2026-07-22T11:09:14.607Z
---

STATUS (2026-07-22): **STARTED — anchor + census + sequence decode are in.**
`locate.py` finds the player and its tables; `extract/decode.py` decodes
orderlists + sequence streams; `tools/masm_census.py` / `tools/masm_decode_check.py`
are the scale checks. **5,618 / 6,351 (88.5%) locate; of those 5,455 (97.1%)
decode cleanly** (1.28M notes, 290k preset selects, 57k filter cmds, 18k
slides), and the 8-byte PRESET table is decoded for all of them (46,660
presets). Next: the arpeggio table, then a model -> USF -> composer. Nothing
is write-stream-verified yet — no rebuild exists, so every number here is
structural, not a verdict.

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
| presets with vibrato / pulse-slide / arpeggio | 22,829 / 22,715 / 35,833 |

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
