#!/usr/bin/env python3
"""Execute DDL statements (CREATE VIEW, etc.) against Redshift.

This script bypasses the read-only mode used by other utilities
to allow executing DDL statements like CREATE VIEW.

Usage:
    python execute_ddl.py <sql_file_path>

Example:
    python execute_ddl.py /path/to/005_account_costs_summary_adjusted_view_create.sql
"""

import sys
from pathlib import Path

from db_connector import get_connection


def execute_ddl(sql):
    """Execute a DDL statement."""
    conn = get_connection(read_only=False)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        print("✓ DDL executed successfully")
    except Exception as e:
        print(f"✗ Error executing DDL: {e}")
        sys.exit(1)
    finally:
        conn.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python execute_ddl.py <sql_file_path>")
        print("Example: python execute_ddl.py /path/to/create_view.sql")
        sys.exit(1)

    sql_file = Path(sys.argv[1])
    if not sql_file.exists():
        print(f"✗ File not found: {sql_file}")
        sys.exit(1)

    sql = sql_file.read_text()

    # Display the SQL being executed
    print(f"Executing DDL from: {sql_file}\n")
    print("-" * 60)
    print(sql[:500] + ("..." if len(sql) > 500 else ""))
    print("-" * 60)
    print()

    execute_ddl(sql)


if __name__ == "__main__":
    main()
