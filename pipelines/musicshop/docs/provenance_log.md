# Provenance log — The Music Shop research sweep (2026-06-14)

Every source attempted this sweep. The 50-page user manual + the byte-stable player
structure are captured; the note-column sub-structure is migration-phase RE.

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/musicshop/docs/research.md` | read | pre-existing stub (manual archived at IA) |
| `tools/sidid.cfg` (local) | read | single `MusicShop` sig (16-bit indirect pointer-add note-walk) |
| `tools/engine_docs.json` | read | prior state |
| `hvsc84.db` (read-only) + PSID header read | queried | 182 SIDs, fixed $A04D/$575A; **speed=0x01 = CIA-timed** (confirmed) |

## Phase 2 — cluster agents

### Manual + program (cluster_manual_and_program.md)
| Source | Status | Notes |
|---|---|---|
| archive.org The_Music_Shop_Users_Manual (50-page OCR) | fetched | full notation/synth model → `src/manual_full_text_extract.md` |
| Commodore 64/128 Music Software Guide (Gilkes 1986), Compute! #60, Lemon64 t=45281/t=36765 | fetched | feature corroboration + `.seq` format note + MIDI version |

### Write model + binary (cluster_write_model_and_binary.md)
| Source | Status | Notes |
|---|---|---|
| HVSC MusicShop binaries (read-only inspection) | analysed | 3-region layout, note format, note-walk → `src/payload_layout_95f6.txt`, `src/sidid_and_note_walk_978a.txt` |
| Lemon64 partial-RE thread | fetched | confirms layout-encoding (symbol-code + vertical placement) |
| cadaver/sidid sidid.cfg | read | signature provenance |

### Corpus + scene (cluster_corpus_and_scene.md)
| Source | Status | Notes |
|---|---|---|
| `hvsc84.db` (read-only) | queried | fixed-layout confirmation; folder breakdown; Karateka |
| HVSC DOCUMENTS/STIL (local) | read | no Music Shop entries |
| archive.org magazines / mobygames / Brøderbund history | fetched | release date, MIDI version, historical context |

## Failures / blocked (retry later)
- **The step_size column sub-structure** (gate/duration/vibrato/filter/PW extra bytes) —
  needs `siddump --writelog` correlation + a $575A/$978A disassembly (migration phase).
- **Compute! Gazette Aug 1985 review** — PDF too large to extract.
- **The Music Shop program disk** — not fully retrieved; the editor save/playback code is
  the best remaining format source.
- Author name Don vs Dan Williams — unresolved (manual says Don).