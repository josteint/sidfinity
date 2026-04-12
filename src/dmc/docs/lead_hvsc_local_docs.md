---
source_url: /home/jtr/sidfinity/data/C64Music/DOCUMENTS/STIL.txt, /home/jtr/sidfinity/data/C64Music/DOCUMENTS/HVSC.faq, /home/jtr/sidfinity/data/C64Music/DOCUMENTS/Update37.hvs, /home/jtr/sidfinity/data/C64Music/DOCUMENTS/Update36.hvs
fetched_via: local read
fetch_date: 2026-04-11
author: HVSC Team (STIL annotations by PVCF, Richard Bayliss, and other musicians)
content_date: unknown (STIL comments span 1990s–2020s; update files circa 2010s)
reliability: secondary
---
# HVSC Local Collection — DMC Document Search Results

Searched: `/home/jtr/sidfinity/data/C64Music/DOCUMENTS/` and `/home/jtr/sidfinity/data/C64Music/MUSICIANS/`

## Summary

No standalone DMC technical documentation found. The HVSC collection contains no dedicated DMC spec, README, or format document. All DMC references are incidental — appearing in STIL.txt musician comments, update changelogs, and title metadata. The most technically useful content is in STIL.txt comments from prolific DMC users (especially PVCF and Richard Bayliss).

---

## 1. `/home/jtr/sidfinity/data/C64Music/DOCUMENTS/` — Contents

Key files checked:
- `STIL.txt` — 66 lines match "DMC" (see below)
- `HVSC.faq` — 1 mention: DMC listed as a recommended C64 music editor
- `Musicians.txt` — 2 matches: "Danish Music Company (DMC)" and "Run DMC featuring Aerosmith" — neither relevant
- `BUGlist.txt` — 0 DMC mentions
- `Songlengths.faq` — 0 DMC mentions
- `SID_file_format.txt` — 0 DMC mentions
- `HVSC.txt` — 0 DMC mentions
- `Creators.txt` — 0 DMC mentions
- `hv_sids.txt` — 0 DMC mentions
- `Update*.hvs` — References to DMC in filenames and brief editorial notes, no technical specs

### HVSC.faq mention (line 511)
> "...recommended JCH's Editor, Music Assembler, **DMC Editor**, Future Composer, Voicetracker, SID DUZZ'IT, Soundmonitor..."

Confirms DMC Editor is a recognised C64 music editor, listed alongside JCH Editor, Future Composer, and Soundmonitor.

### Update file technical notes

- **Update37.hvs, line 329:** `# from Steppe: DMC4 loopcode at $0FF9 restored, shortened by ~650 bytes, credits fixed.`
  - File: `/VARIOUS/A-F/AEG/Triage_3_tune_2.sid` — implies DMC4 player has a loop continuation routine at address `$0FF9`

- **Update36.hvs, line 919:** `# from Stryyker: the original file from the DMC5 packer`
  - File: `/VARIOUS/S-Z/Stryyker/Last_Ninja_2_Level_1.sid` — confirms DMC5 uses a packer format distinct from raw player data

---

## 2. `STIL.txt` — DMC Technical Content

### Version history implied by comments

From musician annotations in STIL.txt, the following DMC versions are confirmed to exist:

| Version | Evidence |
|---------|----------|
| DMC2 / DMC2.x | PVCF: "Yeah, my first DMC2 song with digis... composed with two different routines, DMC2.x and Polonus' DigiTracker" |
| DMC3 / DMC3.x | PVCF: "DMC3 with 5 times multispeed routine" / "made in DMC3.x" / "hard sounds on DMC3" |
| DMC4 / DMC4.x / DMC4.0 | Multiple composers: "written in DMC V4.0", "DMC4 loopcode at $0FF9", "DMC4 doesn't exists a filtercommand in pattern" |
| DMC V5.0+ / DMC5 | Richard Bayliss: "rewritten instruments in DMC V5.0+" / Deetsay: "three original randomly named DMC5 tunes" |
| DMC V6 | `/MUSICIANS/T/The_Syndrom/DMC_V6_note.sid` |
| DMC V7.0 | Richard Bayliss: "done using DMC V7.0 by Unreal" |
| DMC 7 | NecroPolo: "Vincenzo's C64GT Challenge tune for June with DMC7" |

### Key technical observations from STIL comments

**DMC is a "duration editor" (not a tracker)**
- PVCF: "very hard to compose this with a durationeditor (DMC4.x)" — confirms DMC uses duration/length columns, not tracker rows
- PVCF: "in DMC or GMC2 duration editor"

**GMC is a predecessor to DMC**
- PVCF: "Made in GMC, the predecessor of the great DMC"
- Paco: "All SIDs were composed in Brian's GMC 1.0 (not DMC)"
- NecroPolo references using GMC 1.6 before switching to DMC

**DMC4 — filter limitation**
- PVCF (`Megasweet_6581.sid`): "in DMC4 doesn't exists a filtercommand in pattern, so I must use different filtered basses and endless glide-effects in bassline"
- This is a key architectural fact: DMC4 has no per-pattern filter command; filter changes must be baked into instrument definitions

**DMC3 — multispeed support**
- PVCF: "DMC3 with 5 times multispeed routine. Too much bass... The song is very stylish."
- PVCF: "DMC and somekind of doublespeed tune IIRC. I think only the third voice is doublespeeded."

**DMC4 — frequency table is customisable**
- PVCF: "Brian/Graffity, who didn't implement the right frequency table in his DMCs. From DMC4 I used a own table, which KB/TOM/farbrausch has edited."
- Implies the frequency table in DMC4 is user-replaceable or editable within the editor

**DMC5 packer**
- Update36.hvs: "the original file from the DMC5 packer" — DMC5 uses a distinct packed binary format

**DMC4 loop code address**
- Update37.hvs: "DMC4 loopcode at $0FF9" — the loop continuation routine is at `$0FF9` in the player

**DMC V7.0 credited to "Unreal"**
- Richard Bayliss: "using DMC V7.0 by Unreal" — DMC V7 was authored/maintained by someone with the handle "Unreal"

**DMC crash (stability)**
- PVCF (`Megasweet_6581.sid`): "the C64 was freezed (a DMC-crash which occured about once per year)"

**DMC4 multispeed + filter trick (PVCF, complex song)**
- "4speed wave and 2speed filter" — DMC4 tunes can use tricks to get higher multispeed on some voices independently

**DMC used with DigiTracker**
- PVCF: multiple songs composed in DMC then loaded into "Polonus' DigiTracker" to add digi samples — DMC player and DigiTracker are separate tools that could interoperate at the SID level

---

## 3. `/home/jtr/sidfinity/data/C64Music/MUSICIANS/` — README search

No README files exist in the MUSICIANS tree. Subdirectories are only organized alphabetically (A-Z, 0-9). No DMC-specific subdirectory exists.

Relevant musician directories containing DMC-named SIDs:
- `/MUSICIANS/B/Bayliss_Richard/` — DMC_V4_0_Collection_note.sid, Hardcore_DMC.sid, I_Love_DMC.sid, etc.
- `/MUSICIANS/B/Blues_Muz/Gallefoss_Glenn/` — DMC_Demo_remake.sid, DMC_Remix.sid
- `/MUSICIANS/F/Fulcrum/` — Tune_4_DMC_4_0.sid
- `/MUSICIANS/N/Nilsen_Ronny/` — Last_Song_In_DMC-Player.sid
- `/MUSICIANS/S/Stryyker/` — DMC_Tune.sid
- `/MUSICIANS/T/The_Syndrom/` — DMC_V6_note.sid

---

## 4. STIL.txt — DMC Technical Annotations

### File: `/MUSICIANS/T/The_Syndrom/DMC_V6_note.sid`
COMMENT: "The tune was not made by me. I just added finishing touches to a worktune provided by another musician - who preferred to stay anonymous this time." (The Syndrom)
— No technical content, just credits.

### File: `/MUSICIANS/N/Nilsen_Ronny/Last_Song_In_DMC-Player.sid`
— Title itself is significant: a song specifically named as the "last song in DMC-Player", suggesting the DMC player binary is bundled with the SID.

---

## 5. Conclusions and Leads

### What the local HVSC collection does NOT contain
- No DMC format specification document
- No DMC source code or disassembly
- No technical README for any DMC version
- No STIL annotation with byte-level or register-level technical detail

### What it DOES confirm
1. DMC versions confirmed in use: 2, 2.x, 3, 3.x, 4, 4.0, 4.x, 5, 5.0+, 6, 7, 7.0
2. GMC is DMC's predecessor (Brian's GMC 1.0 / GMC 1.6)
3. DMC7 was authored by someone with handle "Unreal"
4. DMC4 has no per-pattern filter command
5. DMC4 loop code lives at `$0FF9`
6. DMC5 uses a distinct packer format
7. DMC frequency table is customisable in DMC4+
8. DMC is a "duration editor" architecture, not a tracker

### Best local SIDs to disassemble for DMC player code
- `/MUSICIANS/T/The_Syndrom/DMC_V6_note.sid` — specifically titled as a DMC V6 note/demo
- `/MUSICIANS/N/Nilsen_Ronny/Last_Song_In_DMC-Player.sid` — player bundled in SID
- `/VARIOUS/A-F/AEG/Triage_3_tune_2.sid` — DMC4 with loopcode at $0FF9 (repaired)
- `/VARIOUS/S-Z/Stryyker/Last_Ninja_2_Level_1.sid` — from DMC5 packer (repaired)
- Any SID in `/MUSICIANS/B/Bayliss_Richard/` tagged with specific DMC versions
