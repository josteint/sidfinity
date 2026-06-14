# The Music Shop (MusicShop) — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

The Music Shop — a **1984 commercial C64 music-composition program** by **Don Williams**,
published by **Brøderbund Software** ($44.95, released 1984-09-27; a MIDI version followed
in 1985 via Passport). 182 HVSC #84 tunes; 0 migrated. **It is a graphical staff-notation
editor, NOT a tracker** — the most application-like target in the project. The full 50-page
user manual was recovered (`src/manual_full_text_extract.md`).

## ⚠ This is a ripped commercial application, not a relocatable player

180/182 SIDs share **one fixed layout**: init=`$A04D`, play=`$575A` (PSID load=$0000 →
actual payload load=`$95F6`). The play vector at `$575A` is **not in the payload** — the
init routine copies stubs from the payload down into low RAM (~$575C, ~$5E46). So HVSC
MusicShop SIDs are the running commercial program captured in place, not a small player.
Exceptions: Karateka (relocated to $1000 for game integration; its music was composed in
Music Shop by Francis Mechner) and one fan Boulder Dash.

**⚠ CIA-timed**: PSID `speed=0x00000001` confirmed across the corpus (direct header read).
The family needs the **Trap-C `--writelog-per-irq`** verdict path, NOT the flat 50 Hz path.

## File index

| Topic | File | Reliability |
|---|---|---|
| Binary structure + per-frame write model + note format | `cluster_write_model_and_binary.md` | secondary (binary) |
| ↳ payload memory map + note-walk disasm | `src/payload_layout_95f6.txt`, `src/sidid_and_note_walk_978a.txt` | primary |
| Manual + program + full musical/notation model | `cluster_manual_and_program.md` | primary (manual) |
| ↳ full 50-page manual text | `src/manual_full_text_extract.md` | primary |
| HVSC corpus / fixed layout / historical context | `cluster_corpus_and_scene.md` | primary (DB) |

## What's solved

**Binary structure** (3 regions, byte-stable player across all 182):
- **Player stubs `$95F6–$A0FF`** (2570 B, identical every tune): note-walk routine (SIDId
  sig at `$978A`), per-voice play stub, and the init that re-installs everything into low
  RAM. Duration table at `$97D0` = `[0,20,40,60,80,100,120,140]` ticks.
- **Song header `$A100–$A1FF`** (→ runtime $77D4): `step_size` at $77D5 (4–20, varies by
  song), `"MS"` magic at $77E0, per-voice ADSR blocks (5 B × 3 voices), CIA tempo bytes $77DA.
- **Note data `$A200+`** (→ runtime $78D4): **always 480 note-columns × step_size bytes**
  (4×480=1920 … 20×480=9600). First 12 B zero (3 silent columns). Each column = one
  time-slice for all 3 voices.

**Note format**: 2-byte **SID frequency pairs** `[freq_lo][freq_hi]` LE (`$0000`=rest);
validated against known scores (Canon in D D6≈$4E68, Maple Leaf Rag C6≈$4669). Stream
markers: `$FD`=tie, `$FA`=end, `$FC`=loop-back, bit7=1=rest. The note-walk (`$978A`) reads a
2-byte relative offset from the note record + adds step_size to advance a per-voice pointer
`$3F:$40` — **a relative-offset linked list within the note stream**. The `step_size` extra
bytes beyond the freq pair carry gate/duration/vibrato/filter/PW (exact sub-structure = the
main RE gap). **Notably the player stores SID-frequencies directly** (the notation→pitch
conversion happened at save time in the editor), so we don't re-derive pitch from staff
position — the SID stream is the data.

**Musical model** (from the manual — what the score represents):
- Up to 20 pages (double-staff); **3 voices = 3 SID oscillators**, ≤3 simultaneous notes/column.
- Pitch by vertical staff position (treble/bass clef, accidentals, key sigs, octave shifts).
- Durations whole→32nd + dotted + rests + ties + triplets; any time signature.
- **Per-voice SID synth**: ADSR (4 sliders), waveform (tri/saw/pulse/noise), control
  (gate/sync/ring/vibrato), pulse-width (coarse/med/fine), filter (LP/BP/HP + cutoff +
  resonance). **8 factory presets**, switchable mid-score via embedded `COMMODORE+1–8` events.
- Globals: tempo (Tp), master volume (Vo), vibrato intensity (Vi).
- `.seq` save file stores **screen layout** (symbol-code + vertical-placement per voice per
  column), not abstract pitch/duration — but the SID **export** (what HVSC has) is already
  the frequency stream above.

## Corpus shape (182 tunes — all PSID v2, all CIA-timed speed=1)

180/182 the fixed $A04D/$575A layout; single-subtune except Karateka (20). Folders:
`DEMOS/UNKNOWN/Music_Shop` 121 (international community content, mid-late 80s, propagated
via a 1988 crack — Polish/German clusters), `Williams_Don` 28 (the author / retail bundle),
`Safavy_Mehdi` 20 (Farsi originals), Ewens_Louis 3 (Brøderbund demos), + 10 games/demos. No
HVSC DOCUMENTS/STIL entries.

## What remains (migration-phase RE)

The player + note-stream skeleton are mapped; the column sub-structure is the open work:
- **Disassemble the $575A/$978A player** (the `src/` disasm is a head start) to decode the
  **`step_size` column sub-structure** — which of the extra bytes drive gate, note duration,
  vibrato, filter, PW per voice (correlate against `siddump --writelog`).
- **Per-voice ADSR/preset application**: the 5-byte ADSR blocks + how `COMMODORE+1–8`
  preset-switch events appear in the stream → which $D4xx writes.
- **CIA tempo decode**: $77DA/$77DB CIA bytes → the per-IRQ rate; verify on `--writelog-per-irq`.
- **Confirm note-stream markers** ($FD tie / $FA end / $FC loop / bit7 rest) and the 480-column
  invariant across the corpus.

## Top leads

1. ~~User manual~~ — **OBTAINED** (`src/manual_full_text_extract.md`).
2. The Music Shop **program disk** (archive.org / CSDb #82453) — the editor's save/playback
   code documents the column format precisely; pair with the `src/` player disasm.
3. **siddump --writelog correlation** on a known-score tune (Canon in D) — the cheapest way
   to map the step_size extra bytes to $D4xx writes (migration phase).

Full provenance in each file + `provenance_log.md`.
