# Workflow Patterns Guide

## Pattern A: Simple Linear Workflow

**Best for:** Straightforward tasks with clear sequential steps

```markdown
## Workflow

1. **First Step**: Action to take
2. **Second Step**: Next action
3. **Third Step**: Final action
```

**Example:**
```markdown
## Creating Basic Skill

1. **Create Directory**: `mkdir .claude/skills/skill-name/`
2. **Write SKILL.md**: Add YAML frontmatter and content
3. **Validate**: Check YAML syntax
4. **Test**: Invoke skill and verify behavior
```

## Pattern B: Conditional Workflow

**Best for:** Tasks with different paths based on context

```markdown
## Workflow

1. **Detect Context**: Check current state
2. **Branch Based on Context**:
   - **If condition A**: Follow workflow A
   - **If condition B**: Follow workflow B
3. **Execute Selected Workflow**
```

**Example:**
```markdown
## Choosing Skill Location

1. **Determine Scope**:
   - **If personal use only**: Use `~/.claude/skills/`
   - **If team-shared**: Use `.claude/skills/`
2. **Create Directory**: Create in chosen location
3. **Proceed with Implementation**
```

## Pattern C: Validation Loop

**Best for:** Quality-critical tasks requiring iteration

```markdown
## Workflow

1. **Initial Implementation**: Create first draft
2. **Validation**: Check for errors
3. **Feedback Loop**:
   - If issues found:
     - Document issues
     - Apply fixes
     - Return to step 2
   - If validation passes:
     - Proceed to step 4
4. **Completion**: Finalize
```

**Example:**
```markdown
## Frontmatter Creation

1. **Write YAML**: Create initial frontmatter
2. **Validate Syntax**: Run YAML parser
3. **Check Quality**:
   - If errors found:
     - Fix YAML syntax
     - Return to step 2
   - If validation passes:
     - Check name format (gerund form)
     - Check description includes triggers
4. **Finalize**: Save validated frontmatter
```

## Pattern D: Multi-Phase with Checklists

**Best for:** Complex tasks with multiple stages

```markdown
## Workflow

### Phase 1: Preparation
- [ ] Prerequisite 1
- [ ] Prerequisite 2
- [ ] Prerequisite 3

### Phase 2: Implementation
- [ ] Core task 1
- [ ] Core task 2
- [ ] Core task 3

### Phase 3: Validation
- [ ] Test 1
- [ ] Test 2
- [ ] Finalize
```

**Example:**
```markdown
## Creating Complex Skill

### Phase 1: Planning
- [ ] Identify capability gap
- [ ] Create test scenarios
- [ ] Determine file structure
- [ ] Choose storage location

### Phase 2: Structure
- [ ] Create skill directory
- [ ] Write YAML frontmatter
- [ ] Validate metadata
- [ ] Create supporting files

### Phase 3: Implementation
- [ ] Write core workflow
- [ ] Add examples
- [ ] Create helper scripts
- [ ] Reference guidelines

### Phase 4: Testing
- [ ] Test with Haiku
- [ ] Test with Sonnet
- [ ] Test with Opus
- [ ] Refine based on results
```

## Pattern E: Iterative Section-by-Section

**Best for:** Large tasks requiring approval at each stage

```markdown
## Workflow

For each section:
1. **Propose Content**: Draft section
2. **Get Approval**: User reviews and approves
3. **Implement**: Write final content
4. **Commit**: Save progress
5. **Move to Next Section**
```

**Example:**
```markdown
## Implementing Skill Content

### Sections to Complete:
1. Purpose and When to Use
2. Prerequisites
3. Core Workflow
4. Best Practices
5. Examples

### For Each Section:
1. **Draft**: Write proposed content
2. **Review**: Present to user for approval
3. **Refine**: Adjust based on feedback
4. **Implement**: Write final version
5. **Commit**: Git commit with message
6. **Continue**: Move to next section
```

## Pattern F: Parallel Tasks with Convergence

**Best for:** Independent tasks that come together

```markdown
## Workflow

### Parallel Stream A:
1. Task A1
2. Task A2

### Parallel Stream B:
1. Task B1
2. Task B2

### Convergence:
1. Combine results from A and B
2. Finalize
```

**Example:**
```markdown
## Creating Skill with Scripts

### Documentation Stream:
1. Write YAML frontmatter
2. Write main SKILL.md content
3. Create guideline files

### Script Stream:
1. Write validation script
2. Write token counter
3. Test scripts independently

### Integration:
1. Reference scripts in SKILL.md
2. Test complete skill
3. Validate all components work together
```

## Choosing the Right Pattern

**Simple Linear:**
- Clear sequential steps
- No branching needed
- Example: Basic file creation

**Conditional:**
- Multiple valid approaches
- Context determines path
- Example: Choosing between personal vs project skill

**Validation Loop:**
- Quality-critical operations
- May need multiple attempts
- Example: YAML syntax validation

**Multi-Phase Checklists:**
- Complex multi-stage tasks
- Progress tracking important
- Example: Full skill creation lifecycle

**Iterative Section-by-Section:**
- Large tasks requiring approval
- User collaboration needed
- Example: Writing comprehensive documentation

**Parallel with Convergence:**
- Independent tasks that integrate
- Efficiency through parallelization
- Example: Creating skill with separate docs and scripts

**Important:** Once you've selected a workflow pattern, confirm with the user that they're happy with the choice before proceeding.

## Best Practices

✅ **Clear progression**: Each step builds on previous
✅ **Verifiable outcomes**: Know when step is complete
✅ **Error handling**: What to do when things fail
✅ **Progress tracking**: Use checkboxes or numbered steps
✅ **Validation points**: Check quality before proceeding
✅ **Appropriate granularity**: Not too detailed, not too vague

## Anti-Patterns

❌ **Too many options**: "Do A or B or C or D or E"
❌ **Unclear order**: Steps could be done in any order (when sequence matters)
❌ **Missing validation**: No quality checkpoints
❌ **Overly detailed**: Step-by-step for trivial operations
❌ **Skipping error cases**: No guidance for failures
