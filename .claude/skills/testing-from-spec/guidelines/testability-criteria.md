# What Makes Code Unit Testable

## ✅ Highly Testable (Priority 1)

### Pure Functions
- Input → Output, no side effects
- Deterministic results
- No external dependencies

**Examples**:
```typescript
// Frontend
export function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0)
}

// Backend
def calculate_discount(price: float, discount_rate: float) -> float:
    return price * (1 - discount_rate)
```

### Business Logic
- Core domain rules
- Validation functions
- Computation logic

**Examples**:
```typescript
export function isEligibleForDiscount(user: User): boolean {
  return user.accountAge > 30 && user.totalSpent > 1000
}
```

```python
def is_renewal_due(subscription: Subscription) -> bool:
    return subscription.end_date <= date.today() + timedelta(days=30)
```

### Data Transformations
- Mapping, filtering, reducing
- Formatting functions
- Parsers and serializers

**Examples**:
```typescript
export function formatCurrency(amount: number): string {
  return `$${amount.toFixed(2)}`
}
```

```python
def transform_api_response(raw_data: dict) -> List[Report]:
    return [Report(**item) for item in raw_data.get('results', [])]
```

## ⚠️ Testable with Mocking (Priority 2)

### Functions with External Dependencies
- Can be tested if dependencies are mockable
- Should be refactored if mocking is complex

**Examples**:
```typescript
// Can test by mocking localStorage
export function getUserPreferences(): Preferences {
  const stored = localStorage.getItem('prefs')
  return stored ? JSON.parse(stored) : DEFAULT_PREFS
}
```

```python
# Can test by mocking database client
def get_user_metrics(user_id: int, db_client) -> Metrics:
    result = db_client.query("SELECT * FROM metrics WHERE user_id = ?", user_id)
    return Metrics.from_db(result)
```

### React Components with Props Only
- Presentational components
- No hooks, no context, no side effects

**Example**:
```typescript
export function StatusBadge({ status }: { status: string }) {
  const color = status === 'active' ? 'green' : 'red'
  return <span className={color}>{status}</span>
}
```

## ❌ Not Unit Testable (Skip)

### External Service Calls
- API calls (fetch, axios)
- Database queries
- File system operations
- Network operations

**Rationale**: These are integration tests, not unit tests

**Examples**:
```typescript
// Skip - this is an integration test
async function fetchUserData(userId: string) {
  const response = await fetch(`/api/users/${userId}`)
  return response.json()
}
```

```python
# Skip - this is a database integration test
def save_to_database(data: dict):
    connection = psycopg2.connect(DB_URL)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO ...", data)
    connection.commit()
```

### Orchestration Functions
- Pure glue code calling other functions
- No logic of their own

**Example**:
```typescript
// Skip - just orchestration
async function processOrder(orderId: string) {
  const order = await fetchOrder(orderId)
  const validated = validateOrder(order)
  const result = await saveOrder(validated)
  return result
}
```

### Stateful Components with Complex Lifecycle
- Components with multiple useEffect hooks
- Components with complex state management
- Components heavily dependent on context

**Rationale**: These are better tested as integration tests

## Refactoring Opportunities

If you encounter code that's hard to test, suggest refactoring:

### Extract Pure Logic
**Before** (hard to test):
```typescript
function processData(data: any[]) {
  const result = fetch('/api/process', { method: 'POST', body: JSON.stringify(data) })
  return result.json()
}
```

**After** (testable):
```typescript
// Testable: pure function
export function preparePayload(data: any[]): string {
  return JSON.stringify(data)
}

// Skip testing: I/O operation
async function processData(data: any[]) {
  const payload = preparePayload(data)
  const result = await fetch('/api/process', { method: 'POST', body: payload })
  return result.json()
}
```

### Dependency Injection
**Before** (hard to test):
```python
def calculate_metrics():
    db = get_database_connection()  # Hard-coded dependency
    data = db.query("SELECT ...")
    return sum(data)
```

**After** (testable):
```python
def calculate_metrics(data: List[float]) -> float:
    return sum(data)

def fetch_and_calculate():
    db = get_database_connection()
    data = db.query("SELECT ...")
    return calculate_metrics(data)  # Testable separately
```

## Quick Decision Tree

```
Is it a pure function?
  → YES: Test it (Priority 1)

Does it have business logic?
  → YES: Test it (Priority 1)

Does it transform data without I/O?
  → YES: Test it (Priority 1)

Does it make API/DB calls?
  → YES: Skip (or suggest refactoring to extract logic)

Is it just orchestration?
  → YES: Skip

Can it be easily mocked?
  → YES: Test it (Priority 2)
  → NO: Suggest refactoring, then test
```
