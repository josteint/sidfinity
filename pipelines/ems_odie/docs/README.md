# EMS (Electronic Music System) / Odie — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

EMS — "The Electronic Music System" — a native C64 SID editor by **Sean Connolly
("Odie") of Cosine** (UK; also Sonix Systems), active from 1989; V7.03 released 18 Jan
1997. 196 HVSC #84 tunes (engine string `EMS/Odie`); 0 migrated. Player base $1000, play
$1003. **Best-documented of the obscure editors** — the official V7.03 disk's **7 bundled
HELP files were recovered and decoded from PETSCII** (saved verbatim in `src/`), giving the
complete feature/command model + the 15 instrument parameters.

## File index

| Topic | File | Reliability |
|---|---|---|
| Per-frame write model + the 3 version generations + Odie subgroups | `cluster_write_model_and_versions.md` | secondary (binary) |
| Editor + complete feature model + Cosine provenance | `cluster_editor_and_cosine.md` | primary (help files) |
| ↳ verbatim decoded HELP files (general/track/sequence/sound/waveform/arp/filter) | `src/*.txt` | primary |
| HVSC corpus / address clusters / scene + related Odie strings | `cluster_corpus_and_scene.md` | primary (DB) |

## What's solved

**Complete feature model** (from the bundled HELP files — `src/`):
- **3-level hierarchy: Tracks → Sequences → Notes+Commands.** Up to 8 tunes/module, 3
  voices, 96 sequences (≤$FF bytes each), note duration ≤$40.
- **Track commands**: `rst`, `stop`, `fad`, `tmp` (tempo $02–$0D), `tr+`/`tr-` transpose,
  `it` (instrument transpose, wraps), `rep` (repeat next seq N×), sequence numbers $00–$5F.
- **Sequence commands**: notes C-0..B-7, `vol` (volume+filter+resonance), `^` glide, `event`
  (screen-sync counter), `hdnon`/`hupon` (oscillating glide), `arpon`/`vibon`, `arp??`,
  `sfx??`, `dur??`, `filXXX`, `slion/off`, `cycon/off`, `porton/off`, `sus`/`gat`, `nrep??`.
- **15 instrument parameters**: firstwf, wf+gateoff (5-bit table idx + 3-bit gateoff period),
  AD, SR, pulse lo/hi, pulse rate, pulse delay, pulse min/max, vibrato delay, osc-delay+
  vibrato-depth, vibrato speed, **soundtype** (0=vibrato/1=arp/2=osc-glide-dn/3=osc-glide-up/
  5=hi-freq), filter high-byte, filter table, arp override ($FF=sequence-controlled).
- **24 waveform tables / 24 arpeggio tables / 24 filter tables** ($00–$17), all loop/terminate.
- **Vibrato is amplitude-compensated** across the frequency range (non-trivial math). **Glide**
  uses a division routine (9–12 scanlines on first frame only). **Filter is never sped up by
  multispeed** (stated in HELP, confirmed structurally).
- **Player API**: 5-entry JMP table at base (init / play / engine / clear / fade); relocatable.

**Per-frame write model** (V7.03 dominant): voice order **V3→V2→V1 (X=2,1,0)** — voice 0
handled inside the combined global-filter JSR. Per voice: freq-lo/hi → PW-lo/hi → ctrl
($D4xx gate). Global after all voices: `$D418` (master vol + filter routing), `$D415`,
`$D416`, `$D417`. Hard-restart inserts a gate-off frame before gate-on.

**Three version generations** (distinct sidid sub-sigs = real player differences):
- **V7.03** (dominant): 5-JMP table at $1000; init `LDY #$16` loop clears $D400–$D416, then
  primes $D404/$D40B/$D412=$08; per-voice Y offset from table `$1015,X`.
- **V9.x** (the scene's V8/V9): same init, but the **play dispatcher passes Y=SID-base
  ($0E/$07/$00) as a parameter** to a uniform 3-way JSR (vs deriving Y inside the sub) —
  mutually exclusive with V7.03 (0 SIDs match both).
- **V10.x** (rare): adds an **init-time ASL/ROL table-expand loop** (83 entries, count $53)
  that **decompresses packed frequency data**; uses **SMC** to patch the dispatcher for
  subtune selection; X-indexed 25-register clear.

**Related Odie engine strings — all Sean Connolly, but distinct players** (separate
migration targets, NOT folded into EMS):
- `Odie/Cosine` (9, 1987–91): pre-EMS, $80 sentinel (not $FF/$FE/$FD), different layout.
- `Odie_tiny` (3, 1998–99): stripped ~1 KB player for 4 KB compos, 3-entry JMP, incompatible data.
- `Odie/Pulse` (2, 1987–88): oldest, Pulse Productions, uses CPU banking + KERNAL calls.
- (`Digital_Systems` is **NOT** Odie — Harlequin/Silicon Limited, separate engine.)

## Corpus shape (196 EMS/Odie tunes)

195 PSID v2 + **1 v3 (2SID `Lovefunk`)**; 195 VBI + **1 CIA (`Brian_the_Lion` subtune 1)**;
87% single-subtune. 142/196 (72%) canonical $1000/$1003; play=init+3 in 186/196; 37 distinct
(init,play) pairs = real relocation diversity ($E000=8, $8000=4, $9000=3, scattered). Authors:
**Merman/Andrew Fisher (99, 50%** — almost all his 1999–2008 Ozone covers; 82 SIDs from 1999
alone), Connolly/Odie himself (61), TMR/Jason Kelk (13, Cosine, d. 2021), Richard Bayliss (10,
still using EMS 2023–24). Tight UK scene. STIL has only one non-technical EMS mention.

## What remains (migration-phase RE)

The feature model is fully documented; the **binary record offsets** are the open work:
- **Disassemble one V7.03 $1000 tune** to pin the **instrument binary record byte-offsets**
  (the 15 params → exact bytes), the **sequence/track stream wire format** (command byte
  encoding), the **wave/arp/filter table wire format**, and the multi-subtune pointer table.
- **Version dispatch**: the extractor keys on V7.03 vs V9.x vs V10.x (init/dispatch shape) —
  and V10.x's **packed-freq decompress** ($53-entry ASL/ROL) + SMC subtune patch need handling.
- **The 1 CIA tune** (`Brian_the_Lion`) → `--writelog-per-irq`; **the 1 2SID tune**
  (`Lovefunk`) → 6-voice verdict. The other 194 are flat VBI Mode-1.
- **Odie/Cosine, Odie_tiny, Odie/Pulse** are separate small engines (handle later, if at all).

## Top leads

1. ~~EMS feature docs~~ — **OBTAINED** (V7.03 disk help files, `src/*.txt`).
2. **A V9 or V10 disk image** — not found this sweep; would document the later-gen data format
   (esp. V10's packed-freq encoding). Try cosine.org.uk + CSDb.
3. **TMR's EMS tutorial** (~2003, mentioned but not found) + **contact Richard Bayliss/Odie**
   on CSDb (both active) — for the binary record layout.

Full provenance in each file + `provenance_log.md`.
