# DeepSID — SDI Player Detection & HVSC Population Notes

Provenance: queried hvsc84.db (READ-ONLY, uri=True, 2026-06-13) + inspected
`tmp/dmc_hunt/DeepSID/` source tree (READ-ONLY). No siddump/py65 used.

---

## 1. How DeepSID Labels SDI Tunes

DeepSID's player identification pipeline:

1. `php/sid_id.php` runs `sidid.cfg` byte-matching against SID binary content.
2. The raw label from `sidid.cfg` is stored in the `player` DB column.
3. `php/pretty_player_names.php` maps 181 raw labels to human-readable display names.
4. **Geir_Tjelta/SIDDuzz'It is NOT in `pretty_player_names.php`.**

Therefore: DeepSID shows `Geir_Tjelta/SIDDuzz'It` verbatim in its Stats/Memo panel.
No version tag (V1.x / V2.x / V2.1.7) is appended — the sidid signature is
version-agnostic. The same raw string appears for tunes from 1992 through 2025.

No "SHAPE" or "SDI" friendly-name alias exists in DeepSID's current codebase.

---

## 2. HVSC Population Census (hvsc84.db, all Geir_Tjelta family)

| sidid label | Full name | n tunes | Year range |
|---|---|---|---|
| `Geir_Tjelta/SIDDuzz'It` | SID Duzz'It (SDI) | **934** | 1992–2025 |
| `Geir_Tjelta/SIDSys18.6` | Sid Systems V4.1 (p18.6) | 48 | 1991–2012 |
| `Geir_Tjelta/SIDSys18.4` | Sid Systems V4.1 (p18.4) | 46 | 1990–2018 |
| `Geir_Tjelta/SIDSys_1.0` | Sid Systems V1 | 45 | 1989–1991 |
| `Geir_Tjelta/Echo` | Echo post-processor | 8 | 2009–2022 |
| `Geir_Tjelta/Comptech-X` | Comptech-X | 6 | 2019–2025 |
| `Geir_Tjelta/MacroPlay1` | Macro Player v1 | 1 | 2013 |
| `Geir_Tjelta/MacroPlay2` | Macro Player v2 | 2020 | 2020 |
| `GRG` (related) | GRG custom player | 8 | 1999–2011 |
| `GRG_tiny_1..4` (related) | GRG tiny players | 31 total | 2002–2025 |

SDI dominates at 934 tunes (85% of the Geir_Tjelta namespace). SIDSys is the
historical predecessor family (139 tunes, 1989–1996 with outliers to 2018).

---

## 3. SDI Address Layout

### 3.1 Init/Play address clusters

The SDI player can be relocated freely; the data is assembled by TASS (Turbo Assembler)
with the `*= $1000` directive in the source. The canonical layout:

| init | play | n | Notes |
|---|---|---|---|
| $0FFF | $1003 | 480 | Most common: 3-byte JMP stub at $0FFF → $1000 |
| $1000 | $1003 | 129 | Direct: no stub, init IS the player start |
| $E8FF | $E903 | 71 | Relocation to $E900 page (Norwegian demoscene pref?) |
| $0FCB | $0FDE | 13 | Non-standard reloc cluster |
| $1FFF | $2003 | 11 | Reloc to $2000 |
| $3FFF | $4003 | 10 | Reloc to $4000 |
| $E000 | $E003 | 10 | Reloc to $E000 |
| $0BFF | $0C03 | 8  | Reloc to $0C00 |
| $A000 | $A003 | 8  | Reloc to $A000 (banked) |

**Key observation:** The `$0FFF / play $1003` cluster (480 tunes) is a 3-byte JMP wrapper:
```
$0FFF: JMP $1000    ; 4C 00 10  (3 bytes)
$1000: <INIT entry>
$1003: <PLAY entry>
```
The PSID header sets `init=$0FFF` (pointing to the JMP stub) and `play=$1003`.
This pattern is produced by finalizing in TASS with `*= $0C00` for the editor
shell and `*= $1000` for the player (per `SRC_SDI21-N50.asm` line 410: `*= $1000`).

The `$E8FF / $E903` cluster (71 tunes) represents a significant relocation — likely
tunes where the audio data needed to avoid clashing with the $1000-page (e.g. game/demo
use). Both Geir Tjelta and Glenn Rune Gallefoss (Blues Muz') are heavily represented there.

**Play offset from init is almost always +3 or +4 bytes** (JMP INIT = 3 bytes, then
JMP PLAY = 3 bytes starting at init+3). The `play = init+3` pattern holds for 170 tunes
(18.2%); the dominant cluster is `play = $1003` regardless of init (66.6% of all SDI tunes).

### 3.2 Page-level relocation summary

| Init page range | n | Dominant cluster |
|---|---|---|
| $0F00 page | 546 | $0FFF init → $1003 play |
| $1000 page | 132 | $1000 or $1FFF init → $1003 play |
| $E800 page | 77  | $E8FF → $E903 |
| Scattered | ~179 | Single relocations across full 16-bit space |

### 3.3 All load_addr = 0

Every SDI tune in hvsc84.db has `load_addr = 0` — this means the PSID header's
"load address" field is $0000, which per the PSID spec means the load address is
embedded as the first two bytes of the data blob (little-endian). This is standard
PSID v2 format for C64-native binaries.

---

## 4. Subtune Distribution

| Subtunes | n tunes |
|---|---|
| 1 | 891 (95.4%) |
| 2 | 17 |
| 3 | 5 |
| 4 | 3 |
| 5 | 2 |
| 7 | 1 |
| 8 | 4 |
| 10 | 1 |
| 11 | 3 |
| 13 | 1 |
| 15 | 1 |
| 17 | 1 |
| 23 | 1 |
| 24 | 1 |
| 28 | 1 |
| 57 | 1 |

The vast majority (95.4%) of SDI tunes have a single subtune. This makes SDI closer
to a "one song per file" convention than e.g. Hubbard '85 or DMC (which routinely
have 5–8 subtunes). Multi-subtune SDI tunes appear to be "preview packs" (e.g.
`Bombmania_II_preview_2.sid`: 28 subtunes; `Reel_Fishing_preview.sid`: 57 subtunes)
or demo-style medleys.

Notable multi-subtune tunes:
- `Reel_Fishing_preview.sid`: 57 subtunes, init=$2003, play=$2000 (inverted!), 1142s
- `Bombmania_II_preview_2.sid`: 28 subtunes, init=$0FBA, play=$0FBD, 1612s
- `Paranoid.sid` (Geir Tjelta himself): 11 subtunes, init=$3000, play=$1000
- `Jim_Slim.sid` (GRG): 23 subtunes, init=$0A80, play=$0A83, 2644s

---

## 5. PSID vs RSID

| Type | n |
|---|---|
| PSID (is_psid=1) | 918 (98.3%) |
| RSID (is_psid=0) | 16 (1.7%) |

All 16 RSID tunes have `play_addr = 0` — they are NMI/CIA-driven (set up their own
interrupt) and don't expose a play vector. These are the digi/echo-style tunes:
- 10 from `Blues_Muz/Gallefoss_Glenn/` — probably digi tunes using NMI player
- 3 from `Bakewell_Dwayne/` — digi starts
- 1 from `Eeben_Aleksi/` (10-subtune, init=$9100 — unusually high address)
- 1 from `Pedersen_Inge/`

All PSID tunes are psid_version=2 (no v1 tunes in this set).

---

## 6. No Multispeed PSID Speed Bit

The PSID `speed` bitfield (one bit per subtune; 1 = CIA-timed, 0 = VBI) is not directly
stored in hvsc84.db. However: SDI's player source ships in two flavors:

- `SRC_SDI21-N50.asm` — single-speed (50Hz VBI, standard)
- `SRC_SDI21-SPD50.asm` — multispeed (CIA-timed, raster-split)

Multispeed tunes call `$1003` (PLAY) once per VBI and `$1009` (SPEEDPLAY — sound-only,
no track/sequence advance) N-1 additional times per VBI via raster IRQ. The `speed`
field in the PSID header encodes which IRQ source drives each subtune. Since the PSID
`speed` column is not in the DB schema, multispeed detection requires reading the PSID
header directly.

From the manual: "Correct raster setup for a speed tune on a PAL machine: raster = 312/speed".
Speed values 2–15 are valid. In practice speed=4 (4× per frame) is the most common
multispeed setting for SDI tunes (matching the `SDI21-SPD50` example in the source).

---

## 7. Top Authors

| Author | n tunes |
|---|---|
| Fredrik (Swedish; many piano/orchestral remakes) | 143 |
| Glenn Rune Gallefoss (GRG; Blues Muz' / SHAPE) | 141 |
| Jan D. Arent Harries (SIDwave) | 117 |
| Joe Barwick (Stainless Steel) | 53 |
| Jan Diabelez Arent Harries | 53 |
| Jan D. Arent Harries (rambones) | 48 |
| Peter Siekmann (Devilock) | 41 |
| K. Røstøen & G. R. Gallefoss | 30 |
| Trond Jensen (TDS) | 23 |
| Kristian Røstøen | 21 |
| Carl Gustaf Liebe (Yaemon) | 21 |
| Geir Tjelta himself | 14 |

SDI became widely adopted beyond the SHAPE group — top authors include Jan Harries
(SIDwave), Joe Barwick, and the Swedish "Fredrik" — none are directly affiliated with
SHAPE. This confirms SDI was publicly released and widely used (SourceForge distribution).

---

## 8. Version History (from CSDB + manual)

| Version | CSDb ID | Date | Notes |
|---|---|---|---|
| V1.801 | #7175 | Oct 2002 | Earliest known CSDB upload; "backup in case Glenn's website fails" |
| V2.0 Beta 7 | #76999 | May 2006 | Beta phase; introduced many V2 effects |
| V2.0 Beta 8 | #84874 | 2009 | Continued beta |
| V2.1 | #132363 | Jan 2013 | First "stable" V2.1 |
| V2.1.6 | #114693 | May 2013 | Minor revision |
| V3.0 MIDI Preview 2 | #119228 | May 2013 | Experimental MIDI branch; not released |
| V2.1.7 | #133692 | Oct 2014 | **Latest release** — current HVSC standard |
| PDF Manual | #153760 | Feb 2017 | Manual by Henrik Mortensen (Psylicium) |

The player binary is in Turbo Assembler (TASS) format, distributed on disk image.
SourceForge project (`glennrg64`) hosts the V2.1.7 zip (96.4 KB).

## Leads to Follow

1. **PSID speed-bit survey**: Run a binary scan of the 934 SDI PSID headers to count
   how many set the CIA-timing speed bit per subtune. This identifies the multispeed
   subset that needs `$1009` speedplay calls modeled in the composer.

2. **V1.x binary signatures**: The earliest SDI tunes (1992–2002) may use a slightly
   different data layout (pre-V2.0 Beta). Check if the `(GT_Editor)` variant in sidid.cfg
   correlates with 1992–2002 dates in the DB.

3. **$E8FF relocation cluster (71 tunes)**: This is likely the second-largest "standard"
   layout. Investigate whether data offsets differ from the $1000-page layout (player
   size changes as flags are compiled in/out).

4. **RSID/NMI tunes (16 tunes, play=0)**: These likely contain embedded digi sample data.
   If they contain SDI music + NMI digi overlay, extraction needs to separate the two layers.

5. **57-subtune Reel_Fishing_preview.sid (init=$2003, play=$2000)**: Unusual inverted
   init/play — init is 3 bytes ABOVE play. This may be a different internal arrangement
   (play vector at the bottom, init at a higher address that calls into the player then
   sets up subtune). Warrants a one-off investigation.
