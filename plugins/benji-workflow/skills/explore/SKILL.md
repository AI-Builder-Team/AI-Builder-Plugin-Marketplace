---
name: explore
description: Spawns an Agent Team for divergent exploration of a problem space. Multiple teammates investigate in parallel, debate findings, and converge on a brief that feeds into /research. Use before /research when a problem needs multi-perspective discovery.
argument-hint: [problem description or feature path]
disable-model-invocation: true
allowed-tools:
  - Teammate
  - Task
  - SendMessage
  - TaskCreate
  - TaskList
  - TaskGet
  - TaskUpdate
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
color: Violet
---

# Explore Skill

## Purpose

Divergent, multi-perspective exploration of a problem space using Agent Teams. Spawns a team of specialized teammates who investigate in parallel, share findings, challenge each other's assumptions, and converge on an exploration brief.

**This is the "cast a wide net" phase** — surfacing options, tradeoffs, unknowns, and risks before `/research` formalizes them into specs.

## Pipeline Position

```
/explore → /research → /orchestrate → /spec → /implement
   ↑            ↑
 divergent    convergent
 (team)       (single agent)
```

`/explore` produces an `exploration-brief.md` that gives `/research` a sharper starting point — less back-and-forth, fewer surprises, better-informed architecture decisions.

## When to Use

- Starting work on a feature where the design space is wide
- Investigating a problem with multiple viable approaches
- Needing to understand both codebase constraints AND external options
- When a single-agent exploration would miss important angles

## When NOT to Use

- Bug fixes or small enhancements (just use `/research` directly)
- Well-understood problems with obvious solutions
- Work that's already been explored and just needs formalization

## Inputs

The user's input is available as `$ARGUMENTS`. This may contain:

- **Problem description** (required) — natural language description of what to explore
- **Feature path** (optional) — `features/{domain}/{feature}/`
- **Custom roles** (optional) — e.g., "Roles: CRDT specialist, WebSocket architect"

Example invocations:
```
/explore Add real-time collaboration to the document editor
/explore features/collab/real-time-editing Add real-time collaboration
/explore Add caching layer. Roles: performance analyst, DBA, API architect
```

## Outputs

- `exploration-brief.md` in the feature directory (or user-specified location)
- Populated with team findings, debate outcomes, and recommended approach

---

## Workflow

### Step 1: Understand the Request

Parse `$ARGUMENTS` to extract:

1. **Problem description** — what are we exploring?
2. **Feature path** — if a path like `features/...` is present, use it; otherwise ask or infer
3. **Custom roles** — if the user specified roles (e.g., "Roles: ..."), use those; otherwise use defaults

If the problem is unclear, use `AskUserQuestion` to clarify scope and goals. Keep it brief — this is exploration, not requirements gathering.

### Step 2: Set Up Feature Directory

If a feature path was provided or can be inferred:

```
features/{domain}/{feature}/
```

Create the directory if it doesn't exist. This is where `exploration-brief.md` will land.

If the user hasn't committed to a feature path yet, ask:

```
AskUserQuestion: "Where should I save the exploration brief?"
Options:
  - Suggest a path based on the problem description
  - Let user specify
  - Use scratchpad (temporary, user copies later)
```

### Step 3: Spawn the Agent Team

Create the team using the Teammate tool:

```
Teammate:
  operation: spawnTeam
  team_name: explore-{feature-name}
  description: "Exploring: {problem summary}"
```

### Step 4: Create Exploration Tasks

Create tasks for the shared task list. These give teammates structure while allowing organic discovery.

**Default tasks** (adjust based on problem):

1. **Codebase Analysis** — Explore existing architecture, patterns, constraints, and integration points relevant to this problem
2. **External Research** — Investigate approaches, libraries, prior art, and industry patterns for solving this problem
3. **Critical Review** — Challenge assumptions from tasks 1 and 2, identify risks, surface what might go wrong
4. **Cross-Pollination** — (Unassigned) After initial findings, teammates message each other to debate and refine
5. **Convergence** — (Blocked by 1-4) Synthesize findings into recommended approach

Tasks 1-3 are assigned to teammates at spawn. Task 4 is organic (happens via messaging). Task 5 is for the lead.

### Step 5: Spawn Teammates

Spawn teammates using the Task tool with `team_name` parameter. Each teammate is a full Claude Code session.

**Default team composition** (3 teammates):

#### Teammate: Codebase Analyst

```
Task:
  name: codebase-analyst
  team_name: explore-{feature-name}
  subagent_type: general-purpose
  prompt: |
    You are the Codebase Analyst on an exploration team.

    PROBLEM: {problem description}

    YOUR ROLE: Deep-dive into the existing codebase to understand:
    - Current architecture and patterns relevant to this problem
    - Key files, modules, and integration points
    - Technical constraints and existing contracts
    - What the codebase already does well that we should build on
    - What technical debt or limitations might block us

    INSTRUCTIONS:
    1. Read your assigned task from the TaskList for details
    2. Explore the codebase thoroughly — use Glob, Grep, Read
    3. Document your key findings
    4. When done with initial exploration, message your teammates with findings
    5. Engage with challenges from the Critic — defend or revise your findings
    6. Mark your task as completed when done

    Be thorough but focused. We need actionable findings, not a codebase tour.
```

#### Teammate: External Researcher

```
Task:
  name: external-researcher
  team_name: explore-{feature-name}
  subagent_type: general-purpose
  prompt: |
    You are the External Researcher on an exploration team.

    PROBLEM: {problem description}

    YOUR ROLE: Look outward to find the best approaches:
    - Research libraries, frameworks, and tools relevant to this problem
    - Find prior art — how have others solved similar problems?
    - Identify industry patterns and best practices
    - Evaluate tradeoffs between approaches (performance, complexity, maintenance)
    - Consider what fits our codebase vs. what would fight it

    INSTRUCTIONS:
    1. Read your assigned task from the TaskList for details
    2. Use WebSearch and WebFetch to research approaches
    3. Read relevant codebase files to understand what would fit
    4. Document options with clear pros/cons
    5. Message teammates with your findings — especially the Codebase Analyst for fit assessment
    6. Engage with the Critic's challenges
    7. Mark your task as completed when done

    Focus on practical options, not exhaustive surveys. We need 2-4 viable approaches, not 20.
```

#### Teammate: Critic

```
Task:
  name: critic
  team_name: explore-{feature-name}
  subagent_type: general-purpose
  prompt: |
    You are the Critic (Devil's Advocate) on an exploration team.

    PROBLEM: {problem description}

    YOUR ROLE: Stress-test everything the team discovers:
    - Challenge assumptions from the Codebase Analyst and External Researcher
    - Identify risks, edge cases, and failure modes
    - Ask "what about X?" for scenarios others might miss
    - Test whether proposed approaches hold up under pressure
    - Surface non-obvious constraints (security, scale, maintenance burden)

    INSTRUCTIONS:
    1. Read your assigned task from the TaskList for details
    2. Wait briefly for teammates to share initial findings (check TaskList progress)
    3. Read the codebase yourself to form independent opinions
    4. When teammates share findings, actively challenge them via messages
    5. Be constructively adversarial — the goal is stronger conclusions, not blocking
    6. Track which assumptions survived scrutiny and which didn't
    7. Mark your task as completed when the debate has converged

    You succeed when the team's final recommendation is battle-tested. Push hard but fair.
```

**Custom roles**: If the user specified different roles, adapt the prompts accordingly. The three defaults can be replaced entirely or augmented with additional teammates (e.g., "security specialist", "UX researcher", "performance analyst").

### Step 6: Delegate and Monitor

**You (the lead) are in delegate mode.** Do NOT explore the codebase yourself or implement anything. Your job:

1. **Monitor progress** — check TaskList periodically
2. **Facilitate** — if teammates seem stuck or talking past each other, send clarifying messages
3. **Steer** — if a teammate goes off-track, redirect them
4. **Relay user input** — if the user gives you additional context, share it with relevant teammates
5. **Nudge convergence** — when initial exploration seems complete, prompt teammates to start debating

Key signals to watch for:
- All three initial tasks marked complete → prompt cross-pollination
- Active messaging between teammates → healthy debate, let it run
- A teammate is idle too long → check in and redirect
- Debate is going in circles → intervene with a focusing question

### Step 7: Synthesize the Brief

Once teammates have explored, debated, and converged (tasks 1-4 complete):

1. **Gather findings** — read messages from all teammates, review any documents they produced
2. **Load the template** — read `~/.claude/skills/explore/templates/exploration-brief-template.md`
3. **Write the brief** — synthesize into `exploration-brief.md` at the feature path
4. **Fill every section** — do not leave template placeholders. If a section has no findings, say so explicitly.

The brief should be:
- **Opinionated** — present the team's recommendation, not just a neutral summary
- **Evidence-backed** — cite specific files, patterns, or research that support conclusions
- **Honest about gaps** — surface open questions for `/research` to resolve
- **Actionable** — a reader should know the recommended path forward after reading it

### Step 8: Clean Up

1. Send shutdown requests to all teammates
2. Wait for confirmations
3. Run Teammate cleanup
4. Mark the convergence task as completed

### Step 9: Handoff

Present the user with:

```
Exploration complete.

Brief: features/{domain}/{feature}/exploration-brief.md

Key findings:
- {1-3 sentence summary of recommended approach}

Open questions for /research:
- {list from the brief}

Next step: /research features/{domain}/{feature}
```

---

## Principles

### Lead Delegates, Teammates Explore

The lead agent MUST NOT do codebase exploration, web research, or analysis itself. All investigative work happens through teammates. The lead's job is: spawn, assign, facilitate, steer, synthesize.

### Debate is the Point

The value of `/explore` over single-agent `/research` is the multi-perspective debate. If teammates aren't messaging each other, something is wrong. Nudge them to share and challenge findings.

### Brief, Not Spec

`exploration-brief.md` is an input to `/research`, not a replacement for it. It should:
- Surface the landscape and recommend an approach
- NOT define interface contracts, test plans, or spec decompositions
- NOT create FEATURE.md or spec-research.md (that's `/research`'s job)

### Time-Box Implicitly

Agent Teams are token-expensive. The default 3-teammate setup is sized for a focused 10-15 minute exploration. If the problem needs more depth, the user can:
- Add more teammates for specific angles
- Run `/explore` again with refined questions
- Move to `/research` and dig deeper on specific areas

### Hybrid Roles

The three defaults (codebase analyst, external researcher, critic) cover most cases. But the user can override with any roles that fit their problem:

```
/explore Add real-time collaboration
  Roles: CRDT specialist, WebSocket architect, conflict resolution analyst
```

Parse natural language role descriptions and craft appropriate prompts.

---

## Anti-patterns

- **Lead does the work** — defeats the purpose; always delegate
- **Teammates don't talk to each other** — means prompts aren't encouraging cross-pollination; intervene
- **Brief is just concatenated findings** — must be synthesized, opinionated, and structured
- **Exploring something trivial** — overhead isn't worth it; tell the user to use `/research` directly
- **Producing spec artifacts** — `/explore` produces a brief, not FEATURE.md or spec-research.md
- **Running too many teammates** — 3 is the sweet spot; more adds coordination cost without proportional value for most explorations
