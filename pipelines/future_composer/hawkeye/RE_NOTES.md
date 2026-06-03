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

⚠️ The above is a **best-guess mapping** based on Cybernoid II's
sequential layout. The byte order may be permuted in Hawkeye (Tel
sometimes reordered for cache layout). Verify by:
1. Cross-reference each `$90XX,x` reference in `disassembly.s` against
   the same access in Cybernoid II.
2. Or py65-trace Hawkeye's init+first-frame, dump $90C5..$913B before
   and after each frame, infer roles from update patterns.

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

## Data section addresses (Hawkeye)

| Address | Purpose | Notes |
|---|---|---|
| `$7AE0` | PSID entry: JMP init | |
| `$7AE3` | PSID entry: JMP play | |
| `$7AE6..$7B31` | data gap (76 bytes) | per-subtune seqlochi pointers + speedbyte table + scratch buffer (the 6 bytes Cybernoid II copies at $83FC) |
| `$7B2C..$7B31` | 6-byte template copied to $8403,Y on init | (Cybernoid II copies from `template:` to `seqloclo`) |
| `$7B32..$7B97` | init / reset code | |
| `$7B98..$7DC9` | play loop | |
| `$7DCA..$7DF8` | sustain freq update | |
| `$7DF9..$830C?` | per-frame instrument processing (wave/pulse/filter walking) | |
| `$830C..??` | continue play loop | |
| `$8337..$83F4` | freq lookup table (lo at $8337, hi at $8396) | 96-entry PAL freq table, 96 bytes each |
| `$83F5..$83FB` | per-subtune setup data (×12 subtunes?) | `$83F5,X` = init data, `$83FC,X` = speedbyte |
| `$83FC..$8402` | per-subtune speedbyte table (12 bytes) | |
| `$8403..$8408` | runtime sequence pointers (6 bytes, modified by init) | `seqloclo` / `seqlochi` per voice |
| `$8409..$84??` | sequence pointer table (per pattern) | `sequence,y` indexed by 2*pattern_id |
| `$8580..$8588` | instrument table column 1 | (per `L_7CD0`) |
| `$8589..$8591` | instrument table column 2 | |
| `$8FC5..$??` | sequence data (the actual byte streams) | per `L_7BE3: LDA $8FC5,y` |
| `$90C5..$913B` | per-voice runtime variables | 119 bytes |
| `$918F` | subtune dispatch (entered from `JMP init`) | |

⚠️ Many of these are EDUCATED GUESSES from a single-pass disassembly read.
They need verification — see "Open questions" below.

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
