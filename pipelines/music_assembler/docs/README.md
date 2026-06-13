# Music Assembler — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

Music Assembler ("masm"), by Marco Swagerman (MC) + Oscar Giesen (OPM) of
Dutch USA-Team, 1989, published by Markt+Technik. ~6,351 HVSC tunes (the
3rd-largest engine family). 0 migrated.

A six-cluster research-player sweep ran on 2026-06-13 (CSDb+manual, GitHub,
Archive.org, forums, DeepSID/SIDId, packed-format hunt). Outcome: the packed
assembled-output format — initially thought undocumented — is **effectively
documented** via (a) a public hand-annotated JC64dis disassembly and (b) two
independent end-to-end RE traces produced this session, which agree. The
editor data model is fully covered by the vendored manual. This family is
cleared to start disassembly/annotation of a first SID.

## Start here (canonical docs)

1. **`spec_GAP_analysis.md`** — the synthesis + the **extraction checklist**
   (binary → USF, item by item) and per-frame SID write model. Read first.
2. **`spec_player_RE_grounded.md`** — one HVSC binary (`OPM/Sid_Slam`) traced
   end-to-end; the concrete parsing target.
3. **`spec_player_jc64dis.md`** + **`jc64dis_MusicAssembler_annotations.txt`** —
   the authoritative packed sequence/opcode map, from Stefano Tognon's
   JC64dis hand-annotation (`ice00/jc64` `doc/example/MusicAssembler.dis`).
4. **`csdb_manual_notes.md`** (+ `csdb_manual_0_01b.pdf`/`.txt`) — the official
   manual: editor data model + effect *semantics* a USF converter must match
   (pulse-rate nibble-swap, duration=stored+1, hard-reset wave $08/$09→$08,
   filter direction/speed table, rattling slide, ring/sync 1↔3 adjacency,
   filter-cascade-to-lower-voices).

## Full file index

| Topic | Canonical | Corroborating (independent traces) |
|---|---|---|
| Extraction plan + write model | `spec_GAP_analysis.md` | — |
| Player RE / per-frame writes | `spec_player_RE_grounded.md` | `csdb_packed_format_disasm.md`, `github_disasm_verified_runtime.md`, `archive_player_writemodel.md` |
| Packed sequence/opcode map | `spec_player_jc64dis.md` | `jc64dis_MusicAssembler_annotations.txt` |
| Editor data model | `csdb_manual_notes.md` | `spec_editor_model.md` |
| sidid signature / variants | `sidid_signature_analysis.md` | `forum_sidid_signatures.md`, `github_sidid_signatures.md`, `deepsid_and_web_findings.md` |
| Version lineage | `csdb_versions_and_pouet.md` | `archive_versions_and_fingerprints.md`, `forum_voicetracker_lemon64.md` |
| Open-source decoder lead | `forum_jitt64_importer.md` | — |
| Release / publication trail | `csdb_release_94388.md` | `archive_publication_trail.md`, `archive_editor_disk_1990.md` |
| Consolidated leads | `forum_leads.md` | (and each doc's own "Leads to follow") |

Multiple files per topic = **multiple independent disassemblies that agree**,
which is why confidence is high. Provenance headers are on every file;
`provenance_log.md` lists every URL hit/blocked.

## What's solved

- **Entry points** (reloc-invariant): IRQ=base+$00, play=base+$21, init=base+$48;
  sidid signature lands at base+$91 and directly yields the per-track seq#
  array + the sequence pointer tables.
- **Per-frame SID write model**: per-voice freq/PW/ctrl/AD/SR + global
  `$D416`/`$D417`/`$D418`; fixed init prefix `$D418=$1F`,`$D417=$F0` →
  fits the Mode-1 instruction-stream verdict (`compare_instruction_stream`,
  init-trichotomy handles the prefix). No digi.
- **Packed format**: data-section layout, sequence opcode map, preset/arp/track
  encoding — from JC64dis + the grounded trace.
- **Effect semantics**: from the manual.
- **Variant taxonomy**: V1.0 (DUSAT 1989) → V1.1/1.3/1.4 (Triad) → derivatives
  (VoiceTracker, Music Mixer, DoubleTracker/Ten Tracker = multispeed). The base
  sidid signature matches 6351/6351; best build discriminator is the
  fingerprint offset from base (`+$91` = 5311, then `+$B5`, `+$70`, `+$191`).

## What remains (for the migration, not for research)

- **Fingerprint the 6,351 members into version groups** before bulk extraction
  (template: `project_fc_fingerprint_and_standard` + `tools/engine_fingerprint.py`).
  Two PSID header conventions exist (init+$48/play+$21 vs init+$00/play+$03) —
  accept both.
- **Confirm the opcode map against a 2nd binary** (the JC64dis map is from MC_01;
  cross-check the grounded `OPM/Sid_Slam` trace).
- **Multispeed members** (DoubleTracker 2×, Ten Tracker 10×) → CIA/dispatch-rate
  per-tune; CLAUDE.md Trap C / per-play verdict applies.
- These are RE/implementation tasks — no further doc acquisition needed.

## ⚠ Name collision (important)

A **different, unrelated** product also called "Music Assembler" exists —
**V3.1 by Harald Rosenfeldt** (1989, 64'er/Markt&Technik), with a different
signature and write model. cadaver's `sidid.nfo` even mislabels the MASM
signature with Rosenfeldt's name. HVSC string-filtering on "Music Assembler"
will catch Rosenfeldt's tunes — they are a separate engine and must be excluded.

## Binary specimens

Kept locally for RE but **git-ignored** (see `.gitignore`): the `.d64` editor
disk images and `.zip`s (bulky, reproducible from CSDb/Archive.org; source URLs
in each doc's provenance). Committed: the manual PDF/txt, the JC64dis annotation
dump, and small `.prg` fixtures (`song_*.prg`, `presets_only_*.prg`,
`standalone_player_*.prg`, `editor_v1.*_triad_*.prg`,
`masm_editor_1990_OMUSICASSEMBLER.prg`) as reproducible RE targets.

## Top leads (if the migration needs more)

1. **JITT64** (Ice Team, GPL Java; SourceForge SVN `jitt64`) — a working
   open-source MASM/VoiceTracker→tracker importer. Highest-leverage artifact;
   needs a networked host with `svn`. Use as a black-box oracle if the opcode
   map resists.
2. **JC64dis `.dis` example projects** (`ice00/jc64` `doc/example/`) — load in
   JC64dis for the full labelled listing with exact table operands.
3. **MASM V1.1/V1.4 (Triad)** CSDb #27470/#27472 + **VoiceTracker V1.0**
   #10756 — pull to lock the version-group fingerprint.
4. **Author contact** — Marco Swagerman is active (amiga.cafe as `MC-DusaT`,
   YouTube `marcoswagerman`) and has said he likely still has his Devpac source.
5. **German/Polish scene** (forum64.de, Polish c64 scene for VoiceTracker) —
   most likely home of any non-English player analysis; not yet found.
