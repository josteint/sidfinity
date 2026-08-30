---
name: diligence
description: Session-level canon audit. Contemplate what was done this session and assess how well it aligns with The Principle, The Core Tenet, The Trichotomy and The Convergence Ledger. Use when the owner asks for due diligence, or PROACTIVELY at a natural pause after a substantial run of work.
user-invocable: true
allowed-tools: Bash Read Write Edit Glob Grep
effort: high
---

# diligence — canon audit of the session's work

Contemplate what you've done this session and consider how well it
aligns with The Principle, The Core Tenet, The Trichotomy and The
Convergence Ledger. If you suspect there could be complex trichotomy
issues, please also consult the trichotomy appendix
(`docs/the_trichotomy_appendix.md`).

Run the four docs as ADVERSARIAL checks, not a scorecard — the audit is
only worth doing if it can find something. Report honest demerits with
the same prominence as the wins, and verify your own session claims
mechanically where a tool exists (e.g. a "zero regressions" claim is
checked with `tools/batch_diff.py`, not restated). The deliverable is
the assessment; propose concrete follow-ups but apply them only when
the owner says so.
