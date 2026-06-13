# SoedeSoft / Soundmaster — Version History

<!-- PROVENANCE
source_urls:
  - https://csdb.dk/group/?id=1815   (Soedesoft group — tools list)
  - https://csdb.dk/release/?id=117095  (SoedeSound Editor V1.0)
  - https://csdb.dk/release/?id=10735   (Soundmaster V1.0, Fire-Eagle release)
  - https://csdb.dk/release/?id=180209  (Soundmaster V1.0, EGO+FE+RfO release)
  - https://csdb.dk/release/?id=90307   (Soundmaster V3.1)
  - https://csdb.dk/release/?id=117086  (Soundmaster V3.2)
  - https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
  - https://sidpreservation.6581.org/sid-trackers/
  - https://remix64.com/interviews/interview-michiel-soede-www-soedesoft-com.html
  - pipelines/soedesoft/docs/csdb_manual_de.md  (Soundmaster V3.1 German manual)
  - pipelines/soedesoft/docs/sidid_signature_analysis.md  (byte signatures)
  - pipelines/soedesoft/docs/population_census.md  (HVSC addr clusters)
fetched_via: WebFetch (direct) + WebSearch + local repo docs
fetch_date: 2026-06-13
reliability: PRIMARY for version metadata (CSDb fetched directly or via sidid.nfo);
             SECONDARY for format/effect changes (inferred from sidid byte signatures
             and V3.1 German manual; no V1.0 or V3.2 manual was recovered);
             NOTE: CSDb was intermittently 503 during fetching — some release pages
             were inferred from search snippets.
-->

---

## Summary Table

| Version | CSDb ID | Release Date | Distributor | Status | Known from |
|---|---|---|---|---|---|
| SoedeSound Editor V1.0 | 117095 | 1988 | Soedesoft | Public (d64) | CSDb |
| Soundmaster V1.0 (FE release) | 10735 | Feb 1989 | Fire-Eagle + Soedesoft | Public (t64+d64) | CSDb |
| Soundmaster V1.0 (import) | 180209 | Mar 5 1989 | EGO + Fire-Eagle + Rage for Order | Public (d64) | CSDb |
| Soundmaster V3.1 | 90307 | 1989 | Soedesoft | Public (prg + PDF manual) | CSDb |
| Soundmaster V3.2 | 117086 | 1988* | Soedesoft/Fire-Eagle only | Internal only | CSDb |
| S.F.X. Editor | — | 1989 | Soedesoft | Unclear | Demozoo group page |
| SoedeSound Editor V1.1 | — | 1992 | Soedesoft | Unknown | CSDb scener page |
| Soede Editor V4.0 | — | post-1990? | Soedesoft? | Unknown | SID Preservation site |
| Soede Editor Turbo GTI SSS | — | post-1990? | Third-party custom | Unknown | SID Preservation site |

*V3.2 CSDb date reads "1988" but sidid treats it as post-V3.1; see notes below.

---

## Pre-Soundmaster: The Early Engine (~1985–1987)

The earliest SoedeSoft SIDs in HVSC carry copyright strings as early as "1985 Soedesoft"
(e.g., Yep, Ritme, Stijl, Real_Crazy). These predate any versioned "Soundmaster" branding.
The engine was already functional — at minimum for 3-voice melody + arpeggio + basic effects.

No editor disk for this era has been located in any archive. These SIDs appear to have been
composed in an unnamed precursor to SoedeSound Editor V1.0.

---

## SoedeSound Editor V1.0 (1988)

- **CSDb ID:** 117095
- **Also known as:** "Soede Sound Editor V1.0", "Soundmaster"
- **Release year:** 1988 (Soedesoft group)
- **Download:** `https://csdb.dk/getinternalfile.php/115253/SoedeSound_Editor_FE.d64`
  (243 downloads as of 2026-06-13)
- **Credits:** No credits listed in CSDb entry; authors are Jeroen Soede (player) and
  Michiel Soede (editor) by all other sources.

**CSDb user comment (Fred, 24 March 2013):**
> "This release uses the exact same player/editor as Soundmaster V1.0 but is released
> under a different name."

**Interpretation:** SoedeSound Editor V1.0 and Soundmaster V1.0 are the same software,
distributed at different times under two different names. The d64 disk directory string
"SOEDE-EDITOR /FE" confirms the Fire-Eagle internal label. The "SoedeSound Editor" name
appears to be the SoedeSoft-branded version; "Soundmaster V1.0" is the Fire-Eagle public
release name.

---

## Soundmaster V1.0 (February 1989)

Two CSDb entries document the public spread of V1.0:

### Entry A — CSDb #10735 (Fire-Eagle release)
- **Date:** February 1989
- **Groups:** Fire-Eagle, Soedesoft
- **AKA:** Sound Master v1.0, Sound Editor from FE
- **Credits:**
  - Code: Jeroen Soede (Fire-Eagle) + Michiel Soede (Fire-Eagle)
  - Music: Jeroen Soede + Michiel Soede (demo tunes: Airwolf, Last Ninja Mix)
- **Intro:** Fire Eagle Intro 02
- **Downloads:**
  - `http://csdb.dk/getinternalfile.php/115262/Soundmaster_V1_FireEagle.t64` (387 downloads)
  - `https://csdb.dk/getinternalfile.php/239985/Soundmaster V1.0 [fe].d64` (63 downloads)

### Entry B — CSDb #180209 (import spread)
- **Date:** 5 March 1989
- **Groups:** EGO, Fire-Eagle, Rage for Order
- **Import credit (comment by Frozen Fire, 30 Jul 2019):** "Toronto / Canadian import / spread"
- **Credits:** Code: Jeroen Soede + Michiel Soede; Import: Asterix! (RfO), G-Man
- **Demo SIDs included:** Airwolf, Last Ninja Mix, Magic Funk, The Big Deal
- **Note:** The March 5 date is the import spread date; the original release is February.

**Format notes for V1.0 (from sidid byte signature):**
The V1.0 player binary has a substantially different write path from V3.x:
```
9D ?? ?? BD ?? ?? D0 ?? 18 B9 ?? ?? 7D ?? ?? 99 ?? ?? 99 00 D4
B9 ?? ?? 69 ?? 99 ?? ?? 99 01 D4 4C
```
Key differences from V3.1:
- Uses `BNE` branch (`D0`) — implying a loop with conditional exit
- `99 00 D4 / 99 01 D4` — stack-indexed Y stores to $D400/$D401 (freq lo/hi); this is
  a different indexing scheme than V3.1's `9D 00 D4 / 9D 01 D4` (X-indexed absolute)
- `69 ??` (ADC #imm) present — immediate-operand addition in the freq computation path
- The overall structure is longer and more complex than V3.1's minimal snippet

This suggests V1.0 used a different internal loop organisation for the note/frequency
dispatch compared to V3.1, not merely a refactoring.

---

## Soundmaster V3.1 (1989)

- **CSDb ID:** 90307
- **AKA:** Sound Master V3.1
- **Release year:** 1989 (Soedesoft)
- **Distribution:** Released on Magic Disk 64 (per CSDb V3.2 note referencing "Magic Disk 64")
- **Downloads:**
  - Editor: `http://csdb.dk/getinternalfile.php/87430/soundmaster3.1.prg` (384 downloads)
  - C64 docs: `http://csdb.dk/getinternalfile.php/115243/Soundmaster_V3_1_Docs.prg` (136 downloads)
  - German PDF: `http://csdb.dk/getinternalfile.php/115254/Soundmaster_v3.1_[german].pdf` (166 downloads)
    — 18-page manual by Walter Konrad; translated in full in `csdb_manual_de.md`
- **Community reception:**
  - DRAX: "I also did a couple of tunes in this editor... and I still trying to find them"
  - Stainless Steel: "I actually liked this one back then."

**Format — what changed from V1.0 to V3.1:**
The V3.1 player signature is a short, clean sequence:
```
A9 ?? 9D ?? ?? 4C ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60
```
- `A9 ?? 9D ?? ??` — LDA #imm; STA abs — set a register then store
- `4C ?? ??` — JMP to another routine
- `BD ?? ?? 9D 00 D4` — LDA abs,X; STA $D400 (freq lo, X-indexed voice offset)
- `BD ?? ?? 9D 01 D4` — LDA abs,X; STA $D401 (freq hi)
- `60` — RTS

The X-register selects the voice (X=0,7,14 for voices 1/2/3). Freq lo/hi are stored
directly from a lookup table without any additional accumulation — pure table-lookup.

**Effect chain (per the V3.1 German manual — full detail in csdb_manual_de.md):**
The Soundmaster V3.1 engine provides these effects:
1. **3-voice playback** — indexed $D400-$D418 via X=0/7/14
2. **48 sound presets** ($00–$2F) — each with up to 3 parts
3. **ADSR** — attack/decay ($D405), sustain/release ($D406)
4. **Pulse width sweep** — initial value + per-tick delta, bounded by global max/min
5. **Arpeggio** — offset table (semitone offsets from current note), with one-shot prefix
   + looped body, $7F = "current note" sentinel (used for drum tick effect)
6. **Waveform table** — parallel to arpeggio, per-step $D404 writes; bit 4 enables
   vibrato/portamento within arp
7. **Vibrato** — amplitude or increasing-amplitude mode; global speed; per-sound delay
8. **Portamento** — 16-bit counter; enabled per-note via bit $80 in bar note byte
9. **Filter** — $D416 cutoff: initial value + per-tick delta (rate-gated); $D417 resonance
   + voice routing; $D418 filter mode + master volume
10. **Song hierarchy:** Steps → Blocks → Bars; per-step track transpose; per-block
    sound-number offset; per-block all-tracks transpose
11. **Per-note transpose-off flag** (bit $40) — suppresses track transpose on one note
12. **VBlank 50 Hz** — all timing

**Memory layout:**
The standalone player (saved with "R" command) loads at $6000 and starts via `SYS $6000`.
This produces the most common HVSC address pair: init=$6000, play=$6006 (309 of 929 SIDs).
The play offset of $0006 relative to init is the canonical V3.1 layout. See
population_census.md for the full cluster table.

**Embedded signature string:** `"88 SOEDESOFT-"` (year 1988 encoded in data area, even in
V3.1 copies dated 1989 — this is the copyright year of the original engine).

---

## Soundmaster V3.2 (date ambiguous — "1988" in CSDb, likely 1989)

- **CSDb ID:** 117086
- **AKA:** Sound Master V3.2
- **CSDb date:** 1988 (likely the engine's copyright year, not the release year — same
  pattern as the "88 SOEDESOFT-" string that appears in all versions)
- **Distribution:** Fire-Eagle members only; NOT publicly released by Soedesoft.
  CSDb note: "This is the 'only for members from Fire-Eagle' release of Soundmaster."
  sidid.nfo note: "This version of the editor is not officially released by Soedesoft
  and was only meant for internal use only."
- **Download:** Available on CSDb (332 downloads recorded)

**Format — what V3.2 adds over V3.1 (from sidid byte signature):**
```
A9 ?? 9D ?? ?? 4C ?? ?? 18 BD ?? ?? 7D ?? ?? 9D ?? ??
BD ?? ?? 7D ?? ?? 9D ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60
```
Compared to V3.1, V3.2 inserts before the final $D400/$D401 writes:
- `18` — CLC (clear carry)
- `BD ?? ?? 7D ?? ??` — LDA abs,X; ADC abs,X (add two indexed values)
- `9D ?? ??` — STA abs,X (store intermediate result)
- This pattern is repeated twice (for freq lo and freq hi)

**Interpretation:** V3.2 adds an accumulation step to both frequency bytes before
writing them to $D400/$D401. The `18 / ADC abs,X` sequence computes
`freq_lo = table_lo + offset_lo` (and similarly for hi). This is consistent with
a portamento implementation that accumulates a delta into the running frequency
each tick, rather than computing the target frequency directly from the note table.

The V3.2 player is therefore a superset of V3.1 with a modified portamento path.
Whether this was an experimental refinement that never made it into a public release
(hence the Fire-Eagle-only distribution) is not known.

---

## S.F.X. Editor (1989)

- **CSDb ID:** Not recovered in this session
- **Demozoo entry:** Listed under Soedesoft group (https://demozoo.org/groups/7598/)
  as "S.F.X. Editor, Tool, C64, 1989"
- **Purpose:** Sound effects editor, separate from the music editor

The S.F.X. Editor was a companion tool to Soundmaster for composing and editing
one-shot SFX patches. Its relationship to the Soundmaster player binary is unclear —
it may share the same player code (with SFX stored as separate sound preset data) or
may have its own player routine.

OPEN: No format documentation or download URL was recovered in this session.

---

## SoedeSound Editor V1.1 (1992)

- **CSDb ID:** Not recovered
- **Source:** Michiel Soede's CSDb scener page (id=6063) lists this under tool credits
- **Year:** 1992 — significantly later than the 1988–1989 active period
- **Significance:** The only known post-scene editor release. It may represent a
  resurrection or refinement of the editor after the Fire-Eagle dissolution. Whether
  it is C64 or Amiga is not established from available sources.

OPEN: No format documentation, download, or description recovered.

---

## Soede Editor V4.0 (date unknown)

Source: https://sidpreservation.6581.org/sid-trackers/

> "This successor [to Soundmaster] featured an expanded GUI with enhanced Bar Editor
> capabilities and sound design options. It reportedly allowed bars of varying lengths
> rather than strict 4/4 measures."

Key improvements over V3.1 as described:
- Bigger GUI
- Enhanced Bar Editor with more possibilities
- Variable bar lengths (not locked to 4/4 time signatures)

**Warning:** This version is mentioned only on the SID Preservation tracker page.
No CSDb entry, no HVSC SIDs with a V4.0 sidid signature sub-tag, and no disk image
were found. It may be a post-C64 or late-era continuation, or the name may be
informal. No sidid sub-tag `(Soundmaster_V4.0)` exists in sidid.cfg.

---

## Soede Editor Turbo GTI SSS (date unknown)

Source: https://sidpreservation.6581.org/sid-trackers/

> "Custom versions created by groups who modified official releases for specialized needs."

This appears to be a scene-custom fork of the Soundmaster editor (not player). "SSS"
is unexplained. No CSDb entry, HVSC sub-signature, or disk image was found in this
session. It is noted here only as a data point.

---

## What changed between versions — delta summary

| Version transition | Player change | Format change | Distribution change |
|---|---|---|---|
| Early engine → V1.0 | Unknown | Unknown | First versioned public release |
| V1.0 → V3.1 | Complete rewrite of freq write path (Y-indexed loop → X-indexed direct) | Unknown (format likely identical at song data level) | Fire-Eagle → Soedesoft public |
| V3.1 → V3.2 | Freq write path gains CLC+ADC accumulation (portamento refinement) | Unknown | Public → Fire-Eagle internal only |
| V3.x → V4.0 | Unknown | Variable bar lengths added | Unknown |

---

## HVSC Version Distribution (from sidid sub-tag classification)

From sidid_signature_analysis.md and population_census.md:

| sidid sub-tag | HVSC count (approx) | Notes |
|---|---|---|
| Soundmaster_V1.0 | minority | Early tunes; different addr cluster |
| Soundmaster_V3.1 | majority | Most common; $6000/$6006 cluster dominant |
| Soundmaster_V3.2 | minority | Fire-Eagle tunes only |
| SoedeSoft (unversioned) | some | Top-level tag catches any unmatched |

Exact counts by sub-tag require running `sidid` over all 929 SIDs; the DeepSID
classifier (deepsid_classifier.md) processes the resulting CSV but the CSV itself
was not available in this session.

---

## Leads to Follow

1. **V3.2 CSDb page (id=117086).** CSDb was 503 during fetch. When accessible, check
   whether the V3.2 .prg binary reveals any song data format differences from V3.1,
   or only the player binary differs.

2. **V1.0 player binary analysis.** The SoedeSound_Editor_FE.d64 binary was
   successfully downloaded (170.8 KB). Once loaded into a C64 emulator or disassembled
   with tools/seed_disassembly.py, the V1.0 player structure can be compared against
   the V3.1 structure derived from the German manual. This will answer: did the song
   data format change between V1.0 and V3.1, or only the player?

3. **Version gap V1.0 → V3.1.** No V2.x releases appear anywhere. Three hypotheses:
   a) V2.x was developed but never released (internal to SoedeSoft/Fire-Eagle);
   b) The jump to V3 was a marketing rebrand with no V2 public existence;
   c) V2.x was released under a different name (possibly the "SoedeSound Editor"
      branding applied to intermediate versions).

4. **Magic Disk 64 appearance.** The V3.2 CSDb entry references "Magic Disk 64"
   as the V3.1 distribution vehicle. Magic Disk 64 archives are preserved at
   http://magicdisk.untergrund.net/ and https://preservation64.de — search these
   for the specific issue that contained Soundmaster V3.1.

5. **SoedeSound Editor V1.1 (1992).** Unknown whether C64 or Amiga. If C64, it would
   be the last C64 player variant. Finding the CSDb entry would clarify its purpose
   and format compatibility with existing V3.x SIDs.

6. **S.F.X. Editor format.** Confirm whether SFX data is stored in the same sound
   preset format as Soundmaster ($00–$2F sound bank) or as a separate binary.
   This affects whether a USF pipeline must handle SFX data separately.
