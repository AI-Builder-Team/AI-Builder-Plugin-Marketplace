---
name: "m:locator"
description: Load a feature's FEATURE.md and all its specs into context
argument-hint: "<hint>"
---

# Feature Locator

The user wants to load feature documentation into context. Their hint is: **$ARGUMENTS**

## Feature Tree

! `find features -type d | sort`

## Instructions

1. **Identify the feature.** Using the feature tree above and the hint "$ARGUMENTS", determine which feature directory the user is referring to. Use judgment — the hint may be partial, misspelled, or colloquial. If genuinely ambiguous between multiple candidates, list them and ask. Otherwise, pick the best match and proceed.

2. **Read the FEATURE.md.** Read the `FEATURE.md` inside the identified feature directory in full. It will tell you the purpose and reference any connected specs.

3. **Discover and read specs.** `ls` the `specs/` subfolder inside the feature directory (if it exists). Apply this filter:
   - Read files named exactly `spec.md` or matching `spec-*.md` — these are primary specs.
   - Skip `checklist.md`, `research.md`, `design.md`, and any other auxiliary files.

4. **Present a summary.**
   - Feature directory path
   - FEATURE.md purpose (one line)
   - Each spec file read (path + one-liner of what it covers)

All primary spec files are now in context for follow-up questions.
