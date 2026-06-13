<!--
source_url: https://github.com/theyamo/CheeseCutter  (GPL)
local: tmp/dmc_hunt/CheeseCutter/  (read-only checkout, Version 2.10)
  - player asm:   src/c64/player_v4.acme   (the actual 6502 player, 1764 lines)
  - .ct format:   src/ct/base.d            (CC2 / .ct file structures, 1883 lines)
fetched_via: local read-only checkout (Read tool); codebase64 cross-check via WebFetch
fetch_date: 2026-06-13
author: CheeseCutter player by "abad" (Abaddon), "Based on JCH NP 21.G4 by Laxity/VIB"; .ct format (C) Abaddon
content_date: CheeseCutter 2.10 (player header "cc4.07"); player_v4.acme comment "feb '12"
reliability: PRIMARY (real 6502 source for the player; real D structs for the file format)
-->

# CheeseCutter — JCH NewPlayer (NP21.G4 lineage) player + .ct format

CheeseCutter (CC) is the cross-platform GPL port of the JCH NewPlayer engine.
The player at `src/c64/player_v4.acme` is the **actual 6502 player**, explicitly
labelled *"CCUTTER 2.x musicplayer by abad / Based on JCH NP 21.G4 by Laxity/VIB"*.
This is the most authoritative open-source artifact for the NP21+ write model and
the 4-byte pulse/filter table rows. The CC editor stores songs in a `.ct`/`CC2`
container whose layout is defined by D structs in `src/ct/base.d`.

The CC runtime architecture is a **relocatable variant** of the JCH NP layout: the
editor pointer block lives at `$0fa0` and a 6-char version string `"cc4.07"` at
`$0fee` (the same slots JCH NP20.gX uses — see github_sidfactory2.md). When a tune
is exported/packed the editor-only routines (`EXPORT=FALSE` regions at `$0e00`,
`$0fa0`, `$f000`, `$f800`) are stripped; the player code itself sits at
`BASEADDRESS = $1000` with `init`/`play`/`mplay` jump table.

---

## 1. Entry points (player_v4.acme lines 244-261)

```asm
        *= BASEADDRESS              ; $1000
init    jmp subinit                 ; (or jmp cinit if USE_MDRIVER)
play    jmp subplay                 ; (or jmp cplay)
mplay   jmp submplay                ; MULTISPEED extra play() for >1x frames
sync    !8 0
```

- `init` = `$1000`, `play` = `$1003`, `mplay` = `$1006` (multispeed tick).
- `subinit` (`A` = subtune) reads `songsets` to set the 3 track (orderlist) pointers
  + per-subtune song speed, clears speed/sync state, sets `state=1`.
- The first `subplay` call sees `state != 0` → runs the one-shot **silence/HR-prime
  reset** (volume=$0f, `$d417`=$f0, `synccnt=2` "HR allowed", `tsync=$fe` "sync done"
  per voice) then `state=0`; subsequent calls run the real `run` path.

### Editor dispatch byte `state` (lines 1374-1399)
`state` is a bit-flag steering the per-voice loop tail (`next`):
- bit7 (`$80`) set by `subnoteplay`/`submplayplay` = keyjam (sound-only `updsound`).
- bit6 (`$40`) set by `submplay`/`submplayplay` = multispeed call (sound-only,
  skips sequence/track advance). This is the `JMP ... / AND #$E0 / CMP #$80`
  pattern that the sidid `JCH_NewPlayer` signature `4C ?? ?? 48 29 E0 C9 80 ...`
  matches (the keyjam entry).

---

## 2. Per-voice main loop & speed/tempo (lines 324-438)

```asm
run     dec speedcnt
        bpl speeddone
        lda speed
        cmp #2
        bpl speedok            ; speed>=2 => fixed tempo
speedalt ldy speedsub          ; speed<2 => "breakspeed": tempo program read
        lda chord,y            ;   from the CHORD table (shared storage!)
        ...
speedok sta speedcnt
```

- `speedcnt` counts down each frame; at 0 a new sequence row is fetched (`updseq`),
  at 1 the track/orderlist is advanced (`updtrack`), otherwise only sound is
  updated (`updsound`). So **tempo = frames per sequence row**.
- "Breakspeed" (`speed < 2`) reads a tempo list out of the **chord table** memory
  (a `$0` speed command toggles `sync` instead — line 1152). SF2's JCH converter
  reconstructs this into a dedicated Tempo table (see github_sidfactory2.md).
- Voice loop runs `ldx #2` downward (V3, V2, V1); `voicon,x` (1/0) gates each voice.
- `synccnt,x` is incremented per frame and is the **hard-restart-eligibility**
  counter (HR only allowed when `synccnt >= 2`, i.e. enough frames since last note).

### updtrack — orderlist stepping (lines 392-438)
```asm
updtrack lda newseq,x          ; only step when a new seq is requested
        ...
        lda (ZREG),y           ; ZREG = tracklo/hi,x  (orderlist pointer)
        bpl trk02              ; <$80 => raw seq number (no transpose change)
        cmp #$80
        beq skiptrans          ; $80 => "no transpose" marker
        sbc #$a0               ; $a0+n => transpose value (n signed), store shtrans2,x
skiptrans inc tracklo,x ...
trk02   sta curseq,x           ; current sequence number
        iny
        lda (ZREG),y
        cmp #$f0               ; >=$f0 => END / wrap marker
        bcc trk03
        ...                    ; $fX low byte => new track pointer = twrap + (lo) ; song wrap (and #$07)
```

So the **orderlist** is a byte stream of optional `$a0±n` transpose bytes interleaved
with sequence numbers, terminated by a `$f0..$ff` 2-byte wrap pointer (high nibble
`$f`, plus a low byte giving the restart offset into the track). `$80` = keep
transpose. This is the same encoding the SF2 converter decodes as
`transpose = 0x20 + rawbyte`, `0xff` = end.

---

## 3. Sequence data & the per-row note/instrument/command stream (lines 440-534)

Each voice points (via `seqlo`/`seqhi[curseq]`) at a packed sequence. The decoder:

```asm
seqnext lda (ZREG),y
        cmp #$c0
        bcs command            ; >=$c0 => "command" branch (dur/instr)
        cmp #$60-1
        bcc nocmdbyt           ; <$5f => note value, no embedded cmd
        sbc #$60
        bpl nottie
        inc tienote,x          ; $5f => set TIE flag, advance
        ...
nottie  pha                    ; $60..$bf => note WITH following super-command byte
        iny
        lda (ZREG),y           ; fetch the super/command index
        beq skipcmd
        sta shsuper,x          ; shadow super pointer
        inc newcmdflag,x
...
command cmp #$f0
        bmi notdur
setdur  and #$0f
        sta duration,x         ; $fX => set per-row DURATION (delay) = low nibble
        iny ...
notdur  sbc #$c0-1
        sta shinst,x           ; $c0..$ef => set INSTRUMENT (value = byte-$bf)
        inc newinsflag,x
```

Decoded byte alphabet of the packed sequence stream (CC `Sequence.compact()`,
base.d lines 654-713 — this is the canonical packer, read it as the inverse):

| Byte range | Meaning |
|---|---|
| `$00` | rest / gate-off note (note value 0) |
| `$01` | gate-off (`===`, NOTE_KEYOFF) |
| `$02` | gate-on / hold (`+++`, NOTE_KEYON) |
| `$03..$5e` | note value (semitone), used directly (added to transpose) |
| `$5f` | TIE flag prefix for the following note byte |
| `$60..$bf` | note value (`byte-$60`) **followed by** a super-command index byte |
| `$c0..$ef` | set instrument (`value = byte - $bf`, i.e. `$c0`→inst 0) |
| `$f0..$ff` | set row delay/duration = low nibble (`$f0`=0 frames … `$ff`=15) |
| `$bf` (`SEQ_END_MARK`) | end of sequence |

`base.d` enums: `SEQ_END_MARK=0xbf`, `MAX_SEQ_ROWS=0x40` (64 rows max),
`MAX_SEQ_NUM=0x80` (128 sequences). The packer emits an instrument byte only on
change, emits a `$fX` delay byte only on change, optionally a `$5f` tie, the note,
and optionally a command byte. Delays >15 are emitted as repeated `$fX`+`$00`.

Note: CC's **on-disk** sequence is the *uncompacted* 4-byte-per-row Element form
(`[cmd, tieflag, note, ins?]` — see §6); the packed stream above is what gets
written into c64 memory for the player at save time.

---

## 4. Sound work: note trigger, ADSR/HR, pulse/filter reset (lines 539-685)

`updsound` is the per-voice sound core. Key sub-steps when a note triggers
(`tsync` reaches the gate-on phase):

```asm
syncgateon lda newinsflag,x
        beq checknote
        ldy shinst,x
        lda inst,y             ; INS_AD  (byte0)  -> shadow shad,x
        sta shad,x
        lda inst+INS_SR,y      ; INS_SR  (byte1)  -> shadow shsr,x
        sta shsr,x
        ...
checknote lda shtrans,x        ; transpose -> trans,x
        sta trans,x
        lda shnote,x
        clc
        adc trans,x            ; notereal = note + transpose
        sta notereal,x
        ...
        ldy shinst,x
        lda inst+INS_ARP,y     ; byte7 = WAVE table start pos -> wavepos,x
        sta wavepos,x
        lda shad,x : sta ad,x
        lda shsr,x : sta sr,x
        lda inst+INS_PULSP,y   ; byte5 = PULSE pointer
        beq setflt             ;   0 => no pulse program
        bpl skippdirect        ;   $80+ => DIRECT pulse (low nibble => pulsehi)
        ...
skippdirect asl : asl          ;   else *4 (row index -> byte offset, 4-byte rows)
pulsdirset sta pulsenxt,x
setflt  lda inst+INS_FLTP,y    ; byte4 = FILTER pointer (0 => no filter reset)
        asl : asl              ;   *4
        sta filtnxt
        ...
        lda inst+INS_HR,y      ; byte2: low nibble = wave/arp delay -> wavetime,x
        and #$0f
        sta wavetime,x
        lda inst+INS_HR,y
        and #$c0
        cmp #$40               ; byte2 bit pattern: $40 => SOFT restart (skip wf set)
        beq wavenotoff
        lda inst+INS_4,y       ; byte3 = HR waveform -> waveform,x ; gate test bit on
        ora #1
        sta waveform,x
        inc hardon,x
wavenotoff lda #$ff
        sta gate,x             ; GATE ON
```

### Hard restart (`syncnottied` / `syncnohr`, lines 551-573)
```asm
        lda synccnt,x : cmp #2 : bmi syncnohr   ; need >=2 idle frames
        ldy shinst,x
        lda inst+INS_HR,y : bpl syncnohr        ; bit7 set => do HR
        and #$20 : bne laxhr                    ; bit5 set => "Laxity" HR
        lda cmd2 : sta ad,x                      ; normal HR: load HR-AD from cmd2 (cmd table row0 col1)
laxhr   lda inst+INS_7,y : sta sr,x             ; HR-SR from instrument byte6
syncnohr lda #$fe : sta gate,x                  ; GATE OFF ($fe) during HR
        jmp dowave
```

HR ADSR is taken from **command-table row 0** (`cmd2`, the global "HR ADSR" slot)
for AD, and from **instrument byte 6** (`INS_7`) for SR; the Laxity variant
(`$Ax` restart type) leaves AD untouched. The `state`/`tsync` machine spreads the
gate-off / waveform-clear / gate-on across the 3 frames before the note (see
`subplay`'s `synccnt=2`, `tsync=$fe`).

---

## 5. Effect chain — exact `$D400-$D418` write model

This is the per-frame write sequence the SIDfinity rebuild must match. The chain
runs per voice inside `updatepulse` → sfx (`effstate`) → `dowave` → `checksuper` →
`setsid`, then the filter block runs once per frame at the end.

### 5a. Pulse program (`updatepulse`, lines 690-746) — 4-byte rows
`pulsenxt,x` is a **byte offset** into `pulstab` (row index × 4). Per frame:
```asm
        dec pulsecnt,x : bpl pulsenotnew        ; still counting this row?
        lda pulsenxt,x : ... tay
        lda pulstab+2,y : cmp #$ff : beq pulseskipset  ; byteC = initial PW ($ff=retain)
        sta ZREG : and #$f0 : sta pulselo,x     ; NB nibbles reversed: $48 => $8400
        lda ZREG : and #$0f : sta pulsehi,x
pulseskipset lda pulstab+0,y : and #$7f : sta pulsecnt,x  ; byteA low7 = frame count
        lda pulstab+3,y : ...                    ; byteD = jump: 0=>next row(+4), $7f=>stop, else *4
pulsenotnew lda pulstab,y : bmi pulsesub         ; byteA bit7 => subtract direction
        lda pulselo,x : clc : adc pulstab+1,y    ; byteB = add value -> pulselo (16-bit w/ pulsehi)
        ...
pulsesub lda pulselo,x : sec : sbc pulstab+1,y   ; subtract path
```
Pulse table row = **[A=duration|dir($00-7f add / $80-ff sub n frames), B=add value,
C=initial PW low/hi nibble-reversed ($ff=retain), D=jump ($00 next, $7f stop, else
×4 target)]**. (base.d `pdescr0..3` confirm verbatim.)

### 5b. SFX / commands (`effstate,x`, lines 750-947)
`effstate,x` selects the running per-voice effect; the values are:
```
0    = none
1    = slide up        (shfreq += slide  16-bit)
2    = slide down      (shfreq -= slide)
3    = hi-fi vibrato    (per-note delta scaled by amp; vibrafl "feel" ramp)
4    = lo-fi vibrato    (fixed amp shifted left twice, dir toggled by vibrafrq)
$81  = portamento       (glide plo/phi toward freqtable[notereal] by portalo/hi)
```
- **Slide up** (lines 758-766): `shfreqlo/hi += slidelo/hi`.
- **Slide down** (773-780): `shfreqlo/hi -= slidelo/hi`.
- **Hi-fi vibrato** (807-877): computes the semitone interval
  `freqtable[notereal+1]-freqtable[notereal]`, scales it right by `vibraamp`, adds a
  `vibrafl` "feel" ramp (`vibraflv` add per frame), then adds/subtracts to `shfreq`
  based on `vibradir` toggling every `vibrafrq` frames.
- **Lo-fi vibrato** (783-796 + 1273-1288): cheap fixed-depth version.
- **Portamento** (880-946): moves a 16-bit `plo/phi` toward the target note freq by
  `portalo/hi`, then `shfreq = plo/phi - freqtable[notereal]`. Started by a `$07`
  command **and** by a tie note (see `snotporta` immediate-parse at lines 505-533).
- `shfreqlo/hi` is the per-voice frequency **offset accumulator**; final freq is
  computed in `dowave`.

### 5c. Wave table & final frequency (`dowave`, lines 951-1026) — 2-byte rows
```asm
waveok  dec wavecnt,x : bpl waveprocess
        lda wavetime,x : sta wavecnt,x          ; reload wave delay
        ldy wavepos,x
        lda arp1,y : sta wavetrans,x            ; arp1[] = wave col A (transpose/loop)
        lda arp2,y                              ; arp2[] = wave col B (waveform)
        cmp #$10 : bcc waveskip                 ; <$10 => leave waveform unchanged
        cmp #$e0 : bcc wavereg                  ; $10..$df => SID ctrl reg value
        and #$0f                                ; $e0..$ef => ctrl reg $00..$0f
wavereg sta waveform,x
waveskip lda arp1+1,y : cmp #$7e : beq wavestore ; $7e => loop-to-prev (stop advancing)
        iny
        cmp #$7f : ... lda arp2,y : tay          ; $7f => loop: next col-A; jump target = col B
        ...
waveprocess lda wavetrans,x : bpl wavenotabs
waveabs and #$7f : tay                           ; $80+ => ABSOLUTE pitch (ignore note/transpose)
        lda freqtable_lo,y : sta freqlo,x
        lda freqtable_hi,y : sta freqhi,x : jmp wavedone
wavenotabs clc : adc notereal,x                  ; $00..$5f => RELATIVE transpose up
        adc chordvalue,x                         ; + current chord offset
        tay
        lda freqtable_lo,y : clc : adc shfreqlo,x : sta freqlo,x   ; + slide/vib offset
        lda freqtable_hi,y : adc shfreqhi,x : sta freqhi,x
```
Wave table row = **[A=transpose/loop, B=waveform/ctrl]**, 2 bytes/row, the two
columns stored in **separate 256-byte arrays** `arp1`/`arp2` (the `.ct` "wave"
table is `arp1` 256 + `arp2` 256, see base.d `Offsets.Arp1`). The chord engine
(`chordtpos`/`chordvalue`) adds an arpeggio offset from the chord table.

### 5d. The actual SID register writes (`setsid`, lines 1308-1323)
This is the canonical per-voice write block — **order matters**:
```asm
setsid  ldy voice,x            ; voice,x = {0,7,14} => channel base offset
        lda freqlo,x  : sta $d400,y
        lda freqhi,x  : sta $d401,y
        lda sr,x      : sta $d406,y     ; SR written BEFORE AD
        lda ad,x      : sta $d405,y
        lda pulselo,x : sta $d402,y
        lda pulsehi,x : sta $d403,y
        lda waveform,x
        and gate,x                       ; gate,x = $ff (on) / $fe (off) / and-mask
        sta $d404,y
```
Per-voice write order: **D400, D401, D406, D407?** — no: it is D400(freqlo),
D401(freqhi), D406(SR), D405(AD), D402(PWlo), D403(PWhi), D404(ctrl&gate). The
gate is folded into the control register via `AND gate,x` (`$fe` clears bit0 to
gate off without disturbing the waveform bits; `$ff` leaves gate on).

### 5e. Filter — once per frame (lines 1405-1476) — 4-byte rows, 10-bit sweep
```asm
        dec filtcnt : bpl filtnotnew
        lda filtnxt : sta filtcur : tay
        lda filttab,y : bpl filtsetcnt          ; byteA bit7 set => INIT row
        and #$70 : sta bandpass                 ; byteA bits 4-6 => passband (OR'd into $d418)
        lda filttab+1,y : sta $d417             ; byteB => $d417 (res + routing) on init row
        ...
filtsetcnt sta filtcnt
        lda filttab+1,y : and #3 : asl : sta filtadd+1   ; sweep add (10-bit)
        ...
        lda filttab+3,y : ...                    ; byteD = jump (0 next, $7f stop, else *4)
        lda filttab+2,y : cmp #$ff : beq filtnotset  ; byteC = initial cutoff ($ff skip)
        sta filter : lda #0 : sta filtlo
filtnotnew lda filtadd+1 : clc : adc filtlo ...  ; sweep accumulate (10-bit res)
        adc filtadd : sta filter
filterskip lda filtlo : sta $d415               ; cutoff low (10-bit lo)
        lda filter : sta $d416                   ; cutoff high
        lda volume
        ora bandpass                             ; volume | passband bits
        sta $d418
        rts
```
Filter table row = **[A: <$80 sweep duration / >=$80 ($90-$F0) filter-type+passband
in bits 4-6, B: add value OR (on init) resonance+channel-mask written to `$d417`,
C: initial cutoff ($ff=skip), D: jump (0 next-row+4, $7f stop, else ×4 target)]**.
The frame ends with `$d415`/`$d416` (cutoff) and `$d418` (`volume | bandpass`).
Sweeps were widened to 10-bit res in Feb 2012 (`$80` in 10-bit ≈ `$20` in 8-bit).

**Per-frame write summary (all 3 voices then global):**
for x in {V3,V2,V1}: `$D400+o,$D401+o` (freq), `$D406+o,$D405+o` (SR,AD),
`$D402+o,$D403+o` (PW), `$D404+o` (ctrl/gate). Then once: `$D417` (only on a
filter-init row), `$D415,$D416` (cutoff), `$D418` (vol|passband). `voice,x={0,7,14}`.

---

## 6. The `.ct` / CC2 on-disk format (base.d)

CC saves a `.ct` file as the 3-byte magic `"CC2"` followed by a **zlib-compressed**
blob (`std.zlib.compress`, base.d lines 1538-1539, `open()` 1301-1345). The
decompressed blob is a 65536-byte C64 memory image plus trailing metadata:

```
DatafileOffset (base.d 717-725):
  Binary    = 0          ; 64KB C64 memory image (player + tables + data)
  Header    = 65536      ; ver(1) clock(1) multiplier(1) sidModel(1) fppres(1)
                         ;   [ver>=6] songspeeds[32]  [ver>10] highlight, highlightOffset
  Title     = Header+261 ; 32 bytes
  Author    = Title+32   ; 32 bytes
  Release   = Author+32  ; 32 bytes
  Insnames  = Title+160  ; 48 instrument labels x 32 bytes
  Subtunes  = Insnames+2048 ; 32 subtunes x 3 voices x 1024-byte orderlists
SONG_REVISION (current ver) = 12.  ver<6 rejected. ver>=128 = stereo (rejected).
```

### Offset table — `$0fa0` + i*2, 16*6 entries (base.d 1364-1366)
The 64KB image carries a pointer table at `$0fa0` (one little-endian word per
`Offsets` enum entry). `initialize()` reads every table base from it:

| `Offsets` enum | meaning (CC) |
|---|---|
| Features `$0fa0` | requestedTables + per-instrument-byte flags + cmdFlags |
| Songsets | orderlist pointers (track1/2/3) + `5,7` voice masks + song speed (byte 6) |
| FREQTABLE / FINETUNE | freq tables (`freqtable_lo/hi`, 96 entries each) |
| Arp1 / Arp2 | wave table col A / col B (256 bytes each) |
| FILTTAB | filter table (256 bytes = 64 rows × 4) |
| PULSTAB | pulse table (256 bytes = 64 rows × 4) |
| Inst | instrument table (**512 bytes = 8 cols × 64**, column-major) |
| Track1/2/3 | orderlists, 0x400 each (`TRACK_LIST_LENGTH=0x200` Track entries) |
| SeqLO / SeqHI | sequence pointer low/high tables (256 each) |
| CMD1 | super/command table (`cmd1`/`cmd2`/`cmd3` packed) |
| ChordTable / ChordIndexTable | chord (128) + chord index (32) |

### Instrument layout — column-major, stride 48 (player) / 48 (CC editor)
The player (`player_v4.acme` lines 20-27, `INSNO=48`) addresses instruments
column-major: `inst+INS_xx,y` where `INS_AD=0`, `INS_SR=48`, `INS_HR=96`,
`INS_4=144`, `INS_FLTP=192`, `INS_PULSP=240`, `INS_7=288`, `INS_ARP=336`. So byte
*k* of instrument *n* lives at `inst + k*48 + n`. (base.d `getInstrument`:
`data[no + i*48]`.) The CC editor exposes 48 instruments; the classic JCH NP20
player uses 32 with stride 32.

8 instrument bytes (base.d `idescr0..7`, `instrumentFlags = 0,0,0,0,4,3,0,1`):
| Byte | INS_* | Field |
|---|---|---|
| 0 | AD | Attack/Decay |
| 1 | SR | Sustain/Release |
| 2 | HR | bit7 hard-restart, bit5 Laxity HR, bits6-7 $40=soft; low nibble = wave/arp delay |
| 3 | (INS_4) | Hard-restart waveform |
| 4 | FLTP | Filter table index (flag 4 = points to filter table) |
| 5 | PULSP | Pulse table index `$00-$3f` (flag 3 = pulse table); `$80+` = direct PW |
| 6 | (INS_7) | Hard-restart SR value |
| 7 | ARP | Wave table start pointer (flag 1 = wave table) |

### Sequence on-disk (base.d `Sequence`, 4-byte Elements)
In the editor a sequence is `MAX_SEQ_ROWS(64) × 4` bytes; each row Element =
`[Cmd, tieflag, Note, (ins)]` accessed as `raw[i*4 .. i*4+4]`. Encodings:
- Note: `data[2]`; raw value `note+0x60`; `%0x60` gives semitone; values 0/1/2 =
  `---`/`===`/`+++`. Tie = `data[1]==0x5f`.
- Instrument: `data[0]`; raw `value+0xc0`; valid when `<0x30`.
- Command: `data[3]`; non-zero ⇒ a super/command-table index.
`SEQ_END_MARK = 0xbf`. The packer `compact()` (§3) converts this to the byte stream
the player reads. The seqlo/seqhi tables hold the in-memory start address of each
of up to 128 sequences.

### Orderlist / Track on-disk (base.d `Track`, `Tracklist.compact`)
A Track is 2 bytes `[trans, number]`. `trans` `$80` = "no change", `$a0±n` =
transpose, `>=$f0` = end/wrap marker whose value encodes the loop offset
(`wrapOffset = (smashedValue/2) & 0x7ff`). `compact()` emits a trans byte only on
change and a wrap pointer `0xf000 | (wrapptr)` at the end — i.e. the same
`$a0±/seqno…$fX` byte stream the player's `updtrack` decodes.

### Command / "super" table (base.d `tSuper`, player `cmd1/cmd2/cmd3`)
Stored as three parallel 64-entry columns `cmd1` (command number), `cmd2`,`cmd3`
(two parameter bytes). **Row 0 is reserved**: `cmd2` row 0 holds the global
hard-restart AD value (player line 567 `lda cmd2`). The command numbers
(player lines 57-65, `mdescr0` 184-204):

| Cmd | Effect (`effstate`/action) |
|---|---|
| `$00` | Slide up — param = signed 16-bit speed (`effstate=1`) |
| `$01` | Slide down (`effstate=2`) |
| `$02` | Hi-fi vibrato — param1 lo-nib "feel", param2 hi-nib speed / lo-nib depth-divider (`effstate=3`) |
| `$03` | Set offset / detune — writes `shfreqhi/lo` directly (`CMD_SET_OFFSET`) |
| `$04` | Set ADSR for current note — `cmd2→ad`, `cmd3→sr` |
| `$05` | Lo-fi vibrato — speed / depth (`effstate=4`) |
| `$06` | Set waveform (param → `waveform,x`) — disabled by default in CC (`INCLUDE_CMD_SET_WAVE=FALSE`) |
| `$07` | Portamento (to a tie note) — runs until `$08` (`effstate=$81`) |
| `$08` | Stop portamento/slide (`effstate=0`) |

### "Super" high-range index commands (player `superparse2`, lines 1039-1170)
When a sequence references a super index `>= $40`, it is **not** a command-table
row but an inline action selected by the value's high range (these are the
"command table cmds" the research.md alludes to; they double as direct table jumps
and register setters):
- `$40..$5f` → set pulse program (`& $1f`, ×4 → `pulsenxt`)
- `$60..$7f` → set filter program (`& $1f`, ×4 → `filtnxt`)
- `$80..$9f` → set chord (`& $1f` → chordtpos via chordindex)
- `$a0..$af` → set Attack nibble of AD
- `$b0..$bf` → set Decay nibble of AD
- `$c0..$cf` → set Sustain nibble of SR
- `$d0..$df` → set Release nibble of SR
- `$e0..$ef` → set main volume (`& $0f` → `volume`)
- `$f0..$ff` → set speed/tempo (`& $0f`; `$0`→toggle `sync`; else set `speed`)

(Indices `< $40` go to `iscmd` and use the cmd1/cmd2/cmd3 command table above.)

---

## 7. Frequency table (player lines 1503-1536)
96-entry `freqtable_lo` / `freqtable_hi` (8 octaves × 12). First entries
`lo=$16,$27,$38,…  hi=$01,$01,$01,…`. This is the standard JCH/NP tempered table;
notereal indexes it directly. Vibrato uses `freqtable[n+1]-freqtable[n]` as the
semitone interval.

## 8. Build conditionals (player lines 11-53)
`EXPORT` (strip editor code), `MULTISPEED`, `INSNO=48`, `CIA_VALUE=$4cc7` (multispeed
CIA timer), `BASEADDRESS=$1000`, and per-effect `INCLUDE_*` flags. A finalized
(exported) tune drops the `$0e00`/`$0fa0`/`$f000`/`$f800` editor regions; the
relocatable JCH-style player + tables remain. The default CC build has
`INCLUDE_CMD_SET_WAVE=FALSE` (command `$06` absent).

## Cross-checks vs codebase64 NP20.G4 spec
codebase64 (`base:jch_20.g4_player_file_format`) gives the NP20 fixed memory map
(`$18CB` arp colA … `$2CCB` seq data) and the same sequence control-byte alphabet
(`$7F` end, `$90` tie, `$A0-$BF` instrument, `$C0-$DF` super pointer, `$80` nothing;
note byte `$00` gate-off, `$7E` gate-hold). CC is the NP21.G4 descendant: 4-byte
pulse/filter rows (vs NP20.G4 2-byte), 48 instruments (vs 32), relocatable layout.

## Leads to follow
- The `.ct` packed-sequence ($bf-terminated) and packed-orderlist ($a0±/$fX)
  byte streams are produced by `base.d` `Sequence.compact()` / `Tracklist.compact()`
  — read those as the exact inverse when writing the SIDfinity extractor.
- CC `INSNO=48` / stride 48 is a CC-ism; classic NP20.G4 HVSC tunes use 32 / stride
  32 with a fixed `$1CCB` instrument base — verify stride per-fingerprint, not
  hardcoded. The 8 instrument *fields* are identical; only the column stride differs.
- `cmd2` row-0 = global HR-AD and instrument byte6 = HR-SR is the precise HR-ADSR
  source; confirm whether NP20.G4 sources HR-AD the same way (super table row 0).
- The "breakspeed"/tempo program living inside the chord-table memory is a sharp
  edge: a `speed<2` value means "read tempo list from chord storage", and SF2's JCH
  converter rebuilds a separate Tempo table for it (github_sidfactory2.md §Tempo).
- `tools/ct2util.d` + `src/ct/build.d`/`purge.d` (not yet read) hold the .ct→.sid
  export packer and table-purge logic; mine for the exact exported memory layout.
