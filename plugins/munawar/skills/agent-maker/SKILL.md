---
name: "m:agent-maker"
description: Create Claude Code agents using production-tested patterns and techniques
argument-hint: "[agent-name-or-description]"
model: opus
---

# Agent Maker

Build a Claude Code agent based on: **$ARGUMENTS**

This skill is your playbook for creating agents that work reliably when launched by a main orchestrator via the Task tool. Every pattern here comes from production agents — techniques that survived real use and earned their place.

Read through the patterns, then apply them to build the requested agent.

---

## How Agents Work (The Mental Model)

An agent is a markdown file with YAML frontmatter. When the main Claude session launches a subagent via the Task tool, two things form the subagent's instructions:

1. **The `description` field** from frontmatter — injected as part of the agent's system-level context
2. **The prompt** the main agent writes when calling the Task tool

The description is durable. The prompt is improvised. This asymmetry is the foundation of every pattern below.

---

## Agent File Structure

```
agents/
└── my-agent.md
```

### Frontmatter

```yaml
---
name: my-agent
description: "One paragraph that defines the agent's purpose, constraints, and examples."
model: haiku|sonnet|opus
color: green|yellow|orange|cyan|purple
tools: Tool1, Tool2, Tool3  # optional whitelist
---
```

| Field | Purpose |
|-------|---------|
| `name` | Agent identifier — the main session references this via `subagent_type` |
| `description` | The most important field. See Pattern 1. |
| `model` | `haiku` for lightweight/fast, `sonnet` for balanced, `opus` for deep reasoning |
| `color` | Visual tag in the UI |
| `tools` | Optional tool whitelist — restricts what the agent can call |

### Body

Everything after the frontmatter `---` is the agent's system prompt. This is where detailed workflow instructions, phase definitions, and output format specs live.

---

## The Patterns

### Pattern 1: Description as Shield

**The most important technique.** The `description` field survives intact into the subagent's context regardless of what prompt the main agent sends. Use it to embed non-negotiable rules that the caller's prompt cannot override.

Put behavioral contracts, hard constraints, and "MUST NOT" rules in the description. The body can be overridden by a creative prompt — the description cannot.

```yaml
# From pr-reader-alt-agent:
description: "Skill invocation agent for fetching GitHub PR comments via the
  /pr-reader skill workflow. Invokes the Skill tool with skill='m:pr-reader'
  — does NOT fetch PR data itself."
```

The description says "does NOT fetch PR data itself" — so even if a caller's prompt says "fetch the PR comments using gh," the agent's own description contradicts it. The agent follows its description.

**When to use:** Any time the agent has a specific job boundary that callers might accidentally blur.

---

### Pattern 2: Caller Instructions in the Description

The description isn't just for the subagent — it's also read by the **main agent** deciding whether and how to launch it. Embed caller-facing instructions directly in the description so the orchestrator knows how to construct a good prompt.

```yaml
# From issue-qc:
description: "...IMPORTANT: When launching this agent with a file path,
  your Task prompt MUST instruct it to edit the file in-place using the
  Edit tool — do NOT tell it to 'return' findings as text."
```

This tells the caller: "When you launch me, phrase your prompt this specific way." The main agent reads this before writing the Task prompt and follows the instruction.

**When to use:** When the agent needs its input formatted a particular way, or when callers commonly make the same mistake.

---

### Pattern 3: Examples in the Description

Include `<example>` blocks in the description to show the main agent exactly when and how to invoke this agent. These serve double duty — they help the orchestrator pattern-match user requests to the right agent, and they demonstrate proper prompt construction.

```yaml
# From bugfix:
description: "...
  <example>
  Context: A senior engineer has left comments about a race condition.
  user: \"There's a race condition in the WebSocket handler...\"
  assistant: \"I'll launch the bug-fix-engineer agent to investigate...\"
  <commentary>
  Since the user described a specific bug with engineer-level detail,
  use the Task tool to launch the bug-fix-engineer agent.
  </commentary>
  </example>"
```

**When to use:** Always, for any non-trivial agent. Three examples is the sweet spot.

---

### Pattern 4: Proxy Agent (Agent-Wraps-Skill)

When the real logic lives in a skill, create a thin agent whose only job is to invoke that skill. Skills can't be launched as subagents directly — the proxy bridges the gap.

**The prompt alignment problem:** Subagents weight the caller's prompt more heavily than their system prompt. If the raw user message is trivially answerable ("whats today"), smaller models will answer literally and never call the Skill tool. The fix is forcing the caller to rewrite the prompt so the only sensible response is a tool call.

**Three mandatory pieces for every proxy agent:**

**1. CALLER INSTRUCTIONS in the description** — tells the main agent how to write the prompt:
```yaml
description: "...
  CALLER INSTRUCTIONS — how to write the prompt:
  The prompt MUST begin with 'Invoke the {skill} skill for:' followed by
  the user's intent. This framing ensures the subagent calls the Skill tool
  instead of answering literally. Do NOT forward the user's raw message
  as a bare question."
```

**2. Examples showing the prompt transformation** — in the description:
```yaml
description: "...
  - user: \"What's on my plate today?\"
    <launches agent with prompt: \"Invoke the todoist-v2 skill for: whats today\">
  - user: \"Reschedule overdue tasks\"
    <launches agent with prompt: \"Invoke the todoist-v2 skill for: reschedule overdue tasks\">"
```

**3. CRITICAL RULES in the body** — the non-negotiable gate:
```markdown
## CRITICAL RULES
1. You MUST use the Skill tool with `skill: "{skill}"` as your FIRST action.
2. Pass the caller's instructions as the `args` parameter.
3. You MUST NOT answer the user's question yourself.
4. You MUST NOT use MCP tools or call APIs directly.
5. After the skill executes, relay its output back concisely.
```

Without all three pieces, the agent will intermittently fail — especially on haiku/sonnet with short prompts.

**When to use:** When a skill already does the work and you need it callable as a subagent from orchestration flows.

---

### Pattern 5: Model Selection

Match the model to the cognitive load:

| Model | Cost | Use For | Example Agent |
|-------|------|---------|---------------|
| `haiku` | Low | Mechanical tasks, parsing, formatting, running commands | `diff-parser` |
| `sonnet` | Medium | Balanced tasks with some judgment | `pr-reader-alt-agent` |
| `opus` | High | Deep reasoning, code analysis, multi-step investigation | `issue-qc`, `bugfix`, `pr-comment-qc` |

Rule of thumb: if the agent needs to *understand* code, use `opus`. If it just needs to *run* something and format output, use `haiku`.

---

### Pattern 5b: Portable Script Paths

When an agent references bundled scripts or resources, use `${CLAUDE_PLUGIN_ROOT}` for all paths. Claude Code substitutes this at runtime with the plugin's actual install directory.

```markdown
# In agent body — portable:
Run the validation script:
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py "$FILE"

# NOT portable (breaks when installed as plugin):
python3 ~/.claude/agents/my-agent/scripts/validate.py "$FILE"
```

This applies to any path in bash commands, script references, or resource file paths within agent markdown files.

---

### Pattern 6: Tool Whitelisting

Restrict what an agent can do by listing only the tools it needs. This prevents scope creep and accidental side effects.

```yaml
# From diff-parser — only gets read/search tools plus Bash for git:
tools: Bash, Glob, Grep, Read, WebFetch, WebSearch

# From ui-checker — only gets Playwright + file tools:
tools: mcp__plugin_playwright_playwright__browser_navigate,
  mcp__plugin_playwright_playwright__browser_take_screenshot,
  Bash, Read, Write, Glob, Grep
```

If you don't specify `tools`, the agent gets everything. Be explicit when the agent should stay in its lane.

---

### Pattern 7: Phased Workflow with Gates

Structure complex agents as sequential phases with explicit checkpoints. This prevents the agent from jumping ahead and ensures human oversight at critical moments.

```
# From bugfix:
Phase 1: Investigation (read code, trace paths, verify root cause)
Phase 2: Fix Proposal (present plan, ask for approval)
   ← GATE: "Do NOT proceed until you receive explicit approval"
Phase 3: Implementation (only after approval)
```

The gate is a hard stop. Write it as an imperative rule, not a suggestion:
- "Do NOT proceed with any code changes until you receive explicit approval."
- "This is non-negotiable."

**When to use:** Any agent that modifies code or takes irreversible actions.

---

### Pattern 8: Parallel Fan-Out

Agents that investigate multiple concerns should launch parallel sub-tasks, not work sequentially. Instruct the agent to use the Task tool for parallelism.

```
# From issue-qc:
For each distinct issue or concern:
1. Identify what needs to be traced
2. Create a focused investigation task
3. Launch multiple exploration tasks in parallel using the Task tool
```

For orchestrator skills that launch multiple agents:

```
# From issues-fix:
Launch all agents within a phase in parallel — do not wait for any agent
in the phase to finish before launching the next agent in that phase.
DO wait for all agents in a phase to complete before starting the next phase.
```

**When to use:** Investigation agents, QC agents, any agent handling a list of independent items.

---

### Pattern 9: In-Place Edit Pattern

Instead of returning findings as text, have the agent edit the source file directly with annotations. This keeps the results co-located with the context they reference.

```
# From issue-qc:
Mark up the file in-place with `QC_BOT_COMMENTS:` annotations
- Example: `# QC_BOT_COMMENTS: ✅ BUG — confirmed, line 45 passes None`
- Example: `# QC_BOT_COMMENTS: ❌ NOT A BUG — upstream validator ensures non-empty input`
```

**When to use:** QC agents, review agents, any agent that evaluates items listed in a file.

---

### Pattern 10: Template Prompts for Sub-Agents

When a skill or agent launches other agents, include the exact prompt template. Don't let the launcher improvise — give it a fill-in-the-blanks template.

```
# From issues-eval:
Each agent prompt MUST follow this template exactly:

  Investigate this PR review concern:
  **PR_Comments_File:** <absolute path to $ARGUMENTS>
  **PR_Comment_Issue_Line(s):** <line numbers>
  **Concern:** <the reviewer's comment text>

  IMPORTANT: You MUST use the Edit tool to annotate the PR_Comments_File
  in-place...
```

**When to use:** Any skill or agent that orchestrates sub-agents. The template prevents drift.

---

### Pattern 11: Circuit Breaker / QC Gate

Before doing expensive work, check a precondition. If it fails, stop and tell the user what to do first.

```
# From issues-fix:
## Step 0: QC Gate (Circuit Breaker)

Check whether the file contains any `QC_BOT_COMMENTS:` annotations.

- If NO annotations found: STOP immediately. Tell the user:
  "This file has not been QC-annotated yet. Run `/m:issues-eval` first..."
- If annotations ARE found: Proceed to Step 1.
```

**When to use:** When the agent depends on output from a prior stage in a pipeline.

---

### Pattern 12: Persona with Teeth

Give the agent a specific role identity, but make it functional — it should change how the agent thinks, not just how it introduces itself.

```
# From issue-qc:
You are an elite Quality Control Investigation Specialist — a senior
software engineer with deep expertise in debugging, code archaeology,
and systematic root cause analysis.

# From pr-comment-qc:
You are an elite code review quality controller — a senior principal
engineer who has reviewed thousands of PRs... Your role is NOT to review
the code yourself, but to audit the quality of reviewer comments.
```

The persona defines the *lens* through which the agent analyzes. "Quality controller" means it evaluates others' work, not does the work itself. "Bug-fix engineer" means it traces root causes, not surface symptoms.

---

### Pattern 13: Agent Memory

For agents that run repeatedly across conversations, instruct them to write persistent notes about what they discover. This builds institutional knowledge.

```
# From bugfix:
**Update your agent memory** as you investigate and fix bugs.
Examples of what to record:
- Common bug patterns in specific modules
- Code areas with known fragility
- Architectural decisions that constrain fix approaches
- Test coverage gaps
```

**When to use:** Investigation agents, QC agents, any agent that builds understanding of a codebase over time.

---

### Pattern 14: Side Effects as Full-Fidelity Output

When a subagent returns to the main agent, its response gets aggressively summarized. This is baked into how Claude handles agent-to-agent communication — the subagent's full work product gets compressed into a brief summary. You lose detail, nuance, and raw data.

The escape hatch: **have the agent write its real output to a file as a side effect.** The summary back to the caller becomes a pointer ("results written to X"), while the full uncompressed work product lives on disk where it can be read in full by the next stage, another agent, or the user.

```
# From pr-reader:
Your final message should contain ONLY:
1. The file path where comments were saved
2. A short summary (3-8 bullet points)

Do NOT paste the full verbatim comment text into your final message — it's in the file.
```

This naturally enables **pipeline composition** — agents that chain together, each consuming the previous stage's output file:

```
/m:pr-reader → writes .scratch/outputs/pr-N-comments.md
    ↓
/m:issues-eval → reads that file, launches m:issue-qc agents,
                  annotates file in-place with QC_BOT_COMMENTS
    ↓
/m:issues-fix → reads annotated file, launches m:bugfix agents
                 in phased batches
```

Each stage has a clear contract: what file it reads, what it produces, what format it uses. The file IS the interface — not the agent's return message. Design your agent to accept a file path and produce a file path.

**When to use:** Any agent whose output matters beyond the immediate conversation. If a downstream agent, skill, or human needs the full uncompressed result, write it to disk.

---

## Creation Checklist

When building a new agent, work through this:

1. **Define the job boundary.** What does this agent do? Where does it stop?
2. **Write the description first.** Put the behavioral contract, caller instructions, and examples here. This is the most important part.
3. **Choose the model.** Match cognitive load to cost.
4. **Whitelist tools.** Only give the agent what it needs.
5. **Structure the body as phases.** Investigation → Analysis → Output. Add gates where needed.
6. **Define output as side effects.** Write the real work product to a file. Return a summary and file path to the caller.
7. **Write examples.** Show the main agent when and how to invoke this one.
8. **Test the description.** Read it as if you're the main agent deciding whether to launch this subagent. Does it tell you everything you need?
9. **Consider the pipeline.** Does this agent consume another agent's output? Does another agent consume this one's output?

---

## Your Task

**$ARGUMENTS**

### Routing: read the user instruction first

- **Custom objective**: If the user's instruction is something other than creating a new agent (e.g. reviewing an existing agent against the patterns, diagnosing why an agent misbehaves, applying a specific pattern to an existing agent, asking which pattern fits a situation, refactoring an agent's description), use the 14 patterns and creation checklist above to achieve their objective directly. You are not bound to the creation steps.

- **Default workflow** (when the user wants a new agent built, or when no specific instruction is provided): Follow the creation steps below.

### Creation Steps

1. Determine the agent's purpose and job boundary
2. Select appropriate patterns from the playbook above
3. Write the description field first (Pattern 1, 2, 3)
4. Choose model and tools (Pattern 5, 6)
5. Write the body with phased workflow (Pattern 7)
6. Define side-effect output (Pattern 14)
7. Write the agent file to the appropriate location

If the request is ambiguous, ask clarifying questions. Otherwise, build the agent.
