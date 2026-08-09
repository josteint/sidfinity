---
source_url: local: tools/basic_program_survey.py over hvsc85/ (ROM-enabled siddump)
fetched_via: local read
fetch_date: 2026-06-23
author: SIDfinity orchestrator
content_date: 2026-06-23
reliability: primary
---

# Basic_Program — capture survey results (post-ROM-patch)

After patching `siddump` to load real C64 ROMs (commit 495c877, `--roms-dir`),
all 486 RSID-BASIC tunes now execute and emit `$D400` write streams. This is the
empirical survey that validates Blocker 1's fix and sizes the exclusion set.

Tool: `tools/basic_program_survey.py` — each tune captured TWICE via
`siddump --writelog` at `min(songlength*1.1, 30s)`; records richness +
run-to-run determinism. Raw: `tmp/basic_program_research/survey.jsonl`.

## Headline results

- **Determinism: 486/486** produce **byte-identical** `(reg,val)` streams across
  two runs. The whole family is reproducible under Path B (freeze one canonical
  emulator realization). This empirically confirms C3's thesis and overrides
  C4's "RND/TI = nondeterministic" worry — that framing is real-hardware /
  re-execution; it does NOT apply to capturing a deterministic emulator.
  (Structural reason: libsidplayfp's only entropy is `m_rand`, used solely for a
  random `powerOnDelay`; we set `powerOnDelay=0`, so it is never drawn.)
- **Musical content: 486/486.** 481 show clear freq+activity within 30s; the
  other 5 are **late-start** (long DATA-read / array-build before the first note)
  and were confirmed musical with a 120s window (see below). **No tune requires
  input to make music.**
- **Genuine exclusions needed: 0** (vs the agents' estimate of ~5–32). No
  nondeterministic-unreproducible tunes; no "no music without keypress" tunes.

## The 5 late-start tunes (survey window too short, NOT broken/empty)

Confirmed musical at `--duration 120` (freq / gate write counts):

| Tune | freq | gate | why slow |
|---|---|---|---|
| `DEMOS/UNKNOWN/God_Save_the_King_BASIC.sid` | 613 | 736 | builds `PI%(168,1)` pitch table from DATA first |
| `DEMOS/UNKNOWN/Mexican_Hat_Dance_BASIC.sid` | 1356 | 1686 | same "Voice Player" `PI%(168,1)` build |
| `DEMOS/UNKNOWN/Ueber_den_Wolken_BASIC.sid` | 552 | 440 | `GOTO 1000` past lyrics; `DIM …(999)` + 95 DATA |
| `GAMES/A-F/Casino_Poker_BASIC.sid` | 1077 | 281 | builds `H/L/K(1,300)` note arrays from DATA |
| `MUSICIANS/L/Latimer_Joey/Computer_Shake_BASIC.sid` | 2158 | 1532 | builds `V1/V2/V3(~400,3)` arrays from DATA |

The `IF PEEK(653)>0 THEN END` lines in the Voice-Player tunes are "press Shift to
stop", NOT an input gate. **Implication for migration:** the capture/verify window
must be `max(songlength*1.1, generous_floor)` — HVSC songlengths for these obscure
BASIC tunes can understate the setup phase (see [[reference_songlength_overrides]]);
a few may need overrides so the captured stream includes the actual music.

## The 1 digi tune — Mode 2, not Mode 1

- `DEMOS/A-F/Black_Box_V8_Demo_BASIC.sid` writes **`$D418` ~107×/frame** (53,553
  writes / 10s) — classic 4-bit volume-register digi (sample playback). Timing IS
  the signal here, so it belongs in **Mode 2 (cycle-exact)** like Chimera, not the
  flat `(reg,val)` stream. It is the ONLY digi tune in the 486; the other 485 are
  Mode 1 (flat per-write sequence, cycles dropped).

## Net for the migration

- Path B (writelog trace-lift) is viable for **all 486**; expected exclusions: **0**.
- Verify the 485 with a flat un-bucketed `(reg,val)` compare + `duration_tol`.
- Route the 1 digi tune (`Black_Box_V8_Demo`) through the existing cycle-strict
  (Mode 2) path.
- Capture window = `max(songlength*1.1, floor)`; add songlength overrides for the
  handful of late-start tunes whose HVSC duration is too short.
