---
name: implement
description: Implements specifications using TDD methodology with quality review. Use when implementing a spec, writing code from requirements, following TDD workflow. Includes test-first development, implementation, and thorough code review before PR.
allowed-tools:
  - Task
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - TodoWrite
---

# Implement

Implements specifications using TDD methodology: Phase X.0 (tests first), Phase X.1 (implementation), Phase X.2 (review).

## When to Use This Skill

- Implementing a spec after spec has been created
- Following TDD workflow
- Executing Phase X.0 (test foundation)
- Executing Phase X.1 (implementation)
- Phase X.2 (quality review before merge)

## Workflow Overview

```
Read spec.md + checklist.md + spec-research.md
    │
    ▼
Phase X.0: Test Foundation (all FRs)
    │
    ├─ Write failing tests for each FR
    ├─ Commit with test(FR{N}) prefix
    ├─ GATE: red-phase-test-validator (must PASS)
    │
    ▼
Phase X.1: Implementation (all FRs)
    │
    ├─ Implement to make tests pass
    ├─ Commit with feat(FR{N}) prefix
    │
    ▼
Phase X.2: Review (all 4 steps mandatory)
    │
    ├─ Step 0: spec-implementation-alignment (must PASS)
    ├─ Step 1: pr-review-toolkit:review-pr (6 agents)
    ├─ Step 2: Address feedback, fix issues
    ├─ Step 3: test-optimiser (final pass)
    │
    ▼
Implementation complete
```

---

## Critical Stop Guidance (Andon)

During implementation, if you encounter a disconnect that breaks fundamental spec assumptions, **stop and escalate**.

### Stop Conditions

- Interface contract requires data that doesn't exist and can't be derived
- Spec assumes dependency/provider that doesn't exist
- Core data flow is impossible as designed

### When Triggered

Do NOT work around silently. Escalate:

```
IMPLEMENTATION BLOCKED

Spec assumes: [quote the specific requirement]
Reality: [what actually exists or doesn't]

This breaks: [interface contract / data flow / core assumption]

Options:
1. Return to Spec/Research to address
2. Descope this requirement
3. [Other options if apparent]

Need decision to proceed.
```

### What IS Critical (Stop)

| Scenario | Action |
|----------|--------|
| Spec requires field X, API doesn't have it, can't derive | STOP |
| Spec says "receives props" but no provider exists | STOP |
| Interface contract assumes data source that doesn't exist | STOP |
| Core architectural assumption is invalid | STOP |

### What's NOT Critical (Proceed with Note)

| Scenario | Action |
|----------|--------|
| Missing dependency but can implement without it | Note it, proceed |
| Typo in spec | Fix inline |
| Unclear requirement | Clarify, proceed |
| Minor detail not specified | Make reasonable choice, document |

### The Test

Does this break the interface contracts or fundamental assumptions?
- **Yes** → STOP and escalate
- **No** → Note issue, proceed

### After Escalation

Based on user decision:
- **Resume:** Workaround approved, continue with modified approach
- **Return:** Go back to Spec/Research to fix the gap properly
- **Descope:** Remove the blocked requirement, continue with reduced scope

---

## Stage 1: Load Context

### Read Spec Artifacts

1. Read `spec.md` for requirements (FRs with success criteria)
2. Read `checklist.md` for task list
3. Read `spec-research.md` for implementation context

### Using Research Context

The `spec-research.md` contains:
- **Interface Contracts** - Types and function signatures
- **Key Decisions** - Rationale for approach
- **Test Plan** - Test cases derived from contracts

Use these as the source of truth for implementation.

---

## Stage 1.5: FR Dependency Analysis (for Parallel Execution)

When running as spec-executor (orchestrating sub-agents), analyze FR dependencies before execution.

### Identify FR Dependencies

Read spec-research.md Test Plan section. For each FR, determine:
- Does this FR's implementation depend on types/functions from another FR?
- Does this FR's test require mocks that another FR provides?

### Build FR Dependency Graph

| FR | Depends On | Can Parallel With |
|----|------------|-------------------|
| FR1 | - | FR3 |
| FR2 | FR1 | - |
| FR3 | - | FR1 |

### Execution Waves

Group FRs into waves based on dependencies:

**Wave 1:** FRs with no dependencies (FR1, FR3)
**Wave 2:** FRs depending only on Wave 1 (FR2)
**Wave 3:** FRs depending on Wave 2 (...)

This wave structure drives parallel sub-agent dispatch.

---

## Stage 2: Determine Phase

Check checklist.md status:
- If Phase X.0 tasks incomplete OR Test Design Validation incomplete: Start/continue Phase X.0
- If Phase X.0 + validation complete, Phase X.1 incomplete: Start/continue Phase X.1
- If Phase X.1 complete, Phase X.2 incomplete: Run Phase X.2 Review
- If all complete: Confirm completion with user

---

## Phase X.0: Test Foundation

**Goal**: Write failing tests that verify each Functional Requirement.

### For Each FR in spec.md:

1. **Identify test cases** from Success Criteria
2. **Write test file** (or add to existing)
3. **Run tests** to verify they fail appropriately
4. **Update checklist** marking test tasks complete

### Test Guidelines:

- One test file per component/module when practical
- Test names should reference FR: `test_FR1_accepts_valid_input`
- Focus on behavior, not implementation
- Include edge cases from spec

### Parallel Execution (Spec-Executor Mode)

When orchestrating via spec-executor, dispatch FR test work in parallel:

**Wave-Based Dispatch:**

1. **Wave 1** - Launch parallel sub-agents for independent FRs:
   ```
   Task(subagent_type="general-purpose",
        description="FR1 tests",
        prompt="Write tests for FR1 per spec. File: {test-file}")

   Task(subagent_type="general-purpose",
        description="FR3 tests",
        prompt="Write tests for FR3 per spec. File: {test-file}")
   ```

2. **Wait** for Wave 1 completion

3. **Wave 2** - Launch sub-agents for newly unblocked FRs:
   ```
   Task(subagent_type="general-purpose",
        description="FR2 tests",
        prompt="Write tests for FR2 per spec. FR1 types now available.")
   ```

4. **Continue** until all FR tests complete

5. **Run red-phase-test-validator** on combined test output

### Commits (Phase X.0):

One commit per FR test group. Use the standard commit format (see Commit Discipline section):

```bash
git add {test-file-path}
git commit -m "test(FR1): add input validation tests ..."  # HEREDOC format with Co-Author-By
```

Stage only test files, not implementation files.

### Phase X.0 Completion:

Verify:
- [ ] All FRs have corresponding tests
- [ ] All tests fail (red phase)
- [ ] Test checklist items marked complete
- [ ] **GATE: red-phase-test-validator returns PASS** (see below)

### GATE: Test Design Validation

⚠️ **Do NOT proceed to Phase X.1 until this gate passes.**

Run the `red-phase-test-validator` agent:

```
subagent_type: "red-phase-test-validator"
description: "Validate test design quality"
prompt: "Validate the tests written for this spec:

Test files: {paths to test files}
Spec: {spec-path}/spec.md
Research: {spec-path}/spec-research.md

Check:
1. Spec alignment - all FR success criteria have tests
2. Assertion specificity - tests verify specific behavior
3. Mock discipline - mocks at boundaries, realistic data
4. Behavior focus - tests describe WHAT, not HOW

Report PASS or FAIL with specific issues."
```

**If PASS:** Proceed to Phase X.1

**If FAIL:**
1. Review specific issues (missing coverage, weak assertions, over-mocking)
2. Fix test design issues
3. Re-run validation
4. Repeat until PASS (max 2 iterations)

**Why this matters:** Weak tests lead to implementation guided by weak contracts. Tests failing ≠ tests well-designed. This gate catches no-op tests, missing coverage, and poor mock discipline before you implement against them.

---

## Phase X.1: Implementation

**Goal**: Implement code to make tests pass.

### For Each Failing Test:

1. **Read test** to understand expected behavior
2. **Implement minimum code** to pass the test
3. **Run test** to verify it passes
4. **Refactor** if needed (tests should still pass)
5. **Update checklist** marking impl tasks complete

### Implementation Guidelines:

- Follow patterns from spec-research.md
- Reference files listed in Technical Design
- Keep changes minimal and focused
- Target 50-150 lines per FR (200 max)

### Parallel Execution (Spec-Executor Mode)

Same wave-based pattern as Phase X.0:

1. Dispatch Wave 1 implementation sub-agents in parallel
2. Wait for completion
3. Dispatch Wave 2 (now unblocked)
4. Continue until all FRs implemented
5. Run full test suite to verify integration

### Commits (Phase X.1):

One commit per FR implementation. Use the standard commit format (see Commit Discipline section):

```bash
git add {implementation-file-path}
git commit -m "feat(FR1): implement validation logic ..."  # HEREDOC format with Co-Author-By
```

Stage only implementation files, NOT test files (they were committed in X.0).

### Phase X.1 Completion:

Verify:
- [ ] All tests pass (green phase)
- [ ] All implementation checklist items complete
- [ ] No regressions in existing tests

**Next: Phase X.2 is MANDATORY.** Do not commit or skip to completion.

---

## Phase X.2: Review

⚠️ **MANDATORY GATE** - Do NOT commit until this phase is complete.

**Goal**: Quality gate before PR. Catch issues that would be found in human review.

**Always run all four steps.** No scope-based shortcuts - every change gets full QC.

### Step 0: Spec-Implementation Alignment

**Run this FIRST.** No point reviewing code quality if it's the wrong code.

Run the `spec-implementation-alignment` agent:

```
subagent_type: "spec-implementation-alignment"
description: "Verify implementation matches spec"
prompt: "Validate implementation alignment:
- spec.md: {spec-path}/spec.md
- spec-research.md: {spec-path}/spec-research.md
- checklist.md: {spec-path}/checklist.md

Verify:
1. Each FR success criterion is satisfied by the implementation
2. Types/signatures match interface contracts
3. No scope creep (features added beyond spec)
4. No scope shortfall (requirements quietly dropped)

Report PASS or FAIL with specific gaps."
```

**If PASS:** Proceed to Step 1 (code quality)

**If FAIL:**
1. Review specific gaps
2. Fix alignment issues (or escalate if spec needs updating)
3. Re-run alignment check
4. Repeat until PASS (max 2 iterations)

**If stuck:** Escalate to user - may need spec revision.

### Step 1: Comprehensive PR Review

Run the `pr-review-toolkit:review-pr` skill for multi-agent analysis:

```
Use Skill tool:
skill: "pr-review-toolkit:review-pr"
```

This runs 6 specialized agents:

| Agent | Focus |
|-------|-------|
| code-reviewer | CLAUDE.md compliance, style, bugs, quality |
| silent-failure-hunter | Error handling, silent failures, missing logging |
| pr-test-analyzer | Test coverage quality, critical gaps, edge cases |
| comment-analyzer | Comment accuracy, doc completeness |
| type-design-analyzer | Encapsulation, invariants, type quality (1-10 ratings) |
| code-simplifier | Readability, unnecessary complexity, redundancy |

### Step 2: Address Feedback

**If issues found:**
1. Review each agent's findings
2. Fix issues by priority (critical → high → medium)
3. Re-run tests to ensure fixes don't break anything
4. Commit fixes: `fix({spec}): {description}`

**If no significant issues:**
- Proceed to Step 3

### Step 3: Test Quality Optimization

Run the `test-optimiser` agent as a final pass:

```
subagent_type: "test-optimiser"
description: "Optimize test quality"
prompt: "Review the tests for this spec implementation.

Focus on recently modified test files. Ensure tests provide genuine confidence:
- Tests would fail if implementation were broken
- Behavior tested, not implementation details
- Edge cases and error paths covered
- No pageantry testing (tests that look good but verify nothing)

Optimize any weak tests found."
```

### Handle Final Results

**If test-optimiser suggests changes:**
1. Review suggested improvements
2. Apply changes that strengthen test confidence
3. Re-run tests
4. Commit: `fix({spec}): strengthen test assertions`

**If all passes:**
1. Confirm: "Review passed. Implementation complete."

---

## Stage 3: Completion

After review complete, update documentation and finalize.

### 3.1: Verify Checklist Complete

Read `{spec-path}/checklist.md` and verify all tasks marked `[x]`:
- [ ] All Phase X.0 tasks complete
- [ ] All Phase X.1 tasks complete
- [ ] All Phase X.2 tasks complete

If any tasks unmarked, update them now.

### 3.2: Add Session Notes

Append to checklist.md:

```markdown
## Session Notes

**{date}**: Implementation complete.
- Phase X.0: {N} test commits
- Phase X.1: {N} implementation commits
- Phase X.2: Review passed, {N} fix commits (if any)
- All tests passing.
```

### 3.3: Update FEATURE.md

Read `features/{domain}/{feature}/FEATURE.md` and update:

1. **Changelog section** - Update spec entry:
   ```markdown
   ### {NN}-{spec-name}
   - **Status**: Complete
   - **Date**: {date}
   - **Commits**: test(FR1-N), feat(FR1-N), fix (if any)
   ```

2. **Files Touched section** - Add any new files created

### 3.4: Commit Documentation Updates

```bash
git add {spec-path}/checklist.md features/{domain}/{feature}/FEATURE.md
git commit -m "$(cat <<'EOF'
docs({NN}-{spec-name}): update checklist and FEATURE.md

- Mark all checklist tasks complete
- Add session notes
- Update FEATURE.md changelog

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
git status  # Verify clean working tree
```

### 3.5: Confirm with User

```
"Implementation complete for {NN}-{spec-name}.

Commits (in TDD order):
1. test(FR1-N): tests for all FRs
2. feat(FR1-N): implementations for all FRs
3. fix({spec}): review fixes (if any)
4. docs({spec}): documentation updates

Documentation Updated:
  ✓ checklist.md - all tasks marked complete, session notes added
  ✓ FEATURE.md - changelog updated

All tests passing. Git state clean.

Next step: Proceed to next spec using `spec` then `implement` skills"
```

---

## Checklist Management

Use Edit tool to update checklist.md as you work:

```markdown
# Before
- [ ] Task description

# After
- [x] Task description
```

Add session notes at bottom:
```markdown
## Session Notes

**2025-01-05**: Completed X.0 and X.1. Review found 2 issues, both fixed.
```

---

## Commit Discipline

Each spec follows this commit sequence:

| Order | Prefix | Phase | Purpose | Created By |
|-------|--------|-------|---------|------------|
| 1 | `spec` | Setup | Spec artifacts | spec skill |
| 2 | `test` | X.0 | Test commits (red phase) | implement skill |
| 3 | `feat` | X.1 | Implementation commits (green phase) | implement skill |
| 4 | `fix` | X.2 | Review fix commits (if needed) | implement skill |
| 5 | `docs` | Completion | Documentation updates | implement skill |

**Note:** The `spec()` commit is created by the spec skill before implement runs.

### Commit Format (REQUIRED)

Always use HEREDOC format with Co-Author-By:

```bash
git add {specific-files}  # Never use git add -A
git commit -m "$(cat <<'EOF'
{prefix}({scope}): {concise description}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
git status  # Verify commit succeeded
```

### Anti-Patterns

- **NEVER** bundle tests and implementation in one commit
- **NEVER** use `git add -A` or `git add .` - stage specific files
- **NEVER** skip `git status` verification after commit
- **NEVER** commit implementation before tests (breaks TDD visibility)

---

## Key Principles

- **Tests Before Implementation**: Always write tests before code
- **Small Commits**: One logical change per commit, reference FR number
- **Review Before Merge**: Phase X.2 catches issues early
- **Commit Discipline**: Follow the sequence in Commit Discipline section
- **Checklist Discipline**: Update immediately after completing each item
- **Documentation Current**: Update checklist and FEATURE.md before completion
- **Parallelize independent FRs** - Use sub-agents for FRs with no dependencies
- **Wave-based execution** - Group FRs by dependency depth, execute waves in parallel
- **Integration verification** - Always run full test suite after parallel implementation
