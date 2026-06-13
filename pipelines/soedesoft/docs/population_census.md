# SoedeSoft / Soundmaster — HVSC Population Census

**Provenance:** Queried from `hvsc84.db` (read-only, `file:…?mode=ro`).
Date: 2026-06-13. Total HVSC #84 SoedeSoft entries: **929**.

---

## Summary

| Metric | Value |
|---|---|
| Total SIDs | 929 |
| All PSID version 2 | yes (all 929) |
| VBlank (speed=0) | expected for all — all PSID v2, 50 Hz VBI |
| Excluded | 0 |
| Single-subtune | 899 (96.8%) |
| Multi-subtune | 30 (3.2%) |
| Max subtunes | 15 (Western_Contest, Logical) |
| Songlength range | 3.0 s – 1006.7 s |
| Songlength average | 171.8 s |
| All load_addr | 0x0000 (PSID data-load convention) |

---

## Init/Play address clusters — version taxonomy

The dominant structural discriminator across the 929 tunes is the
offset between `init_addr` and `play_addr`.  Six major clusters cover
929/929 (with a small "other" tail of ~59):

| Cluster | init low byte | play offset | Count | Version hypothesis |
|---|---|---|---|---|
| Offset+6  | 0x00 | +6 | 319 | SoedeSound V1.0 (1988) — earliest |
| Offset+3  | 0x00 / 0x03 / 0x0a … | +3 | 151 | Short-dispatch (V3.x short init) |
| Offset+262 (+0x106) | 0x00 | +262 | 163 | Soundmaster V1.0 |
| Offset+0xDD | 0x29 | +221 | 99 | Soundmaster Vx (mid-series) |
| Offset+0xDF | 0x27 | +223 | 78 | Soundmaster Vx (mid-series variant) |
| Offset−41 (−0x29) | 0x29 | −41 | 60 | play at page+0x00, init at page+0x29 |
| Other | various | various | 59 | CreaMD outliers, exotic relocations |

### Dominant relocation pages

| Page | Count |
|---|---|
| $60xx | 346 |
| $20xx | 206 |
| $10xx | 126 |
| $38xx | 29 |
| $84xx | 24 |
| $40xx | 19 |
| Others | 179 |

The $6000 page (init=$6000, play=$6006) is by far the most common single
address pair: **309 tunes** (33% of the family).  $2000 / $1000 are the
next most common homes.

---

## Detailed cluster breakdown

### Cluster A: offset+6, init_lo=0x00 (319 tunes — SoedeSound V1.0 era)

All tunes: `init = PAGE+0x00`, `play = PAGE+0x06`.
Play is 6 bytes after init — the init routine is a very short preamble
(likely a `JMP ????` / `RTS` stub at the top, with the actual play
entry immediately after).

Top address pairs:
- `init=$6000 play=$6006` — 309 tunes
- `init=$1000 play=$1006` — 4
- `init=$A000 play=$A006` — 4
- `init=$E000 play=$E006` — 1

### Cluster B: offset+262 (+0x106, init_lo=0x00 — 163 tunes)

Soundmaster V1.0 layout: `init = PAGE`, `play = PAGE+0x106`.
The play routine is 262 bytes into the binary — sizeable init/setup
code before the play entry.  Play offset +0x106 matches sidid's
`(Soundmaster_V1.0)` sub-variant signature fragment.

### Cluster C: offset+3, init_lo=0x00 (151 tunes — V3.x short)

`init = PAGE+0x00`, `play = PAGE+0x03`.  Three-byte init stub
(almost certainly a `JMP abs` — $4C hi lo — which is exactly 3 bytes).
This is the "init is just a JMP" variant where the init routine
immediately jumps to the actual engine init, and play follows 3 bytes later.
Confirmed by V3.1 sidid signature starting with `A9 ?? 9D ?? ?? 4C ?? ??`
(LDA #, STA, JMP — 7 bytes, not 3; the 3-byte gap likely means play IS
at the JMP target landing).

Top address pairs:
- `init=$1000 play=$1003` — 34
- `init=$3803 play=$3806` — 29
- `init=$6000 play=$6003` — 29
- `init=$2000 play=$2003` — 11

### Cluster D: offset+0xDD (+221, init_lo=0x29 — 99 tunes)

`init = PAGE+0x29`, `play = PAGE+0x106`.  Init is not at page start
but 0x29 = 41 bytes in.  Play is still at page+0x106 (same as cluster B).
These are likely Soundmaster V1.0 tunes with a slightly different
binary layout where 41 bytes of data or player-state precede the init
entry point but the play entry remains at the canonical +0x106.

### Cluster E: offset+0xDF (+223, init_lo=0x27 — 78 tunes)

Similar to D: `init = PAGE+0x27`, `play = PAGE+0x106`.
Two-byte difference in init entry point vs cluster D.

### Cluster F: offset−0x29 (−41, init_lo=0x29, play_lo=0x00 — 60 tunes)

`play = PAGE+0x00`, `init = PAGE+0x29`.  The play address is BEFORE
init in address space.  Player loop at page start, init at page+$29.
This is the "reversed" layout: PSID play vector → page top (player
entry is at the very first byte of the engine), PSID init vector →
page+$29 (init code follows after the player prolog).

Representative tunes:
- `MUSICIANS/B/Bluez/Contact_Demo.sid`  init=$1029 play=$1000
- `MUSICIANS/D/Daw/Pravda_1_Magnifier.sid`  init=$B829 play=$B800
- Various "Daw" tunes, "Coax", "Richard Krvaric" (Richard), etc.

---

## Subtune distribution

| Subtunes | Count |
|---|---|
| 1 | 899 |
| 2 | 12 |
| 3 | 6 |
| 4 | 3 |
| 5 | 2 |
| 6 | 1 |
| 8 | 2 |
| 9 | 1 |
| 12 | 1 |
| 15 | 2 |

Most multi-subtune SIDs are from a small group of composers
(Rudolf Stember, The_Blue_Ninja, PST) suggesting those composers
built multi-song containers; the vast majority of community users
exported one tune per SID file.

---

## Notable multi-subtune SIDs

| Songs | Init | SID path | Title |
|---|---|---|---|
| 15 | $7E00 | Stember_Rudolf/Western_Contest.sid | Western Contest |
| 15 | $A38A | Stember_Rudolf/Logical.sid | Logical |
| 12 | $5F20 | Stember_Rudolf/Curse_of_RA.sid | The Curse of RA |
| 9 | $5C5A | Stember_Rudolf/Cylogic.sid | Cylogic |
| 8 | $7F00 | PST/Aidon_Apocalypse.sid | Aidon Apocalypse |
| 8 | $4E99 | The_Blue_Ninja/Plutonium.sid | Plutonium |
| 6 | $5E80 | GAMES/M-R/Newcomer.sid | Newcomer |
| 5 | $6000 | Doussis_Stello/PLIS.sid | PLIS |
| 5 | $7000 | The_Blue_Ninja/12_O_Clock.sid | 12 O'Clock |

---

## Composer attribution in HVSC

Tunes directly attributed to the Soede brothers:
- **Jeroen & Michiel Soede** (joint): 5 tunes (Ghostbusters, Battlestar Galactica, TrailMix, Simple Music, JT_Intro_Clone)
- **Jeroen Soede** (solo): ~40 tunes (in `MUSICIANS/S/SoedeSoft/Soede_Jeroen/`)
- **Michiel Soede** (solo): ~20 tunes (in `MUSICIANS/S/SoedeSoft/Soede_Michiel/`)

The other ~860 tunes are by third-party composers who used the
SoedeSoft / Soundmaster editor to create music.

---

## CreaMD outlier group

10 tunes by **CreaMD** (`MUSICIANS/C/CreaMD/`) have unusually large
init→play offsets (+2854 to +5158).  Their layout: `init = $7Cxx–$86xx`
(varying), `play = $9106` (fixed).  The fixed play address at $9106
across all members and the large init-to-play gap suggest a container
format where the Soundmaster engine is placed at a fixed location ($9106)
and a per-tune init block loads/decodes music data from a lower address
before jumping to the engine's play entry.
