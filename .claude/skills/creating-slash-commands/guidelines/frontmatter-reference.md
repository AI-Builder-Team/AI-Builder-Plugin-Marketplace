# Frontmatter Reference

YAML frontmatter goes at the top of your command file between `---` markers.

## Template

```yaml
---
description: Brief description of what the command does
argument-hint: [expected-arguments]
model: claude-3-5-sonnet-20240620
allowed-tools: Bash(git add:*), Bash(git commit:*)
disable-model-invocation: false
---
```

## Field Descriptions

### `description` (Recommended)

**Purpose**: Brief description shown in `/help` and used by SlashCommand tool for discovery.

**Format**: One concise sentence describing what the command does.

**Examples**:
```yaml
description: Review code for security vulnerabilities
description: Create and push a git commit
description: Analyze file for performance issues
```

**Best practices**:
- Keep under 100 characters
- Be specific and actionable
- Focus on what it does, not how

### `argument-hint` (Optional)

**Purpose**: Helps users understand expected arguments.

**Format**: Square brackets with argument names.

**Examples**:
```yaml
argument-hint: [issue-number]
argument-hint: [pr-number] [priority] [assignee]
argument-hint: [filename]
```

### `model` (Optional)

**Purpose**: Specify which Claude model to use for this command.

**Default**: Inherits from current conversation.

**Options**:
- `claude-3-5-sonnet-20240620`
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

**When to use**: Specify when command needs specific model capabilities.

### `allowed-tools` (Required for Bash)

**Purpose**: Specify which tools the command can use. Required for bash execution.

**Format**: Comma-separated list of tool permissions.

**Examples**:
```yaml
# Allow specific git commands
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)

# Allow all npm commands
allowed-tools: Bash(npm run:*)

# Allow all bash commands (less secure)
allowed-tools: Bash

# Allow multiple tool types
allowed-tools: Read, Write, Bash(git add:*)
```

**Security note**: Be specific with permissions. Use wildcards only when necessary.

### `disable-model-invocation` (Optional)

**Purpose**: Prevent SlashCommand tool from automatically invoking this command.

**Default**: `false`

**When to use**:
- Rarely-used commands to save character budget
- Commands that should only be manually invoked
- Commands without descriptions (SlashCommand tool ignores these anyway)

**Example**:
```yaml
disable-model-invocation: true
```

## Complete Example

```yaml
---
description: Analyze and fix GitHub issue
argument-hint: [issue-number]
model: claude-3-5-sonnet-20240620
allowed-tools: Bash(gh issue:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*)
disable-model-invocation: false
---
```

## Common Patterns

### Git Workflow Command

```yaml
---
description: Create and push a git commit
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git push:*)
---
```

### File Analysis Command

```yaml
---
description: Analyze file for security issues
argument-hint: [filename]
---
```

### Deployment Command

```yaml
---
description: Pre-deployment quality check
allowed-tools: Bash(npm run:*), Bash(git status:*)
---
```

## Validation Checklist

- [ ] `description` included (required for SlashCommand tool discovery)
- [ ] `argument-hint` matches actual argument usage in prompt
- [ ] `allowed-tools` includes all bash commands used in prompt
- [ ] Tool permissions are as specific as possible
- [ ] YAML syntax is valid (proper indentation, no tabs)

## Troubleshooting

**Command not appearing in `/help`**:
- Check YAML syntax is valid
- Ensure `---` markers are present
- Verify no syntax errors (run `claude --debug`)

**Bash commands not executing**:
- Add `allowed-tools: Bash(command:*)` to frontmatter
- Check command name matches exactly
- Verify permission includes wildcard `*` if using arguments

**SlashCommand tool not invoking**:
- Ensure `description` field exists
- Check `disable-model-invocation` is not `true`
- Verify command is not in permissions deny list
