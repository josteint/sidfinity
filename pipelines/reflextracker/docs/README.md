---
source_url: orchestrator synthesis (this dir)
fetched_via: synthesis
fetch_date: 2026-06-15
author: research-player sweep (6 parallel sonnet agents + orchestrator)
content_date: 2026-06-15
reliability: secondary (index over the per-file primary/secondary sources)
---

# Reflextracker — research docs index

**Engine:** **Reflex-Tracker V1.1** (1995) by the group **Reflex / The Obsessed Maniacs (TOM)**.
Per the in-binary credits: editor code **Zorc**, design/docs/songs/samples **PVCF**, disk +
optimize + sample-menu **kb (Tammo Hinrichs)**, sample-pack compression **Quiss (Matthias
Kramm)**. Module header reads *"CODE BY ZORC/REFLEX AND KB/T.O.M"*. HVSC engine string
`Reflextracker`, **137 SIDs**.

`research-player` sweep status: **COMPLETE** (this 2026-06-15 sweep → `engine_docs` state `OK`).

## ⚠️ Two findings that REFRAME this engine — read before anything

1. **It is a 2-voice DIGI / SAMPLE tracker, not a melodic SID tracker.** During play the player
   writes **only `$D418`** (the 4-bit master-volume DAC). It installs its own **CIA2 Timer A**
   interrupt at ~**6702 Hz** ($DD04=$93), reads one nibble from each of two sample streams
   (ZP pointers `$D0/$D1` and `$D2/$D3`), mixes them, and writes the result to `$D418`. The
   SID's 3 synthesis voices are unused; the "third voice" (drum/snare) is a software trick in
   the 2-channel mixer (PVCF's STIL note). → **This means migration is Mode 2 (cycle-exact),
   not the frame-by-frame instruction-sequence mode — same class as Chimera.** See CLAUDE.md
   "Mode 2 — cycle-exact (digi only)". The USF must carry PCM sample data + the 2-voice
   pattern/track structure, via the digi sidecar pipeline (`pipelines/hubbard/sample.py` /
   `flac_io.py` / `digi_pack.py`), not the tracker note path.

2. **`research.md`'s "PC-based cross-tracker / up to 10 channels" framing is misleading for the
   HVSC corpus.** Sources disagree (iAN CooG calls it a PC cross-tracker; the recovered D64
   contains a fully C64-native `REFLEXTRACK.V1.1` editor + German manual). Resolution that
   matters: **(a)** the **player** in all 137 HVSC SIDs is a C64 binary (2 KB @ $C000); **(b)**
   "PC" referred to a PC↔C64 sample-transfer workflow; **(c)** **QuadSID** (up to 10 channels
   via 4 SID chips) exported **MIDI only — never .sid**, so **zero QuadSID/multi-SID tunes
   exist in HVSC** (PVCF's "Bladeswede" survives only as its DMC 3-ch downmix). For our 137,
   it's purely the **2-channel digi player**.

## Start here

- **`player_format.md`** — THE canonical reference: disk layout, the 2 KB player ($C000, init
  $C006, play=0 own-IRQ), init routine (CIA2 setup), the **RFX1 module format**, track table
  (`--`/`RP`/`ED`), 16-row pattern grid (fields SND/IS/Direction/Speed/Volume), sample drivers,
  the playback-mixer mechanism, credits, and translated manual quotes. **Read first.**
- `src/module_format.md` — RFX1 magic + pattern/sequence byte stream notes (with OPEN questions).
- `src/player_architecture.md` — the two player layouts (standalone $C000 vs. iAN-CooG-wrapped
  self-relocating $1F00→$F000), ZP state table, SID-write inventory.
- `src/disasm_rfxt_player.md` — the (first known) annotated disassembly of the 2 KB player.
- `sidid_signature.md` / `sidid_analysis.md` — the signature decoded against the binary
  (the $D0/$D1+$D2/$D3 stream walkers; pervasive SMC = why the sig has many wildcards).
- `beschreibung_translation.md` / `beschreibung_german_manual.md` — the decoded German manual.
- `hvsc_corpus_census.md` / `hvsc_sid_layout.md` — the 137-SID census.

**Preserved binaries** (`src/`, would vanish on `tmp/` wipe): `RFXT_PLAYER_V1.1.prg` (2 KB
player), `BESCHREIBUNG.prg` (28 KB German manual), `MOD.TRANCE202.prg`, `MOD.ENDLOSCHOOR.prg`
(authentic RFX1 modules for format study).

> **Redundancy note:** six parallel agents produced overlapping files (e.g.
> `disk_contents.md`+`disk_contents_and_format.md`; `beschreibung_*` ×2; `sidid_*` ×3;
> `*pouet*` ×2; `csdb_*` set). The files cited above are canonical; the rest corroborate.

## Format in one paragraph (from the manual + binary)

Player = 2048 bytes @ `$C000`, init `$C006` (also SYS 49158), **play = $0000** (installs its own
CIA2 Timer-A IRQ). **RFX1 module** = `"RFX1"` magic + track table + pattern data + bulk PCM
sample data. **Track table** = a 2-voice orderlist; entries are pattern numbers (hex, ≤256) or
`--` (voice silent — but never both voices at once, or the player can't find the speed), `RP`
(loop to pos 0), `ED` (stop). **Pattern** = 16 rows; each row carries, per voice: SND (note;
`--`=rest, `=`=stop), IS (8-bit sample/instrument #; `--`=continue prev sample at new pitch =
the "switch" effect), Direction (0=fwd/1=reverse), Speed (hex 0–F; **Voice 1 has priority**;
7=normal 4/4), Volume (2-bit, 4 levels). **Instruments** = named samples with start/end RAM
addresses; data is signed 8-bit PCM or 4-bit nibble-packed. **Playback:** per ~6702 Hz CIA IRQ,
read+mix the two voices' nibbles → clip → `$D418`; advance row by Speed; on pattern end advance
the track table. The disk also ships **sample-capture drivers** (Userport/IO1/IO2/Joystick
2–8-bit, plus `SDRV.SIDWAVE`) — composition-time only, not part of the player.

## Key facts established

- **Pure $D418 digi**, CIA2-timed ~6702 Hz, 2 software-mixed sample voices. Cycle-exact (Mode 2).
- **Corpus:** 137 SIDs (incl. 6 under `DEMOS/`), all PSID v2, all **1 subtune**, all **play=0**
  (own-IRQ), **130/137 init=$C006** (player @ $C000). Outliers: a `$C050` group (PVCF's
  Gubber/Trance202/Originalzak — slightly different init stub) and `Jonny/Future_Come.sid` at
  `$1C06` (player relocated to $1C00). No PSID v3 / 2-SID headers (QuadSID isn't here).
  Composers dominated by the Polish scene (CJ Warlock = Piotr Grabowski, ~25 tunes).
- **No source code exists** anywhere (predates GitHub; kb/Quiss/Zorc never released it). But
  the recovered **D64 + 2 KB player + German manual + 3 RFX1 modules** make the format
  effectively complete from primary artifacts.
- A pre-V1.0 **"FTRAC V1"** existed by mid-1994 (Brainbeat 3). **LSD (Liquid Sound Designer)**
  (1997, Quiss + PVCF) is the related follow-on (a 3-channel SID duration editor).
- An **English manual** exists in **Insider #6** (Reflex diskmag), chapter 10 "TRACKERINSTR."
  — needs VICE to read; not yet captured.

## What each priority need looks like now

| Need | Status | Where |
|---|---|---|
| Original player **source** | ❌ never released; not public | — |
| Player **binary** + annotated disasm | ✅ HAVE (2 KB) | `src/RFXT_PLAYER_V1.1.prg`, `src/disasm_rfxt_player.md` |
| Format / module layout | ✅ **strong** (manual + binary) | `player_format.md`, `src/module_format.md` |
| Other tools' parsers | none exist | — |
| Effect → register semantics | ✅ it's just $D418 DAC mixing | `player_format.md` |
| Version/variant differences | V1.0 vs V1.1 (in-tracker bass-split); FTRAC pre-1.0 | `beschreibung_translation.md`, `archive_brainbeat3_1994.md` |

## Gaps — and which phase owns each

**Migration-phase (RE) tasks — out of research scope:**
1. **Decode the RFX1 internal layout precisely** — where the instrument/sample table, track
   table, and pattern stream sit relative to the `"RFX1"` magic (the manual gives field
   *semantics*; byte offsets need tracing on `src/MOD.*.prg`). Pattern stream starts ~`$3D80`
   in one module; bytes `00–4F`=notes, `≥$50`=control. **The instrument table (sample base/
   loop/pitch) is the main undecoded piece.**
2. **Confirm the ~6702 Hz CIA rate + the SMC sample-rate patch** — the init writes $DD04=$93;
   the note→period sub at `$F2CF` (relocated build) has two ADC-immediates patched at init.
   This is the cycle-exact timing signal — must be verified on the binary, and is **the crux
   of Mode-2 verification** for this engine.
3. **The two player builds** — standalone (`Access_Denied_remix`, init $C006 directly) vs. the
   iAN-CooG-wrapped self-relocating build ($1F00→$F000). Migrate against the standalone first.
4. **Digi pipeline wiring** — this engine belongs on the Chimera-style digi sidecar path
   (Sample/FLAC/pack), with a `compare_strict` cycle-exact verdict — NOT `verify_all`.

**Online-fillable but optional** (logged in `provenance_log.md`): Insider #6 ch.10 English
manual (VICE); Brainbeat 4 side B + the Polish North-Party competition disks (more modules);
LSD as a format cross-reference; PVCF/CJ Warlock contact for the original distribution disk.

**Probably unfillable:** the original tool/player source (never released).
