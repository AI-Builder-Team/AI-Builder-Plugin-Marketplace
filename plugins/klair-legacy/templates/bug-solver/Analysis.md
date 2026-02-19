# Root Cause Analysis: [Bug Title]

**Bug ID:** bug-XXX-short-description  
**Status:** In Progress  
**Created:** YYYY-MM-DD HH:MM  
**Updated:** YYYY-MM-DD HH:MM  
**Analyst:** [Name]

**Related Report:** [Report.md](./Report.md)

---

## Investigation Summary

Brief overview of the investigation approach and key findings.

## Investigation Timeline

| Time | Action Taken | Finding |
|------|-------------|---------|
| HH:MM | Started investigation | - |
| HH:MM | Examined [component] | [Finding] |
| HH:MM | Reproduced locally | [Result] |
| HH:MM | Identified root cause | [Cause] |

## Investigation Methodology

**Approach taken:**
1. [Step 1 of investigation]
2. [Step 2 of investigation]
3. [Step 3 of investigation]

**Tools and techniques used:**
- [ ] Log analysis
- [ ] Code review
- [ ] Debugger
- [ ] Profiling
- [ ] Network inspection
- [ ] Database queries
- [ ] Other: ___________

## Code Components Involved

### Primary Component

**File:** `path/to/primary/file.ext`  
**Lines:** L[start]-L[end]  
**Role:** [What this component does]

```language
[Relevant code snippet]
```

### Secondary Components

**File:** `path/to/secondary/file.ext`  
**Lines:** L[start]-L[end]  
**Role:** [What this component does]

**Additional files:**
- `path/to/file1.ext` - [Brief description]
- `path/to/file2.ext` - [Brief description]

## Data Flow Analysis

### Normal Flow (Expected)

```
[Component A] → [Component B] → [Component C]
     ↓
  Expected Result
```

### Buggy Flow (Actual)

```
[Component A] → [Component B] ⚠️ → [Component C]
     ↓
  Bug Occurs Here
```

**Breakdown point:** [Where the flow breaks]

## Root Cause

### Technical Explanation

[Detailed technical explanation of why the bug occurs]

**Category:**
- [ ] Logic error
- [ ] Race condition
- [ ] Null/undefined handling
- [ ] Type mismatch
- [ ] Resource exhaustion
- [ ] Integration issue
- [ ] Configuration error
- [ ] Data corruption
- [ ] Security vulnerability
- [ ] Other: ___________

### Why It Went Undetected

[Explanation of why this bug wasn't caught earlier]

- Missing test coverage: Yes/No
- Edge case: Yes/No
- Recent change introduced: Yes/No
- Environmental difference: Yes/No

## Contributing Factors

1. **Primary cause:** [Main technical reason]
2. **Contributing factor 1:** [Additional factor]
3. **Contributing factor 2:** [Additional factor]

## Impact Analysis

### Affected Scenarios

1. **Scenario 1:** [Description]
   - Frequency: [How often]
   - User impact: [What users experience]

2. **Scenario 2:** [Description]
   - Frequency: [How often]
   - User impact: [What users experience]

### Data Integrity

- [ ] No data corruption
- [ ] Potential data loss
- [ ] Data inconsistency
- [ ] Requires data cleanup

### System State

- [ ] No persistent issues
- [ ] System state corruption
- [ ] Requires manual intervention
- [ ] Affects other features

## Related Issues

### Historical Context

Have we seen this before?
- [ ] New issue
- [ ] Similar to: [reference previous bug]
- [ ] Related to: [architectural decision]

### Dependencies

**Upstream dependencies:**
- [Library/service name] version [X.Y.Z]
- Known issues: [link to issue tracker]

**Downstream impact:**
- Features affected: [list]
- Systems affected: [list]

## Evidence

### Logs

```
[Relevant log excerpts showing the issue]
```

### Stack Traces

```
[Stack trace if applicable]
```

### Database State

```sql
-- Query showing problematic state
SELECT * FROM table WHERE condition;
```

**Results:** [Description of findings]

### Network Traffic

```
[Relevant network requests/responses if applicable]
```

## Hypothesis Validation

### Initial Hypothesis (from Report)

[What we thought initially]

### Actual Root Cause

[What we found]

**Hypothesis accuracy:** ✅ Correct | ❌ Incorrect | 🟡 Partially correct

## Solution Approaches Considered

### Approach 1: [Name]
**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

**Verdict:** ✅ Recommended | ❌ Not recommended | 🟡 Viable alternative

### Approach 2: [Name]
**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

**Verdict:** ✅ Recommended | ❌ Not recommended | 🟡 Viable alternative

## Recommended Solution

**Selected approach:** [Name of approach]

**Rationale:** [Why this approach is best]

**Estimated effort:** [Hours/Days/Weeks]

**Risk level:** Low | Medium | High

## Prevention Recommendations

**To prevent similar bugs:**

1. **Code changes:**
   - [Specific prevention measure]

2. **Testing improvements:**
   - [Test cases to add]

3. **Process improvements:**
   - [Development process changes]

4. **Documentation:**
   - [Documentation to add/update]

## Open Questions

- [ ] Question 1 that needs resolution
- [ ] Question 2 that needs resolution

---

**Status Update:** Analysis complete. Ready to proceed to Fix phase.

**Next Steps:** Implement the recommended solution in Fix.md