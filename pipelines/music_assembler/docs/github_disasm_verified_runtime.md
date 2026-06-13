---
source_url: https://github.com/WilfredC64/player-id (signature) + direct disassembly of HVSC MUSICIANS/O/OPM/Sid_Slam.sid, Fantjes_Beat.sid, MUSICIANS/O/Ozone/Power_Wars.sid
fetched_via: direct
fetch_date: 2026-06-13
author: signature: WilfredC64/cadaver; disassembly: this session (minimal 6502 disasm in tmp/dis6502.py) cross-checked against the sidid signature
reliability: primary=source code (the running player bytes pulled from HVSC binaries; the sidid signature is a verbatim fragment of this code, so the two corroborate)
---

# Music Assembler — verified player runtime + per-frame SID write model

This is what the player ACTUALLY does, decoded straight out of three HVSC
binaries. It cross-checks against the sidid signature (the signature is a
verbatim slice of routine `$xx91`). All addresses below are for the
Sid_Slam.sid base $C000; subtract $C000 to get load-relative offsets — the
SAME offsets hold in every member (the player is position-independent data
laid out at fixed load-relative offsets).

NOTE: this is RE done as part of GitHub-cluster research to PROVE the
open-source signature maps onto a real, decodable format. It is not a
full disassembly.s — but the offsets are reusable directly.

## The two layout variants are ONE engine (priority #3: version variants)

Load-relative entry-offset census across all on-disk MA members in hvsc84.db:

| init off | play off | count | meaning |
|----------|----------|-------|---------|
| +$0000   | +$0003   | 3305  | **Variant B** — JMP trampoline + SYS/IRQ wrapper prepended |
| +$0048   | +$0021   | 2605  | **Variant A** — manual's classic layout, player core at base |
| +$0027   | +$0000   | 116   | minor reloc/wrapper variant |
| +$0048   | +$001c   | 43    | minor variant |
| +$0000   | +$0012   | 33    | wrapper variant |
| +$0028   | +$0001   | 18    | minor variant |
| +$0041   | +$007a   | 16    | minor variant |

**Variant A** (e.g. OPM/Sid_Slam, OPM/Fantjes_Beat — base $C000): the player
core starts at the base. play=base+$21, init=base+$48.

**Variant B** (e.g. Ozone/Power_Wars — base $1000): IDENTICAL core, but a
6-byte JMP table + a standalone IRQ installer is prepended, and PSID
init/play point at the trampolines:

```
$1000: 4c 48 10   JMP $1048   ; init trampoline  -> real init (= base+$48)
$1003: 4c 21 10   JMP $1021   ; play trampoline  -> real play (= base+$21)
$1006: 78         SEI         ; <-- the "SYS base" standalone entry (manual)
$1007: 20 00 10   JSR $1000   ; init
$100a: a9 ff      LDA #$ff
$100c: cd 12 d0   CMP $d012   ; wait for raster line $FF
$100f: d0 fb      BNE $100c
$1011: 20 03 10   JSR $1003   ; play once
$1014: ad 01 dc   LDA $dc01
$1017: 29 10      AND #$10    ; test fire button (joy2)
$1019: d0 ef      BNE $100a   ; loop until pressed
$101b: 8d 18 d4   STA $d418   ; silence ($d418=0) on exit
$101e: 58         CLI
$101f: 60         RTS
```

CONSEQUENCE for the decoder: the MA primary sidid signature
(`BC ?? ?? C0 FE D0 09 ...`) lands at the SAME body offset (145 bytes past the
real player base) in BOTH variants. **A single decoder handles all variants by
locating the signature, deriving `base = sig_addr - 145 - $91`... — simpler:
the real player base is `init - $48` in Variant A and `init_trampoline_target
- $48` in Variant B; either way the play core is at `base+$21`, the signature
routine at `base+$91`.** Treat the trampoline+IRQ-installer as an outer shell
to strip; decode the inner core uniformly.

## init (base+$48) — chip priming for USF init.sid

```
$c048: a9 1f      LDA #$1f
$c04a: 8d 18 d4   STA $d418     ; $D418 = $1F  -> master vol $F + LOW-PASS filter on
$c04d: a9 f0      LDA #$f0
$c04f: 8d 17 d4   STA $d417     ; $D417 = $F0  -> filter resonance hi-nibble, no voices routed yet
$c052: 29 0f      AND #$0f
$c054: 8d 62 c2   STA $c262     ; stash low nibble (filter routing accumulator)
$c057: a2 0f      LDX #$0f
$c059: 9d 81 c0   STA $c081,X   ; clear 16-byte per-voice state block $c081..$c090
$c05c: ca         DEX
$c05d: 10 fa      BPL $c059
$c05f: a2 02      LDX #$02      ; for each of 3 voices (X=2,1,0):
$c061: bd b9 c4   LDA $c4b9,X   ;   set up ($fa)= track pointer from $c4b9/$c4bc tables
$c064: 85 fa      STA $fa
$c066: bd bc c4   LDA $c4bc,X
$c069: 85 fb      STA $fb
$c06b: a0 00      LDY #$00
$c06d: b1 fa      LDA ($fa),Y   ;   first track byte -> sequence number ($c08d,X)
$c06f: 9d 8d c0   STA $c08d,X
$c072: c8         INY
$c073: b1 fa      LDA ($fa),Y   ;   second track byte -> transpose ($c0e6,X)
$c075: 9d e6 c0   STA $c0e6,X
$c078: 29 0f      AND #$0f
$c07a: 9d e9 c0   STA $c0e9,X   ;   low nibble -> repeat counter ($c0e9,X)
$c07d: ca         DEX
$c07e: 10 e1      BPL $c061
$c080: 60         RTS
```

USF init.sid for MA: `master_vol=$F`, `filter { low_pass, resonance hi=$F }`
(i.e. `$D418=$1F`, `$D417=$F0`). These two writes are constant across the
family (`A9 F0 8D 17 D4 29 0F` is literally the **Music_Mixer sidid signature**
— it is the shared MA init).

## play (base+$21) — frame dispatch + the speed counter

```
$c021: a2 00      LDX #$00
$c023: ce 90 c0   DEC $c090     ; master speed counter
$c026: 30 0c      BMI $c034     ; underflow -> reload tempo + step sequences
$c028: 20 26 c2   JSR $c226     ; voice 0 frame update (no step)
$c02b: 20 25 c2   JSR $c225     ; voice 1 (entry does INX first)
$c02e: 4c 25 c2   JMP $c225     ; voice 2
$c034: a9 02      LDA #$02       ; tempo reload value (= speed; here 2)
$c036: 8d 90 c0   STA $c090
$c039: 20 40 c0   JSR $c040     ; voice 0 step+update
$c03c: 20 3f c0   JSR $c03f     ; voice 1
$c03f: e8         INX
$c040: de 8a c0   DEC $c08a,X   ; per-voice duration counter
$c043: 30 4c      BMI $c091     ; expired -> pull next sequence command (the sig routine)
$c045: 4c 26 c2   JMP $c226     ; not expired -> just refresh SID for this voice
```

- `$c090` = global speed/tempo counter; reload value ($02 here) is the song
  tempo. Multispeed members (DoubleTracker / Ten_Tracker) drive play() multiple
  times per frame via CIA / multiple IRQs — expect PSID `speed` bit set there
  (CLAUDE.md Trap C / CIA per-play verdict applies).
- `$c08a,X` = per-voice 16th-note duration counter.

## The sidid signature routine (base+$91) — sequence-command fetch + dispatch

This is the routine the canonical `Music_Assembler` signature is carved from:

```
$c091: bc 8d c0   LDY $c08d,X   ; Y = current sequence number for this voice  ]
$c094: c0 fe      CPY #$fe      ; $FE sentinel?                                | -- SIGNATURE
$c096: d0 09      BNE $c0a1     ;                                              |    BC ?? ?? C0 FE D0 09
$c098: bd 84 c0   LDA $c084,X   ; (stop) load the voice ctrl byte             |    BD ?? ??
$c09b: 29 fe      AND #$fe      ; clear bit0 (gate-retrigger flag)            |    29 FE
$c09d: 9d 84 c0   STA $c084,X   ;                                            |    9D ?? ??
$c0a0: 60         RTS           ;                                            |    60
$c0a1: b9 75 c6   LDA $c675,Y   ; seq-pointer LO table indexed by seq number  ]    B9 ?? ?? 85
$c0a4: 85 fa      STA $fa
$c0a6: b9 69 c6   LDA $c669,Y   ; seq-pointer HI table
$c0a9: 85 fb      STA $fb
$c0ab: bc 81 c0   LDY $c081,X   ; Y = byte offset within the sequence
$c0ae: b1 fa      LDA ($fa),Y   ; <-- READ THE PACKED SEQUENCE BYTE
$c0b0: 30 20      BMI $c0d2     ; bit7 set ($80-$FF) -> command class 2
$c0b2: c9 60      CMP #$60      ; < $60 ?
$c0b4: 90 43      BCC $c0f9     ;   -> NOTE (value $00-$5F = note + duration code)
$c0b6: 29 1f      AND #$1f      ; $60-$7F: AND #$1F -> duration/length value
$c0b8: 9d 8a c0   STA $c08a,X   ;   store as duration counter
$c0bb: a9 fe      LDA #$fe
$c0bd: 9d 31 c0   STA $c031,X
$c0c0: 20 98 c0   JSR $c098     ; clear gate bit0
$c0c3: 4c 87 c1   JMP $c187     ; advance to next sequence byte
$c0d2: c9 a0      CMP #$a0      ; $80-$9F vs $A0-$FF split (command class 2)
$c0d4: 90 16      BCC $c0ec
$c0d6: 29 1f      AND #$1f      ; another duration/param mask
$c0d8: 9d 8a c0   STA $c08a,X
$c0db: b0 e6      BCS $c0c3
```

### Packed sequence byte encoding (decoded from the dispatch)

| byte value  | class          | handling |
|-------------|----------------|----------|
| `$00–$5F`   | **note + duration** | falls to $c0f9 note path; the value indexes a note→frame-duration table at `$c1c5` (see below) |
| `$60–$7F`   | duration/length set | `AND #$1F` -> duration counter `$c08a,X`; sets a $FE marker; continues |
| `$80–$9F`   | command class 2a | `AND #$1F` param at $c0ec |
| `$A0–$FF`   | command class 2b | `AND #$1F` -> duration counter; continues |
| `$FE`       | sequence STOP sentinel (tested at $c094, $c0bb) | clears gate, RTS |
| `$FF`       | sequence-end / loop sentinel (handled in $c187) | pull next track entry |
| `$FD`       | third sentinel (per VoiceTracker variant `C9 FD F0 01 60`) | return |

The note→duration lookup table lives at `$c1c5` (right after the $c187
routine). Decoded bytes confirm an ascending duration map:
`01 01 01 01 01 01 01 02 02 02 ... 0a 0b 0c 0d 0d 0e 0f 10 11 12 13 14 15 17 18 1a 1b 1d 1f 20`
— i.e. note-value -> number of 16th-frames it sustains (the manual's
"$00=16th .. $1F=double-whole" expanded by an internal table).

## Track-advance / $FF-loop routine (base+$187)

When a sequence hits `$FF`, this pulls the next entry from the voice's TRACK
(orderlist) and decrements a repeat counter:

```
$c187: c8         INY
$c188: b1 fa      LDA ($fa),Y
$c18a: c9 ff      CMP #$ff       ; sequence ended?
$c18c: d0 32      BNE $c1c0
$c18e: de e9 c0   DEC $c0e9,X    ; repeat counter--
$c191: 10 2b      BPL $c1be      ;   still repeating -> restart same sequence
$c193: bd b9 c4   LDA $c4b9,X    ; else reload TRACK pointer ($fa) from $c4b9/$c4bc
$c196: 85 fa      STA $fa
$c198: bd bc c4   LDA $c4bc,X
$c19b: 85 fb      STA $fb
$c19d: bc 87 c0   LDY $c087,X    ; Y = current track position
$c1a0: c8 c8      INY INY        ; track entries are 2 bytes (seqnum, transpose)
$c1a2: b1 fa      LDA ($fa),Y
$c1a4: c9 ff      CMP #$ff       ; track end?
$c1a6: d0 02      BNE $c1aa
$c1a8: a0 00      LDY #$00       ;   -> loop track to start ($FF = track loop)
$c1aa: 98         TYA
$c1ab: 9d 87 c0   STA $c087,X    ; save track position
$c1ae: b1 fa      LDA ($fa),Y    ; new sequence number
$c1b0: 9d 8d c0   STA $c08d,X    ;   -> $c08d,X
$c1b3: c8         INY
$c1b4: b1 fa      LDA ($fa),Y    ; transpose byte
$c1b6: 9d e6 c0   STA $c0e6,X    ;   -> $c0e6,X (full byte = transpose)
$c1b9: 29 0f      AND #$0f       ;   low nibble = repeat count
$c1bb: 9d e9 c0   STA $c0e9,X    ;   -> $c0e9,X
$c1be: a0 00      LDY #$00
$c1c0: 98         TYA
$c1c1: 9d 81 c0   STA $c081,X    ; reset sequence byte offset
$c1c4: 60         RTS
```

Confirms the manual's TRACK format: 2-byte entries (sequence number,
transpose+repeat), `$FF` = track loop, repeat count in the transpose byte's low
nibble.

## Per-frame SID write routine (base+$226) — THE WRITE MODEL (priority #2)

This runs for every voice every frame and IS the $D400-block emitter:

```
$c225: e8         INX            ; (entry for voices 1,2)
$c226: bc d9 c3   LDY $c3d9,X    ; Y = current PRESET/wave index for this voice
$c229: 84 fc      STY $fc
$c22b: bd 41 c1   LDA $c141,X
$c22e: 29 40      AND #$40       ; bit6 = "voice held / skip update" flag
$c230: d0 5e      BNE $c290      ;   if set, branch past write
$c232: 9d 44 c1   STA $c144,X
$c235: b9 81 c6   LDA $c681,Y    ; preset table column @ $c681  -> freq/pulse LO
$c238: 85 fa      STA $fa
$c23a: b9 82 c6   LDA $c682,Y    ; preset table column @ $c682  -> hi byte
$c23d: bc c6 c0   LDY $c0c6,X    ; Y = voice register offset (0 / 7 / 14)
$c240: 99 06 d4   STA $d406,Y    ; $D406+voff = SUSTAIN/RELEASE  (SR)
$c243: a5 fa      LDA $fa
$c245: 99 05 d4   STA $d405,Y    ; $D405+voff = ATTACK/DECAY     (AD)
$c248: bd 84 c0   LDA $c084,X    ; per-voice control byte
$c24b: 29 fe      AND #$fe       ; <-- clear gate-retrigger bit0 (the AND #$FE)
$c24d: 99 04 d4   STA $d404,Y    ; $D404+voff = CONTROL/WAVEFORM (gate/wave)
$c250: a4 fc      LDY $fc
$c252: b9 83 c6   LDA $c683,Y    ; preset column @ $c683
$c255: 9d 84 c0   STA $c084,X    ;   -> next-frame control byte
$c258: b9 84 c6   LDA $c684,Y    ; preset column @ $c684
$c25b: 9d dc c3   STA $c3dc,X
$c25e: 9d df c3   STA $c3df,X
...
```

Write-model summary per voice per frame (voff = `$c0c6,X` = $00/$07/$0E):
- `$D405+voff` = AD (attack/decay)
- `$D406+voff` = SR (sustain/release)
- `$D404+voff` = control/waveform, **bit0 (gate-retrigger) masked off after
  use** — this is the canonical MA quirk the signature captures (`AND #$FE`).
- Frequency ($D400/1+voff) and pulse-width ($D402/3+voff) are written by the
  arpeggio/vibrato/pulse path (the $c290 branch and the wave-table walk), not
  shown here — that path reads the preset's vibrato/pulse/arp parameters and is
  the next thing to disassemble for a complete writelog reproduction.

### Preset table layout (the packed instrument format)

Presets are stored **column-major** (NOT 8 contiguous bytes per preset).
Indexed by a single Y = preset/wave-step index, the columns seen so far:
`$c681[Y]`=AD, `$c682[Y]`=SR, `$c683[Y]`=control/next, `$c684[Y]`=arp/next-step
link. With the manual's "32 presets × 8 bytes" + "16 arpeggios", the full
column set spans 8 columns of 32+ entries each. Because arpeggio steps and
presets are walked through the SAME `LDA col,Y` mechanism, **the player merges
the preset and arpeggio tables into one indexed wavetable** — Y advances each
frame through arp steps, with $FF=loop / $FE=stop sentinels (matches the
manual's arpeggio loop/stop bytes).

## Open RE items (to finish a full writelog reproduction)

1. The $c290 branch (vibrato + pulse-width + filter sweep) — writes $D400/1
   (freq) and $D402/3 (PW) and $D415/6 (filter cutoff). Not yet disassembled.
2. Note value -> SID frequency: note path at $c0f9 + a frequency table (the
   `B9 ?? ?? 9D ?? ??` block in the Dutch-USA_Team/86 signature looks like the
   freq-table copy loop).
3. Multispeed dispatch for DoubleTracker / Ten_Tracker (CIA / N×play per frame).
