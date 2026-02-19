"""Unit tests for db_connector.py utility functions."""

import sys
import pytest
from pathlib import Path

# Add the utils directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "exploring-redshift-tables" / "utils"))

from db_connector import sanitize_identifier, get_output_file_path, get_repo_root


class TestSanitizeIdentifier:
    """Tests for sanitize_identifier() function."""

    def test_valid_alphanumeric(self):
        """Test valid alphanumeric identifiers."""
        assert sanitize_identifier("table123", "table") == "table123"
        assert sanitize_identifier("Schema_Name", "schema") == "Schema_Name"
        assert sanitize_identifier("column_1", "column") == "column_1"

    def test_valid_with_hyphens(self):
        """Test valid identifiers with hyphens."""
        assert sanitize_identifier("my-table", "table") == "my-table"
        assert sanitize_identifier("user-events-2024", "table") == "user-events-2024"
        assert sanitize_identifier("financial-data", "schema") == "financial-data"

    def test_valid_with_underscores(self):
        """Test valid identifiers with underscores."""
        assert sanitize_identifier("_private_table", "table") == "_private_table"
        assert sanitize_identifier("my_table_name", "table") == "my_table_name"
        assert sanitize_identifier("user_events_2024", "table") == "user_events_2024"

    def test_mixed_valid_characters(self):
        """Test identifiers with mixed valid characters."""
        assert sanitize_identifier("my_table-2024", "table") == "my_table-2024"
        assert sanitize_identifier("User_Events-Archive", "table") == "User_Events-Archive"

    def test_empty_string(self):
        """Test that empty string raises SystemExit."""
        with pytest.raises(SystemExit) as exc_info:
            sanitize_identifier("", "table")
        assert exc_info.value.code == 1

    def test_starts_with_digit(self):
        """Test that starting with digit raises SystemExit."""
        with pytest.raises(SystemExit) as exc_info:
            sanitize_identifier("123table", "table")
        assert exc_info.value.code == 1

    def test_starts_with_hyphen(self):
        """Test that starting with hyphen raises SystemExit."""
        with pytest.raises(SystemExit) as exc_info:
            sanitize_identifier("-table", "table")
        assert exc_info.value.code == 1

    def test_special_characters(self):
        """Test that special characters raise SystemExit."""
        invalid_chars = ["table@name", "table$name", "table!name", "table#name",
                        "table%name", "table&name", "table*name", "table(name",
                        "table)name", "table+name", "table=name", "table[name",
                        "table]name", "table{name", "table}name", "table|name",
                        "table\\name", "table:name", "table;name", "table'name",
                        'table"name', "table<name", "table>name", "table,name",
                        "table.name", "table?name", "table/name", "table name"]

        for invalid in invalid_chars:
            with pytest.raises(SystemExit) as exc_info:
                sanitize_identifier(invalid, "table")
            assert exc_info.value.code == 1

    def test_sql_injection_attempts(self):
        """Test that SQL injection patterns are rejected."""
        injection_attempts = [
            "table'; DROP TABLE users;--",
            "table' OR '1'='1",
            "table;",
            "../../etc/passwd",
            "../table",
            "table/../other"
        ]

        for attempt in injection_attempts:
            with pytest.raises(SystemExit) as exc_info:
                sanitize_identifier(attempt, "table")
            assert exc_info.value.code == 1

    def test_valid_double_hyphens(self):
        """Test that double hyphens are allowed (valid in identifiers)."""
        # Note: "--" is valid in quoted identifiers, and SQL comments require space
        assert sanitize_identifier("table--name", "table") == "table--name"


class TestGetOutputFilePath:
    """Tests for get_output_file_path() function."""

    def test_valid_schema_and_table(self):
        """Test valid schema and table names produce correct path."""
        path = get_output_file_path("public", "users")
        repo_root = get_repo_root()

        assert path == repo_root / "public_users_exploration.md"
        assert path.name == "public_users_exploration.md"

    def test_path_within_repo_root(self):
        """Test that output path is within repo root."""
        path = get_output_file_path("schema", "table")
        repo_root = get_repo_root()

        resolved_path = path.resolve()
        resolved_root = repo_root.resolve()

        assert str(resolved_path).startswith(str(resolved_root))

    def test_path_traversal_rejected(self):
        """Test that path traversal attempts are rejected by sanitize_identifier."""
        # These should fail in sanitize_identifier before reaching path construction
        with pytest.raises(SystemExit):
            get_output_file_path("../etc", "passwd")

        with pytest.raises(SystemExit):
            get_output_file_path("../../root", "secrets")

        with pytest.raises(SystemExit):
            get_output_file_path(".", ".")

    def test_special_chars_in_names_rejected(self):
        """Test that special characters are rejected."""
        with pytest.raises(SystemExit):
            get_output_file_path("schema/test", "table")

        with pytest.raises(SystemExit):
            get_output_file_path("schema", "table\\test")

    def test_hyphenated_names(self):
        """Test that hyphenated names work correctly."""
        path = get_output_file_path("my-schema", "my-table")
        repo_root = get_repo_root()

        assert path == repo_root / "my-schema_my-table_exploration.md"
        assert str(path).startswith(str(repo_root))


class TestGetRepoRoot:
    """Tests for get_repo_root() function."""

    def test_finds_repo_root(self):
        """Test that get_repo_root finds a directory with .git."""
        root = get_repo_root()
        assert root.exists()
        # Either .git exists or we're at cwd
        assert (root / ".git").exists() or root == Path.cwd()

    def test_returns_path_object(self):
        """Test that return value is a Path object."""
        root = get_repo_root()
        assert isinstance(root, Path)
