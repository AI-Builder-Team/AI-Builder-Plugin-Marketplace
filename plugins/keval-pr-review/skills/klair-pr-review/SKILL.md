---
name: klair-pr-review
description: Comprehensive PR review tailored to Klair codebase patterns. Use when reviewing a pull request, checking code quality, or running pre-merge validation. Triggers on "review PR", "review my changes", "pre-merge check", "klair review".
allowed-tools: [Read, Bash, Glob, Grep, Task, Edit]
---

# Klair PR Review

Comprehensive code review skill derived from analysis of 500+ PRs and 1,988 human review comments from the Klair team. Covers both frontend (React/TypeScript) and backend (Python/FastAPI) with codebase-specific patterns.

## When to Use

- Before creating or merging a PR
- After implementing a feature or fix
- When asked to review code changes

## Workflow

```
1. Gather Changes  ──►  2. Review (7 dimensions)  ──►  3. Report
   git diff main           Run all applicable           Structured output
   Read changed files      checklists in parallel       by severity
```

### Step 1: Gather Context

```bash
# Get the diff
git diff main...HEAD --stat        # Overview of changed files
git diff main...HEAD               # Full diff
git log main..HEAD --oneline       # Commits in this PR
```

Read each changed file in full (not just the diff). Many issues require surrounding context.

### Step 2: Run Review Dimensions

Run ALL 7 dimensions that apply to the changed files. Use Task agents in parallel for independent dimensions.

| # | Dimension | Applies To | Guideline |
|---|-----------|-----------|-----------|
| 1 | **Correctness & Logic** | All files | [guidelines/correctness-review.md] |
| 2 | **Error Handling & Resilience** | All files | [guidelines/error-handling-review.md] |
| 3 | **Security** | All files | [guidelines/security-review.md] |
| 4 | **Frontend Patterns** | .ts/.tsx/.css | [guidelines/frontend-review.md] |
| 5 | **Backend Patterns** | .py | [guidelines/backend-review.md] |
| 6 | **Data Pipeline** | pipelines/, ETL code | [guidelines/pipeline-review.md] |
| 7 | **Cross-Cutting Concerns** | All files | [guidelines/cross-cutting-review.md] |

### Step 3: Generate Report

Output a structured report following this format:

```markdown
# PR Review: [PR title or branch name]

## Critical (must fix before merge)
- [file:line] Issue description. **Why:** Impact explanation. **Fix:** Specific recommendation.

## High (strongly recommended)
- ...

## Medium (should fix)
- ...

## Low / Suggestions
- ...

## Positive Observations
- Things done well (reinforces good patterns)

## Summary
- X critical, Y high, Z medium, W low findings
- Recommendation: APPROVE / REQUEST CHANGES / APPROVE WITH SUGGESTIONS
```

### Severity Classification

| Level | Criteria | Examples |
|-------|----------|---------|
| **Critical** | Will cause incorrect behavior, data loss, security vulnerability, or production failure | Wrong formula, silent data corruption, XSS, unhandled crash path |
| **High** | Significant quality issue likely to cause problems | Silent failures, missing error propagation, React anti-patterns causing state bugs |
| **Medium** | Should be fixed but won't cause immediate problems | Missing validation, hardcoded values, stale comments, inconsistent patterns |
| **Low** | Suggestions for improvement | Naming, minor refactoring, optional type narrowing |

### Key Principles

1. **Trace through the code** - Don't just pattern-match on the diff. Follow data flow across files.
2. **Check both what changed AND what should have changed** - Missing changes are as important as incorrect changes.
3. **Verify cross-file consistency** - Same concept should behave the same everywhere.
4. **Distinguish between actual bugs and stylistic preferences** - Prioritize correctness over style.
5. **Include fix recommendations** - Every finding should have a concrete fix suggestion.
6. **Acknowledge good work** - Note positive patterns to reinforce them.
