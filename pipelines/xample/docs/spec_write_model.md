# X-Ample / Compotech — Per-Frame $D400–$D418 Write Model

## Provenance
- Source: `research.md` (sibling-agent synthesis), HVSC #84 DB queries (`hvsc84.db`)
- Author: synthesis agent, 2026-06-13
- Method: GATHER + SYNTHESISE only — no siddump, no disasm, no py65
- Labels: DOCUMENTED = from research.md or confirmed DB observation;
          INFERRED = logical deduction from DB patterns or general C64 convention;
          OPEN = requires disassembly / writelog capture to confirm

---

## 1. Verification Mode Assignment

| Variant | Mode | Rationale |
|---|---|---|
| Layout A/B/C (standard Compotech/XTracker) | **Mode 1 — per-frame instruction sequence** | Non-zero play_addr; 50 Hz VBI-driven; tracker music |
| Reflextracker / CIA-driven | **DEFERRED** (likely Mode 2 or excluded) | play_addr=0; CIA-timer-driven; 137 SIDs; see §4 |
| X-Ample_Digi sidid variant | **DEFERRED** (likely Mode 2 — cycle-exact) | CIA sample playback; $DD04/$DD05 timer; see §4 |

---

## 2. Structural Architecture (DOCUMENTED + INFERRED)

### 2.1 Voice Dispatch
DOCUMENTED (from `research.md`): The player iterates three voices via a **bitmask**,
calling a per-voice subroutine for each active voice. The SID register base
advances by **+7 per voice**:

```
Voice 1: SID base $D400  (registers $D400–$D406)
Voice 2: SID base $D407  (registers $D407–$D40D)
Voice 3: SID base $D40E  (registers $D40E–$D414)
```

This is the standard C64 SID voice stride and matches the hardware register map.

INFERRED: The bitmask is likely a 3-bit value where bit 0 = voice 1 active,
bit 1 = voice 2 active, bit 2 = voice 3 active. This is a common C64 tracker
convention (cf. DMC, Future Composer). OPEN: actual bitmask encoding and
ZP/RAM storage address.

### 2.2 Per-Voice Subroutine
DOCUMENTED (from `research.md`): Each voice is processed by a per-voice subroutine.

INFERRED per C64 tracker convention: the subroutine likely:
1. Loads voice-specific pattern/sequence position
2. Reads note/command from the pattern stream
3. Updates SID registers for that voice (freq lo/hi, pulse lo/hi, waveform+ADSR)
4. Advances the pattern pointer

OPEN: the exact subroutine entry, argument passing (ZP index? X register?
Y register? absolute address table?), and return convention.

### 2.3 Write Order Within a Frame
OPEN: exact write order unknown without disassembly. General tracker conventions
suggest the following is likely but NOT confirmed:
- INFERRED: ADSR writes ($D405/$D406 per voice) happen at note-on
- INFERRED: Frequency writes ($D400/$D401 per voice) happen every frame
- INFERRED: Waveform/gate register ($D404 per voice) gate-on and gate-off
  writes are split across frames (standard C64 gate-edge convention)
- INFERRED: Pulse width ($D402/$D403 per voice) written when pulse waveform active
- INFERRED: Filter ($D415–$D417) and master volume ($D418) written from
  some global or per-song table

The ORDER within a frame (voice 1 before voice 2 before voice 3, or interleaved)
is OPEN — the bitmask iteration determines voice order.

---

## 3. SID Register Map (DOCUMENTED stride; details OPEN)

```
Per-voice block (×3, stride +7):
  BASE+0  $D400/07/0E  Freq lo
  BASE+1  $D401/08/0F  Freq hi
  BASE+2  $D402/09/10  Pulse width lo
  BASE+3  $D403/0A/11  Pulse width hi
  BASE+4  $D404/0B/12  Waveform + gate + test + ring + sync
  BASE+5  $D405/0C/13  Attack / Decay
  BASE+6  $D406/0D/14  Sustain / Release

Global (voice-independent):
  $D415   Filter cutoff lo (bits 0-2)
  $D416   Filter cutoff hi
  $D417   Filter resonance + routing
  $D418   Master volume + filter mode
```

---

## 4. Effect Write Model (all OPEN — inferred from comparable trackers)

The following effects are INFERRED as plausible given the engine's era
(1989–1995) and the comparable DMC/FC effect sets. All are OPEN until
confirmed by disassembly and writelog capture.

### 4.1 Likely Effects (INFERRED, high confidence)
- **Arpeggio:** Multiple note frequencies within one frame or across successive
  frames. Would produce repeated $D400/$D401 writes per frame at different values.
- **Vibrato:** Frequency modulation via a sine/triangle-approx table. Produces
  $D400/$D401 writes with small signed offsets from the base frequency.
- **Portamento / Glide:** Frequency slides between two notes. Produces
  $D400/$D401 writes incrementing/decrementing toward the target over N frames.
- **Pulse-width modulation (PWM):** Produces $D402/$D403 writes each frame
  sweeping between two bounds.
- **Filter sweep:** Produces $D415/$D416 writes each frame.
- **Master volume ramp / song-end fade:** Produces $D418 writes. INFERRED from
  the engine's documented fade capability (Compotech trackers typically include
  song-end volume fade).

### 4.2 Effects of Unknown Presence (OPEN)
- Ring modulation / sync enable (waveform register bit manipulation)
- Hard restart (test bit: $D404 bit 3)
- Sample / digi voice (for non-Reflextracker members, if any)
- Per-note volume (unlikely in this era, but OPEN)
- Note-length commands vs. duration bytes

---

## 5. Multi-Subtune Model (OPEN)

The HVSC DB shows X-Ample SIDs with 1–24 subtunes (median: 1, but many
have 5–14). The subtune selection mechanism is OPEN:

INFERRED: The PSID `init` call passes the subtune number (0-based or 1-based)
in the accumulator (A register) — standard PSID calling convention. The init
stub stores this and selects the corresponding song data base addresses from
a pointer table.

OPEN: the pointer table format, whether voices can have independent sequence
loops, and whether subtune switching resets ZP state.

---

## 6. Init vs. Play Stream (Mode 1 trichotomy applicability)

For Layout A/B standard members:
- INFERRED: init performs a chip reset + state initialisation, then returns.
  Play is called repeatedly at 50 Hz.
- INFERRED: the init sequence likely includes writing $D418=$0F (master vol
  on, filter off — standard C64 tracker init) + ADSR priming + voice gate-off.
- OPEN: whether the composer should emit a `universal_reset` init (as in FC
  standard) or reproduce the engine's original init write sequence.
- Recommendation: after writelog capture, compare init streams and apply the
  **trichotomy** (`compare_instruction_stream(mode='trichotomy')`) to decide.
  See `docs/the_trichotomy.md`.

---

## 7. CIA Timer / PSID `speed` Bit

- INFERRED: the standard Layout A/B/C members use the PSID `speed` bit = 0
  (VBI 50 Hz), standard for Compotech tracker music.
- OPEN: some SIDs may use CIA timer for tempo variation or multispeed playback.
  Check the PSID `speed` field on canary SIDs; if non-zero, apply the
  `writelog_per_irq_capture` path (as for Human_Race CIA tunes).

---

## 8. Reflextracker / X-Ample_Digi — Mode-2 Deferred

**Reflextracker (137 SIDs, all `play=$0000`):**
- DOCUMENTED: CIA-timer-driven; no VBI play vector.
- These are **Mode-2 (cycle-relevant)** or require a CIA-sample pipeline
  analogous to Chimera.
- RECOMMENDATION: Exclude from the initial migration scope. Add to
  `tools/excluded_sids.json` with reason:
  `"Reflextracker: CIA-driven; play_addr=0; requires Mode-2 digi pipeline or separate CIA-timer player migration. Defer until X-Ample standard (Mode-1) is complete."`
- QUANTIFICATION: 137 / (380 + 137) = **26% of the combined X-Ample family**
  is Reflextracker. The remaining 380 X-Ample SIDs are the standard target.
  Of those 380, approximately 14 (3.7%) have `play=$0000` or other anomalous
  addresses (only 1 confirmed: `Hawkeye_II.sid`, Schneider, play=$0000).

**X-Ample_Digi sidid variant:**
- DOCUMENTED (sidid taxonomy): uses CIA $DD04/$DD05 for sample playback.
- INFERRED: these are within the `X-Ample` engine label in the DB (not
  separately labelled).
- OPEN: which specific SIDs in the 380 X-Ample set carry digi samples.
  The only confirmed play=$0000 X-Ample entry is `Hawkeye_II.sid` (1 SID).
  RECOMMENDATION: Defer digi SIDs to Mode-2 after the tracker subset is done.

---

## 9. Write-Log Capture Recipe (when disasm is ready)

1. Pick a single-subtune Layout-A canary (e.g. `Castlevania_64_Mixes.sid`,
   subtune 0).
2. `siddump --writelog hvsc84/.../canary.sid > tmp/xample_orig.writelog`
3. After building the USF + rebuilt SID:
   `siddump --writelog hvsc84/.../canary.sidfinity.sid > tmp/xample_rebuilt.writelog`
4. `python3 tools/find_first_divergence.py tmp/xample_orig.writelog tmp/xample_rebuilt.writelog --subtune 0`
5. For CIA-timed subtunes (PSID speed != 0):
   `siddump --writelog-per-irq … > tmp/xample_orig_irq.writelog`
   and compare with `writelog_per_irq_capture` path.
6. Declare PASS when the flat `(reg, val)` stream matches at full songlength.
