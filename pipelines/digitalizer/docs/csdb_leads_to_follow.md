---
source_url: synthesised from research session 2026-06-13
fetched_via: n/a
fetch_date: 2026-06-13
author: research synthesis
content_date: 2026-06-13
reliability: secondary (unverified leads)
---

# Digitalizer — Leads to Follow

Ordered by estimated information density (highest first).

---

## TIER 1 — Highest priority: downloadable docs / help text

### 1a. V3.0 help text file — ALREADY RECOVERED
**Status: DONE — see docs/src/digitalizer_v3.0_instructions.txt**
Downloaded from: http://csdb.dk/getinternalfile.php/118523/Digitalizer-2.9(ff)%20v3.0.zip
Contains: complete keyboard reference for all three editor modes (Seq/Inst/Trk),
data format byte ranges for sequence commands, author's acknowledgments, dated June 1992.
Key findings summarised in csdb_version_differences.md.

### 1b. V3.5 zip — possible README or updated help
**URL:** http://csdb.dk/getinternalfile.php/23372/DIGITALIZER-V35.zip
**Why:** V3.5 added "alot of new functions" — may have updated docs.
**Action:** Download zip → list files → extract any .txt or readable docs
**Dest:** docs/src/digitalizer_v35_readme.txt (if found)

### 1c. V2.2 zip — earliest version, possible seed help file
**URL:** http://csdb.dk/getinternalfile.php/23398/Digitalizer_V2.2.zip
**Action:** Download zip → list files → extract any .txt or PETSCII docs

### 1d. V2.7 d64 — disk image with directory
**URL:** http://csdb.dk/getinternalfile.php/105675/panoramic_designs_-_digitalizer_v2_7.d64.gz
**Why:** Only Digitalizer version distributed as a bare D64 (no zip wrapper). D64
disk images often carry a BASIC README file or example songs visible in the directory.
**Action:** gunzip → open with c1541 or cbmconvert → list directory → extract text files
**Dest:** docs/src/digitalizer_v27_disk_contents.txt

### 1e. SteinTronic disk image — ancestor editor
**URL:** http://csdb.dk/getinternalfile.php/186137/SteinTronic1.d64
**Why:** Digitalizer's ancestor (Olav "borrowed" this). Comparing SteinTronic's format
with Digitalizer would show which structures Olav inherited.
**Action:** Open D64 → list files → compare instrument/pattern structure with Digitalizer

---

## TIER 2 — CSDb content not fully fetched

### 2a. V3.5 forum threads (4 threads)
**URL:** https://csdb.dk/release/?id=33650 → click "Forum Discussion"
**Why:** 4 threads are listed; technical notes from SHAPE/Blues Muz' users likely.
**Action:** Visit each thread URL and read all posts.

### 2b. V2.2 production note (1 entry)
**URL:** https://csdb.dk/release/?id=33646 (expand "Production Notes" section)
**Why:** CSDb lists 1 production note; WebFetch didn't expand it. May contain
format documentation or keyboard shortcuts.

### 2c. V2.8 production note (1 entry)
**URL:** https://csdb.dk/release/?id=33648 (expand "Production Notes" section)

### 2d. DTZ2SDI converter — production notes / comments
**URL:** https://csdb.dk/release/?id=237762
**Why:** The DTZ2SDI converter by 6R6 may have production notes describing what
Digitalizer V3.x format fields it reads and how they map to SDI.

### 2e. Raw JCH Format To SDI Converter (SHAPE)
**URL:** Search CSDb for "JCH" "SDI" SHAPE — find the release ID
**Why:** Parallel converter (JCH→SDI); the conversion logic reveals JCH format
which can be cross-referenced with Digitalizer format (both in SDI converter group).

---

## TIER 3 — Downloaded disk images / binaries needing analysis

### 3a. DTZ2SDI converter binary
**URL:** From CSDb #237762 download link
**Why:** The converter's C64 code READS Digitalizer V3.x data structures. The memory
access patterns in the converter reveal the byte offsets of the Digitalizer format.
**CONSTRAINT:** Do NOT disassemble in this session; note as OPEN RE task.
**OPEN RE:** disassemble DTZ2SDI → document every absolute address/offset it reads
from the Digitalizer song buffer → infer V3.x format structure.

### 3b. PD-editor.prg (zimmers.net)
**URL:** https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/PD-editor.prg
**Why:** Already confirmed as Digitalizer (contains "OLAV MORKRID/PANORAMIC" + 
"SAVE SOUNDTRACK DUMP SOUNDTRACK" strings). Load address and version unknown.
**OPEN RE:** c1541 / cbmconvert → extract → check 2-byte PRG header (load address)
→ disassemble player init to find entry points.

### 3c. V2.8 zip
**URL:** http://csdb.dk/getinternalfile.php/23400/Digitalizer_v2.8.zip
**Why:** 1991 version; compare binary size with V2.2/V2.5 to estimate scope of changes.

---

## TIER 4 — Scene databases not fully explored

### 4a. Kestra Bitworld
**URL:** https://kestra.exotica.org.uk/ → search "Digitalizer"
**Why:** Kestra archives many C64 tools with technical info not on CSDb.

### 4b. DeepSID — Olav Mørkrid music files
**URL:** https://deepsid.chordian.net/?file=/MUSICIANS/M/Morkrid_Olav/
**Why:** DeepSID identifies the player engine used in each SID. Browsing Olav's
HVSC directory would show which sidid entry fires for his tunes (Olav_Moerkrid?
Panorama? Digitalizer_V2.x?). Also: JCH added SteinTronic to DeepSID in 2019.

### 4c. DeepSID — Blues Muz' directory
**URL:** https://deepsid.chordian.net/?file=/MUSICIANS/B/Blues_Muz/
**Why:** 154 tunes by Blues Muz' use the Olav_Moerkrid player. DeepSID's per-file
player tag will show whether they identify as Olav_Moerkrid or Panorama or something else.

### 4d. Pouet.net — Panoramic Designs
**URL:** https://www.pouet.net/groups.php?which=... (find Panoramic Designs)
**Why:** Pouet sometimes has technical comments on tools not in CSDb.

### 4e. ExoticA
**URL:** https://www.exotica.org.uk/wiki/Panoramic_Designs_(c64)
**Note:** Returned browser-verification block in this session; retry in browser.

---

## TIER 5 — External references not chased

### 5a. "Equalizer V2.0" by Olav Mørkrid (CSDb #132732, 1992)
- Same year as Digitalizer V3.0; may be a companion tool or an effects processor
- Could share data format with Digitalizer

### 5b. Flimatic V3.7 (CSDb #38252, undated)
- Listed in Olav's releases; possibly a related tool

### 5c. Recollection #2 diskmag (CSDb #42400, 2006)
- Contains the Olav Mørkrid interview (Recollection interview ID 129)
- Full diskmag download may have additional technical articles about Digitalizer

### 5d. Hotspot #04 (CSDb #4236, 1990) — Olav interviewed
- Earlier interview; may have pre-V3.0 descriptions of Digitalizer

### 5e. World News #11 (CSDb #49721, 1991) — Olav interviewed
- 1991 = active Digitalizer development year; may describe V2.8 or upcoming V3.0

### 5f. Addymag (CSDb #189582, 1991) — Olav involvement
- Norwegian diskmag; may cover Digitalizer

---

## TIER 6 — Download mirrors to check

### 6a. Pokefinder.org
All Digitalizer versions list Pokefinder.org as an external source. The Pokefinder
mirror may have additional file listings not on CSDb (e.g., README files extracted
from disk images).
**URL:** Search pokefinder.org for "Digitalizer" (URL structure unknown — visit manually)

### 6b. C64 FTP mirrors
- ftp://ftp.funet.fi/pub/cbm/c64/audio/editors/ — the full editors directory
  (returned 403 from commodore.ca mirror; try direct FTP or wayback)

---

## RE Tasks (not for this research session — flag for disassembly phase)

These require binary analysis (siddump, py65, or disassembly). Document here as tasks
for when the research phase completes and disassembly phase begins.

| Task | What to run | Expected output |
|------|-------------|-----------------|
| Load address of V3.0 | read 2-byte PRG header | e.g., $1000 or $9000 |
| Load address of V2.2 | read 2-byte PRG header | probably same or different |
| V3.0 player entry points | +$0000 JMP init, +$0003 JMP play | confirm from research.md |
| Format of on-disk song data | disassemble SAVE SOUNDTRACK handler | byte offsets of patterns/instruments |
| Sentinel values per version | disassemble sequence reader | $7F vs $FF end-of-pattern |
| V3.5 player vs V3.0 | compare binary at sidid signature offset | same/different player engine |
| DTZ2SDI input parsing | disassemble converter | exact V3.x song data layout |
| OmegaSupreme_Digi output | trace $D418 writes | 4-bit digi output rate and encoding |
| ZP $FB/$FC usage | trace across all versions | data pointer vs. other ZP roles |

