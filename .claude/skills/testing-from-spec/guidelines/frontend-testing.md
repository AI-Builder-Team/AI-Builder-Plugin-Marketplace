# Frontend Testing Patterns (Vitest + React Testing Library)

## File Structure

Test files live next to implementation files:
```
src/
  components/
    Widget.tsx
    Widget.test.tsx
  utils/
    calculations.ts
    calculations.test.ts
```

## Basic Test Template

```typescript
import { describe, it, expect, vi } from 'vitest'

describe('ModuleName', () => {
  describe('functionName', () => {
    it('should handle normal case', () => {
      const result = functionName(input)
      expect(result).toBe(expected)
    })

    it('should handle edge case', () => {
      const result = functionName(edgeInput)
      expect(result).toBe(edgeExpected)
    })
  })
})
```

## Testing Pure Functions

**Example**: Testing a calculation utility

```typescript
// utils/calculations.ts
export function calculateDiscount(price: number, discountRate: number): number {
  if (discountRate < 0 || discountRate > 1) {
    throw new Error('Discount rate must be between 0 and 1')
  }
  return price * (1 - discountRate)
}
```

```typescript
// utils/calculations.test.ts
import { describe, it, expect } from 'vitest'
import { calculateDiscount } from './calculations'

describe('calculations', () => {
  describe('calculateDiscount', () => {
    it('should calculate discount correctly', () => {
      expect(calculateDiscount(100, 0.2)).toBe(80)
      expect(calculateDiscount(50, 0.5)).toBe(25)
    })

    it('should handle zero discount', () => {
      expect(calculateDiscount(100, 0)).toBe(100)
    })

    it('should throw error for invalid discount rate', () => {
      expect(() => calculateDiscount(100, -0.1)).toThrow('Discount rate must be between 0 and 1')
      expect(() => calculateDiscount(100, 1.5)).toThrow('Discount rate must be between 0 and 1')
    })
  })
})
```

## Testing React Components (Simple)

**Example**: Testing a presentational component

```typescript
// components/StatusBadge.tsx
interface StatusBadgeProps {
  status: 'active' | 'inactive'
  label?: string
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const color = status === 'active' ? 'text-green-600' : 'text-red-600'
  return <span className={color}>{label || status}</span>
}
```

```typescript
// components/StatusBadge.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatusBadge } from './StatusBadge'

describe('StatusBadge', () => {
  it('should render active status with green color', () => {
    render(<StatusBadge status="active" />)
    const badge = screen.getByText('active')
    expect(badge).toHaveClass('text-green-600')
  })

  it('should render inactive status with red color', () => {
    render(<StatusBadge status="inactive" />)
    const badge = screen.getByText('inactive')
    expect(badge).toHaveClass('text-red-600')
  })

  it('should use custom label when provided', () => {
    render(<StatusBadge status="active" label="Running" />)
    expect(screen.getByText('Running')).toBeInTheDocument()
  })
})
```

## Testing with Mocks

**Example**: Testing a function that uses localStorage

```typescript
// utils/storage.ts
export function getUserPreferences(): UserPreferences {
  const stored = localStorage.getItem('userPreferences')
  return stored ? JSON.parse(stored) : { theme: 'light', language: 'en' }
}

export function saveUserPreferences(prefs: UserPreferences): void {
  localStorage.setItem('userPreferences', JSON.stringify(prefs))
}
```

```typescript
// utils/storage.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { getUserPreferences, saveUserPreferences } from './storage'

describe('storage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('getUserPreferences', () => {
    it('should return stored preferences', () => {
      const prefs = { theme: 'dark', language: 'es' }
      localStorage.setItem('userPreferences', JSON.stringify(prefs))

      expect(getUserPreferences()).toEqual(prefs)
    })

    it('should return default preferences when none stored', () => {
      expect(getUserPreferences()).toEqual({ theme: 'light', language: 'en' })
    })
  })

  describe('saveUserPreferences', () => {
    it('should save preferences to localStorage', () => {
      const prefs = { theme: 'dark', language: 'fr' }
      saveUserPreferences(prefs)

      const stored = localStorage.getItem('userPreferences')
      expect(JSON.parse(stored!)).toEqual(prefs)
    })
  })
})
```

## Testing Data Transformations

**Example**: Testing a data formatter

```typescript
// utils/formatters.ts
export interface RawData {
  id: number
  name: string
  created_at: string
}

export interface FormattedData {
  id: number
  name: string
  createdDate: Date
}

export function formatApiResponse(raw: RawData[]): FormattedData[] {
  return raw.map(item => ({
    id: item.id,
    name: item.name,
    createdDate: new Date(item.created_at)
  }))
}
```

```typescript
// utils/formatters.test.ts
import { describe, it, expect } from 'vitest'
import { formatApiResponse } from './formatters'

describe('formatters', () => {
  describe('formatApiResponse', () => {
    it('should transform raw data to formatted data', () => {
      const raw = [
        { id: 1, name: 'Item 1', created_at: '2024-01-01T00:00:00Z' },
        { id: 2, name: 'Item 2', created_at: '2024-01-02T00:00:00Z' }
      ]

      const result = formatApiResponse(raw)

      expect(result).toHaveLength(2)
      expect(result[0]).toEqual({
        id: 1,
        name: 'Item 1',
        createdDate: new Date('2024-01-01T00:00:00Z')
      })
    })

    it('should handle empty array', () => {
      expect(formatApiResponse([])).toEqual([])
    })
  })
})
```

## Minimizing Test Count

**Combine related scenarios in one test**:

```typescript
// ❌ Too many tests
it('should return true for valid email', () => {
  expect(isValidEmail('test@example.com')).toBe(true)
})

it('should return false for email without @', () => {
  expect(isValidEmail('testexample.com')).toBe(false)
})

it('should return false for email without domain', () => {
  expect(isValidEmail('test@')).toBe(false)
})

// ✅ Better: Combine into one test with multiple assertions
it('should validate email addresses correctly', () => {
  expect(isValidEmail('test@example.com')).toBe(true)
  expect(isValidEmail('user@domain.co.uk')).toBe(true)

  expect(isValidEmail('testexample.com')).toBe(false)
  expect(isValidEmail('test@')).toBe(false)
  expect(isValidEmail('@domain.com')).toBe(false)
})
```

## Running Tests

```bash
# From klair-client directory
cd klair-client

# Run specific test file
pnpm vitest run src/utils/calculations.test.ts

# Run all tests
pnpm test

# Run with coverage
pnpm test -- --coverage
```

## Key Principles

1. **Test behavior, not implementation**: Focus on inputs and outputs
2. **One logical concept per test**: But multiple assertions are OK
3. **Descriptive test names**: Use "should" format
4. **Arrange-Act-Assert**: Clear structure
5. **Avoid testing React internals**: Test from user perspective
6. **Mock external dependencies only**: Don't mock what you're testing
