---
name: Worktree agents must commit
description: Always tell worktree agents to git add + commit — untracked files get deleted on cleanup
type: feedback
---

When launching agents with `isolation: "worktree"`, ALWAYS include in the prompt: "Before finishing, `git add -A && git commit -m 'description'`."

**Why:** Worktree cleanup checks git status. New untracked files appear as "clean" (no tracked changes), so the worktree is deleted — along with all new files the agent created. This happened multiple times in the April 2026 session: code_flow.py, regtrace_to_usf.py, memdiff.py, and freq_reconstruct.py were all created by agents in worktrees but lost because they weren't committed.

**How to apply:** Every Agent tool call with `isolation: "worktree"` must include commit instructions in the prompt. A WorktreeRemove hook in `.claude/settings.json` acts as a safety net but shouldn't be relied on as the primary mechanism.
