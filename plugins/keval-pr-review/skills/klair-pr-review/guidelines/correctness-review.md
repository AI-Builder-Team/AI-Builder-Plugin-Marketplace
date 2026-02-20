# Correctness & Logic Review

The most impactful dimension. Human reviewers at Klair catch domain logic bugs, semantic inversions, and cross-file inconsistencies more than any other category. This is where automated review tools typically fall short.

## 1. Semantic Correctness

Check that code does what its name/docstring/context claims.

### Formula & Calculation Verification
- **Verify every arithmetic expression** against its docstring or variable name
- Watch for inversions: `revenue - expenses` vs `expenses - revenue`
- Watch for percentage semantics: "remaining budget %" vs "utilization %"
- Check that the same metric uses the same formula everywhere in the codebase
- **Real example (PR #1672):** `variance_pct` computed as `(budget - spend) / budget * 100` in the summary but `actual / budget * 100` at the account level — same field name, opposite semantics in the same report

### Value Semantics
- When a value defaults to `0` or `""`, can the consumer distinguish "actual zero" from "data unavailable"?
- **Real example (PR #1692):** `KeyLeverCard` defaults to 0 when data is null — users can't tell if the value is actually zero or if loading failed

### Conditional Logic
- Verify all conditions are exhaustive (no missing else branches for meaningful cases)
- Check threshold comparisons: `<=` vs `<` should be consistent across related checks
- **Real example (PR #1672):** Service spike threshold used `<=` while WoW and budget used `<` — inconsistent without documentation

## 2. Cross-File Consistency

When the same concept exists in multiple files, verify they behave identically.

### Check For
- Same type/interface defined in multiple places (should be single source of truth)
- Same validation logic duplicated with subtle differences
- Same constant with different values across files
- **Real example (PR #1529):** `WoWFirstOfMonthData`, `WoWWeekData`, and `WoWHeatmapRow` defined in both `awsSpendApi.ts` and `types/wowHeatmap.ts`
- **Real example (PR #1672):** MD5 used for cache keys in one service, truncated SHA-256 in another, with no documented reason

### How to Check
1. When a new type/interface is introduced, search for similar names in the codebase
2. When a formula is changed, search for the same metric name in other files
3. When a constant is modified, search for its value or name elsewhere

## 3. Sort/Order Correctness

Sort operations are a frequent source of bugs.

- Verify sort comparators produce the intended order
- Watch for alphabetical sort on severity strings: `"critical" < "info" < "warning"` (wrong!)
- **Real example (PR #1672):** Jinja2 template `sort(attribute='severity')` sorted alphabetically, putting "info" before "warning"

## 4. Config Parameter Pass-Through

When a config/options object is accepted, verify every field is actually used.

- **Real example (PR #1672):** `ReportConfig.thresholds` accepted by API but never passed to `detect_outliers()` — custom thresholds silently dropped
- **Real example (PR #1672):** `ReportConfig.drill_down_limit` accepted but hardcoded to `10` internally

## 5. Docstring Accuracy

Verify docstrings match implementation (not just that they exist).

- Check specific numbers, formulas, and algorithm descriptions
- **Real example (PR #1734):** Test docstring claimed "6x standard rates" but fixture data showed 3x
- **Real example (PR #1692):** Docstring said "expenses - revenue" but code computed "revenue - expenses"

## 6. Model/Schema Validation

For Pydantic models and TypeScript interfaces:

- Check that `Field()` constraints match business rules (e.g., `ge=0` for amounts)
- Verify ordering constraints (e.g., `warning_threshold < critical_threshold`)
- Check that Literal types are used instead of plain `str` for finite value sets
- **Real example (PR #1672):** `OutlierThresholds` accepted inverted thresholds without validation
- **Real example (PR #1692):** `status: str` instead of `Literal["on_track", "warning", "over_budget"]`
