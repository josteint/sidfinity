# DefleMask C64/SID Musical Model and Effect Catalogue

## Provenance

| Field | Value |
|-------|-------|
| primary_source_1 | https://www.deflemask.com/DMF_SPECS.txt (version 0x18) |
| primary_source_2 | https://www.deflemask.com/DMF_SPECS_0x15.txt (version 0x15) |
| primary_source_3 | https://www.deflemask.com/DMF_SPECS_0x11.txt (version 0x11) |
| furnace_effects_src | https://raw.githubusercontent.com/tildearrow/furnace/master/src/engine/sysDef.cpp |
| furnace_c64_platform | https://raw.githubusercontent.com/tildearrow/furnace/master/src/engine/platform/c64.cpp |
| furnace_c64_doc | https://raw.githubusercontent.com/tildearrow/furnace/master/doc/7-systems/c64.md |
| furnace_c64_ins_doc | https://raw.githubusercontent.com/tildearrow/furnace/master/doc/4-instrument/c64.md |
| furnace_dmf_importer | https://raw.githubusercontent.com/tildearrow/furnace/master/src/engine/fileOps/dmf.cpp |
| raw_specs_saved_to | pipelines/deflemask/docs/src/ |
| fetched_via | curl + gh API (GitHub raw) + WebFetch |
| fetch_date | 2026-06-14 |
| author | Leonardo Demartino (DefleMask); tildearrow and contributors (Furnace) |
| content_date | DMF spec: 2021 (Delek); Furnace: continuously maintained through 2026 |
| reliability | HIGH — primary source (official DMF_SPECS.txt fetched verbatim), corroborated by Furnace open-source implementation whose C64 importer was read directly |

---

## 1. System Identification

DefleMask represents the Commodore 64 as two system variants (different SID revisions), both with exactly 3 channels:

| System constant | Byte value | Chip | Channels |
|----------------|-----------|------|----------|
| SYSTEM_C64 (SID 8580) | `0x07` | MOS 8580 | 3 |
| SYSTEM_C64 (SID 6581) | `0x47` | MOS 6581 | 3 |

The two variants are musically identical in the DMF model; the difference is in emulation behaviour (6581 has a DC-offset hardware quirk enabling crude 4-bit PCM via `$D418` volume register). In older DMF versions (0x11/0x15) the 6581 variant was `0x17` instead of `0x47`.

All three channels use the same per-voice register layout: `$D400..D406` (V1), `$D407..D40D` (V2), `$D40E..D414` (V3). Global filter registers are `$D415..$D418`.

---

## 2. DMF Format Version History (C64-relevant changes)

Raw spec files are preserved in `docs/src/`. Version bytes found in the wild:

| File version byte | DefleMask version | Notes |
|-------------------|-------------------|-------|
| `0x11` (17) | v9c (2013-06-09) | C64 introduced; single system byte `0x07` for both chip variants; `volIsCutoff` stored as 4-byte int |
| `0x15` (21) | v11.1 (2016) | 6581 variant moved to `0x17`; `volIsCutoff` stored as 1-byte char; `TOTAL_ROWS_PER_PATTERN` still 1 byte; arpeggio tick speed REMOVED |
| `0x18` (24) | v1.0.0 (2021+) | 6581 variant moved to `0x47`; `TOTAL_ROWS_PER_PATTERN` widened to 4 bytes; sample format gains name field + bits field; system mode bits (bits 7-8) formalized |

Changes that affect C64 extraction specifically:
- v0x11 → v0x15: `volIsCutoff` int→char (Furnace DMF importer branches on `ds.version < 0x11`).
- v0x11: waveform macro values were stored as 1-byte chars; v0x0e+ stores all macro values as 4-byte ints.
- Pulse width in the C64 instrument block is stored as a 0–100 percentage in the DMF binary; Furnace maps this to the 12-bit hardware range as `duty = (raw_byte * 4095) / 100`.
- Filter cutoff is stored as 0–100 percentage; Furnace maps to 11-bit hardware range as `cut = (raw_byte * 2047) / 100`.

---

## 3. DMF File Structure (C64 Relevant)

The `.dmf` file is zlib-compressed. After decompression:

```
16 bytes  ".DelekDefleMask." magic
 1 byte   file version
 1 byte   system (0x07 or 0x47)

VISUAL INFO
  song name, author (length-prefixed strings)
  highlight A, highlight B

MODULE INFO
  time base         (1 byte)
  tick time 1       (1 byte)   — speed 1 in ticks per row
  tick time 2       (1 byte)   — speed 2 in ticks per row
  frames mode       (1 byte)   0=PAL (50Hz), 1=NTSC (60Hz)
  using custom Hz   (1 byte)
  custom Hz value   (3 bytes ASCII decimal, e.g. "060")
  total rows/pattern (1 byte pre-v0x18, 4 bytes v0x18+)
  total rows in matrix (1 byte)
  [arpeggio tick speed: 1 byte REMOVED in v11.1/0x15]

PATTERN MATRIX
  3 channels × N_MATRIX_ROWS bytes (pattern indices per channel per order)

INSTRUMENTS DATA
  (see section 4)

WAVETABLES DATA
  N wavetables (each: 4-byte size + size×4-byte data values)

PATTERNS DATA
  Per channel:
    1 byte: CHANNEL_EFFECTS_COLUMNS_COUNT
    For each matrix row, for each pattern row:
      2 bytes: note   (1–12=C#..C, 100=NOTE OFF, 0=empty)
      2 bytes: octave (ignored when note=0 or note=100)
      2 bytes: volume (-1=empty; 0–15 for C64)
      CHANNEL_EFFECTS_COLUMNS_COUNT × (2-byte effect code + 2-byte effect value)
      2 bytes: instrument index (-1=empty)

PCM SAMPLES DATA
  (unused for standard C64 SID, only relevant for 6581 PCM variant)
```

Note encoding: octave 1 = hardware octave 0; note 12 = C (not C-sharp — the numbering wraps).

---

## 4. C64 Instrument Format (DMF Binary Layout)

Within the INSTRUMENTS DATA block, for STANDARD mode instruments on the C64 system, after the four common macro blocks (volume, arpeggio, duty/noise, wavetable), the C64-specific block is appended:

```
1 byte: Triangle Wave Enabled     (0/1)
1 byte: Saw Wave Enabled          (0/1)
1 byte: Pulse Wave Enabled        (0/1)
1 byte: Noise Wave Enabled        (0/1)
1 byte: Attack   (0–15)
1 byte: Decay    (0–15)
1 byte: Sustain  (0–15)
1 byte: Release  (0–15)
1 byte: Pulse Width               (0–100, percentage → hardware 0–4095 = (val * 4095) / 100)
1 byte: Ring Modulation Enabled   (0/1)
1 byte: Sync Modulation Enabled   (0/1)
1 byte: To Filter                 (0/1)  — route this voice through filter
1 byte: Volume Macro To Filter Cutoff Enabled  (volIsCutoff: 0/1)
1 byte: Use Filter Values From Instrument      (initFilter: 0/1)
  [FILTER GLOBALS — only meaningful when initFilter=1]
1 byte: Filter Resonance  (0–15)
1 byte: Filter Cutoff     (0–100, percentage → hardware 0–2047 = (val * 2047) / 100)
1 byte: Filter High Pass  (0/1)
1 byte: Filter Low Pass   (0/1)
1 byte: Filter CH2 Off    (0/1)  — disable voice 3 (for oscillator readback trick)
```

### Macro blocks (standard instrument, all systems)

Each macro is a sequencer that advances one step per tick. For C64:

| Macro | DMF field | SID register(s) affected | Notes |
|-------|-----------|--------------------------|-------|
| Volume | `volMacro` | `$D418` bits 0–3 (global master volume) | Warning: global, affects all voices |
| Arpeggio | `arpMacro` | frequency regs `$D4x0/$D4x1` | Signed int, offset 12; mode=0 relative, mode=1 fixed |
| Duty/Noise | `dutyMacro` | `$D4x2/$D4x3` (pulse width) | Relative or absolute depending on `dutyIsAbs` flag |
| Wavetable | `waveMacro` | `$D4x4` bits 4–7 (waveform select) | 4-bit bitmask: bit0=tri, bit1=saw, bit2=pulse, bit3=noise |

In Furnace's extended `.fur` format, additional C64-specific macros exist:
- **Cutoff** (`algMacro`): controls `$D415/$D416` filter cutoff (routed from `volMacro` when `volIsCutoff=1` in DMF)
- **Filter Mode** (`ex1`): controls `$D418` bits 4–6
- **Resonance**: controls `$D417` bits 4–7
- **Special** (`ex4`): gate bit (bit0) and test bit (bit1) of `$D4x4`; ring mod (bit2), osc sync (bit1) flags
- **Attack / Decay / Sustain / Release** (ex5–ex8): each controls the respective ADSR nibble in `$D4x5/$D4x6`

### `volIsCutoff` quirk

When the `Volume Macro To Filter Cutoff Enabled` byte is set in a DMF instrument, the volume macro does NOT control `$D418` master volume but instead drives the filter cutoff `$D415/$D416`. Furnace imports this by relocating the volMacro data into the `algMacro` slot and negating+offsetting by 18: `filtCut = -(vol_val - 18)`.

---

## 5. SID Register Map (Reference)

| Address | Name | Width | Content |
|---------|------|-------|---------|
| `$D400+n*7` | FreqLo[n] | 8 bits | Frequency low byte, voice n (0–2) |
| `$D401+n*7` | FreqHi[n] | 8 bits | Frequency high byte |
| `$D402+n*7` | PWLo[n]   | 8 bits | Pulse width low byte (bits 0–7) |
| `$D403+n*7` | PWHi[n]   | 4 bits | Pulse width high nibble (bits 8–11) |
| `$D404+n*7` | Control[n]| 8 bits | bit7=noise, bit6=pulse, bit5=saw, bit4=tri, bit3=test, bit2=ring, bit1=sync, bit0=gate |
| `$D405+n*7` | AtkDcy[n] | 8 bits | High nibble=attack (0–15), low nibble=decay (0–15) |
| `$D406+n*7` | StnRls[n] | 8 bits | High nibble=sustain (0–15), low nibble=release (0–15) |
| `$D415` | FCLo | 3 bits | Filter cutoff low 3 bits |
| `$D416` | FCHi | 8 bits | Filter cutoff high 8 bits (11-bit total: 0–2047) |
| `$D417` | FilterRes | 8 bits | High nibble=resonance (0–15), bits 0–2=voice routing (bit0=V1, bit1=V2, bit2=V3) |
| `$D418` | FilterMode | 8 bits | bit7=ch3off, bits4–6=filter mode (bit4=LP, bit5=BP, bit6=HP), bits0–3=master volume |

---

## 6. Global / Universal Effects (All Systems Including C64)

These effect codes work on every DefleMask/Furnace system and are available on all three C64 channels:

| Code | Value range | Meaning | SID register impact |
|------|------------|---------|---------------------|
| `00xy` | x,y: 0–F semitones | Arpeggio: cycle note→note+x→note+y per tick | `$D4x0/$D4x1` (frequency) |
| `01xx` | 0–FF | Pitch slide up at speed xx | `$D4x0/$D4x1` |
| `02xx` | 0–FF | Pitch slide down at speed xx | `$D4x0/$D4x1` |
| `03xx` | 0–FF | Portamento to next note at speed xx | `$D4x0/$D4x1` |
| `04xy` | x=speed, y=depth | Vibrato | `$D4x0/$D4x1` |
| `05xy` | compat only | Volume slide + vibrato (legacy compat) | |
| `06xy` | compat only | Volume slide + portamento (legacy compat) | |
| `07xy` | x=speed, y=depth | Tremolo | `$D418` (master volume) |
| `08xy` | x=left, y=right | Set stereo panning | Routing only (no SID register, software) |
| `09xx` | 0–FF | Set speed/groove pattern | Timing |
| `0Axy` | 0y=down, x0=up | Volume slide | `$D418` |
| `0Bxx` | 0–FF | Jump to order xx | Pattern matrix |
| `0Cxx` | 0–FF | Retrigger note | Gate bit in `$D404` |
| `0Dxx` | 0–FF | Jump to next order (break) | Pattern matrix |
| `0Exx` | (compat) | Same as 0Dxx in some versions | |
| `0Fxx` | 0–FF | Set speed 2 (or BPM if ≥`0x20`) | Timing |
| `80xx` | 0–FF | Set panning (00=left, 80=center, FF=right) | Software |
| `E5xx` | 0–FF (80=center) | Set fine pitch | `$D4x0/$D4x1` |
| `E6xy` | x=time, y=semitones | Quick legato | |
| `E7xx` | 0–FF | Macro release | Macro engine |
| `EAxx` | 0–FF | Legato | Frequency only (no re-trigger) |
| `ECxx` | 0–FF | Note cut after xx ticks | `$D4x4` gate bit clear |
| `EDxx` | 0–FF | Note delay (trigger note after xx ticks) | `$D4x4` gate bit set |
| `EExx` | | Send external command | |
| `EFxx` | | Fine pitch | `$D4x0/$D4x1` |
| `F0xx` | 0–FF | Set tick rate (BPM) | Timing |
| `F1xx` | 0–FF | Single-tick pitch slide up | `$D4x0/$D4x1` |
| `F2xx` | 0–FF | Single-tick pitch slide down | `$D4x0/$D4x1` |
| `FAxx` | 0y=down, x0=up | Fast volume slide | `$D418` |
| `FCxx` | 0–FF | Note release | Macro engine |
| `FDxx` | | Set virtual tempo numerator | Timing |
| `FExx` | | Set virtual tempo denominator | Timing |
| `FFxx` | | Stop song | |
| `9xxx` | 0–FFF | Set sample offset (PCM only; irrelevant for standard SID) | |

---

## 7. C64/SID-Specific Effects

These effect codes are only available on the C64 system. Source: `sysDef.cpp` `c64PostEffectHandlerMap` (Furnace), corroborated by `doc/7-systems/c64.md`.

| Code | Value range | Meaning | SID register(s) written | DIV_CMD |
|------|------------|---------|--------------------------|---------|
| `10xx` | 0–0F (bitmask) | **Set waveform.** bit0=triangle, bit1=saw, bit2=pulse, bit3=noise. Multiple bits = AND-mix of waveforms (noise cannot combine on real SID). | `$D4x4` bits 4–7 | `DIV_CMD_WAVE` |
| `11xx` | 0–64 | **Set coarse filter cutoff** (legacy; use `4xxx` instead). Maps 0–100 range to 0–2047 hardware range. | `$D415/$D416` | `DIV_CMD_C64_CUTOFF` |
| `12xx` | 0–64 | **Set coarse pulse width** (legacy; use `3xxx` instead). Maps 0–100 to 0–4095. | `$D4x2/$D4x3` | `DIV_CMD_STD_NOISE_MODE` |
| `13xx` | 0–0F | **Set filter resonance.** 0–15. | `$D417` bits 4–7 | `DIV_CMD_C64_RESONANCE` |
| `14xx` | 0–07 (bitmask) | **Set filter mode.** bit0=low pass, bit1=band pass, bit2=high pass. Combinations allowed (e.g. `03`=low+band, `05`=notch/bandstop). `00`=filter off. | `$D418` bits 4–6 | `DIV_CMD_C64_FILTER_MODE` |
| `15xx` | 0–FF | **Set envelope reset time** (ticks). The SID envelope is reset by briefly clearing the gate bit before a note-on. `xx` is the number of ticks the channel is silenced before the new note. `00` or a value ≥ song speed disables reset. | `$D4x4` gate bit timing | `DIV_CMD_C64_RESET_TIME` |
| `1Axx` | 0 or 1 | **Disable envelope reset for this channel.** `01`=disable, `00`=enable. | (gate-reset logic) | `DIV_CMD_C64_RESET_MASK` |
| `1Bxy` | x=0/1, y=0/1 | **Reset filter cutoff.** x≠0: reset on new note. y≠0: reset now. Restores cutoff to instrument's `initFilter` value. Not needed when the instrument's cutoff macro is absolute. | `$D415/$D416` | `DIV_CMD_C64_FILTER_RESET` |
| `1Cxy` | x=0/1, y=0/1 | **Reset pulse width.** x≠0: reset on new note. y≠0: reset now. Restores to instrument's `duty` value. Not needed when duty macro is absolute. | `$D4x2/$D4x3` | `DIV_CMD_C64_DUTY_RESET` |
| `1Exy` | x=0–6, y=0–F | **Change additional parameters (legacy).** x selects parameter: 0=attack (y 0–F), 1=decay (y 0–F), 2=sustain (y 0–F), 3=release (y 0–F), 4=ring mod (y 0/1), 5=osc sync (y 0/1), 6=disable channel 3 (y 0/1). Superseded by `20xy`/`21xy`. | `$D4x4`, `$D4x5`, `$D4x6` | `DIV_CMD_C64_EXTENDED` |
| `20xy` | x=0–F, y=0–F | **Set attack/decay.** x=attack, y=decay (4-bit each). | `$D4x5` | `DIV_CMD_C64_AD` |
| `21xy` | x=0–F, y=0–F | **Set sustain/release.** x=sustain, y=release (4-bit each). | `$D4x6` | `DIV_CMD_C64_SR` |
| `22xx` | 0–FF | **Pulse width slide UP** at speed xx (per tick). `00`=stop slide. | `$D4x2/$D4x3` every tick | `DIV_CMD_C64_PW_SLIDE` |
| `23xx` | 0–FF | **Pulse width slide DOWN** at speed xx. `00`=stop slide. | `$D4x2/$D4x3` every tick | `DIV_CMD_C64_PW_SLIDE` |
| `24xx` | 0–FF | **Filter cutoff slide UP** at speed xx. `00`=stop. | `$D415/$D416` every tick | `DIV_CMD_C64_CUTOFF_SLIDE` |
| `25xx` | 0–FF | **Filter cutoff slide DOWN** at speed xx. `00`=stop. | `$D415/$D416` every tick | `DIV_CMD_C64_CUTOFF_SLIDE` |
| `3xxx` | 0–FFF | **Set pulse width (fine).** 12-bit value, direct hardware range 0–4095. Spans effect codes `30`–`3F`. | `$D4x2` (low byte), `$D4x3` (high nibble) | `DIV_CMD_C64_FINE_DUTY` |
| `4xxx` | 0–7FF | **Set filter cutoff (fine).** 11-bit value, direct hardware range 0–2047. Spans effect codes `40`–`47`. | `$D415` (low 3 bits), `$D416` (high 8 bits) | `DIV_CMD_C64_FINE_CUTOFF` |

### Notes on register encoding

**Waveform (`10xx`)** maps directly to the upper nibble of the SID control register `$D4x4`. The lower nibble of `$D4x4` holds: test bit (bit3), ring mod (bit2), osc sync (bit1), gate (bit0). The effect only changes the waveform nibble; the other bits are preserved from channel state.

**Pulse width (`3xxx` / `12xx`):** The full 12-bit duty cycle writes to `$D4x2` (low byte) and `$D4x3` bits 0–3 (high nibble). Values 0–4095; hardware interprets as fraction of oscillator period. Pulse wave must be enabled (bit2 of `$D4x4`) to be audible.

**Filter cutoff (`4xxx` / `11xx`):** The 11-bit cutoff writes to `$D415` bits 0–2 (low 3 bits) and `$D416` bits 0–7 (high 8 bits). Range 0–2047. Filter routing (`$D417` bits 0–2) must route at least one voice for the filter to have effect.

**Slide effects (`22`–`25`):** Per-tick delta applied inside the `tick()` loop: `duty -= pw_slide; duty = CLAMP(duty, 0, 0xFFF)` for PW; `filtCut += cutoff_slide; filtCut = CLAMP(filtCut, 0, 0x7FF)` for cutoff. Both slides are channel-local for PW but GLOBAL (chip-wide) for cutoff (since the filter is shared).

**Envelope reset (`15xx`):** Before a note-on the engine clears the gate bit in `$D4x4` for `resetTime` ticks (with configurable AD/SR during reset period), then re-enables gate. This is necessary because the SID's envelope hardware does not restart if gate was already high. Disabling via `1Axx` avoids the silence gap but risks envelope not resetting properly.

---

## 8. Per-Frame Register Write Model

The DefleMask/Furnace SID player runs at the song's tick rate (typically 50Hz PAL or 60Hz NTSC, or custom). Each tick:

1. **Macro advance**: each active channel's sequencer macros (volume, arpeggio, duty, wave, cutoff, filter mode, resonance, ADSR, special/gate) advance by one step. Changed values are queued as register writes.
2. **Slide update**: if `pw_slide != 0`, duty is adjusted and `$D4x2/$D4x3` are written. If `cutoff_slide != 0`, `filtCut` is adjusted and `$D415/$D416` are written.
3. **Effect processing**: per-row effects are processed on the first tick of each row (with `EDxx` note delay shifting the note-on forward).
4. **Note-on / envelope reset**: if a new note starts, the pre-note reset logic fires (clearing gate → silence for `resetTime` ticks → set gate). Instrument ADSR, waveform, and duty are written to `$D4x5`, `$D4x6`, `$D4x4`, `$D4x2/$D4x3`.
5. **Frequency**: updated whenever pitch changes (portamento, vibrato, arpeggio, `01xx`/`02xx`), writes `$D4x0/$D4x1`.
6. **Filter**: `updateFilter()` writes `$D415`, `$D416`, `$D417`, `$D418` whenever cutoff, resonance, filter routing, or master volume changes.

The filter register `$D417` is written as: `(filtRes << 4) | (chan[2].filter << 2) | (chan[1].filter << 1) | chan[0].filter`.

The volume/filter mode register `$D418` is written as: `(filtControl << 4) | vol`, where `filtControl` is bits 4–6 (filter mode HP/BP/LP + CH3OFF at bit7).

---

## 9. Channel Structure and Ring Mod / Sync Routing

SID ring mod and oscillator sync use adjacent-channel coupling:
- Ring mod on channel n uses channel (n-1) mod 3 as the modulator.
- Osc sync on channel n resets when channel (n-1) mod 3 completes a cycle.
- Special case for channel 0: it uses channel 2 as the modulator (wrap-around).

In Furnace's platform state:
- `chan[i].ring` → bit2 of `$D4(i*7+4)` (`ring mod enable`)
- `chan[i].sync` → bit1 of `$D4(i*7+4)` (`osc sync enable`)
- `chan[i].test` → bit3 of `$D4(i*7+4)` (`test bit` — hard-mutes oscillator, stops ADSR, used for noise reset)
- `chan[i].gate` → bit0 of `$D4(i*7+4)` (`gate bit` — key-on/key-off)

---

## 10. Timing / Speed Model

```
time_base   — multiplier on speed values (normal = 1; double speed = 2, etc.)
tick_time_1 — speed 1: ticks per row for even rows (or all rows if single speed)
tick_time_2 — speed 2: ticks per row for odd rows (creates "groove" feel)
frames_mode — 0=PAL 50Hz, 1=NTSC 60Hz
custom_hz   — overrides frames_mode when enabled; 3-char ASCII decimal string
```

PAL = 50 timer interrupts/second (standard for European C64 music). NTSC = 60Hz. Custom Hz allows arbitrary rates (e.g. `025` for 25Hz half-speed).

One tick = one SID chip update at the configured frame rate. The speed values determine how many ticks each pattern row occupies, hence how many SID updates occur between note changes.

---

## 11. Notable Quirks and Compatibility Notes

### Waveform AND-mixing
When multiple waveform bits are set (e.g. `10xx` with `xx=03` = tri+saw), the SID hardware performs a logical AND of the two waveform outputs. On the 8580 this produces relatively predictable results; on the 6581 the behaviour is chip-revision-dependent and creates distinctive, noisy timbres.

### Pulse width PWHi byte encoding
Furnace's `c64.cpp` `tick()` function writes: `rWrite(i*7+3, (chan[i].duty>>8) | (chan[i].outVol<<4))`. Note that in some Furnace code paths the high byte of PW is OR'd with the output volume shifted to the upper nibble — this appears to be a quirk of one specific code path related to outVol; in standard paths it is `rWrite(i*7+3, chan[i].duty>>8)`.

### CH3OFF (`$D418` bit7)
Mutes voice 3's audio output while keeping its oscillator running. Used to suppress voice 3 when it acts as a modulator for ring mod or sync on voice 1 (or to read the oscillator/envelope at `$D41B/$D41C` without the audio being audible). In DefleMask this is an instrument-level flag (`Filter CH2 Off` — note: "CH2" in the DMF label refers to what Furnace calls channel index 2, i.e. the third voice).

### Envelope reset time
DefleMask's default is `resetTime=2` ticks for the gate-off period before a note. The Furnace documentation notes: "1 is short, but may exhibit SID envelope bugs; 2 is a good value." The `15xx` effect and `1Axx` per-channel disable give per-song and per-channel control.

### DefleMask `1Exy` legacy vs modern ADSR effects
The `1Exy` effect is described as legacy in Furnace documentation; `20xy` (AD) and `21xy` (SR) are the modern replacements. In Furnace source (`c64.cpp`), the `DIV_CMD_C64_EXTENDED` dispatch for `1Exy` has a `no1EUpdate` flag: when set, the ADSR register is NOT immediately written (only the channel state is updated, and the register write happens on the next note-on). This is for compatibility with some old DefleMask modules.

### Global filter vs per-channel
The SID chip has exactly one filter shared across all three voices. The filter cutoff/resonance/mode registers (`$D415`–`$D418`) are global. Furnace models per-voice `filter` routing (bit in `$D417`) but cutoff/resonance/mode are chip-wide state. The "Global parameter priority" chip config option controls which channel's macros win when multiple channels attempt to drive the filter simultaneously.

---

## 12. Instrument Macros: Summary of SID-Relevant Mappings

| Macro name | Internal field | Per-frame SID writes | Range |
|-----------|---------------|----------------------|-------|
| Volume | `volMacro` | `$D418` bits 0–3 (master vol, global) | 0–15 |
| Arpeggio | `arpMacro` | `$D4x0/$D4x1` frequency regs | semitone offsets (signed, offset=12) |
| Duty | `dutyMacro` | `$D4x2/$D4x3` pulse width | 0–4095 (absolute) or relative steps |
| Wave | `waveMacro` | `$D4x4` bits 4–7 waveform | bitmask 0–15 |
| Pitch | `pitchMacro` | `$D4x0/$D4x1` | fine pitch offset |
| Cutoff | `algMacro` (repurposed) | `$D415/$D416` filter cutoff | 0–2047 (absolute) or relative |
| Filter mode | `ex1` | `$D418` bits 4–6 | 0–7 bitmask |
| Resonance | `ex2` / resonance macro | `$D417` bits 4–7 | 0–15 |
| Special (gate/test/ring/sync) | `ex4` | `$D4x4` bits 0–3 | per-bit |
| Attack | `ex5` | `$D4x5` high nibble | 0–15 |
| Decay | `ex6` | `$D4x5` low nibble | 0–15 |
| Sustain | `ex7` | `$D4x6` high nibble | 0–15 |
| Release | `ex8` | `$D4x6` low nibble | 0–15 |

---

## Leads to Follow

1. **DefleMask manual PDF** (`https://www.deflemask.com/manual.pdf`) — 4.5MB binary PDF; could not be parsed to text by fetch tool. Contains user-facing effect documentation in section "Effects" + C64-specific section. Retrieve with a PDF parser to cross-check the effect descriptions against this document.

2. **Older DMF spec versions (0x09–0x10)** — Not fetched: `https://www.deflemask.com/DMF_SPECS_0x09.txt` etc. (if they exist). The Furnace DMF importer comments suggest versions 9–16 may exist. Could confirm when C64 was first introduced and whether the instrument format changed between 0x11 and 0x15 beyond the `volIsCutoff` int→char fix.

3. **DMP_SPECS.txt** (`https://www.deflemask.com/DMP_SPECS.txt`) — the instrument patch format (single instrument save). May contain additional insight into C64 ADSR encoding limits or instrument parameter constraints.

4. **DefleMask legacy source code** — Delek has not open-sourced DefleMask itself. The only open-source reference implementation is Furnace. Some community-written DMF parsers exist on GitHub (search `dmf parser C64`). Cross-checking a few would validate the instrument/effect byte interpretations.

5. **`1Exy` effect behaviour under `no1EUpdate`** — The exact conditions under which DefleMask set this flag are not fully documented. The Furnace `c64.cpp` source has a `no1EUpdate` field; worth reading the `setFlags()` function in that file to understand which compatibility modes trigger it. Relevant for modules made with DefleMask v11.x vs v1.0.0+.

6. **CIA-timed vs VBI-timed DefleMask modules** — The DMF `frames_mode` and `custom_hz` fields set the interrupt rate, but it is unclear whether DefleMask uses the CIA timer or VBI for its actual player IRQ. This matters for the Furnace `verify_all` / `siddump --writelog-per-irq` pipeline path. The `speed != 0` PSID field in exported SIDs is the discriminator.

7. **Furnace's DMF→SID export path** — `src/engine/export/` and `vgmOps.cpp` / `wavOps.cpp` should reveal how Furnace renders a DMF to a PSID binary: specifically the player stub it embeds, the CIA timer settings, and whether it emits a standard Furnace DMC-style play routine or the original DefleMask player. This is the critical bridge between the DMF authoring model and the actual `$D400` write stream.

8. **DefleMask's own SID player stub** — Legacy DefleMask exported `.sid` files embed a custom player; its disassembly would show the exact register-write order and any quirks (e.g. whether `$D418` is written before or after `$D417`, whether ADSR is written before or after the gate bit). This is what `siddump --writelog` would capture from real DefleMask-exported SIDs.
