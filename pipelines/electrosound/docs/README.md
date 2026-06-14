# Electrosound — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

Electrosound (a.k.a. Electrosound 64), a **commercial** C64 music editor by
**Orpheus Ltd.** (author **Steve Mellin**), 1985, ~£14.95. 297 HVSC #84 tunes; 0
migrated. **No public source exists** (commercial product) and **no published
disassembly/RE exists anywhere online** — a genuine gap for a 297-SID family.

`Electronic_Speech_Sys` (5 SIDs) is a **separate engine**, not Electrosound.

## ⚠ This is a from-scratch RE target (unlike the JCH-family sweeps)

There is no open-source player and no third-party parser to lean on. This sweep
captured everything *documentable* — the editor's musical model (from the manual /
magazine coverage), the compiled-SID layout offsets (from a Lemon64 RE note), the
corpus structure, and the scene history — but the **byte-level song-data encoding is
unrecoverable from public sources** and is the migration phase's first job (the
disassembly of a compiled HVSC SID is the ground-truth path).

## File index

| Topic | File | Reliability |
|---|---|---|
| Editor + manual + musical model (instruments/sequences/modulators) | `cluster_editor_and_manual.md` | secondary |
| RE/tool handling + player layout + variant analysis | `cluster_disassembly_and_tools.md` | secondary |
| HVSC corpus characterisation + scene timeline | `cluster_corpus_and_scene.md` | primary (DB) / secondary |

(`src/` is intentionally empty — no source or disassembly is publicly available to save.)

## What's solved

**ONE relocatable player** (the single most important migration fact). The compiled
player is a fixed binary loaded at a composer/ripper-chosen `BASE`, with fixed internal
offsets — independently corroborated by all three agents (Lemon64 RE note + DB
address analysis):

- **play() (IRQ) entry = `BASE+$0A65`** — confirmed by 235/297 (79%) tunes having
  `play_addr & $FF == $65`. Two minor build offsets ($0A75/$0A7A) exist (≤3 player
  builds), but the dominant canonical offset is $0A65.
- **init() entry = `BASE+$0518`**; song data starts at `BASE+$007C`; IRQ patch sites
  at `BASE+$007B` / `BASE+$0084` (`JMP $EA31`→`RTS`).
- **Fixed (non-relocated) zero-page state**: `$02AB` = tune number (0-based),
  `$02FF` = speed, `$02AD` = current tempo (changes mid-song), `$02F9` = enable flag.
- **CIA1-timer driven** (not VIC raster); dynamic tempo = per-change CIA timer values.
  The PSID `speed` field isn't stored in `hvsc84.db`, so the CIA fraction is unconfirmed
  — but the player is inherently CIA-timed → expect the Trap-C `--writelog-per-irq` path.
- **Non-looping** — the driver does not restart at song end (the game program did).

The apparent address variety is **ripper packing conventions, not engine variants** —
the same binary; rippers differ only in where they place the tune-select stub (4 init
styles A–D). Dominant bases: `$4000` (Barry Leitch cohort, 87 SIDs) + `$1000` (Dunn /
Stormont, 56). All 297 are PSID v2.

**Musical model** (from manual + Zzap!/interviews — `cluster_editor_and_manual.md`):
- **Up to 10 instruments**, each with full SID-register access + **5 modulators**
  targeting pitch / pulse-width / cutoff / key-down / key-up. Per modulator: **delay**
  (frames before onset), **speed** (rate), **depth** (amplitude), **direction**
  (up / down / vibrato / shuffle — "shuffle" semantics undocumented), **restart**
  (every note / after rest / never).
- **Up to 20 sequences**, ≤240 steps each, **3 instruments locked to the 3 voices**
  for the whole sequence (no mid-sequence voice reassignment), per-sequence tempo, 16
  note lengths; on a voice rest, one of **24 fixed unmodifiable drum sounds** may play.
- **Up to 5 tracks/songs** chaining sequences MOD-style (no confirmed track transpose).
- **Tuning A = 423.9 Hz, NOT 440** — ⚠ the USF note codec for this engine CANNOT use
  the standard 440 Hz freq table.

**Write-model character**: reputedly "the slowest/worst-coded player of its era" —
consistent with 4–5 modulators × 3 voices evaluated every frame and writing the full
SID register set each frame with no dirty-register skipping. (Good for us: a dense,
deterministic per-frame write stream.)

**Scene timeline**: 1985 launch → 1986 peak (188/297 SIDs; Leitch 68, Dunn 26) → 1987
decline (Soundmonitor superseded it) → 2020 revival (John Stormont, 17 tunes,
Gubbdata 2020). Top composers: Barry Leitch (68), Jonathan Dunn (26), John Stormont
(17), Matthew Perry (15), Peter Clarke (12), Stu Taylor (11).

## What remains (migration-phase RE — the bulk of the format work)

This family is research-light by necessity; the byte-level format must be reverse-
engineered from binaries (no public spec exists):

- **Disassemble a canonical $1000/$4000 compiled SID** (`seed_disassembly.py` →
  `disassembly.s`) to recover: the instrument record layout (10 × ? bytes, SID regs +
  5 modulator descriptors), the sequence step encoding (≤240 steps, note + length +
  drum), the track/orderlist chaining, and the 24-entry drum table. This is the whole
  format — start here.
- **Map the modulator direction/restart semantics** to per-frame freq/$D402-3/$D415-16
  deltas (esp. "shuffle" and vibrato).
- **Build the 423.9 Hz note table** from the player's freq data (don't reuse the 440 Hz one).
- **Confirm the ≤3 build offsets** ($0A65/$0A75/$0A7A) are pure relocation, not
  behavioural — and whether the init-stub style (A–D) needs detection or can be ignored
  (the extractor keys on the player body, not the stub).
- **CIA-timing verdict**: confirm against `--writelog-per-irq` (player is CIA-driven).

## Top leads (if migration needs more; CSDb 503 all session)

1. **The Electrosound editor disk (D64)** on CSDb (release IDs 27433, 85170, 150998,
   254231) — the editor binary itself is the closest thing to a spec; its data-entry
   code reveals the in-memory format. Retry CSDb / find on archive.org / Gamebase64.
2. **Scribd `ELECTROSOUND-pdf`** (18 pp, likely the printed manual) — subscription-gated;
   try archive.org / Lemon64 Documents for a free scan.
3. **JC64dis** auto-labels a compiled Electrosound binary (example: "Mission of Mercy",
   Peter Clarke 1986) — its label set, if extractable, names the routines.
4. **CSDb user comments** on the release pages (503 this session) — most likely place
   for scene RE notes.

Full provenance in each file + `provenance_log.md`.
