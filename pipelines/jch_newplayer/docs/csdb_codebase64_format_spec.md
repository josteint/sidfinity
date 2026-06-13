# JCH NewPlayer — codebase64 byte-level file-format spec (+ authoritative cross-refs)

> **Provenance**
> - **source_url (primary):** https://codebase64.com/doku.php?id=base:jch_20.g4_player_file_format
>   (raw DokuWiki source fetched via `?do=export_raw`)
> - **source_url (authoritative cross-ref):** https://raw.githubusercontent.com/theyamo/CheeseCutter/master/src/c64/player_v4.acme
>   (the CheeseCutter v4.07 player source — header reads *"Based on JCH NP 21.G4 by Laxity/VIB"*)
>   and `src/ct/dump.d` (the binary serializer that emits the table layout below).
> - **fetched_via:** curl (Firefox UA) for the codebase64 raw export + raw.githubusercontent.com; WebFetch for codebase64 HTML render.
> - **fetch_date:** 2026-06-13
> - **author:** codebase64 page by **FTC/HT** (Frank Tegelkamp? signed "FTC/HT"), NOT JCH; player asm by **Abaddon** porting **Laxity/Vibrants'** NP21.G4.
> - **content_date:** codebase64 page undated (~2010s); CheeseCutter player asm version string `cc4.07` (man page dated Nov 2018).
> - **reliability:** HIGH for table memory offsets + sequence byte-pair encoding (codebase64, self-described "not 100% complete"). VERY HIGH for byte-field *semantics*, effect encodings and the per-frame write model (taken from the actual player source). **Caveat:** the codebase64 page documents **NP 20.G4** (2-byte pulse/filter rows, 32 instruments, 8-byte row-major instrument records); the CheeseCutter player documents the **NP 21.G4 / CC v4 lineage** (4-byte pulse/filter rows, 48 instruments, *column-major* instrument table, 3-byte command table). Version deltas are flagged inline and summarised at the bottom.

---

## 0. Engine identity & entry points

- **Author:** Jens-Christian Huus (JCH) of **Vibrants**; editor first released Nov 1988. Descends from DMC. Later G-series/Q-series players maintained/extended by **Laxity** (Vibrants) and **Dane** (Booze Design, NP22–25).
- **Load address:** `$1000`. **init = $1000** (`A` = subtune number), **play = $1003** (call at 50 Hz).
- A multispeed variant exposes a third entry **mplay = $1006** (CIA-driven extra sound-only frames); see §9.
- Player code ≈ 1 KB (NP20.G4) up to ≈ 1.9 KB (CheeseCutter v4); 2 zero-page bytes (`ZREG=$fb/$fc` in CC). CPU ≈ 12–13 rasterlines (NP20.G4).

---

## 1. Memory map of tables — NP 20.G4 (codebase64, VERBATIM)

The codebase64 page lists fixed table base addresses for a `$1000`-based NP20.G4 file
(player occupies `$1000`..~`$18CA`, then the data tables):

```
Arpeggio table Col 1       | $18CB    (a.k.a. "wave table A" / arp1)
Arpeggio table Col 2       | $19CB    (wave table B / arp2)
Filter table               | $1ACB
Pulse table                | $1BCB
Instrument table           | $1CCB
Sequence Pointers (Lobyte) | $1DCB    (seqlo)
Sequence Pointers (Hibyte) | $1ECB    (seqhi)
Super Table                | $1FCB    (command table)
Sequence List - Voice 0    | $20CB    (order list / "tracks" voice 0)
Sequence List - Voice 1    | $24CB    (order list voice 1; +$0400)
Sequence List - Voice 2    | $28CB    (order list voice 2; +$0400)
Sequence 0 data            | $2CCB    ("Seq data starts at +3 bytes from here")
Sequence 1 data            | $2DCB    ("Seq data starts at +3 bytes from here")
Sequence ... data          | ...      (each sequence on its own $100-byte page)
```

Notes pulled from the page text:
- *"Most of the tables contain data just as it is shown from within the editor."* — i.e. each table is a flat byte image of the corresponding editor screen.
- The **arpeggio tables are the wave table** (col 1 / col 2 = the two wave-table columns; see §6). codebase64 calls them "Arpeggio" because they drive relative-pitch arps.
- Order list per voice spans `$0400` bytes (1024). Sequence-pointer tables are 256 bytes each (lo + hi → up to 256 sequences addressable, though editor caps lower — see version notes).
- *"Seq data starts at +3 bytes from here"*: each sequence page begins with 3 header/pad bytes before the AA/BB stream. (The CheeseCutter `emptyseq` macro emits `$f0,$f0,$60,$00,$bf` — see §5 for how `$f0`/`$60` decode; the "+3" reflects the editor's per-seq leading bytes.)

> ⚠ These absolute addresses are **NP20.G4-specific** and depend on player size. A real decompiler MUST NOT hardcode them across versions — instead read the **pointer block at `$0FA0`** (present in editor builds; see §2) or fingerprint the player and derive table bases from its size. The player-relative table *order* (arp1, arp2, filt, pulse, inst, seqlo, seqhi, cmd, track1-3, seq data) is stable across the family; the absolute bases shift with player length and INSNO.

---

## 2. Editor header / pointer block (from the player source)

CheeseCutter/JCH editor builds carry a **fixed pointer table at `$0FA0`** and a **feature/description block at `$0E00`**. A finalized (packed/exported) tune normally strips the `$0E00`/`$0F00` editor regions, but the `$0FA0` pointer block is how tools locate every data table without hardcoding addresses. Layout (from `player_v4.acme`, `Offsets` enum in `ct/base.d`):

`$0FA0` pointer block (each entry is a 16-bit pointer to the named table):
```
$0FA0 features              $0FC0 filttab        (filter table)
$0FA2 volume                $0FC2 pulstab        (pulse table)
$0FA4 editorflag            $0FC4 inst           (instrument table)
$0FA6 songsets              $0FC6 track1         (order list V0)
$0FA8 playspeed             $0FC8 track2         (order list V1)
$0FAA subnoteplay           $0FCA track3         (order list V2)
$0FAC submplayplay          $0FCC seqlo
$0FAE instrumentDescr.Hdr   $0FCE seqhi
$0FB0 pulseDescr.Hdr        $0FD0 cmd1           (command table col 1)
$0FB2 filterDescr.Hdr       $0FD2 s0             (sequence 0 data)
$0FB4 waveDescr.Hdr         $0FD4 speed
$0FB6 cmdDescr.Hdr          $0FD6 tracklo
$0FB8 (dummy)               $0FD8 voice
$0FBA (dummy)               $0FDA gate
$0FBC arp1  (wave col 1)    $0FDC chord          (chord table)
$0FBE arp2  (wave col 2)    $0FDE trans
                            $0FE0 chordindex     (chord index table)
                            $0FE2 shtrans
                            $0FEE newseq
version string "cc4.07"  (PETSCII) follows
```

`$0E00` feature block (editor metadata; tells the editor how many table columns each table has and which instrument bytes are table pointers):
```
requestedTables  !8 %00001111   ; bit1=wave tbl, bit2=cmd tbl(NI), bit3=pulse, bit4=filter
instrumentFlags  !8 0,0,0,0,4,3,0,1
                 ;   per instrument byte: 1=ptr→wave, 3=ptr→pulse, 4=ptr→filter
                 ;   => byte4(idx4)=filter ptr, byte5(idx5)=pulse ptr, byte7(idx7)=wave ptr
cmdFlags         !8 0,0,0,0,0,0,0,0  !8 0,0,0,0,0,0,0,0
```

`songsets` (the subtune table, pointed to by `$0FA6`): per subtune, three 16-bit order-list pointers (V0,V1,V2) followed by `!8 speed, 7`. CheeseCutter dump emits:
```
songsets: !word track<i>_0, track<i>_1, track<i>_2
          !byte <songspeed[i]>, 7
```
The trailing `7` = all three voices enabled bitmask (`%00000111`), read by `subinit` into `voicon`.

---

## 3. Instrument table

### 3a. NP 20.G4 — row-major, 8 bytes × 32 (codebase64-era understanding)

`research.md` records the NP20.G4 instrument as **8 consecutive bytes per instrument, 32 instruments** (256-byte table). Byte meanings (cross-checked against the player's instrument-byte semantics in §3c):

| Byte | Field | Meaning |
|------|-------|---------|
| 0 | AD | Attack/Decay (→ `$D405`) |
| 1 | SR | Sustain/Release (→ `$D406`) |
| 2 | HR type + arp delay | hi-nibble = hard-restart type (`$0x`/`$4x`/`$8x`/`$Ax`); lo-nibble = wave-table step delay (frames) |
| 3 | HR waveform | SID control-reg value used during hard restart |
| 4 | Filter ptr | index into filter table (`$00` = no filter) |
| 5 | Pulse ptr | index into pulse table (`$00` = none) |
| 6 | HR SR / (spare) | hard-restart SR envelope value (see §3c — `INS_7`) |
| 7 | Wave ptr | start row in wave table |

### 3b. NP 21.G4 / CheeseCutter — **column-major (transposed)**, 8 columns × INSNO rows

The CheeseCutter player and `dump.d` store the instrument table **transposed**: each of the 8 fields is its own contiguous column of `INSNO` bytes (INSNO = **48** in CC v4; was 32 in NP20.G4). The player addresses it as `inst + (field*INSNO) + instrument_number`:

```
INS_AD    = 0*INSNO    ; Attack/Decay
INS_SR    = 1*INSNO    ; Sustain/Release
INS_HR    = 2*INSNO    ; $x0 = HR type, $0x = arp/wave delay count
INS_4     = 3*INSNO    ; HR waveform
INS_FLTP  = 4*INSNO    ; Filter table pointer
INS_PULSP = 5*INSNO    ; Pulse table pointer
INS_7     = 6*INSNO    ; Hard-restart SR envelope value
INS_ARP   = 7*INSNO    ; Wave table pointer (start row)
```

`dump.d` emits 8 separate columns (`inst0..inst7`), each `maxInsno+1` bytes wide, sliced from a 48-stride buffer:
```d
for(int i = 0; i < 8; i++)
    hexdump(sng.instrumentTable[i*48 .. i*48 + (maxInsno+1)], 16);
```

> ⚠ **DECOMPILER DECISION POINT:** byte layout differs by version. NP20.G4 = row-major 8×32. NP21/CC = column-major 8×INSNO(48). Detect via player fingerprint / INSNO and read accordingly.

### 3c. Authoritative byte semantics (player_v4.acme editor `idescrN` strings)

These are the **canonical field descriptions shown in the editor**, lifted verbatim from the player source (`&` = newline in the editor help):

- **Byte 0 — Attack / Decay.** → `$D405`.
- **Byte 1 — Sustain / Release.** → `$D406`.
- **Byte 2 — "Restart type / arpeggio speed.** `$00` = 3 Frame Restart. `$40` = Soft restart. `$80` = Hard Restart. `$00-$0F` = Arpeggio delay value." (hi-nibble = HR type, lo-nibble = wave step delay.)
- **Byte 3 — Hard Restart waveform.**
- **Byte 4 — Filter Table pointer.**
- **Byte 5 — Pulse Table pointer `$00-$3f`.**
- **Byte 6 — Hard restart SR envelope value.**
- **Byte 7 — Wave Table pointer.**

### 3d. Hard-restart types (exact player behaviour — `dosync`/`updsound`)

The HR-type nibble (byte 2 hi-nibble) selects one of four pre-trigger behaviours. The player runs a 3-frame "sync" countdown (`tsync`) before a note. The decode in `updsound`:
- bit7 set (`$80`/`$A0`) → **hard restart**: during the pre-frame, set `ad = cmd2` (the row-0 command-table AD = HR ADSR, see §7) and `sr = inst[INS_7]` (the per-instrument HR SR byte 6).
- bit5 also set (`$A0`) → **"laxity" restart**: like `$80` but **AD is left untouched** (skips the `ad = cmd2` write — `laxhr` entry).
- bits `$40` → **soft restart**: gate off only; the waveform is NOT cleared (`wavenotoff` path skips `inc hardon`).
- `$00` → **3-frame restart**: standard gate-off + waveform-clear sequence.

Gate handling: `gatestat = $FE,$FF`. During sync the gate byte is forced `$FE` (gate bit cleared, holds waveform-off vs hard-off depending on path); at note-on `gate=$FF`. The waveform written to `$D404` is always `waveform AND gate` (so clearing gate masks bit0).

---

## 4. Order list ("tracks" / "Sequence List") — per voice

Per voice, a stream of entries selecting which sequence to play, with optional transpose and an end/jump marker. Each subtune's three voice lists are `$0400` bytes max. Default/empty list (CC) = `$A0,$00, $F0,$00` (play seq $00 at transpose 0, then jump to start). Decode (player `updtrack`/`trk0x`):

| Byte (1st of entry) | Meaning |
|---|---|
| `$00`–`$7F` | **(low range)** taken as a **sequence number directly** (`bpl trk02` → `curseq = byte`). No transpose change. |
| `$80` | **"no transpose" sentinel** — keep current transpose (`beq skiptrans`), next byte is the sequence number. |
| `$81`–`$EF` | **transpose value** then sequence number: player does `transpose = byte - $A0` (signed; `$A0`=0, `$A1`=+1, `$9F`=−1, …) and stores into `shtrans2`; the **following** byte is the sequence number. |
| `$F0`–`$F7` | **end-of-track JUMP marker.** The low 3 bits are the high part of a 11-bit jump offset; the **next byte** is the low byte. New track pointer = `twrap + ((byte&7)<<8 | nextbyte)` — i.e. jump to an absolute offset *within this voice's order list region* (relative to the subtune's order-list base `twrap`). This implements song loop / restart. |

So an order-list entry is **1 byte (low seq#)**, **2 bytes (transpose + seq#)**, or **2 bytes ($Fx + lo)** for a jump. `research.md`'s "transpose, seq#, $FF=end" summary is approximate: the **real end/loop marker is `$F0`–`$F7` + offset byte** (a jump, not a bare `$FF`), and bare low bytes are sequence numbers.

---

## 5. Sequence data format (codebase64, VERBATIM + player decode)

Each sequence is a stream of **byte pairs (AA, BB)** representing one editor row. AA = left column (instrument / command / tie), BB = note/gate column. From the codebase64 page verbatim:

**Byte AA:**
```
$7F     | End of Sequence (byte BB is not significant)
$90     | Tie Note (***)              [change pitch w/o retrigger]
$A0-$BF | Instrument $00-$1F          [select instrument, then note in BB]
$C0-$DF | Pointer to Super Table      [run command-table entry $00-$1F]
$80     | "Nothing" (no instr / no supertable ptr / no tie)
```
**Byte BB:**
```
$00     | No note (gate off)
$01-..  | Note value (triggers currently active instrument)
$7E     | Gate on hold (+++)
```
**Worked examples (verbatim from page):**
```
$A2 $24  → Instrument $02 and C-3
$80 $7E  → "Do nothing" in column 1, instrument held with gate on
$80 $00  → Empty row in the sequence
$90 $25  → Change note to C#4 without retriggering the instrument
```

> ⚠ **The CheeseCutter v4 player uses a DIFFERENT, more compact in-RAM sequence encoding** than the byte-pair editor image above. In the *packed* stream the player reads (one byte at a time, `seqnext`), the thresholds are:
> - `>= $C0` → **command byte** (`command` branch): `$F0-$FF` → set step **duration** = low nibble (`setdur`); `$C0-$EF` → **instrument select** = `byte - ($C0-1)` (`shinst`).
> - `$60-$BF` → it's a **note + optional cmd**: subtract `$60`; the result `$5F`(=`$BF-$60`) flags a **tie note** (`inc tienote`); otherwise it's a note value, and the **next byte** is a **command-table pointer** (`shsuper`, `$00` = none).
> - `< $60` → bare note/rest/gate (`shnote`); `< 3` (`$00`/`$01`/`$02`) are rest / gate-off / gate-on controls (`gatestat`); `>= 3` is a real note.
> - End-of-sequence in the packed stream = **`$BF`** (`SEQ_END_MARK`, checked at `cmp #$bf` → `newseq`).
>
> So there are **two encodings**: the *editor file image* (AA/BB pairs, $7F end, documented by codebase64) and the *runtime/packed* form (single-byte tokens, $BF end, what the player actually walks). The HVSC .sid binaries contain the **packed** form. A decompiler reading a real .sid must use the runtime decode above; the codebase64 AA/BB table is the editor's pre-pack representation. See `dump.d`'s `Sequence.compact()` and §5 markers.

---

## 6. Wave table (= "arpeggio" cols 1 & 2) — 2 × 256

Two parallel columns (`arp1` = byte A, `arp2` = byte B), indexed by `wavepos`. Authoritative field meanings (player `wdescr0/1` + `dowave`):

**Column A (`arp1`, byte 1) — Transpose / Loop:**
```
$00-$5F = Relative transpose up (added to the note's real pitch)
$80-$DF = Absolute tuning (pitch index used directly; ignores note + transpose)
$7E     = loop to previous row  (wavestore w/o advancing)
$7F     = loop to row given in column B (arp2[y] becomes new wavepos)
```
(Player: `wavetrans` bit7 set → absolute branch `waveabs` (`and #$7f` → freqtable index); else relative, add `notereal` (+ chord value) → freqtable + `shfreq` offset.)

**Column B (`arp2`, byte 2) — Waveform / Wave-delay / Loop pointer:**
```
$00      = Do nothing (keep current waveform)
$01-$0F  = Override this row's wave-delay (frames to hold this row)
$10-$DF  = Waveform: SID control-register value written to $D404 (combined with gate)
$E0-$EF  = SID control-register value $00-$0F  (i.e. low nibble; lets you write ctrl $00-$0F which the $10-$DF range can't reach)
$00-$FF  = Loop pointer (used as the target row when column A = $7F)
```
(Player `dowave`: `arp2[y]` `< $10` → skip waveform write; `>= $E0` → `and #$0f` then write; `$10-$DF` → write as-is to `waveform`. Step timing: per-row delay defaults to `wavetime` (= inst byte2 lo-nibble), overridable by a `$01-$0F` byte at the next column-A position via `wavenotend2`.)

---

## 7. Command / "Super" table

Indexed `$00-$1F` from a sequence `$C0-$DF` byte (editor image) or `shsuper` (runtime). **Row 0 is reserved for the hard-restart ADSR** (`cmd2` row 0 = HR AD value used by `$80` hard restart; see §3d).

### 7a. Width by version
- **NP 20.G4:** documented as **2 bytes/row** (`research.md`).
- **NP 21.G4 / CheeseCutter:** **3 columns** (`cmd1`,`cmd2`,`cmd3`), each 64 bytes (`dump.d` emits `cmd1`@0, `cmd2`@64, `cmd3`@128). **Byte 1 (`cmd1`) = command number; bytes 2-3 (`cmd2`,`cmd3`) = parameters.**

### 7b. Commands (player `mdescr0/1`, VERBATIM + behaviour)
```
$0 = Slide up         param = slide speed (signed 16-bit, cmd2=hi, cmd3=lo); effstate=1
$1 = Slide down       param = slide speed (signed 16-bit);                  effstate=2
$2 = Hi-fi Vibrato    cmd2 lo-nibble = vibrato "feel"; cmd3 hi-nibble = speed,
                          cmd3 lo-nibble = depth divider (bigger = narrower); effstate=3
$3 = Detune cur note  signed 16-bit added to shadow freq (cmd2=hi, cmd3=lo)  [CMD_SET_OFFSET]
$4 = Set ADSR         cmd2 → AD ($D405), cmd3 → SR ($D406)
$5 = Lo-fi vibrato    cmd2 = speed/freq, cmd3 = depth/amplitude;            effstate=4
$6 = Set wave         cmd3 → waveform ($D404)   [disabled by default: INCLUDE_CMD_SET_WAVE=FALSE]
$7 = Portamento (to a tie note)  cmd2 lo-nibble→portahi, cmd3→portalo;       effstate=$81
                          "Runs until a command 8-00 00 is given."
$8 = Stop portamento  effstate = 0
```

`effstate` codes (player comment): `0`=none, `1`=slide up, `2`=slide down, `3`=vibrato, `4`=lo-fi vibrato, `$81`/`$80`=portamento.

### 7c. Inline super-table tokens ≥ $40 (runtime `superparse`)
When `shsuper >= $40` the player treats it not as a command-table index but as an **inline one-shot effect** (no table row needed). Ranges (`superparse2`):
```
$40-$5F → set pulse program  (and #$1f, <<2 → pulsenxt)
$60-$7F → set filter program (and #$1f, <<2 → filtnxt)
$80-$9F → set chord          (and #$1f → chordindex[n] → chordtpos)
$A0-$AF → set Attack         (low nibble → AD hi-nibble)
$B0-$BF → set Decay          (low nibble → AD lo-nibble)
$C0-$CF → set Sustain        (low nibble → SR hi-nibble)
$D0-$DF → set Release        (low nibble → SR lo-nibble)
$E0-$EF → set Volume         (low nibble → $D418 volume)
$F0-$FF → set Speed          (low nibble → song speed; $F0/low-nibble 0 with INCLUDE_SYNC → inc sync flag)
```
(Note: these inline ranges only apply on the runtime/packed path. They overlap the editor's `$C0-$DF` "supertable pointer" range, hence the two encodings must not be conflated — see §5 caveat.)

---

## 8. Pulse table

Drives `$D402`/`$D403` (12-bit pulse width). Player processes rows of **4 bytes** (`pulstab+0..+3`) in CC v4; NP20.G4 used **2 bytes/row**.

### 8a. 4-byte row (NP21.G4 / CheeseCutter) — `pdescr0..3` VERBATIM
```
Byte 1 (pulstab+0): "Duration and direction. $00-$7F = Add n frames. $80-$FF = Subtract n frames."
                    (bit7 = direction; low 7 bits = frame count for this segment)
Byte 2 (pulstab+1): "Add value."  (per-frame delta added/subtracted from the 12-bit pulse)
Byte 3 (pulstab+2): "Initial pulse value. Note: Nibbles are reversed! $48 = $8400"
                    ($FF = retain current pulse, do not reload)
Byte 4 (pulstab+3): "Pointer to next set ($00-$3F) or $7F = stop pulse program."
                    ($00 = continue to next row sequentially: pulsenxt += 4)
```
Player decode (`updatepulse`): when the segment counter expires, reload from `pulsenxt`; if `pulstab+2 != $FF`, set pulse lo/hi from the *nibble-reversed* init byte (`and #$f0`→`pulselo`, `and #$0f`→`pulsehi`). `pulstab+0 & $7f` → new duration. `pulstab+3`: `$00`→advance +4; `$7f`→stop (next=0); else `<<2` → jump to row N. Per-frame: `pulstab+0` bit7 → add or subtract `pulstab+1` (with carry into pulsehi).

### 8b. NP20.G4 (2-byte) — `research.md`
`A = duration/direction, B = add value` (no per-row init / jump column; init & looping handled differently). ⚠ verify against an actual NP20.G4 binary.

### 8c. Direct pulse (instrument byte 5, `INS_PULSP`)
If the instrument's pulse-pointer byte is **negative (≥ $80)**, the player treats it as a **direct/initial pulse** rather than a table pointer (`INCLUDE_DIRECT_PULSE`): `and #$0f → pulsehi`, `pulselo = 0`. If `$01-$7F` it's a table-row pointer (`<<2 → pulsenxt`).

---

## 9. Filter table

Drives `$D415` (cutoff lo, 3 bits used), `$D416` (cutoff hi), `$D417` (res/routing), and bandpass/mode bits OR'd into `$D418`. Rows of **4 bytes** (CC v4); NP20.G4 = 2 bytes/row.

### 9a. 4-byte row (NP21.G4 / CheeseCutter) — `fdescr0..3` VERBATIM
```
Byte 1 (filttab+0): "Duration or filter type. $00-$7F = Duration, or $90-$F0 select filter type."
                    (bit7 set = an "init" row: $70 mask of it → bandpass/mode bits)
Byte 2 (filttab+1): "Add value or filter resonance and channel mask."
                    On an init row → written to $D417 (resonance + voice routing).
                    On a sweep row → low 2 bits scaled give the 10-bit cutoff add step.
Byte 3 (filttab+2): "Initial filter value or $FF = skip."  ($FF = keep current cutoff)
Byte 4 (filttab+3): "Pointer to next set ($00-$3F) or $7F = stop filter program."
                    ($00 = advance +4 sequentially)
```
Player (`filtstart`): if `filttab+0` bit7 set → init row: `bandpass = filttab+0 & $70`; `$D417 = filttab+1`; reset counter. Compute 10-bit add step from `filttab+1` (`&3 <<1` → `filtadd+1`; sign-extend via `cmp #$80 ror` → `filtadd`). `filttab+2 != $FF` → load `filter` (cutoff hi) and clear `filtlo`. Jump byte handling identical to pulse (`$00`→+4, `$7f`→stop, else `<<2`). Per-frame sweep: 10-bit accumulate (`filtlo` low 3 bits → `$D415`, `filter` → `$D416`). Sweeps are 10-bit resolution (Feb-2012 change: `$80` in 10 bits == `$20` in 8 bits).

### 9b. NP20.G4 (2-byte) — `research.md`
`A >= $80` = init row (filter type, resonance+routing, cutoff); `A < $80` = sweep row (duration, add, cutoff). ⚠ verify against actual binary.

---

## 10. Chord table (NP21.G4 / CC; absent in oldest NP20.G4)

Two structures emitted by `dump.d`: `chord` (the chord step table, 128 bytes) and `chordindex` (32 bytes, maps a chord id → start row in `chord`). Selected by sequence inline token `$80-$9F` (chord id = low nibble) or by instrument default. Player `chordinit`: read `chord[y]`; values `>= $40` get `ora #$80` (negative = transpose down); `chord[y+1]` bit7 set → loop (`and #$7f` → new chordtpos). The chord value is **added to the wave-table relative transpose** each frame (`adc chordvalue` in `wavenotabs`). The `chord` table region is also reused by the **break-speed / per-step-speed** mechanism (`speedalt`/`speedsub` index `chord`).

---

## 11. Per-frame SID write model — `setsid` (CANONICAL, from player_v4.acme)

This is the **exact per-voice $D400-$D418 write sequence** the play() routine emits. **Verification target.** For each voice (X = 2,1,0; `voice = 0,7,14` is the per-voice register base offset Y):

```
$D400+Y  <- freqlo[x]                ; frequency lo
$D401+Y  <- freqhi[x]                ; frequency hi
$D406+Y  <- sr[x]                    ; sustain/release   (NOTE: SR written BEFORE AD)
$D405+Y  <- ad[x]                    ; attack/decay
$D402+Y  <- pulselo[x]               ; pulse width lo
$D403+Y  <- pulsehi[x]               ; pulse width hi
$D404+Y  <- waveform[x] AND gate[x]  ; control register (waveform gated)
```
Voice order is **V2 → V1 → V0** (the `main0` loop runs `ldx #2 … dex … bpl`). After all three voices, **once per frame** (filter routine + master):
```
$D415 <- filtlo                      ; filter cutoff lo (3 bits)   [if INCLUDE_FILTER]
$D416 <- filter                      ; filter cutoff hi            [if INCLUDE_FILTER]
$D417 <- (filttab+1 on filter init rows only; also $F0 at subplay reset)
$D418 <- volume OR bandpass          ; master volume + filter mode bits
```
Notes for matching:
- **Write order within a voice is fixed: freq lo, freq hi, SR, AD, PW lo, PW hi, ctrl.** The SR-before-AD order is a JCH signature (relevant to fingerprinting / distinguishing from GoatTracker, which differs — cf. GTUltra note "tweaked to resemble JCH NewPlayer 21").
- `$D417` is written `$F0` once on the stop/reset path (`subplay` reset) and is otherwise written only on filter-table **init rows** (`filtstart`), not every frame.
- `$D418` is written every frame (`volume OR bandpass`), even with no filter.
- Hard-restart frames: gate is forced off and HR ADSR loaded the frame(s) before a note (so you see `$D405/$D406` change and `$D404` lose its gate bit ahead of the retrigger) — see §3d.
- **Multispeed (NP*.Q* and 21+ with MULTISPEED):** extra "sound-only" frames are driven by a CIA timer calling `mplay`/`submplay` (`state=$40`, jumps straight to `syncskip`/`updsound` skipping sequence advance). These emit the **same `setsid` block** but do NOT advance the sequence/track. For verification this means the per-`play()` write capture must bucket per IRQ (cf. CLAUDE.md Trap C / `--writelog-per-irq`).

---

## 12. Frequency table (from player_v4.acme — VERBATIM, 96 entries)

8-octave equal-tempered table (low byte / high byte), index = note value. PAL. (This is the CC v4 table; older NP versions may use a slightly different table — verify per fingerprint.)

`freqtable_lo` (96 bytes):
```
16 27 38 4b 5f 73  8a a1 ba d4 f0 0e
2d 4e 71 96 bd e7  13 42 74 a9 e0 1b
5a 9b e2 2c 7b ce  27 85 e8 51 c1 37
b4 37 c4 57 f5 9c  4e 09 d0 a3 82 6e
68 6e 88 af eb 39  9c 13 a1 46 04 dc
d0 dc 10 5e d6 72  38 26 42 8c 08 b8
a0 b8 20 bc ac e4  70 4c 84 18 10 70
40 70 40 78 58 c8  e0 98 08 30 20 2e
```
`freqtable_hi` (96 bytes):
```
01 01 01 01 01 01  01 01 01 01 01 02
02 02 02 02 02 02  03 03 03 03 03 04
04 04 04 05 05 05  06 06 06 07 07 08
08 09 09 0a 0a 0b  0c 0d 0d 0e 0f 10
11 12 13 14 15 17  18 1a 1b 1d 1f 20
22 24 27 29 2b 2e  31 34 37 3a 3e 41
45 49 4e 52 57 5c  62 68 6e 75 7c 83
8b 93 9c a5 af b9  c4 d0 dd ea f8 fd
```
Note index → pitch: index 0 = C-0; the editor `NOTES` array (base.d) runs C-0..B-7 (96 notes). A `FINETUNE` table is present in the file header layout (Offsets enum) but not in this exported player (likely a per-version global tuning offset).

---

## 12a. Internal player-version numbers vs marketing names (version fingerprinting)

There are **two numbering schemes** and they must not be confused:
- **Internal player version** `Vnn` — what SIDId fingerprints and what tools like *JCH Music Search Pro* report. Known set (from Demozoo / JCH Music Search Pro): **V06, V08, V11, V12, V13, V14, V15, V17, V18, V19, V20** (+ the SIDId set V1-V20, V0x, and `Dane_NewPlayer`). E.g. DRAX/Vibrants music from Nov 1989 used **"Newplayer V14."**
- **Marketing/editor name** `NPxx.Gn`/`NPxx.Qn` — NP17.G0, NP20.G4 (standard), NP20.Q0 (multispeed), NP21.G4-G6, NP22-25.

These do **not** line up 1:1 (the internal `V` counter predates and runs alongside the `NP##` naming). **For the decompiler, the internal `Vnn` (SIDId signature) is the reliable discriminator** — derive the table-layout + write-model branch from the SIDId fingerprint, then confirm against the §13 deltas. SIDId reports **21 distinct NP signatures** total. (Separately: **EdLib** is a *different* JCH/Vibrants music tool — NOT NewPlayer; don't conflate when classifying HVSC.)

---

## 13. Version deltas (the part the decompiler must branch on)

| Feature | NP17.G0 | **NP20.G4 (standard)** | NP20.Q0 | **NP21.G4-G6 / CheeseCutter v4** | NP22-25 (Dane) |
|---|---|---|---|---|---|
| Pulse table row | — | **2 bytes** | 2 bytes | **4 bytes** (dur+dir / add / init(nibble-rev) / next) | varies per bundled player |
| Filter table row | — | **2 bytes** | 2 bytes | **4 bytes** (dur/type / add or res+mask / init / next) | varies |
| Command table width | — | **2 bytes** | 2 bytes | **3 bytes** (cmd# + 2 params), 3×64 | varies |
| Instrument layout | row-major 8×n | **row-major 8×32** | 8×32 | **column-major 8×INSNO(48)** | varies |
| Max instruments | — | **32** | 32 | **48** | — |
| Multispeed | no | **no (1×)** | **yes (Q-series)** | **optional (MULTISPEED build flag, CIA)** | yes (some players) |
| Chord table | — | (likely absent) | — | **present** (chord + chordindex) | present |
| Wave-ptr settable from seq/cmd | — | (yes via editor) | — | **NO** (CC removed it; INCLUDE_CMD_SET_WAVE=FALSE) | — |
| Filter control | mixed | partly from instrument | — | **only from filter table** (more flexible) | — |
| Player size / raster | ~1 KB / 12-13 rl | ~1 KB / 12-13 rl | larger | ~1.9 KB | "several players, raster-vs-flexibility tradeoff" |

The "G" series = standard/game players; "Q" series = multispeed (e.g. NP20.Q0). Suffix letters (G4, G5, G6, b4) = minor revisions. Dane's NP22-25 (Booze Design, JCH-editor 3.1) is a **bundle of several players** with a documented "little-raster-but-less-flexible … vs … more-options-but-more-time" spectrum; full English manual exists (CSDb id=100406; CSDb was 503 at fetch time — follow up).

> **CheeseCutter is a port of the NP21.G4 lineage, not byte-identical to JCH's own NP21**: its in-RAM packing (single-byte tokens, `$BF` end-mark, 48 insts, column-major) is CC's own. The HVSC .sid binaries authored in JCH's editor will match JCH's NP20/21 packing; treat CC's `dump.d` layout as a *very close reference*, then confirm against a real HVSC binary per version. SIDId reports **21 distinct signature variants** (V1-V20, V0x, Dane_NewPlayer) — fingerprint first, then pick the layout.

---

## 14. Codebase64 page — full prose (VERBATIM)

> **JCH 20.G4 Player File Format** — By FTC/HT.
>
> "I wanted to code a converter from the JCH editor file format into the format I use in my own editor, and I thought I could just as well share the structure of the JCH file format with you. The description is not 100% complete, but maybe someone will find it useful anyway. Enjoy!"
>
> "I might add some more info here some other day, but don't hesitate to improve on this info yourself!"
>
> (Memory-locations table, sequence-data AA/BB table, and the four worked examples — all reproduced verbatim in §1 and §5 above. The page contains **no** instrument-format table, no wave/pulse/filter internals, and no command-table detail — those gaps are filled here from the player source.)

---

## Leads to follow

- **CSDb was hard-blocked (HTTP 503, Retry-After: 3600) for the entire session** from both egress paths (curl + WebFetch) and the `noname.c64.org` mirror (301→csdb.dk). Re-fetch when unblocked:
  - `csdb.dk/release/?id=165426` — **"JCH NP20.g2 Docs by Deek"** (a dedicated NP20 docs release — likely the cleanest NP20-era format doc; HIGH priority).
  - `csdb.dk/release/?id=100406` — **JCH-editor 3.1 + NP22-25** (Dane/Booze Design); the bundled **English manual** is the authoritative source for NP22-25 player differences + multispeed.
  - `csdb.dk/release/?id=26563` (NP21.G4 Final) and `id=20112` (21.b4 beta) release notes.
- **JCH's OWN released player/editor source** (Task 2) — find the JCH-editor source on CSDb (Vibrants releases) to get JCH's *native* NP20/NP21 binary packing (vs CheeseCutter's reimplementation). The CC asm header credits "JCH NP 21.G4 by Laxity/VIB" — the original Laxity/Vibrants source is the ground truth for the HVSC binaries.
- **Internet Archive `d64_JCH_Editor_v3.04_19xx_Onslaught`** — D64 disk image (910 KB) of JCH Editor v3.04; contains the actual player binaries + possibly docs. Mount/extract to read the embedded players and confirm NP20/21 layouts against this spec.
- **SID Factory II** (github.com/Chordian/sidfactory2; manual at files.chordian.net/sf2/) — JCH's modern successor. Its "driver 11" (NewPlayer-style) uses instrument **flag bytes + bit-selectors** and index pointers for pulse/filter/wave — a *divergent re-encoding*, useful for lineage/semantics but NOT the HVSC binary format. Read its driver source/manual for confirmation of effect semantics only.
- **Pull a representative HVSC NP20.G4 and NP21.G4 .sid** and validate §3/§5/§8/§9 byte-for-byte; specifically confirm: (a) instrument row-major(32) vs column-major(48) per version; (b) the runtime/packed sequence token scheme (§5 caveat) vs the editor AA/BB image; (c) the 2-byte vs 4-byte pulse/filter row split; (d) the `$0FA0` pointer block presence in *packed* (editor-stripped) tunes.
