---
name: spec
description: Creates a technical specification from research. Use after the research skill to produce spec.md and checklist.md for a decomposed spec unit.
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

# Spec

Creates a detailed technical specification for one unit of work.

## When to Use This Skill

- After `research` skill has created research artifacts
- When creating spec.md and checklist.md for any decomposed spec
- To produce implementable artifacts

## Prerequisites

- **FEATURE.md exists** for the parent feature
- **spec-research.md exists** in the spec folder (created by research skill)

---

## Workflow Overview

```
Locate Feature + Spec
       │
       ▼
Verify spec-research.md exists
       │
       ▼
Gather Clarifications (upfront)
       │
       ▼
Parallel Draft Sections
       │
       ▼
Assemble Full Spec
       │
       ▼
Coherence Check (spec-coherence-checker)
       │
       ├─ FAIL (2x) → ESCALATE (Andon)
       │
       ▼
Autonomous Validation (or Human Review if interactive)
       │
       ▼
Generate Checklist
       │
       ▼
Checklist Validation (checklist-completeness-validator)
       │
       ├─ FAIL → Fix gaps
       │
       ▼
QC Validation (spec-qc agent)
       │
       ├─ FAIL → Address deltas, re-run QC
       │
       ▼
Commit to main
       │
       ▼
Output: Spec ready for implementation
```

---

## Step 1: Setup

### Locate Feature and Spec

1. Ask user which feature and spec to work on
2. Read `features/{domain}/{feature}/FEATURE.md`
3. List existing specs: `ls features/{domain}/{feature}/specs/`
4. Confirm target spec folder exists (created by research skill)

### Create tmp Directory

```bash
mkdir -p features/{domain}/{feature}/specs/{NN}-{spec-name}/tmp
```

---

## Step 2: Verify spec-research.md

The `research` skill should have already created `spec-research.md` for ALL specs. Verify it exists:

```bash
ls features/{domain}/{feature}/specs/{NN}-{spec-name}/spec-research.md
```

**If missing:** Run `research` skill first. Do not proceed without spec-research.md.

Read the spec-research.md to understand:
- Problem context
- Interface contracts
- Test plan
- Key decisions

---

## Step 3: Gather Clarifications (Upfront)

**Before drafting**, identify and resolve any ambiguities:

1. **Review spec-research.md** for open questions
2. **Identify gaps** in requirements, scope, or technical approach
3. **Use AskUserQuestion** for any decisions needed

**Example clarification points:**
- Unclear scope boundaries
- Multiple valid approaches for a requirement
- Missing success criteria
- Dependency questions

### Clarification Checklist

Before drafting, verify:

- [ ] All data fields in interface contracts exist in documented APIs
- [ ] Each "Mocks Needed" item maps to real code or a spec
- [ ] No open questions remain in spec-research.md
- [ ] Scope boundaries are clear (what's in vs out)

Use AskUserQuestion for any failures.

**Goal:** Have all information needed to draft a complete spec. No questions should arise during drafting.

---

## Step 4: Parallel Draft Sections

Launch **4 parallel agents** in a SINGLE message:

**Agent 1: Overview**
```
subagent_type: "general-purpose"
model: "haiku"
run_in_background: true
description: "Draft Overview section"
prompt: "Read {spec-path}/spec-research.md for context.
Draft the Overview section: what is being built and how.
Write to {spec-path}/tmp/overview.md.
Return 'DONE' when complete."
```

**Agent 2: Out Of Scope**
```
subagent_type: "general-purpose"
model: "haiku"
run_in_background: true
description: "Draft Out Of Scope section"
prompt: "Read {spec-path}/spec-research.md for context.
Draft Out Of Scope: numbered items with rationale for each exclusion.

For each Out of Scope item, classify as one of:
- **Descoped:** Not part of this feature (no action needed)
- **Deferred to {spec-name}:** Will be done in named spec (verify spec exists)
- **⚠️ Unassigned:** Needs to be done but no spec owns it yet

Rules:
- Never write 'will be in another spec' without naming the spec
- ⚠️ Unassigned items flag gaps for resolution before finalizing

Write to {spec-path}/tmp/out-of-scope.md.
Return 'DONE' when complete."
```

**Agent 3: Functional Requirements**
```
subagent_type: "general-purpose"
model: "haiku"
run_in_background: true
description: "Draft Requirements section"
prompt: "Read {spec-path}/spec-research.md for context.
Draft Functional Requirements using FR1/FR2/FR3 format.
Each FR MUST include Success Criteria.
Write to {spec-path}/tmp/requirements.md.
Return 'DONE' when complete."
```

**Agent 4: Technical Design**
```
subagent_type: "general-purpose"
model: "haiku"
run_in_background: true
description: "Draft Technical Design section"
prompt: "Read {spec-path}/spec-research.md for context.
Draft Technical Design including:
- Files to Reference
- Files to Create/Modify
- Data Flow
- Edge Cases
Write to {spec-path}/tmp/technical-design.md.
Return 'DONE' when complete."
```

Wait for all agents using TaskOutput.

---

## Step 5: Assemble Full Spec

After all agents complete, assemble the complete spec.md:

1. **Initialize with metadata:**
```markdown
# {Spec Name}

**Status:** Draft
**Created:** {YYYY-MM-DD}
**Last Updated:** {YYYY-MM-DD}
**Owner:** @{github-id}

---
```

2. **Append sections in order:**
   - Read `tmp/overview.md` → append
   - Read `tmp/out-of-scope.md` → append
   - Read `tmp/requirements.md` → append
   - Read `tmp/technical-design.md` → append

3. **Write complete spec.md** to spec folder

---

## Step 6: Coherence Check

**Before presenting to the user, validate internal consistency.**

### Launch Coherence Checker

```
subagent_type: "spec-coherence-checker"
description: "Validate spec consistency"
prompt: "Validate internal consistency of the spec at:
- spec.md: {spec-path}/spec.md

Check that FR references, type names, and scope are consistent across all sections."
```

### Handle Results

**If PASS:**
- Proceed to user review (Step 7)

**If FAIL:**
1. Review the specific inconsistencies listed
2. Fix the spec.md sections that are inconsistent
3. Re-run the coherence checker
4. Repeat until PASS (max 2 iterations)

**If stuck after 2 iterations:** Proceed to Step 7 (Autonomous Validation) which handles Andon escalation. Do not escalate separately here.

---

## Step 7: Autonomous Validation (or Human Review)

### Autonomous Mode (Default for Sub-Agent Execution)

When running as a sub-agent (dispatched by spec-executor), skip human review if ALL conditions pass:

**Auto-Approve Criteria:**
- [ ] spec-coherence-checker: PASS
- [ ] No ⚠️ TBD items remain from spec-research.md
- [ ] All interface contracts have traced sources
- [ ] Out of Scope items are all classified (no ⚠️ Unassigned)

If all criteria pass → Proceed directly to Step 8 (Generate Checklist)

### Human Review Mode (Interactive Execution)

When running interactively (user invoked /spec directly):

1. **Show full document** - Display the assembled spec.md
2. **Collect feedback** - User reviews entire document at once
3. **Iterate if needed** - Make changes based on consolidated feedback
4. **Finalize** - Once user approves, proceed to checklist generation

### Andon Escalation

If autonomous validation fails, ESCALATE - do not proceed:

```
SPEC BLOCKED

Validation failure: [which check failed]
Details: [specific issue]

Impact: Cannot proceed to implementation without resolution.

Options:
1. Return to research phase to update contracts
2. Clarify with user: [specific question]
3. Proceed with assumption: [state assumption explicitly]

Need decision to proceed.
```

**Escalation Triggers:**
- spec-coherence-checker fails 2+ iterations
- Discovered gap in research interface contracts
- ⚠️ TBD items that cannot be resolved from available context
- Scope ambiguity that contracts don't address

---

## Step 8: Generate Checklist

After spec approved:

1. Read final `spec.md`
2. Read `spec-research.md` Test Plan section
3. Generate `checklist.md` with:
   - Phase 1.0 tasks from Test Plan
   - Phase 1.1 tasks from Functional Requirements
   - **Phase 1.2 review tasks** (mandatory - do not omit)

Use [checklist-template.md](templates/checklist-template.md).

**Important:** Phase 1.2 includes mandatory review agent steps. Ensure these are included in every generated checklist.

---

## Step 9: Checklist Validation

**Before proceeding to QC, validate checklist completeness.**

### Launch Checklist Validator

```
subagent_type: "checklist-completeness-validator"
description: "Validate checklist coverage"
prompt: "Validate checklist completeness at:
- checklist.md: {spec-path}/checklist.md
- spec.md: {spec-path}/spec.md
- spec-research.md: {spec-path}/spec-research.md

Ensure every FR has test and implementation tasks, and Phase 1.2 review section exists."
```

### Handle Results

**If PASS:**
- Proceed to QC validation (Step 10)

**If FAIL:**
1. Review the specific gaps listed
2. Add missing tasks to checklist.md
3. Re-run the checklist validator
4. Repeat until PASS (max 2 iterations)

**If stuck after 2 iterations:** Escalate to user - spec or research may need adjustment.

---

## Step 10: QC Validation

**Before committing, spawn the spec-qc agent to validate outputs.**

### Launch QC Agent

```
subagent_type: "spec-qc"
description: "Validate spec outputs"
prompt: "Validate the spec at:
- spec.md: {spec-path}/spec.md
- spec-research.md: {spec-path}/spec-research.md

Compare spec against research foundation. Run delta checks and report PASS or FAIL."
```

### Handle QC Results

**If PASS:**
- Proceed to commit (Step 11)

**If FAIL:**
1. Review the specific deltas listed
2. Fix inconsistencies in spec.md (or escalate if research needs updating)
3. Re-run the spec-qc agent
4. Repeat until PASS (max 2-3 iterations)

**If stuck after 2-3 iterations:**
- Escalate to user with remaining issues
- User decides: fix manually, proceed with known gaps, or return to research phase

---

## Step 11: Cleanup and Commit

### Delete tmp/ folder

Remove the temporary drafts folder - it has served its purpose:

```bash
rm -rf {spec-path}/tmp
```

### Update FEATURE.md Changelog

1. Read `FEATURE.md`
2. Add entry to Changelog table:
   ```
   | {YYYY-MM-DD} | [{NN}-{spec-name}](specs/{NN}-{spec-name}/spec.md) | {description} |
   ```

### Stage and Commit Spec Artifacts

```bash
git add features/{domain}/{feature}/specs/{NN}-{spec-name}/spec.md
git add features/{domain}/{feature}/specs/{NN}-{spec-name}/checklist.md
git add features/{domain}/{feature}/FEATURE.md
git commit -m "$(cat <<'EOF'
spec({NN}-{spec-name}): add spec and checklist

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

**Important:** Stage specific files, not `git add -A`.

---

## Step 12: Completion

Confirm with user:

```
"Spec complete.

Created:
- spec.md: [path] (requirements)
- checklist.md: [path] (tasks for implementation)
- FEATURE.md changelog updated

Next step: Run `implement` skill to build it"
```

---

## Key Principles

- **Clarifications upfront** - Resolve ambiguities before drafting
- **spec-research.md already exists** - Created by research skill
- **Test plan from contracts** - Derive tests from interface definitions
- **Parallel for speed** - 4 agents draft simultaneously
- **Single review for efficiency** - User reviews complete document once (interactive mode)
- **Checklist enables execution** - Clear tasks for implement phase
- **Autonomous when possible** - Skip human review if QC passes and contracts are clear
- **Escalate on exception** - Andon pattern for genuine blockers, not minor issues
