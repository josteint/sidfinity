---
source_url: local: /home/jtr/sidfinity/hvsc84.db + /home/jtr/sidfinity/hvsc85/DOCUMENTS/STIL.txt + /home/jtr/sidfinity/hvsc85/DOCUMENTS/Musicians.txt
fetched_via: local read
fetch_date: 2026-06-15
author: HVSC team
content_date: HVSC #84, December 2025
reliability: primary
---

# HVSC #84 Ariston Corpus Census

## Total corpus: 147 SIDs

(DB query: `SELECT COUNT(*) FROM sids WHERE engine='Ariston'`)

---

## Per-composer breakdown

| Composer | SID count | Total subtunes | Min song len (s) | Max song len (s) | Avg song len (s) |
|---|---|---|---|---|---|
| Steve Barrett | 21 | 76 | 78 | 356 | 195.9 |
| Wally Beben | 19 | 55 | 123 | 1542 | 412.6 |
| Mark Wilson | 19 | 79 | 21 | 669 | 247.1 |
| Ian W. Crabtree | 19 | 27 | 52 | 473 | 222.8 |
| Sandra Park (Perdita) | 10 | 10 | 82 | 225 | 134.4 |
| Neil Scales (Neil) | 10 | 11 | 24 | 147 | 78.1 |
| Wally Beben (Hagar) | 9 | 16 | 93 | 399 | 230.8 |
| Steve Barrett (The Eggman) | 6 | 14 | 77 | 385 | 200.5 |
| `<?>` (unknown) | 5 | 9 | 24 | 422 | 169.5 |
| Matt Gray | 4 | 17 | 57 | 578 | 253.5 |
| Allister Brimble | 4 | 13 | 164 | 294 | 206.8 |
| Wally Beben `<?>` | 2 | 10 | 39 | 508 | 273.5 |
| Lyndon Sharp `<?>` | 2 | 4 | 108 | 110 | 109.0 |
| Kendal | 2 | 2 | 31 | 93 | 62.0 |
| Jonathan Dunn | 2 | 4 | 156 | 307 | 231.3 |
| Denis Harris (Moley) | 2 | 2 | 93 | 185 | 139.0 |
| Barry Leitch | 2 | 11 | 120 | 620 | 369.8 |
| Paul Meredith | 1 | 2 | 132 | 132 | 132.0 |
| Lyndon Sharp | 1 | 7 | 159 | 159 | 159.0 |
| Kevin Bruce | 1 | 1 | 156 | 156 | 156.0 |
| Jukka Tapanimäki `<?>` | 1 | 1 | 276 | 276 | 276.0 |
| Ian Crabtree & Roy Fielding | 1 | 16 | 386 | 386 | 386.0 |
| Ian Crabtree | 1 | 1 | 160 | 160 | 160.0 |
| Dennis Lindroos (Deadman) | 1 | 1 | 88 | 88 | 88.0 |
| Arno Pedersen (Panther) | 1 | 1 | 144 | 144 | 144.0 |
| Andy Grimson | 1 | 1 | 230 | 230 | 230.0 |

**Notes:**
- "Ariston Design" is a C64 scene group (per Musicians.txt): Denis Harris (Moley) and Neil Scales
  (Neil) are listed as members of "Ariston Design". This is a *scene group*, not the Ariston
  software author (Ian Crabtree). The group name was inspired by the software.
- Wally Beben is listed under both "Wally Beben" and "Wally Beben (Hagar)" — same person,
  different HVSC attribution conventions for handle vs real name.
- Jukka Tapanimäki entry is tentative (`<?>` qualifier).

---

## Song length distribution

| Duration band | SID count |
|---|---|
| < 1 min | 14 |
| 1–2 min | 19 |
| 2–5 min | 82 |
| 5–10 min | 27 |
| > 10 min | 5 |

**Note:** Wally Beben/Scuba_Kidz (1542 s = 25.7 min) is the outlier driving ">10 min"; likely
a 4-subtune collection. 55.8% of the corpus is in the 2–5 min range — consistent with game
loader / background music usage.

---

## PSID header analysis

All 147 SIDs have `psid_version = 2`. No PSID v1 entries.

### Speed bits (CIA/multispeed)

Only **3 SIDs** have non-zero speed bits (speed != 0):
- `Blue_Meanies.sid` (Steve Barrett / The Eggman) — speed=0x2 (voice 2 CIA)
- `Egg_in_Space.sid` (Steve Barrett / The Eggman) — speed=0x2
- `Fraeulein_Kinski.sid` (Steve Barrett / The Eggman) — speed=0x2

All three are by the same composer (Steve Barrett, Eggman alias). 144/147 SIDs are VBI-only
(speed=0). The Ariston engine is overwhelmingly a **50Hz VBI player**.

### Play vector census

- **134 SIDs** have a non-zero play_addr (standard VBI play vector).
- **13 SIDs** have play_addr = 0 (own-IRQ / RSID-style, or embedded IRQ handler):

| SID file | Composer | init_addr | n_subtunes |
|---|---|---|---|
| Abyss_Zone_Demo.sid | Jukka Tapanimäki | 0x4060 | 1 |
| Digi_Panth_2.sid | Arno Pedersen (Panther) | 0x69c0 | 1 |
| Galdregons_Domain.sid | Mark Wilson | 0x6a70 | 1 |
| Tetris.sid | Wally Beben | 0x7440 | 1 |
| Pulsoid.sid | Steve Barrett | 0x8002 | 1 |
| Pulse_Warrior.sid | Steve Barrett | 0x8430 | 1 |
| Popped_Corn.sid | Wally Beben (Hagar) | 0x8c00 | 1 |
| Viking.sid | Wally Beben (Hagar) | 0x9c00 | 1 |
| Mark_Wilson_Demo_Disk_4_Menu.sid | Mark Wilson | 0x9f30 | 2 |
| Face_It.sid | Wally Beben (Hagar) | 0x9fa0 | 1 |
| Device_for_Alien_Destruction.sid | Mark Wilson | 0xc000 | 3 |
| Scuba_Kidz.sid | Wally Beben | 0xcd00 | 4 |
| European_5-A-Side.sid | Steve Barrett | 0xcd22 | 3 |

These include the "digi" candidate (Digi_Panth_2) and Tetris (Beben's famous phasing demo).
The play=0 group is mostly Beben + Barrett + Wilson — the composers most likely to embed custom
IRQ handlers for digi or advanced effects.

---

## Load/init address clustering

The corpus spans a wide range of load/init addresses, confirming that Ariston was
**heavily relocated** rather than living at a fixed address:

| Init address band | Primary composers | Count |
|---|---|---|
| $0800–$0FFF (low, ≤$1000) | Sandra Park, Neil Scales, Ian W. Crabtree, early Beben, Steve Barrett, Denis Harris, Kendal | ~36 |
| $1000–$1FFF | Barry Leitch, Allister Brimble, Ian W. Crabtree, Matt Gray, Steve Barrett | ~45 |
| $2000–$3FFF | Ian W. Crabtree | ~4 |
| $4000–$7FFF | Ian W. Crabtree, Matt Gray, Wally Beben, Steve Barrett | ~15 |
| $8000–$BFFF | Mark Wilson, Wally Beben/Hagar, Steve Barrett/Eggman, Wally Beben/? | ~30 |
| $C000–$FFFF | Wally Beben, Steve Barrett, Allister Brimble, Jonathan Dunn | ~17 |

**Composition patterns by composer:**
- **Ian W. Crabtree**: primarily $0800–$0FFF and $2000–$7000 range — likely his own builds where
  he controlled load address. His entries at init=$0x832, $0x856 cluster with Neil Scales/Sandra
  Park, suggesting a shared low-memory layout (possibly the Ariston Music Editor default).
- **Sandra Park (Perdita) + Neil Scales**: all at init=$0x832 or $0x856 — strongly suggests
  these were composed in the Brabbin GUI editor (fixed layout).
- **Mark Wilson**: predominantly $A000–$AFFF band (init starts at $Ax00 with play=$A000).
  His cluster of 13 SIDs with init in $A7xx–$Abxx all have play=$A000 — a consistent "Wilson
  layout" suggesting he had a standard personal build configuration.
- **Steve Barrett (Eggman alias)**: $9000–$9FFF band, all play=$9nnn.
- **Wally Beben**: scattered ($0856, $1508, $3680, $6C28, $7C6D, $8000, $A720, $CB50, $CF00,
  $F058, $F0FB, $FD18, $FF03) — huge variance. Each game was a new relocation. His entries
  span nearly the full 64KB address space.
- **Barry Leitch**: two SIDs, both at init=$1000 (play varies: $1076, $10C2) — consistent
  personal layout.
- **Allister Brimble**: $116D, $6D89, $EFF8, $FEE0 — scattered, game-specific relocation.

**Conclusion**: No single fixed load address. The engine was routinely relocated into whatever
memory region the game needed. The Brabbin GUI editor probably had a fixed default layout
(low memory ~$0800), while professional composers relocated for each game.

---

## STIL notes for Ariston-engine SIDs

Searched all Ariston-composer entries in STIL.txt. Technical notes found:

- **Beben/Summer_Olympiad**: Ian Crabtree's tunes were pulled at the 11th hour; only Beben's
  appear in the released game. Unused Crabtree tunes are in Crabby_Music_Demo_3.sid.
- **Crabtree/Total_Eclipse**: "A very close cover of his own tune" (Kraxxon Zone).
- **Crabtree/Warhawk_Music**: covers Rob Hubbard's Warhawk.
- **Crabtree/Frantic**: SFX by Roy Fielding (Toy); subtune 1 is 50% Toy, 50% Ian.
  "Sounds exactly like Technicolour_1.sid."
- **Beben/Total_Eclipse**: "Also used in sequel, Total Eclipse 2."
- **Beben/Dark_Side**: "Also used in Driller II without Beben's permission."
- **Dunn/RoboCop**: The STIL notes the *Ariston appliance company*'s European TV commercial
  ("Ariston...and on...and on and on and Ariston") used the Game Boy version of RoboCop music,
  NOT the C64 version. This is a distinct "Ariston" — the C64 music driver was presumably named
  after this slogan.
- **Barrett/Egg_in_Space**: "First composed tune in Sound Monitor" — implies Barrett later
  switched FROM Sound Monitor TO Ariston.
- **Brimble/Wild_West_Seymour**: Brimble explicitly mentions copying Rob Hubbard drum sounds
  and David Whittaker-style instruments — showing Ariston composers were adapting sounds from
  other drivers.

No STIL entries contain technical comments about the Ariston player's internals (format,
instrument encoding, multispeed, etc.).

---

## Musicians.txt findings

- "Ariston Design" is listed as a **C64 Music Group** in Musicians.txt.
- Members: Denis Harris (Moley) / Ariston Design, Neil Scales (Neil) / Ariston Design.
- Ian Crabtree is listed separately: "Crabtree, Ian W. — UNITED KINGDOM (ENGLAND)."
- Philip Brabbin does not appear in Musicians.txt (not a musician/composer, only the editor author).
- Wally Beben's entry mentions Total Eclipse used "the SID chip's unstable filter" — only one
  C64 game he worked on (per VGMPF), which is `Beben_Wally/Total_Eclipse.sid` (engine=Ariston).

---

## hv_sids.txt findings

The hv_sids.txt file is only 35 bytes in HVSC #84 (appears to be a stub/placeholder).
No Ariston-specific content found.
