# DefleMask C64 SID Player Variants and Scene Context

<!-- provenance
  primary_sources:
    - url: https://www.deflemask.com/changelog.txt
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      author: Leonardo Demartino (Delek)
      content_date: 2011–2024 (rolling changelog)
      reliability: HIGH — official author changelog
    - url: https://github.com/cadaver/sidid/blob/master/sidid.nfo
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      author: cadaver (Lasse Öörni)
      content_date: ongoing
      reliability: HIGH — primary SIDId tool; signatures extracted from real binaries
    - url: https://vgmrips.net/forum/viewtopic.php?t=342
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      author: various (Delek + community)
      content_date: 2012–2016
      reliability: HIGH — includes Delek posts, contemporaneous
    - url: https://www.deflemask.com/bugs/view.php?id=216
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      author: various + Delek
      content_date: 2021–2022
      reliability: HIGH — official bug tracker
    - url: https://www.deflemask.com/bugs/view.php?id=353
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      author: various + Delek
      content_date: 2023–2025
      reliability: HIGH — official bug tracker; Delek confirmed fix 2025-05-27
    - url: https://www.deflemask.com/forum/rom-builders/c64-sid-export-options-possibilities/
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      author: various
      content_date: 2021–2025
      reliability: HIGH — official forum
    - url: https://battleofthebits.com/lyceum/View/DefleMask+Tracker
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      author: BotB community wiki
      content_date: unknown, continuously updated
      reliability: MEDIUM — community wiki; DMF version table cross-checks with specs
    - url: https://www.lemon64.com/forum/viewtopic.php?t=75892
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      author: various C64 scene members
      content_date: 2020
      reliability: HIGH — direct user experience reports
    - url: https://hvsc84.db (local)
      fetched_via: sqlite3 read-only
      fetch_date: 2026-06-14
      reliability: HIGH — derived from HVSC #84 binary headers + SIDId classification
    - url: https://github.com/cadaver/sidid/blob/master/sidid.cfg
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      author: cadaver
      reliability: HIGH
-->

## 1. DefleMask Application Version Overview

DefleMask is a cross-platform multi-system chiptune tracker by Leonardo Demartino
("Delek"), first released publicly around 2011. It supports Commodore 64 (SID 6581/8580),
SEGA Genesis, NES, Game Boy, and other systems. It is not a native C64 tool; it runs
on Windows, macOS, Linux, iOS, and Android.

Key version milestones from the official changelog:

| App version   | DMF file format (hex) | C64 relevance |
|---------------|----------------------|---------------|
| v0.9.0 (2012–2013) | 0x11           | C64 system added; "basic .SID exporting" |
| v0.9.x "9b"  | 0x11 (subversion)    | **Player rewrite**: "new and better SID export, awesome use of memory and great sync"; 15xx/1Axx ADSR effects added |
| v0.10.c (2015) | 0x12                | No documented C64-specific changes |
| v0.11.0 (Oct 2015) | 0x13 / 0x15    | C64 rom exporter "improved" (no structural details found) |
| **v0.12.0 (Jun 2016)** | **0x16**   | **Player rewrite**: "Updated the C64 rom exporter, it is fast and roms are smaller"; SIDId tag = DefleMask_v12 |
| v1.0.0 (Apr 2021) | 0x18             | No documented C64-specific player changes |
| v1.0.9 (Aug 2021) | 0x18+            | Better emulation of 6581 combined waveforms (emulator only, not player) |

The "v12" in the SIDId tag `DefleMask_v12` is app version 0.12.x. The naming
convention (v12 = version 12 in single-integer counting) is consistent with
Delek's own numbering style on VGMRips and CSDb where he referred to the releases
as "DefleMask 9", "DefleMask 10c", "DefleMask 11", "DefleMask v12", etc.

DMF format version table cross-reference (from BotB wiki and specs):
- 9+  → 0x11, 10c+ → 0x12, 11+ → 0x13, 11.1+ → 0x15, v12+ → 0x16, 1.0.0+ → 0x18

## 2. SIDId Variant Map: App Version → Player Tag

| SIDId tag       | App version(s) | HVSC #84 count | Date range in HVSC |
|-----------------|----------------|----------------|--------------------|
| `DefleMask_v1`  | v0.9.0 initial release (2012–early 2013) | 1 | 2013 |
| `DefleMask_v2`  | v0.9.x "9b" through v0.11.x (2013–2016) | 69 | 2013–2023 |
| `DefleMask_v12` | v0.12.0+ and all v1.x (2016–present)   | 240 | 2014–2025 |

Notes:
- Three v2 entries carry release dates 2010–2011 (Nitro Pulse). These are
  almost certainly attribution errors in the HVSC SID header (composition date
  vs. upload date) — the binary player bytes are byte-for-byte identical to
  confirmed 2013 v2 exports.
- Five v2 entries date to 2022–2023 (Drozerix, Tex). These authors appear to
  still be using old DefleMask versions (pre-0.12) in those years.
- Two v12 entries date to 2014–2015, predating the June 2016 v0.12.0 release —
  these may have used a pre-release or a custom build. Alternately they may
  be reclassified SIDs from an intermediate build between 0.11 and 0.12.

## 3. Player Signatures (SIDId)

From `sidid.cfg` (cadaver/sidid repo):

```
DefleMask_v1
E6 02 D0 02 E6 03 60 86 03 84 02 A9 00 85 04 20 END

DefleMask_v2
99 00 D4 CA D0 F4 86 03 A2 02 B5 END

DefleMask_v12
B5 ?? 9D 00 D4 CA 10 F8 C6 ?? 30 END
```

Decoded:
- **v1**: `INC $02 / BNE +2 / INC $03 / RTS / STX $03 / STY $02 / ...` — byte-streaming
  counter increment for a 16-bit pointer in zero page $02/$03.
- **v2**: `STA $D400,Y / DEX / BNE -12 / STX $03 / LDX #$02 / LDA zp,X` — Y-indexed
  bulk blit of register shadow block to $D400.
- **v12**: `LDA zp,X / STA $D400,X / DEX / BPL -8 / DEC zp / BMI` — X-indexed
  bulk blit (descending) with frame-counter gate.

## 4. Player Structure: Layout Differences

### DefleMask_v1 (Green_Tea.sid — the only HVSC #84 example)

- **Load address**: $0FF0
- **Init address**: $1061
- **Play address**: $102D
- PSID v2, single subtune, vblank (speed=0)
- File size: 51,449 bytes (single large SID)

Player structure (reconstructed from binary):
```
$0FF0: data/tables (?)
$1006: get_next_byte — reads 16-bit pointer in $02/$03, advances it
       The v1 signature sits here: INC $02 / BNE / INC $03 / RTS / STX $03 / STY $02
$102D: play() entry — reads song stream via get_next_byte, dispatches commands,
       single-byte-at-a-time register writes: TAX / JSR $1006 / STA $D400,X
$1061: init() entry
```

Key characteristic: no bulk blit. Registers are written one at a time by
fetching a byte from the stream (X = register offset, A = value). This is
compact but slower per frame than a shadow-array blit.

No CIA reads/writes in the player region examined.

### DefleMask_v2 (standard layout — 58/69 SIDs)

- **Load address**: $1006 (actual)
- **Init address**: $110F
- **Play address**: $1117 (init+8) — thin wrapper calling play_main at $103F
- PSID v2, single subtune, vblank (speed=0)

Layout:
```
$1006: header/data (4 bytes: 04 0B 12 ...)
$100A: player code begins
$1049: SID register blit loop (Y-indexed):
       STA $D400,Y / DEX / BNE -12   ← v2 signature region
       STX $03 / LDX #$02 / LDA zp,X
$103F: play_main — main per-frame dispatcher
$1117: play() entry (PSID play addr) — a wrapper that calls play_main ($103F)
       then returns; init also calls play_main once at startup
$110F: init() entry — LDX #$11 / LDY #$1B / JSR $1013; JSR $103F; RTS
       (copies $11 bytes × $1B = parameter block); instrument table at $1117+
```

CIA usage: reads $DC04/$DC05 (CIA1 timer A lo/hi) during init code — likely
for random seed or sync. Not a CIA-timed player; PSID speed=0.

Player code footprint: $110F − $1006 = $109 = 265 bytes (player stub only;
song data appended after).

Instrument/config table starts at $1117 (after the play wrapper), written
at init time. The table is part of the SID binary data.

Alternative v2 play addresses: 3 SIDs have play=$103F (pointing directly to
play_main, skipping the wrapper). Same player, different PSID header export.

### DefleMask_v12 (dominant layout — 112/240 SIDs: init=$1103, play=$1006)

- **Load address**: $1006 (actual)
- **Init address**: $1103
- **Play address**: $1006 (= load address = start of player)
- PSID v2, single subtune, vblank (speed=0)

Layout:
```
$1006: play() entry — immediately begins X-indexed blit:
       LDX #$18 / LDA $04,X / STA $D400,X / DEX / BPL -8   ← v12 signature
       Then: DEC $02 / BMI done / ...  (frame counter gate)
$1010–$10FF: player routines (stream decoder, effect engine)
$1103: init() entry — LDY #$09 / LDX #$11 / JMP $10B2 (or similar)
       Instrument/config table follows init entry point
```

CIA usage: **writes** $DC04 and $DC05 (CIA1 timer A lo/hi) during what
appears to be a timing-setup section of the init or play routine. This is
the probable cause of the sidreloc "Write out of bounds at $dc04-$dc05"
warnings reported in bug #216 (2021) and bug #353 (2023). These writes
SET the CIA timer values but the PSID play dispatch is still vblank (speed=0).
On hardware the CIA writes could corrupt the system IRQ timing.

Player code footprint: $1103 − $1006 = $FD = 253 bytes — **12 bytes smaller
than v2**, consistent with the changelog "roms are smaller" claim.

Register shadow array base: $04 (zero page + offset), size $19 (25 entries for
3 voices × 7 regs + $D418 master vol + extras). X counts down from $18.

#### v12 layout sub-clusters (from HVSC #84 survey)

| init addr | play addr | count | Notes |
|-----------|-----------|-------|-------|
| $1103 | $1006 | 112 | Standard: play at load start, init at end of player |
| $1000 | $1006 | 60  | Load at $1000; two JMPs at $1000/$1003 (init+play stubs), then player at $1006 |
| $1106 | $1000 | 60  | Load at $1000; play at $1000 (= load), init at $1106 |

All three sub-clusters contain the same v12 signature bytes and the same
X-indexed blit loop starting at the play address. The differences are in
the PSID header entries and whether the binary starts with jump-table stubs.
The "$1000 play=$1006" variant starts with `JMP $1103 / JMP $1006` at $1000–$1005
then the player body begins at $1006. The "$1106 play=$1000" variant places
the blit loop first at $1000, then init at $1106.

## 5. Write-Model Summary

All three variants are **vblank-driven, single-subtune, PSID v2** players.
None use CIA-timed PSID dispatch (speed=0 across 310/310 SIDs).

| Property | v1 | v2 | v12 |
|----------|----|----|-----|
| $D400 write method | Single-byte stream, X=reg index | Y-indexed shadow blit | X-indexed shadow blit (descending) |
| Per-frame blit direction | N/A (byte-at-a-time) | Y ascending (0→$18) | X descending ($18→0) |
| Shadow array ZP base | n/a | low-addr ZP | $04 (ZP) |
| CIA1 reads in player | none observed | yes (LDA $DC04/05 — read, likely seed) | yes (STA $DC04/05 — write, sets timer) |
| $D418 filter/vol handling | unknown (single SID) | included in blit | included in blit ($18 is $D418 offset) |
| Player code size (bytes) | ~113 estimated | ~265 | ~253 |
| Multi-subtune support | none | none | none (all single-subtune in HVSC) |
| PSID speed | 0 (vblank) | 0 (vblank) | 0 (vblank) |

## 6. Scene Reception and Tooling

### CSDb releases
- **DefleMask V0.09.0b** (CSDb #118363, 27 Apr 2013) — first CSDb entry; the 9b
  release with the rewritten C64 SID player ("new and better SID export").
- **DefleMask V0.12.0 Prerelease** (CSDb #148620, 28 May 2016)
- **DefleMask V0.12.0** (CSDb #148640, 3 Jun 2016) — the v12 player
- **DefleMask V0.12.1** (CSDb #187536, 2017)

CSDb pages return HTTP 503 at time of research; content not directly retrieved.

### Scene opinion
The C64 demoscene generally regards DefleMask SID exports as unsuitable for
genuine C64 production:

- **Lemon64 (2020, user "Tobias")**: "GT2 or Sidfactory is what you want to use...
  forget Deflemask, its useless for making tunes that should run on actual C64."
  Context: a developer found DefleMask SIDs too large (≥25 KB for basic songs)
  and incompatible with hardware.
- The C64 community criticism clusters around three issues:
  1. **File size**: DefleMask embeds the full song data uncompressed and includes
     DMF instrument/effect metadata in the SID. A bare song can be 2–54 KB;
     comparable tunes in GT2 or SIDFactory II are typically 2–8 KB.
  2. **CIA writes on hardware**: Bug #216 (2021) and #353 (2023) confirm that
     DefleMask-exported SIDs crash on real C64 hardware or VICE, writing outside
     permitted address ranges ($DC04–$DC05, $0001, $0103 per sidreloc). Delek
     confirmed a header fix (offset correction, 2025-05-27) but the CIA writes in
     the player body remain.
  3. **Not a native C64 tool**: DefleMask targets cross-platform chiptune users,
     not C64 sceners. Its sound model (per-instrument ADSR+wave+filter macros)
     maps to SID but not to the live-programming idioms of GT2/SIDFactory.
- DeepSID (Sep 2025) added a "D" focus icon for composers who primarily use
  DefleMask — indicating the collection is large enough to warrant its own UI marker.
- chordian.net comparison article (2018) added DefleMask 0.12.0 to the editor
  comparison table but noted no rasterline measurement was available; the article
  was subsequently discontinued in favour of the DeepSID editor list.

### VGM interop
Early DefleMask (v9, 2013) VGM exports were non-compliant: they used chip ID
0xC6 for C64 and omitted the SID clock field, breaking all VGM tools (reported
by ValleyBell on VGMRips, 2013). Delek acknowledged this and deferred to future
VGM spec updates.

### deflestream64 (chiptunecafe)
An alternative player for DefleMask SID tunes (GitHub: chiptunecafe/deflestream64)
uses VGM-streamed data off disk via Krill's Loader + Bitnax LZ compression — a
completely different architecture from the embedded player. No disassembly of the
original player is present in that repo.

## 7. DMF Format C64 Parameters (v1.0.0 spec, 0x18)

System IDs: `SYSTEM_C64 SID 8580 = 0x07`, `SYSTEM_C64 SID 6581 = 0x47`.
Both: 3 channels.

C64 instrument data (per-instrument in DMF): Triangle/Saw/Pulse/Noise wave enables;
Attack/Decay/Sustain/Release; Pulse Width; Ring Mod; Sync Mod; Filter routing;
Filter Resonance/Cutoff; High Pass/Low Pass; Filter CH2 Off;
Volume Macro→Filter Cutoff enable flag.

Earlier DMF format (0x15, DefleMask 11.1): SID 6581 was coded as `0x17` not `0x47`.
The `0x47` encoding appeared in format 0x18 (v1.0.0+).

## 8. Known Bugs and Hardware Compatibility

| Bug | Reporter/Date | Status |
|-----|---------------|--------|
| SID crashes on real C64 hardware (sidreloc: out-of-bounds writes to $0001, $DC04–$DC05) | anon, Aug 2021 (#216) | "Feedback" (unresolved as of Jan 2022); Delek asked if sidreloc fix helps |
| SID files don't load on real hardware or VICE (v1.1.7); sidreloc "No solution found" | anon, 2023 (#353) | Delek confirmed header fix 2025-05-27; body-level CIA writes unaddressed |
| Memory embedding causes crash when called from interrupt handler | Darrenor64, Nov 2021 | Workaround: use PSID64 wrapper |

## 9. Leads to Follow

1. **CSDb comment threads** for V0.09.0b (#118363), V0.12.0 (#148640), and V0.12.1
   (#187536) — not retrievable (HTTP 503 during research). May contain Delek
   commentary on player changes or community reaction. Retry on a future date.

2. **ChipMusic.org thread pages 23–25** — the "new and better SID export" quote
   for v9b was found in search snippets but the pages returned HTTP 403. The full
   post text (author, exact date, technical detail) is unconfirmed. Retry with
   a different client/VPN.

3. **v12 CIA write purpose** — `STA $DC04 / STA $DC05` in the v12 player: is this
   setting CIA1 timer A for a PAL lock, a melody-sync feature, or is it an
   unintended side-effect of the stream reader? Needs a full disassembly of the
   ~253-byte v12 player to determine the exact calling context and what value is
   written. A good starting point: Coral_Cavern.sid (Coral_Cavern = standard
   v12 layout, smallest of the init=$1103 cluster).

4. **v1 player full structure** — only one HVSC example (Green_Tea.sid, 51 KB).
   The byte-streaming architecture is structurally different from v2/v12. Full
   disassembly would clarify whether the SID register write sequence is equivalent
   or whether the stream encoding differs. Could explain why it never became common.

5. **Two pre-0.12 v12-tagged SIDs** — Schallwelle (2015) and Zlew (2015, one SID
   tagged v12) predate the June 2016 v0.12.0 release. Check if these used a
   pre-release build, a nightly, or were re-exported later.

6. **Delek's GitHub / delek.net** — search engine results for delek.net returned
   the legacy PDF manual but no blog or git source. No public DefleMask source
   repository found during this research sweep. If source becomes available the
   C64 player assembly source file would definitively resolve the v1/v2/v12
   structural questions.

7. **DeepSID editor list** — chordian.net blog notes that the C64 editor
   comparison table was moved to "the list of editors in DeepSID." The DeepSID
   /images/players/ subdirectory may contain DefleMask player/rasterline data.
   Retrieve via the DeepSID GitHub (Chordian/deepsid) if needed.

8. **Multiple-subtune support** — all 310 HVSC DefleMask SIDs are single-subtune.
   The forum post from Darrenor64 (2021) explicitly requested "multi-song
   compilation support" as a missing feature. Confirmed absent from the current
   PSID export.
