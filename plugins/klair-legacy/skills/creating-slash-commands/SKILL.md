---
name: creating-slash-commands
description: Guides users through creating custom slash commands for Claude Code. Use when user wants to create, build, or develop slash commands, automate workflows, or create command shortcuts.
---

# Creating Slash Commands for Claude Code

This skill guides you through creating custom slash commands—shortcuts that automate repetitive workflows, maintain team consistency, and save tokens by storing complex instructions externally.

## Table of Contents

1. [Core Workflow](#core-workflow)
   - [Step 1: Choose Command Scope](#step-1-choose-command-scope)
   - [Step 2: Create Command File](#step-2-create-command-file)
   - [Step 3: Write Frontmatter](#step-3-write-frontmatter-recommended)
   - [Step 4: Write Command Prompt](#step-4-write-command-prompt)

**Output:** A working slash command ready to use in Claude Code.

## Core Workflow

### Step 1: Choose Command Scope

Ask the user where to create the command:

**Project Commands** (`.claude/commands/command-name.md`)
- Shared with team via git, shows "(project)" in `/help`

**Personal Commands** (`~/.claude/commands/command-name.md`)
- Personal to you across all projects, shows "(user)" in `/help`

### Step 2: Create Command File

Create a Markdown file named after your command:

```bash
# For project command
.claude/commands/command-name.md

# For personal command
~/.claude/commands/command-name.md
```

**Naming conventions**:
- Use lowercase with hyphens: `fix-issue.md`, `deploy-check.md`
- Keep names short and descriptive

### Step 3: Write Frontmatter (Recommended)

**⚠️ Complete this step as its own task.** Reference [guidelines/frontmatter-reference.md](guidelines/frontmatter-reference.md) for comprehensive guidance when crafting your frontmatter.

Add YAML frontmatter at the top of the file:

```yaml
---
description: Brief description of what the command does
argument-hint: [expected-arguments]
allowed-tools: Bash(git add:*), Bash(git commit:*)
---
```

**Key fields**:
- `description`: Shows in `/help` and enables SlashCommand tool discovery
- `argument-hint`: Helps users understand expected parameters
- `allowed-tools`: Required for bash execution (see [guidelines/advanced-features.md](guidelines/advanced-features.md))

**Consult the guide**: [guidelines/frontmatter-reference.md](guidelines/frontmatter-reference.md) contains all available fields, validation rules, and best practices.

### Step 4: Write Command Prompt

**⚠️ Complete this step as its own task.** Reference [guidelines/writing-effective-prompts.md](guidelines/writing-effective-prompts.md) for comprehensive guidance when crafting your command prompt.

Below the frontmatter, write clear, specific instructions:

```markdown
---
description: Review code for security issues
---

Perform a comprehensive security review of the provided code.

Check for:
- SQL injection vulnerabilities
- Cross-site scripting (XSS)
- Authentication and authorization issues
- Sensitive data exposure

Provide specific recommendations for each issue found.
```

**Consult the guide**: [guidelines/writing-effective-prompts.md](guidelines/writing-effective-prompts.md) contains prompt writing best practices and patterns.

---

## Advanced Features

Once you've mastered the basic workflow, reference [guidelines/advanced-features.md](guidelines/advanced-features.md) for:

- **Arguments**: Using `$ARGUMENTS` or `$1`, `$2`, `$3` for dynamic commands
- **File References**: Including file contents with `@filename`
- **Subdirectories**: Organizing related commands by feature/domain
- **Extended Thinking**: Triggering deeper analysis with thinking keywords
- **SlashCommand Tool**: Enabling programmatic command invocation
- **Tool Permissions**: Configuring `allowed-tools` for commands that need specific tool access

Start simple with the core workflow above, then add these features as your needs grow.
