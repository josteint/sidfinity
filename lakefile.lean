import Lake
open Lake DSL

package sidfinity where
  leanOptions := #[⟨`autoImplicit, false⟩]

-- ---------------------------------------------------------------------------
-- Commando pipeline — byte-perfect rebuild of Rob Hubbard's "Commando".
-- Locked invariant: `sidgen_commando` produces a SID whose siddump writelog
-- matches the original frame-for-frame. Do not modify this lib for new
-- engines without re-verifying the byte-perfect status.
-- ---------------------------------------------------------------------------

lean_lib Commando where
  srcDir := "pipelines/commando/codegen"
  roots  := #[`Commando.SID, `Commando.Asm6502, `Commando.PSIDFile,
              `Commando.USF, `Commando.Constants, `Commando.SongData,
              `Commando.Codegen, `Commando.Properties]

lean_exe sidgen_commando where
  srcDir := "pipelines/commando/codegen"
  root   := `Commando.Main

-- ---------------------------------------------------------------------------
-- Monty on the Run pipeline — independent clone of the Commando pipeline,
-- extended with Hubbard quirks specific to early-era Monty (skydive,
-- pulsedelay init, notenum/freq table overlap aliasing). Grade A 98.8% under
-- siddump; 0-divergence under py65.
-- ---------------------------------------------------------------------------

lean_lib Monty where
  srcDir := "pipelines/monty/codegen"
  roots  := #[`Monty.SID, `Monty.Asm6502, `Monty.PSIDFile,
              `Monty.USF, `Monty.Constants, `Monty.SongData,
              `Monty.Codegen, `Monty.Properties]

lean_exe sidgen_monty where
  srcDir := "pipelines/monty/codegen"
  root   := `Monty.Main


lean_lib FiveTitleTunes where
  srcDir := "pipelines/five_title_tunes/codegen"
  roots  := #[`FiveTitleTunes.SID, `FiveTitleTunes.Asm6502, `FiveTitleTunes.PSIDFile,
              `FiveTitleTunes.USF, `FiveTitleTunes.Constants, `FiveTitleTunes.SongData,
              `FiveTitleTunes.Codegen, `FiveTitleTunes.Properties]

lean_exe sidgen_five_title_tunes where
  srcDir := "pipelines/five_title_tunes/codegen"
  root   := `FiveTitleTunes.Main


lean_lib ActionBiker where
  srcDir := "pipelines/action_biker/codegen"
  roots  := #[`ActionBiker.SID, `ActionBiker.Asm6502, `ActionBiker.PSIDFile,
              `ActionBiker.USF, `ActionBiker.Constants, `ActionBiker.SongData,
              `ActionBiker.Codegen, `ActionBiker.Properties]

lean_exe sidgen_action_biker where
  srcDir := "pipelines/action_biker/codegen"
  root   := `ActionBiker.Main


lean_lib BattleOfBritain where
  srcDir := "pipelines/battle_of_britain/codegen"
  roots  := #[`BattleOfBritain.SID, `BattleOfBritain.Asm6502, `BattleOfBritain.PSIDFile,
              `BattleOfBritain.USF, `BattleOfBritain.Constants, `BattleOfBritain.SongData,
              `BattleOfBritain.Codegen, `BattleOfBritain.Properties]

lean_exe sidgen_battle_of_britain where
  srcDir := "pipelines/battle_of_britain/codegen"
  root   := `BattleOfBritain.Main


lean_lib Chimera where
  srcDir := "pipelines/chimera/codegen"
  roots  := #[`Chimera.SID, `Chimera.Asm6502, `Chimera.PSIDFile,
              `Chimera.USF, `Chimera.Constants, `Chimera.SongData,
              `Chimera.Codegen, `Chimera.Properties]

lean_exe sidgen_chimera where
  srcDir := "pipelines/chimera/codegen"
  root   := `Chimera.Main


lean_lib Confuzion where
  srcDir := "pipelines/confuzion/codegen"
  roots  := #[`Confuzion.SID, `Confuzion.Asm6502, `Confuzion.PSIDFile,
              `Confuzion.USF, `Confuzion.Constants, `Confuzion.SongData,
              `Confuzion.Codegen, `Confuzion.Properties]

lean_exe sidgen_confuzion where
  srcDir := "pipelines/confuzion/codegen"
  root   := `Confuzion.Main


lean_lib CrazyComets where
  srcDir := "pipelines/crazy_comets/codegen"
  roots  := #[`CrazyComets.SID, `CrazyComets.Asm6502, `CrazyComets.PSIDFile,
              `CrazyComets.USF, `CrazyComets.Constants, `CrazyComets.SongData,
              `CrazyComets.Codegen, `CrazyComets.Properties]

lean_exe sidgen_crazy_comets where
  srcDir := "pipelines/crazy_comets/codegen"
  root   := `CrazyComets.Main


lean_lib DevilsGalop where
  srcDir := "pipelines/devils_galop/codegen"
  roots  := #[`DevilsGalop.SID, `DevilsGalop.Asm6502, `DevilsGalop.PSIDFile,
              `DevilsGalop.USF, `DevilsGalop.Constants, `DevilsGalop.SongData,
              `DevilsGalop.Codegen, `DevilsGalop.Properties]

lean_exe sidgen_devils_galop where
  srcDir := "pipelines/devils_galop/codegen"
  root   := `DevilsGalop.Main


lean_lib Gremlins where
  srcDir := "pipelines/gremlins/codegen"
  roots  := #[`Gremlins.SID, `Gremlins.Asm6502, `Gremlins.PSIDFile,
              `Gremlins.USF, `Gremlins.Constants, `Gremlins.SongData,
              `Gremlins.Codegen, `Gremlins.Properties]

lean_exe sidgen_gremlins where
  srcDir := "pipelines/gremlins/codegen"
  root   := `Gremlins.Main


lean_lib HunterPatrol where
  srcDir := "pipelines/hunter_patrol/codegen"
  roots  := #[`HunterPatrol.SID, `HunterPatrol.Asm6502, `HunterPatrol.PSIDFile,
              `HunterPatrol.USF, `HunterPatrol.Constants, `HunterPatrol.SongData,
              `HunterPatrol.Codegen, `HunterPatrol.Properties]

lean_exe sidgen_hunter_patrol where
  srcDir := "pipelines/hunter_patrol/codegen"
  root   := `HunterPatrol.Main


lean_lib OneManAndHisDroid where
  srcDir := "pipelines/one_man_and_his_droid/codegen"
  roots  := #[`OneManAndHisDroid.SID, `OneManAndHisDroid.Asm6502, `OneManAndHisDroid.PSIDFile,
              `OneManAndHisDroid.USF, `OneManAndHisDroid.Constants, `OneManAndHisDroid.SongData,
              `OneManAndHisDroid.Codegen, `OneManAndHisDroid.Properties]

lean_exe sidgen_one_man_and_his_droid where
  srcDir := "pipelines/one_man_and_his_droid/codegen"
  root   := `OneManAndHisDroid.Main


lean_lib Rasputin where
  srcDir := "pipelines/rasputin/codegen"
  roots  := #[`Rasputin.SID, `Rasputin.Asm6502, `Rasputin.PSIDFile,
              `Rasputin.USF, `Rasputin.Constants, `Rasputin.SongData,
              `Rasputin.Codegen, `Rasputin.Properties]

lean_exe sidgen_rasputin where
  srcDir := "pipelines/rasputin/codegen"
  root   := `Rasputin.Main


lean_lib SampleMusicIKarate where
  srcDir := "pipelines/sample_music_i_karate/codegen"
  roots  := #[`SampleMusicIKarate.SID, `SampleMusicIKarate.Asm6502, `SampleMusicIKarate.PSIDFile,
              `SampleMusicIKarate.USF, `SampleMusicIKarate.Constants, `SampleMusicIKarate.SongData,
              `SampleMusicIKarate.Codegen, `SampleMusicIKarate.Properties]

lean_exe sidgen_sample_music_i_karate where
  srcDir := "pipelines/sample_music_i_karate/codegen"
  root   := `SampleMusicIKarate.Main


lean_lib HumanRace where
  srcDir := "pipelines/human_race/codegen"
  roots  := #[`HumanRace.SID, `HumanRace.Asm6502, `HumanRace.PSIDFile,
              `HumanRace.USF, `HumanRace.Constants, `HumanRace.SongData,
              `HumanRace.Codegen, `HumanRace.Properties]

lean_exe sidgen_human_race where
  srcDir := "pipelines/human_race/codegen"
  root   := `HumanRace.Main


lean_lib LastV8 where
  srcDir := "pipelines/last_v8/codegen"
  roots  := #[`LastV8.SID, `LastV8.Asm6502, `LastV8.PSIDFile,
              `LastV8.USF, `LastV8.Constants, `LastV8.SongData,
              `LastV8.Codegen, `LastV8.Properties]

lean_exe sidgen_last_v8 where
  srcDir := "pipelines/last_v8/codegen"
  root   := `LastV8.Main


lean_lib LastV8C128 where
  srcDir := "pipelines/last_v8_c128/codegen"
  roots  := #[`LastV8C128.SID, `LastV8C128.Asm6502, `LastV8C128.PSIDFile,
              `LastV8C128.USF, `LastV8C128.Constants, `LastV8C128.SongData,
              `LastV8C128.Codegen, `LastV8C128.Properties]

lean_exe sidgen_last_v8_c128 where
  srcDir := "pipelines/last_v8_c128/codegen"
  root   := `LastV8C128.Main


lean_lib MasterOfMagic where
  srcDir := "pipelines/master_of_magic/codegen"
  roots  := #[`MasterOfMagic.SID, `MasterOfMagic.Asm6502, `MasterOfMagic.PSIDFile,
              `MasterOfMagic.USF, `MasterOfMagic.Constants, `MasterOfMagic.SongData,
              `MasterOfMagic.Codegen, `MasterOfMagic.Properties]

lean_exe sidgen_master_of_magic where
  srcDir := "pipelines/master_of_magic/codegen"
  root   := `MasterOfMagic.Main


lean_lib ThingOnASpring where
  srcDir := "pipelines/thing_on_a_spring/codegen"
  roots  := #[`ThingOnASpring.SID, `ThingOnASpring.Asm6502, `ThingOnASpring.PSIDFile,
              `ThingOnASpring.USF, `ThingOnASpring.Constants, `ThingOnASpring.SongData,
              `ThingOnASpring.Codegen, `ThingOnASpring.Properties]

lean_exe sidgen_thing_on_a_spring where
  srcDir := "pipelines/thing_on_a_spring/codegen"
  root   := `ThingOnASpring.Main
