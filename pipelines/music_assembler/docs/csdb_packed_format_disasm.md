---
source_url: local: song_confuzion_C000.prg, song_action_biker_5000.prg, song_hello_monty_C000.prg, song_dutch_usa_6800.prg, standalone_player_2900.prg, presets_only_4300.prg (extracted from CSDb #94388 disk images)
fetched_via: local disassembly 2026-06-13 (Python 6502 disassembler over the vendored song PRGs)
fetch_date: 2026-06-13
author: SIDfinity research session (disasm of DUSAT V1.0 player output)
content_date: player code = 1989 Music-Assembler V1.0
reliability: primary — disassembled directly from real song binaries (ground truth), but PARTIAL (entry points + decode loop + table layout mapped; full per-effect runtime not yet traced)
---

# Music Assembler — the PACKED assembled-output format (first RE pass)

This is the priority-1 gap from `research.md`: the binary that the editor
"assembles" and the player "disassembles while playing." Disassembled from
six real specimens (`song_*.prg`, `standalone_player_2900.prg`,
`presets_only_4300.prg`) extracted from the CSDb #94388 disks. This is a
**first structural pass**, not a complete RE — enough to seed a
`disassembly.s` + decoder, with the exact decode opcodes quoted below.

## Specimen set (all DUSAT V1.0 player)

| file | load base | size | notes |
|---|---|---|---|
| `song_confuzion_C000.prg`    | $C000 | 2567 | worked example below |
| `song_hello_monty_C000.prg`  | $C000 | 3071 | |
| `song_action_biker_5000.prg` | $5000 | 2711 | different base → relocation test |
| `song_dutch_usa_6800.prg`    | $6800 | 1936 | smallest |
| `standalone_player_2900.prg` | $2900 | 2944 | JMP-table entry variant |
| `presets_only_4300.prg`      | $4300 |  768 | the `p.` format |

## Relocation-invariant landmarks (verified across all 4 songs)

Offsets are **from the load base** (= `SYS base`). These are stable regardless
of base address ($5000/$6800/$C000/$2900 all identical):

| offset | role | first bytes |
|---|---|---|
| `base+$00` | IRQ installer (`s.` files) | `78 20 48 <hh> A9 18` = SEI / JSR init / LDA #$18 |
| `base+$18` | IRQ handler | `EE 19 D0` (ACK $D019) / `JSR base+$21` / `JMP $EA31` |
| `base+$21` | **play** (call per frame) | `A2 00 CE 90 <hh> 30` = LDX #0 / DEC speedctr / BMI |
| `base+$48` | **init** | `A9 1F 8D 18 D4 A9 F0 8D 17 D4` |
| `base+$91` | per-voice seq-fetch (the sidid sig) | `BC 8D <hh> C0 FE D0 09 BD 84 <hh> 29 FE 9D 84 <hh> 60` |

- The `s.<name>` files install a raster IRQ at $0314/$0315 → `base+$18`, which
  ACKs $D019 and calls play at `base+$21`. (Confuzion: `STA $0314 / STY $0315 /
  STX $DC0E / STX $D01A`.)
- The **standalone `MUSIC` file** replaces `base+$00` with a **2-entry JMP
  table**: `4C 48 29 (JMP init) / 4C 21 29 (JMP play)`. Same player body. This
  is a packaging variant — a decompiler must detect both entry styles.

## init (`base+$48`) — the universal-reset + chip priming

```
base+$48: LDA #$1F ; STA $D418      ; volume $F + LP filter mode on
          LDA #$F0 ; STA $D417      ; resonance $F + filter-routing nibble
          AND #$0F ; STA <savedrouting>
          LDX #$0F : <loop> STA tbl,X ; DEX ; BPL  ; clear 16-byte state block
          LDX #$02 ...               ; per-voice (3) init follows
```
USF mapping: this is a fixed reset ($D418=$1F, $D417=$F0) + a global LP filter
already enabled — fits the `init.sid` typed-priming model (master_vol=$F,
filter LP on). NOT a verbatim init prefix to reproduce.

## Per-frame play model (`base+$21`)

```
base+$21: LDX #$00
          DEC <speedctr@base+$90>    ; song speed countdown (F1..F8 = tempo)
          BMI <reload+advance>       ; when it underflows: advance song step
          ... JSR effects for each of 3 voices ...
```
Then per voice X∈{0,1,2}:
```
          DEC <durcnt@base+$8A,X>    ; note-duration countdown
          BMI <fetch next seq step for voice X>
          JMP <run continuous effects>   ; vibrato/pulse/slide/filter/arp tick
```
So: a global speed counter gates song-position advance; each voice has its own
duration counter; when a voice's counter underflows it fetches the next
sequence step. **This matches the manual's "duration counts from 0" model.**

## Per-voice state block (indexed by X, parallel arrays)

From the decode (Confuzion addresses; all are `base`-relative arrays of 3):

| array @ (Confuzion) | base-rel | meaning |
|---|---|---|
| `$C081,X` | +$81 | sequence read-index Y (position within current seq) |
| `$C084,X` | +$84 | live waveform/control byte (gate in bit0; `AND #$FE` clears gate) |
| `$C08A,X` | +$8A | note-duration countdown |
| `$C08D,X` | +$8D | (arp/seq sub-state; `CPY #$FE` = arp-stop test) |
| `$C090`   | +$90 | global song-speed counter (shared, not per-voice) |
| `$C031,X` | +$31 | per-voice flag set/cleared on note start ($FE/$FF) |

## Sequence-pointer indirection

Per-voice the player loads a 16-bit pointer into zero-page `$FA/$FB` from
**split lo/hi tables**, then reads the packed sequence with `LDA ($FA),Y`:
```
base+$91: LDY <seqstate,X>
          CPY #$FE → if FE: clear gate bit (AND #$FE), RTS   ; arp/seq stop
          LDA <seqptr_hi_table>,Y → $FB                       ; @ +$96F in Confuzion
          LDA <seqptr_lo_table>,Y → $FA                       ; @ +$98F in Confuzion
          LDY <seqpos,X> ; LDA ($FA),Y                        ; read packed byte
```
- Two parallel tables, **HI table at +$96F, LO table at +$98F** (0x20 apart),
  one entry per sequence (≤ $FD seqs). They point into the packed sequence
  stream. (Confuzion seq#0 → $C567.)
- The track/orderlist (which seq plays on which voice, transpose, repeat) is a
  separate higher-level table consumed at the speed-counter-underflow branch
  (not yet fully traced — TODO).

## Packed SEQUENCE byte stream — opcode decode (the core of the format)

After fetching `b = ($FA),Y`, the player at +$B0 onward dispatches:
```
LDA ($FA),Y
BMI <special $80+>          ; bit7 set
CMP #$60 ; BCC <note $00..$5F>  ; values < $60 = a NOTE
<else $60..$7F>             ; preset/PRE-style command range
  AND #$1F → durcnt ; LDA #$FE → flag ; JSR ; ...
```
Then for a NOTE it reads a **second "flags+duration" byte** and dispatches its
bits (Confuzion $C120..$C16E):
```
LDA ($FA),Y → store@+$141,X           ; raw flag/dur byte
AND #$1F → durcnt@+$8A,X               ; low 5 bits = duration (stored+1 sixteenths)
LDA ($FA),Y
  BMI  → FILTER command  (bit7)        ; see below
  AND #$20 ; BEQ skip → SLIDE command  (bit5)
```
- **SLIDE (bit5)**: reads **2 more bytes** = LSB(fine), MSB(coarse) → +$147,X /
  +$14A,X. (Matches the manual's 2 slide columns; downward = MSB $FF/$FE.)
- **FILTER (bit7)**: reads filter param byte → `AND #$0F` cutoff start,
  `ASL ; SEC ; SBC #$10` scales it; reads a frame-count byte; if 0 → restore
  `$D417 = #$F0`, else set sweep + `STA $D417`. (Matches the manual's
  cutoff-nibble + direction-nibble + frame-count.)
- **End-of-sequence**: after the step, `INY ; LDA ($FA),Y ; CMP #$FF ; BNE` —
  `$FF` byte terminates the sequence (→ advance the track/orderlist; `DEC` a
  repeat counter at +$E9,X). `$FE` is the arp/seq-stop sentinel.

### Working opcode summary (to refine)
| byte b | meaning |
|---|---|
| `$00`–`$5F` | NOTE (note index; freq via tables below), followed by flag/dur byte |
| `$60`–`$7F` | preset/PRE-select-ish command (sets durcnt + flag, more tracing needed) |
| `$80`–`$FD` | special command (bit7) — note the flag/dur byte itself reuses bit7=FILTER, bit5=SLIDE |
| `$FE` | stop (arpeggio/sequence sentinel) |
| `$FF` | end-of-sequence (advance orderlist / decrement repeat) |

(The exact $60–$7F vs $80+ command taxonomy needs one more trace pass — the
flag-byte's bit5/bit7 reuse is distinct from the primary opcode byte's ranges.)

## Frequency tables (in-binary, semitone-spaced)

Two parallel note→freq tables referenced as `,Y`:
- **freq LO** at Confuzion `$C437` (`base+$437`), **freq HI** at `$C1C5`
  (`base+$1C5`). Note index from the seq stream (0..$5F) plus track transpose +
  arpeggio offset indexes these. A second small table near `base+$200` holds
  ascending values `20 22 24 27 29 2B 2E 31 ...` (a per-semitone delta /
  freq-derivation table). USF needs none of these tables — note → USF note is
  by table-index, freq is engine-derived.

## PRESET records — 8 bytes each (the `p.` format too)

Visible at Confuzion `$C9AF` onward as 8-byte rows (e.g. `35 48 41 02 F0 42 1C
50`). The play code reads preset fields with `,Y` (Y = preset#×8-ish) and writes
$D405/$D406 (ADSR) and $D404 (control). The `presets_only_4300.prg` (768 bytes,
load $4300) is the standalone 32-preset + 16-arp bank — the cleanest specimen
to map the exact 8-byte field order against the manual's
ADSR/wave/pulse/vibrato/arp-link layout. **TODO:** pin the 8-byte field order
(manual gives the *fields*; the byte order in the record is still to confirm by
diffing several presets).

## Open items for the next RE pass

1. Map the **8-byte preset record** field order (use `presets_only_4300.prg`).
2. Trace the **track/orderlist** structure (seq#, transpose, repeat) at the
   speed-underflow branch (`base+$34` region).
3. Pin the **$60–$7F vs $80+** primary-opcode taxonomy (PRE / hold / rest /
   no-trigger note) vs. the flag-byte bits.
4. Trace the **arpeggio** runtime (the +$8D / `CPY #$FE` path) and the
   per-frame wave/note-offset/filter application.
5. Confirm **pulse-rate nibble-swap** and **vibrate** in the continuous-effects
   tick.
6. Diff the **Triad V1.1/V1.3/V1.4** player bodies (editors vendored as
   `editor_v1.*_triad_0801.prg`) — King Fisher continued V1.4; the write-model
   may differ. The packed sequence sig still appears in song output, but init /
   effect ordering may drift across versions.
