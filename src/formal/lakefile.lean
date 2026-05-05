import Lake
open Lake DSL

package dasmodel where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

@[default_target]
lean_lib DasModel where
  roots := #[`SID, `State, `Effects, `Compile, `Properties, `Asm6502, `PSIDFile, `Codegen, `CommandoData, `CPU6502, `USFv3, `CommandoV3]

lean_exe dasmodel where
  root := `Main

lean_exe commando where
  root := `CommandoMain

lean_exe sidgen where
  root := `SidgenMain

lean_exe verify6502 where
  root := `VerifyMain

lean_exe compare where
  root := `CompareMain

lean_exe validate where
  root := `ValidateModel
