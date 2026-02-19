# Spec Review: {Spec Name}

**Spec:** `{spec-path}/spec.md`
**Reviewed:** {YYYY-MM-DD}
**Verdict:** {PASS | PASS WITH RESERVATIONS | REVISE}

---

## Summary

{2-3 sentences. What is the spec trying to do, and what is the overall assessment. No hedging.}

---

## Findings

### Critical

{If none: "None."}

**C1: {Finding title}**
- **Dimension:** {which review dimension}
- **Location:** {FR number, section, or line reference}
- **Issue:** {what is wrong}
- **Evidence:** {what you found in the codebase or spec that proves this}
- **Impact:** {what happens if this isn't fixed}

### Major

{If none: "None."}

**M1: {Finding title}**
- **Dimension:** {which review dimension}
- **Location:** {FR number, section, or line reference}
- **Issue:** {what is wrong}
- **Evidence:** {what you found}
- **Impact:** {what happens if this isn't fixed}

### Minor

{If none: "None."}

**m1: {Finding title}**
- **Location:** {FR number, section, or line reference}
- **Issue:** {what is wrong}

### Suggestions

{If none: "None."}

**S1: {Suggestion}**
- **Rationale:** {why this would improve the spec}

---

## Dimension Ratings

| Dimension | Rating | Key Issue |
|-----------|--------|-----------|
| Feasibility | {PASS/CONCERN/FAIL} | {one-line summary or "—"} |
| Completeness | {PASS/CONCERN/FAIL} | {one-line summary or "—"} |
| Scope Calibration | {PASS/CONCERN/FAIL} | {one-line summary or "—"} |
| Assumption Audit | {PASS/CONCERN/FAIL} | {one-line summary or "—"} |
| Risk Identification | {PASS/CONCERN/FAIL} | {one-line summary or "—"} |
| Interface Contracts | {PASS/CONCERN/FAIL} | {one-line summary or "—"} |
| Testability | {PASS/CONCERN/FAIL} | {one-line summary or "—"} |

---

## Codebase Verification

### Confirmed
- {file or contract element} — {what was verified}

### Mismatches
- {file or contract element} — {what differs}

### Missing
- {file or contract element} — {not found}

---

## Recommended Actions

{If PASS: "No blocking actions. Consider addressing Minor/Suggestion items at implementation time."}

{If PASS WITH RESERVATIONS: numbered list of Major items to address}

{If REVISE: numbered list of Critical items, plus guidance on whether to revise spec in-place or return to research phase}
