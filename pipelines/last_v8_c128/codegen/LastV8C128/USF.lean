/-
  USF.lean — placeholder for this pipeline.

  The Last V8 (C128) engine does not yet have a USF lifting. This file
  exists so the lakefile's module list stays satisfied; it intentionally
  declares no types. See SongData.lean for the engine-specific
  representation we actually use today.
-/

namespace LastV8C128NS

/-- A marker so other modules can `import LastV8C128.USF`. -/
def usfStatus : String :=
  "USF lifting not implemented for the Last V8 (C128) engine yet."

end LastV8C128NS
