# Error Handling & Resilience Review

The second most common category of review findings. Klair's CLAUDE.md has a strict rule: "Exceptions MUST be propagated to FastAPI's error handlers. NEVER catch exceptions and return false/zero/empty data."

## 1. CLAUDE.md Exception Propagation (CRITICAL)

This is the #1 most-caught violation in Klair PRs.

### The Rule
Services must let exceptions bubble up to routers so clients receive proper HTTP error codes and can distinguish between legitimate empty results vs actual errors.

### Violations to Look For
- `try/except` that returns `[]`, `{}`, `0`, `False`, `None`, or `""` instead of re-raising
- `try/except Exception` that logs and continues (swallowing the error)
- `return_exceptions=True` in `asyncio.gather()` without checking for exceptions in results
- Functions that catch exceptions and return default/placeholder values

### Real Examples
- **PR #1672:** Redshift queries used `fetch_with_params()` which returns `None` on error — code fell through to `rows = []` and generated reports with zero outliers, no indication of failure
- **PR #1672:** `Cache.set(ttl=3600)` — `ttl` parameter doesn't exist, `TypeError` caught and swallowed by surrounding try/except — caching never worked
- **PR #1734:** `fetch_api_keys`, `fetch_users`, `fetch_workspaces` all catch bare `Exception` and return empty dicts — pipeline reports success with empty metadata
- **PR #1739:** LLM exception swallowing causes pain point deletion — returns `[]`, account added to processed list, existing data deleted and replaced with nothing

### What to Check
1. Every `try/except` block: does it re-raise or return empty data?
2. Every `catch` block in TypeScript: does it swallow or propagate?
3. Functions that return `Optional` or `| None`: is the caller checking for None vs empty?

## 2. Silent Failure Chains

Follow the error path through multiple layers to find where information is lost.

### Pattern: Service → Router → Client
1. Service catches exception, returns `None`
2. Router checks for `None`, returns `[]` (empty list)
3. Client receives `200 OK` with empty data — indistinguishable from "no data exists"

### Pattern: Cache Operation Failure
- Cache `.get()` fails → returns `None` → treated as cache miss → falls through to expensive DB query
- Cache `.set()` fails → swallowed → data never cached → every request hits DB
- **Real example (PR #1672):** `Cache.set(ttl=3600)` always raised `TypeError` (no `ttl` param), caught and swallowed

### Pattern: AI/LLM Failure
- AI call fails → catch Exception → insert placeholder text → report shows `success=True`
- Programming bugs (`TypeError`, `KeyError`) caught alongside expected API errors
- **Real example (PR #1672):** Three broad `except Exception` blocks replaced AI insights with placeholder HTML, report returned `success=True`

## 3. Error Exposure to Clients (HIGH)

Internal error details should never reach API consumers.

### Check For
- `HTTPException(detail=f"Failed: {e}")` — may leak DB hostnames, file paths, or stack traces
- `return {"error": str(e)}` — raw exception messages to clients

### Correct Pattern
```python
logger.error(f"Operation failed: {e}", exc_info=True)
raise HTTPException(status_code=500, detail="Operation failed")
```

## 4. Module-Level Initialization (HIGH)

Watch for service clients instantiated at module import time.

- If `RedshiftHandler()`, `Cache()`, or external service clients are created at module level, a temporary outage during deployment crashes the entire API — all endpoints, not just the affected ones
- **Real example (PR #1672):** `RedshiftHandler()`, `Cache()`, and service classes instantiated at module import time

### Correct Pattern
Use FastAPI `Depends()` or lazy initialization.

## 5. Graceful Degradation Quality

When degradation is intentional, verify:
- Is it documented why degradation was chosen over failure?
- Is there logging/monitoring to detect when degradation occurs?
- Can the consumer distinguish degraded results from normal results?
- **Real example (PR #1692):** `currentValue` defaults to 0 when data is null — no way to show loading/error state

## 6. Exception Class Hygiene

- Check for phantom exception references in docstrings (exceptions that don't exist in codebase)
- Check for duplicate exception classes across modules
- Check for shadowing builtins (e.g., `TimeoutError` shadowing Python's builtin)
- **Real example (PR #1672):** `DatabaseError`, `ServiceError` referenced in docstrings but didn't exist; `TimeoutError` shadowed Python builtin

## 7. Return Value Contracts

When a function has documented `Raises:` in its docstring, verify those exceptions actually can be raised. Conversely, if a function silently returns a default, verify the caller handles it.
