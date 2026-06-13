# HardTrack Composer — elysium.filety.pl mirror contents + decoded read-me

```
source_url:   http://elysium.filety.pl/  (FTP mirror of ftp.elysium.pl, "GamesArchive")
              + canonical SDK at http://elysium.filety.pl/gnu-generation/Brush/hardtrack_sdk.zip
local:        tmp/hardtrack/elysium_filelist.txt   (mirror listing, built 2019-03-03, READ-ONLY)
              tmp/hardtrack/OUT_PRZECZYTAJ_MNIE.prg (decoded read-me, READ-ONLY)
              tmp/hardtrack/*.d64                    (disk images, READ-ONLY)
              pipelines/hardtrack/docs/_artifacts/sdk/extracted/  (already-extracted SDK binaries)
fetched_via:  local read of pre-fetched artifacts + Wayback CDX API cross-check
fetch_date:   2026-06-13
author:       site maintained by CenTraX/Agony Design; HardTrack content by Brush + Longhair/Elysium
content_date: files dated 1991-12 .. 2010-08; mirror listing 2019-03-03
reliability:  HIGH — primary artifacts (the authors' own SDK + the editor's own embedded read-me)
```

## 1. Every HardTrack-related file on the elysium.filety.pl mirror

Grep of the 20,296-line mirror listing (`grep -ai hardtrack`). The mirror only ever held
the items below — there is **no separate `.nfo`/`.txt`/`.doc`** for HardTrack on the site;
all documentation lives *inside* the disk images (decoded below).

| # in list | mirror date | size (B) | path | what it is |
|---|---|---|---|---|
| 5843 | 2008-03-07 | 78998 | `./gnu-generation/Brush/hardtrack_sdk.zip` | **Canonical SDK** under Brush's own GNU-Generation source folder. |
| 6391 | 2008-03-09 | 78998 | `./groups/Elysium/Sources/hardtrack_sdk.zip` | Same SDK, mirrored under the Elysium group's Sources. |
| 6397 | 2008-03-09 | 30771 | `./groups/Elysium/misc/hardtrack_cracks.zip` | **NOT yet fetched** — a collection of game cracks that use HardTrack music (deployment provenance, not the engine). |
| 10618 | 2010-08-09 | 78998 | `./party/North_6/hardtrack_sdk.zip` | Same SDK, re-released at North Party 6 (2010). |
| 17075 | 2010-08-08 | 11748 | `./tools/music/Hardtrack.Composer.v1.6speed.BHG.zip` | The "6 speed" variant by Beverly Hills Group (= `tmp/hardtrack/...6speed...`). |
| 17076 | 2010-08-08 | 55230 | `./tools/music/Hardtrack_Composer_1_0_Timsoft_1994.zip` | V1.0 full disk, Tim Soft 1994 distribution (= `tmp/hardtrack/Hardtrack_Composer_1_0_Timsoft_1994.d64`). |
| 17077 | 2010-08-08 | 11641 | `./tools/music/Hardtrack_Tape.zip` | Tape (single-load) version (= `tmp/hardtrack/Hardtrack_Tape.d64`). |

### Cross-reference: same folder always ships the cross-dev toolchain
`hardtrack_sdk.zip` always travels next to `illmatic-1.0.tar.gz` (a separate Brush cross-dev
toolchain) in the Brush / Elysium-Sources / North_6 folders — not part of HardTrack itself.

### Possibly-relevant non-HardTrack docs in the same neighbourhood (NOT fetched)
- `./groups/Elysium/misc/C64_music_pl_v01.txt.zip` / `.doc.zip` — a Polish "C64 music" document that may mention HardTrack among other editors. Worth a look if a broader format survey is wanted.

### What is NOT on the mirror
- No `.nfo`, `.readme`, `.txt`, `.diz` or manual file for HardTrack.
- No V1.1 disk image (V1.1 exists only as the player binary inside the SDK — see §3).
- No V2.0 (a forum poster once referred to "v2.0"; unverified, see `archive_authors_versions.md`).

Wayback CDX confirms the SDK zip was archived at
`http://elysium.filety.pl/gnu-generation/Brush/hardtrack_sdk.zip` (capture 2024-03-09,
digest `JGU6EXZWX4T3IUOZWJ6TDOG2UGGUSWN6`, 79858 B). The site root has snapshots from
2007-09 through 2012-09 (1–4 KB index pages).

## 2. Disk-image directory listings (the actual on-disk docs)

Decoded with `tmp/hardtrack/d64.py`. The Timsoft V1.0 disk is the only one with separate
files; the 6speed and Tape disks are single packed one-file releases.

### `Hardtrack_Composer_1_0_Timsoft_1994.d64` — disk name `(C) TIM SOFT`
```
  7 blk PRG  HARDTRACK         <- BASIC loader; embeds fastloader stamp "K.M.91-12-12"
 88 blk PRG  MAIN              <- the editor itself (crunched)
 12 blk PRG  HDT PLAYER        <- standalone player
  9 blk PRG  HDT DEPACKER      <- in-memory depacker (turns editor data into a playable tune)
  9 blk PRG  HDT RELOCATOR     <- relocates a packed tune to a new address
 15 blk PRG  P.INTRO ZAK       \
 17 blk PRG  P.EXPERIM.BASS     |
 20 blk PRG  P.NEW CONDITIONS   |
 10 blk PRG  P.MODULATED EXA.   |  example tunes ("P." prefix = packed song),
 14 blk PRG  P.DOGS             >  by Longhair / Touldie / Shogoon (see read-me §4)
 41 blk PRG  P.DRIP SCORE       |
 15 blk PRG  P.INTRO MUSIC      |
 26 blk PRG  P.X-STYLE          |
 16 blk PRG  P.XTD COVER        |
 27 blk PRG  P.THATSBRRR...    /
 23 blk PRG  PRZECZYTAJ MNIE!  <- the Polish read-me (decoded & translated in §4)
```
`HDT PLAYER`, `HDT DEPACKER`, `HDT RELOCATOR`, `MAIN` and the read-me were the files the
prior agent extracted into `_artifacts/sdk/extracted/` (as `PLAYER_V1.*.bin`,
`DEPACKER.SRC.bin`, `EDYTOR.SRC.bin`, `PACKER.SRC.bin`, `RELEASE_NOTES.bin`) and
`tmp/hardtrack/OUT_*.prg`.

### `Hardtrack_Composer_v1_-6speed-.d64` — disk name `[CENTRAX/AGONY!]`
```
 41 blk PRG  HARDTRACK V1.0+6  <- single packed file, the 6× multispeed editor
```
The bundled `.inf0` release note reads verbatim:
> Hardtrack Composer 6\*speed version
> Done by **Shatter/Beverly Hills Group (now Glover/Samar.)**
> Uploaded by **CenTraX./.Agony**
> ftp://ftp.elysium.pl/ ......republic

### `Hardtrack_Tape.d64` — disk name `]CENTRAX/AGONY![`
```
 44 blk PRG  HARDTRACK TAPE    <- single packed file, tape-loader build
```

## 3. SDK binaries already extracted (`_artifacts/sdk/extracted/`)

| file | size | notes (from `strings`) |
|---|---|---|
| `PLAYER_V1.0.bin` | 5309 | xa65-style source listing; embeds `PLAYER V1.0 BY LONGHAIR/ELYSIUM`, `MUSIC BY YOU /ELYSIUM!`. Polish state labels: NRTUNE, TRPO/PTPO, SPEEE, PETLA (loop), PRWA/NRWA/POSWA (wave prev/num/pos), NRDRU/PRDRU (drum), PULST/PULS, NRPU/POSPU/CZASPU (pulse num/pos/time), NRFI/POSFI/CZASFI (filter), KASAD (clear ADSR), WOLNE (free). |
| `PLAYER_V1.1.bin` | 5646 | `PLAYER V1.1 BY LONGHAIR/ELYSIUM`. Same label set + extra `QWERT` rows + an `IRQ LDA $FB` fragment — ~337 bytes larger than V1.0 (see version table in `archive_authors_versions.md`). |
| `RELEASE_NOTES.bin` | 7170 | Mis-named — it is itself a player binary (loads $1000) embedding `PLAYER 1.0 BY LONGHAIR/ELYSIUM! - MUSIC DONE BY LONGHAIR/ELYSIUM`, followed by a SID note-data table. |
| `EDYTOR.SRC.bin` | 35016 | Editor source (Polish comments). |
| `PACKER.SRC.bin` | 6170 | Packer source. |
| `DEPACKER.SRC.bin` | 5193 | Depacker source. Polish comments document the data layout — see §3.1. |

These source labels/comments are owned by the player-source documentation task; cross-referenced
here only for provenance. The format-table semantics are in `archive_authors_versions.md` §
"Format (from CSDb forum)".

### 3.1 DEPACKER.SRC.bin — Polish comments (data-layout relevant, translated)
```
DLUG.PATERNOW                = "długość paternów"  = pattern lengths
ODSTEPY MIEDZY PATERNAMI     = spacing between patterns
... I MACROS                 = ... and macros
CZYSZCZENIE PATERNOW,        = clearing of patterns,
  TRACKOW, SOUNDOW             tracks, sounds (= reset to defaults)
PROCEDURA USTAWIAJACA        = procedure that sets the addresses in the PLAYER
  ADRESY W PLAYERZE            to standard values
DODATKOWA PROCEDURA          = extra procedure that re-writes the LAST pattern
  PRZEPISUJACA OSTATNI PATERN
SKOK GDY TYLKO 1 PATERN      = jump (branch) when there is only 1 pattern
PRZEPISYWANIE MACROS         = rewriting (copying) of macros
PRZEPISANIE SOUNDOW          = rewriting of sounds (instruments)
PRZEPISANIE MUZYCZKI POD ... = relocating the music under (a given address)
CZYTANIE MUZYCZKI DO PAMIECI = reading the music into memory
TUNE*                        = (per-tune block marker)
```
Read: the depacker assembles a self-contained tune from the editor's separate
pattern / track / macro / sound / pulse / filter tables and re-points the player's
absolute pointers — confirming the "engine holds absolute pointers per build" picture.

## 4. `PRZECZYTAJ MNIE!` ("READ ME!") — decoded and translated

The read-me on the V1.0 disk is a crunched self-displaying note (BASIC `SYS 2059`).
It was decoded by emulating the depacker (one-off 6502 emulator at
`_artifacts/decrunch_readme.py`); the cleartext lands in RAM at $3000–$3A6F as 40-column
screen text. Reproduced verbatim, then translated. **This is the single most authoritative
provenance artifact — the authors' own credits, in their own words.**

### 4.1 Polish original (verbatim, decoded screen text)
```
WITAM!
DZIEKUJE, ZE WCZYTALES TA NOTKA. NIESTETY W TYM ZESTAWIE ZNAKOW NIE MA
POLSKICH LITER, WIEC BEDZIESZ MUSIAL ZADOWOLIC SIE TEKSTEM "POLSKAWYM".
DO POWSTANIA TEGO EDYTORA PRZYCZYNILO SIE WIELE OSOB, WIEC MYSLE ZE
POWINIENEM JE WYMIENIC. WSZYSTKIM Z NICH DZIEKUJE ZA ICH POMOC. BEZ NICH
TEN EDYTOR PEWNIE NIGDY BY NIE UJZAL SWIATLA DZIENNEGO.

KOD EDYTORA: JA CZYLI KRZYSIEK DABROWSKI ALIAS BRUSH/ELYSIUM
KOD PLAYERA: MILOSZ IGNATOWSKI CZYLI LONGHAIR/ELYSIUM
KOD INTRA: KRZYSIEK AUGUSTYN VEL ZEPHYR/ELYSIUM
TYTULOWY OBRAZEK: WOJTEK NIEMCZYK - CRUISE/ELYSIUM
MUZYKA W INTRZE: MATTHIAS HARTUNG VEL THE SYNDROM/TIA/CREST
GRAJEK DO MUZYCZEK: SLAWEK ABRAMCZYK - KSB/DATACRIME
FASTLOADER DYSKOWY: KRZYSIEK MATULA - K.M./TABOO
TURBO ROM SAVER: MAREK MATULA - MMS OF TABOO
UTWORY PRZYKLADOWE: LONGHAIR. BARTOSZ TABAKA - TOULDIE/ELYSIUM,
  WOJTEK RADZIEJEWSKI VEL SHOGOON/TABOO
BETA TESTERZY: LONGHAIR, TOULDIE, SHOGOON.
CENNE UWAGI: THE SYNDROM, TOMEK OLSZEWSKI ALIAS HAIN/ELYSIUM

JAK WIDAC POKAZNA EKIPA!

KORZYSTAJAC Z OKAZJI CHCIALBYM TEZ POZDROWIC WSZYSTKICH MOICH PRZYJACIOL:
TOMKA OLSZEWSKIEGO, PAWLA BONDARYKA, TOMKA MIELNIKA, ROMKA DOBOSZA,
KRZYSKA AUGUSTYNA, MILOSZA IGNATOWSKIEGO, BARTKA TABAKE, WOJTKA
RADZIEJEWSKIGO, MATULA BROTHERS, ARTURA BYCHOWSKIEGO, ROBERTA KANA,
RAFALA PIASKA, WOJTKA NIEMCZYKA, PAWLA PAWLAKA, BARTKA SUPCZINSKIEGO,
KUBE PROCHOCKIEGO, MARIUSZA WOSKO, MACKA DENCA, WITKA BRYNDZE (POWINIENES
BYC NA POCZATKU, NIE OBRAZ SIE) ORAZ KILKU KTORYCH ZNAM TYLKO Z
PSEUDONIMOW: RASCAL'A/SUN, LATIFAH'A/ESM, DICKENS'A/SUN, MAJE/F4CG,
COMANCHE/AGONY I WSZYSTKICH POZOSTALYCH, KTORZY MNIE DOBRZE WSPOMINAJA.

JEZELI SADZISZ, ZE TWOJE KOMPOZYCJE NA HARDTRACK'U SA WYSOKIEJ JAKOSCI,
TO NAPISZ DO MNIE I POCHWAL SIE NIMI (ALE TYLKO WTEDY, GDY MASZ LEGALNA
KOPIE EDYTORA!). JESLI NAPRAWDE BEDZIESZ DOBRY, TO NIE POZALUJESZ SWOJEJ
DECYZJI.
           KRZYSIEK DABROWSKI
             ZEROMSKIEGO 5
            06-300 PRZASNYSZ
```

### 4.2 English translation
> **WELCOME!**
> Thank you for loading this note. Unfortunately this character set has no Polish
> letters, so you'll have to make do with "Polish-ish" text.
> Many people contributed to creating this editor, so I think I should list them.
> I thank all of them for their help. Without them this editor would probably never
> have seen the light of day.
>
> - **Editor code:** me, i.e. **Krzysiek Dąbrowski, alias Brush/Elysium**
> - **Player code:** **Miłosz Ignatowski, i.e. Longhair/Elysium**
> - **Intro code:** Krzysiek Augustyn, a.k.a. Zephyr/Elysium
> - **Title picture:** Wojtek Niemczyk – Cruise/Elysium
> - **Intro music:** Matthias Hartung, a.k.a. The Syndrom/TIA/Crest
> - **Music driver/player [used for the example tunes]:** Sławek Abramczyk – KSB/Datacrime
> - **Disk fastloader:** Krzysiek Matula – K.M./Taboo
> - **Turbo ROM saver:** Marek Matula – MMS of Taboo
> - **Example tunes:** Longhair; Bartosz Tabaka – Touldie/Elysium; Wojtek Radziejewski a.k.a. Shogoon/Taboo
> - **Beta testers:** Longhair, Touldie, Shogoon
> - **Valuable feedback:** The Syndrom; Tomek Olszewski, alias Hain/Elysium
>
> As you can see, quite a crew!
>
> [Greetings list of friends — Tomek Olszewski, Paweł Bondaryk, Tomek Mielnik, Romek
> Dobosz, Krzysiek Augustyn, Miłosz Ignatowski, Bartek Tabaka, Wojtek Radziejewski,
> the Matula brothers, Artur Bychowski, Robert Kan, Rafał Piasek, Wojtek Niemczyk,
> Paweł Pawlak, Bartek Supczyński, Kuba Próchocki, Mariusz Wosko, Maciek Deniec,
> Witek Bryndza ("you should be at the top, no offence"), plus a few known only by
> handle: Rascal/Sun, Latifah/ESM, Dickens/Sun, Maje/F4CG, Comanche/Agony, and
> everyone else who remembers me fondly.]
>
> If you think your HardTrack compositions are high quality, write to me and show
> them off (but only if you own a **legal copy** of the editor!). If you're really
> good, you won't regret your decision.
>
> > **Krzysiek Dąbrowski**
> > Żeromskiego 5
> > 06-300 Przasnysz [Poland]

### 4.3 Provenance takeaways from the read-me
- **Brush = Krzysiek Dąbrowski** wrote the **editor** (real name now confirmed).
- **Longhair = Miłosz Ignatowski** wrote the **player/replay routine** (the engine HVSC plays).
- The Elysium-internal `Sławek Abramczyk / KSB / Datacrime` "grajek do muzyczek" is the
  *example-tune driver*, not the HardTrack replay — do not confuse with the player.
- Author postal address (Przasnysz, Poland) anchors the Polish-scene provenance.

> Note: the read-me lists no version number — it shipped on the V1.0 disk. V1.1 is a
> later player-only revision (see `archive_authors_versions.md`).
```
local one-off tool: pipelines/hardtrack/docs/_artifacts/decrunch_readme.py
(minimal NMOS-6502 emulator; reads tmp/hardtrack/OUT_PRZECZYTAJ_MNIE.prg READ-ONLY,
 runs the crunched note's depacker, dumps the cleartext from $3000. Re-runnable.)
```

## Leads to follow
- Fetch `./groups/Elysium/misc/hardtrack_cracks.zip` (30771 B) — game cracks scored with HardTrack; useful for a deployment/usage census, not the engine itself.
- Fetch `./groups/Elysium/misc/C64_music_pl_v01.txt.zip` — Polish C64-music survey doc that may carry a HardTrack section / manual excerpt.
- The original V1.0 shipped with a *printed* Polish manual (a sealed copy was auctioned on Allegro.pl per c64scene.pl thread t=584). If a scan ever surfaces it would be the only first-party prose format spec.
