# Frontend Review (React/TypeScript)

Patterns derived from 338 inline review comments on frontend code across 500 Klair PRs.

## 1. React State Management Anti-Patterns (HIGH)

### State Updates During Render
- Comparing props and calling `setState` inside the render function body is an anti-pattern
- Use `useEffect` with appropriate dependencies instead
- **Real example (PR #1692):** Comparing `buId !== prevBuId` inside render body and calling `setState`

### Missing Cleanup in Effects
- `useEffect` with subscriptions, timers, or event listeners must return a cleanup function
- Watch for WebSocket connections, `setInterval`, `addEventListener` without cleanup

### Stale Closures
- `useEffect` or `useCallback` capturing stale values due to missing dependencies
- Check that dependency arrays include all referenced variables

### Repeated Pattern: Dark Mode Tracking
- If dark mode detection (`document.documentElement.classList.contains('dark')`) is repeated across components, it should be a shared hook
- **Real example (PR #1524):** Dark mode tracking pattern repeated across different components

## 2. Object Mutation (HIGH)

### Never Mutate Props or State Directly
- Check for mutations on objects received from hooks or props
- **Real example (PR #1779):** Normalization mutated `result` object in place instead of creating a new spread

### Correct Pattern
```typescript
// Bad
result.field = normalized;

// Good
const normalized = { ...result, field: normalizedValue };
```

## 3. Date/Timezone Handling (HIGH)

This is the single largest gap category (109 comments).

### The UTC Midnight Bug
- `new Date('YYYY-MM-DD')` parses as UTC midnight per ECMAScript spec
- `.getMonth()`, `.getDate()` return local time
- For users west of UTC, this can return the wrong month/day at midnight boundaries
- **Real example (PR #1696):** `new Date('YYYY-MM-DD')` followed by `.getMonth()` — wrong month for US Pacific users

### Correct Pattern
```typescript
// Bad
const date = new Date('2025-01-15');
const month = date.getMonth(); // Could be Dec for US Pacific!

// Good
const [year, month, day] = '2025-01-15'.split('-').map(Number);
const date = new Date(year, month - 1, day);
```

## 4. TypeScript Type Safety (MEDIUM)

### Avoid Broad Types
- `Record<string, string>` when a specific interface exists
- `any` or implicit `any` in function parameters
- `string` when a Literal union type would be appropriate
- **Real example (PR #1692):** `BUId` as `string` instead of literal union `'physical-schools' | 'academics' | ...`

### Non-null Assertions
- `!` (non-null assertion) hides potential runtime errors
- Add defensive checks with helpful error messages
- **Real example (PR #1692):** `getBUConfig(buId)!` assumes config always exists — throws unhelpful error if config drifts

### Interface Duplication
- Same interface defined in multiple files — should have a single source of truth
- Check `types/` directory before adding new type definitions

## 5. Currency & Number Formatting (MEDIUM)

- Verify currency sign placement is consistent: `$-1.00M` vs `-$1.00M`
- Verify percentage values use consistent semantics (remaining vs utilization)
- **Real example (PR #1585):** `formatCurrency` produces `$-1.00M` (sign after $) while `formatGapImpact` produces `-$1.00M` (sign before $)

## 6. Accessibility (MEDIUM)

### Interactive Elements
- Clickable `<div>` elements need: `role="button"`, `tabIndex={0}`, `onKeyDown` handler
- **Real example (PR #1585):** Expandable header bar used `div` with `onClick()` but lacked keyboard accessibility

### Toast Notifications vs Alerts
- Klair uses toast notifications, not browser `alert()`
- **Real example (PR #1524):** Used `alert()` instead of `toast.error()`

## 7. Tooltip & Dynamic ID Fragility (MEDIUM)

- If tooltip IDs are generated dynamically but referenced with hardcoded strings, title changes break tooltips silently
- **Real example (PR #1524):** Tooltip IDs generated dynamically in component but hardcoded in render

## 8. Conditional Rendering & Loading States

- When data is `null`/`undefined`, show loading or error state — don't default to `0` or empty string
- Users must be able to distinguish "no data" from "loading" from "error"

## 9. Route & Navigation

### External Link Active State
- If external links have `path: ''`, the active state check `activePath === page.path` may incorrectly match at root `/`
- **Real example (PR #1496):** Active state matched empty string path for external links

## 10. Unused Props & Parameters

- Props declared in interface but never used in component
- Parameters prefixed with `_` suggesting incomplete implementation
- **Real example (PR #1692):** `buColor` prop declared but never used; `_bu` parameter prefixed with underscore
