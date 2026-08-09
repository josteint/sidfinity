# Music Assembler — player runtime & per-frame SID write model

> **Provenance**
> - source: disassembled from a verified HVSC Music Assembler tune,
>   `hvsc85/MUSICIANS/R/Rage/Kalle_Kloakk_part_8.sid` (base $3000), cross-checked
>   against `tools/siddump --writelog` (libsidplayfp ground truth).
> - method: py65 disassembler (`tools/py65_lib`) over the relocated player image +
>   one-frame writelog capture.
> - fetched_via: direct (local RE, not a web source)
> - fetch_date: 2026-06-13
> - reliability: HIGH for the structure shown (the dispatch + init + per-voice
>   decode were read instruction-by-instruction and the canonical sidid
>   fingerprint matches at $3091). The data-stream byte encoding is partially
>   inferred — full packer spec still requires the editor's save path
>   (see `archive_editor_disk_1990.md`).

This is the priority-2 deliverable: how the relocated player turns packed data
into `$D400–$D418` writes each frame. Addresses below are for a base of **$3000**;
subtract $3000 to get base-relative offsets. The init/play entry offsets match
the manual exactly: **init = base+$48, play = base+$21**, IRQ installer = base+$00.

## Memory layout (base-relative)

| base+offset | role |
|---|---|
| `+$00` | IRQ installer (`SEI; JSR init; set $0314/$0315 → +$18; CIA $DC0E; raster $D01A; CLI`) |
| `+$18` | IRQ handler: `INC $D019; JSR play (+$21); JMP $EA31` |
| `+$21` | **play()** entry — speed dispatch (see below) |
| `+$48` | **init()** entry |
| `+$81..+$90` | per-voice / global state bytes (zeroed by init) |
| `+$84,X` | per-voice flag byte (bit0 cleared on track-stop) |
| `+$8A,X` | per-voice note **duration counter** (loaded `AND #$1F` from the note's length nibble) |
| `+$8D,X` | per-voice **track sequence-pointer** (index into the active sequence; $FE = track stopped) |
| `+$90` | **master speed counter** (the multispeed divider; reloaded to 2 here) |
| `+$C9,X / +$CC,X / +$CF,X` | per-voice runtime regs written by the note path (freq/wave derived) |
| `+$E6,X` | per-voice **transpose** (high nibble = octave shift; low nibble routed to `+$E9,X`) |

(The exact `+$81..+$90` packing differs slightly between player builds — see the
version table in `archive_versions_and_fingerprints.md`. This is the `+$91`
canonical 1989 layout.)

## init() — base+$48

```
LDA #$1F ; STA $D418      ; volume $F + low-pass filter-type bit ON  (master vol/filter)
LDA #$F0 ; STA $D417      ; resonance = $F, NO voices routed to filter yet
AND #$0F ; STA <work>     ; stash res nibble
LDX #$0F : zero +$81..+$90 (16 state bytes)
LDX #$02 : for each of 3 voices:
    fetch track-table pointer from (+$34B9,X / +$34BC,X)   ; per-voice track start ptr lo/hi
    STA +$8D,X            ; track sequence pointer (= first byte: sequence #)
    2nd byte -> +$E6,X    ; transpose; AND #$0F -> +$E9,X
RTS
```

Init is therefore a **typed priming**, not a verbatim register dump: it sets
`$D418=$1F` and `$D417=$F0` and seeds three per-voice track pointers + transpose.
For USF this is the standard reset+priming split — the `$D418`/`$D417` go in the
`init.sid` block; everything else is engine bookkeeping.

## play() — base+$21 — the multispeed dispatch

```
+$21 LDX #$00
     DEC +$90               ; master speed counter
     BMI <reload>           ; counter expired -> advance song this frame
     ; counter not expired: still run the per-frame effect updaters twice
     JSR $3226 ; JSR $3225 ; JMP $3225
<reload> LDA #$02 ; STA +$90   ; reload divider = 2
     JSR <advance-voice> ; ... per voice ...
     DEC +$8A,X (duration) ; BMI -> fetch next sequence step
     JMP <note-fetch>
```

Interpretation: the player runs at **50 Hz** but advances the *song* on a
sub-rate governed by `+$90` (reloaded to 2 here → effective tempo). On the
in-between frames it still runs the continuous effect updaters (vibrato / pulse /
slide / filter sweep), which is why the writelog shows SID writes on *every*
frame even though notes only change every few frames. The per-tune speed is the
`F1–F8` song-speed from the manual's track editor; expect the reload constant to
vary per tune and per variant (Ten_Tracker = "10x speed", DoubleTracker =
"multispeed").

## Per-voice note/command decode — base+$91 (canonical engine)

This is the routine matched by the sidid `Music_Assembler` fingerprint
(`BC ?? ?? C0 FE D0 09 BD ?? ?? 29 FE 9D ?? ?? 60 ...`). It reads the **packed
sequence stream** one byte at a time:

```
LDY +$8D,X                ; track's current sequence number
CPY #$FE  -> if $FE, track stopped: clear +$84,X bit0, RTS
LDA $3AC1,Y / $3AA4,Y     ; sequence-start pointer table (lo @ $3AC1, hi @ $3AA4),
                          ;   indexed by sequence number -> ($FA/$FB) = seq read ptr
LDY +$81,X                ; per-voice offset within the sequence
LDA ($FA),Y               ; fetch a sequence byte
  BMI <command>           ; bit7 set  = command byte
  CMP #$60                 
    BCS <duration/dur-cmd> ; $60-$7F : note-length token (AND #$1F = duration; bit5 = slide present)
    BCC <note>             ; $00-$5F : a NOTE value
```

### Note path ($00–$5F)

```
STA $FC                   ; raw note
INY
LDA +$E6,X : LSR x4 (high nibble) : CLC ADC $FC -> +$C9,X   ; note + transpose-octave  -> freq index
TAY
LDA $3437,Y -> +$CC,X and +$33E2,X   ; freq LO table -> voice freq-lo + a saved copy
LDA $31C5,Y -> +$CF,X and +$32B6,X   ; freq HI table -> voice freq-hi + saved copy
```

So pitches are produced from **two 96-entry frequency tables** (`$3437` lo,
`$31C5` hi), indexed by `note + (transpose>>4)`. (Table addresses are base-
relative; they relocate with the player.)

### Duration / slide token ($60–$7F)

```
AND #$1F -> +$8A,X        ; duration counter (this matches the manual's 00=16th .. 1F=double-whole)
test bit5 (AND #$20): if set, this step has a portamento (slide):
    read 2 more bytes -> +$47,X (LSB/fine) and +$4A,X (MSB/coarse)   ; the slide vector
```

This exactly realises the manual's "two extra columns hold LSB and MSB (fine and
coarse) of the slide", and "FF/FE in the last column slides down" — the slide is
a signed 16-bit add to the running frequency per frame, with the documented
"odd LSB = rattling slide (effect only every 2nd frame)" trick living in the
slide updater.

### Filter command (a `BMI`/command branch, decoded near base+$150)

```
INY ; LDA ($FA),Y ; STA <filter-cmd>
AND #$0F ; ASL ; SEC ; SBC #$10 -> <filter step>
```

`AND #$0F` extracts the rate/direction nibble; `ASL; SEC; SBC #$10` converts it
to a **signed per-frame cut-off delta**. This matches the manual's filter table
(value 8 = hold; 9..F = up by 2,4,..,14; 7..0 = down by 2,4,..,16): the per-frame
delta is `±2*n`. A separate "frames remaining" byte (the manual's last column)
gates how long the sweep runs.

## Per-frame write model (from `--writelog`, libsidplayfp)

For each ACTIVE voice the player writes the SID registers in a fixed
**control-first, then pulse-width, then frequency** order. Captured order for
voice 1 (regs are `$D40x` offsets):

```
$04 (CTRL) , $03 (PW hi) , $02 (PW lo) , $00 (FREQ lo) , $01 (FREQ hi)
```
then voice 2 (`$0B,$0A,$09,$07,$08`), then voice 3 (`$12,$11,$10` + `$0E,$0F`).
Filter writes (when a filter effect is active on the triggering voice) appear as
`$18` (mode+vol, e.g. `$F2`), `$13` (cutoff hi), `$12` (cutoff lo) — i.e. the
shared low-pass is driven from the lowest-numbered triggering track, matching the
manual's "filtering applies to the triggering track and all lower tracks".

**This descending within-voice write order is the MA instruction-sequence
fingerprint** — a future composer must emit `CTRL → PWhi → PWlo → FREQlo → FREQhi`
per voice to match the write stream (verify mode 1, per-frame instruction
sequence).

Init writes observed: `$D418=$0F` then `$D418=$1F`, `$D417=$F0` (the `$1F`/`$F0`
priming from init()); the leading `$0F` is the universal volume reset before the
filter-type bit is set.

## Open items for a full migration

1. **Packed sequence-stream byte grammar** — the note/duration/slide/filter
   tokenisation above is read directly, but the *exact* boundary cases (rest vs
   hold vs legato `<` no-retrigger, the PRE preset-select command, arpeggio
   attach) need the editor's save path (`archive_editor_disk_1990.md`) to pin
   down byte-for-byte.
2. **Track-list format** — `+$8D,X` walks a per-voice track list of
   `(sequence#, transpose, repeat)` triples with `$FE`=stop / `$FF`=loop; the
   on-disk packing of that list (and where the `$34B9/$34BC` track-start
   pointers come from) is the other half of the packer.
3. **Preset (8-byte) → register mapping** — the 32×8-byte preset table feeds
   ADSR/wave/pulse/vibrato; confirm the byte order against the editor.
