---
source_url: https://github.com/realdmx/c64_6581_sid_players
fetched_via: direct
fetch_date: 2026-06-03
author: realdmx (dmx87) — converted from TurboAssembler originals
content_date: 1988-1989 (original Deenen / Tel / Bjerregaard code)
reliability: primary (reverse-engineered + commented)
---

# MoN driver disassembly notes (realdmx C64 SID players repo)

This repo contains the actual **TurboAssembler source** for the MoN
driver in three variants (Deenen, Tel, Bjerregaard), converted to
ACME by dmx87. **This is the architectural parent of Future Composer
— FC V1 was Granberg's editor wrapped around exactly this driver.**

Files in repo (all `.asm`):
- `Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm`
- `Deenen_Charles_MON/Deenen_Charles_Test_Tune.asm`
- `Deenen_Charles_MON/Deenen_Charles_Test_Tune2.asm`
  (header `"Maniacs of Noise music player (C) Scoop designs ltd. / m.o.n."`)
- `Deenen_Charles_MON/Deenen_Charles_SFX_Player.asm`
  (header `"M.O.N. SFXplayer (C) Scoop ltd. 1989"`)
- `Bjerregaard_Johannes_MON/Bjerregaard_J_James_Bond_3.asm`
- `Bjerregaard_Johannes_MON/Bjerregaard_J_Myth.asm`

## Cybernoid II (Tel + Deenen 01-07-1988) — the foundational reference

### PSID header
- Version 2 format, data offset $7C
- Load address $1000 (auto-relocation)
- PAL / 6581
- 2 songs, default=1

### Zero-page allocations
- `$40-$52`: effect parameters, current note, vibrato/glide state,
  scratch.

### Per-voice global arrays (3 voices, parallel)
Counters for timing, note length, waveform selection, filter setting,
effect parameters. Voice register offsets at `d4point` = `$00, $07, $14`.

### Pattern stream command byte ranges
| Range | Meaning |
|---|---|
| `$00-$3F` | Note index (`$40-$7F` would be note + tone modulation if applied) |
| `$60-$7F` | Voice/instrument selection (mask low 5 bits) |
| `$80-$BF` | Note length |
| `$C0-$DF` | Waveform/voice parameters |
| `$E0-$EF` | Glide / pitch slide |
| `$FE` | Song end |
| `$FF` | Pattern end |

### Instrument format (8 bytes per instrument)
1. Pulse width high nibble
2. Waveform select + gate/ADSR attack high
3. Attack/Decay ADSR
4. Sustain/Release ADSR
5. Filter count flags
6. fx1 (effect 1 — vibrato or arp index)
7. fx2 (effect 2)
8. fx3 (effect 3)

## Test Tune (Deenen 1988) — MoN canonical

### Pattern command nibble bands (clearer in this version)
| Range | Meaning |
|---|---|
| `$c0-$cf` | Waveform select |
| `$70-$7f` | Arpeggio |
| `$80-$bf` | Note length |
| `$e0-$ef` | Glide |
| `$ff` | Repeat / pattern end |
| `$fe` | Song end |

### Instrument byte layout (refined)
| Byte | Field |
|---|---|
| 0 | Pulse width high |
| 1 | Waveform + ADSR attack |
| 2 | ADSR decay/sustain |
| 3 | ADSR release + filter cutoff |
| 4 | Filter configuration |
| 5-7 | Effects (vibrato / modulation / drums) |

### Frequency tables
Two **separate** tables `lonote` and `hinote`, each 96 entries
(C0..B7), 12-bit precision split low/high.

### Glide command
Opcode `$e0` followed by direction (`up`/`down`) and speed parameter.

## Test Tune 2 (Deenen) — TASM-source-style constants

This file uses **symbolic constants** matching the MoN editor —
extremely valuable for understanding the binary format:

```
end      = $00     ; block terminator
arpend   = $00     ; arpeggio end
drend    = $ff     ; drum end
wfend    = $08     ; waveform table end
endsong  = $ff     ; song end
rep      = $bf     ; repeat
dur      = $80     ; duration base
snd      = $e0     ; sound/instrument select
vol      = $ef     ; volume control
pause    = $7c
stop     = $7b
filter   = $7e
glide    = $7f
drum     = $80     ; drum trigger
arp      = $00     ; arpeggio mode
larp     = $40     ; locked arpeggio
```

Notes use C0..B7 mapped to values 1..96, indexing `lobyte` / `hibyte`
frequency tables → `$D400` / `$D401`.

### Instrument layout (this file, 8 bytes)
| Byte | Field |
|---|---|
| 0-1 | Waveform settings |
| 2 | Attack/Decay |
| 3 | Sustain/Release |
| 4 | Gate-on length |
| 5 | Pulse effect index |
| 6 | Arpeggio / drum offset |
| 7 | Vibrato effect index |

### Effect tables (parametric, indexed by instrument byte 5/6/7)
- **Pulse effect** (5 bytes/entry): slide speed, min width, max width,
  sweep speed, loop offset
- **Vibrato effect** (4 bytes/entry): delay, length, amplitude, speed
- **Drum** (variable): signed pitch deltas + waveform changes

### Voice state arrays (full list — useful for state matching)
`voi1x, nnh, blockix, drix, logl, higl, repc, pwud, duration,
durtel, vix, soundnr, breb, sp, glb, frr, pur, blocknr, wnf,
loopadd, stopb`

## James Bond 3 (Bjerregaard 18-19/6/1988) — improved MoN variant

Header comments document **changes to the standard MoN driver**:
```
"2ND SUSTAIN"
"SET1+7 BIT 4-7 = LEVEL"
"RELEASE ONLY WHILE RESTING"
"(!)CHIP RESET ALWAYS"
"AUTO SUSTAIN DELAY"
"SET1+6 BIT 5-7 = TIME=FRAMES"
"RELEASE TRIGGER"
"SET1+3 BIT 4-7 = 2*TIME=FRAMES"
"FILTER SEQUENCE END/STOP"
"RECOGNITION BYTES CHANGED"
```

### Instrument (SET1) layout — Bjerregaard variant
| Byte | Field |
|---|---|
| 0 | Attack/Decay |
| 1 | Sustain/Release |
| 2 | Vibrato parameters |
| 3 | Pulse width / Delay (high nibble = 2×release-trigger frames) |
| 4 | Note selection |
| 5 | Filter program |
| 6 | Waveform sequence (high 3 bits = auto-sustain delay frames) |
| 7 | Vibrato 2 / Sustain 2 (high nibble = sustain-2 level) |

### Pattern bytes — Bjerregaard variant
| Range | Meaning |
|---|---|
| `$60-$7F` | Arpeggio select |
| `$80-$9F` | Envelope / instrument select |
| `$A0-$BF` | Glide |
| `$C0-$DF` | Note length |
| `$E0-$FF` | Pause duration |
| `$FE` | Tie / hold |
| `$FF` | End |

This is a **different command-byte layout** from the canonical
Deenen variant — confirming that MoN is not a single binary format
but a *family* of closely related drivers.

## SFX Player (Deenen 1989)

Real-time SFX engine, 6 effects via keys 1-6, 3 voices, block-based.

### Block structure
Named blocks `block01..block16`. Commands:
- `snd + [0-8]`: instrument select
- `dur + [n]`: note length
- Note name `c0..b7` or `glide`
- `filter`, `pause`, `filtoff`, `repeat`, `end`

### Instrument (`wfadsr`) — 9 sounds, 0-8
Per-sound: waveform (0-4), AD register, SR register, pulse width,
freq-table reference, vibrato index.

## Cross-variant invariants (FC's core too)

These hold across **all** MoN variants (Deenen/Tel/Bjerregaard/FC):

1. **3 voices, parallel state arrays** (not interleaved struct-of-array).
2. **96-entry C0-B7 frequency tables**, split lo/hi (12-bit precision).
3. **Pattern bytes are command-tagged**: high nibble selects command,
   low nibble is parameter — but the exact band-to-command mapping
   differs per variant.
4. **8-byte instruments** with effect-table indices (vibrato/pulse/arp
   are looked up, not inline).
5. **`$D417`** (filter/voice routing) is written explicitly each frame
   — this is the `STA $D417` byte in the sidid signature for MoN.
6. **Voice register offsets** `$00, $07, $14` (not `$00, $07, $0E` — note
   the gap between voice 2 and voice 3, which uses the SID's gap
   between v2's $D40D-end and v3's $D40E-start. ACTUALLY this should
   be $00, $07, $0E — verify when reading the actual asm).

## Hawkeye-specific implications

Cybernoid II (the only Tel_Jeroen_MON in the repo) is from 1988 —
**same year as Hawkeye**, same author. Hawkeye is very likely the
*same driver family* with potentially different effect-table layouts
or instrument-byte bit assignments. The Cybernoid II asm should be
the **primary reference** for the Hawkeye rebuild.

## Format-spec uncertainties (need binary confirmation)

- Voice register stride: `$07` or `$0E` for voice-2 → voice-3? (One
  fetched summary said `$14`, another would imply `$0E`. SID's actual
  voice spacing is 7 bytes; `$14 = 20` would skip voice 3 entirely.
  Verify from raw asm.)
- Whether Hawkeye uses the Cybernoid pattern-byte band layout
  (`$00-$3F`/`$60-$7F`/`$80-$BF`/`$C0-$DF`/`$E0-$EF`) or the FC V3
  layout (`$60-$7F`/`$80-$BF`/`$C0-$DF`/`$E0-$FF`) suggested by the
  sidid signature.
