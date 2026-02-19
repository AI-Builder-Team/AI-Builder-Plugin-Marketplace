---
name: Evaluating skills
description: Guides Claude through evaluating Agent Skills using a comprehensive framework based on best practices, testing methodology, and quality criteria. Use when reviewing existing skills or validating newly created skills for effectiveness and efficiency.
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit]
---

# Skill Evaluation Framework

## Purpose
Systematically evaluate Agent Skills to ensure they are concise, well-structured, effective, and follow best practices. This framework implements an evaluation-driven approach to skill development.

This framework is based on guidelines from the [Claude Agent Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) documentation.

## When to Use This Skill
- Reviewing an existing skill for quality and effectiveness
- Validating a newly created skill before deployment
- Iterating on a skill based on observed usage patterns
- Auditing skills for token efficiency and clarity
- Comparing multiple skills for similar use cases

## Table of Contents
1. [Initial Assessment](#step-1-initial-assessment)
2. [Metadata Quality Check](#step-2-metadata-quality-check)
3. [Content Structure Analysis](#step-3-content-structure-analysis)
4. [Instruction Quality](#step-4-instruction-quality)
5. [Examples and Demonstrations](#step-5-examples-and-demonstrations)
6. [Workflow and Complexity](#step-6-workflow-and-complexity)
7. [Executable Code Review](#step-7-executable-code-review)
8. [Anti-Patterns Detection](#step-8-anti-patterns-detection)
9. [Token Efficiency Analysis](#step-9-token-efficiency-analysis)
10. [Model Compatibility](#step-10-model-compatibility)
11. [Observational Analysis](#step-11-observational-analysis)
12. [Evaluation-Driven Development Check](#step-12-evaluation-driven-development-check)

## Evaluation Workflow

### Step 1: Initial Assessment
Read the skill file and gather basic information:

**Checklist:**
- [ ] Skill file location identified (personal: `~/.claude/skills/` or project: `.claude/skills/`)
- [ ] YAML frontmatter present with required fields (name, description)
- [ ] File structure follows SKILL.md format
- [ ] Token count estimated (use character count / 4 as rough estimate)

**Questions to Answer:**
1. What problem does this skill solve?
2. Who is the intended user (individual/team)?
3. What is the expected frequency of use?

### Step 2: Metadata Quality Check

**Name Evaluation (64 char max):**
- [ ] Uses gerund form (verb + ing): "Testing code", "Reviewing PRs"
- [ ] Clear and descriptive
- [ ] Follows consistent naming pattern
- [ ] Not overly generic or too specific

**Description Evaluation (1024 char max):**
- [ ] Written in 3rd person
- [ ] Includes what the skill does
- [ ] Specifies when to use it (triggers/contexts)
- [ ] Contains relevant keywords for discoverability
- [ ] Avoids unnecessary words

**Token Cost:**
- [ ] Metadata stays under ~100 tokens
- [ ] Description is concise but complete

### Step 3: Content Structure Analysis

**Progressive Disclosure Check:**
- [ ] Main SKILL.md body is lean (<5k tokens recommended)
- [ ] Complex reference material split into separate files
- [ ] Table of contents present for files >100 lines
- [ ] Clear file references for bundled resources
- [ ] Instructions indicate when to read additional files

**Organization:**
- [ ] Logical flow from start to finish
- [ ] Related information grouped together
- [ ] Clear section headings
- [ ] Consistent formatting throughout

### Step 4: Instruction Quality

**Clarity and Precision:**
- [ ] Instructions are step-by-step and actionable
- [ ] Technical terms used consistently
- [ ] Ambiguity avoided (no "you can use X or Y or Z")
- [ ] Decision points clearly marked with guidance
- [ ] Prerequisites and dependencies explicitly stated

**Appropriate Freedom Level:**

Evaluate if instructions match task needs. High freedom (text-based) for flexible tasks with multiple valid approaches. Medium freedom (pseudocode/parameterized) for preferred patterns with variations. Low freedom (specific scripts) for fragile operations requiring consistency. Verify freedom level matches task fragility—avoid over-constraining flexible tasks or under-constraining critical tasks.

### Step 5: Examples and Demonstrations

**Example Quality:**
- [ ] Concrete input/output pairs provided where needed
- [ ] Examples demonstrate common use cases
- [ ] Edge cases or variations shown if relevant
- [ ] Examples follow consistent format
- [ ] Code examples are syntactically correct

**Coverage:**
- [ ] Success scenarios demonstrated
- [ ] Error handling scenarios shown if applicable
- [ ] Multiple approaches shown only if truly necessary

### Step 6: Workflow and Complexity

**For Complex Tasks:**
- [ ] Clear sequential steps provided
- [ ] Checklist format used for tracking progress
- [ ] Feedback loops implemented (validate → fix → repeat)
- [ ] Validation steps included between major operations
- [ ] Claude can track progress through the workflow

**For Simple Tasks:**
- [ ] Skill doesn't over-complicate straightforward operations
- [ ] Instructions are appropriately brief
- [ ] No unnecessary ceremony or scaffolding

### Step 7: Executable Code Review

**If skill includes scripts/code:**

**Code Quality:**
- [ ] Error conditions handled gracefully
- [ ] Dependencies explicitly documented
- [ ] Configuration parameters justified (no magic numbers)
- [ ] Clear whether Claude should execute or read as reference
- [ ] File paths use forward slashes (cross-platform)

**Utility Script Benefits:**
- [ ] More reliable than generated code
- [ ] Saves tokens (no code in context)
- [ ] Saves time (no generation needed)
- [ ] Ensures consistency

**Documentation:**
- [ ] Parameters documented with purpose
- [ ] Return values/outputs explained
- [ ] Usage examples provided
- [ ] Error messages are helpful

### Step 8: Anti-Patterns Detection

**Common Issues to Flag:**
- [ ] Too many choices offered ("use library1, library2, or library3")
- [ ] Backward slashes in file paths on Windows
- [ ] Unnecessary explanations of basic concepts
- [ ] Overly verbose instructions
- [ ] Missing error handling in scripts
- [ ] Vague references to external files
- [ ] Inconsistent terminology within the skill
- [ ] Documentation for imagined problems (not tested)
- [ ] Bundled files that are never accessed

### Step 9: Token Efficiency Analysis

**Calculate Token Costs:**

Use the bundled token counting script for accurate analysis:
```bash
python count_tokens.py /path/to/skill/directory
```

The script provides:
- Metadata tokens (frontmatter)
- Main body tokens (SKILL.md content)
- Bundled files tokens (additional .md, .py, .sh files)
- Total token count with efficiency guidance

**Efficiency Questions:**
1. Does every paragraph justify its token cost?
2. Can Claude infer any of this information already?
3. Are there redundant explanations?
4. Could instructions be more concise without losing clarity?
5. Are examples bloated or minimal?

**Token Savings Opportunities:**
- Replace verbose explanations with concise instructions
- Remove assumed knowledge (Claude is already smart)
- Use executable scripts instead of generating code
- Link to files instead of repeating information

### Step 10: Model Compatibility

**Test Considerations for Different Models:**

- **Haiku**:
  - [ ] Sufficient guidance provided
  - [ ] Critical steps not skipped
  - [ ] Examples clear enough for smaller model

- **Sonnet**:
  - [ ] Instructions clear and efficient
  - [ ] No unnecessary verbosity
  - [ ] Balanced guidance level

- **Opus**:
  - [ ] Not over-explaining basic concepts
  - [ ] Trusts model capabilities
  - [ ] Focuses on specific needs

### Step 11: Observational Analysis

**If Skill Has Been Used:**

Track usage patterns: file reading order, reference following effectiveness, repeated file reads, unused bundled files, workflow deviations, and common failure modes. Use insights to optimize: move repeatedly-read content to main file, remove unused files, restructure for intuitive flow, and add guidance for common failures.

### Step 12: Evaluation-Driven Development Check

**Has EDD Been Followed?**

- [ ] **Gaps Identified**: Specific failures documented before skill creation
- [ ] **Scenarios Built**: 3+ test scenarios exist
- [ ] **Baseline Measured**: Performance without skill documented
- [ ] **Minimal Instructions**: Started with just enough to pass tests
- [ ] **Iteration Applied**: Refined based on evaluation results
- [ ] **Real Problems Solved**: Addresses actual (not imagined) issues

**If No:**
- Recommend building evaluation scenarios first
- Establish baseline performance without skill
- Iterate with measurements

## Evaluation Output Format

After completing evaluation, provide a structured report using the template in `report-template.md`. The report should include scores (1-5 scale), strengths, issues found, recommendations, token analysis, testing status, and next steps.

**Output Location**: Save the final evaluation report as `EVALUATION_REPORT.md` in the `.claude/skills/<skill-name>/` directory (basically same directory as the skill you are evaluating). Overwrite existing file if it exists.

## Best Practices Reminders

Challenge assumptions, trust Claude's intelligence, measure token impact, start with minimal instructions, iterate based on usage data, maintain single purpose per skill, use progressive disclosure, and test with all target models.

## Version History

**Current Version**: v2.2 (2025-10-22)

For detailed version history and changelog, see [VERSION_HISTORY.md](VERSION_HISTORY.md).
