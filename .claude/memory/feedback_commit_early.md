---
name: Commit early to prevent lost work
description: Never leave parser/pipeline improvements uncommitted — working directory changes get clobbered by agents and stash operations
type: feedback
---

Commit code changes immediately after verifying they work (regression passes). Do NOT batch uncommitted changes across multiple improvement rounds.

**Why:** In the April 2026 session, parser improvements (generic freq finder, candidate-pair AD/SR, indirect BD path, duration encoding fix) were applied via Edit but never committed. They were lost THREE times:
1. `git stash` saved them, then stash pop was overwritten by agent activity
2. Agent worktrees writing to the same files on main
3. System file-modification detection reverting to committed state

Each re-application took 15-30 minutes. Total wasted time: ~2 hours.

**How to apply:** After any Edit that changes pipeline code:
1. Run regression test
2. If it passes, immediately `git add <files> && git commit -m "description"`
3. Don't wait to "batch" multiple changes into one commit
4. Small focused commits are better than losing work
