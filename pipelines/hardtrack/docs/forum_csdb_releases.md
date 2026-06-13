<!--
source_url:
  https://csdb.dk/release/?id=74928  (Hardtrack Composer V1.0 by Elysium, 1992)
  https://csdb.dk/release/?id=36647  (Hardtrack Composer V1.0+ [6 speed] by Beverly Hills Group)
fetched_via: WebFetch + WebSearch
fetch_date: 2026-06-13
authors/handles: Fred (CSDb commenter), release credits below
content_date: 1992 (release) / 2013 (comment)
reliability: secondary (CSDb release metadata + one comment; community-curated)
-->

# CSDb releases + comments — HardTrack Composer

CSDb release pages double as the scene's canonical credit/version record. Two
distinct CSDb entries matter for the version question.

## Release #74928 — "Hardtrack Composer V1.0" by Elysium (1992)

Credits (from CSDb):
- **Code:** Brush AND **Longhair** (both Elysium / Parados).
- Music: The Syndrom (Crest / The Imperium Arts) — demo tune "Frozen Energy".
- Graphics: Cruise (Padua).
- Main executable filename: `-HARDTRACK 1.PRG`.

Comment thread (verbatim):
> **Fred — 2013-08-04:** "I've added Longhair to the credits since he made the
> code of the player."

**Significance:** This is the authority for the split authorship the prompt
records — **Brush wrote the editor, Longhair (Miłosz Ignatowski) wrote the
PLAYER routine.** For our purposes the *player* is what emits the SID writes,
so Longhair's routine is the binary we parse. The 1992 date and Elysium/Parados
(Polish) provenance are confirmed.

## Release #36647 — "Hardtrack Composer V1.0+ [6 speed]" by Beverly Hills Group

Credits (from CSDb):
- **Code:** Brush (Elysium, Parados, Sex Instructors, Success), **Glover**
  (Samar Productions), **Longhair** (Elysium, Parados).
- Title string: "Hardtrack Composer **V1.0+ [6 speed]**".
- Download filename references **`v1.6speed`**.
- Released by Beverly Hills Group (a re-release / cracked-and-fixed variant).

**Significance — this is the multispeed lineage.** The "≤6× multispeed" trait in
our engine brief traces to this **"[6 speed]"** variant. Two takeaways:

1. The multispeed capability was packaged as a distinct **"V1.0+ [6 speed]"**
   build, with a THIRD co-author, **Glover (Łukasz Baran)** — corroborated by a
   YouTube upload "Hardtrack - Lukasz Baran (Glover) - (1997)". Glover appears
   to have produced the 6-speed player variant on top of Brush+Longhair's V1.0.
2. "V1.0+" naming (not "V1.1") suggests the **V1.1** label and the
   **[6 speed]** label may be the same lineage or adjacent — the
   community used loose version strings. The robust statement is: there is a
   plain V1.0 player and a 6-speed-capable V1.0+/V1.1 player; HVSC's ~1,170
   tunes mix both, and a multispeed tune is identified by its CIA timer rate
   (≤6×), NOT by a distinct data format.

## comp.sys.cbm (Usenet) — negative result

Searched Google Groups / narkive for HardTrack / Elysium in comp.sys.cbm. **No
HardTrack-specific thread exists.** The newsgroup discusses SID hardware (6581,
filters, HardSID) generically. This is expected: HardTrack was a Polish-scene
tool, and its discussion lived on Polish boards (c64scene.pl, c64power.com),
not English-language Usenet. Recording the negative result so a future session
doesn't re-search it.

## Version map (community-sourced, to confirm against binaries)

| Build string | Source | Co-authors | Notes |
|---|---|---|---|
| V1.0 | CSDb #74928 (Elysium 1992) | Brush + Longhair | Original release, demo tune "Frozen Energy" |
| V1.0+ [6 speed] / "v1.6speed" | CSDb #36647 (Beverly Hills Grp) | Brush + Glover + Longhair | Multispeed (≤6×) variant; Glover added |
| V1.1 | c64power.com v2.0 thread ("Player 1.1 = original 1.0 format") | Longhair | Same *data format* as V1.0; player-code revision |
| V2.0 | c64power.com topic 4120 (beta, ~2002) | abby_/Brush + Longhair | Decoupled data/player, new players 2.0/3.0/4.0, pattern compression, tempo+volume opcodes — NOT in HVSC V1.x |

**Parser implication:** V1.0, V1.0+/[6 speed], and V1.1 all share the V1.0
*song-data encoding*. The only runtime difference is the multispeed dispatch
(CIA rate ≤6×) in the 6-speed/V1.1 player. A single V1.x parser + a multispeed
rate field covers the whole HVSC HardTrack set.
