# Master Composer — sidid / player-id signatures

> **Provenance**
> - source_url: https://github.com/WilfredC64/player-id (sidid.cfg + Signature_File_Format.txt), https://github.com/cadaver/sidid (upstream sidid.nfo); `local: tmp/dmc_hunt/player-id/config/sidid.cfg` (the in-repo copy actually queried)
> - fetched_via: local grep of the in-repo player-id `sidid.cfg`/`sidid.nfo`; WebFetch of the player-id README + `doc/Signature_File_Format.txt` (for the convention) and cadaver `sidid.nfo`
> - fetch_date: 2026-06-13
> - author: signatures by the WilfredC64/player-id + cadaver/sidid maintainers; this digest by the SIDfinity research pass
> - content_date: 2026-06 snapshot of the signature DBs; engine 1983
> - reliability: PRIMARY for the signature bytes + format convention (quoted from the spec); the engine↔signature mapping is re-derived from the §-disasm and is high-confidence.

## 1. The `Master_Composer` signature (WilfredC64/player-id)

From `player-id/config/sidid.cfg` (lines 1257–1260):

```
Master_Composer
F0 ?? C9 64 D0 0E ?? ?? ?? ?? ?? ?? 29 FE 8D 0B D4 4C ?? ?? A8
(Patrick_Payne)
29 FE 8D 04 D4 4C ?? ?? A8 B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4 AE ?? ?? BD ?? ?? 29 FE 8D 04 D4 09 01 8D 04 D4
```

(`??` = a single wildcard byte — used here for the relocatable absolute operands, since the player is relocatable.)

### What the parent signature matches (grounded to the disasm)

It anchors on **voice 2's note routine** (`outNoteV2`/`releaseV2`, $7762–$7779 at canonical load $7580):

| sig bytes | disasm | meaning |
|---|---|---|
| `F0 ??` | `BEQ +25` | bar byte `$00` → rest/hold, skip voice |
| `C9 64 D0 0E` | `CMP #$64 / BNE +14` | bar byte `$64` → gate-release branch (the sentinel) |
| `?? ?? ?? ?? ?? ??` | (freq lo/hi store via reloc operands) | (skipped: relocatable) |
| `29 FE 8D 0B D4` | `AND #$FE / STA $D40B` | V2 gate-off keeping waveform (releaseV2) |
| `4C ?? ?? A8` | `JMP …` / `TAY` | branch + note→Y for the freq-table index |

So the family fingerprint = "the `$64` gate-release test + `AND #$FE / STA $D40B` voice-2 gate-off + note-indexed freq table". This is reloc-invariant (the `??`s absorb the moved addresses), which is exactly why one signature covers all ~1,019 family members regardless of relocation.

### The `(Patrick_Payne)` sub-signature

**`(Patrick_Payne)` is a *sub-signature of* `Master_Composer`, NOT a separate engine.** Per the player-id spec (`Signature_File_Format.txt`, quoted verbatim):

> "You can also specify sub signatures when e.g. a certain player is covered by a signature, and you want to cover a certain version of it or additional routine with another signature. The convention for specifying sub signatures is to put the player name between brackets."

So a name in parentheses = a **more specific variant / additional routine** of the player immediately above it. The `(Patrick_Payne)` bytes match **voice 1's note + retrigger routine** (`outNoteV1` + `outCtrlV1`, $772C–$7841):

| sig bytes | disasm | meaning |
|---|---|---|
| `29 FE 8D 04 D4` | `AND #$FE / STA $D404` | V1 gate-off (releaseV1) |
| `4C ?? ?? A8` | `JMP …` / `TAY` | branch + note→Y |
| `B9 ?? ?? 8D 00 D4` | `LDA $7881,y / STA $D400` | V1 freq lo from freq table |
| `B9 ?? ?? 8D 01 D4` | `LDA $78E0,y / STA $D401` | V1 freq hi from freq table |
| `AE ?? ?? BD ?? ??` | `LDX $7941 / LDA $7990,x` | load block control byte |
| `29 FE 8D 04 D4` | `AND #$FE / STA $D404` | gate off |
| `09 01 8D 04 D4` | `ORA #$01 / STA $D404` | gate on → **retrigger** (outCtrlV1) |

This is the same player code, just a longer/more-specific stretch anchored on voice 1. **Patrick Payne** is a composer (CSDb musician) who used the Master Composer editor; player-id reports `Master_Composer (Patrick_Payne)` to attribute those tunes. For SIDfinity purposes treat both as the **single Master Composer engine** — there is no format/engine fork implied. (The HVSC `sidid` engine label may surface either string; the migration target is one engine.)

## 2. The `Master_Composer` entry (cadaver/sidid — upstream)

cadaver's upstream `sidid.nfo`:

```
Master Composer
NAME:     Master Composer
AUTHOR:   Paul Kleimeyer
RELEASED: 1983 Access Software Inc.
REFERENCE: https://csdb.dk/release/?id=128699
```

Upstream cadaver/sidid does **not** carry the `(Patrick_Payne)` sub-signature — that is a WilfredC64/player-id addition. Both DBs agree on author/publisher/year.

## 3. `TFMX/MasterComposer` is a SEPARATE engine (name collision)

`player-id/config/sidid.cfg` (lines 1990–1991) and cadaver's `sidid.nfo`:

```
TFMX/MasterComposer
F0 26 B1 06 48 4A 4A 4A 4A 9D
AUTHOR:   Playboy & Sir Tippitt
RELEASED: 1990 Bierfront
COMMENT:  Editor that is based on the player of
          /MUSICIANS/H/Huelsbeck_Chris/Starball.sid
```

This is **unrelated** to Kleimeyer's Master Composer:
- Different author/year (Playboy & Sir Tippitt, 1990) and a different lineage entirely — it is a TFMX-family editor derived from **Chris Hülsbeck's Starball player**, not from Access Software's editor.
- Different code: `B1 06` (indirect load via ZP $06), `4A 4A 4A 4A` (LSR ×4 = high-nibble extract), `9D` (STA abs,X) — none of which appears in the Kleimeyer player (which has no nibble-packing and reads notes via `(zp),Y` from 64-byte voice rows).
- The shared word "MasterComposer" is a naming coincidence; sidid namespaces it under `TFMX/`. **Do not conflate.** The Kleimeyer engine is `Master_Composer` (no slash); the TFMX one is `TFMX/MasterComposer`.

## 4. Format-convention reference (player-id sidid.cfg)

Quoted from `Signature_File_Format.txt`:
- Player name line: "A signature starts with a name that can be a player/editor name or if that is not known, it is common to put the author's name."
- Sub-signature (parens): see §1 quote above.
- `??` = single wildcard byte (unknown/relocatable).
- `AND` / `&&` = skip-gap token: "you can skip multiple bytes until the next occurrence is found" (i.e. match two byte-groups separated by a variable-length run). The Master Composer signatures use only `??`, no `AND`.

## Sources
- WilfredC64/player-id — https://github.com/WilfredC64/player-id (sidid.cfg, README, doc/Signature_File_Format.txt)
- cadaver/sidid — https://github.com/cadaver/sidid/blob/master/sidid.nfo
- CSDb Master Composer release — https://csdb.dk/release/?id=128699
- Local copies queried: `tmp/dmc_hunt/player-id/config/sidid.cfg` + `sidid.nfo` (read-only)
