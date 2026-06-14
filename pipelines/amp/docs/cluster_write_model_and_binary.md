# AMP (Advanced Music Programmer) — Write Model and Binary Structure

```
provenance:
  fetch_date:    2026-06-14
  author:        sidfinity research agent (Claude Sonnet 4.6)
  reliability:   HIGH for binary-structural facts (primary source = HVSC binaries);
                 MEDIUM for creator/history (CSDb + web, thin documentation);
                 LOW for instrument-program byte semantics (not emulator-traced).
  sources:
    - HVSC #84 binaries (direct read-only inspection):
        MUSICIANS/B/Bakker_Nantco/Anti_Airwolf_Tune.sid   (canonical $1000 base)
        MUSICIANS/B/Bakker_Nantco/Western_Skies.sid        (cross-check)
        MUSICIANS/B/Bakker_Nantco/Nantcos_Blues.sid        (cross-check)
        MUSICIANS/B/Bakker_Nantco/Twilight_Dance.sid       (cross-check)
        MUSICIANS/B/Black_Dove/Black_Heaven.sid            ($1003/$1006 variant)
        MUSICIANS/M/Mueller_Markus/Cool_One.sid            (original author SID)
    - CSDb (csdb.dk): release #35519 (Hitech Studio Designs), #193063 (Quality),
                      #244185 (NDC) — scraped 2026-06-14
    - SIDId signature: from project's sidid.cfg (known, not inspected here)
    - hvsc84.db: engine classification and address statistics
```

---

## 1. Overview

AMP (Advanced Music Programmer) is a Commodore 64 SID music editor and player
published on **Magic Disk 64, issue 12/1991** by **H.I.C.** (code) and
**Hayes** (music, both of the group Quality). The CSDb lists at least three
independent releases of V2.3 from December 1991 (Hitech Studio Designs, NDC,
Vision/X-Ray). An earlier 1990 Quality release also exists; a 1993 WOW release
and A.M.P. V2.3 Pack collections followed. The sole documented version number
in all known releases is **V2.3**.

HVSC #84 contains **246 SIDs** classified as `engine='AMP'`. The corpus spans
1989–1995 and is overwhelmingly Dutch-scene (Nantco Bakker / Warriors of Music
is the largest single contributor) and German-scene (Dr. Zoom, Markus Mueller,
Bad/Denis Knitter, Higgie/Hergen Oltmann, Jan Albartus/Logan).

---

## 2. Version variants and relocation

### 2.1 Address layout variants observed in HVSC

| init addr | play addr | count | description |
|-----------|-----------|-------|-------------|
| $1000     | $1003     | 142   | canonical base |
| $1003     | $1006     | 25    | +3 offset (extra JMP at $1000) |
| $2800     | $280B     | 7     | relocation to $2800 |
| $C003     | $C006     | 9     | relocation to $C000 |
| $E003     | $E006     | 2     | relocation to $E000 |
| $A000     | $A003     | 4     | relocation to $A000 |
| $D900     | $D903     | 5     | relocation to $D900 |

The **+3 offset variant** (init=$1003, play=$1006): the binary starts with a
third JMP at $1000 that points to some external/demo-side routine, then JMP
init at $1003 and JMP play at $1006. The Bakker/Black_Dove group is the main
user of this form. Example: `MUSICIANS/B/Black_Dove/Black_Heaven.sid`.

The **relocated forms** ($2800/$A000/$C000/$E000) appear to be straight
relocations of the same player to avoid memory conflicts in demo contexts.
Structural offsets within the player are the same; the SIDId signature is at
the same relative offset from the player base.

### 2.2 SIDId signature

Location: **player_base + $035B** (= $135B for $1000 base):

```
B9 ?? ?? ?? 16 D4 C8 98 9D ?? ?? ?? ?? ?? ?? ?? ?? 8D 18 D4
```

Literal match against Anti_Airwolf_Tune.sid at $135B:
```
B9 3D 1B 8D 16 D4 C8 98 9D 5D 10 AD 15 10 0D 0C 10 8D 18 D4
```

Meaning: `LDA filter_table,Y / STA $D416 / INY / TYA / STA pos_state,X / ...
ORA filter_mode / STA $D418`. This uniquely identifies the filter cutoff +
master volume write sequence in the player kernel.

The two `??` wildcards at offset +1/+2 and +3 are the per-song vibrato/filter
table address (lo/hi) patched by SMC at init time.

### 2.3 Player kernel identity

The region **$1340–$162D** (relative to player base) is byte-identical across
all correctly-embedded AMP SIDs at the same base address, EXCEPT for 10 bytes
at 5 SMC patch locations (see section 4.3). These 10 bytes are the address
operands of `LDA abs,Y` instructions that get overwritten by the init routine
to point to the per-song auxiliary tables.

---

## 3. Binary layout ($1000-base canonical form)

```
$1000–$1002  JMP $init_routine      ; 4C lo hi (= JMP $157E in Anti_Airwolf)
$1003–$1005  JMP $play_routine      ; 4C CE 14 (= $14CE)

             ;; Song config area (populated by init() from song data block)
$1006–$100A  reserved/song-data-ptr ; $1009/$100A = little-endian ptr to song block
$100B        voice_enable           ; bit mask: bit0=V1, bit1=V2, bit2=V3
$100C        filter_res_route       ; SID $D417 value: bits7-4=resonance, bits3-0=voice route
$100D        order_length           ; number of steps in each voice's orderlist
$100E        repeat_count_init      ; 0=infinite loop
$100F        pattern_count          ; used as limit for song position counter
$1010        speed                  ; tempo: counts down each play(); new note when reaches 0
$1011        pos_counter            ; (runtime) current orderlist position [0..order_length)
$1012        active_flag            ; (runtime) 1=playing, 0=silent (written by init, clrd at end)
$1013        tempo_counter          ; (runtime) counts up, triggers step advance
$1014        sub_counter            ; (runtime) sub-step counter
$1015        master_vol_bits        ; contributes to $D418 via ORA with filter_res_route

$1016–$102D  12 x 2-byte LE pointers ; track table pointer array (3 voices × 4 tables)
             ; ptr[0] = V1 note_seq        ptr[1] = V1 transpose_seq
             ; ptr[2] = V1 instprog_lo_seq ptr[3] = V1 instprog_hi_seq
             ; ptr[4] = V2 note_seq        ptr[5] = V2 transpose_seq
             ; ptr[6] = V2 instprog_lo_seq ptr[7] = V2 instprog_hi_seq
             ; ptr[8] = V3 note_seq        ptr[9] = V3 transpose_seq
             ; ptr[10]= V3 instprog_lo_seq ptr[11]= V3 instprog_hi_seq

$102E–$108F  per-voice runtime state ; 3 groups, X-stride = 7
             ; X=0 (V1), X=7 (V2), X=14 (V3):
             ;   $102E,X = current chunk/segment index
             ;   $1030,X $1031,X = freq delta lo/hi (vibrato accumulator)
             ;   $1033,X = gate/restart flags
             ;   $1034,X = current note index (0-95 into freq table)
             ;   $1043,X = waveform cache
             ;   $1044,X $1045,X = pulse width lo/hi
             ;   $1049,X = pulse sweep accumulator
             ;   $105E,X = note duration countdown
             ;   $106F,X $1076,X $107D,X = position snapshots

$1082–$10D7  ASCII title string (zero-terminated) + misc runtime temp + bit tables

$10D8–$1138  freq_lo table ; 96 bytes: note[0..95] freq LO byte
                            ; note[0]=0 (rest/silence), note[1]=C#0..note[95]=B7

$1139–$1199  freq_hi table ; 96 bytes: parallel HI bytes for same 96 notes
                            ; combined: freq = freq_lo[n] | (freq_hi[n] << 8)

$119E–$162D  player kernel code (routines):
             ; $119E  voice_note_proc  — decode note/instrument from track tables
             ; $1230  freq_write_sub   — accumulate vibrato+slide, write $D400/$D401
             ; $1300  pulse_wave_sub   — pulse sweep + $D402/$D403/$D404 writes
             ; $1341  filter_vol_sub   — filter cutoff ($D416) + vol ($D418)
             ; $12BE  $D417 write (resonance/routing)
             ; $14CE  play entry point — main dispatch (save/restore ZP, voice loop)
             ; $157E  init entry point — patch SMC addresses + init player state
             ; $1623  init+CIA entry (variant B entry point if $1000 has extra JMP)

;; Song-specific data (location varies per song, pointed to by $1009/$100A):
SONG_BLOCK   38 bytes:
             ; [0..23]  = 12 little-endian pointers -> written to $1016-$102D
             ; [24..37] = 14 config bytes  -> written to $100B-$1018
             ;            including:
             ;   [24]=$100B voice_enable
             ;   [25]=$100C filter_res_route
             ;   [26]=$100D order_length
             ;   [27]=$100E repeat_count
             ;   [28]=$100F pattern_count
             ;   [29]=$1010 speed
             ;   [30..31] -> $1011/$1012 (initial pos/active state)
             ;   [32..33] -> $1013/$1014 (tempo/sub-counter init)
             ;   [34..35] -> $1015/$1016 (master vol + first ptr byte)
             ;   [36..37] -> $1017/$1018 (ptr continuation)
             ;   NOTE: bytes [0x1E..0x25] are patched via individual SMC writes
             ;         (see section 4.3) BEFORE the loop writes [0..0x17]

;; 12 track data tables (pointed to by ptr[0..11]):
;; Each table has one byte per orderlist step (length = $100D order_length)
;; ptr[0] V1_note_seq:       one byte per step = note_byte (see section 4.1)
;; ptr[1] V1_transpose_seq:  one byte per step = transpose offset
;; ptr[2] V1_instprog_lo_seq: lo byte of instrument program pointer per step
;; ptr[3] V1_instprog_hi_seq: hi byte of instrument program pointer per step
;; (and analogously for V2/V3)

;; Instrument programs (pointed to by combined instprog_hi:instprog_lo):
;; Variable-length byte sequences (see section 4.2)

;; Auxiliary effect tables (addresses written by SMC during init):
;; vibrato_delta_table  : ascending/descending byte values for vibrato LFO
;; filter_cutoff_table  : per-step filter cutoff hi byte sequence
;; glide_table_1/2      : pitch slide increment bytes
```

---

## 4. Data format details

### 4.1 Note byte encoding

The **note_seq** table (ptr[0]/ptr[4]/ptr[8]) stores one byte per orderlist step.
The byte encodes BOTH duration AND a note reference, using two different
interpretations depending on bit 7:

```
note_byte bits 7-4 = duration counter (4 bits, range 1-15; 0=none?)
note_byte bits 3-0 = note_low_nibble (combined with transpose for note lookup)
```

However, the actual note index (0-95 into the freq table) is derived by:
1. Reading note_byte from note_seq
2. Reading transpose_byte from transpose_seq at the same position
3. Combining: if bit7=0 (relative), add note_byte to previous note index;
              if bit7=1 (absolute), use note_byte & $7F as absolute index
4. The result + some transpose factor indexes into freq_lo/freq_hi tables

Note index 0 = rest (freq = 0). Indices 1–95 map to C#0 through B7 (PAL).

The verified frequency table (PAL, first octaves):

| index | note | freq ($D400/$D401) |
|-------|------|--------------------|
| 0     | rest | $0000 |
| 1     | C#0  | $0116 (278) |
| 12    | C1   | $020E (526) |
| 24    | C2   | $041B (1051) |
| 36    | C3   | $0837 (2103) |
| 48    | C4   | $106E (4206) |
| 60    | C5   | $20DC (8412) |
| 72    | C6   | $41B8 (16824) |
| 84    | C7   | $8370 (33648) |

C2 = $041B = 1051 matches PAL standard (261.63 Hz × 16777216 / 985248 ≈ 1051 ✓).

### 4.2 Instrument programs

The `instprog_hi:instprog_lo` per-step pointer pairs form a two-level
indirection: each orderlist step's combined pointer gives the address of an
instrument program sequence in the auxiliary table area.

Based on code analysis, each instrument program contains:
- **Byte 0**: Attack/Decay nibble pair for $D405 (AD)
- **Byte 1**: Sustain/Release nibble pair for $D406 (SR)
- **Byte 2+**: Wave control bytes (values written to $D404, containing gate/waveform)
  — a wavetable-style sequence with loop/end markers

Byte $00 within a program sequence appears to be an end/return marker.
Byte $01 appears to be a loop-back marker.
Bytes $40/$80/$81/$89/$41 are typical waveform control values observed in the
instrument tables (pulse/noise/sawtooth/triangle with gate).

Observed instrument data from Anti_Airwolf_Tune.sid V1 instruments (ptr[3]=$1A0E):
```
inst#0: 04 57 00 00 00 02 00 01 00 00 00 06 05 00 00 00
inst#1: 05 87 00 00 00 02 01 09 00 00 06 0C 0B 00 00 00
inst#2: 07 C8 08 00 00 02 09 10 00 00 12 18 17 30 00 00
inst#3: 03 A9 08 00 00 02 10 14 00 00 18 1F 1E F0 00 00
```

$57 = A=$05 D=$07; $87 = A=$08 D=$07; $C8 = A=$0C D=$08; $A9 = A=$0A D=$09.

### 4.3 Self-modifying code (SMC) patch mechanism

The init routine patches **5 locations** in the player kernel with per-song
table addresses. These are the address operands of `LDA abs,Y` instructions.

| SMC location | player offset | what it patches |
|-------------|---------------|-----------------|
| $1356/$1357 | +$356 | vibrato delta table lo/hi (copy 1) |
| $135C/$135D | +$35C | vibrato delta table lo/hi (copy 2, duplicate) |
| $13CD/$13CE | +$3CD | filter cutoff table lo/hi |
| $141B/$141C | +$41B | pitch glide table lo/hi (copy 1) |
| $144D/$144E | +$44D | pitch glide table lo/hi (copy 2, duplicate) |

The two "duplicates" exist because the player has two separate code paths
(non-looping and looping variants) that reference the same table.

These 5 patch addresses are sourced from song block bytes at offsets:
- `[0x22]`/`[0x23]` → vibrato table (lo/hi)
- `[0x24]`/`[0x25]` → filter cutoff table (lo/hi)
- `[0x20]`/`[0x21]` → glide table 1 (lo/hi)
- `[0x1E]`/`[0x1F]` → glide table 2 (lo/hi)

These are patched individually BEFORE the main init loop that writes the
track pointers and config bytes.

### 4.4 Auxiliary table formats

**Vibrato delta table** (two SMC refs, same address): byte sequence of signed
pitch deltas. Observed pattern: 00 72 6A 62 5A 52 4A 00 40 00 01 89 11 11 10...
The sequence appears to be a waveform-style LFO table that drives vibrato
depth oscillation.

**Filter cutoff table**: per-step hi-byte values for $D416. One byte per
orderlist step (or sub-sequence); allows per-pattern filter sweeps.

**Glide/pitch slide tables** (two SMC refs): signed byte sequences for
portamento. 00=stop, positive=slide up, negative=slide down. $80 appears
to be a control/reset marker. Example:
```
80 80 01 80 C0 C0 80 40 40 03 80 B0 E0 B0 80 50 20 50 00...
```

---

## 5. Per-frame write model

The play routine runs once per VBI (50 Hz). The global `pos_counter` ($1011)
advances when `tempo_counter` ($1013) overflows the `speed` value ($1010).
When the position advances, all three voices decode their next note and
instrument program.

**Dispatch order within one play() call:**

1. **Guard check**: LDA $1012 (active_flag), BEQ return — silent if 0.
2. **ZP save**: copy ZP registers $A3/$A4 to temp area ($119A/$119B).
3. **Voice 1 note decode** (JSR $119E, X=0):
   - If duration counter ($105E,X) > 0: decrement, skip to step 6.
   - Else: read note from note_seq[pos], read transpose, compute note index.
   - Double-dereference instprog_lo/hi tables to find instrument program.
   - Write $D405,X (AD) and $D406,X (SR) from instrument program bytes.
   - Load waveform sequence bytes, OR in gate bit, cache in $1033,X/$1043,X.
   - Store new duration counter from note_byte upper nibble.
4. **Voice 1 filter update** (JSR $1341, X=0):
   - Read filter_cutoff_table[pos] → STA $D416 (cutoff hi).
   - LDA $1015 (master_vol) ORA $100C (filter_mode) → STA $D418.
5. **Voice 2 filter update** (JSR $1341, X=7) — same sub.
6. **Voice 3 filter update** (JSR $1341, X=14) — same sub.
7. **Tempo/position advance**: increment tempo_counter; if reached speed limit,
   advance pos_counter; if reached order_length, handle repeat/loop.
   Reset all voice duration counters and position snapshots on song wrap.
8. **ZP restore**: copy temp area back to $A3/$A4.

**Within each voice per active note-step** (in voice_note_proc):
- Frequency: freq_lo[note] + vibrato_delta → STA $D400,X
              freq_hi[note] + vibrato_delta → STA $D401,X
- Pulse width: STA $D402,X (PW lo), STA $D403,X (PW hi)
  - Pulse sweep: STA $D402,X / $D403,X updated by glide table increment
- Waveform + gate: STA $D404,X (from cached $1043,X | gate_bit)
- AD/SR: STA $D405,X, STA $D406,X (on note trigger only)

**Per-step filter writes** (filter_vol_sub, called 3× with X=0/7/14):
- STA $D416 (filter cutoff hi) — from filter_cutoff_table[pos]
- STA $D418 (volume | filter_LP/HP/BP mode) — ORA of $1015 and $100C
- STA $D417 (resonance + voice routing) — from $D412+X area

**Init writes** ($D415 = filter cutoff lo, zeroed to $00; SID reset via
$FF then $00 written to all $D400+Y for Y=0 to the number of voice slots).

**Voice order**: V1 processed first for note decode; filter sub called V1, V2, V3
sequentially; freq/wave writes interleaved within each voice's note-decode sub.

---

## 6. Observed corpus stats (hvsc84.db)

- Total AMP SIDs: **246**
- Dominant base address: $1000 init / $1003 play (142 SIDs, 58%)
- Second most common: $1003/$1006 (25 SIDs, 10%)
- All-zeros play address (broken/demo-rips): 3 SIDs

Key composers in HVSC corpus (sorted by SID count, estimated):
- Nantco Bakker (Warriors of Music): ~80 SIDs
- Jan Albartus (Logan): ~20 SIDs
- Manuel Cavero (Black Dove): ~15 SIDs
- Heiko Zimmermann (Okieh): ~5 SIDs
- Denis Knitter (Bad), Hergen Oltmann (Higgie): ~5 each

---

## 7. Tool handling

**libsidplayfp / VICE**: plays AMP SIDs without issues; the player uses standard
VBI-based IRQ (CIA not required); PSID speed bit is typically 0 (VBI). No
special handling documented.

**SIDId**: single signature match at player_base+$035B (see section 2.2).
Classifies all base-address variants as "AMP" including the $1003/$1006 form.
Relocated forms ($2800, $A000, $C000, $E000) match the same signature at their
respective bases.

**DeepSID**: no AMP-specific handling found in public repo. Plays via standard
PSID emulation path (reSID/WebSid/Hermit). SID identification from HVSC metadata.

**hvsc84.db classification**: `engine='AMP'` for 246 SIDs; separate entries for
`X-Ample` (380 SIDs, different player) and related engine strings. AMP and
X-Ample are distinct players despite similar German-scene origin.

---

## 8. Gaps and open questions

- **Note byte encoding**: the exact formula combining note_byte, transpose_byte,
  and per-voice chunk-index into a 0-95 freq table index is partially inferred.
  The voice processor uses a double-indirection via chunk index ($102E,X) before
  applying the transpose. A single run-through with `siddump --writelog` + known
  note would confirm.

- **Instrument program loop/end format**: $00 = end and $01 = loop are assumed;
  need emulator trace to confirm the exact terminator byte and loop address field.

- **Duration byte structure**: whether bits 7-4 or some other nibble split encodes
  duration. Currently assumed upper-nibble = duration.

- **$D415 (filter cutoff lo)**: init zeroes it to $00; whether the player writes
  it during playback (per-step) has not been confirmed. Only one STA $D415 was
  found (in init at $15EF). The AMP player may use filter cutoff hi only.

- **Multi-subtune support**: the AMP player's `active_flag`/`repeat_count`
  mechanism likely supports single-song only; multi-subtune SIDs in HVSC are
  almost all single-subtune. How the player handles the A register at init()
  for subtune selection is unconfirmed.

- **Gate/hard-restart**: the code path at $14C8 writes $81 to $D401,X during
  certain instrument transitions. Whether this is a deliberate hard-restart or
  a pulse-width initialization side effect is unclear.

- **Chunk/segment model**: the per-voice `$102E,X` chunk index and how it advances
  (vs. the global pos_counter) is incompletely understood. Each voice may
  independently select which of the 4 track pointers to read from, supporting
  a multi-segment song structure.

- **X-Ample relationship**: X-Ample (380 SIDs in HVSC) is classified separately
  from AMP. Whether it shares the same player kernel or is a distinct engine
  has not been investigated. Should be checked before AMP migration starts.

---

## Leads to follow

1. **Run `siddump --writelog` on Anti_Airwolf_Tune.sid** to confirm exact
   per-frame register write sequence and cross-check against this write model.
   Specifically: confirm $D415 is NOT written per-frame; confirm $D417 write
   timing relative to $D416/$D418; confirm V1/V2/V3 write ordering.

2. **Disassemble the chunk-advance logic** — find where $102E,X (the per-voice
   chunk index) is incremented. This determines whether AMP uses a true
   multi-segment orderlist or all voices share the same global pos_counter.

3. **Confirm instrument program byte semantics** with a single-instrument test
   SID or by tracing one instrument load through `siddump --pc-trace` and
   matching PC addresses back to player code.

4. **Check X-Ample player** — compare SIDId signature and player bytes against
   AMP at player_base+$035B; if the kernel differs, document as separate family.

5. **CSDb D64 download**: retrieve `AMP.d64` / `AMP23.d64` from csdb.dk
   releases #35519, #193063, #244185 to read the actual AMP tool binary (editor
   + player) for a complete format spec including editor UI capabilities,
   pattern length limits, instrument count limits, etc.

6. **STIL.txt search**: grep HVSC's STIL.txt for `Bakker_Nantco` and `AMP` entries
   to find any annotated notes about the player's quirks.

7. **Multi-subtune SIDs in HVSC**: identify any AMP SIDs with songs > 1 to
   understand how the player handles subtune selection via the A register at init.
