#!/usr/bin/env python3
"""Get distinct values for a column with counts."""

import sys
from db_connector import execute_query, get_output_file_path, sanitize_identifier


def main():
    if len(sys.argv) != 4:
        print("Usage: python get_distinct_values.py <schema> <table> <column>")
        sys.exit(1)

    # Sanitize inputs to prevent SQL injection
    schema = sanitize_identifier(sys.argv[1], "schema")
    table = sanitize_identifier(sys.argv[2], "table")
    column = sanitize_identifier(sys.argv[3], "column")

    print(f"Fetching distinct values for {schema}.{table}.{column}...")

    query = f"""
        SELECT
            "{column}" as value,
            COUNT(*) as count
        FROM "{schema}"."{table}"
        GROUP BY "{column}"
        ORDER BY count DESC
        LIMIT 100
    """

    columns, rows = execute_query(query)

    print(f"\n✓ Found {len(rows)} distinct values (showing top 100):\n")
    print(f"{'Value':<40} | {'Count':>10}")
    print("-" * 53)

    for row in rows:
        value, count = row
        value_str = str(value) if value is not None else "NULL"
        print(f"{value_str:<40} | {count:>10,}")

    # Append to exploration file at repo root
    output_file = get_output_file_path(schema, table)
    try:
        with open(output_file, "a") as f:
            f.write(f"\n### DISTINCT Values: {column}\n\n")
            f.write("| Value | Count |\n")
            f.write("|-------|-------|\n")
            for row in rows:
                value, count = row
                value_str = str(value) if value is not None else "NULL"
                f.write(f"| {value_str} | {count:,} |\n")
        print(f"\n✓ Results appended to {output_file}")
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
