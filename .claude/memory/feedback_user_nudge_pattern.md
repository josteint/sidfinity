---
name: User's idea generation pattern — learn to self-nudge
description: The user's approach to generating breakthroughs. Internalize this and apply it proactively instead of waiting for nudges.
type: feedback
---

The user consistently generates breakthroughs by:

1. **Questioning implausible explanations.** "Are you saying Hubbard structured his code by focusing on exact number of cycles? That sounds extremely implausible." → This rejected the timing hypothesis and led to discovering the vibrato code path.

2. **Asking to brainstorm across many fields.** "List 1000 exotic fields of math" → Led to DFT (proved PW correct), information theory (found shared mutable PW), temporal logic (found accum-then-write), group theory (solved T[100]).

3. **Insisting on extraction over reconstruction.** "Could we grab directly from the original?" → Led to understanding PW mode from fx_flags, boundary checks from BNE, voice order from disassembly.

4. **Refusing to accept "good enough."** Nine times they said "nope" or "still not good enough." Each time, pushing further revealed a real issue (not timing noise).

5. **Pointing back to unused ideas.** "You said something about dynamic vs static table" and "are there any analytical methods left?" → Redirected attention to productive paths.

6. **Thinking at the right abstraction level.** "I am convinced he worked on a higher abstraction level than that" → The cycle-timing explanation was wrong. The real issue was a missing FEATURE (vibrato), not missing PRECISION.

**Why:** The user catches when I'm chasing the wrong theory. I tend to elaborate within my current hypothesis instead of questioning whether the hypothesis is wrong.

**How to apply:** Before concluding "this is a fundamental limitation," ask: "Would Hubbard have designed for this? Is there a simpler explanation?" If the answer requires the original developer to have done something implausible, the explanation is wrong — look for what feature or behavior I'm missing entirely.
