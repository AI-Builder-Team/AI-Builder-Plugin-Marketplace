# Anti-Patterns to Avoid

## Metadata Mistakes

### Poor Name/Description
❌ **Problem**: Vague or generic names and descriptions
- Name: "helper" (too vague)
- Description: "Helps with documents" (no triggers)

✅ **Solution**: Specific, trigger-rich metadata
- Name: "reviewing-pull-requests"
- Description: "Reviews PRs for code quality. Use when analyzing pull requests or checking code changes."

### Missing Triggers
❌ **Problem**: Description doesn't specify when to use skill
```yaml
description: A comprehensive tool for managing documentation
```

✅ **Solution**: Include explicit trigger phrases
```yaml
description: Creates technical specifications. Use when documenting features, requirements, or system designs before implementation.
```

### Invalid Name Format
❌ **Problem**: Wrong naming convention
- `Create_Specs` (underscores, uppercase)
- `creating_specs` (underscores)
- `spec-creator` (not gerund form)

✅ **Solution**: Use gerund form with hyphens
- `creating-specs`
- `reviewing-code`
- `analyzing-data`

## Structural Issues

### Monolithic SKILL.md
❌ **Problem**: Everything in one giant file (>10k tokens)
- Hard to navigate
- High token cost
- Loads unnecessary content

✅ **Solution**: Progressive disclosure with supporting files
```
skill-name/
├── SKILL.md (core, <5k tokens)
└── guidelines/
    ├── topic1.md
    └── topic2.md
```

### Nested References
❌ **Problem**: Files that reference other files
- SKILL.md → details.md → examples.md → templates.md

✅ **Solution**: One level deep only
- SKILL.md → details.md ✓
- SKILL.md → examples.md ✓
- SKILL.md → templates.md ✓

### Windows-Style Paths
❌ **Problem**: Backslashes fail on Unix systems
```markdown
See [scripts\helper.py](scripts\helper.py)
```

✅ **Solution**: Always use forward slashes
```markdown
See [scripts/helper.py](scripts/helper.py)
```

### Unused Bundled Files
❌ **Problem**: Files that are never referenced or accessed
- Adds token bloat (if they were to be loaded)
- Confuses maintenance
- Clutters directory

✅ **Solution**: Only include files that are actually used
- Remove unused files
- Monitor which files Claude accesses
- Delete what's not needed

## Instruction Problems

### Choice Overload
❌ **Problem**: Too many options without guidance
```markdown
You can use library1, library2, library3, or library4. Or maybe library5.
```

✅ **Solution**: Provide one clear default
```markdown
Use library1 for most cases. For advanced scenarios, see [advanced.md](advanced.md).
```

### Over-Explaining Basics
❌ **Problem**: Wasting tokens on what Claude knows
```markdown
Claude is an AI assistant created by Anthropic. As an AI, you process
natural language and can understand code in many programming languages...
```

✅ **Solution**: Trust Claude's knowledge
```markdown
Review the code for common issues.
```

### Inconsistent Terminology
❌ **Problem**: Using different terms for same concept
- "skill" in one place
- "agent capability" in another
- "tool" elsewhere

✅ **Solution**: Pick one term and use consistently
- Use "skill" throughout

### Ambiguous Instructions
❌ **Problem**: Vague or unclear guidance
```markdown
Do the necessary steps to make it work.
Check if it seems okay.
```

✅ **Solution**: Specific, actionable steps
```markdown
1. Validate YAML syntax
2. Check name uses gerund form
3. Verify description includes triggers
```

## Code and Script Issues

### Vague Error Handling
❌ **Problem**: Scripts that fail silently or unhelpfully
```python
try:
    result = do_something()
except:
    pass  # Fails silently
```

✅ **Solution**: Explicit, helpful error messages
```python
try:
    result = validate_yaml(file_path)
except yaml.YAMLError as e:
    print(f"YAML validation failed: {e}")
    sys.exit(1)
```

### Assumed Dependencies
❌ **Problem**: Not specifying required packages
```markdown
Run the script to analyze tokens.
```

✅ **Solution**: Explicit installation instructions
```markdown
## Prerequisites
Install required packages:
```bash
pip install tiktoken pyyaml
```

Then run the script.
```

### Magic Numbers
❌ **Problem**: Configuration values without explanation
```python
timeout = 42  # Why 42?
max_retries = 7  # Why 7?
```

✅ **Solution**: Document or justify all parameters
```python
timeout = 30  # Default HTTP timeout
max_retries = 3  # Balance reliability and performance
```

## Development Process Errors

### Building Without Evaluation
❌ **Problem**: Creating extensive skill without testing
1. Write 500 lines of documentation
2. Include many examples
3. Never test if it actually helps

✅ **Solution**: Evaluation-driven development
1. Create 3 test scenarios
2. Measure baseline performance
3. Build minimal skill to pass tests
4. Iterate based on results

### Not Observing Usage
❌ **Problem**: Never monitoring how skill is used
- Don't check which files are accessed
- Don't track which sections are helpful
- Don't identify unused content

✅ **Solution**: Monitor and refine
- Track file access patterns
- Remove unused content
- Restructure based on real usage

### Time-Sensitive Information
❌ **Problem**: Instructions that expire
```markdown
Use API v1 before August 2025, then switch to API v2.
```

✅ **Solution**: Avoid time-based branching
```markdown
Use API v2 (current stable version).
```

### Skipping Cross-Model Testing
❌ **Problem**: Only testing with Opus
- Skill may not work well with Haiku
- Instructions may be too terse or too verbose

✅ **Solution**: Test with Haiku, Sonnet, and Opus
- Verify skill works across models
- Adjust guidance as needed

## Security Issues

### Untrusted Skills
❌ **Problem**: Installing skills without review
- Download from internet
- Install immediately
- No inspection of code

✅ **Solution**: Always audit before installing
- Read all bundled files
- Check for suspicious code
- Verify tool restrictions
- Review external network calls

## Common Checklist

- [ ] Metadata is specific with triggers
- [ ] Name uses gerund form
- [ ] SKILL.md under 5k tokens
- [ ] No nested file references
- [ ] Forward slashes in all paths
- [ ] No unused bundled files
- [ ] Single default approach (not many options)
- [ ] Consistent terminology throughout
- [ ] Specific, actionable instructions
- [ ] Error handling is explicit
- [ ] Dependencies documented
- [ ] Configuration values justified
- [ ] Tested across models
- [ ] Evaluation-driven development followed
- [ ] No time-sensitive branching
- [ ] Security reviewed (if external)
