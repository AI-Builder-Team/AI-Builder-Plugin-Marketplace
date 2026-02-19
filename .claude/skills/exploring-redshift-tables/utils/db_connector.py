"""Shared Redshift connection utility using AWS Secrets Manager."""

import json
import sys
from pathlib import Path
import boto3
import redshift_connector

SECRET_NAME = "klair/redshift-creds"


def sanitize_identifier(identifier, identifier_type="identifier"):
    """
    Sanitize SQL identifiers and file path components to prevent injection attacks.

    Only allows alphanumeric characters, underscores, and hyphens.
    Rejects empty strings, leading digits, and special characters.

    Args:
        identifier: The identifier to sanitize (schema, table, or column name)
        identifier_type: Type of identifier for error messages (e.g., "schema", "table", "column")

    Returns:
        The validated identifier if safe

    Raises:
        SystemExit: If identifier contains unsafe characters
    """
    if not identifier:
        print(f"✗ {identifier_type.capitalize()} name cannot be empty")
        sys.exit(1)

    # Allow only alphanumeric, underscore, and hyphen
    # Must start with letter or underscore (not digit or hyphen)
    if not identifier[0].isalpha() and identifier[0] != '_':
        print(f"✗ {identifier_type.capitalize()} '{identifier}' must start with a letter or underscore")
        sys.exit(1)

    for char in identifier:
        if not (char.isalnum() or char in ('_', '-')):
            print(f"✗ {identifier_type.capitalize()} '{identifier}' contains invalid character '{char}'")
            print(f"  Only alphanumeric characters, underscores, and hyphens are allowed")
            sys.exit(1)

    return identifier


def get_repo_root():
    """Find the repository root by looking for .git directory."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    # If no .git found, return current working directory
    return Path.cwd()


def get_output_file_path(schema, table):
    """
    Get the full path for the exploration output file at repo root.

    Sanitizes schema and table names to prevent path traversal attacks.
    """
    # Sanitize inputs to prevent directory traversal
    safe_schema = sanitize_identifier(schema, "schema")
    safe_table = sanitize_identifier(table, "table")

    repo_root = get_repo_root()
    output_path = repo_root / f"{safe_schema}_{safe_table}_exploration.md"

    # Additional safety check: ensure resolved path is within repo root
    try:
        resolved_output = output_path.resolve()
        resolved_root = repo_root.resolve()

        if not str(resolved_output).startswith(str(resolved_root)):
            print(f"✗ Security error: Output path would be outside repository root")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error validating output path: {e}")
        sys.exit(1)

    return output_path


def get_credentials():
    """Fetch Redshift credentials from AWS Secrets Manager."""
    try:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager")
        response = client.get_secret_value(SecretId=SECRET_NAME)
        secret_string = response["SecretString"]
        return json.loads(secret_string)
    except Exception as e:
        print(f"✗ Failed to fetch credentials from AWS Secrets Manager: {e}")
        sys.exit(1)


def get_connection(read_only=True):
    """Establish connection to Redshift using credentials from Secrets Manager.

    Args:
        read_only: If True (default), enforces read-only mode to prevent accidental writes.
                   Set to False for DDL operations (CREATE VIEW, INSERT, etc.).
    """
    creds = get_credentials()

    try:
        conn = redshift_connector.connect(
            host=creds["host"],
            port=int(creds.get("port", 5439)),
            database=creds["database"],
            user=creds["user"],
            password=creds["password"],
        )
        conn.autocommit = True

        if read_only:
            # Enforce read-only mode at database level to prevent accidental writes
            cur = conn.cursor()
            cur.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
            cur.close()

        return conn
    except Exception as e:
        print(f"✗ Failed to connect to Redshift: {e}")
        sys.exit(1)


def execute_query(query, params=None):
    """Execute a query and return results as list of tuples with column names."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        cur.close()
        return columns, rows
    except Exception as e:
        print(f"✗ Error executing query: {e}")
        sys.exit(1)
    finally:
        conn.close()
