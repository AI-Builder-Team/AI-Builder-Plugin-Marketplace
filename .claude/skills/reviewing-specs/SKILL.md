---
name: reviewing-specs
description: Critically reviews a spec for feasibility, completeness, risks, and shortcomings. Use after spec creation to get an objective, non-sycophantic assessment before implementation. Triggers on "review spec", "spec review", "critique spec", "audit spec".
allowed-tools: [Task, Read, Write, Glob, Grep, AskUserQuestion]
---

# Reviewing Specs

Performs an adversarial, objective review of a technical specification. This is NOT a consistency check (spec-coherence-checker and spec-qc already do that). This skill questions whether the spec is *correct*, *complete*, and *buildable* — catching problems that internal consistency checks miss.

## When to Use This Skill

- After `/spec` or `/creating-specs` has produced a spec.md
- Before `/implement` or `/orchestrate` kicks off implementation
- When you want a second opinion on a spec before committing engineering time
- When revisiting an old spec that may have drifted from the codebase

## What This Is NOT

- Not a proofreading or formatting check
- Not a re-run of spec-coherence-checker or spec-qc
- Not a rewrite service — it produces a review report, not a revised spec

---

## Workflow Overview

```
Locate Spec
     │
     ▼
Read Spec + Research Artifacts
     │
     ▼
Verify Against Codebase (parallel agents)
     │
     ▼
Assess Review Dimensions
     │
     ▼
Produce spec-review.md
     │
     ▼
Present Findings + Verdict
```

---

## Step 1: Locate the Spec

1. Ask user which spec to review (or accept path directly)
2. Read the spec.md
3. Read spec-research.md if it exists
4. Read checklist.md if it exists
5. Read the parent FEATURE.md if it exists

Collect all paths for reference:
- `{spec-path}/spec.md` (required)
- `{spec-path}/spec-research.md` (optional)
- `{spec-path}/checklist.md` (optional)
- `{feature-path}/FEATURE.md` (optional)

If spec.md does not exist, stop and inform the user.

---

## Step 2: Codebase Verification (Parallel)

The spec makes claims about existing code. Verify them. Launch **3 parallel agents**:

**Agent 1: File Existence & Structure**
```
subagent_type: "Explore"
description: "Verify spec file references"
prompt: "The following files are referenced in a spec. For each one:
1. Determine which bucket it belongs to:
   - Files to Reference: must already exist
   - Files to Create/Modify with Action=modify: must already exist
   - Files to Create/Modify with Action=create: may not exist yet (expected before implementation)
2. If the file should exist, confirm it exists and verify the interfaces/functions/exports the spec mentions are actually present
3. If Action=create and the file does not exist, treat that as expected (not a defect)
4. If the action is unclear, call that out as a mismatch in the spec

Files referenced:
{list from spec's 'Files to Reference' and 'Files to Create/Modify' sections}

Report format:
- CONFIRMED: {file} — {what was verified, or "planned create; not present yet (expected)"}
- MISSING: {file} — expected existing file does not exist (reference file or modify target)
- MISMATCH: {file} — exists but {what differs from spec's claims}, OR action/create-modify intent is ambiguous"
```

**Agent 2: Interface Contract Validation**
```
subagent_type: "Explore"
description: "Validate interface contracts"
prompt: "The spec defines these interface contracts:
{paste interface contracts from spec}

Search the codebase to verify:
1. Do the types/interfaces referenced actually exist with the fields described?
2. Do the API endpoints return the fields the spec claims?
3. Are there fields the spec assumes exist but don't?

Report CONFIRMED, MISSING, or MISMATCH for each contract element."
```

**Agent 3: Pattern Consistency**
```
subagent_type: "Explore"
description: "Check pattern consistency"
prompt: "The spec proposes this technical approach:
{paste technical design summary}

Search the codebase for similar features. Report:
1. Does this approach match how similar things are built in this codebase?
2. Are there established patterns the spec ignores or contradicts?
3. Are there utilities, hooks, or helpers the spec should use but doesn't mention?"
```

Wait for all agents. Collect findings.

---

## Step 3: Assess Review Dimensions

Using the spec content AND the codebase verification results, evaluate each dimension from [guidelines/review-dimensions.md](guidelines/review-dimensions.md).

For each dimension, produce:
- **Rating**: PASS / CONCERN / FAIL
- **Findings**: Specific issues with evidence
- **Severity**: Critical / Major / Minor / Suggestion (per finding)

### Severity Definitions

| Severity | Meaning | Action Required |
|----------|---------|-----------------|
| **Critical** | Will cause implementation failure or incorrect behavior. Must fix before implementing. | Block implementation |
| **Major** | Significant gap that will cause rework or missed requirements. Should fix. | Fix recommended |
| **Minor** | Small issue that won't block implementation but should be addressed. | Fix if convenient |
| **Suggestion** | Improvement idea, not a defect. Take it or leave it. | Optional |

---

## Step 4: Produce spec-review.md

Write the review report to `{spec-path}/spec-review.md` using the template at [templates/spec-review-template.md](templates/spec-review-template.md).

### Verdict Rules

- **PASS**: Zero Critical, zero Major findings. Spec is ready for implementation.
- **PASS WITH RESERVATIONS**: Zero Critical, 1-3 Major findings. Can proceed but should address majors.
- **REVISE**: Any Critical findings, OR 4+ Major findings. Do not implement until addressed.

---

## Step 5: Present to User

1. Show the verdict prominently
2. List Critical and Major findings with one-line summaries
3. Provide the path to the full spec-review.md
4. If verdict is REVISE, suggest specific next steps (which sections to rework, whether to return to research phase, etc.)

**Do NOT:**
- Soften findings with qualifiers like "otherwise great spec"
- Apologize for critical feedback
- Suggest the spec is "almost there" if it has Critical issues
- Pad the review with praise to balance criticism

---

## Key Principles

- **Verify, don't trust** — Read actual code, don't take the spec's word for what exists
- **Be specific** — "FR3 success criteria is vague" is useless. "FR3 says 'data displays correctly' but doesn't define what 'correctly' means for edge case X" is useful
- **Distinguish severity** — Not every issue is Critical. Not every issue is a Suggestion. Calibrate honestly
- **Stay in scope** — Review what the spec says, not what you wish it said. Don't add your own feature requests
- **One report, no rewrites** — Produce the review. The spec author decides what to fix
