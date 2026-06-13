---
source_url: multiple — see section headers
fetched_via: local HVSC binary inspection + web sources (see forum_discussion.md for full provenance)
fetch_date: 2026-06-13
author: aggregated
content_date: 1989–2026
reliability: primary for HVSC binary observations; secondary for inferences
---

# RoMuzak — Technical Notes from Forum/Scene Research

This file captures concrete technical claims gathered from forum discussion, scene interviews,
and direct HVSC binary observation (printable-string extraction only — NOT disassembly RE).
All RE-needed claims are flagged explicitly.

---

## 1. Physical identity

| Field | Value |
|-------|-------|
| Author | Oliver Blasnik (handle: ROM) |
| Publisher | Digital Marketing, Krefelder Str. 16, 5142 Hückelhoven 2, NRW, Germany |
| V6.3 phone | 02435-1295 (area code 02435 = Hückelhoven) |
| V6.3 year | 1989 |
| V7.96 year | 1990 (CSDb: 15 March 1990) |
| Cracked by | Apa-Soft + Cosmos (V6.3) |

The business address in the V7.9 binary string (`/KREFELDER STR.16 /5142 HUECKELHOVEN2`)
matches a print-shop/media company in Hückelhoven-Baal (Dieter Mückter, Krefelder Str. 16,
41836 Hückelhoven-Baal; noted in web search). "Digital Marketing" was likely a local software
PD distribution label operating out of this address circa 1989–1990.

---

## 2. Version differences (observable from HVSC binaries)

### Version identification strings (verbatim, from in-binary printable strings)

**V6.3:**
```
ROMUZAK89F                                          ← compact machine tag (10 bytes, at load+$09)
** ROMUZAK V6.3 <W> BY OLIVER BLASNIK, <C> DIGITAL MARKETING!! 02435-1295!! **
```

**V7.96:**
```
RMZ+V7.96                                           ← compact machine tag (9 bytes, at V7 block +$09)
*** ROMUZAK V7.9 (W) BY OLIVER BLASNIK (C) BY DIGITAL MARKETING /KREFELDER STR.16 /5142 HUECKELHOVEN2 ***
```

Note: The version string says "V7.9" (abbreviated) while the compact tag says "V7.96" (full).

### sidid detection bytes (from cadaver/sidid, source: `github_sidid_signature.md`)

These are the instruction sequences that uniquely identify each version (at player code region):

```
V6.x: C9 ?? F0 ?? 0A 8D ?? ?? 0A 6D ?? ?? AA A0 00
      = CMP #?? / BEQ ?? / ASL A / STA abs / ASL A / ADC abs / TAX / LDY #0

V7.x: C9 ?? F0 ?? 48 29 07 0A 8D ?? ?? 0A 6D ?? ?? AA A0
      = CMP #?? / BEQ ?? / PHA / AND #$07 / ASL A / STA abs / ASL A / ADC abs / TAX / LDY #?
```

**Key V7 change:** `48 29 07` (PHA + AND #$07) inserted before the frequency table index
multiply sequence. V6 uses raw note byte; V7 masks the low 3 bits before the freq table
lookup — indicating a changed note byte encoding where semitone/octave are packed differently.

**OPEN (RE):** What do the upper bits of the V7 note byte encode? Effect flag, octave index,
or something else? Requires tracing the V7 play routine.

### PSID layout differences

| Property | V6.3 | V7.96 |
|----------|------|-------|
| Default load address | $8000 | contains two blocks: $6E00 (V6.3 sub-player) + $8000 (V7 sub-player) |
| Init address | $8000 (same as load) | $9493 (above both sub-player blocks) |
| Play address | $8003 (=load+3, 2nd JMP) | $7FFD (3 bytes before V7 block, a relay jump) |
| Songs | 1 (typical) | 2 (Crime_Time example) |
| Speed | 0 (VBlank/50Hz) | 0 (VBlank/50Hz) |
| Subtune dispatch | single player | OPEN (RE): init at $9493 selects sub-player per subtune |

### V7.96 dual-player layout (observational)

A V7.96 SID (e.g. Crime_Time.sid, load=$6E00) contains two complete player blocks:

```
C64 $6E00 – $7FFF:  V6.3 player block (4608 bytes)
                    - Contains ROMUZAK89F tag + V6.3 version string
                    - Likely used for FC-converted voices (legacy compatibility)
C64 $8000 – $9???:  V7.96 player block (5319 bytes in Crime_Time)
                    - Contains RMZ+V7.96 tag + V7.9 version string
                    - 3 JMP vectors: init=$8308, play=$8340, stop=$82DA
C64 $9493:          Top-level init (dispatches to correct sub-player per subtune)
```

OPEN (RE): Why does V7.96 include a V6.3 sub-player? Hypotheses:
1. Multi-subtune SIDs use V6.3 for some subtunes (FC-converted) and V7.96 for others (native)
2. V7.96 SIDs always include V6.3 as a backwards-compatible player (for FC-import voices)
3. The V6.3 block is repurposed as the V7.96 song data (not a player instance)

---

## 3. Performance characteristics

**Source:** c64scene.pl thread t=112 (user "skull"), March 2009.

- RoMuzak V6.3 consumes **~20 raster lines per channel per call** (measured with sprites active)
- Full 3-voice playback: ~60 raster lines per VBI interrupt (out of 312 PAL lines ≈ 19%)
- By comparison, Future Composer (optimized Geir port): **~2× less raster** than RoMuzak
- The player has a **modular per-channel structure** — each of the 3 voice routines can be
  called independently (confirmed by successful decomposition in 2009)
- The player contains **author/copyright validation code** that can be stripped to save cycles
  (location: unknown — OPEN for RE)
- Disassembly tool used by the Polish scener: **64COPY**

---

## 4. Player structure (observable / community-documented)

From the existing `research.md` (compiled in a previous session, method unspecified):

```
+$0000  JMP init
+$0003  JMP play
+$0006  JMP stop/reset
+$0009  "ROMUZAK89" (9-byte ASCII tag)        [V6.3: "ROMUZAK89F" = 10 bytes]
+$0012  Three 2-byte pointers to per-voice pattern data
+$0018  Instrument parameter block (~136 bytes): ADSR, waveform, PW, filter, vibrato/portamento
+$00A2  Standard frequency table (96 entries; consistent across V6.x tunes)
+$0202  Player code (~2636 bytes)
```

Total V6.3 binary size range: 2747–4041 bytes.

**NOTE:** The `+$0012` offset gives 3 × 2-byte pointers = 6 bytes ending at +$0018. This means
the pointers start 6 bytes after the ROMUZAK89 tag (which ends at +$0012). The instrument block
starts immediately after these pointers.

**OPEN (RE):** Confirm the instrument block structure — specifically: how many instruments? How
many bytes per instrument? What are the exact field offsets (ADSR = 2 bytes, waveform = 1 byte,
PW = 2 bytes, vibrato params = ?, portamento = ?)?

---

## 5. Feature: Future Composer V1.0 conversion

**Source:** VGMPF wiki (FC article), Lemon64 (V-Ga entry), multiple HVSC STIL entries.

- RoMuzak can **import / convert** Future Composer V1.0 songs
- Conversion produces a native RoMuzak SID (not an FC SID played through FC player)
- Many HVSC SIDs are annotated "RoMuzak conversion of [FC tune]" in STIL
- Example: V-Ga game music, originally in FC, appeared as "21.RoMuzak Tune" on Digital Marketing
  disk #182 (1989)

**Implication for format design:** If RoMuzak is a full re-encoder of FC data (not a hybrid
player), the instrument/effect model must be a superset or lossless translation of what FC V1.0
supports. FC V1.0 (C64) features include: per-voice patterns, instruments with ADSR + waveform
+ pulse width + vibrato, and a seq/orderlist structure. RoMuzak's model likely mirrors these.

---

## 6. Known user base

From HVSC census (V6.x: 598 SIDs; V7.96: 22 SIDs):

| Handle | HVSC folder | Version | Notes |
|--------|-------------|---------|-------|
| ECO (Raik Picheta) | MUSICIANS/E/Eco/ | V6.3 | 20+ SIDs, cover versions |
| Ass It | MUSICIANS/A/ | V6.3 | 56 SIDs (most prolific V6.3 user) |
| Sony (various) | MUSICIANS/S/ | V6.3 | 27 SIDs |
| Stefan Hartwig | MUSICIANS/H/Hartwig_Stefan/ | V7.96 | 8+ V7.96 commercial game music |
| Goesta Feiweier | MUSICIANS/F/Feiweier_Goesta/ | V7.96 | 12 SIDs, game music 1990–91 |
| Arndt Heitkamp | MUSICIANS/H/Heitkamp_Arndt/ | V7.96 | at least 1 (Digital_Excess-The_Demo.sid) |
| Schaefers Frank (Rockin Ltd) | MUSICIANS/R/Rockin_Limited/ | V7.96 | Ikarus.sid, Vincent.sid |
| Thomas Detert | MUSICIANS/D/Detert_Thomas/ | V6.3 | 1 SID (early work, switched to Compotech) |
| Robert Bachner (Esprit) | MUSICIANS/E/Esprit/ | V6.3 | Romuzak_Test.sid |
| Extern (various) | MUSICIANS/E/Extern/ | V6.3 | 4 SIDs |
| ODI (various) | MUSICIANS/O/Odi/ | V6.3 | 4 SIDs |

**Pattern:** V7.96 is **strongly correlated with commercial game music** (Starbyte, Rockin
Limited, Digital Excess) and dates to 1990–1991. V6.3 is the demo/PD scene version (1989).
V7.96 was apparently used exclusively by professionals with access to the updated editor.

---

## 7. Archive.org disk images — editor binaries

Two disk images exist on Archive.org (both labeled ACT 501, 1989):
```
https://archive.org/details/d64_Romuzak_Music_Demo-Editor_1989_ACT_501
https://archive.org/details/d64_Romuzak_Analyser-Play_Construction_Kit_1989_ACT_501
```

These are C64 D64 disk images of the **editor software** itself (not just SID files). The
"Analyser Play Construction Kit" title suggests it may include a separate utility for
analysing / playing back RoMuzak files — possibly the source of skull's "Turbo Reassembler"
and 64COPY-based reverse engineering in the c64scene.pl thread.

**Highest-ROI action:** Extract PRGs from these D64s using `c1541` or `cbmconvert`, then
examine printable strings + structure without emulation. No disassembly needed to see menu
text, field labels, and command names.

---

## 8. Clarification: Manfred Trenz mis-attribution

Several web sources state "RoMuzak is a music program by Manfred Trenz." This is **incorrect**.

Correct: Oliver Blasnik wrote RoMuzak; Digital Marketing published it.
Likely source of confusion: Manfred Trenz was also a prominent German C64 developer (Turrican,
R-Type) associated with Digital Marketing distribution — but as a customer/client, not author.

---

## Leads to follow

- **OPEN (high priority):** Extract PRG files from the two Archive.org D64 disk images using
  `c1541` (VICE disk tool, available on most systems) or `cbmconvert`. No emulation needed.
  This gives direct access to the editor's menu text, field labels, and structure constants.
  Command: `c1541 -attach romuzak.d64 -list` to see directory, then `-read FILENAME fname.prg`.

- **OPEN (medium priority):** Retry Forum64 thread #15654 via Wayback Machine:
  `https://web.archive.org/web/*/https://www.forum64.de/index.php?thread/15654-romuzak/`
  The thread is in the "Musik" sub-forum and appears to have 20+ posts about version availability.

- **OPEN (medium priority):** Search CSDb download section (when CSDb is available) for the
  Kryoflux disk image mentioned in Forum64 thread #83160 — this may be the only surviving
  copy of the actual V7.96 editor program.

- **OPEN (RE):** sidid V7.x signature includes `AND #$07` — determine what the upper 5 bits of
  the V7 note byte encode. This determines whether V7.96 changed the note format (and thus
  whether V6.3 tunes need re-encoding to play under V7.96 — which would explain the dual-block
  structure in V7.96 SIDs).

- **OPEN (RE):** Locate and characterize the copyright validation routine that skull stripped.
  It checks the in-binary credit string and likely stalls/crashes if tampered. Its size/behavior
  affects how much code must be isolated vs. called during RE of the init path.

- **OPEN (community):** "skull" (c64scene.pl, March 2009) completed a full disassembly of V6.3
  and offered to share it. If shared on c64scene.pl or another site, this is a huge shortcut.
  The thread (t=112) appears complete; check if skull replied to any file-share request.
