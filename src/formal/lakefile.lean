import Lake
open Lake DSL

package dasmodel where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

@[default_target]
lean_lib DasModel where
  roots := #[`SID, `State, `Effects, `Compile, `Properties]

lean_exe dasmodel where
  root := `Main

lean_exe commando where
  root := `CommandoData
