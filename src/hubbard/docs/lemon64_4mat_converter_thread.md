---
source_url: "multiple"
  - https://www.lemon64.com/forum/viewtopic.php?t=62157
  - https://www.lemon64.com/forum/viewtopic.php?t=24542
fetched_via: direct
fetch_date: 2026-04-11
author: "4mat (Matt Simmonds) — original poster; thread archived from Lemon64"
content_date: "October 2016 (main thread); September 2007 (related thread t=24542)"
reliability: secondary
---
# Lemon64: 4mat's GoatTracker-to-Hubbard Converter Thread

Source: https://www.lemon64.com/forum/viewtopic.php?t=62157
Date: October 2016

## Summary

4mat (Matt Simmonds, NOT Jason Page) posted a brief announcement of a
GoatTracker-to-Hubbard driver converter. The thread has only 5 posts and
unfortunately contains NO technical details about the data format or
conversion process.

Note: 4mat and Jason Page are two different people. 4mat is Matt Simmonds,
an English demoscene musician. Jason Page (handle "Jay") is a separate British
game composer who worked at Graftgold and later Sony. Both are Hubbard
admirers but are distinct individuals.

4mat's motivation: "I always wanted to try out Rob's driver after hearing the
great Judges and Demon demos in the '80s, but without having to compose
directly in assembly."

He described it as "just a fun project" and chose not to release the converter,
sharing only a YouTube video demonstration.

## What We Can Infer

The fact that 4mat built a working converter means he fully understood:
- The Hubbard driver's data format (patterns, tracks, instruments)
- How to map GoatTracker's data model to Hubbard's
- The specific byte encodings for notes, lengths, effects

However, none of this knowledge was shared in the thread itself.

## Responses

Only brief positive reactions from schumi, Lasse, YogibearRenoise, and
HubbardHero. No technical follow-up questions or answers.

## Related Note from Trackers Thread (t=24542)

nata (Sep 17, 2007) noted key differences between GoatTracker and Hubbard's
driver:
- "In GoatTracker the famous Hubbard slide won't work."
- "No pre programmed special effects are there" (referring to drums, skydive,
  octave arpeggio)
- "Old style songs (without hardrestart) can't be done very well with GT2,
  because first frame is always skipped."

This suggests 4mat had to handle these incompatibilities in his converter.
