# Data Pipeline Review

Patterns from review comments on ETL pipelines, Lambda handlers, and data processing code in `klair-udm/pipelines/`, `klair-api/` services, and related infrastructure.

## 1. Pipeline Failure Modes (CRITICAL)

### Silent Success on Failure
- If an entity fails mid-sync and the orchestrator catches and continues, verify:
  - Temp tables are cleaned up in the error path
  - Failed entities are tracked and reported
  - The pipeline return value distinguishes success from partial failure
- **Real example (PR #1851):** If `BaseLoader.load_entity` fails after S3 COPY but before MERGE, temp table may be left behind
- **Real example (PR #1734):** Pipeline runs to completion, reports success, but inserts rows with empty metadata

### Pipeline Return Values
Lambda/Step Function handlers must include:
```python
return {
    "status": "partial_failure",
    "processed": 45,
    "failed": 3,
    "errors": ["entity X: connection timeout", ...],
    "warnings": ["entity Y: no new data", ...]
}
```

Not just:
```python
return {"status": "success", "processed": 45}
```

### Data Deletion on LLM Failure
- If an LLM extraction fails and returns `[]`, verify the caller doesn't delete existing data and replace with nothing
- **Real example (PR #1739):** `extract_pain_points_for_account` caught all exceptions and returned `[]` — existing pain points deleted and replaced with nothing

## 2. SQL Construction in Pipelines (HIGH)

### Parameterization
- Use parameterized queries or the Redshift Data API's `Parameters` feature
- If using custom sanitization, apply it consistently to ALL paths (INSERT, DELETE, UPDATE)
- **Real example (PR #1734):** DELETE path used `_sanitize_string()` but INSERT path only did simple quote replacement

### Temp Table Management
- Prefer `CREATE TEMP TABLE` (auto-drops on session end) over permanent temp tables
- Add explicit cleanup in error paths

## 3. Entity Validation (HIGH)

### Input Validation
- Validate entity names against known allowlists before processing
- A typo in entity name should fail loudly, not silently skip
- **Real example (PR #1851):** `contact` (missing 's') would silently skip that entity

### Data Type Handling
- If external APIs return nested JSON or unexpected types, handle explicitly
- Float-to-int truncation should warn, not silently truncate
- **Real example (PR #1851):** `int(float(value))` silently truncates `3.7` to `3`
- **Real example (PR #1851):** Nested JSON objects stringified via `str()` could contain unescaped quotes

## 4. Environment & Configuration (MEDIUM)

### Env Var Documentation
- Every env var used in pipeline code should be in `pipeline.json` or equivalent config
- **Real example (PR #1851):** Env var used in code but not listed in `pipeline.json` environment section

### Dependency Files
- If `pyproject.toml` declares dependencies, don't also have a `requirements.txt` that can drift
- **Real example (PR #1851):** `requirements.txt` had 2 deps while `pyproject.toml` already declared them; Dockerfile didn't use `requirements.txt`

## 5. Retry & Error Classification (MEDIUM)

### Exception Filtering
- Don't filter exceptions by string matching on error messages — fragile and may miss cases
- **Real example (PR #1734):** `_wait_for_statement` caught all exceptions, only re-raised if message contained specific substrings — credential expiration would be swallowed

### Pricing/Cost Calculation
- When a model/product has no pricing match, it should NOT silently produce $0.00 records
- Zero-cost should be distinguishable from no-pricing-data
- **Real example (PR #1734):** New model names without pricing rows produced $0.00 records indistinguishable from zero-usage

## 6. Script Safety (MEDIUM)

### Database Migration Scripts
- Scripts that drop and recreate views/tables should use transactions or have rollback mechanisms
- **Real example (PR #1480):** Views dropped and created one by one — mid-way failure leaves DB inconsistent

### Exit Codes
- Pipeline scripts should exit with non-zero code on failure
- **Real example (PR #1779):** Script continued after endpoint failures without setting exit code
