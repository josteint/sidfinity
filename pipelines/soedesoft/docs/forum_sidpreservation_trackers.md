---
source_url: https://sidpreservation.6581.org/sid-trackers/
fetched_via: WebFetch
fetch_date: 2026-06-13
author/handle: Cris "Xiny6581" Ekstrand (SID Preservation)
content_date: ~2015–2020 (page footer: "All rights reserved © 2026 Cris Xiny6581 Ekstrand SID Preservation")
reliability: secondary — third-party, author used Soundmaster V3.1 circa 1989–1990 but writes from memory, explicitly notes incomplete recall
---

# SID Preservation — "SID Trackers" Article (Xiny6581)

Full URL: https://sidpreservation.6581.org/sid-trackers/

## Soundmaster V3.1 as "one of the first trackers on the market"

Verbatim:

> "One of the first trackers on the market was 'Soundmaster V3.1' from SoedeSoft. This was used not only by SoedeSoft and FireEagle, once it was released. The base sounds and sound design was unique for this Tracker and to begin with it kind of set the 'Soede Signature'. This tracker did not use the typical C-1 notes, as discussed in the Editor part. This was far different and used hexadecimal values that corresponded to notes."

RE-NOTE: Xiny6581 classifies Soundmaster as a **Tracker** (step sequencer / pattern view) rather than an **Editor** (command/duration based). The SID Preservation site distinguishes Editors from Trackers explicitly: Trackers use a pattern grid where "separators" (blank rows) define timing; Editors use duration commands (.DUR). Soundmaster V3.1's hex note values and row-based grid structure are what define it as a tracker.

## Note/pattern byte format (from memory, circa 1989–1990)

Verbatim — author's disclaimer included:

> "Quick follow-off. The bone structure if I remember correctly (last time used this Tracker was around 1989 or early 1990).
> The first two bytes: Octave and Note
> The second two bytes: bit and sound number. The bit $80 was for portamento and you could press the commodore key to assign up/down
> The third bytes to access sustain (++)
> The fourth bytes had something to do with cycle time and filter triggers. Sorry I can't remember it all 🙂
> Anyhow, this note style was kind of simple to use and I was able to clove up some tunes."

RE-NOTES from this fragment:

1. **Note entry format is ~4 bytes per step** (possibly more). Byte layout:
   - Byte 0: Octave
   - Byte 1: Note (in hex, not C-1 notation — likely 0–11 or 0–C semitone index within octave)
   - Byte 2: flags + sound number. Bit $80 = portamento flag. Likely bits 0–6 = sound/instrument index.
   - Byte 3: sustain access (++)
   - Byte 4 (or byte 3 high nibble?): cycle time and filter trigger

2. **Portamento direction:** set by Commodore key (↑/↓) — keyboard-controlled direction during note entry, stored as a flag in the byte 2 bit field (up/down portamento, presumably bit $40 or a separate bit).

3. **"Cycle time":** unclear — could mean the note duration (row timing), or an effect speed parameter. In the tracker model, "cycle time" might be pattern speed (rows per frame). OPEN.

4. **"Filter triggers":** confirms filter modulation is per-note in the pattern, not just an instrument-level setting.

5. **Hex note input:** composer types hex values (e.g., $3C for note C in octave 3?) rather than alphanumeric C-1 style.

6. **Sound/instrument numbering:** referenced as "sound number" — suggests instruments are called "sounds" in the editor UI.

## Soundmaster as tracker vs. editor distinction

The article context (immediately precedes this section):

> "Trackers was a complement to all the Editors. This was because some musicians did not want to work with duration and use command to compose music. Sometimes you are more visual and want to 'see' what you're doing..."

And:

> "Technically speaking a Tracker is working the same way as an Editor, since they both use a Music Routine and Player."

So the Soundmaster *editor front-end* is a tracker-style UI, but the underlying *player* is the same kind of SID music routine. The terms "editor" and "tracker" in the C64 scene distinguished UI paradigm, not player architecture.

## Successor: "Soede Editor"

Verbatim:

> "The next step and successor to 'Sound Master', was 'Soede Editor'. The GUI was bigger and it added more possibilities to the Bar Editor, as well for the Sound Design. I didn't spend too much time with this Tracker, but the foundation was the same as for all Soede's Editors."

And:

> "Even if the Bar Editor looks smaller it had some additional workflow, if not mistaken it was possible to define Bars to be longer and not locked to 4/4 per Bar."

RE-NOTE: "Bar Editor" is the name of Soundmaster's pattern arrangement section. Soundmaster V3.1 bars were locked to 4/4 (fixed pattern length). The successor "Soede Editor" (referred to in the sidid.nfo section header as related to the V3.1 family but not given a CSDb ID in research) removed this restriction. "Foundation was the same" = same player routine underneath.

The sidid.nfo entry also mentions "Soede Editor TURBO GTI SSS" as a named variant — consistent with "many big groups wanted to make their own special versions and it was very often done by 'hacking' or 'improve' the official versions" (Xiny6581, same article).

Verbatim on hacked variants:

> "Many big groups wanted to make their own special versions and it was very often done by 'hacking' or 'improve' the official versions."

## Broader tracker context

Xiny6581 places Soundmaster V3.1 as the earliest entry in the C64 tracker chronology, followed by Laxity Editor → JCH Editor → SDI → XSID → SID-Wizard. Soundmaster's position as "one of the first trackers on the market" (1989) is consistent with the CSDb dates.
