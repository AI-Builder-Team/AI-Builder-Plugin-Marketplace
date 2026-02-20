---
name: prime
description: Load essential project context and show current development status
tools: Read, Glob, TaskList, TaskGet
color: Blue
---

# Purpose

Get up to speed quickly in a fresh session. Loads project context, checks work status, and provides the exact next command to run.

**Goal:** After running `/prime`, you should know exactly what to do next - either `/research` a new feature or `/orchestrate` an existing one.

## Instructions

### Step 1: Load Project Guidance

Read core documentation:

```
Read: CLAUDE.md (if exists)
```

Note key conventions, patterns, and project-specific rules.

### Step 2: Discover Features

Find all features with research artifacts:

```
Glob: features/**/FEATURE.md
```

For each FEATURE.md found, extract:
- Feature path: `features/{domain}/{feature-name}`
- Feature name from the path

### Step 3: Check TaskList and Link to Features

```
TaskList
```

For each Task, use TaskGet to read the full description:

```
TaskGet: {taskId}
```

**Parse the feature path from the description.** Research creates Tasks with descriptions like:
```
"Run spec and implement skills for features/{domain}/{feature}/specs/{NN}-{name}"
```

Extract `features/{domain}/{feature}` from this pattern.

**Build a feature → tasks mapping:**

```
features/notifications/user-alerts:
  - #1: Spec + Implement 01-foundation (pending, ready)
  - #2: Spec + Implement 02-data (pending, blocked by #1)
  - #3: Spec + Implement 03-ui (pending, blocked by #1, #2)

features/billing/invoices:
  - #4: Spec + Implement 01-setup (in_progress)
```

### Step 4: Determine Feature Status

For each feature, determine status:

| Condition | Status |
|-----------|--------|
| FEATURE.md exists, no Tasks | **Research incomplete** - needs `/orchestrate` or manual Task creation |
| Tasks exist, all pending with blockers clear | **Ready to start** - run `/orchestrate` |
| Tasks exist, some in_progress | **In progress** - agents may be running |
| Tasks exist, some blocked | **Partially complete** - waiting on dependencies |
| All Tasks completed | **Done** - ready to merge |

### Step 5: Present Status

Output in this format:

```markdown
# Project Primed

**Loaded:** CLAUDE.md

## Features

### features/notifications/user-alerts
**Status:** In progress (1/3 specs complete)

| Task | Spec | Status | Blocked By |
|------|------|--------|------------|
| #1 | 01-foundation | ✅ completed | - |
| #2 | 02-data | 🔄 in_progress | - |
| #3 | 03-ui | ⏳ pending | #2 |

**Next:** Agent running on 02-data. Re-run `/orchestrate features/notifications/user-alerts` to check progress.

---

### features/billing/invoices
**Status:** Ready to start

| Task | Spec | Status | Blocked By |
|------|------|--------|------------|
| #4 | 01-setup | ⏳ pending | - |

**Next:** Run `/orchestrate features/billing/invoices`

---

## No Tasks Found

These features have FEATURE.md but no Tasks:
- features/auth/sso → Run `/orchestrate features/auth/sso` (will prompt if Tasks missing)

---

## Summary

| Feature | Status | Next Action |
|---------|--------|-------------|
| notifications/user-alerts | In progress | Wait or check `/orchestrate` |
| billing/invoices | Ready | `/orchestrate features/billing/invoices` |
| auth/sso | No Tasks | Check research or `/orchestrate` |

## Quick Commands

Most urgent action:
\`\`\`
/orchestrate features/billing/invoices
\`\`\`

Or start new work:
\`\`\`
/research
\`\`\`
```

### Step 6: Handle Edge Cases

**No features directory:**
```markdown
# Project Primed

No features/ directory found. This project may not use the feature organization system.

**Next:** Run `/research` to start planning a new feature.
```

**No FEATURE.md files:**
```markdown
# Project Primed

No features with research found.

**Next:** Run `/research` to explore and decompose a feature.
```

**Tasks exist but can't parse feature path:**
```markdown
**Warning:** Task #5 has description that doesn't match expected pattern.
Description: "{description}"
Cannot determine feature path. Check Task manually.
```

---

## Key Principle

**Be specific.** Don't say "run orchestrate" - say "run `/orchestrate features/billing/invoices`".

The user should be able to copy-paste the next command directly from the output.

---

## Output Checklist

Before finishing, verify your output includes:

- [ ] List of features discovered
- [ ] Tasks grouped by feature with status
- [ ] Clear status for each feature (ready/in_progress/blocked/done)
- [ ] **Specific next command** for each feature
- [ ] Summary table for quick scanning
- [ ] Copy-pasteable command in "Quick Commands" section
