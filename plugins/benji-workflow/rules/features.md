# Feature Organization Rules

This document describes the feature-centric organization system used in this project.

## Directory Structure

```
features/
├── index.md                        # Domain registry
└── {domain}/                       # Domain folder
    └── {feature-id}/               # Feature folder
        ├── FEATURE.md              # Living documentation (intended state)
        └── specs/                  # Specifications
            └── {NN}-{spec-name}/   # Numbered spec
                ├── spec-research.md # Research for this spec (context, contracts, test plan)
                ├── spec.md          # Requirements
                └── checklist.md     # Progress tracking
```

## File Purposes

### features/index.md
Domain registry listing all feature domains with descriptions and folder names.

### FEATURE.md
Living documentation showing current intended state of a feature. Updated as the feature evolves. Contains:
- Metadata and ownership
- Files touched
- Problem/goals/non-goals
- Intended state
- Architecture
- Changelog of specs

### spec-research.md
Research output for each spec (lives in spec folder). Contains:
- Problem context for this spec
- Exploration findings (patterns, key files, integration points)
- Key decisions with rationale
- Interface contracts (types, function signatures)
- Test plan (derived from contracts: happy path, edge cases, error cases, mocks)
- Files to create/modify
- Edge cases to handle

### spec.md
Requirements document (~200-400 lines target, 600 max). Contains:
- Overview
- Out of scope
- Functional requirements with success criteria
- Technical design

### checklist.md
Progress tracking for implementation. Contains:
- Tasks organized by phase (1.0 tests, 1.1 impl, 1.2 review)
- Checkbox status
- Session notes

> **Note:** Phase numbering uses 1.0/1.1/1.2 for all specs. The "1" refers to the TDD cycle (tests → impl → review), not the spec sequence number.

## Naming Conventions

- **Domains**: lowercase, hyphenated (e.g., `notifications`)
- **Features**: lowercase, hyphenated (e.g., `user-notifications`)
- **Specs**: numbered prefix + name (e.g., `01-foundation`, `02-advanced`)

## Workflows

### Phase 1: Research
1. Use `research` skill
2. Explore codebase, dialog with user
3. Design approach, define interface contracts
4. Derive test plan from contracts
5. Decompose into spec units with **explicit dependencies** (Blocks/Blocked By)
6. Create FEATURE.md + spec-research.md for ALL decomposed specs
7. Commit research artifacts to main
8. **Create Tasks** for each spec with blockedBy relationships
9. **Handoff:** User runs `/orchestrate` in fresh session to begin execution

### Phase 2: Orchestration (Fresh Context)
1. Use `orchestrate` skill with feature path
2. Reads committed FEATURE.md and spec-research.md files
3. Checks TaskList for spec Tasks and their dependencies
4. Spawns spec-executor agents for unblocked specs
5. Re-run `/orchestrate` as specs complete to dispatch next wave

### Phase 3: Spec (Autonomous via spec-executor)
1. spec-executor runs `spec` skill (autonomous mode)
2. Parallel drafting → QC validation (autonomous)
3. **Skip human review** if all QC passes; escalate via Andon if blocked
4. Generate checklist
5. Commit spec.md + checklist.md to main

### Phase 4: Implement (Parallel FR Execution via spec-executor)
1. spec-executor runs `implement` skill with wave-based FR parallelism
2. Analyze FR dependencies, build wave structure
3. Phase X.0: Tests first (parallel sub-agents for independent FRs)
4. Phase X.1: Implementation (parallel sub-agents for independent FRs)
5. Phase X.2: Review (sequential QC gates)
6. Commit and merge to main

---

## Autonomous Execution Model

### Human Involvement by Phase

| Phase | Human Role | Automation Role |
|-------|------------|-----------------|
| **Research** | Heavy - scope decisions, architecture choices, contract approval | Explore, suggest, document |
| **Orchestration** | Trigger only - run `/orchestrate` | Read artifacts, dispatch agents, track progress |
| **Spec** | Exception only (Andon) | Write against contracts, validate via QC |
| **Implement** | Exception only (Andon) | Execute TDD, validate via QC, review via agents |

### Andon Escalation Pattern

When automation encounters a fundamental blocker, it STOPS and escalates:

```
{PHASE} BLOCKED

Issue: [what went wrong]
Details: [specific problem]

Impact: [what cannot proceed]

Options:
1. Return to earlier phase to fix
2. Proceed with assumption: [state it]
3. Descope: [what to remove]

Need decision to proceed.
```

**Escalation Triggers:**
- QC fails 2+ iterations
- Interface contract gap discovered
- Core architectural assumption invalid
- Data source doesn't exist

---

## Parallel Execution Architecture

### Task-Based Spec Dependencies

Research creates Tasks with explicit dependencies:

```
┌─────────────────┐
│ 01-foundation   │ (no blockers - start immediately)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐  ┌────────┐
│02-data │  │04-other│ (blocked by 01)
└───┬────┘  └────────┘
    │
    ▼
┌────────┐
│ 03-ui  │ (blocked by 01, 02)
└────────┘
```

### Agent Hierarchy

```
Main Agent (conversation)
    │
    ├─ Manages TaskList (spec-level)
    │
    ├─ Dispatches spec-executor agents in parallel
    │
    ▼
┌─────────────────┬─────────────────┬─────────────────┐
│ spec-executor   │ spec-executor   │ spec-executor   │
│ (01-foundation) │ (02-data)       │ (04-other)      │
└────────┬────────┴────────┬────────┴────────┬────────┘
         │                 │                 │
         ▼                 ▼                 ▼
    FR sub-agents     FR sub-agents     FR sub-agents
    (wave-based)      (wave-based)      (wave-based)
```

### FR-Level Wave Execution

Within each spec, FRs execute in waves:

**Wave 1:** Independent FRs (parallel)
**Wave 2:** FRs depending on Wave 1 (parallel)
**Wave 3:** FRs depending on Wave 2 (parallel)
...

```
FR1 ────┬───► FR2 ───► FR4
FR3 ────┘         └──► FR5

Wave 1: FR1, FR3 (parallel)
Wave 2: FR2 (after FR1, FR3)
Wave 3: FR4, FR5 (after FR2)
```

### spec-executor Agent

Purpose-built orchestrator that:
1. Runs spec skill (autonomous mode)
2. Builds FR dependency graph from spec-research.md
3. Dispatches parallel sub-agents for FR work
4. Manages wave-based execution
5. Runs Phase X.2 review
6. Reports completion to parent

**Key rule:** spec-executor ORCHESTRATES, it does NOT implement code directly.

---

## QC in the Pipeline

The full pipeline (research → orchestrate → spec → implement) always uses the **full QC chain**. If work is going through orchestration and spec-executors, it warrants full validation. No scope-based shortcuts within the pipeline.

Lighter QC is reserved for the **lightweight path** (see below) where the human is closer to the loop.

## Bug Fixes / Enhancements (Lightweight Path)

For small bugfixes and minor enhancements (<100 lines) that don't warrant the full pipeline:

**Use the `/quick-fix` skill.** This provides:
1. Micro-research (scan FEATURE.md for context, not full exploration)
2. Plan mode for the fix
3. Implementation with tests-are-current discipline (not strict TDD)
4. Single pr-review-toolkit pass
5. **FEATURE.md spot-check** before commit (mandatory — prevents drift)
6. Clean commit with appropriate prefix

### Choosing the Right Path

| Signal | Path |
|--------|------|
| Small bug, clear root cause | `/quick-fix` |
| Minor enhancement, <100 lines | `/quick-fix` |
| New feature, needs decomposition | `/research` → full pipeline |
| Cross-cutting, 5+ files, new patterns | `/research` → full pipeline |
| Started as quick-fix, scope grew | Stop, switch to `/research` |

### FEATURE.md Reconciliation

After accumulated lightweight changes, FEATURE.md may drift. Periodically (or before starting new feature work in an area), review the git log since the last FEATURE.md update and reconcile:

```
git log --oneline -- {files-in-feature-area} | head -20
```

If significant drift: update FEATURE.md to reflect current reality.

---

## Progressive Disclosure

Load only what you need:
- Quick overview? Read FEATURE.md
- Context/decisions/tests? Read spec-research.md (in spec folder)
- Requirements? Read spec.md
- Progress? Read checklist.md

---

## Commit Discipline

| Order | Prefix | Created By | Purpose |
|-------|--------|------------|---------|
| 1 | `research` | research skill | FEATURE.md + all spec-research.md |
| 2 | `spec` | spec skill | spec.md + checklist.md |
| 3 | `test` | implement skill | Test commits (red phase) |
| 4 | `feat` | implement skill | Implementation commits (green phase) |
| 5 | `fix` | implement skill | Review fix commits |
| 6 | `docs` | implement skill | Documentation updates (checklist, FEATURE.md) |

### Commit Examples

```
research({feature}): add FEATURE.md and spec-research for {N} specs
spec({NN}-{spec}): add spec and checklist
test(FR1): add validation tests
feat(FR1): implement validation
fix({spec}): address review feedback
docs({spec}): update checklist and FEATURE.md
```

### Spec Scoping

| Metric | Target | Guideline Max |
|--------|--------|---------------|
| FRs per spec | 3-5 | 8 |
| Lines per spec | 200-400 | 600 |
| Specs per research | 2-4 | 6 |

> These are guidelines, not hard gates. A naturally cohesive 7-FR spec is preferable to two artificially split specs with cross-dependencies. The real constraint: can one agent hold this in context and implement it well?

### Commit Granularity

Commit granularity should match spec size:

| Spec Size | Test Commits | Impl Commits | Example |
|-----------|-------------|--------------|---------|
| Small (1-3 FRs) | 1 commit (all tests) | 1 commit (all impl) | `test(01-auth): add tests`, `feat(01-auth): implement` |
| Medium (4-6 FRs) | Per-FR or grouped | Per-FR or grouped | Agent's judgement |
| Large (7+ FRs) | Per-FR | Per-FR | `test(FR1): ...`, `feat(FR1): ...` |

The principle remains: tests committed before implementation. The granularity is flexible.

### Anti-patterns

- Implementation commits before test commits
- Squashing all commits (loses TDD sequence visibility)
- Skipping Phase X.2 review

### Parallel Execution Anti-patterns

- **No dependency tracking** - Decomposing without Blocks/Blocked By columns
- **Sequential when parallel possible** - Running independent specs one-by-one
- **spec-executor implements directly** - Orchestrator should spawn sub-agents, not write code
- **Skipping FR dependency analysis** - May cause conflicts in parallel FR execution
- **Proceeding after Andon** - Building on broken foundation; must escalate and wait
- **Running review agents in parallel** - Phase X.2 steps are sequential gates
