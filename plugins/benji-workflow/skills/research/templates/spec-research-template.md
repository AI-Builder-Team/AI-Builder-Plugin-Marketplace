# Spec Research: {Spec Name}

**Date:** {YYYY-MM-DD}
**Author:** @{github-id}
**Spec:** `{NN}-{spec-name}`

---

## Problem Context

{What problem does this spec address? What's the scope?}

---

## Exploration Findings

### Existing Patterns

{What patterns exist in the codebase for similar functionality?}

| Pattern | Used In | Notes |
|---------|---------|-------|
| {pattern} | {files/features} | {observations} |

### Key Files

| File | Relevance |
|------|-----------|
| `{path}` | {why it matters} |

### Integration Points

{How does this connect to existing systems?}

- {Integration point 1}
- {Integration point 2}

---

## Key Decisions

### Decision 1: {Topic}

**Options considered:**
1. {Option A} - {pros/cons}
2. {Option B} - {pros/cons}

**Chosen:** {Option X}

**Rationale:** {Why this was selected}

---

## Interface Contracts

### Types

```typescript
// Key interfaces for this spec
interface {Name} {
  {fields}
}
```

### Function Contracts

| Function | Signature | Responsibility | Dependencies |
|----------|-----------|----------------|--------------|
| `{name}` | `{signature}` | {what it does} | {deps} |

---

## Test Plan

**Derived from Interface Contracts above.** This defines WHAT to test. The checklist.md tracks execution.

### {function_name}

**Signature:** `{signature}`

**Happy Path:**
- {test case}: {expected behavior}
- {test case}: {expected behavior}

**Edge Cases:**
- Empty input: {expected behavior}
- Null/undefined: {expected behavior}
- Boundary values: {expected behavior}

**Error Cases:**
- Network failure: {expected behavior}
- Invalid input: {expected behavior}
- State conflict: {expected behavior}

**Mocks Needed:**
- `{dependency}`: {mock strategy}

### {next_function_name}

{Same format...}

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `{path}` | create/modify | {what it does} |

---

## Edge Cases to Handle

1. **{Case}** - {How to handle}
2. **{Case}** - {How to handle}

---

## Open Questions

**Must be empty before research phase completes.** Use this section to track questions during exploration, then resolve each before finalizing.

<!-- Example of resolved question:
✓ How should we handle rate limiting? → Decided: Use exponential backoff, documented in Key Decisions.
-->

None remaining.
