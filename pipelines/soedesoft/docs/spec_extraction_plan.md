# SoedeSoft / Soundmaster — Extraction Plan

**Provenance:**
- Soundmaster V3.1 German manual (18 pages, PDF from CSDb #90307, written by Walter Konrad, 1989)
- `research.md` in this directory (prior overview synthesis)
- `deepsid_classifier.md` in this directory (DeepSID sub-classifier analysis)
- sidid.cfg SoedeSoft entry (extracted from `deprecated/gt2_pipeline/tools/sidid.cfg`)
- `hvsc84.db` PSID header statistics across 929 classified SoedeSoft SIDs
- CSDb entries #10735 (V1.0), #90307 (V3.1)

Status of source material: NO public source code, NO annotated disassembly exists.
Everything below that goes beyond the manual is either INFERRED from PSID-header
statistics or OPEN pending disassembly.

---

## 1. Engine identity & scope

**Family:** SoedeSoft / Soundmaster (Jeroen Soede — player/code; Michiel Soede — editor)
**Versions confirmed by sidid.cfg:** V1.0, V3.1, V3.2  
**Corpus:** 929 HVSC SIDs (engine='SoedeSoft' in hvsc84.db), 0 migrated  
**Top composers:** Nagie Sascha (157), Danko Tomas (52), Vulgarik (48), Doussis Stello (46), Drumtex (40)  
**Timing:** VBlank / 50 Hz (manual: "Abspielgeschwindigkeit" = playback speed; no CIA timer mentioned)  
**Known not from scratch:** manual explicitly states "Nothing was ripped — developed from scratch"

---

## 2. Fixed anchors (DOCUMENTED or STRONGLY INFERRED from headers)

These are facts that can be relied on before any disassembly.

### 2a. Player entry points

The background task documents: **+$0 = JMP init / +$3 = JMP play** at the load base.

Confirmed by PSID-header statistics:
- 29 SIDs: init=$6000, play=$6003 — delta=+3 (textbook JMP/JMP)
- 34 SIDs: init=$1000, play=$1003 — delta=+3
- 29 SIDs: init=$3803, play=$3806 — delta=+3
- 11 SIDs: init=$2000, play=$2003 — delta=+3

The delta=+3 cluster (total ~103 SIDs across all load addresses) confirms the
JMP-init / JMP-play layout at the load base.

INFERRED: The dominant cluster (init=$6000, play=$6006, 309 SIDs) likely
reflects a different convention: the PSID play address points past a 6-byte
preamble, possibly because $6000-$6005 is init-only code and $6006 is the
actual play-routine entry (no JMP-dispatch stub at the load base for this
variant). This needs disassembly to resolve.

### 2b. Embedded ASCII signature

**DOCUMENTED:** The string `"88 SOEDESOFT-"` is embedded in the data area.
This is a relocation-invariant anchor: scan any SoedeSoft SID binary for
this 14-byte ASCII string to locate the data segment base regardless of
load address.

### 2c. Variable area

**DOCUMENTED:** Player variables at $0333–$039D (~106 bytes = $6A bytes).  
**DOCUMENTED:** Init clears this area: `LDA #$00 / LDY #$69 / STA $0333,Y / DEY / BNE`.  
This is a FIXED page-3 address — NOT relocated with the player. All versions
appear to use the same variable page (confirmed by the init description
across V1.0–V3.2 in the manual).

### 2d. Per-voice register writes

**DOCUMENTED (background task):** The player uses indexed `STA $D4xx,X`
with X = 0 / 7 / 14 (decimal) = $00 / $07 / $0E to address voice 1 / 2 / 3.
This is standard C64 SID voice-stride addressing.

### 2e. Timing / IRQ

**INFERRED:** VBlank / 50 Hz. The manual's "Speed" parameter (Abspielgeschwindigkeit)
controls playback tempo but appears to be a software divider, not CIA. PSID `speed`
bit is OPEN pending disassembly of the play-routine dispatch.

### 2f. Version taxonomy (from sidid.cfg byte signatures)

Three player variants are identified by sidid:

**V1.0** signature (relocated pattern):
```
D0 03 BD ?? ?? 9D ?? ?? 60 END
B9 ?? ?? 4A 4A 4A 4A 9D ?? ?? B9 ?? ?? 0A 0A 0A 0A 9D ?? ?? B9 END
```
Observation: The second sequence (nibble split via 4x `4A LSR A` for the low
nibble, 4x `0A ASL A` for the high nibble) strongly suggests splitting a
packed byte into two 4-bit fields written to two SID registers — consistent
with pulse-width encoding (low nibble → $D402 low, high nibble → $D403 hi)
or ADSR packing.

**V3.1** signature:
```
9D ?? ?? BD ?? ?? D0 ?? 18 B9 ?? ?? 7D ?? ?? 99 ?? ?? 99 00 D4
B9 ?? ?? 69 ?? 99 ?? ?? 99 01 D4 4C END
```
Observation: `99 00 D4` = `STA $D400,Y` and `99 01 D4` = `STA $D401,Y` —
freq-lo and freq-hi writes via Y-indexed (voice-stride). The `7D ?? ??` =
`ADC table,X` followed by `99 00 D4` suggests arp/transpose addition to
frequency. The `69 ??` = `ADC #imm` before the second store suggests a
coarse freq-hi adjustment. This is INFERRED as the frequency-write section
of the play loop with arpeggio/transpose applied.

**V3.2** signature:
```
A9 ?? 9D ?? ?? 4C ?? ?? 18 BD ?? ?? 7D ?? ?? 9D ?? ?? BD ?? ??
7D ?? ?? 9D ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60 END
```
Observation: `9D 00 D4` = `STA $D400,X` and `9D 01 D4` = `STA $D401,X` —
freq-lo/hi via X-indexed (voice-stride). `RTS` (`60`) terminates the
fragment. Multiple `7D ?? ??` = `ADC table,X` patterns — arp additions
to freq. This is INFERRED as V3.2's frequency + arp write sequence.

---

## 3. Data model (DOCUMENTED from manual)

### 3a. Song structure hierarchy

The manual defines four levels:

```
Song
└── Blocks  (ordered list of blocks; each block plays bars b1..b2 on step range)
    └── Steps  (song position: each step assigns a track/bar per voice + transpose)
        └── Bars  (pattern: sequence of note rows)
            └── Note rows  (note + sound-number + flags)
```

**Block** (Blockedit screen):
- `nr`: block number
- `b1-b2`: bar range (play bars b1 through b2)
- `tp`: block-level transpose delta added to ALL transposes in the 3 tracks
- `s1, s2, s3`: sound-number offset added to each voice's sound number (0..N)

**Step** (Stepedit screen):
- `nr`: step number
- Per voice: `trkN` (bar number) + `tp` (transpose value added to each note in the bar)
- The manual example: tp=$0C adds 12 (1 octave) to every note; tp=$FE subtracts 2

**Bar** (Bar edit screen):
- `bar length`: number of rows (note slots) in each bar
- Each row: `note` + `sound-number` (instrument ref) + flags
- Note encoding (DOCUMENTED): 0=C, 1=C#, 2=D, 3=D#, 4=E, 5=F, 6=F#, 7=G, 8=G#, 9=A, A=A#, B=B; plus octave field
- Flags per note row (DOCUMENTED):
  - bit 8 ($80): Portamento (C= key in editor)
  - bit 7 ($40): Transpose off (disables per-step transpose for this note)
  - $00–$2F: Sound-number (instrument index, 0–47 decimal)
- Special row values: `--` = sustain (release on this row), `++` = "zyclus auslösen" (cycle trigger)

**INFERRED note binary layout:** A bar row appears to be 2 bytes: [note+octave+flags] [sound-number].
The manual text "die erste Nummer ist die Note, die zweite ist die Soundnummer" confirms two
fields per row. Exact byte packing is OPEN.

### 3b. Sound (instrument) structure

The manual defines "Erster Teil" (part 1) and "Zweiter Teil" (part 2), plus an optional
arp/wave table (part 3 when arpeggio is used).

**Part 1 — waveform init:**
- Byte 1 (DOCUMENTED): waveform for $D404 (voice control). Written on every note trigger.
  Bit 1=gate, bit 2=sync, bit 3=ring mod, bit 4=$08=enables vibrato/portamento in arp,
  bits 5–8=waveform select. "Das erste Bit muß gesetzt sein" (gate bit must be set).
- Byte 2 (DOCUMENTED): secondary waveform for $D404, used on `--` (sustain/release) rows.
- If arp/wave table is used: bytes 3–6 are the arp/wave table header (see §3d below).
  Otherwise byte 3 must be $00 (end-marker, no arp table).

**Part 2 — envelope + pulse + vibrato + portamento:**
- Attack/Decay (DOCUMENTED): $D405 equivalent. "Wird vom Waveformregister initialisiert."
- Sustain/Release (DOCUMENTED): $D406. "Release startet bei '--' in den bars."
- Pulse start (DOCUMENTED): packed byte — low nibble = high nibble of $D402 (PW lo),
  high nibble = $D403 (PW hi). ("1 nibble ist ein halbes bit" — Nibble = 4 bits.)
- Pulse count level (DOCUMENTED): delta added to pulse-width low register when a new
  sound plays (PWM increment per frame when active).
- Vibrato/increase (DOCUMENTED): if < $80, sets vibrato amplitude directly; if ≥ $80,
  encodes "vibrato level addition" — the amplitude grows while the sound plays.
  "Vibrato startet mit dem Wert aus dem Spezial-Funktion-Menü" (levelinc.start field).
- Delay/Portamento count high (DOCUMENTED): packed byte:
  - bits 0–2: portamento count high ($00–$07)
  - bits 3–7: vibrato delay (how many frames before vibrato begins)
  - Example: $21 = delay=4, port.high=1; $08 = delay=1, port.high=0
- Portamento count low (DOCUMENTED): low byte of portamento rate.
- Filter start (DOCUMENTED): initial value written to $D416 (filter cutoff lo).
- Filter count (DOCUMENTED): per-frame delta added to $D416. Special value $FE means
  $D416 = $D416 - 2 (decrement by 2 instead of increment).

**Part 2 byte count:** OPEN (exact byte offsets within the sound record unresolved).

### 3c. Global / song-level parameters (Spezial Funktionen)

All DOCUMENTED from manual:
- `bar length`: rows per bar (applies globally? or per-bar? OPEN)
- `Speed`: playback speed divider
- `Filter mode/volume`: $D418 value (master vol + filter mode)
- `Resonance/filtervoice`: $D417 (resonance + voice-filter-enable bits). Manual:
  $D417 low nibble bit y selects voice: y=1→voice1, y=2→voice2, y=4→voice3
- `Filter start on voice`: "wenn Filter auf Stimme x ist, muß dieser Wert x-1 sein" — OPEN meaning
- `Filter count time`: per-frame filter sweep timer. If > $80, no time limit (infinite sweep).
- `Vibrato level`: "Geschwindigkeit des Vibrato (normal=4)" — global vibrato rate
- `Filter type`: $00 or $01; only used when filter count time < $80
- `Levelinc. start`: initial vibrato amplitude for "increasing vibrato" sounds
- `Pulshigh max/min`: clamp values for PW hi-byte when pulse count is active
- `Constant effect value`: when $7F appears in the arp table, it substitutes the current
  note value. Used for a "tick at sound start" effect. "Waveform muß $81 sein."
- `Highest bar number`: max bar index in use
- `Unused bar number`: unused/free bar slot

### 3d. Arp & wave table (Part 3 of sound, optional)

**DOCUMENTED:**
- Table header in Part 1 bytes 3–6:
  - Byte 3: start offset within arp/wave table ($00–$FF)
  - Byte 4: repeat address (loop-back point within arp table)
  - Byte 5: end address + 1
  - Byte 6: secondary sound number ($00–$1F) — provides att/dec, sus/rel, pulse start
    etc. for the arp/wave part (the other "Soundvoreinstellungen")

- Arp table entry format (DOCUMENTED from arp editor example `arp.:00!7F!07!03 04 00 7f!00!`):
  - `!` marks = "revers" flag on the entry
  - Numeric values are SIGNED offsets added to the current note (e.g. +7 = fifth, -4 = major third down)
  - $7F = "constant effect value" — substitutes actual note (see above)
  - Repeat target entry is shown in WHITE in the editor; entries before it are played once only (yellow)

- Wave table byte format (DOCUMENTED from wave editor `wave:11 81 49 41 41 41 41`):
  - Matches $D404 (voice control register) bit layout:
    - bit 0 ($01): Gate
    - bit 1 ($02): Sync
    - bit 2 ($04): Ring Modulator
    - bit 3 ($08): enables vibrato or portamento within arp
    - bits 4–7 ($F0): Waveform select

- The arp and wave tables are INTERLEAVED in the same indexed table (sound Part 1
  byte 3 = start index into a shared table). Exact byte layout of combined arp+wave
  entries is OPEN.

---

## 4. Player layout variants (from PSID headers)

INFERRED from hvsc84.db statistics across 929 SIDs:

| Cluster | init | play | delta | Count | Interpretation (INFERRED) |
|---------|------|------|-------|-------|--------------------------|
| A | $6000 | $6006 | +6 | 309 | 6-byte init preamble; play at +6 |
| B | $2000 | $2106 | +262 | 135 | ~256-byte init block (reloc variant) |
| C | $2029 | $2106 | +221 | 45 | init at +$29 offset (multi-song?) |
| D | $1027 | $1106 | +223 | 36 | similar to C |
| E | $1029 | $1000 | −41 | 35 | play before init in address space |
| F | $1000 | $1003 | +3 | 34 | classic JMP-init/JMP-play |
| G | $3803 | $3806 | +3 | 29 | classic JMP-init/JMP-play |
| H | $6000 | $6003 | +3 | 29 | classic JMP-init/JMP-play at $6000 |

The delta=+3 clusters (F, G, H) most cleanly match the documented "+$0 JMP init / +$3 JMP play"
layout. The delta=+6 cluster (A, 309 SIDs) is the LARGEST and likely the canonical V3.1
layout with no dispatch stubs. Clusters B/C/D have large deltas suggesting the music data
sits BETWEEN the init and play routines.

**The V3.1 canonical target for migration phase 1: Cluster A (init=$6000, play=$6006).**
This is the majority cluster and matches the manual's "SYS $6000 startet die Musik."

---

## 5. OPEN list — items requiring disassembly to resolve

Every item below is explicitly OPEN. The trace to run is noted.

### OPEN-1: Exact binary layout of a bar row
**What:** 2 bytes per row confirmed (note+octave vs. sound-number are separate fields);
exact bit packing of note (4 bits?), octave (3 bits?), portamento flag, transpose-off flag,
and sound number ($00–$2F) within those 2 bytes is unknown.
**Trace:** `tools/seed_disassembly.py` on canary (e.g. Ritme.sid at $2000/$2003) →
annotate bar-read loop; identify LDA/AND mask for note vs. sound fields.

### OPEN-2: Exact byte layout of Sound Part 1 and Part 2
**What:** The manual names each field but does NOT give byte offsets within the sound record.
Approximate size: Part1 is 2–6 bytes (2 waveform bytes + optional 4 arp-header bytes);
Part2 is ~9 bytes (AD, SR, pulse start, pulse count, vibrato, delay/port-hi, port-lo,
filter start, filter count). Exact count and ordering unknown.
**Trace:** Disasm of init → find sound-table base → annotate each STA $D4xx back to
the source offset in the sound record.

### OPEN-3: Combined arp+wave table encoding
**What:** Whether arp entries and wave entries interleave as (arp_byte, wave_byte) pairs
or are separate indexed tables. $7F sentinel behaviour in mixed table.
**Trace:** Annotate the arp/wave step loop in the play routine; find how the table index
advances and how each byte is split into arp-offset vs. waveform.

### OPEN-4: Exact "bar length" scope and storage
**What:** Manual calls it "Anzahl der Zeilen in den bars" (number of rows per bar), but
whether it is global or per-bar is unclear.
**Trace:** Find bar-read loop termination condition in disasm.

### OPEN-5: Speed parameter encoding
**What:** Manual says "Abspielgeschwindigkeit" (playback speed) but gives no value range
or formula. Whether it is a frame-counter reload or a note-duration divisor is unknown.
**Trace:** Find the speed counter decrement / reload in the play routine.

### OPEN-6: Filter count time > $80 = no-limit mechanism
**What:** Manual states "Ist der Wert höher als $80, gibt es kein Zeitlimit" — but the
implementation (perhaps: MSB set = skip the counter check entirely) is OPEN.
**Trace:** Disasm filter-sweep section; find BPL/BMI/BCS on the timer byte.

### OPEN-7: Multi-sound / multi-subtune structure
**What:** The DB shows SIDs with up to 15 subtunes. How the player selects a subtune
(init parameter in A register, Y, or X?) and how block/step lists are indexed per
subtune is OPEN.
**Trace:** Disasm init routine → find accumulator/register use for subtune select.

### OPEN-8: PSID `speed` bit
**What:** Whether any SoedeSoft SIDs use CIA timing rather than VBlank. The manual
mentions no CIA; all evidence points to VBlank-only. But 35 SIDs have play BEFORE init
in address space (Cluster E), which is unusual and may indicate a non-standard IRQ setup.
**Trace:** `siddump --pc-trace` on a Cluster-E SID; check PSID speed bit in PSID header.

### OPEN-9: Exact variable assignments at $0333–$039D
**What:** Which byte offsets hold which per-voice state (bar pointer, row counter, arp
table pointer, portamento accumulator, vibrato phase, filter state, etc.).
**Trace:** Annotate the variable-clear loop target range; then cross-reference each
`LDA $033x,Y` / `STA $033x,Y` in the play loop body.

### OPEN-10: Version differences between V1.0, V3.1, V3.2
**What:** sidid has distinct byte signatures for all three. Whether the USF data model
is the same across versions (only player code differs) or whether the sound/bar format
changed between V1.0 and V3.1 is unknown.
**Trace:** Disasm one V1.0 canary (e.g. Airwolf.sid load=$3800 init=$3803 play=$3806)
alongside a V3.1 canary; compare sound-record layout field by field.

---

## 6. Migration phase plan

**Phase 0 — Canary selection and seed disassembly**
- Primary canary: `hvsc84/MUSICIANS/S/SoedeSoft/Soede_Jeroen/Ritme.sid`
  (init=$2000, play=$2003, 13s, single subtune, Cluster F — textbook JMP/JMP).
  Short enough to fully annotate. Load $2000, JMP at $2000 = JMP to init routine,
  JMP at $2003 = JMP to play routine.
- Secondary canary (Cluster A / V3.1): `hvsc84/MUSICIANS/S/SoedeSoft/Soede_Jeroen/Airwolf_Title.sid`
  (init=$6000? OPEN — check actual PSID).
- Run: `tools/seed_disassembly.py` on primary canary → `pipelines/soedesoft/standard/disassembly.s`
- Annotate init + play routine headers before writing any Python.

**Phase 1 — Data extraction (canary only)**
- Resolve OPENs 1–5 above using the annotated disassembly.
- Write `pipelines/soedesoft/standard/extract/engine_model.py` (typed data model).
- Write `pipelines/soedesoft/standard/extract/to_usf.py` (binary → USF).

**Phase 2 — Composer (canary)**
- Write a SoedeSoft engine in `pipelines/composer.py` (or a companion-style module).
- Target: binary → USF → rebuilt SID, `verify_all` passes on canary.
- Use `find_first_divergence.py` for per-frame debugging.

**Phase 3 — Factory (Cluster A / V3.1, 309 SIDs)**
- Use the embedded `"88 SOEDESOFT-"` signature + init/play address heuristics to
  auto-detect layout for each SID.
- Batch extract + rebuild; `regression.py` gate.

**Phase 4 — Variant coverage**
- Cluster F (JMP/JMP, ~103 SIDs) — likely same data format, different player version.
- V1.0 (sidid sub-variant) — verify data-format compatibility; add `v1_compat` flag if needed.

---

## Leads to follow

1. **Locate the Soundmaster V3.1 PRG file** (CSDb #90307 download:
   `soundmaster3.1.prg`). The T64 binary fetched was unrelated (Chris Huelsbeck demo).
   The actual PRG contains the editor + embedded player; disassembling it would resolve
   OPENs 2–5 directly without needing a SID canary. URL:
   `http://csdb.dk/getinternalfile.php/87430/soundmaster3.1.prg`

2. **Docs PRG** (`Soundmaster_V3_1_Docs.prg`, CSDb #90307 third download) may contain
   a machine-readable version of the manual with exact byte offsets.

3. **Nagie Sascha tunes (157 SIDs)** — largest single-composer corpus; likely all V3.1.
   Pick the shortest (`Synopsis.sid` is 785s long, but others are shorter) as
   a wide-batch regression target once phase 2 passes.

4. **V1.0 Cluster** — identify via sidid sub-variant label `Soundmaster_V1.0`.
   The sidid signature fragment `B9 ?? ?? 4A 4A 4A 4A 9D ?? ??` (nibble-split store
   sequence) should allow writing a relocation-invariant fingerprinter analogous to
   `tools/engine_fingerprint.py` (FC standard player).

5. **Cluster E (play before init, −41 delta)** — check whether these are actually
   SoedeSoft or a mis-classification. The Danko Tomas tunes in that cluster have
   init=$1029, play=$1000; the player routine at $1000 is called as play, and
   something at $1029 is the init entry. Unusual — may be an in-lining of the
   init routine past the play routine body.
