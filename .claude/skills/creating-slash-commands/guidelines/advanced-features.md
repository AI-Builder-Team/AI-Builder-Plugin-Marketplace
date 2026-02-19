# Advanced Features

Beyond basic commands, slash commands support arguments, bash execution, file references, and more.

## Arguments

### Using `$ARGUMENTS`

Captures all text after the command as a single string.

**Best for**:
- Variable number of arguments
- All arguments treated as one string
- Order doesn't matter

**Example**:
```markdown
---
description: Review and fix GitHub issue
argument-hint: [issue-number]
---

Review and fix the bug described in GitHub issue #$ARGUMENTS.
Follow our coding standards and write tests.
```

**Usage**:
```bash
/fix-issue 123 high-priority
# $ARGUMENTS becomes: "123 high-priority"
```

### Using Positional Arguments (`$1`, `$2`, `$3`)

Access specific arguments individually.

**Best for**:
- Individual control over each argument
- Providing defaults for missing arguments
- Structured commands with specific parameter roles

**Example**:
```markdown
---
description: Review pull request with priority
argument-hint: [pr-number] [priority] [assignee]
---

Review PR #$1 with priority $2 and assign to $3.

Focus on:
- Security vulnerabilities
- Performance issues
- Code style violations
```

**Usage**:
```bash
/review-pr 456 high alice
# $1 = "456", $2 = "high", $3 = "alice"
```

### Argument Best Practices

**When to use each**:
- Use `$ARGUMENTS` when all arguments should be treated as one string
- Use `$1`, `$2` when you need individual control over each argument

**Syntax rules**:
- ✅ `$ARGUMENTS` (uppercase, no braces)
- ❌ `$arguments` (lowercase)
- ❌ `${ARGUMENTS}` (with braces)
- ✅ `$1 $2 $3` (no braces)
- ❌ `${1} ${2}` (with braces)

## Tool Permissions

By default, slash commands require user approval before executing tools. You can pre-approve specific tools using the `allowed-tools` frontmatter field.

### Basic Usage

```markdown
---
allowed-tools: Bash(git status:*)
description: Show current git status
---

Check the current git status and provide recommendations based on the changes.
```

When this command runs, Claude can use `git status` without requiring approval.

### Multi-Command Example

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*)
description: Create a git commit
---

Review the current changes and create a commit:

1. Check what files have changed
2. Review the diff to understand the changes
3. Stage appropriate files
4. Create a commit with a descriptive message following conventional commit format

Check recent commits to match the style.
```

### Permission Formats

```yaml
# Specific command with any arguments
allowed-tools: Bash(git commit:*)

# Multiple commands
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)

# Multiple tools
allowed-tools: Bash(git:*), Read, Edit

# All commands (less secure)
allowed-tools: Bash
```

### When to Use allowed-tools

Use `allowed-tools` when:
- ✅ Commands need to run without interruption (e.g., automated workflows)
- ✅ Multiple related bash commands are expected
- ✅ You trust the specific commands being allowed

Don't use `allowed-tools` when:
- ❌ Commands could be destructive
- ❌ You want to review each action
- ❌ The command doesn't need tool execution

### Best Practices

- ✅ Use specific permissions (e.g., `Bash(git status:*)`)
- ✅ Only allow necessary commands
- ✅ Be specific about command prefixes when possible
- ❌ Don't use `allowed-tools: Bash` unless absolutely necessary
- ❌ Never pre-approve destructive commands without good reason

### Example: Git Workflow

```markdown
---
description: Create and push git commit
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git push:*)
---

Create a git commit following our team conventions:

1. Review what has changed
2. Stage relevant files
3. Create a commit with:
   - Conventional commit format (feat/fix/docs/etc)
   - Scope in parentheses
   - Subject under 50 characters
4. Push to remote

Check recent commit history to match our style.
```

## File References

Include file contents using the `@` prefix.

### Basic Usage

```markdown
Review the implementation in @src/utils/helpers.js
```

### Multiple Files

```markdown
Compare @src/old-version.js with @src/new-version.js
```

### With Arguments

```markdown
---
description: Analyze file for security issues
argument-hint: [filename]
---

Analyze @$ARGUMENTS for security issues:

Check for:
- SQL injection
- XSS vulnerabilities
- Authentication issues
- Sensitive data exposure

Provide specific recommendations.
```

**Usage**:
```bash
/analyze src/auth/login.js
# Reads contents of src/auth/login.js
```

### Best Practices

- ✅ Use relative paths from project root
- ✅ Verify file exists before referencing
- ❌ Don't reference extremely large files (may exceed token limits)

## Subdirectories

Organize related commands in subdirectories.

### Structure

```
.claude/commands/
├── frontend/
│   ├── component.md
│   └── style.md
├── backend/
│   ├── api.md
│   └── database.md
└── testing/
    ├── unit.md
    └── e2e.md
```

### Display & Invocation

**Display in `/help`**: Commands show subdirectory namespace:
```
/component (project:frontend)
/api (project:backend)
```

**Invocation**: Still use simple command name:
```bash
/component  # Not /frontend/component
/api        # Not /backend/api
```

### Best Practices

- ✅ Group related commands by feature or domain
- ✅ Use consistent subdirectory naming
- ✅ Document structure in CLAUDE.md
- ❌ Don't nest too deeply (max 1-2 levels)

## Extended Thinking

Trigger extended thinking by including thinking keywords in your prompt.

### Thinking Levels

- `"think"` - Basic extended thinking
- `"think hard"` - More thinking budget
- `"think harder"` - Even more thinking
- `"ultrathink"` - Maximum thinking budget

### Example

```markdown
---
description: Complex problem analysis
---

Think carefully about this problem and analyze all edge cases.

Provide a comprehensive solution that considers:
- Performance implications
- Security concerns
- Maintainability
- Edge cases and error handling

Think harder about potential failure modes and provide robust error handling.
```

### When to Use

Use extended thinking for:
- Complex architectural decisions
- Security-critical analysis
- Performance optimization planning
- Comprehensive code reviews

## SlashCommand Tool Integration

Claude can programmatically invoke your commands using the SlashCommand tool.

### Requirements

- Command must have a `description` in frontmatter
- Command must be user-defined (not built-in)

### Encouraging Usage

Reference the command by name in instructions:

**In CLAUDE.md**:
```markdown
When writing tests, run /write-unit-test before starting.
```

**In command prompt**:
```markdown
After implementing the feature, run /deploy-check to verify readiness.
```

### Disabling Auto-Invocation

To prevent SlashCommand tool from invoking specific command:

```yaml
---
disable-model-invocation: true
---
```

To disable SlashCommand tool entirely:
```bash
/permissions
# Add to deny rules: SlashCommand
```

## Combining Features

You can combine multiple features in a single command.

### Example: Full-Featured Command

```markdown
---
description: Analyze and fix GitHub issue
argument-hint: [issue-number]
allowed-tools: Bash(gh issue:*), Bash(git:*)
---

Think carefully about the best approach to fix issue #$ARGUMENTS.

1. Fetch and analyze the issue details using gh CLI
2. Check current branch and status
3. Search codebase for relevant files
4. Implement the fix
5. Review @tests/related-test.js and add appropriate tests
6. Create commit and push

Reference issue #$ARGUMENTS in the commit message. Follow conventional commit format based on recent commit history.
```

**This command uses**:
- Arguments (`$ARGUMENTS`)
- Tool permissions (`allowed-tools`)
- File references (`@tests/related-test.js`)
- Extended thinking ("Think carefully")
- SlashCommand tool integration (has description)

## Quick Reference

```markdown
$ARGUMENTS              # All arguments as single string
$1 $2 $3               # Individual positional arguments
@filename              # Reference file content
allowed-tools: Bash    # Pre-approve tools for automation
"think", "think hard"  # Trigger extended thinking
```

Remember: Start with basic features and add complexity as needed.
