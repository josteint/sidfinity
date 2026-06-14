# Jeff (Søren Lund) — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

The custom SID player(s) of **Søren Lund ("Jeff")**, Danish composer (1974–2013), of
**Cyberzound Productions / Camelot** (and Daniax/X-Factor/Crest/Bonzai/Viruz/Cosine/MoN).
192 HVSC #84 tunes tagged `Jeff`; 0 migrated. Player base $1000, play $1003. Jeff wrote
~30 players + 2 editors over his career; 178/192 of the corpus is his own music. No public
source/format spec. Editors: **CZP Music Editor V2.0** (1996, never officially released,
`.d64` at CSDb #122334) and **X-SID** (Viruz, 2007, the only released one — `6581.dk/
xsid-viruz.rar`). (`Jeff_Minter`, 2 SIDs, is the unrelated Llamasoft dev — excluded.)

## File index

| Topic | File | Reliability |
|---|---|---|
| Write model + binary structure + variant taxonomy | `cluster_write_model_and_variants.md` | secondary (binary) |
| ↳ annotated V9.6 hex dump | `src/action_hunter_v96_hexdump.txt` | primary |
| Author + editor + feature model (from interviews) | `cluster_author_and_editor.md` | secondary |
| ↳ Remix64 2002 + Recollection interview transcripts | `src/remix64_interview_2002_lund.md`, `src/recollection_domination13_interview.md` | primary |
| HVSC corpus / address clusters / scene | `cluster_corpus_and_scene.md` | primary (DB) |

## What's solved

**Binary structure** (V9.x, the dominant ~130 SIDs, $1000 base) — version string
`-PLAYER V9.6 (C) JEFF / CAMELOT-` at $1020:
- `$1000–$1005` two JMP trampolines (init, play); `$1040–$10C3` per-voice state (7-byte
  stride, X=0/7/$0E); `$10C4–$1183` freq lo+hi tables (96 entries each); `$1184–$11A3`
  arp/vibrato semitone offsets; `$11A4–$12EF` init; `$12F0–$17B7` play+effect chain;
  `$17C8–$17FF` 16-bit address table (orderlists → instruments → patterns); `$18xx+`
  instrument programs then pattern data.
- **Pattern format**: `(duration:u8, note:u8)*` terminated by `$FF`; notes $01–$7B =
  semitone, `$7F`=tie, `$7D`=rest. **Instrument programs**: `(duration:u8, wave:u8)*`,
  e.g. `$41`=pulse+gate, `$21`=saw+gate, `$81`=noise+gate, `$FE`=loop.

**Per-frame write model** (VBI ~50 Hz, speed=0):
1. `$D418` (vol|filter-LPF) — **unconditional, first write every frame**.
2. Per-voice (X=$00/$07/$0E): `$D415/$D416` filter (cond.), `$D402/$D403` PW (cond.),
   `$D404` gate-off+old-wave (new note — hard restart), `$D405/$D406` ADSR (new note, not
   tie), `$D400/$D401` freq (new note or glide/vibrato), `$D404` gate-on+new-wave.
3. `$D417` (filter mode) is **init-only**.
- **Gate**: hard-restart (`$D404` written twice per new note); `$7F` tie = no gate toggle;
  `$7D` rest = gate=0. **Additive freq lookup**: vibrato+glide+arp accumulate, then
  `(counter & $1F)×8` indexes the 96-entry split freq table.

**Feature model** (from the Remix64 2002 interview): JCH-like two-level track/sequence;
**wave-freq tables**, **glide table**, **detune table**, **vibrato table**, **ADSR/gate-
manipulation table** (enables tremolo/echo/reverb-like effects); heavy pulse programming;
extensive combined-filter use; multispeed via wave-freq tables; max **$1C rastertime**.
Hard-restart present in V9.x (per binary), though Jeff disliked HR conceptually.

## ⚠ Variant taxonomy — NOT all one engine (binary analysis refines this)

The sidid sub-tags split into THREE classes (the byte-level binary check is authoritative):

| Variant | HVSC | Relationship to V9.x core |
|---|---|---|
| `Jeff` (V9.x) | ~bulk | the canonical engine |
| `Jeff/BullSID` | 3 | **same engine** — init/exit micro-variant (ZP $FB/$FC saved to RAM, not stack) |
| `Jeff/FLT` | 2 | **same engine** — init-only (adds PW priming $D402=$00/$D403=$08); CSDb: "custom player for One Million Lightyears from Earth/FairLight" |
| `Jeff/BullSID3` | 2 | **same engine** — init-only (full `LDY #$16` SID clear) |
| `Jeff/Airwalk` | 3 | **OLDER, DIFFERENT engine** (V4) — 3-ZP-pointer scheme ($F9/$FA/$FB), fixed absolute JSR targets |
| `Jeff/XLarge` | 3 | **DIFFERENT engine** — a tiny direct-table player, no tracker |
| X-SID (2007) | ~1 | **genuine redesign** — 3-iter Y init, 2 JSRs/voice, all regs every frame (not fingerprinted in sidid) |

So BullSID/FLT/BullSID3 fold into the V9.x extract path; **Airwalk (V4), XLarge, and X-SID
need their own paths** (small counts). The `$FD0`-base era (19 SIDs, 1991–94) is an earlier
player generation (predecessor to V9.x) — also a likely separate layout.

## Corpus shape (192 `Jeff` tunes; ~205 incl. sub-tags, all PSID v2)

78.5% canonical $1000/$1003; the rest = relocations ($B00 Crest-2000, $E000, $8000) +
the $FD0 stub era (19, earlier gen) + one-offs (24 distinct init/play pairs). Only 6 SIDs
multi-subtune (max 4; the Jeff/FLT 2-subtune = 6581+8580 versions). Author concentration:
Søren Lund 174/205 (85%), Duck LaRock/Anders Daugaard 14 (CZP co-founder, shared the
binary). Span peaks 1991–94 (Camelot era), extends to 2013; 4 tribute SIDs 2021–25. STIL
has ~20 first-person Jeff annotations; no engine tech doc in HVSC DOCUMENTS. CIA fraction
unconfirmed (no DB speed field) — V9.x is VBI/speed=0; verify the relocated/old-gen ones.

## What remains (migration-phase RE)

The V9.x flow + formats are well-mapped; the binary record offsets + older gens are open:
- **Disassemble one V9.x $1000 tune** (the `src/` hex dump is a head start) to confirm:
  the instrument-program full opcode set ($7C/$FC/$FD pattern bytes, the wave-byte table),
  whether orderlists select patterns vs only step duration, and the 16-bit address-table
  indexing.
- **Older/other engines** as separate paths: the **$FD0-era predecessor** (19), **Airwalk
  V4** (3, 3-ZP-pointer), **XLarge** tiny player (3), **X-SID** (2007 redesign). Small but
  distinct.
- **CZP Music Editor V2.0 `.d64`** (CSDb #122334) contains the canonical editor binary +
  4 example SIDs — **inspecting it is the highest-value next step** (format spec by example).
- Confirm VBI-only (no DB speed field) for the relocated/old-gen subsets.

## Top leads

1. **CZP Music Editor V2.0 `.d64`** (CSDb #122334) — canonical editor + example SIDs.
2. **X-SID** (`6581.dk/xsid-viruz.rar`, CSDb #47985) — the released 2007 editor; documents
   the redesigned data format.
3. Interview transcripts (`src/`) already captured — re-read for effect-table semantics.

Full provenance in each file + `provenance_log.md`.
