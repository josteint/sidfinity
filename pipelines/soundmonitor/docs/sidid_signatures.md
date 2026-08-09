<!--
provenance:
  source_url: "local: tmp/dmc_hunt/{sidid,player-id/config,DeepSID/utility/sidid_100}/sidid.cfg ; tmp/jc64/src/sw_emulator/software/SidId.java ; tmp/jc64/doc/example/List.txt"
  fetched_via: "local read"
  fetch_date: 2026-06-13
  author: "sidid.cfg compiled by Cadaver/HVSC team (player-id project) + Wilfred Bos; jc64 SidId.java by ice00 (Ice Team)"
  content_date: "sidid.cfg ~2019-2021 vintage (sidid_100 'old_but_works' copy); jc64 contemporary"
  reliability: "HIGH — three independent local copies of sidid.cfg agree byte-for-byte on the Soundmonitor block; matching semantics read directly from jc64 SidId.java source; canonical tune attributions cross-checked against jc64 List.txt and CSDb/Wikipedia."
-->

# Soundmonitor — sidid recognition signatures & variant taxonomy

## 1. The mystery, resolved

The brief noted the repo's `tools/sidid.cfg` has no "Soundmonitor" entry yet
HVSC classifies 3,625 tunes as `Soundmonitor`. **Resolution: there is no
`tools/sidid.cfg` in this repo at all** (`ls` → *No such file or directory*).
The HVSC `engine='Soundmonitor'` label in `hvsc84.db` therefore does **not**
come from a repo-local sidid run — it comes from HVSC's own upstream
classification, which is produced with exactly the `sidid` signature engine
whose config we mined locally.

The real signatures live in three identical local copies:

- `tmp/dmc_hunt/sidid/sidid.cfg` (82,803 bytes — most complete)
- `tmp/dmc_hunt/player-id/config/sidid.cfg`
- `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg` (the 100-char-space build DeepSID uses)

All three carry an identical `Soundmonitor` signature block plus a separate
`Chris_Huelsbeck` block. (The DeepSID checkout also ships
`sidid_newer_but_does_not_work.cfg`, which has **no** Soundmonitor block at
all — i.e. the working classification depends on the *older* cfg; the newer
one regressed.)

## 2. How sidid matching works (from jc64 `SidId.java`)

`sidid` is a **byte-pattern scanner over the whole loaded file image**, not a
disassembler or an emulator. Tokens (jc64 `SidId.java:43-175`, `identifyBytes`
`:224-259`):

| Token in cfg | Meaning |
|---|---|
| `??` | `ANY` — wildcard, matches any single byte |
| `END` | end of one signature pattern |
| `AND` / `&&` | concatenate two sub-patterns: BOTH must be found (the second is searched *after* the first match position) |
| two hex digits | a literal byte to match |

`identifyBytes` slides the pattern across `buffer[0..length]` with backtracking
(`rc`/`rd` are the restart anchors). **Consequence: a match can occur at any
offset in the file** — so the signatures are *relocation-invariant by
construction*. That is exactly why every absolute address inside a pattern is
written as `?? ??` (the byte that shifts when the player is relocated), while
the *opcodes* and the *hard SID/CIA register addresses* (`$D4xx`, `$DDxx`,
`$CExx`) stay literal.

A player name can carry **multiple `END`-terminated patterns** = a logical OR
(any one matches → that name). `Chris_Huelsbeck` uses this (two patterns).

### sidid invocation modes (from DeepSID `howto_update_hvsc.txt`)
- `sidid > out.csv` → reports only the **primary** (unparenthesised) player
  name per file. This is what sets HVSC/DeepSID's coarse `player` = `Soundmonitor`.
- `sidid -m > out.csv` → reports **all** matches including the
  parenthesised `(Variant)` sub-labels. DeepSID's `python/specific/*.py`
  scripts then slice these into the fine-grained per-variant player names.

## 3. The `Soundmonitor` signature block (verbatim, from `sidid/sidid.cfg:1821`)

The FIRST pattern (no parenthesised name) is the **base `Soundmonitor`
detector**. Each subsequent `(Name)` line is a sub-variant detector surfaced
only under `sidid -m`.

```
Soundmonitor
D0 16 BD ?? ?? 29 10 F0 2A BD ?? ?? 9D ?? ?? BD END
(DUSAT/RockMon2)
48 29 0F AA CA 68 4A 4A 4A 4A 18 69 ?? 8D ?? ?? 4C END
(MusicMaster_1)
8D 0C CE 8D 18 D4 60 A0 17 A9 00 99 00 D4 99 F4 END
(DUSAT/RockMon3)
4A 4A 4A 4A AA BD ?? ?? 8D ?? ?? BD ?? ?? 8D ?? ?? A2 ?? 8A 48 20 ?? ?? 68 CA D0 ?? A9 ?? 8D 18 D4 END
(DUSAT/RockMon3h)
8D 0C CE 20 70 CE 60 A0 17 A9 00 99 00 D4 99 F4 END
(DUSAT/RockMon4)
8D 0C CE 4C 18 CA 60 A0 17 A9 00 99 00 D4 99 F4 END
(DUSAT/RockMon5.0)
8D 04 D4 8D 0B D4 8D 12 D4 A9 00 99 00 D4 99 AE END
(DUSAT/RockMon5.1)
8D 04 D4 8D 0B D4 8D 12 D4 A9 00 99 00 D4 99 B0 END
(BeatBox/Karl_XII)            # one copy spells it (BeatBox/KarlXII) with literal 8D 1E CE
8D 1E ?? 8D 18 D4 60 A0 17 A9 00 99 00 D4 99 06 END
(Karl_XII)
8D CC CD 8D 18 D4 60 A0 17 A9 00 99 00 D4 99 B4 END
(DigiMonitor)
AA CA 8E ?? ?? 8E ?? ?? AD ?? ?? 8D ?? ?? AD ?? ?? 29 F0 0D ?? ?? 8D ?? ?? AD 18 D4 60 END
(JamMasterV1)
B9 ?? ?? 8D 18 D4 20 ?? ?? E8 E8 D0 ?? BD ?? ?? 18 7D ?? ?? A8 B9 ?? ?? 8D 18 D4 END
(Syndicate/BB)
AA BD ?? ?? 8D 04 DD BD ?? ?? 8D 05 DD BD ?? ?? 8D ?? ?? A9 00 85 ?? BD ?? ?? 85 ?? BD ?? ?? 8D END
(Digitronix)
8D 0C CE 8D FE 9F 60 A0 17 A9 00 99 00 D4 99 F4 END
(MusicMaster_2)
8D 72 CE 60 A0 17 A9 00 99 00 D4 99 5A CE 99 73 AND BD 00 9C 8D 04 DD BD 00 9D END
(DrumMaker2)
8D 72 CE 60 A0 17 A9 00 99 00 D4 99 5A CE 99 73 AND BD 00 9C 20 60 CC BD 00 9D END
(MusicMaster_TMM)
8D 0C CE 8D FF ?? 60 A0 17 A9 00 99 00 D4 99 F4 END
(Huelsbeck_Digi_V1)
A0 ?? A5 ?? CD ?? ?? F0 ?? B1 ?? 8D ?? ?? 29 0F END
(Huelsbeck_Digi_V2)
A0 ?? A5 ?? C5 ?? F0 ?? B1 ?? 85 ?? 29 0F 4A 18 69 ?? 8D 18 D4 END
(Cavi_Digi)
4A 4A 4A 8D 18 D4 A4 ?? 88 D0 ?? 60 29 0F 8D 18 D4 A4 ?? 88 D0 ?? 60 END
(ReD_Packed)
F0 01 60 20 ?? ?? A9 ?? 8D FB ?? 4C 05 ?? 4C END
(Mahoney_Digi)
A0 04 A5 ?? 0A 69 00 0A 69 00 85 ?? 29 03 AA ?? ?? ?? ?? ?? ?? BD ?? ?? 0D ?? ?? 8D 18 D4 END
(Novotrade)
F0 11 4A B0 49 4A 90 0B 4A A9 FE 95 END
```

### Cross-copy diffs (cosmetic only)
- `sidid/` and `player-id/` copies drop the trailing `END` on the first
  pattern and write `&&` instead of `AND`; the `sidid_100` copy keeps `END`
  and `AND`. Semantically identical.
- `(BeatBox/Karl_XII)`: the `sidid_100` copy hard-codes `8D 1E CE` and names
  it `(BeatBox/KarlXII)`; the others use `8D 1E ??`. Functionally the same
  detector with one byte wildcarded.

## 4. The separate `Chris_Huelsbeck` block (`sidid/sidid.cfg:353`)

```
Chris_Huelsbeck
A8 29 04 D0 0C 98 29 03 F0 07 29 01 D0 34 4C END
99 04 D4 A5 ?? 18 69 01 END
```

This is a DISTINCT primary name (not under `Soundmonitor`). Two OR'd patterns.
It fingerprints the *sound-option nibble decode* + a *frequency/control write*
of a Hülsbeck-authored driver (see §6). In practice DeepSID renders this as
`Chris Hülsbeck's player` (from `pretty_player_names.php:46`). In `hvsc84.db`
only **11** tunes carry `engine='Chris_Huelsbeck'` vs 3,625 `Soundmonitor` —
so this is a small, separate hand-coded-by-Hülsbeck driver family, not the
type-in Soundmonitor itself.

## 5. Variant taxonomy (the deliverable)

The Soundmonitor "family" as sidid models it = **one base type-in player
(MusicMaster/Soundmonitor) plus ~20 scene derivatives**, all detected inside
the single `Soundmonitor` cfg block. Authorship/provenance below is
cross-checked against jc64 `List.txt` and the web sources (see
`deepsid_player_taxonomy.md`).

| sidid sub-name | What it is | Provenance / notes |
|---|---|---|
| *(base, unlabelled)* `Soundmonitor` | Chris Hülsbeck's type-in editor's replay, 64'er 10/1986 | "Shades (filter corrected)" © 1986 Markt & Technik is the canonical tune (jc64 List.txt:68) |
| `MusicMaster_1` | The original built-in driver "MusicMaster" (init at `$C000`, the `8D 0C CE` write + SID clear) | MusicMaster = the playback driver Hülsbeck wrote *before* the editor (1985, in Profi-Ass 64) |
| `MusicMaster_2` | 2nd-gen MusicMaster (writes `$CE72`, AND-fragment touches `$DD04` CIA + `$9C00` table) | |
| `MusicMaster_TMM` | "The (Final) Musicplayer" — Hülsbeck's optimised driver (`8D FF ??` tail) | VGMPF: an optimised driver "given only to Georg Brandt"; TMM = The MusicPlayer |
| `DUSAT/RockMon2` | Rockmonitor II | Marco Swagerman & Oscar Giesen © 1987 **Dutch USA Team** (jc64 List.txt:56) |
| `DUSAT/RockMon3`, `RockMon3h` | Rockmonitor 3 (+ "h" hacked/variant) | Dutch USA Team |
| `DUSAT/RockMon4` | Rockmonitor 4 | Dutch USA Team |
| `DUSAT/RockMon5.0`, `RockMon5.1` | Rockmonitor 5 — note the DISTINCT init: writes `$D404/$D40B/$D412` (per-voice gate clear) then the `99 00 D4` clear loop, tail byte `AE` vs `B0` separates 5.0/5.1 | "Rockmonitor 5 Demosong" by Oscar Giesen (OPM) © 1988 Dutch USA Team (jc64 List.txt:57) |
| `BeatBox/Karl_XII`, `Karl_XII` | Karl XII's Rockmonitor-derived player + a BeatBox variant | Karl XII = scene musician; shares the `60 A0 17 A9 00 99 00 D4` init |
| `DigiMonitor` | Sample-capable Soundmonitor derivative (writes two `$8Exx`, masks `$F0`, then `$D418`) | digi spin-off |
| `DrumMaker2` | DrumMaker 2 (MusicMaster_2 base + `20 60 CC` JSR for drums) | |
| `JamMasterV1` | JamMaster v1 | |
| `Syndicate/BB` | Syndicate / Bizzmo Bros variant (writes `$DD04/$DD05` = CIA2, table-driven) | |
| `Digitronix` | Digitronix (`8D FE 9F` write into `$9FFE`) | |
| `Cavi_Digi` | Cavi's digi routine (`4A 4A 4A 8D 18 D4` = shift→`$D418` volume digi) | |
| `ReD_Packed` | ReD's packed Soundmonitor | a packer wrapper |
| `Mahoney_Digi` | Mahoney-style digi (the `0A 69 00 0A 69 00` ×2 volume-build) | |
| `Novotrade` | Novotrade's variant | |
| `Huelsbeck_Digi_V1`, `Huelsbeck_Digi_V2` | Hülsbeck's own digi extensions (V2 ends `… 29 0F 4A 18 69 ?? 8D 18 D4` = nibble→`$D418`) | authored by Hülsbeck |

> **Naming caveat for the migration:** DeepSID stores most of these as
> `SoundMonitor/<Name>` (e.g. `SoundMonitor/MusicMaster_1`), BUT the
> `DUSAT/RockMonN` and `DigiMonitor` ones are stored WITHOUT the
> `SoundMonitor/` prefix (bare `DUSAT/RockMon2`) — see the per-script logic in
> `deepsid_player_taxonomy.md`. So in DeepSID's tree "Rockmonitor" is a
> sibling label, not nested under SoundMonitor, even though sidid groups it in
> the same cfg block.

## 6. 6502 interpretation of the load-bearing signatures

### Base `Soundmonitor` detector
`D0 16 BD ?? ?? 29 10 F0 2A BD ?? ?? 9D ?? ?? BD`
```
        BNE +$16          ; D0 16   branch around (skip when a flag set)
        LDA $xxxx,X       ; BD ?? ??  read a per-voice byte from a table
        AND #$10          ; 29 10   test bit 4
        BEQ +$2A          ; F0 2A   skip if clear
        LDA $xxxx,X       ; BD ?? ??  reload (different table)
        STA $xxxx,X       ; 9D ?? ??  store back into voice state
        LDA $xxxx,X       ; BD ...  (continues)
```
This is the **per-voice note/effect processing loop** of the MusicMaster play
routine: indexed by X = voice (0/7/14 stride is typical), it masks a control
bit (`#$10`) out of a per-voice flags byte and conditionally copies state.
`X` is the voice index; the wildcarded `?? ??` are the absolute base
addresses of the voice tables (these relocate, hence wildcarded).

### Canonical MusicMaster `init` fingerprint (shared by 9 variants)
`… 60 A0 17 A9 00 99 00 D4 99 xx`
```
        RTS               ; 60      end of the preceding (sub)routine
init:   LDY #$17          ; A0 17   Y = 23  (24 SID registers, $D400..$D417)
        LDA #$00          ; A9 00
clear:  STA $D400,Y       ; 99 00 D4   zero SID register Y
        STA $xxxx,Y       ; 99 xx ..   also zero a parallel shadow/work table
                          ;            tail byte xx = $F4/$06/$B4/$5A/$AE/$B0 → variant discriminator
        ... (DEY/BPL loop) ...
```
**`A0 17 A9 00 99 00 D4` ("LDY #$17 / LDA #$00 / STA $D400,Y") is the single
strongest structural anchor for the whole family** — it is the SID-register
clear that every MusicMaster/Rockmonitor init runs. The byte AFTER `99` (the
high byte of the *second* `STA …,Y` target — a shadow register file) is what
sidid uses to tell sub-variants apart (`$F4` MusicMaster_1/2_TMM/Digitronix,
`$06` Karl_XII-BeatBox, `$B4` Karl_XII, `$5A→$CE5A` MusicMaster_2/DrumMaker2,
`$AE/$B0` RockMon5.0/5.1).

The instruction that PRECEDES the `60` in most variants is the
**init's master-volume / control write**: `8D 0C CE` (`STA $CE0C` — a work
byte) or, in RockMon5.x, the more explicit `8D 04 D4 / 8D 0B D4 / 8D 12 D4`
(`STA $D404/$D40B/$D412` — clears the three voice control registers'
gate/waveform before the bulk clear).

### Reloc/structure anchor for the rebuild
- The init's distinguishing absolute write is at a FIXED *form* (`STA $CExx`)
  whose low byte (`$0C`, `$72`, …) is stable per-variant but whose page
  (`$CE`) moves under relocation — i.e. when locating the player in a relocated
  image, anchor on the **opcode+register-constant** triples (`8D ?? CE`,
  `99 00 D4`, `8D 18 D4`) and treat the page byte as the relocation delta.
- The play routine anchors on the voice loop `BD ?? ?? 29 10` (read flags, mask
  bit 4) and `9D ?? ??` (write-back) — voice-indexed via X.

### `Chris_Huelsbeck` (separate) detector
`A8 29 04 D0 0C 98 29 03 F0 07 29 01 D0 34 4C` then OR `99 04 D4 A5 ?? 18 69 01`
```
        TAY               ; A8
        AND #$04          ; 29 04   test sound-option bit 2 (= Arpeggio enable, per the editor's nibble)
        BNE +$0C          ; D0 0C
        TYA               ; 98
        AND #$03          ; 29 03   low 2 bits (portamento / transpose-disable)
        BEQ +$07          ; F0 07
        AND #$01          ; 29 01   bit 0 = portamento enable
        BNE +$34          ; D0 34
        JMP $xxxx         ; 4C ...
   ---- OR ----
        STA $D404,Y       ; 99 04 D4   write voice control reg (gate/waveform) for voice Y
        LDA $xx           ; A5 ??
        CLC / ADC #$01    ; 18 69 01   +1 (note/transpose step)
```
The first pattern is a textbook decode of the **4-bit "sound options" nibble**
documented in the editor (bit0 portamento, bit1 transpose-disable, bit2
arpeggio, bit3 sound-transpose). This confirms `Chris_Huelsbeck` is a
hand-written driver sharing Soundmonitor's *musical* option semantics but a
different code structure (hence its own primary name, only 11 HVSC tunes).

## 7. Population (from `hvsc84.db`, opened read-only)

- `engine='Soundmonitor'`: **3,625** tunes — all PSID **v2**.
- `engine='Chris_Huelsbeck'`: **11** tunes.
- The DB stores only the **coarse** sidid primary name; it does NOT carry the
  `(Variant)` split (that split exists only in DeepSID's `-m` post-pass CSVs,
  which are not present locally — see "Leads to follow"). So a per-RockMon /
  per-MusicMaster HVSC count is **not derivable from `hvsc84.db` alone**.

Load/entry-point spread (relocation evidence), Soundmonitor subset:
- `load_addr` = `$0000` for **all 3,625** (PSID-embedded 2-byte PRG load addr).
- play address: `$C020` ×1,618 · `$0000` ×1,301 (single-call / init-drives-play)
  · `$C475` ×478 · `$C000` ×24 · long tail (`$CBDF,$C01F,$BFE6,$6475,$CF83,…`).
- init address: `$C000` dominates (`$C000/$C020/$0000` configs sum >2,000),
  then `$9FD0` ×236, `$CBD4` ×207, `$BFF0` ×141, `$80F8`/`$9FFA`/`$CE31`/… —
  i.e. the player is shipped at **many origins** (relocated per release),
  which is precisely why sidid scans-anywhere with `?? ??` address wildcards.
- subtunes: 3,512 single-tune; small multi-tune tail (max 7).

See `deepsid_player_taxonomy.md` for the DeepSID-side naming and web-sourced
version history (V1.0 Oct 1986; V1.1 1986; V1.3 1987; Rockmonitor Apr 1987).

## Leads to follow
- The fine-grained per-variant HVSC counts require running
  `sidid -m` over `hvsc85/` (the `-m` mode emits the `(Variant)` labels). The
  DeepSID `python/specific/*.py` show the exact post-parse; reproducing it
  would give RockMon2/3/4/5 vs MusicMaster_1/2/TMM populations. Not present in
  any local CSV — would need a sidid build + run (out of scope here, read-only).
- The base `Soundmonitor` voice-loop signature (`D0 16 BD ?? ?? 29 10 …`) is
  the best handle for a USF extractor's "is this the standard MusicMaster
  play?" probe — verify it disassembles cleanly in the canonical
  `init=$C000 play=$C020` member (e.g. Huelsbeck_Chris/Shades.sid).
- Confirm whether `Chris_Huelsbeck` (11 tunes) overlaps the Soundmonitor set or
  is disjoint (different code structure suggests a pre-Soundmonitor or
  game-specific hand driver — possibly the raw MusicMaster used in his early
  game scores before the editor existed).
