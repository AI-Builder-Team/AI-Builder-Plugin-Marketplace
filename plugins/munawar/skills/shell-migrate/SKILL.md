---
name: "m:shell-migrate"
description: "Plan migration of a legacy screen to the new-ui shell system"
argument-hint: "[screen-path-or-name]"
---

# Shell Migration Planner

You are migrating a legacy screen to the new-ui shell system. The target screen is: `$ARGUMENTS`

## Source of Truth

Read the migration guide first:
- `features/shell/new-ui-migration/FEATURE.md` -- full architecture, filter reference, data-feeding lifecycle, design tokens

Then read the shell implementation files for current filter types:
- `klair-client/src/shells/DesktopShell/FiltersContext.tsx` -- all filter types, interfaces, setters
- `klair-client/src/shells/DesktopShell/ConfigSidebar.tsx` -- desktop filter rendering
- `klair-client/src/shells/MobileShell/FilterSheet.tsx` -- mobile filter rendering

## Canonical Reference

The renewals screen is the gold standard. If you need to understand how a shell-integrated screen works end-to-end, read:
- Route config: `klair-client/src/shells/DesktopShell/routes.tsx` (search for `renewals`)
- Screen: `klair-client/src/screens/RenewalsShell/RenewalsShell.tsx`

## Migration Philosophy: Dual-Mode

**Screens must work at both routes simultaneously.** After migration:
- The screen renders at **both** the shell route (`/new-ui/...`) and the legacy route (`/...`)
- The **same screen component** serves both routes — no duplication
- Use `useFiltersOptional()` to detect which mode:
  - Returns the filters context when inside the shell (`/new-ui/...`)
  - Returns `null` when at the legacy route (no `FiltersProvider` wrapping it)
- **Shell mode** (`useFiltersOptional()` returns context): hide the inline filter component, read all filter values from `appliedValues.*` via the shell sidebar
- **Legacy mode** (`useFiltersOptional()` returns `null`): show the inline filter component as-is, read filter values from URL params / local state as before
- **Keep** the legacy filter component file (e.g., `FilterBar.tsx`) — it still renders on legacy routes
- **Keep** the legacy route entry in `App.tsx` — do NOT delete it
- Shared filtering/sorting logic uses a unified filters object via `useMemo` that normalizes from either source

**The key pattern:**
```tsx
const shellFilters = useFiltersOptional();
const isShellMode = !!shellFilters;
```

Then conditionally render the inline FilterBar only when `!isShellMode`.

## Migration Process

### Phase 1: Catalogue Legacy Filters

Read the target screen component thoroughly. For each piece of filter UI found:

1. **Identify every filter control** -- dropdowns, date pickers, range sliders, toggles, search inputs, tab selectors, checkboxes, radio groups
2. **Document each filter** in a table:

| Filter | Current UI | Data Source | Behaviour |
|--------|-----------|-------------|-----------|
| (name) | (dropdown / toggle / etc.) | (static / API / derived from data) | (multi-select / single / range / etc.) |

3. **Note where each filter lives** -- is it in a sticky header? Inline? A sidebar? URL params?

### Phase 2: Map to Shell Primitives

For each catalogued filter, map to the closest shell primitive:

**Four generic primitives (prefer these):**

| Shell Type | Use For |
|------------|---------|
| `dateRange` | Any date range picker, time period selector, predefined period chips |
| `range` | Any numeric min/max slider or range input |
| `viewMode` | Any tab/toggle that changes the data perspective or display mode (2+ states) |
| `multiSelect` | Any dropdown, checkbox group, or list selection -- configure N instances by key |

**Legacy types have generic equivalents (don't use legacy for new screens):**

| Legacy Type | Replace With |
|------------|-------------|
| `period` | `multiSelect` with `singleSelect: true` for year + quarter |
| `periodMonth` | `multiSelect` with `singleSelect: true` for year + month |
| `timeRange` | `dateRange` with `dateRangeShowQuickPresets: true` |
| `entityType` | `multiSelect` |
| `businessUnit` | `multiSelect` with `{ key: 'businessUnits' }` |
| `classes` | `multiSelect` with `{ key: 'classes' }` |
| `businessUnitSingle` | `multiSelect` with `singleSelect: true` |
| `classSingle` | `multiSelect` with `singleSelect: true` |

**multiSelect configuration properties:**

| Property | Type | Description |
|----------|------|-------------|
| `key` | string | Unique ID, used in `multiSelectValues[key]` |
| `label` | string | Sidebar display label |
| `singleSelect` | boolean | Radio behavior (one value only) |
| `hideSearch` | boolean | Hide search for short option lists |
| `hideAllToggle` | boolean | Hide "All" checkbox |
| `showForViewMode` | string or string[] | Conditional visibility based on viewMode |
| `tooltip` | string | Help text on hover |

**`singleSelect` guidance:**
- Default to plain `multiSelect` (multi-select). Users benefit from filtering by multiple values (e.g., "High + Medium" impact, "Triage + Assigned" status).
- Only use `singleSelect: true` when explicitly instructed, or when selecting multiple values is genuinely nonsensical (e.g., a time period like "Q1 2025", a view mode toggle, or a mutually exclusive grouping dimension).

Produce a mapping table:

| Legacy Filter | Shell Primitive | Config Key | Notes |
|--------------|----------------|------------|-------|
| (name) | (dateRange / range / viewMode / multiSelect) | (config detail) | (any nuance) |

### Phase 3: Gap Analysis

For each filter that does NOT cleanly map to an existing primitive:

1. **Can it be expressed as multiSelect?** Most categorical filters can. multiSelect supports singleSelect mode, conditional visibility, icon, count/percentage metadata.
2. **Can it be expressed as viewMode?** If it switches between display perspectives.
3. **Can it be expressed as dateRange with presets?** If it selects time windows.
4. **Is it truly unique?** Only flag as a gap if NONE of the four primitives work.

**Conservative enhancement principle:**
- Prefer mapping to existing primitives over proposing new filter types
- If a small, generic extension to an existing primitive solves the problem (e.g., adding a `maxOptions` prop to multiSelect), suggest it as a targeted enhancement
- If the extension would be too opinionated or only useful for this one screen, DON'T propose it -- recommend `CustomFilterComponent` as a fallback instead
- Thread the needle: enhance generically when the enhancement serves multiple future screens; use custom fallback when it's a one-off

Output either:
- "All filters map to existing primitives" (ideal case)
- A list of targeted, generic enhancements needed
- Filters that should use `CustomFilterComponent` (genuinely complex cases only)

### Phase 4: Generate Route Config

Write the complete route config entry for `routes.tsx`:

```tsx
const MyScreen = lazy(() => import('@/features/my-feature-v2/screens/MyScreen'));

// In newUIRoutes array:
{
  path: 'my-screen',
  title: 'My Screen',
  element: <LazyScreen component={MyScreen} />,
  filters: ['dateRange', 'viewMode', 'multiSelect'],  // only types actually needed
  filterDefaults: {
    // dateRange config...
    // viewMode config...
    // multiSelect instances...
  },
  permissionPath: 'legacy-route-path',  // maps to existing permission
}
```

### Phase 5: Screen Refactoring Plan

Describe the changes needed to the screen component:

1. **Dual-mode detection** -- add `useFiltersOptional()` import and `const isShellMode = !!shellFilters` at the top of the component
2. **Conditionally hide inline filters** -- wrap the existing filter component (e.g., `<FilterBar>`) in `{!isShellMode && <FilterBar ... />}`. Do NOT delete FilterBar.tsx — it still serves the legacy route.
3. **Unified filter object** -- create a `useMemo` that normalizes filters from either source into a single object:
   - Shell mode: read from `shellFilters.appliedValues.multiSelectValues[key]`, `shellFilters.appliedValues.search`, etc.
   - Legacy mode: read from existing URL params / local state (the current code)
4. **Feed data (shell mode only)** -- when `isShellMode`, call `setMultiSelectOptions()`, `setRangeDataBounds()`, `setDateRangeDataBounds()` after data loads. Guard these calls behind `if (shellFilters)`.
5. **boundsOnly pattern** -- on data refresh, call setters with `boundsOnly=true` to preserve user selections
6. **Shell contract (shell mode only)** -- when `isShellMode`:
   - Hide internal page title (shell provides it)
   - Outer wrapper should be `h-full overflow-y-auto`
   - Replace hardcoded colors with `var(--klair-*)` tokens
   - Use `appliedValues` not `values` for API calls
7. **Preserve legacy route** -- do NOT remove the legacy route entry from `App.tsx`. Do NOT delete the inline filter component file.

### Phase 6: Desktop + Mobile Verification

Verify both shells will work correctly:

**Desktop (ConfigSidebar):**
- All filter types declared in `filters` array render automatically
- multiSelect instances render in order declared in `multiSelectFilters`
- `showForViewMode` conditional visibility works
- Apply button workflow (working values -> applied values)

**Mobile (FilterSheet):**
- FilterSheet mirrors ConfigSidebar automatically for all generic primitives
- `singleSelect`, `hideSearch`, `showForViewMode`, `icon` all supported
- Bottom sheet interaction pattern (swipe to dismiss)
- No custom mobile work needed if using only generic primitives

**If CustomFilterComponent is used:**
- Must handle `isMobile` prop for responsive layout
- Must work within FilterSheet bottom sheet on mobile
- Document any mobile-specific considerations

## Output Format

Present the migration plan as a single document with these sections:

1. **Filter Catalogue** -- table of all legacy filters found
2. **Primitive Mapping** -- how each maps to shell types
3. **Gap Analysis** -- any enhancements needed (or "none")
4. **Route Config** -- complete `routes.tsx` entry (copy-paste ready)
5. **Screen Changes** -- bulleted list of removals, additions, refactoring steps
6. **Mobile Parity** -- confirmation or specific mobile concerns
7. **Data Feeding** -- which setters to call, when, with what data

Keep the plan actionable and specific. Reference actual function names, file paths, and code patterns from the target screen.
