# Commit & PR Style

## PR Descriptions

```
## Summary
[1-3 bullets. What changed, at a glance.]

## Why
[Motivation. What problem, what ticket, what was broken or missing.]

## Breaking changes
[Only if applicable. API contracts, data models, auth — not internal refactors.]

## Test plan
[Verification steps. Brief.]

[Screenshots if UI work.]
```

### Principles

- The Summary is NOT a changelog. 3 bullets max. Describe the change, not every file.
- The Why section is the most important part. Don't skip it.
- Never include "Files Changed" tables, commit lists, or per-spec/per-FR breakdowns in the body.
- Breaking changes only for core system boundary breaks that affect consumers. Internal rework doesn't count.
- Test plan: what a reviewer needs to verify it works. Not exhaustive.
- Aim for the minimum length that conveys What, Why, and How to test.

### Good PR summary

```
## Summary
- Add cross-domain field resolvers on SchoolMaster (enrollment, financials, surveys, marketing)
- Replace hardcoded school mapping dict with table-based lookups
- Deprecate consumer functions in quickbooks_school_mapping.py

## Why
School data lives across multiple domains but SchoolMaster had no way to resolve
related data. Hardcoded mappings were fragile and diverged from source tables.

## Test plan
- [x] 571 tests passing
- [ ] Deploy to dev and verify GraphQL cross-domain queries
```

### Anti-patterns

- Restating the diff (file lists, commit lists, type names, service internals)
- Spec-level detail in PR descriptions — the PR is not a spec
- 10+ bullet "summaries" that are really changelogs
- "Changes by spec" or "Changes by FR" breakdowns

## PR Titles

Format: `{prefix}({domain}): concise description`

- The scope is the **feature domain** from `features/` (e.g., `education`, `renewals`, `incidents`).
- NOT the spec name, sub-feature, or implementation detail.
- Stacking PRs in the same domain should all share the same scope — the stack should read as a coherent series.
- The description should be outcome-oriented. No class names, service names, or implementation details.
- Don't chain items with `+` — find the unifying theme instead.
- Keep under ~70 chars after the prefix.
- For fixes outside a feature domain, scope to the codebase area (e.g., `vendor`, `budgets`). Repeated fixes in the same area signal it's time to formalize a domain.

Good (consistent, outcome-oriented):
```
feat(education): add ontology YAML definitions and data layer conventions
feat(education): add GraphQL foundation and EduOps ontology layer
feat(education): add core data layer tables and refresh endpoint
feat(education): align GraphQL schema and update MCP tools
feat(education): add cross-domain resolvers and mapping cleanup
```

Bad (scattered scopes, implementation details in titles):
```
docs(ontology): ...
feat(fto-graphql): add FTO GraphQL API and EduOps ontology layer
feat(edu): add SchoolMaster.site reverse link + SchoolAliasService
feat(eduops): fto-gql-alignment + schools-gql-alignment + MCP tools
```

## Commit Messages

Format: `{prefix}({scope}): concise message`

Prefixes: `feat`, `fix`, `test`, `docs`, `spec`, `research`

- Commit scope can be more granular than PR scope (FR-level, spec-level) since commits are internal to the PR.
- Say what the commit does, not what files it touches.
- One line. No body unless genuinely complex.
- Good: `fix(budgets): preserve department in CF elimination entries`
- Bad: `fix(budgets): update CF COGS and CF Expenses elimination entry queries to include department column in GROUP BY and SELECT clauses instead of hardcoding to MS and G&A respectively`
