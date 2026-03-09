---
name: "m:sync"
description: "Sync main + all worktree branches using Git Town. Handles conflicts, iterates worktrees, reports results."
argument-hint: "[all | main | worktrees | continue]"
allowed-tools: Bash(git *), Bash(echo *), Bash(cd *), Bash(pwd), Read(*)
---

# Git Town Sync — All Branches + All Worktrees

Synchronize the entire repo: main branch, all feature branches, and all worktree working directories in one pass.

For worktree management (create, remove, list, launch servers), use `/m:gtr`.

## Current Context

- Repository root: !`git rev-parse --show-toplevel 2>/dev/null || echo "Not in a git repo"`
- Current branch: !`git branch --show-current 2>/dev/null || echo "N/A"`
- Git Town installed: !`git town --version 2>/dev/null || echo "NOT INSTALLED — install via: brew install git-town"`
- Git Town sync strategy: !`git config git-town.sync-feature-strategy 2>/dev/null || echo "not set (default: merge)"`
- Worktrees: !`git worktree list 2>/dev/null || echo "No worktrees"`

## User's Request

$ARGUMENTS

## Routing

- **"continue"** → Jump straight to the Continue section. The user is resuming after resolving merge conflicts.
- **"main"** → Sync only the main worktree (Step 1 + Step 2, skip Step 3).
- **"worktrees"** → Skip main sync, iterate worktrees only (Step 3).
- **"all"** or **no argument** → Full cycle: Steps 1 through 4.

---

## Step 1: Pre-Sync — Ensure Non-Interactive

Git Town has no `--non-interactive` flag. Any unclassified local branch triggers an interactive prompt that breaks automation. Run this before every sync.

### 1a. Set regex classifiers (idempotent)

```bash
git config git-town.perennial-regex "^prod$"
git config git-town.observed-regex "backup"
```

### 1b. Set parent=main for all orphan feature branches

```bash
known_parents=$(git config --get-regexp 'git-town-branch\..*\.parent' 2>/dev/null | sed 's/git-town-branch\.\(.*\)\.parent.*/\1/')
perennial_regex=$(git config git-town.perennial-regex 2>/dev/null || echo "^$")
observed_regex=$(git config git-town.observed-regex 2>/dev/null || echo "^$")

for branch in $(git for-each-ref --format='%(refname:short)' refs/heads/ | grep -v '^main$'); do
  echo "$known_parents" | grep -qxF "$branch" && continue
  echo "$branch" | grep -qE "$perennial_regex" && continue
  echo "$branch" | grep -qE "$observed_regex" && continue
  git config git-town.perennial-branches 2>/dev/null | tr ' ' '\n' | grep -qxF "$branch" && continue
  git config "git-town-branch.$branch.parent" main
  echo "Set parent: $branch -> main"
done
```

### 1c. Verify no orphans

```bash
git town sync --all --dry-run 2>&1 | grep -c "cannot determine parent"
```

If count > 0, investigate before proceeding.

---

## Step 2: Sync Main Worktree

Run from the main worktree (repo root):

```bash
git town sync --all
```

This fetches all remotes, syncs every branch that isn't checked out in another worktree, pushes, and cleans up merged branches.

**If sync stops with a conflict:** print the conflict details and tell the user to resolve, then run `/m:sync continue` to resume. Do NOT attempt to resolve conflicts automatically.

---

## Step 3: Sync Each Worktree

`git town sync --all` skips branches checked out in other worktrees. To truly sync everything, iterate through each worktree and sync from within it.

```bash
main_wt=$(git rev-parse --show-toplevel)
git worktree list --porcelain | grep '^worktree ' | sed 's/^worktree //' | while read wt_path; do
  [ "$wt_path" = "$main_wt" ] && continue
  branch=$(cd "$wt_path" && git branch --show-current)
  echo "=== Syncing worktree: $wt_path ($branch) ==="
  (cd "$wt_path" && git town sync) || echo "  CONFLICT in $wt_path — resolve manually, then run: /m:sync continue"
done
```

If a worktree sync fails with conflicts:
1. Note which worktree and branch had the conflict
2. Continue with the remaining worktrees
3. Report all failures at the end

---

## Step 4: Report

Summarize what happened:
- How many branches synced successfully
- Which worktrees (if any) have unresolved conflicts
- Any branches that were cleaned up (merged into main)

---

## Continue (after conflict resolution)

When the user says "continue" or invokes `/m:sync continue`:

1. Check if there's a suspended Git Town operation:
   ```bash
   git town status
   ```

2. If suspended, resume it:
   ```bash
   git town continue
   ```

3. If `continue` succeeds and there are more worktrees to sync, pick up where Step 3 left off — iterate the remaining worktrees.

4. If `continue` hits another conflict, report it and wait.

---

## Execution Style

Brief narration between commands. No inline teaching. At the end, provide a summary of what was synced and any issues found.

Keep it tight — this skill is about getting branches synced, not explaining git theory.
