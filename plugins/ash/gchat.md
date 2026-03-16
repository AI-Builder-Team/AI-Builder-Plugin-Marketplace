---
description: "Google Chat operations for the AI Builders space"
argument-hint: "unread | mentions [days] | reviewed"
allowed-tools: Bash(gws chat:*), Bash(jq:*), Bash(cat:*), Bash(python3:*), Bash(mktemp:*), Bash(rm:*), AskUserQuestion
---

# GChat — Google Chat CLI

Interact with Google Chat via the Google Workspace CLI (`gws`).

**Subcommand:** $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` to determine the subcommand:

| Input | Action |
|---|---|
| `unread` | Run the **Unread** flow below |
| `mentions` | Run the **Mentions** flow with default 7 days |
| `mentions <N>` | Run the **Mentions** flow for the last N days |
| `reviewed` | Run the **Reviewed** flow — auto-discover the thread and post "Review posted" reply |
| *(anything else or empty)* | Reply: "Usage: `/gchat unread`, `/gchat mentions [days]`, or `/gchat reviewed`" and stop |

## IMPORTANT: Confirmation required before sending

**NEVER send a message, reply, or reaction to Google Chat without explicit user approval.** Before executing any write action (message create, reaction create), you MUST:

1. Show the user exactly what will be posted (message text, emoji, etc.)
2. Show which thread it will be posted to (thread name or context from the original message)
3. Use `AskUserQuestion` to ask for confirmation (e.g. "Send this? [Yes / No]")
4. Only proceed if the user approves. If denied, stop or ask for edits.

This applies to ALL flows — unread actions, mentions actions, and the reviewed flow.

## Constants

<!-- UPDATE THESE for your own setup -->
<!-- Space ID: Google Chat space identifier. Find yours via `gws chat spaces list` -->
- **Space ID:** `spaces/AAAAI17dp28` *(AI Builders space)*
<!-- User ID: Your Google Chat user ID. Find yours via `gws chat users get --params '{"name": "users/me"}'` -->
- **User ID (Ashwanth):** `users/116176676259067405846`

## Steps

### 1. Get read state

```bash
gws chat users spaces getSpaceReadState --params '{"name": "users/me/spaces/AAAAI17dp28/spaceReadState"}'
```

Extract the `lastReadTime` from the JSON response.

### 2. Fetch unread messages

```bash
gws chat spaces messages list --params '{"parent": "spaces/AAAAI17dp28", "filter": "createTime > \"LAST_READ_TIME\"", "orderBy": "createTime asc"}' --page-all
```

Replace `LAST_READ_TIME` with the value from step 1.

### 3. Present results

- If there are no unread messages, say "No unread messages in AI Builders."
- If there are unread messages, show each message with:
  - **Sender** (use the `text` field which contains resolved @mention display names, or `sender.name`)
  - **Time** (`createTime`, converted to a human-readable relative time like "2 hours ago")
  - **Message text** (`text` field)
  - **Thread** context if available (`thread.name`)
- Group messages by thread when possible for readability.
- Show a count summary at the end, e.g. "5 unread messages across 3 threads."

### 4. Ask user for actions

After presenting unread messages, ask the user what they'd like to do. Supported actions:

#### React to a message

Add an emoji reaction (default 👀) to a message:

```bash
gws chat spaces messages reactions create \
  --params '{"parent": "MESSAGE_NAME"}' \
  --json '{"emoji": {"unicode": "EMOJI"}}'
```

#### Reply in a thread

To reply in a thread while tagging someone, write the JSON body to a temp file first (to avoid shell escaping issues with `<>` in user mentions):

```bash
TMPFILE=$(mktemp /tmp/gchat-reply.XXXXXX.json)
cat > "$TMPFILE" << 'EOF'
{"text": "<users/USER_ID> Reply text here", "thread": {"name": "THREAD_NAME"}}
EOF
gws chat spaces messages create \
  --params '{"parent": "spaces/AAAAI17dp28", "messageReplyOption": "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"}' \
  --json "$(cat "$TMPFILE")"
rm -f "$TMPFILE"
```

- Replace `USER_ID` with the sender's user ID from `sender.name`
- Replace `THREAD_NAME` with the thread name from `thread.name`
- Always use the temp file approach for message bodies containing `<>` user mentions

#### Common workflow

For PR review requests or similar messages, offer to:
1. React with 👀 (acknowledge)
2. Reply tagging the sender (e.g. "I am looking into it!")

Execute both actions in parallel when the user approves.

---

## Mentions flow

Fetch all messages where Ashwanth is tagged in the AI Builders space within the last N days.

### 1. Calculate cutoff timestamps

Compute ISO 8601 timestamps using Python for cross-platform compatibility (works on both macOS and Linux):

```bash
python3 -c "from datetime import datetime, timedelta, timezone; print((datetime.now(timezone.utc) - timedelta(days=N)).strftime('%Y-%m-%dT%H:%M:%SZ'))"
```

Replace `N` with the number of days.

### 2. Fetch messages mentioning Ashwanth (progressive)

<!-- Note: The Google Chat API does not support filtering by mention server-side.
     Only `createTime` and `thread.name` filters are available on `messages.list`.
     To minimize payload, we fetch progressively: 1 day at a time, expanding until
     mentions are found or the full N-day window is exhausted. -->

Use progressive fetching to minimize payload — start with 1 day, expand day-by-day up to N days:

1. Set `D = 1` (current window in days).
2. Compute the cutoff for D days ago (using the Python command above).
3. Fetch messages:

```bash
gws chat spaces messages list --params '{"parent": "spaces/AAAAI17dp28", "filter": "createTime > \"CUTOFF_TIME\"", "orderBy": "createTime asc"}' --page-all
```

4. Filter the results to only messages where `annotations` contains a `USER_MENTION` with `user.name` equal to `users/116176676259067405846` (Ashwanth's user ID).
5. If mentions are found, proceed to step 3 (Present results).
6. If no mentions found and `D < N`, increment `D` and repeat from step 2.
7. If `D == N` and still no mentions, report "No mentions in AI Builders in the last N days."

### 3. Present results

- If no mentions found, say "No mentions in AI Builders in the last N days."
- If mentions found, show each message with:
  - **Sender** (from the `text` field or `sender.name`)
  - **Time** (`createTime`, as a human-readable relative time)
  - **Message text** (`text` field)
  - **Thread** context if available
- Group by thread for readability.
- Show a count summary, e.g. "8 mentions across 5 threads in the last 7 days."

### 4. Ask user for actions

Same as the unread flow — offer to react or reply to any message.

---

## Reviewed flow

Post a follow-up message in a thread where Ashwanth previously indicated he would review a PR. This is intended to be run in a session where a PR review link is already in the conversation context.

### 1. Extract the PR review link and determine review type

Search the current conversation context for a GitHub PR review URL. These typically look like:
- `https://github.com/<org>/<repo>/pull/<number>`
- `https://github.com/<org>/<repo>/pull/<number>#pullrequestreview-<id>`

If no PR link is found in the conversation, use `AskUserQuestion` to ask the user to provide the review link.

Also determine the review type from the conversation context (e.g. from `gh pr review` output, submitted review text, or user statements). Possible types:

| Review type | Message |
|---|---|
| Approval | `✅ Approved: PR_REVIEW_LINK` |
| Changes requested | `Review posted (changes requested): PR_REVIEW_LINK` |
| Comment only / unclear | `Review posted: PR_REVIEW_LINK` |

Store: `PR_REVIEW_LINK` and `REVIEW_TYPE`.

### 2. Find the thread

Auto-discover the thread where Ashwanth previously acknowledged the PR review request. Use progressive fetching to minimize payload — start with 1 day, expand day-by-day up to 7 days:

<!-- Note: Same progressive approach as mentions flow — the Chat API doesn't support
     server-side filtering by message content, so we fetch and search locally. -->

1. Set `D = 1`.
2. Compute the cutoff for D days ago:

```bash
python3 -c "from datetime import datetime, timedelta, timezone; print((datetime.now(timezone.utc) - timedelta(days=D)).strftime('%Y-%m-%dT%H:%M:%SZ'))"
```

3. Fetch messages:

```bash
gws chat spaces messages list --params '{"parent": "spaces/AAAAI17dp28", "filter": "createTime > \"CUTOFF_TIME\"", "orderBy": "createTime desc"}' --page-all
```

4. From the results, look for a thread that contains a message referencing the same PR URL (or PR number) from `PR_REVIEW_LINK`. The thread to use is the one where the original review request was posted.
5. If a matching thread is found, proceed to step 3 (Preview and confirm).
6. If no match and `D < 7`, increment `D` and repeat from step 2.
7. If `D == 7` and no match, ask the user for context (see below).

**Matching strategy (in priority order):**
1. Look for messages containing the PR URL (e.g. `github.com/.../pull/2215`)
2. Look for messages containing the PR number (e.g. `#2215` or `/pull/2215`)
3. If multiple threads match, prefer the one where Ashwanth is mentioned (`annotations` with `USER_MENTION` for `users/116176676259067405846`)

If no matching thread is found, use `AskUserQuestion` to ask the user for more context (e.g. "I couldn't find a thread referencing PR #2215. Can you describe the message or provide the thread name?").

Store: `THREAD_NAME` (the `thread.name` from the matched message).

### 3. Preview and confirm

Show the user a preview:

> **Thread:** `THREAD_NAME`
> **Message:** *(based on review type — e.g. "✅ Approved: PR_REVIEW_LINK")*

Use `AskUserQuestion` to ask: "Send this to the thread? [Yes / No]"

If denied, stop or ask for edits.

### 4. Post the review update

Only after user approval:

```bash
TMPFILE=$(mktemp /tmp/gchat-reply.XXXXXX.json)
cat > "$TMPFILE" << 'EOF'
{"text": "MESSAGE_BASED_ON_REVIEW_TYPE", "thread": {"name": "THREAD_NAME"}}
EOF
gws chat spaces messages create \
  --params '{"parent": "spaces/AAAAI17dp28", "messageReplyOption": "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"}' \
  --json "$(cat "$TMPFILE")"
rm -f "$TMPFILE"
```

Replace `PR_REVIEW_LINK` and `THREAD_NAME` with the values from steps 1 and 2.

### 5. Confirm

Tell the user the review update was posted to the thread.
