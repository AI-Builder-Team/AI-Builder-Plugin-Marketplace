---
name: creating-specs
description: Guides users through creating comprehensive technical specifications using spec-driven development methodology. Use when users need to document features, requirements, or system designs before implementation. Helps structure specifications with proper sections, requirements, and technical details.
---

# Creating Technical Specifications

This skill guides you through creating comprehensive technical specifications following spec-driven development best practices. You'll receive a complete, well-structured spec document that aligns stakeholders before implementation begins. The process is highly collaborative—the agent will discuss each section with you to understand requirements, get your approval, then write it to the spec file before moving to the next section.

## When to Use This Skill

Use this skill when users need to create a technical specification, write a feature spec, document requirements, draft a design doc, or formalize a project proposal. Specifications created by this skill are stored within feature folders at `features/<domain>/<feature-id>/specs/`.

## Spec Format

This skill generates comprehensive technical specifications with the following characteristics:

- **Metadata Format**: Status, Created, Last Updated, Owner
- **Horizontal Rules**: `---` separators between major sections
- **Detailed Subsections**: Technical Design has rich subsections (Files to Reference, Files to Modify, Data Flow)
- **FR Labeling**: Functional Requirements use FR1, FR2... format
- **Separate Checklist**: Implementation checklist in `checklist.md` file
- **tmp/ Folder**: Section drafts stored temporarily in `features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp/`
- **spec-research.md**: Research stored at spec level in `features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec-research.md`
- **Spec Numbering**: Specs are automatically numbered (01, 02, 03, etc.) based on implementation order

**IMPORTANT**: Do NOT read other existing specs in the repository. There are varying standards and approaches being tested. ONLY follow the template in `template.txt` for structure and guidelines.

## Workflow

### Step 1: Locate Feature & Setup

**IMPORTANT: Features must exist before specs can be created. Use the feature-workflow skill to create features first.**

1. **Locate Existing Feature**
   - Read `features/index.md` to get list of domains
   - Present domains as a numbered, comma-separated list (e.g., "1. Admin, 2. Renewals, 3. Budget Bot, ...")
   - Ask user to select a domain by number
   - List existing features in the selected domain: `ls features/<domain-folder>/`
   - If no features exist, inform user: "No features found in this domain. Please create a feature first using the feature-workflow skill."
   - Ask user to select a feature OR create one first
   - Verify feature has `FEATURE.md` file: Check if `features/<domain>/<feature-id>/FEATURE.md` exists
   - If FEATURE.md is missing, warn user: "FEATURE.md not found. The feature folder may be corrupted. Do you want to proceed anyway?"

2. **Determine Spec Number and Name**
   - List existing specs in `features/<domain>/<feature-id>/specs/`
   - Extract numbers from folders matching pattern `^\d{2}-` (e.g., `01-`, `02-`)
   - Find the highest number (ignore unnumbered folders)
   - Calculate next number: `highest + 1`, zero-padded to 2 digits (e.g., `01`, `02`, ... `99`)
   - If no numbered specs exist, start with `01`
   - Ask user: "What should this spec be named?"
   - Examples: `phase-1-0-foundation`, `accordion-refactor`, `api-integration`
   - Convert to kebab-case if needed
   - Final spec folder name: `<number>-<spec-name>` (e.g., `04-accordion-refactor`)
   - Check for duplicate: Verify `features/<domain>/<feature-id>/specs/<number>-<spec-name>/` doesn't exist
   - If duplicate exists, ask user for alternative name

3. **Confirm Spec Location**
   - Inform user of the numbered spec folder: "This will be spec #<number>."
   - Confirm with user: "I'll create the spec in `features/<domain>/<feature-id>/specs/<number>-<spec-name>/`. Proceed?"

4. **Create Directory Structure**
   ```bash
   mkdir -p features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp
   ```

5. **Initialize `spec.md` with metadata**
   - Run `gh api user --jq '.login'` to get the current user's GitHub ID for the Owner field
   - Create `features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec.md` with title and metadata:
   ```md
   # [Spec Name from user]

   **Status:** Draft
   **Created:** [Today's date YYYY-MM-DD]
   **Last Updated:** [Today's date YYYY-MM-DD]
   **Owner:** [GitHub ID from gh api user command]

   ---
   ```

### Step 2: Feature Research

**Check if research has already been provided by the user.**

**Option A: Research Already Provided**

If the user has already provided feature research (e.g., in a file, in their message, or from a previous exploration session):

1. Use the provided research directly - do NOT re-research
2. Copy or summarize the provided research into `features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec-research.md` for reference
3. Proceed to Step 3

**Option B: No Research Provided - Conduct Research Directly**

If no research has been provided, conduct the research yourself using Glob, Grep, and Read tools:

1. **Find relevant files and patterns**:
   - Use Glob to locate files related to the feature area
   - Use Grep to search for similar functionality, patterns, or keywords
   - Read key files to understand existing implementations

2. **Identify similar implementations**:
   - Look for features with similar UI patterns, data flows, or business logic
   - Note which components, hooks, or utilities are commonly used

3. **Map dependencies and integration points**:
   - Identify API endpoints, services, or data sources involved
   - Note any shared state, contexts, or stores

4. **Document findings** in `features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec-research.md`:
   - Existing patterns and conventions to follow
   - Similar features that can serve as reference
   - Key files and integration points
   - Dependencies and technical constraints

### Step 3: Initial Clarifications

Based on the research, identify any HIGH-LEVEL clarifications needed:
- Questions about business logic and requirements
- Scope boundaries and priority
- Technical approach and architecture decisions
- Integration points and dependencies

**DO NOT ask about**:
- Visual design details (colors, fonts, spacing)
- UI/UX specifics (button placement, animations)
- Implementation minutiae (variable names, file structure)

These details should be deferred to the implementation phase.

### Step 4: Parallel Draft Creation

**Create all section drafts at once using parallel Task calls.**

Launch 4 parallel general-purpose agents (one per section) using a SINGLE message with 4 Task tool calls:

**Agent 1: Overview Draft**
```
- subagent_type: "general-purpose"
- model: "haiku"
- description: "Draft Overview section"
- prompt: "Read features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec-research.md. Based on the research and our discussion about [feature], draft the Overview section following the template in .claude/skills/creating-specs/template.txt. Write your draft to features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp/overview.md. Be concise and cover what is being built and how it works. Do NOT include a paragraph explaining why the implementation is needed or its benefits. Return 'DONE' when complete."
```

**Agent 2: Out Of Scope Draft**
```
- subagent_type: "general-purpose"
- model: "haiku"
- description: "Draft Out Of Scope section"
- prompt: "Read features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec-research.md. Based on the research and our discussion about [feature], draft the Out Of Scope section following the template in .claude/skills/creating-specs/template.txt. Write your draft to features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp/out-of-scope.md. Include numbered items with rationale for each exclusion. Be concise - cover only what's needed. Return 'DONE' when complete."
```

**Agent 3: Functional Requirements Draft**
```
- subagent_type: "general-purpose"
- model: "haiku"
- description: "Draft Functional Requirements section"
- prompt: "Read features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec-research.md. Based on the research and our discussion about [feature], draft the Functional Requirements section following the template in .claude/skills/creating-specs/template.txt. Write your draft to features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp/requirements.md. Use FR1/FR2/FR3 format. Each FR MUST include a Success Criteria. Be concise - cover only what's needed. Return 'DONE' when complete."
```

**Agent 4: Technical Design Draft**
```
- subagent_type: "general-purpose"
- model: "haiku"
- description: "Draft Technical Design section"
- prompt: "Read features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec-research.md. Based on the research and our discussion about [feature], draft the Technical Design section following the template in .claude/skills/creating-specs/template.txt. Write your draft to features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp/technical-design.md. Include subsections: Files to Reference, File(s) to Modify, Data Flow. Return 'DONE' when complete."
```

**After all 4 agents complete:**
- Inform user that initial drafts are ready for review
- Proceed to sequential approval process

### Step 5: Sequential Section Approval (STRICTLY ENFORCED)

**CRITICAL: Review sections in this EXACT order. Do NOT skip ahead.**

**Section Order:**
1. Overview
2. Out Of Scope
3. Functional Requirements
4. Technical Design

**For EACH section (in order):**

1. **Present Draft**: Read `tmp/<section>.md` and present to user
   - Format: Show the full section content
   - Say: "Here's the draft for the [Section Name] section. Please review and provide feedback."

2. **Iterate Until Approved**:
   - Listen to user feedback
   - Make changes to `tmp/<section>.md` as requested
   - Present updated version
   - Repeat until user explicitly approves (user says "approved", "looks good", "move on", etc.)

3. **Write to Main Spec**:
   - Once approved, append the section to `features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec.md`
   - Add horizontal rule (`---`) after the section (except for last section)

4. **Check for Understanding Changes** (Self-Reflection):
   - Based on user feedback and changes made during this section's review, reflect on whether the conversation has revealed new information that affects the remaining draft sections
   - If YES: Inform user which sections need updates, regenerate those drafts in tmp/, then proceed to next section
   - If NO: Proceed to next section without comment

5. **State Tracking**:
   - Keep track of which section you're currently reviewing
   - Refuse to skip ahead if user tries to jump to a later section
   - Say: "Let's finish reviewing [Current Section] first before moving to [Later Section]."

**Enforcement Example:**
```
[Currently reviewing Overview]
User: "Let's skip to Technical Design"
Assistant: "Let's finish reviewing the Overview section first before moving to Technical Design. Are you ready to approve the Overview, or would you like to make changes?"
```

### Step 6: Generate Implementation Checklist

**After all sections are approved and written to spec.md:**

1. Read the final `features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec.md`

2. Generate comprehensive `checklist.md` based on:
   - **Requirements**: Extract all FR1-FRN items
   - **Technical Design**: Extract implementation tasks from Files to Modify
   - **Do NOT include**: Testing items (unit tests, integration tests, manual testing)

3. Format checklist as:
   ```md
   # Implementation Checklist

   ## Data Layer
   - [ ] [Task from requirements or technical design]

   ## Business Logic
   - [ ] [Task from requirements or technical design]

   ## UI/UX
   - [ ] [Task from requirements or technical design]

   ## Code Quality
   - [ ] Run type checker and fix all errors
   - [ ] Follow existing code patterns
   ```

4. Write to `features/<domain>/<feature-id>/specs/<number>-<spec-name>/checklist.md`

### Step 7: Cleanup & Finalization

1. **Ask about tmp/ folder**:
   - Say: "The spec is complete! Would you like me to keep or delete the `tmp/` folder with section drafts?"
   - Options:
     - **Keep**: Leave `features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp/` as-is for reference
     - **Delete**: Remove `features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp/` entirely

2. **Execute user's choice**:
   - If delete: `rm -rf features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp`
   - If keep: Do nothing

3. **Summary**:
   - Confirm spec location: `features/<domain>/<feature-id>/specs/<number>-<spec-name>/spec.md`
   - Confirm checklist location: `features/<domain>/<feature-id>/specs/<number>-<spec-name>/checklist.md`
   - Mention tmp/ status (kept or deleted)
   - Note: FEATURE.md Changelog will be updated in Step 7.5

### Step 7.5: Update FEATURE.md Changelog

**After spec and checklist are complete, automatically update the feature's Changelog.**

1. **Read FEATURE.md**
   - Read `features/<domain>/<feature-id>/FEATURE.md`
   - Locate the "## Changelog of Feature Specs" section
   - If section doesn't exist, warn user and skip this step

2. **Prepare Changelog Entry**
   - Format: `| {YYYY-MM-DD} | [<number>-<spec-name>](specs/<number>-<spec-name>/spec.md) | {Brief description} |`
   - Ask user: "What brief description should I add to the FEATURE.md Changelog for this spec?"
   - Alternative: Auto-generate from spec Overview section (extract first sentence)
   - Use today's date in YYYY-MM-DD format
   - Include the spec number in both the link text and URL

3. **Update FEATURE.md**
   - Add new row to the Changelog table
   - Determine chronological order by examining existing entries (oldest first or newest first)
   - Insert new entry following the existing pattern
   - If table is empty, add the new entry as the first data row (after header row)

4. **Verify Update**
   - Confirm to user: "Updated FEATURE.md Changelog with link to spec #<number>"
   - Show the added entry for user verification

**Example Changelog Entry:**
```
| 2025-12-15 | [04-phase-1-0-foundation](specs/04-phase-1-0-foundation/spec.md) | Implement foundation for table refactoring |
```

## Key Sections

See `template.txt` for the complete spec template with guidelines and examples for each section. The template includes 5 core sections:

1. **Title & Metadata**: Status, Created, Last Updated, Owner
2. **Overview**: Description of what is being built and how it works
3. **Out Of Scope**: What is explicitly not included with rationale
4. **Functional Requirements**: Requirements (FR1-FRN) with success criteria
5. **Technical Design**: Files to reference/modify, data flow, edge cases

## Important Notes

- **Spec numbering is automatic** - specs are numbered sequentially (01, 02, 03, etc.) based on implementation order
- **Always use tmp/ folder** for section drafts within the spec directory at `features/<domain>/<feature-id>/specs/<number>-<spec-name>/tmp/`
- **Store research at spec level** as `spec-research.md`, not in tmp/
- **Always verify feature exists** before creating spec - use feature-workflow skill to create features first
- **Always ask user for spec location confirmation** before creating directories
- **Always update FEATURE.md Changelog** after spec completion (Step 7.5) with numbered spec link
- **Strictly enforce sequential review** - never skip ahead to later sections
- **Generate checklist from final spec** - don't create it upfront
- **Ask about tmp/ cleanup** - don't assume user wants it deleted
- **Use horizontal rules** (`---`) to separate major sections
- **Use FR labeling** for functional requirements (FR1, FR2, FR3, etc.)
- **Be concise** - cover only what needs to be covered, no prescribed lengths
