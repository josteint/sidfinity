# Ubik's Musik — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

Ubik's Musik (a.k.a. Ubik's MusiK), a C64 music editor by **Dave Korn ("Ubik")**,
published by **Firebird**, 1987. 288 HVSC #84 tunes; 0 migrated. Compiled player
maps to fixed base **$C600** (~7 KB PRG). **No public source or annotated disassembly
exists** — but the player binary is byte-stable across tunes, so the structure was
recoverable from corpus analysis (this sweep includes an annotated disasm of the
canonical player from `Fire_Breath.sid` under `src/`).

## File index

| Topic | File | Reliability |
|---|---|---|
| Per-frame write model + effect register semantics + tools | `cluster_write_model_and_tools.md` | secondary (binary) |
| ↳ annotated canonical-player disasm ($C600–$CF40) | `src/fire_breath_c600_disasm.txt` | primary |
| Player binary structure + source hunt + biography | `cluster_editor_re_and_source.md` | secondary |
| HVSC corpus / address clusters / scene timeline | `cluster_corpus_and_scene.md` | primary (DB) / secondary |

## What's solved

**Player layout ($C600 canonical)** — three agents converged independently:
- `$C600` init: `CLC; ADC #$80` (set active flag) + store subtune# (0–25) + zero
  `$D400-$D41F` + RTS. `$C603` play: saves banking (`$01=$36`), `JSR $C666`, restores.
- **`$C666` = main play body / multi-song select entry** (the PRG2SID detection target,
  pattern `AD ?? ?? 30 03 D0 22 60 18 29 7F A2`). Stable code regions: `$C666–$C71A`
  (main loop), `$C7B5–$C821`, `$C824–$CDFF` (effects block), drum table at `$CF00`.
- **⚠ One SID voice per `play()` call** — a self-modifying `LDX` at `$C672` rotates the
  voice counter 2→1→0 then resets. This is the root of the "high rastertime" reputation
  AND a Trap-C-relevant dispatch detail (the per-`play()` write set is one voice, not all
  three — the full 3-voice frame spans 3 IRQs). **Confirm the verdict path carefully.**

**Per-frame write model** (from binary analysis of `Fire_Breath.sid`):
- **Voice update order 2→1→0** (X counts down, BPL loop).
- **Normal frame** (per in-progress voice): vibrato step → freq-lo/hi; PWM step → PW-lo/hi.
  Then once: `$D418`, `$D416`, `$D417`. (`$D415` filter-lo not observed — possibly unused.)
- **Note-start frame**, per voice with a new note: `$D404,Y=0` (gate clear) → `$D406,Y=SR`
  → `$D405,Y=AD` → `$D403,Y=PWhi` → `$D402,Y=PWlo` → `$D404,Y=ctrl|gate` → `$D400,Y=freqlo`
  → `$D401,Y=freqhi`. Gate-clear and gate-set in the SAME frame; no test-bit hard-restart.

**Distinctive effects** (register semantics — what the rebuild must reproduce):
- **Logarithmic vibrato**: delta = freq(note) − freq(note−1 semitone) → auto-scales with
  pitch. Direction bit `$C771,X`, half-period `$C76B,X`.
- **PWM**: triangle sweep of PW regs; per-instrument speed/direction/limits.
- **Echo** (the famous one): NOT a delay line — it's a **sustain-level staircase**. The SR
  sustain byte at `$C783,X` oscillates per **note event** (not per frame); writes `$D406,Y`
  at note trigger.
- **Waveform swap**: per-note ctrl override from a table at `$C507+Y`.
- **Wavetable drums (8 fixed)**: global table at **`$CF00`**; two entry types — 2-byte
  `(ctrl, freqhi)` waveform-change (bit7=1) and 3-byte `(ctrl, flo_delta, fhi_delta)`
  pitch-slide (bit7=0); `$FF` end-marker. Each drum = a start offset into `$CF00`; writes
  `$D401,Y`+`$D404,Y` each frame during decay.

**Sequence stream**: dominant command `$F3 nn` (tempo change), `$FF` = end-of-sequence.

**SFX game API** ($C68F handler): when `$C71D` nonzero with bit7 clear, scans `$C732,X`
per voice for one-shot SFX — the documented "2-voice music + 1-voice SFX" mode.

**SIDId**: single signature for all 288 tunes (no sub-versions), anchored on the
gate-clear `STA $D404,Y` (`99 04 D4`) subroutine. Both cadaver/sidid and WilfredC64/
player-id use it. **One player, no version fork.**

## Corpus shape (288 tunes — all PSID v2, all VBI/speed=0, zero CIA)

170 single- / 118 multi-subtune (up to 23 subtunes). The address variety is
**relocation of one player**, not engine variants:

| Cluster | init | play | Count | Note |
|---|---|---|---|---|
| A canonical | $C600 | $C603 | 120 | standard; song# in A |
| B/D/E multi-song | $C600/$CE../$B.. | **$C666** | ~70 | same player, song-select entry; data fills different init ranges |
| C / G patches | $C601 / $Bxxx | $C64E/$C666 | ~24 | minor entry-point patches (Eeben Aleksi, Marc François) |
| F fully relocated | varies | non-$C6xx | 62 | same player, different base (Japmaster/Deadman) |
| play=0 / misc | — | $0000 | 12 | one-offs to audit |

~200/288 fall under two structural models (A and the $C666 family). Top composers:
Waz/Pilkington (56), Stormont_John (45), Noise_of_SID (30), Lyon_Legend (18),
Japmaster (14). Used in many Firebird games (Thrust II by Korn himself, Joe Blade 2,
International 3D Tennis, Tim Follin's Agent X II stage 1). Span 1987–2018, period peak
1987–1991. No STIL entries.

## What remains (migration-phase RE)

The player CODE structure is mapped; the **DATA encoding is the open work**:

- **Disassemble a canonical $C600 tune** (the `src/` disasm is a head start) to recover:
  the **instrument table layout** (`$C73B–$C7B4` / `$C2xx–$C5xx` — which offsets hold
  AD/SR/vibrato/PWM/echo params), the **note/duration byte encoding** in sequences, the
  **26-song pointer-table stride**, and the **8-drum→$CF00-offset table**.
- **Resolve the one-voice-per-play() dispatch vs the write-stream verdict** — since each
  `play()` updates a single voice, the 3-voice frame spans 3 IRQs; verify whether the
  flat Mode-1 path or `--writelog-per-irq` is correct here. (All tunes are VBI/speed=0.)
- **Confirm `$D415` is unused** and that the ~100 scattered-address tunes (cluster F) are
  pure relocations, not modified players.
- **Audit the 12 play=0 / misc tunes** before counting them in scope.

## Top leads (if migration needs more; CSDb 503 this session)

1. **The Ubik's Musik editor disk (D64)** — CSDb #39950 + Gamebase64; the editor's
   data-entry code is the closest thing to a format spec. Retry CSDb / archive.org.
2. **PRG2SID v1.26** source — the only tool with explicit Ubik handling (`$C666` scan +
   stub injection); its detection code documents the entry conventions.
3. **More canonical disassemblies** across the $C666 family + a cluster-F relocated tune —
   to confirm relocation-only and pin the data-pointer table.

Full provenance in each file + `provenance_log.md`.
