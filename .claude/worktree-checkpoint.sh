#!/bin/bash
# Read hook input from stdin
input=$(cat)

# Extract worktree path from the hook input
worktree_path=$(echo "$input" | jq -r '.worktree_path // .tool_input.path // empty' 2>/dev/null)

if [ -z "$worktree_path" ] || [ ! -d "$worktree_path" ]; then
    exit 0
fi

cd "$worktree_path" || exit 0

# Check for uncommitted changes (tracked or untracked)
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    git add -A 2>/dev/null
    git commit -m "WIP: agent checkpoint" --no-verify 2>/dev/null
    echo '{"systemMessage": "Worktree checkpoint: committed uncommitted agent changes"}'
else
    echo '{}'
fi
