---
name: comparing-prototypes
description: Compares two branch implementations of the same spec across multiple criteria (spec compliance, code quality, testing, performance). Use when analyzing competing implementations, evaluating prototype branches, or choosing between implementation approaches. Triggers on "compare prototypes", "compare branches", "compare implementations", "evaluate prototypes".
allowed-tools: [Read, Write, Bash, Glob, Grep, Edit, SlashCommand, AskUserQuestion]
---

# Comparing Prototypes

Systematically compares two branch implementations of the same specification to determine which better meets requirements and follows best practices.

## Workflow Overview

This is a **multi-phase workflow** with context management:

1. **Spec Understanding** - Locate and analyze the specification
2. **Branch 1 Analysis** - Checkout, analyze, and document first implementation
3. **Context Compaction** - Reduce context before analyzing second branch
4. **Branch 2 Analysis** - Checkout, analyze, and document second implementation
5. **Context Compaction** - Reduce context before comparison
6. **Comparison & Report** - Compare implementations and generate final report

## Phase 1: Spec Understanding

1. **Locate Specification**:
   - Search for spec files using Glob: `specs/**/*.md`, `docs/specs/**/*.md`, `**/*spec*.md`
   - If multiple found, present list to user with AskUserQuestion
   - If none found, ask user to provide spec file path

2. **Read and Analyze Spec**:
   - Read the spec file completely
   - Identify key requirements, features, acceptance criteria
   - Note technical constraints and implementation guidelines
   - Create mental model of what "success" looks like

## Phase 2: Branch 1 Analysis

1. **Get Branch Information**:
   - If user hasn't provided branch names, use AskUserQuestion to ask for:
     - Branch 1 name
     - Branch 2 name
   - Store these for the workflow

2. **Checkout Branch 1**:
   ```bash
   git checkout <branch-1-name>
   ```

3. **Analyze Implementation**:
   - Use Glob/Grep to locate relevant implementation files
   - Read key implementation files
   - Apply analysis criteria from [guidelines/analysis-criteria.md](guidelines/analysis-criteria.md):
     - Spec compliance
     - Code quality
     - Testing coverage
     - Performance considerations

4. **Document Findings**:
   - Create `spec_matching_tree1.md` using [templates/spec-matching-template.md](templates/spec-matching-template.md)
   - Create `implementation_approach_tree1.md` using [templates/implementation-approach-template.md](templates/implementation-approach-template.md)
   - Save both files to project root

## Phase 3: Context Compaction (After Branch 1)

Run the compact command to reduce context window:
```
/compact summarize under 200 words
```

Wait for compaction to complete before proceeding.

## Phase 4: Branch 2 Analysis

1. **Checkout Branch 2**:
   ```bash
   git checkout <branch-2-name>
   ```

2. **Analyze Implementation**:
   - Repeat the same analysis process as Branch 1
   - Use same criteria from [guidelines/analysis-criteria.md](guidelines/analysis-criteria.md)
   - Focus on same files/areas for fair comparison

3. **Document Findings**:
   - Create `spec_matching_tree2.md` using [templates/spec-matching-template.md](templates/spec-matching-template.md)
   - Create `implementation_approach_tree2.md` using [templates/implementation-approach-template.md](templates/implementation-approach-template.md)
   - Save both files to project root

## Phase 5: Context Compaction (After Branch 2)

Run the compact command again:
```
/compact summarize under 200 words
```

Wait for compaction to complete before proceeding.

## Phase 6: Comparison & Final Report

1. **Read All Documentation**:
   - Read `spec_matching_tree1.md` and `spec_matching_tree2.md`
   - Read `implementation_approach_tree1.md` and `implementation_approach_tree2.md`

2. **Compare Implementations**:
   - **Spec Compliance**: Which implementation better fulfills spec requirements?
   - **Code Quality**: Which has better organization, readability, maintainability?
   - **Testing Coverage**: Which has more comprehensive and effective tests?
   - **Performance**: Which has better performance characteristics?
   - **Overall Recommendation**: Which implementation should be preferred and why?

3. **Generate Final Report**:
   - Create `prototype_comparison_report.md` using [templates/comparison-report-template.md](templates/comparison-report-template.md)
   - Include:
     - Executive summary with clear recommendation
     - Detailed comparison across all criteria
     - Strengths and weaknesses of each approach
     - Specific examples and code references (file:line format)
     - Action items or next steps

4. **Present Summary to User**:
   - Provide a concise verbal summary (3-5 key points)
   - Highlight the recommended implementation
   - Note any critical differences or concerns
   - Reference the full report for details

## Best Practices

- **Fair Comparison**: Analyze the same aspects of both implementations
- **Objective Analysis**: Focus on measurable criteria, not subjective preferences
- **Specific Examples**: Reference actual code with file:line format
- **Context Management**: Don't skip the /compact commands - they're essential for managing token budget
- **Clear Recommendation**: Always provide a definitive recommendation with reasoning

## Notes

- All output files are saved to the project root directory
- The skill automatically searches for spec files in common locations
- Context compaction is critical - don't skip those phases
- If a branch doesn't exist, ask the user to verify the branch name
