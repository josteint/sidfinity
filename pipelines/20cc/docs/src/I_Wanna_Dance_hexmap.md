---
source_url: file:hvsc85/MUSICIANS/0-9/20CC/I_Wanna_Dance.sid
fetched_via: binary inspection (python3, read-only)
fetch_date: 2026-06-14
author: jtr (inspection)
content_date: ~1988-1989
reliability: primary (binary)
---

# I_Wanna_Dance.sid — Binary Hex Map (20CC Variant A reference)

PSID header:
  magic=PSID, version=2
  load=$0000 (embedded), embed_load=$1000
  init=$1000, play=$1003
  num_songs=1, start=1, speed=0 (VBI)
  data_offset=$7C (124 bytes), body_length=2028 bytes
  loads $1000–$17EB

## Region Map

```
$1000–$1005  Entry stubs
  $1000: 4C 24 14   JMP $1424       ; init
  $1003: 4C 72 10   JMP $1072       ; play

$1006–$006F  Per-voice state (zero at load time, init clears to 0)
  stride-3 arrays for voices 0/1/2; see state map in main doc

$1072–$13CA  Player code
  $1072  Main play loop (A2 02 / JSR $107B / CA / 10 FA / 60)
  $107B  Per-voice processor
  $1204  Pulse subroutine 3
  $1221  Pulse down routine
  $125E  Pulse up routine
  $1272  New note fetch
  $12BC  Note command dispatch (hi2-bit dispatcher)
  $13CB  Sequence advance / command parser
  $13DC  Sequence command thresholds

$1424–$1467  Init routine
  Clears $1006–$106D to 0 (loop: LDA #0, STA $xx,X, DEX from $67)
  Clears SID $D400–$D418 to 0 (loop: LDA #0, STA $D400,X DEX from $18)
  Sets $106A = $0F (master vol)
  Computes Y = subtune * 6, reads voice ptrs from $1545
  Calls $13CB for each voice to prime sequence state

$1468–$146C  Vibrato depth table
  01 02 04 00 07 0E  (6 values — per-octave vibrato depths?)

$146D–$146F  SID voice base offset table
  00 07 0E            [voice 0 → $D400, voice 1 → $D407, voice 2 → $D40E]

$1470–$147F  Small ramp table (01 02 04 00 07 0E 00 00 00 00 04 07 00 05 08 00)

$1480–$14E4  Freq table lo (96 bytes, notes 0–95)
  $1480: 0C 1C 2D 3E 51 66 7B 91 A9 C3 DD FA  (octave 0: C to B)
  $1490: 18 38 5A 7D A3 CC F6 23 53 86 BB F4  (octave 1)
  ...

$14E5–$1543  Freq table hi (96 bytes)
  $14E5: 01 01 01 01 01 01 01 01 01 01 01 01  (octave 0 hi bytes = $01xx)
  $14F5: 02 02 02 02 02 02 02 03 03 03 03 03  (octaves 1-2)
  ...
  $1533: 0C 0D 0E 0E 0F 10 11 12 13 15 16 17  (octave 7 region)
  $153F: 19 1A 1C 1D 1F 21 23 25 27 2A 2C 2F  

$1544        (pad byte)

$1545–$154A  Song/voice table (6 bytes = 1 subtune × 3 voices × 2 byte ptr)
  Song 0: V1=$165B V2=$165F V3=$1667 (lo/hi interleaved: 5B 16 5F 16 67 16)

$154B–$1552  Wave-program pointer table lo (8 entries)
  96 9A C0 E9 56 68 7B AC

$1553–$155A  Wave-program pointer table hi (8 entries)  
  16 16 16 16 17 17 17 17

  → Ptrs: [0]=$1696 [1]=$169A [2]=$16C0 [3]=$16E9 [4]=$1756 [5]=$1768 [6]=$177B [7]=$17AC

$155B–$1561  Pattern pointer table lo (7 entries)
  00 69 A5 B9 CD DC EC

$1562–$1568  Pattern pointer table hi (7 entries)
  00 15 15 15 15 15 15

  → Ptrs: [0]=$0000(null) [1]=$1569 [2]=$15A5 [3]=$15B9 [4]=$15CD [5]=$15DC [6]=$15EC

$1569–$15FA  Sequence/pattern stream data (mixed)
  $1569: 04 18 1A 29 00 10 20 30 40 50 90 D0 E0 F0 FF F0
  $1579: E0 D0 C0 B0 A0 90 FF FF 0C FF 59 41 41 41 41 41
  ...

$15FB–$1659  Instrument records (8 bytes each × 12 instruments)
  Inst 0 @ $15FB: 00 00 00 00 00 00 FF 00
  Inst 1 @ $1603: 00 00 00 FA 00 21 FF 00
  Inst 2 @ $160B: 00 00 00 F8 00 02 FF 00
  Inst 3 @ $1613: 00 00 00 F8 00 03 FF 00
  Inst 4 @ $161B: 00 00 00 78 00 05 FF 00
  Inst 5 @ $1623: 00 00 00 7D 00 F4 FF 54
  Inst 6 @ $162B: 00 00 00 FA 00 06 FF 44
  Inst 7 @ $1633: 02 45 00 7B 00 D0 FF 54
  Inst 8 @ $163B: 00 11 00 8A 00 00 FF 00
  Inst 9 @ $1643: 00 21 00 6D 00 00 FF 44
  Inst 10 @ $164B: 20 41 00 A9 00 A0 FF 54
  Inst 11 @ $1653: 00 11 00 FD 00 00 FF 54
  (Record byte[4]=$FF means no filter write; byte[4]≠$FF → STA $D416)

$165B+  Sequence for Song 0 Voice 1 (at $165B):
  8E 01 02 FF 90 41 03 05 41 06 07 FF 90 43 04 8D ...
  Decoded:
    $8E  SET_1018 val=$0E   ($80–$BF: arp/swing param)
    $01  SELECT_WAVEPROG 1  ($00–$3F: select wave-program entry [1])
    $02  SELECT_WAVEPROG 2
    $FF  END/LOOP
    $90  SET_1018 val=$10
    $41  REPEAT count=1     ($40–$5F: set repeat count)
    $03  SELECT_WAVEPROG 3
    ...

$1696+  Wave-program 0 data (at $1696):
  90 00 00 FF             (3 bytes: two data bytes, $FF end)

$169A+  Wave-program 1 data (at $169A):
  81 03 00 81 08 32 01 3E 81 04 32 82 02 04 81 03 ...
  (long: note/effect stream with $81 hi2=2 and $01 hi2=0 cmds interleaved)

$16C0+  Wave-program 2 data, $16E9+ Wave-prog 3, etc.
```

## SID Write Summary

All per-voice SID writes use `STA $D4xx,Y` with Y ∈ {0, 7, 14}:

| Register | Write site | When |
|----------|-----------|------|
| $D400,Y (freq lo) | $1100 | Every frame (per voice) |
| $D401,Y (freq hi) | $10FC | Every frame (per voice) |
| $D402,Y (pw lo)   | $1106 | Every frame (per voice) |
| $D403,Y (pw hi)   | $110C | Every frame (per voice) |
| $D404,Y (ctrl)    | $10C8 | Frame counter == 2 (hard restart); conditional |
| $D404,Y (ctrl)    | $112D | On note load |
| $D405,Y (AD)      | $138B/$139B | On instrument load |
| $D406,Y (SR)      | $1391/$13A1 | On instrument load |
| $D416   (filt_lo) | $1344 | On instrument load |
| $D417   (filt_hi) | $135C | On instrument load |
| $D418   (vol/flt) | $1116 | Every frame (written 3× — once per voice loop!) |
