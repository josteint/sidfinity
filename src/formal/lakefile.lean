import Lake
open Lake DSL

package dasmodel where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

-- Commando pipeline (canonical, byte-perfect, DO NOT MODIFY for
-- Monty work — every file Monty depends on has its own clone below).
@[default_target]
lean_lib DasModel where
  roots := #[`SID, `Asm6502, `PSIDFile, `USFv3, `CommandoV3, `CodegenV3,
             `PropertiesV3,
             -- Monty's fully independent clone of the entire stack:
             `MontySID, `MontyAsm6502, `MontyPSIDFile, `MontyUSFv3,
             `MontyV3, `MontyCodegenV3, `MontyPropertiesV3,
             -- Dormant Batch tool (not used right now):
             `BatchV3]

lean_exe sidgen_v3 where
  root := `SidgenV3Main

lean_exe sidgen_monty where
  root := `SidgenMontyMain

lean_exe sidgen_batch where
  root := `SidgenBatchMain
