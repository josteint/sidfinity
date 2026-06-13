# SID Duzz'It upstream source + docs (third-party reference)

The **open-source SID Duzz'It player + official docs**, kept in-repo as migration
reference — NOT our code. Per the core tenet we compose our own engine to match
the write-log; we read this to write the extractor and learn the effect semantics.

- **Upstream:** sourceforge.net/p/sidduzzit/ (owner `glennrg64`); extracted from
  the `Sid_Duzz_It_v2.1.7-shape` release D64s, fetched 2026-06-13.
- **Authors:** Geir Tjelta (GT) + Glenn Rune Gallefoss (6R6/GRG), SHAPE. Free for
  use with credit.

| File | What it is |
|------|-----------|
| `SRC_SDI21-N50.asm` | the normal (single-speed) player, Turbo Assembler — the format + write-model spec |
| `SRC_SDI21-SPD50.asm` | the multispeed player (`$1009` speedplay path) |
| `SDI.2.1.6-docs.txt` | the official 65 KB format doc (authoritative) |
| `SDI.2.1.6-note_tables.txt` | waveform-program note-encoding tables |
| `sdi_217_manual.txt` | community PDF manual (Psylicium / H. Mortensen), text-extracted |
| `sdi217_releasenotes.txt` | V2.1.7 bugfix notes |

(`*.raw` = redundant raw-PETSCII dumps of the decoded `.asm`/`.txt`, git-ignored.
The player is Turbo-Assembler-specific source; `V1.x` is a separate, binary-
incompatible format not included here.)
