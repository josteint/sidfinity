---
source_url: orchestrator synthesis (this dir)
fetched_via: synthesis
fetch_date: 2026-06-15
author: research-player sweep (6 parallel sonnet agents + orchestrator)
content_date: 2026-06-15
reliability: secondary (index over the per-file primary/secondary sources)
---

# Ariston — research docs index

**Engine:** the **Ariston** music driver — a UK commercial C64 game-music system. Driver by
**Ian Crabtree** (1987); GUI editor "**(C) ARISTON DESIGNS '88 / PROGRAMMED BY PHILIP BRABBIN
1987/88**" (string in the editor binary); a **Wally Beben** variant (improved drums, the
dominant one). Named after the *"Ariston… and on… and on"* UK appliance TV advert (per the
STIL note on `Dunn/RoboCop.sid`). HVSC engine string `Ariston`, **147 SIDs**. 3 voices,
mostly 50 Hz VBI. Ported to Atari ST + Amiga in 1988 (same data format).

`research-player` sweep status: **COMPLETE** (this 2026-06-15 sweep → `engine_docs` state `OK`).

## The headline: source is lost, but a tool-assisted DISASSEMBLY gave us the full format

The original driver source is **not public** — and Beben's copy (incl. the ST/Amiga port) was
**lost to a hard-drive failure**. BUT the sweep found and decoded **JC64dis's annotated
disassembly project of Beben's *Dark Side*** (1988 Incentive) — by JC64dis author Stefano
Tognon. From it we recovered a complete byte-level format for the **Wally_Beben variant**
(90% of the corpus). The compressed JC64dis project is preserved at
`src/jc64dis_DarkSide_project.dis.gz` (open in JC64dis 2.3 to regenerate labelled asm).

So unlike a pure-RE engine, **the format is documented** — but only the Beben variant is fully
mapped; the Crabtree V1/V2 variants are inferred from SIDId signatures and need a confirming
disassembly at migration time.

## Start here

- **`src/archive_format_summary.md`** — THE canonical format spec (data hierarchy,
  8-byte instrument block, track/orderlist bytes, pattern command bytes, voice state,
  freq table/tuning, feature list). **Read first.**
- `src/archive_jc64dis_disassembly.md` — the raw findings behind it: in-binary credits,
  tuning label, the full routine-label list (`initSongs`/`playSound`/`calculateNote`/
  `testEffectPlunk`/…), per-voice state vars, SID stride, editor UI strings.
- `sidid_signature_analysis.md` / `disasm_sidid_signatures.md` / `archive_sidid_fingerprints.md`
  — the 4 SIDId sub-signatures (Ariston / Crabtree V1 / V2 / Beben) decoded opcode-by-opcode
  = the variant taxonomy + write-order differences.
- `hvsc_corpus_census.md` / `article_hvsc_corpus.md` — the 147-SID census.
- `engine_overview.md` — authorship + lineage synthesis.

> **Redundancy note:** parallel agents produced overlapping files (several VGMPF extracts:
> `wiki_vgmpf_ariston.md`/`csdb_vgmpf_ariston.md`/`article_vgmpf_ariston.md`/`src/archive_vgmpf_ariston.md`;
> several CSDb-release + sidid files). The files cited above are the canonical ones; the rest
> are corroborating copies, not independent sources.

## Format in one paragraph (Wally_Beben variant, from the disassembly)

Hierarchy **Song → 3 Tracks (one per voice) → Patterns → notes+effects**; voices processed in
a loop at SID stride {0,7,$0E}. **Track/orderlist bytes:** `$00–$7F` pattern#, `$80–$BF`
transpose-down, `$C0–$FE` transpose-up, `$FF` end/loop. **Pattern bytes:** `$00–$5F` note
(96-note / 8-octave range); special-note cmds `$7A` DVI (delay-vibrato), `$7B` GLI (glissando),
`$7C` CTR / `$7D` TRL / `$7E` TIN / `$7F` TDE (trill family); `$80–$BF` Lxx note-length;
`$C0–$DF` Ixx instrument-select (0–31); `$F0–$FB` Sxx speed (12 tempo levels); `$FC vv` VOL
(→$D418); `$FE` STP (gate-off); `$FF` END. **Instrument = 8 bytes:** control, AD, SR, pulse-width
(2-byte lo|hi), vibrato(step|size), pulse-sweep, trill-bits, effect-flags (bit0 BASS-drum,
bit1 plunk, bit2 echo, bit3 SIDE-drum). Notable: trill ornament system, glissando, pulse-sweep,
the drum/plunk/echo effect bits (Maniacs-of-Noise-enhanced "phasing"), and an unusual
**bidirectional pattern scan** (per-voice $FE=forward / $DE=backward). **Tuning:** A4=459 Hz PAL
/ 477 Hz NTSC for the Beben variant (VGMPF's "424/434 Hz" likely the Crabtree V1/V2 variants;
Crabtree's own tunes 433.5 Hz PAL).

## Key facts established

- **One engine, four SIDId sub-fingerprints.** `Ian_Crabtree_V1`, `Ian_Crabtree_V2`,
  `Wally_Beben` are sub-variants that match *after* the primary `Ariston` sig — not separate
  engines. **132/147 (90%) carry the Wally_Beben sub-signature**; ~15 do not (Barry Leitch,
  early Steve Barrett, early Beben). Write-order differs by variant (V2 adds explicit
  $D405/$D406 ADSR + double-$D404 hard restart; Beben adds PW writes + a drum-tick DEC counter).
- **Corpus census:** 147 SIDs, all PSID v2; **144 VBI / 3 CIA** (Steve Barrett/Eggman, speed bit)
  **/ 13 own-IRQ (play=0)** — Beben×5, Barrett×3, Wilson×3, Tapanimäki×1, Pedersen×1. Load
  addresses fully **scattered ($08xx–$F1xx)** — each composer assembled at their own origin.
  Two clusters: Sandra Park + Neil Scales at $0832–$0856 (Brabbin editor default), Mark Wilson
  at the $A000 band. Zero HVSC STIL *technical* comments (only the name-origin note).
- **Workflow:** almost all composers typed note data **directly in 6502 assembler** (Brimble,
  Gray, Dunn testimony); the Brabbin GUI editor was secondary. Drivers passed informally between
  UK composers (Compunet/personal). Maniacs of Noise got the source in late 1987 and enhanced
  the drums.
- **No third-party parser** (libsidplayfp/VICE/DeepSID none handle it specifically). The driver
  is fully relocatable. `Ariston Design` is a *scene group* named after the driver (Moley / Neil
  Scales) — unrelated to authorship.

## What each priority need looks like now

| Need | Status | Where |
|---|---|---|
| Original player **source** | ❌ lost (Beben HDD failure); not public | — |
| Tool-assisted **disassembly** | ✅ HAVE (JC64dis, Beben variant) | `src/jc64dis_DarkSide_project.dis.gz`, `src/archive_jc64dis_disassembly.md` |
| Format byte layout | ✅ **complete for Beben variant** | `src/archive_format_summary.md` |
| Other tools' parsers | none exist | — |
| Effect → register semantics | ✅ strong (routine labels + state vars) | `src/archive_jc64dis_disassembly.md` |
| Version/variant differences | partial — 4 sub-sigs decoded; only Beben disassembled | `sidid_signature_analysis.md` |

## Gaps — and which phase owns each

**Migration-phase (RE) tasks — out of research scope:**
1. **Crabtree V1/V2 variants** — only the Beben variant is disassembled. Run JC64dis (or
   `tools/seed_disassembly.py`) on a clean V1 tune (cleanest target: a `init=load+3` Crabtree
   tune, e.g. `Crabtree/Outrun.sid` 2841 B, or `Angel_Meadows.sid`) and a V2 tune to confirm
   their instrument layout + write order vs the Beben spec.
2. **VOL opcode ambiguity** — the format spec lists `$FC vv` = VOL→$D418 but the JC64dis
   constants block lists `VOL=$FD`. **OPEN: confirm whether VOL is $FC or $FD (and what $FD is)
   on the actual binary** before trusting the pattern decoder.
3. **13 own-IRQ (play=0) tunes** — embed their own IRQ install; need the per-IRQ verdict path
   (esp. Beben's `Tetris.sid` — 13 KB, init=$7440, play=0; and `Pedersen/Digi_Panth_2.sid`,
   possible digi). The 3 CIA tunes likewise need the multispeed path.
4. **Effect semantics to register-confirm:** the drum BASS/SIDE, plunk, echo (the "phasing")
   and the bidirectional pattern scan ($FE/$DE) — labelled but not register-traced.
5. **Tuning-variant census** — which SIDs use 459 vs 424/434/433.5 Hz freq tables (a USF
   `tuning_hz` parameter); fingerprint the freq table per variant.

**Online-fillable but unnecessary** (logged in `provenance_log.md`): the locked Atari-Forum
attachments (`R_TYPE.W_B.zip` Mug-UK ST RE; Xerud rips), SNDH archive Beben ST replayers (a
second independent copy of the engine, YM-adapted), the cracked editor D64s (already downloaded;
running in VICE shows the editor UI). Living composer **Wally Beben** could be contacted.

**Probably unfillable:** the pristine original 6502 source (lost).
