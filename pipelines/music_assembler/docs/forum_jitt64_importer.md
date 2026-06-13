# JITT64 — an existing working Music Assembler / VoiceTracker decoder (GPL Java)

> **source_url:** https://iceteam.itch.io/jitt64 ; https://sourceforge.net/projects/jitt64/ ;
>   https://jitt64.sourceforge.net/ ; code: https://sourceforge.net/p/jitt64/code/ (SVN, trunk @ rev 499+)
> **fetched_via:** WebFetch + WebSearch
> **fetch_date:** 2026-06-13
> **author/handle:** Ice Team (Italy) — also authors of JC64dis disassembler.
> **content_date:** project active 2009–2020+ (JITT64 1.04 = 2020, CSDb #193611).
> **reliability:** secondary, but HIGH value — this is *executable, source-available
>   evidence* that the MA/VoiceTracker packed format has already been fully decoded.

## The lead

**JITT64 (Java Ice Team Tracker 64) can IMPORT Music Assembler, VoiceTracker,
Music Mixer (and ElectroSound, Soundmaster) tunes — directly from PSID files.**
Verbatim from the itch.io feature list:

> "allow to import Music Assembler/Voicetracker tune even from PSID file"
> "allow to import Music Mixer tune even from PSID file"
> "allow to import ElectroSound tune from PSID file"
> "allow to import Soundmaster tune from PSID file"

This means JITT64 contains a complete, working parser that takes a packed
MA/VoiceTracker binary (the exact extraction target) and recovers presets,
sequences, tracks and arpeggios. **It is the single best RE shortcut available:**
porting/translating JITT64's importer is far cheaper than re-deriving the format
from raw bytes.

Notes:
- "Music Assembler/VoiceTracker" are listed as ONE importer → confirms (from the
  Lemon64 quote in `forum_voicetracker_lemon64.md`) that VoiceTracker reuses the
  Music Assembler player/compression. One decoder covers both.
- Import is "even from PSID file" → the importer locates the data region inside a
  relocatable PSID image (not just raw `s.`/`p.` editor files). It must therefore
  do something equivalent to SIDId fingerprinting (find the player) then follow
  the player's pointers to the data — useful because HVSC stores everything as PSID.

## How to get the decoder source

- **License:** GPLv2, Java. Source is in SourceForge **SVN**, not Git:
  - Repo browser: `https://sourceforge.net/p/jitt64/code/HEAD/tree/trunk/`
  - SVN checkout URL (standard SF layout): `https://svn.code.sf.net/p/jitt64/code/trunk/`
  - (No `svn` client + no Bash network egress in this sandbox; check out on a
    networked host, or fetch individual files via the SF "?format=raw" endpoint.)
- Look for the importer classes — by JITT64's naming convention these are likely
  under a `sw_emulator`/`software`/`importer` package. Candidate class-name stems
  to grep once checked out: `MusicAssembler`, `VoiceTracker`, `MusicMixer`,
  `ImportSid`, `Sid` reader, `*Importer`. The PSID-import path + per-format reader
  is what to translate into the SIDfinity extractor.
- Ice Team's JC64dis (Java C64 disassembler, same authors) may also carry
  player-recognition signatures worth cross-checking against SIDId.

## Why this matters for the migration

The CORE TENET is "match the write-log, not the engine code." But JITT64's
importer gives us the *musical content model already lifted out of the packed
stream* (presets/seqs/tracks/arps) — i.e. it's a ready-made `binary → (T,I,S)`
lifter for the extract half of the SID→USF→SID pipeline. The composer half
(producing the per-frame $D400-$D418 writes) still has to be built and verified
against `siddump --writelog`, but JITT64 removes the hardest unknown: parsing
"intricate, unreadable data which is disassembled by the player while playing."
