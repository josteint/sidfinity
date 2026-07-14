---
name: tooling-reflex
description: "META. After every non-trivial debugging session (>30 min), ask \"what tool would have collapsed this to <5 min?\" — then add to tools/INVESTIGATION_BACKLOG.md or build if <1 hour. If a tool hurts (silent failure, misleading output, rotting), MODIFY OR REMOVE — don't work around. When you add/modify a diagnostic tool, update CLAUDE.md + relevant memory so future sessions know it exists."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 02f65b25-1c68-4ebb-b180-7ebbd9c37c55
---

The analysis pipeline is the long pole, not the code. Cyb II's pulse_run
fix was 10 lines; finding it took hours of bespoke py65 scripts, address
lookups, and writelog filtering. The fix-to-investigation ratio across
this project is ~1:30. Investing in diagnostic tooling pays back across
the entire migration roadmap.

## The reflex

End of session, ask:
1. **What would have collapsed this to <5 min?** Be specific — name the
   command-line invocation you wish you'd had.
2. **<1 hour to build?** Build now. **More?** Add to
   [`tools/INVESTIGATION_BACKLOG.md`](../../tools/INVESTIGATION_BACKLOG.md)
   with a concrete use case anchored to this session.
3. **Did any tool we used HURT us?** Wrong default, silent failure,
   stale output, misleading interface? Add it to the backlog's "Hurt
   list" — to MODIFY or REMOVE next time we touch it. Bad tools cost
   more than no tool because they create false confidence.

## Maintain context for new/modified tools

A tool that future-you can't find doesn't exist. **Every new diagnostic
tool requires four context updates BEFORE the commit lands.** Treat
this as a checklist, not a maybe:

1. **`CLAUDE.md` "Working conventions"** — one-liner pointing at the
   tool with the specific situation it answers. This surfaces in EVERY
   session's context window, so it's the highest-leverage placement.
   Format: "For X situation, use TOOL with FLAGS. Output: Y." Don't
   bury it under a wall of explanation.
2. **`tools/INVESTIGATION_BACKLOG.md` "Built (active)" table** — entry
   with use case + pointer to where else it's documented. This is the
   tooling INVENTORY; if a tool isn't here, it's invisible to fresh
   sessions even if it exists on disk.
3. **Relevant memory** (usually [[feedback_writelog_divergence_recipe]]
   for diagnostic tools) — slot the tool into the right STEP of the
   workflow. Future sessions follow the recipe and want the tool to
   appear at the moment they need it.
4. **Commit message** — mention the new tool's name and one-line use
   case. `git log` is the fallback index when memory + CLAUDE.md fail.

If you skip ANY of the four, the tool rots. User caught this twice
this project: explicit feedback "you need to maintain context knowledge
of new tools or modified tools." Build the discipline so they don't
have to catch it a third time.

When MODIFYING an existing tool (new flag, new output format, behavior
change): same four updates apply. Stale documentation is worse than no
documentation.

## When to demote/remove

A tool earns removal when:
- Its default behavior produces wrong results (e.g., the `--duration 0.5`
  int-only parsing in siddump that silently zero'd duration).
- Its output is misleading (e.g., py65 reporting state that doesn't
  match libsidplayfp ground truth for engines that depend on CIA timing).
- It only ever runs as part of a longer pipeline and adds no value as
  a standalone (= fold it back into the pipeline).

Demote by modifying first (fix the default, add a warning, narrow the
contract). Remove only when modification can't restore trust.

## Related

- [[feedback_writelog_divergence_recipe]] — concrete protocol that uses
  the tools described in CLAUDE.md
- [[feedback_ground_truth]] — why libsidplayfp / siddump is authoritative
  and py65 isn't (motivates `siddump --memwatch` over py65 traces)
