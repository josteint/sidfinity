# Ubik's Musik — Write-Model and Tool Handling

```
provenance:
  author:         Claude Sonnet 4.6 (agent research sweep)
  fetch_date:     2026-06-14
  reliability:    HIGH for §3-§6 (derived from direct binary analysis of
                  hvsc84/GAMES/A-F/Fire_Breath.sid, a canonical C600/C603 tune);
                  MEDIUM-HIGH for §1-§2 (cross-referenced across three web sources);
                  MEDIUM for §7 echo/waveform-swap (observed in code structure but
                  full per-note SR write sequence not fully traced to a clean path)

sources:
  - url: https://www.vgmpf.com/Wiki/index.php?title=Ubik%27s_Musik
    content_date: ~2015 (wiki, undated)
  - url: https://www.lemon64.com/forum/viewtopic.php?t=39350
    content_date: ~2012
  - url: https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.cfg
    fetched_via: WebFetch
  - url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
    fetched_via: WebFetch
  - url: https://csdb.dk/release/?id=260620&show=summary   (PRG2SID v1.26)
    fetched_via: WebFetch
  - url: https://cadaver.github.io/rants/music.html
    fetched_via: WebFetch
  - binary: hvsc84/GAMES/A-F/Fire_Breath.sid
    load: $BBBE  init: $C600  play: $C603  songs: 12
    analysis: direct byte-level disassembly (Python, no siddump/py65)
```

---

## §1  Overview

Ubik's Musik is a commercial C64 music editor and player runtime written by
Dave Korn ("Ubik"), published by Firebird in October 1987 (retail £2.99).
It produces compiled PRG bundles of ~7 KB containing both song/instrument
data and a self-contained player. There are 288 tunes in HVSC #84 using this
engine (SIDId engine label `Ubik's_Musik`).

Key reputation facts:
- First editor to support logarithmic vibrato and waveform swaps.
- First (or among the first) to support per-note echo (sustain level
  oscillates each note).
- Wavetable drums: 8 fixed drum sounds stored globally in the player.
- Game-programmer API: driver can play song on two voices + SFX on third.
- Closest to Hubbard's driver capability at release (1987).
- Known weakness: high rastertime usage.

Data limits per compiled file:
- 26 songs, 32 instruments.
- Note lengths in hex 1–$20 (1–32 frames at current tempo).
- Tempo: 16-bit fractional counter; carry = note advance.

---

## §2  Address Distribution (HVSC #84, 288 tunes)

| init_addr | play_addr | count | class |
|-----------|-----------|-------|-------|
| $C600 | $C603 | 120 | Standard canonical (VBI, song# in A) |
| $C600 | $C666 | 19 | Multi-song, song-select at $C666 |
| $CE60 | $C666 | 14 | Player relocated to $CE60, play at $C666 |
| $C601 | $C666 | 8 | Variant init at +1 |
| $6600 | $6603 | 6 | Player relocated to $6600 |
| $C601 | $C64E | 5 | Alternative play entry |
| $7A00 | $7A03 | 2 | Relocation to $7A00 |
| $7C00 | $7C03 | 2 | Relocation to $7C00 |
| $9600 | $9603 | 1 | Relocation to $9600 |
| various | various | ~111 | Heavily modified / full relocation |

**Play-address low-byte distribution** (all 288): `$03` = 137 tunes,
`$66` = 86 tunes, `$4E` = 11 tunes. The `$?666` / `$?66` play address
is the song-select entry — it is what PRG2SID uses as its detection scan
target ("scan whole file for `AD xx xx 30 03 D0 22 60 18 29 7F A2`,
usually at $C666").

The canonical form is `init=$C600 / play=$C603`. Relocations are true
relocations — same player code, different base address. The relationship
init+3 = play holds for all standard instances.

---

## §3  $C600 Layout — Canonical Player (from Fire_Breath.sid)

Disassembly is from `hvsc84/GAMES/A-F/Fire_Breath.sid`
(load=$BBBE, size=$13B0 / 5040 bytes, addresses $BBBE–$CF6D).

```
$C600: 4C 06 C6       JMP $C606     ; INIT ENTRY (PSID calls with A=song#)
$C603: 4C 19 C6       JMP $C619     ; PLAY ENTRY (PSID calls each VBI)

; --- Init body ---
$C606: 18             CLC
$C607: 69 80          ADC #$80       ; song-index = (A + $80), so song 0 -> $80
$C609: 8D 1D C7       STA $C71D      ; store effective song index in state
$C60C: A2 00          LDX #0
$C60E: A9 00          LDA #0
$C610: 9D 00 D4       STA $D400,X    ; zero all 32 SID registers ($D400-$D41F)
$C613: E8             INX
$C614: E0 20          CPX #$20
$C616: D0 F6          BNE $C610
$C618: 60             RTS

; --- Play dispatcher ---
$C619: A5 01          LDA $01        ; save CPU banking register
$C61B: 48             PHA
$C61C: A9 36          LDA #$36       ; BASIC off, KERNAL off, I/O on
$C61E: 85 01          STA $01
$C620: 20 66 C6       JSR $C666      ; call main play body
$C623: 68             PLA
$C624: 85 01          STA $01        ; restore banking
$C626: 60             RTS
```

Notes on the init:
- The `CLC; ADC #$80` maps song 0→$80, song 1→$81, …, song 25→$99.
  The high bit distinguishes "valid song" from end-of-list.
- SID registers are zeroed in the init, not hard-restarted via test bit.
- Banking: play body saves/restores `$01` — important if called from contexts
  where I/O might be mapped out.

---

## §4  $C666 Song-Select Entry Point

```
$C666: AD 1D C7       LDA $C71D      ; current song index state
$C669: 30 03          BMI $C66E      ; negative = wraparound/invalid -> branch
$C66B: D0 22          BNE $C68F      ; nonzero = already-init'd -> jump to play loop
$C66D: 60             RTS            ; zero = invalid -> bail out

; (song-advance / new-note code path when BNE taken skips to main loop)
; If BMI taken (song re-init path):
$C66E: 18             CLC
$C66F: 29 7F          AND #$7F       ; mask sign bit off song number
$C671: A2 02          LDX #2         ; X = 2 (voice index, descends 2→1→0)
$C673: 7D 2F C7       ADC $C72F,X    ; add per-voice sequence offset from song table
$C676: A8             TAY            ; Y = voice sequence offset
$C677: 20 D8 C6       JSR $C6D8      ; per-voice note handler
$C67A: CA             DEX
$C67B: 8E 72 C6       STX $C672      ; store voice index (used by routines)
$C67E: 10 ED          BPL $C66E      ; loop: voices 2 → 1 → 0
```

PRG2SID detection pattern for this entry point (byte-exact at $C666):
```
AD ?? ??  30 03  D0 22  60  18  29 7F  A2
```
= `LDA abs; BMI +3; BNE +$22; RTS; CLC; AND #$7F; LDX #`

---

## §5  Per-Frame Write Model

### 5.1  Voice update order

**Voices are updated in REVERSE order: 2, 1, 0** (X register counts down
from 2 to 0 using BPL loop). Filter/vol writes come after all three voices.

### 5.2  Tempo model

A 16-bit fractional counter at `$C71B` (lo) / `$C71C` (hi) is incremented
each VBI frame. Carry out of the 16-bit add triggers a "song advance" (new
note for each voice whose duration has expired). This gives fractional-tempo
control — the effective BPM is determined by the increment value stored in
the song table.

### 5.3  Normal frame (no note advance — most frames)

For each voice X in {2, 1, 0}:
1. Load `$C79B,X` (gate state byte). If bit7=0 (note in progress):
   - JSR $CB5A (effect updater — see §6)
   - Effect updater writes freq_lo/hi and optionally PW if effects are active.

After all three voices:
- `STA $D418` — master vol + filter mode
- `STA $D416` — filter cutoff hi
- `STA $D417` — filter res + voice routing

### 5.4  Note-advance frame (tempo carry)

For each voice X in {2, 1, 0} where `$C79B,X` bit7=1 (new note pending):
1. Decrement `$C7A7,X` (duration counter). If expired → advance sequence.
2. JSR $C7C5 (note-start handler):
   - Clear gate: `STA $D404,Y` with value 0 (Y = voice SID offset: 0, 7, or 14)
   - Load new instrument → compute initial PW, AD, SR, waveform
   - `STA $D406,Y` — write SR (sustain+release)
   - `STA $D405,Y` — write AD (attack+decay)
   - `STA $D403,Y` — write PW hi
   - `STA $D402,Y` — write PW lo
   - `STA $D404,Y` — write ctrl/waveform with gate=1
   - `STA $D400,Y` — write freq lo
   - `STA $D401,Y` — write freq hi

After all three voices: same filter/vol writes as normal frame.

**Write order per note-start (within one voice Y):**
```
$D404+Y = $00        (gate clear)
$D406+Y = SR value   (sustain/release)
$D405+Y = AD value   (attack/decay)
$D403+Y = PW hi
$D402+Y = PW lo
$D404+Y = ctrl|gate  (waveform + gate bit = 1)
$D400+Y = freq lo
$D401+Y = freq hi
```

Then after all voices: `$D418`, `$D416`, `$D417`.

### 5.5  Gate handling

- No test-bit hard-restart observed in register writes.
- Gate clear and gate set happen in the SAME frame (note-start frame): first
  `$D404,Y = $00` (gate=0), then `$D404,Y = waveform | $01` (gate=1).
- Gate clear is done via a dedicated subroutine at $C7B6 (the SIDId signature
  match point):
  ```
  $C7B6: A9 00         LDA #0
  $C7B8: 9D 9B C7      STA $C79B,X    ; clear gate state byte
  $C7BB: BC 2C C7      LDY $C72C,X    ; Y = SID voice offset
  $C7BE: 99 04 D4      STA $D404,Y    ; write ctrl=0 (gate=0, waveform=0)
  $C7C1: 60            RTS
  ```

### 5.6  Per-voice SID offset table

`$C72C,X` maps voice X to its SID Y-offset:
- X=0 (voice 1): Y=0  → $D400
- X=1 (voice 2): Y=7  → $D407
- X=2 (voice 3): Y=14 → $D40E

All SID writes are Y-indexed (`STA $D4xx,Y`) giving voice-generic code.

---

## §6  Effect Mechanisms

### 6.1  Logarithmic Vibrato (per frame)

State per voice:
- `$C747,X` / `$C74A,X`: current freq lo/hi (accumulator)
- `$C771,X`: direction byte (bit7=0 ascending, bit7=1 descending)
- `$C7AA,X`: steps-taken counter
- `$C76B,X`: half-period (steps before direction flip)

Algorithm (CB5A / CB85 region):
```
delta = |freq(current_note) - freq(current_note - 1 semitone)|
  (computed using the freq table at ~$C962/$C963)

Each frame:
  if direction == ascending:
    freq_lo += delta_lo  (16-bit add with carry)
    freq_hi += delta_hi + carry
    if counter >= half_period: flip direction, reset counter
    else: counter++
  else (descending):
    freq_lo -= delta_lo  (16-bit subtract)
    freq_hi -= delta_hi - borrow
    (similar limit/flip logic)
```

The delta is computed from the adjacent-note frequency difference. This
naturally scales: the same vibrato depth setting sounds the same number of
cents at all octaves (logarithmic vibrato). This was a signature feature —
linear vibrato (adding a fixed Hz delta) sounds narrower in high octaves and
wider in low ones.

After vibrato adjustment: the updated freq lo/hi is written to `$D400,Y` /
`$D401,Y` at CB8D area each frame.

### 6.2  Pulse Width Modulation (per frame)

State per voice:
- `$C753,X` / `$C756,X`: current PW lo/hi
- `$C774,X`: PWM delta (speed; 0 = PWM disabled)
- `$C77D,X`: direction byte (bit7 = direction)
- `$C780,X`: delay counter (skip N frames before starting)
- `$C777,X`: upper PW limit (hi byte)

Algorithm (CBD8 region):
```
if $C774,X == 0: skip PWM entirely
if $C780,X > 0: DEC $C780,X; skip this frame

if ascending:
  PW += delta   (16-bit add)
  if PW_hi >= upper_limit: flip direction
else (descending):
  PW -= delta
  if PW_hi <= lower_limit: flip direction

Write $D402,Y = PW_lo;  $D403,Y = PW_hi
```

Symmetric triangle sweep between configurable limits. Limits appear to be
instrument-defined per voice.

### 6.3  Echo — Per-Note Sustain Oscillation (per note event, not per frame)

The echo effect modulates the SR (sustain+release) register at each new note
event, causing the sustain level to step up or down on successive notes,
giving the impression of notes echoing at decreasing volume.

State per voice:
- `$C783,X`: current SR byte value
- `$C786,X`: echo delta (0 = echo disabled)
- `$C78C,X`: upper SR limit
- `$C78F,X`: lower SR limit
- `$C7B0,X`: direction byte (bit7 = direction)
- `$C792,X`: echo countdown / delay

Algorithm (CC48 region):
```
At each note trigger (or periodically per frame — code checks $C792 delay):
  if $C786,X == 0: no echo
  if delay > 0: DEC delay; skip
  if ascending:
    SR += delta
    if SR >= upper_limit: flip direction
  else:
    SR -= delta
    if SR <= lower_limit: flip direction
  STA $D406,Y  <- write SR with new sustain value
```

The echo is NOT a delay-line — it is not feeding audio back. It is a
sustain-level modulation: each note's decay envelope has a different sustain
floor, producing a staircase of volumes that audibly resembles an echo decay.

### 6.4  Waveform Swap (per note event)

Each voice has a waveform-swap table offset (`$C73E,X`). On certain note
events, the table at `$C507` (instrument table region) provides a new
waveform byte that overrides the instrument's default ctrl byte. This enables
per-note waveform morphing (e.g., pulse → triangle per note sequence).

Code (CC88 region):
```
LDY $C73E,X         ; waveform table index
LDA $C507,Y         ; load from table
BEQ (skip)          ; 0 = no swap
LSR;LSR;LSR;LSR     ; shift to extract waveform type bits
AND #$07            ; mask to 3 bits (0-7 waveform selector)
STA $C720           ; store as new ctrl byte
```

### 6.5  Wavetable Drums (per frame during drum decay)

Eight fixed drum sounds are stored as wavetable sequences in a global table
at `$CF00`. Each drum is identified by its START OFFSET within this table.

Drum table entry format — two types, distinguished by bit7 of first byte:

**Type 1 — Waveform change (bit7=1):**
```
byte[0]: ctrl/waveform byte (bit7=1, so SID ctrl = 0x80..0xFF)
byte[1]: freq_hi value
(2 bytes total per entry)
```
Each frame: write `$D401,Y = freq_hi`; `$D404,Y = ctrl`.

**Type 2 — Frequency slide (bit7=0):**
```
byte[0]: ctrl byte (any value, bit7=0)
byte[1]: freq_lo_delta (16-bit subtracted from current freq)
byte[2]: freq_hi_delta
(3 bytes total per entry)
```
Each frame: freq -= (freq_hi_delta:freq_lo_delta); then write freq + ctrl.

**End marker: $FF** → drum sequence done; fall through to normal note path.

The drum wavetable at $CF00 (from Fire_Breath.sid):
```
CF00: 43 00 04 41 00 03 40 00 02 40 00 01 40 00 02 40
CF10: 00 01 40 00 01 40 00 01 40 00 01 80 F0 FF 81 F0
CF20: 41 00 02 80 F0 40 00 02 80 F0 40 00 02 80 F0 40
CF30: 00 02 80 F0 40 00 02 80 F0 40 00 02 80 F0 FF 04
```

Reading this as 2-byte (type 1) entries and 3-byte (type 2) entries:
- Frames 0-1: ctrl=$43 (pulse+triangle+gate), freq_hi=$00 (hit)
- Frame 2-3: ctrl=$41 (triangle+gate), freq_hi=$00 (decay start)
- Frames 4+: ctrl=$40 (triangle, gate=0), freq_hi descending
- Later: ctrl=$80 (noise burst), freq_hi=$F0 (noise transient)
- $FF end marker → fall through

The 8 drum sounds start at different offsets into CF00, giving distinct
timbres by entering the sequence at different points. Drum 0 starts at
offset 0 (full sequence), drum 1 at offset 3, etc.

---

## §7  Memory State Map (per voice, X=0,1,2)

Reconstructed from Fire_Breath.sid. All addresses are relative to
player base at $C600 (i.e., base=$C600 for canonical build).

| Address | Width | Purpose |
|---------|-------|---------|
| $C71B | 1 | Song tick counter lo (tempo increment accumulator) |
| $C71C | 1 | Song tick counter hi |
| $C71D | 1 | Current song index ($80..$99 = songs 0..25; $FF = end) |
| $C71E | 1 | Current SID voice offset Y (0, 7, or 14) |
| $C720 | 1 | Ctrl/waveform byte staging |
| $C722 | 1 | Filter mode OR mask for $D418 |
| $C723 | 1 | Filter res+route ($D417 value) |
| $C724 | 1 | Filter cutoff hi ($D416 value) |
| $C725 | 1 | Master vol + filter mode ($D418 base value) |
| $C72C,X | 1×3 | Per-voice SID Y-offset (values: 0, 7, 14) |
| $C72F,X | 1×3 | Per-voice sequence-pointer offset in song table |
| $C735,X | 1×3 | Per-voice drum/wavetable table index |
| $C738,X | 1×3 | Per-voice glide freq_hi accumulator |
| $C73B,X | 1×3 | Per-voice glide freq_lo accumulator |
| $C73E,X | 1×3 | Per-voice waveform-swap table index |
| $C741,X | 1×3 | Per-voice waveform-pending flag |
| $C744,X | 1×3 | Per-voice drum type byte staging |
| $C747,X | 1×3 | Per-voice freq lo current value |
| $C74A,X | 1×3 | Per-voice freq hi current value |
| $C74D,X | 1×3 | Per-voice (unknown — zeroed on note init) |
| $C750,X | 1×3 | Per-voice (unknown — zeroed on note init) |
| $C753,X | 1×3 | Per-voice PW lo current value |
| $C756,X | 1×3 | Per-voice PW hi current value |
| $C762,X | 1×3 | Per-voice note-data stream Y-offset |
| $C765,X | 1×3 | Per-voice active/muted flag (0=muted → skip) |
| $C76B,X | 1×3 | Per-voice vibrato half-period (frames per direction) |
| $C76E,X | 1×3 | Per-voice note duration countdown |
| $C771,X | 1×3 | Per-voice vibrato direction (bit7) |
| $C774,X | 1×3 | Per-voice PWM delta (0=disabled) |
| $C777,X | 1×3 | Per-voice PWM upper limit (hi byte) |
| $C77A,X | 1×3 | Per-voice PWM lower limit (hi byte) |
| $C77D,X | 1×3 | Per-voice PWM direction byte |
| $C780,X | 1×3 | Per-voice PWM start delay |
| $C783,X | 1×3 | Per-voice echo current SR value |
| $C786,X | 1×3 | Per-voice echo delta (0=disabled) |
| $C78C,X | 1×3 | Per-voice echo upper SR limit |
| $C78F,X | 1×3 | Per-voice echo lower SR limit |
| $C792,X | 1×3 | Per-voice echo countdown |
| $C795,X | 1×3 | Per-voice instrument index |
| $C798,X | 1×3 | Per-voice waveform-pending flag (set $80 on new note) |
| $C79B,X | 1×3 | Per-voice gate state: bit7=1 = new note pending |
| $C79E,X | 1×3 | Per-voice waveform-pending flag (second copy) |
| $C7A1,X | 1×3 | Per-voice cached AD byte |
| $C7A7,X | 1×3 | Per-voice duration counter |
| $C7AA,X | 1×3 | Per-voice vibrato steps-taken counter |
| $C7B0,X | 1×3 | Per-voice echo direction byte |
| $CF00–$CF3F | 64 | Global drum wavetable (all 8 drums) |

Song/instrument data lives BELOW the player (e.g., $BBBE–$C5FF in
Fire_Breath), in the `$C0xx`–`$C5xx` range:
- `$C0xx`, `$C1xx`: sequence note streams
- `$C2xx`–`$C5xx`: instrument parameter tables

---

## §8  SIDId Signatures

### cadaver/sidid.cfg

Single entry (no sub-versions):
```
Ubik's_Musik
A9 00 9D ?? ?? BC ?? ?? 99 04 D4 60 4C ?? ?? DE ?? ?? 10 F8 BC ?? ?? 8C ?? ?? A9 00 9D ?? ?? 9D ?? ?? A9 FF 9D ?? ?? BC ?? ?? BD ?? ?? 85 ?? BD END
```

Decoded (relative to match point at $C7B6):
```
+00: A9 00         LDA #0
+02: 9D ?? ??      STA $C79B,X    ; clear gate state byte
+05: BC ?? ??      LDY $C72C,X    ; Y = voice SID offset
+08: 99 04 D4      STA $D404,Y    ; GATE=0 write (*** the STA $D404,Y that SIDId anchors on)
+0B: 60            RTS
+0C: 4C ?? ??      JMP $CB5A      ; jump to play body
+0F: DE ?? ??      DEC $C7A7,X    ; DEC per-voice duration counter
+12: 10 F8         BPL $C7C2      ; BPL loop (still counting -> play)
...
+3F: A9 ??         LDA #vol       ; (final section: $D418 write path)
+41: D0 04         BNE +4
+43: 8D 18 D4      STA $D418      ; write master vol
+46: 60            RTS
+47: A9 ??         LDA #vol
+49: 8D 18 D4      STA $D418      ; (alternate vol write path)
```

The signature anchors on the gate-clear subroutine at $C7B6.

### WilfredC64/player-id (sidid.cfg)

Identical signature, single entry:
```
Ubik's_Musik
A9 00 9D ?? ?? BC ?? ?? 99 04 D4 60 4C ?? ?? DE ?? ?? 10 F8 BC ?? ?? 8C ?? ?? A9 00 9D ?? ?? 9D ?? ?? A9 FF 9D ?? ?? BC ?? ?? BD ?? ?? 85 ?? BD ?? ?? 85 ?? C8 B1 ?? C9 FF D0 E1 9D ?? ?? 60 A9 ?? D0 04 8D 18 D4 60 A9 ?? 8D 18 D4
```

(Extended vs. cadaver — includes the $D418 write tail and per-voice
note-stream scan loop at the end.)

No sub-version entries in either sidid.cfg. One signature covers all
288 tunes — consistent with a single compiled player at different base
addresses (all use the same code, just relocated).

---

## §9  Tool Handling

### PRG2SID v1.26 (iAN CooG)

Detection: scans whole file for the pattern
```
AD ?? ??  30 03  D0 22  60  18  29 7F  A2
= LDA abs; BMI +3; BNE +$22; RTS; CLC; AND #$7F; LDX #
```
usually at $C666 (the song-select entry point).

On detection: patches an `init/play` routine at $C600/$C603 (adds "code
for init/play (4)"). This handles the multi-song tunes that have a song-select
entry at $C666 but no standard $C600/$C603 dispatch.

### DeepSID (Chordian)

No Ubik-specific player handling. DeepSID uses the SIDId engine label for
display metadata only. Playback routes through the standard emulator backends
(WebSid / reSIDfp). No special code path for Ubik's Musik.

### libsidplayfp / VICE / sidplayfp

No Ubik-specific handling. These emulators are player-agnostic (they execute
the PSID's init/play entry points via the 6502 emulator). Ubik tunes play
correctly from the standard PSID header.

### HVSC STIL.txt

No STIL entries for Ubik's Musik tunes were found (searched for "Korn" and
"Ubik" in $HVSC/DOCUMENTS/STIL.txt — no matches). No special per-tune notes
in HVSC documentation.

---

## §10  Per-Frame D4xx Write Summary

This is the register-write order expected in a writelog for a canonical
Ubik's Musik frame:

**Ordinary frame (no note advance, all voices active):**
```
per voice (order: V3, V2, V1):
  $D400+Y  freq_lo   (if vibrato/glide active)
  $D401+Y  freq_hi   (if vibrato/glide active)
  $D402+Y  PW_lo     (if PWM active)
  $D403+Y  PW_hi     (if PWM active)
  [no $D404 write unless drum wavetable active]
  [drum active: $D401+Y freq_hi; $D404+Y ctrl -- from wavetable]

after voices:
  $D418    vol+mode
  $D416    filter cutoff hi
  $D417    filter res+routing
```

**Note-start frame:**
```
per voice (order: V3, V2, V1) for each voice with new note:
  $D404+Y  = $00          (gate clear)
  $D406+Y  = SR byte      (new sustain/release)
  $D405+Y  = AD byte      (new attack/decay)
  $D403+Y  = PW_hi        (from instrument)
  $D402+Y  = PW_lo        (from instrument)
  $D404+Y  = ctrl|$01     (waveform + gate=1)
  $D400+Y  = freq_lo
  $D401+Y  = freq_hi

after voices:
  $D418    vol+mode
  $D416    filter cutoff hi
  $D417    filter res+routing
```

Note: `$D415` (filter cutoff lo) was NOT observed in the write scan —
only `$D416` (cutoff hi) and `$D417` (res+routing) appear. This may
mean the filter cutoff is only 8-bit in Ubik's Musik (hi byte only), or
that `$D415` is set to zero during init and not updated.

---

## §11  Unanswered Questions / Gaps

1. **Two-voice + SFX mode**: The manual says game programmers can call the
   driver to play on 2 voices with SFX on the 3rd. The specific API
   (register, entry point, or song index convention) for SFX mode is unknown.
   Likely a special song index value or separate entry point.

2. **Song data format**: The note stream at `$C0xx`/$C1xx and the instrument
   tables at `$C2xx`–$C5xx were not fully decoded. Specifically:
   - Exact note byte encoding (is it a note number + duration packed, or two bytes?)
   - Instrument parameter layout (AD, SR, waveform, vibrato depth, PWM settings,
     echo delta — what offset within the instrument record?)
   - The 8 drum IDs and their offsets into $CF00

3. **$D415 writes**: Not observed in Fire_Breath.sid. Needs confirmation:
   does Ubik's Musik ever write the filter cutoff LO byte?

4. **Echo timing**: The echo seems to fire on note events but the exact timing
   relative to gate/freq writes within the note-start frame sequence is not
   fully confirmed. The $C792 countdown suggests it can fire on arbitrary
   frames (once per N ticks), not necessarily synchronized to note events.

5. **Relocations**: Are the >100 "other" tunes in the HVSC truly relocated
   player instances (same binary, different base), or do some represent
   modified/patched players with different state variable layouts?

6. **Sub-versions**: SIDId has only ONE signature for all 288 tunes. No
   sub-version variants are known. But the heavy relocation diversity may
   hide version differences that share the same code fingerprint.

7. **Waveform table format at $C507**: The waveform-swap table was identified
   but not fully decoded. What are the valid values, what triggers an entry?

---

## Leads to Follow

1. **Full instrument table decode**: Load Ubik's Musik editor in VICE,
   create a known instrument, save PRG, hexdump the $C2xx-C5xx region
   to reverse the exact per-instrument layout.

2. **Drum offset table**: The 8 drum IDs must map to offsets into $CF00.
   Find the drum-ID-to-offset table (probably 8 bytes stored near $C71x
   or in the song data area).

3. **Note stream format**: Use voice_writelog.py on a known simple tune
   (single note + rest) to confirm the note byte encoding. Alternatively,
   compare the $C0xx bytes in two tunes with known notes.

4. **CSDb Ubik's Musik disassembly request**: No published disassembly exists
   as of 2026-06-14. A CSDb post request or direct contact with iAN CooG
   (who wrote PRG2SID Ubik detection) may yield unpublished notes.

5. **Multi-song tune analysis**: Pick a known multi-song tune
   (e.g., Die_Alien_Slime: 18 subtunes) and trace the $C666 init path
   for song selection vs. the simple CLC/ADC/STA path at $C600.

6. **SFX mode**: Examine a game using Ubik for SFX (e.g., Thrust II —
   init=$9000, play=$A666) to find the SFX API.
