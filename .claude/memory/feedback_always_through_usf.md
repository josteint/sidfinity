---
name: Always go through USF
description: The pipeline MUST always go through USF — no shortcuts bypassing it. USF is the entire point of the project.
type: feedback
---

The pipeline MUST always be: SID → USF → SID. Never bypass USF with raw data passthrough.

**Why:** The entire project exists to build USF as the canonical format for ML training. A pipeline that bypasses USF proves nothing about USF's completeness. We spent days optimizing a raw roundtrip (decompile → pack) that skipped USF entirely, which was a waste — it didn't validate that USF can faithfully represent the data.

**How to apply:** Every test, every comparison, every demo must go through USF. If something breaks when going through USF, that's the bug to fix — not a reason to bypass USF. The pack_from_decompiled() shortcut should be removed or only used as a debugging tool, never as the production pipeline.
