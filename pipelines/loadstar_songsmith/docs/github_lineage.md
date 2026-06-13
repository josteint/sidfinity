---
source_url: multiple (see per-claim citations)
fetched_via: WebSearch + WebFetch
fetch_date: 2026-06-14
author: research session (Claude Code)
content_date: 2026-06-14
reliability: secondary (synthesised from multiple primary sources; binary RE still needed)
---

# Loadstar SongSmith — Lineage and Engine Family Analysis

## Core Conclusion

**Loadstar SongSmith is NOT a Sidplayer/.MUS-family tool.**
It is Loadstar/Softdisk's own proprietary C64 music composition and playback engine.
The four variants (v1, v2, v3, unversioned) share no byte signatures with
COMPUTE!'s Sidplayer, and sidid treats them as entirely separate engine families.

Evidence:
1. sidid.nfo (cadaver/sidid) has a **separate entry block** for `Loadstar_SongSmith`
   and for `Sidplayer` — the two are never aliased or cross-referenced.
2. The SongSmith byte signatures (all four variants) show a custom note-index-to-
   frequency lookup + direct SID register write architecture that does not match
   the Sidplayer dispatch model (which uses 2-byte command/option pairs with
   packed bit fields — a completely different data format).
3. The Sidplayer player routine is an IRQ handler installed at $0314 playing .MUS
   stream files with a rich command set. SongSmith's signatures show a simpler
   direct note→freq-table→SID-register loop with no evidence of the MUS multi-
   command dispatch tree.
4. No web source, forum post, or technical document links SongSmith to Sidplayer
   compatibility.

---

## SongSmith Identity

### What it is
- A music composition tool (editor + player) distributed as part of **Loadstar**,
  Softdisk Publishing's monthly C64 disk magazine (1984–2007).
- Purpose: "transcribe music from sheet music or make up your own tunes."
- Shipped with: a 30-page manual + a jukebox player with eight demo tunes.
  Source: Loadstar Complete promotional description (comp.sys.cbm / itch.io sources).
- Targeted at hobbyist/non-scene composers; not the demoscene.

### Author
- **Unknown** in all available public records. The CSDb release id=122855 lists no
  creator. sidid.nfo lists no author for the Loadstar_SongSmith entry.
- The Loadstar Complete collection was managed by Fender Tucker (Softdisk).

### Precursor tool
- An earlier songmaker used in Loadstar's early days was written by **Joe Garrett
  and Alan Gardner**. This is explicitly described as "the precursor to SongSmith"
  in a letter published in Loadstar #168 (comp.sys.cbm post, verbatim quote):
  > "Jim W. said that the songmaker they used in those days was written by
  > Joe Garrett and Alan Gardner, and was the precursor to SongSmith."
- The same post notes that reverse-engineering the "old song codes" from issues
  27-28 (presumably using the Garrett/Gardner tool) was considered but lacked
  interest.
- OPEN: The `Song_Writer` engine tag in sidid/HVSC (6 SIDs, all by Jeremy Thorne:
  `MUSICIANS/T/Thorne_Jeremy/Song_Writer-*.sid`) may be this earlier precursor
  tool or a closely related variant. The name "Song Writer" matches the concept.
  RE needed to determine if Song_Writer and Loadstar_SongSmith_v1 share code.
  Source: hvsc84.db query + comp.sys.cbm Loadstar #168 thread.

### CSDb release
- **URL:** https://csdb.dk/release/?id=122855 (C64 Tool)
- **Download:** `http://csdb.dk/getinternalfile.php/121491/Songsmith-Loadstar.d64`
  (a 1541 D64 disk image, 141 downloads as of research date)
- **Associated SIDs** (by Cruz, Debby, the reference composer):
  Alouette, Funiculi Funicula, Meadowlands, Muss I Denn,
  Scarborough Fair, Skye Boat Song, The Parting Glass.

---

## HVSC Corpus

337 SIDs in hvsc84 use a SongSmith engine tag:

| Engine Tag | Count |
|---|---|
| Loadstar_SongSmith | 308 |
| Loadstar_SongSmith_v1 | 19 |
| Loadstar_SongSmith_v3 | 3 |
| Loadstar_SongSmith_v2 | 1 |
| Song_Writer | 6 |

**Composer base:** 15 distinct HVSC directory groups. Heaviest: Mario Oropesa
(MUSICIANS/O — Cuban classical transcriptions) and Cruz, Debby (MUSICIANS/C).
Also appears in DEMOS/ and GAMES/ directories, indicating the tool was used for
game and demo soundtracks, not only standalone music.

**Key observation:** The dominant tag is unversioned `Loadstar_SongSmith` (308/331 =
93%). This means most of the corpus uses the variant with the `EE/AC` (INC abs /
LDY abs) data-read architecture from the sidid signatures. The v2 / v3 tagged
files (4 total) are rare edge cases.

---

## Relationship to Other C64 Music Tools

### COMPUTE!'s Sidplayer (Craig Chamberlain, 1985/1986)
- **NOT related to SongSmith** (see Core Conclusion above).
- Completely separate engine, separate format (.MUS files), separate player (SID.OBJ.64).
- 16,601 .MUS files in the CGSC collection vs. 337 SongSmith SIDs in HVSC.
- Sidplayer was heavily US-focused (distributed via Quantum Link BBS, COMPUTE!'s
  Gazette magazine). Also US-focused but an entirely different product from
  a different publisher (Softdisk vs. COMPUTE! Publications).
- Source: https://github.com/MyDeveloperThoughts/ComputeSidPlayerC64Source;
  https://sidplayer.org/; sidid.nfo separate entry blocks.

### Master Composer (Paul Kleimeyer / Access Software Inc., 1983)
- sidid.nfo entry: separate entry, no relationship to SongSmith.
- Earlier (1983) US-market C64 music editor; different engine entirely.
- Source: sidid.nfo, CSDb release id=128699.

### SIDFactory II, GoatTracker, CheeseCutter, SID-Wizard
- None of these import or reference SongSmith. All post-date SongSmith by many years
  and target the demoscene, not Softdisk's hobbyist user base.

### Music Construction Set (Electronic Arts, 1984)
- No evidence of relationship. Different publisher, different era, different architecture.

### Song_Writer (Jeremy Thorne, HVSC tag)
- 6 SIDs tagged in HVSC under `MUSICIANS/T/Thorne_Jeremy/`.
- Possibly the Garrett/Gardner precursor tool, possibly a separate variant.
- OPEN: sidid signature for Song_Writer not retrieved in this session; should be
  fetched from sidid.cfg to compare with SongSmith_v1 architecture.

---

## Engine Architecture (from sidid Signatures — RE not done)

The four signature variants reveal the following about the player architecture:

### v1 (19 SIDs, fixed ZP $F9/$FA)
- Simple indirect-Y read loop: `LDA ($F9),Y` / `INC $F9` / `INC $FA`.
- Dual range compare: `CMP #$19` / `BCC` / `CMP #$1D` / `BCC` — likely a
  note-range validation (values 25-28 have special meaning?).
- No freq table reference in signature. Possibly maps note numbers to SID freqs
  differently (inline table, or offset-based).
- Fixed ZP ($F9/$FA), so not relocated. Very early architecture.

### v2 (1 SID, fixed at $C290)
- `SEC / SBC #$01 / ASL A / TAY` — note-to-word-table-index: `(note-1)*2 = Y`.
- `LDA $C290,Y` + `STA $D400` / `LDA $C290+1,Y` + `STA $D401` — freq-lo/hi
  from freq table at FIXED address $C290 → SID V1 freq registers.
- 16-bit pointer arithmetic (CLC/ADC) for data stream advance.
- `STA $D404` — writes SID V1 control register.
- `DEC abs` — decrements duration counter.
- This is a simple track-based note player: load note, look up freq, write SID,
  update data pointer, decrement duration. No complex command dispatch.

### v3 (3 SIDs, relocated)
- Same structure as v2 but freq table address is wildcarded (relocation-ready).
- SBC operand also wildcarded (can subtract different note-base offset).
- Data pointer high-byte increment uses `ADC #00` (zero carry propagation, not
  a non-zero increment) — data is organized within a single page.
- $D404 write is moved BEFORE the indirect data read (control register updated
  first, then pitch data fetched).

### Unversioned (308 SIDs, relocated)
- Same `SEC / SBC / ASL / TAY / LDA freq,Y / STA D400 / D401 / D404` preamble.
- Data reading: `EE ?? ??` (INC abs) + `AC ?? ??` (LDY abs) + `B1 ??` (LDA (zp),Y)
  — a distinctly different data-pointer model from v2/v3's CLC/ADC 16-bit arithmetic.
- Two `EE ?? ??` (INC abs) instructions — one likely for lo-byte, one for absolute
  address counter. The entire data-pointer mechanism uses absolute RAM cells, not ZP
  16-bit pointers.
- This is the dominant architecture (93% of corpus). Likely represents the mature
  SongSmith release that shipped in the Loadstar "30-page manual" version.

### What is NOT visible in signatures (OPEN — RE needed)
- How voice 2 and voice 3 are handled (signatures show V1 writes only).
- Instrument/envelope programming (ADSR registers $D405-$D418).
- Tempo/timing mechanism (CIA timer vs. VBI).
- How songs are structured in memory (headers, pattern pointers, repeat/loop data).
- The editor side: how notes are entered, stored, and serialized to the player format.
- Whether "phrases" or patterns exist (like Sidplayer's HED/TAL repeat blocks).

---

## Loadstar Context

- **Publisher:** Softdisk Publishing, Shreveport, Louisiana.
- **Run:** 199 issues, 1984–2007; Loadstar 128 for C128; UpTime companion.
- **Archive:** https://archive.org/details/loadstar_disk (331 D64 images);
  also Loadstar Compleat on itch.io (https://rodneylives.itch.io/loadstar,
  $15, 488 MB, all 199 issues in D64+D81).
- **Loadstar Compleat collection** separates SongSmith as a discrete product
  in the collection's directory tree: "SongSmith [bad]" appears in one user's
  corrupt copy listing (Lemon64 thread), alongside Brain Stuff, Compleat Bible,
  KC's PUD, etc. — confirming SongSmith was distributed as a self-contained
  sub-product within Loadstar, not embedded in individual issues.
- **Music composers noted in HVSC using SongSmith:**
  Cruz, Debby (7 SIDs, reference release); Mario Oropesa (classical transcriptions).
  Also: MUSICIANS/B, MUSICIANS/G, MUSICIANS/H, MUSICIANS/M, MUSICIANS/R,
  MUSICIANS/S, MUSICIANS/W directories (exact names not extracted this session).
- **DeepSID 'L' icon:** DeepSID adds an 'L' focus icon for composers who exclusively
  used Loadstar SongSmith. This confirms the tool produced a recognizable and
  catalogued subset of the HVSC.

---

## Leads to Follow

1. **Fetch sidid.cfg entry for Song_Writer** — compare its byte signature with
   Loadstar_SongSmith_v1 to determine if they share code (precursor vs. variant).
   `grep -A3 "Song_Writer" sidid.cfg` on raw file.
2. **Disassemble CSDb D64** — `Songsmith-Loadstar.d64` is the primary binary.
   Mount with VICE / c1541, list directory, load player routine, run seed_disassembly.
   The unversioned signature anchor (`38 E9 ?? 0A A8 B9 ?? ??`) gives a
   precise entry point into the play routine.
3. **Identify instrument/ADSR programming** — the signature covers only V1 freq+ctrl.
   A full disassembly will reveal whether envelope (ADSR) is per-instrument or
   per-song, and whether $D402/$D403 (pulse width) is set.
4. **Confirm voice 2/3 handling** — likely at fixed offsets from V1 registers
   ($D400→$D407→$D40E), but could be loop-structured.
5. **Identify data format** — what does the data stream look like? Is it pure
   note+duration pairs? Are there embedded commands (tempo, instrument change)?
   The simplicity of the signatures (vs. Sidplayer's rich command set) suggests
   a simpler format, possibly note-only with per-voice header for tempo/instrument.
6. **Archive.org Loadstar issues 27-28** — the comp.sys.cbm Loadstar #168 post
   mentions "reverse-engineering the song codes from LS #27-28" as theoretically
   possible. This implies issues 27-28 used the Garrett/Gardner precursor format.
   Fetch D64s of issues 27-28 from https://archive.org/details/loadstar_disk
   to check if they contain a songmaker tool different from SongSmith.
7. **Locate the 30-page SongSmith manual** — it likely ships on the D64 as a text
   file (Loadstar's typical doc format). Mounting the CSDb D64 or any Loadstar
   issue containing SongSmith and reading the `MANUAL` or `DOCUMENTATION` file
   would give the user-facing format description.
