#!/usr/bin/env python3
"""Run custom query with WHERE clause or other SQL fragments."""

import sys
from db_connector import execute_query, get_output_file_path, sanitize_identifier


def format_value(val):
    """Format value for display."""
    if val is None:
        return "NULL"
    if isinstance(val, str):
        return f'"{val}"'
    return str(val)


def main():
    if len(sys.argv) != 4:
        print("Usage: python run_custom_query.py <schema> <table> \"<sql_fragment>\"")
        print("Example: python run_custom_query.py core_finance arr_data \"WHERE arr_current > 10000 LIMIT 5\"")
        sys.exit(1)

    # Sanitize schema and table to prevent SQL injection
    # Note: sql_fragment is intentionally user-provided SQL for WHERE/LIMIT clauses
    schema = sanitize_identifier(sys.argv[1], "schema")
    table = sanitize_identifier(sys.argv[2], "table")
    sql_fragment = sys.argv[3]

    # Build full query
    query = f'SELECT * FROM "{schema}"."{table}" {sql_fragment}'

    print(f"Running custom query:\n{query}\n")

    columns, rows = execute_query(query)

    print(f"\n✓ Query returned {len(rows)} rows:\n")

    # Print header
    header = " | ".join(columns)
    print(header)
    print("-" * len(header))

    # Print rows
    for row in rows:
        formatted_row = [format_value(val) for val in row]
        print(" | ".join(formatted_row))

    # Append to exploration file at repo root
    output_file = get_output_file_path(schema, table)
    try:
        with open(output_file, "a") as f:
            f.write(f"\n### Custom Query Results\n\n")
            f.write(f"**Query**: `{sql_fragment}`\n\n")
            f.write("| " + " | ".join(columns) + " |\n")
            f.write("|" + "|".join(["---"] * len(columns)) + "|\n")
            for row in rows:
                formatted_row = [format_value(val) for val in row]
                f.write("| " + " | ".join(formatted_row) + " |\n")
        print(f"\n✓ Results appended to {output_file}")
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
