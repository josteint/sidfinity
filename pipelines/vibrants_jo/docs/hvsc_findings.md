---
source_url: local: /home/jtr/sidfinity/hvsc85/
fetched_via: local read
fetch_date: 2026-06-16
author: research agent
content_date: 2026-06-16
reliability: primary
---

# Vibrants/JO — HVSC Local Research Findings

## Musicians.txt bio

Verbatim entry (line 840):

```
JO (Olsen, Jesper {Technic, Rock}) / Amok / Vibrants - DENMARK
```

Full name: **Poul-Jesper Olsen**. Handles used: `JO`, `Technic`, `Rock`.
Groups: Amok, Vibrants (also credited to Genesis Project, Futurity, BUDS/NATO, Maniacs of Noise, Amok Sound Dept., Amok Developments, Fire Eagle, Tale Software/Kingsoft).
Country: Denmark.

Note: **Vibrants** is also home to **JCH** (who made the DeepSID online player) and **Metal** (Torben Hansen, factory sound bank for an unrelated product). JO and JCH are separate members of the same group.

---

## STIL excerpts — technical notes on JO tunes

(From `/home/jtr/sidfinity/hvsc85/DOCUMENTS/STIL.txt`)

```
/MUSICIANS/J/JO/Airwolf.sid
  TITLE: Airwolf Theme [from the TV series]
 ARTIST: Sylvester Levay

/MUSICIANS/J/JO/Airwolf_Theme.sid
  TITLE: Airwolf Theme [from the TV series]
 ARTIST: Sylvester Levay

/MUSICIANS/J/JO/Bakery_Rock.sid
  TITLE: Comic Bakery, Tune #1
 ARTIST: Martin Galway

/MUSICIANS/J/JO/Bat-Crap.sid
  TITLE: Batman Theme [from the TV series]
 ARTIST: Neal Hefti

/MUSICIANS/J/JO/Behind_the_Wheel.sid
  TITLE: Behind the Wheel [from Music for the Masses]
 ARTIST: Depeche Mode

/MUSICIANS/J/JO/Billie_Jean_unfinished.sid
  TITLE: Billie Jean [from Thriller]
 ARTIST: Michael Jackson

/MUSICIANS/J/JO/Comic_Bakery_Remix.sid
  TITLE: Comic Bakery, Tune #1
 ARTIST: Martin Galway

/MUSICIANS/J/JO/Commando_Theme_Remix.sid
  TITLE: Commando, Tune #1
 ARTIST: Rob Hubbard

/MUSICIANS/J/JO/Crockets_Theme.sid
  TITLE: Crockett's Theme [from the TV series Miami Vice]
 ARTIST: Jan Hammer
COMMENT: JO states this tune is a remake of MAD's cover, since JO himself never
         heard the original.

/MUSICIANS/J/JO/Destiny_v3.sid
(#3)
  TITLE: Funeral March [from Sonate No. 2 in B flat minor Op. 35]
 ARTIST: Frédéric François Chopin

/MUSICIANS/J/JO/Gamekiller_1989_Remix.sid
  TITLE: The Human Race, Tune #5
 ARTIST: Rob Hubbard
COMMENT: Covers the version in /MUSICIANS/H/Hubbard_Rob/Game_Killer.sid

/MUSICIANS/J/JO/Grid.sid
  TITLE: Blue Monday
 ARTIST: New Order

/MUSICIANS/J/JO/Hit_It.sid
COMMENT: Later used in the game "Woody the Worm", (C) 1993 Golden Disk
         64/CP Verlag. See /MUSICIANS/H/HJE/Woody_the_Worm.sid, Tune #1.

/MUSICIANS/J/JO/JT_House_S-Express.sid
  TITLE: Theme From S-Express [from Original Soundtrack]
 ARTIST: S'Express, written by Mark Moore and Pascal Gabriel
COMMENT: Covers the version in /MUSICIANS/T/Tel_Jeroen/S-Express.sid

/MUSICIANS/J/JO/Jaws_Imitation.sid
  TITLE: Jaws [from the movie]
 ARTIST: John Williams

/MUSICIANS/J/JO/Monday_Mix.sid
  TITLE: Blue Monday
 ARTIST: New Order

/MUSICIANS/J/JO/Moon_Patrol.sid
  TITLE: BGM [from the arcade game Moon Patrol]
 ARTIST: Ichirou Takagi
COMMENT: Covers the music from the C64 game "Moon Patrol" by Atarisoft.
         See /GAMES/M-R/Moon_Patrol.sid, Tune #1

/MUSICIANS/J/JO/Ode_to_Robs_Race.sid
  TITLE: The Human Race, Tune #4
 ARTIST: Rob Hubbard

/MUSICIANS/J/JO/Popcorn.sid
  TITLE: Popcorn [from Music To Moog By]
 ARTIST: Gershon Kingsley

/MUSICIANS/J/JO/Rautaudan_preview.sid
COMMENT: Earlier version of /MUSICIANS/J/JO/Rautaudaw.sid, Tune #1

/MUSICIANS/J/JO/Rautaudaw.sid
COMMENT: Also used in the game "Killozapp", (C) 1991 Golden Disk 64/CP Verlag.

/MUSICIANS/J/JO/Rob_Lam_Fejl.sid
  TITLE: Dragon's Lair Part II, Tune #3
 ARTIST: Rob Hubbard

/MUSICIANS/J/JO/Sex_n_Crime_5.sid
COMMENT: Also used in Sex 'n' Crime #21

/MUSICIANS/J/JO/Some_Sanne.sid
  TITLE: Hvis du forstod
 ARTIST: Sanne Salomonsen
COMMENT: Covers /MUSICIANS/L/Link/Sanne.sid

/MUSICIANS/J/JO/Some_of.sid
  TITLE: Shapes
 ARTIST: Jeroen Tel
COMMENT: Covers the version in /MUSICIANS/D/Deenen_Charles/Ala_Gal.sid, Tune #2

/MUSICIANS/J/JO/TWS_Gonna_Die.sid
  TITLE: Funeral March [from Sonate No. 2 in B flat minor Op. 35]
 ARTIST: Frédéric François Chopin
COMMENT: This theme can be heard at 0:00 and 0:43
```

No STIL entries contain technical player implementation notes — comments are
purely about musical attribution.

---

## PSID header table

All 105 native Vibrants/JO SIDs (excludes Multi_Move.sidfinity.sid which is a
pipeline artifact, and Grid.sid which sidid classifies as unidentified rather
than Vibrants/JO). All load addresses are 0x0000 (embedded in the SID binary
with a 2-byte load address prefix at data start — typical for PSID v2).

| File | init | play | songs | released | name |
|------|------|------|-------|----------|------|
| 01_1989.sid | 0x1800 | 0x1806 | 1 | 1989 Amok Sound Dept. | 01/1989 |
| 2_Cool_Ones.sid | 0x0fff | 0x1006 | 2 | 1988-89 Jesper Olsen | 2 Cool Ones |
| 5_Minutes_Crap.sid | 0x0fff | 0x1003 | 1 | 1988-89 Jesper Olsen | 5 Minutes Crap |
| A_Way_to_be_Cool_for_W_S.sid | 0x1e23 | 0x107c | 1 | 1988 Genesis Project | A Way to be Cool (for W. S.) |
| A_r_cade_Sprint.sid | 0x3003 | 0x3000 | 7 | 1990 Amok Sound Dept. | A(r)cade Sprint |
| Airwolf.sid | 0xf000 | 0xf016 | 1 | 1988 Amok Sound Dept. | Airwolf! |
| Airwolf_Theme.sid | 0x1003 | 0x1009 | 1 | 1988-89 Amok Sound Dept. | Airwolf Theme |
| Amok_Title.sid | 0x1000 | 0x1003 | 1 | 1988 Amok Sound Dept. | Amok Title |
| Bad_Again.sid | 0x1000 | 0x1016 | 1 | 1988 Amok Sound Dept. | Bad Again |
| Bad_One.sid | 0x5047 | 0x509a | 1 | 1988 Genesis Project | Bad One |
| Bad_Track.sid | 0xa900 | 0xa903 | 3 | 1988-89 Amok Sound Dept. | Bad Track |
| Bakery_Rock.sid | 0x4000 | 0x4003 | 1 | 1988 Amok Sound Dept. | Bakery Rock! |
| Basic_Tune.sid | 0x1000 | 0x1003 | 1 | 1989 Amok | Basic Tune |
| Bat-Crap.sid | 0x4000 | 0x4003 | 1 | 1988 Genesis Project | Bat-Crap |
| Batfunk.sid | 0x15e0 | 0x09b3 | 1 | 1989 Maniacs of Noise | Batfunk |
| Battle_Pac.sid | 0x0abf | 0x0aff | 2 | 1989 Amok Sound Dept. | Battle Pac |
| Beat.sid | 0x2003 | 0x2006 | 1 | 1988-89 Jesper Olsen | Beat! |
| Behind_the_Wheel.sid | 0x2003 | 0x2006 | 1 | 1988 Genesis Project | Behind the Wheel |
| Better_Weird.sid | 0x0900 | 0x0906 | 1 | 1989 Amok Sound Dept. | Better/Weird |
| Billie_Jean_unfinished.sid | 0x39f7 | 0x3003 | 1 | 1989 Amok Sound Dept. | Billie Jean (unfinished) |
| Busy_Scene.sid | 0x1003 | 0x1006 | 1 | 1988 Genesis Project | Busy Scene |
| Catcher_tune_1.sid | 0x3400 | 0x3403 | 1 | 1989 BUDS/NATO | Catcher (tune 1) |
| Col.sid | 0x3000 | 0x3003 | 1 | 1989 Amok | Col |
| Comic_Bakery_Remix.sid | 0x1000 | 0x1003 | 1 | 1988 Amok Sound Dept. | Comic Bakery Remix |
| Commando_Theme_Remix.sid | 0x4000 | 0x4003 | 1 | 1989 Amok Sound Dept. | Commando Theme Remix |
| Contex.sid | 0x081f | 0x0826 | 1 | 1989 Amok Sound Dept. | Contex |
| Cool_Intro_Music.sid | 0x1003 | 0x1006 | 1 | 1988 Futurity | Cool Intro Music |
| Creep_Mix.sid | 0x1003 | 0x1006 | 1 | 1988 Futurity | The Creep Mix |
| Crockets_Theme.sid | 0x0a0b | 0x0a11 | 1 | 1989 Amok Sound Dept. | Crocket's Theme |
| Cyb_Test.sid | 0x3000 | 0x3003 | 1 | 1989 Amok | Cyb Test |
| Delirious_V_second_part.sid | 0x100e | 0x1055 | 1 | 1989 Amok Sound Dept. | Delirious V (second part) |
| Destiny_v1.sid | 0x4f4f | 0x43ae | 2 | 1989 Amok Sound Dept. | Destiny (v1) |
| Destiny_v2.sid | 0x1a3a | 0x0b9b | 2 | 1989 Amok Sound Dept. | Destiny (v2) |
| Destiny_v3.sid | 0x1000 | 0x1006 | 3 | 1989 Amok Sound Dept. | Destiny (v3) |
| Disco_Flip.sid | 0x1000 | 0x1016 | 1 | 1988 Amok Sound Dept. | Disco Flip |
| Dos.sid | 0x3000 | 0x3003 | 1 | 1989 Amok | Dos |
| Dreams.sid | 0xc052 | 0xc055 | 1 | 1988 Jesper Olsen | Dreams |
| Fast_n_Lame.sid | 0x1828 | 0x1039 | 1 | 1988-89 Amok Sound Dept. | Fast'n'Lame |
| First_Digi.sid | 0x2300 | 0x0000 | 1 | 1989-90 Amok Sound Dept. | First Digi |
| For_MON_Tune.sid | 0x095d | 0x0a42 | 1 | 1989-90 Amok Sound Dept. | For MON Tune |
| For_Weird_Science.sid | 0x4003 | 0x4006 | 1 | 1988 Genesis Project | For Weird Science |
| Frighthour.sid | 0x0fff | 0x1006 | 1 | 1988-89 Jesper Olsen | Frighthour |
| Gamekiller_1989_Remix.sid | 0x0fff | 0x1006 | 1 | 1989 Amok Sound Dept. | Gamekiller 1989 Remix |
| Gamlere.sid | 0x4f91 | 0x425c | 3 | 1989-90 Amok Sound Dept. | Gamlere |
| Gamlest.sid | 0x4e37 | 0x425c | 2 | 1989-90 Amok Sound Dept. | Gamlest |
| Genesist_Muzak_for_the_demo.sid | 0x2003 | 0x2006 | 1 | 1988 Genesis Project | Genesist Muzak (for the demo) |
| Hangman.sid | 0x2cbc | 0x2006 | 2 | 1989 Genesis Project | Hangman |
| Hi-Score.sid | 0x1000 | 0x1003 | 1 | 1989 Amok | Hi-Score |
| Highlands.sid | 0x3000 | 0x3003 | 1 | 1989 Amok | Highlands |
| Hit_It.sid | 0xc003 | 0xc009 | 1 | 1989 Amok Sound Dept. | Hit It |
| Hrmm.sid | 0x0fff | 0x1006 | 1 | 1989 Genesis Project & Fire Eagle | Hrmm... |
| Impressive.sid | 0x1000 | 0x1003 | 1 | 1989 Amok | Impressive |
| Intro_Music.sid | 0x2003 | 0x2006 | 1 | 1988 Genesis Project | Intro Music |
| Intro_Music_3.sid | 0x1000 | 0x101f | 1 | 1988-89 Jesper Olsen | Intro Music 3 |
| Intro_Tune_1.sid | 0x0810 | 0x0816 | 1 | 1988-89 Jesper Olsen | Intro Tune 1 |
| JO_01.sid | 0x1000 | 0x1006 | 1 | 1989 Amok | <?> |
| JO_Test_1.sid | 0x1000 | 0x1006 | 1 | 1989 Jesper Olsen | JO Test 1 |
| JO_Test_2.sid | 0x2000 | 0x2003 | 1 | 1989 Jesper Olsen | JO Test 2 |
| JO_goes_Myth.sid | 0x1000 | 0x1003 | 1 | 1989-90 Amok Sound Dept. | JO goes Myth! |
| JT_House_S-Express.sid | 0x1000 | 0x1009 | 1 | 1988-89 Jesper Olsen | JT House (S-Express) |
| Jans_Tune.sid | 0x500c | 0x500f | 1 | 1988 Genesis Project | Jan's Tune |
| Jaws_Imitation.sid | 0x1000 | 0x1003 | 1 | 1988-89 Amok Sound Dept. | Jaws Imitation |
| Lame.sid | 0x0fff | 0x1003 | 1 | 1988-89 Jesper Olsen | Lame |
| Lame_Part.sid | 0xe000 | 0xe00b | 1 | 1990 Genesis Project | Lame Part |
| Le_Action.sid | 0x1000 | 0x1006 | 1 | 1988-89 Amok Sound Dept. | Le Action |
| Le_Cool.sid | 0x1000 | 0x1006 | 1 | 1989 Amok Sound Dept. | Le Cool |
| Little_Game_Tune.sid | 0x2fff | 0x3006 | 1 | 1989 Jesper Olsen | Little Game Tune |
| Megabad.sid | 0xe000 | 0xe016 | 1 | 1988 Jesper Olsen | Megabad |
| Megafast.sid | 0x0ffb | 0x1003 | 1 | 1988 Genesis Project | Megafast |
| Monday_Mix.sid | 0x5003 | 0x5006 | 1 | 1988 Genesis Project | The Monday Mix |
| Moon_Patrol.sid | 0x08ff | 0x0906 | 1 | 1989 Amok Sound Dept. | Moon Patrol |
| Music_Demo.sid | 0x6000 | 0x6003 | 1 | 1989 Amok Sound Dept. | Music Demo |
| My_Best_Tune.sid | 0x1003 | 0x1006 | 1 | 1988 Futurity | My Best Tune |
| No_Good.sid | 0x0fff | 0x1006 | 1 | 1989 Amok Sound Dept. | No Good |
| No_Name.sid | 0x6779 | 0x6042 | 1 | 1989 Amok Sound Dept. | No Name |
| Ny_unfinished.sid | 0x0b52 | 0x0b9f | 1 | 1990 Amok Sound Dept. | Ny (unfinished) |
| Ode_to_Robs_Race.sid | 0x1000 | 0x1006 | 1 | 1988-89 Amok Sound Dept. | Ode to Rob's Race |
| Old.sid | 0x1003 | 0x1006 | 1 | 1989 Amok Sound Dept. | Old |
| Pice_of_Mind.sid | 0x4000 | 0x4003 | 1 | 1988 Amok Sound Dept. | Pice of Mind |
| Pice_of_Mind_2.sid | 0x4fff | 0x5003 | 1 | 1989 Amok Sound Dept. | Pice of Mind 2 |
| Popcorn.sid | 0xcafc | 0xc0bb | 1 | 1989 Amok Sound Dept. | Popcorn |
| Psycho.sid | 0x1000 | 0x1006 | 1 | 1988 Amok Sound Dept. | Psycho |
| Quick_Kill.sid | 0x10e2 | 0x10e5 | 1 | 1988 Genesis Project | Quick Kill |
| Rautaudan_preview.sid | 0x0b07 | 0x0b0a | 1 | 1989 Amok Sound Dept. | Rautaudan (preview) |
| Rautaudaw.sid | 0x0bba | 0x0bf4 | 5 | 1989 Amok Sound Dept. | Rautaudaw |
| Rob_Lam_Fejl.sid | 0x4e00 | 0x425c | 1 | 1989-90 Amok Sound Dept. | Rob Lam Fejl |
| Sex_n_Crime_10.sid | 0xf003 | 0xf000 | 1 | 1989 Amok Sound Dept. | Sex'n'Crime #10 |
| Sex_n_Crime_20_intro.sid | 0x100d | 0x1003 | 1 | 1990 Amok Sound Dept. | Sex'n'Crime #20 (intro) |
| Sex_n_Crime_5.sid | 0xefff | 0xf009 | 1 | 1989 Amok Sound Dept. | Sex'n'Crime #5 |
| Short_Jingle.sid | 0x0814 | 0x081d | 1 | 1989 Amok Sound Dept. | Short Jingle |
| Some_Sanne.sid | 0x3000 | 0x3003 | 1 | 1989 Amok | Some Sanne |
| Some_of.sid | 0x0fff | 0x1006 | 1 | 1988-89 Jesper Olsen | Some of... |
| Soporific.sid | 0xefff | 0xf006 | 1 | 1988 Amok | Soporific |
| Soporific_2.sid | 0xeffe | 0xf006 | 1 | 1989 Amok Sound Dept. | Soporific 2 |
| Soundtrack_1.sid | 0xe000 | 0xe003 | 5 | 1988 Amok Sound Dept. | Soundtrack 1 |
| Stormlord_2_Demo.sid | 0x1000 | 0x1006 | 1 | 1989 Amok | Stormlord 2 Demo |
| TWS_Gonna_Die.sid | 0x4a03 | 0x4a06 | 1 | 1988 Genesis Project | TWS Gonna Die |
| Technic_01.sid | 0x4003 | 0x4006 | 1 | 1989 Genesis Project | <?> |
| Tune.sid | 0x3000 | 0x3003 | 1 | 1988-89 Jesper Olsen | Tune |
| Turn_It.sid | 0xf009 | 0xf000 | 1 | 1990 Tale Software/Kingsoft | Turn It |
| Tweetys_Tweedledeed.sid | 0xf000 | 0xf003 | 1 | 1989 Amok Sound Dept. | Tweety's Tweedledeed! |
| Ultima_1.sid | 0xe000 | 0xe003 | 1 | 1988 Amok Sound Dept. | Ultima 1 |
| Wraxirmer_part_5.sid | 0x3fff | 0x4003 | 1 | 1989 BUDS | Wraxirmer part 5 |

**Non-Vibrants/JO files in the directory (sidid override):**
- `JO_goes_Myth.sid` — sidid: `MoN/Bjerregaard` (Johannes Bjerregaard / Maniacs of Noise engine)
- `Grid.sid` — sidid: unclassified (not matched to any known engine)
- `Multi_Move.sid` — sidid: `MoN/FutureComposer` (already migrated; usf_path present)

---

## Header variant clusters

### Cluster A — $1000 range, init≈$1000, play≈$1003/$1006 (most common)
**~35 files.** init in range $0fff–$100e, play in range $1003–$1016/$101f.
Init address often $1000 (canonical) but also $0fff (one byte before — init
routine starts at $1000, PSID header claims $0fff as a "JSR $1000" trampoline
or data prefix trick), $1003, $100d, $100e.
Play address clustered at $1003, $1006, $1009, $1016, $101f.

This appears to be JO's **primary engine** — simple, $1000-based layout.
The $0fff init variants (2_Cool_Ones, 5_Minutes_Crap, Frighthour, Gamekiller,
Hrmm, Lame, No_Good, Some_of, Megafast=$0ffb) likely share the same engine
with a trampoline byte at $0fff→$1000. A few have slightly different play
offsets, suggesting engine revisions or per-tune customization.

Largest sub-groups:
- init=$1000, play=$1003 (~12 files): Amok_Title, Basic_Tune, Comic_Bakery_Remix, Highlands (=$3000), Hi-Score, Impressive, Jaws_Imitation, JO_goes_Myth (MoN), Commando_Theme_Remix (=$4000), Bat-Crap (=$4000), Pice_of_Mind (=$4000), Bakery_Rock (=$4000)
- init=$1000, play=$1006 (~14 files): Bad_Again, Beat (=$2003), Behind_the_Wheel (=$2003), Destiny_v3, JO_01, JO_Test_1, Le_Action, Le_Cool, My_Best_Tune (=$1003), Ode_to_Robs_Race, Old (=$1003), Psycho, Stormlord_2_Demo
- init=$0fff, play=$1006 (~7 files): 2_Cool_Ones, Frighthour, Gamekiller_1989_Remix, Hrmm, No_Good, Some_of
- init=$1003, play=$1006 (~5 files): Airwolf_Theme (play=$1009), Busy_Scene, Cool_Intro_Music, Creep_Mix, My_Best_Tune, Old

### Cluster B — $2000 range
**~5 files.** init=$2003, play=$2006 (Beat, Behind_the_Wheel, Genesist_Muzak,
Intro_Music) + JO_Test_2 (init=$2000, play=$2003). Likely same engine at a
different base address.

### Cluster C — $3000 range
**~9 files.** init=$3000/$3003/$3400/$3fff, play=$3000/$3003/$3006/$3403.
Col, Catcher_tune_1, Cyb_Test, Dos, Highlands, Some_Sanne, Tune,
Wraxirmer_part_5. A(r)cade_Sprint has 7 subtunes (the most in this cluster).

### Cluster D — $4000 range
**~9 files.** init=$4000/$4003/$4a03/$4e37/$4f4f/$4f91, play=$4003/$4006/$4a06/$425c/$43ae.
Bakery_Rock, Bat-Crap, Commando_Theme_Remix, For_Weird_Science, Pice_of_Mind,
Technic_01, TWS_Gonna_Die + multi-subtune Gamlere/Gamlest/Destiny_v1/Rob_Lam_Fejl.

Notable sub-cluster: **play=$425c** appears in Gamlere (init=$4f91),
Gamlest (init=$4e37), Rob_Lam_Fejl (init=$4e00) — same play address despite
different init addresses. Likely the same engine instance with the init routine
at different locations but play routine fixed at $425c.

### Cluster E — $5000/$6000 range
**~4 files.** init=$5003/$500c/$6000/$6779, play=$5003/$5006/$500f/$6003/$6042.
Monday_Mix, Jans_Tune, Pice_of_Mind_2, Music_Demo, No_Name.

### Cluster F — $c000 range
**~4 files.** Dreams (init=$c052, play=$c055), Hit_It (init=$c003, play=$c009),
Popcorn (init=$cafc, play=$c0bb).
Popcorn is an outlier: init far above play ($cafc → $c0bb), suggesting the
init routine is elsewhere in the file or a large data block precedes the player.

### Cluster G — $e000/$f000 range (high memory)
**~12 files.** Airwolf (init=$f000, play=$f016), Lame_Part/$e000, Megabad/$e000,
Sex_n_Crime_5/10 ($efff–$f009), Soporific/$efff, Soporific_2/$effe,
Soundtrack_1/$e000, Turn_It (init=$f009, play=$f000), Tweetys_Tweedledeed/$f000,
Ultima_1/$e000. The $efff/$effe init variants mirror the $0fff pattern from
Cluster A — a trampoline byte before the engine.
Note: $e000–$ffff is ROM territory in the C64 without custom banking — these
tunes likely disable KERNAL ROM or remap. Need banking investigation if migrating.

### Cluster H — Scatter / early experiments
**~15 files.** Widely varying addresses, unusual patterns:
- **First_Digi** (init=$2300, play=$0000): play address $0000 is extremely unusual;
  likely a digi/sample playback tune that doesn't use a standard IRQ play routine.
- **Batfunk** (init=$15e0, play=$09b3): sidid attributes to Maniacs of Noise not JO.
- **Billie_Jean_unfinished** (init=$39f7, play=$3003): init above play in separate area.
- **A_Way_to_be_Cool** (init=$1e23, play=$107c): split layout.
- **For_MON_Tune** (init=$095d, play=$0a42): low page $09/$0a, very small footprint.
- **Bad_Track** (init=$a900, play=$a903): $A900 range — just below $BFFF banked ROM.
- **Dreams** (init=$c052, play=$c055), **Popcorn** (init=$cafc, play=$c0bb): $C000 range.
- **Sex_n_Crime_10** (init=$f003, play=$f000), **Turn_It** (init=$f009, play=$f000):
  play BEFORE init in address space — reversed layout.
- **Grid.sid**: sidid UNCLASSIFIED — may be a different engine entirely.

### Multi-subtune tunes
| File | subtunes |
|------|---------|
| A_r_cade_Sprint.sid | 7 |
| Rautaudaw.sid | 5 |
| Soundtrack_1.sid | 5 |
| Destiny_v3.sid | 3 |
| Gamlere.sid | 3 |
| Bad_Track.sid | 3 |
| 2_Cool_Ones.sid | 2 |
| Battle_Pac.sid | 2 |
| Destiny_v1.sid | 2 |
| Destiny_v2.sid | 2 |
| Gamlest.sid | 2 |
| Hangman.sid | 2 |

---

## Engine detection summary (sidid)

Of the 106 entries in the directory:
- **103** classified as `Vibrants/JO` by sidid
- **1** classified as `MoN/Bjerregaard` (JO_goes_Myth.sid)
- **1** classified as `MoN/FutureComposer` (Multi_Move.sid — already migrated)
- **1** unclassified (Grid.sid)

The `Vibrants/JO` label covers the full address scatter above — sidid sees a
consistent fingerprint across all load/play address ranges, suggesting either
JO's player has a distinctive byte pattern regardless of placement, or sidid
uses a flexible relocation-invariant fingerprint.

---

## Leads to follow

1. **Is there a single relocatable JO engine?** The scatter of load addresses
   ($1000, $2000, $3000, $4000, $c000, $e000, $f000) is very unusual for a
   tracker. Either: (a) JO hand-assembled each tune at a chosen base address
   with his player embedded inline (common for 1988-era demoscene), OR (b) there
   is a relocatable player stub that JO linked at different addresses per
   production context. The sidid match across all addresses favors a consistent
   byte fingerprint (option b or a very consistent coding style).

2. **play=$425c cluster** (Gamlere, Gamlest, Rob_Lam_Fejl): all share the same
   absolute play address despite different init addresses. This is strong evidence
   for ONE specific engine instance linked at a fixed address for these three tunes.
   Good candidates for a "reference" disassembly starting point.

3. **First_Digi (play=$0000)**: The zero play address means the PSID emulator
   won't call a play routine — this is effectively a one-shot init tune (digi
   sample). Its sidid classification as Vibrants/JO suggests the digi mechanism
   is also JO's own. Worth special handling if migrating.

4. **Grid.sid (unclassified, play=$1000)**: same play address as cluster A but
   not fingerprint-matched. May be a borrowed engine (another scener's player)
   or a heavily modified JO engine. Low priority.

5. **High-memory tunes ($e000–$f000)**: Sex_n_Crime_5/10, Soporific, Airwolf,
   Megabad etc. load into ROM-shadowed pages. Verify they use `$01` banking
   manipulations before any migration attempt. `Soporific` (init=$efff) and
   `Sex_n_Crime_5` (init=$efff) follow the $0fff trampoline pattern, suggesting
   the same engine used in Cluster A, just relocated to $F000.

6. **play BEFORE init in address space** (Sex_n_Crime_10: play=$f000,
   init=$f003; Turn_It: play=$f000, init=$f009; A_r_cade_Sprint: play=$3000,
   init=$3003): init+3 = play → init is a 3-byte JSR to the play routine or
   similar minimal wrapper. Very common JO pattern.

7. **CSDb / online research needed**: No local HVSC docs describe JO's player
   internals. CSDb likely has Amok demo releases with source/discussion. The
   `research-player` skill should be run targeting "Vibrants JO Amok demoscene
   C64 music player" to pull CSDb release pages.

8. **Temporal evolution**: Earliest tunes (1988: Genesis Project era) use
   Cluster A ($1000) and Cluster D ($4000) addresses. Later tunes (1989-90:
   Amok era) show more variety. The 1990 tunes (Turn_It, Lame_Part) use
   non-standard layouts — possible engine maturation or guest engines.

9. **Confirmed non-JO engines in directory**: Multi_Move = FutureComposer (already
   migrated), JO_goes_Myth = MoN/Bjerregaard (Johannes Bjerregaard). These
   should remain excluded from any Vibrants/JO migration.
