# Rob Hubbard SID Player Engine — Research Notes

## Summary

The definitive published documentation is Anthony McSweeney's article in
**C=Hacking Issue 5 (1993)**, available at:
`http://www.ffd2.com/fridge/chacking/c=hacking5.txt`

It contains the full commented disassembly of the "Monty on the Run" driver —
Hubbard's **first music routine**, used (with small modifications) in his first
~30 songs (1985-1986). The article was written by a law student who concluded
the published code was past the copyright period.

No other published disassembly of the second or later driver variants exists
online. The C=Hacking article explicitly promised a "Second Rob Hubbard Music
Routine" article in a future issue, but the author lost internet access in
August 1993 and it was never published.

## Key Findings

### Driver Generations

sidid (the C64 player identification tool) recognizes only **one** signature
class: `Rob_Hubbard` (plus `Rob_Hubbard_Digi` for digi variants). It does NOT
distinguish between the 1985 first driver and the post-1986 second driver in
its identification — they share enough common code patterns.

The sidid.cfg signatures for Rob_Hubbard:
```
BD ?? ?? 99 ?? ?? 48 BD ?? ?? 99 ?? ?? 48 BD ?? ?? 48 BD ?? ?? 99 ?? ?? BD ?? ?? 99 END
2C ?? ?? 30 ?? 70 ?? B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4 98 38 END
AE ?? ?? AD ?? ?? 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 ?? 9D ?? ?? FE END
99 04 D4 BD ?? ?? 99 02 D4 48 BD ?? ?? 99 03 D4 48 BD ?? ?? 99 05 D4 END
2C ?? ?? 70 ?? FE ?? ?? AD ?? ?? 10 ?? C8 B1 ?? 10 ?? 9D ?? ?? 4C END
0A 0A 0A AA BD ?? ?? 8D ?? ?? BD ?? ?? 2D ?? ?? 99 04 D4 END
```

There is no published documentation of HOW MANY variants exist. From our
reverse engineering, we know at least:
- **Phase 1 (1984, Companion book driver)**: Type-in driver from Keith Bowden's
  book "The Companion to the Commodore 64" (1984 Pan Books). Hubbard's two
  earliest SIDs use this.
- **Phase 2 (1985, "first routine")**: Confuzion, Monty on the Run, Action
  Biker, Commando, etc. (~30 songs). Documented in C=Hacking Issue 5.
- **Phase 3/4 (post-1986, "second routine")**: Chain Reaction, ACE II, After 8,
  W.A.R., etc. Adds table arpeggio, nested speed counters. NOT documented.

### The C=Hacking Issue 5 Article

**Article title:** "Rob Hubbard's Music: Disassembled, Commented and Explained"
**Author:** Anthony McSweeney (u882859@postoffice.utas.edu.au)
**Source:** Ripped from Monty on the Run, memory $8000-$9554

Songs confirmed to use this driver (Phase 2):
- Confuzion, Thing on a Spring, Monty on the Run, Action Biker, Crazy Comets,
  Commando, Hunter Patrol, Chrimera, The Last V8, Battle of Britain, Human
  Race, Zoids, Rasputin, Master of Magic, One Man & His Droid, Game Killer,
  Gerry the Germ, Geoff Capes Strongman Challenge, Phantoms of the Asteroids,
  Kentilla, Thrust, International Karate, Spellbound, Bump Set and Spike,
  Formula 1 Simulator, Video Poker, Warhawk/Proteus, and more.

### Feature Set (Phase 2 Driver — confirmed from C=Hacking source)

#### Data Structures

**Song structure:**
- Module contains multiple songs (title, in-game, game-over)
- Each song has 3 track pointers (one per SID voice)
- Track = list of pattern numbers, terminated by $FF (loop) or $FE (once)
- Pattern = sequence of notes, terminated by $FF

**Note data format (up to 4 bytes):**
- Byte 1: Note length (bits 0-4 = duration 0-31)
  - Bit 5: No release (gate not cleared at note end)
  - Bit 6: Append/tie (no re-trigger, continues previous note)
  - Bit 7: Second byte present (instrument or portamento)
- Byte 2 (optional, if bit 7 of byte 1 set):
  - Positive ($00-$7F): new instrument number
  - Negative ($80-$FF): portamento speed (bits 1-6 = speed, bit 0 = direction)
    - Bit 0 = 0: portamento up
    - Bit 0 = 1: portamento down
- Byte 3: Pitch (0 = lowest C, 12 = next C, etc.; values above $48 supported)
- Byte 4 (preview, not consumed): $FF = end of pattern

**Instrument format (8 bytes each):**
- Byte 0: Pulse width low
- Byte 1: Pulse width high
- Byte 2: Control register (waveform: tri/saw/pulse/noise + gate)
- Byte 3: Attack/Decay
- Byte 4: Sustain/Release
- Byte 5: Vibrato depth (0 = no vibrato)
- Byte 6: Pulse speed (0 = no pulse modulation; lower 5 bits = delay between
  steps; upper 3 bits = speed of increment/decrement)
- Byte 7: FX flags:
  - Bit 0: Drum (noise waveform on first frame, then ctrl byte's waveform;
    fast frequency decrement from savefreqhi each frame)
  - Bit 1: Skydive (slow frequency down — decrements savefreqhi every 2
    frames; sounds like falling pitch)
  - Bit 2: Octave arpeggio (alternates between note and note+12 each frame)
  - Bits 3-7: Not used in Phase 2; "were used alot in later music for the fx"

#### Effects/Processing (SoundWork section, runs every frame if no new note)

1. **Release**: When note length expires, clear gate bit. Unless bit 5 of
   note byte (no-release flag) is set. Also clears AD and SR registers.

2. **Vibrato**: Uses `counter AND #$07 CMP #$04` to create oscillating value
   0-1-2-3-3-2-1-0 (the "01233210" pattern). Vibrato depth (byte 5) controls
   the divisor. The vibrato only activates when note length >= 8. Computes
   frequency difference between note and note+1, divides by 2^depth, then
   adds scaled amount per oscillation step.

3. **Pulse width modulation**: The PW bounces between $08xx and $0Exx at a
   rate controlled by byte 6. The delay between steps equals the speed byte.
   Current PW is stored back in the instrument table (self-modifying!).
   Direction (up/down) stored in per-voice `pulsedir` variable.

4. **Portamento**: If portamento byte was read, add/subtract `portaval AND $7E`
   to/from savefreqhi:savefreqlo each frame. Bit 0 selects direction.

5. **Drums** (bit 0): First frame = noise waveform. Subsequent frames = ctrl
   byte's waveform. Each frame: `DEC savefreqhi` and write to $D401.

6. **Skydive** (bit 1): Every other frame (counter AND $01 != 0): if
   savefreqhi > 0, `DEC savefreqhi`.

7. **Octave arpeggio** (bit 2): On odd counter frames, use note+12; on even
   frames, use note. Writes full 16-bit frequency to SID each frame.

#### Tempo

Single speed counter:
```
dec speed
bpl mainloop       ; still counting down
lda resetspd       ; reset counter
sta speed
```
- `resetspd` = speed-1 (default 1 for Monty on the Run)
- A note of length $1F with speed=1 lasts 64 frames (~1.28 seconds at 50Hz)
- Tempo = `(note_length + 1) * (resetspd + 1)` frames per note

The NoteWork only fires when `speed == resetspd` (counter just reset). All
SoundWork effects run every frame regardless of speed.

#### Key Global Variables

```
counter    - global frame counter (inc each play call)
speed      - countdown to next tick
resetspd   - speed preset value (tempo)
mstatus    - $00=playing, $40=init, $80=off (quiet), $C0=off (kill SID)
posoffset  - per-voice position in track (pattern list index)
patoffset  - per-voice position within current pattern
lengthleft - per-voice note duration countdown
savelnthcc - per-voice saved length+flags byte
voicectrl  - per-voice saved control register
notenum    - per-voice current note number
instrnr    - per-voice current instrument
savefreqhi/lo - per-voice saved frequency
portaval   - per-voice portamento value (0=none)
pulsedelay - per-voice PW delay counter
pulsedir   - per-voice PW direction
appendfl   - $FF=no append, $FE=append (used as AND mask for ctrl write)
```

### Features NOT in Phase 2 (but in Phase 3/4 and later)

According to the C=Hacking article: "All the other bits have no meaning in
this music, but were used alot in later music for the fx."

From our own reverse engineering of Phase 3/4 songs:
- **Nested speed counters** (outer DEC/BPL guard): 28+ F-grade songs affected.
  Outer counter values 3-11, inner typically 1. When outer fires, it JMPs past
  the inner DEC, skipping one tick. The effective frames-per-tick formula is
  more complex than `(D+1) * (speed+1)`.
- **Table arpeggio** (bit 3, post-1986): fx & $0A == $0A triggers table arp.
  Per-voice frame counter AND #$01 toggles between base note and arp table note.
  Arp table at fixed address (e.g., $0E71 in Chain_Reaction), indexed by inst*8.
- **PW mode selector** (bit 3, 1985 era): In Commando and similar, bit 3
  selects between unidirectional (bit3=1) and oscillating (bit3=0) PW sweep.
  The oscillating mode uses a period counter and direction flag.
- **Upper nibble arpeggio** (Phase 4): fx_flags upper nibble is the arp
  interval in semitones (not just octave).
- **Per-voice transpose**: Some variants apply a fixed semitone offset to one
  or more voices via `ADC abs,X` before the freq table lookup.

### Vibrato Details (from C=Hacking)

The vibrato oscillation value is computed as:
```
lda counter
and #7           ; 0-7 repeating
cmp #4
bcc +            ; if < 4, keep as-is (0,1,2,3)
eor #7           ; if >= 4: 4->3, 5->2, 6->1, 7->0
+ sta oscilatval ; result: 0,1,2,3,3,2,1,0
```

Then the frequency difference between note and note+1 is computed, divided
by 2^vibrdepth shifts. Then oscilatval copies of this diff are added to the
base frequency.

Note: vibrato is suppressed if note length < 8 (short notes don't vibrate).

### Drum Mechanism (from C=Hacking)

Bass drums use ctrl reg with non-noise waveform (e.g., $21 for square+gate).
On first frame: write noise ($80) to ctrl reg regardless. On subsequent frames:
write ctrl reg value from instrument. Every frame: `DEC savefreqhi`.

This means:
- First frame: noise + original high freq
- Second frame onwards: square (or whatever) + decreasing freq

Hihats/cymbals: ctrl reg has noise always ($81), so freq decrement produces
the characteristic hi-hat decay.

### Pulse Width Modulation (from C=Hacking)

The delay byte (bits 0-4 of byte 6) creates a delay between PW steps.
The speed (bits 5-7, stored in `pulsevalue AND $E0 -> pulsespeed`) is the
amount added/subtracted each step.

Direction bounces between $08xx (min) and $0Exx (max) using exact equality:
`CMP #$0E` → switch to down, `CMP #$08` → switch to up.

Current PW values are STORED BACK into the instrument table each frame
(self-modifying data). This is why the decompiler must copy instrument data
before accessing it — the "initial" values are modified by play.

### What the C=Hacking Article Does NOT Cover

1. The second driver variant (promised but never published)
2. Phase 4 variants (upper nibble arp, table arp)
3. Multi-song initialization (songs table indexing by song_num * 6)
4. Any nested speed counter mechanism
5. The exact format of later fx_flags bits (3-7)
6. Filter usage (no filter in Phase 2 driver apparently)

## Online Resources

### Primary Source
- **C=Hacking Issue 5** (1993):
  `http://www.ffd2.com/fridge/chacking/c=hacking5.txt`
  - Full commented disassembly (Monty on the Run driver, ~30 songs)
  - Article by Anthony McSweeney
  - Complete data format documentation
  - No copyright concerns (author took legal responsibility)

### Secondary/Identification
- **sidid.cfg** (cadaver, HVSC team):
  `https://github.com/cadaver/sidid/blob/master/sidid.cfg`
  - 6 binary signature patterns for Rob_Hubbard player
  - Only ONE class — does not distinguish driver variants
  - Also identifies Rob_Hubbard_Digi variant

- **sidid.nfo** (cadaver):
  `https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo`
  - Lists "Companion" as a precursor driver (1984, Keith Bowden book)
  - Note: "The book suggests to add features, which has been done on Rob
    Hubbard's two earliest SIDs and Clever Music's. In 1988 and in 1989,
    Vic H. Berry based two editors on this driver."

### Scene Context
- **HVSC STIL** (song title index): Has extensive comments on specific songs
  including direct Hubbard quotes about composition, but nothing technical
  about the driver internals.
- **CSDb**: No forum threads or releases with Hubbard player disassembly found.
- **GitHub**: No repos found with Hubbard driver analysis or disassembly.
- **Lemon64**: Search access denied; no direct hits found.

## Conclusions for SIDfinity

### What We Already Had Right
The C=Hacking source confirms our current implementation is correct for the
Phase 2 driver:
- 8-byte instrument format (matches RHInstrument in rh_decompile.py)
- fx_flags bits 0=drum, 1=skydive, 2=octave arpeggio
- Note byte format (bits 5/6/7)
- Portamento encoding (bit 0 = direction, bits 1-6 = speed)
- Vibrato oscillation: `counter AND #7 CMP #4 BCC ... EOR #7` → 01233210
- Pulse width bounce between $08xx and $0Exx

### What We Are Missing (confirmed gaps)
1. **Nested speed counters** — not documented anywhere online; we must
   empirically measure effective tick rates from register traces.
2. **Table arpeggio (Phase 3/4 bit 3)** — must be reverse-engineered per-song.
3. **Upper nibble arpeggio (Phase 4)** — must be reverse-engineered.
4. **Filter usage** — no Phase 2 songs use filter; unknown if later variants do.
5. **Second driver format** — the promised C=Hacking article was never written.

### Vibrato Formula Confirmed
The C=Hacking source confirms the vibrato oscillation pattern 0,1,2,3,3,2,1,0
(byte+5 controls depth = right-shift count on the freq difference). Our
current implementation should verify it uses this exact pattern.

### Key Implementation Insight
From the C=Hacking source: the PW values are stored BACK into the instrument
table each frame. This is why in our decompiler we must use py65 to measure
the "live" PW state rather than just reading the static binary.

The C=Hacking article explicitly confirms: "The current values of the pulse
width are actually stored in the instrument" (self-modifying data pattern).

## Variant Detection Summary

Based on all research, the driver generations are:
1. **Companion** (1984): Keith Bowden book driver; earliest 2 Hubbard SIDs
2. **Phase 2** (1985-1986): ~30 songs; documented in C=Hacking Issue 5
   - Single speed counter
   - fx_flags bits 0-2 only (drum/skydive/octave arp)
   - PW oscillates between $08xx and $0Exx
3. **Phase 3** (1986-1987): ~30+ songs (W.A.R., Chain Reaction, etc.)
   - Nested speed counters (outer DEC/BPL)
   - Table arpeggio (fx_flags bit 3 with bit 1)
   - Different PW logic (bit 3 alone = unidirectional)
4. **Phase 4** (1987-1988): Later songs (After 8, Mr. Meaner, etc.)
   - Upper nibble arp interval
   - Most complex nested counters (outer=11)

Detection method: sidid identifies all as "Rob_Hubbard" — we must use
our own pattern matching in rh_decompile.py to distinguish generations.
