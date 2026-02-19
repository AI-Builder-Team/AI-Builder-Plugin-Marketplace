# Examples Writing Guide

## Purpose of Examples

Examples should:
- Demonstrate specific functionality
- Clarify ambiguous instructions
- Provide copyable formats
- Show concrete input/output pairs
- Illustrate best practices

## Examples Placement Strategy

### For Templates
**Use inline examples throughout**
- Show how to fill out each section
- Provide placeholder text that can be replaced
- Demonstrate the expected format directly

**Example:**
```markdown
## Template Section

**Name:** [verb]-[objects]  # e.g., "reviewing-pull-requests"
**Description:** [What it does]. Use when [trigger phrases].
```

### For Guidelines
**Place examples at the end of each guideline file**
- Examples should only be referenced when something is unclear
- Keeps main content concise and instruction-focused
- Allows Claude to refer to examples on-demand

**Structure:**
```markdown
[Main guideline content...]

---

## Examples

### Example 1: [Title]
[Example content]

### Example 2: [Title]
[Example content]
```

### In SKILL.md
**Include this instruction:**
```markdown
**Note on Guidelines:** Guideline files contain examples at the end. Refer to them if something is unclear or if the guideline notes the example is opinionated.
```

## Opinionated Examples

When a guideline includes an opinionated approach, mark it at the start:

```markdown
# Guideline Title

**Note:** This guideline demonstrates an opinionated approach. See examples at the end for concrete implementations.

[Guideline content...]
```

This signals Claude to reference the examples proactively.

## Example Patterns

### Pattern A: Input/Output Pair
**Best for:** Showing transformations or results

```markdown
## Example: Generating Commit Message

**Input:**
```bash
git diff --staged
```

**Output:**
```
feat: Add user authentication

- Implement JWT token generation
- Add login endpoint
```
```

### Pattern B: Before/After
**Best for:** Showing improvements or refactoring

```markdown
## Example: Improving Description

**Before:**
```yaml
description: Helps with code
```

**After:**
```yaml
description: Reviews code for quality issues. Use when analyzing pull requests.
```

**Why better:** Specifies what it does and when to use it
```

### Pattern C: Template with Placeholders
**Best for:** Providing structure to follow

```markdown
## Example: YAML Frontmatter Template

```yaml
---
name: [verb]-[objects]  # e.g., "reviewing-pull-requests"
description: [What it does]. Use when [trigger phrases].
---
```

Fill in bracketed sections with your specifics.
```

### Pattern D: Annotated Example
**Best for:** Explaining complex structures

```markdown
## Example: Skill with Supporting Files

```markdown
# Main SKILL.md

## Workflow
1. Check prerequisites
2. See [guidelines/specs.md](guidelines/specs.md)  ← Reference to guideline
3. Implement core functionality
```

**Key points:**
- Main file stays lean
- Supporting files referenced when needed
```

### Pattern E: Comparison Table
**Best for:** Showing multiple options or variations

```markdown
## Example: Freedom Levels

| Task Type | Freedom Level | Example |
|-----------|---------------|---------|
| Creative writing | High | "Write a summary" |
| Structured report | Medium | "Report with: Summary, Findings" |
| Database migration | Low | Provide exact SQL script |
```

### Pattern F: Step-by-Step Walkthrough
**Best for:** Demonstrating workflow

```markdown
## Example: Creating Personal Skill

**Step 1:** Create directory
```bash
mkdir ~/.claude/skills/my-skill/
```

**Step 2:** Create SKILL.md
```bash
cat > ~/.claude/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Does something useful. Use when working on X.
---
EOF
```
```

## Example Quality Guidelines

### Use Realistic Examples

❌ **Don't:** Use foo/bar/baz placeholders
```markdown
description: Processes foo to generate bar
```

✅ **Do:** Use realistic domain examples
```markdown
description: Reviews pull requests for code quality issues
```

### Make Examples Copyable

✅ **Good:** Complete, working example
```yaml
---
name: reviewing-code
description: Reviews code for quality issues. Use when analyzing PRs.
allowed-tools: [Read, Grep, Glob]
---
```

❌ **Bad:** Partial or broken example
```yaml
name: [something]
description: [fill this in]
```

### Keep Examples Concise

**Too long:**
```markdown
[Pages of example code with every possible variation]
```

**Right size:**
```markdown
## Basic Example
[Minimal working example]

For advanced usage, see [examples/advanced.md](examples/advanced.md)
```

### Annotate When Necessary

```markdown
## Example with Annotations

```yaml
---
name: analyzing-data          # ← Gerund form
description: Analyzes data for trends. Use when reviewing reports.  # ← What + when
allowed-tools: [Read, Bash]   # ← Optional: restricts tools
---
```
```

## Examples Checklist

- [ ] Demonstrates specific functionality
- [ ] Uses realistic domain examples
- [ ] Copyable and complete (not partial)
- [ ] Concise (not overly verbose)
- [ ] Correct syntax
- [ ] Annotated if complex
- [ ] Follows consistent format
- [ ] Placed correctly (inline for templates, end for guidelines)

## Common Mistakes

❌ **Too many examples**: Showing every possible variation
❌ **Incomplete examples**: Missing required parts
❌ **Unrealistic examples**: foo/bar placeholders
❌ **Broken code**: Syntax errors in examples
❌ **No context**: Example without explanation
❌ **Wrong placement**: Inline examples in guidelines (should be at end)

## Best Practices

✅ **Templates = Inline**: Show format directly where needed
✅ **Guidelines = End**: Examples at bottom, reference when unclear
✅ **Realistic domain**: Use actual use cases
✅ **Complete and working**: Can be copied directly
✅ **Opinionated markers**: Note at file start when applicable
✅ **Concise**: One good example better than many poor ones
✅ **Consistent format**: Same structure throughout
