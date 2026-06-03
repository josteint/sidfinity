# FutureComposer — research index

24 documents (~4000 lines) covering the MoN/FutureComposer driver family,
gathered 2026-06-03 to scope the byte-exact rebuild of Hawkeye.sid (Jeroen
Tel, 1988) and similar V3.x-lineage tunes.

## TL;DR

The sidid label `MoN/FutureComposer` is an umbrella over a single driver
lineage with several variants. **Charles Deenen wrote the original MoN
driver in 1987** (first heard in *Noisy Pillars*, Scoop Designs 1987 —
init=$1800, play=$1806, +6 offset). **Juha Granberg / FCS ripped it for
the FC editor in June 1988**; FCS later admitted in interview that
"ripping other's code was wrong." Deenen and Tel sent cease-and-desist
letters; the FC editor scene continued anyway.

The driver evolved into several variants that share the V3.x sidid
signature: FC V1.0–V5.0 editor releases (Mnemonic Designs, Union,
Dynamix, Warlords); Tel's own MoN driver (Hawkeye, Cybernoid II);
Deenen's MoN driver (Noisy Pillars); Bjerregaard's MoN variant. They
differ in entry layout (+3 vs +6 — see below), subtune count cap, and a
few effect-slot details, but **the per-frame data-execution code is the
same lineage.**

**+3 vs +6 entry offset is NOT a different driver.** It's two layouts of
the same interface: V4 inlines bytes 0–5 and starts play at +6; V3.x
(including Hawkeye) uses 3-byte JMP trampolines at +0/+3. A single
rebuilder can produce either layout based on per-SID config.

## Canary: Hawkeye.sid

| | |
|---|---|
| Path | `hvsc84/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid` |
| Author | Jeroen Tel |
| Year | 1988 (Thalamus) |
| Load addr | $7AE0 |
| Init / play | $7AE0 (JMP $918F) / $7AE3 (JMP $7B98) — +3 offset |
| Subtunes | 12 |
| Length | 18:52 (longest in Cujo's curated set) |
| Driver | Deenen's MoN routine, Tel variant |
| File size | 8768 bytes (PSID + plaintext body; no depacking needed) |
| FC V3.x sig | found at $7C1F / $7C22 inside the binary |
| MoN/FC top sig | $7D9C |

**Per-voice runtime variables located by signature scan:**
```
tabcount   @ $90C5   (per-voice 3 bytes — sequence-pos counter)
begcount   @ $90C8   (per-voice 3 bytes — section-start pos)
repeatsto  @ $9118   (per-voice 3 bytes — pattern repeat stack)
voiceinc   @ $9139   (per-voice 3 bytes — wave-table advance counter)
```

These are the anchor points for any future py65 trace.

## Primary byte-exact reference

**`/tmp/fc_research/c64_6581_sid_players/Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm`**
— 1817 lines of ACME source for Cybernoid II (same author + same year +
same driver as Hawkeye). The single most valuable artifact for rebuild.
Contains the full instrument-byte semantics, pattern-byte dispatcher
(`CMP #$60 / CMP #$40` — the FC_V3.x signature shape), 96-entry PAL
freq table, 9-knob per-tune config, and 18-step effect chain order.

Three of the four research agents independently flagged it as their
highest-value find.

## File index

### Format specs

| File | Source | Reliability | Content |
|------|--------|---|---|
| `research.md` | Initial summary (pre-2026-06-03) | secondary | 95-line overview — version timeline, basic format outline |
| `wiki_fc_v41_manual.md` | CSDb getinternalfile 224874 | **primary** | Full FC V4.1 manual by The Beat-Machine: 8-byte instrument layout, track byte ranges ($00–$2B jump, $3F+ repeat, $80+ transpose, $FE/$FF/$FD terminators), opcode `$FD` = global song-table terminator |
| `csdb_format_inferences.md` | synthesis of CSDb binaries | secondary | Wave-table 3-tier dispatch, filter-table fetch, voice indexing |
| `wayback_fc4_binary_strings.md` | FC V4 binary | secondary | UI structure: 16-entry wave program, 10-drum slot count, `$FF/$FE` terminators, `$4000` default relocation |
| `github_fc14_amiga_spec.md` | ImHex pattern (Amiga FC1.4) | tertiary | Note: Amiga FC ≠ C64 FC — separate codebase. Included for structural analogy only |

### Driver disassemblies

| File | Source | Reliability | Content |
|------|--------|---|---|
| `github_realdmx_mon_players.md` | github.com/realdmx/c64_6581_sid_players | **primary** | Cybernoid II ACME dissection: zero-page map, sequence command bytes, 8-byte instrument format, fx-flag bit map |
| `wayback_cybernoid2_driver.md` | mirror of same | **primary** | Cybernoid 2 driver verbatim with annotations |
| `wiki_mon_driver_disasm.md` | TurboAsm→ACME notes | **primary** | Tel/Deenen/Bjerregaard MoN drivers compared |
| `csdb_fc_v4_player_disasm.md` | CSDb V4 standalone player | **primary** | Full 80-byte FC V4 standalone player annotated. Smallest complete FC driver harness |
| `hawkeye_sid_layout.md` | direct binary parse of Hawkeye.sid | **primary** | PSID parse + signature scan + per-voice variable map (the addresses above) |
| `csdb_hawkeye_provenance.md` | CSDb #28158 | secondary | Hawkeye header facts + entry prologue |

### Engine identification

| File | Source | Content |
|------|--------|---|
| `csdb_sidid_signatures.md` | cadaver/sidid | 5 FC-family signatures with 6502-level decode |
| `github_sidid_signatures.md` | same | duplicate analysis from different agent |
| `wayback_sidid_signatures.md` | same | with mnemonic decoding of `LDY #$06; DEY×6` literal-in-code |
| `wiki_sidid_signatures.md` | same | FC + 8 sibling MoN drivers |

### Context

| File | Content |
|------|---|
| `wayback_lineage_and_corrections.md` | Lineage timeline + corrections to `research.md` |
| `wayback_csdb_release_history.md` | Per-release credits |
| `csdb_release_catalogue.md` | Full PRG inventory across CSDb D64s with load addresses |
| `csdb_player_note_text.md` | Verbatim V4 PLAYER NOTE BASIC |
| `csdb_fc_editor_binaries.md` | Index of staged editor binaries |
| `forum_csdb_lemon64.md` | CSDb forum + Lemon64 + Recollection extracts |
| `github_libsidplayfp_negative.md` | Confirmed: libsidplayfp has zero FC support; siddump remains ground truth |

### Process

| File | Content |
|------|---|
| `leads.md` | Open leads for next research pass |
| `provenance_log.md` | Every URL attempted (376 lines) — success and failure |

## Staged binaries (artifacts/)

Seven FC-family editor binaries downloaded from CSDb, available at
`pipelines/future_composer/artifacts/`:

| Binary | Notes |
|---|---|
| `FC_V1.0.prg` | Earliest editor release |
| `MoN_FC_V3.0.prg` | Mnemonic Designs 1989 — packed |
| `FC_V3.1.prg` | Union 1990 — packed (marker `'2066 CODE'`) |
| `FC_V4.0.prg` | Dynamix 1989 — with TestTunes |
| `FC_V4.1.prg` | Beat-Machine — referenced by `wiki_fc_v41_manual.md` |
| `FC_V4_Player_4000.prg` | **80-byte standalone player**, unpacked plaintext. Complete IRQ/banking/subtune-init protocol. Smallest known-good driver harness |
| `FC_Relocator.prg` | Address-relocation tool |

## Key technical facts (synthesized)

### 8-byte instrument format
```
+0  pulse_hi
+1  waveform / ctrl
+2  attack / decay
+3  sustain / release
+4  filcount (filter table pointer)
+5  fx1 (vibrato?)
+6  fx2 (arpeggio?)
+7  fx3 (drum/skydive flags + bits)
```

### Sequence command byte ranges
- `$00–$2B` — jump to pattern
- `$40–$5F` — transpose
- `$60–$7F` — voice increment / wave-table command
- `$80–$BF` — repeat
- `$E0–$EF` — glide
- `$F0` — filter-set
- `$FD` — global song-table terminator (V4.1)
- `$FE` — end-of-pattern
- `$FF` — end-of-sequence

### Other constants
- 96-entry PAL freq table (C-0 to B-7)
- 16-entry wave program
- 10 drum slots
- 18-step effect-chain ordering
- $4000 default relocation address
- Per-voice state arrays in editor: 3 bytes (one per voice)

## Open gaps / next steps

1. **Disassemble Hawkeye.sid directly.** All ingredients ready: PSID body
   is plaintext (no cruncher), variable addresses located, primary
   reference (Cybernoid2.asm) loaded. Run
   `tools/seed_disassembly.py hvsc84/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid`
   with the variable addresses passed as `--entry` hints. Output goes to
   `pipelines/future_composer/<engine>/disassembly.s` (or similar) for
   hand-annotation.

2. **Depack the FC V3.0/V3.1 editor binaries** (`'2066 CODE'` marker —
   Equinoxe/Pu-238 cruncher family). Once unpacked, the editor's
   reference player code is recoverable byte-for-byte. Lower priority
   than (1) — Hawkeye gives us the same code in a plaintext SID.

3. **18 small known-good FC tunes** (KIPPER1..14 from FC V4 editor +
   4 acid-demo bundles) as a regression-set alongside Hawkeye. Use after
   the first byte-exact rebuild passes.

4. **Restore64.dev** advertises 787-signature byte-exact reassemblable
   disassembly. Try it as a cross-reference on Hawkeye once we have our
   own disassembly via `tools/seed_disassembly.py`. Don't formalize as a
   toolset entry pre-emptively — see-it-first.

## Provenance integrity

Every doc in this folder begins with a YAML frontmatter block declaring
its `source_url`, `fetched_via`, `fetch_date`, and `reliability`. When
two sources disagree, the higher-reliability source (primary) wins.
`provenance_log.md` lists every URL the four research agents attempted —
~50 successes plus the failed pages, so future research waves don't
re-fetch.

Wayback Machine was blocked in the harness — pivoted to direct mirrors
(funet, zimmers, GitHub raw, CSDb getinternalfile.php).
