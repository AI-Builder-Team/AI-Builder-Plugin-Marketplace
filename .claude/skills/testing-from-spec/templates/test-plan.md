# Test Plan for [Feature Name]

## Overview
- **Spec**: [path/to/spec.md or link]
- **Feature Branch**: [branch-name]
- **Files Touched**: [count] files across [count] domains
- **Testable Functions Identified**: [count]
- **Existing Test Coverage**: [count] tests found
- **New Tests Needed**: [count]
- **Estimated Test Cases**: [count]

---

## Refactoring Suggestions

> **Note**: If no refactoring is needed, write "No refactoring required - all functions are unit testable as-is."

### File: [path/to/file]

#### Issue: [Brief description of testability issue]

**Current Code**:
```[language]
// Before - problematic code with testability issues
[current code snippet showing the problem]
```

**Proposed Refactoring**:
```[language]
// After - refactored code with improved testability
[refactored code snippet]
```

**Benefits**:
- [Benefit 1: e.g., "Separates business logic from I/O operations"]
- [Benefit 2: e.g., "Enables pure function testing without mocks"]
- [Benefit 3: e.g., "Improves code reusability"]

**Test Coverage Impact**:
- [Description of how this improves testability]
- Enables testing: [specific scenarios that become testable]
- Estimated new test cases: [number]

**Effort**: [Low/Medium/High]

**Recommendation**: [Implement/Skip - with clear reasoning]

---

### File: [path/to/another-file]

[Repeat structure for each file needing refactoring]

---

## Test Plan by Domain

> **Legend**:
> - ✓ **Existing** - Test coverage already exists
> - ⊕ **Add tests for** - New tests to be written
> - ✗ **No existing tests** - No test file exists
> - ⚠️ **Requires refactoring** - Function needs refactoring before testing (see Refactoring Suggestions)
> - 🔄 **Update existing** - Existing tests need updates for new functionality

### Domain: klair-client

**Testing Framework**: Vitest + Testing Library
**Test File Location**: Next to implementation files (`*.test.tsx`, `*.test.ts`)

#### File: [path/to/component.tsx]
- ✓ **Existing**: [component.test.tsx] (covers: [what it covers])
- ⊕ **Add tests for**:
  - [ ] `functionName()` - [description] ([count] test cases)
    - Test case 1: [scenario]
    - Test case 2: [scenario]
    - Test case 3: [scenario]
  - [ ] `anotherFunction()` - [description] ([count] test cases)
    - Test case 1: [scenario]
- ⚠️ **Requires refactoring**: `problematicFunction()` (see Refactoring Suggestions above)

#### File: [path/to/utils.ts]
- ✗ **No existing tests**
- ⊕ **Add tests for**:
  - [ ] `utilFunction1()` - [description] ([count] test cases)
  - [ ] `utilFunction2()` - [description] ([count] test cases)

---

### Domain: klair-api

**Testing Framework**: pytest
**Test File Location**: `tests/test_*.py` directory

#### File: [path/to/service.py]
- ✓ **Existing**: tests/test_service.py (covers: [what it covers])
- 🔄 **Update existing**:
  - [ ] Update `test_process_data()` to cover new validation logic
- ⊕ **Add tests for**:
  - [ ] `new_function()` - [description] ([count] test cases)
    - Test case 1: [scenario]
    - Test case 2: [scenario]

#### File: [path/to/calculator.py]
- ✗ **No existing tests**
- ⊕ **Add tests for**:
  - [ ] `calculate_metric()` - [description] ([count] test cases)
  - [ ] `transform_data()` - [description] ([count] test cases)

---

### Domain: [other-domain]

[Repeat structure for additional domains like klair-udm, etc.]

---

## Functions Excluded from Testing

> **Note**: Document functions that were analyzed but excluded from testing, with reasoning.

### File: [path/to/file]
- `functionName()` - [Reason: e.g., "Pure API orchestration, no business logic to test"]
- `anotherFunction()` - [Reason: e.g., "External service integration, covered by integration tests"]
- `thirdFunction()` - [Reason: e.g., "Simple pass-through, no logic to test"]

---

## Summary

- **Refactoring recommendations**: [count] ([count] recommended to implement)
- **Total new test cases**: [count]
- **Domains affected**: [count] (list: [domain1, domain2, ...])
- **Test files to create**: [count]
- **Test files to update**: [count]
- **Functions excluded from testing**: [count]

### Implementation Order
1. [Phase 1: e.g., "Implement refactoring for Widget.tsx"]
2. [Phase 2: e.g., "Write klair-client tests (3 files, 12 test cases)"]
3. [Phase 3: e.g., "Write klair-api tests (2 files, 8 test cases)"]

---

## Notes

[Space for user notes, modifications, additional context, and decisions made during review]

### User Modifications
- [Date] - [User]: [Description of change made to plan]

### Implementation Notes (Added During Testing)
- [To be filled in during Phase 6: verification]

---

## Completion Status

> **Note**: This section is updated after test implementation is complete.

### Completed Test Cases
- [ ] Domain: klair-client
  - [ ] [file1]: [x/y] test cases passing
  - [ ] [file2]: [x/y] test cases passing
- [ ] Domain: klair-api
  - [ ] [file1]: [x/y] test cases passing

### Final Results
- **Total tests written**: [count]
- **All tests passing**: [Yes/No]
- **Files created**: [count]
- **Files updated**: [count]
- **Issues encountered**: [list any issues or blockers]
