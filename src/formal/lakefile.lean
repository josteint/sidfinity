import Lake
open Lake DSL

package dasmodel where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

@[default_target]
lean_lib DasModel where
  roots := #[`SID, `Asm6502, `PSIDFile, `USFv3, `CommandoV3, `CodegenV3]

lean_exe sidgen_v3 where
  root := `SidgenV3Main
