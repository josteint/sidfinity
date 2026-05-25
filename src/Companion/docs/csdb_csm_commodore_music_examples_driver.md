---
source_url: https://csdb.dk/sid/?id=14353
fetched_via: WebFetch
fetch_date: 2026-05-25
author: ice00 (comment author on CSDb)
content_date: comment posted on the SID's CSDb entry
reliability: secondary (community comment on primary source)
---

# CSDb: Commodore 64 Music Examples / Rob Hubbard / 1985

PSID specs from the page:
- Load address: $086D
- Init address: $087C
- Play address: $086D
- 15 songs, default song 1
- SID model: 6581 / PAL clock
- Data size: 14782 bytes

## ice00's comment (CRITICAL attribution)

> "tune 1 is not made with the Hubbard player" — uses "a player (heavily
> modified and not used in any other HVSC sids) that points to a **Chris
> Murray** origin with his notes representation (with an A4 note of **423Hz**)".
> The remaining tracks use the standard Hubbard player with an A4 note of
> 440Hz.

## Implications for the migration

1. **The "Companion" player is the Chris-Murray-lineage player**, predating
   Hubbard's own 1985 driver. The `Companion/Murray` sidid sub-tag is therefore
   the **canonical Companion player**; the bare `Companion` tag is the same
   player without the Y=$80/Y=$FF wrap tail being matched.
2. A4 = **423 Hz** (not 440 Hz) means the freq table is tuned ~30 cents flat
   vs. standard. This matters for any USF representation that converts
   note-number to absolute frequency — the Companion freq table is its own
   tuning system and must be carried verbatim (or note numbers must include a
   pipeline-side tuning offset).
3. `Commodore_64_Music_Examples.sid` is a **mixed-driver SID**: tune 1 = pure
   Companion (Murray-tuned), tunes 2-15 = Hubbard 1985 driver. So
   `sidid -> Companion` on this SID is a **majority-vote false positive** if
   you take it at face value; only subtune 1 is actually the Companion engine.
   The migration scope for Companion is therefore: `Up_up_and_Away.sid`
   (all 5 subtunes) + subtune 1 of `Commodore_64_Music_Examples.sid`.
