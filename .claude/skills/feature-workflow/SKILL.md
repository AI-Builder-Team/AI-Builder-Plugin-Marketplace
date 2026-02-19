---
name: feature-workflow
description: Guides through the feature development workflow. Use when starting a new feature, updating an existing feature, or following the standard development process. Trigger phrases: "new feature", "start feature", "feature development", "update feature", "development workflow", "create feature", "begin feature", "follow feature workflow", "feature process"
---

# Feature Workflow

This skill guides you through the standard feature development workflow.

## Table of Contents

- [When to Use](#when-to-use)
- [Workflow](#workflow)
- [Create Feature Workflow](#create-feature-workflow)
  - [Step C1: Identify Domain](#step-c1-identify-domain)
  - [Step C2: Determine Feature ID](#step-c2-determine-feature-id)
  - [Step C3: Create Feature Structure](#step-c3-create-feature-structure)
  - [Step C4: Create Feature Document](#step-c4-create-feature-document)
  - [Step C5: Populate Initial Content](#step-c5-populate-initial-content)
  - [Step C6: Link Feature Specs](#step-c6-link-feature-specs)
- [Update Feature Workflow](#update-feature-workflow)
  - [Step U1: Locate Feature](#step-u1-locate-feature)
  - [Step U2: Identify Updates](#step-u2-identify-updates)
  - [Step U3: Apply Updates](#step-u3-apply-updates)
  - [Step U4: Verify Consistency](#step-u4-verify-consistency)

## When to Use

Use this skill when:
- Starting work on a new feature
- Updating an existing feature
- Following the standard development process

## Workflow

### Step 1: Determine Action

Ask user whether they want to:
1. **Create** a new feature
2. **Update** an existing feature

---

## Create Feature Workflow

### Step C1: Identify Domain

1. Read `features/index.md` to get the list of valid domains
2. Present domains as a numbered, comma-separated list in one paragraph (e.g., "1. Admin, 2. Renewals, 3. Budget Bot, ..."). Ask user to pick a number or specify a new domain.
3. If user suggests a new domain:
   - Cross-check existing domains to see if any already fits the feature
   - If a match exists, recommend it to the user
   - If user disagrees with recommendation, proceed to create new domain
   - Add new domain to `features/index.md` following the existing table format
4. Note the domain's folder name for Step C2

### Step C2: Determine Feature ID

1. Get the feature name from the user
2. Convert to hyphenated lowercase format (e.g., "Budget Variance Report" → `budget-variance-report`)
3. Check `features/<domain-folder>/` directory to ensure no existing feature with the same ID
4. If conflict exists, ask user for alternative name

### Step C3: Create Feature Structure

Create the feature folder inside the domain folder:
```
features/
├── index.md
└── <domain-folder>/
    └── <feature-id>/
        ├── FEATURE.md
        └── specs/
```

### Step C4: Create Feature Document

Use the template at [templates/FEATURE-TEMPLATE.md](templates/FEATURE-TEMPLATE.md) to create `FEATURE.md` in the feature folder.

**Required sections:**
1. **Feature ID** - Unique hyphenated identifier
2. **Metadata** - Domain (from index.md), name, contributors (GitHub IDs)
3. **Table of Contents** - Links to all sections below
4. **Files Touched** - Key files/directories affected by this feature
5. **Linear Tickets** - Tickets created for implementation/updates
6. **Related Surfaces** - Routes, backend endpoints (FastAPI/GraphQL), Redshift & DB tables, schemas, models, config vars, permissions
7. **Related Features** - Links to other feature docs
8. **Feature Overview** - Summary, problem statement, goals, non-goals
9. **Intended State** - Final intended design only (not current state + changes)
10. **System Architecture** - Brief architecture summary
11. **Changelog of Feature Specs** - Specs implemented and their order

### Step C5: Populate Initial Content

1. **Auto-populate Contributors**: Run `gh api user --jq '.login'` to get the current user's GitHub ID and add it to the Contributors field
2. Work with user to fill in known sections. Mark unknown sections with `TBD` placeholder.

### Step C6: Link Feature Specs

As specs are created in the `specs/` subfolder, update the Changelog of Feature Specs section with links and descriptions.

---

## Update Feature Workflow

### Step U1: Locate Feature

1. Ask user for the feature name or ID
2. Search `features/` directory for matching feature folder
3. If not found, list available features in relevant domain(s) for user to choose from
4. Read existing `FEATURE.md` to understand current state

### Step U2: Identify Updates

Ask user what they want to update:
- Add new Linear tickets
- Update Related Surfaces (new routes, endpoints, tables, etc.)
- Add Related Features
- Update Feature Overview or Intended State
- Add new spec to Changelog
- Update Metadata (contributors)
- Update Files Touched section
- Other section updates

### Step U3: Apply Updates

1. Make the requested changes to `FEATURE.md`
2. If adding a new spec, ensure it exists in `specs/` subfolder
3. **Auto-update Contributors**: Run `gh api user --jq '.login'` to get the current user's GitHub ID. If not already in the Contributors list, add it.
4. Update Files Touched section if new files were added

### Step U4: Verify Consistency

The feature doc is a **living document** that should always reflect the intended state. It should NOT show "before and after" or how the feature evolved—the Changelog and specs folder already capture that history.

1. Ensure the document reads coherently as the **intended state**, not as incremental updates
2. Update all sections to reflect the intended design (e.g., if goals changed, rewrite Goals—don't append)
3. Ensure Table of Contents links are still valid
4. Verify Related Features links point to existing feature docs
5. Check that Changelog entries link to existing specs
