# DefleMask — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

DefleMask, a cross-platform chiptune tracker by **Leonardo "Delek" Demartino**
(2012+). 310 HVSC #84 tunes; 0 migrated. **Not a native C64 tool** — the C64 SID
is one of many target chips (Genesis/NES/GB/...). Our target is the **6502 player +
song-data layout embedded in DefleMask's `.SID` EXPORT**, NOT the `.DMF` authoring
file format (which HVSC never ships).

`Reflextracker` (137 SIDs) is a **separate engine**, not part of this family.

## ⚠ Three structurally DIFFERENT players under one family name

The decompiler must branch on the SIDId tag — these are not one player with options,
they are three separate export builds (the tag = DefleMask *app* version, in Delek's
integer-version convention):

| SIDId tag | App version | HVSC | Write model |
|---|---|---|---|
| `DefleMask_v1` | v0.9.0 (2013) | **1** | byte-at-a-time `(reg,val)` stream reader, `$80`/`$FF` separators; no shadow blit. `Green_Tea.sid` only. |
| `DefleMask_v2` | v0.9.x–0.11.x (2013–23) | **69** | write-QUEUE model: queue at ~$CFD3, flushed by play(); **Y-indexed** blit `STA $D400,Y / DEX / BNE`. |
| `DefleMask_v12` | v0.12.0+ / all v1.x (2014+) | **240** | full ZP-shadow **bank blit**: `LDX #$18 / LDA $04,X / STA $D400,X / DEX / BPL` — writes all 25 regs D418→D400 every frame. |

"v12" = **app version 0.12**, not "v1+v2". Confirmed against the DMF format version
table (v12+ = format byte 0x16).

## The v12 write model (the dominant target — 77% of the corpus)

The sidid signature `B5 ?? 9D 00 D4 CA 10 F8` and independent binary analysis agree:
**v12 is a register-bank blitter.** Every frame it copies a 25-byte zero-page shadow
(`$04–$1C`, a 1:1 mirror where ZP `$04+i` = `$D400+i`) to `$D400–$D418` in fixed
**descending** order. This is the cleanest possible Mode-1 target — the per-frame
write SEQUENCE is deterministic (D418, D417, ..., D401, D400) and the only musical
content is *what the shadow holds* each frame.

**v12 song-data layout** (per-SID, after the ~253-byte fixed player):
```
$110A-$110B  CIA timer (lo,hi) = playback rate (e.g. $49EA≈52 Hz, $4FE5≈48 Hz)
$110C-$110D  song-data pointer (lo,hi)
$110E-$1126  25-byte register REORDER table (per-tune D4xx-offset permutation)
$1127+       bit-compressed song stream
```
**Stream**: tick values (1–$9F), voice-jump 2-byte commands ($A0–$FF + lo), zero-prefix
commands (`$00,$FD`=loop-save, `$00,$FE`=loop-restore, `$00,$FF`=song-end/gate-off).
Per-voice segments use **bit-field compression**: each control byte flags which of the
25 registers changed; only changed registers carry a following value byte; the
register↔field mapping is the per-tune reorder table.

**⚠ ZP self-modifying read routine**: the player installs a 7+1-byte fetch routine at
ZP `$1F–$28` whose `LDA <ptr>` instruction literally spans `$25/$26/$27` (opcode +
pointer lo/hi), so the read address self-patches as the pointer advances. Per the CORE
TENET, the rebuild does NOT reproduce this SMC — it emits clean code producing the same
$D4xx writes.

**⚠ CIA timer writes**: v12 *writes* CIA1 timer A ($DC04/$DC05) — this is the known
cause of sidreloc warnings + hardware-incompatibility bug reports (#216, #353). v2 only
*reads* CIA1 (likely a random seed). Relevant to the dispatch/verify path.

## Effect & instrument model (the musical content the shadow encodes)

The DMF format stores only raw `(effect-code, value)` pairs — the **semantics live in
the player stub**, which Delek never open-sourced. `cluster_dmf_spec_and_effects.md`
derives the C64 effect catalogue from **Furnace** (tildearrow's open-source
DefleMask-compatible tracker — the best available reference). Highlights (full table in
that file):
- Waveform bitmask `10xx`; ADSR `20xy`/`21xy`; pulse-width fine `3xxx` + slides `22/23`;
  filter cutoff fine `4xxx` + slides `24/25`, resonance `13xx`, mode `14xx` ($D418 hi);
  ring/sync/test via legacy `1Exy`; envelope-reset controls `15xx`/`1Axx`/`1Bxy`/`1Cxy`.
- SID instrument: waveform flags, 4-bit ADSR, 12-bit pulse width, filter routing +
  init (resonance/cutoff/LP-BP-HP/CH3OFF), and macro sequences over all of the above.

## File index

| Topic | File | Reliability |
|---|---|---|
| Embedded player write model + v12 song-data layout + stream | `cluster_embedded_player.md` | primary (source + binary) |
| ↳ v12 player hex / deflestream64 asm | `src/deflemask_v12_player_hex.txt`, `src/deflestream64_main_s.txt` | primary |
| C64 effect catalogue + SID instrument model (Furnace-derived) | `cluster_dmf_spec_and_effects.md` | secondary |
| ↳ DMF format specs (3 versions, verbatim) | `src/DMF_SPECS_0x11.txt` (v9c), `0x15` (v11.1), `0x18` (v1.0.0) | primary |
| Variant→app-version map + player architecture diffs + scene | `cluster_variants_and_scene.md` | secondary |

## Corpus shape

All 310 HVSC DefleMask SIDs: **PSID v2, vblank (speed=0), single-subtune.** No
multispeed/CIA-timed playback and no multi-subtune confirmed (despite the CIA *writes*).
Most load at $1000–$1100. v12 dominates (240/310 = 77%); v2 = 69; v1 = 1 (`Green_Tea`).
Scene consensus is that DefleMask is unsuited to native C64 production (file size +
CIA-write hardware crashes) — so this corpus is exports, not scene-crafted players.

## What's solved

- **Three variants disambiguated** (tag = app version) with per-build write model.
- **v12 write model** = deterministic 25-register bank blit (Mode-1-clean) + the song-
  data layout (CIA-rate / song-ptr / 25-byte reorder table / bit-field stream).
- **Effect catalogue + instrument model** grounded in Furnace + 3 DMF spec versions.
- **Players are NOT open-source** — confirmed; deflestream64 is a VGM streamer, unrelated
  to the HVSC `.sid` player.

## What remains (migration-phase RE, not research)

- **Disassemble one v12 `.sid`** (`seed_disassembly.py` → `disassembly.s`) to close:
  the bit-field decode loop's exact X start / off-by-one for field indexing (the one
  unresolved decode detail), the reorder-table application, and the SMC fetch routine's
  pointer arithmetic. v12 is 77% of the corpus — start here.
- **v2 stream encoding** only partially traced (write-queue flush semantics) — second
  priority (69 SIDs).
- **v1** is a single SID (`Green_Tea`) — a direct `(reg,val)` stream; trivial, do last.
- **CIA-write semantics** — confirm v12's $DC04/$DC05 writes don't affect the 50 Hz
  vblank verdict (all tunes are speed=0, so the flat Mode-1 path should hold; ear-test).
- **DMF `frames_mode`/`custom_hz` ↔ PSID speed** — unresolved, but moot here since all
  HVSC DefleMask tunes are speed=0/vblank.

## Top leads (if migration needs more; mostly 503/403-blocked this session)

1. **Full v12 player disassembly** from our own binaries — the only path to the bit-field
   decode detail (no public source exists). This IS the migration first step.
2. CSDb DefleMask comment threads (503 this session) + ChipMusic.org pages 23–25 (403).
3. Furnace `src/engine/platform/c64.cpp` + DMF import (`fileOps`) for any remaining
   effect-order / compatibility-flag detail (`no1EUpdate`, `15xx` env-reset timing).
4. Older DMF versions (0x09–0x10) + the DMP instrument-patch format (not fetched).

Full provenance in each file + `provenance_log.md`.
