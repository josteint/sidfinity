# AMP (Advanced Music Programmer) — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

AMP — "Advanced Music Programmer", **V2.3** — by **Andrew Miller (= András Molnár,
handle "Burton")**, a Hungarian scener (groups Euratom / Quality / Hitech Studio
Designs), with co-development + all the demo songs by **Markus Müller ("Hayes")**,
1988–1990. Published commercially via the German disk magazine **Magic Disk 64
12/1991** (CP Verlag). 246 HVSC #84 tunes; 0 migrated. Player base $1000, play $1003.
No public source. (Authorship per the embedded binary credits string — saved at
`src/amp_binary_credits_extracted.txt`; H.I.C./John Almási's exact role in the Quality
release is unresolved.)

## File index

| Topic | File | Reliability |
|---|---|---|
| Per-frame write model + binary layout + SMC + frequency table | `cluster_write_model_and_binary.md` | secondary (binary) |
| ↳ disasm fragment + freq/instrument tables | `src/Anti_Airwolf_player_disasm.txt` | primary |
| Editor + feature model + provenance + 4-file format | `cluster_editor_and_magicdisk.md` | secondary |
| ↳ binary credits + .DAT structure notes | `src/amp_binary_credits_extracted.txt`, `src/amp_dat_file_structure_notes.txt` | primary |
| HVSC corpus / address clusters / scene | `cluster_corpus_and_scene.md` | primary (DB) |

(No formal format spec or source was published; structure is from byte-stable binary
analysis. The `.DAT`/`.VOI`/`.NOT`/`.SNG` editor files are the authoring format; HVSC
ships the assembled `.sid`.)

## What's solved

**Binary layout ($1000 base — 142/246 SIDs; player kernel byte-identical bar ~10 SMC bytes):**
- `$1000` JMP init; `$1003` JMP play.
- `$100B–$1015` 11-byte song config (voice_enable, filter_res_route, order_length,
  repeat_count, pattern_count, speed, runtime counters).
- `$1016–$102D` 12 × 2-byte LE pointers (3 voices × 4 track tables).
- `$102E–$108F` per-voice runtime state, **7-byte stride at X=0/7/14**.
- `$10D8–$1138` freq LO (96 entries, entry 0 = silence); `$1139–$1199` freq HI (parallel).
  PAL-standard, entry 24 = C2 = $041B; covers C#0–B7.
- `$119E–$162D` player kernel.
- Song-data block (38 bytes, addr in `$1009/$100A`): [0..23] = 12 LE track pointers;
  [24..37] = config + the SMC table addresses.

**Per-frame write model** (per `play()`):
1. guard active_flag + ZP save; 2. per-voice note decode (JSR $119E): `$D405,X` (AD),
`$D406,X` (SR) from the instrument program, freq+vibrato → `$D400/$D401,X`, `$D402/$D403`
(PW), `$D404,X` (wave+gate); 3. filter sub ×3 (X=0/7/14): `filter_table[pos]` → `$D416`,
then `master_vol | filter_mode` → `$D418`; 4. `$D417` (resonance + voice routing) from
per-voice state; 5. tempo advance + position/loop/repeat; 6. ZP restore. (`$D415` filter-lo
likely not written per frame — OPEN.)

**SMC mechanism**: `init()` patches ~5 kernel locations with per-song table addresses
(vibrato-delta ×2, filter-cutoff, pitch-glide ×2), sourced from the song block. Per the CORE
TENET the rebuild emits clean code producing the same writes — it does NOT reproduce the SMC.

**Track-table format** (per voice, 4 parallel byte arrays): note_seq / transpose_seq /
instprog_lo_seq / instprog_hi_seq. The instprog hi:lo pairs are double-indirect pointers to
**wavetable-style instrument programs** (AD/SR header + waveform control byte sequences).

**Instrument model (16 params)**: AD, SR, pulse-hi, add-pulse, vibrato start/end, **"accord"
(arpeggio) start/end** (German "Akkord"), filter start/end, waveform start1/end/start2, glide
control, filter byte1 ($D417), filter byte2 ($D418). Effects: vibrato (range-table), arpeggio,
filter sweep (range-table, two SID bytes), two-segment wavetable, glide, PWM.

**Note encoding** (from the editor format): high-2-bit class (note/hold/rest/command) +
low-6-bit note number; **German note names (H = B♮)**; `$80` rest, `$40` hold/tie, `$00` empty.

**Editor 4-file format**: `.SNG` (song order), `.VOI` (instruments), `.NOT` (patterns),
`.DAT` (packed combined, loads $2FFA).

## Corpus shape (246 tunes — all PSID v2, all VBL, no CIA)

One relocatable player kernel; the address spread is relocation/packaging, not engine variants:

| Cluster | init | play | Count | Note |
|---|---|---|---|---|
| canonical $1000 | $1000 | $1003 | 142 | the reference layout |
| +3 offset | $1003 | $1006 | 25 | extra JMP at $1000 (demo hook); same kernel |
| $C003 (LMan) | $C003 | $C006 | 9 | relocated |
| $2800 | $2803 | $2806 | 9 | relocated |
| $E000 | $E000 | $E003 | 5 | relocated |
| **early Euratom (pre-v2.3)** | $13xx etc | varies | 8 | 1988-89 — may be a DIFFERENT/earlier driver |
| play=$0000 / scattered | — | varies | ~48 | audit |

All single-subtune except 15 (max 21, Griff/Pot_Fun). Peak 1991–1993 (70%). Authors:
Nantco Bakker (NL, 49, mostly the 1992 Warriors of Music batch), Dr. Zoom (CH, 30), Markus
Müller (DE, 27 — also co-author), Griff (HU), Black Dove (ES). German-distributed (Magic
Disk 64) → German/Dutch scene dominance. No HVSC DOCUMENTS/STIL mention.

## What remains (migration-phase RE)

The kernel + write model are well-mapped; the data-byte details are the open work:
- **Disassemble a canonical $1000 tune** (the `src/` disasm is a head start) to pin: the
  exact **note_byte → note_index** formula, the **instrument-program terminator** byte, the
  gate/hard-restart mechanism at ~$14C8 (`$81` → `$D401,X`), and whether `$D415` is written.
- **Confirm the early Euratom (1988-89, $13xx) tunes** use a pre-v2.3 driver — they may need
  a second layout/extract path (8 SIDs) or be out of the canonical fingerprint.
- **Audit the play=$0000 + scattered tunes** before counting them in scope.
- **X-Ample relationship** — is it a separate engine or an AMP variant? (already a separate
  `xample` family in our DB — confirm no overlap.)
- No CIA → flat Mode-1 path family-wide.

## Top leads (if migration needs more)

1. **A.M.P. V2.3 Pack** (NDC 1992, CSDb #200544) — reportedly bundles **Cobra's
   documentation**; the closest thing to a format spec. Fetch + read the D64.
2. **Magic Disk 64 12/1991 D64** (archive.org MD64 scans) — likely a German-language
   tutorial for AMP; mount + read.
3. CSDb #35519 editor disk — the editor's data-entry code documents the in-memory format.

Full provenance in each file + `provenance_log.md`.
