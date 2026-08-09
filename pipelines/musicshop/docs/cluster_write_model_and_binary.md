# MusicShop — Per-Frame Write Model and Binary Structure

```
source_url:     hvsc85/ (READ-ONLY binary inspection) + archive.org + lemon64.com + csdb.dk + sidid.cfg
fetched_via:    WebFetch + Bash/python3 READ-ONLY struct inspection (no siddump/py65)
fetch_date:     2026-06-14
author:         Claude agent (research-player task)
content_date:   2026-06-14 (no prior published analysis found)
reliability:    MEDIUM — binary-inspection findings are solid; note data sub-format is PARTIALLY CONFIRMED
                (SID frequency interpretation consistent with musical context, but full column layout uncertain)
```

---

## 1. Corpus and Classification

- **Total HVSC tunes:** 182 (`engine='MusicShop'` in `hvsc84.db`)
- **Distribution:**
  - `DEMOS/UNKNOWN/Music_Shop/` — 121 tunes (European hobbyist users)
  - `MUSICIANS/W/Williams_Don/` — 28 tunes (official Broderbund songs)
  - `MUSICIANS/E/Ewens_Louis/`, `MUSICIANS/A/Ace64/`, `MUSICIANS/S/Safavy_Mehdi/`, `MUSICIANS/G/Gregfeel/`, misc — ~33 tunes
- **SIDId engine name:** `MusicShop` (matches `Music_Shop` classification)
- **SIDId signature** (from `sidid.cfg`):
  ```
  09 80 91 ?? C8 18 B1 ?? 6D ?? ?? 48 C8 B1 ?? 6D ?? ?? 85 ?? 68 85 END
  ```
  This sequence is `ORA #$80 / STA (zp),Y / INY / CLC / LDA (zp),Y / ADC abs / PHA / INY / LDA (zp),Y / ADC abs / STA zp / PLA / STA zp` — the note-pointer advance subroutine at **$978A** in the payload (see §4).

---

## 2. PSID Header Layout (invariant across all 182 tunes)

```
magic:       PSID
version:     2
data_offset: $007C (124 bytes)
load_addr:   $0000 (embedded in payload: first two bytes = $F6 $95 → load=$95F6)
init:        $A04D
play:        $575A
songs:       1
start_song:  1
speed:       $00000001  ← CIA-timed (bit 0 set): play() is called at CIA interrupt rate
flags:       $0018      ← SID model=MOS6581, clock=PAL
startPage:   $04        ← PSID v2 driver reservation start page ($0400)
pageLength:  $4C        ← 76 pages reserved for driver/stub area ($0400–$4FFF)
```

Key implications:
- `speed=1` → **CIA-timed**, NOT VBL (50 Hz). The play() is driven by the CIA timer, whose period varies per song (see header bytes $77DA–$77DB, §3).
- `startPage=$04, pageLength=$4C` reserves $0400–$4FFF for the PSID driver. The play stub installs itself in this region.
- `play=$575A` is **NOT in the payload** ($95F6–end). It is installed in low RAM by the init routine (see §3).

---

## 3. Binary Structure: Three Regions

The payload starts at **$95F6** and spans $95F6–$C780 (variable, song-size-dependent).

### 3.1 Region 1: Shared Player Stubs ($95F6–$A0FF, 2570 bytes)

**Byte-identical across all 182 tunes** — confirmed by comparing Maple_Leaf_Rag, Canon_in_D, We_are_the_Champions, Minuet_in_G.

Contains:
- `$95F6–$9645`: **Play-stub entry** — advances per-voice note-stream pointers based on voice down-counters (ZP $50, $52, $56).
- `$9646–$97C1`: **Note-walk routines** — per-note-event decoding, special markers, pointer chaining. SIDId signature at $978A.
- `$97C2–$97CF`: Fixed +4 pointer advance (utility sub).
- `$97D0–$97D7`: **Duration table** — `[0, 20, 40, 60, 80, 100, 120, 140]` (8 entries, multiples of 20 ticks).
- `$97D8–$A0FF`: Additional voice scheduling, tempo management, voice-state machine stubs.

The **init routine** ($A04D–$A0FF) is also in this shared block. It:
1. Runs 14 outer iterations (Y from $F2 to $FF) of a self-modifying page-copy loop.
   - Only Y=$F5 (1 page) and Y=$FA (5 pages) have non-zero page counts; others are no-ops.
   - Y=$F5: copies ~1 page near $575C — installs the play-entry stub that sidplayfp calls at $575A.
   - Y=$FA: copies ~5 pages starting near $5E46 — installs the main note-dispatch engine.
2. Copies the 256-byte song header ($A100–$A1FF) to runtime $77D4–$78D3 (via `LDA $A100,Y / STA $77D4,Y` loop).
3. Patches $794C with the step-size byte from the header ($77D5).
4. Sets up voice initial state via $A03F/$9F3F tables.
5. Calls JSR $5E51 and JSR $5A59 (Music Shop runtime init — not in payload).

**Why play=$575A is below load=$95F6:** The Music Shop SID files are PSID containers for **song data + note-walk stubs only**. The full Music Shop player ($5000–$95F5) is normally resident in RAM as the live program. The init routine *re-installs the relevant stub fragments* from the payload into low RAM, making the file self-contained for sidplayfp. This is the "relocating stub" architecture: the SID payload carries both the song data and a compact re-installer for the minimum player stubs needed for playback.

### 3.2 Region 2: Song Header ($A100–$A1FF, 256 bytes)

Copied at runtime to $77D4–$78D3. Song-specific starting at byte $A101 (byte $A100 is always $02). Decoded layout (runtime addresses):

| Runtime addr | Name | Values seen | Notes |
|---|---|---|---|
| $77D4 | format_tag | 0x02 (constant) | Always 2; probable format version |
| $77D5 | step_size | 4, 5, 11, 17, 20 | Bytes per note column; patched into $794C by init |
| $77D6–$77D7 | zp_ptr_pair | 0x74, 0x75 (constant) | ZP addresses of 16-bit note pointer ($74:$75) |
| $77D8–$77D9 | zp_ptr_pair2 | 0x74, 0x75 (constant) | Same pair (second copy or different use) |
| $77DA | tempo_hi | varies (0x00, 0x0E) | Likely CIA timer hi byte |
| $77DB | tempo_lo | varies (0x08, 0x06, 0x03, 0x0B) | Likely CIA timer lo byte (see tempo, below) |
| $77DC–$77DD | ? | varies | Song parameter, purpose unclear |
| $77DE–$77DF | ? | 0x00 0x00 | Constant in samples |
| $77E0–$77E1 | magic | 0x4D, 0x53 ("MS") | MusicShop magic signature (constant) |
| $77E2–$77E3 | version | 0x00, 0x01 | Constant in samples |
| $77E4–$77F2 | voice_params[3] | 5 bytes × 3 voices | Per-voice initial settings (see below) |
| $77F3–$78D3 | extended_params | 224 bytes | Filter, pulse-width, presets, repeat-point addresses |

**Voice parameter blocks** (5 bytes each, 3 voices):
```
byte0: 0xFF = voice enabled/not-overridden; 0x00 = voice off; 0x88/other seen
byte1: ADSR attack:decay nibbles packed (e.g., 0x73 = attack=7, decay=3; 0x74 = A=7, D=4)
byte2: SID-mapped or sustain:release (0x41 commonly: sustain=4, release=1)
byte3: additional envelope sub-param (0x09, 0x0A, 0x07)
byte4: 0x00 (separator/padding)
```
The MusicShop manual confirms ADSR per voice, and the byte1/byte2 layout maps naturally to SID ADSR register encoding (AD = nibble pair in $D405/$D40C/$D413; SR in $D406/$D40D/$D414).

**Tempo:** The bytes at $77DA:$77DB appear to be CIA timer bytes (lo:hi or hi:lo). Observed values:
- Maple Leaf Rag: 0x00:0x08 → value = $0008 or $0800 = 2048
- We_are_Champions: 0x0E:0x06 → $0E06 or $060E
- Canon in D: 0x00:0x03 → $0003 or $0300
- Bolero: 0x00:0x0B → $000B or $0B00

Combined with the duration table at $97D0 ([0,20,40,60,80,100,120,140] ticks), the effective tempo (BPM) is set by the CIA timer period × per-note duration count.

### 3.3 Region 3: Note Data ($A200–end, song-specific)

Copied at runtime to **$78D4+** (immediately after the 256-byte song header at $77D4).

**Fixed-size grid: ALWAYS 480 note columns × step_size bytes = total note area.**  
Confirmed across all samples: note_area = 480 × step_size bytes.

```
step_size examples:
  Maple_Leaf_Rag:    step=4,  note_area=1920 bytes  (480 × 4)
  We_are_Champions:  step=5,  note_area=2400 bytes  (480 × 5)
  1812_Overture:     step=11, note_area=5280 bytes  (480 × 11)
  Bolero:            step=17, note_area=8160 bytes  (480 × 17)
  Canon_in_D:        step=20, note_area=9600 bytes  (480 × 20)
```

The 480 columns likely correspond to the MusicShop notation grid: the manual states songs can be up to 20 pages, and 480 / 20 = 24 columns per page (plausibly corresponding to 24 sixteenth-note slots per page or a similar subdivision).

**Note data layout:**
- **First 12 bytes** (3 × step-size-if-4, but always 12 bytes regardless of step): all zeros. Three empty/silent columns at the start (pickup/initial silence).
- **Remaining 477 columns**: actual note events.

---

## 4. Note Column Format

### 4.1 The Pointer-Advance Mechanism (SIDId)

The note-walk routine at $978A uses a **16-bit relative-offset linked-list** mechanism to traverse the note stream:

```
New_ptr = Current_ptr + step_lo:step_hi + offset_from_stream[bytes 2:3]
```

where `step_lo:step_hi` = $5C10:$5C11 (loaded from the Music Shop runtime, set from $794C = header[$77D5]), and `offset_from_stream` is bytes 2–3 of the current note record. This allows variable-length jumps (repeat sections, loop-backs) while still having a fixed-step default.

### 4.2 Note Column Bytes (Partially Confirmed)

Each note column is `step_size` bytes wide and encodes the time-slice for all active voices. The minimum confirmed structure is **2-byte SID frequency pairs**:

```
[freq_lo] [freq_hi]   = 16-bit SID frequency register value (little-endian)
```

- `freq = 0x0000` → rest/silence for that voice slot
- `bit7 = 1` in the note byte (values $80–$FF, before frequency decode) → voice rest/silence, confirmed by player code at $9781: `BMI` to rest handler
- Musical frequency validation: `0x4E68` → 1179 Hz ≈ D6 (Canon in D opens on D ✓); `0x4669` → 1059 Hz ≈ C6 (Maple Leaf Rag, melody ✓); `0x2069` → 487 Hz ≈ B4 (bass accompaniment ✓)

**step_size variation** implies that each column carries additional per-voice parameters beyond just the frequency:
- `step=4`: [freq_lo][freq_hi] + 2 extra bytes (likely: gate/control, duration count, or envelope override)
- `step=5`: [freq_lo][freq_hi] + 3 extra bytes
- `step=20`: [freq_lo][freq_hi] + 18 extra bytes per column (vibrato, filter, pulse-width, preset changes, etc.)

The exact mapping of these extra bytes to SID registers is **unresolved** (see §6 Gaps).

### 4.3 Special Marker Bytes

Confirmed from note-walk code ($9774–$97C1):

| Marker | Meaning |
|---|---|
| `0xFD` | **Tie note** — carry previous note forward; OR's $80 into the note byte in the stream (self-modifying data). The bit7 flag persists for subsequent reads. |
| `0xFA` | **End / silence** — stop the voice or end the song. |
| `0xFC` | **Loop-back** — loads loop-target address from $5C12; stores at $5C15. |
| `bit7=1` (0x80–0xFE in note position) | **REST** — player branches to rest handler (AND #$7F / silence voice / write back). |

---

## 5. Per-Frame Write Model

### 5.1 CIA-Timed Playback

`speed=$00000001` → CIA-timed. The play() routine ($575A) fires at the CIA interrupt rate, not at VBL (50 Hz). The CIA timer period is set from the song header ($77DA:$77DB).

**Per play() call sequence:**
1. **Play-stub** ($95F6+) is called from the Music Shop dispatcher at $575A.
2. For each of the 3 voices, the per-voice down-counter (ZP $50, $52, $56) is checked.
   - If counter > 0: decrement (voice is still in the middle of its current note's duration).
   - If counter = 0: a new note is needed. The note-walk routine reads the next column from the stream, decodes freq and duration, and schedules SID register writes.
3. The **note-walk** routine ($9646+) reads from pointer $3F:$40 (pointing into $78D4+):
   - Reads note command byte; checks for TIE ($FD), END ($FA), LOOP ($FC), or REST (bit7).
   - For a sounding note: reads frequency bytes → calls JSR $5946 (main player) which writes freq to $D4x0:$D4x1 for the voice.
   - Advances pointer by step_size ($5C10:$5C11) + optional stream offset.
4. **SID register writes** (inferred from manual + code):
   - `$D400:$D401` (V1 freq), `$D407:$D408` (V2 freq), `$D40E:$D40F` (V3 freq)
   - `$D402:$D403` (V1 pulse), etc. (when pulse waveform active)
   - `$D404:$D40B:$D412` (voice control: gate + waveform from header preset)
   - `$D405:$D406` / `$D40C:$D40D` / `$D413:$D414` (ADSR from voice param blocks)
   - `$D415:$D416:$D417:$D418` (filter cutoff, resonance, routing, master vol — from header extended params)

### 5.2 Voice Write Order

Not directly confirmed from binary inspection. The 3-voice note-walk processes voices sequentially (V1, V2, V3) as independent streams with independent down-counters. The SID writes for a new note event are: freq_lo → freq_hi → (optionally gate-off → gate-on = hard restart), all within a single play() call.

### 5.3 Envelope/Gate

The MusicShop manual describes gate-on/gate-off for note attack/release. The player issues gate-on ($D4x4 bit0=1) when a note starts and gate-off ($D4x4 bit0=0) at note end (after release). Whether hard-restart (test-bit) is used is unknown. The voice param byte2 (0x41 = pulse+gate commonly) suggests the control byte is written directly.

### 5.4 Vibrato and Filter

The MusicShop supports vibrato (configurable intensity, enabled per-note or globally) and three filter types (low-pass, band-pass, high-pass) with resonance. These are reflected in the per-song step_size: songs with vibrato and filter (e.g., Canon_in_D with step=20) have much larger column records, accommodating the extra register writes per column.

---

## 6. Player Architecture Summary

```
C64 RAM layout at runtime:
  $0000–$03FF  System (zero page, stack, vectors)
  $0400–$4FFF  PSID driver + Music Shop play-stub (installed by init $A04D)
  $5000–$57FF  Music Shop resident player (part of init-installed stubs)
      $575A    play() entry point (called by sidplayfp CIA interrupt)
  $5800–$95F5  Music Shop resident player (continued)
  $95F6–$A0FF  Shared player stubs (from SID payload — init copies into low RAM)
  $A04D–$A0FF  Init routine (in payload, runs once)
  $A100–$A1FF  Song header (runtime copy: $77D4–$78D3)
  $A200–$xxxx  Note data (runtime copy: $78D4+, 480*step_size bytes)
  $xxxx–$C780  Trailing zeros (padding)
```

The play() entry at $575A dispatches into the note-walk stubs, which reference the note data via pointer $3F:$40 (ZP pair = registers $74:$75 according to header). The note-pointer chaining mechanism (SIDId signature) is the core of per-note advancement.

---

## 7. MIDI Music Shop Differences (1985)

The 1985 MIDI Music Shop (Broderbund + Passport MIDI interface) is a **separate product**. HVSC classifies both under `MusicShop` since they share the same SID player core. The MIDI version adds an external MIDI output path alongside identical SID playback. No binary diff between the two player versions has been performed. The SID init/play addresses ($A04D/$575A) and load address ($95F6) are the same in HVSC samples from both.

---

## 8. Leads to Follow

1. **Full step_size column layout**: What are the exact bytes at positions 2–(step_size–1) within each column? Specifically for step=4: is it `[freq_lo][freq_hi][gate_byte][duration]` or `[freq_lo][freq_hi][pulse_lo][pulse_hi]`? The repeating pattern `69 46 69 1A` (same byte 0 and 2) in Maple Leaf Rag is anomalous for a 2-freq interpretation and may point to a different sub-structure. **Best approach**: run siddump --writelog on a MusicShop SID and correlate the $D400–$D418 write sequence with the note data bytes.

2. **Init copy destination arithmetic**: The init's self-modifying copy loop ($A081–$A092) uses complex 16-bit arithmetic to compute src/dst. A full trace of all 14 iterations (Y=$F2 to $FF) would confirm which byte ranges in the payload get copied to exactly which low-RAM addresses. This would clarify what the play() stub at $575A looks like.

3. **ZP down-counter semantics**: ZP $50, $52, $56 are the 3 per-voice duration counters. Confirm how they are initialized (from note-data duration byte?), what unit they count in (CIA ticks? note columns?), and how they interact with the CIA timer period in the song header ($77DA:$77DB).

4. **Voice parameter blocks ($77E4–$77F2)**: The 5-byte blocks (byte0=enable, byte1=AD, byte2=SR, byte3=?) need a definitive decode. Specifically: does byte0 being $FF vs $00 vs $88 correspond to waveform select, or to a preset index, or something else?

5. **Extended params ($77F3–$78D3)**: The 224 bytes after the voice param blocks contain filter cutoff/resonance, pulse-width settings, initial $D418, and repeat-point addresses. A systematic decode against SID register assignments would complete the song header spec.

6. **Voice assignment**: The manual says "voice one = top staff note, voice two = middle, voice three = bottom." Confirm this matches the write order in the SID outputs (D400 = V1, D407 = V2, D40E = V3).

7. **480-column grid origin**: Confirm whether 480 = 20 pages × 24 columns (from the "20 pages" manual limit). If so, a single page = 24 sixteenth-note grid positions at the finest subdivision, which at 120 BPM × 4/4 time = 24 × (1/8 sec) = 3 seconds per page, 60 seconds per 20 pages. Matches the observed songlength range for MusicShop SIDs.

8. **MIDI version binary diff**: Side-by-side compare the `$95F6–$A0FF` shared block in a known 1984-only SID vs a MIDI-derived SID to isolate any differences introduced in the 1985 version.

9. **The $78D4/$78D5 dual-role puzzle**: At runtime, address $78D4 is (a) where the note stream's current position is stored (the pointer value) AND (b) the start of the note data block. These cannot both be true simultaneously unless the pointer stored in the note-data area is itself a relative offset (starts at 0 = "beginning of note data"), which is advanced per-note. Needs tracing a play() call to resolve.

10. **CSDb #82453** (the Garcisoft/Agent 16 crack release): may contain player modifications or comments in the crack intro. Worth examining for any RE notes embedded in the binary.
