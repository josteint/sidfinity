---
source_url: https://www.lemon64.com/forum/viewtopic.php?t=55408
fetched_via: direct
fetch_date: 2026-06-15
author: Monk (forum handle), with replies from other Lemon64 users
content_date: ~2013 (thread date approx)
reliability: secondary (user perspective / anecdotal)
---

# Lemon64 Forum: "C64 and Amiga Collaboration Project"

Thread at https://www.lemon64.com/forum/viewtopic.php?t=55408

User "Monk" attempted to synchronize a Commodore 64 running OdinTracker 1.13 with
a Commodore Amiga 1200 running ProTracker 2.3a. The C64/OdinTracker handled melody
and bass; the Amiga/ProTracker handled drums, chords, and rhythm. Thread documents
OdinTracker features/limitations from a practitioner perspective.

## Key quotes (verbatim, from page 1 and page 2 of thread)

### Monk on OdinTracker strengths (post ~685144):
> "it has slidearps, it can be used with the real C64, and it is the most
> user-friendly Tracker after ProTracker"

### Monk on OdinTracker weaknesses (post ~685144):
> "bad drum capabilities" and "only one SID chip" and no sample channels.

### Monk on drum workaround:
> "The point was more like to use Commodore 64 and Odin Tracker...so I could free
> the SID's three channels to do whatever I want instead of having to 'sacrifice'
> one channel for drums (Odin Tracker can't produce good snares)."

### Monk on speed command incompatibility (post ~685139):
> "I just put the 'same speed', a in 'F05' to both machines. Didn't sync AT ALL"

> "Please try it some day...and you will see that 'F05' in Odin Tracker and 'F05'
> in ProTracker are two completely different entities."

### Monk on the missing feature that would make OdinTracker ideal (post ~685144):
> "if there could only be a version that supports four (4) simultaneous SIDs, AND
> that darn 'arpeggio-slide' function...it would be a perfect editor."

### Another user on fine-speed tuning:
> "If OdinTracker also had a 'fine speed tuning', it might be easier."

### Monk on sync approach:
> "The problem is that they quickly fall out of sync, if you don't do special
> speed-changing tricks continuously on both trackers."

Monk resolved this by continuously inserting F-command speed changes in both
tracker patterns — producing an "odd-looking, non-symmetrical pattern" of speed
adjustments that maintained coarse alignment.

## Technical observations from the thread

1. **Speed command semantics**: OdinTracker's Fxx speed command is NOT equivalent
   to ProTracker's Fxx. The underlying tempo calculations differ. The F05 command
   in OdinTracker sets speed to 5 (5 VBI ticks/row), but the PAL VBI vs PAL CIA
   interaction means the actual BPM differs from ProTracker's interpretation.

2. **Slidearps confirmed**: OdinTracker supports "slidearps" — a feature Monk
   explicitly cites as a differentiator from GoatTracker. This matches the source
   code's effect 3 (slide-to-note) combined with arpeggio table support, effectively
   allowing glide+arpeggio in a single instrument program.

3. **Single SID limitation**: OdinTracker supports exactly one SID chip (3 voices).
   No dual-SID or stereo extension. This is confirmed by the source code (no
   provision for a second SID base address).

4. **No sample support**: Confirmed — no digi/PCM channel. Drum sounds must be
   synthesized via waveform programming, which users found inadequate for snares.

5. **User-friendliness**: Monk rates OdinTracker as "most user-friendly tracker
   after ProTracker" — suggesting it was more approachable than GoatTracker,
   JCH Editor, or CyberTracker at the time.

6. **"Arpeggio-slide" gap**: Monk mentions wanting "arpeggio-slide" as a feature.
   GoatTracker has a form of this (arp-slides in its instrument tables). OdinTracker
   has separate effects for slide (effect 3) and arpeggio (effect A / arp table),
   but no combined arp-slide effect (smooth glide between chord tones). This is a
   notable missing feature from the user's perspective.

## Context: Who is Monk?

Antti Mäkynen (Monk) is one of the top OdinTracker composers in HVSC (~14 SIDs).
His perspective here is that of a long-term OdinTracker user. The thread confirms
he used OdinTracker 1.13 specifically.
