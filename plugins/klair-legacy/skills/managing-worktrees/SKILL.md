---
name: managing-worktrees
description: Guides users through creating, using, and cleaning up git worktrees for parallel feature development. Use when users want to work on multiple branches simultaneously, test changes in isolation, or manage parallel development workflows.
allowed-tools: [Bash, Read, Write, Glob, Grep]
---

# Managing Git Worktrees

This skill helps you work with multiple branches simultaneously using git worktrees. Each worktree is an isolated working directory with its own dependencies, environment configuration, and dedicated ports for services.

## What Are Worktrees?

Git worktrees allow you to check out multiple branches simultaneously in separate directories:

```
/path/to/project/
  ├── .git/              # Shared git directory
  ├── klair-api/         # Main worktree (tree1)
  ├── klair-client/      # Main worktree (tree1)
  └── trees/
      ├── tree2/         # Second worktree (ports 3002/5002)
      │   ├── klair-api/
      │   └── klair-client/
      └── tree3/         # Third worktree (ports 3003/5003)
          ├── klair-api/
          └── klair-client/
```

**Benefits:**
- Work on multiple features without switching branches
- Test different implementations side-by-side
- Keep main working directory clean
- Run services on different ports simultaneously
- Isolated dependencies per worktree

## When to Use This Skill

Use this skill when the user wants to:
- Work on multiple features simultaneously
- Test changes in isolation
- Compare different implementations
- Review code while continuing development
- Keep main branch clean while working on experimental features
- Run multiple versions of the application concurrently

## Prerequisites

- Git repository with worktree support (git 2.5+)
- **pnpm** for frontend dependencies
- **uv** for backend dependencies
- **direnv** (optional but recommended for auto-configuration)
- **Warp/WezTerm/tmux** (optional for automatic terminal opening)

## Core Workflows

### 1. Creating a Worktree for a New Feature

Use this when starting new development work:

```bash
bash .claude/scripts/create-worktrees/create.sh <feature-name>
```

**What it does:**
1. Finds next available tree number (tree2, tree3, etc.)
2. Creates new branch: `treeN-<feature-name>` from `main`
3. Copies all `.env` files from main worktree
4. Installs frontend (pnpm) and backend (uv) dependencies
5. Configures ports: frontend `3000+N`, backend `5000+N`
6. Configures API URL based on branch:
   - Local branches → `http://localhost:5000+N`
7. Opens terminal with services (optional)
8. Opens Claude Code session (optional)

**Example:**
```bash
# Create worktree for user authentication feature
bash .claude/scripts/create-worktrees/create.sh user-authentication

# Result:
# - Location: trees/tree2/
# - Branch: tree2-user-authentication (new)
# - Based on: main
# - Ports: 3002 (frontend), 5002 (backend)
# - API URL: http://localhost:5002
```

**Flags:**
- `--full`: Install all sub-project dependencies (not just client+api)
- `--no-install`: Skip dependency installation (fastest)
- `--no-terminal`: Don't open terminal window
- `--no-claude`: Skip opening Claude Code session
- `--task "desc"`: Task description for Claude session

**Examples:**
```bash
# Create from develop branch
bash .claude/scripts/create-worktrees/create.sh payment-gateway develop

# Quick worktree without installation
bash .claude/scripts/create-worktrees/create.sh quick-fix --no-install --no-terminal

# Full installation with Claude task
bash .claude/scripts/create-worktrees/create.sh new-feature --full --task "Implement user dashboard"
```

### 2. Creating a Worktree for an Existing Branch

Use this when you need to work on an existing branch (local or remote):

```bash
bash .claude/scripts/create-worktrees/create.sh --branch <branch-name>
```

**What it does:**
1. Checks if branch exists locally or remotely
2. Fetches from remote if needed
3. Creates worktree checking out the existing branch
4. Copies `.env` files and configures based on branch:
   - **`main` branch** → Dev API: `https://dev-adoption-api.klairvoyant.ai/`
   - **`prod` branch** → Prod API: `https://adoption-api.klairvoyant.ai/`
   - **Other branches** → Local API: `http://localhost:5000+N`
5. Installs dependencies
6. Opens terminal and Claude session (optional)

**Examples:**
```bash
# Work on main branch (uses dev API)
bash .claude/scripts/create-worktrees/create.sh --branch main

# Work on prod branch (uses prod API)
bash .claude/scripts/create-worktrees/create.sh --branch prod

# Work on existing feature branch
bash .claude/scripts/create-worktrees/create.sh --branch feature/analytics-dashboard

# Work on remote branch
bash .claude/scripts/create-worktrees/create.sh --branch origin/feature/payment-gateway

# Existing branch without installation
bash .claude/scripts/create-worktrees/create.sh --branch hotfix/critical-bug --no-install
```

### 3. Starting Services in a Worktree

After creating a worktree, start the services:

```bash
cd trees/tree2
./start-services.sh 3002 5002
```

**What it does:**
1. Checks if ports are available
2. Prompts to kill existing processes if ports are in use
3. Updates `.env` files with dynamic ports (preserves remote API URLs)
4. Starts frontend on specified port (e.g., 3002)
5. Starts backend on specified port (e.g., 5002)
6. Prefixes output with `[FRONTEND]` and `[BACKEND]` tags
7. Handles graceful shutdown with Ctrl+C

**Important:** The script preserves remote API URLs (dev/prod) and only updates localhost URLs to use the dynamic port.

### 4. Working with Multiple Worktrees

Each worktree is completely isolated:

```bash
# Main worktree (tree1)
cd ~/project
pnpm dev           # Frontend: 3001
uv run fast_endpoint.py  # Backend: 5001

# Second worktree (tree2)
cd ~/project/trees/tree2
./start-services.sh 3002 5002

# Third worktree (tree3)
cd ~/project/trees/tree3
./start-services.sh 3003 5003
```

**Access your apps:**
- Main: http://localhost:3001 → http://localhost:5001
- Tree2: http://localhost:3002 → http://localhost:5002
- Tree3: http://localhost:3003 → http://localhost:5003

### 5. Cleaning Up Worktrees

After merging PRs or abandoning features, clean up worktrees.

**Interactive cleanup (recommended):**
```bash
bash .claude/scripts/create-worktrees/cleanup.sh
```

Shows a list of all worktrees with:
- Remote push status (↑ = pushed, - = local only)
- PR status (✓ = merged, ○ = open, ✕ = closed, - = no PR)
- Last modified time

You can then select which worktrees to remove.

**Automated cleanup:**
```bash
# Remove specific worktrees
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2,tree3

# Remove all worktrees
bash .claude/scripts/create-worktrees/cleanup.sh --auto "*"

# Remove and update main branch
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2 --update-main
```

**IMPORTANT:** Always ask the user if they want to update main branch after cleanup:
```
"Would you like me to also checkout main and pull the latest changes after cleanup?
(This is useful since the worktree cleanup typically happens after a PR is merged)"
```

**When to clean up:**
- After PR is merged to main
- When abandoning a feature branch
- To free up disk space

**Note:** Ensure changes are committed and pushed before cleanup!

## Port Assignment Scheme

| Worktree Location | Tree Number | Frontend Port | Backend Port |
|-------------------|-------------|---------------|--------------|
| Main worktree (repo root) | 1 | 3001 | 5001 |
| `trees/tree2/` | 2 | 3002 | 5002 |
| `trees/tree3/` | 3 | 3003 | 5003 |
| `trees/treeN/` | N | 3000+N | 5000+N |

## Environment Configuration

The creation script automatically configures `.env` files based on the branch:

| Branch | Frontend API URL | Backend Port |
|--------|-----------------|--------------|
| `main` | `https://dev-adoption-api.klairvoyant.ai/` | N/A (uses remote) |
| `prod` | `https://adoption-api.klairvoyant.ai/` | N/A (uses remote) |
| Other branches | `http://localhost:5000+N` | `5000+N` |

**Preserved by start-services.sh:**
- Remote API URLs (dev/prod) are never overwritten
- Only localhost URLs are updated with dynamic ports

## Best Practices

### 1. Branch Naming Convention
When creating new branches via worktrees, use descriptive names:
```bash
# Good
bash .claude/scripts/create-worktrees/create.sh user-authentication
bash .claude/scripts/create-worktrees/create.sh fix-invoicing-bug
bash .claude/scripts/create-worktrees/create.sh refactor-api-client

# Avoid
bash .claude/scripts/create-worktrees/create.sh test
bash .claude/scripts/create-worktrees/create.sh tmp
bash .claude/scripts/create-worktrees/create.sh asdf
```

### 2. Dependency Management
- Each worktree has isolated dependencies (`.venv`, `node_modules`)
- Use `uv` and `pnpm` - they hardlink packages from cache (saves disk space)
- A new worktree costs ~50-100MB physical disk, not 1GB+
- No need for shared venvs or symlink tricks

### 3. Use direnv for Auto-Configuration
With direnv installed and configured:
- Python virtualenv auto-activates when entering worktree
- `.env` files auto-load
- Port environment variables auto-export

Without direnv:
- Manually activate: `source klair-api/.venv/bin/activate`
- Manually load: `source klair-api/.env`

### 4. Commit Frequently
Since worktrees share the same git repository:
- Commit changes before switching between worktrees
- Push changes to backup your work
- Use descriptive commit messages

### 5. Clean Up Regularly
- Remove worktrees after PRs are merged
- Free up disk space by removing unused worktrees
- Keep main worktree for stable development

### 6. Testing Multiple Implementations
For comparing different approaches:
1. Create multiple worktrees with different branches
2. Implement different solutions in each
3. Test side-by-side at different ports
4. Choose the best implementation
5. Clean up unused worktrees

## Troubleshooting

### Worktree Creation Fails

**"Branch already exists":**
```bash
# Remove the branch first
git branch -D tree2-feature-name

# Or use --branch to checkout existing branch
bash .claude/scripts/create-worktrees/create.sh --branch existing-branch
```

**"Worktree already exists":**
```bash
# Remove the worktree
git worktree remove trees/tree2 --force

# Or use cleanup script
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2
```

**"Directory not empty":**
```bash
# Manually remove directory
rm -rf trees/tree2

# Then recreate worktree
bash .claude/scripts/create-worktrees/create.sh feature-name
```

### Dependency Installation Fails

**Frontend (pnpm) issues:**
```bash
# Manually install in worktree
cd trees/tree2/klair-client
pnpm install
```

**Backend (uv) issues:**
```bash
# Manually install in worktree
cd trees/tree2/klair-api
uv sync
```

**Quick worktree without installation:**
```bash
# Skip installation, install manually later
bash .claude/scripts/create-worktrees/create.sh feature-name --no-install
```

### Port Conflicts

**"Port already in use":**
```bash
# start-services.sh will detect and offer to kill the process
# Or manually find and kill process:
lsof -ti:3002 | xargs kill -9  # Frontend
lsof -ti:5002 | xargs kill -9  # Backend
```

**Check what's running on a port:**
```bash
lsof -i:3002  # Check frontend port
lsof -i:5002  # Check backend port
```

### Environment Configuration Issues

**API URL not updating:**
```bash
# Manually update frontend .env
cd trees/tree2/klair-client
# Edit .env and update VITE_AI_ADOPTION_API_URL
```

**Backend port not updating:**
```bash
# Manually update backend .env
cd trees/tree2/klair-api
# Edit .env and update PORT
```

**start-services.sh overwrites remote API URL:**
- This shouldn't happen with the updated script
- If it does, verify you're using the latest version
- The script checks for remote URLs and preserves them

### Git Issues

**"Worktree not found":**
```bash
# Verify git version supports worktrees
git --version  # Need 2.5+

# List all worktrees
git worktree list

# Prune stale worktree records
git worktree prune
```

**"Branch not tracking remote":**
```bash
# Set upstream tracking
cd trees/tree2
git branch --set-upstream-to=origin/tree2-feature-name
```

### direnv Issues

**Environment not auto-loading:**
```bash
# Allow direnv for worktree
cd trees/tree2
direnv allow

# Also allow subdirectories
direnv allow klair-api/
direnv allow klair-client/
```

**Port variables not set:**
```bash
# Check if direnv is working
cd trees/tree2
echo $KLAIR_FRONTEND_PORT  # Should show 3002
echo $KLAIR_BACKEND_PORT   # Should show 5002

# If empty, direnv may not be installed or configured
# Follow direnv setup in CLAUDE.md
```

## Example Workflows

### Workflow 1: Feature Development

```bash
# 1. Create worktree for new feature
bash .claude/scripts/create-worktrees/create.sh user-dashboard

# 2. Start services
cd trees/tree2
./start-services.sh 3002 5002

# 3. Develop and test at http://localhost:3002

# 4. Commit and push
git add .
git commit -m "Add user dashboard"
git push -u origin tree2-user-dashboard

# 5. Create PR
gh pr create --draft

# 6. After PR merged, clean up
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2 --update-main
```

### Workflow 2: Testing Existing Branch

```bash
# 1. Checkout existing branch in worktree
bash .claude/scripts/create-worktrees/create.sh --branch feature/analytics

# 2. Start services
cd trees/tree2
./start-services.sh 3002 5002

# 3. Test the feature at http://localhost:3002

# 4. Clean up when done
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2
```

### Workflow 3: Comparing Implementations

```bash
# 1. Create first worktree with approach A
bash .claude/scripts/create-worktrees/create.sh approach-a

# 2. Create second worktree with approach B
bash .claude/scripts/create-worktrees/create.sh approach-b

# 3. Start services for both
cd trees/tree2 && ./start-services.sh 3002 5002 &
cd trees/tree3 && ./start-services.sh 3003 5003 &

# 4. Test both implementations
# - Approach A: http://localhost:3002
# - Approach B: http://localhost:3003

# 5. Choose best implementation and clean up
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree3
```

### Workflow 4: Working on main/prod

```bash
# 1. Create worktree for main branch (uses dev API)
bash .claude/scripts/create-worktrees/create.sh --branch main

# 2. Services will use remote dev API
cd trees/tree2
./start-services.sh 3002 5002
# Frontend at :3002 calls https://dev-adoption-api.klairvoyant.ai/

# 3. Similarly for prod
bash .claude/scripts/create-worktrees/create.sh --branch prod
cd trees/tree3
./start-services.sh 3003 5003
# Frontend at :3003 calls https://adoption-api.klairvoyant.ai/
```

## Quick Reference

### Create Worktree Commands
```bash
# New feature from main
bash .claude/scripts/create-worktrees/create.sh <feature-name>

# New feature from specific branch
bash .claude/scripts/create-worktrees/create.sh <feature-name> <base-branch>

# Existing branch
bash .claude/scripts/create-worktrees/create.sh --branch <branch-name>

# Quick setup (no install, no terminal)
bash .claude/scripts/create-worktrees/create.sh <feature-name> --no-install --no-terminal

# Full setup (all dependencies)
bash .claude/scripts/create-worktrees/create.sh <feature-name> --full
```

### Start Services
```bash
cd trees/tree2
./start-services.sh 3002 5002
```

### Cleanup Commands
```bash
# Interactive
bash .claude/scripts/create-worktrees/cleanup.sh

# Automated
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2,tree3
bash .claude/scripts/create-worktrees/cleanup.sh --auto "*"

# With main update
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2 --update-main
```

### Git Commands
```bash
# List all worktrees
git worktree list

# Remove worktree manually
git worktree remove trees/tree2 --force

# Prune stale worktrees
git worktree prune
```

## Additional Resources

- Git Worktree Documentation: https://git-scm.com/docs/git-worktree
- direnv Setup: See CLAUDE.md § direnv Setup
- Create Script Documentation: `.claude/scripts/create-worktrees/create.sh` header comments
- Cleanup Script Documentation: `.claude/scripts/create-worktrees/cleanup.sh` header comments
