---
source_url: local: /home/jtr/sidfinity/hvsc85/ (binary inspection of SID files)
fetched_via: local read
fetch_date: 2026-06-16
author: research session (Claude Sonnet 4.6)
content_date: 2026-06-16
reliability: primary
---

# LordsOfSonics/MS — Binary Survey of HVSC SID Files

## Version History String (from Move.sid, load=$1000, offsets $1000–$117F)

The following PETSCII-encoded text is embedded in Move.sid as a "header" block
before the player code. It documents the development lineage of the engine:

```
COMPTECH MUSIC PLAYER BY XAP
TRACKNAME: MOVE, LENGTH: 05:13, YEAR: 2020, COMPOSER: MARKUS SCHNEIDER
VERSION 2.4 UPGRADE PLAYER AND EDITOR BY MARKUS SCHNEIDER
VERSION 2.3 UPGRADE PLAYER AND EDITOR BY GEIR TJELTA
VERSION 2.2 UPGRADE PLAYER BY MARKUS SCHNEIDER
VERSION 2.0 PLAYER BY MARKUS SCHNEIDER, ADDITIONAL CODE BY HELGE KOZIELEK,
  EDITOR BY JOACHIM MULTERMANN
```

The `YEAR: 2020` timestamp confirms the Comptech engine is used for new compositions
as of 2020. The JMP table in Move.sid uses a different structure from V05.1:
`JSR $1B11` (init) + `JMP $1208` (play) — reflecting post-1989 evolution.

---

## V05.1 Memory Map (Parsec 5.1 — from Babyface/Babes_Boogie.sid, load=$1000)

```
$1000: JMP $10D8    ; 4C D8 10  — INIT entry point
$1003: JMP $10E6    ; 4C E6 10  — PLAY entry point (also called from INIT)

$1006–$10D7  : SONG DATA BLOCK (210 bytes)
  $1006: song-init flag / song selector (observed: $01 for single-song SIDs)
  $1007–$100B: zeroed playback state (reset by init)
  $100C: voice count index (set to $02 by init, counts down 2→1→0 for 3 voices)
  $100D–$10xx: instrument table, wavetable, note data (structure TBD)
  $10xx: orderlist/sequence pointers (structure TBD)
  ~$095F: embedded text string ("BABE'S BOOGIE" COMPOSED BY BABYFACE IN PLAYER V05.1! ...)

$10D8–$10E5  : INIT ROUTINE (14 bytes)
  AD 06 10      LDA $1006          ; check init flag
  C9 01         CMP #$01
  F0 74         BEQ $1154          ; if already init'd, jump to player
  C9 02         CMP #$02
  D0 3C         BNE $1124
  4C 48 11      JMP $1148          ; jump to "first call" handler

$10E6–$1xxx  : PLAY ROUTINE
  AA            TAX                ; A=song number → X
  BD A4 1B      LDA $1BA4,X        ; look up something (per-song table?)
  8D 46 10      STA $1046          ; store
  8A            TXA
  8D 7C 10      STA $107C          ; store song number
  A2 00         LDX #$00
  ; ... voice processing loop continues ...

$1132 (Parsec sig site):
  9D 21 10      STA $1021,X        ; zero voice state × 9 pairs
  9D 83 10      STA $1083,X
  9D 24 10      STA $1024,X
  CA            DEX
  10 E5         BPL *-$1B          ; loop
  A9 1F         LDA #$1F
  8D 54 11      STA $1154          ; ? (some count/flag)
  A9 01         LDA #$01
  8D 06 10      STA $1006          ; mark as init'd
  A2 18         LDX #$18
  A9 00         LDA #$00
  9D 00 D4      STA $D400,X        ; zero SID regs $D418–$D400
  CA            DEX
  10 FA         BPL *-3
  60            RTS

$1148 (after RTS — SID volume and start):
  A9 1F         LDA #$1F
  8D 18 D4      STA $D418          ; master vol = $0F (low nibble), filter off
  A2 02         LDX #$02
  8E 0C 10      STX $100C          ; voice counter = 2 (counts 2,1,0 = 3 voices)
  CE 42 10      DEC $1042          ; decrement something
  10 06         BPL +6             ; skip if not first time
```

---

## Version Distribution Across All 123 LordsOfSonics/MS SIDs

| Version Tag | Count | Representative SID |
|---|---|---|
| V05.1 (Parsec) | 12 | Babyface/Babes_Boogie.sid |
| v4.1 | 1 | Schneider_Markus/Lingo.sid |
| v2.4 + history | 1 | Schneider_Markus/Move.sid (year 2020!) |
| v2.3 (shortened) | 1 | Schneider_Markus/Vectormania.sid |
| v1.0 | 1 | Babyface/G-G-Goodbye.sid |
| LOS text (no version#) | 9 | various |
| No embedded string | 99 | majority |

The 99 "no-label" SIDs probably use versions 2.x–4.x (pre-Parsec); the player
binary is present but without the text annotation. These may require sidid
fingerprinting or comparative byte-matching to version.

---

## Player Binary Byte Comparison (V05.1 vs v4.1)

**Lingo.sid (v4.1), load=$A000:**

```
$A000: 4C 9A A0    JMP $A09A   ; INIT
$A003: 4C A4 A0    JMP $A0A4   ; PLAY
$A006–$A09B: SONG DATA BLOCK (147 bytes)
$A09A: ...         ; INIT routine
$A0A4: ...         ; PLAY routine
```

Version string in Lingo.sid at offset $0090:
```
\n\x06MUSIC BY LOS ... PLAYER 4.1
```

The data block is shorter in Lingo (147 bytes vs 210 bytes in V05.1), suggesting
either fewer instruments or a more compact data format in earlier versions.

---

## Sample Data Block (V05.1, Babes_Boogie, $1006–$10D7)

```
1006: 01 00 00 00 00 00 FF D7 84 02 82 40 50 40 04 02
1016: 04 FF FF 0D 00 07 0E 00 02 02 02 00 0B 00 0A 02
1026: 0A 01 00 05 00 41 00 04 36 10 00 06 00 FE FE FE
1036: 00 00 01 41 1E 00 00 00 00 01 18 02 02 00 00 00
1046: 02 00 02 00 00 01 18 02 5F 9D BE 1F 03 1F 00 00
1056: 00 00 00 00 00 00 90 00 00 04 00 00 00 00 40 04
1066: 40 00 00 00 00 00 00 00 03 07 27 4E 4E 06 02 0C
1076: 10 50 01 00 00 00 00 5F 9D BE 00 00 00 00 00 00
1086: 00 00 00 B5 E5 C8 00 00 00 23 0A 08 06 04 03 02
1096: 03 3F 0E 34 34 34 34 34 34 3F 0A 09 08 07 06 05
10A6: 04 3F 0E 24 0F 24 0F 24 0F 81 41 41 11 11 11 11
10B6: 11 81 41 80 80 80 80 80 80 81 11 11 11 11 11 11
10C6: 11 81 41 81 11 80 11 80 11 04 10 10 08 0F 0F F1
10D6: F2 F4
```

Observations:
- `$1006` = $01: single-song init flag (matches across all single-song SIDs checked)
- `$100C` = $0D (13): possibly instrument/voice-parameter index (overwritten to $02 during init)
- `$102E` = $36 $10: looks like a 16-bit pointer to $1036 (within the data block!)
- Values `FE FE FE` at $1033–$1035: likely song-end sentinel for 3 voices
- Values `$3F 0E ...` at $1097: look like ADSR or envelope data
- Values `$81 $41 $41 $11 ...` at $10A7: look like waveform control bytes (SID wave register)
- Values `$80 $80 $80 ...` at $10B0: may be additional waveform bytes or pulse width
- Values `F1 F2 F4` at $10D5–$10D7: could be note/freq data or filter settings
- Pointer at $102E (`$36 $10`) points to $1036, which is the start of an orderlist/seq block

---

## Confirmed Multi-Subtune SID (Timezone.sid, 13 songs, load=$3000)

```
$3000: JMP $30CB   ; INIT
$3003: JMP $30D9   ; PLAY

Songs: 13 (confirmed by PSID header)
Data block: ~$3006–$30CA (varies)
```

The presence of 13 subtunes suggests an orderlist-per-voice-per-subtune structure.
The init routine must accept the subtune number and load appropriate per-subtune state.

---

## Diagnostic Notes for Migration

1. The JMP table at load+$00 and load+$03 is the standard entry structure for V05.1.
2. INIT zeroes SID registers fully ($D400–$D418), then calls into PLAY.
3. 3-voice player confirmed by: (a) "A2 02" at init (voice count 2→0), (b) three per-voice
   STA pairs in the state-clear loop.
4. The data block (~210 bytes in V05.1) precedes the player code in memory.
5. Note values: Sequence of bytes with $FE/$FD/$FB sentinels seen in Move.sid after the
   version block — may be note length markers or effect codes.
6. Waveform table evidence: Alternating $81/$41/$80/$11 bytes suggest a
   wavetable-program model where bytes are written directly to $D404 (voice waveform/gate).
