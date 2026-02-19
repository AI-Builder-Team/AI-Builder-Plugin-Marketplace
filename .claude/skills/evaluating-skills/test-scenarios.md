# Evaluation Test Scenarios

This document contains test scenarios for validating the `evaluating-skills` skill. Each scenario includes a sample skill to evaluate and expected findings.

## Scenario 1: Poorly Written Skill (Should score 2/5)

### Sample Skill: "code-helper"
```markdown
---
name: Helping with code
description: This skill helps you with coding tasks and stuff
---

# Code Helper

This skill will help you write better code. It's useful for many things.

## How to Use

1. Look at the code
2. Try to fix it
3. Make it better
4. Test if needed

You can use Python or JavaScript or whatever language you want. Just do your best to improve things.
```

### Expected Findings:
- **Metadata Issues**: Name not in gerund form, vague description
- **Structure Issues**: No clear workflow, missing specifics
- **Instruction Quality**: Ambiguous steps, no actionable guidance
- **Token Efficiency**: Vague content provides little value
- **Missing Elements**: No examples, no checklists, no decision criteria

### Expected Score: 2/5
- Metadata Quality: 2/5 (name format wrong, vague description)
- Structure & Organization: 2/5 (minimal structure)
- Instruction Clarity: 1/5 (extremely vague)
- Token Efficiency: 3/5 (short but unhelpful)
- Overall: 2/5

---

## Scenario 2: Mediocre Skill (Should score 3/5)

### Sample Skill: "reviewing-pull-requests"
```markdown
---
name: Reviewing pull requests
description: Reviews pull requests for code quality, style, and best practices
---

# Pull Request Review Skill

This skill helps you review pull requests systematically.

## Steps

1. Read the PR description and understand the purpose
2. Review the changed files
3. Check for code quality issues:
   - Are there any syntax errors?
   - Is the code readable?
   - Are there tests?
   - Is documentation updated?
4. Look for security issues
5. Check performance implications
6. Provide feedback with specific line references
7. Approve or request changes

## Checklist
- [ ] Code builds successfully
- [ ] Tests pass
- [ ] No security vulnerabilities
- [ ] Documentation updated
- [ ] Code follows project conventions

## Example Feedback Format

```
## Review Feedback

### Strengths
- [What was done well]

### Issues
- [file.py:123] Issue description
- [file.py:456] Another issue

### Suggestions
- [Optional improvements]
```
```

### Expected Findings:
- **Strengths**: Good structure, includes checklist, has example
- **Issues**:
  - No guidance on how to check for security issues or performance implications
  - Missing tool usage instructions (should it use Grep, Read, etc.?)
  - Example is generic, could be more specific
  - No guidance on prioritizing issues
  - Doesn't specify when to approve vs request changes
- **Token Efficiency**: Reasonable, but some redundancy

### Expected Score: 3/5
- Metadata Quality: 4/5 (good name and description)
- Structure & Organization: 4/5 (clear sections)
- Instruction Clarity: 3/5 (steps are clear but lack depth)
- Token Efficiency: 3/5 (could be more concise)
- Examples: 3/5 (template provided but generic)
- Overall: 3/5

---

## Scenario 3: Well-Written Skill (Should score 4-5/5)

### Sample Skill: "creating-api-tests"
```markdown
---
name: Creating API integration tests
description: Creates comprehensive integration tests for REST API endpoints using pytest and FastAPI TestClient. Use when adding new API endpoints or improving test coverage for existing endpoints.
allowed-tools: [Read, Write, Grep, Bash]
---

# API Integration Test Creation

Creates pytest-based integration tests for FastAPI endpoints following project patterns.

## When to Use
- New API endpoint requires tests
- Existing endpoint lacks coverage
- Refactoring requires test validation

## Workflow

### 1. Analyze the Endpoint
- Read the router file containing the endpoint
- Identify HTTP method, path, request schema, response schema
- Note authentication requirements and dependencies

### 2. Locate Test Patterns
Search existing tests for similar endpoints:
```bash
grep -r "test_.*endpoint" tests/
```

### 3. Create Test File
Follow naming convention: `test_{router_name}.py`

Location: `tests/integration/test_{feature}_api.py`

### 4. Write Test Structure

Include test cases for:
- ✓ Successful request (200/201)
- ✓ Invalid input (422 validation error)
- ✓ Unauthorized access (401 if protected)
- ✓ Not found (404 for GET by ID)
- ✓ Edge cases specific to endpoint

### 5. Verify Coverage
```bash
pytest tests/integration/test_{feature}_api.py -v
pytest --cov=app.routers.{feature} --cov-report=term-missing
```

## Test Template

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_{endpoint}_success():
    \"\"\"Test successful {operation}.\"\"\"
    response = client.{method}("/api/{path}", json={...})
    assert response.status_code == 200
    data = response.json()
    assert data["field"] == expected_value

def test_{endpoint}_validation_error():
    \"\"\"Test validation error with invalid input.\"\"\"
    response = client.{method}("/api/{path}", json={...})
    assert response.status_code == 422

def test_{endpoint}_unauthorized():
    \"\"\"Test unauthorized access without token.\"\"\"
    response = client.{method}("/api/{path}")
    assert response.status_code == 401
```

## Validation

- [ ] All test cases pass
- [ ] Coverage >80% for endpoint
- [ ] Test names clearly describe scenarios
- [ ] Assertions validate response structure and values
- [ ] Authentication mocked appropriately
```

### Expected Findings:
- **Strengths**:
  - Excellent metadata with clear triggers
  - Structured workflow with numbered steps
  - Concrete test template with placeholders
  - Clear validation checklist
  - Specifies allowed tools
  - Includes bash commands for verification
  - Follows naming conventions
- **Minor Issues**:
  - Could include example of mocking authentication
  - Template could show parametrized tests for multiple cases

### Expected Score: 4-5/5
- Metadata Quality: 5/5 (perfect)
- Structure & Organization: 5/5 (clear workflow)
- Instruction Clarity: 5/5 (actionable steps)
- Token Efficiency: 4/5 (very good, minor room for optimization)
- Examples: 4/5 (good template, could add auth mocking)
- Overall: 4.5/5

---

## Baseline Performance Expectations

### Without Skill (Baseline)
Claude should still be able to evaluate skills, but may:
- Miss structural issues
- Inconsistently apply criteria
- Provide generic feedback
- Skip token efficiency analysis
- Not follow systematic workflow

### With Skill (Expected Improvement)
- Systematic evaluation following 12 steps
- Consistent scoring methodology
- Specific, actionable recommendations
- Token efficiency analysis included
- Structured report format
- Coverage of all quality dimensions

## Success Metrics

A successful evaluation using this skill should:
1. Complete all 12 steps or explicitly note which are N/A
2. Provide scores with justification
3. Identify at least 3 specific issues or strengths
4. Include token count estimation
5. Provide prioritized recommendations
6. Follow the report template format
