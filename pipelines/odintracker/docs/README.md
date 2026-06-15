---
source_url: orchestrator synthesis (this dir)
fetched_via: synthesis
fetch_date: 2026-06-15
author: research-player sweep (6 parallel sonnet agents + orchestrator)
content_date: 2026-06-15
reliability: secondary (index over the per-file primary/secondary sources)
---

# OdinTracker — research docs index

**Engine:** **OdinTracker**, a native C64 SID tracker by **Zoltán Konyha ("Zed")**, BME
Budapest (`zed@inf.bme.hu`). Versions v1.00 (Feb 2000) → **v1.13 (Apr 2001)**. HVSC engine
string `OdinTracker`, **159 SIDs**. 3 voices, 50 Hz VBI (no CIA multispeed), no digi/samples.

`research-player` sweep status: **COMPLETE** (this 2026-06-15 sweep → `engine_docs` state `OK`).

## The headline: full player SOURCE is public — this is a green-field migration

Unlike most engines, OdinTracker shipped its **complete commented DASM source**
(`OdinTracker113src.zip`, CSDb #2628 / zimmers.net). We have it in-tree under `src/`:
- **`src/vplayer.s`** (1222 lines) — the relocatable player that ships *inside* the SID.
  THE decompiler target: init/play/stop, `fetchrow` row decode, `process_instrument`,
  `calcvibrato`, the effect jump-table, `pp_dump2sid` write order.
- **`src/defines.s`** (105 lines) — authoritative memory map + instrument field offsets.
- `src/eplayer.s` — editor's player (computes track pointers dynamically; vplayer uses
  precomputed pointer tables — the key packed-vs-editor structural difference).
- `src/tracker.s` (8163 lines) — full editor + **packer/relocator** (the packed-SID
  serialization order lives here).
- `src/help.txt` + `src/help/help.in` — the complete in-editor manual (effect reference).
- `src/HISTORY.txt` — verbatim v1.00→v1.13 changelog (the format-version split).
- `src/freqtab/freqtab.cpp` — PAL freq-table generator; `src/vibrato/vibrato.s` — sine table;
  `src/c64pack/depacker.s` — depack + SID-type detection.

**Consequence:** the format is *fully* documented by primary source — no proxy, no RE
needed to understand it. The migration is "transcribe the source's data model into the
extractor," not "reverse-engineer a binary."

## Start here

- **`src/github_odintracker_format_and_player.md`** — THE canonical, migration-ready
  reference (18 sections: memory map, song/pattern/track/instrument byte layout, all 16
  effects + F-subcommand table, SID write order, hard restart, vibrato, channel state,
  packed binary layout, freq table, multi-song, USF-conversion notes). **Read this first.**
- `source_analysis_vplayer.md` — deep walk of `vplayer.s` (dispatch order, row encoding,
  state layout, ZP usage) cross-referenced to line numbers.
- `player_format.md` / `csdb_format_spec.md` — two more format derivations (redundant with
  the canonical one above; kept for cross-checking, not separate truth).
- `sidid_signature.md` / `src/github_sidid_signature.md` — signature decoded against actual
  source lines (see correction below).
- `csdb_hvsc_corpus.md` / `hvsc_corpus.md` — the 159-SID corpus census.

## Format in one paragraph (from the source)

3 voices; **orderlist** ($FF-terminated) of **pattern** indices; each pattern = 6 bytes
(3 track-numbers + 3 signed transposes); each **track** = 64 rows × 3 bytes. Row =
`[note|eff_bit3][instr|eff_bits2-0 (via ROR)][param]`; note 1=C-0..96=B-7, 97=note-off.
**32 instruments × 16 bytes, COLUMN-MAJOR** (field N of all instruments contiguous at
`INSTRUMENTS + N*32`): AD, SR, wave start/end/loop, arp start/end/loop, vib delay,
vib depth/speed, pulse width/speed/limits, filter start/end/loop. Shared 256-byte
**wave / arp / filter** tables stepped by per-instrument start/end/loop. **16 effects (0–F)**,
F being a multi-command (speed / volume / filter-mode / fine-slide / note-cut / note-delay
[unimplemented] / filter-controller / hard-restart). **Per-frame SID writes**, voices 2→1→0:
PWlo, PWhi, freqlo, freqhi, ctrl+gate, AD, SR; then once: $D416 cutoff, $D417 res/routing,
$D418 (globalvolume | filter_mode). Hard restart (default 2 ticks) zeroes AD/SR/waveform
before a new note; wave-table byte `$FF` = zero waveform+ADSR (percussive). Gate = waveform
bit0 AND-ed with chn_gateon.

## Key facts established

- **SIDId signature CORRECTION:** our local `deprecated/gt2_pipeline/tools/sidid.cfg` starts
  the OdinTracker sig with `C0 0F`; the canonical cadaver/sidid sig is **`29 0F C0 80 F0 ...`**
  = `AND #$0F` then the `CPY #$80 / BEQ … CPY #$90 …` effect-F sub-command dispatch chain
  ($80=vol, $90=filter-mode, $A0/$B0=fine slide, $C0=note-cut). Confirmed against `vplayer.s`
  `effect0f`. **Fix the local cfg's leading byte when migrating.**
- **One player format covers the corpus.** Two on-disk generations exist — **v1.0x** (no
  filter table) and **v1.1x–1.13** (adds the $4E00 filter table + instrument fields 13–15) —
  but the agents believe all 159 HVSC SIDs are v1.1x. **OPEN (migration-phase): confirm by
  fingerprinting instrument bytes 13–15 / filter-table presence across the 159.**
- **Corpus census** (from PSID headers): 159 SIDs, all PSID v2; init/play offset always +3
  (JMP table); `$1000/$1003` = 126/159 (79%); **156 VBI, 1 CIA (`CiaTno.sid`), 2 RSID
  (play=0, own IRQ — `Dirt_Ball.sid`, `Gods_preview.sid`)**. Relocation outlier `Whirl.sid`
  (offset $3E not $3 → custom wrapper). Zero HVSC STIL/BUGlist entries.
- **No third-party tooling** parses OdinTracker (libsidplayfp/VICE/DeepSID/SF2/GoatTracker/
  CheeseCutter all play it as generic self-contained PSID). The source is the only spec.
- Top composers: SounDemoN (~50), Hoffmann_Michal (~22), Factor6 (~16), Monk (~14),
  LordNikon (~13), Ahti (~9), Hukka (~6). Cadaver's `Darkness.sid` is a good technical
  test case. (Note: SounDemoN said in 2009 he composes in Turbo Assembler — his role here is
  demo-music contributor to releases, not necessarily that every tune is hand-tracked.)

## What each priority need looks like now

| Need | Status | Where |
|---|---|---|
| Original player **source** | ✅ **HAVE — complete commented DASM** | `src/vplayer.s`, `src/defines.s`, `src/tracker.s` |
| Per-frame write model | ✅ confirmed from source | `src/github_..._player.md` §12, `source_analysis_vplayer.md` |
| Format byte layout | ✅ complete | `src/github_..._player.md` §§3–8,15 |
| Other tools' parsers | n/a — none exist (documented) | `src/github_third_party_tools.md` |
| Version differences | ✅ verbatim changelog | `src/HISTORY.txt`, `src/archive_odintracker_changelog.md` |
| Effect → register semantics | ✅ complete | `src/github_..._player.md` §10 + `help.txt` |

## Gaps — and which phase owns each

**Nothing blocks the migration.** Remaining items are all confirm-on-the-binaries tasks (RE = migration phase, out of research scope):
1. **v1.0x vs v1.1x census** — confirm all 159 are v1.1x (fingerprint instrument bytes 13–15 / filter-table region). If any v1.0x exist, they need the older instrument layout (see `src/tracker_v100_header.s`).
2. **RSID handling** — `Dirt_Ball.sid`, `Gods_preview.sid` (play=0, own IRQ) and the CIA tune `CiaTno.sid` need the per-IRQ verdict path, not the standard 50 Hz play() model.
3. **Relocation outlier** `Whirl.sid` (init/play offset $3E) — custom driver wrapping the standard player; investigate at extract time.
4. **Packed-binary parse** — the extractor must read the *packed* layout (`src/github_..._player.md` §15): the precomputed `TRACKTRANSPOSES0-2` / `TRACKPOINTERSLO/HI0-2` pointer tables, not the editor's dynamic track addressing. The packer/relocator ground truth is in `src/tracker.s` (savetables/savetracks routines).
5. **Unimplemented effect $FD0 (note delay)** — `rts` stub in all versions; SIDs using it ignore it silently. Harmless for USF, but note during extraction.

**Online-fillable but unnecessary** (logged in `provenance_log.md`): Dat2Sid v1.4 binary (PSID-wrapping convention), Wayback song `.prg` corpus (format validation examples), CSDb `OdinPack` utility.

**Probably unfillable / not needed:** none — the source closes the format completely.
