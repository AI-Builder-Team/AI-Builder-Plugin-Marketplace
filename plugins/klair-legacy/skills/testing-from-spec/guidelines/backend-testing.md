# Backend Testing Patterns (pytest)

## File Structure

Test files live in `tests/` directory with `test_` prefix:
```
klair-api/
  services/
    calculator.py
  routers/
    budget.py
  tests/
    test_calculator.py
    test_budget_router.py
```

## Basic Test Template

```python
import pytest
from services.calculator import calculate_metrics


def test_calculate_metrics_with_valid_data():
    """Test that calculate_metrics returns correct result for valid input."""
    result = calculate_metrics([1, 2, 3, 4, 5])
    assert result == 15


def test_calculate_metrics_with_empty_list():
    """Test that calculate_metrics handles empty list."""
    result = calculate_metrics([])
    assert result == 0
```

## Testing Pure Functions

**Example**: Testing a business logic function

```python
# services/discount.py
def calculate_discount(price: float, discount_rate: float) -> float:
    """Calculate discounted price."""
    if not 0 <= discount_rate <= 1:
        raise ValueError("Discount rate must be between 0 and 1")
    return price * (1 - discount_rate)
```

```python
# tests/test_discount.py
import pytest
from services.discount import calculate_discount


def test_calculate_discount_valid_inputs():
    """Test discount calculation with valid inputs."""
    assert calculate_discount(100, 0.2) == 80
    assert calculate_discount(50, 0.5) == 25
    assert calculate_discount(100, 0) == 100


def test_calculate_discount_invalid_rate_raises_error():
    """Test that invalid discount rate raises ValueError."""
    with pytest.raises(ValueError, match="Discount rate must be between 0 and 1"):
        calculate_discount(100, -0.1)

    with pytest.raises(ValueError, match="Discount rate must be between 0 and 1"):
        calculate_discount(100, 1.5)
```

## Testing Data Transformations

**Example**: Testing a data transformer

```python
# services/transformers.py
from typing import List, Dict
from datetime import datetime


def transform_api_response(raw_data: List[Dict]) -> List[Dict]:
    """Transform raw API response to internal format."""
    return [
        {
            "id": item["id"],
            "name": item["name"],
            "created_date": datetime.fromisoformat(item["created_at"]),
            "is_active": item.get("status") == "active"
        }
        for item in raw_data
    ]
```

```python
# tests/test_transformers.py
from datetime import datetime
from services.transformers import transform_api_response


def test_transform_api_response_valid_data():
    """Test transformation of valid API response."""
    raw = [
        {"id": 1, "name": "Item 1", "created_at": "2024-01-01T00:00:00", "status": "active"},
        {"id": 2, "name": "Item 2", "created_at": "2024-01-02T00:00:00", "status": "inactive"}
    ]

    result = transform_api_response(raw)

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["name"] == "Item 1"
    assert result[0]["created_date"] == datetime(2024, 1, 1)
    assert result[0]["is_active"] is True
    assert result[1]["is_active"] is False


def test_transform_api_response_empty_list():
    """Test transformation of empty list."""
    assert transform_api_response([]) == []


def test_transform_api_response_missing_status():
    """Test transformation when status field is missing."""
    raw = [{"id": 1, "name": "Item 1", "created_at": "2024-01-01T00:00:00"}]
    result = transform_api_response(raw)
    assert result[0]["is_active"] is False
```

## Testing with Mocks

**Example**: Testing a function that depends on external service

```python
# services/data_fetcher.py
def process_user_data(user_id: int, api_client) -> dict:
    """Fetch and process user data."""
    raw_data = api_client.get_user(user_id)
    return {
        "user_id": raw_data["id"],
        "full_name": f"{raw_data['first_name']} {raw_data['last_name']}",
        "email_domain": raw_data["email"].split("@")[1]
    }
```

```python
# tests/test_data_fetcher.py
from unittest.mock import Mock
import pytest
from services.data_fetcher import process_user_data


def test_process_user_data_success():
    """Test processing of user data with mocked API client."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 123,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }

    result = process_user_data(123, mock_client)

    assert result["user_id"] == 123
    assert result["full_name"] == "John Doe"
    assert result["email_domain"] == "example.com"
    mock_client.get_user.assert_called_once_with(123)
```

## Testing with Fixtures

**Example**: Using pytest fixtures for setup

```python
# tests/conftest.py
import pytest


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
        {"id": 3, "value": 30}
    ]


@pytest.fixture
def mock_database():
    """Provide mock database connection."""
    db = Mock()
    db.query.return_value = [{"id": 1, "name": "Test"}]
    return db
```

```python
# tests/test_processor.py
def test_calculate_total(sample_data):
    """Test total calculation using fixture."""
    from services.processor import calculate_total
    result = calculate_total(sample_data)
    assert result == 60


def test_fetch_data(mock_database):
    """Test data fetching with mock database."""
    from services.processor import fetch_data
    result = fetch_data(mock_database)
    assert len(result) == 1
    assert result[0]["name"] == "Test"
```

## Testing Exception Handling

**Example**: Testing error cases

```python
# services/validator.py
def validate_age(age: int) -> bool:
    """Validate age is within acceptable range."""
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age cannot exceed 150")
    return True
```

```python
# tests/test_validator.py
import pytest
from services.validator import validate_age


def test_validate_age_valid():
    """Test age validation with valid inputs."""
    assert validate_age(25) is True
    assert validate_age(0) is True
    assert validate_age(150) is True


def test_validate_age_negative_raises_error():
    """Test that negative age raises ValueError."""
    with pytest.raises(ValueError, match="Age cannot be negative"):
        validate_age(-1)


def test_validate_age_too_high_raises_error():
    """Test that age over 150 raises ValueError."""
    with pytest.raises(ValueError, match="Age cannot exceed 150"):
        validate_age(151)
```

## Parametrized Tests

**Example**: Testing multiple scenarios efficiently

```python
# services/calculator.py
def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
```

```python
# tests/test_calculator.py
import pytest
from services.calculator import is_prime


@pytest.mark.parametrize("number,expected", [
    (2, True),
    (3, True),
    (5, True),
    (7, True),
    (11, True),
    (4, False),
    (6, False),
    (8, False),
    (9, False),
    (0, False),
    (1, False),
    (-5, False)
])
def test_is_prime(number, expected):
    """Test prime number detection with various inputs."""
    assert is_prime(number) == expected
```

## Minimizing Test Count

**Combine related assertions**:

```python
# ❌ Too many tests
def test_format_currency_with_integer():
    assert format_currency(100) == "$100.00"

def test_format_currency_with_decimal():
    assert format_currency(100.5) == "$100.50"

def test_format_currency_with_zero():
    assert format_currency(0) == "$0.00"

# ✅ Better: Combine into one test
def test_format_currency_various_inputs():
    """Test currency formatting with various numeric inputs."""
    assert format_currency(100) == "$100.00"
    assert format_currency(100.5) == "$100.50"
    assert format_currency(0) == "$0.00"
    assert format_currency(999.99) == "$999.99"
```

## Running Tests

```bash
# From klair-api directory
cd klair-api

# Run specific test file
pytest tests/test_calculator.py

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=services tests/
```

## Key Principles

1. **Test behavior, not implementation**: Focus on inputs and outputs
2. **Use descriptive names**: Function name + scenario
3. **One logical concept per test**: But multiple assertions are OK
4. **Use fixtures for setup**: Avoid repetition
5. **Mock external dependencies**: Database, API clients, file systems
6. **Test edge cases**: Empty inputs, nulls, boundary values
7. **Use parametrize for similar tests**: DRY principle
8. **Follow FastAPI exception pattern**: Let exceptions bubble up to routers

## Common Patterns

### Testing Pydantic Models

```python
from pydantic import BaseModel, ValidationError
import pytest


class User(BaseModel):
    name: str
    age: int


def test_user_model_valid():
    """Test User model with valid data."""
    user = User(name="John", age=30)
    assert user.name == "John"
    assert user.age == 30


def test_user_model_invalid_age():
    """Test User model validation for invalid age type."""
    with pytest.raises(ValidationError):
        User(name="John", age="thirty")
```

### Testing Async Functions

```python
import pytest


@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    from services.async_service import fetch_data_async
    result = await fetch_data_async()
    assert result is not None
```
