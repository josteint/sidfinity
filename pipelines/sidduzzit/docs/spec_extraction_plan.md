---
provenance:
  primary_source: "local: docs/src/SRC.SDI21-N50.txt (PETSCII-decoded from sdi217_seqsrc.d64)"
  secondary_source: "local: tmp/sidduzzit_research/SDI.2.1.6-docs.txt (official docs)"
  tertiary_source: "local: tmp/sidduzzit_research/sdi_217_manual.txt (PDF manual by Henrik Mortensen)"
  note_tables: "local: tmp/sidduzzit_research/SDI.2.1.6-note_tables.txt"
  release_notes: "local: tmp/sidduzzit_research/sdi217_releasenotes_README.txt"
  fetch_date: 2026-06-13
  authors: "Geir Tjelta & Glenn Rune Gallefoss (SHAPE)"
  content_date: "2013-05-18 (docs), 2014-10-12 (v2.1.7 release), 2014-05-16 (player source)"
  reliability: HIGH — player source is original Turbo Assembler source from official disk image;
    docs are official and match source labels; manual confirms and clarifies docs.
---

# SID Duzz'It v2.1 — Extraction Plan (Binary SID → USF)

## Background

An SDI SID file is produced by the editor's "DUMP" function followed by assembly
in Turbo Assembler.  The process concatenates the player source
(`SRC.SDI21-N50` or `SRC.SDI21-SPD50`) with the dumped music data, assembles
from `$1000`, and saves the resulting PRG as a raw binary (loaded as a PSID).

The music data is APPENDED at the end of the player source in Turbo Assembler;
the labels `w`, `f`, `p`, `a` (arp data), `ad`/`al` (arp table), `v`
(vibrato), `fi` (filter), `z0`–`z9` (instrument columns), `sl`/`sh` (sequence
lo/hi ptrs), `tl`/`th` (track lo/hi ptrs), `s`, `c`, `fv`, `fs`, `tp`, `tem_p`,
`tem_d` are defined by the music data block.  The player code references these
labels directly.

---

## HVSC Coverage Note

- Engine tag in `hvsc84.db`: `Geir_Tjelta/SIDDuzz'It`
- Total HVSC SIDs: 934
- Canonical layout (init=$0FFF or $1000, play=$1003): 609 (65%)
- Other load addresses ($2000, $3000, $4000, $8000, $E000, etc.): 325 SIDs —
  same player engine relocated to a different address.  Extraction strategy is
  identical; only the absolute addresses differ.
- The `init=$0FFF` pattern means the PSID header init address is `$1000 - 1 = $0FFF`:
  a common PSID convention meaning "jump into the init stub one byte before the
  JMP table" — in SDI's case, `$0FFF` is a one-byte stub (often `NOP` or a fill
  byte) that falls through into `$1000 = JMP init`.  The actual init logic is at
  the `JMP init` at $1000.

---

## Step 1 — Anchor the Player Version and Detect Assembly Flags

### 1a. Entry-Point Fingerprint

The exported SID always starts at load address `$1000` with this JMP table
(source: `SRC.SDI21-N50.txt`, `*= $1000` section):

```
$1000  JMP init      ; 3 bytes — init, X = subtune 0..$1F
$1003  JMP play      ; 3 bytes — main play (tracks + sequences + sounds)
$1006  JMP fadeout   ; 3 bytes — fadeout, A = $00..$7F (only if rem_fad = 0)
$1009  [varies]      ; normal player: no 4th entry (or filler bytes)
                     ; speed player: JMP splay
```

From the source:
```
jmp init    ;Call with X
jmp play
r▁fad3   jmp fadeout ;negative # =down
         *= *-((*-r▁fad3)*rem▁fad)
jmp splay          ; speed player only — this becomes $1009
```

**Note:**  When `rem_fad = 1` (fadeout stripped), the `$1006` JMP is omitted
(the assembler removes it via the `*= *-(...)` trick).  The $1009 jump is
present only in the speed-player variant.

Player identification string follows at `$100C` (or wherever the filler lands):
```
.text "-player v2.1 "   (normal)
.text "-speedplayer v2.1 " (speed)
```

**OPEN [RE-1]**: Confirm exact bytes at `$1000`–`$100F` with
`tools/siddump --memwatch 1000-100f` on a representative HVSC SDI SID to verify
the exact layout (the `rem_fad` flag affects byte layout).

### 1b. Detect Assembly Flags Baked into the Binary

The player source uses TASS's `*= *-(condition)` trick to
conditionally include/omit code blocks.  The following flags affect the exported
SID's size and capabilities:

| Flag | Default | Effect |
|------|---------|--------|
| `rem_4ch` | 1 | Strip channel 4 (tempo/transpose/filter track) |
| `rem_det` | 0 | Keep detuning |
| `rem_gout` | 0 | Keep gate timeout |
| `rem_1wf` | 0 | Keep 1st WF byte |
| `rem_wfd` | 1 | Strip WF delay (FE cmd) |
| `rem_adsr` | 1 | Strip ADSR command (FD cmd) |
| `rem_mp` | 1 | Strip multipulse (FB cmd) |
| `rem_wfr` | 1 | Strip WF repeat (FA cmd) |
| `rem_wf0` | 1 | Strip D415 write (F0-F7) |
| `rem_puw` | 1 | Strip WF pulse cmds (EB-EE) |
| `rem_pu` | 0 (default N50 src) | Keep pulse routine |
| `rem_we2` | 1 | Strip E2-E7 noise trick |
| `rem_arp` | 0 | Keep arpeggio |
| `rem_fi` | 0 | Keep filter |
| `rem_fspd` | 0/1 | Filter speed (variable) |
| `rem_glid` | 0 | Keep glide |
| `rem_vib` | 0 | Keep vibrato |
| `rem_cc` | 1 | Strip Crazy Comet vibrato |
| `rem_fad` | 1 | Strip fadeout |
| `rem_gat` | 1 | Strip GAT/FLG sequence command |
| `rem_f20` | 1 | Strip seq command $20 (filter toggle) |
| `rem_wfo` | 1 | Strip WF ORA command |
| `rem_voff` | 1 | Strip voice on/off |
| `rem_trkl` | 1 | Tracks max $FF bytes (NOT 16-bit) |
| `rem_tp` | 0 | Keep tempo programs |
| `rem_opt` | 0 | All channels get speed update |

**OPEN [RE-2]**: These flags are baked silently into the binary.  Detecting which
flags were used requires disassembling the player and checking whether the
conditional code blocks are present.  A practical approach: for each SID in the
family, run `siddump --pc-trace` and look for presence/absence of the known code
patterns (e.g., pulse routine entry, filter routine).  For the initial migration,
target SIDs with the most common default flag set (rem_pu=0, rem_arp=0, rem_fi=0,
rem_glid=0, rem_vib=0, rem_tp=0 — i.e., the N50 defaults).

**OPEN [RE-3]**: Distinguish normal vs speed player variant by checking for the
`JMP splay` at `$1009` (speed player) vs absent/filler (normal player).  The
speed player source (`SRC.SDI21-SPD50`) assembles to a slightly different binary.

---

## Step 2 — Locate the Music Data Region

The player code (`$1000`..`~$19xx`) is followed immediately by the music data
appended by the dumper.  The exact start address of the music data region is
**not fixed** — it depends on which assembly flags were active (each `rem_*=0`
adds code).

**OPEN [RE-4]**: Determine the music data start address empirically per SID:
scan forward from `$1900` (approximate minimum player size) for the label anchor
bytes. The first label in the data block is `w` (waveform program), which starts
with the first waveform byte.  However, because `w` is just a Turbo Assembler
label (no sentinel byte), the actual anchor must be derived from the player's
use of `lda w-1,y` — i.e., the waveform table is at `w` = first byte of
program-table data.  A cleaner anchor: use the player's `*= $1000` and the
known player source size to estimate the data start, then validate by reading
the instrument columns.

Alternative: extract the music data start by disassembling the player and reading
the literal address operand of the first `lda w-1,y` instruction (absolute indexed
mode — the address will be `w-1`).

**Strategy for extraction**: after verifying the player size for a given flag set,
read the binary offsets of `w`, `f`, `p`, etc. directly from the assembled binary.
Use `tools/siddump --pc-trace` + `--writelog` on a real SID to establish ground truth.

---

## Step 3 — Player In-Memory Data Layout

The player has a 7-byte-stride interleaved per-voice state block starting at
the `chanon` label.  From the source (`*= $1000`):

```
chanon   = *          ; [chanidx+0] channel-on bitmask (1=$01/$02/$04)
chanoff  = *+1        ; [chanidx+1] channel-off bitmask (~chanon)
trklo    = *+2        ; [chanidx+2] track ptr lo
trkhi    = *+3        ; [chanidx+3] track ptr hi
tdelay   = *+4        ; [chanidx+4] track delay countdown
tracky   = *+5        ; [chanidx+5] track Y index (8-bit or lo of 16-bit)
trackhi  = *+6        ; [chanidx+6] track ptr hi (16-bit mode only)
```

Three initial entries at offsets 0, 7, 14 (voices 1–3) plus a 4th at offset 21
(channel 4, only when `rem_4ch=0`).

Per-voice sequencer state (stride 7, starting after chanx):
```
transp   = *+1  ; transpose
dur      = *+2  ; note duration (frames, reload)
duration = *+3  ; note duration countdown
seqp     = *+4  ; sequence position
sound2   = *+5  ; pending instrument number
note2    = *+6  ; pending note
```

**Key point**: the player references these as `transp,x`, `sound2,x`, etc. where
`x` is the 7*voice offset (x=0 for voice 3, x=7 for voice 2, x=14 for voice 1 —
player iterates from high to low, `ldx #channels*7` then decrements by 7).

---

## Step 4 — Track Data Format

From `track_init` in the source:

```
lda (mzero),y
bpl bn28           ; ≥$80: special byte
cmp #$f7           ; $f8-$ff: jump
bcc t▁del          ; $c0-$f7: delay byte ($C0-$BF encodes delay, $Cx = delay count &$3f)
                   ; then seqbyte follows after
; $80-$BF: loop-jump or stop
; $A0-$BF transpose then seq#
; $80-$9F: transpose down (transp = val - $A0, signed)
; $00-$7F: sequence number
```

Track bytes (confirmed by source `track_init` code):

| Byte value | Meaning |
|-----------|---------|
| $00–$7F | Sequence number (sequence to play) |
| $80–$9F | Transpose down: transp = byte - $A0 (i.e., -(byte & $1F) semitones) |
| $A0 | No transpose (transp = 0) |
| $A1–$BF | Transpose up: transp = byte - $A0 (positive) |
| $C0–$F7 | Delay: `tdelay = byte & $3F`, then next byte = sequence number |
| $F8+ | Jump: `and #7` gives hi-bits of jump offset, next byte is lo offset |
| $60 (= STOP) | Stop track (`trk_end` when no 4th channel) |
| $E0 (= STOP, 4ch mode) | Stop track when channel 4 active |

**OPEN [RE-5]**: The stop-byte value depends on `rem_4ch`.  In the source:
```
trin1    sta trk▁end     ; $60 written here if rem_4ch=1
trin3    sta trk▁end     ; $e0 written here if rem_4ch=0
```
Confirm which value is used in the actual exported SID binary by reading the
byte at `trk_end` address.

Track pointer init: from `init` routine, `tl,y` / `th,y` are the track lo/hi
address arrays; the music data has one entry per subtune × channel.

---

## Step 5 — Sequence Data Format (Dumped Binary Format)

The dumped sequence format is COMPACT (not the editor's row-based format).
From the docs and the serialized examples (docs.txt lines 1386–1494):

Each sequence is a variable-length byte stream terminated by `$00`.

### Sequence stream byte encoding

Parsed in `fxjmp` / sequencer section of the player:

**FX byte** (`lda (mzero),y` — first byte read per event):

| Value | Meaning |
|-------|---------|
| $5F | End of sequence / tie note marker |
| $F0–$FF | Set release nibble (lo 4 bits) + no note |
| $C0–$EF | Arpeggio select: `arpnum2 = (val & $3F) << 1`; next byte = note |
| $A0–$BF | Glide: `glidadd2 = (val & $1F) << 2`; next byte = note |
| $80–$9F | Instrument select + arpeggio wf: `arpnum2 = val; sound2 = val & $3F` |
| $00–$7F | Instrument select: `sound2 = val` |

From the FX decode section (`sequ2`/`fxjmp`):
```
cmp #$c0 → bcs → arpeggio ($C0-$EF range)
cmp #$a0 → bcs → glide ($A0-$BF range)
cmp #$80 → bcs → arpeggio wf (instrument in $80-$9F with arp waveform flag)
else → plain instrument select
```

**Note byte** (second byte, read after FX byte):

| Value | Meaning |
|-------|---------|
| $E0–$FF | Duration (2-byte encoding: `$E0-$FF` → extended, next = actual duration) |
| $DF–$E0 | Extended duration (see below) |
| $60–$7F | Duration (1-byte: `dur = val & $1F`) |
| $00–$5F | Note (`note2` = val + transp) |
| $5F | Gate off (tie note gat) |

From docs line 1387 (example): `01 C-4` → dumped as `81,61,30,0`
- `$81` = sound $01 (instrument select, $80 means arp-wf mode for inst 01)
- `$61` = duration $01 (= $61 & $1F = 1)
- `$30` = note C-4 (from note table: $30 = C-4)
- `$00` = end of sequence

Extended duration example from docs:
```
A empty $1F long sequence: 7F,5F,0
  $7F = duration ($7F & $1F = $1F = 31 frames? — actually $60-$7F range: dur = val & $1F)
  $5F = end of seq marker
A empty $3F long sequence: 5F,FF,5F,0
  $5F = first end marker / empty
  $FF = ?
  $5F = second end marker
  $00 = term
A empty $7F long sequence: 5F,E0,7F,5F,0
```

**OPEN [RE-6]**: The exact duration/note byte encoding needs RE from the player
source sequencer section.  From the `fxjmp` decode:
```
cmp #$df → bcc bn7   (< $DF = note)
beq dur▁20           ($DF = two-byte duration follows)
and #$3f → bne bn12  ($E0-$FF with nonzero lo = duration = val & $3F)
dur▁20: iny; lda (mzero),y; bne bn12  (follow-on byte)
```
So:  $60-$7F = duration (`dur = val & $1F`); $DF = long duration; $E0-$FF = duration `val & $3F`.
Full decoding of the $80-$DE range, tie notes, and the `$F0-$FF` release effect
requires careful source tracing.  Run `tools/siddump --pc-trace` on a known SID
to observe the branch paths per note.

**Tie notes** (small-letter notes in editor): from source,
```
bn6:  iny; lda (mzero),y → note read; cmp #$5F → note2 stored as 'tie'
```
Tie notes do not restart instrument programs.

**Gate/GAT**: The `$5F` value in the note column sets `gate=0` (gate off).
The `$00` terminates the sequence stream.

---

## Step 6 — Channel 4 (Tempo / Transpose / Filter Track)

Channel 4 is only present when `rem_4ch = 0`.

From `cond_seq` / `track_conduct` code path:
- FX byte `$01–$1F` = set tempo directly
- FX byte `$40–$60` = look up tempo program
- Note byte = transpose value (GAT = 0 transpose)

The conductor runs off the duration counter at `duration+21` (the 4th voice slot).
When a new track entry fires, `release+21` (hi nibble × 16) sets the filter
cutoff, `glidadd2+21` controls filter program/force.

**OPEN [RE-7]**: Full channel-4 command encoding needs detailed tracing of
`cond_dur`, `cond_seq`, `cond_ret`, `cond_on` paths.  The filter-program pointer
from channel 4 vs. instruments on channels 1–3 interact non-trivially.

---

## Step 7 — Instrument Table (z0–z9 columns)

From the player source accesses and docs:

| Column label | Instrument field | Docs name |
|-------------|-----------------|-----------|
| `z0,y` | Waveform PRG pointer | WAVEFORM PRG |
| `z1,y` | Attack/Decay | ATTACK/DECAY |
| `z2,y` | Sustain/Release | SUST/RELEASE |
| `z3,y` | Gate Timeout | GATE TIMEOUT |
| `z4,y` | Vibrato PRG pointer | VIBRATO PRG |
| `z5,y` | Pulse PRG pointer | PULSE PRG |
| `z6,y` | Filter PRG pointer | FILTER PRG |
| (z7,x) | Band/Resonance | BAND/RESONANS |
| `z8,y` | Detune Hi | DETUNE HI |
| `z9,y` | Detune Lo | DETUNE LO |

**Column-major layout** (from docs + editor memory map):
```
E700–E730   z0 = WF prog ptrs (48 instruments × 1 byte each)
E730–E760   z1 = AD
E760–E790   z2 = SR
E790–E7C0   z3 = Gate timeout
E7C0–E7F0   z4 = Vibrato PRG ptr
E7F0–E820   z5 = Pulse PRG ptr
E820–E850   z6 = Filter PRG ptr
E850–E880   z7 = Band/Resonance (note: accessed as z7,x not z7,y in player)
E880–E8B0   z8 = Detune hi
E8B0–E8E0   z9 = Detune lo
```

Each column is $30 bytes = 48 instruments (32 normal + 16 arpeggio-only).

**OPEN [RE-8]**: The `z7` access uses `z7,x` (voice index) not `z7,y`
(instrument index) in the filter section of the source:
```
lda z7,x       ; in filter routine, fi+2-4 branch
```
This may indicate `z7` is addressed differently — confirm by examining exactly
where `z7` is defined and accessed in the full source.  There is also no `z7,y`
access found in the player; filter band/resonance may be stored differently.

**In the exported (dumped) SID binary**, the instrument columns appear at a
fixed relative layout determined by the TASS `*= $1000` assembly.  Their
absolute addresses in the SID binary can be found by:
1. Disassemble the player and find `lda z0,y` → read the absolute address operand
   = `z0`.  Then `z1 = z0 + $30`, `z2 = z0 + $60`, etc.

---

## Step 8 — Waveform Program Table (w, f)

From the source: accessed as `lda w-1,y` (waveform byte, column 1) and
`lda f-1,y` (note byte, column 2).  The `-1` offset exists because `y` is
incremented BEFORE the waveform byte is read within the loop.

Layout (from editor memory: `E000–E100` = waveform, `E100–E200` = note):
- `w[i]` = waveform byte for table entry `i`
- `f[i]` = note byte for table entry `i`

In the exported binary, `w` and `f` are two separate $100-byte arrays.

**Waveform byte values** (column 1):

| Value | Meaning |
|-------|---------|
| $10 | Triangle |
| $20 | Sawtooth |
| $40 | Pulse |
| $80 | Noise |
| $11 | Triangle + gate |
| $21 | Sawtooth + gate |
| $41 | Pulse + gate |
| $81 | Noise + gate |
| $91 | Triangle + gate (arpeggio wf) |
| $A1 | Sawtooth + gate (arpeggio wf) |
| $B1 | Tri+Saw + gate (arpeggio wf) |
| $C1 | Pulse + gate (arpeggio wf) |
| $D1 | Pulse+Tri + gate (arpeggio wf) |
| $E1 | Pulse+Saw + gate (arpeggio wf) |
| $FF | Jump: `f[y]` = jump target |
| $FE | Delay: `f[y]` = delay frames |
| $FD | ADSR: `f[y]` = gate-off timeout, `w[y+1]` = AD, `f[y+1]` = SR |
| $FB | Multipulse: 3-byte command |
| $FA | Repeat: `f[y]` = repeat count |
| $F0–$F7 | Write to $D415 (lo filter cutoff) |
| $EE | Pulse init: write `f[y]` to $D402/D403 |
| $ED | Pulse subtract: sub `f[y]` from pulse |
| $EC | Pulse add: add `f[y]` to pulse |
| $EB | Pulse write: write `f[y]` lo/hi to $D402/D403 |
| $E2–$E7 | Noise trick: write value to waveform register |
| $90–$BF | (arp range): and'd with $7F before SID write |

**Note byte values** (column 2, `f[y]`):

| Value | Meaning |
|-------|---------|
| $00–$5E | Soft note upwards: add to note+transpose |
| $60–$7F | Soft note downwards: subtract from note+transpose |
| $80–$DE | Fixed note (index into frequency table, ignores transpose) |
| $DF–$FF | Unused |

---

## Step 9 — Pulse Program Table (p)

From the docs and source (accessed as `p-4,y`):

4 bytes per entry:
- `p[i*4+0]` = pulse lo start value → $D402
- `p[i*4+1]` = pulse hi start value → $D403
- `p[i*4+2]` = target hi value / sweep target
- `p[i*4+3]` = mode / speed / jump:
  - `$00,$40,$80,$C0` = stop at end value
  - `$01–$3F` = sweep to end, then jump to entry (lo nibble = target entry)
  - `$40–$7F` = continuous sweep (same program line or different)
  - `$80–$BF` = reverse sweep, jump on end
  - `$C0–$FF` = reverse continuous sweep

From source: `lda p-4,y; sta sid+2,x; sta sid+3,x` — pulse is accessed with
`y = pulsle*4`, i.e., 4 bytes per entry, hence `p-4` offset.

**OPEN [RE-9]**: Confirm exact byte ordering of pulse table entry vs. what the
source reads (`p-4,y` accesses first, then presumably `p-4+1,y` etc.) by
tracing the pulse routine in `pulse3` / `go_pulse`.

---

## Step 10 — Filter Program Table (fi)

From the source (accessed as `fi-4,y`, `fi+1-4,y`, `fi+2-4,y`, `fi+3-4,y`):

4 bytes per entry (same 4-byte stride as pulse, referenced as fi-4 offset):
- `fi[i*4+0]` = filter cutoff hi → $D416
- `fi[i*4+1]` = target hi value (or filter-frame data)
- `fi[i*4+2]` = sweep speed
- `fi[i*4+3]` = mode / jump (same mode encoding as pulse, with filter-frame
  special case when `fi[i*4+1] == 0`)

From source comment: `fi+1-4,y ;frame v2.1` — when `fi+1-4,y == 0`, the filter
enters "filter frame" mode (different handling of band+resonance + delay).

Docs describe (docs.txt lines 912–936):
```
c1 = filter cutoff hi ($D416)
c2 = target (or 0 = filter frame)
c3 = band+resonance (when frame mode) or speed
c4 = mode/delay
```

**OPEN [RE-10]**: Confirm exact filter-frame vs normal filter-sweep detection
condition.  From source: `fi+1-4,y; bne *+7` → non-zero = normal sweep;
zero = filter frame.  Trace the filter-frame branch (z7 band/res write path).

---

## Step 11 — Vibrato Program Table (v)

From the source (accessed as `v-3,y`, `v+1-3,y`, `v+2-3,y`):

3 bytes per entry (referenced as `v-3` offset):
- `v[i*3+0]` = delay / command byte
- `v[i*3+1]` = width (vibrato) or detune lo
- `v[i*3+2]` = speed (vibrato) or detune hi

From docs:
- `$01–$FD` = delay (wait N frames before running vibrato)
- `$00` = detuning and continue
- `$FE` = detuning and hold
- `$FF` = infinite loop on vibrato

The player references `v-3,y` then increments for `v+1-3,y` and `v+2-3,y`,
confirming 3-byte stride.

---

## Step 12 — Arpeggio Tables (a = data, ad = program table)

From the docs and source (accessed as `ad,y`, `ad+1,x`, `a,y`):

**Arpeggio data** (`a` label): byte stream of arp note offsets; `$80+` = loop marker.

**Arpeggio program table** (`ad` label): entries are 2 bytes (`ad[i*2+0]`,
`ad[i*2+1]`):
- `ad[i*2+0]` = program line pointer (byte index into arp data `a`)
- `ad[i*2+1]` = speed + sound:
  - lo nibble–1 = speed-1 (speed 1–4; nibble $0=speed1 ... $3=speed4)
  - hi nibble = instrument number for arpeggio

From source:
```
r▁arp1  lda arpnum2,x    ; arp number (0..47)
         sta arpnum,x
         tay
         lda ad,y         ; ad[arpnum] = data pointer
         sta arple,x
```

And in the arp execution:
```
r▁arp4  bcc wf▁stand
         lda arpnum,x
         bmi wf▁stand
         tay
         sec
         lda arpde,x
         sbc #$40
         bcs *+5
         lda ad+1,y       ; ad[arpnum+1] = speed/sound
         sta arpde,x
         ldy arple,x
         bcs *+5
         inc arple,x
         lda a,y          ; arp data byte
```

**OPEN [RE-11]**: The exact arpeggio speed counter and wrapping logic needs
full source tracing.  `arpde,x` appears to serve as a speed counter, initialized
from `ad+1,y`.  Trace the `arpde` decrement path and loop-back condition.

---

## Step 13 — Tempo Program Table (tem_p, tem_d)

From source:
```
tem▁prg  lda #0         ; load tempo program pointer
         bmi tem▁num    ; negative = use raw tempo value
         tay
         lda tem▁p,y    ; load tempo data ptr
         clc
tem▁y    adc #0         ; add offset
         tay
         lda tem▁d,y    ; load tempo value
         bpl tpl        ; positive = use value
         ldy #$ff       ; negative: reset to start
         sty tem▁y+1
tpl      inc tem▁y+1
tem▁num  and #$7f       ; mask to 7 bits
         sta tempo+1
```

**Tempo data** (`tem_d`): byte array; `$80+` = loop (jump to start of this
tempo program).

**Tempo program table** (`tem_p`): pointer array, one entry per tempo program,
pointing into `tem_d`.

From editor memory: `ED40–ED70` = Tempo program table ($30 = 48 entries).

---

## Step 14 — Subtune / Song Table (s, c, fv, fs, tp, tl, th)

From `init` routine:
```
lda c,x    → voff+1         (channel-on mask for subtune)
lda s,x    → tem_prg+1      (tempo program for subtune)
lda fs,x   → filter speed / filter-enable init for subtune
lda fv,x   → volume init for subtune (hi nib = fade, lo nib = start vol)
ldy tp,x   → Y = initial track pointer index for subtune
lda tl,y   → trklo for each channel
lda th,y   → trkhi for each channel
```

Each subtune has one entry in the `s`, `c`, `fv`, `fs`, `tp` arrays.
`tl`/`th` are arrays of track addresses, organized with `tp[subtune]` as an
index into them.

**OPEN [RE-12]**: Layout of the `s`, `c`, `fv`, `fs`, `tp` arrays and their
stride.  Are they single-byte arrays indexed directly by subtune (0–31)?
From the source the `x` register holds the subtune number at init time and is
used directly to index `c,x`, `s,x`, etc., suggesting flat arrays of 32 bytes.

The `tl`/`th` arrays hold absolute addresses of track data for each subtune ×
channel combination.  With 32 subtunes × 4 channels (or 3 if rem_4ch=1) = up
to 128 entries.

**OPEN [RE-13]**: Exact layout of `tl`/`th` (single flat array of addresses, or
grouped per subtune?).  Trace the index `y` = `tp[x]` → `tl[y]` access.

---

## Step 15 — Initial Volume / Filter (fv, fs)

From `init`:
```
lda fv,x        ; fv = InVol entry for subtune
pha
and #$0f
sta vol+1       ; set initial master volume
...
lda fs,x        ; fs = filter setup for subtune
tay
and #$0f
sta fspeed+1    ; filter speed delay
lsr a ×4
sta filtena+1   ; forced filter enable mask (1,2,4 = ch1,2,3; 3,5,6,7 = combos)
```

This maps to the `INVOL` / filter setup from the editor (`EDC0–EDE0` = InVol volume,
`EDE0–EE00` = InVol filter).

Format:
- `fv[subtune]` hi nibble = fade-in rate (0 = no fade); lo nibble = starting volume
- `fs[subtune]` hi nibble = forced filter channel mask; lo nibble = filter speed delay

---

## Step 16 — Frequency Table

From source (end of player code):
```
freqhi  .byte ... (96 entries, PAL)
freqlo  .byte ... (96 entries, PAL)
```

96 note entries covering octaves 0–7, 12 semitones each.  Indexed by note value
($00–$5F in the waveform note column → index 0–95).

The same frequency table appears in the dumped binary.  Its location is fixed
relative to the player code.

**OPEN [RE-14]**: Confirm whether the frequency table is always PAL in HVSC
SIDs (most HVSC SIDs target PAL).  The source includes a separate NTSC table
as an optional substitution.

---

## Summary of Extraction Order

1. Anchor player at `$1000`, identify normal vs speed variant
2. Detect `rem_4ch` flag (affects channel count and stop-byte)
3. Locate music data start (relative to `$1000` + player size)
4. Extract subtune count from `chanon` array or by scanning `c`/`s`/`fv`/`fs`/`tp`
5. Extract per-subtune: initial volume, filter mask, filter speed, tempo program, track ptrs
6. Extract track data for each subtune × channel
7. Extract sequence data (variable-length byte streams, 0-terminated)
8. Extract waveform program table (w[] and f[], $100 each)
9. Extract pulse program table (p[], 4 bytes/entry)
10. Extract filter program table (fi[], 4 bytes/entry)
11. Extract vibrato program table (v[], 3 bytes/entry)
12. Extract arpeggio data (a[] stream) and program table (ad[], 2 bytes/entry)
13. Extract tempo data (tem_d[]) and program table (tem_p[])
14. Extract instrument columns z0–z9 (48 entries each)
15. Cross-validate: for each subtune, simulate the play loop and compare against
    `siddump --writelog` output

---

## OPEN Items Summary

| ID | Description |
|----|-------------|
| RE-1 | Confirm JMP table layout at $1000 (rem_fad effect) |
| RE-2 | Detect assembly flags baked into binary (pc-trace approach) |
| RE-3 | Distinguish normal vs speed player variant |
| RE-4 | Locate music data start address per SID |
| RE-5 | Stop-byte value ($60 vs $E0) depends on rem_4ch |
| RE-6 | Full sequence byte encoding (duration, note, tie, release) |
| RE-7 | Channel 4 command encoding (tempo, filter, transpose) |
| RE-8 | z7 (band/resonance) access pattern — not z7,y but z7,x |
| RE-9 | Confirm exact pulse table byte ordering |
| RE-10 | Filter-frame vs normal sweep detection condition |
| RE-11 | Arpeggio speed counter and loop-back logic |
| RE-12 | s/c/fv/fs/tp array stride (32-byte flat?) |
| RE-13 | tl/th track address array layout |
| RE-14 | PAL vs NTSC frequency table detection |

Each OPEN requires a `siddump --pc-trace` + `--writelog` run on a known SDI SID,
NOT py65 or speculative code.
