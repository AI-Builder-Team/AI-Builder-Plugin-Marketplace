---
description: Trace data lineage for a feature keyword from source to UI
argument-hint: [feature-keyword]
---

## Context

You are tracing **data lineage** for the feature keyword: `$ARGUMENTS`

Data lineage means mapping how data flows end-to-end: from its origin (database tables, external APIs, third-party integrations) through backend services and API endpoints, all the way to the frontend components that display it.

## Task

Investigate and map the complete data flow for the given feature keyword. Launch parallel research agents to explore all layers simultaneously.

### 1. Identify Data Sources
- Database tables (Redshift, DynamoDB, Cassandra) that store the raw data
- External APIs or integrations (Salesforce, NetSuite, QuickBooks, Google Sheets) that provide data
- Redis cache keys involved
- Any S3 objects or files

### 2. Trace Pipeline Processing
- Pydantic models that define the data shape
- Any places where AI is used to compute or add to the data, particularly noting
  - inputs to the AI
  - outputs from the AI
- Very important to catch where missteps might occur in case the AI is provided with wrong / null / none or default inputs that could potentially cause it to spit out garbage. 

### 4. Map Transformations
- Where data gets transformed, aggregated, or filtered
- Any computed/derived fields
- Format conversions or enrichments

## Output Format

Present the lineage as a clear flow diagram using text:

```
SOURCE(S)
  database_table / external_api
    ↓
PIPELINES
  router → service → model
    ↓
CACHE (if any)
  redis key / pattern
    ↓
```

Then provide a **file reference table**:

| Layer | File | Key Function/Class | Purpose |
|-------|------|--------------------|---------|
| DB | ... | ... | ... |
| Router | ... | ... | ... |
| Service | ... | ... | ... |
| Model | ... | ... | ... |

Finally, note any **gaps or concerns**:
- Missing error handling in the chain
- Data that could go stale (cache without invalidation)
- Transformations that lose information
- Undocumented dependencies between layers
