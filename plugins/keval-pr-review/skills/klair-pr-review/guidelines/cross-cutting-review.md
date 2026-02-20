# Cross-Cutting Concerns Review

Patterns that apply across frontend, backend, and pipelines.

## 1. DRY Violations (150 comments — top pattern)

### What to Check
- Same helper function defined in two files — extract to shared utility
- Same constant/config repeated with hardcoded values — extract to constants file
- Same validation logic duplicated across routers/components
- **Real example (PR #1851):** Helper function defined in both `loaders/program_sessions.py` and `loaders/programs.py`
- **Real example (PR #1371):** Year conversion logic duplicated in multiple routers

### How to Check
When reviewing a new function/utility, search the codebase:
```bash
grep -r "function_name\|similar_logic" --include="*.py" --include="*.ts" --include="*.tsx"
```

## 2. Hardcoded Values (142 comments)

### Check For
- Magic numbers in conditions (`if count > 5`, `limit=10`, `ttl=3600`)
- Hardcoded strings that represent configuration (`"Virtual"`, `"Other"`)
- Inline data lineage descriptions that should be extracted from code
- **Real example (PR #1493):** Data lineage modal hardcoded "5 master payer accounts" when reality was 10
- **Real example (PR #1672):** `limit=10` hardcoded instead of using `config.drill_down_limit`

### When NOT to Flag
- Single-use values that are self-documenting (e.g., `status_code=200`)
- Test fixtures with specific values
- Constants that are already in a constants file

## 3. Stale/Misleading Comments (144 comments)

### Most Common Patterns
- Comment describes old logic that was changed
- Docstring formula doesn't match code
- TODO/FIXME that references completed work
- Comment says "5 minutes" but config says "1 hour"
- **Real example (PR #1525):** Comment says "Map 50-150% pace to 0-100%" but code maps 0-150% to 0-100%
- **Real example (PR #1672):** Docstring says "5 minutes" cache TTL but actual is 1 hour

### Verification Approach
For every comment that describes behavior, verify the behavior matches by reading the code.

## 4. Testing Gaps (117 comments)

### Skipped Tests
- Tests with `pytest.skip()` or `test.skip()` that were never un-skipped after implementation
- **Real example (PR #1672):** 105 tests all called `pytest.skip("not yet implemented")` — implementation complete but tests never activated

### Integration Test Coverage
- Validate frontend-backend contracts with integration tests
- **Real example (PR #1584):** Constants duplicated between frontend and backend — suggest integration test to validate sync

### Test Assertions
- Tests should verify specific behavior, not just "no error thrown"
- Mock data should be realistic (not all zeros or empty strings)

## 5. API Contract Consistency (121 comments)

### Frontend-Backend Alignment
- When backend adds a new field, verify frontend types include it
- When backend changes response shape, verify frontend handles both old and new
- When a config parameter exists in the API contract, verify it's actually used

### Response Models
- Backend endpoints should declare `response_model`
- Response shape should match documented types

## 6. Logging Discipline (205 comments)

### When to Log
- Warning: recoverable degradation (cache miss, fallback behavior)
- Error: failures that affect correctness
- Info: significant operations (pipeline start/complete, data refresh)

### What to Include
- Operation context: what was being attempted
- Relevant identifiers: account ID, entity name, cache key
- For renamed/misleading log variables, ensure the message matches reality
- **Real example (PR #1779):** Renamed `updated` to `attempted` in log message to accurately reflect behavior

## 7. Dead Code & Unused Exports (38 comments)

### Check For
- Functions defined but never called (search for references)
- Imports that are unused
- Code behind unreachable conditions
- **Real example (PR #1584):** `aggregateToParent()` function no longer used — should be removed with its tests
- **Real example (PR #1672):** `_inline_css()` implemented but `render_report()` never calls it
- **Real example (PR #1672):** `severity = "warning"` hardcoded, making `_classify_severity` branch unreachable

### Commented-Out Code
- Remove completely or add a comment explaining why it's kept
- **Real example (PR #1544):** Commented code without explanation

## 8. SQL in Frontend & Backend

### SQL Query Patterns
- CASE statement ordering matters — same condition in different positions produces different behavior
- **Real example (PR #1500):** `Dummy Customer for Bank charges` condition placed in different positions in two CASE statements, leading to different behavior

### Date Handling in SQL
- Be explicit about timezone handling in queries
- `DATE` vs `TIMESTAMP` semantics differ across databases

## 9. Error String Matching (Fragile Pattern)

- Don't check error types by matching on `err.message` strings — use error classes or status codes
- **Real example (PR #1779):** Changed from `err.message` string matching to `AxiosError.response?.status === 404`

## 10. Performance Considerations (89 comments)

### What to Check
- N+1 query patterns (loop executing individual queries)
- Missing pagination on endpoints returning large datasets
- Unbounded cache growth without eviction
- **Real example (PR #1718):** Cache intentionally unbounded (acknowledged tradeoff with documented reasoning)

### When NOT to Flag
- If the dataset is known to be small and bounded (e.g., <1000 schools)
- If the tradeoff is documented and accepted
