# Exploration Options

After initial table discovery, offer these exploration capabilities:

## 1. DISTINCT Values

**Use Case**: Understand unique values in categorical columns (status, type, category, etc.)

**Command**: `python utils/get_distinct_values.py <schema> <table> <column>`

**Output**: List of distinct values with counts, sorted by frequency

**Example**:
```
python utils/get_distinct_values.py core_finance maint_report_late_renewals status
```

## 2. Column Statistics

**Use Case**: Get numeric distributions, null counts, min/max values

**Command**: `python utils/get_column_stats.py <schema> <table> <column>`

**Output**:
- Total count
- Null count
- Distinct count
- Min/max values (for numeric/date columns)
- Sample values

**Example**:
```
python utils/get_column_stats.py core_finance maint_report_late_renewals arr_current
```

## 3. More Sample Rows

**Use Case**: See more examples beyond the initial 2 rows

**Command**: `python utils/get_sample_rows.py <schema> <table> <limit>`

**Output**: N rows in table format

**Example**:
```
python utils/get_sample_rows.py core_finance maint_report_late_renewals 10
```

## 4. Custom Query

**Use Case**: Run specific WHERE clauses or filters

**Command**: `python utils/run_custom_query.py <schema> <table> "<sql_fragment>"`

**Output**: Query results in table format

**Example**:
```
python utils/run_custom_query.py core_finance maint_report_late_renewals "WHERE arr_current > 10000 LIMIT 5"
```

## Presentation to User

When presenting options, show them as a menu:

```
Available explorations:
1. Get DISTINCT values for a column
2. Get column statistics (count, nulls, min/max)
3. Fetch more sample rows
4. Run custom query with filters

What would you like to explore?
```
