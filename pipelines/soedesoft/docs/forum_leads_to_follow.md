---
source_url: (internal — synthesised from this research session)
fetched_via: N/A
fetch_date: 2026-06-13
author/handle: SIDfinity research agent
content_date: 2026-06-13
reliability: N/A — open questions, not findings
---

# Forum Research Session 2026-06-13 — Leads to Follow

## Leads to follow

### High priority (RE-critical)

1. **Soundmaster V3.1 official Docs.prg** — `Soundmaster_V3_1_Docs.prg` (136 downloads, CSDb #90307) is the original SoedeSoft documentation program. Fetch via `csdb.dk/getinternalfile.php/<id>/Soundmaster_V3_1_Docs.prg` and run in VICE or extract the text. This is likely the closest thing to a formal reference for the note/pattern/instrument format. The German PDF manual ("Walter") is user-written secondary documentation; the Docs.prg is the official source.

2. **Soundmaster V3.1 .prg binary** — `soundmaster3.1.prg` (384 downloads, CSDb #90307) is the actual editor executable. Disassembling it would give the definitive note/instrument/pattern byte layout. This is the RE path but outside scope of the current forum-only session.

3. **S.F.X. Editor (1989, Soedesoft)** — Demozoo lists this as a separate Soedesoft tool. Look up its CSDb entry to determine if it is: (a) a separate sound-effects editor, (b) an alias for Soundmaster at a certain stage, or (c) a companion tool used alongside Soundmaster for game SFX. If it has its own player, it may be a distinct engine variant within the ~929-tune HVSC family.

4. **"Soede Editor" and "Soede Editor TURBO GTI SSS"** — mentioned in sidid.nfo as variants; no CSDb IDs found in this session. Search CSDb for "Soede Editor" directly. The TURBO GTI SSS variant may use a modified player that differs from the standard Soundmaster signatures — affecting which HVSC tunes are identified as which player version.

5. **SoedeSound Editor V1.1 (1992)** — listed in Michiel Soede's CSDb profile (#6063) but no release page found. Determine if this has a distinct CSDb entry (search CSDb for "SoedeSound Editor V1.1"). If it shipped a modified player routine, sidid may have a separate signature for it not found in this session.

6. **Version V2.x gap** — no V2.x entries exist in CSDb. Either V2.x was purely internal (never leaked), or the numbering skips (V1.0 public → V3.x internal with no intermediate public release). Ask on CSDb forums or contact Fred (CSDb scener #6746) who uploaded the V3.1 and V3.2 docs and appears to be the primary preservationist for this engine family.

### Medium priority (context / format details)

7. **Soundmaster V3.1 German PDF** (`Soundmaster_v3.1_[german].pdf`, 166 downloads) — downloaded during this session but was binary/corrupted in the WebFetch response. Try opening with a proper PDF reader or OCR tool. If text-extractable, it provides user-perspective documentation of the editor UI and format, written by a German user ("Walter") circa 1989–1990. May describe the note entry format (hex values, byte layout) in accessible terms.

8. **forum64.de** — the German C64 community forum. Magic Disk 64 distribution of Soundmaster V3.1 means German-language discussion is the most likely source of user-level format documentation. Search forum64.de directly for "Soundmaster" and "Soede". The forum was not directly accessible in this session.

9. **DRAX's lost Soundmaster tunes** — DRAX (Jesper Olsen) mentioned in CSDb comment (Sep 2010) that he made tunes in Soundmaster V3.1 and may have sent them to "nato or noise members". If these tunes are in HVSC under a SoedeSoft-identified player, they would be useful test cases (DRAX's tunes are extensively documented on CSDb).

10. **Xiny6581 (Cris Ekstrand) contact** — the SID Preservation article author used Soundmaster V3.1 around 1989–1990 and explicitly notes incomplete memory. Contacting him directly (via SID Preservation site or demoscene contact) could fill in the forgotten details: the "cycle time" field meaning, the filter trigger byte encoding, and whether "sustain (++)" means ADSR sustain or a note-hold effect.

### Lower priority (broader context)

11. **Nagie Sascha (157 tunes)** — the largest single Soundmaster user in HVSC. CSDb profile may have scene contact info or release notes. His tunes span the full version range and would be useful for detecting per-version differences in the player binary (different HVSC tunes may use different Soundmaster versions based on date of composition).

12. **Magic Disk 64 archive** — the issue that carried Soundmaster V3.1 is likely archived on archive.org or Gamebase64. Finding the specific issue would give the original disk image and any accompanying text description of the tool (Magic Disk 64 typically included short descriptions of tools it distributed).

13. **Reason Talk forum thread** on SIDmaster (https://forum.reasontalk.com/viewtopic.php?t=7514852) — returned HTTP 403 in this session. A retry may reveal Michiel Soede describing technical details of the original C64 routine while explaining what the plugin implements.

14. **Demozoo music editor tag** — search https://demozoo.org/productions/tagged/music-editor/ for Soundmaster. The current tag list did not include it, but tagging may be incomplete for 1989-era tools.

15. **"Final Music Collection" (1991)** — Demozoo credits Jeroen Soede with "Music Routine development" for this release. If this collection ships the Soundmaster player or a derivative, it may be an alternative source for the player binary.
