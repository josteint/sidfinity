import MontyCodegenV3
import MontyV3

open MV3

def main : IO Unit := do
  let sid := generateSID montyV3
  writeFile "monty_v3.sid" sid
  IO.println s!"Generated monty_v3.sid ({sid.size} bytes)"
  IO.println s!"  Freq table: {montyV3.freqTable.entries.length} entries"
  IO.println s!"  Instruments: {montyV3.instruments.length}"
  IO.println s!"  Patterns: {montyV3.patterns.length}"
  IO.println s!"  Subtunes: {montyV3.subtunes.length}"
