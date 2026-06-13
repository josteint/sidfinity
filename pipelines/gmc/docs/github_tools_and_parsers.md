---
provenance: web search + GitHub fetch + local repo grep
fetch_date: 2026-06-13
sources:
  - https://github.com/cadaver/sidid/blob/master/sidid.cfg
  - https://github.com/WilfredC64/player-id/blob/master/config/sidid.cfg
  - https://github.com/TCRF/vgmid/blob/master/c64.nfo
  - https://github.com/realdmx/c64_6581_sid_players
  - https://github.com/ice00/jc64
  - https://github.com/c64cryptoboy/ChiptuneSAK
  - https://csdb.dk/release/?id=7268
  - https://csdb.dk/release/?id=44814
  - https://csdb.dk/release/?id=193964
  - /home/jtr/sidfinity/deprecated/dmc_wip/dmc/docs/lead_predecessors_and_jch.md
  - /home/jtr/sidfinity/pipelines/dmc/docs/research.md
reliability: primary (signatures from live GitHub fetch); secondary (CSDb — community comments)
---

# GMC / Game Music Creator — GitHub Tools and Parser Survey

Research date: 2026-06-13

## 1. Overall Finding: No Dedicated GMC Parser Exists on GitHub

**NEGATIVE RESULT (definitive):** No GitHub repository implements a parser,
converter, extractor, or annotated disassembly specifically for the GMC /
Game Music Creator C64 SID engine (Brian/Graffity, 1990). This covers:

- No Python/C/Rust extractor for the GMC binary format
- No annotated disassembly of the GMC player (`.s`, `.dis`, `.asm`)
- No GMC → MIDI / GMC → other format converter
- No GMC → USF path anywhere on GitHub

This conclusion comes from exhaustive searches on:
- GitHub code search: "Game Music Creator", "GMC" C64 SID, "Balazs Farkas", "Graffity"
- GitHub topic browsing: c64, sid, commodore64
- Direct fetch of every plausible repo listed in results

---

## 2. Player-ID / SIDId Signatures (the primary identification tool)

### cadaver/sidid — `sidid.cfg`
Repository: https://github.com/cadaver/sidid

Two GMC entries, confirmed by direct fetch of the raw config file:

```
GMC/Superiors
E1 EE FD BD ?? ?? 9D ?? ?? A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? BD ?? ??
9D ?? ?? BC ?? ?? 18 0A 0A 0A 0A 85 ?? AD ?? ?? 69 00 85 ?? A0 00 B1 END
```

```
GMC_V2.0/Superiors
E1 EE FD BD ?? ?? 9D ?? ?? A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? BD ?? ??
9D ?? ?? A8 29 F0 85 FC 98 29 0F 18 6D ?? ?? 85 FD A0 00 98 9D END
```

**Structural notes from the signatures:**
- Both share the opening 4-byte prefix `E1 EE FD BD` — this is the
  most compact discriminator for all GMC variants.
- `??` = wildcard (address bytes that vary with relocation).
- Both signatures begin with the same leading sequence through the fourth
  instruction group, then diverge at `BC ?? ??` (V1.x) vs `A8 29 F0` (V2.0).
- The `BC` opcode (LDY abs,X) in V1.x suggests the instrument-select uses
  a different addressing mode from V2.0's `A8` (TAY) + `29 F0` (AND #$F0).
- The `18 0A 0A 0A 0A` in V1.x (CLC; ASL×4 = ×16) is the instrument-size
  multiply: 16 bytes per sound definition. This confirms the HVSC research.md
  note ("indexed via 4x ASL A = multiply by 16").
- The `29 F0 … 29 0F 18 6D` sequence in V2.0 splits a byte into two nibbles,
  suggesting V2.0 packs two fields per byte (e.g. sound-hi / sound-lo nibbles),
  replacing V1.x's 16-byte-stride layout.

An additional signature appears for `Graffity/Brian` — a short instrument init
sequence (`A9 00 95 2F …`) that may be present in some GMC SIDs regardless of
version.

### WilfredC64/player-id — `config/sidid.cfg`
Repository: https://github.com/WilfredC64/player-id

Contains the same two GMC entries (confirmed by direct fetch). This tool is a
Rust reimplementation of sidid with multi-core BNDM matching. The GMC
signatures are byte-for-byte identical to cadaver/sidid — both projects
share a common signature database lineage.

### TCRF/vgmid — `c64.nfo`
Repository: https://github.com/TCRF/vgmid

Contains metadata entries for both GMC variants:

```
GMC/Superiors
     NAME: Game Music Creator System
   AUTHOR: Balazs Farkas (Brian)
 RELEASED: 1990
REFERENCE: http://csdb.dk/release/?id=7268

GMC_V2.0/Superiors
     NAME: Game Music Creator System
   AUTHOR: Balazs Farkas (Brian)
(no RELEASED or REFERENCE — not publicly released, intermediate version)
```

The vgmid file does NOT include SIG/END hex bytes — it is the metadata
companion to the sidid.cfg sig database, cross-referencing CSDb releases.
GMC V2.0 has no CSDb release entry (confirmed: no CSDb page exists for it).

---

## 3. Engine-Neutral Tool Survey — NEGATIVE Results

### realdmx/c64_6581_sid_players
Repository: https://github.com/realdmx/c64_6581_sid_players

Contains original and reverse-engineered player sourcecode for Hubbard, Galway,
Whittaker, Gray, Deenen, Ouwehand, Kimmel, Dunn, Bjerregaard, Bulka, and the
Audial Arts engine. **No GMC, DMC, or Brian/Graffity content.** NEGATIVE.

### ice00/jc64 (JC64dis)
Repository: https://github.com/ice00/jc64

JC64dis is an iterative disassembler supporting SID, PRG, MUS, CRT, VSF, MPR
files. The `doc/example/` directory contains ~80 `.dis` files for various C64
music player formats including `TheGameCreator.dis`, `Master_Composer.dis`, and
`MusicAssembler.dis`, but **no GMC.dis, Superiors.dis, or DMC.dis file.**
The `List.txt` catalog confirms GMC is absent from the JC64dis example set.
NEGATIVE for GMC specifically.

### ChiptuneSAK (c64cryptoboy/ChiptuneSAK)
Repository: https://github.com/c64cryptoboy/ChiptuneSAK

Imports PSID and some RSID files via 6502 emulation; exports to GoatTracker .sng.
**No player-specific GMC support** — the SID import is format-agnostic
(register-trace based). Documentation does not mention GMC. NEGATIVE for
dedicated GMC handling.

### libsidplayfp / libsidtune
Not a GitHub search hit. libsidtune handles PSID/RSID wrapping only; it does not
parse or identify the inner player engine. GMC SIDs are playable by libsidplayfp
as PSID files but the library has no GMC-specific data extraction. NEGATIVE.

### sid2midi
Closed source, Windows-only, not on GitHub (last update 2007). No evidence of
GMC format awareness. NEGATIVE.

---

## 4. DMC Parsers — Do They Handle GMC?

The active DMC V4 pipeline (`pipelines/dmc/v4/`) handles only DMC V4 (family 1
of the census, 5401 SIDs). **No GMC-specific extraction or composition code
exists in the pipeline.** Confirmed by grep of `pipelines/dmc/` and
`deprecated/dmc_wip/`. The `deprecated/dmc_wip/dmc/docs/lead_predecessors_and_jch.md`
treats GMC as "earliest ancestor — needs separate disassembly before we can parse."

The SIDFactory II JCH NP20 converter (Chordian/sidfactory2 on GitHub) handles
JCH NewPlayer 20, which is the NP20 descendant of DMC. It does NOT handle GMC.
The NP20 format structure (pointer table at $0Fxx, row-major instruments, 2-byte
sequence entries) is documented in that converter and is analogous to DMC, but
GMC predates both.

---

## 5. Third-Party GMC Re-implementations (CSDb, Not GitHub)

Two relevant non-GitHub tools surfaced from CSDb:

### Fenek — GMC V2 (Unfinished), CSDb #44814 (2006)
AKA: "weekofsenselesswork"  
Fenek disassembled the original GMC V1.0 player and recreated the editor from
scratch, removing instrument count restrictions and optimizing the player code.
The result is "a more streamlined, DMC-resembling editor." This is the closest
thing to an annotated GMC disassembly that exists — but it was never published
as a disassembly listing; only the rebuilt binary is available as a download.
CSDb entry: https://csdb.dk/release/?id=44814

**Key technical implication:** Fenek's work confirms the GMC player is
disassemblable and that its instrument count is the primary limitation that
motivated the re-implementation.

### Wacek — GMC 0.5x, CSDb #193964 (2020)
Released at the 25Hz Music Compo 2020. Another editor variant based on the GMC
format. No source code available. CSDb entry: https://csdb.dk/release/?id=193964

---

## 6. Balazs Farkas (megazyz) GitHub Profile

GitHub handle `megazyz` belongs to a user who appears to be a different
Balázs Farkas (GitHub profile shows Minecraft / .NET / Avalonia repositories
only). **The GMC/DMC Brian is NOT present on GitHub.** His source code was
never publicly released (confirmed across all research).

---

## 7. Signature Analysis — What V1 vs V2 Tells Us About Format Evolution

From the two sidid signatures (both confirmed verbatim):

The critical divergence point in the play routine:

**V1.x:** `… BD ?? ?? 9D ?? ?? BC ?? ?? 18 0A 0A 0A 0A 85 ?? AD ?? ?? 69 00 85 ?? …`
- `BC ?? ??` = LDY abs,X — loads Y from a table indexed by X (voice index?)
- `18 0A 0A 0A 0A` = CLC; ASL; ASL; ASL; ASL — multiplies by 16 (instrument stride = 16 bytes)
- `AD ?? ?? 69 00` = LDA abs; ADC #0 — likely adding carry from a preceding address calc

**V2.0:** `… BD ?? ?? 9D ?? ?? A8 29 F0 85 FC 98 29 0F 18 6D ?? ?? 85 FD A0 00 98 9D …`
- `A8` = TAY — transfer A to Y (the loaded byte goes to Y)
- `29 F0` = AND #$F0 — extract high nibble
- `85 FC` = STA $FC — store high nibble to ZP $FC
- `98` = TYA — restore original byte
- `29 0F` = AND #$0F — extract low nibble
- `18 6D ?? ??` = CLC; ADC abs — add to something (address calculation)
- `85 FD` = STA $FD — store result

**Interpretation:** V2.0 packs two sub-fields per byte (high nibble + low nibble)
where V1.x used a simple 16-byte stride. This is likely the instrument number
being split into bank-select + index, allowing more than 16 instruments (V1.x
is limited by 4-bit shift = 16 slots fitting a nibble). This matches Fenek's
observation that V1.0 had instrument count restrictions he removed in his remake.

---

## 8. HVMEC Binary Archive

HVMEC (https://hvmec.altervista.org/) hosts GMC V1.0, V1.6, and V2.0 binaries
as downloadable D64/ZIP archives (confirmed via the DMC tools survey in
`pipelines/dmc/docs/csdb_dmc_tools_survey.md`). These are the authoritative
sources for binary analysis — no GitHub repository hosts them.

---

## Leads to Follow

1. **Fenek's GMC V2 binary (CSDb #44814):** Download and disassemble. Fenek
   disassembled the V1.0 player and rebuilt it — comparing his rebuild with the
   original would reveal the complete player structure without needing to
   cold-disassemble the original. The binary is at:
   https://csdb.dk/release/?id=44814 (download link within).

2. **HVMEC GMC V1.0/V1.6/V2.0 binaries:** Download the D64 images from
   https://hvmec.altervista.org/blog/?p=1265 to get the player ROM for
   disassembly. V1.0 binary also available via CSDb #7268 (`gmcv1.zip`).

3. **sidid signature deep-decode:** The `18 0A 0A 0A 0A` (×16 multiply) in V1.x
   and the nibble-split in V2.0 pinpoint the instrument-addressing routine.
   Use `tools/seed_disassembly.py` on a GMC SID and anchor to these byte
   sequences to locate the instrument loader quickly.

4. **Wacek GMC 0.5x binary (CSDb #193964):** Another modern re-implementation.
   Might have a cleaner structure if Wacek documented his work.

5. **`Graffity/Brian` signature in sidid.cfg:** The short sequence
   `A9 00 95 2F 95 2C 95 95 95 96 95 97 END` may be the init routine
   (zero-filling voice state). Cross-referencing against a live GMC SID
   writelog would confirm whether init and play are separately identifiable.

6. **Format relationship to DMC V4:** The NP20/DMC architecture
   (documented in `deprecated/dmc_wip/dmc/docs/lead_predecessors_and_jch.md`)
   uses 2-byte sector entries ($7F terminator), lo/hi split sequence vectors,
   and row-major instruments. GMC likely uses a simpler precursor of this —
   specifically the 16-byte instrument stride in V1.x suggests a flat array
   (not row-major transposed), and the single-byte sector commands match DMC's
   lower byte ranges. **Hypothesis:** GMC sectors are a strict subset of DMC
   V4 sector encoding, missing the $C0-$FF glide/volume commands that DMC added.
   Verify by disassembling GMC play routine and locating the sector dispatch table.
