---
source_url: local: pipelines/gmc/docs/research.md + local: pipelines/dmc/docs/ (research.md, tnd_dmc_tutorial.txt, dmc_sector_commands.md) + local: pipelines/dmc/v4/disassembly.s + local: .claude/memory/project_dmc.md
fetched_via: in-repo synthesis (no external fetch)
fetch_date: 2026-06-13
author: sidfinity research wave (Claude, 2026-06-13)
content_date: 2026-06-13
reliability: DOCUMENTED where directly from GMC research.md or TND/DMC confirmed facts; INFERRED from GMC→DMC kinship + author identity; OPEN where byte-level facts are unknown
---

# GMC Per-Frame $D400-$D418 Write Model

This document describes the expected per-`play()` SID register write sequence
for GMC.  It is the basis for the per-frame instruction-sequence (Mode-1)
verification target once a canary is migrated.

---

## 1. Timing model

| Property | Fact | Confidence |
|----------|------|------------|
| VBlank IRQ (50 Hz PAL) | INFERRED from DMC V4 (same author, same entry at $1003) | Medium-High |
| Duration unit | One "tick" = one `play()` invocation × (speed+1) | INFERRED — TND tutorial §2.5.3 gives the formula `L = (SPD+1) × ΣDURs` for DMC 4; same formula expected for GMC |
| Speed field | Per-subtune, in the tune table | INFERRED |
| CIA / multispeed | OPEN — DMC V4 has CIA variants; GMC may not, but unknown | OPEN |

**Verification path (Mode 1):** flat `compare_instruction_stream` over the
play-stream (init prefix dropped by trichotomy).  This is the same as DMC V4
(see `feedback_verification_modes.md` + `project_dmc.md`).

---

## 2. Per-frame write sequence (INFERRED from DMC V4 kinship)

DMC V4's per-frame write order is fully established in `pipelines/dmc/v4/disassembly.s`:

```
for voice in [V1, V2, V3]:
    freq LO  → $D400/$D407/$D40E
    freq HI  → $D401/$D408/$D40F
    PW LO    → $D402/$D409/$D410
    PW HI    → $D403/$D40A/$D411
    ctrl     → $D404/$D40B/$D412
global:
    filter cutoff → $D416
    res|route     → $D417
$D418 written ONLY at: init, and at note-init of a filter-using instrument
```

GMC is expected to follow a similar order for these reasons:
- Same author (Brian/Graffity), same player architecture.
- The TND tutorial documents the same SID register model (ADSR, PW, wave,
  filter) for both DMC and, implicitly, GMC.
- Same two-level Tracks→Sectors hierarchy implies the same per-voice processing
  loop driven by the same SID write path.

**OPEN:** whether the exact register write ORDER within a frame matches DMC V4
(e.g. whether filter writes come before or after voice writes, whether $D418
is written every frame or only at note-init).  This must be confirmed from the
GMC disassembly.

---

## 3. Note lifecycle (INFERRED)

Based on DMC V4 (from `project_dmc.md` "Note lifecycle"):

**DMC V4 established:**
- Fetch frame: writes only $08→ctrl + $0F→AD + $0F→SR (hard-restart test-bit preset).
- Frame 2: real AD/SR written; PW, filter, vibrato initialised; wave stepped; freq+PW+ctrl written.
- Gate on ≥3 frames (guard counter); non-holding instruments then get gate-mask $FE → tail rides SID release.
- Holding: gate off at duration ctr == 1 (+ AD=$00, SR=$00).

**GMC expectation (INFERRED):**
- Hard-restart (test-bit method) is likely present — DMC V4's hard-restart
  is marked in research.md as "shared with JCH player", indicating it was
  already present in the era.  The TND tutorial says DMC 5 has "proper
  hardrestart ... implemented in the player's coding", implying DMC 4 (and
  thus likely GMC) also had it.
- HLD field in GMC's sector step may correspond to the "holding" behaviour
  (gate stays until duration ctr == 1), or may be a separate hold-duration
  override.  OPEN.

---

## 4. Per-register write model (DOCUMENTED vs INFERRED vs OPEN)

### $D400/$D407/$D40E — Freq LO (voice 1/2/3)
- **INFERRED:** written every frame from the freq table (96 entries, 8 octaves
  × 12 notes) + any vibrato/glide offset accumulator.
- **OPEN:** whether the freq table is a standard PAL 16-bit table split into
  LO/HI arrays (as in DMC V4: $1647/$16A7), or a different encoding.

### $D401/$D408/$D40F — Freq HI (voice 1/2/3)
- **INFERRED:** same as above (parallel HI array).

### $D402/$D409/$D410 — Pulse Width LO (voice 1/2/3)
- **INFERRED:** written every frame when the instrument uses PW (pulse mode).
  The instrument record's PW fields drive a PWM oscillator.
- **OPEN:** exact PWM algorithm — DMC V4 uses 6-phase PW-speed nibbles + a
  direction-flip at bounds; GMC may use a similar or simpler model.

### $D403/$D40A/$D411 — Pulse Width HI (voice 1/2/3)
- **INFERRED:** written together with PW LO.

### $D404/$D40B/$D412 — Control (voice 1/2/3)
- **INFERRED:** driven by the wave table (ctrl byte per step, stepped each
  frame).  Gate bit is ANDed with a per-voice gate mask.
- **INFERRED:** SWITCH/CONT command ($7D in DMC V4) toggles the gate-mask
  bit, enabling tie/legato.
- **OPEN:** exact wave table encoding (see OPEN-1 in `spec_extraction_plan.md`).

### $D405/$D40C/$D413 — AD (voice 1/2/3)
- **INFERRED:** written once per note at the hard-restart frame (preset $0F)
  and then at frame 2 (real AD from the instrument record byte 0).
  **DOCUMENTED for DMC V4** (disassembly.s); GMC should match.

### $D406/$D40D/$D414 — SR (voice 1/2/3)
- **INFERRED:** written at frame 2 (real SR from instrument record byte 1).
  The APM and/or VOL sector-step command may override the sustain nibble
  (analogous to DMC V4's $F0-$FF VOL command which replaces the sustain nibble).
- **OPEN:** whether GMC's APM maps to sustain override, or to $D418 volume.

### $D415 — Paddle X (not used)
- **INFERRED:** not used (same as DMC V4).

### $D416 — Filter cutoff
- **INFERRED:** written every frame (single global filter, driven by the
  filter definition's step envelope).  In DMC V4 written unconditionally
  each frame to $D416.
- **OPEN:** whether GMC writes $D416 every frame or only on filter-active frames.

### $D417 — Resonance + voice route
- **INFERRED:** written every frame (hi nibble = resonance from filter def;
  lo nibble = accumulated voice-route bits).  In DMC V4 the $1018 shadow
  is NOT cleared by init — this is the `init.sid` priming candidate.
- **OPEN:** whether GMC has the same $D417-shadow leftover quirk.

### $D418 — Volume + filter mode
- **INFERRED:** written at init (master volume from tune table) and at
  note-init of filter-using instruments (mode bits set).  NOT written every
  frame in DMC V4.
- **OPEN:** whether GMC's APM field causes $D418 writes mid-song (i.e. if
  APM = amplitude and controls $D418 per-note or per-frame, this changes the
  write density significantly).

---

## 5. Sector-step write effects (DOCUMENTED command names; byte encoding OPEN)

From research.md (field names are DOCUMENTED; byte ranges are OPEN):

| Field | Write effect | Confidence |
|-------|-------------|------------|
| Note (0-95) | $D400/$D401 freq lookup; $D404 ctrl (hard-restart + wave); $D405/$D406 AD/SR | INFERRED |
| DUR | Sets duration counter (ticks until next note); no direct SID write | DOCUMENTED name; byte range OPEN |
| SND | Selects instrument record; takes effect at next note's init | DOCUMENTED name; byte range OPEN |
| APM | Likely overrides sustain nibble ($D406) or sets $D418 volume | DOCUMENTED name; effect OPEN |
| GLD | Sets glide/slide parameters; affects $D400/$D401 freq accumulator | DOCUMENTED name; byte range OPEN |
| HLD | Controls gate-off timing; affects $D404 ctrl gate bit | DOCUMENTED name; effect OPEN |
| CONT | Suppresses hard-restart (tie); gate bit stays set | DOCUMENTED name; byte encoding OPEN |
| END | Advances track pointer to next sector; no SID write | DOCUMENTED name; byte value OPEN |

---

## 6. Likely Mode-1 flat verification target

Based on DMC V4's established pattern and the structural correspondence:

**Expected play() write sequence per frame:**
```
V1: freq_lo, freq_hi, pw_lo, pw_hi, ctrl
V2: freq_lo, freq_hi, pw_lo, pw_hi, ctrl
V3: freq_lo, freq_hi, pw_lo, pw_hi, ctrl
global: $D416 (cutoff), $D417 (res|route)
$D418 sparse: only at note-init of filter instruments + init
```

**OPEN:** the exact order (e.g. whether freq/PW precede ctrl, and whether
$D416 comes before or after voice 3's ctrl) must be read from the GMC
disassembly.  In DMC V4 this order is confirmed in `disassembly.s`.

**Verification mode:** flat `compare_instruction_stream`, init prefix dropped
by `mode='trichotomy'`, play-stream compared frame-by-frame.

---

## 7. Init write model

At `init($1000, A=subtune)`:

- **INFERRED:** sets per-voice track pointers from the tune table.
- **INFERRED:** writes master volume to $D418 (mode|vol byte from tune table
  byte 7 in DMC V4; analogous in GMC).
- **INFERRED:** NOT clearing some state (the DMC V4 $D417 shadow at $1018
  is a known leftover — see `project_dmc.md`; GMC may have the same or
  similar).
- **USF init.sid block** should carry: master_vol + any $D417 leftover that
  must be primed.  Follow the `docs/the_trichotomy.md` protocol.

---

## 8. Effect summary for USF schema

These are the USF-representable effects expected in GMC, in order of
confidence.  Each maps to an existing DMC USF schema field unless marked NEW:

| Effect | USF field (DMC) | GMC confidence |
|--------|----------------|----------------|
| Note + freq table lookup | note / freq_table | INFERRED |
| ADSR envelope | envelope_prime (init.sid) + instrument AD/SR | INFERRED |
| Duration counter | duration | INFERRED |
| Instrument select | instrument ref | INFERRED |
| Wave table (ctrl + freq parallel) | wave_ctrl_programs + wave_freq | INFERRED |
| PW oscillator (6-phase speed nibbles OR simpler) | pwm | INFERRED |
| Vibrato (delay + width + ramp) | vibrato | INFERRED |
| Glide/slide | glide | INFERRED |
| Filter envelope (step-based) | filter_programs | INFERRED |
| Tie/legato (CONT) | gate_toggle | INFERRED |
| Volume/sustain override (APM) | vol_override OR new APM field | OPEN |
| Hold gate extension (HLD) | holding FX flag OR new HLD field | OPEN |
| Hard-restart gate control | gate_mode | INFERRED |
| Drum mode (abs freq hi) | drum / noise_attack | INFERRED |

**Schema discipline note:** before adding any new USF field for APM or HLD,
exhaust the derivation path per `feedback_schema_addition_discipline.md`.
APM likely maps to the existing vol_override mechanism.  HLD likely maps to
the existing `holding` FX flag.  Only add new fields if the write-log shows
effects that existing USF cannot represent.

---

## Leads to follow

1. **SIDid signature bytes** — read the sidid.cfg entries for `GMC/Superiors`
   and `GMC_V2.0/Superiors`.  The opcode sequences constrain the player
   structure and may answer OPEN-3 (track transpose) and OPEN-4 (V1 vs V2).
   Source: `https://github.com/cadaver/sidid/blob/master/sidid.cfg`.

2. **HVMEC GMC binaries** — the HVMEC page (hvmec.altervista.org) lists
   GMC V1.0, V1.6, V2.0.  The editor binaries contain the player; carving
   the player (as was done for DMC in `dmc4editor_embedded_player_notes.md`)
   gives the canonical player binary for seed_disassembly.

3. **CSDb #7268** — the GMC CSDb release page.  May carry download links and
   community comments on the format.

4. **FUNET/zimmers mirror** — the zimmers.net CBM archive
   (`http://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/`) may carry
   GMC editor binaries alongside the DMC versions already documented in
   `csdb_dmc_tools_survey.md`.

5. **HVSC canary selection** — query `hvsc84.db` for `engine LIKE 'GMC%'`,
   sort by songlength_s DESC, pick a mid-length single-subtune V1.0 member
   as the first canary.  Run `seed_disassembly.py` on it to get the
   annotatable skeleton.

6. **APM semantics** — search CSDb / scene-forum threads for "GMC APM" or
   "Game Music Creator amplitude".  This is the most GMC-specific effect and
   the hardest to infer from DMC alone.

7. **HLD semantics** — similarly, search for "GMC HLD" or "hold duration".
   If HLD is a per-step hold-duration override it would require a new USF
   field; if it is just the "holding" gate-extension mechanism it maps to the
   existing FX flag.

8. **Verify packer-patched operands** — probe 10 diverse GMC SIDs (across
   V1.0 and V2.0) and check whether the instrument table and wave table
   addresses are constant or per-SID.  If variable → dataflow extraction
   (same as DMC V4); if constant → fixed-offset extraction (simpler but
   fragile for edge members).
