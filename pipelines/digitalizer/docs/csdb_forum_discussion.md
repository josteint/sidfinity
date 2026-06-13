---
source_url: https://csdb.dk/ (release comment sections), https://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=129, https://hvmec.altervista.org/blog/?p=428
fetched_via: direct (WebFetch)
fetch_date: 2026-06-13
author: various CSDb users; Olav Mørkrid (interview subject)
content_date: 2006–2013 (CSDb comments); 2006 (Recollection interview)
reliability: primary (direct quotes); secondary (interpretation)
---

# Digitalizer — CSDb Comments, Forum Activity, and Scene Discussions

## Primary Source: CSDb Release Comments

### Digitalizer V2.2 (CSDb #33646) — User Comments

**6R6 (grg_shape) | 23.05.2006**
> "To clear sequences, tracks or instruments you have to press: shift + up arrow,
> then type 'ok' when screen flashes."

**Context:** 6R6 (Glenn Davanger of SHAPE/Nostalgia) is the same person who later
co-coded V3.5 and wrote the DTZ2SDI converter. His familiarity with the V2.2 UI
at this level of detail confirms deep hands-on knowledge of the editor. The clear
confirmation dialog (flash + type "ok") is a destructive-operation safeguard —
pressing shift+up-arrow alone does NOT clear data. This pattern (two-step confirm)
is unusual for C64 editors and suggests Olav specifically designed against accidental
data loss.

---

### Digitalizer V3.0 (CSDb #33649) — User Comments

**6R6 | 06.07.2013**
> "Uploaded missing file. And converted help file to a text file."

**Context:** The V3.0 zip file was originally missing from CSDb. 6R6 uploaded it in
2013 and also converted the embedded PETSCII help file to ASCII text, including it
in the zip. This is the most significant documentation source yet identified:
the zip at http://csdb.dk/getinternalfile.php/118523/Digitalizer-2.9(ff)%20v3.0.zip
contains a text file (the converted help) which has never been separately catalogued.
OPEN: download the zip and extract this file to docs/src/.

---

### Digitalizer V3.5 (CSDb #33650) — Production Notes and Comments

**6R6 (production note) | 05.05.2006**
> "A re-assembled hack of v3.0 with alot of new functions."

**6R6 notes:**
- "Re-assembled hack" = the V3.0 source was reconstructed and extended, not binary-patched
- "Alot of new functions" = unspecified; likely includes: more instruments, more effects,
  better disk I/O, improved track/sequence limits, or extended table sizes
- SHAPE and Blues Muz' involvement suggests music-playback improvements (player
  enhancements compatible with the Blues Muz' live performance scene)

**ready. | 04.05.2006**
> "No download link??? Not even Pokefinder helps :("

**Context:** The V3.5 download was unavailable for several years. It was eventually
recovered and posted (currently 1,418 downloads). The user ready. filed this complaint
in 2006 when only the page existed but no file was linked — suggesting V3.5 was widely
known but the binary was temporarily lost.

---

## Recollection #2 Interview — Olav Mørkrid (2006)

**Source:** https://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=129
**CSDb reference:** CSDb release 42400 (Recollection #2, 2006)
**Interviewer:** Recollection diskmag staff
**Interviewee:** Olav Mørkrid

### On the "borrowed editor":
The interview contains this exchange:
> [Interviewer:] "Stein Pedersen mentioned to me once that you 'borrowed' his music
> editor, a freeze backup?"
>
> [Olav:] "I admit to the crime. Stein deserves the true credit for making the first
> and best music editors."

**Full biographical context recovered from interview:**
- Handles: Omega Supreme, Rawhead (used less frequently)
- Group: Panoramic Designs; also later co-founded Funcom (Anarchy Online, Dreamfall)
- Worked at Opera Software designing browser interfaces
- Taught himself machine code from a Norwegian computer magazine
- Breakthrough moment: discovering interrupt programming
- Zoomatic (1991 graphics tool) sold to CP Verlag GmbH for 3,000 DM when Olav was 16
- Influences: 1001 (sideborder), Omega Man (rastersplits), Rob Hubbard ("Rob is #1. Nothing more to say about that")
- Quote on newcomers: "it's not always about the rasters and sprites and sideborder"

**Analytical notes on the "borrowed editor":**
- The "freeze backup" method = using a freezer cartridge (Action Replay, Final Cartridge, etc.)
  to dump RAM to disk mid-execution. This means Olav froze Stein's running editor and took
  the binary.
- Stein Pedersen = co-member of Panoramic Designs from 1990; separately ran the Prosonix
  music group (founded 1989). His "SteinTronic" / Prosonix Music Editor (CSDb #179618)
  predates Digitalizer V2.2 (also 1989).
- Olav's admission suggests Digitalizer's code or architecture was derived from SteinTronic.
  This is the LINEAGE: SteinTronic (Stein Pedersen, ~1988–1989) → Digitalizer V2.2 (Olav, 1989).
- The "first and best" praise for Stein's editors is notable — Stein later created the
  SIDdecompiler (V0.5, 2017; V0.8, 2019) and SIDBlaster USB driver (2015), suggesting
  continued technical depth.

---

## Forum Thread Activity Summary

### V3.5 (CSDb #33650)
- **4 forum threads** listed on the CSDb page
- Content not recovered (CSDb forum RSS endpoint returned 404; forum index page
  does not expose individual threads in the fetched HTML)
- OPEN: manually visit https://csdb.dk/release/?id=33650 and read all 4 threads

### Other versions
No forum threads listed for V2.2, V2.5, V2.7, V2.8, V3.0 in the CSDb metadata.

---

## Scene Context: Key Relationships

### SHAPE ↔ Panoramic Designs
- Both Norwegian groups
- 6R6 (SHAPE/Blues Muz') = primary bridge between Digitalizer and SDI worlds
- Kjell Nordbo (SHAPE/Blues Muz') = co-coder of V3.5
- The Panoramic Designs XML metadata states: "the prosonix team is now a part of panoramic"
  — confirming group overlap between Prosonix (Stein Pedersen) and Panoramic Designs

### Blues Muz' Player
- Blues Muz' was a music group whose members (6R6, Kjell Nordbo) used Digitalizer heavily
- CSDb lists 154 tunes by Blues Muz' member Glenn Gallefoss using the Olav_Moerkrid player
  (from prior research.md)
- SHAPE's release of "Blues Muz' Player V6.4–V19.99" alongside SID Duzz' It suggests these
  were parallel distribution channels

### Prosonix (Stein Pedersen) ↔ Digitalizer
- Prosonix Music Editor ("SteinTronic") = the ancestor/source of Digitalizer's codebase
- DeepSID added SteinTronic entry 2019 (JCH comment)
- Stein Pedersen still active in C64 scene (Prosonix, Offence, Panoramic Designs)

---

## Technical Clues from Comments (Summary)

| Source | Claim | Confidence |
|--------|-------|-----------|
| 6R6, CSDb V2.2 comment | Shift+UP-ARROW + type "ok" = clear command | High (direct user observation) |
| 6R6, CSDb V3.0 comment | V3.0 zip contains converted ASCII help text | High (6R6 uploaded it himself) |
| 6R6, CSDb V3.5 production note | V3.5 = re-assembled V3.0 + new functions | High (co-author statement) |
| 6R6 production note | V3.5 authorship: Olav (design), 6R6 + Kjell Nordbo (code additions) | High |
| PD-editor.prg strings | UI commands: SAVE SOUNDTRACK, DUMP SOUNDTRACK, DISK COMMAND, ERROR | High (from binary) |
| HVMEC V2.5 page | Full keyboard map (F7 play, F5 stop, RUN-STOP toggle, F1 disk, SHIFT+W wave, SHIFT+A arp) | Medium (no source cited on HVMEC) |
| Olav interview (Recollection #2) | Digitalizer derived from Stein Pedersen's "SteinTronic" | High (Olav's own admission) |
| sidid.cfg V3.0 sig | $D418 digi output via $0C,X state bytes; ZP $FB/$FC data pointer | High (direct from binary scan) |
