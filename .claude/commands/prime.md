# Prime

Load essential project context to begin development. Reads core documentation and shows current project status.

## Usage

```
/prime
```

No parameters needed.

## Process

When this command is invoked:

### Step 1: Load Core Documentation

Read the following files (these auto-import other docs):
1. `CLAUDE.md` - Main guide (imports patterns.md, tsdoc-standards.md, specs/CLAUDE.md, specs/ROADMAP.md, includes directory structure)
2. `specs/ROADMAP.md` - Current project status and spec dependencies

### Step 2: Present Current Status

Parse specs/ROADMAP.md and present:

```markdown
## Current Project Status

**In Progress** (🚧):
- [List specs with status "In Progress"]

**Ready to Start** (📋):
- [List specs with status "Planned" and no dependencies or dependencies complete]

**Blocked** (⏸️):
- [List specs with status "Blocked" and what they're waiting for]

**Recently Completed** (✅):
- [List recently completed specs if any]
```

### Step 3: Suggest Next Steps

Based on current status:
- If work in progress: "Continue with `/implement_spec [path]`"
- If specs ready: "Start new work with `/implement_spec [path]`"
- If planning needed: "Plan features with `/plan_feature [description]`"

## Output Format

```markdown
# Project Primed

**Loaded**: CLAUDE.md, specs/ROADMAP.md, project structure

## Current Status
[Parsed status from specs/ROADMAP.md]

## Next Steps
[Suggested actions based on status]

Ready for development.
```

## Context Optimization

- **Total loaded**: ~10-15KB (CLAUDE.md + imports + specs/ROADMAP.md)
- **Files NOT read**: Individual specs, source code, tests, templates
- **Use agents for**: Deep codebase exploration when needed
