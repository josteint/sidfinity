# X-Ample / Compotech — Leads to Follow

**source_url:** synthesis
**fetched_via:** This session (2026-06-13) — forum/wiki cluster research
**fetch_date:** 2026-06-13
**reliability:** synthesis of secondary sources

This document records what was NOT found and what should be looked up in
a future RE/disasm session.

---

## What this session established (new vs prior docs)

Prior session (earlier 2026-06-13) built:
- `sidid_variant_taxonomy.md` — complete fingerprint analysis
- `deepsid_population_and_digi.md` — HVSC population, CIA tunes, Digi scope
- `spec_extraction_plan.md`, `spec_write_model.md` — RE plan
- `csdb_releases.md`, `archive_version_history.md`, `archive_authors_scene.md`
- `github_editor_lineage.md`, `github_parsers_survey.md`
- `csdb_manual.md`

This session (forum/wiki cluster) adds:

1. **forum_csdb_releases.md** — verbatim CSDb user comments (Fred's "player
   100% identical to Compotech V2.1"; Richard's DMC comparison); exact
   credit lines for Compotech V2.1 and Parsec V5.1.

2. **forum_dev_interviews.md** — verbatim interview extracts from Remix64
   (Schneider, Detert) and Atlantis Prophecy (Detert), cross-checked for
   consistency. Confirms: Kozielek + Schneider + Mario van Zeist + Fräder
   built the system. Usenet, forum64.de, Lemon64, Codebase64 searches
   documented (all negative for format RE — expected).

3. **forum_digi_cia_mode.md** — detailed CIA mode analysis from sidid
   fingerprint + general CIA digi background; confirms X-Ample_Digi uses
   CIA#2 ($DD04/$DD05/$DD0E) NMI-based sample playback with variable-rate
   timer reload and 5-bit sample nibbles.

4. **forum_family_relationships.md** — definitive answer on family structure:
   one engine, multiple forks. XTracker by SoNiC (not X-Ample). Quick
   reference table of all variants vs data format status.

5. **forum_wiki_group_history.md** — group members, founding discrepancy
   resolved, Detert and Schneider biographies, key SID context.

6. **forum_xtracker_by_sonic.md** — XTracker V3.1/V4.x authorship
   documented; V3.1 player identical to Compotech V2.1 (Fred's comment);
   V4.1x structural change documented; SoNiC biography.

---

## Key technical statement established this session

From CSDb #17708 (XTracker V3.1) user comment by "Fred", October 2013:
> "The player of this editor is 100% identical to Compotech V2.1"

This is the highest-quality public claim about format identity. It means:
- XTracker V3.1 embeds the Compotech V2.1 player binary unmodified.
- The data format XTracker V3.1 produces must be compatible with
  Compotech V2.1's player — i.e., same format.

Second key discovery:
- **Mario van Zeist** (Hawkeye programmer) made "improvements on the routine
  for less CPU-usage" — he is a fourth contributor to the player, not
  previously documented in sidid.nfo or csdb_releases.md.

---

## Leads to follow

### 1. Data format RE — highest priority

**What:** The X-Ample / Compotech data format (note table, instrument
programs, sequence encoding, orderlist) is NOT documented publicly. No
forum, wiki, or interview source contains this information.

**How to get it:** Disassemble the Compotech V2.1 D64 disk image
(CSDb #122614, 451 downloads). The disk contains:
- The Compotech V2.1 editor binary
- The player (standalone, used by released SIDs)
- Possibly documentation files

Procedure:
1. Download the D64 from CSDb: https://csdb.dk/release/?id=122614
2. Mount with `d64tools` or extract with `cbmconvert`
3. Identify the player binary (look for PRG files matching the sidid
   `(Compotech_V2.x)` fingerprint: `A9 ?? 8D ?? ?? CE ?? ?? 10 ??`)
4. Disassemble with `tools/seed_disassembly.py` (or equivalent)
5. Trace the init and play() routines to map data offsets

Similarly for XTracker V3.1 (CSDb #17708, D64 available):
- If Fred is right that the player is "100% identical to Compotech V2.1",
  the data format is the same — confirmed by loading the XTracker player
  into the same analysis tool.

### 2. Lemon64 — retry when 503 clears

**Threads to fetch when Lemon64 is back:**
- https://www.lemon64.com/forum/viewtopic.php?t=67248
  ("Comparison of C64 Music Editors" — may have Compotech technical details)
- https://www.lemon64.com/forum/viewtopic.php?t=71942
  ("C64 Music tracker software" — may compare editors including Compotech)
- https://www.lemon64.com/forum/viewtopic.php?t=4872
  ("Reflextracker Stuff" — confirmed distinct from X-Ample, but may have
  comparative notes about C64 tracker formats in general)

### 3. forum64.de — retry with authenticated access

forum64.de returns 403 on direct board fetches. A logged-in session or
Google cache might yield:
- Any thread about Compotech (German C64 community; X-Ample was German)
- Any thread about Thomas Detert's player / Markus Schneider's player
- Possible "Musik Editoren" category threads

Suggested queries inside forum64.de search:
- "Compotech" — should find any direct mentions
- "X-Ample Musik" — broader search
- "Markus Schneider Musik" — player discussions

### 4. Does XTracker V4.1x change the data format?

**Question:** The V4.1x player dispatch is structurally different from
Compotech_V2.x. Does it also change what bytes it reads (instrument table
layout, pattern encoding)?

**How to check:** Compare the player binary from XTracker V4.13 (CSDb #82320
D64) against a Compotech V2.1 tune binary:
- Find the data layout in the player binary (IY-indexed table walks, LDA
  from base+N offsets)
- If the offsets match Compotech V2.1 player exactly, format is the same
- If offsets differ, format changed in V4.1x

This is a 1-hour disasm task, not requiring RE from scratch.

### 5. Identify actual X-Ample_Digi tunes in HVSC

**Question:** Are there any X-Ample tunes in HVSC that actually use the
X-Ample_Digi CIA extension?

**How to check:** For each of the 11 CIA-timed SoNiC tunes, and for
Hawkeye_II (RSID, 18,873 bytes), run:
```bash
siddump --writelog hvsc84/MUSICIANS/S/Schneider_Markus/Hawkeye_II.sid 2>&1 | grep -i "DD0"
```
If $DD04/$DD05/$DD0E writes appear, it's X-Ample_Digi. If not, it's just
CIA-timed music (Mode 1, CIA path).

Also: examine file sizes. X-Ample_Digi tunes should contain embedded sample
data → larger file sizes. All 380 X-Ample SIDs < 32KB except Turrican_3
(42KB) and Hawkeye_II (18KB). Hawkeye_II is the primary candidate.

### 6. Clarify "Sonic/SDS" identity

**Question:** What is "SDS" in the sidid variant name `Sonic/SDS`?

**Hypothesis:** SDS = Sonic Design Studio (SoNiC's private label before
APS / The Art Project Studios). This would mean `Sonic/SDS` identifies the
earliest SoNiC player fork, predating XTracker. Investigate:
- Look for releases credited to "SDS" or "Sonic Design Studio" on CSDb
- Check if any SoNiC SIDs from before XTracker V3.1 (pre-April 1996) carry
  the `Sonic/SDS` fingerprint

### 7. Mario van Zeist — Hawkeye SID and player contributions

**Quote (Atlantis Prophecy interview, Thomas Detert, verbatim):**
> "Mario van Zeist (programmer of Hawkeye) did some improvements on the
> routine for less CPU-usage."

**Hawkeye (RSID):** `MUSICIANS/S/Schneider_Markus/Hawkeye_II.sid` is an
RSID by Markus Schneider, 18,873 bytes, play=$0000. This is likely Mario van
Zeist's Hawkeye game music, embedded with Schneider's player AND the Digi
extension (most likely candidate for X-Ample_Digi in HVSC).

**Mario van Zeist** does not appear as a coder credit in sidid.nfo or CSDb
Compotech entries. His contribution was informal (speed optimizations).
Check if he has a CSDb scener entry and any related tool releases.

### 8. Comptech-X (2019) — Geir Tjelta collaboration

**Quote (sidid.nfo):**
> "First used in 2019 by Geir Tjelta and Markus Schneider, probably private
> player for X-Ample members."

This is a MODERN (2019) private player. If Markus Schneider is reachable,
he may be willing to document the original Compotech format. His CSDb profile
shows activity into 2026+ (music credits on CSDb updated to 2025).

**Lead:** Contact Markus Schneider via CSDb (scener ID 6003) to ask about
format documentation or willingness to share source code.

### 9. csdb_manual.md content — verify completeness

`csdb_manual.md` was written in a prior session. Verify that it correctly
captures any documentation found on the Compotech V2.1 disk. If the D64
contains a text documentation file (common for C64 tools), it would be the
best primary source for data format info.

---

## What is NOT on any public forum / wiki / Usenet

After exhaustive searching:
- **No forum post** documents the X-Ample data format (note encoding,
  instrument table layout, sequence format, orderlist structure)
- **No RE notes** exist publicly for the X-Ample / Compotech player
- **No source code** is publicly available for the player or editor
- **No manual** is indexed online (though may be on the D64 disk itself)

The X-Ample / Compotech format documentation will require disassembly.
The sidid_variant_taxonomy.md (prior session) provides the player-level
entry points and dispatch skeleton. The next step is to trace from those
entry points into the data tables.
