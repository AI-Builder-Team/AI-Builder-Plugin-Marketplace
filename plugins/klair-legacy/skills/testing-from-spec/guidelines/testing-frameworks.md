# Testing Frameworks by Domain

## klair-client (Frontend)

**Framework**: Vitest + React Testing Library

**Test file location**: Next to implementation file
- `src/components/Widget.tsx` → `src/components/Widget.test.tsx`
- `src/utils/calc.ts` → `src/utils/calc.test.ts`

**Run tests**:
```bash
cd klair-client
pnpm vitest run <relative-path-to-test-file>  # Single file
pnpm test                                       # Full suite
```

**Configuration**: `vitest.config.ts`

**Key imports**:
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
```

## klair-api (Backend)

**Framework**: pytest

**Test file location**: `tests/` directory with `test_` prefix
- `services/calculator.py` → `tests/test_calculator.py`
- `routers/budget.py` → `tests/test_budget_router.py`

**Run tests**:
```bash
cd klair-api
pytest tests/test_<module>.py  # Single file
pytest                         # Full suite
```

**Configuration**: `pyproject.toml` (pytest section)

**Key imports**:
```python
import pytest
from unittest.mock import Mock, patch
```

## klair-udm (or other domains)

**Detection**: Check for:
- `package.json` with test scripts → likely Jest or Vitest
- `pytest.ini`, `pyproject.toml` → pytest
- `jest.config.js` → Jest

**Fallback**: Ask user which framework to use
