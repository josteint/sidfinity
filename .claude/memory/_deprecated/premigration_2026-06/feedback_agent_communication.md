---
name: Agent communication limitation
description: Cannot send messages to running background agents — significant drawback for iterative work
type: feedback
---

Running background agents cannot receive additional context or corrections mid-task.

**Why:** SendMessage tool is not available in this environment. Once an agent is launched, it works only from its initial prompt. If we discover critical context after launch (like the noise burst rule correction, tempo formula, or extended freq table method), we can't share it.

**How to apply:** Front-load ALL known context into the agent prompt. Include specific findings, verified values, known pitfalls, and corrected rules. Don't launch agents for exploratory work where discoveries during the session would change the approach. For iterative debugging, work hands-on instead of delegating to agents.
