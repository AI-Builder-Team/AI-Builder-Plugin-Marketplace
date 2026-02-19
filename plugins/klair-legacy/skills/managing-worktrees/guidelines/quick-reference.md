# Worktree Management Quick Reference

## One-Line Commands

### Create Worktrees
```bash
# New feature from main
bash .claude/scripts/create-worktrees/create.sh user-authentication

# New feature from specific branch
bash .claude/scripts/create-worktrees/create.sh payment-gateway develop

# Existing local/remote branch
bash .claude/scripts/create-worktrees/create.sh --branch feature/analytics

# Work on main (uses dev API)
bash .claude/scripts/create-worktrees/create.sh --branch main

# Work on prod (uses prod API)
bash .claude/scripts/create-worktrees/create.sh --branch prod

# Quick setup (no install)
bash .claude/scripts/create-worktrees/create.sh quick-fix --no-install --no-terminal

# Full install (all sub-projects)
bash .claude/scripts/create-worktrees/create.sh big-feature --full

# With Claude task
bash .claude/scripts/create-worktrees/create.sh new-feature --task "Implement dashboard"
```

### Start Services
```bash
cd trees/tree2 && ./start-services.sh 3002 5002
```

### Cleanup Worktrees
```bash
# Interactive (shows status, select to remove)
bash .claude/scripts/create-worktrees/cleanup.sh

# Remove specific worktree
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2

# Remove multiple worktrees
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2,tree3

# Remove all worktrees
bash .claude/scripts/create-worktrees/cleanup.sh --auto "*"

# Remove and update main
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2 --update-main
```

## Port Scheme

| Worktree | Frontend | Backend |
|----------|----------|---------|
| Main (tree1) | 3001 | 5001 |
| trees/tree2 | 3002 | 5002 |
| trees/tree3 | 3003 | 5003 |
| trees/treeN | 3000+N | 5000+N |

## Environment Configuration

| Branch | Frontend API URL | Notes |
|--------|-----------------|-------|
| `main` | `https://dev-adoption-api.klairvoyant.ai/` | Dev environment |
| `prod` | `https://adoption-api.klairvoyant.ai/` | Production environment |
| Other branches | `http://localhost:5000+N` | Local development |

## Common Flags

| Flag | Description |
|------|-------------|
| `--branch <name>` | Use existing branch instead of creating new one |
| `--full` | Install all sub-project dependencies |
| `--no-install` | Skip dependency installation (fastest) |
| `--no-terminal` | Don't open terminal window |
| `--no-claude` | Skip opening Claude Code session |
| `--task "desc"` | Task description for Claude session |

## Git Commands

```bash
# List all worktrees
git worktree list

# Remove worktree manually
git worktree remove trees/tree2 --force

# Prune stale worktree records
git worktree prune

# Check worktree branch
cd trees/tree2 && git branch
```

## Troubleshooting Quick Fixes

```bash
# Port conflict
lsof -ti:3002 | xargs kill -9  # Kill frontend
lsof -ti:5002 | xargs kill -9  # Kill backend

# Worktree already exists
git worktree remove trees/tree2 --force
rm -rf trees/tree2

# Branch already exists
git branch -D tree2-feature-name

# Dependencies failed
cd trees/tree2/klair-client && pnpm install
cd trees/tree2/klair-api && uv sync

# direnv not working
cd trees/tree2 && direnv allow
cd trees/tree2/klair-api && direnv allow
cd trees/tree2/klair-client && direnv allow
```

## Typical Workflows

### Feature Development
```bash
# 1. Create worktree
bash .claude/scripts/create-worktrees/create.sh user-dashboard

# 2. Develop in trees/tree2
cd trees/tree2

# 3. Commit and push
git add . && git commit -m "Add user dashboard" && git push -u origin tree2-user-dashboard

# 4. Create PR
gh pr create --draft

# 5. Clean up after merge
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2 --update-main
```

### Testing Existing Branch
```bash
# 1. Checkout branch in worktree
bash .claude/scripts/create-worktrees/create.sh --branch feature/analytics

# 2. Test in trees/tree2
cd trees/tree2 && ./start-services.sh 3002 5002

# 3. Clean up when done
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2
```

### Comparing Implementations
```bash
# 1. Create two worktrees
bash .claude/scripts/create-worktrees/create.sh approach-a
bash .claude/scripts/create-worktrees/create.sh approach-b

# 2. Start both services
cd trees/tree2 && ./start-services.sh 3002 5002 &
cd trees/tree3 && ./start-services.sh 3003 5003 &

# 3. Test at :3002 and :3003

# 4. Keep winner, remove loser
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree3
```

## Best Practices Checklist

- ✅ Use descriptive feature names (not "test", "tmp", "asdf")
- ✅ Commit changes before switching worktrees
- ✅ Push changes regularly to backup work
- ✅ Clean up worktrees after PR merge
- ✅ Use direnv for auto-configuration
- ✅ Ask user about updating main after cleanup
- ✅ Verify ports are available before starting services
- ✅ Keep main worktree for stable development

## Environment Files

Critical `.env` files automatically copied:
- `klair-api/.env` - Backend configuration
- `klair-client/.env` - Frontend configuration

Optional `.env` files (if present):
- `klair-misc/klair-mcp-ts/.env`
- `klair-misc/redshift-mcp-old/.env`
- `klair-udm/*/.env` (various sub-projects)

## When to Ask User

Always ask user before:
1. Cleaning up worktrees (which ones to remove)
2. Updating main branch after cleanup
3. Killing processes on ports
4. Overwriting existing worktrees

## direnv Port Variables

With direnv configured, these auto-export when entering worktree:
```bash
echo $KLAIR_FRONTEND_PORT  # 3002 for tree2
echo $KLAIR_BACKEND_PORT   # 5002 for tree2
```

Used by scripts and development tools automatically.
