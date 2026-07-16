---
name: bug-investigation-methodology
description: "Proven methodology for finding and fixing bugs — pick one song, trace the first divergence, fix root cause, batch test"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4994dfd8-7bf7-414e-a073-16595cdd2a38
---

The pattern that works (proven across the GT2 era's Grade-A climbs and
every USF-era family since):

1. **Pick the closest-to-passing failing member** — smallest fix needed
2. **Localize the first divergence** — today that is
   `tools/find_first_divergence.py` (first `(reg, val)` mismatch + the
   register's voice/role); show orig vs rebuilt with context
3. **Classify the error**: verdict/observation artifact (Trap A/B/C —
   see [[feedback_verification_modes]]) vs real content bug
4. **If verdict artifact**: fix the verdict/tooling, then re-census —
   never widen a tolerance to make a real bug pass
5. **If real bug**: trace to the specific pattern/instrument/table
   entry, find root cause in extract or composer
6. **Fix and batch test** — must not regress the family (regression
   portfolio / full family batch)

**How to apply:** Always start with ONE song. Don't try to fix
categories abstractly. The concrete song gives you the exact bytes to
compare. (The full current protocol lives in
[[feedback_writelog_divergence_recipe]]; this memory is the general
discipline behind it.)

(Rewritten 2026-07-16: the original was GT2-grading-era — gt2_compare.py
tolerances, 3,478-song regression, Grade A/F vocabulary. The method
survived intact; only the tooling names changed.)
