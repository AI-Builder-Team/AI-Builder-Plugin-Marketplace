---
name: crafting-daily-update
description: Generates daily standup updates from your GitHub PRs formatted for Google Chat. Use when creating standup reports, preparing daily updates, generating work summaries, or crafting team status updates.
allowed-tools: [Bash, Read, Write]
---

# Crafting Daily Update

Generates a daily standup update by fetching your GitHub PRs and formatting them for Google Chat.

## What It Does

Creates a standup update with two sections:
- **Done**: PRs you merged in the last N days (configurable)
- **Doing**: PRs you currently have open

Output is formatted for Google Chat and saved to a dated text file in the repository root, ready to paste directly into your team chat.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Access to the repository you want to report on

## Workflow

### 1. Ask for Lookback Period

Ask the user: "How many days back should I look for merged PRs?" (e.g., 1, 3, 7, 14)

Common options:
- `1`: Yesterday/today only
- `3`: Last 3 days
- `7`: Last week
- `14`: Last 2 weeks

Store the user's input as `MERGED_DAYS`.

### 2. Fetch PR Data

Execute the fetch script with the lookback period:

```bash
bash .claude/skills/crafting-daily-update/scripts/fetch-prs.sh $MERGED_DAYS
```

This returns JSON with:
- `merged`: Array of PRs merged in the last N days (includes reviewer info)
- `open`: Array of open PRs

Each merged PR includes: `number`, `title`, `url`, `body`, `reviews`
Each open PR includes: `number`, `title`, `url`, `body`

### 3. Analyze and Format PRs

For each PR:

**Generate concise description:**
- Read the PR title and body
- Create a single 1-sentence summary that captures the key change
- Focus on the "what" and "why", not implementation details
- Keep it clear and non-technical when possible
- Use exactly one bullet point per PR, no sub-bullets

**For merged PRs only:**
- Extract the reviewer name from the PR reviews
- If multiple reviewers, use the first one who approved
- Add reviewer info in the format: `(Reviewed by @username)`

### 4. Format Output

Use this exact template:

```
*Done:*
- Concise description of what was accomplished - https://github.com/org/repo/pull/123 (Reviewed by @reviewer1)
- Another merged PR description - https://github.com/org/repo/pull/456 (Reviewed by @reviewer2)

*Doing:*
- Description of work in progress - https://github.com/org/repo/pull/789
- Another open PR description - https://github.com/org/repo/pull/012
```

### 5. Save to File

Write the formatted standup update to a text file in the repository root:

```
daily-standup-YYYY-MM-DD.txt
```

Use today's date for the filename (e.g., `daily-standup-2025-01-15.txt`).

This allows you to:
- Copy/paste directly from the file into Google Chat
- Keep a history of your daily updates
- Reference past standups when needed

## Google Chat Formatting

Google Chat supports:

- **Bold text**: `*text*` → **text**
- **Bullet points**: Standard `- ` syntax
- **Links**: Plain URLs are automatically converted to clickable links

## Output Template

```
*Done:*
- Brief description - https://github.com/org/repo/pull/123 (Reviewed by @reviewer1)
- Another accomplishment - https://github.com/org/repo/pull/456 (Reviewed by @reviewer2)

*Doing:*
- Current work item - https://github.com/org/repo/pull/789
- Another active task - https://github.com/org/repo/pull/012
```

## Tips for Great Descriptions

- **Be specific**: "Add user authentication" not "Update login"
- **Show impact**: "Fix critical bug affecting 50% of users" not "Fix bug"
- **Use action verbs**: "Implement", "Refactor", "Optimize", "Fix"
- **Keep it short**: Exactly one bullet point per PR
- **Be consistent**: Use similar phrasing across all items

## Example Output

```
*Done:*
- Add month-over-month comparison for key metrics dashboard - https://github.com/ai-builder/klair/pull/937 (Reviewed by @john-reviewer)
- Fix cleanup script and add worktree management documentation - https://github.com/ai-builder/klair/pull/932 (Reviewed by @jane-reviewer)
- Implement web research slash command with Firecrawl integration - https://github.com/ai-builder/klair/pull/925 (Reviewed by @mike-reviewer)

*Doing:*
- Add business unit retention trend analysis - https://github.com/ai-builder/klair/pull/940
- Implement AI-powered budget variance analyzer - https://github.com/ai-builder/klair/pull/941
```

## Troubleshooting

**No PRs found:**
- Verify you're in the correct repository directory
- Check that you have PRs matching the criteria (merged in the specified period or currently open)
- Ensure GitHub CLI is authenticated: `gh auth status`
- Try increasing the `MERGED_DAYS` value to look back further

**Script errors:**
- Verify script is executable: `chmod +x .claude/skills/crafting-daily-update/scripts/fetch-prs.sh`
- Check GitHub CLI is installed: `gh --version`

**Formatting issues:**
- Ensure asterisks for bold: `*Done:*` not `**Done:**`
- Verify URLs are complete with `https://`
- Check format: `- Description - URL` with space-hyphen-space between description and URL
- Ensure each PR is on a single line with no line breaks between PRs
