---
source_url: https://github.com/cadaver/sidid/blob/master/sidid.cfg
fetched_via: direct (local clone at tmp/ariston_research/sidid/)
fetch_date: 2026-06-15
author: Cadaver (Andreas Varga) and contributors
content_date: ongoing (sidid project)
reliability: primary (binary fingerprint database)
---

# Ariston Family — sidid.cfg Fingerprint Signatures

These are the byte-pattern fingerprints used by sidid to identify Ariston-family players.
`??` = wildcard byte.

## Main Ariston Player

```
Ariston
A2 00 6E ?? ?? 90 07 BD ?? ?? 99 ?? ?? C8 E8 E0 08 D0 EF AE ?? ?? A9 FF END
```

## Ian_Crabtree_V1

```
(Ian_Crabtree_V1)
9D ?? ?? 20 ?? ?? CA 10 EF A0 ?? A9 ?? 99 00 D4 END
```

## Ian_Crabtree_V2

```
(Ian_Crabtree_V2)
AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 29 0F 48 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 BD END
```

## Wally_Beben (Ariston variant with improved drums)

```
(Wally_Beben)
48 C9 08 B0 ?? A9 ?? 9D ?? ?? AC ?? ?? 68 99 03 D4 68 99 02 D4 CE ?? ?? 30 END
BD ?? ?? AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 END
BD ?? ?? 99 04 D4 AE ?? ?? EE ?? ?? BD ?? ?? 18 END
```

---

## sidid.nfo Entry

From `tmp/ariston_research/sidid/sidid.nfo`:

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

---

## Notes on Variants

- **Ariston (main)** — the base player pattern. Relocatable.
- **Ian_Crabtree_V1** — earliest version; identified by writing to $D400+00 (voice 1 control).
- **Ian_Crabtree_V2** — second version; identified by writes to $D405/$D406 (voice 1 ADSR),
  with instrument-select mask (`29 0F` = AND #$0F).
- **Wally_Beben** — improved drum variant. The Maniacs of Noise added better drums and
  returned it; Beben used this for his own compositions. Identified by a BASS drum check
  (`C9 08 B0`) and multi-write ADSR pattern.

The `(Wally_Beben)` pattern has THREE fingerprint sequences, suggesting the sidid tool
requires all three to match — probably because the Wally_Beben variant has the most
distinct drum/ADSR code path.

## Observation on Relocation

The main `Ariston` fingerprint uses `??` for all table addresses, confirming the player
is relocatable (load address varies per game/demo). The `E0 08` = CPX #$08 in the main
pattern suggests 8 slots (possibly 8 voices processed, or 8 patterns per track step?).
Actually given 3 voices × stride 7 = 21 bytes per voice set, E0 08 is more likely
checking the outer loop counter for the 3-voice processing loop (e.g. 0, 7, 14 →
the SID offset table check).
