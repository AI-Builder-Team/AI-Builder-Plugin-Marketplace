---
name: runexact
description: Execute a command exactly as written and return full output
argument-hint: [command]
allowed-tools: Bash(*)
---

Execute this command using the Bash tool. Do NOT modify, interpret, or add flags to it. Run it VERBATIM as a single Bash call. Return the full output to the user. Do NOT launch subagents, do NOT summarize, do NOT add --stat or any other flags. One Bash call, exact command, full output.

```
$ARGUMENTS
```
