#!/usr/bin/env python3
"""Fetch N sample rows from a table."""

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
        print("Usage: python get_sample_rows.py <schema> <table> <limit>")
        sys.exit(1)

    # Sanitize inputs to prevent SQL injection
    schema = sanitize_identifier(sys.argv[1], "schema")
    table = sanitize_identifier(sys.argv[2], "table")
    try:
        limit = int(sys.argv[3])
        if limit <= 0:
            print("✗ Limit must be a positive integer")
            sys.exit(1)
    except ValueError:
        print("✗ Limit must be an integer")
        sys.exit(1)

    print(f"Fetching {limit} sample rows from {schema}.{table}...")

    query = f'SELECT * FROM "{schema}"."{table}" LIMIT {limit}'
    columns, rows = execute_query(query)

    print(f"\n✓ Fetched {len(rows)} rows:\n")

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
            f.write(f"\n### Sample Rows ({len(rows)} rows)\n\n")
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
