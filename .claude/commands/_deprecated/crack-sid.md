Throw every available tool at a specific SID to get it to Grade A (or S).

Usage: /crack-sid <path_to_sid>

## Procedure

1. Identify the engine: `from sidid import identify_player`
2. Try static parsing first (gt2_to_usf, dmc_to_usf, rh_to_usf — whatever matches the engine)
3. If no static parser exists: use regtrace_to_usf (universal, works for any engine)
4. Build rebuilt SID, compare with original, report grade
5. If not Grade A:
   a. Run taint tracking to understand driver structure
   b. Run abstract interpreter for data table locations
   c. Use formal semantics player for fast diagnosis (extraction vs codegen bug?)
   d. Trace the first wrong frame: which voice, which register, what value?
   e. Classify the root cause and fix it
6. Re-test, iterate until Grade A or determine what USF feature is missing

Read `docs/formal/procedure.md` for the decision framework on which tool to use when.
