<!--
provenance:
  doc: JCH NewPlayer — binary → USF extraction plan
  sources:
    - source_url: https://codebase64.com/doku.php?id=base:jch_20.g4_player_file_format
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      author: (codebase64 wiki; original JCH/Vibrants doc)
      content_date: ~2010s
      reliability: MEDIUM — author states "the description is not 100% complete";
                   gives the $xxCB memory map + sequence byte-pair codes only.
    - local: tmp/jch/player_v4.acme   (CheeseCutter player source, 1763 lines)
      source_url: https://raw.githubusercontent.com/theyamo/CheeseCutter/master/src/c64/player_v4.acme
      fetched_via: curl (raw.githubusercontent.com)
      fetch_date: 2026-06-13
      author: abad (Aleksi Eeben), "Based on JCH NP 21.G4 by Laxity/VIB"
      content_date: header "cc4.07"
      reliability: HIGH for SEMANTICS (HR types, wave/pulse/filter stepping, command
                   set, write order). NOTE: its DATA ENCODING is CheeseCutter's own
                   RUNTIME (columnar, INSNO=48 stride) + EXPORT=FALSE editor layout —
                   NOT the packed NP20.G4 on-disk layout that HVSC uses. Use it for
                   "what the engine DOES", not "how bytes are laid out on disk".
    - local: hvsc84/MUSICIANS/O/Odkin/Wild.sid  (real packed NP20.G4, load=$1000)
      fetched_via: direct binary read (read-only)
      fetch_date: 2026-06-13
      reliability: HIGH — GROUND TRUTH for the packed on-disk $xxCB layout, instrument
                   stride, order-list encoding. This is what 3195/3611 HVSC JCH tunes use.
    - local: hvsc84.db (read-only)  — engine census + load/init/play distribution.
-->

# JCH NewPlayer — Binary → USF Extraction Plan

## 0. Scope, census, and the CRITICAL version split

HVSC #84 census (`hvsc84.db`, engine column from sidid):

| engine                  | count | note |
|-------------------------|------:|------|
| `JCH_NewPlayer`         | 3611  | THE target family |
| `Laxity_NewPlayer_V21`  |  313  | sibling (`pipelines/laxity_newplayer/`) |
| `JCH_Protracker`        |   94  | different player |
| `Glover_NewPlayer_V21`  |   67  | derivative |
| `JCH_OldPlayer`         |   32  | predecessor (pre-NP) |
| `(Dane_NewPlayer)`      |    5  | derivative |
| `JCH_DigiPlayer`        |    4  | digi |

Entry-point distribution of the 3611 `JCH_NewPlayer` tunes:

| count | load(hdr) | init   | play   |
|------:|-----------|--------|--------|
| 3195  | $0000     | $1000  | $1003  | ← dominant NP20.G4-style (88%) |
|   31  | $0000     | $5000  | $5003  | relocated |
|   31  | $0000     | $e000  | $e003  | relocated |
|   21  | $0000     | $8000  | $8003  | relocated |
|   18  | $0000     | $0fe0  | $0ff1  | variant header (jump table longer) |
|   16  | $0000     | $4000  | $4003  | relocated |
|   11  | $0000     | $1000  | $1006  | variant header (play = init+6) |
|  ...  |           |        |        | (other relocations) |

`load(hdr)=$0000` is the standard PSID convention: **the real load address is the
first two bytes (little-endian) of the data block** at `header[0x06:0x08]` offset.
For `Wild.sid`: dataoff=$7C, first two data bytes → realload=`$1000`.

> **THE BIG FACT — two distinct binary encodings under one engine name.**
> 1. **Packed NP20.G4 on-disk layout** (what HVSC ships, 3195+ tunes): fixed
>    `$xxCB` table map relative to load; **row-major 8-byte instruments**;
>    **2-byte (transpose, seq#) order-list pairs terminated by `$FF`**; sequence
>    = (control,note) byte pairs.
> 2. **CheeseCutter / NP21.G4 runtime layout** (the `.acme` source): **columnar
>    instrument arrays** (stride `INSNO=48`); **4-byte track entries** with `$Fx`
>    wrap; **3-column command table** (cmd1/cmd2/cmd3, stride $40); 4-byte
>    pulse/filter rows.
>
> The CheeseCutter SOURCE is authoritative for *engine behaviour* (what each byte
> MEANS, the per-frame write order, HR timing). The BINARY is authoritative for
> *byte layout*. **Extraction reads the packed binary; the write model uses the
> CheeseCutter semantics.** Do not assume CheeseCutter's disk encoding for HVSC tunes.

Verification target (per project CORE TENET): the `$D400-$D418` write stream, NOT
the player code. Mode-1 (per-frame instruction-sequence) for tracker tunes;
multispeed Q-series may need the CIA per-play capture (see `spec_write_model.md`).

---

## 1. Anchor the player

1. Parse PSID header: `magic@0`, `version@7`, `dataOffset@0x06` (BE16),
   `loadAddress@0x08`, `initAddress@0x0A`, `playAddress@0x0C`, `songs@0x0E`,
   `startSong@0x10`, `speed@0x12` (BE32, CIA bits), `flags@0x76` (PSIDv2+).
2. `data = file[dataOffset:]`. If header loadAddress == 0:
   `realload = data[0] | data[1]<<8`; `body = data[2:]` (maps to `realload`).
   Else `realload = header loadAddress`; `body = data`.
3. **Signature check** (dominant variant). At `body[0:9]` (the jump table at load):
   ```
   4c 40 10  4c bf 10  01 01 01      ; JMP $1040 (init) / JMP $10BF (play) / data
   ```
   Both `init=$1000` tunes sampled share `4c ?? ?? 4c ?? ??` then volume default
   `$0f` near +$09. The header is **2× JMP = 6 bytes** for the `play=init+3` group;
   the `play=init+6` and `$0fe0/$0ff1` groups have a longer header (3 jump
   vectors incl. the multispeed `mplay`, cf. CheeseCutter lines 252-260:
   `init→jmp / play→jmp / mplay→jmp / sync !8 0`). **VERSION-DEPENDENT:** detect
   header length from the jump-vector count, not a constant.
   For the CANONICAL reloc-invariant fingerprints (the ~20 versioned sidid
   patterns V1-V20 + Dane), use `sibling: github_parser_notes.md §2` — the stable
   dispatch signature is `4C ?? ?? 48 29 E0 C9 80 D0 ?? 68 48 29 10` (the `state`
   bit7/bit6 keyjam-vs-multiplay test) and the 3-voice init-copy loop
   `A2 00 … C8 C8 E8 E0 03 D0` (`subinit0`). Prefer those over a raw-byte compare.
4. Relocated tunes (init=$5000/$8000/$e000/...) are the SAME engine at a different
   load; some are self-relocating (e.g. `Starburst.sid`, load=$2200, header
   `aa bd 58 89 …` = TAX/LDA $89xx,X copy loop). For these, the `$xxCB` map is
   taken relative to the EFFECTIVE base after relocation, not the file load.
   **OPEN-1:** confirm the post-relocation base for self-relocating variants by
   `tools/siddump --pc-trace FILE $init $init+0x40` and watching the copy target.

> The `$xxCB` offsets below are stated as ABSOLUTE for a load=$1000 tune. For any
> other load, use `base = realload` and `addr = base + ($xxCB - $1000)` i.e. the
> offset-from-load is the invariant: arpA=+$8CB, arpB=+$9CB, filt=+$ACB,
> puls=+$BCB, inst=+$CCB, seqlo=+$DCB, seqhi=+$ECB, super=+$FCB, ol0=+$10CB,
> ol1=+$14CB, ol2=+$18CB, seqdata-arena=+$1CCB. **VERSION-DEPENDENT:** these
> offsets are the NP20.G4 packer's choice; other JCH player versions (17.x, 22-25,
> the `$0fe0` group) may place tables differently — see §9.

---

## 2. Memory map — packed NP20.G4 (confirmed against `Wild.sid`)

| Table                       | addr (load=$1000) | size  | confirmed bytes (Wild.sid) |
|-----------------------------|-------------------|-------|----------------------------|
| Player code + jump table    | $1000             | ~$8CB | `4c4010 4cbf10 010101…`     |
| Wave table col A (arp1)     | $18CB             | 256   | `67 6c 6f 7f 70 73 78 7f …` |
| Wave table col B (arp2)     | $19CB             | 256   | `41 41 41 10 41 41 41 14 …` |
| Filter table                | $1ACB             | 256   | `0f 09 56 10 00 …`          |
| Pulse table                 | $1BCB             | 256   | `00 00 …` (unused here)     |
| Instrument table            | $1CCB             | 256   | `00 6a 80 f1 04 04 0a 0a │ 00 7f 80 f1 04 04 0a 0a` |
| Sequence ptr LO (seqlo)     | $1DCB             | 256   | `bd bd bd bd …` (all $BD)   |
| Sequence ptr HI (seqhi)     | $1ECB             | 256   | `3c 3d 3e 3f 40 41 …` (asc) |
| Super / command table       | $1FCB             | 256   | `00 3c 20 17 00 00 20 30 …` |
| Order list voice 0          | $20CB             | 1024  | `8c 03 8c 03 8c 03 …`       |
| Order list voice 1          | $24CB             | 1024  | `8a 02 8c 0a ff 00 …`       |
| Order list voice 2          | $28CB             | 1024  | `8c 05 8c 09 ff 00 …`       |
| Sequence data arena         | $2CCB+            | —     | (located via seqlo/seqhi)   |

The codebase64 page (verbatim, rendered) gives the same map and adds:
`Sequence 0 data $2CCB (+3 bytes offset)`, `Sequence 1 data $2DCB (+3 bytes offset)`.
**The "+3 bytes offset" hints the seqdata arena slots are $100-spaced** (matches
CheeseCutter `s0` spaced `$100` apart, lines 1719-1725) but the actual sequence
addresses come from the pointer table, not from this arena base — see §5.

---

## 3. Instrument decode — packed (row-major, 8 bytes/instrument)

> **Packed disk layout = 8 CONTIGUOUS bytes per instrument** (confirmed:
> `00 6a 80 f1 04 04 0a 0a` then next instr `00 7f 80 f1 04 04 0a 0a`).
> Instrument N at `inst_base + N*8`. (CheeseCutter's *runtime* uses columnar
> `inst+k*48`; the packer transposes. Don't apply the ×48 stride to disk bytes.)

Per-byte (byte index → field; CheeseCutter `idescr*` lines 152-159 give meaning):

| idx | field         | meaning (verbatim idescr) |
|----:|---------------|---------------------------|
| 0   | AD            | "Attack / Decay." → $D405 |
| 1   | SR            | "Sustain / Release." → $D406 |
| 2   | HR/arp        | "Restart type / arpeggio speed. $00 = 3 Frame Restart. $40 = Soft restart. $80 = Hard Restart. $00-$0F = Arpeggio delay value." (hi nibble = type, lo nibble = wave/arp delay) |
| 3   | HR waveform   | "Hard Restart waveform." |
| 4   | Filter ptr    | "Filter Table pointer." (row index; ×4 to get byte offset, see §7) |
| 5   | Pulse ptr     | "Pulse Table pointer $00-$3f." (row index; ×4) |
| 6   | HR SR         | "Hard restart SR envelope value." (← BACKGROUND called this "unused"; it is the HR SR. CheeseCutter `INS_7`, used at `laxhr lda inst+INS_7,y / sta sr,x`, line 569) |
| 7   | Wave ptr      | "Wave Table pointer." (start row into arp1/arp2) |

USF instrument fields to emit (parametric, per `docs/the_principle.md`):
`ad`, `sr`, `hr_type` ∈ {3frame,soft,hard,laxity}, `arp_delay` (lo nibble of byte2),
`hr_waveform`, `hr_sr` (byte6), `filter_program` (ref by content, §7),
`pulse_program` (ref by content, §7), `wave_program` (ref by content, §6).
HR-AD is NOT per-instrument; it is the global super-table row-0 value (see §8, §write_model).

> **HR type nibble decode** (CheeseCutter `syncnottied`, lines 551-573):
> - byte2 bit7 = 0 (`$0x`): "3-frame" — gate-off only, no ADSR overwrite.
> - byte2 bit7 = 1, bit5 = 0 (`$8x`): hard restart — AD←`cmd2` (global HR-AD), SR←byte6.
> - byte2 bit7 = 1, bit5 = 1 (`$Ax`): "Laxity" restart — AD untouched, SR←byte6.
> - `$4x` (soft): bit7=0 too, but bits7-6=`01` is checked at gate-on (lines 667-670:
>   `and #$c0 / cmp #$40 / beq wavenotoff`) → soft restart SKIPS forcing the HR
>   waveform on the gate-on frame. **VERSION/decode subtlety:** `$4x` shares the
>   bit7-clear path for gate-off purposes with `$0x`. Treat the full bits7-6 field
>   as the type: 00=3frame, 01=soft, 10=hard, 11=laxity.

**Number of instruments:** packed tunes do not store a count inline; derive from
the highest instrument index referenced by any sequence (control byte $Ax-$Bx, §5),
clamped to the table region ($1CCB..$1DCB = 32 max for NP20.G4; CheeseCutter
runtime allows 48). **VERSION-DEPENDENT max:** 32 (NP20.G4), 48 (NP21/CheeseCutter).

---

## 4. Order list (track) decode — packed NP20.G4

> Confirmed: **2-byte `(transpose, seq#)` pairs, terminated by `$FF`.**
> v0: `8c 03 | 8c 03 | …` (transpose=$8C, seq=$03 repeated).
> v1: `8a 02 | 8c 0a | ff` (then `00` pad).
> v2: `8c 05 | 8c 09 | ff`.

Decode loop per voice (start at ol_base for that voice; voices at +$0000/+$0400/+$0800):
1. Read `t = byte`. If `t == $FF` → end of order list → **loop** (back to start, or
   to a stored loop point — packed NP20.G4 loops to start; CheeseCutter uses the
   `$Fx`+lo-byte wrap target, different encoding — see §9). 
2. `transpose = t`. Per BACKGROUND/codebase64: `$A0 = none (0)`, `$A0±n = ±n
   semitones`. So `signed_transpose = t - $A0`. (Wild's `$8C` = `$8C-$A0` = −$14 =
   −20 semitones; `$8A` = −22.) **OPEN-2:** confirm the transpose zero-point is `$A0`
   for the PACKED format (CheeseCutter `updtrack` uses `sbc #$a0`, line 409, which
   confirms $A0 = 0; AND short-circuits `$80` as "keep previous transpose", line
   407-408 — check whether packed NP20.G4 also reserves `$80`).
3. Read `seq# = byte`. Append `(signed_transpose, seq#)` to the voice orderlist.
4. Repeat until `$FF`.

USF: per voice an `Orderlist` of `(transpose, sequence_id)` entries + a loop marker.
This maps cleanly onto the existing `Orderlist` + `Orderlist.transposes` schema
(cf. FC's `loop@N+T` / `loop_transpose` — JCH's per-entry transpose is the same shape).

> CheeseCutter track encoding (DIFFERENT — VERSION-DEPENDENT, do NOT use for HVSC):
> 4-byte logic in `updtrack` (lines 392-438): transpose byte (`$80`=keep, else
> `sbc #$a0`), then seq#, then a 2-byte `$Fx`+lo wrap (`cmp #$f0 / bcc trk03` then
> `and #$07` hi-adjust + next-byte lo). Its order-list TERMINATOR is `$F0..$F7`,
> not `$FF`. This is the cc/NP21 packer, not the HVSC NP20.G4 packer.

---

## 5. Sequence decode — packed NP20.G4 (control,note byte pairs)

Locate sequence N: `addr = seqlo[N] | (seqhi[N] << 8)`.

> **OPEN-3 (IMPORTANT) — the static seqlo/seqhi pointers may be editor-relative.**
> In `Wild.sid`, `seqlo[0]=$BD, seqhi[0]=$3C → $3CBD`, but body ends at `$36E0`
> (load $1000 + 9952 bytes). The pointer is OUT OF the loaded image. Two
> possibilities: (a) the player REBASES these pointers at init (CheeseCutter
> `subinit` copies `songsets→twraplo/twraphi` rather than trusting absolutes,
> lines 274-282), or (b) seqlo/seqhi here are stale editor values and the live
> sequence base is computed. **CLOSE IT** with
> `tools/siddump --pc-trace Wild.sid $1000 $10ff` to capture the init's pointer
> setup, then `--memwatch-on-write` the seqlo/seqhi/ZREG region, OR disassemble
> init ($1040) to see how the (ZREG) sequence pointer is formed at `nextnote`
> (CheeseCutter `nextnote`, lines 443-447: `ldy curseq,x / lda seqlo,y / sta ZREG /
> lda seqhi,y / sta ZREG+1`). Until resolved, treat the sequence ARENA as starting
> at `$2CCB` (codebase64 map) and the pointer table as an index into it modulo the
> rebase. This is the #1 blocker for a working extractor.

Byte-pair decode (codebase64 verbatim + BACKGROUND, control=AA, note=BB):

AA (control byte):
| value     | meaning |
|-----------|---------|
| `$7F`     | end of sequence (NP20.G4). (CheeseCutter uses `$BF`, line 499 `cmp #$bf` — VERSION-DEPENDENT.) |
| `$90`     | tie note (hold; no re-gate) |
| `$80`     | no operation / empty (keep current instr) |
| `$A0-$BF` | select instrument `$00-$1F` (value − $A0) |
| `$C0-$DF` | super-table pointer (value − $C0) → applies the command/super entry (§8) |

BB (note byte):
| value     | meaning |
|-----------|---------|
| `$00`     | gate off (rest) |
| `$01-$7D` | note value (index into freq table after +transpose) |
| `$7E`     | gate hold |

Confirmed against `Wild.sid` seqdata-arena bytes `a2 30 80 00 80 00 80 00 a3 30
80 00 a2 30 80 00`: `a2`=instr$02, `30`=note$30; `80 00`=nop+gate-off ×3; `a3`=
instr$03, `30`=note; etc. — exactly the (control,note) pairing.

USF: each sequence → a list of note rows `(note|rest|tie|hold, instrument?, super?)`.
Duration in NP20.G4 is implicit (one frame per row × song speed) unless a super/speed
command sets it. **OPEN-4:** confirm NP20.G4 per-row duration model — CheeseCutter
has an explicit `$Fx` set-duration command in-sequence (`setdur and #$0f`, lines
477-482) and a `duration,x`/`durcnt,x` counter; the packed format's BB=note/AA=ctrl
pairs do NOT obviously carry per-row duration, so duration is likely the global
`speed`/`speedcnt`. Verify by tracing row advance vs. frame count on a known tune.

---

## 6. Wave table decode (arp1 = col A, arp2 = col B; 256 each, parallel)

Per-row `(A, B)`. Confirmed Wild rows: `(67,41)(6c,41)(6f,41)(7f,10)(70,41)…`
Stepping logic from CheeseCutter `dowave`/`waveok` (lines 951-1024):

Column A (arp1) — transpose/loop (codebase64 `wdescr0` verbatim):
| value     | meaning |
|-----------|---------|
| `$00-$5F` | relative transpose up: `freq_index = A + notereal (+chord)`, then `freq += shfreq` (slide/vib accumulator) |
| `$80-$DF` | absolute tuning: `freq_index = A & $7F` (note/transpose ignored). `lda freqtable_lo/hi,y` directly |
| `$7E`     | loop to PREVIOUS row (stop advancing; hold) |
| `$7F`     | loop to row given by col B at the `$7F` position |

Wild row3 A=`7f` B=`10` and row7 A=`7f` B=`14`: these are the `$7F` loop markers
whose col-B byte (`10`,`14`) is the loop-TARGET row. (`waveskip lda arp1+1,y / cmp
#$7e … cmp #$7f / lda arp2,y / tay`, lines 971-985.)

Column B (arp2) — waveform / delay / loop ptr (codebase64 `wdescr1` verbatim):
| value     | meaning |
|-----------|---------|
| `$00`     | do nothing (keep waveform) |
| `$01-$0F` | override this row's wave delay (`sta wavecnt,x`) |
| `$10-$DF` | waveform = this value (→ $D404 control reg, with gate ANDed) |
| `$E0-$EF` | waveform = value & $0F (control reg $00-$0F) |
| any       | when col A = $7F: this is the loop-pointer (target row) |

Wild row0 B=`41` = waveform $41 (pulse + gate); row3 B=`10`=loop target; row10
A=`10` B=`81` = relative+16, waveform $81 (noise+gate).

USF: a `wave_program` (referenced BY CONTENT from the instrument's byte7 start row),
a list of `(transpose_or_abs, waveform_or_delay, is_loop, loop_target)` rows. This
is the FC `wave_adjust`/wavetable shape — reuse that representation.

---

## 7. Pulse & filter tables — STRIDE IS VERSION-DEPENDENT

> **NP20.G4 (BACKGROUND): 2 bytes/row.** **NP21+/CheeseCutter: 4 bytes/row.**
> Wild.sid's pulse region is all-zero (unused) so it doesn't disambiguate; the
> filter region `0f 09 56 10 00…` is consistent with EITHER a 4-byte row
> `[0f 09 56 10]` or two 2-byte rows. **OPEN-5:** disassemble the packed NP20.G4
> player's pulse/filter stepping to confirm the row stride for the 2-byte variant
> (CheeseCutter is unambiguously 4-byte; the codebase64 page does not state the
> NP20.G4 pulse/filter byte count). Close with `tools/siddump --pc-trace` over the
> filter/pulse update code, or find a 2-byte-table-era player source.

### Pulse table — 4-byte rows (CheeseCutter, `pdescr0-3` lines 161-164; `updatepulse` 690-746)
| byte | field (verbatim pdescr) |
|-----:|--------------------------|
| 0    | "Duration and direction. $00-$7F = Add n frames. $80-$FF = Subtract n frames." (bit7 = direction; `and #$7f` = duration count) |
| 1    | "Add value." (added to/subtracted from pulse-width lo each frame) |
| 2    | "Initial pulse value. Note: Nibbles are reversed! $48 = $8400" — `$FF` = retain (skip set). `sta pulselo (lo nibble→lo) / pulsehi (hi nibble)` per the reversed-nibble code lines 701-706 |
| 3    | "Pointer to next set ($00-$3F) or $7F = stop." `$00` = auto-advance (+4 bytes / +1 row); `$7F` = stop; else ×4 = jump to row |

Instrument pulse-ptr (byte5) ×4 = byte offset; `$00` = no pulse program.
CheeseCutter also supports DIRECT pulse (`INS_PULSP` bit7 set → `and #$0f` → pulsehi
direct, lines 626-633) — a `$8x` pulse pointer means "set pulse hi = x directly".

### Filter table — 4-byte rows (CheeseCutter, `fdescr0-3` lines 166-169; filter routine 1405-1471)
| byte | field (verbatim fdescr) |
|-----:|--------------------------|
| 0    | "Duration or filter type. $00-$7F = Duration or $90-$F0 select filter type." bit7 set → INIT row: `and #$70` → routing/bandpass (→ $D418 hi bits via `bandpass`) |
| 1    | "Add value or filter resonance and channel mask." On init row → `$D417` (res + voice routing); `and #3` + sweep-rate bits feed `filtadd` |
| 2    | "Initial filter value or $FF = skip." → `filter` (cutoff hi $D416); `$FF` = don't set |
| 3    | "Pointer to next set ($00-$3F) or $7F = stop." `$00`=auto +4; `$7F`=stop; else ×4 |

Filter is a GLOBAL resource in this engine (single `filter`/`bandpass`/`filtnxt`,
NOT per-voice — see the non-`,x` stores at lines 1408-1470). Instrument filter-ptr
(byte4) ×4 = offset; `$00` = no filter reset. Filter cutoff written each frame to
`$D415` (lo, masked to 3 bits / 10-bit sweep) + `$D416` (hi); routing to `$D417`;
resonance/routing high-bits ORed into `$D418`.

USF: `pulse_program` + `filter_program` referenced by content; a top-level / global
filter channel (the filter is shared, like a master effect). Represent the filter
program as `(type, res_routing, init_cutoff, rows[(duration,add)…], loop)`.

---

## 8. Super / command table decode ($1FCB)

> **TWO different shapes — VERSION-DEPENDENT.**

### CheeseCutter / NP21 (authoritative semantics; `checksuper`/`iscmd` lines 1028-1306)
A sequence super-pointer (`$Cx-$Dx` control) sets `shsuper,x`. On the gate frame
(`tsync==$ff`), `superparse2` dispatches on the super VALUE:
- `$00-$3F` → **command-table index** → `iscmd`: read 3 parallel columns
  `cmd1[y]`, `cmd2[y]`, `cmd3[y]` (stride $40 in cc runtime). `cmd1[y]` = command #:

  | cmd1 | command (verbatim mdescr0) | params (cmd2,cmd3) | effstate |
  |-----:|----------------------------|--------------------|----------|
  | $0   | Slide up                   | signed 16-bit speed (hi=cmd2, lo=cmd3) | 1 |
  | $1   | Slide down                 | signed 16-bit speed | 2 |
  | $2   | Hi-fi Vibrato              | cmd2 lonib=feel; cmd3 hinib=speed, lonib=depth-divider | 3 |
  | $3   | Detune ("Set offset")      | sets shfreqhi=cmd2, shfreqlo=cmd3 | — |
  | $4   | Set ADSR                   | ad=cmd2, sr=cmd3 | — |
  | $5   | Lo-fi vibrato              | cmd2=freq, cmd3=amp | 4 |
  | $6   | Set wave                   | waveform=cmd3 (DISABLED: INCLUDE_CMD_SET_WAVE=FALSE) | — |
  | $7   | Portamento                 | cmd2 lonib=portahi, cmd3=portalo; runs until cmd 8 | $81 |
  | $8   | Stop portamento/slide      | effstate=0 | 0 |

- `$40-$FF` → **inline super commands** (no table lookup), dispatched by range
  (lines 1043-1170):

  | range     | action (→ register effect) |
  |-----------|-----------------------------|
  | `$40-$5F` | set pulse program (`& $1f`, ×4 → pulsenxt) |
  | `$60-$7F` | set filter program (`& $1f`, ×4 → filtnxt) |
  | `$80-$9F` | set chord (`& $1f` → chordindex → arpeggio table) |
  | `$A0-$AF` | set Attack (hi nibble of AD) |
  | `$B0-$BF` | set Decay (lo nibble of AD) |
  | `$C0-$CF` | set Sustain (hi nibble of SR) |
  | `$D0-$DF` | set Release (lo nibble of SR) |
  | `$E0-$EF` | set Volume (lo nibble → $D418) |
  | `$F0-$FF` | set Speed (`& $0f`; `$F0`=toggle sync flag; else `speed`) |

### Packed NP20.G4 ($1FCB, confirmed flat in Wild.sid)
Wild super bytes: `00 3c 20 17 | 00 00 20 30 | 20 50 20 f0 | 20 60 90 b4 | 20 17
00 50 | 00 40 00 1f | 20 20 20 80 …` (then zeros, last row `00 00 00 fe`). A
columnar-stride-$40 read gives all data in column 0 (cols 1-3 ≈ 0), so **the
packed NP20.G4 super table is a DENSE byte stream, not 3 separate $40 columns.**
The values look like 4-byte groups but do not parse as clean (cmd, p1, p2) triples.

> **OPEN-6 (IMPORTANT) — packed super-table stride + row-0 semantics.**
> The codebase64 page says "row 0 stores hard restart ADSR values" and lists cmds
> 0-8, but does not give the packed byte stride. Wild row0 = `00 3c 20 17`; the HR
> path reads the global HR-AD from a fixed location (CheeseCutter `cmd2` = byte at
> `supertab+$40`, default `$0f`). **CLOSE IT** by disassembling the packed NP20.G4
> player's `$1FCB` access: find every `LDA $1Fxx,Y` / `LDA (ptr),Y` that indexes
> the super table and read off the stride + which byte is HR-AD. Use
> `tools/seed_disassembly.py` on `Wild.sid` init+play, annotate, then
> `tools/effect_chain_profiler.py Wild.sid --register D405` to see which super row
> drives an AD write. Until closed, the super-table command decode for the PACKED
> format is the second blocker (after OPEN-3).

USF: super/command entries become per-row effect parameters on the note that
references them (slide rate, vibrato depth/speed, porta, ADSR set, detune,
pulse/filter/chord/volume/speed change). All map to existing FC/Hubbard effect
primitives (freq slide, vibrato, portamento, ADSR override, pulse/filter program
select) — no new schema kinds expected. The chord ($80-$9F) is an arpeggio-table
index → reuse the arpeggio/chord representation.

---

## 9. Version differences — extraction switches

| concern | NP20.G4 (packed, HVSC) | NP21 / CheeseCutter | other JCH |
|---------|------------------------|---------------------|-----------|
| table map | fixed `$xxCB` rel. load | editor `$0fa0` ptr block + dynamic `*=$2000` data | 17.x / 22-25 / `$0fe0` group differ — OPEN-7 |
| header / jump table | 2× JMP (6 B), `play=init+3` | 3 vectors (init/play/mplay)+sync byte | `play=init+6` and `$0ff1` variants exist |
| instrument | row-major 8 B/instr, max 32 | columnar stride 48, max 48 | — |
| order list | 2-B `(transpose,seq)`, `$FF` end | 4-B track, `$Fx`+lo wrap | — |
| seq end mark | `$7F` | `$BF` | — |
| seq super range | `$C0-$DF` (sequence control) | `$Cx-$Dx` ctrl → super, super itself `$00-$FF` ranged | — |
| pulse/filter row | 2 B/row | 4 B/row | — |
| speed | 1× (G4); multispeed = Q-series | `MULTISPEED=TRUE`, CIA | G vs Q suffix = speed class |
| `G` vs `Q` | `G` = vblank (50Hz) | — | `Q` = multispeed/CIA-timed |

> **OPEN-7:** acquire format details for non-NP20.G4 packed variants (17.G0, 21.G4-G6,
> 22-25, the `$0fe0/$0ff1` group, the self-relocating `Starburst`-type). These are
> ~416 of 3611 tunes. Use `tools/engine_fingerprint.py`-style reloc-invariant
> fingerprinting (cf. FC standard-player work, `project_fc_fingerprint_and_standard`)
> to bucket the 3611 by player sub-version, then anchor each bucket's table map
> against one representative binary. Likely 80-90% collapse to the single dominant
> NP20.G4 map (mirrors FC's 91%-one-player finding).

---

## 10. Extraction order of operations (the checklist)

1. PSID parse → realload, body, subtunes, CIA speed bits. (§1)
2. Fingerprint the player sub-version (jump-table length + header bytes); pick the
   table map. Default: NP20.G4 `$xxCB`. (§1, §9)
3. Read instrument table (8-B rows) → instruments. (§3)
4. Read wave (arp1/arp2), pulse, filter tables → programs (by content). (§6, §7)
5. Read super/command table → effect/command parameter pool. (§8) — needs OPEN-6.
6. **Resolve sequence pointer base** (seqlo/seqhi rebase). (§5) — needs OPEN-3.
7. Decode each referenced sequence (control,note pairs) → note rows. (§5)
8. Decode order lists (transpose, seq#) per voice, `$FF` end → orderlists. (§4)
9. Emit USF: init.sid priming (master vol $0F, filter off, HR-AD), per-voice
   orderlists w/ transpose, sequences, instruments, wave/pulse/filter/chord
   programs. (write model: `spec_write_model.md`)
10. Verify: build → `tools/find_first_divergence.py ORIG REBUILD --subtune N`;
    Mode-1 instruction-stream verdict. Multispeed (Q) → CIA per-play path.

---

## OPEN items index (each with its closing trace)
- **OPEN-1** self-relocating variant base — `siddump --pc-trace FILE $init $init+0x40`.
- **OPEN-2** packed order-list transpose zero-point / `$80` reservation — compare
  decoded transpose vs audible pitch on a known tune; check player disasm `sbc #$a0`.
- **OPEN-3** seqlo/seqhi rebase (BLOCKER) — `--pc-trace` init + disasm `nextnote`.
- **OPEN-4** packed per-row duration model — trace row advance vs frame count.
- **OPEN-5** packed pulse/filter row stride (2-B vs 4-B) — `--pc-trace` over update code.
- **OPEN-6** packed super-table stride + HR-AD byte (BLOCKER) — `seed_disassembly.py`
  + `effect_chain_profiler.py --register D405`.
- **OPEN-7** non-NP20.G4 variant table maps — `engine_fingerprint.py` bucketing.

## Leads to follow
1. **Close OPEN-3 + OPEN-6 first** — they are the two blockers. Both want a
   hand-annotated `pipelines/jch_newplayer/disassembly.s` of `Wild.sid` init($1040)
   + play($10BF). Generate via `tools/seed_disassembly.py`, annotate the seqlo/seqhi
   pointer setup and the `$1FCB` indexing. This is the next concrete task and
   follows the project's "full decompile before engine work" reflex.
2. **Fingerprint the 3611** (OPEN-7) with a reloc-invariant signature over the
   player code region (skip the `$xxCB` data). Expect a dominant NP20.G4 bucket
   (~88% already at init=$1000) — pick its longest tune as the migration canary.
3. **Acquire the actual NP20.G4 player SOURCE** (JCH released player sources; CSDb).
   CheeseCutter is NP21-derived; an NP20.G4 `.asm` would close OPEN-4/5/6 directly
   and resolve the 2-byte-vs-4-byte table stride without disasm guesswork. Search
   CSDb for "JCH NewPlayer 20.G4 source" / Vibrants player-source releases.
4. **Sibling reuse**: `pipelines/laxity_newplayer/` (313 tunes, NP21-based) shares
   this engine's semantics — coordinate the two so the shared composer config
   covers both (the version switches in §9 are the parametric knobs).
