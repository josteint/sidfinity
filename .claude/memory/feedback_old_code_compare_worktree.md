---
name: feedback_old_code_compare_worktree
description: "To compare current vs pre-change behavior, use a git WORKTREE, never git stash in the main tree — and never stash/pop across a timeout-prone command."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d376eaeb-2dd0-4c86-9a72-d8dbc9020d3b
  modified: 2026-07-22T23:06:54.468Z
---

To measure whether a change altered behavior (old-code vs new-code), the
instinct is `git stash` → run → `git stash pop`. DON'T do it in the main tree.

**Why:** a `git stash` … `git stash pop` dance placed inside ONE Bash command
that then TIMED OUT stranded the changes in the stash — the working tree
reverted to old code with the edits invisible (2026-07-23, DMC round 90).
Recovery cost several tool calls; a linter reminder even showed the reverted
file, briefly looking like the edits had been lost. `git add -A` after a
stranded stash would have committed the OLD code.

**How to apply:**
- Prefer a **git worktree** for run-old-code: `git worktree add ../old <ref>`
  (or the Agent tool's `isolation: "worktree"`). Your edits stay live in the
  main tree the whole time; the comparison runs in an isolated checkout. No
  stash, no way to strand work.
- If you must stash, `git diff > tmp/backup.patch` FIRST, and split
  stash / run / pop into SEPARATE Bash commands so a timeout can't land between
  stash and pop. Never `git add -A` while a stash of your work is outstanding.
- Question whether the comparison is even needed: a spot-check of a few
  representative members (spec-identical old vs new) often settles it without a
  whole-corpus old-vs-new sweep. The full sweep here was belt-and-suspenders
  after 3 members had already proven identical.

Related: [[feedback_background_jobs_harness]] (timeout-prone long commands),
[[feedback_repo_tmp_dir]] (where the .patch backup goes).
