---
name: exploring-redshift-tables
description: Help users explore Redshift table schemas and data interactively. Use when user wants to understand table structure, see sample data, or explore column values. Trigger phrases "explore redshift table", "show me table structure", "redshift table schema", "what's in the table"
---

# Exploring Redshift Tables

Help users explore Redshift table schemas and data interactively by fetching column metadata, sample rows, and providing utilities for deeper exploration.

## When to Use

Use this skill when users want to:
- Explore a specific Redshift table's structure and sample data
- Get DISTINCT values for a column
- Check column statistics (counts, nulls, distributions)
- Understand table contents through various explorations

**Trigger phrases**: "explore redshift table", "show me table structure", "redshift table schema", "what's in the table"

## Prerequisites

- AWS credentials configured (for Secrets Manager access)
- User provides table in format: `schema.table` (e.g., `core_finance.maint_report_late_renewals`)
- Python dependencies: `boto3`, `redshift-connector`

## Core Workflow

### Phase 1: Initial Discovery

1. **Parse Input**: Extract schema and table name from user input (format: `schema.table`)

2. **Fetch Table Metadata**:
   - Run `python utils/get_table_schema.py <schema> <table>`
   - This fetches columns, data types, and 2 sample rows
   - Outputs to `<schema>_<table>_exploration.md` at repo root

3. **Present Results**: Show the user the markdown file location and contents summary

4. **Offer Explorations**: Present available exploration options from `guidelines/exploration-options.md`

### Phase 2: Optional Explorations

Based on user interest, run the appropriate utility:

- **DISTINCT values**: `python utils/get_distinct_values.py <schema> <table> <column>`
- **Column statistics**: `python utils/get_column_stats.py <schema> <table> <column>`
- **More sample data**: `python utils/get_sample_rows.py <schema> <table> <limit>`
- **Custom query**: `python utils/run_custom_query.py <schema> <table> "<sql_fragment>"`

Output exploration results to the same markdown file or separate files as appropriate.

### Phase 3: Cleanup (Optional)

Ask user if they want to keep the exploration files or remove them.

## File Structure

```
utils/
  db_connector.py            # Shared AWS Secrets Manager + Redshift connection
  test_connection.py         # Verify setup and test connection
  get_table_schema.py        # Fetch columns, types, sample rows
  get_distinct_values.py     # Get unique values for a column
  get_column_stats.py        # Get count, nulls, min, max for a column
  get_sample_rows.py         # Fetch N sample rows
  run_custom_query.py        # Run custom SQL fragment

guidelines/
  exploration-options.md     # Detailed descriptions of each exploration type
  setup-guide.md            # AWS Secrets Manager setup, dependencies

requirements.txt             # Python dependencies
```

## Important Notes

- All utilities use AWS Secrets Manager secret: `klair/redshift-creds`
- Output files created at repo root: `<schema>_<table>_exploration.md`
- Files are temporary - user can keep or discard
- Handle errors gracefully (missing tables, permission issues, connection failures)
- Run `python3 utils/test_connection.py` to verify setup before exploring tables
