---
source_url:
  - "local: tmp/dmc_hunt/player-id/config/sidid.cfg (lines 761-762, 949-1005, 1139-1141, 2075-2081) — READ-ONLY"
  - "local: pipelines/jch_newplayer/docs/sidid_variant_taxonomy.md + deepsid_lineage_and_version_map.md + github_cheesecutter.md — READ-ONLY"
  - "upstream: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg (fetched via WebFetch 2026-06-14)"
  - "upstream: https://github.com/cadaver/sidid/blob/master/sidid.nfo (fetched via WebFetch 2026-06-14)"
  - "HVSC population: local hvsc84.db (mode=ro, query 2026-06-14)"
fetched_via: local READ-ONLY + WebFetch (cadaver/sidid GitHub, raw.githubusercontent.com) + WebSearch
fetch_date: 2026-06-14
author: synthesis by Claude (sidfinity research wave); underlying sidid.cfg by Cadaver / Wilfred Bos / DeepSID community; NP 21.G4 by Thomas Egeskov Petersen (Laxity/Vibrants); NP by JCH (Jens-Christian Huus)
content_date: sidid.cfg signatures cumulative ~1989-2020; NP 21.G4 beta CSDb #20112 dated 2005-08-27; CheeseCutter cc4.07 player ~2012; this doc 2026-06-14
reliability: PRIMARY for hex signatures (verbatim copy from two independent sidid.cfg sources that agree byte-for-byte); PRIMARY for HVSC population (direct READ-ONLY DB query); PRIMARY for NP 21 authorship (github_cheesecutter.md + CSDb); SECONDARY (inference, flagged) for sub-sig opcode readings
---

# Laxity_NewPlayer_V21 — SIDId Discrimination Document

How sidid distinguishes `Laxity_NewPlayer_V21` from `JCH_NewPlayer`,
`Vibrants/Laxity`, `Glover_NewPlayer_V21`, and `SidFactory_II/Laxity` in HVSC #84.

---

## 1. Background: the JCH NewPlayer lineage

The `JCH_NewPlayer` / `Laxity_NewPlayer_V21` / `Vibrants/Laxity` / `SidFactory_II/Laxity`
cluster all descend from Jens-Christian Huus's (JCH) NewPlayer — a modular C64 music
engine where different player binaries ("generations") can be merged into the same editor.
The taxonomy is:

| SIDId name | HVSC #84 count | player generation | author | notes |
|---|---|---|---|---|
| `JCH_NewPlayer` | 3611 | V1 … V20 | JCH (Vibrants) | Base + 17 sub-sigs; HVSC folds all into one label |
| `Laxity_NewPlayer_V21` | 313 | V21.G4 | Laxity (Vibrants/MoN) | 2005 beta (CSDb #20112); CheeseCutter is based on this |
| `Glover_NewPlayer_V21` | 67 | V21 fork | Lukasz Baran (Glover) | Same V21-era base, different author variant |
| `Vibrants/Laxity` | 179 | pre-V21 Laxity player | Laxity (Vibrants) | Distinct play-offset (+$06) and freq-write model |
| `SidFactory_II/Laxity` | 377 | SF2 (NP successor) | Laxity | Different engine / format; play at +$06 or +$09 |
| `SidFactory/Laxity` | 39 | SF1 | Laxity | Earlier SF |

Crucially: **`Laxity_NewPlayer_V21` is a TOP-LEVEL sidid signature**, not a sub-sig under
`JCH_NewPlayer`. SIDId treats V21 as a separate engine because Laxity rewrote enough of
the player that its distinctive routine shape no longer matched any of the
`(JCH_NewPlayer_V1)` … `(JCH_NewPlayer_V20)` sub-sigs. HVSC therefore emits the
distinct engine string `Laxity_NewPlayer_V21` (not `JCH_NewPlayer`) for these 313 tunes.

---

## 2. The exact sidid signature hex patterns

All signatures are taken verbatim from `tmp/dmc_hunt/player-id/config/sidid.cfg` and
cross-checked byte-for-byte against the upstream cadaver/sidid GitHub raw. They agree.

### 2a. `Laxity_NewPlayer_V21` (top-level — one line)

```
99 04 D4  BD ?? ??  C9 FF  F0 ??  4C ?? ??  DE ?? ??  BD ?? ??  D0 ??  4C
```

**Disassembly reading (inference — flagged):**

| bytes | mnemonic | interpretation |
|-------|----------|----------------|
| `99 04 D4` | `STA $D404,Y` | write voice control register (ctrl write to $D404 indexed by Y = voice) |
| `BD ?? ??` | `LDA abs,X` | load per-voice duration or note counter |
| `C9 FF` | `CMP #$FF` | compare to $FF = **sequence end sentinel** |
| `F0 ??` | `BEQ +N` | branch if end of sequence |
| `4C ?? ??` | `JMP abs` | jump (to next sequence advance or note read) |
| `DE ?? ??` | `DEC abs,X` | decrement per-voice duration counter |
| `BD ?? ??` | `LDA abs,X` | re-check counter |
| `D0 ??` | `BNE +N` | branch if not zero (note still held) |
| `4C` | `JMP` start of next opcode | continues to next-note fetch |

**What this pins down:** the V21 play core uses `STA $D404,Y` (ctrl write via Y-indexed
absolute) + a `CMP #$FF` end-of-sequence test + `DEC abs,X` duration decrement. These
three together are the distinctive V21 routine shape that graduated away from the V20
`CE / AD / 8D` framecounter layout.

**The `$D404` literal is the load-bearing anchor.** Convention: sidid wildcards addresses
(`??`) but keeps SID I/O literals. `04 D4` = voice-1 control ($D404) — confirms this is a
voice-ctrl write in the play routine, not the init.

### 2b. `JCH_NewPlayer` (base + sub-sigs — for contrast)

Four OR-ed base fingerprints, any one of which fires the top-level `JCH_NewPlayer` match:

```
; BASE LINE 1 — play-entry multispeed dispatch
4C ?? ?? 48 29 E0 C9 80 D0 ?? 68 48 29 10

; BASE LINE 2 — 3-voice state-table init loop (CPX #$03 = 3 voices)
A2 00 B9 ?? ?? 9D ?? ?? ?? ?? ?? B9 ?? ?? 9D ?? ?? ?? ?? ?? C8 C8 E8 E0 03 D0

; BASE LINE 3 — sequence-fetch core ($7E = gate-on-hold sentinel)
B1 ?? 30 ?? F0 ?? C9 7E F0

; BASE LINE 4 — wave/arp + master-vol = $0F write (A9 0F 8D = LDA #$0F; STA $D4xx)
AD ?? ?? F0 26 A2 03 B9 ?? ?? 3D ?? ?? 9D ?? ?? CA D0 F4 B9 ?? ?? 10 13 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? C8 C8 E8 E0 03 D0 ED A9 0F 8D
```

Key sub-sigs (verbatim):

```
(JCH_NewPlayer_V17)  — compact dispatch (NP 17.G0 generation):
A5 ?? 48 A5 ?? 48 A2 02 BD ?? ?? D0 03 4C ?? ?? BD ?? ?? D0 03 4C ?? ?? C9 02 F0 06 DE ?? ?? 4C

(JCH_NewPlayer_V20)  — framecall-counter generation (NP 20.G4 / 20.Q0):
48 A5 ?? 48 CE ?? ?? 10 1D AD ?? ?? 8D ?? ?? C9 02 B0 13 AC ?? ?? B9 ?? ?? 8D ?? ?? CE ?? ?? 10 05 A9

(JCH_NewPlayer_V0x)  — universal SID-reset init prologue (#$88 test preset, AND-skip to AD write):
98 99 00 D4 C8 C0 19 D0 F8 A9 88 8D 04 D4 8D 0B D4 8D 12 D4 A9 ?? 8D 05 D4 8D 0C D4 && 8D 13 D4 A9
```

Note: `(JCH_NewPlayer_V0x)` matches the **init routine** (zero $D400-$D418, `LDA #$88;
STA $D404/$D40B/$D412`). This is not a play generation — it is the hard-restart reset
prologue. Equivalent to our `init_style='universal_reset'` parametrisation (trichotomy-safe).

**Why `Laxity_NewPlayer_V21` is NOT caught by `JCH_NewPlayer`:** none of the four
JCH base lines (above) match V21's control-register write structure. SIDId's V21
signature instead keys on the `99 04 D4` + `C9 FF` + `DE abs,X` pattern which is absent
from the V20 and earlier routines. There is no overlap — a V21 binary hits exactly one
of the two top-level names, never both.

### 2c. `Glover_NewPlayer_V21` (top-level — one line)

```
B9 ?? ?? 85 ??  29 F0  C9 20  F0 ??  B0 ??  9D ?? ??  B9 ?? ??  9D ?? ??  A5 ?? 29 0F  9D ?? ??  A9 ?? 9D
```

**Disassembly reading (inference — flagged):**

| bytes | mnemonic | interpretation |
|-------|----------|----------------|
| `B9 ?? ??` | `LDA abs,Y` | load from table |
| `85 ??` | `STA zp` | store to zero-page (working register) |
| `29 F0` | `AND #$F0` | mask hi-nibble |
| `C9 20` | `CMP #$20` | compare to **$20 = super-table marker** |
| `F0 ??` | `BEQ` | if super-table entry |
| `B0 ??` | `BCS` | if >= $20 (other high-nibble marker) |
| `9D ?? ??` | `STA abs,X` | store to indexed voice slot |
| `B9 ?? ??` | `LDA abs,Y` | load second byte |
| `9D ?? ??` | `STA abs,X` | store second byte |
| `A5 ?? 29 0F` | `LDA zp; AND #$0F` | lo-nibble extraction |
| `9D ?? ??` | `STA abs,X` | store lo-nibble |
| `A9 ?? 9D` | `LDA #imm; STA abs,X` | store a literal immediate |

**What distinguishes Glover from Laxity V21:** Glover's signature is in the **super-table
command decode** — the `AND #$F0; CMP #$20` hi-nibble test is his variant's entry point into
the supertable dispatcher. Laxity's V21 signature keys on the **ctrl-register write +
duration decrement** (the note-play core). These are two different routines within the same
generational era — Glover forked the player and adjusted the super-table dispatch, but the
two players share the same V21-era overall architecture.

**Both are separate from `JCH_NewPlayer` in HVSC.** SIDId does not put Glover as a
sub-sig of Laxity or JCH; they are three independent top-level entries.

**Author:** Lukasz Baran (Glover), per sidid.nfo.

### 2d. `Vibrants/Laxity` (five OR-ed lines)

```
; LINE 1 — 16-bit freq write via table (ADC + TAY + STA $D401 + STA $D400)
18 7D ?? ?? 0A A8 B9 ?? ?? 48 B9 ?? ?? AC ?? ?? 99 01 D4 68 99 00 D4

; LINE 2 — voice ctrl write + sequence advance
FE ?? ?? BD ?? ?? 99 04 D4 4C ?? ?? BD ?? ?? 29 ?? F0 ?? A9 ?? 99 04 D4

; LINE 3 — timer/speed init (CE loop × 4 counters, then AD/8D)
A9 ?? 8D ?? ?? 60 A2 ?? CE ?? ?? 10 ?? CE ?? ?? CE ?? ?? CE ?? ?? AD ?? ?? 8D

; LINE 4 — command dispatch with nibble extraction
C9 ?? B0 ?? 29 ?? 48 A9 ?? 9D ?? ?? 68 0A 0A 9D ?? ?? 4C ?? ?? 29

; LINE 5 — filter write via add ($D416)
AD ?? ?? 18 79 ?? ?? 8D ?? ?? 8D 16 D4 2C ?? ?? 70 ?? D9 ?? ?? 90
```

**Key discriminators vs Laxity_NewPlayer_V21:**

- Line 1: `ADC abs,X; ASL; TAY; LDA tbl,Y; PHA; LDA tbl,Y; LDY abs; STA $D401; PLA; STA $D400`
  — a **16-bit frequency table lookup with stack-separated hi/lo** that writes $D401 then
  $D400. This is an OLDER Laxity freq-write model; V21 does not have this pattern.
- Line 5: `18 79 … 8D 16 D4` — an **explicit `STA $D416`** (filter cutoff high / volume)
  write via `ADC abs,Y`. The `16 D4` literal is load-bearing; V21's main sig has `04 D4`.
- **Play offset**: `Vibrants/Laxity` standard init=$1000, play=$1006 (note +$06, not +$03).
  `Laxity_NewPlayer_V21` uses play=$1003 (same as JCH). The +$06 offset implies a 6-byte
  jump table (init/play/mplay) vs the 4-byte (init/play + no mplay or sync) implied by +$03.

### 2e. `SidFactory_II/Laxity` (two-fragment signature with `&&`)

```
C8 B1 ?? C9 FF D0 04 C8 B1 ?? A8 98  &&  C9 7E F0 ?? 18
```

The `&&` is a gap: these two fragments must occur separated by an arbitrary number of
bytes, both present. Reading:

| fragment | bytes | interpretation |
|---|---|---|
| first | `C8 B1 ?? C9 FF D0 04 C8 B1 ?? A8 98` | `INY; LDA(ptr),Y; CMP #$FF; BNE +4; INY; LDA(ptr),Y; TAY; TYA` — double-indirect sequence read with `$FF` end sentinel; double-`INY` pattern |
| second | `C9 7E F0 ?? 18` | `CMP #$7E; BEQ; CLC` — `$7E` = the NP gate-on-hold sentinel, same invariant as the JCH base sig line 3 |

SF2 is the **SidFactory II** editor (Laxity's modern successor to JCH Editor). It has its
own distinct format (.dat) and a `converter_jch` to import old JCH .dat files. SIDId
gives it a separate name; HVSC treats it as a separate engine (377 SIDs). Standard play
offset in HVSC: play=$1006 (64%) or $1009 (7%).

---

## 3. What the `_V21` suffix detection keys on

The `_V21` in `Laxity_NewPlayer_V21` is **NOT keyed on a version string** in the binary,
**NOT a relocation address**, and **NOT an init sequence**. It is keyed on a specific
**play-routine shape** — the `STA $D404,Y` + `CMP #$FF` + `DEC abs,X` sequence that is
structurally distinctive of Laxity's V21 player rewrite.

Summary of discriminating dimensions:

| dimension | `JCH_NewPlayer` | `Laxity_NewPlayer_V21` | `Glover_NewPlayer_V21` |
|---|---|---|---|
| sidid match type | base (4 OR-lines) + 17 sub-sigs | top-level (1 line) | top-level (1 line) |
| key anchor byte | `C9 7E` ($7E sentinel), `A9 0F 8D` ($D418=$0F), `E0 03` (CPX #$03) | `99 04 D4` ($D404,Y), `C9 FF` ($FF end), `DE` (DEC dur) | `29 F0 C9 20` ($20 super-marker test), `29 0F` (lo-nibble) |
| SID register literals | `$D400`–`$D418` (various) | `$D404` | none (all wildcarded) |
| play offset (canonical) | $1003 | $1003 | $1003 |
| authorship | JCH (Jens-Christian Huus) | Laxity (Thomas Egeskov Petersen) | Glover (Lukasz Baran) |
| HVSC count | 3611 | 313 | 67 |

**The `_V21` is a community label** applied by the SIDId author (Cadaver) to distinguish
Laxity's V21-era player from JCH's earlier generations. There is no V21 byte embedded in
the binary (the sig does not key on any version-number register or string).

---

## 4. HVSC #84 population survey — `Laxity_NewPlayer_V21` (313 SIDs)

All data from `hvsc84.db` (mode=ro query, 2026-06-14).

### 4a. Load / init / play addresses

| load | init | play | count | fraction |
|------|------|------|-------|---------|
| $0000 | $1000 | $1003 | 289 | 92.3% |
| $0000 | $9000 | $9003 | 4 | 1.3% |
| $0000 | $5000 | $5003 | 3 | 1.0% |
| $0000 | $A000 | $A003 | 3 | 1.0% |
| $0000 | $4000 | $4003 | 2 | 0.6% |
| $0000 | $E000 | $E003 | 2 | 0.6% |
| misc (8 single-SID variants) | various | various | 10 | 3.2% |

**Notable:** all 313 have `load_addr=$0000` (PSID 2-byte prefix = load from PSID header),
and all canonical entries follow the NP standard convention init=base, play=base+$03.
The play=base+$03 (not +$06) confirms V21 has the same 3-entry table as JCH_NewPlayer
(init, play, mplay at +$00/$03/$06 where mplay is addressed internally, not as a PSID
`play` header field).

The 8 misc variants have unusual bases ($0800/$0810/$0900/$0A00/$3000/$6000/$7000/$8000/
$AC00/$ED00), suggesting one-off packed/relocated modules. The $0810 entry has play=$0000
(no play vector set — init-only or ROM-dependent).

### 4b. Subtune distribution

| n_subtunes | count | notes |
|---|---|---|
| 1 | 307 | 98.1% — overwhelmingly single-subtune |
| 2 | 4 | |
| 4 | 1 | |
| 6 | 1 | |

**Contrast:** `JCH_NewPlayer` has 186 multi-subtune entries (~5.1%) vs V21's 6 (~1.9%).
V21 is predominantly used for single-song compositions.

### 4c. Songlength distribution

```
min = 5.0 s    max = 764.0 s    mean = 129.8 s    n = 313    no_length = 0
```

All 313 have a songlength in HVSC. Mean ~2 min 10 s. Range is wide (5 s to ~12.7 min).
The low minimum may reflect very short jingles or intro music.

### 4d. PSID format

- 312/313: `is_psid=1, psid_version=2` (standard PSID v2)
- 1/313: `is_psid=0, psid_version=2` (RSID — real SID, requires full C64 environment)

The HVSC taxonomy doc previously noted "1 RSID" — confirmed.

**No `speed` field in hvsc84.db** — the CIA-timed (multispeed) fraction cannot be
directly queried from the DB. A PSID `speed` word field would need to be parsed from
the raw SID header. The taxonomy doc's earlier note ("6 multi-subtune, 1 RSID") is
consistent; CIA multispeed status is not currently indexed.

### 4e. Top authors

| count | author |
|---|---|
| 166 | Thomas Mogensen (DRAX) |
| 92 | Gerhard Flagge (G-Fellow) |
| 7 | Torben Hansen (Metal) |
| 7 | Marcin Romanowski (Sidder) |
| 6 | Timo Taipalus (Abaddon) |
| 6 | Ronny Engmann (dalezy) |
| 6 | Alexander Rotzsch (Fanta) |
| 4 | Thomas E. Petersen (Laxity) — the engine's own author |
| 4 | Nick Vivid |
| 3 | Gerard Hultink |

**DRAX + G-Fellow account for 83% of the corpus (258/313).** This is a tight author
concentration — V21 was the preferred tool of a small circle. Laxity himself authored
only 4 of the 313 tunes in HVSC tagged as his engine (consistent with him building the
engine for others to use).

---

## 5. `Glover_NewPlayer_V21` population survey (67 SIDs)

### Load / init / play

| load | init | play | count |
|------|------|------|-------|
| $0000 | $1000 | $1003 | 64 (95.5%) |
| $0000 | $1AC0 | $1003 | 1 |
| $0000 | $24B2 | $24C5 | 1 |
| $0000 | $A000 | $A003 | 1 |

Almost all at the canonical $1000 base. All 67 are single-subtune (n_subtunes=1 for all).
**No multi-subtune, no RSID.** Glover tunes are single-song only.

The one entry with init=$1AC0/play=$1003 (init ≠ play base) is unusual — possibly a
relocated module where init is a separate initialiser at a different address.

---

## 6. `Vibrants/Laxity` population context (179 SIDs)

The **+$06 play offset** (play=base+$06 for 89+52+4=145 entries = 81%) is the most
reliable layout discriminator vs both V21 and JCH_NewPlayer (both use +$03). The 4
entries with play=$1003 alongside init=$1000 are potentially mis-tagged or are a build
variant that happens to match the Vibrants/Laxity signature despite using the +$03 table.

Subtune distribution is much more varied than V21: 10 multi-subtune entries (20/22/10/7/6
/5/4/3 subtunes represented) — Vibrants-era tunes were more commonly multi-subtune.

---

## 7. Relationship summary: discrimination rules

1. **`JCH_NewPlayer` (3611):** fires if ANY of the 4 base lines OR any of the 17 sub-sigs
   match. V-number versions (V1..V20) only distinguishable by SIDId sub-sig, not by HVSC label.

2. **`Laxity_NewPlayer_V21` (313):** one line, keys on `99 04 D4` + `C9 FF` + `DE`. Not a
   sub-sig of JCH — completely independent top-level. Play at init+$03. Authored by Laxity.

3. **`Glover_NewPlayer_V21` (67):** one line, keys on `29 F0 C9 20` super-table dispatch.
   Same V21-era but different routine fingerprint. Play at init+$03. Author: Glover.

4. **`Vibrants/Laxity` (179):** five OR-lines, keyed on freq-write (`$D401/$D400`) and
   filter (`$D416`) literal SID addresses plus 16-bit freq-table pattern. Older Laxity
   engine, play at init+$06.

5. **`SidFactory_II/Laxity` (377):** `&&`-gapped double-indirect `(ptr),Y` + `$7E` sentinel.
   Modern engine, play at +$06 or +$09. Separate format.

6. **No overlap:** each top-level name is an independent signature. SIDId reports exactly
   one match per binary from this cluster.

---

## 8. CheeseCutter connection

CheeseCutter (GPL, by Abaddon/Timo Taipalus) explicitly labels its player:
`"Based on JCH NP 21.G4 by Laxity/VIB"` (src/c64/player_v4.acme header).
CheeseCutter exports tunes at BASEADDRESS=$1000 with the same init/play/mplay table
(+$00/+$03/+$06). CheeseCutter tunes would match `Laxity_NewPlayer_V21` in SIDId if
their player binary contains the V21 signature bytes — Timo Taipalus (Abaddon) appears
in the V21 top-6 author list with 6 tunes, consistent with this.

CheeseCutter's player is identified in its own packed SIDs by the version string `"cc4.07"`
stored at editor-layout +$FEE (same slot used by JCH NP 20.gX). This string is an
INTERNAL identifier — not what SIDId keys on. SIDId identifies the output SID by its
play-routine shape, not by version strings.

---

## Leads to follow

- **PSID `speed` bit parse:** hvsc84.db does not store the per-subtune CIA/VBI speed flag.
  To measure the multispeed fraction of V21 tunes, add a `psid_speed` column populated
  from `struct.unpack_from('>I', data, 0x12)` (PSID header offset $12 = speed word).
  The DMC + Human_Race migrations both had CIA-timed tunes; V21 likely has some too.

- **Sub-sig population for `JCH_NewPlayer`:** the 3611 `JCH_NewPlayer` SIDs are not split
  by version in HVSC. To sequence the migration, run SIDId locally (player-id binary +
  sidid.cfg) over all 3611 to get V1..V20 population histogram. V20 (NP 20.G4/Q0) is
  expected to dominate (the "most-known" versions per community sources); V17.G0 is the
  second candidate.

- **Verify Glover `init=$1AC0 / play=$1003` anomaly:** the one Glover_NewPlayer_V21 entry
  where init ≠ play-base suggests an unusual packed module. Confirm whether this is a
  legitimate Glover fork variant or a mis-tag.

- **NP 22–25 coverage gap:** no SIDId sub-sig exists for generations past V21. If NP 22–25
  tunes exist in HVSC they are either caught by the V21 signature (shared core routine) or
  fold into `SidFactory_II/Laxity`. No separate signature in the local or upstream config.

- **`SidFactory_II/Laxity` format:** SF2 is Laxity's modern successor. Its 377 SIDs and
  the +$06/+$09 play offsets suggest a different header layout. SF2's .dat format has a
  `converter_jch` to import old JCH .dat — if V21 migration is done via the JCH composer,
  SF2 would need a separate extract path.

- **Vibrants/Laxity +$03 entries (4 SIDs):** 4 Vibrants/Laxity tunes have play=+$03
  instead of the canonical +$06. Confirm whether these are a genuine layout variant or
  a SIDId mis-identification (a V21-era tune that also happens to match the Vibrants sig).

- **`(JCH_NewPlayer_V0x)` init sig = our `init_style='universal_reset'`:** the V0x
  sub-sig fingerprints the NP hard-restart init prologue (`#$88` test-bit preset, zero all
  $D400-$D418). This maps directly to our existing `universal_reset` parametrisation +
  trichotomy comparator path. Confirm empirically on a V21 tune before assuming.
