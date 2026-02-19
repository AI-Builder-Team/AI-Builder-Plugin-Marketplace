# Review Dimensions

Each dimension below defines what to look for and common failure modes. Evaluate every dimension for every spec. Rate each as PASS, CONCERN, or FAIL.

---

## 1. Feasibility

**Question:** Can this actually be built as described with the technology, codebase, and constraints that exist?

**What to check:**
- Do the APIs, libraries, and frameworks mentioned actually support what the spec describes?
- Are there performance constraints the spec ignores (e.g., large dataset rendering, API rate limits)?
- Does the proposed data flow actually work end-to-end, or does it hand-wave over a hard part?
- Are there infrastructure or deployment constraints (e.g., needs a new service, requires DB migration)?

**Common failures:**
- Spec assumes an API returns data it doesn't actually return
- Spec proposes a UI pattern that the component library doesn't support
- Spec ignores latency/performance for operations that will be slow
- Spec requires changes to shared infrastructure but scopes it as a simple feature change

---

## 2. Completeness

**Question:** Does the spec cover everything needed to implement this feature, or will the implementer hit unknowns?

**What to check:**
- Are all user-facing states covered? (loading, empty, error, populated, edge cases)
- Are error handling behaviors specified? (what happens when the API fails, when data is missing)
- Are there implicit requirements the spec doesn't mention? (permissions, mobile/responsive, accessibility)
- Do the FRs cover the full scope described in the Overview, or does the Overview promise more than the FRs deliver?

**Common failures:**
- Overview describes 5 capabilities but FRs only cover 3
- No error state handling defined
- Empty state not specified (what does the user see with no data?)
- Permissions/authorization not addressed when the feature clearly needs it

---

## 3. Scope Calibration

**Question:** Is this the right size for one spec? Is the boundary drawn in the right place?

**What to check:**
- Number of FRs: 3-5 is healthy, 8+ is a red flag for scope creep
- Estimated lines of code: >600 LOC suggests the spec should be split
- Out of Scope items: do any of them actually need to be in-scope for the feature to be useful?
- Dependencies on other specs: circular or excessive dependencies suggest poor decomposition

**Common failures:**
- Spec tries to do too much (backend + frontend + new component library + tests)
- Spec does too little (creates a type file but nothing uses it — not independently valuable)
- Out of Scope excludes something critical (e.g., "error handling is out of scope" for an API integration)
- Spec depends on 3+ other specs, making it unprioritizable

---

## 4. Assumption Audit

**Question:** What does the spec assume without saying so? Are those assumptions valid?

**What to check:**
- Data availability assumptions (does the data actually exist where the spec says it does?)
- User behavior assumptions (will users actually interact with this the way the spec expects?)
- Performance assumptions (will this be fast enough without optimization?)
- Dependency assumptions (will upstream services/APIs remain stable and available?)

**How to find hidden assumptions:**
- Look for phrases like "the existing endpoint returns...", "the component already supports...", "this data is available in..."
- Each of these is a claim that can be verified against the codebase
- Unverifiable claims are unvalidated assumptions

**Common failures:**
- "The API already returns this field" — but it doesn't
- "This component accepts a custom renderer" — but it doesn't
- Spec assumes single-tenant behavior but the system is multi-tenant
- Spec assumes synchronous flow but the actual system is async

---

## 5. Risk Identification

**Question:** What could go wrong during implementation that the spec doesn't anticipate?

**What to check:**
- Are there known fragile areas of the codebase this spec touches?
- Could this change break existing functionality? (regression risk)
- Are there race conditions, timing issues, or concurrency concerns?
- Is there a migration or data transformation that could fail?
- Are there third-party service dependencies that could be unreliable?

**Common failures:**
- Spec modifies a shared component but doesn't consider other consumers
- Spec adds a new DB query but doesn't consider query performance at scale
- Spec relies on an external service with no fallback strategy
- Spec changes state management without considering concurrent access

---

## 6. Interface Contracts

**Question:** Are the interface contracts precise enough to code against, and do they match reality?

**What to check:**
- Are types fully specified? (no `any`, no hand-wavy "object with fields")
- Do function signatures include error cases? (what does the function return on failure?)
- Are optional vs required fields clearly marked?
- Do the contracts match the actual API responses / component props in the codebase?

**Common failures:**
- Interface says field is required but the API sometimes omits it
- Interface uses `string` for what should be a union type or enum
- Contract doesn't specify null/undefined handling
- Contract defines types that conflict with existing types in the codebase

---

## 7. Testability

**Question:** Can the success criteria actually be verified with automated tests? Are they specific enough?

**What to check:**
- Each FR success criteria: is it a verifiable statement or a vague aspiration?
- Can the criteria be tested without manual inspection? (if not, it's not a success criterion)
- Are there numeric thresholds or specific behaviors stated, or just "works correctly"?
- Does the test plan in spec-research.md actually cover the FRs in spec.md?

**Vague vs Specific examples:**

| Vague (FAIL) | Specific (PASS) |
|---------------|-----------------|
| "Data displays correctly" | "Table renders all rows from API response with columns: name, amount, date" |
| "Error handling works" | "API failure shows error banner with message, retry button re-fetches" |
| "Performance is acceptable" | "Table renders 500 rows in <200ms, verified via test timing" |
| "UI matches design" | "Component uses `MetricCard` with `comparison` prop showing delta chip" |

**Common failures:**
- Success criteria is just the requirement restated ("the feature works as described")
- No error case testing specified
- Success criteria requires visual inspection ("looks correct")
- Criteria can't be automated (requires specific user accounts or production data)
