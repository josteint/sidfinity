---
source_url: https://github.com/realdmx/c64_6581_sid_players
fetched_via: git clone
fetch_date: 2026-06-03
author: realdmx (collated); original disassemblies by various scene authors / dmx87
content_date: 1988-1990 (original SIDs); ACME conversion ongoing
reliability: primary
---

# realdmx/c64_6581_sid_players — Reverse-engineered MoN-family SID drivers

ACME-buildable disassemblies of the MoN (Maniacs of Noise) / FutureComposer
driver family. Each `.asm` rebuilds byte-exact to the matching `.sid`. The
**MoN driver and the FC3.x driver are the same code lineage** — Charles
Deenen's "MUSICFILE V01-07-1988" player (literally headered as such in
Cybernoid II) is what FC1.0 ripped, and what FC2.x/FC3.x extended.

This is the single highest-value source we have for byte-exact rebuild
work — it gives us the **complete 6502 source of a working player from
the FC family**, not just a format description.

## Files cloned (12,291 lines of MoN-family asm)

| File | Lines | Composer | Notes |
|------|-------|----------|-------|
| `Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm` | 1817 | Jeroen Tel | Headered "MUSICFILE V01-07-1988 / Programmed by Charles Deenen". This IS the driver Hawkeye uses. |
| `Deenen_Charles_MON/Deenen_Charles_Test_Tune.asm` | 1985 | Charles Deenen | Reference test tune |
| `Deenen_Charles_MON/Deenen_Charles_Test_Tune2.asm` | 1293 | Charles Deenen | Reference test tune 2 |
| `Deenen_Charles_MON/Deenen_Charles_SFX_Player.asm` | 958 | Charles Deenen | SFX-only variant |
| `Bjerregaard_Johannes_MON/Bjerregaard_J_Myth.asm` | 1932 | Johannes Bjerregaard | MoN-family variant |
| `Bjerregaard_Johannes_MON/Bjerregaard_J_James_Bond_3.asm` | 0 | — | Placeholder, empty |
| `Ouwehand_Reyn_MON/Ouwehand_Reyn_Dutch_Breeze.asm` | 1936 | Reyn Ouwehand | "1990 MON" — late MoN/FC family |
| `Ouwehand_Reyn_MON/Ouwehand_Reyn_Armada.asm` | 2370 | Reyn Ouwehand | Late MoN |

Also useful for context: full `Hubbard_Rob/Commando.asm` + Monty (MoN
descends from Hubbard's 1985 driver), plus `Galway`, `Whittaker`, `Dunn`,
`Kimmel`. Repo is ACME-targeted; sources also under
`Audial_Arts/`, `Bulka_Adam_FAME/`.

## Driver shape (from Cybernoid II = canonical MoN/FC family)

The Cybernoid II driver has the **same data hierarchy** as FC and the
same per-VBI execution model. Key entry-point structure:

```
RELOC = $1000
* = $1000
init      jmp song      ; song-select entry  (a = subtune number)
          jmp songout   ; stop entry         (init+3)
play      jmp playirq   ; per-frame entry    (init+6  <-- FC's "+6 offset")
```

This **confirms FC's +6 play offset** is inherited directly from the MoN
driver's three-jump dispatcher (init / quit / play).

## Zero-page layout (ZP $40-$52)

```
fx1sto    = $40   ; cached fx1 byte (vibrato + arp params) for current voice
fx2sto    = $41   ; cached fx2 byte (pulse + filter)
fx3sto    = $42   ; cached fx3 byte (drum/sweep/wavearp/pulsearp/etc.)
tabbytsto = $43   ; current pattern byte
zer0fillo = $44   ; (lo, hi at $45) — filter table indirect ptr
zp3       = $46   ; (lo, hi at $47) — pattern indirect ptr
wax       = $48   ; current voice index (0..2)
voicesto  = $49   ; current $D400-base offset (0/7/14)
vibrasto  = $4a   ; vibrato lookup
zodat3    = $4b
vibreallo = $4c   ; (lo, hi at $4d)  — vibrato output frequency
temphino  = $4e
templono  = $4f
glideslo  = $50   ; (lo, hi at $51)
denom     = $52
```

## Per-voice state (3-byte arrays indexed by `wax` = 0..2)

```
tabcount      ; sequence-index counter (which step in seqXX list)
begcount      ; pattern-index counter  (byte offset inside stXX)
nootcount     ; note-duration countdown
nootleng      ; note duration (set when new note starts)
wavesto       ; current waveform/control byte
noothoogt     ; current pitch index in freq table (after toneadd applied)
noho          ; base pitch (before toneadd applied)
wavecount     ; instrument number selected (used as *8 index into pulsehi/waveform/attdec/...)
hinotesto     ; current $D401 (lo half stored too)
hinotesto2    ;   shadow for vibrato compare
lonotesto     ; current $D400
glidetest     ; glide-active flag
glidetest2    ;   second glide flag
pulsestolo    ; current $D402 (lo PW)
pulsehisto    ; current $D403 (hi PW, low nibble)
pulsehitemp   ; cached pulsehi byte from instrument
counter2      ; per-voice global counter, incremented every frame
toneadd       ; transpose (semitones) from $20-$3F sequence command (and #$1F)
voiceinc      ; instrument transpose from $40-$5F sequence command (and #$0F)
repeatsto     ; pattern repeat count from $60-$9F sequence command (and #$3F)
vibstore1/2/3 ; vibrato phase state
tonearpcounter; arp position
arpieoklo/hi  ; ptr to current arp table for tone-arp ($70 cmd)
filter        ; current filter cutoff
filtercount   ; bit 3 = "double voice" flag, low 3 bits = filter-table position
pulsetest     ; PW direction flag (1 = ascending)
pulseruntest  ; pulserun (PWM sweep) init flag
pulserunlo/hi ; pulserun phase
vibcounter    ; vibrato delay/sweep counter
d400/d401     ; output shadow registers (lo freq, hi freq)
d402/d403     ; output shadow (lo pw, hi pw)
stod404       ; output waveform/control byte
newnote       ; "new-note-just-started" flag
byteand       ; AND mask applied to wave control byte ($FF normal, $FE on note-off, etc.)
```

## Sequence table format (per voice — voice points into `sequence[]`)

The sequence list is a stream of bytes interpreted by the inner loop in
`h2:` (`Tel_Jeroen_Cybernoid2.asm` lines ~250-320). Three voices each
have their own seqloclo/seqlochi pointer; `seqtabel` holds the 3
sub-list pointers for each subtune (`<seq0a,<seq0b,<seq0c, >seq0a,...`).

**Sequence command bytes (verbatim from the player):**

| Byte range | Action | Code |
|------------|--------|------|
| `$00..$1F` | (Falls through to $40-$5F handler — wraps as transpose?) Actually: BCC h3a path, see ASL/TAY at h3f — these are pattern indices: `pat_id = byte; ptr = sequence[byte*2]` → fetch pattern from word table at `sequence`. |
| `$40..$5F` | `toneadd = byte & $1F` (set semitone transpose for this voice) |
| `$60..$7F` | `voiceinc = byte & $0F` (instrument transpose / set base) |
| `$80..$BF` | `repeatsto = byte & $3F` (set pattern-repeat counter) |
| `$FE` | End of song → `songout` (jumps to init+3 path) |
| `$FF` | End of subtune segment / loop back: `nootcount=0; tabcount=0; begcount=0; jmp h2` (loops the sub-list) |
| else | `pat = sequence[byte*2]` — fetch pattern pointer from word-table |

**Cybernoid II `seqtabel` (subtune dispatch):**
```
seqtabel
    !by <seq0a,<seq0b,<seq0c   ; song 1 voice 1/2/3 (lo)
    !by >seq0a,>seq0b,>seq0c   ; song 1 voice 1/2/3 (hi)
    !by <seq1a,<seq1b,<seq1c   ; song 2 (game-over)
    !by >seq1a,>seq1b,>seq1c
snelheid !by 2, 2              ; per-subtune speed
```

## Pattern data format ($Bx, $Cx, $Dx, $Ex, $Fx commands)

Once inside a pattern (`(zp3),y` indirect), bytes are interpreted in the
section labelled `startnewnote:` / `skip:` (lines ~330-450).

| Byte range | Meaning | Side-effect bytes that follow |
|------------|---------|-------------------------------|
| `$00..$7F` | Note (pitch index into `lonote`/`hinote` freq table, +`toneadd`) → continues to ADSR/instrument application | (none — pitch byte is "self") |
| `$80..$BF` | Note duration set: `nootleng = (byte & $3F) - 1` then continues; cmd is "and #$3F sec sbc #1 sta nootleng" | none |
| `$C0..$DF` | Voice/instrument set: `wavecount = (byte & $1F) + voiceinc`, then `jsr verhoogtest` to step | next byte |
| `$E0..$EF` | Glide set: `glidetest=1; glidedelay=(next byte); tempglide=(next byte+toneadd)` — 3-byte command | 2 following bytes |
| `$F0` | bit 0 of next byte controls "filter set" branch: if `(byte&1)==0` then `newnote=1, begcount++, fetch next` (a note-restart marker); else `$D417 = (next byte)` (set filter resonance/routing directly) | conditional follow |
| `$F1..$F7` | (range hits `dofilset` after `cmp #$f0; bcs`) — direct $D417 write of next byte | 1 byte |
| `$70..$7F` | Tone-arp set: `arp_idx = byte & $0F; arpieoklo/hi = arplo[arp_idx]/arphi[arp_idx]` | 0 follow |
| `$FF` | End of pattern: `nextjmp`: `begcount=0`; if `repeatsto>0` then `repeatsto--; jmp h10b` (replay same pattern); else `tabcount++` (advance sequence position) | none |

Sequence/pattern decoder structure (Cybernoid II `h2:` block — paraphrased):
```
h2:  ldy tabcount,x
     lda (yoa1),y           ; fetch sequence byte
     cmp #$fe: beq songout  ; song end
     cmp #$ff: beq (loop)
     cmp #$40: bcc h3f      ; <$40 → pattern index lookup
     cmp #$60: bcc TRANSPOSE ; $40-$5F → toneadd
     cmp #$80: bcc INSTBASE  ; $60-$7F → voiceinc
     cmp #$C0: bcc REPEAT    ; $80-$BF → repeatsto
     ; else falls through; for ≥$C0, h3f handles pattern lookup
h3f: asl; tay; lda sequence,y / lda sequence+1,y → zp3/zp4 (pattern ptr)
```

## Instrument format (8 bytes per instrument)

Bank-of-8 layout from Cybernoid II `pulsehi = * + 0`:

```
offset 0: pulsehi      ; high nibble of pulse width init
offset 1: waveform     ; SID waveform/control byte (gate cleared at start)
offset 2: attdec       ; $D405 attack/decay
offset 3: susrel       ; $D406 sustain/release
offset 4: filcount     ; filter-table index (& $07) + flags
                       ;   bit 3 ($08) = "double voice" / detune voice
                       ;   bit 4 ($10) = ? (release-gate flag, see gwo2)
                       ;   high nibble used directly by drum
offset 5: fx1          ; vibrato + arp parameters
                       ;   bit 7 = vibrato direction (BPL → adc abs, BMI → ldy abs)
                       ;   bits 6-4 = vibrato depth/speed exponent (>>4 ANDed)
                       ;   bits 3-0 = vibrato amount
                       ;   when low nibble = $0: vibrato disabled
                       ;   high nibble in `(byte & $0F) << 0`: drum-table index when fx3.bit4 set
offset 6: fx2          ; pulse-table + filter-mod
                       ;   bits 2-0 = pulse-table program (1-7), 0 = no PWM
                       ;   bit 3 = "strangefilter" (LFO-style)
                       ;   high nibble = pulserun speed when bit 3 of fx3 set
offset 7: fx3          ; effects bitfield
                       ;   bit 0 = filter-table active
                       ;   bit 1 = pulserun (sweeping PW)
                       ;   bit 2 = tone-arp (uses arp_idx from $70 pattern cmd)
                       ;   bit 3 = pulse-arp (use pulsearp table)
                       ;   bit 4 = drum
                       ;   bit 5 = tone-sweep up (decrement hinotesto each frame)
                       ;   bit 6 = wave-arpeggio
                       ;   bit 7 = noise-tick attack
```

**Cybernoid II instrument bank (19 instruments, 8 bytes each):**

```asm
; pulsehi waveform attdec susrel filcount fx1 fx2 fx3   ; comment
  !by $00,$00,$00,$00,$00,$00,$00,$00     ; 0 = leeg (empty)
  !by $05,$41,$08,$89,$00,$53,$64,$80     ; 1 = bass
  !by $08,$11,$00,$a8,$f0,$00,$00,$10     ; 2 = bassdrm  (fx3=$10 drum)
  !by $08,$11,$00,$a9,$f0,$01,$00,$10     ; 3 = snardrm
  !by $04,$21,$00,$c8,$01,$00,$81,$85     ; 4 = arp+filt (fx3=$85)
  !by $0c,$41,$00,$b8,$00,$52,$22,$01     ; 5 = melo-1
  ...
```

## Auxiliary tables

- **`lonote` / `hinote`** — 91-entry 16-bit frequency table (8 octaves × 12 ≈ 96, here 91). `lonote2 = *+1` overlap is an aliased pointer pair used by the vibrato code to read entry+1 cheaply.
- **`arp0..arp7`** — 4-byte (or longer) arp sequences referenced from $70 pattern cmd. `arp6` is unusual: `!by $17` then 24 bytes of `$e9..$ff,$00` → long custom-arp.
- **`drumtabel`** (word table) → per drum entry: `dwaN` (waveform sequence, prefixed with length byte) + `dtoN` (frequency sequence). See `dwa0!by$0b,$81,$81,$20,...` (length 11) + `dto0!by$34,$0a,...`.
- **`pulsetabel`** — 8 bytes per PWM program (4 programs in Cybernoid II). Layout per entry:
  - byte 0: bit 7 = "purepbyte" flag, low nibble = `pulsecountlo` threshold
  - byte 1: `pulsecounthi` threshold
  - byte 2 + bit 7 = end-pulse flag, low 7 bits = first counter2 compare
  - byte 3: speed when first phase active
  - byte 4: second counter2 compare
  - byte 5: speed for second phase
  - byte 6: third counter2 compare
  - byte 7: third-phase speed (or end-flag)
- **`filterbytes`** — word table of 4 filter programs (`fb0..fb3`). Each program is 10 bytes:
  - byte 0: ramp target / direction
  - byte 1: ramp delta (signed)
  - byte 2: ramp target 2
  - byte 3: ramp delta 2
  - byte 4: ramp final
  - byte 5: `$D418` byte (e.g. `fp0 = $10 + volume` = $1F = lowpass + vol 15)
  - bytes 6-9: counter2 thresholds for each phase
- **`vibtabwait`** — per-instrument vibrato delay (entry-aligned with instrument bank).
- **`startlen` / `starttabel`** — noise-tick attack: `startlen[wavecount]` cycles, `starttabel[wavecount]` waveform during attack.
- **`wavearp`** — 4-byte waveform-arpeggio sequence (cmd-stream of SID control values; `$81` = special "trigger silence").
- **`pulsearp`** — 8-byte pulse-arp sequence (used as `$D403` direct overwrite).

## Per-frame execution flow (verbatim mapped from playirq)

For each voice 2, 1, 0 (`ldx #2 ... dex bpl ...` outer loop):

1. **Speed gate** — `dec speedsto; bpl startplayer` (skip frame if not yet due).
2. **`counter2,x` increment** (global per-voice frame counter — drives PWM/filter timing).
3. **Sequence step** — `dec nootcount,x; bmi h2` (note duration expired → fetch new). `h2` parses sequence byte (commands above), eventually loads `(zp3),y` from pattern.
4. **Pattern decode** — `startnewnote:` parses cmd nibble at top, sets `glidetest`, instrument, duration, etc.
5. **Note pitch** — `lda lonote,y / hinote,y → d400/d401` (with `noho = pitch+toneadd`, `noothoogt` after arp offset).
6. **Instrument set on new note** — copy `pulsehi/waveform/attdec/susrel/filcount` from bank into per-voice shadow (only when `newnote` is set).
7. **Tone-arp** (`fx3 & $04`) — overwrites freq from `arpieoklo/hi` sequence indexed by `tonearpcounter`.
8. **Vibrato** (`fx1sto != 0 && !glidetest2`) — phase machine using `vibstore1/2/3` and `vibcounter` against `vibtabwait`.
9. **Tone glide** (`glidetest`) — 16-bit ramp from `lonotesto/hinotesto` toward `tempglide`, distance / nootleng per frame.
10. **PWM** — `pulsegedoe`: either `pulsetabel` program (`fx2 & $07`) or `pulserun` (`fx3 & $02`) ramp.
11. **Wave-arpeggio** (`fx3 & $40`) — every `wavearpwait` frames rotate `stod404` through `wavearp[counter2&3]`.
12. **Pulse-arpeggio** (`fx3 & $08`) — every `pulsearpwait` frames overwrite `$D403` from `pulsearp[counter2&7]`.
13. **Tone-sweep** (`fx3 & $20`) — `dec hinotesto` each frame (chromatic falling).
14. **Filter** (`fx3 & $01`) — read `filterbytes` program, advance filter cutoff, write `$D418`.
15. **Drum** (`fx3 & $10`) — overrides waveform from `dwaN` + freq from `dtoN`.
16. **Noise-tick** (`fx3 & $80`) — short attack burst using `starttabel/startlen`.
17. **Double voice** (`filcount & $08`) — adds `dubvoice` (=$0C) to `d400/d401` for detuned voicing.
18. **Space effect** (`filcount & $00`) — note: this is always-false in Cybernoid II; in other MoN tunes the mask is non-zero and decrements `hinotesto2` for a "space-echo" tail.
19. **`nextvoice:`** writes `stod404 & byteand → $D404,y`, `d400→$D400,y`, ... `d403→$D403,y`.

## What this gives us for the FC byte-exact build

This is **not** FC's exact byte layout (FC stores songs as a compact
header + indirect arrays; this disassembly is post-link absolute), but:

1. The **player runtime is the FC V3.x runtime** (Cybernoid II shipped
   with literally the same code lineage Hawkeye uses; sigid says FC_V3.x
   matches `EE 99 ?? EE 9A ?? EE 9B ?? A9` — these are three `INC ABS`
   instructions that increment the three per-voice `tabcount` /
   `begcount` shadow pointers, exactly the structure we see in `h2`).

2. The **instrument format, drum format, pulse/filter/vibrato tables**
   above are the runtime semantics — when we parse Hawkeye's tables,
   they should match this exact 8-byte instrument record and its
   sub-tables byte-for-byte.

3. The **command-byte ranges** ($40-$5F transpose, $60-$7F voiceinc,
   $80-$BF repeat/duration, $C0-$DF instrument, $E0-$EF glide, $F0
   filter-set / new-note, $FF end) are the **exact sequence-language**
   the FC editor writes into its module.

## Build / verify

```bash
cd /tmp/fc_research/c64_6581_sid_players/Tel_Jeroen_MON
acme Tel_Jeroen_Cybernoid2.asm   # produces Tel_Jeroen_Cybernoid2.sid
md5sum Tel_Jeroen_Cybernoid2.sid
# Should match HVSC's Cybernoid_II.sid modulo header
```

(ACME assembler not in the sidfinity tree; the xa65 in `tools/xa65/`
would need syntax adaptation. The source is principally a *reference*,
not a build target.)
