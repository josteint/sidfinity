---
source_url: https://github.com/cadaver/sidid/blob/master/sidid.cfg + https://github.com/cadaver/sidid/blob/master/sidid.nfo
fetched_via: git clone (external); repo cloned to /home/jtr/sidfinity/tmp/ariston_research/sidid/
fetch_date: 2026-06-15
author: cadaver (Lasse Öörni) + contributors
content_date: ongoing (as of 2026-06-15 clone)
reliability: primary (canonical SID engine detection database)
---

# cadaver/sidid — Ariston/Ian_Crabtree/Wally_Beben Signatures

## sidid.nfo (lines 693–707, verbatim from local clone)

```
Ariston
   AUTHOR: Ian Crabtree

(Ian_Crabtree_V1)
   AUTHOR: Ian Crabtree

(Ian_Crabtree_V2)
   AUTHOR: Ian Crabtree

(Wally_Beben)
     NAME: Ariston Music Editor
   AUTHOR: Ian Crabtree, Philip Brabbin & Wally Beben
 RELEASED: 1988
REFERENCE: https://csdb.dk/release/?id=119920
  COMMENT: This is an improved version of the player/editor by Ian Crabtree.
```

## sidid.cfg (lines 138–151, verbatim from local clone)

```
Ariston
A2 00 6E ?? ?? 90 07 BD ?? ?? 99 ?? ?? C8 E8 E0 08 D0 EF AE ?? ?? A9 FF END
(Ian_Crabtree_V1)
9D ?? ?? 20 ?? ?? CA 10 EF A0 ?? A9 ?? 99 00 D4 END
(Ian_Crabtree_V2)
AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 29 0F 48 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 BD END
(Wally_Beben)
48 C9 08 B0 ?? A9 ?? 9D ?? ?? AC ?? ?? 68 99 03 D4 68 99 02 D4 CE ?? ?? 30 END
BD ?? ?? AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 END
BD ?? ?? 99 04 D4 AE ?? ?? EE ?? ?? BD ?? ?? 18 END
```

## Key points

- Parenthesised entries (Ian_Crabtree_V1), (Ian_Crabtree_V2), (Wally_Beben) are secondary
  sub-fingerprints that only trigger after the primary Ariston signature matches. They do not
  identify independent engines — they disambiguate sub-variants within the Ariston family.
- The sidid.nfo explicitly identifies the Wally_Beben variant as "Ariston Music Editor" authored
  by "Ian Crabtree, Philip Brabbin & Wally Beben", released 1988.
- CSDb reference for Wally_Beben variant: https://csdb.dk/release/?id=119920 (CIC crack).
- The online cadaver/sidid repo (github.com/cadaver/sidid) matches our local copy exactly.

## Corpus signature distribution (HVSC #84, 147 Ariston SIDs)

Measured 2026-06-15 by scanning for byte-exact sub-sequences in each SID body:

| Condition | Count | Description |
|-----------|-------|-------------|
| Ariston primary + Wally_Beben sub-sig | 132 | Beben variant (dominant) |
| Ariston primary only (no Wally sub-sig) | 15 | Earlier Crabtree/Barrett/Leitch |
| Neither signature | 0 | None |
| Wally sub-sig without Ariston primary | 0 | None |

The 15 ariston-primary-only SIDs:
- Barry Leitch (2): Captain_Courageous, Marauder
- Paul Meredith (1): Mean_City
- Steve Barrett (4): Hyber_Blob, Knightmare, Monopoly_Deluxe, Super_Hang-On
- Steve Barrett/Eggman (6): Blue_Meanies, Egg_in_Space, Fraeulein_Kinski, Galactic_Games_1/2/3
- Wally Beben (2): I-Xera, Shockwave (early compositions before adding the Beben sub-sig path)

All 15 also contain the $D405 write ($99 05 D4), confirming they are Ian_Crabtree_V2-class engines
(proper ADSR programming) without the pulse-width phasing additions.

**Implication:** 90% of the Ariston corpus (132/147) uses the full Wally_Beben feature set
(pulse-width per note, 3× gate toggle, note-range gate). The "plain" Ariston main sig without
Wally sub-features is the minority.
