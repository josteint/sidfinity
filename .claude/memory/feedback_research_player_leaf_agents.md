---
name: feedback_research_player_leaf_agents
description: research-player sweep agents must be leaf agents — recursive sub-spawning blew the token budget
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d64508f1-420d-412d-bed5-ac3641af168b
---

When running `/research-player` (or any multi-agent fan-out), the cluster
agents are spawned as `general-purpose` agents, which **hold the `Agent` tool
and will recursively spawn their own helper sub-agents**. On 2026-06-17 a
"6-agent" david_whittaker sweep became 30+ live agents and **exhausted the
session token limit mid-sweep** — almost all summaries were lost; only one
artifact survived.

**Why:** no Write-capable agent type lacks the `Agent` tool (Explore/Plan can't
Write), so recursion can only be stopped at the prompt level.

**How to apply:** every research/fan-out agent prompt MUST open with a LEAF
constraint — "You are a LEAF agent; NEVER use the Agent/Task tool, never spawn
sub-agents or background tasks; do ALL work yourself." The `research-player`
SKILL.md now bakes this in as the first MANDATORY hard constraint + a
launch-point note (commit a9a1049). Keep sweeps to 5-6 agents total and don't
launch follow-up waves that themselves fan out. The user flagged this twice and
it cost real money — watch live agent count (the `tasks/` dir mtimes reveal
fan-out), and report the TRUE count, not just the number you launched.

Related: [[feedback_subagents_no_git]], [[feedback_background_jobs_harness]].
