# MoN / Deenen player — research docs index

**Engine:** Maniacs of Noise driver ("Musicfile" / Music_Assembler family) by
Charles Deenen, with variants by Jeroen Tel, Reyn Ouwehand and a Johannes
Bjerregaard fork. HVSC engine tag: **`MoN/Deenen`** (135 SIDs in HVSC #84).
Load address consistently `$1000`; 3-voice; commercial C64 game-music driver,
~1988–1993, written in TurboAssembler, distributed only as binary.

Research sweep: 2026-06-15, follow-up wave 2026-06-16 (research-player skill).
GATHER+SUMMARISE phase only — no reverse-engineering done here. State after the
follow-up: **OK** (sweep complete; recovered/RE'd player source for every
variant + full sidid signatures + decoded format; remaining items are
migration-phase work, not research). Cleared to start disassembling.

## Files

| File | What it is |
|------|-----------|
| `research.md` | Original 7-line stub (pre-sweep). |
| `forums_wiki_findings.md` | **Best single doc.** Per-variant format breakdown extracted from the recovered sources: instrument records, sequence-byte encodings, effect tables, the MoN family tree, variant comparison. Start here. |
| `followup_csdb_findings.md` | **Wave-2.** Monase tool contents (editor/relocator/crash-saver), MONASE editor binary strings + SFX `.SFX` data-format hints, full Bjerregaard James-Bond-3 instrument/sequence decode, digi-routine decode. |
| `followup_sidid_subvariant_identity.md` | **Wave-2.** Decodes the sidid sub-signature names + maps variants to author clusters + the digi-variant analysis. **Read the disambiguation below before trusting the counts.** |
| `archive_author_findings.md` | Archive.org / author-site / CSDb sweep; history + tool releases (MON SFX Editor/Relocator/Crash Saver). |
| `web_search_findings.md` | Web search sweep; sidid fingerprint overview + biographical context + leads. |
| `local_analysis.md` | What our own repo/HVSC already knew before the sweep. |
| `src/*.asm` | **Recovered/RE'd player sources** (ACME, from `realdmx/c64_6581_sid_players`; complete — repo holds nothing more for MoN): Deenen Test Tune 1/2 + SFX Player, Tel Cybernoid 2, Ouwehand Armada + Dutch Breeze, Bjerregaard Myth + James Bond 3. The holy grail — exact data layout per variant. |
| `src/realdmx_README.md` | Root README of the source repo. |
| `src/sidid_cfg_*.txt` | **sidid signatures.** `sidid_cfg_cadaver.txt` is authoritative (others 404'd; signatures identical upstream). Every MoN/* + Music_Assembler pattern + NFO author/reference notes. |

## What we have (quality: good)

1. **Reverse-engineered player sources for every major variant** (`src/*.asm`) —
   Deenen, Tel (Cybernoid 2), Ouwehand (Armada, Dutch Breeze), Bjerregaard
   (Myth). These give exact instrument/sequence/effect layouts. This is enough
   to start a `disassembly.s` + extractor without re-deriving the format.
2. **Common-core format** (all non-Bjerregaard variants): 8-byte instrument
   record `[waveform, AD, SR, gate_len, pulse_fx, fx1=vibrato, fx2=pulse_sweep,
   fx3=arp/drum/flags]`; 96-note freq table (C0–B7); sequence stream with
   `$C0–$DF`=instrument, `$80–$BF`=note length, `$FF`=loop, `$FE`=end; effects
   = vibrato / pulse-sweep / glide / arpeggio / drum / filter. See
   `forums_wiki_findings.md` for per-variant divergences.
3. **Bjerregaard fork** is structurally different (AD/SR-first instrument byte
   order, different sequence opcode ranges, "second sustain", global tempo) —
   treat as a separate sub-engine.
4. **Full sidid signature set** (`src/sidid_cfg_cadaver.txt`) — `MoN/Deenen`,
   `MoN/Bjerregaard`, `MoN/Cyb2`, `MoN/TTWII`, `MoN/JTS`, `MoN/RWE`,
   `MoN/Bantam`, `MoN/Deenen_Digi`, plus the related `Music_Assembler` family.
   **Not yet ported into our `tools/sidid.cfg`** — open task.

## Key disambiguations — THREE separate HVSC engine tags

sidid emits three distinct `MoN/*` engine tags. **This doc covers only the
first.** Do not conflate them:

| HVSC tag | SIDs | Our family | Notes |
|----------|------|-----------|-------|
| **`MoN/Deenen`** | **135** | **`mon_deenen`** (this engine) | Tel 72 / Deenen 19 / Ouwehand 16 + minor. The 8 cfg signatures in the `MoN/Deenen` section. |
| `MoN/FutureComposer` | 4024 | `future_composer` | The FC standard player (Deenen wrote it, Juha Granberg/FCS the editor; ref SID `Tel_Jeroen/Noisy_Pillars_tune_1.sid`). **The tune-named sub-signatures `(MoN/Cyb2)`, `(MoN/TTWII)`, `(MoN/JTS)`, `(MoN/RWE)`, `(MoN/Bantam)` AND `(MoN/Deenen_Digi)` are all parenthesised sub-IDs UNDER this section — they roll up to `MoN/FutureComposer`, NOT to `MoN/Deenen`.** So the 16 digi tunes are FutureComposer-classified, handled by the FC family, not here. |
| `MoN/Bjerregaard` | 77 | (own) | Johannes Bjerregaard's **fork** — structurally different (see below). Tagged separately; not in the 135. Our `src/*.asm` includes two Bjerregaard sources (Myth, James Bond 3) for reference, but migrating it is a separate engine. |

- The parenthesised sub-IDs only surface via `sidid -s"(MoN/Cyb2)"`; normal
  sidid output (and our DB `engine` column) reports just the parent tag.
- **JCH NewPlayer / JCH format ≠ MoN/Deenen.** JCH is Laxity's player for Tel's
  *demoscene* music; Tel's *game* music used the MoN driver. Separate engines.
- **`Music_Assembler`** (Dutch USA-Team, 6351 SIDs) is an unrelated family
  despite sharing the cfg file — no code relationship.

## Status of leads (wave 2 resolved most)

Chased and **closed**:

- ✅ **realdmx repo fully inventoried** — we now hold every MoN-related source
  it has (added Bjerregaard James Bond 3 + the repo README). No per-folder
  READMEs exist; the RE author left no separate format notes.
- ✅ **Monase / Music-Mania zip contents identified** — `Monase_1.0.zip` =
  one D64 with `MONASE V1.0` editor (~28 KB, $0801–$79A1), `SFX RELOCAT.`,
  `SFX CRASHSV.`; `Music Mania.zip` = two demo-music D64s, no tools. Editor
  binary strings decoded (SFX `.SFX` format, default player load $2000, 8
  sub-effects/entry). See `followup_csdb_findings.md`.
- ✅ **CSDb #10604** — turned out to be Future Composer V1.0, not MoN docs.
- ✅ **sidid sub-IDs decoded + variant→author map** — see disambiguation table.

Remaining items are **migration-phase work, not research** (this is why the
state is OK rather than blocked):

- **First migration step:** `tools/seed_disassembly.py` on a representative SID
  (e.g. Cybernoid II or Mantalos), then cross-reference against the matching
  `src/*.asm` to build `disassembly.s` + the extractor.
- **Watch for the Bjerregaard fork** if any of its 77 SIDs get pulled in — it's
  a different instrument byte order + sequence encoding; treat as its own engine.

Note: detection already works — no sidid config to maintain. This repo does not
run sidid live; the `engine` column comes from a cached dump
(`deprecated/gt2_grading/data/sidid_full.txt`, made with upstream cadaver/sidid),
which already tags all 135 as `MoN/Deenen`. There is no `tools/sidid.cfg`. The
`src/sidid_cfg_*.txt` files here are reference copies of the upstream signatures,
not a config our pipeline reads.

Could-not-fetch (low value, all alternatives covered elsewhere): web.archive.org
(blocked in env), exotica.org.uk (Cloudflare wall), justsolve.archiveteam.org
(site down), ZX Spectrum 128K port (no public source found).

## Note on this sweep

The fan-out spawned far more subagents than intended (a recursion: full-access
research agents re-launched their own waves, compounded by session/rate-limit
retries). Most of those produced nothing. The useful output above all came from
the first wave before the limit hit; scratch dirs were cleaned. No migration/RE
work was done — that remains for the migration phase.
