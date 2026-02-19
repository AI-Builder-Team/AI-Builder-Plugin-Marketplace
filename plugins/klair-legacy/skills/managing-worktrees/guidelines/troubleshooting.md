# Worktree Troubleshooting Guide

This guide covers common issues when working with git worktrees and their solutions.

## Table of Contents

- [Creation Issues](#creation-issues)
- [Dependency Issues](#dependency-issues)
- [Port Conflicts](#port-conflicts)
- [Environment Configuration](#environment-configuration)
- [Git Issues](#git-issues)
- [direnv Issues](#direnv-issues)
- [Service Issues](#service-issues)
- [Cleanup Issues](#cleanup-issues)

## Creation Issues

### "Branch already exists"

**Problem:** Creating a worktree fails because the branch name already exists.

**Cause:** You previously created a worktree with the same feature name, and the branch wasn't deleted.

**Solution 1 - Delete the branch:**
```bash
git branch -D tree2-feature-name
bash .claude/scripts/create-worktrees/create.sh feature-name
```

**Solution 2 - Use existing branch:**
```bash
bash .claude/scripts/create-worktrees/create.sh --branch tree2-feature-name
```

### "Worktree already exists at trees/tree2"

**Problem:** The worktree directory exists but is not properly registered with git.

**Cause:** Previous worktree wasn't cleaned up properly, or script was interrupted.

**Solution 1 - Use cleanup script:**
```bash
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2
bash .claude/scripts/create-worktrees/create.sh feature-name
```

**Solution 2 - Manual cleanup:**
```bash
git worktree remove trees/tree2 --force
bash .claude/scripts/create-worktrees/create.sh feature-name
```

**Solution 3 - Force directory removal:**
```bash
git worktree remove trees/tree2 --force
rm -rf trees/tree2  # If above fails
bash .claude/scripts/create-worktrees/create.sh feature-name
```

### "Directory not empty"

**Problem:** The trees/treeN directory exists and contains files.

**Cause:** Manual directory creation or incomplete cleanup.

**Solution:**
```bash
rm -rf trees/tree2
bash .claude/scripts/create-worktrees/create.sh feature-name
```

### "Failed to create worktree"

**Problem:** Git worktree command fails for unknown reasons.

**Diagnosis:**
```bash
# Check git version (need 2.5+)
git --version

# Check if you're in a git repository
git status

# List existing worktrees
git worktree list

# Check for locked worktrees
git worktree prune
```

**Solution:**
```bash
# Update git if version is too old
brew upgrade git  # macOS
sudo apt update && sudo apt upgrade git  # Ubuntu/Debian

# Prune stale worktree records
git worktree prune

# Try creating worktree again
bash .claude/scripts/create-worktrees/create.sh feature-name
```

### Base branch doesn't exist

**Problem:** Trying to create worktree from non-existent branch.

**Cause:** Specified base branch doesn't exist locally or remotely.

**Solution:**
```bash
# List available branches
git branch -a

# Fetch from remote
git fetch origin

# Create from correct branch
bash .claude/scripts/create-worktrees/create.sh feature-name main
```

## Dependency Issues

### Frontend (pnpm) installation fails

**Problem:** `pnpm install` fails during worktree creation.

**Diagnosis:**
```bash
# Check pnpm is installed
pnpm --version

# Check if package.json exists
ls trees/tree2/klair-client/package.json

# Try manual installation
cd trees/tree2/klair-client
pnpm install
```

**Common causes:**
1. **pnpm not installed:** `npm install -g pnpm`
2. **Network issues:** Check internet connection
3. **Corrupted lock file:** Delete `pnpm-lock.yaml` and retry
4. **Node version mismatch:** Use `nvm use` or `fnm use`

**Solution:**
```bash
# Reinstall pnpm
npm install -g pnpm

# Clear cache and retry
cd trees/tree2/klair-client
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Or skip installation during worktree creation
bash .claude/scripts/create-worktrees/create.sh feature-name --no-install
cd trees/tree2/klair-client
pnpm install
```

### Backend (uv) installation fails

**Problem:** `uv sync` fails during worktree creation.

**Diagnosis:**
```bash
# Check uv is installed
uv --version

# Check if pyproject.toml exists
ls trees/tree2/klair-api/pyproject.toml

# Try manual installation
cd trees/tree2/klair-api
uv sync
```

**Common causes:**
1. **uv not installed:** Install from https://github.com/astral-sh/uv
2. **Python version mismatch:** Check required Python version in pyproject.toml
3. **Lock file issues:** Delete `uv.lock` and retry

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clear and retry
cd trees/tree2/klair-api
rm -rf .venv uv.lock
uv sync

# Or skip installation during worktree creation
bash .claude/scripts/create-worktrees/create.sh feature-name --no-install
cd trees/tree2/klair-api
uv sync
```

### Slow dependency installation

**Problem:** Installation takes too long.

**Optimization:**
```bash
# Use --no-install to skip during creation
bash .claude/scripts/create-worktrees/create.sh feature-name --no-install

# Install dependencies later when needed
cd trees/tree2/klair-client && pnpm install
cd trees/tree2/klair-api && uv sync

# Or install only core dependencies (default behavior)
# --full flag installs ALL sub-projects
bash .claude/scripts/create-worktrees/create.sh feature-name
```

## Port Conflicts

### "Port already in use"

**Problem:** Cannot start services because port is occupied.

**Check what's using the port:**
```bash
lsof -i:3002  # Check frontend port
lsof -i:5002  # Check backend port
```

**Solution 1 - Let start-services.sh handle it:**
```bash
cd trees/tree2
./start-services.sh 3002 5002
# Script will detect and prompt to kill process
```

**Solution 2 - Manually kill process:**
```bash
# Find PID
lsof -ti:3002

# Kill process
lsof -ti:3002 | xargs kill -9
lsof -ti:5002 | xargs kill -9

# Start services
./start-services.sh 3002 5002
```

**Solution 3 - Use different ports:**
```bash
# Use next available tree number
bash .claude/scripts/create-worktrees/create.sh feature-name
# Creates tree3 with ports 3003/5003
```

### Port conflicts between worktrees

**Problem:** Multiple worktrees trying to use same ports.

**Prevention:**
- Each worktree automatically gets unique ports (tree2=3002/5002, tree3=3003/5003)
- Create script handles port assignment automatically

**If conflict still occurs:**
```bash
# List running services
ps aux | grep "pnpm dev"
ps aux | grep "fast_endpoint.py"

# Kill specific services
pkill -f "pnpm dev"
pkill -f "fast_endpoint.py"

# Restart services with correct ports
cd trees/tree2 && ./start-services.sh 3002 5002
```

### Cannot find process using port

**Problem:** Port shows as in use but lsof doesn't find process.

**Advanced detection:**
```bash
# Try netstat (Linux)
netstat -tulpn | grep :3002

# Try ss (Linux)
ss -tulpn | grep :3002

# macOS alternative
netstat -vanp tcp | grep 3002
```

**Force kill if needed:**
```bash
# Find all node/python processes
ps aux | grep node
ps aux | grep python

# Kill specific process by PID
kill -9 <PID>
```

## Environment Configuration

### Frontend not connecting to backend

**Problem:** Frontend makes API calls but gets connection errors.

**Check frontend .env:**
```bash
cd trees/tree2/klair-client
cat .env | grep VITE_AI_ADOPTION_API_URL
```

**Expected values:**
- For local branches: `http://localhost:5002`
- For main branch: `https://dev-adoption-api.klairvoyant.ai/`
- For prod branch: `https://adoption-api.klairvoyant.ai/`

**Solution - Update .env:**
```bash
cd trees/tree2/klair-client
# Edit .env file
# Set VITE_AI_ADOPTION_API_URL to correct value
```

**Solution - Recreate worktree:**
```bash
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2
bash .claude/scripts/create-worktrees/create.sh feature-name
```

### Backend not using correct port

**Problem:** Backend starts on wrong port.

**Check backend .env:**
```bash
cd trees/tree2/klair-api
cat .env | grep PORT
```

**Expected:** `PORT=5002` for tree2

**Solution:**
```bash
cd trees/tree2/klair-api
# Edit .env file
# Set PORT=5002
```

### start-services.sh overwrites remote API URL

**Problem:** Remote API URL (dev/prod) gets overwritten with localhost.

**Expected behavior:** Should NOT happen with updated start-services.sh

**Check script version:**
```bash
cd trees/tree2
grep "Preserving remote API URL" start-services.sh
```

**If missing, update from main worktree:**
```bash
cp start-services.sh trees/tree2/
```

### Environment variables not loading

**Problem:** Application doesn't see environment variables.

**Without direnv:**
```bash
# Manually load .env
cd trees/tree2/klair-api
source .env
# Or for frontend (if needed)
cd trees/tree2/klair-client
export $(cat .env | xargs)
```

**With direnv:**
```bash
# Allow direnv
cd trees/tree2
direnv allow

# Check if working
echo $KLAIR_FRONTEND_PORT  # Should show 3002
echo $KLAIR_BACKEND_PORT   # Should show 5002
```

## Git Issues

### "Worktree not found" in git worktree list

**Problem:** Worktree directory exists but git doesn't track it.

**Solution:**
```bash
# Prune stale records
git worktree prune

# List what git knows about
git worktree list

# If needed, remove manually and recreate
rm -rf trees/tree2
bash .claude/scripts/create-worktrees/create.sh feature-name
```

### Cannot push from worktree

**Problem:** `git push` fails with "no upstream branch".

**Solution:**
```bash
cd trees/tree2
git push -u origin tree2-feature-name
```

### Branch not tracking remote

**Problem:** `git pull` doesn't work in worktree.

**Solution:**
```bash
cd trees/tree2
git branch --set-upstream-to=origin/tree2-feature-name
```

### Detached HEAD in worktree

**Problem:** Worktree is in detached HEAD state.

**Solution:**
```bash
cd trees/tree2
git checkout tree2-feature-name
# Or checkout the correct branch
```

### Cannot switch branches in worktree

**Problem:** Trying to checkout different branch in worktree fails.

**Explanation:** Each worktree is designed for ONE branch. Don't switch branches within a worktree.

**Solution:** Create a new worktree for the other branch:
```bash
bash .claude/scripts/create-worktrees/create.sh --branch other-branch
```

### Changes showing in multiple worktrees

**Problem:** Git status shows changes in multiple worktrees.

**Explanation:** Worktrees share the same git database. Uncommitted changes may appear across worktrees if on same branch.

**Solution:** Commit changes in each worktree:
```bash
cd trees/tree2
git add .
git commit -m "Changes for tree2"

cd trees/tree3
git add .
git commit -m "Changes for tree3"
```

## direnv Issues

### Environment not auto-loading

**Problem:** direnv doesn't auto-load when entering worktree.

**Check if direnv is installed:**
```bash
direnv --version
```

**Check if shell hook is configured:**
```bash
# Should see direnv hook in output
cat ~/.bashrc | grep direnv
cat ~/.zshrc | grep direnv
```

**Solution:**
```bash
# Install direnv
brew install direnv  # macOS
sudo apt install direnv  # Ubuntu/Debian

# Add hook to shell config
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc  # bash
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc    # zsh

# Reload shell
source ~/.bashrc  # or ~/.zshrc

# Allow direnv in worktree
cd trees/tree2
direnv allow
```

### direnv shows errors on cd

**Problem:** Error messages when entering worktree directory.

**Check .envrc files:**
```bash
cd trees/tree2
cat .envrc
cat klair-api/.envrc
cat klair-client/.envrc
```

**Common issues:**
- Syntax errors in .envrc
- Missing dependencies (nvm, uv, etc.)
- Path issues

**Solution:**
```bash
# Fix syntax errors in .envrc
# Ensure nvm/fnm is installed for Node version management
# Ensure uv is installed for Python

# Re-allow
direnv allow
```

### Port variables not set

**Problem:** `$KLAIR_FRONTEND_PORT` and `$KLAIR_BACKEND_PORT` are empty.

**Check root .envrc:**
```bash
cat trees/tree2/.envrc
```

**Should contain:**
```bash
# Auto-detect tree number and export ports
TREE_PATH=$(pwd)
TREE_NUM=$(basename "$TREE_PATH" | sed 's/tree//')
export KLAIR_FRONTEND_PORT=$((3000 + TREE_NUM))
export KLAIR_BACKEND_PORT=$((5000 + TREE_NUM))
```

**Solution:**
```bash
cd trees/tree2
direnv allow
echo $KLAIR_FRONTEND_PORT  # Verify it works
```

## Service Issues

### Frontend doesn't start

**Problem:** `pnpm dev` fails to start.

**Check:**
```bash
cd trees/tree2/klair-client

# Verify dependencies installed
ls node_modules

# Check package.json exists
cat package.json

# Try starting manually
pnpm dev --port 3002
```

**Common fixes:**
```bash
# Reinstall dependencies
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Check Node version
node --version
nvm use  # or fnm use

# Check for TypeScript errors
pnpm tsc --noEmit
```

### Backend doesn't start

**Problem:** Backend fails to start.

**Check:**
```bash
cd trees/tree2/klair-api

# Verify venv exists
ls .venv

# Try activating and starting manually
source .venv/bin/activate
uv run fast_endpoint.py
```

**Common fixes:**
```bash
# Reinstall dependencies
rm -rf .venv
uv sync

# Check Python version
python --version

# Check for import errors
uv run python -c "import fastapi"
```

### Services start but not accessible

**Problem:** Services running but browser cannot connect.

**Check if services are listening:**
```bash
lsof -i:3002  # Should show pnpm/node process
lsof -i:5002  # Should show python process
```

**Check firewall:**
```bash
# Temporarily disable firewall to test
# macOS: System Preferences > Security & Privacy > Firewall
# Linux: sudo ufw status
```

**Check localhost resolution:**
```bash
ping localhost
curl http://localhost:3002
curl http://localhost:5002
```

### Services crash on startup

**Problem:** Services start but immediately crash.

**Check logs:**
```bash
cd trees/tree2

# Start services in foreground to see errors
cd klair-client && pnpm dev --port 3002

# In another terminal
cd trees/tree2/klair-api && uv run fast_endpoint.py
```

**Common causes:**
- Missing .env variables
- Port already in use
- Dependency version conflicts
- Database connection issues

## Cleanup Issues

### Cleanup script fails to remove worktree

**Problem:** Cleanup script cannot remove worktree.

**Manual removal:**
```bash
# Force remove
git worktree remove trees/tree2 --force

# If that fails, remove directory first
rm -rf trees/tree2
git worktree prune
```

### "Worktree contains modified or untracked files"

**Problem:** Git refuses to remove worktree with uncommitted changes.

**Option 1 - Commit changes:**
```bash
cd trees/tree2
git add .
git commit -m "Save work"
git push
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2
```

**Option 2 - Discard changes:**
```bash
cd trees/tree2
git reset --hard
git clean -fd
bash .claude/scripts/create-worktrees/cleanup.sh --auto tree2
```

**Option 3 - Force remove:**
```bash
git worktree remove trees/tree2 --force
```

### Cannot remove worktree directory

**Problem:** `rm -rf trees/tree2` fails with "Permission denied".

**Solution:**
```bash
# Check if processes are using files
lsof +D trees/tree2

# Kill processes if found
pkill -f trees/tree2

# Try removing again
rm -rf trees/tree2

# If still fails, check permissions
ls -la trees/
sudo rm -rf trees/tree2  # Last resort
```

### Cleanup removes wrong worktree

**Problem:** Accidentally removed the wrong worktree.

**Prevention:** Always use interactive mode first:
```bash
bash .claude/scripts/create-worktrees/cleanup.sh
# Review list before selecting
```

**Recovery:**
```bash
# If you haven't pushed commits, they may be lost
# Check reflog
git reflog | grep tree2-feature-name

# Recreate worktree with existing branch
bash .claude/scripts/create-worktrees/create.sh --branch tree2-feature-name
```

## Getting Help

If you encounter an issue not covered here:

1. **Check script help:**
   ```bash
   bash .claude/scripts/create-worktrees/create.sh
   bash .claude/scripts/create-worktrees/cleanup.sh
   ```

2. **Check git worktree documentation:**
   ```bash
   git worktree --help
   man git-worktree
   ```

3. **Debug mode:**
   ```bash
   bash -x .claude/scripts/create-worktrees/create.sh feature-name
   # Shows each command as it executes
   ```

4. **Check Claude.md:**
   - Git Worktree Management section
   - direnv Setup section
   - GitHub Pull Request Management section

5. **Use the skill:**
   ```bash
   # In Claude Code
   Use the managing-worktrees skill
   ```
