# SoedeSoft / Soundmaster — GitHub & Tools Survey

<!-- PROVENANCE
source: Web searches + WebFetch against GitHub, cadaver/sidid, WilfredC64/player-id,
        ice00/jc64, realdmx/c64_6581_sid_players, desidulate, ChiptuneSAK, sid2midi,
        libsidplayfp, and CSDb/Remix64/VGMPF reference pages.
date: 2026-06-13
researcher: automated cluster (github_tools cluster)
note: This file covers the GitHub code-search scope only. Signature analysis is in
      sidid_signature_analysis.md; manual format docs in csdb_manual_de.md;
      population numbers in population_census.md; DeepSID classifier in
      deepsid_classifier.md.
-->

---

## 1. GitHub code search — SoedeSoft-specific parsers / disassemblies

**Result: NEGATIVE. No public GitHub repository contains SoedeSoft/Soundmaster
source code, a hand-annotated disassembly, or a format-aware parser.**

Searched terms: "SoedeSoft", "Soundmaster C64", "Jeroen Soede", "Michiel Soede",
"Soundmaster_V1.0".

All hits returned are:

| Repository | Relevance |
|---|---|
| cadaver/sidid | Byte-pattern signatures only (no structural parser). Covered in §3. |
| WilfredC64/player-id | Re-packages sidid's sidid.cfg; same signatures. Covered in §3. |
| ice00/jc64 | Binary `.dis` annotation file `SoundMaster1.dis` — proprietary JC64dis format, not human-readable source. Covered in §2. |
| realdmx/c64_6581_sid_players | NOT present. The repo has ~13 player directories (Hubbard, Kimmel, Tel, Galway, etc.); SoedeSoft/Soundmaster is absent. |
| anarkiwi/desidulate | NOT present. Engine-blind register-log tool. Covered in §4. |
| ChiptuneSAK | NOT present. Covered in §4. |

**Conclusion:** SoedeSoft source is not public, and no one has published a
reverse-engineered disassembly on GitHub. The player binary (~884 bytes) has not
been annotated to the level of, say, the Tel/Kimmel engines in realdmx's repo.

---

## 2. JC64dis (ice00/jc64) — the only tool with SoundMaster-aware output

JC64dis is an iterative C64 disassembler (Java) that ships with ~70+ `.dis`
annotation files in `doc/example/`. One of these is:

```
doc/example/SoundMaster1.dis
```

URL: https://github.com/ice00/jc64/tree/master/doc/example

**What it is:** A JC64dis-proprietary binary annotation file (~237 KB). When
applied to a SoundMaster SID in JC64dis, it provides labelled disassembly
(routine names, entry points, data labels). The file is not human-readable in
isolation — it is parsed by the JC64dis Java application.

**What it implies:** ice00 (Ian Coog, the JC64dis author) has done enough
structural analysis of SoundMaster to produce this annotation. He is also a
contributor to sidid signatures (per sidid.nfo: "Signatures provided by Ian Coog,
Ice00, Ninja, Yodelking, Wilfred/HVSC and Prof. Chaos"). The annotation covers
"SoundMaster1" — likely the V1.0 or the dominant V3.x layout; unclear whether
it covers all sub-variants.

**To extract labels:** run JC64dis (jar from iceteam.itch.io/jc64dis) on a
representative SoundMaster SID with the `SoundMaster1.dis` profile loaded and
export as text. That would yield a human-readable labelled disassembly — the
most useful bootstrapping artifact for SIDfinity migration.

**No `example/` subdirectory** was found (only `demo/`, `digi/`, `image/`
subdirs); the `.dis` file is at the flat `doc/example/` level.

---

## 3. Player identification tools — sidid / WilfredC64/player-id

### 3a. cadaver/sidid (https://github.com/cadaver/sidid)

The canonical SoedeSoft signatures live in `sidid.cfg` and `sidid.nfo`.

**sidid.nfo metadata block (complete):**

```
SoedeSoft
   AUTHOR: Jeroen Soede & Michiel Soede
 RELEASED: 1988 Soedesoft
REFERENCE: https://csdb.dk/release/?id=117095
  COMMENT: The editor is also known as Soundmaster or SoedeSound Editor

(Soundmaster_V1.0)
   AUTHOR: Jeroen Soede & Michiel Soede
 RELEASED: 1988 Soedesoft
REFERENCE: https://csdb.dk/release/?id=10735
  COMMENT: The editor is also known as SoedeSound Editor

(Soundmaster_V3.1)
   AUTHOR: Jeroen Soede & Michiel Soede
 RELEASED: 1989 Soedesoft
REFERENCE: https://csdb.dk/release/?id=90307

(Soundmaster_V3.2)
   AUTHOR: Jeroen Soede & Michiel Soede
 RELEASED: 1988 Soedesoft
REFERENCE: https://csdb.dk/release/?id=117086
  COMMENT: This version of the editor is not officially released by Soedesoft
           and was only meant for internal use only
```

**sidid.cfg signature block (complete):**

```
SoedeSoft
D0 03 BD ?? ?? 9D ?? ?? 60
B9 ?? ?? 4A 4A 4A 4A 9D ?? ?? B9 ?? ?? 0A 0A 0A 0A 9D ?? ?? B9

(Soundmaster_V1.0)
9D ?? ?? BD ?? ?? D0 ?? 18 B9 ?? ?? 7D ?? ?? 99 ?? ?? 99 00 D4
B9 ?? ?? 69 ?? 99 ?? ?? 99 01 D4 4C

(Soundmaster_V3.1)
A9 ?? 9D ?? ?? 4C ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60

(Soundmaster_V3.2)
A9 ?? 9D ?? ?? 4C ?? ?? 18 BD ?? ?? 7D ?? ?? 9D ?? ??
7D ?? ?? 9D ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60
```

(`??` = wildcard byte; `END` implicit at line break.)

**Engine-label space used by sidid:**
- `SoedeSoft` — parent engine label (matches all variants via root sig)
- `(Soundmaster_V1.0)` — sub-variant, 1988
- `(Soundmaster_V3.1)` — sub-variant, 1989
- `(Soundmaster_V3.2)` — sub-variant, 1988 internal

**No other SoedeSoft-related entries exist** in sidid. There is no V2.x
label and no separate "SoedeSound" label — all are grouped under `SoedeSoft`.

**Algorithm:** Pure byte-pattern match with wildcard `??` and `AND` recovery
points. No player-specific logic; no init/play address heuristics. The three
sub-variant patterns are secondary signatures that only fire after the root
`SoedeSoft` block matches. See `sidid_signature_analysis.md` for the full
disassembly interpretation of each signature.

**Signature provenance:** Per `sidid.nfo`, signatures are contributed by
"Ian Coog, Ice00, Ninja, Yodelking, Wilfred/HVSC and Prof. Chaos." The
SoedeSoft signatures were presumably contributed by ice00 (same person as
JC64dis author; see §2).

### 3b. WilfredC64/player-id (https://github.com/WilfredC64/player-id)

A modern reimplementation of sidid's approach. Stores signatures in
`config/sidid.cfg` — content is **identical** to cadaver/sidid's cfg (both
tools share the same community-maintained signature file). Also ships a
`config/sidid.nfo` with the same metadata shown in §3a.

**Finding:** WilfredC64/player-id adds no new SoedeSoft-specific signatures
beyond what cadaver/sidid already has. It is not independently useful for
format analysis.

---

## 4. Engine-neutral tools — confirmed NEGATIVE results

These tools have **no SoedeSoft-specific handling**. They treat SoedeSoft
SIDs as opaque PSID blobs and process them at the chip-register level only.

### 4a. libsidplayfp / libsidtune

**NEGATIVE.** libsidplayfp is a cycle-accurate 6510+SID emulator. It has no
engine-specific code paths for any composer format including SoedeSoft. Every
PSID is played by emulating the CPU executing the embedded player binary. The
library has no concept of "Soundmaster notes" or "Soundmaster instruments."

Confirmed by: web search returning no libsidplayfp hits for "SoedeSoft" or
"Soundmaster"; architecture of libsidplayfp as documented (plays any PSID via
6510 emulation).

### 4b. ChiptuneSAK

**NEGATIVE.** ChiptuneSAK v0.6 supports: PSID/RSID (via 6502 emulation),
GoatTracker 2 / GoatTracker 2 Stereo. Proposed/in-progress: MusicXML, MOD,
NSF, SAP. SoedeSoft/Soundmaster is not mentioned anywhere in its documentation
or import/export list.

Source: https://chiptunesak.readthedocs.io/en/stable/sid.html

### 4c. sid2midi

**NEGATIVE.** sid2midi (version 0.17.8, latest known) works by emulating the
C64 environment and analysing SID register output — it is engine-blind. Its
release announcement mentions no engine-specific support. It would process
SoedeSoft SIDs by emulating the player binary, not by parsing the music data
format.

Source: https://remix64.com/news/new-sid2midi-version.html

### 4d. desidulate (anarkiwi)

**NEGATIVE.** desidulate operates on VICE `-sounddev dump` SID register logs
— completely engine-blind. No SoedeSoft or Soundmaster entry in README or
source. Outputs to WAV, SMF MIDI, Sid Wizard instruments, Pandas dataframes.

Source: https://github.com/anarkiwi/desidulate

### 4e. JC64dis (ice00/jc64) — partially positive

**PARTIAL POSITIVE.** Unlike the above, JC64dis is NOT engine-blind for
SoundMaster — it ships the `SoundMaster1.dis` annotation profile (§2).
However it does not parse or convert the music data format; it only provides
a labelled disassembly view of the player code in context. It does not expose
note tables, instrument structures, or bar/block data programmatically.

---

## 5. CSDb / Demoscene — historical context

**SoedeSoft release catalogue (from CSDb group #1815):**

| Title | Year | Type |
|---|---|---|
| SoedeSound Editor V1.0 | 1988 | Tool |
| Soundmaster V3.2 | 1988 | Tool (internal, not publicly released) |
| Soundmaster V3.1 | 1989 | Tool |
| S.F.X. Editor | 1989 | Tool |
| Contact Demo | 1989 | Music Collection |
| Magic Drums | 1988 | One-File Demo |
| Trail Mix | 1988 | One-File Demo |
| + 12 further demo/game/intro releases | 1987–1989 | various |

**Key historical facts from Remix64 interview with Michiel Soede:**
- Jeroen Soede (brother) wrote "the routine" (the player); Michiel Soede wrote
  "the editor."
- Both built from scratch: "everything from scratch, nothing was ripped."
- Inspired by dissatisfaction with Chris Huelsbeck's Soundmonitor (judged "too
  limited" and producing excessive file sizes).
- The Amiga port "SoundMaster II" was based on their C64 routine.
- Jeroen focused on melodies (most SoedeSoft music); Michiel focused on
  experimenting with unusual sounds.

Source: https://remix64.com/interviews/interview-michiel-soede-www-soedesoft-com.html

**Soundmaster V3.1 CSDb release (#90307):**
- Download: `soundmaster3.1.prg` (C64 .prg file, 384 downloads), a German
  PDF manual (`Soundmaster_v3.1_[german].pdf`, 166 downloads), and a .prg docs
  file (136 downloads). The German PDF is translated/documented in
  `csdb_manual_de.md`.

**VGMPF notes (12 O'Clock C64):**
- Confirms Soundmaster V3.1 was used in commercial game scores.
- Notes: "basslines, non-title rhythms, and a few Title melodies sound different
  on every 6581 because they use SID's unstable filter" — SoedeSoft exploits
  filter resonance in ways that are hardware-revision-dependent.

---

## 6. SoedeSoft modern presence

**soedesoft.com** currently sells "SIDmaster," a Rack Extension / VST plugin
for Reason Studios that emulates the SID 6581/8580 chip. The plugin description
states effects are "based on SoedeSoft's original music routine of the 80's"
(arpeggios, wave patterns, pulse width modulation, filter). This is a
re-implementation, not a documentation of the original format.

---

## Summary table

| Tool | SoedeSoft-specific? | Format-aware? | Verdict |
|---|---|---|---|
| cadaver/sidid | YES — engine label + 3 sub-variant byte sigs | code pattern only | Identification only |
| WilfredC64/player-id | YES — same cfg as sidid | code pattern only | Identification only |
| ice00/jc64 (JC64dis) | YES — `SoundMaster1.dis` annotation | player code labels only | Best bootstrap for disassembly |
| realdmx/c64_6581_sid_players | NO | — | Not present |
| libsidplayfp / libsidtune | NO | — | Engine-blind emulator |
| ChiptuneSAK | NO | — | Not supported |
| sid2midi | NO | — | Engine-blind |
| desidulate | NO | — | Engine-blind |
| Any GitHub parser/converter | NO | — | Does not exist |

---

## Leads to follow

1. **Extract JC64dis annotation labels** — run `java -jar jc64dis.jar` on a
   representative SoundMaster SID (e.g. `hvsc85/MUSICIANS/S/SoedeSoft/...`)
   with the `SoundMaster1.dis` profile and export as text. This would give
   routine names + data-section labels without writing new disassembly from
   scratch. Most valuable first step.

2. **Contact ice00 / Ian Coog** — the JC64dis author has already annotated the
   player (the `.dis` file proves it). He may have unpublished notes or a more
   complete disassembly. His GitHub is https://github.com/ice00.

3. **Download `soundmaster3.1.prg` from CSDb #90307** — the actual C64 tool
   binary. Run it under VICE, load a song, step through the player code with
   the built-in monitor. The German PDF manual (already in `csdb_manual_de.md`)
   is the companion reference.

4. **Download `SoedeSound Editor V1.0` from CSDb #117095** — the 1988 "V1.0"
   edition (what sidid calls the root SoedeSoft + Soundmaster_V1.0 variant).
   Important because it predates V3.x and may have a simpler data format that
   is easier to analyse first.

5. **Locate `SoedeSound V3.2` (internal) from CSDb #117086** — the unreleased
   internal version (1988). May reveal intermediate format evolution between
   V1.0 and V3.1.

6. **HVSC STIL scan** — `C64Music/DOCUMENTS/STIL.txt` under the
   `MUSICIANS/S/SoedeSoft/` tree may have per-tune comments by HVSC cataloguers
   that give musician/game credits and occasionally note player quirks.

7. **Unstable-filter note** (from VGMPF) — SoedeSoft's filter usage is noted as
   hardware-revision-sensitive. USF representation will need to decide whether
   to model filter init state (already handled by `init.sid` block) and whether
   filter count sweep values need clamping logic for 8580 compatibility.

8. **Examine "S.F.X. Editor" (1989, CSDb)** — a separate SoedeSoft tool for
   sound effects. May share the same instrument/sound format as Soundmaster,
   or may be an independent format. If shared, it could provide additional
   instrument examples.
