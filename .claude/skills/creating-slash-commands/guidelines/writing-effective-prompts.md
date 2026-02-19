# Writing Effective Command Prompts

The quality of your command prompt directly affects the quality of results. This guide covers best practices for writing clear, actionable command prompts.

**Philosophy**: Start with concise prompts and expand them based on real usage. Avoid over-specifying upfront—let your actual needs drive complexity.

## Core Principles

### 1. Be Specific and Concise

**Poor**:
```markdown
Review this code
```

**Good**:
```markdown
Review this code for security vulnerabilities, performance issues, and code style violations.

Provide specific recommendations for each issue found.
```

**Better** (after testing and iterating):
```markdown
Review this code for:
- Security vulnerabilities (SQL injection, XSS, CSRF)
- Performance issues (N+1 queries, memory leaks)
- Code style violations (naming, formatting)
- Missing error handling

Provide specific recommendations with code examples for each issue found.
```

**Why**: Start concise to avoid overwhelming the prompt. Add detail based on real use cases and testing when you need more specific behavior.

### 2. Focus on "Why" and "What", Not Just "How"

**Poor**:
```markdown
Run the linter and fix all errors
```

**Good**:
```markdown
Ensure code quality by:
1. Running the linter
2. Fixing all errors to maintain consistency
3. Documenting any exceptions with justification

Our team prioritizes code readability and maintainability.
```

**Why**: Context helps Claude make better decisions.

### 3. Structure with Clear Sections

**Poor**:
```markdown
Check git status, look at the diff, check recent commits, and create a commit following our conventions
```

**Good**:
```markdown
## Context

Review the current git state to understand what has changed.

## Task

Create a commit following our convention:
- Use conventional commit format (feat/fix/docs/etc)
- Include scope in parentheses
- Keep subject under 50 characters
- Check recent commit history to match our style
```

**Why**: Sections make instructions easier to follow and verify.

## Prompt Patterns

### Pattern 1: Analysis & Recommendations

```markdown
Analyze @$ARGUMENTS and provide:

1. **Purpose** - What does this code do?
2. **Issues** - What problems exist?
3. **Recommendations** - Specific improvements with priority
4. **Examples** - Code snippets showing fixes

Format recommendations as actionable tasks.
```

### Pattern 2: Multi-Step Workflow

```markdown
Complete the following workflow:

1. Verify prerequisites:
   - Check dependencies are installed
   - Ensure environment variables are set

2. Execute main task:
   - Run tests
   - Build project

3. Validation:
   - Verify no errors occurred
   - Check output is correct

Report status at each step.
```

### Pattern 3: Code Generation

```markdown
Create a new React component that:

**Requirements**:
- Uses TypeScript with strict types
- Follows our naming convention (PascalCase)
- Includes PropTypes documentation
- Implements proper error boundaries
- Has unit tests with >80% coverage

**Style**:
- Use functional components with hooks
- Follow our style guide in @docs/style-guide.md
- Use existing utility functions from @utils/

Provide both component and test files.
```

### Pattern 4: Review & Validation

```markdown
Review @$ARGUMENTS for security issues.

**Check for**:
- Input validation (all user inputs sanitized)
- Authentication (proper auth checks)
- Authorization (role-based access control)
- Data exposure (no sensitive data in logs/errors)
- Crypto (secure algorithms, no hardcoded secrets)

**Output format**:
For each issue found:
1. Severity (Critical/High/Medium/Low)
2. Location (file:line)
3. Description
4. Fix recommendation with code example
```

## Best Practices

### Use Bullet Points

✅ **Good**:
```markdown
Check for:
- SQL injection vulnerabilities
- XSS attacks
- CSRF issues
- Insecure dependencies
```

❌ **Poor**:
```markdown
Check for SQL injection vulnerabilities, XSS attacks, CSRF issues, and insecure dependencies.
```

### Include Expected Output Format

✅ **Good**:
```markdown
Provide recommendations in this format:

**Issue**: Brief description
**Location**: file:line
**Fix**: Specific code changes needed
```

❌ **Poor**:
```markdown
Provide recommendations for improvements.
```

### Reference Team Standards

✅ **Good**:
```markdown
Follow our coding standards:
- Use TypeScript with strict mode
- Follow style guide in @docs/style-guide.md
- Include JSDoc comments for public APIs
- Write tests with 80% minimum coverage
```

❌ **Poor**:
```markdown
Write good code with tests.
```

### Provide Context Requirements

✅ **Good**:
```markdown
## Current State

Check the following before determining deployment readiness:
- Git status and any uncommitted changes
- Test results
- Recent changes and commits

## Your Task

Based on the above context, determine if code is ready to deploy.
```

❌ **Poor**:
```markdown
Check if code is ready to deploy.
```

## Common Mistakes

### ❌ Too Vague

```markdown
Make this better
```

**Fix**: Be specific about what "better" means.

### ❌ Too Prescriptive

```markdown
First open the file, then on line 42 change the variable name from foo to bar, then save the file, then run the tests.
```

**Fix**: Describe the goal, let Claude determine the steps.

### ❌ Missing Context

```markdown
Fix the bug
```

**Fix**: Provide context about the bug, expected behavior, current behavior.

### ❌ No Success Criteria

```markdown
Optimize the code
```

**Fix**: Define what success looks like (performance targets, metrics, etc.).

## Examples from Real Commands

### Example 1: Git Commit Command

```markdown
---
description: Create and push a git commit
allowed-tools: Bash(git:*)
---

## Your Task

Create and push a git commit following our conventions:

1. Check current status and what has changed
2. Stage all relevant files
3. Create a conventional commit message based on the changes
4. Commit the changes
5. Push to remote

Follow our commit message conventions by checking recent commit history.
```

**Why this works**:
- Clear step-by-step instructions
- References existing patterns (recent commits)
- Specific about following conventions
- Uses allowed-tools for automation
- Lets Claude figure out which commands to run

### Example 2: Security Review Command

```markdown
---
description: Review code for security vulnerabilities
---

Perform a comprehensive security review of the provided code.

**Check for**:
- SQL injection vulnerabilities
- Cross-site scripting (XSS)
- Insecure direct object references
- Authentication and authorization issues
- Sensitive data exposure
- Security misconfigurations
- Use of vulnerable dependencies

**For each issue found, provide**:
1. Severity level (Critical/High/Medium/Low)
2. Exact location (file and line number)
3. Description of the vulnerability
4. Specific code fix with examples
5. Prevention recommendations

**Output format**: Markdown with code blocks for examples.
```

**Why this works**:
- Comprehensive checklist
- Clear output format
- Specific requirements for findings
- Actionable recommendations

## Quick Checklist

Before finalizing your command prompt:

- [ ] Instructions are specific and concise
- [ ] Success criteria are clear (add detail through iteration)
- [ ] Expected output format is defined (if needed)
- [ ] Team standards are referenced (if applicable)
- [ ] Context is provided (bash commands, file references when needed)
- [ ] Structure uses clear sections (for complex commands)
- [ ] Uses bullet points for lists (when appropriate)
- [ ] Avoids being too prescriptive
- [ ] Focuses on "what" and "why", not just "how"
- [ ] Start simple - add complexity based on real usage


