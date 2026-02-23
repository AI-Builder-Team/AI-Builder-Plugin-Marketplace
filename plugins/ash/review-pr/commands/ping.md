---
description: Post a PR review request to Google Chat
allowed-tools: Bash(gh pr view:*), Bash(git branch:*), Bash(curl:*)
---

# Ping — Post PR Review Request to Google Chat

Post a message to the team's Google Chat channel requesting a PR review.

## Step 1 — Find the PR URL

Check the recent conversation context for any GitHub PR links (e.g., `https://github.com/.../pull/123`).

If no PR link is found in the conversation, run:

```bash
gh pr view --json url,title,headRefName -q '"\(.url)\n\(.title)\n\(.headRefName)"'
```

If no open PR exists for the current branch, stop and tell the user:
> "No PR found. Please open a PR first or provide a PR link, then re-run /ping."

Store: `PR_URL`, `PR_TITLE`, `HEAD_BRANCH`.

## Step 2 — Extract the KLAIR ID

Try to extract a `KLAIR-<number>` identifier:

1. **PR title first**: Look for `KLAIR-\d+` in `PR_TITLE`.
2. **Branch name fallback**: Look for `KLAIR-\d+` (case-insensitive) in `HEAD_BRANCH`.
3. **If neither works**: Use `AskUserQuestion` to ask the user to provide the KLAIR linear ID explicitly.

Store: `KLAIR_ID` (e.g., `KLAIR-1993`).

## Step 3 — Determine the display label

Use `KLAIR_ID: PR_TITLE` as the label. If the PR title already starts with the KLAIR ID, just use the PR title as-is to avoid duplication.

## Step 4 — Post to Google Chat

Send the message using the webhook:

```bash
curl -s -X POST \
  'https://chat.googleapis.com/v1/spaces/AAQAJOLbn2E/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=BSUYFPrTBIzD-fKuopnf9tiFGERzG4POAfatF5qloLM' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "*PR Review Requested*\n<'"$PR_URL"'|'"$LABEL"'>"
  }'
```

Where `$LABEL` is the display label from Step 3 (e.g., `KLAIR-1993: Add review-pr plugin`).

**Important**: Escape any special characters in the label that would break JSON (double quotes, backslashes).

## Step 5 — Confirm

Tell the user the message was posted successfully and show them what was sent.
