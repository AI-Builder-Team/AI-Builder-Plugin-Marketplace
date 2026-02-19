# Comparing Prototypes Skill

A systematic skill for comparing two branch implementations of the same specification across multiple quality criteria.

## Purpose

When you have two competing implementations of the same feature (e.g., two different developers or two AI agents implementing the same spec), this skill provides a structured workflow to:
- Analyze both implementations objectively
- Compare them across spec compliance, code quality, testing, and performance
- Generate comprehensive documentation
- Provide a clear recommendation

## Usage

Invoke this skill with:
```
/comparing-prototypes
```

Or trigger with phrases like:
- "compare prototypes"
- "compare these two branches"
- "evaluate competing implementations"
- "which implementation is better"

## What It Does

1. **Finds and analyzes the spec** - Automatically searches for spec files
2. **Analyzes Branch 1** - Checks out first branch, analyzes implementation, creates documentation
3. **Compacts context** - Runs `/compact` to manage token budget
4. **Analyzes Branch 2** - Repeats analysis for second branch
5. **Compacts context again** - Another `/compact` for final comparison
6. **Generates comparison report** - Detailed side-by-side analysis with recommendation

## Output Files

All files are saved to the project root:

1. **spec_matching_tree1.md** - How well Branch 1 meets spec requirements
2. **implementation_approach_tree1.md** - Code quality, testing, performance analysis for Branch 1
3. **spec_matching_tree2.md** - How well Branch 2 meets spec requirements
4. **implementation_approach_tree2.md** - Code quality, testing, performance analysis for Branch 2
5. **prototype_comparison_report.md** - Final comparison and recommendation

## Analysis Criteria

The skill evaluates implementations across four dimensions:

1. **Spec Compliance** - Requirements coverage, acceptance criteria, constraints
2. **Code Quality** - Architecture, organization, readability, patterns, error handling
3. **Testing Coverage** - Unit tests, integration tests, edge cases, test quality
4. **Performance** - Algorithm efficiency, caching, database queries, bottlenecks

## Skill Structure

```
comparing-prototypes/
├── SKILL.md                                    # Main workflow (~688 words)
├── README.md                                    # This file
├── guidelines/
│   └── analysis-criteria.md                    # Detailed evaluation criteria
└── templates/
    ├── spec-matching-template.md               # Template for spec compliance docs
    ├── implementation-approach-template.md     # Template for implementation analysis
    └── comparison-report-template.md           # Template for final comparison report
```

## Best Practices

- **Provide branch names upfront** - Include them in your initial request to save time
- **Ensure branches exist** - The skill will check out branches, so they must exist locally
- **Review the final report** - The `prototype_comparison_report.md` contains the most important findings
- **Don't skip context compaction** - The `/compact` commands are essential for managing token budget

## Example Usage

```
User: "I have two implementations of the user authentication feature in branches
       'auth-v1' and 'auth-v2'. Can you compare them using the comparing-prototypes
       skill? The spec is in specs/authentication-spec.md"

Claude: [Invokes comparing-prototypes skill]
        [Analyzes both branches systematically]
        [Generates all documentation]
        [Provides recommendation]
```

## Token Efficiency

- Main SKILL.md: ~1000 tokens
- Guidelines loaded on-demand: ~1500 tokens
- Templates used as structure (not loaded into context)
- Total skill overhead: ~2500 tokens

The skill uses context compaction strategically to manage token budget during the multi-phase analysis.
