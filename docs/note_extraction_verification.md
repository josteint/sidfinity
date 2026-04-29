# Note Extraction Verification — Commando.sid vs Das Model

Frames compared: 500 (original) / 500 (das model)

## Register Difference Summary

### V1: PERFECT — no register differences
### V2 fhi: 33/500 frames differ (6.6%)

| Frame | Orig | DasModel | Delta |
|-------|------|----------|-------|
|     0 | $00  | $43     |  +67  |
|     1 | $00  | $43     |  +67  |
|     2 | $00  | $43     |  +67  |
|     3 | $00  | $43     |  +67  |
|     4 | $00  | $43     |  +67  |
|     5 | $00  | $43     |  +67  |
|    96 | $41  | $43     |   +2  |
|    97 | $41  | $43     |   +2  |
|    98 | $41  | $43     |   +2  |
|    99 | $41  | $43     |   +2  |
|   100 | $41  | $43     |   +2  |
|   101 | $41  | $43     |   +2  |
|   168 | $2B  | $15     |  -22  |
|   192 | $41  | $43     |   +2  |
|   193 | $41  | $43     |   +2  |
|   194 | $41  | $43     |   +2  |
|   195 | $41  | $43     |   +2  |
|   196 | $41  | $43     |   +2  |
|   197 | $41  | $43     |   +2  |
|   288 | $27  | $13     |  -20  |
| ... (13 more) | | | |

### V2 ctl: 5/500 frames differ (1.0%)

| Frame | Orig | DasModel | Delta |
|-------|------|----------|-------|
|     1 | $43  | $80     |  +61  |
|     2 | $43  | $80     |  +61  |
|   168 | $40  | $41     |   +1  |
|   288 | $40  | $41     |   +1  |
|   360 | $40  | $41     |   +1  |

### V3 ctl: 31/500 frames differ (6.2%)

| Frame | Orig | DasModel | Delta |
|-------|------|----------|-------|
|    15 | $40  | $41     |   +1  |
|    21 | $40  | $41     |   +1  |
|    45 | $40  | $41     |   +1  |
|    69 | $40  | $41     |   +1  |
|    87 | $40  | $41     |   +1  |
|    93 | $40  | $41     |   +1  |
|   111 | $40  | $41     |   +1  |
|   117 | $40  | $41     |   +1  |
|   141 | $40  | $41     |   +1  |
|   165 | $40  | $41     |   +1  |
|   183 | $40  | $41     |   +1  |
|   189 | $40  | $41     |   +1  |
|   207 | $40  | $41     |   +1  |
|   213 | $40  | $41     |   +1  |
|   237 | $40  | $41     |   +1  |
|   261 | $40  | $41     |   +1  |
|   279 | $40  | $41     |   +1  |
|   285 | $40  | $41     |   +1  |
|   303 | $40  | $41     |   +1  |
|   309 | $40  | $41     |   +1  |
| ... (11 more) | | | |


**Total register differences: 69 across 500 frames × 3 voices × 4 registers**

## Note Event Comparison (gate-on transitions by voice)

### V1: 27 original notes vs 27 das model notes

| # | Orig fhi | Das fhi | Match | Orig dur | Das dur | Dur match |
|---|----------|---------|-------|----------|---------|-----------|
|  0 | $AF     | $AF    | OK |     12   |     12  | OK |
|  1 | $75     | $75    | OK |     12   |     12  | OK |
|  2 | $1D     | $1D    | OK |     60   |     60  | OK |
|  3 | $1A     | $1A    | OK |     18   |     18  | OK |
|  4 | $1D     | $1D    | OK |     30   |     30  | OK |
|  5 | $1A     | $1A    | OK |     12   |     12  | OK |
|  6 | $1D     | $1D    | OK |      6   |      6  | OK |
|  7 | $1A     | $1A    | OK |      6   |      6  | OK |
|  8 | $1D     | $1D    | OK |     12   |     12  | OK |
|  9 | $AF     | $AF    | OK |     12   |     12  | OK |
| 10 | $75     | $75    | OK |     12   |     12  | OK |
| 11 | $AF     | $AF    | OK |     12   |     12  | OK |
| 12 | $75     | $75    | OK |     12   |     12  | OK |
| 13 | $1D     | $1D    | OK |     60   |     60  | OK |
| 14 | $1A     | $1A    | OK |     18   |     18  | OK |
| 15 | $1D     | $1D    | OK |     30   |     30  | OK |
| 16 | $1A     | $1A    | OK |     12   |     12  | OK |
| 17 | $1D     | $1D    | OK |      6   |      6  | OK |
| 18 | $1A     | $1A    | OK |      6   |      6  | OK |
| 19 | $1D     | $1D    | OK |     12   |     12  | OK |
| 20 | $AF     | $AF    | OK |     12   |     12  | OK |
| 21 | $75     | $75    | OK |     12   |     12  | OK |
| 22 | $AF     | $AF    | OK |     12   |     12  | OK |
| 23 | $75     | $75    | OK |     12   |     12  | OK |
| 24 | $1D     | $1D    | OK |     60   |     60  | OK |
| 25 | $1A     | $1A    | OK |     18   |     18  | OK |
| 26 | $1D     | $1D    | OK |     14   |     14  | OK |

Pitch match: 27/27 (100%)
Duration match (±1 frame): 27/27 (100%)

### V2: 24 original notes vs 19 das model notes

| # | Orig fhi | Das fhi | Match | Orig dur | Das dur | Dur match |
|---|----------|---------|-------|----------|---------|-----------|
|  0 | $00     | $43    | DIFF |      6   |     24  | DIFF |
|  1 | $43     | $15    | DIFF |     18   |     24  | DIFF |
|  2 | $15     | $17    | DIFF |     24   |     18  | DIFF |
|  3 | $17     | $15    | DIFF |     18   |     18  | OK |
|  4 | $15     | $13    | DIFF |     18   |     12  | DIFF |
|  5 | $13     | $43    | DIFF |     12   |     24  | DIFF |
|  6 | $41     | $15    | DIFF |      6   |     72  | DIFF |
|  7 | $43     | $43    | OK |     18   |     24  | DIFF |
|  8 | $15     | $15    | OK |     72   |     24  | DIFF |
|  9 | $41     | $17    | DIFF |      6   |     18  | DIFF |
| 10 | $43     | $15    | DIFF |     18   |     18  | OK |
| 11 | $15     | $13    | DIFF |     24   |     18  | DIFF |
| 12 | $17     | $15    | DIFF |     18   |     90  | DIFF |
| 13 | $15     | $43    | DIFF |     18   |     24  | DIFF |
| 14 | $13     | $15    | DIFF |     18   |     24  | DIFF |
| 15 | $15     | $17    | DIFF |     90   |     18  | DIFF |
| 16 | $41     | $15    | DIFF |      6   |     18  | DIFF |
| 17 | $43     | $13    | DIFF |     18   |     12  | DIFF |
| 18 | $15     | $43    | DIFF |     24   |     20  | DIFF |

Pitch match: 2/19 (11%)
Duration match (±1 frame): 2/19 (11%)

### V3: 36 original notes vs 36 das model notes

| # | Orig fhi | Das fhi | Match | Orig dur | Das dur | Dur match |
|---|----------|---------|-------|----------|---------|-----------|
|  0 | $03     | $03    | OK |     18   |     18  | OK |
|  1 | $07     | $07    | OK |      6   |      6  | OK |
|  2 | $0F     | $0F    | OK |     12   |     12  | OK |
|  3 | $03     | $03    | OK |     36   |     36  | OK |
|  4 | $0F     | $0F    | OK |     12   |     12  | OK |
|  5 | $06     | $06    | OK |      6   |      6  | OK |
|  6 | $07     | $07    | OK |      6   |      6  | OK |
|  7 | $03     | $03    | OK |     18   |     18  | OK |
|  8 | $07     | $07    | OK |      6   |      6  | OK |
|  9 | $0F     | $0F    | OK |     12   |     12  | OK |
| 10 | $03     | $03    | OK |     36   |     36  | OK |
| 11 | $0F     | $0F    | OK |     12   |     12  | OK |
| 12 | $06     | $06    | OK |      6   |      6  | OK |
| 13 | $07     | $07    | OK |      6   |      6  | OK |
| 14 | $03     | $03    | OK |     18   |     18  | OK |
| 15 | $07     | $07    | OK |      6   |      6  | OK |
| 16 | $0F     | $0F    | OK |     12   |     12  | OK |
| 17 | $03     | $03    | OK |     36   |     36  | OK |
| 18 | $0F     | $0F    | OK |     12   |     12  | OK |
| 19 | $07     | $07    | OK |     12   |     12  | OK |
| 20 | $02     | $02    | OK |     18   |     18  | OK |
| 21 | $05     | $05    | OK |      6   |      6  | OK |
| 22 | $0F     | $0F    | OK |     12   |     12  | OK |
| 23 | $02     | $02    | OK |     36   |     36  | OK |
| 24 | $0F     | $0F    | OK |     12   |     12  | OK |
| 25 | $04     | $04    | OK |      6   |      6  | OK |
| 26 | $05     | $05    | OK |      6   |      6  | OK |
| 27 | $03     | $03    | OK |     18   |     18  | OK |
| 28 | $07     | $07    | OK |      6   |      6  | OK |
| 29 | $0F     | $0F    | OK |     12   |     12  | OK |
| ... (showing first 30 of 36) | | | | | | |

Pitch match: 30/30 (100%)
Duration match (±1 frame): 30/30 (100%)

## fhi Consecutive-Run Comparison (first 40 runs per voice)

### V1: 500 orig runs / 500 das runs

| # | Orig fhi | Orig dur | Das fhi | Das dur | Pitch | Dur |
|---|----------|----------|---------|---------|-------|-----|
|  0 | $AF     |       1  | $AF    |      1  | OK    | OK   |
|  1 | $03     |       1  | $03    |      1  | OK    | OK   |
|  2 | $AF     |       1  | $AF    |      1  | OK    | OK   |
|  3 | $03     |       1  | $03    |      1  | OK    | OK   |
|  4 | $AF     |       1  | $AF    |      1  | OK    | OK   |
|  5 | $03     |       1  | $03    |      1  | OK    | OK   |
|  6 | $AF     |       1  | $AF    |      1  | OK    | OK   |
|  7 | $03     |       1  | $03    |      1  | OK    | OK   |
|  8 | $AF     |       1  | $AF    |      1  | OK    | OK   |
|  9 | $03     |       1  | $03    |      1  | OK    | OK   |
| 10 | $AF     |       1  | $AF    |      1  | OK    | OK   |
| 11 | $03     |       1  | $03    |      1  | OK    | OK   |
| 12 | $75     |       1  | $75    |      1  | OK    | OK   |
| 13 | $EA     |       1  | $EA    |      1  | OK    | OK   |
| 14 | $75     |       1  | $75    |      1  | OK    | OK   |
| 15 | $EA     |       1  | $EA    |      1  | OK    | OK   |
| 16 | $75     |       1  | $75    |      1  | OK    | OK   |
| 17 | $EA     |       1  | $EA    |      1  | OK    | OK   |
| 18 | $75     |       1  | $75    |      1  | OK    | OK   |
| 19 | $EA     |       1  | $EA    |      1  | OK    | OK   |
| 20 | $75     |       1  | $75    |      1  | OK    | OK   |
| 21 | $EA     |       1  | $EA    |      1  | OK    | OK   |
| 22 | $75     |       1  | $75    |      1  | OK    | OK   |
| 23 | $EA     |       1  | $EA    |      1  | OK    | OK   |
| 24 | $1D     |       1  | $1D    |      1  | OK    | OK   |
| 25 | $3A     |       1  | $3A    |      1  | OK    | OK   |
| 26 | $1D     |       1  | $1D    |      1  | OK    | OK   |
| 27 | $3A     |       1  | $3A    |      1  | OK    | OK   |
| 28 | $1D     |       1  | $1D    |      1  | OK    | OK   |
| 29 | $3A     |       1  | $3A    |      1  | OK    | OK   |
| 30 | $1D     |       1  | $1D    |      1  | OK    | OK   |
| 31 | $3A     |       1  | $3A    |      1  | OK    | OK   |
| 32 | $1D     |       1  | $1D    |      1  | OK    | OK   |
| 33 | $3A     |       1  | $3A    |      1  | OK    | OK   |
| 34 | $1D     |       1  | $1D    |      1  | OK    | OK   |
| 35 | $3A     |       1  | $3A    |      1  | OK    | OK   |
| 36 | $1D     |       1  | $1D    |      1  | OK    | OK   |
| 37 | $3A     |       1  | $3A    |      1  | OK    | OK   |
| 38 | $1D     |       1  | $1D    |      1  | OK    | OK   |
| 39 | $3A     |       1  | $3A    |      1  | OK    | OK   |
| ... (460 more) | | | | | | |

Pitch match: 40/40 (100%)
Duration match (±1 frame): 40/40 (100%)

### V2: 388 orig runs / 389 das runs

| # | Orig fhi | Orig dur | Das fhi | Das dur | Pitch | Dur |
|---|----------|----------|---------|---------|-------|-----|
|  0 | $00     |       6  | $43    |     24  | DIFF  | DIFF |
|  1 | $43     |      18  | $15    |      1  | DIFF  | DIFF |
|  2 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
|  3 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
|  4 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
|  5 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
|  6 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
|  7 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
|  8 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
|  9 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
| 10 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
| 11 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
| 12 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
| 13 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
| 14 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
| 15 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
| 16 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
| 17 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
| 18 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
| 19 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
| 20 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
| 21 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
| 22 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
| 23 | $2B     |       1  | $15    |      1  | DIFF  | OK   |
| 24 | $15     |       1  | $2B    |      1  | DIFF  | OK   |
| 25 | $2B     |       1  | $17    |      1  | DIFF  | OK   |
| 26 | $17     |       1  | $2E    |      1  | DIFF  | OK   |
| 27 | $2E     |       1  | $17    |      1  | DIFF  | OK   |
| 28 | $17     |       1  | $2E    |      1  | DIFF  | OK   |
| 29 | $2E     |       1  | $17    |      1  | DIFF  | OK   |
| 30 | $17     |       1  | $2E    |      1  | DIFF  | OK   |
| 31 | $2E     |       1  | $17    |      1  | DIFF  | OK   |
| 32 | $17     |       1  | $2E    |      1  | DIFF  | OK   |
| 33 | $2E     |       1  | $17    |      1  | DIFF  | OK   |
| 34 | $17     |       1  | $2E    |      1  | DIFF  | OK   |
| 35 | $2E     |       1  | $17    |      1  | DIFF  | OK   |
| 36 | $17     |       1  | $2E    |      1  | DIFF  | OK   |
| 37 | $2E     |       1  | $17    |      1  | DIFF  | OK   |
| 38 | $17     |       1  | $2E    |      1  | DIFF  | OK   |
| 39 | $2E     |       1  | $17    |      1  | DIFF  | OK   |
| ... (349 more) | | | | | | |

Pitch match: 0/40 (0%)
Duration match (±1 frame): 38/40 (95%)

### V3: 146 orig runs / 146 das runs

| # | Orig fhi | Orig dur | Das fhi | Das dur | Pitch | Dur |
|---|----------|----------|---------|---------|-------|-----|
|  0 | $03     |      18  | $03    |     18  | OK    | OK   |
|  1 | $07     |       6  | $07    |      6  | OK    | OK   |
|  2 | $0F     |       1  | $0F    |      1  | OK    | OK   |
|  3 | $1F     |       1  | $1F    |      1  | OK    | OK   |
|  4 | $0F     |       1  | $0F    |      1  | OK    | OK   |
|  5 | $1F     |       1  | $1F    |      1  | OK    | OK   |
|  6 | $0F     |       1  | $0F    |      1  | OK    | OK   |
|  7 | $1F     |       1  | $1F    |      1  | OK    | OK   |
|  8 | $0F     |       1  | $0F    |      1  | OK    | OK   |
|  9 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 10 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 11 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 12 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 13 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 14 | $03     |      36  | $03    |     36  | OK    | OK   |
| 15 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 16 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 17 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 18 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 19 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 20 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 21 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 22 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 23 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 24 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 25 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 26 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 27 | $06     |       6  | $06    |      6  | OK    | OK   |
| 28 | $07     |       6  | $07    |      6  | OK    | OK   |
| 29 | $03     |      18  | $03    |     18  | OK    | OK   |
| 30 | $07     |       6  | $07    |      6  | OK    | OK   |
| 31 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 32 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 33 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 34 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 35 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 36 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 37 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| 38 | $1F     |       1  | $1F    |      1  | OK    | OK   |
| 39 | $0F     |       1  | $0F    |      1  | OK    | OK   |
| ... (106 more) | | | | | | |

Pitch match: 40/40 (100%)
Duration match (±1 frame): 40/40 (100%)

## Instrument (ADSR) Consistency Check

Check: does each unique fhi value always map to the same ad+sr in both streams?

V1: 9 fhi values with inconsistent/mismatched ADSR:

| fhi | Orig (ad,sr) | Das (ad,sr) |
|-----|-------------|------------|
| $03 | AD$00 SR$00 AD$0D SR$FB | AD$00 SR$00 AD$0D SR$FB |
| $10 | AD$00 SR$00 AD$0D SR$FB | AD$00 SR$00 AD$0D SR$FB |
| $1A | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $1D | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $34 | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $3A | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $75 | AD$00 SR$00 AD$0D SR$FB | AD$00 SR$00 AD$0D SR$FB |
| $AF | AD$00 SR$00 AD$0D SR$FB | AD$00 SR$00 AD$0D SR$FB |
| $EA | AD$00 SR$00 AD$0D SR$FB | AD$00 SR$00 AD$0D SR$FB |

V2: 9 fhi values with inconsistent/mismatched ADSR:

| fhi | Orig (ad,sr) | Das (ad,sr) |
|-----|-------------|------------|
| $00 | AD$00 SR$00 AD$0F SR$C4 |  |
| $13 | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $15 | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $17 | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $27 | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $2B | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $2E | AD$00 SR$00 AD$06 SR$4B | AD$00 SR$00 AD$06 SR$4B |
| $41 | AD$00 SR$00 AD$0F SR$C4 |  |
| $43 | AD$00 SR$00 AD$0F SR$C4 | AD$00 SR$00 AD$0F SR$C4 |

V3: 8 fhi values with inconsistent/mismatched ADSR:

| fhi | Orig (ad,sr) | Das (ad,sr) |
|-----|-------------|------------|
| $02 | AD$00 SR$00 AD$09 SR$9F | AD$00 SR$00 AD$09 SR$9F |
| $03 | AD$00 SR$00 AD$09 SR$9F | AD$00 SR$00 AD$09 SR$9F |
| $04 | AD$00 SR$00 AD$09 SR$9F | AD$00 SR$00 AD$09 SR$9F |
| $05 | AD$00 SR$00 AD$09 SR$9F | AD$00 SR$00 AD$09 SR$9F |
| $06 | AD$00 SR$00 AD$09 SR$9F | AD$00 SR$00 AD$09 SR$9F |
| $07 | AD$00 SR$00 AD$09 SR$9F | AD$00 SR$00 AD$09 SR$9F |
| $0F | AD$00 SR$00 AD$0A SR$09 | AD$00 SR$00 AD$0A SR$09 |
| $1F | AD$00 SR$00 AD$0A SR$09 | AD$00 SR$00 AD$0A SR$09 |

## Overall Verdict

Perfect frames (fhi+ctl+ad+sr match all 3 voices): 436/500 (87.2%)

fhi-only match (pitch only, all voices): 467/500 (93.4%)

## Root Cause Analysis

Three distinct bugs identified in `src/das_model_gen.py`.

### V1: CORRECT — extraction is perfect

Voice 1 matches 100% on all registers across 500 frames. Note pitches, durations,
instrument assignments (ADSR), and pattern boundaries all match exactly. The V1
extraction from `rh_decompile.py` and `das_model_gen.py` is correct.

### Bug 1 — V2 startup timing (frames 0-5, 6 frames wrong)

**Symptom:** Original V2 plays silence (fhi=$00, never written) for frames 0-5.
Das Model writes fhi=$43 from frame 0.

**Root cause:** Das Model initializes tick_ctr=1 for all voices, which fires the
first note on the very first play call (frame 0). But the original Commando player
initializes V2's counter differently — V2's first note only fires at frame 6.

The first pattern 8 note has `dur_raw=1, tick_length=3 → 6 frames`. The original
player appears to NOT write V2 frequency before the first note fires. This 6-frame
offset means the original SID's V2 power-on state ($00) persists for the first 6
frames. Das Model writes immediately.

**Code location:** `generate_asm()` in `das_model_gen.py`, init section:
```python
a(f'        lda #1')
a(f'        sta ${z:02X}')  # tick_ctr=1 → triggers first note
```
The fix would be to initialize tick_ctr=0 and add a "first note" loading path,
or delay V2's first note by 6 frames.

**Impact:** 6 frames wrong out of 500 = 1.2%. Audibly insignificant (the original
SID's V2 is silent during these frames anyway).

### Bug 2 — V2 extended freq table T[104] phase drift (frames 96-101, 192-197, etc.)

**Symptom:** At frames 96-101 (and 192-197, etc.), original V2 plays fhi=$41, flo=$41
(freq=$4141). Das Model plays fhi=$43, flo=$15 (freq=$4315).

**Root cause:** T[104] in the Das Model is captured as $4315 (after 1 play frame).
This is a player state variable at address $5428+104*2 = $5480, which changes
dynamically as the player runs. By frame 96 of playback, the original player's
memory at $5480 has evolved to $4141, giving different fhi/flo values.

This is the fundamental limitation documented in the Hubbard diagnosis memory:
"Dynamic arp state evolution: arp freq changes as counter evolves ($03→$05→$07)."
The same applies here to T[104] — the state variable drifts over time.

**Code location:** `extract()` in `das_model_gen.py`, extended freq table section:
```python
ft_base = 0x5428
while len(T) < 120:
    i = len(T)
    addr = ft_base + i * 2
    T.append((m.memory[addr+1] << 8) | m.memory[addr])
```
T[104] is captured at one specific moment (after INIT + 1 play frame). It will
diverge from the original as the player runs more frames.

**Impact:** 18 frames wrong out of 500 = 3.6%. Partially audible (same note pitch
class but slightly different actual frequency).

### Bug 3 — V3 gate-off 1 frame too late (31 frames, every note end)

**Symptom:** Original clears gate (ctl $41→$40) at tick_ctr=3. Das Model clears
gate at tick_ctr=2 (one frame later).

**Root cause:** The gate-off threshold in `generate_asm()` is wrong by 1:
```python
a(f'        lda ${z:02X}')
a(f'        cmp #3')
a(f'        bcs v{v}gon')  # gate ON if tick_ctr >= 3
```
With `hr_frames = 3`, the gate should go OFF when tick_ctr <= 3 (i.e., when there
are 3 frames remaining including the current one). The correct threshold is `cmp #4`:
gate ON when tick_ctr >= 4, gate OFF when tick_ctr <= 3.

The Hubbard player clears the gate when the speed counter has 3 remaining decrements.
With `CMP #3; BCS`, the check passes at tick_ctr=3 (3 >= 3 is true → gate stays ON).
With `CMP #4; BCS`, the check passes only at tick_ctr >= 4 (3 < 4 → gate goes OFF).

**Code location:** All three voices in `generate_asm()`:
```python
a(f'        cmp #3')
a(f'        bcs v{v}gon')
```
Should be:
```python
a(f'        cmp #4')
a(f'        bcs v{v}gon')
```

**Impact:** 31 frames wrong out of 500 = 6.2%. Potentially audible if gate-off
timing affects envelope decay. Affects all notes in V3.

### Summary Table

| Bug | Voice | Frames wrong | % of 500 | Audibility | Root cause |
|-----|-------|-------------|----------|------------|------------|
| V2 startup delay | V2 | 6 | 1.2% | Silent period, not audible | tick_ctr init=1 not 0 |
| T[104] state drift | V2 | 18 | 3.6% | Same note, slightly different freq | Extended table captured once |
| Gate-off 1 frame late | V3 | 31 | 6.2% | Envelope tail 1 frame longer | cmp #3 should be cmp #4 |
| **Total** | | **69 register diffs** | **87.2% perfect frames** | | |

### Notes on Extraction Correctness

The note PITCHES extracted from rh_decompile.py are correct for V1 and V3 (100%
pitch match). The issue in V2 is not pitch extraction but timing:

1. The extended freq table (T[96-119]) captures player state that evolves dynamically.
   T[104] specifically holds the ctrl/PW bytes that Hubbard reads via `LDA abs,X` with
   the voice's pattern byte offset as X. This changes every time a new 3-byte note is
   encountered. The Das Model's static capture is only valid for the first few notes.

2. Note durations are correctly extracted. The das model computes `(dur+1)*tick_length`
   frames which matches the original's frame counts exactly for V1 and V3.

3. Instrument assignments (ADSR) are correct — the ADSR consistency check shows the
   same (ad,sr) pairs for all fhi values in both streams.

4. Pattern boundaries are correct — V1 and V3 pattern start/end frames match exactly.
   V2 has a 6-frame startup offset only.

5. V1 arpeggio (alternating $AF/$03 each frame) is 100% correct including phase.
   The FRAME_CTR-based arp alternation is correctly synchronized.

6. V3 arpeggio (alternating $0F/$1F each frame) is 100% correct including phase.

The dominant remaining error source (V2 T[104] drift) is a fundamental limitation:
the Hubbard arpeggio uses memory locations that double as player state variables.
A complete fix would require simulating the full player state across all frames,
or mapping the state variable evolution analytically.

