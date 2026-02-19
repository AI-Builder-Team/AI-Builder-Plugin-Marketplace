---
name: creating-skills
description: Guides users through creating Agent Skills for Claude Code. Use when building new skills, designing skill structure, or authoring skill documentation. Triggers on "create skill", "build skill", "new agent skill", or "skill development".
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# Creating Agent Skills for Claude Code

This skill guides you through creating Agent Skills—packaged prompts that extend Claude Code's capabilities for specific workflows.

**What you'll learn:**
- Design skill structure with progressive disclosure
- Write token-efficient YAML frontmatter and instructions
- Choose appropriate workflow patterns
- Apply best practices and avoid common pitfalls

**Output:** A complete, well-structured skill ready for use in Claude Code.

## When to Use This Skill

Use this skill when:
- **Creating a new skill**: Building from scratch with proper structure

**Trigger phrases**: "create skill", "build skill", "new agent skill", "skill development"

## Prerequisites

Before creating a skill:
- Clear understanding of the task/workflow your skill will address

**Note on Guidelines:** Guideline files contain examples at the end. Refer to them if something is unclear or if the guideline notes the example is opinionated.

## Core Workflow

1. **Understand the Need**: Identify the capability gap and specific tasks the skill will handle
2. **Choose Workflow Pattern**: Select from [guidelines/workflow-patterns-guide.md](guidelines/workflow-patterns-guide.md) and confirm with user
3. **Create Structure**:
   - Create directory: `.claude/skills/skill-name/` or `~/.claude/skills/skill-name/`
   - Create `SKILL.md` with YAML frontmatter (see [Creating Frontmatter](#creating-frontmatter))
4. **Write Core Content**:
   - Add main workflow instructions (keep main file <5k tokens)
   - Create supporting files in `guidelines/` for detailed content
   - Reference guidelines using relative paths

See [Supporting Workflows](#supporting-workflows) for detailed guidance on each step.

## Supporting Workflows

### Creating Frontmatter

Write YAML frontmatter at the top of `SKILL.md`:

```yaml
---
name: skill-name          # Use gerund form: "verb-ing"
description: What it does. Use when [trigger phrases].
allowed-tools: [Read, Write, Bash]  # Optional: restrict tools
---
```

**Details**: See [guidelines/frontmatter-guide.md](guidelines/frontmatter-guide.md)

### Structuring Files

Use progressive disclosure:
- **SKILL.md**: Core workflow (<5k tokens)
- **guidelines/**: Detailed content loaded on-demand (optional)
- **templates/**: Reusable templates (optional)
- **scripts/**: Executable helpers (optional)

**Details**: See [guidelines/file-structure-guide.md](guidelines/file-structure-guide.md)

### Writing Instructions

Match instruction specificity to task fragility:
- **High freedom**: Creative tasks
- **Low freedom**: Critical operations requiring exact steps

Use clear, actionable language. Avoid choice overload.

**Details**: See [guidelines/instruction-writing-guide.md](guidelines/instruction-writing-guide.md)

### Optimizing Tokens

- Challenge every word: "Does Claude already know this?"
- Keep SKILL.md under 5k tokens
- Move verbose content to supporting files
- Use executable scripts instead of long code listings

**Details**: See [guidelines/token-efficiency-guide.md](guidelines/token-efficiency-guide.md)

## Guidelines Reference

Detailed guides available on-demand:

- **[frontmatter-guide.md](guidelines/frontmatter-guide.md)**: YAML specifications, naming conventions, description formats
- **[file-structure-guide.md](guidelines/file-structure-guide.md)**: Progressive disclosure patterns, directory organization
- **[instruction-writing-guide.md](guidelines/instruction-writing-guide.md)**: Freedom levels, instruction patterns, writing clear steps
- **[token-efficiency-guide.md](guidelines/token-efficiency-guide.md)**: Token budgets, optimization strategies
- **[workflow-patterns-guide.md](guidelines/workflow-patterns-guide.md)**: 6 workflow patterns (linear, conditional, validation loop, multi-phase, iterative, parallel)
- **[anti-patterns-guide.md](guidelines/anti-patterns-guide.md)**: Common mistakes and how to avoid them
- **[examples-guide.md](guidelines/examples-guide.md)**: Example placement strategies (templates vs guidelines)

## Common Patterns & Anti-Patterns

### ✅ Do

- Use gerund form for names: `creating-reports`, `analyzing-data`
- Include trigger phrases in description
- Keep SKILL.md under 5k tokens
- Use progressive disclosure with supporting files
- Provide one clear default approach
- Use forward slashes in all paths
- Match instruction specificity to task fragility

### ❌ Don't

- Vague names: `helper`, `tool`
- Missing trigger phrases in description
- Monolithic files (>10k tokens)
- Choice overload: "Use A or B or C or D"
- Windows-style backslashes in paths
- Over-explaining what Claude already knows
- Nested file references (more than one level deep)

See [guidelines/anti-patterns-guide.md](guidelines/anti-patterns-guide.md) for detailed examples.

## Best Practices

1. **Token Efficiency First**: Challenge every word. Does Claude already know this?
2. **Progressive Disclosure**: Load content on-demand via supporting files. Use clear file structure and section mapping (e.g., table of contents) to help Claude quickly identify which files are most relevant
3. **Clear Defaults**: Provide one recommended approach, not multiple options
4. **Actionable Instructions**: Specific steps that are verifiable
5. **Consistent Terminology**: Use the same terms throughout
6. **Appropriate Freedom**: Match instruction specificity to task fragility

Remember: A well-crafted skill should be concise, clear, and immediately actionable.
