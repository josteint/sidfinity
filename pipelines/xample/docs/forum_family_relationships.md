# X-Ample / Compotech — Family Relationships

**source_url:** Various (CSDb, sidid.nfo, VGMPF, c64-wiki.de, Remix64, HVSC DB)
**fetched_via:** WebFetch + WebSearch + local DB query
**fetch_date:** 2026-06-13
**reliability:** secondary synthesis; primary sources cited inline

---

## Summary answer: one engine, multiple editor front-ends and player forks

The X-Ample family is **one music engine** (Schneider's player, ~1989) that
evolved through successive editor versions and personal forks. The data
format stayed closely related across all variants; the player routines
diverged. XTracker V4.1x and V4.2x are unrelated in authorship (Tufan Uysal)
but use an identical or near-identical data format (confirmed for V3.1 by the
CSDb comment "player 100% identical to Compotech V2.1").

---

## Lineage tree

```
1988: Markus Schneider writes personal sound driver
      └── Based on Soundmonitor (Chris Hülsbeck) — too slow for game use
          [source: Thomas Detert interview, Remix64]

1989: The Parsec Music Editor V5.1 (Mnemonic Designs)
      Authors: Markus Schneider + Nic + ADT; bug-fix: SMC (Pretzel Logic)
      Music: Jeroen Tel (included demo tune "Tomcat")
      [source: CSDb #10744; sidid.nfo entry (Parsec)]
      ↓
      Schneider joins X-Ample Architectures (March 1989)
      Helge Kozielek + Mario van Zeist optimize the player
      Joachim Fräder codes the editor UI
      [source: Markus Schneider interview, Remix64]

1990: Compotech V1 (X-Ample Architectures)
      Player: Schneider + Kozielek
      Editor UI: Fräder
      [sidid.nfo: RELEASED: 1990 X-Ample Architectures]
      Note: CSDb group page shows "Compotech 1992" — year discrepancy;
      sidid.nfo likely correct (1990); CSDb may reflect a release update.

1992: Compotech (CSDb listing, "1992 Tool") — same or revised V1

1995: Compotech V2.1 (X-Ample Architectures)
      Coders: Chap Bizarre + Joachim Fräder + Markus Schneider
      [source: CSDb #122614]
      This is the DEFINITIVE Compotech release.

1996: The Ultimate X-Tracker V3.1 (Tufan Uysal / Smash Designs + APS)
      "Player of this editor is 100% identical to Compotech V2.1"
      [source: CSDb #17708, Fred comment 2013]
      → SoNiC wrote a new EDITOR wrapping the Compotech V2.1 PLAYER

1996: The Ultimate X-Tracker V4.00 Beta (Tufan Uysal; Detert credited for music)
      → V4.x replaces the player routine (new fingerprint: XTracker_V4.1x)
      [source: Thomas Detert CSDb scener page]

1996: The Ultimate X-Tracker V4.13 (Tufan Uysal / APS)
      [source: CSDb #82320]

2019: Comptech-X (Geir Tjelta; private, with Markus Schneider)
      "Probably private player for X-Ample members"
      [source: sidid.nfo Geir_Tjelta/Comptech-X section]
```

---

## Are the data formats the same or different?

### Compotech V1 → Compotech V2.1: same format
The sidid base `X-Ample` signature covers both. The `(Compotech_V2.x)` sub-
signature covers V2.x specifically. The `(Compotech_V2.x)` fingerprint is
the dispatch loop (bitmask, frame counter, ADC #7 voice stride) — this is
a player-level signature, not a data-format signature. Both versions almost
certainly use the same on-disk data format; the V2.x player was an optimization
of V1.

### Compotech V2.1 ↔ XTracker V3.1: identical player, same data format
CSDb comment is definitive: "The player of this editor is 100% identical to
Compotech V2.1." XTracker V3.1 is a new editor UI shipping the same player.
Data format: **same as Compotech V2.1**.

### XTracker V4.1x: new player, unknown data format change
The V4.1x sidid fingerprint shows a structurally different dispatch loop
(unrolled 3-voice, no bitmask). The data format MAY have changed. This
is the primary open question. Given SoNiC was maintaining backward
compatibility with existing tunes, the data format likely changed minimally.
The shift from `(Compotech_V2.x)` to `(XTracker_V4.1x)` sub-tag means the
player was rewritten.

### XTracker V4.2x: minor player revision
One HVSC SID carries this fingerprint (`Falk-Ohr-Filter_Model_50.sid` by
SoNiC). The `(XTracker_V4.2x)` sub-signature starts with `A0 00 / F0 01`
(init trick) and reverses the bitmask polarity (BCS vs BCC). Possibly a
brief experimental release. Data format likely same as V4.1x.

### Thomas_Detert fork: same data format, modified player
The `(Thomas_Detert)` signature matches the same dispatch skeleton as
Compotech_V2.x with specific additions (`09 0F` force master-vol=$F,
`F0 03` BEQ-always trick, explicit $D416 write). Detert modified the player
for his personal workflow but almost certainly kept the same data format
(he was composing in Compotech). Data format: **same as Compotech V2.1**.

### Sonic/SDS fork: same data format, customized player
SoNiC's custom player has hardcoded $D404,X writes and hardcoded $D418/$D416
writes, but retains the `CE/10` frame counter and `ADC #7` voice stride
from Compotech. The data format is almost certainly the same; the player is
a performance-optimized variant embedded at fixed addresses ($1000 for most
SoNiC tunes).

### X-Ample_Digi: different mode, CIA extension
This is an extension module activated when sample playback is required.
It programs CIA1 ($DD04/$DD05/$DD0E) and uses a different sample-stream
format (packed 5-bit nibbles with $80 end sentinel). This is NOT a separate
engine — it is an add-on to the main X-Ample player for digi interludes.
Data format: **different (sample data); requires CIA-exact Mode 2 treatment**.

---

## The "LordsOfSonics/MS" sidid group

The sidid.cfg/nfo uses `LordsOfSonics/MS` as the parent group for the
Parsec variant and the base driver. `Lords of Sonics` was Markus Schneider's
early handle/group before fully joining X-Ample. The `(Parsec)` sub-signature
lives under `LordsOfSonics/MS` in sidid, not under `X-Ample`.

In HVSC, 123 tunes are tagged `LordsOfSonics/MS` (separate from the 380
`X-Ample` tunes). These represent Schneider's pre-Compotech era work
(Parsec Music Editor) and/or composers who used the Parsec player.

---

## Is Reflextracker related?

**No.** Reflextracker is a completely separate engine:
- Created by kb, Quiss, Zorc (Reflex group) — CSDb release ID 43348
- Published 1995 by Reflex + The Obsessed Maniacs
- sidid signature is under a separate Geir_Tjelta/SIDDuzz block (NOT X-Ample)
- All 137 HVSC Reflextracker SIDs are RSID (self-playing), Polish demoscene
  authors, init=$C006 — no overlap with X-Ample patterns
- The "Obsessed Maniacs" group link to SoNiC is coincidental (SoNiC was in
  both APS and The Obsessed Maniacs, but Reflextracker is by Reflex)

---

## Is XTracker V4.1x by X-Ample Architectures?

**No.** XTracker V4.1x and V4.2x were created by Tufan Uysal (SoNiC) of
The Art Project Studios (and Smash Designs, The Obsessed Maniacs). SoNiC
was the PRIMARY USER of the X-Ample player (123 of 380 X-Ample SIDs are
his), but he is not an X-Ample Architectures member. He developed XTracker
as his own tool using/extending the Compotech player.

The sidid.nfo entry confirms:
```
(XTracker_V4.1x)
     NAME: The Ultimate X-Tracker
   AUTHOR: Tufan Uysal (SoNiC)
 RELEASED: 1996 The Art Project Studios
REFERENCE: https://csdb.dk/release/?id=82320
```

The X-Ample Architectures co-development narrative sometimes circulated in
descriptions ("X-Ample & Lords of Sonic" for Compotech) is about the
ORIGINAL Compotech, not XTracker. XTracker is entirely SoNiC's work.

---

## The "Sonic/SDS" variant

`SDS` likely stands for "Sonic Design Studio" — SoNiC's design studio
handle. The `(Sonic/SDS)` sidid variant appears to be SoNiC's early
personal fork of the Compotech player (before he wrote XTracker V3.1 as
a formal editor). It has hardcoded $D404,X writes and a fixed 3-voice loop
with explicit $D418/$D416 management.

The 11 CIA-timed SoNiC tunes in HVSC likely use this Sonic/SDS or XTracker
player variant.

---

## Quick reference table

| sidid name | Actual editor | Data format | Who composed | HVSC count |
|---|---|---|---|---|
| X-Ample (base) | Compotech V1 or V2 | X-Ample native | All X-Ample composers | 380 |
| (Compotech_V2.x) | Compotech V2.x | Same as base | All X-Ample composers | subset of 380 |
| (Thomas_Detert) | Compotech V2.x (modified player) | Same | Thomas Detert (92 SIDs) | subset |
| (Sonic/SDS) | SoNiC personal fork | Same | Tufan Uysal (SoNiC, 123 SIDs) | subset |
| (XTracker_V4.1x) | XTracker V3.1–V4.1x | Same? (OPEN) | SoNiC and later users | subset |
| (XTracker_V4.2x) | XTracker V4.2x | Same? | SoNiC | 1 |
| (X-Ample_Digi) | Compotech + digi extension | CIA+sample | Unknown (likely SoNiC) | 0 confirmed |
| Parsec (LordsOfSonics/MS) | Parsec Music Editor V5.1 | Parsec format | Schneider early work | 123 |
| Geir_Tjelta/Comptech-X | Comptech-X (private, 2019) | Unknown | Geir Tjelta + Schneider | unknown |

---

## OPEN questions

1. Does XTracker V4.1x change the data format vs Compotech V2.1, or only
   the player code? (RE needed: compare a V4.1x tune vs a Compotech V2.1 tune
   at the binary level)
2. What exactly is "Sonic/SDS"? Is SDS a product name for SoNiC's editor
   predecessor to XTracker?
3. Are any HVSC X-Ample tunes actually using the X-Ample_Digi extension?
   (Need to examine CIA register writes in SoNiC's unusual-load-address tunes)
4. How many HVSC tunes are Compotech V1 (1990) vs V2.1 (1995)?
   (sidid doesn't distinguish V1 vs V2.1 — both match the base X-Ample signature)
5. What is the exact data format? Instrument table layout, sequence/pattern
   encoding, orderlist structure — no public documentation found.
