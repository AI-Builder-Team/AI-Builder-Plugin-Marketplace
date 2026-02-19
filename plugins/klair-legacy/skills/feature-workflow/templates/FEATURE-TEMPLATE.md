# Feature: {Feature Name}

## Feature ID

`{feature-id}`

## Metadata

| Field | Value |
|-------|-------|
| **Domain** | {Must be from features/index.md} |
| **Feature Name** | {Feature Name} |
| **Contributors** | {Auto-populated via `gh api user --jq '.login'`} |

## Table of Contents

- [Files Touched](#files-touched)
- [Linear Tickets](#linear-tickets)
- [Related Surfaces](#related-surfaces)
- [Related Features](#related-features)
- [Feature Overview](#feature-overview)
- [Intended State](#intended-state)
- [System Architecture](#system-architecture)
- [Changelog of Feature Specs](#changelog-of-feature-specs)

## Files Touched

- `{path/to/file-or-directory}` - {Brief description}

## Linear Tickets

| Ticket ID | Title |
|-----------|-------|
| {KLAIR-XXX} | {Ticket title} |

## Related Surfaces

### Frontend Routes
- `{/path/to/route}` - {Description}

### Backend Endpoints

<!--
GUIDANCE: This project has two backend systems. Document all endpoints your feature uses.

**Backend Types:**

1. **FastAPI (klair-api/)** - Primary REST API
   - Format: `METHOD /path`
   - Examples:
     - `POST /api/budget/analyze` - Analyze budget data
     - `GET /renewals/dashboard` - Fetch renewals dashboard data
     - `POST /claire/chat` - Send message to Claire AI assistant

2. **GraphQL (klair-udm/)** - Unified Data Model API for financial data
   - AppSync-based GraphQL API connected to Redshift
   - Format: `query QueryName(params)` or `mutation MutationName(params)`
   - Examples:
     - `query getFinancials(reportDate, date)` - Fetch financial summary
     - `query getLiveFinancials` - Fetch live ARR data by class/BU
     - `query getRetentionAnalysis` - Fetch retention metrics
     - `query getSnowballVariances(date)` - Fetch ARR variance data

**How to document:**
- Include HTTP method for REST endpoints (GET, POST, PUT, DELETE)
- For GraphQL, specify query vs mutation and list key parameters
- Add brief description of what the endpoint does
- Note any important parameters or filters
-->

- `{METHOD /path}` - {Description}
- `{query/mutation OperationName(params)}` - {Description}

### Redshift & DB Tables
- `{table_name}` - {Description}

### Schemas/Models

<!--
GUIDANCE: Document schemas/models with their fields. Include field types and descriptions.

**Example:**
```
**UserProfile** - User profile data for dashboard display
- `id: string` - Unique user identifier
- `email: string` - User's email address
- `role: 'admin' | 'viewer' | 'editor'` - User's permission level
- `preferences: UserPreferences` - Nested preferences object
```
-->

- **{SchemaName}** - {Description}
  - `{fieldName: type}` - {Field description}

### Config Variables
- `{VARIABLE_NAME}` - {Description}

### Permissions
- `{permission.name}` - {Description}

## Related Features

- [{related-feature-id}](../related-feature-id/FEATURE.md) - {Brief description}

## Feature Overview

### Summary

{Brief summary of the feature}

### Problem Statement

{What problem does this feature solve?}

### Goals

- {Goal 1}
- {Goal 2}

### Non-Goals

- {What this feature explicitly does NOT do}

## Intended State

<!--
GUIDANCE: Describe the final intended design only. Do NOT document current state or changes needed to reach the final state—just describe how the feature should work when complete.
-->

{Description of how the feature should work when complete}

## System Architecture

{Brief summary of the architecture behind the system}

## Changelog of Feature Specs

| Date | Spec | Description |
|------|------|-------------|
| {YYYY-MM-DD} | [spec-name.md](specs/spec-name.md) | {What was implemented} |
