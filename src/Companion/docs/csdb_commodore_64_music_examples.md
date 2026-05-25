---
source_url: https://csdb.dk/sid/?id=14353
fetched_via: WebFetch direct
fetch_date: 2026-05-25
author: CSDb (Commodore Scene Database); comment by user "ice00"
content_date: 1985 (SID release date); CSDb commentary undated
reliability: primary (CSDb is the canonical scene archive); ice00 is
  the author of JC64dis and has reverse-engineered this engine.
---

# Commodore 64 Music Examples — Rob Hubbard 1985

## SID metadata (CSDb)

- **Composer**: Rob Hubbard
- **Released**: 1985 Rob Hubbard
- **Load**: $086D
- **Init**: $087C
- **Play**: $086D
- **Subtunes**: 15 (default 1)
- **SID model**: 6581 / PAL
- **Size**: 14782 bytes ($39BE)
- **HVSC**: /MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid

## The key identification (ice00, JC64dis author)

> "Unless all the others, tune 1 is not made with the Hubbard player
> (that has an A4 note of 440Hz). It uses a player (heavily modified
> and not used in any other HVSC sids) that points to a Chris Murray
> origin with his notes representation (with an A4 note of 423Hz)."

Implications for SIDfinity:

1. **Tune 1 uses the Chris Murray variant** of the Companion engine
   (A4 = 423 Hz frequency-table tuning) — this is recognised by
   sidid as `Companion/Murray`.
2. **Tunes 2..15 use Hubbard's variant** of the Companion engine
   (A4 = 440 Hz), the base `Companion` signature.
3. The Murray version is otherwise unique within HVSC according to
   ice00 ("not used in any other HVSC sids"), but Murray's own
   "Henry's House" (1984 English Software) is the canonical Murray-
   variant tune — it just isn't in HVSC under "Murray" because
   ice00 found the Murray fingerprint inside Hubbard's collection.

## Notable scene usage of this SID

Used in multiple demos and music compilations 1985-1989 by groups
including Thundercats, Crackmasters, and The Force.

## What this tells us about the engine

- The Companion engine family has **distinct frequency tables per
  variant** (440 Hz Hubbard/Bowden vs. 423 Hz Murray vs. 433.5 Hz
  Raeburn-separate-engine). For our pipeline, this means we need to
  detect which tuning is used and emit the appropriate freq table.
- Hubbard apparently re-bundled both his own driver code AND a
  separately-coded Murray-derived driver into a single PSID for the
  *Examples* collection, which is significant for whether we treat
  this as one or two engines in the migration plan.
