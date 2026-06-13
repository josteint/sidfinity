# HardTrack Composer — DeepSID, population & version/relocation taxonomy

**Provenance**
- Author: SIDfinity research session (sidid/DeepSID/taxonomy cluster), 2026-06-13.
- Population figures: `hvsc84.db` opened READ-ONLY (`file:hvsc84.db?mode=ro`, uri=True).
- PSID speed-flag figures: computed by reading the 1170 SID file headers in place
  (offset $12, 4-byte speed mask) — read-only, no files modified.
- Web sources: CSDb release pages, cadaver/sidid.nfo (see inline links).
- Companion doc: `sidid_signature_analysis.md` (signature decode + V1.0/V1.1 diff).

---

## 1. DeepSID / player-name string

- DeepSID identifies players via **sidid** (cadaver's signature engine); its displayed
  player label is the sidid id with underscores rendered as spaces. For this engine that
  is **`HardTrack Composer`** (sidid id `HardTrack_Composer`).
- cadaver `sidid.nfo` entry (authoritative provenance for the signature):
  > `HardTrack_Composer`  — AUTHOR: Milosz Ignatowski (Longhair) —
  > REFERENCE: https://csdb.dk/release/?id=74928
- The DeepSID public web UI does not surface the per-tune player string in fetchable HTML
  (it is rendered client-side from the bundled sidid table — the same single-signature
  table inspected locally at `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg` line 808).
  There is no DeepSID-specific version tag; DeepSID shows one flat `HardTrack Composer`
  label for all 1170 tunes (no V1.0/V1.1 split), because the single signature cannot
  distinguish versions.

## 2. CSDb release taxonomy (web)

The SDK artifacts use internal version names **V1.0** and **V1.1**; CSDb names the public
releases **V1.0** and **V1.0+** (with multispeed sub-variants). These line up:

| SDK name | CSDb name | CSDb id(s) | Notes |
|---|---|---|---|
| V1.0 | Hardtrack Composer V1.0 | 74928 (Elysium, 1992, original tool) | code Brush + Longhair; music The Syndrom "Frozen Energy"; gfx Cruise |
| V1.1 | Hardtrack Composer V1.0+ | 36647 (BHG, 2000, "[6 speed]"), 237295 ("[4 speed]"), 82834 (Fatum crack, 1994) | the "+" adds CIA multispeed (4×/6×) |

i.e. **internal "V1.1" == CSDb "V1.0+"** — the plus is the multispeed upgrade. Numerous
cracks exist (Axelerate 1998, Chromance 1995, Alpha Flight 1995) but they are the same two
code bases. Sources:
- https://csdb.dk/release/?id=74928 (V1.0)
- https://csdb.dk/release/?id=36647 (V1.0+ [6 speed])
- https://github.com/cadaver/sidid (sidid.nfo provenance)

## 3. HVSC population (hvsc84.db, engine='HardTrack_Composer')

- **Total: 1170 SIDs.**
- PSID format version: **1167× PSIDv2**, **3× PSIDv3**. No RSID.

### Subtune distribution

| n_subtunes | count |
|---|---|
| 1 | 1145 |
| 2 | 5 |
| 3 | 3 |
| 4 | 3 |
| 5 | 6 |
| 6 | 2 |
| 7 | 1 |
| 8 | 4 |
| 11 | 1 |

97.9% are single-subtune. The multi-subtune tail (25 files) tops out at one 11-subtune SID.

### Init / play address spread (relocation taxonomy)

`load_addr` is `$0000` for all 1170 (PSID with load address embedded in the data stream;
the real anchor is `init_addr`). `play_addr` is consistently `init_addr + 3` — confirming
the `JMP init / JMP play` header table (3 bytes each) the player uses.

| init_addr | count | play_addr |
|---|---|---|
| $1000 | 1035 | $1003 (1055 total at $x003) |
| $6000 | 34 | $6003 |
| $E000 | 21 | $E003 |
| $0F00 | 8 | $0F03 |
| $A000 | 4 | $A003 |
| $2000 | 3 | $2003 |
| $7FDC | 2 | $7FEC |
| $6800 | 2 | $6803 |
| $4000 | 2 | $4003 |
| $2400 | 2 | $2403 |
| $EFC0, $EF00, $BA00, $B540, $B093, ... | 1 each | (long tail) |

So **~88% load at the canonical $1000**; the rest are relocations to $6000 (34), $E000
(21), $0F00 (8), $A000 (4), and a scatter of one-off addresses (demo-embed / packer
relocations). The $E000/$B0xx/$BA00/$EFxx tail are high-memory embeds (under-ROM /
under-I/O) — those are the C64-banking cases to watch when relocating
(cf. memory `feedback_c64_banking_relocation`).

### CIA / multispeed (PSID speed bit)

| PSID speed mask | count |
|---|---|
| `0` (all subtunes flagged VBI) | 1165 |
| non-zero (≥1 subtune flagged CIA in header) | 5 |

**Critical taxonomy finding:** only **5/1170** SIDs declare CIA via the PSID speed flag.
The HardTrack multispeed (the "V1.0+" 4×/6× feature) is **engine-internal** — the player
programs CIA Timer A itself and the PSID header still declares VBI (speed bit 0). So the
PSID speed bit is NOT a reliable multispeed detector for this family; multispeed must be
detected from the player's own CIA setup, and the verifier should treat these like the
CIA-tune case (capture per-IRQ via `siddump --writelog-per-irq`, cf. CLAUDE.md "CIA-timed
tunes"). Do NOT assume speed-bit==0 means single-speed for HardTrack.

## 4. Version split in HVSC — how to tag V1.0 vs V1.1

The single sidid signature matches all 1170 and cannot split versions (see
`sidid_signature_analysis.md` §4). Cheapest reliable discriminator found:

- **$D417 software-shadow address inside the signature region:**
  V1.0 → `AD 1F 10` (shadow $101F); V1.1/V1.0+ → `AD 1E 10` (shadow $101E).
  (Relocated SIDs shift the high byte $10→load page, but the low byte $1F vs $1E and the
  routine offset $1362 vs $1387 remain the tell.)
- Embedded `PLAYER V1.x` string: present in only **4/1170** SIDs (3× V1.0, 1× V1.1) —
  most tools strip it, so it is not a general tagger.

A full V1.0/V1.1 census across all 1170 was not run this session (the shadow-address probe
needs per-SID relocation handling); it is the top lead below.

## Leads to follow

- Run the $101F-vs-$101E shadow probe across all 1170 HVSC SIDs (relocation-aware: locate
  the signature, read the `AD ?? 10`-equivalent operand) to produce the actual V1.0 vs
  V1.0+ population split — the single most useful taxonomy number still missing.
- Identify the 5 PSID-speed-flagged SIDs and the engine-internal-CIA multispeed SIDs
  separately; confirm whether the V1.0+ players that set CIA Timer A keep the PSID speed
  bit 0 (expected). This decides whether the verifier uses the flat or per-IRQ capture.
- The 135 relocated SIDs (init ≠ $1000) include high-memory embeds ($E000/$B0xx/$BA00/
  $EFxx) — audit those for `sta $01` banking flips before any relocation in the composer.
- Pick a canonical representative per version for migration: V1.0 = a $1000 Bzyk tune
  (e.g. `Good_World.sid`); V1.1/V1.0+ = `Shogoon/Tribute_to_Laxity.sid` ($1000, V1.1).
- Cross-check DeepSID's live display label once (the public HTML doesn't expose it) to
  confirm casing is exactly `HardTrack Composer`.
