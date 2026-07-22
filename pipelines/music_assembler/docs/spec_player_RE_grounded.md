<!--
provenance:
  source_url: (none — primary reverse-engineering of an HVSC binary)
  fetched_via: hand-disassembly of hvsc84/MUSICIANS/O/OPM/Sid_Slam.sid in this session
  fetch_date: 2026-06-13
  author: SIDfinity research session (Claude), grounded against the cadaver/sidid Music_Assembler/MC signature
  content_date: 2026-06-13
  reliability: HIGH for the bytes/offsets quoted (read directly from one canonical V1.0 binary);
               MEDIUM for the generalisation across all 6,351 HVSC members (only one member fully traced;
               offsets below are LOAD-RELATIVE and will shift per relocation/version — see "Relocation").
-->

# Music Assembler — GROUNDED player + packed-format RE

> **CORRECTION (2026-07-22, migration session).** Two table labels below are
> SWAPPED relative to this document's own disassembly, and one anchor rule does
> not generalise. Verified against 5,618 located HVSC members
> (`tools/masm_census.py`) — trust these over the text below:
>
> - **Seq pointer LO is `$C675`, HI is `$C669`** (this file's "Data tables"
>   row says the opposite). The disassembly here is right and the table is
>   wrong: `$C0A1` loads `$C675,Y` into `$FA`, and `($FA),Y` is little-endian,
>   so `$C675` supplies the LO byte. The doc's own dumps agree — `$C669` holds
>   `C5 C5 C4 C4 …` (page numbers = HI). Resolved correctly for 296/300
>   sampled members; 0 needed the swap.
> - **Do NOT derive the player base from the work block** (`seqnum - $8D`) or
>   from the signature (`sig - $91`). Both sit at build-dependent offsets. The
>   reliable anchor is init's fixed opening `A9 1F 8D 18 D4 A9 F0 8D 17 D4`
>   (`LDA #$1F/STA $D418/LDA #$F0/STA $D417`) at **base+$48**, which held on
>   every member measured. With that anchor the signature offset is `+$91` for
>   **all 5,618** located members — i.e. one dominant build, not the
>   `+$91/+$B5/+$70/+$191` spread README.md reports from the research sweep.
>
> **The SEQUENCE OPCODE MAP in this file and in `spec_player_jc64dis.md` has
> the two command ranges BACKWARDS.** Read off the player's own dispatch
> ($C0D2 `CMP #$A0` / `BCC $C0EC`), confirmed by decoding 5,455 members:
>
> | byte | docs say | **actually** |
> |---|---|---|
> | `$80..$9F` | HOLD | **PRESET**, id = byte & `$1F` (32 presets — `$C0EC` does `ASL A`×3 = id*8) |
> | `$A0..$FF` | `$A0..$AF` PRESET (low nibble), rest HOLD | **HOLD**, duration = byte & `$1F` |
>
> A PRESET byte carries NO duration: the player immediately re-reads the next
> byte and dispatches it as a note or a rest/hold ($C0F2). Worked example from
> this file's own seq 1 dump — `80 00 01 00 01 82 3C 01` is *preset 0 / note 0
> dur 1 / note 0 dur 1 / preset 2 / note $3C dur 1*, which only parses under
> the corrected map.
>
> The note's flags byte is **bit-flagged, not a 3-bit opcode**: bits 0-4 =
> duration, **bit 5 = SLIDE** (+2 bytes), **bit 7 = FILTER** (+2 bytes), bit 6
> = legato (no extra bytes). Filter wins when both are set ($C12C `BMI`
> precedes the bit-5 test). Verified: seq 2's `83 1A 87 63 08` = preset 3 /
> note $1A dur 7 with filter params `(63, 08)`.
>
> **The `$FD` orderlist sentinel is `$FD nn` = loop to ENTRY nn**, not a bare
> "restart from command", and it is a PLAYER VARIANT: 260 members replace the
> second `INY` of the orderlist step (base+$1A1) with a `JSR` to a stub that
> tests `CMP #$FD` and does `ASL A` (×2 for the 2-byte entries) into the
> orderlist position. Decode it only when that stub is present.
>
> Independent sanity check on the transpose semantics (high nibble, added to
> the note index): across all clean members the maximum note index after
> transpose is **95**, exactly the last entry of the 96-entry freq table.
>
> Implementation: `pipelines/music_assembler/locate.py` +
> `pipelines/music_assembler/extract/decode.py`; scale checks
> `tools/masm_census.py`, `tools/masm_decode_check.py`.

This is the crux deliverable: the packed runtime layout and the per-frame
`$D400-$D418` write model, derived by **disassembling a real HVSC member**
(`MUSICIANS/O/OPM/Sid_Slam.sid`, Music-Assembler V1.0, Dutch USA-Team, 1989,
load `$C000`). Everything here is read off the actual bytes, not the manual.
Addresses are **load-relative** (this member loads at `$C000`, so subtract
`$C000` for the offset-from-load).

The `cadaver/sidid` signature `Music_Assembler/MC`
(`BC ?? ?? C0 FE D0 09 BD ?? ?? 29 FE 9D ?? ?? 60 B9 ?? ?? 85`) is the
per-track **sequence-pointer fetch** routine — located here at `$C091`
(load+`$0091`). Verified present at load+`$0091` in Sid_Slam and at a
different offset in a packed multitune (Sub.sid), confirming it is the
recognition anchor.

## Entry points (confirmed)

| Vector | Address (this file) | Offset from load |
|--------|---------------------|------------------|
| IRQ install / cold start | `$C000` | **+$0000** |
| play (per-frame)          | `$C021` | **+$0021** |
| init (subtune select)     | `$C048` | **+$0048** |

These three offsets match the documented MASM player signature exactly and
should be stable across cleanly-relocated V1.0 members. (Packed/multi-loader
members such as `Sub.sid` carry a different PSID header load/init, but the
*player* entry offsets relative to the player base are the same.)

## Cold-start / IRQ bootstrap  ($C000)

```
$C000: SEI
$C001: JSR $C048          ; = init (selected subtune in A on entry? see init)
$C004: LDA #$18 / LDY #$C0
$C008: STA $0314 / STY $0315   ; IRQ vector -> $C018
$C00E: INX / STX $DC0E         ; CIA1 control
$C00F: STX $DC0E
$C013: STX $D01A               ; enable raster IRQ
$C016: CLI / RTS
; --- IRQ handler ---
$C018: INC $D019               ; ack raster IRQ
$C01B: JSR $C021               ; = play
$C01E: JMP $EA31               ; KERNAL IRQ exit
```

So when run as a standalone executable the player is a **raster-IRQ, single-
speed (50 Hz)** driver. Under PSID the host calls `play` ($C021) directly.

## play() — frame dispatch  ($C021)

```
$C021: LDX #$00              ; X = track index 0..2
$C023: DEC $C090            ; $C090 = MASTER SPEED COUNTER (song tempo divider)
$C026: BMI $C034            ; underflow -> advance the song this frame
$C028: JSR $C226            ; per-frame voice/effect update (track 0)  [SID writes]
$C02B: JSR $C225            ; (tracks 1,2 via fallthrough/loop)
$C02E: JMP $C225
        ...
$C034: LDA #$02 / STA $C090 ; reload speed = 2  (this == "song speed", set by F1-F8)
$C039: JSR ...              ; advance-track path
$C03F: INX / DEC $C08A,X    ; $C08A,X = per-track NOTE-DURATION counter
$C043: BMI $C091            ; when a track's note expires -> fetch next seq byte ($C091)
$C045: JMP $C226
```

Key state bytes (load-relative, 16-byte work block at `$C081..$C090`):
- `$C090` = **master speed counter**. Reload value `#$02` here = the song
  speed (manual: F1-F8). Decremented every play(); when it underflows the
  engine advances note durations and may fetch new sequence bytes.
- `$C08A,X` (x=0..2) = **per-track note-duration down-counter**. When it hits
  `BMI` the track pulls its next sequence command.
- `$C081,X` = per-track **sequence read position** (Y-index into the seq stream).
- `$C08D,X` = per-track **current sequence number** ($FE = stop).
- `$C084,X` = per-track gate/flags work byte (`AND #$FE` clears bit0 = gate off).

## Sequence-pointer fetch — the sidid signature  ($C091)

```
$C091: LDY $C08D,X          ; Y = track's current SEQUENCE NUMBER
$C094: CPY #$FE             ; $FE = "stop"
$C096: BNE $C0A1
$C098: LDA $C084,X / AND #$FE / STA $C084,X / RTS   ; stop: clear gate, done
$C0A1: LDA $C675,Y / STA $FA      ; SEQ POINTER TABLE (HI) @ $C675, indexed by seq#
$C0A6: LDA $C669,Y / STA $FB      ; SEQ POINTER TABLE (LO) @ $C669, indexed by seq#
$C0AB: LDY $C081,X                ; Y = read position within this sequence
$C0AE: LDA ($FA),Y                ; fetch next SEQUENCE-STREAM byte
$C0B0: BMI $C0D2                  ; byte >= $80  -> command class A
$C0B2: CMP #$60 / BCC $C0F9       ; byte <  $60  -> NOTE
$C0B6: AND #$1F / STA $C08A,X     ; byte $60..$7F -> set duration ($1F mask) ...
```

**This pins the packed sequence format.** A monophonic sequence is a byte
stream; the player dispatches each byte by value range:

| Byte range | Meaning (inferred from dispatch) |
|------------|----------------------------------|
| `$00..$5F` | **NOTE** (note index → freq-table lookup). Handler at `$C0F9`. |
| `$60..$7F` | **duration / repeat-class** command: `AND #$1F` → low 5 bits become the note-duration counter `$C08A,X` (matches manual durations `$00..$1F`). |
| `$80..$9F` | command class A (handler `$C0D2`, `CMP #$A0 / BCC` sub-split). `$C0D6: AND #$1F / STA $C08A,X` — another duration/length encoding. |
| `$A0..$FF` | command class A high sub-range (PRE/preset-select, slide, filter, hold/rest, loop — see note-handler trailer). |

The note handler ($C0F9) shows the per-note decode in detail:
```
$C0F9: STA $FC                 ; raw note byte
$C0FC: LDA $C0E6,X / LSR×4      ; track TRANSPOSE (high nibble of $C0E6,X)
$C104: ADC $FC                 ; transposed note = note + transpose
$C106: STA $C0C9,X
$C10B: TAY
$C10C: LDA $C437,Y / STA ...    ; FREQ LO TABLE @ $C437, indexed by note
$C115: LDA $C1C5,Y / STA ...    ; FREQ HI TABLE @ $C1C5, indexed by note
$C120: LDA ($FA),Y              ; following byte = note flags/duration
$C125: AND #$1F / STA $C08A,X   ; duration into the counter (low 5 bits)
$C12C: BMI $C150                ; bit7 set -> extra command
$C12E: AND #$20 / BEQ $C177     ; bit5 -> two extra param bytes (slide/filter LSB+MSB)
$C133: LDA ($FA),Y / STA $C147,X ; param 1 (e.g. slide fine / filter)
$C139: LDA ($FA),Y / STA $C14A,X ; param 2 (e.g. slide coarse / filter dir)
```

So a **note step** in the packed stream is:
`[note byte $00-$5F] [flags+duration byte]` and **optionally** two extra
parameter bytes when bit5 of the flags byte is set (slide LSB/MSB or filter
params — exactly the "two extra columns" the manual describes for portamento
and filter). bit7 of the flags byte routes to a further command ($C150).

## Per-frame SID write model — voice/effect update  ($C226)

This is the routine play() calls every frame per track (X=track). It is the
authoritative `$D4xx` write source.

```
$C226: LDY $C3D9,X             ; Y = preset/instrument index for this track*8
$C235: LDA $C681,Y / STA $FA   ; PRESET TABLE base @ $C681 (8 bytes/preset)
$C23A: LDA $C682,Y
$C23D: LDY $C0C6,X             ; Y2 = VOICE REGISTER BASE ($00 / $07 / $0E)
$C240: STA $D406,Y2            ; -> SR    (preset+1)
$C243: LDA $FA / STA $D405,Y2  ; -> AD    (preset+0)
$C248: LDA $C084,X / AND #$FE
$C24D: STA $D404,Y2            ; -> CONTROL/waveform (gate cleared this step)
$C252: LDA $C683,Y / STA $C084,X        ; preset+2 = WAVEFORM byte (stashed -> $D404 later)
$C258: LDA $C684,Y / STA $C3DC,X/$C3DF,X ; preset+3 = pulse-rate / pulse-effect
$C277: LDA $C686,Y / LSR×3 / STA $C14D,X ; preset+5 -> vibrato or arp-link field
$C288: LDA $C688,Y / STA $FD,X           ; preset+7
$C2A4: STA $D416               ; FILTER CUTOFF HIGH (only $D416 used; $D415 unused)
```

Confirmed static `$D4xx` store sites in this player (full linear scan):

| Register | How written | Meaning |
|----------|-------------|---------|
| `$D400,Y` `$D401,Y` | `STA abs,Y` (Y2 = voice*7) | freq lo / hi, per-voice |
| `$D402,Y` `$D403,Y` | `STA abs,Y` | pulse width lo / hi, per-voice |
| `$D404,Y` | `STA abs,Y` | control/waveform+gate, per-voice |
| `$D405,Y` | `STA abs,Y` | attack/decay, per-voice |
| `$D406,Y` | `STA abs,Y` | sustain/release, per-voice |
| `$D416`   | `STA abs` (×1) | filter cutoff **high byte only** |
| `$D417`   | `STA abs` (×3) | resonance + filter routing (init `#$F0`) |
| `$D418`   | `STA abs` (×1) | mode/volume (init `#$1F` = vol $F + LP on) |

**Per-voice writes are all `,Y`-indexed with the voice base in `$C0C6,X`
( = `$00`, `$07`, `$0E` ).** This is the single most important structural
fact for reproducing the write stream: ONE shared code path emits all three
voices' `$D400..$D406` by re-loading Y2. The global filter regs
(`$D416/$D417/$D418`) are written once with absolute `STA`. `$D415` (filter
cutoff LO) is **never written** — MASM uses only the coarse high cutoff byte,
consistent with the manual's single-digit (0-F) filter frequency.

Init writes (fixed, every subtune): `$D418 = $1F`, `$D417 = $F0`. Note `$D417`
low nibble (filter-voice routing) is then derived: `AND #$0F / STA $C262`
($C262 = the track index that owns the filter — matches manual "filter applies
to triggering track and all lower tracks").

## Data tables (located in this member, load-relative)

| Table | Address | Stride / size | Content (verbatim sample) |
|-------|---------|---------------|---------------------------|
| Freq LO | `$C437` | 1 B/note | `16 27 38 4B 5F 73 8A A1 BA D4 F0 0E 2D 4E 71 96 ...` |
| Freq HI | `$C1C5` | 1 B/note | `01 01 01 01 01 01 01 01 01 01 01 02 02 02 02 02 ...` (octave doubling — standard C64 PAL note table) |
| Preset table | `$C681` | 8 B/preset | `0E 08 09 08 84 0F 60 31` (preset 0), `0E 08 09 08 00 00 00 02` (preset 1), `0E 07 09 08 00 00 00 03` (preset 2), `0F 07 41 06 70 42 20 30` (preset 3) |
| Seq ptr LO | `$C669` | 1 B/seq | `C5 C5 C4 C4 C5 C5 C5 C5 C5 C5 C5 00 ...` |
| Seq ptr HI | `$C675` | 1 B/seq | `BD 29 C1 E1 15 54 03 81 BF A7 93 ...` |
| Track-init ptr LO | `$C4B9` | 3 (one/track) | `05 E8 E3` |
| Track-init ptr HI | `$C4BC` | 3 | `C6 C5 C5` |

### Preset (instrument) byte layout — INFERRED from the $C226 reads

The voice-update routine indexes the preset table with Y = preset*8 and reads
offsets +0..+7. Mapping read site → SID write gives:

| Preset byte | Read at | Destination | Manual field |
|-------------|---------|-------------|--------------|
| +0 | `$C681,Y` → `$FA` → `$D405` | attack/decay | **AD** |
| +1 | `$C682,Y` → `$D406` | sustain/release | **SR** |
| +2 | `$C683,Y` → `$C084,X` → `$D404` | waveform/control byte | **Waveform** |
| +3 | `$C684,Y` → `$C3DC/$C3DF` | pulse rate / pulse-effect work | **Pulse rate (lo/hi nibbles) + pulse effect** |
| +4 | (not read in this trace window) | — | likely pulse-effect params / vibrato |
| +5 | `$C686,Y` → `LSR×3` → `$C14D` | vibrato or arp-link select | **Vibrato / arpeggio link** |
| +6 | (not read here) | — | likely vibrato params |
| +7 | `$C688,Y` → `$FD,X` | per-voice work init | **arpeggio link / vibrato** |

Cross-check with preset 0 bytes `0E 08 09 08 84 0F 60 31`:
- +0 `0E` AD, +1 `08` SR → reasonable ADSR.
- +2 `09` waveform = `$09` → matches the manual's "$09/$08 = oscillator
  disable / hard-reset" trick described in *Resetting Oscillators*.
- +3 `08` = pulse rate `$08` = the manual's "100% pure pulse" value.

This is strong confirmation the 8-byte preset maps directly to the manual's
documented fields. The exact assignment of +4/+6 (pulse-effect sub-params vs
vibrato delay/speed/level) needs one more pass through `$C290`+ (the
pulse/vibrato/filter effect routines, partially captured: `$C299: DEC $C296`
is a per-frame filter-step counter, `$C29F: ADC #$F0` then `STA $D416` is the
filter cutoff ramp).

## Relocation

V1.0 is a **self-relocating save**: the editor patches every absolute address
when you choose a load address $0400-$FF00. Consequences for parsing 6,351
binaries:
- The entry offsets (+$00/+$21/+$48) are stable; the **internal table
  addresses are NOT** — `$C669/$C675/$C681/$C437/$C1C5` above are
  `load+$0669` etc. for a `$C000` build and shift with the chosen base.
- To find the tables generically: locate the signature ($C091-equivalent) to
  anchor the player base, then follow the absolute operands in the
  sequence-fetch ($C0A1: `LDA tableHI,Y` / `LDA tableLO,Y`) and voice-update
  ($C235: `LDA presetTable,Y`) — those operands give the live table addresses
  for ANY relocation. This is the reloc-invariant extraction hook.
- Expect version variants: HVSC also contains **V1.1 / V1.4 by Triad** (CSDb
  #27470 / #27472) and the VoiceTracker derivative — fingerprint before
  assuming this exact layout. Build a fingerprint set akin to the FC
  standard-player census (`project_fc_fingerprint_and_standard`).
