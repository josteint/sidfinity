---
name: NO writelog replay, ever
description: User strongly rejected writelog-replay as a path. Defeats USF's purpose. Never propose again.
type: feedback
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
NEVER propose writelog-replay (recording a SID's writes via emulator
then playing them back from a tiny "dumb player") as a path to "scale
HVSC quickly." User explicitly rejected this with capitals: "WRITELOG
REPLAY IS A COMPLETELY TERRIBLE IDEA. I DONT WANT EVER TO HEAR SUCH
A SUGGESTION AGAIN. COMPLETELY OFF THE TABLE."

**Why:** USF must preserve MUSICAL STRUCTURE for ML training. Writelog
fragments are opaque audio blobs — they sound right but are useless
for the project's actual purpose (training models on musical
representation). Substituting writelog for musical USF defeats the
entire project.

**How to apply:** When the user asks for "fastest path to most HVSC
sounds right," remember the constraint: it must be MUSICAL USF, not
audio-correctness via any means. Suggest paths that improve
decompilation/encoding, not paths that bypass them. Never include
"raw writelog segment in USF" as an option. If audio-fidelity-without-
USF-quality is the only way to scale faster, say so honestly without
proposing the bypass.
