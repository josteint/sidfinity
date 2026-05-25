---
source_url: tools/sidid.cfg + data/sidid_full.txt + HVSC Musicians.txt
fetched_via: local repo + WebFetch
fetch_date: 2026-05-25
author: HVSC + sidid signature DB
content_date: 1984-1988 (release range of cited SIDs)
reliability: primary (HVSC is the canonical SID archive)
---

# Companion engine users in HVSC

## sidid signatures (from tools/sidid.cfg lines 393-403)

```
Companion
BC ?? ?? C8 98 9D 04 D4 60 END
(Sid_Sequencer)
1E 18 8B 7E FA 06 AC F3 E6 8F F8 2E 00 00 00 F0 END
(Aleatory_Composer)
1E 18 8B 7E FA 06 AC F3 E6 8F F8 2E 00 00 00 0E END

Companion/Jay_Derrett
29 0F 0A A8 B9 ?? ?? 85 ?? B9 ?? ?? 85 ?? EE ?? ?? AD ?? ?? C9 ?? D0 END
```

Note: `Sid_Sequencer` and `Aleatory_Composer` are sub-variants of
the base `Companion` signature (they share the same outer pattern
but with different trailing bytes — these are Vic Berry's sequencer
tunes, see below).

The "Murray" variant referenced in the task brief and in
ice00's CSDb comment does NOT appear as a separate top-level
sidid signature in our copy of sidid.cfg — only `Companion` and
`Companion/Jay_Derrett` are listed as primary engine labels here.
Murray's variant (A4 = 423 Hz) is presumably recognised as base
`Companion` because the structural pattern is identical; only
the frequency table differs.

## HVSC SIDs by Companion signature (from data/sidid_full.txt)

### Base `Companion` (26 hits)
- `MUSICIANS/B/Berry_Vic/Webern_Op_21.sid`
- `MUSICIANS/B/Berry_Vic/Triad.sid`
- `MUSICIANS/B/Berry_Vic/Test_File.sid`
- `MUSICIANS/B/Berry_Vic/Schillinger.sid`
- `MUSICIANS/B/Berry_Vic/In_C.sid`
- `MUSICIANS/B/Berry_Vic/Atonal_Music.sid`
- `MUSICIANS/B/Berry_Vic/SID_Sequencer.sid`
- `MUSICIANS/B/Berry_Vic/Bach_Sonata.sid`
- `MUSICIANS/B/Berry_Vic/Sigma.sid`
- `MUSICIANS/B/Berry_Vic/Te_Deum.sid`
- `MUSICIANS/B/Berry_Vic/Dufay.sid`
- `MUSICIANS/B/Berry_Vic/Progression.sid`
- `MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid` (15 subtunes; tune 1 is the Murray variant per ice00)
- `MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.sid` (5 subtunes)
- `MUSICIANS/H/Hoernell_Karl/Melonmania.sid`
- (remainder ~10 not listed in our snippet — would benefit from a full
  `grep -c "Companion$" data/sidid_full.txt` audit)

### `Companion/Jay_Derrett` (25 hits — partial sample)
- `MUSICIANS/R/Raeburn_Gavin/Gun_Runner.sid` (co-credit; Derrett's engine)
- `MUSICIANS/D/Derrett_Jay/Jetboys.sid`
- `MUSICIANS/D/Derrett_Jay/Destruct.sid`
- `MUSICIANS/D/Derrett_Jay/ZIP.sid`
- `MUSICIANS/D/Derrett_Jay/Thundercross.sid`
- (full list would extend to ~25 total; Derrett has 30+ games and
  the CRL gameography is most of them — e.g. Death or Glory,
  Ninja Hamster, Lifeforce, Equalizer, Mandroid, Rocky Horror,
  Blade Runner, Dracula).

## Nationality / period (from HVSC Musicians.txt)

- Jay Derrett — UK (England)
- Karl Hörnell — Sweden
- Gavin Raeburn (Gaxx) — UK (Scotland)
- Keith Bowden, Vic Berry, Chris Murray — **not listed** in
  Musicians.txt (likely below the 3-SID threshold for inclusion,
  except Bowden who only has "Roundabout").

## Coverage notes

- **Vic Berry's 12 tunes** are a goldmine for stressing the engine
  — they're sequencer/atonal pieces that probably exercise edge
  cases (Schillinger system arrangement, Webern's serialism, etc.).
  No biographical info found on Berry; he might be a contemporary
  scene member or an academic Pan/Birkbeck contact (since the
  book's author Bowden is at Birkbeck).
- **Karl Hörnell's "Melonmania"** is a 1986 Interceptor Software
  game and gives us a Swedish-developed test case.
- **Hubbard's 2 tunes** are our primary target.

## Recommendation for migration

Pick a target set in this order for engine-coverage:
1. `Up_up_and_Away.sid` (Hubbard, 5 subtunes, base Companion, A4=440)
2. `Commodore_64_Music_Examples.sid` (Hubbard, 15 subtunes; tune 1
   forces us to handle the Murray A4=423 variant; tunes 2-15 are
   base Companion)
3. `Roundabout.sid` (Bowden, the canonical "pure" form of the engine
   from the book)
4. Vic Berry's atonal set (12 tunes, stresses unusual patterns)
5. Karl Hörnell's *Melonmania* (one of the few game uses outside
   Hubbard)
6. Derrett's CRL catalogue (only after the base engine is fully
   migrated — Derrett's variant adds drum samples and brush slap
   effects that are not in base Companion).
