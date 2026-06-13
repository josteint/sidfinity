<!--
source_url: http://c64power.com/forumng/index.php?topic=4120.0  (and .15)
fetched_via: WebFetch
fetch_date: 2026-06-13
authors/handles: Abby_ (Krzysztof Dąbrowski), Longhair (Miłosz Ignatowski), Slay_
content_date: 2002 (thread posts dated Aug 2002)
reliability: secondary (developer statements on a public forum; not a primary spec)
-->

# c64power.com — "Hardtrack composer v2.0" thread (topic 4120)

This thread is the single most informative community source on HardTrack
version differences. It documents an in-development **V2.0** of the editor,
posted by one of the original authors (**Abby_ / Krzysztof Dąbrowski**), with
collaboration credited to **Longhair / Miłosz Ignatowski** (the player-routine
author per CSDb). The thread dates to ~August 2002.

> NOTE: V2.0 was a **beta** posted to the scene. The ~1,170 HVSC HardTrack
> tunes are overwhelmingly the shipped **V1.0 / V1.1** players. V2.0's value
> here is that it documents the *player family* and reveals what V1.1 added
> over V1.0 (see below). Treat the "Player 2.0/3.0/4.0" descriptions as
> beta-era and NOT necessarily present in HVSC.

## Player family as described by the author (verbatim summary of claims)

The editor in V2.0 was restructured so the **editor saves only music data
without the player** — i.e. the song data is decoupled from the play routine,
"enabling easy porting between players." Multiple play routines were offered:

- **Player 1.1** — "Original Hardtrack 1.0 format." (i.e. the V1.1 player plays
  the same data format as V1.0.)
- **Player 2.0** — "Version 1.1 plus tempo changes during playback, global
  volume control adjustments."
- **Player 3.0** — "Optimized for demos with shorter raster timing."
- **Player 4.0** — "Ultra-compact code (compatibility unclear)."

All players in V2.0 reportedly feature **"pattern bar compression"** to reduce
file size (a V2-era addition; the V1.x HVSC data is uncompressed pattern/track
streams).

## Multispeed — the load-bearing detail

> "Multispeed Support: Players 2.0 and 3.0 support multispeed via **jump point
> $1006**; editor also supports this."
>
> Known issue reported: "Multispeed jump ($1006) partially non-functional in
> certain players."

**Implication for parsing:** in the V2.0 player family the multispeed entry is a
THIRD JMP vector at **load+$1006**, after init ($1000) and play ($1003). A
multispeed (≤6×) tune calls `$1006` for the extra sub-frames within a video
frame, while `$1003` is the once-per-frame entry. This is consistent with the
documented `init=$1000 / play=$1003` layout — the multispeed sub-call lives at
`$1006`. Worth confirming against the V1.x binary (the sibling asm-decode
agent): whether V1.0/V1.1 also expose `$1006`, or whether multispeed in V1.x is
driven purely by the CIA timer rate with a single `$1003` play that internally
advances N sub-steps.

## Known issues / limitations reported (V2.0 beta)

- Multispeed jump ($1006) partially non-functional in certain players.
- Right-side display frame ("current playback" indicator) didn't work.
- No linker tool — songs were playable only within the editor at that point.
- Feature request: instrument editing while in pattern mode.

## Source / binary distribution (live at the time)

> Beta available at: `http://members.elysium.pl/brush/hardtrack/`
> "Includes snapshot, source code, and binary versions."
> Load sequence: **hardtrack.bin, then player11.obj, start from $9000.**

This corroborates `research.md`'s note that the editor + player asm source were
once hosted at elysium.filety.pl / members.elysium.pl. The `player11.obj`
filename = the **V1.1 player** object, loaded separately from the editor
(`hardtrack.bin`) — direct evidence of the data/player decoupling and that the
V1.1 player is a self-contained relocatable object.

## Verbatim posts captured

### Slay_ — 2002-08-22 00:36 (post #15)
**PL:** "kurcze to jest juz wersja 2.0 lal / 1.0 mi sie podobala / nie znam sie
zbytnio na muzyce, ale swego czasu bawilo sie dziecie ( o sobie mowie )
hardtrackiem / zycze owocnej pracy Panowie Testerzy"

**EN:** "Wow, this is already version 2.0 / I liked 1.0 / I don't know much about
music, but at some point this child (speaking about myself) was having fun with
Hardtrack / I wish you fruitful work, gentlemen Testers."

(Context only — confirms V2.0 was circulated to scene testers; "1.0 I liked"
shows V1.0 was the widely-used release.)

## What this gives the parser

1. **`$1006` is the multispeed sub-call vector** in the V2 family — check
   whether the V1.x HVSC binaries also branch there. (PRIORITY for the
   binary-decode agent.)
2. V1.1 plays the **same data format** as V1.0 ("Player 1.1 = original 1.0
   format") — so a single V1.0/V1.1 parser should cover both; the V1.1 vs V1.0
   difference is in the player code, not the song-data encoding.
3. Tempo-change-during-playback and global-volume control are **V2.0**
   additions — do NOT expect those opcodes in V1.x HVSC data.
4. **Pattern-bar compression is V2-only**; V1.x pattern/track streams are
   uncompressed (matches the byte layout in `research.md`).
