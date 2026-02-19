# Instruction Writing Guidelines

## Core Principles

1. **Clear and Actionable**: Every instruction should have a specific action
2. **Consistent Terminology**: Use same terms throughout
3. **Appropriate Freedom**: Match instruction specificity to task fragility
4. **Avoid Ambiguity**: No "you can use X or Y or Z" without guidance
5. **Trust Claude**: Don't over-explain what Claude already knows

## Freedom Levels

**High Freedom (Text Instructions):**
- For flexible tasks with multiple valid approaches
- Creative or adaptive work
- Example: "Analyze the codebase and identify potential improvements"

**Medium Freedom (Structured Guidance):**
- For preferred patterns with variations
- Structured but adaptable
- Example: "Generate a report with sections: Summary, Findings, Recommendations"

**Low Freedom (Exact Scripts/Templates):**
- For error-prone operations requiring consistency
- Critical, fragile tasks
- Example: Provide exact bash script for database migration

**Match freedom to task fragility:**
- Critical operations = Lower freedom (more specific)
- Creative tasks = Higher freedom (more flexible)

## Instruction Patterns

**Step-by-Step Format:**
```markdown
## Workflow

1. **First Step**: Clear action to take
2. **Second Step**: What to do next
3. **Third Step**: Final action
```

**Conditional Instructions:**
```markdown
## Process

1. **Check Context**: Determine current state
2. **Branch Based on Context**:
   - If condition A: Follow workflow A
   - If condition B: Follow workflow B
3. **Execute Selected Workflow**
```

**Checklist Format:**
```markdown
## Phase 1: Preparation
- [ ] Verify prerequisites exist
- [ ] Create working directory
- [ ] Initialize configuration

## Phase 2: Implementation
- [ ] Implement core functionality
- [ ] Add error handling
- [ ] Write tests
```

## Writing Clear Instructions

**Good:**
```markdown
1. Read the current SKILL.md file
2. Validate YAML frontmatter syntax
3. Check that name uses gerund form (verb + -ing)
4. Verify description includes trigger phrases
```

**Bad:**
```markdown
1. Look at the skill file and make sure everything is correct
2. Check if it's okay
3. Maybe validate some things if needed
```

**Why?** Good instructions are specific, actionable, and verifiable.

## Decision Points

**Provide Clear Guidance:**
```markdown
**Choosing Storage Location:**
- Use `~/.claude/skills/` for personal workflows
- Use `.claude/skills/` for team-shared workflows
- Default to project skills if unsure
```

**Not:**
```markdown
You can put it in personal or project skills, whichever you prefer.
```

## Prerequisites and Dependencies

**Always State Explicitly:**
```markdown
## Prerequisites

Before starting, ensure:
- [ ] Git repository initialized
- [ ] Python 3.10+ installed
- [ ] Required packages: `pip install pyyaml anthropic`
```

## Validation Steps

**Include Checkpoints:**
```markdown
## Step 3: Create Frontmatter

1. Write YAML frontmatter
2. **Validate**: Run `python scripts/validate_yaml.py SKILL.md`
3. **Verify**: Check that validation passes
4. If errors found, fix and repeat step 2
```

## Common Mistakes

❌ **Too many options**: "Use library1, library2, library3, or library4"
❌ **Vague actions**: "Do the necessary steps"
❌ **Assumed knowledge**: Not stating prerequisites
❌ **Inconsistent terms**: Using "skill" and "agent capability" interchangeably
❌ **Over-explaining**: Describing basic concepts Claude knows
❌ **Ambiguous conditions**: "If it seems like X..."

## Best Practices

✅ **One clear default**: Provide single recommended approach
✅ **Explicit validation**: Include checkpoints between major steps
✅ **Consistent terminology**: Same terms throughout
✅ **Concrete examples**: Show specific input/output
✅ **Error handling**: What to do when things fail
✅ **Progress tracking**: Use checkboxes or numbered steps
