---
source_url: file:hvsc84.db (local HVSC #84 database)
fetched_via: direct
fetch_date: 2026-06-15
reliability: primary
---

# Ariston HVSC Corpus Analysis

Data extracted from `hvsc84.db` (read-only). All 147 SIDs classified as engine="Ariston".

## Key Structural Observations

### Load Address
- ALL 147 Ariston SIDs have `load_addr = $0000`
- This means the PSID header does not specify a fixed load address — the binary loads to whatever address was saved from
- Ariston is a **relocatable player** embedded in game binaries, not a fixed-address engine
- Each game rips to a different memory region

### Classic Crabtree Pattern: play+3 = init
- 32 SIDs (most Crabtree + some others) show `init_addr = play_addr + 3`
- The first 3 bytes at the play entry are likely a jump instruction (JMP) that skips to the play routine
- The init entry lands 3 bytes later at the actual initialization code
- OR: the 3-byte region is the player's init entry point, and play=$X000 is the player IRQ handler

### Multi-subtune Support
- 65 of 147 Ariston SIDs (44%) have multiple subtunes
- Maximum: Wilson_Mixer.sid — **48 subtunes** (huge)
- Common: 5–9 subtunes for game compilations
- Subtuning via init parameter (accumulator value at PSID init call)

### Play Address Patterns
- Many Beben SIDs have `play_addr+0x01` or `play_addr+0x0B` offset from start of code
- No universal fixed-offset player — each SID was independently assembled/relocated

## Full Corpus Path List

### Ian W. Crabtree (20 SIDs, engine=Ariston)
```
MUSICIANS/C/Crabtree_Ian/Angel_Meadows.sid           init=$1003 play=$1000
MUSICIANS/C/Crabtree_Ian/Blackout_tune_3.sid         init=$1003 play=$1000
MUSICIANS/C/Crabtree_Ian/Christmas_Show.sid          init=$0856 play=$0853
MUSICIANS/C/Crabtree_Ian/Crabby_Music_Demo_3.sid     init=$2420 play=$1160 (7 subtunes)
MUSICIANS/C/Crabtree_Ian/Damnation_Driveway.sid      init=$2003 play=$2000
MUSICIANS/C/Crabtree_Ian/Dudges_Demo.sid             init=$B003 play=$B000
MUSICIANS/C/Crabtree_Ian/Frantic.sid                 init=$7080 play=$7003 (16 subtunes)
MUSICIANS/C/Crabtree_Ian/Going_Home.sid              init=$6003 play=$6000
MUSICIANS/C/Crabtree_Ian/Going_Home_II.sid           init=$7003 play=$7000
MUSICIANS/C/Crabtree_Ian/Going_Home_III.sid          init=$3003 play=$3000
MUSICIANS/C/Crabtree_Ian/Kraxxon_Zone.sid            init=$4003 play=$4000
MUSICIANS/C/Crabtree_Ian/Midnight_Shiver.sid         init=$3003 play=$3000
MUSICIANS/C/Crabtree_Ian/Moun.sid                    init=$5003 play=$5000
MUSICIANS/C/Crabtree_Ian/Outrun.sid                  init=$2003 play=$2000
MUSICIANS/C/Crabtree_Ian/Plastic_Butter.sid          init=$1003 play=$1000
MUSICIANS/C/Crabtree_Ian/Quantarallax.sid            init=$0832 play=$0854
MUSICIANS/C/Crabtree_Ian/Quick_Demo.sid              init=$16E9 play=$0854
MUSICIANS/C/Crabtree_Ian/Technicolour_1.sid          init=$6003 play=$6000
MUSICIANS/C/Crabtree_Ian/Total_Eclipse.sid           init=$084F play=$0854
MUSICIANS/C/Crabtree_Ian/Warhawk_Music.sid           init=$084F play=$0854
MUSICIANS/C/Crabtree_Ian/Youre_Next.sid              init=$20B7 play=$1000
```
**Note (VGMPF):** Crabtree's tuning is "433.5 Hz on PAL, 450 Hz on NTSC" and "sounds the same on every SID chip."
**Note (VGMPF):** Crabtree primarily used The Ariston Music Editor; used Beben's assembly version for Summer Olympiad.

### Wally Beben Ariston SIDs (28 SIDs, engine=Ariston in HVSC)
```
MUSICIANS/B/Beben_Wally/Aaargh.sid                   init=$68EE play=$68F8
MUSICIANS/B/Beben_Wally/Airborne.sid                 init=$6C28 play=$6005
MUSICIANS/B/Beben_Wally/Dark_Side.sid                init=$1628 play=$0901
MUSICIANS/B/Beben_Wally/Face_It.sid                  init=$9FA0 play=$0000
MUSICIANS/B/Beben_Wally/Hammerfist.sid               init=$0D54 play=$0D48 (7 subtunes)
MUSICIANS/B/Beben_Wally/I-Xera.sid                   init=$AD14 play=$A005
MUSICIANS/B/Beben_Wally/Inside_Outing.sid            init=$CBA5 play=$C101
MUSICIANS/B/Beben_Wally/Knight_Games_II.sid          init=$3680 play=$2811
MUSICIANS/B/Beben_Wally/March_of_Time.sid            init=$7FFA play=$8002
MUSICIANS/B/Beben_Wally/Moonlight_Sonata.sid         init=$0856 play=$0853
MUSICIANS/B/Beben_Wally/Moonshadow.sid               init=$B3F8 play=$B41C
MUSICIANS/B/Beben_Wally/Octapolis.sid                init=$CB50 play=$C001
MUSICIANS/B/Beben_Wally/Oops.sid                     init=$7C6D play=$6E01
MUSICIANS/B/Beben_Wally/Popped_Corn.sid              init=$8C00 play=$0000
MUSICIANS/B/Beben_Wally/R_I_S_K.sid                  init=$CFC0 play=$C343
MUSICIANS/B/Beben_Wally/Ransack.sid                  init=$EB84 play=$E001
MUSICIANS/B/Beben_Wally/Roadwars.sid                 init=$A720 play=$A001
MUSICIANS/B/Beben_Wally/Scuba_Kidz.sid               init=$CD00 play=$0000
MUSICIANS/B/Beben_Wally/Shockwave.sid                init=$8000 play=$800B (9 subtunes)
MUSICIANS/B/Beben_Wally/Starforce_Fighter.sid        init=$7E02 play=$6C05
MUSICIANS/B/Beben_Wally/Starslayer.sid               init=$A1F9 play=$A201
MUSICIANS/B/Beben_Wally/Summer_Olympiad.sid          init=$FD18 play=$E810 (7 subtunes)
MUSICIANS/B/Beben_Wally/Superman-Man_of_Steel.sid    init=$F058 play=$E000
MUSICIANS/B/Beben_Wally/Superman-Man_of_Steel_V2.sid init=$EF48 play=$E000
MUSICIANS/B/Beben_Wally/Tetris.sid                   init=$7440 play=$0000
MUSICIANS/B/Beben_Wally/Total_Eclipse.sid            init=$1508 play=$0901
MUSICIANS/B/Beben_Wally/Vector_Ball.sid              init=$BB50 play=$B001
MUSICIANS/B/Beben_Wally/Viking.sid                   init=$9C00 play=$0000
MUSICIANS/B/Beben_Wally/Winter_Events.sid            init=$FF03 play=$E001 (7 subtunes)
MUSICIANS/B/Beben_Wally/Winter_Olympiad_88_preview.sid init=$5E60 play=$5EDF
```

### Steve Barrett (21 SIDs) — partial list
Bigfoot, Blue_Meanies, Egg_in_Space, European_5-A-Side, Fast_Food, Fraeulein_Kinski, Frosty_the_Snowman, Galactic_Games_1/2/3, Grand_Prix_Simulator_II, Hyber_Blob, Knightmare, Magicland_Dizzy, Mig-29_Soviet_Fighter, Monopoly_Deluxe, Monte_Carlo_Casino, Professional_Ski_Simulator, Pulse_Warrior, Pulsoid, SAS_Combat_Simulator, Super_Hang-On, Superhero, Tarzan_Goes_Ape, Tilt, Trojan_Warrior, Ultimate_Combat_Mission

### Mark Wilson (19 SIDs)
A_Mutant_Xmas_II, Arbitrator, Blue_Monday, Device_for_Alien_Destruction, Galdregon's_Domain, Game_Over_Tune, Hawkeye_Remix, Mark_Wilson_Demo_Disk_4_Menu, Obliterator_Remix, Rendezvous, Secrets_1988, Shanghai_Warriors, Shark, Shylok, Stark_Realities, Summer_Day, Taskforce, Wilson_Mixer (48 subtunes!), Winter_Day

### Other Ariston Composers
- **Sandra Park (Perdita)**: 10 SIDs (Beyond_the_Stars, Carnival, Cradlesong, Demo, I_Just_Go_to_Pieces, Im_Sorry, Jaywalker, Miss_You, Moving, Sleighride)
- **Neil Scales (Neil)**: 10 SIDs (Ariston Design group)
- **Matt Gray**: 4 SIDs (Fruit_Machine_Simulator, Mean_Streak_Loader, Quedex [9 subtunes], Mean_Streak_v1)
- **Allister Brimble**: 4 SIDs (Mean_Machine, Panic_Dizzy, Prince_Clumsy, Slightly_Magic)
- **Jonathan Dunn**: 2 SIDs (Matchday_II, Subterranea)
- **Barry Leitch**: 2 SIDs (Captain_Courageous, Marauder [6 subtunes])
- **Denis Harris (Moley)**: 2 SIDs (A_Short_One, Final_Red) — Ariston Design group
- **Lyndon Sharp**: 3 SIDs (Fruit_Machine_Simulator_2, Skyhigh_Stuntman, Wizard_Willy)
- **Dennis Lindroos (Deadman)**: 1 SID — Colossus_Chess_Atari_ST.sid (ST port!)
