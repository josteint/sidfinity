# Investigation: 100% F-Grade for tempo >= 12 Songs

## Date: 2026-04-10

## Hypothesis Tested
"Init timing offset causes irrecoverable desync at high tempos" -- REJECTED

## Actual Root Cause: Unhandled Multispeed (CIA Timer) Songs

ALL GT2 SIDs with tempo >= 12 are **multispeed songs** that use CIA timer interrupts
to run the player routine multiple times per VBI frame. The V2 rebuilt SID is
VBI-locked (runs once per 50Hz frame), so multispeed songs play at 1/Nx the
correct rate.

### Evidence

Every high-tempo song has CIA timer writes ($DC04/$DC05) in its init routine:

| Multiplier | CIA Timer | Binary Tempo | Effective Tempo |
|-----------|-----------|-------------|-----------------|
| 2x | $2663 (9827) | 12 | 6.0 |
| 3x | $1997 (6551) | 18 | 6.0 |
| 4x | $1331 (4913) | 24 | 6.0 |
| 7x | $0AF7 (2807) | 42 | 6.0 |
| 8x | $0998 (2456) | 48 | 6.0 |
| 12x | $0665 (1637) | 72 | 6.0 |
| 13x | $05E7 (1511) | 78 | 6.0 |
| 16x | $04CC (1228) | 96 | 6.0 |

Formula: `binary_tempo = base_tempo * multiplier`, where base_tempo is almost
always 6 (the GoatTracker default). The original player executes `multiplier`
times per VBI frame. The V2 rebuilt player executes once per VBI frame but uses
the full `binary_tempo`, making notes change `multiplier` times too slowly.

### Scale

- Total GT2 SIDs: 7,325
- Multispeed songs: ~703 (9.6%)
  - 2x: 485, 3x: 46, 4x: 109, 8x: 28, others: 35
- Grade distribution for tempo >= 12: 0 Grade A, 2 Grade B, 3 Grade C, 25 Grade F (from 30 sampled)

### Why tempo >= 12 perfectly identifies multispeed

GoatTracker's packer (greloc.c) computes DEFAULTTEMPO as:
```c
insertdefine("DEFAULTTEMPO", multiplier ? (multiplier*6-1) : 5);
```
For multiplier=2: DEFAULTTEMPO=11, binary stores 11, gt2_to_usf reads it as `11+1=12`.
For multiplier=4: DEFAULTTEMPO=23, binary stores 23, gt2_to_usf reads it as `23+1=24`.

Since base tempo is almost always 6 and the minimum multiplier is 2, the minimum
"high" tempo is `6*2 = 12`.

### What's NOT wrong

1. **Init timing** -- the comparison methodology's +-3 frame window and 10-frame
   init grace would absorb any init timing offset at tempo=6. The problem is NOT
   timing jitter.
2. **Tempo counter logic** -- the V2 player's dec/bne/bpl counter mechanism is
   identical to GT2's. The counter reloads and note processing are correct.
3. **The `song.multiplier` USF field** -- it exists in the Song dataclass but is
   never populated by gt2_to_usf.py and never consumed by usf_to_sid.py or
   codegen_v2.py.

### What needs to happen (not implemented in this investigation)

To support multispeed, the V2 player would need to either:

1. **Run at Nx VBI rate** -- set CIA timer in the rebuilt SID's init and call the
   player routine N times per interrupt. This is the correct approach but requires:
   - CIA timer setup in the rebuilt SID's init
   - Multiple player calls per interrupt
   - Adjusting cycle budget (player must complete in time for next CIA tick)

2. **Divide tempo by multiplier** -- use `effective_tempo = binary_tempo / multiplier`
   as the V2 DEFAULTTEMPO. This preserves note timing but loses the higher-rate
   effects execution (vibrato, pulse modulation, etc. would be coarser).

Option 1 is correct; option 2 is a partial workaround.

### CIA Timer Detection

CIA timer preamble pattern (at init address):
```
LDX #$lo / STX $DC04 / LDX #$hi / STX $DC05
  or
LDA #$lo / STA $DC04 / LDA #$hi / STA $DC05
```

67 of 706 high-tempo songs have CIA writes outside the init preamble (within the
player code body), requiring a broader binary search. 3 songs have no CIA writes
at all (possibly custom player variants or false tempo detection).
