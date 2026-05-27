import CodegenV3
import BatchV3

open V3

def main : IO Unit := do
  let sid := generateSID batchV3
  writeFile "batch_v3.sid" sid
  IO.println s!"Generated batch_v3.sid ({sid.size} bytes)"
