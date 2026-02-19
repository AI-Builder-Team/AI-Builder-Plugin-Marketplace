"""Unit tests for format_value() function used across exploration utilities."""

import sys
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

# Add the utils directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "exploring-redshift-tables" / "utils"))

from get_table_schema import format_value


class TestFormatValue:
    """Tests for format_value() function."""

    def test_none_value(self):
        """Test that None is formatted as 'NULL'."""
        assert format_value(None) == "NULL"

    def test_string_values(self):
        """Test that strings are wrapped in double quotes."""
        assert format_value("hello") == '"hello"'
        assert format_value("test value") == '"test value"'
        assert format_value("") == '""'
        assert format_value("with 'quotes'") == '"with \'quotes\'"'

    def test_integer_values(self):
        """Test that integers are converted to strings."""
        assert format_value(0) == "0"
        assert format_value(42) == "42"
        assert format_value(-100) == "-100"
        assert format_value(999999) == "999999"

    def test_float_values(self):
        """Test that floats are converted to strings."""
        assert format_value(3.14) == "3.14"
        assert format_value(0.0) == "0.0"
        assert format_value(-2.5) == "-2.5"
        assert format_value(1e10) == "10000000000.0"

    def test_boolean_values(self):
        """Test that booleans are converted to strings."""
        assert format_value(True) == "True"
        assert format_value(False) == "False"

    def test_decimal_values(self):
        """Test that Decimal values are converted to strings."""
        assert format_value(Decimal("123.45")) == "123.45"
        assert format_value(Decimal("0.00")) == "0.00"
        assert format_value(Decimal("-99.99")) == "-99.99"

    def test_datetime_values(self):
        """Test that datetime objects are converted to strings."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = format_value(dt)
        assert "2024" in result
        assert isinstance(result, str)

    def test_date_values(self):
        """Test that date objects are converted to strings."""
        d = date(2024, 1, 15)
        result = format_value(d)
        assert "2024" in result
        assert isinstance(result, str)

    def test_list_values(self):
        """Test that lists are converted to strings."""
        assert format_value([1, 2, 3]) == "[1, 2, 3]"
        assert format_value([]) == "[]"
        assert format_value(["a", "b"]) == "['a', 'b']"

    def test_dict_values(self):
        """Test that dicts are converted to strings."""
        result = format_value({"key": "value"})
        assert isinstance(result, str)
        assert "key" in result

    def test_bytes_values(self):
        """Test that bytes are converted to strings."""
        result = format_value(b"hello")
        assert isinstance(result, str)

    def test_special_string_values(self):
        """Test strings with special characters."""
        assert format_value("line1\nline2") == '"line1\nline2"'
        assert format_value("tab\there") == '"tab\there"'
        assert format_value("quote\"here") == '"quote"here"'
        assert format_value("back\\slash") == '"back\\slash"'

    def test_empty_and_whitespace_strings(self):
        """Test empty and whitespace-only strings."""
        assert format_value("") == '""'
        assert format_value(" ") == '" "'
        assert format_value("   ") == '"   "'
        assert format_value("\t") == '"\t"'

    def test_numeric_strings(self):
        """Test strings that contain numbers."""
        assert format_value("123") == '"123"'
        assert format_value("3.14") == '"3.14"'
        assert format_value("1e10") == '"1e10"'
