---
name: quick-fix
description: Lightweight workflow for bugfixes and minor enhancements (<100 lines). Skips the full pipeline in favor of plan mode, focused implementation, and a single review pass. Use when the change is small and well-understood.
allowed-tools:
  - Task
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - EnterPlanMode
---

# Quick Fix

Lightweight alternative to the full pipeline for bugfixes and minor enhancements.

## When to Use

- Small bugfixes (root cause is clear or narrowly scoped)
- Minor enhancements (<100 lines of meaningful change)
- Changes that don't alter architecture or introduce new patterns
- Human judgement says "this is small"

## When NOT to Use (go full pipeline instead)

- New features requiring decomposition
- Cross-cutting changes touching 5+ files with new patterns
- Anything requiring interface contract design
- Work you'd leave running overnight

---

## Step 1: Classify

Determine the type of change:

**Bug Fix** — Something is broken, needs to work correctly.
- Emphasis: root cause analysis, regression test, minimal fix
- Don't refactor surrounding code

**Enhancement** — Something works, needs to work better/differently.
- Emphasis: fit existing patterns, add test coverage for new behavior
- Keep scope tight

This classification is lightweight — just sets the tone for the rest of the workflow.

---

## Step 2: Micro-Research

Quick context scan, not a full exploration.

1. **Check features directory** for related documentation:
   ```
   Glob: features/**/FEATURE.md
   ```
   Skim any FEATURE.md files that cover the area being changed.

2. **Read relevant source files** to understand current state.

3. **For bugs**: Identify root cause before planning the fix.

**Goal:** Understand what exists and what's documented. 2-3 minutes, not 20.

---

## Step 3: Plan

Enter **Plan Mode** to design the approach.

- For bugs: describe root cause, proposed fix, and regression test strategy
- For enhancements: describe what changes and how it fits existing patterns
- Use AskUserQuestion within plan mode for any clarifications needed

Exit plan mode with user approval before implementing.

---

## Step 4: Implement + Test

Implement the change, then ensure tests are current.

### Bug Fixes:
1. Write a regression test that reproduces the bug (if feasible)
2. Verify the test fails against current code
3. Implement the fix
4. Verify the test passes
5. Verify no existing tests broke

### Enhancements:
1. Implement the change
2. Verify existing tests still pass
3. Add test coverage for new behavior
4. Verify all tests pass

> Not strict TDD ordering — just "tests are current when you're done."

---

## Step 5: Review

Run a single `pr-review-toolkit:review-pr` pass:

```
Use Skill tool:
skill: "pr-review-toolkit:review-pr"
```

Address any issues found. This is the only QC gate for the lightweight path.

---

## Step 6: FEATURE.md Spot-Check

**This prevents documentation drift.** Before committing:

1. Check if any changed files appear in a FEATURE.md:
   ```
   Grep for changed filenames across features/**/FEATURE.md
   ```

2. **If a FEATURE.md covers this area:**
   - Read the relevant section
   - Does the change affect the documented intended state?
   - If yes: update FEATURE.md to reflect the new reality
   - If no: no update needed

3. **If no FEATURE.md covers this area:** That's fine — don't force-create one for a bugfix. The commit message carries the context.

---

## Step 7: Commit

Follow commit discipline with appropriate prefix:

- **Bug fix:** `fix(scope): description`
- **Enhancement:** `feat(scope): description`

```bash
git add {specific-files}
git commit -m "$(cat <<'EOF'
fix(scope): concise description of what and why

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

If FEATURE.md was updated, include it in the commit:
```bash
git add features/{domain}/{feature}/FEATURE.md
```

---

## Key Principles

- **Speed over ceremony** — This path exists because the full pipeline is overkill
- **Tests are current, not test-first** — Verify correctness, don't enforce TDD ordering
- **FEATURE.md spot-check is mandatory** — The one step that prevents drift
- **Single review pass** — One pr-review-toolkit run, not the full QC chain
- **Don't scope-creep** — If the fix reveals deeper issues, note them and consider the full pipeline
