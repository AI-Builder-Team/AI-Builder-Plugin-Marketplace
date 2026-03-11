# Step 3: Post-Creation Validation

After creating the skill files, run this validation workflow.

## 3.1 Ask the User to Test

Tell them to invoke the newly created skill (e.g., `/skill-name test-arg`) in their current session or a new one, then come back and confirm it ran.

## 3.2 Trace the Invocation Session

Once the user confirms they ran it, **ask the user for the session ID** where they invoked it. This is critical because:
- The skill may have been invoked in a **long-running, reused session** — not a recently-created one
- Skills with `context: default` (no fork) run inside the existing session, so there's no new JSONL file to find
- The most-recently-modified JSONL is often the *current* audit session, not the invocation session
- Searching by recency (`ls -lt`) is unreliable — a 3-hour-old session that was reused won't be at the top

**How to get the session ID:** Tell the user to check their Claude Code status bar or run `/status` in the session where they invoked the skill. The session ID is a UUID like `01300e01-8a6c-4353-9c4d-02e5b67bd4b2`.

Once you have the session ID, construct the path:
```bash
SESSION_ID="<paste-session-id-here>"
PROJECT_DIR=$(pwd | tr '/' '-' | sed 's/^-//')
ls -la ~/.claude/projects/${PROJECT_DIR}/${SESSION_ID}.jsonl

# If skill used context:fork or agent, also check for subagent sessions
# (they'll be separate JSONL files modified around the same time)
```

**Fallback if user can't provide session ID:** Search all JSONL files for the skill's `<command-name>` tag:
```bash
grep -l "command-name.*skill-name-here" ~/.claude/projects/${PROJECT_DIR}/*.jsonl
```
Then among matches, exclude the current session (you know your own session ID from `$CLAUDE_SESSION_ID`) and pick the one with the most recent modification time.

## 3.3 Audit the Session JSONL

Read the identified session file(s) and check for ALL of the following:

### a) Errors
- Grep for `"error"`, `"Error"`, `"failed"`, `"exception"` in the JSONL
- Check for tool calls that returned error results
- Look for HTTP/API errors in tool outputs

### b) Failed Attempts / Retries
- Look for the same tool being called multiple times with slightly different parameters (indicates the agent had to retry)
- Check for sequences where a Bash command fails then gets re-run with corrections
- Count total tool calls vs unique tool calls — a high ratio suggests thrashing

### c) Agent Self-Correction
- Look for assistant messages containing phrases like "let me try", "that didn't work", "instead", "actually" — signs the agent had to course-correct mid-execution
- Check if the agent read files it shouldn't have needed to (indicates confusion about what context it had)

### d) Skill Firing / Context Injection Issues
- **If the skill uses `!` backtick commands**: verify the command output appears as literal text in the first assistant message's context (not as a command to be run). If the agent is *running* the command itself via Bash tool, the `!` backtick preprocessing failed.
- **If the skill uses `$ARGUMENTS`**: verify the arguments were substituted as literal text, not left as `$ARGUMENTS` or `$0` etc.
- **If the skill uses `context: fork`**: verify a separate subagent JSONL was created (the skill should NOT have run in the main session)
- **If the skill uses `agent: Explore` or similar**: verify the session used that agent type
- **If the skill uses `allowed-tools`**: verify no tool calls outside the whitelist were attempted

### e) Overall Health Signals
- Total turn count — if a simple skill took >10 turns, something is off
- Check that the skill's described purpose was actually achieved in the output
- Look for the agent asking the user clarifying questions (suggests the skill prompt was ambiguous)

## 3.4 Report Findings

Summarize:
- Whether the skill fired correctly (context injected, args substituted)
- Any errors or retries found
- Whether the skill achieved its purpose in a reasonable number of turns
- Specific fixes to apply to the SKILL.md if issues were found

## 3.5 Fix and Re-test

If issues were found, update the SKILL.md and ask the user to test again.
