---
source_url: local binary inspection (hvsc85/ SID files) + web research (App Store, Sound on Sound, sidid.cfg, chordian.net)
fetched_via: direct binary read (Python) + WebFetch + WebSearch
fetch_date: 2026-06-14
author: derived from binary inspection of 259 HVSC SIDs + published app documentation
content_date: 2015–2024 (app launched June 2015, last updated 2024)
reliability: primary (binary inspection) + secondary (published reviews, app store)
---

# SidTracker64 — Write Model and Binary Structure

## 1. Background

**App:** SidTracker64 by Daniel Larsson ("Pernod" / Horizon group)  
**Platform:** iOS iPad app (released June 2015; latest version 1.0.5, updated 2024)  
**HVSC corpus:** 259 SIDs in HVSC #84 (engine tag `SidTracker64`)  
**Native format:** `.s64` (proprietary app format, not publicly documented)  
**Export formats:** `.sid` (PSID), `.prg` (C64 PRG), `.m4a` (audio)  
**Source:** Not available (commercial closed-source iOS app)

The app emulates a SID 8580 R5 chip with three voices. All PSID exports target VBI IRQ
(`speed` field = `0x00000001` for most SIDs, meaning CIA-triggered for some).

## 2. PSID Header Layout

All exported `.sid` files are PSID version 2. Key observations:

| Field | Canonical value | Notes |
|-------|----------------|-------|
| `load_addr` | `$1000` (220/259 SIDs) | User-selectable in app settings since v1.0.5 |
| `init_addr` | = `load_addr` | Init entry = JMP to actual init sub |
| `play_addr` | = `load_addr + $0003` | Play entry 3 bytes after init |
| `speed` | `$00000001` or `$00000000` | Most single-song SIDs use vblank |
| `num_songs` | 1 (most); up to 3 seen | Multi-song uses sub-dispatcher at `play_addr` |

Non-`$1000` load addresses (`$0800`, `$A000`, `$E000`, etc.) are set via
"SID file start address" in the app settings — the player code is identical, just
relocated. 255 of 259 SIDs have `play_addr = load_addr + 3`.

## 3. Player Code Variants — Version Timeline

There are at least 14 distinct code sizes across the 259 HVSC SIDs, ranging from
1930 bytes (oldest) to 2258 bytes (newest). The code is structurally identical
across versions — only internal absolute addresses differ, because each version
grew the player by appending new feature code before the work area.

| Code size | # SIDs | Notes |
|-----------|--------|-------|
| `$078A` (1930) | 2 | Oldest — JSR sub at `base+$72C`, work area at `base+$78A` |
| `$0840` (2112) | 3 | — |
| `$084A` (2122) | 5 | — |
| `$0856` (2134) | 2 | — |
| `$0860` (2144) | 9 | — |
| `$0883` (2179) | 1 | — |
| `$08AA` (2218) | 38 | — |
| `$08B2` (2226) | 43 | — |
| `$08B4` (2228) | 44 | **Largest cluster.** JSR sub at `base+$84C`, work at `base+$8B4` |
| `$08BC` (2236) | 33 | — |
| `$08C0` (2240) | 9 | — |
| `$08C8` (2248) | 8 | — |
| `$08CA` (2250) | 15 | — |
| `$08D2` (2258) | 24 | Newest with most features |

236 of 259 SIDs matched the `60 FE 00 00` boundary pattern (23 likely use
non-`$1000` bases or multi-song stubs that shift the detection).

The player code version is determined by `code_size = work_area_offset - load_addr`.
All versions use the same SidId signature because the gate-clear sequence
(`29 FE 9D 04 D4`) is structurally identical across all variants.

## 4. Memory Map (canonical `$1000`-base, `$08B4`-size player)

```
$1000       JMP $187A               ; init entry: jump to actual init sub
$1003       [play routine begin]    ; play entry (PSID play field)
$1003-$18A9 Play routine + subs     ; ~2228 bytes of player code
$184C       Voice-register writer sub ; init-time SID reg write (JSR'd)
$187A       Actual init sub         ; sets up work area, SMC, ZP ptrs
$18AA       Work area (FE 00 00...) ; ~$6A bytes, zero-init by runtime
$1930+      Static data tables      ; ADSR, waveform, instrument, pulse tables
$19xx+      Pattern/sequence data   ; flat pattern streams, per-voice, per-subtune
$1Cxx+      Orderlist tables        ; 8 tables (4 voices × lo/hi) × (≤40 subtune entries)
```

For the 1930-byte (oldest) player, the same structure holds at lower offsets:
work area at `base+$78A` (= `$178A`), voice-writer sub at `base+$72C` (= `$172C`).

## 5. Init Entry (`$1000`)

```
$1000: 4C 7A 18   JMP $187A        ; single-song: direct jump
```

For multi-subtune SIDs (e.g., `Robs_Life.sid`, 3 songs), the PSID `play_addr`
points to a small stub (at a high address like `$4323`) that does
`JMP $1003` — a trampoline that routes the PSID's "subtune select via init"
back to the standard play entry. The init for multi-song SIDs is at `$1000` and
dispatches based on the subtune accumulator value.

The init sub at `$187A`:
1. Clears voice work area (`$18BA..$18CE`, 21 bytes = 3 voices × 7 SID regs) using `A9 00; LDX #$14; STA $18BA,X; DEX; BPL` loop.
2. Writes default work-area values: gate-clear mask `$18AA=$FE`, master-vol `$18AB=$0F`, counters `$18AD/$AE/$AF/$B0 = $01`, `$18AC=$FF`.
3. **SMC:** `LDA #tempo; STA $105F` — writes tempo speed into the CPX operand in the play routine.
4. **SMC:** orderlist length is baked into a CPX operand at `$107D` by the assembler (not a runtime write — it's a fixed assembled value per-song).
5. Sets ZP pointers `$F0/$F1` (voice 1), `$F2/$F3` (voice 2), `$F4/$F5` (voice 3), `$F6/$F7` (FX/filter) from the per-subtune orderlist tables.
6. `RTS`.

## 6. Play Entry (`$1003`) — Full Frame Flow

Each `play()` call proceeds as follows:

### Step 1: Write SID registers for all 3 voices

```
$1003: A2 00; JSR $184C    ; voice 1 (X=0)
$1008: A2 07; JSR $184C    ; voice 2 (X=7)
$100D: A2 0E; JSR $184C    ; voice 3 (X=14)
```

The JSR sub at `$184C` (voice-register writer) writes 7 registers per voice
using the work area at `$18BA,X`..`$18C0,X` (7 bytes per voice, X-indexed with
stride 7):

```
LDA $18BA,X  AND $18E9,X  STA $D400,X  ; PW lo  (AND gate-mask table for init path)
LDA $18BB,X              STA $D401,X  ; PW hi
LDA $18BC,X              STA $D402,X  ; freq lo
LDA $18BD,X              STA $D403,X  ; freq hi
LDA $18BE,X  AND $18E9,X STA $D404,X  ; ctrl (waveform+gate) — AND table masks gate
LDA $18BF,X              STA $D405,X  ; AD
LDA $18C0,X              STA $D406,X  ; SR
```

The `AND $18E9,X` for the ctrl register is the **init-path gate-control** — the
work area `$18E9` holds a per-voice gate mask that the play routine manages
separately. At runtime gate is set/cleared through the SMC and work-area paths below.

### Step 2: Write filter and volume registers

```
$1012: LDA #0; STA $D415   ; filter cutoff lo (initially 0)
$1017: LDA #0; STA $D416   ; filter cutoff hi (initially 0)
$101C: LDA #filter_mode    ; SMC byte at $101D (0 = no filter)
$101E: BEQ +$30            ; if filter_mode==0, skip filter sweep -> $1050
       [filter sweep code: $1020-$104C, reads filter data from FX sequence via ZP F6/F7]
$104D: LDA $101D; ORA #$00; STA $D417  ; filter routing (SMC at $101D=mode, $101F=routing)
$1052: LDA #$0F; ORA #$00; STA $D418   ; master vol = $0F (full) OR'd with song bits
```

**Filter mode SMC at `$101D`:** init writes the filter mode value here. `0` = no filter
active (play skips filter processing). Non-zero = filter cutoff is swept per-frame from
the FX sequence stream at `ZP:F6/F7`.

### Step 3: Tempo counter — pattern step advance gate

```
AE AA 18  LDX $18AA        ; load tempo counter
E8        INX
E0 08     CPX #tempo        ; SMC: $105F contains the per-song tempo value
B0 03     BCS -> JMP $1297  ; if counter >= tempo: fire pattern advance
8E AA 18  STX $18AA         ; else: save counter and continue to voice state
```

The tempo value (1–255) is written to `$105F` (the CPX operand) by init.
Tempo 5 = advance pattern step every 5th play() call. Tempo 0 is special (never triggers?).

### Step 4: Sub-counter for 16-step pattern groups

```
AE AB 18  LDX $18AB
E8        INX
E0 10     CPX #$10          ; every 16 tempo-ticks
F0 06     BEQ -> pattern_orderlist_advance
8E AB 18  STX $18AB
JMP $10CD ; continue to voice state processing
```

Every 16 tempo fires, the orderlist position counter (`$18AC`) advances.

### Step 5: Orderlist position advance

```
AE AC 18  LDX $18AC
E8        INX
E0 28     CPX #orderlist_len  ; baked into CPX operand at $107D (e.g. $28=40)
90 02     BCC skip
A2 00     LDX #0             ; wrap to beginning = song loop
8E AC 18  STX $18AC
; Then: load new sequence pointers from orderlist tables
BD xx xx  LDA V1_lo_table,X  ; 85 F0 = STA ZP:F0
BD xx xx  LDA V1_hi_table,X  ; 85 F1 = STA ZP:F1
... (×4 voices)
```

### Step 6: Per-voice pattern step state machine

For each of the 3 note voices (and the FX voice), the play routine:

1. **Decrements the duration counter** (`$18AE` for V1, `$18AF` for V2, `$18B0` for V3).
2. If counter > 0: skip to next voice (continue sustaining current note).
3. If counter = 0: **read next pattern step** from `(ZP:Fx),Y`.

**Pattern advance / page wrap:**
- Y increments through pattern bytes. When Y reaches `$80` (bit 7 set after INY):
  - Y is reset to 0.
  - The 16-bit ZP pointer (`F0/F1` etc.) advances by `$0080` (next 128-byte page).
  - The first byte of the new page is read: if `== $01` → two-byte loop-back marker
    follows (`lo`, `hi`); the sequence restarts from that address.

## 7. Pattern Step Encoding

Each pattern step in the flat sequence stream is 1–3 bytes:

### Byte 0 interpretation:

| Range | Meaning | Extra bytes |
|-------|---------|-------------|
| `$00` | End-of-sequence / loop | Read loop address: 2 bytes follow |
| `$01`–`$3F` | Duration tick (6-bit): `dur = byte >> 1`; no note change | 0 extra |
| `$40`–`$7F` | Duration tick with effect: `dur = (byte & $3F) >> 1` | 1 extra (effect param) |
| `$80`–`$FF` | **Note event** with instrument select | 2 extra bytes |

### Note event (byte 0 ≥ $80):

```
byte 0: instrument selector
  shift ops: ASL→$18D4, ASL→$18D3, LSR, LSR, AND #$1F → instrument number (0–31) → $18D2
  instrument bits 6-5 of byte 0 (after mask) → waveform sub-mode bits stored in $18D3/$18D4

byte 1: note/frequency byte (loaded from pattern stream)
  if bit 7 set: read byte 2 also (3-byte event total)
    byte 1 (& $7F) → $18D0 (note / portamento target)
    byte 2 → $18F9 (effect parameter)
  else: 2-byte event; byte 1 → $18EA (note reference)

duration: set to 1 (for immediate next-step processing)
```

The **note event** also triggers:
- Instrument ADSR lookup from the ADSR table (at `$1938` in Lurker's layout):
  `AD = adsr_lo_table[instrument]`, `SR = adsr_hi_table[instrument]`
- Gate-clear path: `LDA ctrl,X; AND #$FE; STA $D404,X` ← **this is the sidid signature**
  — clears gate bit (bit 0) to trigger hard restart, then restores waveform byte
- Waveform byte written from `$18BE,X` (ctrl work area) on next frame

### Special byte values in pattern:

- `$48` = rest / tie (observed in pattern data: single byte, ~8 ticks)  
- `$60 $60` = sequence end / loop markers
- `$19`–`$1A` = short duration ticks (1–2 frames)

**Note frequency lookup:** After instrument select, frequency bytes are loaded from
a frequency table referenced through the instrument definition. The `18 69 44` (CLC; ADC #$44)
is the **portamento/glide step** — adds `$44` to the current freq work value per frame
for a pitch slide toward the target.

The `18 69 80` (CLC; ADC #$80) sequences are the **16-bit ZP pointer page-advance**
(described above in the page-wrap mechanism).

The `18 69 01` (CLC; ADC #1) is a **note-step counter increment** (half-step advance
in the ADSR decay table or similar index).

## 8. Work Area Layout (canonical `$08B4`-size player)

```
$18AA   tempo counter (0 to tempo–1)
$18AB   16-step sub-counter (0..15)
$18AC   orderlist position (0..orderlist_len–1)
$18AD   duration counter, voice 1
$18AE   duration counter, voice 2  ← WAIT: re-examine (may be $18AE/AF/B0)
$18AF   duration counter, voice 3
$18B0   FX duration counter
[work variables interleaved: D0, D1, D2, D3, D4, D5, D7, D8, DA..DF per voice]
$18BA–$18C0  Voice 1 SID shadow: PW_lo, PW_hi, freq_lo, freq_hi, ctrl, AD, SR
$18C1–$18C7  Voice 2 SID shadow
$18C8–$18CE  Voice 3 SID shadow
$18D0   note target / portamento target
$18D1   voice 1 sub-index (sequence table index)
$18D2   current instrument number
$18D3   waveform bits B (byte0 << 2 with wrapping)
$18D4   waveform bits A (byte0 << 1 with wrapping)
$18E9   per-voice gate mask (FE = gate cleared; toggled between FE and FF)
$18EA   note active flag ($80 = new note, 0 = continuing)
$18F9   effect parameter byte
```

**Note:** exact assignment of the 0x6A-byte work area requires full per-voice
tracing. The above is inferred from code paths; some bytes serve dual roles.

## 9. Static Data Tables (after work area)

Static tables begin at `base + code_size` (e.g., `$1938` for Lurker, `$1942` for Laholms).
Layout:

```
[base+0x938] ADSR_lo[0..N]    ; AD byte per instrument (N = instrument count)
[base+0x93C] ADSR_hi[0..N]    ; SR byte per instrument
[base+0x940] waveform[0..N]   ; ctrl waveform byte per instrument ($41=pulse, $81=noise, etc.)
[...]        pulse_width[0..N]; PW values per instrument or per-step
[...]        vibrato/glide tables; referenced by the ADC/portamento code paths
[...]        frequency table;  per-note frequency words
[...]        pattern data;    flat streams, one per voice per subtune
[...]        orderlist tables; 8 tables (4 voices × lo/hi byte), ≤40 entries each
```

The exact offsets vary per SID (depending on instrument count, song length). The
static area is **song-specific** — it is the "song data" exported from the app.

## 10. Orderlist (Song Order)

The orderlist is a set of 8 parallel tables (4 voices × lo/hi byte), each with up
to 40 entries. Each entry is a 16-bit pointer to the START of a flat pattern stream
for that voice at that song position.

```
V1_lo_table[$1ABA]   V1_hi_table[$1AD6]   → ZP F0/F1
V2_lo_table[$1AF2]   V2_hi_table[$1B0E]   → ZP F2/F3
V3_lo_table[$1B2A]   V3_hi_table[$1B46]   → ZP F4/F5
FX_lo_table[$1B62]   FX_hi_table[$1B7E]   → ZP F6/F7
```

(Addresses above are Lurker-specific; differ per song because data is at different offsets.)

Init loads `ZP:F0..F7` from `table[subtune_number]`. The play routine's orderlist
advance reloads these from `table[orderlist_position]` every 16 tempo-ticks.

The **orderlist length** (e.g., 40 for Laholms, 28 for Lurker) is baked into the
CPX operand at `base + $7D` and cannot change at runtime.

## 11. The `18 69` (CLC/ADC) Operations — What They Compute

The sidid signature ends with `18 69` (CLC; ADC imm). These appear in multiple contexts:

| Address range | ADC operand | Context |
|---------------|------------|---------|
| `$1147`, `$11DD`, `$1273`, `$12F1` | `#$80` | 16-bit ZP pointer page-advance (128 bytes per page) |
| `$13F4` | `#$01` | Note-step index increment (1 half-step) |
| `$145E`, `$14BF` | `#$44` | Portamento/glide step: add 68 to freq per frame for pitch-slide |

The signature's `18 69` specifically refers to the **portamento/glide accumulation** in
the gate-clear path: after clearing the gate and reloading the instrument, the freq
work value is advanced by `$44` per frame toward the target note. This is the
"tonal changes per step" / glide feature.

## 12. Voice Register Write Order per Frame

The sequence of `$D400..$D418` writes per `play()` call, in order:

1. Voice 1: `$D400` (PWlo), `$D401` (PWhi), `$D402` (freqlo), `$D403` (freqhi), `$D404` (ctrl), `$D405` (AD), `$D406` (SR)
2. Voice 2: `$D407..D40D` (same set, X=7)
3. Voice 3: `$D40E..D414` (same set, X=14)
4. `$D415` = filter cutoff lo (0 if no filter)
5. `$D416` = filter cutoff hi (0 if no filter; may be non-zero if filter active)
6. `$D417` = filter routing/mode (from `$101D` SMC)
7. `$D418` = master volume (`$0F` ORed with per-song upper bits)

**Gate clear (hard restart):** when a new note event fires:
- `LDA $18BE,X; AND #$FE; STA $D404,X` → clears gate bit → hard restart
  (**this is the sidid signature: `29 FE 9D 04 D4`**)
- Next frame: gate is re-set through normal ctrl write

**Note:** The sidid signature is matched in the PLAY path's gate-clear routine,
NOT in the init-time voice-writer sub (which uses `AND $18E9,X` table form for
conditional gate control).

## 13. SidId Signature

```
SidTracker64
BD ?? ?? 29 FE 9D 04 D4 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? F0 ?? A8 BD ?? ?? 18 69
```

Decoded:
```
BD ?? ??     LDA voice_ctrl_work,X      ; load ctrl byte from voice work area
29 FE        AND #$FE                   ; CLEAR gate bit → hard restart
9D 04 D4     STA $D404,X                ; write ctrl to SID (gate OFF)
B9 ?? ??     LDA new_ctrl_table,Y       ; load new waveform byte from table
9D ?? ??     STA voice_ctrl_work,X      ; store new ctrl to work area
B9 ?? ??     LDA something,Y            ; load next sequence byte
9D ?? ??     STA something_work,X       ; store it
F0 ??        BEQ (check for end-marker) ; test for $00 (loop back)
A8           TAY                        ; transfer to Y for table index
BD ?? ??     LDA freq_or_glide,X        ; load freq/glide value
18           CLC                        ; clear carry
69           ADC #imm                   ; add glide step (portamento)
```

The signature is present in ALL known SidTracker64 players (1930–2258 bytes),
located in the gate-clear / hard-restart path within the per-voice pattern step
state machine. No version variant uses a different gate-clear opcode.

## 14. Filter + FX Voice

The FX voice sequence (`ZP:F6/F7`) carries:
- Per-step filter cutoff values (lo+hi bytes for `$D415/$D416`)
- Volume automation
- Tempo changes (from `$10D8` SMC target written during sequence advance)

The FX stream uses the same 128-byte page structure as note voices. Filter
processing is enabled by a non-zero `filter_mode` byte at `$101D` (init SMC).
When active, the play routine reads cutoff bytes from the FX stream at each step.

## 15. Export Structure: Is the Player Fixed or Per-Song?

The player is **fixed per app version**, with song data appended after the player code.
Evidence:
- All SIDs of the same code size share identical code bytes (modulo address references).
- Internal absolute addresses shift by exactly `code_size_new - code_size_old` bytes
  between versions, consistent with the player code growing upward.
- Song-specific data (instrument ADSR, waveforms, patterns, orderlists) lives entirely
  in the static data region after `base + code_size`.
- The tempo and orderlist-length are baked into SMC bytes within the player by the exporter.

**Per-song parameters written by the exporter into player code (SMC slots):**
- `$105F`: tempo speed (CPX operand, 1 byte)
- `$107D`: orderlist length (CPX operand, 1 byte)
- `$101D`: filter mode (LDA immediate operand, 1 byte)
- `$101F`: filter routing ORA operand (1 byte)

The player is **NOT** per-tune optimized. Same code for all songs of a given app version.

## 16. Version Detection

The player version can be identified by `code_size = work_area_offset - load_addr`,
where `work_area_offset` is the address where the `FE 00 00...` pattern appears
(the byte after the init sub's RTS). Alternatively: check the JSR target address
in the init call sequence (bytes 3–4 of the play entry):

- Oldest player: `20 2C 17` = JSR `$172C` → code_size = `$78A`
- Largest cluster: `20 4C 18` = JSR `$184C` → code_size ≈ `$8B4`

## 17. Tool Handling

- **sidid (Cadaver) / player-id (WilfredC64):** single signature matches all versions.
  No version-specific entries. Signature located in play-time gate-clear path.
- **DeepSID (Chordian):** plays SidTracker64 SIDs via WebSid/JSIDPlay2/reSID.
  No special SidTracker64 handling documented.
- **libsidplayfp / VICE:** standard PSID handling; no engine-specific code.
- **HVSC:** 259 SIDs, all tagged `SidTracker64` by sidid.

## 18. Key Gaps / Open Questions

1. **Exact work-area byte map per version:** the 0x6A-byte zero-init region
   needs full per-voice tracing to assign every byte. Duration counter vs.
   sub-state roles for slots `$18AD`–`$18B0` need verification.

2. **Full note encoding:** the mapping from the `E0`–`FF` event byte to SID
   frequency needs the frequency table (somewhere in static data, not yet located
   precisely).

3. **Instrument definition block:** the ADSR, waveform, pulse, and table
   parameters per instrument. The static data area starting at `$1938`+
   contains these but the exact layout depends on the number of instruments
   and which features are used.

4. **Wavetable / filter table / pulse table encoding:** the app documents these
   as separate "table editors" (vibrato, filter sweep, PW sweep). These tables
   are in the static data area but their byte format is unresolved.

5. **Multi-speed support:** the app claims "multi-speed" support. The
   mechanism is not evident from single-speed binary inspection.

6. **Old player (1930 bytes) vs new player feature diff:** the 298 extra bytes
   in the new player correspond to added features (likely vibrato table + glide
   enhancements + filter table edit), but a byte-level comparison was not done.

7. **FX voice format:** only that it carries filter cutoff values; the exact
   byte encoding (similar to note-voice stream, or different?) is unconfirmed.

8. **Multi-song dispatcher:** for SIDs with `num_songs > 1`, the init stub
   structure and how the subtune index selects different orderlist start
   positions needs verification.

## Leads to Follow

- **csdb.dk:** Search for "Pernod" or "Horizon" scener entries — may have forum
  posts or comments with technical details about the app's export format.
- **App Store reviews / update history:** the 2019 update added "set SID file
  start address from settings" — confirms variable load address is v1.0.5 feature.
  Other update notes may describe format-breaking changes.
- **Archive.org:** try `web.archive.org/web/*/sidtracker64.com` — the app
  apparently had a website; it may have contained a manual.
- **GitHub search:** `"sidtracker64" OR "sid tracker 64" filetype:cfg OR filetype:asm`
  might find unofficial parsers or reimplementations.
- **Chordian.net C64 editors comparison page** (`c64editors.htm`): already partially
  fetched — noted "player ~2000 bytes, zero page 2 bytes ($F8-$F9), ~23–27 rasterlines"
  — fetch the full page for further technical comparison table entries.
- **MusicRadar / CDM articles** (2015 launch coverage): may have technical quotes
  from the developer about the export format.
- **iOS app binary:** The app's own binary (if accessible) would contain the
  authoritative player source. Not publicly available, but may exist in cracked form
  on certain scene sites.
- **YouTube tutorial videos** by Daniel Larsson (linked from app store): may show
  format internals when demonstrating the wavetable / instrument editor.
- The `$12D0` path (`STA $105F` from within the play routine) suggests a SECOND
  SMC write to the tempo slot during play — possibly dynamic tempo change via
  the FX stream. Worth tracing.
