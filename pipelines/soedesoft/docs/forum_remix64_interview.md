---
source_url: https://remix64.com/interviews/interview-michiel-soede-www-soedesoft-com.html
fetched_via: WebFetch
fetch_date: 2026-06-13
author/handle: Michiel Soede (interviewee); Remix64 (interviewer)
content_date: ~2005–2010 (exact interview date not shown on page)
reliability: primary (direct statement from one of the two creators)
---

# Remix64 Interview — Michiel Soede (SoedeSoft)

Full URL: https://remix64.com/interviews/interview-michiel-soede-www-soedesoft-com.html

## Role division between the brothers

> "my brother created the routine, and I created an editor (everything from scratch, nothing was ripped 😉."

Verbatim. **Jeroen Soede wrote the player/driver routine; Michiel Soede wrote the editor.** Both claimed independently developed (not derived from Soundmonitor, Rob Hubbard's code, or other known routines).

## Motivation: why they built their own routine

Michiel examined Chris Hülsbeck's Soundmonitor but found it inadequate:

> "Though I liked the concept of his tool, I thought the creation of sounds was too limited and the size of the music was too much."

Two complaints: (1) insufficient sound design depth; (2) output SID data too large. This implies the Soundmaster format was designed to be compact — important for RE: the music data is probably packed/compressed or uses shorter patterns.

## Rob Hubbard influence

> "copying his famous drum sounds was one of the first things I did."

Also: "[Jeroen Soede] created a driver called Soundmaster to be able to arrange with drums like Rob Hubbard's." (VGMPF Wiki paraphrase of same source.)

RE-NOTE: Hubbard's drums are synthesised (waveform + ADSR + arpeggio combos, no sample playback). Soundmaster likely implements a similar instrument-program-driven drum approach via its arpeggio and waveform effect system.

## Other influences

Ben Daglish and David Whittaker are mentioned alongside Hubbard as inspirations.

## SID chip: what Michiel valued and disliked

Limitations noted:
> "you were limited to using 3 voices, and the limited amount of waveforms it could produce. I also didn't like that you only had one controllable filter."

What he loved:
> "What I loved is all the crazy effects like ring-modulation, synchronisation, which could be triggered by another voice channel."

RE-NOTE: Ring modulation and hard sync are mentioned as valued features. The Soundmaster player likely supports triggering ring-mod/sync from one voice to another; this is a hardware capability (SID CTRL bits $04/$02/$01 per voice) so it would be an instrument or pattern command.

## Amiga successor

> "I also made music on the Amiga, again using our own music routine – called SoundMaster II, which was based on our C64 routine."

The C64 routine was the foundation; SoundMaster II for Amiga is a derived port. C64 Memories Vol. IV (1994) is an Amiga musicdisk by Soedesoft — likely uses SoundMaster II.

## Composition style split

> "My brother mostly focused on melodies (he also is the person who made most of SoedeSoft's musics), while I liked more experimenting with strange sounds."

So Michiel (the editor author) focused on sound design; Jeroen (the driver author) composed most of the actual tunes. The "strange sounds" characterisation aligns with the "Soede Signature" aesthetic mentioned in the SID Preservation article.
