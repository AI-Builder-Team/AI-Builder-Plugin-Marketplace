# File Structure Guidelines

## Progressive Disclosure Architecture

**Three-Level Loading:**
1. **Level 1 - Metadata**: YAML frontmatter loads at startup
2. **Level 2 - Core**: SKILL.md body loads when skill invoked
3. **Level 3+ - Supplementary**: Additional files load on-demand

**Main Principle:** Load only what's needed for the current task

## Directory Structure

**Basic Structure:**
```
skill-name/
├── SKILL.md              # Required: Main skill file
├── guidelines/           # Optional: Reference material
│   ├── topic1.md
│   └── topic2.md
├── scripts/              # Optional: Helper scripts
│   └── helper.py
└── VERSION_HISTORY.md    # Optional: Version tracking
```

## Storage Locations

**Personal Skills:** `~/.claude/skills/skill-name/`

**Project Skills:** `.claude/skills/skill-name/`

## SKILL.md Size Guidelines

**Target:** <5,000 tokens (~500 lines)
- Include essential instructions
- Common workflows
- Basic examples
- References to detailed files

**Move to Supporting Files:**
- Detailed reference material
- Advanced examples
- Complex templates
- Long code snippets
- Comprehensive guidelines

## File Organization Patterns

**Pattern A: Topic-Based Guidelines**
```
skill-name/
├── SKILL.md
└── guidelines/
    ├── topic1.md
    ├── topic2.md
    └── topic3.md
```

**Pattern B: Process-Based**
```
skill-name/
├── SKILL.md
├── planning.md
├── implementation.md
└── testing.md
```

**Pattern C: Reference + Scripts**
```
skill-name/
├── SKILL.md
├── REFERENCE.md
└── scripts/
    ├── helper.py
    └── validator.sh
```

## Referencing Supporting Files

**In SKILL.md:**
```markdown
For detailed frontmatter specifications, see [guidelines/frontmatter.md](guidelines/frontmatter.md).
For token efficiency strategies, see [guidelines/tokens.md](guidelines/tokens.md).
Run the validation script: [scripts/validate.py](scripts/validate.py)
```

**File Path Rules:**
- Always use forward slashes (`/`)
- Use relative paths from SKILL.md
- Keep references one level deep (no nested references)
- Claude loads files on-demand when referenced

## Including Executable Scripts

**When to Include:**
- Deterministic operations
- Data processing
- API interactions
- Operations requiring consistency

**Benefits:**
- More reliable than generated code
- Saves tokens (code not in context)
- Saves time (no generation)
- Ensures consistency

**Example Usage in SKILL.md:**
```markdown
## Token Analysis

Use the bundled token counter:
```bash
python scripts/count_tokens.py /path/to/skill
```

The script provides detailed token breakdown.
```

## Table of Contents

**When to Include:** Files >100 lines

**Example:**
```markdown
## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Planning Phase](#planning-phase)
3. [Implementation Phase](#implementation-phase)
4. [Testing Phase](#testing-phase)
5. [Finalization](#finalization)
```

## Anti-Patterns

❌ **Monolithic SKILL.md**: Everything in one giant file
❌ **Nested references**: Files that reference other files
❌ **Windows paths**: `scripts\helper.py` (use forward slashes)
❌ **Unused bundled files**: Files that are never accessed
❌ **Deep nesting**: Multiple levels of subdirectories
