"""Apply SQL migration files to Redshift (with write access)."""

import sys
from pathlib import Path

from db_connector import get_connection


def execute_sql_file(file_path):
    """Execute a SQL file against Redshift."""
    path = Path(file_path)
    if not path.exists():
        print(f"✗ File not found: {file_path}")
        sys.exit(1)

    sql_content = path.read_text()

    # Split by semicolons but filter out empty statements and comments-only blocks
    statements = []
    for stmt in sql_content.split(';'):
        # Remove leading/trailing whitespace
        stmt = stmt.strip()
        # Skip empty statements
        if not stmt:
            continue
        # Skip statements that are only comments
        lines = [l.strip() for l in stmt.split('\n') if l.strip() and not l.strip().startswith('--')]
        if lines:
            statements.append(stmt)

    conn = get_connection(read_only=False)
    try:
        cur = conn.cursor()
        for i, stmt in enumerate(statements, 1):
            # Skip if only whitespace or comments remain
            if not stmt.strip():
                continue
            print(f"  Executing statement {i}...")
            try:
                cur.execute(stmt)
                print(f"  ✓ Statement {i} completed")
            except Exception as e:
                print(f"  ✗ Statement {i} failed: {e}")
                print(f"    SQL: {stmt[:100]}...")
                raise
        cur.close()
        print(f"✓ Successfully executed {file_path}")
    finally:
        conn.close()


def verify_table_exists(schema, table):
    """Verify a table exists in Redshift."""
    conn = get_connection(read_only=False)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
        """, (schema, table))
        result = cur.fetchone()
        cur.close()
        return result[0] > 0
    finally:
        conn.close()


def get_table_rows(schema, table):
    """Get all rows from a table."""
    conn = get_connection(read_only=False)
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {schema}.{table}")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        return columns, rows
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python apply_migration.py <sql_file>")
        sys.exit(1)

    sql_file = sys.argv[1]
    print(f"Applying migration: {sql_file}")
    execute_sql_file(sql_file)
