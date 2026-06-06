# Canary SID Picker — Top 50 Engines

## Progress (as of 2026-06-06)

| Status | Engines |
|---|---|
| Byte-exact canary | 2 of 50 — #4 MoN/FutureComposer (Hawkeye + Cybernoid_II), #24 Rob_Hubbard (Human_Race) |
| In progress | 1 — #4 MoN/FutureComposer Adrenalin (disasm seeded, FCConfig pending; see `pipelines/future_composer/adrenalin/RE_NOTES.md`) |
| Not started | 47 |

The Hubbard '85 + Companion + Jay_Derrett families have many more
verified subtunes (160+ across `tools/regression.py`), but only
`Human_Race.sid` overlaps with the canary picker's row choices for
engine #24 — the picker selected the 5 longest Hubbard tunes, and our
migration corpus is feature-driven rather than length-driven. The
other migrated engines (Berry_Vic, Clever_Music, Henrys_House, etc.)
are companion/Bowden-era niche engines below the top-50 cutoff.

## What this is

A breadth-first selection list for migrating one canary SID per engine
family in the HVSC top 50. The goal is structural coverage — exercise the
feature space of as many distinct engine shapes as possible — to inform
the deferred composer-unification work (`docs/refactor_1_remaining.md`).

## How candidates were chosen

* **34 engines with curated coverage:** candidates drawn from Cujo's
  curated list at `trondal.com/sid` (a quality filter — popular/competent
  composers). Ranked by songlength descending (long songs exercise more
  code paths).
* **16 engines without curated coverage:** candidates drawn from the
  engine's most prolific composers in HVSC (data-driven proxy for
  "best-known user"). Same length ranking.

Each engine's table lists up to 5 candidates. The first row is the
recommendation; alternatives follow. Override as you prefer.

## How to use this table

* `[ ] selected` — check when you pick this SID as the canary
* `[ ] migrated` — check when extract + verify byte-exact
* Strike through rejected candidates with `~~...~~` markdown
* When all 50 canaries land, the corpus is ~50–250 SIDs (50 baseline, more
  if any engine needs ≥2 canaries to cover its feature space) spanning ~84%
  of HVSC by volume — the input to the composer-unification work.

## Open follow-up

* **No column for "has digi" yet** — digi detection needs a `siddump` audit
  pass. Run it lazily per engine when the canary is selected; if the
  canary has no digi but the engine supports it, add a second SID.
* **Fallback engines list `<?>` if no top composers identified** — some
  engines have author column NULL for most SIDs. For those, fall back to
  picking by songlength alone.

---

## 1. DMC (10660 SIDs)

**Source:** curated (24 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/B/Bakewell_Dwayne/Freezing_12.sid` | Dwayne Bakewell (DJB) | 1 | 4:52 |
| [ ] | [ ] | `MUSICIANS/C/CreaMD/Critical_Grid_Voltage.sid` | Roman Chlebec (CreaMD) | 1 | 4:36 |
| [ ] | [ ] | `MUSICIANS/E/Ed/Rotar_Nut_Pop.sid` | Eddie Svärd (Ed) | 1 | 4:13 |
| [ ] | [ ] | `MUSICIANS/D/Daf/Extasy.sid` | Michal Relkowski (Daf) | 1 | 4:04 |
| [ ] | [ ] | `DEMOS/A-F/Emulating_Vinkuna.sid` | Timo Laitinen (Elektro) | 1 | 3:51 |

## 2. GoatTracker_V2.x (7311 SIDs)

**Source:** curated (86 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/C/Cross_Saul/Argus.sid` | Saul Cross | 5 | 14:39 |
| [ ] | [ ] | `MUSICIANS/E/Encore/Soulless.sid` | Mikkel Hastrup (encore) | 6 | 13:01 |
| [ ] | [ ] | `MUSICIANS/L/Linus/Across_Tundras.sid` | Sascha Zeidler (Linus) | 1 | 12:04 |
| [ ] | [ ] | `MUSICIANS/L/Linus/Darkness.sid` | Sascha Zeidler (Linus) | 6 | 7:35 |
| [ ] | [ ] | `MUSICIANS/H/Hoffmann_Michal/Amaurote_Isometric.sid` | Michal Hoffmann (Hate Bush) | 9 | 6:26 |

## 3. Music_Assembler (6351 SIDs)

**Source:** curated (11 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/R/Rage/Kalle_Kloakk_part_8.sid` | Anders Rodahl (Rage) | 1 | 8:06 |
| [ ] | [ ] | `MUSICIANS/K/Kleinert_Tim/Arcade_Intro.sid` | Tim Kleinert | 1 | 6:21 |
| [ ] | [ ] | `MUSICIANS/0-9/4-Mat/Sub.sid` | Matt Simmonds (4-Mat) | 2 | 5:48 |
| [ ] | [ ] | `MUSICIANS/H/Harmony_Productions/War_at_33.sid` | Ludovic Llorca (Harmony Prods) | 1 | 4:58 |
| [ ] | [ ] | `MUSICIANS/R/Remorhaz/Implosion.sid` | Martin Edwards (Remorhaz) | 1 | 4:25 |

## 4. MoN/FutureComposer (4024 SIDs)

**Source:** curated (14 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [x] | [x] | `MUSICIANS/T/Tel_Jeroen/Hawkeye.sid` | Jeroen Tel | 12 | 18:52 |
| [ ] | [ ] | `MUSICIANS/T/Tel_Jeroen/Eliminator.sid` | Jeroen Tel | 4 | 11:07 |
| [x] | [ ] | `MUSICIANS/H/HeatWave/Adrenalin.sid` | Marvin Severijns & M. de Bree | 4 | 9:25 |
| [ ] | [ ] | `MUSICIANS/T/Tel_Jeroen/Tomcat.sid` | Jeroen Tel | 3 | 8:12 |
| [x] | [x] | `MUSICIANS/T/Tel_Jeroen/Cybernoid_II.sid` | Jeroen Tel | 2 | 5:54 |

## 5. Soundmonitor (3625 SIDs)

**Source:** curated (1 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/D/DRAX/Chukky.sid` | Thomas Mogensen (DRAX) | 1 | 1:43 |

## 6. JCH_NewPlayer (3611 SIDs)

**Source:** curated (50 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/J/JCH/Hawaii.sid` | JCH & Morten Kristensen (MSK) | 2 | 10:33 |
| [ ] | [ ] | `MUSICIANS/A/Agemixer/Freestyler.sid` | Ari Yliaho (Agemixer) | 1 | 4:46 |
| [ ] | [ ] | `MUSICIANS/D/Danko_Tomas/Planetary.sid` | Tomas Danko | 1 | 4:34 |
| [ ] | [ ] | `MUSICIANS/J/JCH/Chordian.sid` | Jens-Christian Huus | 1 | 4:06 |
| [ ] | [ ] | `MUSICIANS/G/Goto80/For_News_Press.sid` | Anders Carlsson (Goto80) | 1 | 4:03 |

## 7. GoatTracker_V1.x (1359 SIDs)

**Source:** curated (18 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/H/Holt_Hein/Synth_X_Error.sid` | Hein Holt (Hein Design) | 1 | 6:28 |
| [ ] | [ ] | `MUSICIANS/H/Holt_Hein/Cantaloupe.sid` | Hein Holt (Hein Design) | 1 | 5:31 |
| [ ] | [ ] | `MUSICIANS/H/Holt_Hein/Creepy_Psychomix.sid` | Hein Holt (Hein Design) | 1 | 5:01 |
| [ ] | [ ] | `MUSICIANS/H/Holt_Hein/Romans_Conquer_the_Discofloor.sid` | Hein Holt | 1 | 4:45 |
| [ ] | [ ] | `MUSICIANS/H/Holt_Hein/Scott-Land_6581.sid` | Hein Holt (Hein Design) | 1 | 4:42 |

## 8. HardTrack_Composer (1170 SIDs)

**Source:** curated (5 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/B/Bzyk/Psychologue.sid` | Piotr Baczkiewicz (Bzyk) | 1 | 2:11 |
| [ ] | [ ] | `MUSICIANS/B/Bzyk/Lovely_Time.sid` | Piotr Baczkiewicz (Bzyk) | 1 | 1:40 |
| [ ] | [ ] | `MUSICIANS/B/Bzyk/Epidemic_1.sid` | Piotr Baczkiewicz (Bzyk) | 1 | 1:38 |
| [ ] | [ ] | `MUSICIANS/S/Shogoon/Astoria_7_tune_2.sid` | Wojciech Radziejewski (Shogoon) | 1 | 0:58 |
| [ ] | [ ] | `MUSICIANS/B/Bzyk/Isolation.sid` | Piotr Baczkiewicz (Bzyk) | 1 | 0:44 |

## 9. Hermit/SidWizard_V1.x (1048 SIDs)

**Source:** curated (2 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/C/C0zmo/Boulder_Dash_Remake.sid` | Markus Jentsch (c0zmo) | 1 | 2:25 |
| [ ] | [ ] | `MUSICIANS/D/DAM/Flight_One.sid` | David Major (DAM) | 1 | 2:24 |

## 10. Master_Composer (1019 SIDs)

**Source:** fallback (no curated; top composers: <?> (498), Graham Marsh (BOGG) (32), Al Weseman (32))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `GAMES/M-R/Omega-Planete_Invisible.sid` | <?> | 1 | 17:14 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Master_Composer/Chiaro_di_Luna.sid` | <?> | 1 | 11:39 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Master_Composer/Adios_Amor.sid` | <?> | 1 | 10:26 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Master_Composer/When_I_Fall.sid` | <?> | 1 | 9:09 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Master_Composer/Carrier_Force.sid` | <?> | 1 | 8:53 |

## 11. Geir_Tjelta/SIDDuzz'It (934 SIDs)

**Source:** curated (38 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/T/Tjelta_Geir/Artillery.sid` | Geir Tjelta | 3 | 10:01 |
| [ ] | [ ] | `MUSICIANS/B/Blues_Muz/Olledunk.sid` | G. R. Gallefoss & K. Røstøen | 1 | 6:12 |
| [ ] | [ ] | `MUSICIANS/D/Devilock/Frost_Point.sid` | Peter Siekmann (Devilock) | 1 | 5:46 |
| [ ] | [ ] | `MUSICIANS/B/Blues_Muz/Nibbleman_plus.sid` | G. R. Gallefoss & K. Røstøen | 1 | 4:25 |
| [ ] | [ ] | `MUSICIANS/D/Devilock/Confidence.sid` | Peter Siekmann (Devilock) | 1 | 4:11 |

## 12. SoedeSoft (929 SIDs)

**Source:** curated (2 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/D/Doussis_Stello/1942_Highscore-Tune.sid` | Stello Doussis | 1 | 2:34 |
| [ ] | [ ] | `MUSICIANS/D/Danko_Tomas/Luft_Med_Isbit.sid` | Tomas Danko | 1 | 1:09 |

## 13. RoMuzak_V6.x (569 SIDs)

**Source:** curated (2 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `GAMES/M-R/Reaction.sid` | Clemens Langowski | 4 | 5:38 |
| [ ] | [ ] | `MUSICIANS/S/Sony/Collection_1_menu.sid` | Markus Raab (Mr. Rap) | 1 | 0:46 |

## 14. Digitalizer_V2.x (542 SIDs)

**Source:** curated (34 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/B/Blues_Muz/Nordboe_Kjell/A_New_Life.sid` | Kjell Nordbø | 20 | 40:04 |
| [ ] | [ ] | `MUSICIANS/B/Blues_Muz/Nordboe_Kjell/Naked_and_Lost.sid` | Kjell Nordbø | 1 | 5:51 |
| [ ] | [ ] | `MUSICIANS/B/Blues_Muz/Nordboe_Kjell/Died.sid` | Kjell Nordbø | 1 | 4:21 |
| [ ] | [ ] | `MUSICIANS/B/Blues_Muz/Roestoeen_Kristian/Bravo.sid` | Kristian Røstøen | 1 | 3:25 |
| [ ] | [ ] | `MUSICIANS/B/Blues_Muz/Nordboe_Kjell/Play_with_Me.sid` | Kjell Nordbø | 1 | 3:00 |

## 15. Basic_Program (486 SIDs)

**Source:** fallback (no curated; top composers: <?> (120), Alan Bond (62), Joey Latimer (22))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/L/Latimer_Joey/Arcade_Alley_BASIC.sid` | Joey Latimer | 1 | 5:18 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Bagpipes_BASIC.sid` | <?> | 1 | 5:18 |
| [ ] | [ ] | `DEMOS/Commodore/Gigue_in_G_Minor_G_F_Handel_BASIC.sid` | <?> | 1 | 4:53 |
| [ ] | [ ] | `MUSICIANS/B/Bond_Alan/Cascading_BASIC.sid` | Alan Bond | 1 | 4:20 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Bach_BASIC.sid` | <?> | 1 | 3:53 |

## 16. GMC/Superiors (446 SIDs)

**Source:** curated (2 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/B/Bleed_Into_One/Law_of_Knotting.sid` | Rene Griebel (Bleed Into One) | 1 | 4:46 |
| [ ] | [ ] | `MUSICIANS/A/Akadem/Titanic.sid` | Andrzej Kucharski (Akadem) | 1 | 1:40 |

## 17. X-Ample (380 SIDs)

**Source:** curated (3 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/D/Detert_Thomas/Gordian_Tomb.sid` | Thomas & Michael Detert | 2 | 34:21 |
| [ ] | [ ] | `MUSICIANS/D/Detert_Thomas/Stone_Age.sid` | Thomas Detert | 8 | 17:22 |
| [ ] | [ ] | `MUSICIANS/A/A-Man/Mysterious_Worlds_level_2.sid` | Steven Diemer (A-Man) | 1 | 3:16 |

## 18. SidFactory_II/Laxity (377 SIDs)

**Source:** curated (3 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/L/Laxity/Stinsens_Last_Night_of_89.sid` | Thomas E. Petersen (Laxity) | 1 | 3:37 |
| [ ] | [ ] | `MUSICIANS/T/TLF/64_Carat_Kylie_Biege.sid` | Chris Lightfoot (TLF) | 1 | 2:49 |
| [ ] | [ ] | `MUSICIANS/L/Laxity/1983_Sauna_Tango.sid` | Laxity & Shogoon | 1 | 2:45 |

## 19. Laxity_NewPlayer_V21 (313 SIDs)

**Source:** curated (20 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/D/DRAX/Star_Flake.sid` | Thomas Mogensen (DRAX) | 1 | 4:47 |
| [ ] | [ ] | `MUSICIANS/D/DRAX/Hypersensational.sid` | Thomas Mogensen (DRAX) | 1 | 4:27 |
| [ ] | [ ] | `MUSICIANS/D/DRAX/Expectations.sid` | Thomas Mogensen (DRAX) | 1 | 3:14 |
| [ ] | [ ] | `MUSICIANS/D/DRAX/Capripholian_Waltz.sid` | Thomas Mogensen (DRAX) | 1 | 3:11 |
| [ ] | [ ] | `MUSICIANS/D/DRAX/Spunk.sid` | Thomas Mogensen (DRAX) | 1 | 2:57 |

## 20. Loadstar_SongSmith (308 SIDs)

**Source:** fallback (no curated; top composers: Dave Marquis (126), Alan Beggerow (48), Debby Cruz (45))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/M/Marquis_Dave/Moonlight_Sonata_A.sid` | Dave Marquis | 1 | 7:04 |
| [ ] | [ ] | `MUSICIANS/M/Marquis_Dave/Sarabande_Minuet_and_Trio.sid` | Dave Marquis | 1 | 5:19 |
| [ ] | [ ] | `MUSICIANS/M/Marquis_Dave/Air_on_the_G_String.sid` | Dave Marquis | 1 | 5:08 |
| [ ] | [ ] | `MUSICIANS/M/Marquis_Dave/Four_Seasons-Autumn.sid` | Dave Marquis | 1 | 4:39 |
| [ ] | [ ] | `MUSICIANS/M/Marquis_Dave/Four_Seasons-Summer.sid` | Dave Marquis | 1 | 4:31 |

## 21. CheeseCutter_2.x (302 SIDs)

**Source:** curated (12 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/L/LMan/Age_We_Aceeed_SCC_Extended.sid` | Markus Klein (LMan) | 1 | 5:33 |
| [ ] | [ ] | `MUSICIANS/L/LMan/Age_We_Aceeed.sid` | Markus Klein (LMan) | 1 | 5:01 |
| [ ] | [ ] | `MUSICIANS/B/Bayliss_Richard/Border_Blast_3.sid` | Richard Bayliss | 1 | 4:21 |
| [ ] | [ ] | `MUSICIANS/S/Scarzix/Back_2_Basic.sid` | Carsten Berggreen (Scarzix) | 1 | 4:16 |
| [ ] | [ ] | `MUSICIANS/L/LMan/Devoid_of.sid` | Markus Klein (LMan) | 1 | 3:58 |

## 22. Electrosound (297 SIDs)

**Source:** fallback (no curated; top composers: Barry Leitch (The Jackal) (60), Jonathan Dunn (Choroid) (26), John Stormont (17))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/L/Leitch_Barry/Sophistry_war.sid` | Barry Leitch (The Jackal) | 5 | 14:19 |
| [ ] | [ ] | `MUSICIANS/D/Dunn_Jonathan/Rebellion.sid` | Jonathan Dunn (Choroid) | 1 | 10:16 |
| [ ] | [ ] | `MUSICIANS/L/Leitch_Barry/A-ha_Soundtrack.sid` | Barry Leitch (The Jackal) | 3 | 8:42 |
| [ ] | [ ] | `MUSICIANS/L/Leitch_Barry/F_R_I_D_G_E.sid` | Barry Leitch (The Jackal) | 1 | 8:41 |
| [ ] | [ ] | `MUSICIANS/D/Dunn_Jonathan/Entry_Three_Entry_Four.sid` | Jonathan Dunn (Choroid) | 2 | 8:34 |

## 23. Ubik's_Musik (288 SIDs)

**Source:** curated (3 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/S/Stormont_John/Snowball.sid` | John Stormont | 2 | 4:35 |
| [ ] | [ ] | `MUSICIANS/S/Stormont_John/Strollin.sid` | John Stormont | 1 | 3:57 |
| [ ] | [ ] | `MUSICIANS/H/Higgins_Neil/Sample_Music.sid` | Neil Higgins (NM156) | 5 | 3:20 |

## 24. Rob_Hubbard (287 SIDs)

**Source:** curated (30 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/H/Hubbard_Rob/Delta.sid` | Rob Hubbard | 13 | 15:32 |
| [ ] | [ ] | `MUSICIANS/H/Hubbard_Rob/Gremlins.sid` | Rob Hubbard | 26 | 14:10 |
| [ ] | [ ] | `MUSICIANS/H/Hubbard_Rob/Gerry_the_Germ.sid` | Rob Hubbard | 23 | 12:55 |
| [ ] | [ ] | `MUSICIANS/H/Hubbard_Rob/International_Karate.sid` | Rob Hubbard | 1 | 10:45 |
| [x] | [x] | `MUSICIANS/H/Hubbard_Rob/Human_Race.sid` | Rob Hubbard | 5 | 9:48 |

## 25. TFX (269 SIDs)

**Source:** fallback (no curated; top composers: David Cwik (Sad) (108), Petr Chlud (PCH) (52), Jaymz Julian (A Life in Hell) (45))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/S/Sad/Dream.sid` | David Cwik (Sad) | 1 | 9:21 |
| [ ] | [ ] | `MUSICIANS/S/Sad/Cruel_Rave.sid` | David Cwik (Sad) | 1 | 8:48 |
| [ ] | [ ] | `MUSICIANS/S/Sad/Kill_Him.sid` | David Cwik (Sad) | 1 | 7:34 |
| [ ] | [ ] | `MUSICIANS/J/Julian_Jaymz/Rekonstruct.sid` | Jaymz Julian (A Life in Hell) | 1 | 7:30 |
| [ ] | [ ] | `MUSICIANS/J/Julian_Jaymz/Fishmagic.sid` | Jaymz Julian (A Life in Hell) | 2 | 6:44 |

## 26. SidTracker64 (259 SIDs)

**Source:** curated (1 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/P/Page_Jason/Eighth.sid` | Jason Page | 1 | 7:57 |

## 27. AMP (246 SIDs)

**Source:** fallback (no curated; top composers: Nantco Bakker (45), Tobias Erbsland (Dr. Zoom) (27), Jan Krolzig (18))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/K/Krolzig_Jan/Cheeky_Twins_2.sid` | Jan Krolzig | 10 | 13:34 |
| [ ] | [ ] | `MUSICIANS/D/Dr_Zoom/Tec_Groove.sid` | Tobias Erbsland (Dr. Zoom) | 1 | 7:49 |
| [ ] | [ ] | `MUSICIANS/K/Krolzig_Jan/Cheeky_Twins.sid` | Jan Krolzig | 7 | 7:46 |
| [ ] | [ ] | `MUSICIANS/K/Krolzig_Jan/Cheeky_Twins_3_preview.sid` | Jan Krolzig | 4 | 6:30 |
| [ ] | [ ] | `MUSICIANS/D/Dr_Zoom/Dreaming.sid` | Tobias Erbsland (Dr. Zoom) | 1 | 6:05 |

## 28. DefleMask_v12 (240 SIDs)

**Source:** curated (4 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/D/DaJoshy/Joshys_First_Burfday.sid` | Jaden Houghton (Disk Joshy) | 1 | 1:26 |
| [ ] | [ ] | `MUSICIANS/D/Dya/Mother_Funk_Signal.sid` | Aaron Hickman (Dya) | 1 | 1:21 |
| [ ] | [ ] | `DEMOS/S-Z/Sunflowers.sid` | None Petrovich (mk7) | 1 | 0:53 |
| [ ] | [ ] | `MUSICIANS/S/Sinc-X/Cool_Battle.sid` | Justin Wamback (Sinc-X) | 1 | 0:31 |

## 29. 20CC (209 SIDs)

**Source:** curated (2 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/O/Ouwehand_Reyn/Last_Ninja_3.sid` | Reyn Ouwehand | 10 | 27:12 |
| [ ] | [ ] | `MUSICIANS/0-9/20CC/van_Santen_Edwin/Strike_It_Up.sid` | Edwin van Santen | 1 | 4:06 |

## 30. Cyberlogic_SoundStudio (196 SIDs)

**Source:** fallback (no curated; top composers: Sascha Nagie (celticdesign) (118), Frank Schanzenbächer (X-Radical) (28), Oliver Klee (Odi) (24))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/N/Nagie_Sascha/Another_Cosmic_Ride.sid` | Sascha Nagie (celticdesign) | 1 | 12:36 |
| [ ] | [ ] | `MUSICIANS/X/X-Radical/Quak_Quak.sid` | Frank Schanzenbächer (X-Radical) | 1 | 8:49 |
| [ ] | [ ] | `MUSICIANS/X/X-Radical/Techno_No_1.sid` | Frank Schanzenbächer (X-Radical) | 1 | 8:03 |
| [ ] | [ ] | `MUSICIANS/N/Nagie_Sascha/Phantom_of_the_Blasteroids.sid` | Sascha Nagie (celticdesign) | 4 | 8:02 |
| [ ] | [ ] | `MUSICIANS/N/Nagie_Sascha/Visions_plus_Tales.sid` | Sascha Nagie (celticdesign) | 1 | 7:40 |

## 31. EMS/Odie (196 SIDs)

**Source:** fallback (no curated; top composers: Andrew Fisher (Merman) (99), Sean Connolly (Odie) (35), Sean Connolly (23))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/C/Connolly_Sean/That_Old_Magic.sid` | Sean Connolly (Odie) | 1 | 10:37 |
| [ ] | [ ] | `MUSICIANS/C/Connolly_Sean/Hammer_Down.sid` | Sean Connolly | 12 | 9:26 |
| [ ] | [ ] | `MUSICIANS/M/Merman/Cute_Game_Soundtrack.sid` | Andrew Fisher (Merman) | 5 | 8:39 |
| [ ] | [ ] | `MUSICIANS/C/Connolly_Sean/Euro_Soccer.sid` | Sean Connolly | 6 | 7:04 |
| [ ] | [ ] | `MUSICIANS/C/Connolly_Sean/Brilliant_Maze.sid` | Sean Connolly | 8 | 6:59 |

## 32. Jeff (192 SIDs)

**Source:** curated (9 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/J/Jeff/Zarathus.sid` | Søren Lund (Jeff) | 1 | 3:03 |
| [ ] | [ ] | `MUSICIANS/J/Jeff/Ode_to_C64.sid` | Søren Lund (Jeff) | 1 | 2:51 |
| [ ] | [ ] | `MUSICIANS/J/Jeff/Jeroen_Tel_Style.sid` | Søren Lund (Jeff) | 1 | 2:50 |
| [ ] | [ ] | `MUSICIANS/J/Jeff/Messy_One.sid` | Søren Lund (Jeff) | 1 | 2:34 |
| [ ] | [ ] | `MUSICIANS/J/Jeff/House.sid` | Søren Lund (Jeff) | 1 | 1:57 |

## 33. John_Player (183 SIDs)

**Source:** curated (4 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/E/Eeben_Aleksi/Greenrunner.sid` | Aleksi Eeben | 11 | 8:00 |
| [ ] | [ ] | `MUSICIANS/E/Eeben_Aleksi/One_for_Reed.sid` | Aleksi Eeben | 1 | 1:35 |
| [ ] | [ ] | `MUSICIANS/E/Eeben_Aleksi/Music_Test_3.sid` | Aleksi Eeben | 1 | 1:25 |
| [ ] | [ ] | `MUSICIANS/E/Eeben_Aleksi/Arabia.sid` | Aleksi Eeben | 1 | 0:39 |

## 34. MusicShop (182 SIDs)

**Source:** fallback (no curated; top composers: <?> (121), Don Williams <?> (28), Mehdi Safavy (20))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/W/Williams_Don/Canon_in_D.sid` | Don Williams <?> | 1 | 6:25 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Music_Shop/Axel_F.sid` | <?> | 1 | 5:32 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Music_Shop/Dolannes_Melodie.sid` | <?> | 1 | 4:36 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Music_Shop/Romance.sid` | <?> | 1 | 4:33 |
| [ ] | [ ] | `DEMOS/UNKNOWN/Music_Shop/Banks_of_the_Ohio.sid` | <?> | 1 | 4:31 |

## 35. Vibrants/Laxity (179 SIDs)

**Source:** curated (2 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/L/Laxity/Alibi.sid` | Thomas E. Petersen (Laxity) | 1 | 3:16 |
| [ ] | [ ] | `MUSICIANS/L/Laxity/Squamp.sid` | Thomas E. Petersen (Laxity) | 1 | 1:51 |

## 36. OdinTracker (159 SIDs)

**Source:** fallback (no curated; top composers: Otto Järvinen (SounDemoN) (50), Michal Hoffmann (Smalltown Boy) (22), Factor6 (16))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/S/SounDemoN/Tomhet.sid` | Otto Järvinen (SounDemoN) | 2 | 27:44 |
| [ ] | [ ] | `MUSICIANS/S/SounDemoN/Martin_Hubbabubba.sid` | Otto Järvinen (SounDemoN) | 2 | 21:50 |
| [ ] | [ ] | `MUSICIANS/S/SounDemoN/Nine_Inch_Ninjas_part_5.sid` | Otto Järvinen (SounDemoN) | 1 | 16:31 |
| [ ] | [ ] | `MUSICIANS/S/SounDemoN/Nine_Inch_Ninjas_part_1.sid` | Otto Järvinen (SounDemoN) | 1 | 16:02 |
| [ ] | [ ] | `MUSICIANS/S/SounDemoN/Nine_Inch_Ninjas_part_4.sid` | Otto Järvinen (SounDemoN) | 1 | 11:46 |

## 37. Ariston (147 SIDs)

**Source:** curated (1 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/B/Brimble_Allister/Mean_Machine.sid` | Allister Brimble | 4 | 2:55 |

## 38. Reflextracker (137 SIDs)

**Source:** fallback (no curated; top composers: Piotr Grabowski (Warlock) (23), Radoslaw Staszak (Data) (13), Jaroslaw Kotlinski (JFK) (12))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/J/JFK/Chaos_Machine.sid` | Jaroslaw Kotlinski (JFK) | 1 | 6:11 |
| [ ] | [ ] | `MUSICIANS/W/Warlock/Xtraterrestrial.sid` | Piotr Grabowski (Warlock) | 1 | 6:02 |
| [ ] | [ ] | `MUSICIANS/W/Warlock/Nostradamus_Version_2.sid` | Piotr Grabowski (Warlock) | 1 | 5:28 |
| [ ] | [ ] | `MUSICIANS/W/Warlock/Energy_Boost.sid` | Piotr Grabowski (Warlock) | 1 | 5:22 |
| [ ] | [ ] | `MUSICIANS/W/Warlock/Cat_for_Dinner.sid` | Piotr Grabowski (Warlock) | 1 | 5:22 |

## 39. MoN/Deenen (135 SIDs)

**Source:** curated (13 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/T/Tel_Jeroen/Rubicon.sid` | Jeroen Tel & Reyn Ouwehand | 11 | 21:03 |
| [ ] | [ ] | `MUSICIANS/T/Tel_Jeroen/Nighthunter.sid` | Jeroen Tel | 6 | 14:24 |
| [ ] | [ ] | `MUSICIANS/T/Tel_Jeroen/Supremacy.sid` | Jeroen Tel | 3 | 7:01 |
| [ ] | [ ] | `MUSICIANS/T/Tel_Jeroen/Gaplus.sid` | Jeroen Tel | 23 | 6:59 |
| [ ] | [ ] | `MUSICIANS/T/Tel_Jeroen/Myth.sid` | Jeroen Tel | 3 | 6:49 |

## 40. CyberTracker_exe (130 SIDs)

**Source:** curated (1 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/F/Fredrik/Feeling.sid` | Fredrik | 1 | 1:19 |

## 41. Vibrants/JO (130 SIDs)

**Source:** curated (2 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/J/JO/Rautaudaw.sid` | Jesper Olsen (JO) | 5 | 7:40 |
| [ ] | [ ] | `MUSICIANS/J/JO/Contex.sid` | Jesper Olsen (JO) | 1 | 0:35 |

## 42. CyberTracker (125 SIDs)

**Source:** curated (1 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/F/Fredrik/Listen_to_the_SID_Baby.sid` | Fredrik | 1 | 2:07 |

## 43. LordsOfSonics/MS (123 SIDs)

**Source:** fallback (no curated; top composers: Jens Blidon (32), Kagan Demir (Babyface) (17), Markus Schneider (13))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/B/Blidon_Jens/Metal_Force.sid` | Jens Blidon | 6 | 23:10 |
| [ ] | [ ] | `MUSICIANS/B/Blidon_Jens/Counter_Force.sid` | Jens Blidon | 6 | 23:09 |
| [ ] | [ ] | `MUSICIANS/S/Schneider_Markus/No_Mercy.sid` | Markus Schneider | 13 | 21:40 |
| [ ] | [ ] | `MUSICIANS/B/Blidon_Jens/American_Express.sid` | Jens Blidon | 6 | 10:53 |
| [ ] | [ ] | `MUSICIANS/S/Schneider_Markus/Timerunner.sid` | Markus Schneider | 3 | 10:39 |

## 44. SidWinder (117 SIDs)

**Source:** curated (4 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/T/Taki/Bastard_tune_2.sid` | Balázs Takács (Taki) | 1 | 5:08 |
| [ ] | [ ] | `MUSICIANS/L/Luca/Crackers_Demo_4.sid` | Luca Carrafiello (Luca) | 3 | 4:00 |
| [ ] | [ ] | `MUSICIANS/L/Luca/Cottoncandy_Clouds.sid` | Luca Carrafiello (Luca) | 1 | 1:33 |
| [ ] | [ ] | `MUSICIANS/E/Eclipse/Cube1.sid` | Zoltán F. Földi (Eclipse) | 1 | 1:05 |

## 45. David_Whittaker (110 SIDs)

**Source:** curated (8 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/W/Whittaker_David/Max_Headroom.sid` | David Whittaker | 18 | 3:48 |
| [ ] | [ ] | `MUSICIANS/W/Whittaker_David/Panther.sid` | David Whittaker | 1 | 2:55 |
| [ ] | [ ] | `MUSICIANS/W/Whittaker_David/Armageddon_Man.sid` | David Whittaker | 4 | 2:33 |
| [ ] | [ ] | `MUSICIANS/W/Whittaker_David/Lazy_Jones.sid` | David Whittaker | 21 | 2:20 |
| [ ] | [ ] | `MUSICIANS/W/Whittaker_David/Solomons_Key.sid` | David Whittaker | 4 | 2:13 |

## 46. SynC (107 SIDs)

**Source:** curated (2 available from Cujo's list)

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/J/Jammic/Waste_of_Time.sid` | Sami Tiittanen (Jammic) | 1 | 3:04 |
| [ ] | [ ] | `MUSICIANS/C/Cube/Glide.sid` | Toni Lönnberg (!Cube) | 1 | 3:01 |

## 47. DefMon (106 SIDs)

**Source:** fallback (no curated; top composers: Anders Carlsson (Goto80) (44), Martin Demsky (26), Ilija Melentijevic (iLKke) (8))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/G/Goto80/Rent-A-Cop_Reloaded.sid` | Anders Carlsson (Goto80) | 10 | 13:11 |
| [ ] | [ ] | `MUSICIANS/G/Goto80/20_Years_Is_Nothing.sid` | Anders Carlsson (Goto80) | 1 | 6:34 |
| [ ] | [ ] | `MUSICIANS/D/Demsky_Martin/Monster.sid` | Martin Demsky | 1 | 6:04 |
| [ ] | [ ] | `MUSICIANS/G/Goto80/Skybox.sid` | Anders Carlsson (Goto80) | 1 | 5:52 |
| [ ] | [ ] | `MUSICIANS/G/Goto80/In_Memory_of.sid` | Anders Carlsson (Goto80) | 1 | 5:28 |

## 48. Walt/Bonzai (102 SIDs)

**Source:** fallback (no curated; top composers: Anders Fogh (Walt) (86), Henrik Tjagvad Madsen (Tjagvad) (16))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/W/Walt/Oxygene_Part_IV.sid` | Anders Fogh (Walt) | 1 | 5:04 |
| [ ] | [ ] | `MUSICIANS/T/Tjagvad/Fivo.sid` | Henrik Tjagvad Madsen (Tjagvad) | 1 | 3:43 |
| [ ] | [ ] | `MUSICIANS/T/Tjagvad/Something.sid` | Henrik Tjagvad Madsen (Tjagvad) | 1 | 3:28 |
| [ ] | [ ] | `MUSICIANS/W/Walt/No_Name_2.sid` | Anders Fogh (Walt) | 1 | 3:20 |
| [ ] | [ ] | `MUSICIANS/W/Walt/Sometimes.sid` | Anders Fogh (Walt) | 1 | 2:51 |

## 49. Michael_Winterberg (100 SIDs)

**Source:** fallback (no curated; top composers: Michael Winterberg (99), Marauder (1))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/W/Winterberg_Michael/Speedy_Music_I.sid` | Michael Winterberg | 4 | 11:38 |
| [ ] | [ ] | `MUSICIANS/W/Winterberg_Michael/Sound_Sample_IV.sid` | Michael Winterberg | 6 | 10:41 |
| [ ] | [ ] | `MUSICIANS/W/Winterberg_Michael/Sound_Sample_VII.sid` | Michael Winterberg | 4 | 10:11 |
| [ ] | [ ] | `MUSICIANS/W/Winterberg_Michael/Android_Music_Mix.sid` | Michael Winterberg | 1 | 8:30 |
| [ ] | [ ] | `MUSICIANS/W/Winterberg_Michael/Pop_Music_1.sid` | Michael Winterberg | 2 | 7:57 |

## 50. Chubrocker_V3.x (99 SIDs)

**Source:** fallback (no curated; top composers: István Szödényi Jr. (Chubrock) (23), Péter Molnár (Peet) (20), Jens Leiers (Decoy) (16))

| Sel | Mig | Path | Author | Subs | Length |
|---|---|---|---|---|---|
| [ ] | [ ] | `MUSICIANS/C/Chubrock/Metamorphosis_02.sid` | István Szödényi Jr. (Chubrock) | 3 | 8:53 |
| [ ] | [ ] | `MUSICIANS/D/Decoy/Fear_of_Sword.sid` | Jens Leiers (Decoy) | 1 | 4:37 |
| [ ] | [ ] | `MUSICIANS/D/Decoy/E-volution.sid` | Jens Leiers (Decoy) | 1 | 4:07 |
| [ ] | [ ] | `MUSICIANS/P/Peet/Rain.sid` | Péter Molnár (Peet) | 1 | 4:00 |
| [ ] | [ ] | `MUSICIANS/D/Decoy/Ingenious.sid` | Jens Leiers (Decoy) | 1 | 3:47 |
