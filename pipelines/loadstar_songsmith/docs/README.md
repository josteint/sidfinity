# Loadstar SongSmith — research docs index

Player: **SongSmith**, a hobbyist music-composition tool for the C64, written by
**Joe Garrett** (deceased; the shipped disk is dedicated to him) and published by
**Softdisk / Loadstar** (the US Commodore disk magazine; editors Fender Tucker →
Dave Moorman). A precursor "songmaker" by **Joe Garrett + Alan Gardner** appeared
in Loadstar ~#27–28 (c.1987). SongSmith proper sold as a standalone Softdisk
product (catalog #069525, ~$10, 30-page printed manual + 8-tune jukebox), and was
re-documented on **Loadstar #237** (2004) by Dave Moorman. **Not a demoscene tool**
— used by hobbyist composers transcribing classical/folk sheet music.

HVSC #84 footprint: **331 SIDs** — `Loadstar_SongSmith` 308 (the mature shipped
version), `_v1` 19, `_v3` 3, `_v2` 1. Heaviest composers: Dave Marquis (126),
Alan Beggerow (48), Debby Cruz (41/45), John S. Davis (24), Mario Oropesa (22).

Research sweep date: **2026-06-14**. One broad wave of parallel sonnet agents
(archive.org/Loadstar · sidid/DeepSID · GitHub/lineage · forums/community).
GATHER-only — no RE, no siddump/py65. 6502-level RE is the migration phase.

## TL;DR for the migration phase

- **It is NOT a Sidplayer/.MUS-family tool** (checked definitively — separate sidid
  entries, completely different player model). SongSmith uses a simple **note-index
  → frequency-table → SID-register-write** loop, not Chamberlain's packed 2-byte
  command stream. The `.MUS` spec we gathered (`github_sidplayer_mus_format.md`) is
  a *contrast/relative*, not the format.
- **It's a notation-style player, not a tracker.** 3 voices; notes + classical
  durations (Whole/Half/Quarter/Eighth/Sixteenth + Dot + Rest); key signature, time
  signature, tempo (~30–260 BPM); ADSR + waveform per voice from a small preset
  bank (~19 named instruments: PIANO…OBOE/BAGPIPES). **No** triplets, tied notes,
  filtering, LFO, portamento, pulse-sweep, ring/sync — confirmed by the converter
  docs (those are SID-Player-only and need post-conversion editing). This makes the
  USF target unusually clean: pitch + duration + per-voice ADSR/waveform, no effect
  chain.
- **Player entry points** (mature version): init `$CC00`, play `$CC48`; per-song
  music data around `$B800–$C700`. Note lookup: `(note-1)*2` index into a word
  freq-table (freq-lo/freq-hi). See `sidid_signatures.md`.
- **On-disk native format** (for context; HVSC SIDs bake it into one PSID):
  `m.SONGNAME` = note/melody stream, `w.SONGNAME` = exactly 1 block (254 bytes) of
  ADSR + timbre/waveform. Both files needed to play. The **exact m-file byte
  encoding is the one real OPEN** (note-index + duration-code interleave across 3
  voices) → recover by disasm.

## sidid variants (all four decoded — `sidid_signatures.md`)

| HVSC tag | n | Reloc? | Architecture (from signature) |
|---|---|---|---|
| `Loadstar_SongSmith` | 308 | yes | mature: ABS pointer read (`INC abs`+`LDY abs`); `38 E9 ?? 0A A8 B9 ?? ?? 8D 00 D4 …` |
| `Loadstar_SongSmith_v1` | 19 | no | earliest: ZP `$F9/$FA` indirect loop, different model |
| `Loadstar_SongSmith_v3` | 3 | yes | relocated v2; `SBC` operand wildcarded |
| `Loadstar_SongSmith_v2` | 1 | no | freq table fixed at `$C290`; writes `$D400/$D401/$D404` |

v2→v3 discriminators: freq-table address (`B9 90 C2` vs wildcard) and the `SBC`
immediate. The unversioned mature tag differs from v3 in the data-read section after
the `$D404` write (ABS `INC`+`LDY` vs ZP-indirect).

## File index

### Format / model (read first)
- `forum_musical_model.md` — the notation-style musical model (voices, durations,
  key/time sig, tempo, instrument bank, what it lacks). The USF-design reference.
- `src/loadstar237_converter_docs_extracted.md` — **PRIMARY**: SIDSmith/SmithSID
  converter docs (Loadstar 237) — the best community description of the `m.`/`w.`
  file format + the SongSmith⊂SID-Player capability subset.
- `src/loadstar237_t_songsmith_extracted.md` — **PRIMARY**: Moorman's SongSmith
  documentation article (Loadstar 237).
- `sidid_signatures.md` + `src/sidid_loadstar_songsmith_signatures.txt` — the four
  decoded player signatures + entry points + note-lookup math.
- `github_sidplayer_mus_format.md` (+ `src/github_compute_sidplayer_mus_format_raw.md`)
  — the Chamberlain `.MUS` spec, kept as the *contrast* format (SongSmith is NOT this).

### Provenance / lineage / detection
- `github_lineage.md` / `github_parser_search.md` — NOT-Sidplayer verdict; confirms
  no parser/converter exists in any open-source tool (SF2, ChiptuneSAK, desidulate…).
- `sidid_version_differences.md` / `sidid_deepsid_notes.md` — version archaeology;
  DeepSID has no SongSmith-specific code (the new 'L' icon just reads HVSC engine strings).
- `archive_loadstar_issues.md` / `archive_songsmith_docs.md` — Loadstar archive
  coverage (itch.io "Loadstar Compleat", CSDb d64, discmaster #237); d64 string dump
  (instrument names, hot keys) in `src/d64_documentation_text.txt`.
- `archive_author_trail.md` / `forum_author_trail.md` / `forum_discussion.md` —
  Joe Garrett authorship, the Garrett/Gardner precursor, the converter authors
  (Debby Cruz, Scott Resh, Doreen Horne), Dave Moorman.
- `src/compsyscbm_loadstar168_extracted.md` — Fender Tucker comp.sys.cbm post
  attributing the precursor to Garrett + Gardner.

## What we have (quality assessment)

| Need | Status |
|---|---|
| Author / lineage / provenance | **SOLVED** — Joe Garrett, Softdisk/Loadstar |
| Is-it-Sidplayer/.MUS? | **SOLVED** — definitively NO |
| Musical model (voices/durations/instruments/effects-absent) | **GOOD** — community + converter docs |
| Player entry points + note-lookup math | **GOOD** — from sidid signatures |
| sidid signatures / version discrimination | **SOLVED** — 4 variants byte-decoded |
| `m.`/`w.` file structure (high level) | **GOOD** — converter docs |
| Exact `m`-file byte encoding (note-index + duration interleave) | **OPEN** — RE |
| Exact per-frame SID write order / timing | **OPEN** — RE (but no effects → simple) |

## Open items (defer to migration/RE phase)

1. **Disassemble the mature player** (`$CC00` init / `$CC48` play) from a
   `Loadstar_SongSmith` SID (e.g. `MUSICIANS/M/Marquis_Dave/Moonlight_Sonata_A.sid`)
   to recover the **exact m-file byte encoding**: how note-index + duration code +
   3-voice interleave are laid out, and the freq-table location/values. This is the
   one substantive unknown; the binary is in hand (also `tmp/.../Songsmith-Loadstar.d64`).
2. **Duration model** — confirm how W/H/Q/E/S durations are stored as tick counts
   and how tempo scales them.
3. **Instrument bank** — recover the ~19 preset ADSR+waveform definitions (or
   confirm they're carried per-song in the `w` block baked into the PSID).
4. **`Dave Marquis` attribution discrepancy** — one community source claims Marquis
   used "SID Editor (Parsec)", yet his 126 HVSC tunes are tagged `Loadstar_SongSmith`.
   Confirm whether the sidid tag is correct (likely yes — verify on one of his SIDs).
5. **v1 vs mature** — v1 (ZP-indirect, 19 SIDs) is a structurally different early
   engine; may need its own small extractor variant.

All Open items are confined to binaries already in hand (331 HVSC SIDs + the CSDb
d64) and are the proper subject of the `disassembly.s` + extractor step. The online
search space is exhausted — the standalone product's 30-page manual was *printed*
(not on disk), so it is likely unrecoverable; the Loadstar 237 on-disk docs +
converter docs are the best surviving textual description and have been captured.

## Suggested first migration target

A mature `Loadstar_SongSmith` tune (308-SID bulk, relocated, `$CC00`/`$CC48`).
Because there is **no effect chain**, the USF mapping is essentially pitch +
duration + per-voice ADSR/waveform — disassemble one player with `forum_musical_model.md`
and the converter docs open, recover the m-file note/duration interleave, done.
