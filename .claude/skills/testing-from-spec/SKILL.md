---
name: testing-from-spec
description: Generates and runs unit tests for files listed in spec or feature documents. Identifies testable functions, suggests refactors for coverage, and executes tests incrementally. Use when adding test coverage for new features or refactoring existing code.
---

# Testing from Spec/Feature Files

Automates unit test creation for files specified in spec or feature documents. Identifies testable code, suggests refactors for better coverage, writes minimal tests for maximum coverage, and runs them incrementally.

## When to Use This Skill

Use when:
- Working from a spec/feature file with a "files touched" section
- Need to add unit test coverage for changed files
- Want to identify refactoring opportunities for better testability
- Need to validate test coverage across multiple domains (frontend/backend)

**Trigger phrases**: "add tests from spec", "test coverage for feature", "unit tests from spec", "test files from feature"

## Core Workflow

### Phase 1: Discovery & Analysis

1. **Locate spec/feature file**:
   - Check `specs/` directory
   - Check `features/` directory
   - Ask user if not found

2. **Extract files touched**:
   - Parse "files touched" or similar section
   - List all implementation files (exclude test files)
   - Group by domain (klair-client, klair-api, klair-udm, etc.)

3. **Identify testing frameworks**:
   - klair-client: Vitest + Testing Library
   - klair-api: pytest
   - klair-udm: Check for test config files
   - See [guidelines/testing-frameworks.md](guidelines/testing-frameworks.md) for details

### Phase 2: Test Planning & Refactoring Analysis

1. **Read implementation files**:
   - Use Read tool for each file in "files touched"
   - Identify exported functions, classes, methods
   - Exclude: API calls, external service integrations, database operations (unless mocking is trivial)

2. **Identify unit testable code**:
   - Pure functions (no side effects)
   - Business logic functions
   - Utility functions
   - Data transformations
   - Validation functions
   - See [guidelines/testability-criteria.md](guidelines/testability-criteria.md)

3. **Analyze testability issues**:
   - Identify tightly coupled code
   - Find functions with side effects that could be split
   - Spot missing error handling
   - Use [guidelines/testability-criteria.md](guidelines/testability-criteria.md)

4. **Find existing test files**:
   - Check for corresponding test files
   - Note coverage gaps

### Phase 2.5: Write TEST_PLAN.md

1. **Create comprehensive test plan document**:
   - Write to `features/<feature-name>/TEST_PLAN.md` or `specs/<spec-name>/TEST_PLAN.md`
   - Use [templates/test-plan.md](templates/test-plan.md) as the template
   - Include all sections:
     * Overview with summary statistics
     * Refactoring Suggestions (if any identified)
     * Test Plan by Domain
     * Summary
     * Notes section (for user additions)

2. **Structure of TEST_PLAN.md**:
   ```markdown
   # Test Plan for [Feature Name]

   ## Overview
   - **Spec**: [link to spec file]
   - **Files Touched**: [count] files across [count] domains
   - **Testable Functions Identified**: [count]
   - **Existing Test Coverage**: [count] tests found
   - **New Tests Needed**: [count]

   ---

   ## Refactoring Suggestions

   ### File: [filename]

   #### Issue: [Issue description]
   **What to change**:
   ```[language]
   // Before
   [current code snippet]

   // After
   [refactored code snippet]
   ```

   **Benefits**:
   - [Benefit 1]
   - [Benefit 2]

   **Test coverage impact**:
   - [Impact description]
   - Estimated new test cases: [number]

   **Effort**: [Low/Medium/High]

   **Recommendation**: [Implement/Skip with reasoning]

   ---

   ## Test Plan by Domain

   ### Domain: klair-client

   #### File: src/components/Widget.tsx
   - ✓ **Existing**: Widget.test.tsx (covers rendering)
   - ⊕ **Add tests for**:
     - [ ] `calculateTotal()` - pure function (3 test cases)
     - [ ] `validateInput()` - validation logic (2 test cases)
   - ⚠️ **Requires refactoring**: `fetchAndCalculate()` (see Refactoring Suggestions)

   #### File: src/utils/calculations.ts
   - ✗ **No existing tests**
   - ⊕ **Add tests for**:
     - [ ] `computeMetrics()` - business logic (4 test cases)
     - [ ] `transformData()` - data transformation (2 test cases)

   ### Domain: klair-api

   #### File: services/calculator.py
   - ✗ **No existing tests**
   - ⊕ **Add tests for**:
     - [ ] `compute_metrics()` - business logic (3 test cases)
     - [ ] `transform_data()` - data transformation (2 test cases)

   ---

   ## Summary

   - **Refactoring recommendations**: [count]
   - **Total new test cases**: [count]
   - **Domains affected**: [count]
   - **Files to create**: [count] test file(s)
   - **Files to update**: [count] test file(s)

   ---

   ## Notes
   [Space for user notes, modifications, and additional context]
   ```

### Phase 3: User Review

1. **Notify user and request review**:
   > "I've written the test plan to `TEST_PLAN.md`. This includes:
   > - **Refactoring suggestions** (if any were identified)
   > - **Test plan** for all testable functions
   >
   > Please review the document. If you'd like any changes, let me know and I'll update it. You can:
   > - Remove or add test cases
   > - Modify or skip refactoring suggestions
   > - Adjust priorities or add notes
   > - Change test case counts
   >
   > When you're happy with the plan, let me know and I'll proceed with implementation."

2. **Interactive editing**:
   - User reads `TEST_PLAN.md`
   - User requests changes through conversation
   - Claude updates `TEST_PLAN.md` with requested edits
   - Repeat until user is satisfied

3. **Confirmation**:
   - Wait for user approval ("looks good", "proceed", etc.)
   - Re-read `TEST_PLAN.md` to get final approved plan

### Phase 4: Implement Refactoring (If Approved)

1. **Check refactoring recommendations**:
   - Re-read `TEST_PLAN.md` for refactoring decisions
   - Identify which refactors are marked for implementation

2. **Implement approved refactors**:
   - Make code changes for each approved refactor
   - Follow the refactoring approach documented in TEST_PLAN.md
   - Test that existing functionality still works

3. **Commit refactoring changes**:
   - Create separate commit for refactoring
   - Use message: "Refactor [files] for better testability"
   - List specific changes in commit body

### Phase 5: Test Implementation

1. **Re-read TEST_PLAN.md for final test list**:
   - User may have modified test cases during review
   - Extract list of tests to write from the plan

2. **Batch tests by domain**:
   - Group tests by testing framework
   - Within domain, batch by file (1 implementation file = 1 batch)
   - Smaller batches for large files (max 5 test cases per batch)

3. **For each batch**:
   - Read existing test file (if exists) or create new one
   - Write tests following domain conventions:
     * Frontend: See [guidelines/frontend-testing.md](guidelines/frontend-testing.md)
     * Backend: See [guidelines/backend-testing.md](guidelines/backend-testing.md)
   - Use Edit for existing files, Write for new files
   - **Minimize test count**: Each test should cover multiple scenarios where logical

4. **Run tests immediately**:
   - Frontend: `cd klair-client && pnpm vitest run <test-file-path>`
   - Backend: `cd klair-api && pytest <test-file-path>`
   - Capture output

5. **Handle failures**:
   - If tests fail, analyze error
   - Fix test or implementation (ask user if implementation change needed)
   - Rerun until batch passes
   - Move to next batch only after current batch passes

6. **Progress tracking**:
   - Use TodoWrite to track batches
   - Mark each batch complete after tests pass
   - Show running summary: "3/7 batches complete, 12/20 test cases passing"

### Phase 6: Verification & Update TEST_PLAN.md

1. **Run full test suite** (optional, ask user):
   - Frontend: `cd klair-client && pnpm test`
   - Backend: `cd klair-api && pytest`

2. **Update TEST_PLAN.md with results**:
   - Check off completed test cases
   - Add completion markers (✓ Completed)
   - Update summary with final counts
   - Add any notes about issues encountered

3. **Summary report** (also show in conversation):
   ```
   ## Test Coverage Summary

   ✓ klair-client: 8 new tests added
     - Widget.test.tsx: 3 tests (all passing)
     - utils/calculations.test.ts: 5 tests (all passing)

   ✓ klair-api: 6 new tests added
     - tests/test_calculator.py: 6 tests (all passing)

   Total: 14 new test cases, 100% passing
   Files created: 1
   Files updated: 2 (+ TEST_PLAN.md updated)
   ```

## Key Principles

1. **Unit tests only**: No integration tests, no external service calls
2. **Minimal tests, maximum coverage**: One test can cover multiple scenarios
3. **Incremental execution**: Run tests after each batch, fix before proceeding
4. **Domain-aware**: Use appropriate testing patterns for each codebase
5. **User approval for refactors**: Never refactor without explicit permission

## Important Notes

- Test files follow conventions:
  - Frontend: `*.test.tsx`, `*.test.ts` (next to implementation)
  - Backend: `tests/test_*.py` (in tests/ directory)
- Always check existing tests before creating duplicates
- Mock external dependencies if function is otherwise unit testable
- Skip functions that are purely I/O or orchestration
- Focus on business logic and data transformations

## Supporting Files

- [guidelines/testing-frameworks.md](guidelines/testing-frameworks.md) - Framework specifics per domain
- [guidelines/testability-criteria.md](guidelines/testability-criteria.md) - What makes code unit testable
- [guidelines/frontend-testing.md](guidelines/frontend-testing.md) - Frontend testing patterns
- [guidelines/backend-testing.md](guidelines/backend-testing.md) - Backend testing patterns
- [templates/test-plan.md](templates/test-plan.md) - TEST_PLAN.md template (combines refactoring + test planning)
- [templates/refactoring-suggestion.md](templates/refactoring-suggestion.md) - Refactoring proposal format (deprecated, now part of test-plan.md)
