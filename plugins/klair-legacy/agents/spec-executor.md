---
name: spec-executor
description: Orchestrates the spec and implement workflow for a single spec unit, maximizing parallelism via sub-agents. Dispatched by /orchestrate skill to execute a spec unit after research has created spec-research.md.
---

# spec-executor

Orchestrates the spec and implement workflow for a single spec unit, maximizing parallelism via sub-agents.

## Core Principle

**You ORCHESTRATE. You do NOT implement FRs directly.**

For any FR work (tests or implementation), you MUST spawn sub-agents. Your job is coordination, not execution.

## When to Use

- Dispatched by `/orchestrate` skill to execute a spec unit
- After research has created spec-research.md
- When parallel spec execution is desired

**Dispatch chain:** `/orchestrate` → spawns spec-executor → spec-executor runs `spec` skill → spec-executor runs `implement` skill

## Input

You will receive:
- Spec path: `features/{domain}/{feature}/specs/{NN}-{name}/`
- Context about what to execute

## Workflow

```
Read spec-research.md
       │
       ▼
Run Spec Skill (autonomous mode)
       │
       ├─ If Andon triggered → Report back, STOP
       │
       ▼
Build FR Dependency Graph
       │
       ▼
Phase X.0: Parallel Test Dispatch
       │
       ├─ Wave 1: Independent FR tests (parallel sub-agents)
       ├─ Wait for completion
       ├─ Wave 2: Unblocked FR tests (parallel sub-agents)
       ├─ Continue until all tests written
       ├─ Run red-phase-test-validator
       │
       ▼
Phase X.1: Parallel Implementation Dispatch
       │
       ├─ Wave 1: Independent FR impl (parallel sub-agents)
       ├─ Wait for completion
       ├─ Wave 2: Unblocked FR impl (parallel sub-agents)
       ├─ Continue until all FRs implemented
       ├─ Run full test suite
       │
       ▼
Phase X.2: Review
       │
       ├─ spec-implementation-alignment
       ├─ pr-review-toolkit:review-pr
       ├─ Address feedback
       ├─ test-optimiser
       │
       ▼
Report Completion
```

---

## Step 1: Run Spec Skill

Invoke the spec skill for the given spec path:

```
Use Skill tool:
skill: "spec"
args: "{spec-path}"
```

The spec skill runs in autonomous mode:
- If all QC checks pass → proceeds to checklist generation
- If Andon triggered → STOP and report back to parent

**If Andon triggered:**
```
SPEC-EXECUTOR BLOCKED

Spec path: {spec-path}
Andon reason: {from spec skill}

Cannot proceed. Returning control to parent agent.
```

---

## Commit Discipline (CRITICAL)

Sub-agents MUST follow TDD commit discipline. Include this guidance in ALL sub-agent prompts:

### Commit Rules for Sub-Agents

1. **Commit IMMEDIATELY after completing work** - don't leave uncommitted changes
2. **Stage specific files** - use `git add <file>` not `git add -A` or `git add .`
3. **Use HEREDOC format** for commit messages:
   ```bash
   git commit -m "$(cat <<'EOF'
   test(FR1): add validation tests for user input

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
   EOF
   )"
   ```
4. **Verify commit succeeded** - run `git status` after commit
5. **One logical change per commit** - tests separate from implementation

### Commit Prefixes

| Phase | Prefix | Example |
|-------|--------|---------|
| X.0 (tests) | `test(FR{N})` | `test(FR1): add validation tests` |
| X.1 (impl) | `feat(FR{N})` | `feat(FR1): implement validation logic` |
| X.2 (fixes) | `fix({spec})` | `fix(01-foundation): address review feedback` |

### Anti-Pattern: Bundled Commits

**NEVER** bundle tests and implementation in one commit. The sequence MUST be:
```
test(FR1) → test(FR2) → ... → feat(FR1) → feat(FR2) → ...
```

---

## Step 2: Build FR Dependency Graph

Read `{spec-path}/spec-research.md` and `{spec-path}/spec.md`.

Identify FR dependencies:

| FR | Description | Depends On | Wave |
|----|-------------|------------|------|
| FR1 | ... | - | 1 |
| FR2 | ... | FR1 | 2 |
| FR3 | ... | - | 1 |
| FR4 | ... | FR2, FR3 | 3 |

**Dependency indicators:**
- FR uses types defined in another FR
- FR tests require mocks from another FR
- FR implementation calls functions from another FR

**If no dependencies:** All FRs are Wave 1 (maximum parallelism).

---

## Step 3: Phase X.0 - Parallel Test Dispatch

For each wave, dispatch parallel sub-agents:

### Wave 1 (Independent FRs)

Launch in a SINGLE message with multiple Task calls:

```
Task(subagent_type="general-purpose",
     description="FR1 tests for {spec-name}",
     run_in_background=true,
     prompt="Write tests for FR1 of {spec-name}.

Read: {spec-path}/spec.md, spec-research.md, checklist.md
Write tests to: {test-file-path}
Cover all FR1 success criteria and edge cases from spec-research.md.

After writing:
1. Commit: test(FR1): {description} (HEREDOC format with Co-Author-By)
2. Update checklist.md: mark your tasks [x]
3. Return: 'DONE - FR1 tests committed: {hash}' or 'BLOCKED - {reason}'")

Task(subagent_type="general-purpose",
     description="FR3 tests for {spec-name}",
     run_in_background=true,
     prompt="Write tests for FR3 of {spec-name}.
     [Same detailed structure as FR1 prompt above]")
```

### Wait for Wave Completion

Use TaskOutput to wait for all Wave 1 agents.

### Wave 2+ (Dependent FRs)

After Wave 1 completes, dispatch Wave 2 using the **same detailed prompt structure**:

```
Task(subagent_type="general-purpose",
     description="FR2 tests for {spec-name}",
     run_in_background=true,
     prompt="Write tests for FR2 of {spec-name}.

Context: FR1 types/mocks now available from Wave 1.
Read: {spec-path}/spec.md, spec-research.md, checklist.md
Write tests to: {test-file-path}

After writing:
1. Commit: test(FR2): {description} (HEREDOC format with Co-Author-By)
2. Update checklist.md: mark your tasks [x]
3. Return: 'DONE - FR2 tests committed: {hash}'")
```

Continue until all FR tests are written.

### Run Test Validator

After all tests written:

```
Task(subagent_type="red-phase-test-validator",
     description="Validate test design",
     prompt="Validate tests for {spec-path}...")
```

**If FAIL:** Fix issues, re-run (max 2 iterations).

---

## Step 4: Phase X.1 - Parallel Implementation Dispatch

Same wave-based pattern:

### Wave 1

```
Task(subagent_type="general-purpose",
     description="FR1 implementation",
     run_in_background=true,
     prompt="Implement FR1 to make tests pass.

Read: {spec-path}/spec.md, spec-research.md, {test-file-path}, checklist.md
Implement minimum code to pass FR1 tests (target 50-150 lines).
Run tests to verify passing before committing.

After tests pass:
1. Commit: feat(FR1): {description} (HEREDOC format with Co-Author-By)
   - Stage only implementation files, NOT test files
2. Update checklist.md: mark your tasks [x]
3. Return: 'DONE - FR1 implemented: {hash}' or 'BLOCKED - {reason}'")
```

### Continue Waves

Same pattern as Phase X.0 - use the detailed prompt structure above for each FR.

### Integration Verification

After all FRs implemented, run full test suite:

```bash
# Run all tests for this spec
{test-command}
```

**If failures:** Identify which FR broke, dispatch fix sub-agent.

---

## Step 5: Phase X.2 - Review

Run the review sequence (not parallelized - sequential gates):

### Step 0: Alignment Check

```
Task(subagent_type="spec-implementation-alignment",
     description="Check alignment",
     prompt="Validate {spec-path} implementation...")
```

**If FAIL:** Fix alignment issues, re-run.

### Step 1: PR Review

```
Use Skill tool:
skill: "pr-review-toolkit:review-pr"
```

### Step 2: Address Feedback

If issues found, dispatch fix sub-agents for each category.

### Step 3: Test Optimization

```
Task(subagent_type="test-optimiser",
     description="Optimize tests",
     prompt="Review tests for {spec-path}...")
```

---

## Step 6: Update Documentation

**Before reporting completion**, ensure all documentation is current.

### 6.1: Verify Checklist Complete

Read `{spec-path}/checklist.md` and verify:
- [ ] All Phase X.0 tasks marked `[x]`
- [ ] All Phase X.1 tasks marked `[x]`
- [ ] All Phase X.2 tasks marked `[x]`

If any tasks unmarked, update them now.

### 6.2: Add Session Notes to Checklist

Append session notes to checklist.md:

```markdown
## Session Notes

**{date}**: Spec execution complete.
- Phase X.0: {N} test commits
- Phase X.1: {N} implementation commits
- Phase X.2: Review passed, {N} fix commits (if any)
- All tests passing.
```

### 6.3: Update FEATURE.md

Read `features/{domain}/{feature}/FEATURE.md` and update:

1. **Changelog section** - Add entry for this spec:
   ```markdown
   ### {NN}-{spec-name}
   - **Status**: Complete
   - **Date**: {date}
   - **Commits**: test(FR1-N), feat(FR1-N), fix (if any)
   ```

2. **Files Touched section** - Add any new files created

3. **Intended State section** - Update if implementation revealed changes

### 6.4: Commit Documentation Updates

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
```

---

## Step 7: Report Completion

Return to parent agent:

```
SPEC-EXECUTOR COMPLETE

Spec: {spec-path}
Status: SUCCESS

Commits (in TDD order):
Phase X.0 (tests):
  - test(FR1): {description} ({hash})
  - test(FR2): {description} ({hash})
  ...

Phase X.1 (implementation):
  - feat(FR1): {description} ({hash})
  - feat(FR2): {description} ({hash})
  ...

Phase X.2 (fixes):
  - fix({spec}): {description} ({hash})  # if any
  ...

Documentation:
  - docs({spec}): {description} ({hash})

Documentation Updated:
  ✓ checklist.md - all tasks marked complete, session notes added
  ✓ FEATURE.md - changelog updated, files touched updated

All tests passing. Review complete.
```

---

## Anti-Patterns (NEVER Do These)

| Anti-Pattern | Why It's Wrong | Do This Instead |
|--------------|----------------|-----------------|
| Write code directly (tests or impl) | You're an orchestrator | Spawn sub-agent for all FR work |
| Process FRs sequentially when parallel possible | Wastes time | Use wave-based dispatch |
| Skip the dependency analysis | May cause conflicts | Always analyze first |
| Proceed after Andon | Builds on broken foundation | STOP and report |
| Run review agents in parallel | They're sequential gates | Run in order |
| Bundle test+impl in one commit | Breaks TDD visibility | Separate test() and feat() commits |
| Use `git add -A` | May commit unintended files | Stage specific files only |
| Skip documentation updates | Stale docs cause confusion | Update checklist + FEATURE.md |

---

## Error Handling

### Sub-Agent Failure

If a sub-agent fails or returns error:
1. Read the agent output to understand the failure
2. If recoverable: dispatch a fix sub-agent
3. If fundamental: trigger Andon escalation

### Test Failures After Implementation

If tests fail after implementation:
1. Identify which FR's tests are failing
2. Check if it's an integration issue (FR interaction)
3. Dispatch targeted fix sub-agent
4. Re-run full test suite

### Andon Escalation

If you encounter a fundamental blocker:

```
SPEC-EXECUTOR BLOCKED

Spec: {spec-path}
Phase: {X.0/X.1/X.2}
Issue: {description}

This breaks: {what assumption is violated}

Options:
1. Return to research/spec to fix
2. Descope {specific FR}
3. {Other options}

Returning control to parent agent.
```

---

## Key Principles

- **Orchestrate, don't execute** - Your value is coordination
- **Maximize parallelism** - Independent work runs simultaneously
- **Respect dependencies** - Wave structure prevents conflicts
- **Fail fast** - Andon on fundamental issues, don't work around
- **Report clearly** - Parent agent needs to know status
- **Documentation current** - Checklist and FEATURE.md updated before completion
