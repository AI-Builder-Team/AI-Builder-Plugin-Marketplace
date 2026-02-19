#!/usr/bin/env python3
"""Fetch table schema and sample rows from Redshift."""

import sys
from datetime import datetime
from db_connector import execute_query, get_output_file_path, sanitize_identifier

def format_value(val):
    """Format value for display."""
    if val is None:
        return "NULL"
    if isinstance(val, str):
        return f'"{val}"'
    return str(val)


def get_table_schema(schema, table):
    """Get column metadata for a table."""
    query = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default,
            ordinal_position
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
    """
    columns, rows = execute_query(query, (schema, table))

    if not rows:
        print(f"✗ Table {schema}.{table} not found or no columns accessible")
        sys.exit(1)

    return rows


def get_sample_rows(schema, table, limit=2):
    """
    Get sample rows from table.

    Note: schema and table should already be sanitized by the caller.
    """
    query = f'SELECT * FROM "{schema}"."{table}" LIMIT {limit}'
    try:
        columns, rows = execute_query(query)
        return columns, rows
    except (Exception, SystemExit) as e:
        print(f"✗ Error fetching sample rows: {e}")
        return [], []


def main():
    if len(sys.argv) != 3:
        print("Usage: python get_table_schema.py <schema> <table>")
        sys.exit(1)

    # Sanitize inputs to prevent SQL injection and path traversal
    schema = sanitize_identifier(sys.argv[1], "schema")
    table = sanitize_identifier(sys.argv[2], "table")

    print(f"Fetching schema for {schema}.{table}...")

    # Get column metadata
    columns = get_table_schema(schema, table)

    # Get sample rows
    sample_columns, sample_rows = get_sample_rows(schema, table, limit=2)

    # Generate markdown output at repo root
    output_file = get_output_file_path(schema, table)

    with open(output_file, "w") as f:
        f.write(f"# Table Exploration: {schema}.{table}\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Write column schema
        f.write("## Table Schema\n\n")
        f.write("| Column Name | Data Type | Nullable | Default | Position |\n")
        f.write("|-------------|-----------|----------|---------|----------|\n")

        for col in columns:
            col_name, data_type, nullable, default, position = col
            default_str = format_value(default)
            f.write(f"| {col_name} | {data_type} | {nullable} | {default_str} | {position} |\n")

        # Write sample rows
        f.write(f"\n## Sample Rows ({len(sample_rows)} rows)\n\n")

        if sample_rows:
            # Header
            f.write("| " + " | ".join(sample_columns) + " |\n")
            f.write("|" + "|".join(["---"] * len(sample_columns)) + "|\n")

            # Rows
            for row in sample_rows:
                formatted_row = [format_value(val) for val in row]
                f.write("| " + " | ".join(formatted_row) + " |\n")
        else:
            f.write("*No sample rows available*\n")

        # Write exploration options
        f.write("\n## Available Explorations\n\n")
        f.write(f"1. **DISTINCT values**: `python utils/get_distinct_values.py {schema} {table} <column>`\n")
        f.write(f"2. **Column statistics**: `python utils/get_column_stats.py {schema} {table} <column>`\n")
        f.write(f"3. **More sample rows**: `python utils/get_sample_rows.py {schema} {table} <limit>`\n")
        f.write(f"4. **Custom query**: `python utils/run_custom_query.py {schema} {table} \"<WHERE clause>\"`\n")

    print(f"✓ Schema written to: {output_file}")
    print(f"✓ Columns: {len(columns)}")
    print(f"✓ Sample rows: {len(sample_rows)}")


if __name__ == "__main__":
    main()
