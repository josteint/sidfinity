---
name: feedback_subagents_no_git
description: "Fan-out/research subagents must be forbidden from running git mutations; one ran `git restore` and reverted live DB state."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3ae28f74-8297-413f-bc76-861f4388809e
---

When spawning research-player / multi-agent fan-out subagents — ESPECIALLY while a separate Claude session is active on the same repo — every agent prompt MUST explicitly forbid all `git` mutations (`restore`/`checkout`/`reset`/`add`/`commit`/`clean`/`stash`) and any write to a tracked file outside the agent's designated output dir.

**Why:** during the 2026-06-13 soundmonitor research sweep, a subagent saw `hvsc84.db` as `M` in `git status`, wrongly assumed its own read-only (`mode=ro`) SELECT had touched the file, and ran `git restore hvsc84.db` "to clean up" — reverting the live DB to the last commit and undoing an `engine_docs` doc-state bump. It could have clobbered the concurrent DMC session's uncommitted DB writes (it didn't — they had committed). Recovered by re-running `tools/apply_engine_docs.py`. A `mode=ro` connection CANNOT write the file, so the `M` was pre-existing real state — the agent acted destructively on a false premise.

**How to apply:** in every fan-out agent prompt add a hard line — "Do NOT run any `git` command. Write ONLY inside `<dir>`. If a tracked file looks modified, leave it — it is not yours." Open shared SQLite DBs read-only (`file:...?mode=ro`, uri=True); that part worked this run (no WAL flip), the git mutation was the new failure mode. Best durable fix: bake this into the `research-player` skill's agent-instruction template. Related: [[feedback_repo_tmp_dir]], [[feedback_worktree_commit]].
