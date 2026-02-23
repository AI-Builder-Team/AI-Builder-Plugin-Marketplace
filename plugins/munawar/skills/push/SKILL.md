---
name: push
description: Format, lint, typecheck, commit, and push changed files
argument-hint: "[commit-message]"
---

# Pre-Push Preparation and Push

Run formatters, linters, and type checkers on all changed files, then commit and push.

## Step 1: Identify changed files

Run `git diff --name-only` and `git diff --staged --name-only` to get all changed files (staged and unstaged). Categorize them:
- **Frontend files**: anything under `klair-client/`
- **Backend files**: anything under `klair-api/`
- If no files are changed, inform the user and stop.

## Step 2: Commit real work first

Before running any formatters or linters, commit the actual code changes so they are safely preserved and isolated from any formatter/linter modifications.

- Run `git diff` (unstaged) and `git diff --staged` (staged) to understand what the changes are about.
- Also run `git log --oneline -5` to see recent commit message style.
- Stage only the specific changed files by name (NEVER use `git add -A` or `git add .`)
- If user provided a commit message via arguments, use it. Otherwise, analyze the diff output and draft a concise descriptive commit message that reflects the "why" of the changes.
- Commit using HEREDOC format with Co-Authored-By trailer.

## Step 3: Lint changed files

Lint BEFORE formatting so that any lint fixes get cleaned up by the formatter afterwards.

- **Frontend**: from `klair-client/`, run `npx eslint --max-warnings 0 --no-warn-ignored <files>` on the changed frontend files
- **Backend**: from `klair-api/`, run `uv run ruff check <files>` on the changed backend files
- If lint fails, fix the issues and re-run. Do NOT proceed until lint passes clean.
- If lint fixes produced file changes, stage and commit as a separate commit with message "Fix lint issues".

## Step 4: Format changed files

Run formatters LAST so they catch everything including any lint fixes. Run on ONLY the files that were changed in Step 1 (not the entire codebase).

- **Frontend** (`klair-client/`): from the `klair-client/` directory, run `npx prettier --write <files>` on the changed frontend files
- **Backend** (`klair-api/`): from the `klair-api/` directory, run `uv run ruff format <files>` on the changed backend files
- Run `git diff --stat` to check if the formatter produced any changes.
- If it did, stage those files and commit as a separate commit with message "Run formatters on changed files".
- If no changes, skip this commit.

## Step 5: Type check

- **Frontend**: from `klair-client/`, run `pnpm tsc --noEmit`
- **Backend**: from `klair-api/`, run `uv run pyright`
- Only run the type checker for the side (frontend/backend) that has changes.
- If type check fails, fix the issues and re-run. Do NOT proceed until it passes.

## Step 6: Handle branch divergence

Before pushing, check if local and remote have diverged:
```
git log --oneline origin/<branch>..HEAD
git log --oneline HEAD..origin/<branch>
```
- If remote has commits that local doesn't, run `git pull --rebase origin <branch>` before pushing.
- If rebase produces conflicts, stop and inform the user.

## Step 7: Push

Run `git push origin <branch>` where `<branch>` is the current branch.

## User-provided commit message

$ARGUMENTS

## Important rules

- NEVER run `npm run format` (creates massive diffs across entire codebase) -- only run prettier on the specific changed files
- NEVER use `git add -A` or `git add .`
- NEVER force push
- NEVER skip pre-commit hooks
- If formatter changes are on top of already-committed work, commit formatting as a SEPARATE commit
- Run frontend and backend tools in parallel where possible (e.g., formatting both sides simultaneously)
