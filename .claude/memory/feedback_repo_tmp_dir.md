---
name: feedback_repo_tmp_dir
description: Use the repo-local tmp/ dir (gitignored) for ALL scratch artifacts — never /tmp. /tmp gets wiped between sessions and ate the FC-standard member/sample lists.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1a969f4b-cad3-4dc0-a302-0b489914e62f
---

Put every scratch artifact — batch member lists, sample JSONs, per-worker
build dirs, probe outputs — in `tmp/` at the repo root (`/home/jtr/sidfinity/tmp/`,
gitignored via `/tmp/` in .gitignore), NEVER in the system `/tmp`.

**Why:** /tmp does not survive between sessions; the FC-standard rollout's
`/tmp/fc_std_members.json` + `/tmp/fc_std_sample.json` were lost and had to be
regenerated. The user asked explicitly (2026-06-11) to stop using /tmp.

**How to apply:** any tool/script that takes an output or workdir path gets
`tmp/<name>` relative to the repo root. Durable lists that other sessions
will need should still graduate to a tracked location (or be regenerable
via a documented probe).
