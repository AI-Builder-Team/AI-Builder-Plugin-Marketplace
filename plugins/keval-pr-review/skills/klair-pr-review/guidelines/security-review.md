# Security Review

Security issues in Klair PRs fall into categories beyond just SQL injection. This guide covers the patterns actually found in the codebase.

## 1. SQL Injection & Query Construction

### String Interpolation in SQL
- Any SQL query built with f-strings, `.format()`, or string concatenation is suspect
- Check that user-controlled values never enter SQL without parameterization
- **Real example (PR #1851):** `_get_last_cursor` constructs SQL with string interpolation — crafted entity names like `contacts' OR 1=1 --` could bypass `_sanitize_string`

### Sanitization Completeness
- If a custom `_sanitize_string` is used instead of parameterized queries, verify it handles:
  - Single quotes
  - Backslash escaping
  - Null bytes
  - Unicode edge cases
- Check that sanitization is applied consistently — not just in DELETE but also INSERT paths
- **Real example (PR #1734):** DELETE path used `_sanitize_string()` but INSERT path only did `str(val).replace("'", "''")`

### Parameter Validation
- Validate inputs against allowlists before use in SQL
- **Real example (PR #1851):** `entity` parameter from event not validated against `ALL_ENTITIES` — a typo silently skips the entity

## 2. XSS & Template Injection

### Jinja2 `| safe` Filter
- Any use of `| safe` on user-controlled or AI-generated content disables auto-escaping
- Attack chain: malicious data in DB → AI model echoes it → rendered unsanitized
- **Real example (PR #1672):** `{{ ai_insights.summary | safe }}` across ~12 locations in daily.html and weekly.html

### React `dangerouslySetInnerHTML`
- Same concern as `| safe` — verify the content source is trusted

## 3. Error Information Exposure

### Check For
- `HTTPException(detail=f"... {e}")` — may expose internal paths, DB hostnames, stack traces
- Error responses that include full exception messages
- **Real example (PR #1672):** `detail=f"Report generation failed: {e}"` could leak database hostnames or file paths

### Correct Pattern
- Log full error internally with `exc_info=True`
- Return generic message to client

## 4. Configuration Security

### Production Fallbacks to Dev URLs
- If an env var is missing and code falls back to a dev URL, production users get dev behavior
- **Real example (PR #1672):** `FRONTEND_BASE_URL` falls back to `dev.d3v0b331t4rxas.amplifyapp.com` in production

### Correct Pattern
- Raise `ConfigurationError` in production when required env vars are missing
- Never use dev URLs as default fallbacks

## 5. Input Validation at Boundaries

### API Endpoints
- Validate and constrain string lengths on query parameters (`max_length=...`)
- Validate array sizes (limit number of IDs in list parameters)
- **Real example (PR #1779):** Added `max_length=4000` on query param and limit of 100 UUIDs

### Module Naming
- Avoid naming modules after Python builtins (`secrets.py` shadows `import secrets`)
- **Real example (PR #1851):** `secrets.py` module name shadows Python's built-in `secrets` module

## 6. Authentication & Authorization

### Check For
- Endpoints missing auth decorators/dependencies
- Service functions that bypass auth checks
- API keys or tokens in code (should be in env vars)
- `os.environ["KEY"]` at module level crashes if missing — use `os.environ.get()` with validation
