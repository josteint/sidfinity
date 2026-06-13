---
source_url: https://csdb.dk/scener/?id=6151 ; https://www.pouet.net/prod.php?which=41806 ; https://csdb.dk/release/download.php?id={32142,32143,32144}
fetched_via: WebFetch + WebSearch + curl 2026-06-13
fetch_date: 2026-06-13
author: CSDb (scener/release records), Pouet (prod record)
content_date: versions 1989–1994
reliability: primary (release records + vendored editor binaries)
---

# Music Assembler — version lineage & packer variants

Answers priority-3 ("version/packer variants"). There are at least **5
distinct editor releases** spanning 1989–1994, across two publishers/groups,
with a hand-off from the original DUSAT authors to Triad (King Fisher). This is
the version-group landscape the migration must account for (cf. GT2 A/B/C/D).

## Release timeline

| Version | Year | Group | CSDb release | download id | vendored editor |
|---|---|---|---|---|---|
| **V1.0** | 1989-02 | Dutch USA-Team | #94388 | 92052 / 38875 | (DUSAT disks; editor = `masm_editor_1990_*` / `ma.d64`) |
| **V1.1** | 1991 | Triad | #27470 | 32142 | `editor_v1.1_triad_0801.prg` (T64 `M.ASS V1.1/TRIAD`, $0801–$4290) |
| **V1.3** | 1992 | Triad | #27471 | 32143 | `editor_v1.3_triad_0801.prg` (T64 `M.ASS V1.3/TRIAD`, $0801–$47A1) |
| **V1.4** | 1994 | Triad | #27472 | 32144 | `editor_v1.4_triad_0801.prg` (D64 `M.ASS V1.4/TRIAD`) |

(V1.2 not located on CSDb — possible gap or unreleased.)

- The DUSAT V1.0 release labels itself "Music-Assembler V1.0" on CSDb;
  the manual is titled "Music Assembler 1.0".
- Editor sizes grow across versions (V1.1 ≈ 14991 B → V1.3 ≈ 16288 B →
  V1.4 ≈ 17339 B), consistent with feature accretion.

## Authorship hand-off (CRITICAL for variant expectations)

- Original: **MC (Marco Swagerman)** + **OPM (Oscar Giesen)**, Dutch USA-Team
  (CSDb scener for MC = id 6151; he is coder+musician, NL).
- The Triad V1.1–V1.4 line is credited to MC on his CSDb page, BUT the Pouet
  record for **V1.4** carries the comment: *"This one was continued and kept
  improved by **King Fisher** alone."* → V1.4 (and possibly V1.3) player code
  may diverge from the DUSAT V1.0 player. King Fisher = Triad coder.
- Implication: expect **two player sub-families** in HVSC — the DUSAT-era
  player (V1.0) and the Triad/King-Fisher-era player (V1.1+). The sidid
  `Music_Assembler` and `(Music_Assembler/MC)` signature split (see the sidid
  docs in this dir) likely reflects exactly this. Fingerprint HVSC members by
  which signature they match before assuming one decoder fits all.

## Predecessor lineage (earlier DUSAT editors)

- **Rockmonitor 2** (1987) — MC + OPM, Dutch USA-Team.
- **Rockmonitor 5** (1988, "Rockmonitor 5 Demosong" by OPM).
These pre-date Music Assembler; if they share player DNA they could explain
early-1988 "MC_01"-style tunes. Worth a fingerprint check but lower priority
(separate engine names in sidid).

## Derivative engine — VoiceTracker

sidid groups a `(VoiceTracker)` signature *under* the Music_Assembler family,
sharing the `C9 FF D0 02 A0 00 98 9D` sequence-loop tail. VoiceTracker is a
later editor **built on the Music Assembler player** (per WebSearch). Any
VoiceTracker-tagged HVSC tunes may be decodable with a close variant of the MA
decoder. (Detail in the sidid signature docs already in this dir.)

## Pouet

- `pouet.net/prod.php?which=41806` = "Music-assembler v1.4" (Demotool, Triad,
  1994, C64). Single comment = the King Fisher note above. No source link.
- No standalone DUSAT-V1.0 Pouet prod with technical comments was found; the
  authoritative record is CSDb #94388 (scraped separately).

## Existing decoder (lead, not chased here)

A working open-source MA/VoiceTracker decoder exists — **JITT64** (Ice Team,
GPL Java, SourceForge). The parallel research doc `forum_jitt64_importer.md`
in this dir covers it; it is the single highest-leverage external artifact for
the packed format (executable evidence the format is already fully decoded).

## Naming collision reminder

"Music Assembler V3.1 by Harald Rosenfeldt (1989, 64'er/Markt+Technik)" in
sidid.nfo is a **DIFFERENT** product. The DUSAT/Triad line documented here is
the one carrying the `Music_Assembler` player signature and the ~6,351 HVSC
tunes. Keep them separate when classifying.
