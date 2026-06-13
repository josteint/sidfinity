---
source_url: https://www.pouet.net/prod.php?which=61442 ; https://www.vgmpf.com/Wiki/index.php?title=Soundmonitor ; local deprecated/gt2_pipeline/tools/sidid.cfg ; github (search) ; chiptunesak/sidplayfp docs
fetched_via: WebFetch (pouet/vgmpf/github-search) + WebSearch + local file read (sidid.cfg) + local player byte-verify
fetch_date: 2026-06-13
author: pouet/VGMPF communities; sidid.cfg = Cadaver/HVSC player-id project; parser landscape = SIDfinity analysis
content_date: sidid.cfg signatures (long-standing); pouet/vgmpf 1986–2024
reliability: primary for the sidid byte signatures (and the local verification of MusicMaster_1); secondary for pouet/vgmpf prose; negative result for external parsers
---

# Soundmonitor — Pouet, VGMPF, and the parser / detection landscape

## Pouet (prod #61442 — Soundmonitor V1.0, "Demotool", Oct 1986)
No new format detail; historical/anecdotal only. Useful corroborations:
- kb_: "Eight pages of tiny hex dump." ultra: "i also typed in the hex dump listing." tomaes:
  "64'er magazine 10/86 … five pages … quite terrible. But … a breakthrough … rather unique."
- visy: "an extremely masochistic way of composing." p01: "Sound program … for ~30 years."
- Searching Pouet for "soundmonitor" returns only this prod; no technical writeups.

## VGMPF wiki (vgmpf.com/Wiki/Soundmonitor) — corroborations + a couple of new facts
- Creator Chris Hülsbeck (18, hobbyist). First published **Sep 19 1986** (the 64'er issue is dated
  10/1986). Driver **slow and non-relocatable**, songs **always > 10 KB**.
- Format = hierarchical: bars entered separately, linked in a **track/step table**; each **step
  row holds tempo, length, volume, fade-out speed**; cells carry bar assignment + transpose +
  instrument-set. (This pins down the **SP "step parameters" byte = {tempo, length, volume,
  fade-out speed}**, which the namelessalgorithm prose left vague.)
- Native driver "Musicmaster" supported **transpose, detune, portamento, vibrato, PWM, filter
  modulation, and arpeggios (a first in an editor)** — matches the 24-param sound layout.
- Variants: **Rockmonitor** (DUSAT, ~April 1987) **adds built-in samples**; **"The Final
  Musicplayer" (1987)** = an optimized driver variant with enhanced waveform changes + sample
  support, given to select composers (e.g. Georg Brandt). → a distinct later replayer to watch for.
- Used by 9 composers for game scores; 6 more (incl. Barry Leitch, Jeroen Tel) used it before
  moving to games.

## Existing external parsers / readers — NEGATIVE RESULT (do the RE ourselves)
- **ChiptuneSAK** (c64cryptoboy) and **sidplayfp/libsidplayfp**: both **emulate** the 6502 and
  capture SID writes; neither *parses* the Soundmonitor module structure. (libsidplayfp ships
  `sidplayer1/2.bin` = the old PlaySID player stubs, unrelated to Soundmonitor.)
- **JC64dis** (Java C64 disassembler) and **JITT64** (per namelessalgorithm) can *identify* a
  Soundmonitor player and import from PSID, but are disassembler/converter UIs, not a documented
  format parser we can lift. (Local JC64dis stash under `tmp/jc64/` — disassembler only.)
- **github.com/arnaud-neny/rePlayer** — multi-format player; not confirmed to carry a Soundmonitor
  reader. Lead.
- GitHub code search for a Soundmonitor format parser requires auth (no `gh` here, web search
  gated); none surfaced. **Conclusion: SIDfinity will be doing original RE** — there is no
  off-the-shelf module parser. The strongest existing artefact is the sidid signature DB below.

## sidid player-ID signatures (PRIMARY — vendored locally, version-discriminating)
Source: `deprecated/gt2_pipeline/tools/sidid.cfg` (the Cadaver/HVSC player-identification DB; this
is what produced `hvsc84.db`'s `engine='Soundmonitor'`). The entire family below is classified by
HVSC as **"Soundmonitor"**. Each `(Name)` is a sub-variant with a discriminating byte pattern
(`??` = wildcard byte, `AND` = a second required pattern). These are reloc-invariant detection
keys and the **best version-discrimination tool we have**.

```
Soundmonitor      : D0 16 BD ?? ?? 29 10 F0 2A BD ?? ?? 9D ?? ?? BD          ; base/original
(DUSAT/RockMon2)  : 48 29 0F AA CA 68 4A 4A 4A 4A 18 69 ?? 8D ?? ?? 4C
(MusicMaster_1)   : 8D 0C CE 8D 18 D4 60 A0 17 A9 00 99 00 D4 99 F4          ; ← V1.0 MusicMaster
(DUSAT/RockMon3)  : 4A 4A 4A 4A AA BD ?? ?? 8D ?? ?? BD ?? ?? 8D ?? ?? A2 ?? 8A 48 20 ?? ?? 68 CA D0 ?? A9 ?? 8D 18 D4
(DUSAT/RockMon3h) : 8D 0C CE 20 70 CE 60 A0 17 A9 00 99 00 D4 99 F4
(DUSAT/RockMon4)  : 8D 0C CE 4C 18 CA 60 A0 17 A9 00 99 00 D4 99 F4
(DUSAT/RockMon5.0): 8D 04 D4 8D 0B D4 8D 12 D4 A9 00 99 00 D4 99 AE          ; gate-off ×3 + clear
(DUSAT/RockMon5.1): 8D 04 D4 8D 0B D4 8D 12 D4 A9 00 99 00 D4 99 B0
(BeatBox/Karl_XII): 8D 1E ?? 8D 18 D4 60 A0 17 A9 00 99 00 D4 99 06
(Karl_XII)        : 8D CC CD 8D 18 D4 60 A0 17 A9 00 99 00 D4 99 B4
(DigiMonitor)     : AA CA 8E ?? ?? 8E ?? ?? AD ?? ?? 8D ?? ?? AD ?? ?? 29 F0 0D ?? ?? 8D ?? ?? AD 18 D4 60
(JamMasterV1)     : B9 ?? ?? 8D 18 D4 20 ?? ?? E8 E8 D0 ?? BD ?? ?? 18 7D ?? ?? A8 B9 ?? ?? 8D 18 D4
(Syndicate/BB)    : AA BD ?? ?? 8D 04 DD BD ?? ?? 8D 05 DD BD ?? ?? 8D ?? ?? A9 00 85 ?? BD ?? ?? 85 ?? BD ?? ?? 8D
(Digitronix)      : 8D 0C CE 8D FE 9F 60 A0 17 A9 00 99 00 D4 99 F4
(MusicMaster_2)   : 8D 72 CE 60 A0 17 A9 00 99 00 D4 99 5A CE 99 73 AND BD 00 9C 8D 04 DD BD 00 9D
(DrumMaker2)      : 8D 72 CE 60 A0 17 A9 00 99 00 D4 99 5A CE 99 73 AND BD 00 9C 20 60 CC BD 00 9D
(MusicMaster_TMM) : 8D 0C CE 8D FF ?? 60 A0 17 A9 00 99 00 D4 99 F4
(Huelsbeck_Digi_V1): A0 ?? A5 ?? CD ?? ?? F0 ?? B1 ?? 8D ?? ?? 29 0F
(Huelsbeck_Digi_V2): A0 ?? A5 ?? C5 ?? F0 ?? B1 ?? 85 ?? 29 0F 4A 18 69 ?? 8D 18 D4
(Cavi_Digi)       : 4A 4A 4A 8D 18 D4 A4 ?? 88 D0 ?? 60 29 0F 8D 18 D4 A4 ?? 88 D0 ?? 60
(ReD_Packed)      : F0 01 60 20 ?? ?? A9 ?? 8D FB ?? 4C 05 ?? 4C
```

### Reading the signatures (cross-checked against the live $C000 player)
- The recurring tail **`A0 17 A9 00 99 00 D4 99 F4`** = `LDY #$17; LDA #$00; STA $D400,Y;
  STA $xxF4,Y` — the **SID-clear loop** (clears all 24 regs $D400–$D417, then a work-var mirror).
  **VERIFIED present at $CA6A** in `Dance_at_Night.sid` (MusicMaster_1). It's the family's reset
  fingerprint; RockMon3h/4/Digitronix/Karl_XII/MusicMaster_TMM are *one-instruction* edits of the
  MusicMaster_1 dispatch right before this loop (`8D 0C CE` then a `JSR/JMP/STA` variant) — i.e.
  the variants are the SAME engine with different glue, exactly as expected from a hacked type-in.
- **RockMon5.0/5.1** replace the front with explicit `8D 04 D4 / 8D 0B D4 / 8D 12 D4` (gate-off on
  all three control regs) — the same silence-all block found at **$C48A** in the V1.0 player. The
  trailing byte (`99 AE` vs `99 B0`) is the only V5.0-vs-V5.1 difference (work-var base offset).
- The **`*_Digi*`, `DigiMonitor`, `DrumMaker2`, `Cavi_Digi`, `Syndicate/BB`** variants add sample/
  digi playback (`8D 04 DD` = write to CIA $DD04 timer → sample replay; `29 0F 8D 18 D4` = 4-bit
  volume-register digi). These are the **sample-bearing forks** (Rockmonitor lineage + Huelsbeck's
  own digi) — they will need Mode-2 (cycle-exact) handling, not the Mode-1 tracker path, and likely
  carry an extra sample table beyond the 24-byte sound bank.
- **Decompiler discriminator strategy:** match the player blob against this table → pick the
  variant → (a) confirm V1.0/MusicMaster vs Rockmonitor vs digi, (b) locate the player base from
  the matched offset, (c) read the $A000-relative data tables. `play=$C475` (V1.1 raster) and
  `play=$0000` (IRQ-installed) are header-level hints that complement the byte match.

## Cross-reference summary (which doc has what)
- **Byte layout / data model** → `csdb_namelessalgorithm_RE.md` (memory map + note encoding +
  24-param sound table) and `csdb_release_and_downloads.md` (HVSC signature census + live data-base
  confirmation).
- **Per-frame SID write model** → `csdb_release_and_downloads.md` §"Player RE" (note-trigger gate
  sequence + register-major steady-state order + reset).
- **Versions / variants** → `csdb_release_and_downloads.md` §"Version map" + this file's sidid table.

## Leads to follow
- **archive.org/details/64er_1986_10/** — original magazine prose: the definitive SP step-parameter
  packing (tempo/length/volume/fade) byte positions, the AR/S record layout, and the song-header
  first/last/loop-step fields. (VGMPF confirms SP = {tempo,length,volume,fade-out}; get the byte
  order from the magazine.) **Top priority primary source.**
- Vendor + disassemble a **Rockmonitor V4/V5** and a **Huelsbeck_Digi** rip to document the
  **sample table** delta and the digi write timing (Mode-2). Candidates: CSDb 20676 (RockMon IV,
  DUSAT), 175027 (RockMon5, FIS); HVSC `init=$9FD0 play=$0000` cluster for IRQ-digi.
- **github.com/arnaud-neny/rePlayer** + **JITT64** — check for an existing Soundmonitor module
  reader to validate our layout against.
- The sidid project upstream (Cadaver) may have newer/finer Soundmonitor signatures than the
  vendored 2017-era cfg — worth refreshing if variant misclassification appears.
- Lemon64 thread `t=15402` — possible English manual / extra docs.
- The named variants in the sidid table that are NOT obviously DUSAT (BeatBox/Karl_XII,
  JamMasterV1, Digitronix, DrumMaker2, ReD_Packed) — identify their origin groups if any of their
  tunes resist the V1.0 layout.
