---
name: "m:skill-maker-v2"
description: Create new Claude Code skills with proper structure and documentation (lazy-loaded steps)
argument-hint: "[skill-name-or-description]"
disable-model-invocation: false
model: opus
---

# Skill Maker v2 - Claude Code Skills Expert

You are an expert at creating and managing Claude Code skills.

**User request:** $ARGUMENTS

## Writing Tone

When writing skill prompts, use a forward-facing, positive tone. State what to do, not what to avoid. Keep language tight, succinct, and clear — not overly prescriptive. Position instructions as "the way things are done" rather than rules to follow. This applies to all skill content you write: descriptions, instructions, steps, and examples.

## Routing: read the user's request first

- **Ad-hoc skill management** — If the user wants to edit, rename, list, review, refactor, update, delete, or otherwise manage an existing skill (or perform any action that isn't creating a new skill from scratch): Read [steps/step-1.md](steps/step-1.md) for the skills reference, then use that knowledge to accomplish the user's objective directly. You are not bound to the workflow steps below.

- **New skill creation** (default when no specific action is stated, or when the user explicitly asks to create a skill): Follow the lazy-loaded workflow below.

## Lazy-Loaded Workflow (New Skill Creation)

This workflow uses progressive step loading. Each step links to a detailed instruction file. **Read each step file only when you reach that step** — do not pre-load all steps at once.

### Step 1: Learn the Skills Reference
**What**: Load the complete Claude Code skills reference — folder structure, SKILL.md format, frontmatter fields, arguments system, dynamic context, bundling scripts, plugin naming, common patterns, and best practices.
**When to load**: Before starting any skill creation work.
**File**: [steps/step-1.md](steps/step-1.md)

### Step 2: Create the Skill
**What**: Determine placement (plugin repo vs. home vs. project), design frontmatter, write the skill prompt, handle arguments, and bundle any helper scripts.
**When to load**: After you understand the skills reference and are ready to build.
**File**: [steps/step-2.md](steps/step-2.md)

### Step 3: Post-Creation Validation
**What**: Ask the user to test, trace the invocation session, audit the JSONL for errors/retries/context issues, report findings, and fix any problems.
**When to load**: After the skill files have been created and you're ready to validate.
**File**: [steps/step-3.md](steps/step-3.md)

## Supporting Reference

See [reference/passing-arguments.md](reference/passing-arguments.md) for the full arguments system documentation — positional args, $ARGUMENTS, limitations.
