---
name: issues-eval
description: "Parse a PR_comments file and launch parallel issue-qc agents for each unresolved issue giving each agent the PR_comments filepath and line numbers relevant to the issue it will investigate"
argument-hint: "<path-to-pr-comments-file>"
---

Read the file at `$ARGUMENTS`. Find every section marked `🟡 Unresolved`.

For each unresolved issue, launch a `issue-qc` agent via the Task tool (`subagent_type: "issue-qc"`). Launch all of them in parallel — do not wait for any agent to finish before launching the next.

Each agent prompt MUST follow this template exactly:

```
Investigate this PR review concern:

**PR_Comments_File:** <absolute path to $ARGUMENTS>
**PR_Comment_Issue_Line(s):** <line numbers in the PR comments file where this issue appears>
**Concern:** <the reviewer's comment text>

IMPORTANT: You MUST use the Edit tool to annotate the PR_Comments_File in-place. Add a `QC_BOT_COMMENTS:` line directly below the reviewer's comment block at the specified lines with your verdict (✅ VALID, ❌ INVALID, or ⚠️ PARTIAL) and a one-line summary of evidence. Do NOT just return text — you must edit the file.
```

After all agents complete, summarize results in a table:

| # | $ARGUMENTS Lines | Reviewer | Verdict | Summary |
|---|------------------|----------|---------|---------|

Then list valid issues grouped by severity.
