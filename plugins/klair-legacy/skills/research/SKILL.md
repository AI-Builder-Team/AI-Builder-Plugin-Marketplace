---
name: research
description: Explores a problem space, gathers context, designs approach, and decomposes into implementable specs. Use when starting new work, investigating issues, planning features, or decomposing large changes. This is the "fuzzy front end" where exploration and human dialog happen.
allowed-tools:
  - Task
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Research

The first phase of development: understand the problem, explore the codebase, design the approach, and decompose into spec-able units.

## When to Use This Skill

- Starting work on a new feature or enhancement
- Investigating a bug or issue
- Planning a refactor or migration
- Decomposing a large change into smaller pieces
- Any time you need to understand before you build

## Workflow Overview

```
Understand Request
       │
       ▼
Explore Codebase ──────► Dialog with User
       │                      │
       ▼                      ▼
Architectural Design ◄───► Scope Decisions
       │
       ▼
Interface Contracts ───► Test Planning (from contracts)
       │
       ▼
Decompose into Specs
       │
       ▼
Create FEATURE.md
       │
       ▼
Create ALL spec-research.md files
       │
       ▼
QC Validation (research-qc agent)
       │
       ├─ FAIL → Address issues, re-run QC
       │
       ▼
Commit to main
       │
       ▼
Create Spec Tasks
       │
       ▼
Output: Research complete, ready for spec
```

---

## Step 1: Understand the Request

1. **Clarify the goal**: What problem are we solving? What's the desired outcome?
2. **Identify constraints**: Timeline, dependencies, existing patterns to follow
3. **Check existing work**: Is there a FEATURE.md? Previous specs? Related features?

**Ask if unclear:**
```
Use AskUserQuestion if the request is ambiguous:
- "What's the primary goal here?"
- "Are there constraints I should know about?"
```

---

## Step 2: Explore the Codebase

Use the built-in **Explore** agent (via Task tool) for thorough investigation.

**Launch exploration:**
```
subagent_type: "Explore"
description: "Explore [area] for [purpose]"
prompt: "I need to understand [specific question].
Look for: [patterns, files, implementations].
Report: key files, existing patterns, integration points."
```

**What to explore:**
- Similar features or implementations
- Existing patterns and conventions
- Integration points and dependencies
- Test patterns and coverage

**Thoroughness levels:**
- `quick` - Basic file search, known locations
- `medium` - Moderate exploration, multiple areas
- `very thorough` - Comprehensive analysis

### API Exploration Prompt

When exploring backend endpoints, document the full response schema:

```
Find the backend endpoints for {feature} data.

For each endpoint discovered:
1. Document the URL, method, and parameters
2. List ALL fields in the response schema (read actual code/types)
3. Note any computed or derived fields
4. Flag if response doesn't include fields the UI/feature seems to need

Output format:

## Endpoint: {path}
**Method:** GET/POST
**Parameters:** {list}

**Response Schema:**
| Field | Type | Notes |
|-------|------|-------|

**Potential Gaps:** {fields the UI/feature needs but aren't in the response}
```

### Pattern Exploration Prompt

When finding reference patterns to follow, trace the complete data flow:

```
Find how {similar feature} implements {capability}.

Document:
1. Key files and their responsibilities
2. Data flow: where does data come from?
3. Props/interfaces: what does each component expect?
4. For each data input, trace to its source (API call, computed, parent prop)

Output format:

## Pattern: {name}
**Key Files:** {list}

**Data Flow:**
{component}
  ← receives: {props}
  ← from: {parent}
  ← which gets it from: {API/hook/context}
```

---

## Step 3: Dialog with User (Interactive Feedback)

**Use AskUserQuestion at key decision points.** Present findings first, then ask.

### Decision Point 1: Scope Confirmation

After initial exploration, confirm scope:

```
"Based on exploration, this involves:
- [Component A] - [what needs to change]
- [Component B] - [what needs to change]
- [Component C] - [what needs to change]

Should we include all of these, or narrow the scope?"

Options:
- Include all (comprehensive)
- Focus on [subset] first
- Other
```

### Decision Point 2: Architectural Approach

When multiple patterns or approaches exist:

```
"Found two approaches in the codebase:

1. **[Pattern A]** - Used in [X, Y]
   - Pros: [...]
   - Cons: [...]

2. **[Pattern B]** - Used in [Z]
   - Pros: [...]
   - Cons: [...]

Which approach fits better for this change?"
```

### Decision Point 3: Test Strategy

For testing approach:

```
"Existing tests use [pattern/framework].

Options:
- Follow existing pattern
- Use [alternative] because [reason]
- Mix: [specific suggestion]"
```

### Guidelines for AskUserQuestion:

- **Present findings first** - Show your work before asking
- **Concrete options** - 2-4 specific choices, not open-ended
- **Don't over-ask** - Save for real decision points
- **Include context** - Why does this decision matter?

---

## Step 4: Architectural Design

Document the chosen approach:

1. **High-level design**: How components interact
2. **Key decisions**: What was decided and why
3. **Files affected**: What will be created/modified
4. **Integration points**: How this connects to existing code

---

## Step 5: Interface Contracts

Define the interfaces before implementation:

1. **Types**: Key data structures and interfaces
2. **Function signatures**: Input/output contracts
3. **API changes**: New or modified endpoints
4. **Dependencies**: What depends on what

This enables clear boundaries for decomposition AND test planning.

### Source Tracing Requirement

**For each field in each interface, document its source:**

- API endpoint + field name
- Computed from X
- Passed as prop from Y
- If source unknown: mark ⚠️ TBD

**TBD items must be resolved before decomposition:**
- Identify real source, OR
- Add to backend work scope, OR
- Descope the field

**Example formats:**

Inline annotation:
```typescript
interface SupportMetrics {
  total_tickets: number;      // ← API: /get-metrics.total_tickets
  solved_count: number;       // ← ⚠️ TBD - needs resolution
}
```

Or companion table:
```markdown
### SupportMetrics Sources
| Field | Source |
|-------|--------|
| total_tickets | /get-metrics.total_tickets |
| solved_count | ⚠️ TBD |
```

---

## Step 6: Test Planning (from Interface Contracts)

**After Interface Contracts are defined**, derive test cases from them.

For each function contract, identify:

| Contract Element | Test Cases to Derive |
|-----------------|---------------------|
| Function signature | Happy path with valid inputs |
| Input types | Edge cases (empty, null, boundaries) |
| Return type | Expected output verification |
| Dependencies | Mock strategies |
| Error conditions | Error case handling |

**Output format:**

```markdown
## Test Plan

### {function_name}
**Signature:** `{signature}`

**Happy Path:**
- [ ] {test case description}

**Edge Cases:**
- [ ] Empty input: {expected behavior}
- [ ] Null handling: {expected behavior}
- [ ] Boundary: {expected behavior}

**Error Cases:**
- [ ] Network failure: {expected behavior}
- [ ] Invalid input: {expected behavior}

**Mocks Needed:**
- {dependency}: {mock strategy}
```

This test plan feeds directly into Phase X.0 of implement.

---

## Step 7: Decompose into Specs

Break work into implementable units:

### Decomposition Principles:

- **Single responsibility**: Each spec does one thing
- **Clear boundaries**: Minimal overlap between specs
- **Testable in isolation**: Can verify without other specs
- **PR reviewable**: Each spec produces a mergeable PR (3-5 FRs, ~200-400 lines of spec → ~300-600 lines of code)
- **Complete in isolation**: Each spec adds value even if other specs are delayed

### Ask User for Decomposition Preference:

```
"This work can be decomposed as:

Option A: By layer
1. Data layer changes
2. Business logic
3. UI updates

Option B: By feature slice
1. Core functionality
2. Edge cases
3. Polish/optimization

Option C: By dependency order
1. [Foundation piece]
2. [Depends on 1]
3. [Depends on 2]

Which decomposition makes more sense?"
```

### Document Each Spec Unit:

For each decomposed piece, create a dependency-aware table:

| Spec | Description | Blocks | Blocked By | Complexity |
|------|-------------|--------|------------|------------|
| 01-foundation | Core types and interfaces | 02, 03 | - | M |
| 02-data-layer | API integration | 03 | 01 | M |
| 03-ui | Component implementation | - | 01, 02 | L |

**Column definitions:**
- **Spec**: Numbered identifier (NN-name format)
- **Description**: Brief summary of what the spec covers
- **Blocks**: Which specs depend on this one (enables parallel execution planning)
- **Blocked By**: Which specs must complete before this one can start
- **Complexity**: S (small), M (medium), L (large)

This table enables Task-based parallel execution after research completes.

### Coverage Verification

**Before finalizing decomposition, verify coverage:**

For each data source identified in interface contracts:
- If existing code → note "existing" (no spec needed)
- If new code needed → assign to a specific spec
- If neither → flag as orphaned dependency

For each "Deferred to X" in Out of Scope:
- Verify X exists in the decomposition

**Checklist before finalizing:**
- [ ] Every "needs new code" source has a spec assigned
- [ ] Every deferred item points to a real spec
- [ ] No spec depends on something that isn't existing or spec'd
- [ ] No ⚠️ TBD items remain in interface contracts (resolve or escalate)
- [ ] No ⚠️ Unassigned items remain in Out of Scope
- [ ] Each spec has 3-5 FRs (max 8) for reasonable PR size
- [ ] Each spec is independently mergeable (no dangling dependencies)
- [ ] Dependency graph has no cycles (validate Blocks/Blocked By columns)

---

## Step 8: Create FEATURE.md

**If new feature:**
1. Create `features/{domain}/{feature}/FEATURE.md`
2. Use [FEATURE-TEMPLATE.md](templates/FEATURE-TEMPLATE.md)
3. Fill in based on research findings

**If existing feature:**
1. Update sections based on new understanding
2. Keep as "intended final state" (not incremental changes)

---

## Step 9: Create ALL Spec Structures

Create folders and `spec-research.md` for ALL decomposed specs:

```bash
# Create all spec folders
mkdir -p features/{domain}/{feature}/specs/01-{spec-name}
mkdir -p features/{domain}/{feature}/specs/02-{spec-name}
mkdir -p features/{domain}/{feature}/specs/03-{spec-name}
# ... for each decomposed spec
```

**Output `spec-research.md`** in EACH spec folder:

Use [spec-research-template.md](templates/spec-research-template.md).

Each document captures (for THAT spec):
- Problem context
- Exploration findings
- Key decisions (with rationale)
- Interface contracts
- Test plan (derived from contracts)
- Files to reference

---

## Step 10: QC Validation

**Before committing, spawn the research-qc agent to validate outputs.**

### Launch QC Agent

```
subagent_type: "research-qc"
description: "Validate research outputs"
prompt: "Validate the research outputs for feature at:
- FEATURE.md: features/{domain}/{feature}/FEATURE.md
- Specs directory: features/{domain}/{feature}/specs/

Read FEATURE.md and all spec-research.md files. Run all checks and report PASS or FAIL."
```

### Handle QC Results

**If PASS:**
- Proceed to commit (Step 11)

**If FAIL:**
1. Review the specific issues listed
2. Address each issue in the relevant files
3. Re-run the research-qc agent
4. Repeat until PASS (max 2-3 iterations)

**If stuck after 2-3 iterations:**
- Escalate to user with remaining issues
- User decides: fix manually, proceed with known gaps, or change approach

---

## Step 11: Commit Research Artifacts

Stage specific files and commit:

```bash
git add features/{domain}/{feature}/FEATURE.md
git add features/{domain}/{feature}/specs/*/spec-research.md
git commit -m "$(cat <<'EOF'
research({feature}): add FEATURE.md and spec-research for {N} specs

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

**Important:** Stage specific files, not `git add -A`.

---

## Step 12: Create Tasks and Handoff

### Create Spec Tasks

After research is committed, create Tasks for parallel spec execution:

For each spec in the decomposition table:
1. Use TaskCreate with subject "Spec + Implement {NN}-{name}"
2. Include spec path and description
3. Map Blocked By column to blockedBy parameter

Example:
```
TaskCreate:
  subject: "Spec + Implement 01-foundation"
  description: "Run spec and implement skills for features/{domain}/{feature}/specs/01-foundation"

TaskCreate:
  subject: "Spec + Implement 02-data-layer"
  description: "Run spec and implement skills for features/{domain}/{feature}/specs/02-data-layer"
  blockedBy: [task-id-of-01]

TaskCreate:
  subject: "Spec + Implement 03-ui"
  description: "Run spec and implement skills for features/{domain}/{feature}/specs/03-ui"
  blockedBy: [task-id-of-01, task-id-of-02]
```

Report to user:
- Task IDs created
- Dependency graph visualization
- Which tasks are immediately actionable (no blockers)
- **Handoff instruction:** Run `/orchestrate` in a fresh session

Example output:
```
"Created {N} spec tasks with dependencies:

Task IDs:
- #1: Spec + Implement 01-foundation (no blockers - ready)
- #2: Spec + Implement 02-data-layer (blocked by: #1)
- #3: Spec + Implement 03-ui (blocked by: #1, #2)

Dependency Graph:
01-foundation
    ├── 02-data-layer
    │       └── 03-ui
    └── 03-ui

Ready to execute: 01-foundation

NEXT STEP:
Start a fresh session and run:
  /orchestrate features/{domain}/{feature}

This will spawn spec-executor agents for all unblocked specs."
```

---

## Key Principles

- **Explore before deciding** - Don't assume, investigate
- **Dialog at decision points** - Use AskUserQuestion for real choices
- **Document decisions** - Capture rationale, not just conclusions
- **Test plan from contracts** - Derive tests from interface definitions
- **Decompose thoughtfully** - Right-sized specs enable parallel work
- **Track dependencies** - Blocks/Blocked By enables parallel execution
- **FEATURE.md is the north star** - It shows intended final state
- **spec-research.md is per-spec** - Each spec gets focused context
- **Clean handoff** - Committed artifacts before creating Tasks
