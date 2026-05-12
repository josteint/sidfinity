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
