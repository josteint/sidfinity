---
source_url: https://blog.chordian.net/computer-timeline/
fetched_via: direct
fetch_date: 2026-06-15
author: Jens-Christian Huus (JCH / Chordian)
content_date: 1988-2006 (events) / 2015+ (page)
reliability: primary
---

# JCH Computer Timeline — Laxity Engine Origin Facts

## Key facts about the Laxity player derived from JCH's timeline

### June 1988: JCH reverse-engineers Laxity's player

> "Reverse engineered Laxity's C64 music player and started composing in it."

This is the earliest external reverse-engineering of the Vibrants/Laxity format.
JCH at this point was a skilled C64 coder who dissected the binary to extract the format.

### March 3, 1989: Six OldPlayer compositions

JCH's JCH-SELEC #2 contains six tunes composed in the Laxity player format
(referred to as "OldPlayer" by JCH — these are the JCH_OldPlayer SIDId entries).

### March 17, 1989: "Popcorn" in Laxity format

JCH converted the classic "Popcorn" tune into the Laxity player format.

### Late 1989: JCH begins developing his own editor

After Laxity asked JCH to stop using his editor (because JCH composed too well
and Laxity didn't want it going public), JCH started building his own player
(the JCH Editor / NewPlayer system, first generation circa 1989-1991).

### September 9, 1990: Laxity joins Vibrants

Laxity joined Vibrants (JCH's group, formed August 1989). By this time both
had their own editors: Laxity's (the Vibrants/Laxity format) and JCH's (the NewPlayer).

---

## Architectural inference: What JCH could see in 1988

JCH reverse-engineered a 1987-1988 Laxity player. The JCH_OldPlayer SIDId signature
shows the nibble-packing approach JCH found:

```
48 18 4A 4A 4A 4A 29 07 0A 0A 0A 48 0A 8D ?? ?? 68 18 6D ?? ?? 8D ?? ?? 68
```

This decodes a note byte by: `PHA; CLC; LSR×4; AND #$07; ASL×3; PHA; ASL; STA abs;
PLA; CLC; ADC abs; STA abs; PLA` — a frequency computation using bit-field extraction.
The structure implies Laxity's note format packed octave + semitone into a single byte.

---

## EdLib / D00 (AdLib) lineage

JCH later built "EdLib" for AdLib (OPL2) using the same track editing system:
> "an editor I wrote that used the same track editing system as my Commodore 64 editor"

This means the JCH NewPlayer track/sequence editing model derived from the
Laxity player, and the AdLib EdLib format inherited the same track model.
The D00 format uses:
- Sequence pointer tables (SeqPointer)
- Track pointers (TrackPoi)
- Instrument tables
- Pattern data

The D00 file header (from ftp.modland.com format documentation):
```
$0000-$0005: Detection bytes ('JCH', $26, $02, $66)
$0006:       Block type ($00 for music)
$0007:       Player version
$0008:       Timer speed
$0009:       Music/SFX count
$000a:       Soundcard ($00 = AdLib)
$000b-$002a: 32 bytes — tune name
$002b-$004a: 32 bytes — composer name
$004b-$006a: 32 bytes — reserved
$006b-$006c: Pointer to "Tpoin" tables
$006d-$006e: Pointer to "SeqPointer" tables
$006f-$0070: Pointer to "Instrument" tables
$0071-$0072: Pointer to "DataInfo" text
$0073-$0074: Pointer to "Special" (SFX) tables
$0075:       End marker ($FF)
```

The D00 player header:
```
$0000-$0002: Jump to player functions
$0003-$0008: Detection signature
$0009-$000a: Player version ($0400)
$000b:       OPL2 indicator
$000c:       Voice count ($09 for AdLib)
$000d-$002c: "AdLib" card name
Variable pairs (WORD type) + byte flags:
  Inst, Dur, SeqPoi, TrackPoi, Freq (WORD-based, 9 entries each)
  Spedr, Gate, Nog, Note (BYTE-based, 9 entries each)
```

The presence of `Spedr` (speed), `Gate`, `Nog` (note-off?), `Note` as per-voice
byte arrays, and `Freq` as a per-voice WORD array mirrors what the SIDId signatures
suggest for the Vibrants/Laxity C64 player: per-voice freq (16-bit), per-voice gate,
per-voice speed, per-voice note value.

---

## AdLib "hard restart SR sometimes sound wrong" bug

From VOGONS forum (AdPlay v1.6 notes): "Hard restart SR sometimes sound wrong"
— indicates the Vibrants/JCH AdLib format ALSO implemented a form of hard restart,
parallel to the Vibrants/Laxity C64 player. This is consistent with the
Vibrants/JO SIDId signature showing `A9 08; STA $D404,Y` (test-bit write = hard
restart setup) in its init code.

---

## Conclusion: Relationship map

```
Laxity C64 player (1986-1987)
     │
     ├─── JCH reverse-engineers (June 1988) ──► JCH OldPlayer (1988-1989)
     │         │                                 (6502 in Laxity's format)
     │         │
     │         └─► JCH builds own editor ──► JCH NewPlayer (1989-1991)
     │                                        (NP17 → NP20 → NP21 → ...)
     │                   └── JCH AdLib version ──► EdLib / D00 format
     │
     └─── Laxity continues own editor ──► TFA Editor V3.24 (1989)
               │                           Laxity Editor v/32-3.34 (1990)
               │                           Laxity Editor v/34-3.35 (1990)
               │
               └─── HVSC: 179 SIDs tagged "Vibrants/Laxity"
                          (SIDId: 5-line OR signature, play at init+$06)
```
