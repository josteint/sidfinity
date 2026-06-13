---
source_url: multiple (see per-section headers)
fetched_via: direct
fetch_date: 2026-06-14
author: synthesized from sidid.cfg + Loadstar archive research
content_date: 2026-06-14
reliability: secondary (signatures primary; version-to-release mapping inferred)
---

# Loadstar SongSmith — Version Differences and Release History

## Product Overview

**Name:** SongSmith (also spelled "Songsmith" in product listings)  
**Publisher:** Softdisk Publishing / Loadstar  
**Platform:** Commodore 64  
**Catalog item:** #069525  
**Price:** $9.95–$10.00 (US)  
**Format:** Single 1541 disk (D64)  
**Contents:** Music editor + player + 30-page manual + 8-tune jukebox  
**Description (from Loadstar Letter catalog, 1995/1996):**  
> "LOADSTAR'S own music-making program. With this deluxe music editor/player you can
> easily transcribe music from sheet music or make up your own tunes. Songsmith comes
> with a slick 30-page manual and a jukebox player with eight tunes."

Sources:
- Loadstar Letter Issue #59 (full text, archive.org): confirmed product listing
- Loadstar Letter Issue #28 (Nov 1995, archive.org): identical listing; price $9.95

**Audience:** Hobbyist/non-demoscene composers (US, Loadstar readership). The HVSC
corpus of Loadstar_SongSmith tunes includes hobbyist transcriptions of folk songs,
anthems, and popular tunes — not demoscene productions.

**Known HVSC composers using SongSmith:**
- Cruz, Debby (Loadstar_SongSmith; 7 SIDs confirmed: folk/classical transcriptions)
- Marquis, Dave (mentioned in Loadstar #168 comp.sys.cbm thread alongside SongSmith)
- Beggerow, Alan (HVSC listing; STIL entry not retrieved)
- Davis, John S. (HVSC listing; STIL entry not retrieved)

OPEN: Retrieve HVSC STIL.txt sections for each composer to confirm SongSmith tool notes.

---

## Historical Context and Precursor

Source: comp.sys.cbm thread "Text From The Brand New LOADSTAR #168"
(https://groups.google.com/g/comp.sys.cbm/c/1TtXLOgICfs), quoting Fender Tucker:

> "the songmaker they used in those days was written by Joe Garrett and Alan Gardner,
> and was the precursor to SongSmith"

The thread further notes (re. LS #27–28):
> "there's probably programming wizards who could reverse-engineer the song codes...
> but there's little chance of anyone wanting to."

This establishes:
1. SongSmith has a precursor songmaker by **Joe Garrett and Alan Gardner**, published
   in early Loadstar issues (circa issues 27–28, which would put the precursor at
   approximately 1987–1988 given Loadstar launched in 1985 and was monthly).
2. SongSmith itself was developed as a replacement/upgrade to this earlier tool.
3. SongSmith is a Loadstar in-house product ("LOADSTAR'S own music-making program"),
   consistent with Softdisk Publishing authoring tools for their platform.

OPEN: Identify who wrote SongSmith proper (is it Garrett/Gardner again, or someone
else at Softdisk?). The Loadstar Compleat archive on itch.io (rodneylives.itch.io/loadstar,
$15) includes SongSmith and may have documentation identifying the author.

---

## Version Archaeology from sidid Signatures

The four HVSC engine labels and their corresponding sidid patterns give us structural
fingerprints for each version of the player. See `sidid_signatures.md` for full decoded
assembly. The key architectural differences:

### v1 — Earliest / Simplest

**Signature anchor:** `B1 F9 E6 F9 D0 02 E6 FA` (LDA ($F9),Y; INC $F9; BNE; INC $FA)

- Uses ZP pointer pair **$F9/$FA** (hardcoded, not wildcarded) — confirms NOT relocated.
- No SID register writes ($D4xx) appear in the 15-byte signature; either the SID
  writes come before/after this sequence, or this version writes them differently.
- The `CMP #$19 / BCC / CMP #$1D / BCC` following the LDA suggests note-range
  clamping or a rest/duration sentinel check (notes 25/$19 and 29/$1D are C-2 and E-2
  in the standard C64 note table — plausible as range sentinels).
- Likely corresponds to the "early songmaker" era or the first version of SongSmith
  proper.

### v2 — Second generation (fixed layout, freq table $C290)

**Signature anchor:** `38 E9 01 0A A8 B9 90 C2 8D 00 D4 C8 B9 90 C2 8D 01 D4`

- Freq table at **absolute $C290** (hardcoded in the signature) → loads at a fixed
  address; NOT relocatable.
- Note arithmetic: `SEC / SBC #1 / ASL` → `(note - 1) × 2` = word-table index.
- Standard SID freq-lo/hi pair written first (`$D400`, `$D401`), then control (`$D404`).
- 16-bit ZP pointer arithmetic for data sequencing (CLC / ADC #imm / STA ZP).
- This is likely the version distributed as catalog item #069525 (the fixed-address
  distribution on the 1541 disk).

### v3 — Relocated version

**Signature anchor:** `38 E9 ?? 0A A8 B9 ?? ?? 8D 00 D4 C8 B9 ?? ?? 8D 01 D4`

- Same general structure as v2 but **all absolute addresses wildcarded** → the player
  can be relocated in memory.
- SBC operand wildcarded (`E9 ??`) — the note-number offset may differ across songs
  or is now a variable.
- The high-byte step of the 16-bit pointer increment is `ADC #0` (`69 00`) — meaning
  data pages are self-contained (no cross-page pointer increments from this step; the
  low byte carries into the high byte automatically via the CLC/ADC carry chain).
- `$D404` write moved before the indirect-Y read vs. v2's order (reordering of
  register-update sequence).
- This is the "reloc" variant: the same basic engine architecture as v2 but packaged
  to be position-independent, consistent with embedding in HVSC PSID files where the
  load address is specified in the PSID header.

### Unversioned `Loadstar_SongSmith` — Alternative data-read architecture

**Signature anchor:** `38 E9 ?? 0A A8 B9 ?? ?? 8D 00 D4 C8 B9 ?? ?? 8D 01 D4 AD ?? ?? 8D 04 D4 EE ?? ??`

- Shares the note→freq-table front-end with v3 (same note arithmetic + freq lo/hi
  writes to $D400/$D401 + control write to $D404).
- After $D404 write, diverges: uses `EE ?? ??` (INC abs) + `AC ?? ??` (LDY abs)
  instead of `A0 ?? / B1 ??` (LDY #imm / LDA (zp),Y). This means:
  - Data pointer is an absolute address, incremented byte-by-byte (not a ZP pair
    with 16-bit arithmetic).
  - Y register is loaded from a RAM cell (absolute), not set as a fixed immediate.
- Followed by another `EE ?? ??` + `CE ?? ??` (DEC abs), then `AD` (LDA abs start).
- This represents a **different data-streaming model** from v2/v3, or a later
  optimization that replaced the ZP pointer pair with a simpler ABS-based scheme.

---

## Working Hypothesis: Release Timeline

| Tag | Architecture | Reloc | Likely era |
|-----|-------------|-------|-----------|
| `Loadstar_SongSmith_v1` | Indirect-ZP $F9/$FA, no freq table | No | Earliest (precursor or initial release?) |
| `Loadstar_SongSmith_v2` | Freq table $C290, ZP ptr | No | Early-mid; fixed-address disk distribution |
| `Loadstar_SongSmith_v3` | Freq table relocated, ZP ptr | Yes | Mid; HVSC-friendly reloc version |
| `Loadstar_SongSmith` | Freq table relocated, ABS ptr | Yes | Latest or parallel branch |

OPEN: The numbering (v1, v2, v3, unversioned) is cadaver's sidid classification, not
Loadstar's own versioning. Loadstar's internal version numbers (if any) are unknown.
The unversioned label might be cadaver's "couldn't determine version, catch-all" or
might represent the actual commercial version while v1/v2/v3 are pre-release/alternate
builds.

---

## HVSC Corpus Count

The project has 314 Loadstar_SongSmith SIDs in HVSC (from the stub `research.md`
already in this docs directory). The distribution across v1/v2/v3/unversioned tags is
unknown.

OPEN: Query `hvsc84.db`:
```python
import sqlite3
db = sqlite3.connect('hvsc84.db')
for eng, cnt in db.execute(
    "SELECT engine, COUNT(*) FROM sids "
    "WHERE engine LIKE 'Loadstar_SongSmith%' GROUP BY engine"
): print(eng, cnt)
```

---

## Leads to Follow

1. **Identify SongSmith author** — Check the Loadstar Compleat archive disk contents
   for a credits screen or documentation file naming the SongSmith programmer.
   Rodneylives itch.io confirms SongSmith is in the archive ($15).

2. **First-issue identification** — The Loadstar Letter back-issue catalog mentions
   #069525 as a standalone product but not as "first appeared in issue N." Earlier
   issues (LS #27–28, ~1987) had the Garrett/Gardner precursor. SongSmith proper
   likely debuted between LS #50–100 (early–mid 1990s) based on the product price
   point and the comp.sys.cbm #168 thread (late-1990s) treating it as current.
   OPEN: Search Loadstar Letter issues #20–#50 for SongSmith first-announcement.

3. **Corpus sweep for version distribution** — Run sidid against all 314 HVSC
   Loadstar_SongSmith SIDs to get v1/v2/v3/unversioned counts. This guides which
   version to prioritize for RE.

4. **Confirm v1 authorship** — Is v1 the Garrett/Gardner precursor (distributed in
   early Loadstar issues) repurposed/ripped into HVSC? Or is it the first commercial
   SongSmith release? The fixed ZP $F9/$FA pointers and absence of SID writes in the
   15-byte v1 signature are very different from v2/v3, suggesting a genuinely different
   (older) tool.

5. **Find the 30-page manual** — The manual is the key to understanding the user-level
   format semantics (what "note number," "instrument," "duration" mean in SongSmith's
   UI). May be in the .d64 as a SEQ file. Download: CSDb internal file
   `http://csdb.dk/getinternalfile.php/121491/Songsmith-Loadstar.d64`.

6. **HVSC STIL.txt for Loadstar composers** — Download the full STIL.txt and grep
   for Beggerow_Alan, Cruz_Debby, Davis_John_S, Marquis_Dave sections. May contain
   tool notes from the HVSC curators.

7. **DeepSID 'L' focus-icon logic** — Find in the DeepSID PHP/JS the exact engine
   string(s) that trigger the Loadstar-composer icon. This will confirm whether
   all four Loadstar_SongSmith* variants are treated equally.
