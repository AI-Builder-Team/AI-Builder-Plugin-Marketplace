# Backend Review (Python/FastAPI)

Patterns derived from 390 inline review comments on backend code across 500 Klair PRs.

## 1. Exception Handling (CRITICAL)

See [error-handling-review.md](error-handling-review.md) for the comprehensive guide. Key backend-specific points:

### Catch-and-Wrap Pattern
- `except Exception as e: raise APIError(...) from e` preserves the chain but loses the original HTTP status
- If the original was `ValueError` (422) or a specific domain error, wrapping as generic `APIError` forces 500
- Either let specific exceptions propagate or map them to appropriate HTTP status codes

### `return_exceptions=True` in `asyncio.gather()`
- When used, you MUST check each result for `isinstance(result, Exception)`
- Otherwise exceptions are silently stored as values in the results list

## 2. Pydantic Model Discipline (HIGH)

### Field Constraints
- Use `Field(ge=0)` for amounts, counts, percentages that can't be negative
- Use `Field(le=100)` for percentages that shouldn't exceed 100
- Add `model_validator` for cross-field constraints (e.g., `warning_threshold < critical_threshold`)
- **Real example (PR #1672):** `OutlierThresholds` accepted inverted thresholds without validation

### Literal Types Over Strings
- Use `Literal["on_track", "warning", "over_budget"]` instead of `str` for finite value sets
- **Real example (PR #1692):** `status: str` allows any string value

### Avoid `List[dict]` Type Holes
- If a model exists for the data, use `List[Model]` not `List[dict]`
- `.model_dump()` into `dict` then passing to templates loses type safety
- **Real example (PR #1672):** `top_accounts: List[dict]` when `TopAccount` model existed

### Count Consistency
- If a model has both a list and a count field, add a validator ensuring they match
- **Real example (PR #1672):** `total_outliers` stored independently from `outliers` list — no consistency validator

## 3. FastAPI Router Patterns (HIGH)

### Response Models
- Every endpoint should have a `response_model` parameter
- Returning plain `dict` without `response_model` skips validation
- **Real example (PR #1598):** Endpoint returned plain `dict` without `response_model`

### Query Parameter Validation
- Add `max_length` constraints on string query parameters
- Limit array sizes for list parameters
- **Real example (PR #1779):** Missing `max_length` on query param — added `max_length=4000` and UUID limit of 100

### Lazy Initialization
- Don't instantiate DB handlers, cache clients, or external service clients at module level
- Use FastAPI `Depends()` for dependency injection

## 4. Redshift & Database Patterns (HIGH)

### `fetch_with_params` vs `fetch_with_params_strict`
- `fetch_with_params()` returns `None` on error (dangerous — callers treat None as empty)
- `fetch_with_params_strict()` raises on error (correct for most use cases)
- Always prefer `fetch_with_params_strict()` unless degradation is explicitly documented

### Year Conversion
- The `if end_year < 100: end_year = 2000 + end_year` pattern is duplicated — should be a utility
- **Real example (PR #1371):** Year conversion duplicated in multiple routers

### Excluded Types Constants
- If the same exclusion list (e.g., `("Virtual", "Other")`) is used across routers, extract to a constant
- **Real example (PR #1371):** Excluded school types used consistently but not extracted to constant

## 5. Cache Usage (MEDIUM)

### TTL Configuration
- TTL is set at cache initialization, not per-call — verify `Cache.set()` isn't passed unsupported `ttl` param
- **Real example (PR #1672):** `Cache.set(ttl=3600)` — parameter doesn't exist, `TypeError` caught and swallowed

### Cache Key Consistency
- Use the same hashing approach across the codebase (MD5 vs SHA-256 vs other)
- **Real example (PR #1672):** Reports used MD5, outlier detection used truncated SHA-256

### Docstring/Comment Accuracy on TTL
- Verify cache TTL comments match actual configuration
- **Real example (PR #1672):** Docstring said "5 minutes" but actual TTL was 1 hour

## 6. Logging & Observability (MEDIUM)

### Log at Appropriate Levels
- `logger.warning` for degraded behavior that's recoverable
- `logger.error` for failures that affect correctness
- Include context: what operation, what input, what happened
- **Real example (PR #1779):** Added `logger.warning` when expected extract key not found

### Pipeline Return Values
- Lambda/pipeline handlers should include error, warning, and skip counts in return values
- **Real example (PR #1734):** Handler return dict had no fields for errors, warnings, or failed counts

## 7. Import & Module Patterns (MEDIUM)

### Module-Level Imports
- Heavy imports (pandas, numpy) should be at module level, not inside functions (unless conditionally needed)
- Module names should not shadow builtins (`secrets.py`, `logging.py`)

### Duplicate Exception Classes
- Check for same exception class defined in multiple modules
- Consolidate to a shared `exceptions.py` or `models/exceptions.py`
- **Real example (PR #1672):** `ConfigurationError` defined in both `reports_service.py` and `outlier_detection_service.py`

## 8. DRY Violations (MEDIUM)

### Common Patterns to Extract
- Date range parsing/validation
- Year conversion logic
- School type exclusion lists
- Currency formatting
- Cache key generation

### Helper Placement
- Shared across routers → `utils/`
- Shared within a feature → feature's own `utils.py`
- Used in only one place → keep inline (don't prematurely abstract)
