# Frontmatter Guidelines

## YAML Format

```yaml
---
name: skill-name
description: What it does and when to use it
allowed-tools: [optional tool list]
---
```

## Field Specifications

| Field | Max Length | Format | Purpose |
|-------|------------|--------|---------|
| `name` | 64 chars | Lowercase, numbers, hyphens | Unique identifier |
| `description` | 1024 chars | 3rd person, what + when | Discovery (CRITICAL) |
| `allowed-tools` | N/A | List of tool names | Restrict tools during execution |

## Name Best Practices

**Use gerund form (verb + -ing):**
- ✅ `creating-specs`, `reviewing-code`, `analyzing-data`
- ❌ `create-specs`, `code-review`, `data-analysis`

**Constraints:**
- Lowercase with hyphens only (no underscores, uppercase, spaces)
- No XML tags or reserved words ("anthropic", "claude")
- Clear and specific to the task

## Description Best Practices

**Template:**
```
[ACTION] [OBJECTS]. Use when [TRIGGERS/CONTEXTS]. [REQUIREMENTS if any].
```

**Must Include:**
1. **What it does**: Specific functionality
2. **When to use**: Trigger phrases or contexts (CRITICAL for discovery)
3. **Requirements**: Dependencies/prerequisites if any

**Good Examples:**
```yaml
# Clear what + when
description: Generate clear commit messages from git diffs. Use when writing commit messages or reviewing staged changes.

# Multiple triggers
description: Use when user wants to explore multiple implementation approaches for a feature by creating parallel Claude Code sessions. Triggers on phrases like "competitive prototyping", "prototype in parallel", "compare implementations", "try different approaches", or "race implementations".

# With requirements
description: Extract text and tables from PDF files. Use when working with PDFs or document extraction. Requires pypdf and pdfplumber.
```

**Bad Examples:**
```yaml
# Too vague
description: Helps with documents

# Missing triggers
description: A comprehensive tool for managing project documentation

# No specific functionality
description: Use this for various tasks
```

## allowed-tools Field

**Purpose:** Restrict Claude to specified tools during skill execution

**Common Use Cases:**
- Read-only operations: `[Read, Grep, Glob]`
- Analysis without modification: `[Read, Grep, Glob, Bash]`
- Full file operations: `[Read, Write, Edit, Glob, Grep]`
- Complete access: `[Read, Write, Edit, Glob, Grep, Bash, TodoWrite, WebFetch]`

**Benefits:**
- Enforce read-only mode
- Eliminate permission prompts for approved tools
- Enhance security for sensitive workflows
- Limit scope for focused tasks

**Available Tools:**
`Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`, `TodoWrite`, `WebFetch`, `WebSearch`, `NotebookEdit`, `MultiEdit`, and others

## Token Budget for Metadata

**Target:** ~100 tokens total for frontmatter
- Keep descriptions concise but complete
- Every word must justify its inclusion
- Focus on discovery keywords and triggers
