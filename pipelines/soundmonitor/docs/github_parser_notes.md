<!--
provenance:
  source_url: multiple — github.com/ice00/jc64 (cloned locally at tmp/jc64), sourceforge.net/projects/jitt64,
              chiptunesak.readthedocs.io, remix64.com/news/new-sid2midi-version.html,
              chiptunesak source modules, libsidplayfp/libsidplayfp.
  fetched_via: local read of cloned ice00/jc64 source (READ-ONLY) + WebSearch/WebFetch for the others.
  fetch_date: 2026-06-13
  author: ICE Team (jc64/JITT64), David Knapp/ChiptuneSAK team, Michael Schwendt (sid2midi), libsidplayfp team.
  content_date: jc64 source as cloned 2026-06-13; ChiptuneSAK 0.6 (2020); sid2midi (last 2007).
  reliability: PRIMARY for jc64 source observations; SECONDARY for tool capability summaries from docs/search.
-->

# SoundMonitor / MusicMaster — parser notes across tools

Goal: find any tool that parses SoundMonitor's **binary data layout** (vs. register-trace
analysis), and corroborate the layout from §3 of `github_jc64dis_local_disasm.md`.

**Headline finding:** No open-source tool ships a SoundMonitor *format-aware* parser. The two
Ice Team tools (JC64dis, JITT64) are the only ones that even *name* the player, and they do so
via Cadaver's SidId byte signatures + a generic 6502 disassembler / freq-table autodetect — the
actual data-layout knowledge is the **hand annotation** in the `.dis` we mined. Everything else
(ChiptuneSAK, sid2midi, libsidplayfp) is engine-neutral register-trace, format-blind. So for
SIDfinity the JC64dis annotated disassembly is the authoritative layout source, and our own
extractor will be the first SoundMonitor format parser in this lineage.

---

## 1. JC64dis (ice00/jc64) — disassembler, not a format parser

Cloned locally at `tmp/jc64/`. Relevant source (READ-ONLY):

- **Detection**: `src/sw_emulator/software/Disassembly.java:1316`
  ```java
  if (option.showSidId) {
    player = SidId.instance.identifyBuffer(buf, buf.length);
  ```
  `SidId.java` is "SidId from XSidplay2 … SIDId V1.09 by Cadaver (C) 2012" — it loads Cadaver's
  `sidid.cfg` byte-pattern database (see `github_sidid_signatures.md`). So JC64dis recognises
  "Soundmonitor" purely by signature match; it has **no SoundMonitor-specific code path**.

- **Freq table autodetect**: `Disassembly.java:1293` calls `SidFreq.instance.identifyFreq(...)`
  — a generic note-frequency-table detector. This is what auto-labelled `frequencyHi`/`frequencyLo`
  ($7370/$73CF) in the Shades project, not SoundMonitor knowledge.

- **Project / `.dis` format**: `src/sw_emulator/swing/main/{Project.java,FileManager.java,MemoryDasm.java}`.
  The `.dis` is a gzip'd custom `DataOutputStream` stream (project VERSION 7 for our examples),
  NOT Java object serialization. Decode recipe documented in `github_jc64dis_local_disasm.md`
  header. The per-cell record carries `userLocation` (label), `userComment`, `userBlockComment`,
  `dasmComment` (auto), `dataType`, `type`. **All SoundMonitor layout knowledge lives in those
  user fields**, authored by Stefano Tognon.

- **Relocation**: `Project.relocates` (a `Relocate[]` of `{fromStart,fromEnd,toStart,toEnd}`) is a
  generic block-move list, used because HVSC SoundMonitor tunes are relocated copies of the
  standalone `$C000` MusicMaster player. Not a SoundMonitor-specific table.

### Local SoundMonitor-family `.dis` examples present in the clone
`tmp/jc64/doc/example/` (all gzip'd, project VERSION 7):
| file | tune | init | play | image |
|------|------|------|------|-------|
| `SoundMonitor_shades.dis` | "Shades (filter corrected)" — Chris Hülsbeck (c)1986 M&T | `$7000` | `$742E` | $4E40–$78FF (PSID v2, CIA speed=1) |
| `Rockmonitor2.dis` | "Rockmonitor 2" — Swagerman & Giesen (c)1987 Dutch USA Team | `$7FDD` | (RSID) | $7FDD–$CBFA |
| `Rockmonitor5.dis` | "Rockmonitor 5 Demosong" — OPM (c)1988 Dutch USA Team | `$C000` | (RSID) | $8414–$CCDF |

These are the three local annotated disassemblies. Shades = the clean SoundMonitor/MusicMaster
ancestor; the Rockmonitors are the evolved Dutch USA Team derivatives (see §4 + the variant
analysis below).

---

## 2. JITT64 (Java Ice Team Tracker 64, Ice Team)

- SourceForge: https://sourceforge.net/projects/jitt64/ ; home: https://jitt64.sourceforge.net/
  (latest 1.04). Itch mirror: https://iceteam.itch.io/jitt64.
- It is a **table-based SID tracker/editor** (instruments fully table-driven), with a PSID
  **import** path. Its importer reuses the same `SidId` detection + disassembly machinery as
  JC64dis (same Ice Team `sw_emulator` package), then maps recognised player data into JITT64's
  *own* native tracker tables — it does **not** expose a documented SoundMonitor on-disk schema.
- Practical value for us: confirms the engine is importable, and JITT64's own help
  (https://jitt64.sourceforge.net/help/track.html) describes a track→sequence→instrument-table
  model congruent with SoundMonitor's progIndex→bar→sound-patch structure. But the byte layout
  comes from JC64dis, not JITT64.

---

## 3. Register-trace tools (format-blind — listed so we don't chase them)

| tool | approach | SoundMonitor support |
|------|----------|----------------------|
| **ChiptuneSAK** (`chiptunesak.sid`) | emulates the SID (based on SIDDump by Lasse Öörni & Stein Pedersen) → RChirp; an open alternative to sid2midi | engine-neutral register trace; **no** SoundMonitor format parser |
| **sid2midi** (Michael Schwendt) | emulates a C64 + analyses SID output to infer notes | closed source, Windows-only, no RSID, last updated 2007; engine-neutral |
| **libsidplayfp / libsidtune** | plays PSID/RSID via reSID/reSIDfp | playback only; libsidtune parses the **PSID/RSID container**, not the player's music data |

None reads `progIndexTable` / bars / sound patches. They observe `$D4xx` writes — exactly what
SIDfinity already does for *verification* (`siddump --writelog`), not what we need for
*extraction*.

---

## 4. Variant corroboration (data-layout deltas, from the local Rockmonitor `.dis`)

Mining the Rockmonitor2/5 `.dis` user labels (parsed locally) shows how the family evolved from
SoundMonitor/MusicMaster. Useful for the extractor's per-variant config:

**Shared invariant core (all variants):** per-voice 7-byte SID shadow + target-freq blocks; the
`makePortamentoEffect / makeVibratoEffect / makeFilterCutEffect / makeWavePulseEffect` effect
quartet; the `processNoteV1/V2/V3 → outVoiceN → outFilter → setFilterVol($D418)` write order;
95-entry `frequencyHi/frequencyLo` note tables; control written LAST per voice (gate edge).

**SoundMonitor / MusicMaster (Shades):**
- Flat `progIndexTable` ($5580) of step indices, `$FF`+target = loop.
- Per-step parallel pointer tables `voice{1,2,3}TableIndex` + `instrTableIndex` (16-bit LE pairs).
- Per-step transpose tables `voice{1,2,3}TranspTable`.
- Sound patches `sound00..` (64-byte slots, 24 used params per §3 of the disasm doc).
- Tempo = patch byte `$0E` → `STA $DC05` (CIA-1 Timer A hi).
- Double-buffered note pointers (`swapNotePointer`, $A5..$AC ↔ $07E9..).

**Rockmonitor 2 (Dutch USA Team, RSID):** SoundMonitor + a **sample/digi sub-engine**:
- Labels `sample0..sample14` ($8100–$8FFF, 256-byte sample blocks), `sampleTableLo/Hi`
  ($9000/$9100), `block0..block6f` ($9200–$9FFF, 32-byte rhythm/drum blocks).
- Split, doubled tables: `v1TableIndexLo`/`v1TableIndexHi` ($A000/$A100) **plus** a *second*
  freq-transpose table per voice: `voice1TranspTable` ($A200) AND `freq1TranspTable` ($A300)
  (×3 voices). So Rockmonitor adds a separate fine freq-transpose alongside the note transpose.
- `instrTableIndexLo/Hi` ($AC00/$AD00), `instruments` ($AE00), `sound00..3C` ($B000+, 64-byte),
  `arsTable00..1f` ($BF00+, 8-byte **arpeggio** tables — the "AR/S DATA" per-bar arps).
- A large **work/buffer area**: `buffer*V1/V2/V3` ($CBFA+) is a per-voice instrument **buffer**
  filled by `FillInstBuffer`/`insertBufferV1`/`multiplyBy12` (the engine pre-computes a per-voice
  instrument copy each step), then the `actual*` shadow block ($CD80+).
- Extra effect detail: `makeRelFreqUp/Down`, `bigPortDn`, `reloadFilterVal`, `setDrumSpeed`,
  `extractSpeedSound`, sample dispatch (`setSampleBlock`/`useSampleInstr`/`outSample`).

**Rockmonitor 5 (OPM, RSID):** Rockmonitor lineage, restructured:
- Explicit `trackLo`/`trackHi` ($9000/$9100) **track tables** + `sequence1..7` ($9220+) +
  `seqLength` ($BF03) — i.e. a true track→sequence two-level structure (vs. Shades' single
  progIndexTable). Bars are `block1..block6` (variable, scattered $8414–$9A43).
- Digi via an **NMI** sample player: `NMIRoutine` ($CBBB) reads 4-bit nibbles (`highNibble`/
  `lowNibble`, `is1F` end test), `setTimerA`/`timerAHi/Lo` drive the sample clock; `sampleBlocks`
  ($9E00), `sampleTable` ($9FB0), `lengthTable` ($9FC0), `sampleTableLo/Hi` ($AC00/$AD00).
- Same split transpose + freq-transpose tables ($A200/$A300 …) and the same buffered-instrument
  + `actual*` work area ($CCEA / $CD3A+) as RM2.

> Implication for the extractor: SoundMonitor/MusicMaster is the base config. Rockmonitor adds
> (a) a sample/digi voice (NMI-clocked 4-bit, cycle-significant — Mode 2 verification),
> (b) a per-voice freq-transpose table, (c) per-bar arpeggio tables, (d) a track/sequence split
> (RM5). These map to per-engine config fields, not new USF schema, in line with the CORE TENET.
> The `Soundmonitor` SidId block (see `github_sidid_signatures.md`) enumerates the exact variant
> set HVSC distinguishes (RockMon2/3/3h/4/5.0/5.1, MusicMaster_1/2/TMM, DrumMaker2, DigiMonitor,
> Huelsbeck_Digi_V1/V2, BeatBox/Karl_XII).

---

## 5. Bottom line for SIDfinity

- **Extraction layout source = the JC64dis annotated `.dis`** (mined in
  `github_jc64dis_local_disasm.md`). No other tool encodes SoundMonitor's data layout.
- **JITT64** confirms importability and the track/sequence/instrument-table mental model but
  reuses JC64dis detection; not a separate spec.
- **Register-trace tools are for verification, not extraction** — we already have a better one
  (`siddump --writelog`).
- The canonical standalone player is **MusicMaster init=$C000 / play=$C020** with a work area
  around `$CExx` (per the `MusicMaster_1` signature `… A0 17 A9 00 99 00 D4 99 F4 CE` = "LDY #$17 :
  LDA #$00 : STA $D400,Y : STA $CEF4,Y" clear loop). HVSC's relocated copies (like Shades @ $7000)
  share that logic at a shifted base — handle via a relocation delta, exactly as JC64dis does.
