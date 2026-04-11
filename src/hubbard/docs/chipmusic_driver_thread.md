---
source_url: https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/
fetched_via: wayback 2023-04-27
fetch_date: 2026-04-11
author: multiple (4mat, neilbaldwin, logikstate, others; primary technical doc by Anthony McSweeney)
content_date: 2010-05-23
reliability: secondary
---
# Rob Hubbard's Music Driver (C64) — chipmusic.org Thread Archive

**Source:** https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/
**Archived via Wayback Machine:** https://web.archive.org/web/20230427162234/https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/
**Thread date:** May 23, 2010 (31 posts across 2 pages)

---

## Thread Summary

The thread was started by 4mat (Mat/Cosine) linking to the documented disassembly of the Monty on the Run driver. The key technical resource is the linked text file:

**Primary technical reference:** http://www.1xn.org/text/C64/rob_hubbards_music.txt

The full text of that document is reproduced below (Section 2). The forum posts themselves are mostly historical discussion with a few technical nuggets (Section 1).

---

## Section 1: Forum Thread Posts

### Post 1 — 4mat (May 23, 2010)
> Documented source of the 'Monty on the run' driver:
> http://www.1xn.org/text/C64/rob_hubbards_music.txt
>
> While later players have taken more of a table-based approach to instruments, the basics of most drivers can still be linked back to these '80s ones. Hubbard's driver was also hacked by other musicians but it has such a distinctive sound you can usually tell.

Links posted:
- Rob Hubbard's SID Music (fairly complete collection as a demo, with some inaccuracies)
- Hubbard's driver with hacked editor

### Post 3 — 4mat (May 23, 2010)
> Yeah Hubbard did it all in assembler afaik... can you imagine the incredible patience doing 12 minute songs like Kentilla or Delta that way?

### Post 7 — 4mat (May 23, 2010)
> I think Rob mentioned in an interview he'd have the driver running and then tweak parameters on the fly to improve the song as it played. It would be kinda the same as having an editor framework on screen, you're just changing hex bytes in a monitor.
>
> Thinking about it there weren't really any 'serious' music editors in '84-'85 where you could a) get the music out in a useable form and b) have data small enough to fit in a game. I can only think of Master Composer from that time... Going forward a bit Electrosound appeared in '85, followed by SoundMonitor, RockMonitor and then the flood of editors like Future Composer.

### Post 13 — neilbaldwin (May 30, 2010)
> When I wrote my (rather ropey) C64 drivers, I studied Rob's code in a disassembler for a long time, figuring out how he did it. Then I pretty much copied what he'd done, like most other music programmers back then. Later on I made myself a little instrument editor which let me tweak sound parameters and dump the numbers out to include in the assembly file.
>
> I did all my NES music in an assembler in the same way.
>
> cTrix - I think the most impressive C64 music routine in terms of features and efficiency is Geir Tjelta's "Macroplayer". Don't know if he ever released it but he sent me one of Jeroen Tel's old tunes that he'd converted to use the Macroplayer and it was using about 9 scan lines or something mental like that.

### Post 21 — logikstate (Jan 13, 2011)
> Based on that disassembly I've created a C version of Rob's Replay and hooked it up to a SID emulator. I then put the replay into a clone of ProTracker and then wrote a ripper that will rip quite a lot of Rob's tunes and even those not written by Rob himself (but using his replay).

### Post 24 — logikstate (Jan 14, 2011) — KEY TECHNICAL POST
> The core of Rob's replay is pretty much the same. By the core I mean the part that decodes the notes and triggers them. Later songs start to differ: International Karate was able to transpose patterns to save memory. Ace II uses arpeggio tables but I haven't set about looking at the changes in the later replays just yet.
>
> Basically each instrument can have a number of effects applied to them, a bit like routing the sound through different patches. There is a Pulse patch, octave arpeggio patch, skydive patch etc.
>
> These different fx were changed slightly with each tune, basically just tweaking the parameters.
>
> Its possible to collate all these tweaks and make a new replay (which is what I've started) which would play all Rob's tunes. The instruments could then be represented on screen like an effects chain in Ableton from left to right. Some of the fx shared parameters with each other as they used the same byte in memory. This could be represented by 'syncing' pairs of fx modules together in the chain.

**Key insight:** The `instrfx` byte (byte 7 of instrument) drives an effects chain. Different songs tweak these parameters differently. Later variants (Ace II) add arpeggio tables.

---

## Section 2: Full Technical Document

**"Rob Hubbard's Music: Disassembled, Commented and Explained"**  
by Anthony McSweeney (u882859@postoffice.utas.edu.au)  
Source: http://www.1xn.org/text/C64/rob_hubbards_music.txt

---

### Introduction

Rob Hubbard created a superb music routine from the very first tune released (Confuzion). He used this routine (with slight modifications) for a very long time. The source presented was used in: Confuzion, Thing on a Spring, Monty on the Run, Action Biker, Crazy Comets, Commando, Hunter Patrol, Chimera, The Last V8, Battle of Britain, Human Race, Zoids, Rasputin, Master of Magic, One Man & His Droid, Game Killer, Gerry the Germ, Geoff Capes Strongman Challenge, Phantoms of the Asteroids, Kentilla, Thrust, International Karate, Spellbound, Bump Set and Spike, Formula 1 Simulator, Video Poker, Warhawk or Proteus, and many more.

This particular routine was ripped from Monty on the Run, appearing in memory from $8000 to about $9554. The routine is ~900-1000 bytes of code.

---

### How to Use the Routine (API)

```
jsr music+0   ; initialize — accumulator = music number
jsr music+3   ; play (call at 50Hz from IRQ)
jsr music+6   ; stop and silence SID
```

The music runs at 50Hz (PAL). NTSC runs at 60Hz and will sound too fast unless the CIA is reprogrammed.

---

### Data Format Overview

#### 1. Module → Songs → Tracks → Patterns → Notes

**Songs:** A module contains one or more songs. Each song has 3 tracks (one per SID voice). Song table at label `songs`: 6 bytes per song (lo/hi pointers for each of 3 tracks).

**Tracks:** A list of pattern numbers in play order. Terminated by:
- `$FF` = loop (restart from beginning)
- `$FE` = play once (stop)

The current position in a track is called the "position" for that track.

**Patterns:** Sequence of note events, terminated by `$FF`. When `$FF` is reached, advance to next pattern in track.

---

#### 2. Note Byte Format (1–4 bytes per note)

**Byte 1 (always present): length + flags**
```
Bits [4:0] = length of note (0–31)
Bit  5     = no-release flag (skip gate-off)
Bit  6     = append flag (no attack — continue from previous note)
Bit  7     = instrument/portamento byte follows (1 = yes)
```

**Byte 2 (optional, present if bit 7 of byte 1 is set):**
```
If positive ($00–$7F): new instrument number
If negative ($80–$FF): portamento (bit 0 = direction: 0=up, 1=down;
                        bits [6:1] = portamento speed)
```

**Byte 3: pitch**
```
0 = lowest C. Each semitone = +1. C-1=$00, C#1=$01, ..., C-6=$48 ($72=c-6+)
```

**Byte 4: implicit** — checked to be `$FF` for end-of-pattern detection.

**Examples:**
```
$84,$04,$24  → length=4, new instrument=4, pitch=$24 (c-3)
$D6,$98,$25,$FF → length=22, append, portamento up speed=24, pitch=$25 (c#3), end-of-pattern
```

Note format explanation:
- `$D6` = `1101 0110` → bit7=1 (2nd byte follows), bit6=1 (append), bit5=0, length=$16=22
- `$98` = `1001 1000` → negative (bit7=1), portamento; bit0=0 (up), speed=`$98&$7E`=$18=24

---

#### 3. Instrument Data Structure (8 bytes per instrument)

Label: `instr` — instruments packed consecutively, 8 bytes each.

```
Byte 0: pulse width low
Byte 1: pulse width high
Byte 2: SID control register (waveform: noise=$80, pulse=$40, saw=$20, tri=$10; gate=$01)
Byte 3: attack/decay (SID $D405)
Byte 4: sustain/release (SID $D406)
Byte 5: vibrato depth (0 = no vibrato)
Byte 6: pulse speed (bits[4:0] = delay/step size; bits[7:5] = speed range $00–$1F)
Byte 7: instrument FX flags (see below)
```

**Byte 7 — FX flags (instrfx):**
```
Bit 0: DRUM
  - Bass drum: noise for 1st VBL only, then uses instrument waveform (square).
               Rapid high-to-low frequency slide with fast attack/decay.
  - Hihat/other: noise always.
  - Implementation: dec savefreqhi each frame; first frame uses noise ($80 ctrl)

Bit 1: SKYDIVE
  - Slow portamento-down from note pitch to zero frequency.
  - Every 2nd VBL: if savefreqhi != 0, dec savefreqhi.
  - Sounds like a falling pitch ("AHHHHhhhhgh").

Bit 2: OCTAVE ARPEGGIO
  - Alternates between note and note+12 (one octave up) each VBL.
  - Even frames: play notenum; odd frames: play notenum+12.

Bits 3–7: unused in the Monty driver. Used in later music for additional FX.
```

**Note on drums (bit 0):** The drum timbre depends on the control register (byte 2):
- ctrl=0: noise always (hihat style)
- ctrl=X: noise for 1st VBL, then X (square wave for bass drum feel)

---

#### 4. Frequency Table (`frequenzlo` / `frequenzhi`)

Full chromatic scale from C-0 upwards, 16-bit little-endian frequency values for SID $D400/$D401:

```
frequenzlo .byt $16
frequenzhi .byt $01
; C-0: $0116
 .byt $27,$01,$38,$01,$4b,$01  ; C#0, D0, D#0
 .byt $5f,$01,$73,$01,$8a,$01,$a1,$01  ; E0, F0, F#0, G0
 .byt $ba,$01,$d4,$01,$f0,$01,$0e,$02  ; G#0, A0, A#0, B0
 .byt $2d,$02,$4e,$02,$71,$02,$96,$02  ; C-1...
 .byt $bd,$02,$e7,$02,$13,$03,$42,$03
 .byt $74,$03,$a9,$03,$e0,$03,$1b,$04
 .byt $5a,$04,$9b,$04,$e2,$04,$2c,$05
 .byt $7b,$05,$ce,$05,$27,$06,$85,$06
 .byt $e8,$06,$51,$07,$c1,$07,$37,$08
 .byt $b4,$08,$37,$09,$c4,$09,$57,$0a
 .byt $f5,$0a,$9c,$0b,$4e,$0c,$09,$0d
 .byt $d0,$0d,$a3,$0e,$82,$0f,$6e,$10
 .byt $68,$11,$6e,$12,$88,$13,$af,$14
 .byt $eb,$15,$39,$17,$9c,$18,$13,$1a
 .byt $a1,$1b,$46,$1d,$04,$1f,$dc,$20
 .byt $d0,$22,$dc,$24,$10,$27,$5e,$29
 .byt $d6,$2b,$72,$2e,$38,$31,$26,$34
 .byt $42,$37,$8c,$3a,$08,$3e,$b8,$41
 .byt $a0,$45,$b8,$49,$20,$4e,$bc,$52
 .byt $ac,$57,$e4,$5c,$70,$62,$4c,$68
 .byt $84,$6e,$18,$75,$10,$7c,$70,$83
 .byt $40,$8b,$70,$93,$40,$9c,$78,$a5
 .byt $58,$af,$c8,$b9,$e0,$c4,$98,$d0
 .byt $08,$dd,$30,$ea,$20,$f8,$2e,$fd
```

Pitch $00 = C-0 ($0116). Each note = +1. Pitch $0C = C-1. Pitch $24 = C-3. Pitch $48 = C-6.

---

### SID Register Layout (per-channel offsets)

```
regoffsets .byt $00,$07,$0e
```

Voice 1: base $D400 (offset $00)
Voice 2: base $D407 (offset $07)
Voice 3: base $D40E (offset $0E)

Per-voice registers (relative to base):
```
+$00/$01: frequency lo/hi
+$02/$03: pulse width lo/hi
+$04:     control register
+$05:     attack/decay
+$06:     sustain/release
```

---

### Player Variables (zero-page / RAM)

```
regoffsets  [3]    channel register offsets ($00, $07, $0E)
tmpregofst  [1]    current channel reg offset (scratch)
posoffset   [3]    current position (pattern index) per channel
patoffset   [3]    current byte offset within current pattern, per channel
lengthleft  [3]    frames remaining for current note, per channel
savelnthcc  [3]    saved 1st note byte (length + flags) per channel
voicectrl   [3]    current control register value per channel
notenum     [3]    current pitch number per channel
instrnr     [3]    current instrument number per channel
appendfl    [1]    append flag ($FF = no append, $00 = append)
templnthcc  [1]    temp for 1st byte processing
tempfreq    [1]    temp frequency lo
tempstore   [1]    scratch
tempctrl    [1]    temp control reg
vibrdepth   [1]    vibrato depth from instrument
pulsevalue  [1]    pulse speed from instrument
tmpvdiflo/hi[2]    freq difference for vibrato calculation
tmpvfrqlo/hi[2]    freq workspace for vibrato
oscilatval  [1]    vibrato oscillator value (01233210 pattern)
pulsedelay  [3]    pulse width delay counter per channel
pulsedir    [3]    pulse width direction (0=up, 1=down) per channel
speed       [1]    current speed counter
resetspd    [1]    speed divisor (default 1 — every frame)
instnumby8  [1]    instrument number * 8 (cache)
mstatus     [1]    music status: $00=playing, $40=init, $80=stopped, $C0=stop+silence
savefreqhi  [3]    saved frequency hi per channel (used by drum/skydive)
savefreqlo  [3]    saved frequency lo per channel (used by portamento)
portaval    [3]    portamento value per channel
instrfx     [1]    FX flags from current instrument byte 7
pulsespeed  [1]    pulse speed masked value
counter     [1]    global VBL counter (wraps 0–255)
currtrkhi   [3]    current track pointer hi per channel
currtrklo   [3]    current track pointer lo per channel
```

---

### Player Execution Flow

#### Main Loop (once per VBL, 3 iterations — one per channel)

```
playmusic:
  inc counter
  check mstatus:
    $80/$C0 → moff (silence if $C0, else just return)
    $40     → init (clear state, set mstatus=0, fall through)
    else    → contplay

contplay:
  loop x = 2 downto 0:
    dec speed; if not reset, skip NoteWork → vibrato
    if speed reset:
      dec lengthleft[x]
      if lengthleft[x] < 0: goto getnewnote
      else: goto soundwork
```

#### NoteWork (getnewnote)

1. Read pattern number from `(currtrklo[x] + posoffset[x])`
2. If `$FF`: restart (reset posoffset, patoffset, lengthleft → loop)
3. If `$FE`: stop music
4. Load pattern pointer from `patptl[pattern] / patpth[pattern]`
5. Read byte 1: store as `savelnthcc`, extract length, check flags
6. If bit 6 (append): skip instrument load, go to fetch initial values with `appendfl=$00`
7. If bit 7: read byte 2 → instrument or portamento
8. Read pitch byte → look up frequency table → write to SID freq regs + save
9. Load instrument data (bytes 0–4) → write pulse width, control, ADSR to SID
10. Preview next byte for `$FF` (end-of-pattern): if so, advance posoffset, reset patoffset

#### SoundWork (each frame when note is active)

1. **Release:** if lengthleft==0 and no-release flag clear → gate off (`$D404&$FE`), zero ADSR
2. **Vibrato:**
   - If vibrato depth == 0: skip
   - Oscillator: `counter & $07`, if >= 4: XOR $07 → values cycle 0,1,2,3,3,2,1,0
   - Compute freq difference between notenum and notenum+1
   - Right-shift by vibrdepth to get vibrato amount
   - If note length >= 8: add oscillated amount to base freq → write to SID
3. **Pulsework:**
   - If pulse speed == 0: skip
   - Decrement pulsedelay counter; only act when it reaches 0 (reset to `speed & $1F`)
   - If pulsedir=0 (up): add `pulsespeed` to `instr[0/1,y]` (lo/hi); if hi reaches $0E → reverse
   - If pulsedir=1 (down): sub `pulsespeed`; if hi reaches $08 → reverse
   - Write updated pulse width back to instrument struct AND to SID
4. **Portamento:**
   - If portaval==0: skip
   - portaval bit 0: 0=up, 1=down
   - Add/subtract `portaval & $7E` to/from savefreqlo/hi → write to SID
5. **Drums (instrfx bit 0):**
   - If savefreqhi==0 or lengthleft==0: skip
   - First VBL of note: write current freq hi; force ctrl=$80 (noise)
   - Subsequent VBLs: dec savefreqhi; use voicectrl (allows square wave sustain)
6. **Skydive (instrfx bit 1):**
   - Every 2nd VBL (counter & $01): if savefreqhi > 0, dec savefreqhi → write to SID
7. **Octave Arpeggio (instrfx bit 2):**
   - Even counter: play notenum; odd counter: play notenum+12
   - Look up frequency for chosen pitch → write to SID

---

### Vibrato Oscillator Detail

```asm
lda counter
and #7         ; 0..7
cmp #4
bcc +
eor #7         ; 4→3, 5→2, 6→1, 7→0
+ sta oscilatval ; result: 0,1,2,3,3,2,1,0
```

The oscillating value is used to add `(freq_diff >> vibrdepth) * oscilatval` to the base frequency.

---

### Pulse Width Timbre Detail

Pulse width is stored IN the instrument data (bytes 0–1), modified in-place each frame. This means the instrument acts as a stateful oscillator. The pulse bounces between `$08xx` (minimum) and `$0Exx` (maximum). The delay between updates is `pulsevalue & $1F` frames; the step size is `pulsevalue & $E0` (top 3 bits).

---

### Song Pointer Table (songs label)

6 bytes per song: lo-ptr track1, lo-ptr track2, lo-ptr track3, hi-ptr track1, hi-ptr track2, hi-ptr track3.

Pattern pointers: `patptl[n]` (lo byte) and `patpth[n]` (hi byte) — 2 parallel arrays indexed by pattern number.

---

## Section 3: Instrument Data (Monty on the Run)

20 instruments × 8 bytes each:

```
instr:
; #0:  pw=$0980, ctrl=$41(pulse+gate), AD=$48, SR=$60, vib=3, pulse=$81, fx=$00
  .byt $80,$09,$41,$48,$60,$03,$81,$00
; #1:  pw=$0800, ctrl=$81(noise+gate), AD=$02, SR=$08, vib=0, pulse=$00, fx=$01(drum)
  .byt $00,$08,$81,$02,$08,$00,$00,$01
; #2:  pw=$02a0, ctrl=$41(pulse+gate), AD=$09, SR=$80, vib=0, pulse=$00, fx=$00
  .byt $a0,$02,$41,$09,$80,$00,$00,$00
; #3:  pw=$0200, ctrl=$81, AD=$09, SR=$09, vib=0, pulse=$00, fx=$05(drum+skydive)
  .byt $00,$02,$81,$09,$09,$00,$00,$05
; #4:  pw=$0800, ctrl=$41, AD=$08, SR=$50, vib=2, pulse=$00, fx=$04(octarp)
  .byt $00,$08,$41,$08,$50,$02,$00,$04
; #5:  pw=$0100, ctrl=$41, AD=$3f, SR=$c0, vib=2, pulse=$00, fx=$00
  .byt $00,$01,$41,$3f,$c0,$02,$00,$00
; #6:  pw=$0800, ctrl=$41, AD=$04, SR=$40, vib=2, pulse=$00, fx=$00
  .byt $00,$08,$41,$04,$40,$02,$00,$00
; #7:  pw=$0800, ctrl=$41, AD=$09, SR=$00, vib=2, pulse=$00, fx=$00
  .byt $00,$08,$41,$09,$00,$02,$00,$00
; #8:  pw=$0900, ctrl=$41, AD=$09, SR=$70, vib=2, pulse=$5f, fx=$04(octarp)
  .byt $00,$09,$41,$09,$70,$02,$5f,$04
; #9:  pw=$0900, ctrl=$41, AD=$4a, SR=$69, vib=2, pulse=$81, fx=$00
  .byt $00,$09,$41,$4a,$69,$02,$81,$00
; #10: pw=$0900, ctrl=$41, AD=$40, SR=$6f, vib=0, pulse=$81, fx=$02(skydive)
  .byt $00,$09,$41,$40,$6f,$00,$81,$02
; #11: pw=$0780, ctrl=$81, AD=$0a, SR=$0a, vib=0, pulse=$00, fx=$01(drum)
  .byt $80,$07,$81,$0a,$0a,$00,$00,$01
; #12: pw=$0900, ctrl=$41, AD=$3f, SR=$ff, vib=1, pulse=$e7, fx=$02(skydive)
  .byt $00,$09,$41,$3f,$ff,$01,$e7,$02
; #13: pw=$0800, ctrl=$41, AD=$90, SR=$f0, vib=1, pulse=$e8, fx=$02(skydive)
  .byt $00,$08,$41,$90,$f0,$01,$e8,$02
; #14: pw=$0800, ctrl=$41, AD=$06, SR=$0a, vib=0, pulse=$00, fx=$01(drum)
  .byt $00,$08,$41,$06,$0a,$00,$00,$01
; #15: pw=$0900, ctrl=$41, AD=$19, SR=$70, vib=2, pulse=$a8, fx=$00
  .byt $00,$09,$41,$19,$70,$02,$a8,$00
; #16: pw=$0200, ctrl=$41, AD=$09, SR=$90, vib=2, pulse=$00, fx=$00
  .byt $00,$02,$41,$09,$90,$02,$00,$00
; #17: pw=$0000, ctrl=$11(tri+gate), AD=$0a, SR=$fa, vib=0, pulse=$00, fx=$05(drum+skydive)
  .byt $00,$00,$11,$0a,$fa,$00,$00,$05
; #18: pw=$0800, ctrl=$41, AD=$37, SR=$40, vib=2, pulse=$00, fx=$00
  .byt $00,$08,$41,$37,$40,$02,$00,$00
; #19: pw=$0800, ctrl=$11(tri+gate), AD=$07, SR=$70, vib=2, pulse=$00, fx=$00
  .byt $00,$08,$11,$07,$70,$02,$00,$00
```

---

## Section 4: Version Differences (from logikstate's analysis)

According to post 24, variations across Hubbard songs:

| Song | Change |
|------|--------|
| International Karate | Pattern transposition added (saves memory) |
| Ace II | Arpeggio tables added (not just octave arpeggio) |
| Most songs | instrfx bits 3–7 used for additional, song-specific effects |

The "core" (note decode + trigger) is nearly identical across all versions. The differences are:
1. instrfx bit definitions change between songs
2. Some FX share memory (same byte used for two purposes, controlled by context)
3. Speed/tempo parameter changes

---

## Section 5: SID Control Register Reference

```
Bit 0: Gate (1=attack/decay/sustain, 0=release)
Bit 1: Sync
Bit 2: Ring mod
Bit 3: Test bit
Bit 4: Triangle wave
Bit 5: Sawtooth wave
Bit 6: Pulse wave
Bit 7: Noise wave
```

Common instrument ctrl values in the driver:
- `$41` = pulse + gate
- `$81` = noise + gate
- `$11` = triangle + gate
- `$21` = sawtooth + gate

---

## Notes on Driver Identification

The tell-tale identifiers of a Hubbard driver:
1. **Drum sound:** noise + rapid freq-hi decrement (savefreqhi--)
2. **Pulse timbre:** in-place modification of instrument pulse width bytes
3. **Skydive FX:** every-other-frame freq-hi decrement on sustained notes
4. **Octave arpeggio:** toggle between note and note+12 each frame
5. **Vibrato:** `counter & 7` oscillator producing 0,1,2,3,3,2,1,0 pattern
6. **Instrument structure:** exactly 8 bytes, pulse width in bytes 0-1, FX in byte 7

These patterns are present (with small variations) across all ~30+ songs using the first generation driver.
