# Hawkeye RE notes

Companion to `disassembly.s` (the seed disassembly, regenerable). This
file maps Hawkeye's auto-traced labels to the canonical labels from
Cybernoid II's ACME source (same author, same year, same driver) and
records what each routine does.

**Source files:**
- `disassembly.s` — auto-traced seed of Hawkeye (Tel 1988, Thalamus)
- `/tmp/fc_research/c64_6581_sid_players/Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm`
  — Cybernoid II ACME (Tel 1988), the canonical reference
- `pipelines/future_composer/docs/README.md` — research bundle index

## Routine map: Hawkeye → Cybernoid II

The two SIDs share the driver byte-for-byte; addresses differ because
the binaries load at different places. The routine SHAPES match
exactly — same control flow, same comparisons, same per-voice
indexing.

| Hawkeye | Cybernoid II label | Purpose |
|---|---|---|
| `$7AE0` (init) | `init` (jmp song) | Entry: JMP to subtune-init at $918F |
| `$7AE3` (play) | `play` (jmp playirq) | Entry: JMP to per-frame play at $7B98 |
| `sub_7B32` | `ok2` | Zero per-voice state ($90C5..$913B, 119 bytes); used by both init and section-end |
| `L_7B3C` | `ok2` (second half) | Zero 3-byte per-voice slots for the four "core" arrays (tabcount/begcount/nootcount/noho) |
| `sub_7B5A` | `song` | Per-subtune init — called from $918F with X=subtune. Stores speedbyte from `$83FC,X` (per-subtune table), copies 6 bytes from `$7B2C` to `$8403`, sets up seqloclo/hi from `$83F5,X` and `$7AFF,X`, calls ok2, clears all 24 SID registers, writes $00 to $D418/$D417 |
| `L_7B98` | `playirq` | Play dispatcher — SMC byte at $7B99 (= Cybernoid's `testbyte`) controls behavior |
| `L_7BA4` | `+` (after `bpl startplayer`) | Main frame entry: inc counter2[0..2], dec global speedsto ($9116), reload from speedbyte ($7AFE) on rollover |
| `L_7BBA` | `startplayer` / `hy` | Per-voice loop body (X = voice index 0/1/2; sidoff = `d4point,x` = {$00, $07, $0E}) |
| `L_7BE0` | `h2` | Read next sequence byte: `LDY tabcount,x; LDA seqloc[x],y` |
| `L_7BFC` | `songout` | Section end ($FE marker): set testbyte=2, gate V1/V2/V3 ctrl off, RTS |
| `L_7C0D` | `h3` (cmp #$80 branch) | Transpose command ($80-$BF): `AND #$1F; STA toneadd,x; INC tabcount,x` |
| `L_7C1F` | `h3a` (cmp #$60 branch) | Voiceinc command ($60-$7F): `AND #$0F; STA voiceinc,x; INC tabcount,x` |
| `L_7C31` | `h3c` (cmp #$40 branch) | Repeats command ($40-$5F): `AND #$3F; STA repeatsto,x; INC tabcount,x` |
| `L_7C43` | `h3f` | Pattern jump ($00-$3F): ASL+TAY, load pattern addr from `sequence,y` / `sequence+1,y` into zp ($FD/$FE), read first pattern byte via `(zp),y` |
| `L_7C64` | `startnote` (post-skip) | Pattern-byte dispatcher (with $FA = `tabbytsto`) |
| `L_7C80` | `dofilset` | $F1 command: write next byte directly to $D417 (filter-set) |
| `L_7CBA` | `noglideset` | Check for $E0+ glide command (3-byte sequence) |
| `L_7CD0` | (instrument change) | $70+ command: read instrument number (low nibble), copy instrument data from `$8580,X` (low byte of …) and `$8589,X` (high byte) into runtime |
| `L_7CF4` | `noinstset` / arp section | $80+ note-length: `AND #$3F; SBC #1; STA nootleng,x`, then read another byte |
| `L_7D22` | (note-play) | Compute frequency: `LDA nootleng,X+vibcounter,X...` (actually uses voiceinc and table lookup at `$8337/$8396` — freq lo/hi tables); write V_FREQ_LO/HI to SID, set up wavesto/ADSR/PW |
| `L_7DA8` | (pattern-end) | Pattern $FF: reset begcount, decrement repeatsto, if exhausted then INC tabcount (advance sequence) |
| `sub_7DBD` | `verhoogtest` | Helper: INC begcount, INY, read next pattern byte via `(zp),y`, check for $FF |
| `L_7DCA` | (sustain) | Sustain-frame freq update (long notes; uses noothoogt + d401 high-byte from instrument) |
| `L_7DF9` | (per-frame instr) | Per-frame instrument table walking — wave/pulse/filter table fetch + apply to SID. **Big section, see disassembly.** |
| `L_918F` | (entered from JMP init) | Subtune dispatch: takes A=subtune, calls song subroutine ($7B5A) |

## Per-voice variable layout

Hawkeye's per-voice arrays start at **`$90C5`** and are contiguous 3-byte
arrays (one byte per voice 0/1/2) following Cybernoid II's `tabcount` /
`begcount` / … sequence. The 119-byte zero-fill at `sub_7B32` covers
the full block.

**Inferred layout** (anchored at $90C5; **EXACT byte-for-byte match
with Cybernoid II is TODO — verify via py65 trace before extract**):

| Hawkeye offset | Cybernoid II label | Size | Meaning |
|---|---|---|---|
| `$90C5..$90C7` | `tabcount` | 3 | sequence-read position (per voice) |
| `$90C8..$90CA` | `begcount` | 3 | pattern-read position (per voice) |
| `$90CB..$90CD` | `nootcount` | 3 | frames-remaining on current note |
| `$90CE..$90D0` | `nootleng` | 3 | total length of current note |
| `$90D1..$90D3` | `wavesto` | 3 | current waveform ctrl byte |
| `$90D4..$90D6` | `noothoogt` | 3 | note pitch (high?) |
| `$90D7..$90D9` | `noho` | 3 | (TBD) |
| `$90DA..$90DC` | `wavecount` | 3 | wave-table cursor |
| `$90DD..$90DF` | `hinotesto` | 3 | freq_hi store |
| `$90E0..$90E2` | `hinotesto2` | 3 | freq_hi store 2 (vibrato?) |
| `$90E3..$90E5` | `lonotesto` | 3 | freq_lo store |
| `$90E6..$90E8` | `glidetest` | 3 | glide-active flag |
| `$90E9..$90EB` | `glidetest2` | 3 | glide-active flag 2 |
| `$90EC..$90EE` | `pulsestolo` | 3 | pulsewidth_lo |
| `$90EF..$90F1` | `pulsehisto` | 3 | pulsewidth_hi |
| `$90F2..$90F4` | `pulsehitemp` | 3 | pulsewidth temp |
| `$90F5` | `pulsecountup` | 1 | global PW counter |
| `$90F6..$90F8` | `counter2` | 3 | per-voice frame counter (incremented at top of play) |
| `$90F9..$90FB` | `toneadd` | 3 | transpose offset |
| `$90FC..$90FE` | `vibstore1` | 3 | vibrato state 1 |
| `$90FF..$9101` | `vibstore2` | 3 | vibrato state 2 |
| `$9102..$9104` | `vibstore3` | 3 | vibrato state 3 |
| `$9105..$9107` | `tonearpcounter` | 3 | arpeggio counter |
| `$9108..$910A` | `arpieoklo` | 3 | arpeggio low byte (or `$910A` is per-tune scratch — Hawkeye's $910A is used as st2 in some routines) |
| `$910B..$910D` | `arpieokhi` | 3 | arpeggio high byte |
| `$910E` | `st2` | 1 | scratch (sequence byte) |
| `$910F..$9117` | (continuing per Cybernoid II) | various | filter, filtercount, pulsetest |
| `$9116` | `speedsto` | 1 | global speed counter (decremented per frame) — matches Hawkeye usage |
| `$9118..$911A` | `repeatsto` | 3 | pattern-repeat counter |
| `$911B..$911D` | `stod404` | 3 | next V_CTRL byte to write |
| `$911E..$9120` | `newnote` | 3 | new-note flag |
| `$9121` | `strfiltest` | 1 | (TBD) |
| `$9122..$9124` | `tempglide` | 3 | glide target |
| `$9125..$9127` | `glidedelay` | 3 | glide delay |
| `$9128` | `strafil` | 1 | (TBD) |
| `$9129..$912B` | `d400` | 3 | V_FREQ_LO mirror |
| `$912C..$912E` | `d401` | 3 | V_FREQ_HI mirror |
| `$912F..$9131` | (post-Cybernoid layout) | | |
| `$9132..$9134` | `byteand` | 3 | (TBD) |
| `$9135..$9137` | `pulseruntest` | 3 | PW direction/active flag |
| `$9138` | (unused / boundary) | 1 | |
| `$9139..$913B` | `voiceinc` | 3 | wave-table advance step |

### Status after py65 trace + disassembly grep

10-frame trace of subtune 0 saved in `trace_subtune0.txt` (script:
`trace.py`).

**Verified per-voice array bases** (from `STA $9XXX,x` writes in the
disassembly — 32 distinct arrays):
```
$90C5, $90C8, $90CB, $90CE, $90D1, $90D4, $90D7, $90DA,
$90DD, $90E0, $90E3, $90E6, $90E9, $90EC, $90EF, $90F2,   ← 16 contiguous, 0x30 bytes
$90F6, $90F9,                                              ← 2 more
$90FE, $9104, $9107, $910C,                                ← gap-separated
$910F, $9112,
$9118, $911B,                                              ← repeatsto, stod404
$9127,
$912B, $912E, $9133, $9136, $9139                          ← d400, d401, …, voiceinc
```

**Verified globals** (1-byte writes without ,X) at `$90F5`, `$90FD`,
`$910A`, `$9116`, plus the SMC operand bytes at `$7B99` / `$7AFE` /
`$7BAE`.

**Role confirmations** (observed update pattern matches Cybernoid II
semantics):
- `counter2` at `$90F6` (offset 0x31) — incremented every frame for
  all 3 voices. Init from $FF.
- `speedsto` at `$9116` (global, 1 byte) — decremented per frame,
  reloads to `speedbyte=$03` at rollover (= 4 frames per step).
- `toneadd` at `$90F9` (offset 0x34) — set to $10 for all voices on
  frame 0 (= transpose $10 from a $80+ sequence command).
- `tabcount` at `$90C5` — advanced in frame 0 (V0=2, V1=1, V2=3 after
  processing the leading sequence commands).
- `begcount` at `$90C8` — pattern-read pos (V1 advanced 0→3→5 across
  frames 0, 4).
- `nootcount` at `$90CB` — note frames remaining ($3F = 63 → decrements).
- `nootleng` at `$90CE` — total note length ($3F = 63 frames).
- `wavesto` at `$90D1` — wave ctrl byte ($41 = pulse + gate for V1).
- `hinotesto`/`hinotesto2`/`lonotesto` at `$90DD`/`$90E0`/`$90E3` —
  pitch values written to SID FREQ regs.
- `stod404` at `$911B` — V_CTRL mirror ($41 for V1's first note).

**Role correction:** the offset-0x46 array (`$910B..$910D`) is actually
**filter state**, not `arpieokhi`. The trace shows it set to $E0 in
frame 1 simultaneously with `$D416 ← $E0` (filter cutoff hi). The
"arpieok" label from Cybernoid II's per-voice region maps elsewhere
in Hawkeye, or is unused.

**Hawkeye vs Cybernoid II layout difference:** Hawkeye has `voiceinc`
at $9139 (offset 0x74). Projecting Cybernoid II's sequence forward
from `tabcount` would land `voiceinc` at offset 0x6A. So Hawkeye has
~10 extra bytes inserted between `speedsto` ($9116) and `voiceinc`
($9139). Those 10 bytes are Hawkeye-specific additions (filter
state? extra vibrato?). The gap arrays at $9118/$911B/$9127 + the
singleton $910A occupy that span.

## Sequence / pattern byte formats

### Sequence stream (per voice)

Read from `seqloclo,X / seqlochi,X` (set in init from `$83F5,X` and
`$7AFF,X`). Bytes:

| Byte range | Command | Effect |
|---|---|---|
| `$00..$3F` | pattern N | jump to pattern-N data via `sequence[N*2]` table at `$8409` |
| `$40..$5F` | repeats | `AND #$3F; STA repeatsto,x` (set pattern-repeat counter) |
| `$60..$7F` | voiceinc | `AND #$0F; STA voiceinc,x` (set wave-table step) |
| `$80..$BF` | transpose | `AND #$1F; STA toneadd,x` (transpose by 0..31 semitones) |
| `$FE` | section end | trigger songout (gate all voices off, set state=2) |
| `$FF` | section wrap | reset tabcount/begcount/nootcount and re-read |

Note: Hawkeye's V3.x ranges differ from FC V4.1's published spec
(the V4.1 manual has $40-$5F = transpose, $80-$BF = repeat — opposite
of what V3.x does). The two versions reordered their command space.

### Pattern stream (per pattern)

Read from `sequence[pat*2]` table (stored at `$8409..$840A` for pat 0,
etc.). Pattern body is bytes read via `(zp_FD),Y` with `Y = begcount,X`.

Pattern byte dispatch (after first read into `$FA = tabbytsto`):

| Byte high nibble | Command | Action |
|---|---|---|
| `$F0` (`$F0`/`$F1`) | filter / set | $F0: end-of-pattern (jump to $FF handler). $F1: read next byte as $D417 value (resfilt) |
| `$E0..$EF` | glide | 3-byte sequence: byte 0 = E0+, byte 1 = glidedelay, byte 2 = target freq (+toneadd → tempglide) |
| `$C0..$DF` | freq adjust | `AND #$1F`; `+voiceinc → wavesto` (wave-table position adjust) |
| `$70..$7F` | instrument change | low nibble = instr id; copy 2 bytes from `$8580,n` and `$8589,n` |
| `$80..$BF` | note-length | `AND #$3F; SBC #1; STA nootleng,x`; loops back to read next byte |
| else (`$00..$5F`) | play note | pitch = byte; lookup freq via `$8337/$8396` (lo/hi PAL freq tables); write to SID; trigger gate |

### Instrument format (8 bytes per inst)

Per `wiki_fc_v41_manual.md` and `csdb_format_inferences.md`:

| Offset | Field |
|---|---|
| +0 | pulse_hi |
| +1 | waveform / ctrl |
| +2 | attack / decay |
| +3 | sustain / release |
| +4 | filcount (filter table pointer) |
| +5 | fx1 (vibrato related) |
| +6 | fx2 (arpeggio related) |
| +7 | fx3 (drum / skydive flags) |

Hawkeye's instrument table base — TBD, but the instrument-change
handler at `L_7CD0` reads from `$8580,x` and `$8589,x`, suggesting
two parallel tables (one byte each per instrument, 16 instruments
total at $8580/$8589). The 8-byte per-instrument structure must live
elsewhere — possibly at `$860C..$8627` based on `L_7D60..L_7D77`
(`LDA $860E,x` for AD, `LDA $860F,x` for SR, `LDA $860C,x`/`$860D,x`
for PW, `LDA $8610,x` for further data).

## Per-subtune setup (verified by trace)

`subtune_init_dump.txt` shows post-init state for all 12 subtunes.
Key findings:

| Subtune | speedbyte | $7BAE | V0 seq | V1 seq | V2 seq | SMC offset |
|---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | $03 | $02 | $8724 | $8792 | $882E | $08 |
| 1 | $02 | $02 | $8C29 | $8C3D | $8C43 | $0E |
| 2 | $02 | $02 | $8CD0 | $8CED | $8CF0 | $14 |
| 3 | $03 | $02 | $8E2D | $8E30 | $8E33 | $1A |
| 4 | $02 | $02 | $8E64 | $8E67 | $8E6A | $20 |
| 5 | $02 | $02 | $8EA0 | $8EDB | $8EE0 | $26 |
| 6 | $02 | $00 | $8FC5 | $9015 | $9015 | $2C |
| 7 | $02 | $00 | $8FC5 | $9056 | $9056 | $2C |
| 8 | $02 | $00 | $8FC5 | $9008 | $9008 | $2C |
| 9 | $02 | $00 | $8FC5 | $9054 | $9054 | $2C |
| 10 | $02 | $00 | $8FC5 | $9014 | $9014 | $2C |
| 11 | $02 | $00 | $8FC5 | $9021 | $9021 | $2C |

**Structure**: 6 music subtunes (0-5) + 6 SFX (6-11). Distinguished
by `$7BAE` value: $02 for music, $00 for SFX. SFX subtunes share V1=V2
seq (sound effect on one voice, mirrored).

**SMC site at $7B6B** is the LDA low-byte that gets patched per
subtune. Subtunes 0-5 each have their own 6-byte seq-pointer template
at $7B08, $7B0E, $7B14, $7B1A, $7B20, $7B26. Subtunes 6-11 all share
the template at $7B2C (their V0 seq is identical = $8FC5).

**Per-subtune tables in the binary** (verified at data dump):
- `$83F5+X` (1 byte): speedbyte for subtune X — though the trace shows
  raw `LDA $83F5,X` doesn't quite match for X≥7 (subtunes 7-11 all get
  speedbyte=$02 while the table contains $08+ at those offsets). The
  `JMP $918F` from PSID init likely does some subtune translation
  before calling `sub_7B5A`. **TODO: disassemble $918F to confirm.**
- `$83FC+X` (1 byte): low byte of the per-subtune SMC template
  (high byte is $7B for all)
- `$7AFF+X` (1 byte): the per-subtune value stored to $7BAE
  (music=$02, sfx=$00)

## Data section addresses (Hawkeye)

| Address | Purpose | Notes |
|---|---|---|
| `$7AE0` | PSID entry: JMP init ($918F) | |
| `$7AE3` | PSID entry: JMP play ($7B98) | |
| `$7AE6..$7B07` | data gap (~34 bytes) | scratch / unused / part of $7AFF,X table |
| `$7AFF..$7B0A` | per-subtune $7BAE values (12 bytes) | music=$02, sfx=$00 |
| `$7B08..$7B31` | per-subtune seq-pointer templates (7 × 6 bytes) | indexed via SMC at $7B6B; subtunes 6-11 share template at $7B2C |
| `$7B32..$7B97` | init / reset code | sub_7B32, L_7B3C, sub_7B5A |
| `$7B98..$7DC9` | play loop | dispatcher, sequence read, command dispatch, pattern read |
| `$7DCA..$7DF8` | sustain freq update | |
| `$7DF9..$830C?` | per-frame instrument processing (wave/pulse/filter walking) | |
| `$830C..$8336?` | continue play loop tail | |
| `$8337..$8395` | freq table lo (96 entries) | **verified** by binary inspection |
| `$8396..$83F4` | freq table hi (96 entries) | **verified** |
| `$83F5..$8400` | per-subtune speedbyte table (12 bytes) | overlapping high-7-byte region also used by SMC offset table — see TODO above |
| `$83FC..$8407` | per-subtune SMC template-lo-byte table (12 bytes) | |
| `$8403..$8408` | RUNTIME per-voice seq pointers (3 lo + 3 hi) | overwritten by sub_7B5A's template copy at each init |
| `$8409..$8488?` | pattern-pointer table (lo,hi pairs) | **40+ patterns confirmed** at $8FC0, $8944, $895C, $8970, $8992, $89B4, $89CD, $89E5, $89FF, $8A13, $8A30, $8A4D, $8A8B, $8AAD, $8AC9, $8ACE, $8AD3, $8AE4, $8B05, $8B10, $8B34, $8B4E, $8B72, $8C01, $8C4B, $8C55, $8C59, $8C5F, $8C91, $8CA9, $8CBD, $8CCA, $8CF8, $8D4B, $8D98, $8DA3, $8DBF, $8DD0, $8DEF, $8E0F, ... |
| `$8580..$858F` | instrument table column 1 (16 entries) | values: $92 $96 $9A $9E $A2 $A6 $AA $AE $B2 $85×7 |
| `$8589..$8598` | instrument table column 2 (16 entries) | values: $85×9 then $02 $00 $03 $07 $02 $00 $04 |
| `$860C..$865B?` | per-instrument 8-byte records | **verified** — at least 8 instruments visible. Record 0 all zero; record 1 = `14 41 08 DD F0 40 61 00` (pulse=14, ctrl=41, AD=08, SR=DD, fil=F0, fx1=40, fx2=61, fx3=00) |
| `$8724..$8FBF?` | per-subtune sequence streams | each subtune's V0/V1/V2 starts (table above) — interleaved or sectioned |
| `$8FC5..$??` | shared SFX V0 sequence (subtunes 6-11) | |
| `$9008..$905F?` | shared SFX V1/V2 sequences | per the subtune init dump |
| `$90C5..$913B` | per-voice runtime variables | 119 bytes — see layout table above |
| `$918F..$91D5` | subtune dispatch (entered from JMP init) | see decoded logic below |
| `$9200..$9CFF` | per-SFX records (6 × 0x200 bytes) | one record per SFX subtune (6-11) |

⚠️ Many of these are EDUCATED GUESSES from a single-pass disassembly read.
They need verification — see "Open questions" below.

## $918F subtune dispatcher (decoded)

```
$918F: CMP #$06         ; A = raw subtune number
       BCS $919A        ;   ≥6 → SFX path
       TAX              ; A < 6: X = A (music subtune 0-5)
       JSR $7B5A        ;        call music init with X = subtune
       RTS

$919A: CMP #$0C         ; SFX path (A ≥ 6)
       BCS $9197        ;   ≥12 → invalid, RTS
       SBC #$06         ; A = SFX index (0-5)
       ASL              ; A = SFX_index * 2
       CLC; ADC #$92    ; A = $92 + SFX_index*2 (record page number)
       STA $03          ; (zp_02:zp_03) = pointer to SFX record
       LDA #$00; STA $02
       ; copy 6 bytes from record+$00 to $7B2C..$7B31 (overwrites
       ; template 6 with this SFX's V0/V1/V2 seq pointers)
       LDY #$05
       LDA ($02),y / STA $7B2C,y / DEY / BPL  ; 6 bytes
       LDA #$06; STA $02   ; ptr += 6
       ; copy 20 bytes from record+$06 to $8475..$8488 (overwrites
       ; pattern-pointer table entries 26..35 with SFX-specific
       ; pattern addresses — 10 new patterns)
       LDY #$13
       LDA ($02),y / STA $8475,y / DEY / BPL  ; 20 bytes
       LDA #$1A; STA $02   ; ptr += $1A (now $1A from page base)
       ; copy 255 bytes from record+$1A to $8FC5..$90C4 (the
       ; sequence/pattern data area; SFX gets fresh content)
       LDY #$00
       LDA ($02),y / STA $8FC5,y / DEY / BNE  ; 255 bytes (wraps)
       LDX #$06         ; force X = template index 6
       JMP $9194        ; tail-call music init with X = 6
```

Per-SFX record layout (each is at page `$92 + 2*SFX_index`, total ~256 bytes):
- bytes `+$00..$05`: 6-byte seq-pointer template (3 lo + 3 hi for V0/V1/V2)
- bytes `+$06..$19`: 20 bytes = 10 pattern pointers (lo,hi) — get written to pattern-pointer table at $8475
- bytes `+$1A..$118`: 255 bytes of sequence + pattern data — gets written to runtime $8FC5+

So SFX subtunes are SELF-CONTAINED RECORDS, not just template aliases. Each SFX record carries its own sequences + patterns. They use shared instruments + freq table from the music side, but everything else is SFX-specific.

SFX record locations: $9200, $9400, $9600, $9800, $9A00, $9C00.

Decoded SFX V0/V1/V2 seq pointers (matches post-init trace):

| Sub | Page | V0 | V1 | V2 |
|---|---|---|---|---|
| 6 | $92xx | $8FC5 | $9015 | $9015 |
| 7 | $94xx | $8FC5 | $9056 | $9056 |
| 8 | $96xx | $8FC5 | $9008 | $9008 |
| 9 | $98xx | $8FC5 | $9054 | $9054 |
| 10 | $9Axx | $8FC5 | $9014 | $9014 |
| 11 | $9Cxx | $8FC5 | $9021 | $9021 |

(All SFX use V0=$8FC5 — the V0 stream is the first 80 bytes of every SFX record's data region, so they all point to the same runtime address after the copy. V1=V2 = mirror-doubling on the second voice.)

## Open questions / verification TODO

1. **Confirm per-voice variable layout** — the table above is anchored
   at $90C5 and projects Cybernoid II's contiguous arrays forward.
   Hawkeye's actual layout may have minor differences. Verify via py65
   trace (dump $90C5..$913B before and after `init`, then after each
   play() call).

2. **Confirm data-section boundaries** — the data addresses above are
   inferred from `LDA`/`STA` references in the seed. Many are educated
   guesses. The full data layout (instruments / sequences / patterns
   / freq table) needs a complete pass.

3. **Map the unreached code** — auto-trace got 2125 of 8768 bytes;
   the other ~76% is either data or code reachable only through
   computed jumps / self-modifying code. Audit the "data gap" markers
   in the seed.

4. **Identify all SMC sites** — at least $7B99 (testbyte), $7BAE
   (segment of song), $7BE4/$7BE5, $7B6B, $7AFE, $910A. Each SMC byte
   doubles as a runtime variable. Note them in this file.

5. **Cross-check against KIPPER1..14** — 14 small known-good FC V4
   tunes from the editor (in `pipelines/future_composer/artifacts/`
   PRG files). They use the V4 dialect. Will the same routines
   handle them?

6. **Multi-subtune handling** — Hawkeye has 12 subtunes. The init at
   `$7B5A` indexes per-subtune via X. The subtune table at `$83FC,X`
   is the speedbyte; per-subtune sequence pointers come from `$83F5,X`
   and `$7AFF,X`. Trace through 2-3 subtunes to confirm.

## Next steps

1. py65 trace pass: instrument the player, dump runtime state per
   frame, verify the variable layout.
2. Build an `engine_model.py` for the FC family — at minimum: list of
   subtunes, per-subtune speed + sequence pointers, instrument table,
   sequence streams, pattern data. The model will inform what the USF
   needs to carry.
3. Sketch the USF representation — informed by both Hawkeye's
   structure and the `docs/usf_representation_principle.md` discipline.
4. Build the extract path: SID binary → USF.
5. Build the composer path: USF → SID (probably as a new emitter chain
   in `pipelines/composer.py`, NOT folded into the existing simple-shape
   or bitpack branches — FC is structurally distinct).
6. Verify byte-exact via `verify_all`.

## Per-voice loop structure (added 2026-06-05)

Hawkeye does NOT have a tight `nextvoice` block like Cybernoid II.
The per-voice processing loop (entered at `$7BBA`, looping via
`dex / jmp $7BBA`) interleaves SID writes with effect processing:

```
Per voice (X = voice index, Y = $D40x voice offset):
  $80F4: sta $d402,y        ; PW LO (early)
  $80FA: sta $d403,y        ; PW HI (early)
  $80FD..$8110:               ; fx3 bit $40 — wave_arp (modifies $911B = cached ctrl)
  $8113..$812B:               ; fx3 bit $08 — pulse_arp (re-writes $D403,y)
  $812E..$813A:               ; fx3 bit $20 — tonesweep_up-like (modifies $9136)
  $813D..$8196:               ; fx3 bit $01 — fx_filter_prog
                              ;   writes $D418 = fb[5], $D416 = computed cutoff
  $8199..$81A5: fm2_cleanup   ; if voice == filwhat:
                              ;   lda #$e0     ← NOT $80 (Cyb II uses $80)
                              ;   sta $910c,x  ; cache
                              ;   sta $d416    ; write
                              ;   (no $D418 write — Cyb II writes both)
                              ; (no strange-filter check — Cyb II checks)
  $81A8..$820B:               ; fx2 bit $08 — strange_filter (writes $D416, $9132)
  ...
  $8311: sta $d404,y        ; CTRL (LATE)
  $8317: sta $d400,y        ; FREQ LO
  $831D: sta $d401,y        ; FREQ HI
  $8320: dex / bmi exit / jmp $7BBA
```

In Cybernoid II, by contrast, the per-voice loop runs ALL effects
first (writing their own regs as they go), then a tight `nextvoice`
block at the end writes ctrl/freq/PW in one chunk.

**Composer implications:**

1. The per-voice layout must be a per-cfg structural choice — not
   just a `nextvoice_write_order` permutation. Two layouts so far:
     - `tight_nextvoice` (Cyb II): all effects → tight 5-reg nextvoice
     - `interleaved` (Hawkeye): pw_writes → effects → ctrl+freq_writes

2. fm2 cleanup behaviour differs:
     - Cyb II: writes $D418 = $10|VOL, $D416 = $80, checks strange-filter bit
     - Hawkeye: writes $D416 = $E0 only, no strange-filter check

3. The strange-filter routine differs too (needs separate analysis);
   it's the `lda $f8 / and #$08` block starting at $81A8.

This is the next chunk of work to make Hawkeye match further.

## $822C octave-up effect + per-instrument flag byte (added 2026-06-05)

### What $822C does
```
$822B: LDA $910F,X / AND #$08 / BEQ skip
$8232: LDA lonotesto,x / CLC / ADC #$20 / STA d400,x
$823B: LDA hinotesto,x / ADC #$00       / STA d401,x  ; +carry from above
```
16-bit add of $0020 to (hinotesto:lonotesto), result into (d401:d400).
Pitch shift up by 32 freq units (~quarter semitone at top octave).

### Source of $910F[X]
Loaded once at note-init ($7D74-$7D99). Trace:
- LDA $8610,X (instrument record offset +4) / PHA
- LDA $860C,X (offset +0 — WAVE byte) / PHA
- LDA $860D,X (offset +1 — initial CTRL/wave shadow) / STA $90D1,x + $911B,x
- (stack pops in reverse)
- LDA $910F,x ← record byte +4

So `$910F,X = instrument_record[N].byte[4]`. Per-instrument flag byte.

### How $910F[X] is consumed
| bit | effect | site |
|---|---|---|
| 0-1 | filter-program selector | $8146 (fx_filter_prog) |
| $04 | enables conditional shadow-bump | $8243-$826B |
| $08 | octave-up ($D40020 16-bit add) | $822C |
| 6/7? | not yet traced | — |

### Cybernoid II comparison
Cyb II's filter_prog uses `filtercount,X & $07` (cyclic per-voice counter) for program selection — NOT a latched per-instrument byte. So this byte is Hawkeye-specific (or differs in role between engines).

### Implementing requires
1. **New instrument field** in USF schema: per-instrument flag byte (e.g. `flags: int` or named per-bit).
2. **Per-voice cache** (RAM slot — `inst_flags,x` 3-byte array) loaded at note-init from the instrument's flag byte.
3. **FCConfig knob** `filter_prog_selector: 'cyclic' | 'inst_latched'` — Cyb II 'cyclic'; Hawkeye 'inst_latched'.
4. **FCConfig knob** `has_octave_up: bool` — Hawkeye True; Cyb II False.

### Sub 1 frame-1 divergence — NOT solely explained by octave-up
orig d401[V3] = $3D, my d401[V3] = $30. Diff $0D.

If $822C is firing in orig but not in mine: adds at most +1 to hinotesto via carry. Doesn't explain $0D.

Likely the underlying hinotesto[V3] ALSO differs between orig and mine — meaning a different note value is loaded for V3 at frame 1, OR an earlier effect (tone_arp / vibrato / glide / drum) modifies it differently. Worth investigating BEFORE implementing octave-up — the fix may be elsewhere.

### Sub 1 V3 divergence — root cause IS noise_tick, not octave-up

py65 dump of V3 across frames (orig vs reb):
```
orig: f0 $D40F=$02 hinote=$02 ctr2=$00
      f1 $D40F=$3D hinote=$02 ctr2=$01
      f2 $D40F=$07 hinote=$02 ctr2=$02
reb:  f0 $D40F=$02
      f1 $D40F=$30
      f2 $D40F=$FA   ← noisehitone!
```

`$D40F=$FA` at reb f2 is Cyb II's `noisehitone` constant from my fx_noise_tick attack branch. My code is mistakenly firing the noise-tick path for V3 because:
  1. Hawkeye `startlen_addr=0` / `starttabel_addr=0` (placeholders).
  2. My fx_noise_tick `lda starttabel,y` reads garbage from $0000+y.
  3. When the garbage is >= $7F it goes into the noise-attack branch (`d401=$FA`).

Real fix: Hawkeye's noise_tick at $82D4-$830B is structurally different:
  - `if fx3 bit $80 not set → skip`
  - `if counter2 < 2 → d400=$00 d401=$58 stod404=$81`  (hardcoded)
  - `if 2 <= counter2 < 4 → d400=lonotesto d401=hinotesto stod404=wavesto&$FE`
  - `else → no-op`

Different constants ($58 vs $FA), no per-instrument startlen/starttabel lookup. This needs an FCConfig knob `noise_tick_style: 'cyb2_table' | 'hawkeye_constants'` plus the Hawkeye-style routine.

### Real root cause: Hawkeye's fx_drum produces $3D, not noise_tick

Re-reading $826C-$82D3 (Hawkeye's fx_drum / fx3 bit $10):
```
$826C: LDA fx3sto / AND #$10 / BEQ skip ; not drum
$8272: LDA $F7 / AND #$0F / ASL / ASL / TAY  ; Y = (inst & $0F) * 4
$8279-$8291: SMC-load 4 drumtabel ptrs into program slots
$829D: LDA counter2,x / CMP #$03 / BCS $82D1 (→ late writes)
$82A5: LDA drum_table_A[counter2] / STA stod404,x
$82AC: LDA drum_table_B[counter2-1] / STA $910B
$82B6: LDA $F7 / AND #$10 / BEQ $82C3
$82BA-$82C0: (alt path) freq via $8327 callback
$82C3: LDA $910B / CLC / ADC #$0D / STA $9136,x  ; d401 = drum_B + $0D
$82CC: LDA #$00 / STA $9133,x                     ; d400 = 0
```

For sub 1 V3 frame 1 (counter2=1):
- `drum_table_B[0] = $30` (likely; from drum prog at drumtabel[V3_inst*4])
- `d401 = $30 + $0D = $3D` ✓ matches orig

For frame 2 (counter2=2): `drum_table_B[1] = ?`, `d401 = ? + $0D = $07` → `drum_B[1] = $FA` (or -6 signed).

This is Hawkeye-specific fx_drum logic — different from Cyb II's. My Cyb II fx_drum uses `lda st / sta d401` with `st` being the drum tone byte. Hawkeye uses two parallel drum tables (drum_A → stod404 shadow, drum_B → d401 with $+0D offset).

**Path forward**: this needs a new noise_tick style + new fx_drum style as parametric FCConfig choices. Both Cyb II's and Hawkeye's are valid engine variants. The chain emitter should select per cfg.

For now, **disabling fx_noise_tick for Hawkeye** (since startlen/starttabel are unset placeholders reading garbage) would at least stop the $FA misfire at frame 2.

Additionally noted: per-voice fx3 cache in Hawkeye may not even be at the same address my model assumes. Hawkeye's instrument-record layout is different — record +0 is WAVE byte (PHA'd, low nibble → $D403), +1 is stod404 init, +2 AD, +3 SR, +4 → $910F (extension flags). No obvious per-instrument fx3 slot in the record; fx2/fx3 come from sequence stream commands instead.
