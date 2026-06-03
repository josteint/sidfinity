---
source_url: https://github.com/Linus123/C64_6581_SID_Players/blob/master/Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm
fetched_via: github raw 2026-06-03
fetch_date: 2026-06-03
author: Charles Deenen / Jeroen Tel (1988), disassembled & re-assembled by Linus Akesson(?)
content_date: original code 1988-07-01 ("MUSICFILE V01-07-1988"); disassembly published ~2018-2020
reliability: primary (ACME-assembler source that rebuilds the original SID byte-exact)
---

# Cybernoid 2 (Jeroen Tel, 1988) — the seed driver for FC V3 / Hawkeye

The `C64_6581_SID_Players` repo bundles a fully-annotated ACME source
for the **Cybernoid 2** driver. The source self-identifies as:

```
; MUSICFILE V01-07-1988
; Programmed by Charles Deenen
; The most advanced music player ever written for the commodore 64!
```

This is the **same family of driver** as Future Composer V3 — sidid's
fingerprint `4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ??`
matches both `MoN/Cyb2` and `FC_V3.x` (see `wayback_sidid_signatures.md`).
Hawkeye (Thalamus 1988) ships a Tel/Deenen driver that is a peer/sibling
of this exact source. **For byte-exact Hawkeye rebuild, this disassembly
is the closest published primary source.**

Source path on disk: `/tmp/fc_research/c64_6581_sid_players/Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm`
(1817 lines, ACME format).

## Architecture overview

### Entry points

```
init    jmp song
        jmp songout
play    jmp playirq
```

Three-vector dispatch table at the load address, **+3 spacing** — so
**init=$LOAD, songout=$LOAD+3, play=$LOAD+6**. The "play offset = +6"
claim in the existing research.md is correct **for this driver**, but
note that Hawkeye's PSID header shows init=$7AE0, play=$7AE3 — the
**+3** form (i.e., the PSID points at the `songout` slot or the
driver uses a 2-vector init/play). This needs verification against
the actual Hawkeye binary.

### Zero-page allocation ($40-$52)

```
fx1sto/fx2sto/fx3sto    $40-$42   ; current instrument's fx flag bytes
tabbytsto               $43       ; current pattern byte
zer0fillo/hi            $44/$45   ; generic indirect pointer
zp3/zp4                 $46/$47   ; sequence-entry pointer
wax                     $48       ; current voice index (0..2)
voicesto                $49       ; voice * 7  ($00/$07/$0E for $D400..)
vibrasto                $4A
zodat3                  $4B
vibreallo/hi            $4C/$4D
temphino/templono       $4E/$4F
glideslo/hi             $50/$51
denom                   $52
```

### Per-voice RAM (3 bytes each, indexed by `wax = 0/1/2`)

```
tabcount        offset into current sequence entry (pattern step)
begcount        offset into current pattern (within step bytes)
nootcount       countdown to next note
nootleng        current note length
wavesto         current waveform
noothoogt       current pitch index
noho            base pitch (before transpose)
wavecount       current instrument number
hinotesto/2     stored hi freq byte
lonotesto       stored lo freq byte
glidetest/2     portamento active flags
pulsestolo      pulse width lo
pulsehisto      pulse width hi
pulsehitemp     pulse hi+control nibble
counter2        global tick counter
toneadd         transpose (semitones)
vibstore1/2/3   vibrato state
tonearpcounter  tone-arpeggio counter
arpieoklo/hi    arpeggio pointer
filter          filter cutoff
filtercount     filter-table index
pulsetest       pulse direction
repeatsto       sequence-repeat counter
stod404         output $D404 (waveform+gate)
newnote         "new-note" flag
tempglide       glide target
glidedelay      glide delay
d400/01/02/03   shadow registers
voiceinc        voice-instrument offset (V3 adds this for instrument banks)
byteand         AND-mask for $D404 (drum-triggered gate kills)
pulseruntest/lo/hi  pulse-run (PWM sweep) state
vibcounter      vibrato delay counter
```

### Sequence entry (per voice, song-start)

The `song` routine reads 5 bytes from `seqtabel` per voice and loads
them into `seqloclo/hi[0..5]` — but only 3 are pointers; the layout is
`song-no * 6 + voice * 2`. Each voice's sequence is a flat byte-stream
of pattern numbers + control bytes.

### Pattern-stream byte semantics (in routine `h2`)

The sequence byte dispatch in `h2` (the **distinctive sidid FC_V3.x
fingerprint shape**):

```
$FE                     → song-end (returns to init)
$FF                     → loop pattern (reset to begcount=0)
$E0..$FF (except above) → control bytes (see below)
$80..$DF                → various commands
$60..$7F (s ≥ $60 < $80) AND $0F → set voiceinc (instrument-bank offset)
$40..$5F (s ≥ $40 < $60) AND $3F → set repeatsto (pattern-repeat count)
$00..$3F (s < $40)       AND $1F → set toneadd (transpose, signed-ish)
```

Confirms the exact dispatch order and bit-masks for V3.

### Per-step (note) byte stream — inside a pattern (`zp3` pointer)

After dispatching, the code reads bytes from the pattern (via `(zp3),y`):

| First byte range | Meaning |
|---|---|
| `$FF`            | pattern end / loop |
| `$F0` + low bit  | filter-resfilt set ($D417) + next byte = resfilt value |
| `$F0`            | new-note flag set, next byte = real note byte |
| `$E0..$EF`       | glide set — next byte = `glidedelay`, then byte = `tempglide` (target pitch + toneadd) |
| `$C0..$DF` AND $1F + voiceinc | set `wavecount` (instrument number) |
| `$80..$BF` AND $3F − 1       | set `nootleng` (note length), then check next byte |
| `$80..$FF` (second AND $7F)  | add to nootleng (long-note extension) |
| `$70..$7F` AND $0F            | arpeggio program index (into arplo/arphi table) |
| other                          | actual pitch byte (index into lonote/hinote freq table) |

(Reconstructed from labels: `skip / noglideset / novoiceset / arpset /
nolengset` chain.)

### Effect flags (`fx1`, `fx2`, `fx3` from instrument)

Each instrument carries 8 bytes: `pulsehi, waveform, attdec, susrel,
filcount, fx1, fx2, fx3`. The fx-byte bit assignments:

```
fx1: low nibble  = vibrato amplitude        ($0F mask)
     bits 4-6    = vibrato base-speed        ($70 mask, lsr×4)
     bit 7       = vibrato direction (+/-)   ($80 → ldy abs (BC) vs adc abs (7D))
     also: $0F selects drum number when fx3.4 (drum-bit) set

fx2: bits 0-2    = pulse-program index       ($07 mask, ×8 into pulsetabel)
     bit 3       = strange-filter active     ($08)
     bits 4-7    = pulse increment           ($F0 stored as pulsecountup default)

fx3: bit 0       = filter-program active     ($01) — uses filterbytes[$08..]
     bit 1       = pulse-run / PWM sweep     ($02)
     bit 2       = tone-arpeggio             ($04) — uses arp0..arp7
     bit 3       = pulse-arpeggio            ($08) — uses pulsearp[0..7]
     bit 4       = drum-routine              ($10) — uses drumtabel
     bit 5       = tonesweep-up              ($20) — decrements hinotesto
     bit 6       = wavearpeggio              ($40) — wavearp[$80,$10,$80,$10]
     bit 7       = noise-tick start          ($80) — uses startlen/starttabel
```

### Frequency table — 96 entries, 16-bit each, lo/hi separate arrays

```
lonote ($C3, $DD, $FA, $18, $38, $5A, $7D, $A3, $CC, $F6, $23, $53, …)
hinote ($01, $01, $01, $02, $02, $02, $02, $02, $02, $02, $03, $03, …)
```

**$01C3 = 451 ($D400/01 freq) corresponds to C-0 PAL** — standard
SID 8-octave PAL table. 96 = 12 × 8 = 8 full octaves indexed 0..95.

The labels `lonote2 = * + 1` / `hinote2 = * + 1` (used for vibrato
detune) suggest a second offset-by-1 access into the same table —
vibrato is computed as the **delta between adjacent frequency entries**
(a common "musical" vibrato that's wider in lower octaves).

### Instrument table layout (per-instrument, 8 bytes)

```
pulsehi = * + 0     ; PW high nibble
waveform = * + 1    ; $D404 waveform+ctrl byte
attdec = * + 2      ; $D405
susrel = * + 3      ; $D406
filcount = * + 4    ; filter table index (lo nibble); also drum-trigger config (hi nibble bit 3)
fx1 = * + 5         ; vibrato+drum-number
fx2 = * + 6         ; pulse-program + strange-filter
fx3 = * + 7         ; effect flags (above)
```

Indexed by `wavecount,x` shifted left 3 (× 8). The leading instrument 0
is all zeros (silence).

### Aux tables (also in Hawkeye-style FC)

```
arplo/arphi     — pointers into 8 arpeggio programs (arp0..arp7)
arp0..arp7      — variable length (last is 23-byte downsweep ending $00)
drumtabel       — 6 words: 3 drum {wave-pointer, tone-pointer} pairs
                  Each drum: length byte + N waveform-bytes + N pitch-bytes
filterbytes     — 4 pointers to 10-byte filter programs (fb0..fb3)
                  Each fb: cutoff-up step / cutoff-down step / down-rate /
                  resfilt-write / target-cutoff / d418-priming-byte /
                  4 segment-thresholds (compared against counter2 to select cutoff increment)
pulsetabel      — 4 PWM programs × 8 bytes
                  [purepbyte+pulsecountlo, pulsecounthi, 4 thresholds, pulsecountup_default, ?]
wavearp         — { $80, $10, $80, $10 } — 4-step wave-toggle (test bit + waveform)
pulsearp        — { $00, $00, $00, $00 } — disabled by default
vibtabwait      — 20 bytes, vibrato delay per instrument number
startlen        — 12 bytes, noise-start length per instrument
starttabel      — 12 bytes, noise-start waveform per instrument
```

### `playirq` — main 50 Hz interrupt body

```
playirq
        lda testbyte
        beq +
        rts                       ; halted

+       lda speedbyte
        ldx #2                    ; voice index, count down 2→0
        dec speedsto
        bpl startplayer

        sta speedsto              ; reload speed counter

startplayer
        stx wax                   ; remember voice
        inc counter2,x            ; global tick
        ldy d4point,x             ; voice * 7 (= $D400 voice offset)
        sty voicesto
        ...                       ; per-voice processing
        ldx wax
        ldy voicesto

        lda stod404,x             ; final SID register writes
        and byteand,x
        sta $d404,y
        lda d400,x
        sta $d400,y
        lda d401,x
        sta $d401,y
        lda d402,x
        sta $d402,y
        lda d403,x
        sta $d403,y
        dex
        bmi playout
        jmp startplayer
```

Standard MoN-family layout: shadow registers per voice are filled by
the effect chain, then `$D400-$D406` written once per voice from the
shadow. `byteand` is the "gate-off mask" (set to $FE by drum routines
to kill the gate bit while keeping the waveform).

### Effect chain order (key for byte-exact rebuild)

Per voice, in this exact order:

1. Take step from sequence (`h2` / `h3` family) — may decode new pattern byte.
2. Glideset / voiceset / arpset / lengthset / note-fetch.
3. Set ADSR + initial $D404, PW from instrument.
4. Wait-out (note still playing) or new-note initialisation.
5. **Tone-arpeggio** (fx3 & $04): cycles `arp[0..N]` adding to pitch.
6. **Vibrato** (fx1 lo nibble != 0 && !glidetest2): adds/subtracts
   delta-freq from current note, controlled by vibtabwait, vibrasto,
   and vibstore1/2/3 LFO.
7. **Tone glide** (glidetest): linear pitch interpolation, divided by
   `denom = (1 << bran) - 1` via long-division loop.
8. **Pulse program** (fx2 & $07): walks pulsetabel, increments/decrements
   pulsestolo / pulsehisto at variable rate, with reset-at-bounds.
9. **Wave-arpeggio** (fx3 & $40): cycles wavearp through $D404.
10. **Pulse-arpeggio** (fx3 & $08): cycles pulsearp through $D403 (PW hi).
11. **Tonesweep-up** (fx3 & $20): decrements hinotesto.
12. **Filter program** (fx3 & $01): walks filterbytes program by counter2,
    writes $D416 (cutoff) and $D418 (volume+filter-route).
13. **Strange filter** (fx2 & $08): bidirectional sweep of $D416.
14. **Pulse-run / PWM sweep** (fx3 & $02): autonomous PWM sweep.
15. **Double voices** (filcount & $08): adds dubvoice ($0C) to lo freq —
    a detune-octave trick.
16. **Space effect** (filcount & $00 — dead code? always skipped).
17. **Drum routine** (fx3 & $10): plays waveform+pitch program from
    drumtabel; sets byteand to $FE for gate-off.
18. **Noise tick** (fx3 & $80): plays starttabel waveform for startlen
    frames, with noisehitone ($FA) pitch.

### Driver-wide constants (the "knobs")

```
volume          = $0f       ; global D418 volume bits
vibtotzover     = $30       ; vibrato counter max (48 frames)
pulserunspeed   = $63       ; PWM-sweep rate (~100 per frame)
dubvoice        = $0c       ; double-voice detune (lo byte)
noisehitone     = $fa       ; noise pitch-hi
pulsearpwait   = $01        ; pulsearp start delay
gitarwait      = $0f        ; (unused in body — guitar-effect param?)
spacelength     = $00       ; space-effect minimum (skip)
spacewait       = $60       ; space-effect threshold
wavearpwait    = 2          ; wavearp start delay (frames)
```

These vary tune-to-tune even with the same driver — these are the
**per-song customisations** that distinguish e.g. Hawkeye from
Cybernoid 2. The driver code itself is byte-identical or nearly so.

## What this tells us for Hawkeye

1. **Pattern-byte interpreter is the V3 dispatcher with $40/$60 splits.**
   Direct match for FC_V3.x signature.
2. **Driver code = ~1 KB.** Tables (freq, arp, drum, filter, pulse, instrument,
   sequence, pattern) make up the rest of the SID's 8768 bytes.
3. **Instruments = 8 bytes each.** Hawkeye should have a similar table.
4. **Hawkeye has 12 subtunes (PSID metadata)** vs Cybernoid 2's 2 subtunes.
   So `snelheid` (speed per-subtune) and `seqtabel` (sequence pointers
   per-subtune × 3 voices) are larger arrays. Number of `sequence`
   entries (patterns) likely 50-100 in Hawkeye.
5. **Frequency table is the standard 96-entry MoN table** —
   `$C3,$DD,$FA,...` PAL — meaning we can detect it by signature.

## Lifting checklist for the extract path

When implementing `pipelines/future_composer/<engine>/extract/engine_model.py`:

1. Identify the driver entry triple at $LOAD (jmp song / jmp songout / jmp play).
2. Find `playirq` → walk the per-voice dispatch loop to locate `wax`, `voicesto`, `counter2` (zero-page) by patterns.
3. Find the **CMP #$60 / CMP #$40 / CMP #$FF dispatcher** — anchor to it; ranges adjacent confirm shape.
4. Find `lonote`/`hinote` by scanning for the C-0 PAL pair `$C3 $DD ... / $01 $01 ...` (96 bytes × 2).
5. Find `seqtabel` indirectly via `song` routine: the SBCs/ASLs that compute `song * 6 + voice * 2` give the base; first word read is the start of voice 0.
6. Parse sequence bytes by following `h2` byte dispatch.
7. Parse pattern bytes by following `skip / noglideset / ...` chain.
8. Walk `pulsetabel`, `filterbytes`, `drumtabel`, `arplo/arphi`, instrument table to extract per-instrument programs.

## Provenance log entry

`https://github.com/Linus123/C64_6581_SID_Players/blob/master/Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm`
— annotated 1988 MoN-Deenen driver source. The repo claims byte-exact
round-trip ("Every assembly file should produce a .sid file which can be
played with any modern SID player"). Sister files in the repo:
`Hubbard_Rob/{Commando,Monty_on_the_Run}.asm`,
`Audial_Arts/{aaplayer1,aaplayer2}.asm`,
`Bjerregaard_J_{James_Bond_3,Myth}.asm`,
`Ouwehand_Reyn_{Armada,Dutch_Breeze}.asm`,
`Whittaker_David/…`, `Galway Martin/…`, `Gray_{Fred,Matt}/…`,
`Kimmel_Jeroen/…`, `Dunn_Jonathan/…`, `Bulka_Adam_FAME/…`.

The **Tel_Jeroen_MON/** subdir contains only Cybernoid 2 — Hawkeye
disassembly is NOT in this repo. Going through siddecompiler /
SIDdump-based RE will be needed.
