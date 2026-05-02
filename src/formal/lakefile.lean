import Lake
open Lake DSL

package dasmodel where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

@[default_target]
lean_lib DasModel where
  roots := #[`SID, `State, `Effects, `Compile]
