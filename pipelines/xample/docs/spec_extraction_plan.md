# X-Ample / Compotech — Extraction Plan

## Provenance
- Source: `research.md` (sibling-agent synthesis), HVSC #84 DB queries (`hvsc84.db`)
- Author: synthesis agent, 2026-06-13
- Method: GATHER + SYNTHESISE only — no siddump, no disasm, no py65
- Labels: DOCUMENTED = from research.md or confirmed DB observation;
          INFERRED = logical deduction from DB patterns or general C64 convention;
          OPEN = requires disassembly of a canary SID to confirm

---

## 1. Family Overview

**Authors:** Markus Schneider (driver/player), Helge Kozielek (optimisations),
Joachim Fräder (editor UI) — X-Ample Architectures, Germany, 1989–1995.
No public source code.

**HVSC #84 census (engine label `X-Ample`):** 380 SIDs
**Related label `Reflextracker`:** 137 SIDs (see §4.4)
**Related label `(XTracker_V4.2x)`:** 1 SID

**Major composers (by SID count):**
- Tufan Uysal (SoNiC) — 123 X-Ample + 26 Reflextracker = 149 total
- Thomas Detert — 92 X-Ample
- Steven Diemer (A-Man) — 60 X-Ample
- Markus Schneider — 38 X-Ample
- Michael Pehl (The Noise Art) — 14 X-Ample
- André Buerger (AEG) — 13 X-Ample

---

## 2. The Multi-Variant Problem — READ THIS FIRST

Unlike FC's standard-vs-Tel split, the X-Ample family shows **at least four
structurally distinct engine configurations** detectable from PSID metadata
alone, before any disassembly. Each variant likely has a different data
format (pattern/sequence/instrument layout) and therefore needs its own
extractor + config, analogous to `pipelines/future_composer/standard/` vs
`pipelines/future_composer/tel/`.

**Do NOT attempt a single unified extractor** until at least two variants are
disassembled and the data layouts compared. The risk of accidental wrong-variant
extraction silently passing on coincident writes is high.

---

## 3. Variant Taxonomy (from DB observation)

### Layout A: `init = BASE, play = BASE+3` (DOCUMENTED — 192 SIDs, 51%)
The standard Compotech/XTracker pattern. `init` is the subtune-select entry;
it stores the subtune number and falls through to `play` (or JSR/JMP to it)
three bytes on. `play` is the per-frame call vector.

**Typical load addresses:** $1000, $A800, $A803, $B000, $B003, $E000/$E003.
The player is fully relocatable. DOCUMENTED: the three-byte gap matches a 6502
JMP absolute ($4C lo hi) — init starts with `JMP play` (INFERRED: so calling
init with subtune in A sets up state then falls into play; play starts the
actual voice iteration loop).

**Representative canaries:**
- `MUSICIANS/S/Sonic/Moorhuhn_2.sid` (SoNiC, 11 subtunes, init=$1000,
  play=$1003)
- `MUSICIANS/A/A-Man/Honeycomb.sid` (A-Man, single subtune, init=$1003,
  play=$1000 — see Layout B below)
- `MUSICIANS/S/Schneider_Markus/Lethal_Zone.sid` (Schneider, 10 subtunes,
  init=$1003, play=$1000)

### Layout B: `init = BASE+3, play = BASE` (DOCUMENTED — 118 SIDs, 31%)
Complement of Layout A: `play` is at the base, `init` is +3. Functionally the
same engine; the two entry-point roles are simply reversed in the PSID header.
May be a later editor version that swapped the convention, or composers who
registered the header addresses differently.

INFERRED: Layouts A and B are almost certainly the **same binary player**,
just with the PSID header's init/play fields set differently by different
composer tool versions. Confirmed by the overlap of SoNiC (103 Layout-A SIDs
vs 9+ Layout-B SIDs) and Schneider using both layouts.

**Canary:**
- `MUSICIANS/S/Schneider_Markus/Apoxoly.sid` (8 subtunes, init=$E003,
  play=$E000)

### Layout C: `init = BASE, play = BASE+6` (DOCUMENTED — 16 SIDs, 4%)
The six-byte gap does not fit a simple `JMP abs + fall-through`. Two
possibilities: (a) an extended entry stub (2× JMP, or a 6-byte init
preamble before the play code begins); (b) a different engine variant
with a longer init sequence.

Seen primarily in **Thomas Detert** (`Circuit`, `Hyper_Aggressive`,
`Bounce`, `Starforce`) and **Tufan Uysal (SoNiC)** (`Crush_level_*` at
$680C/$6812 — 9 SIDs; `Fire-The_Demo` at $A000/$A006).

OPEN: Whether this is the same player binary with a different init stub,
or a distinct version (e.g. XTracker V4.1x vs V4.2x). **Requires disasm
of one Detert +6 canary and one SoNiC Crush canary.**

**Canary:**
- `MUSICIANS/D/Detert_Thomas/Bounce.sid` (3 subtunes, init=$3000, play=$3006)
- `MUSICIANS/S/Sonic/Crush_level_1_tunes.sid` (init=$680C, play=$6812)

### Layout D: `play = $0000` / CIA-driven — Reflextracker (DOCUMENTED — 137 SIDs)
All 130 primary Reflextracker SIDs have `init=$C006, play=$0000`. The zero
play vector means the VBI (50 Hz) player vector is NOT set; the player
runs under CIA timer interrupt only. This is categorically **Mode 2
(cycle-relevant, CIA-driven)** and may be the X-Ample_Digi variant or
a distinct Polish-scene fork (authors: Warlock, Data, JFK, Gregfeel,
Mephisto, Randy, Mini Cat — almost all Polish composers, distinct from
the German-dominated X-Ample core).

**Flagged as LIKELY OUT OF SCOPE for the standard Mode-1 pipeline.**
Recommend deferring the Reflextracker sub-family until the standard
X-Ample is migrated and the digi/CIA pathway (as established for
Chimera) is available. See §4.4.

### Layout E: Other / unusual (DOCUMENTED — 53 SIDs, 14%)
Miscellaneous offsets including:
- **Vincent Merken (Dick) cluster:** 12 SIDs, init=$116C, play=$09D1.
  Very unusual — init/play addresses 1947 bytes apart. OPEN: this may be
  a sub-variant with init and play in different code sections.
- **Thomas Detert multi-section SIDs:** `Eskimo_Games` (init=$5166,
  play=$515D, −9 offset), `Clystron` (init=$644C, play=$6458, +12 offset),
  `Darksword` (init=$6926, play=$698E, +104 offset). OPEN: whether these
  are distinct driver versions or songs with an extra header/loader stub.
- **Markus Schneider exotic SIDs:** `Stuemp` (init=$7CA, play=$5800 —
  huge gap), `Crystal_Fever` (init=$2A88, play=$7000). OPEN: these may
  be early pre-Compotech driver versions or songs with separate init
  loaders.

---

## 4. Per-Variant Extraction Plan

### 4.1 Canonical Target: Layouts A/B (310 SIDs, ~82%)

This is the highest-ROI target. Step-by-step:

**Step 0 — Sidid signature confirmation.**
Run `sidid` (or inspect its `.cfg`) for `Compotech_V2.x` and
`XTracker_V4.1x` / `XTracker_V4.2x` signatures. The sig covers a byte
pattern in the play routine; record the exact byte sequence.
OPEN: which sidid variant maps to Layout A vs B vs C.

**Step 1 — Seed disassembly on a single-subtune Layout-A canary.**
```bash
python3 tools/seed_disassembly.py \
  hvsc84/MUSICIANS/S/Sonic/4k_Intro_windows_95_mix.sid \
  pipelines/xample/standard/disassembly.s
```
Use a small-single-subtune SID to minimise the data section. Annotate:
- The 3-byte init stub (INFERRED: `JMP play` or `STX $zp; JMP play`)
- The voice iteration loop (DOCUMENTED: bitmask over 3 voices)
- The per-voice dispatch subroutine
- SID base register pointer (+7 per voice: DOCUMENTED)
- Song/pattern/sequence table pointers (OPEN: exact layout unknown)
- Instrument table pointer (OPEN)
- Effect table pointer(s) (OPEN)

**Step 2 — Data format reverse engineering (OPEN for all sub-items).**
After disassembly annotation, determine:
- OPEN: Pattern format (note/duration/command bytes? rows×columns?)
- OPEN: Sequence/orderlist format (pattern indices + transpose?)
- OPEN: Instrument program format (ADSR, waveform, arpeggio, pulse, vibrato)
- OPEN: Effect set (arpeggio, vibrato, portamento, PWM, filter, volume fade)
- OPEN: Multi-subtune dispatch mechanism (pointer table? single byte index?)
- OPEN: Song-end detection (loop, halt, or fade)

**Step 3 — Canary extraction + verify.**
Build extractor (`pipelines/xample/standard/extract/to_usf.py`).
Verify with `pipelines.hubbard.verify.verify_all` pattern (adapt for
X-Ample): single-subtune canary first, then multi-subtune.

**Recommended canary sequence:**
1. `MUSICIANS/S/Sonic/Castlevania_64_Mixes.sid` — SoNiC, 3 subtunes,
   Layout A, well-known composition
2. `MUSICIANS/S/Schneider_Markus/Lethal_Zone.sid` — Schneider, 10 subtunes
3. `MUSICIANS/D/Detert_Thomas/Eon.sid` — Detert, 9 subtunes

### 4.2 Layout C (+6 offset) — Secondary Target (16 SIDs)

After Layout A/B is done: seed-disassemble `Bounce.sid` + a SoNiC
`Crush_level_*` SID. Compare the entry stub.

OPEN: If the rest of the player binary is identical to Layout A/B, this
variant only needs a different entry-point detection in the factory probe;
the extractor is shared. If the data format differs, it needs its own
extractor config.

### 4.3 Layout E Exotics (53 SIDs)

Defer until after A/B/C. Each exotic group needs its own per-SID
investigation:
- Vincent Merken cluster: likely an older pre-Compotech variant
- Schneider early SIDs: possibly original Parsec Music Editor driver

### 4.4 Reflextracker / CIA-Driven (137 SIDs) — DEFER

**Recommendation: DEFER and flag in `tools/excluded_sids.json` with
reason "Reflextracker: CIA-driven sampler variant; requires Mode-2
digi pipeline. Defer until X-Ample standard pipeline is complete."**

Rationale:
- play_addr = $0000 on all 130 primary members → no VBI vector →
  standard Mode-1 per-frame capture is not applicable
- The init at $C006 suggests a CIA-timer-driven loop, analogous to
  the X-Ample_Digi sidid variant
- The authors (Warlock, JFK, Data, etc.) form a distinct Polish-scene
  cluster, separate from the German X-Ample core
- Quantification: 137 SIDs, 0 of which have a non-zero play vector
  (= 100% of Reflextracker is digi/CIA)
- Precedent: Chimera's digi pipeline is the right model; revisit
  Reflextracker after standard X-Ample Mode-1 is migrated

---

## 5. Factory Probe Design (INFERRED — verify with disasm)

The FC standard pipeline uses a fingerprint DB (`tools/engine_fingerprint.py`)
to map each SID to its player variant. A similar approach is recommended here:

1. **Relocation-invariant fingerprint:** extract a short byte run from
   the play routine at a fixed offset from `play_addr`. The bitmask-based
   3-voice loop is likely a stable fingerprint across all relocations.
   OPEN: exact byte sequence to use as the fingerprint.

2. **Layout detection:** `abs(play_addr - init_addr)` gives the entry
   offset group (3, 6, or exotic). Use this as a cheap pre-filter before
   the fingerprint check.

3. **Subtune multiplexing:** OPEN — unknown whether multiple subtunes are
   dispatched via a pointer table, a subtune-index byte stored in ZP, or
   a direct pattern-table offset. The multi-subtune Schneider SIDs
   (`Lethal_Zone` with 10 subtunes) are the best canary for this.

---

## 6. USF Schema (Preliminary — all OPEN until data format confirmed)

Do NOT design the USF schema before the data format is known. The following
are placeholders derived from general tracker convention:

- OPEN: Pattern format → likely maps to USF `Pattern` with note/duration/command rows
- OPEN: Sequence/orderlist → likely maps to USF `Orderlist` per voice
- OPEN: Instruments → likely maps to USF `Instrument` with ADSR + program
- OPEN: Effects → unknown set; may share FC or Hubbard effect categories

**Mandatory:** Re-read `docs/usf_representation_principle.md` IN FULL before
designing any USF representation for this engine.

---

## 7. Leads to Follow

See end of document (project-level leads section).
