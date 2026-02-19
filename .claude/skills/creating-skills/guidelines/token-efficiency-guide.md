# Token Efficiency Guidelines

## Core Principle

**Challenge every word**: "Does Claude already know this?"

## Token Budgets

**Metadata:** ~100 tokens
- Name: <64 chars
- Description: <1024 chars (but aim shorter)
- Keep concise but complete

**Main SKILL.md:** <5,000 tokens (~500 lines)
- Essential instructions only
- Common workflows
- Basic examples
- References to detailed files

**Supporting Files:** Load on-demand
- Don't count toward base cost
- Only loaded when explicitly referenced
- Can be longer and more detailed

## Token-Saving Strategies

### 1. Remove Assumed Knowledge

**Before (verbose, ~200 tokens):**
```markdown
When you need to analyze the codebase for potential issues, you should
first read through all the relevant files carefully, making sure to
understand the context and structure. Then you should look for common
problems like missing error handling, performance bottlenecks, security
vulnerabilities, and poor code organization.
```

**After (concise, ~80 tokens):**
```markdown
## Analysis Steps
1. Read relevant files
2. Check for: error handling, performance, security, organization
3. Document findings with line numbers
```

### 2. Use Concise Language

**Eliminate fluff:**
- ❌ "In order to accomplish this task, you will need to..."
- ✅ "To accomplish this:"

**Remove redundancy:**
- ❌ "First and foremost, before you begin..."
- ✅ "Before starting:"

**Active voice:**
- ❌ "The file should be read by you"
- ✅ "Read the file"

### 3. Move Verbose Content

**Main file:**
```markdown
## Frontmatter Design

Create YAML frontmatter with name, description, and allowed-tools.
For detailed specifications, see [guidelines/frontmatter.md](guidelines/frontmatter.md).
```

**Supporting file (frontmatter.md):**
```markdown
[Full detailed specifications with examples, constraints, etc.]
```

### 4. Use Executable Scripts

**Instead of this (high token cost):**
```markdown
To count tokens, write a Python script that:
1. Reads the SKILL.md file
2. Parses YAML frontmatter
3. Counts tokens using tiktoken
4. Calculates metadata vs body tokens
5. Provides efficiency recommendations
[Include full script code...]
```

**Do this (low token cost):**
```markdown
To count tokens:
```bash
python scripts/count_tokens.py /path/to/skill
```
```

Script executes without loading code into context.

### 5. Avoid Redundant Explanations

**Say it once clearly:**
- Don't repeat the same concept in different sections
- Link back to earlier explanations
- Use "See [Section X](#section-x)" for references

## Progressive Disclosure Benefits

**Load only what's needed:**
- Metadata loads at startup (100 tokens)
- Main SKILL.md loads when invoked (3-5k tokens)
- Supporting files load on-demand (0 tokens unless referenced)

**Example:**
- Skill with 10 guideline files (20k tokens total)
- Typical invocation: 100 (metadata) + 3k (main) + 2k (1-2 guidelines) = ~5k tokens
- Not 20k tokens

## Efficiency Questions

For every paragraph, ask:
1. Does this justify its token cost?
2. Can Claude infer this already?
3. Is this redundant with other sections?
4. Could this be more concise without losing clarity?
5. Should this be in a supporting file?

## Token Efficiency Checklist

- [ ] Metadata under 100 tokens
- [ ] Main SKILL.md under 5,000 tokens
- [ ] Removed assumed knowledge
- [ ] Eliminated redundant explanations
- [ ] Moved detailed content to supporting files
- [ ] Used executable scripts where appropriate
- [ ] Challenged every word
- [ ] No fluff or filler language
- [ ] Active voice and concise phrasing
- [ ] Supporting files referenced, not duplicated

## Common Token Waste

❌ **Over-explaining basics**: "Claude is an AI assistant that..."
❌ **Verbose introductions**: "In this section we will cover..."
❌ **Unnecessary context**: Explaining concepts Claude knows
❌ **Redundant examples**: Multiple examples of the same concept
❌ **Long code listings**: Include as scripts instead
❌ **Repetitive phrasing**: Saying the same thing multiple ways
❌ **Filler words**: "basically", "essentially", "generally speaking"

## Best Practices

✅ **Concise but complete**: Every word earns its place
✅ **Progressive disclosure**: Split large content into files
✅ **Executable scripts**: For deterministic operations
✅ **Link don't duplicate**: Reference existing content
✅ **Trust Claude**: Skip explaining basic concepts
✅ **Active voice**: Direct and clear
✅ **Measure**: Use token counter to validate efficiency
