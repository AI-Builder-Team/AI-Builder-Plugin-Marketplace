#!/usr/bin/env python3
"""Get statistics for a column (count, nulls, distinct, min/max)."""

import sys
from db_connector import execute_query, get_output_file_path, sanitize_identifier


def main():
    if len(sys.argv) != 4:
        print("Usage: python get_column_stats.py <schema> <table> <column>")
        sys.exit(1)

    # Sanitize inputs to prevent SQL injection
    schema = sanitize_identifier(sys.argv[1], "schema")
    table = sanitize_identifier(sys.argv[2], "table")
    column = sanitize_identifier(sys.argv[3], "column")

    print(f"Fetching statistics for {schema}.{table}.{column}...")

    query = f"""
        SELECT
            COUNT(*) as total_count,
            COUNT("{column}") as non_null_count,
            COUNT(*) - COUNT("{column}") as null_count,
            COUNT(DISTINCT "{column}") as distinct_count,
            MIN("{column}") as min_value,
            MAX("{column}") as max_value
        FROM "{schema}"."{table}"
    """

    columns, rows = execute_query(query)

    if not rows:
        print("✗ No statistics available")
        sys.exit(1)

    stats = rows[0]
    total_count, non_null_count, null_count, distinct_count, min_value, max_value = stats

    print(f"\n✓ Statistics for {column}:\n")
    print(f"Total Rows:       {total_count:,}")
    print(f"Non-Null Values:  {non_null_count:,}")
    print(f"Null Values:      {null_count:,}")
    print(f"Distinct Values:  {distinct_count:,}")
    print(f"Min Value:        {min_value}")
    print(f"Max Value:        {max_value}")

    # Append to exploration file at repo root
    output_file = get_output_file_path(schema, table)
    try:
        with open(output_file, "a") as f:
            f.write(f"\n### Column Statistics: {column}\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Total Rows | {total_count:,} |\n")
            f.write(f"| Non-Null Values | {non_null_count:,} |\n")
            f.write(f"| Null Values | {null_count:,} |\n")
            f.write(f"| Distinct Values | {distinct_count:,} |\n")
            f.write(f"| Min Value | {min_value} |\n")
            f.write(f"| Max Value | {max_value} |\n")
        print(f"\n✓ Results appended to {output_file}")
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
