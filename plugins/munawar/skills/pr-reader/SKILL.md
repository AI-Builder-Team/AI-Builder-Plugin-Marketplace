---
name: "m:pr-reader"
description: "Fetch and display unresolved PR comments by default. Pass a PR number, branch name, or nothing for current branch. Add --all to include resolved threads."
argument-hint: "<PR# or branch> [--all] e.g. 432, 110-chorus --all, or blank for current branch"
---

You are an expert GitHub PR comments analyst. Your sole purpose is to fetch all comments from a GitHub Pull Request using the `gh` CLI, organize them into coherent threads, and render them as clean, readable markdown.

**Do NOT:**
- Include PR diff or code changes
- Generate any PR summary or analysis
- Paste the full verbatim comment text into your final message (save it to `.scratch/outputs/` instead)

## Core Workflow

1. **Parse arguments**:
   - Check if `$ARGUMENTS` contains `--all`. If so, set `SHOW_ALL=true` and strip the flag from the remaining arguments. Default behavior (no flag) is to hide resolved threads.
   - With remaining arguments:
     - **If a number**: Use it as the PR number directly
     - **If a string**: Treat it as a branch name: `gh pr list --head $ARGUMENTS --base main --state open`
     - **If empty**: Detect current branch via `git branch --show-current`, then `gh pr list --head <branch> --base main --state open`
   - If no open/draft PR is found, inform the user — there's nothing to review.
   - If a PR is found, proceed with it automatically.

2. **Detect the repo** (needed for `gh api` calls):
   ```bash
   gh repo view --json nameWithOwner -q '.nameWithOwner'
   ```
   Store this as `REPO` for use in API calls below.

3. **Fetch all four data sources**:

   GitHub stores PR feedback in **three separate places**, plus resolution status lives in GraphQL. You MUST fetch all four.

   **Source A — PR metadata + general conversation:**
   ```bash
   gh pr view <number> --json number,title,author,state,headRefName,baseRefName,body,createdAt,comments > /tmp/pr_<number>_main.json
   ```
   - `comments` = general conversation (issue comments, not on specific code)
   - NOTE: Do NOT fetch `reviews` from `gh pr view --json` — its review IDs are GraphQL node IDs (e.g. `PRR_kwDO...`) which don't match the numeric IDs from the REST API.

   **Source A2 — Review summaries (via REST API, for consistent IDs):**
   ```bash
   gh api repos/{REPO}/pulls/<number>/reviews --paginate > /tmp/pr_<number>_reviews.json
   ```
   Returns review objects with numeric `id` fields that match `pull_request_review_id` on inline comments.

   **Source B — Inline code review comments (with code snippets):**
   ```bash
   gh api repos/{REPO}/pulls/<number>/comments --paginate > /tmp/pr_<number>_inline.json
   ```
   This is the **MOST IMPORTANT** endpoint. `gh pr view --json` does NOT return these.

   **Source C — Review thread resolution status (GraphQL only):**
   Resolution status (`isResolved`) is ONLY available via GraphQL `reviewThreads`. Fetch with pagination:
   ```bash
   gh api graphql --paginate -f query='
   query($endCursor: String) {
     repository(owner: "{OWNER}", name: "{REPO_NAME}") {
       pullRequest(number: <number>) {
         reviewThreads(first: 100, after: $endCursor) {
           pageInfo { hasNextPage endCursor }
           nodes {
             isResolved
             comments(first: 1) {
               nodes { databaseId }
             }
           }
         }
       }
     }
   }' > /tmp/pr_<number>_threads.json
   ```
   This maps each thread's first comment `databaseId` (which matches inline comment `id` from Source B) to its `isResolved` status.

   **CRITICAL ID MATCHING NOTE:** `gh pr view --json reviews` returns GraphQL node IDs (strings like `"PRR_kwDO..."`), but `gh api pulls/{pr}/comments` returns numeric `pull_request_review_id` integers. These will NEVER match. That's why you MUST use `gh api repos/{REPO}/pulls/{pr}/reviews` (Source A2) for reviews — it returns numeric IDs that match.

4. **Write the reference script** to `/tmp/pr_reader_<number>.py` using Bash with a heredoc (`cat > /tmp/pr_reader_<number>.py << 'PYEOF'`), NOT the Write tool (which requires reading the file first and will fail on new `/tmp/` files). Then run it.

5. **Write the output** to `.scratch/outputs/pr-<number>-comments.md` using the Write tool.

## Reference Script

Write this script to `/tmp/pr_reader_<number>.py`, substituting `<number>` with the actual PR number. You may adapt it slightly if needed but the core logic (especially ID matching and thread grouping) must stay the same.

```python
#!/usr/bin/env python3
"""PR Comment Reader - fetches and organizes all PR comments into markdown."""
import json
import os
import re
import sys
from datetime import datetime
from collections import defaultdict

PR_NUMBER = "<number>"  # Replace with actual PR number
HIDE_RESOLVED = "--all" not in sys.argv  # Default: hide resolved. Pass --all to show everything.

def parse_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y at %I:%M %p UTC")
    except Exception:
        return date_str

def strip_bot_noise(body, author):
    if 'cursor' not in author.lower() and 'bugbot' not in author.lower():
        return body
    # Extract description if present
    desc_match = re.search(r'<!-- DESCRIPTION START -->(.*?)<!-- DESCRIPTION END -->', body, flags=re.DOTALL)
    if desc_match:
        body = desc_match.group(1).strip()
    else:
        body = re.sub(r'<p>.*?cursor\.com.*?</p>', '', body, flags=re.DOTALL)
        body = re.sub(r'<!-- BUGBOT_BUG_ID.*?-->', '', body, flags=re.DOTALL)
        body = re.sub(r'<!-- LOCATIONS START.*?LOCATIONS END -->', '', body, flags=re.DOTALL)
        body = re.sub(r'<details>.*?</details>', '', body, flags=re.DOTALL)
    return body.strip()

def get_last_n_lines(diff_hunk, n=5):
    if not diff_hunk:
        return ""
    lines = diff_hunk.split('\n')
    return '\n'.join(lines[-n:])

def detect_language(file_path):
    ext_map = {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
        '.tsx': 'tsx', '.jsx': 'jsx', '.go': 'go', '.java': 'java',
        '.rb': 'ruby', '.rs': 'rust', '.sh': 'bash', '.yml': 'yaml',
        '.yaml': 'yaml', '.json': 'json', '.md': 'markdown',
        '.html': 'html', '.css': 'css', '.scss': 'scss',
    }
    for ext, lang in ext_map.items():
        if file_path.endswith(ext):
            return lang
    return ''

EMOJI_MAP = {
    'APPROVED': '\u2705', 'CHANGES_REQUESTED': '\u274c',
    'COMMENTED': '\U0001f4ac', 'DISMISSED': '\U0001f6ab'
}

# --- Load data ---
with open(f'/tmp/pr_{PR_NUMBER}_main.json') as f:
    pr_data = json.load(f)

with open(f'/tmp/pr_{PR_NUMBER}_reviews.json') as f:
    reviews = json.load(f)

with open(f'/tmp/pr_{PR_NUMBER}_inline.json') as f:
    inline_comments = json.load(f)

# --- Load thread resolution status from GraphQL ---
# Maps top-level comment databaseId -> bool (isResolved)
resolution_map = {}
try:
    with open(f'/tmp/pr_{PR_NUMBER}_threads.json') as f:
        raw = f.read()
    # gh api graphql --paginate concatenates JSON objects; parse each one
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(raw):
        raw_stripped = raw[pos:].lstrip()
        if not raw_stripped:
            break
        obj, end = decoder.raw_decode(raw_stripped)
        pos += len(raw) - len(raw_stripped) - pos + end
        nodes = obj.get('data', {}).get('repository', {}).get('pullRequest', {}).get('reviewThreads', {}).get('nodes', [])
        for node in nodes:
            comments = node.get('comments', {}).get('nodes', [])
            if comments:
                db_id = comments[0].get('databaseId')
                if db_id is not None:
                    resolution_map[db_id] = node.get('isResolved', False)
except FileNotFoundError:
    pass  # Graceful fallback if threads file missing

resolved_count = sum(1 for v in resolution_map.values() if v)
unresolved_count = sum(1 for v in resolution_map.values() if not v)

# --- Build output ---
out = []

# Header
out.append(f"# PR #{pr_data['number']}: {pr_data['title']}")
out.append(f"**Author:** @{pr_data['author']['login']} | **State:** {pr_data['state']} | **Branch:** `{pr_data['headRefName']}` \u2192 `{pr_data['baseRefName']}`")
if resolution_map:
    filter_note = " | \u26a0\ufe0f **Showing unresolved only** (pass --all for everything)" if HIDE_RESOLVED else ""
    out.append(f"**Threads:** {resolved_count} resolved, {unresolved_count} unresolved{filter_note}")
out.append("\n---\n")

# PR Description
out.append("## PR Description\n")
out.append(f"> **@{pr_data['author']['login']}** \u2014 {parse_date(pr_data['createdAt'])}")
body = pr_data.get('body') or '_(No description provided)_'
for line in body.split('\n'):
    out.append(f"> {line}")
out.append("\n---\n")

# General Conversation
if pr_data.get('comments'):
    out.append("## General Conversation\n")
    for c in pr_data['comments']:
        author = c['author']['login']
        b = strip_bot_noise(c['body'], author)
        out.append(f"> **@{author}** \u2014 {parse_date(c['createdAt'])}")
        for line in b.split('\n'):
            out.append(f"> {line}")
        out.append("")
    out.append("---\n")

# --- Group inline comments by review and into threads ---
inline_by_review = defaultdict(list)
threads = {}  # top_comment_id -> {'comment': ..., 'replies': [...]}

for c in inline_comments:
    review_id = c.get('pull_request_review_id')
    if review_id:
        inline_by_review[review_id].append(c)
    if c.get('in_reply_to_id') is None:
        threads[c['id']] = {'comment': c, 'replies': []}

for c in inline_comments:
    reply_to = c.get('in_reply_to_id')
    if reply_to and reply_to in threads:
        threads[reply_to]['replies'].append(c)

def render_inline_comment(comment, depth=0):
    """Render a single inline comment with optional code snippet."""
    lines = []
    prefix = '>' * (depth + 1) + ' '
    author = comment['user']['login']
    b = strip_bot_noise(comment['body'], author)
    lines.append(f"{prefix}**@{author}** \u2014 {parse_date(comment['created_at'])}")
    for line in b.split('\n'):
        lines.append(f"{prefix}{line}")
    lines.append("")
    return lines

def is_thread_resolved(top_comment_id):
    """Check if a thread is resolved using the GraphQL resolution map."""
    return resolution_map.get(top_comment_id, None)

def render_thread(top_comment):
    """Render a top-level inline comment with code snippet and replies."""
    comment_id = top_comment['id']
    resolved = is_thread_resolved(comment_id)

    # Skip resolved threads when --unresolved flag is set
    if HIDE_RESOLVED and resolved is True:
        return []

    lines = []
    file_path = top_comment.get('path', 'unknown')
    line_num = top_comment.get('line') or top_comment.get('original_line') or '?'

    # Resolution badge
    if resolved is True:
        badge = "\u2705 Resolved"
    elif resolved is False:
        badge = "\U0001f7e1 Unresolved"
    else:
        badge = ""
    location = f"##### `{file_path}:{line_num}`"
    lines.append(f"{location} {badge}" if badge else location)

    if top_comment.get('diff_hunk'):
        lang = detect_language(file_path)
        lines.append(f"```{lang}")
        lines.append(get_last_n_lines(top_comment['diff_hunk'], 5))
        lines.append("```")
        lines.append("")

    lines.extend(render_inline_comment(top_comment, depth=0))

    thread = threads.get(top_comment['id'])
    if thread:
        for reply in sorted(thread['replies'], key=lambda x: x['created_at']):
            lines.extend(render_inline_comment(reply, depth=1))

    lines.append("---\n")
    return lines

# --- Code Reviews with inline comments ---
out.append("## Code Reviews\n")

# Track which inline comments were rendered under a review
rendered_inline_ids = set()

for review in sorted(reviews, key=lambda r: r.get('submitted_at', '')):
    state = review.get('state', 'COMMENTED')
    author = review['user']['login']
    emoji = EMOJI_MAP.get(state, '\U0001f4dd')

    out.append(f"### {emoji} Review by @{author} \u2014 {state} \u2014 {parse_date(review.get('submitted_at', ''))}")
    out.append("")

    if review.get('body'):
        b = strip_bot_noise(review['body'], author)
        for line in b.split('\n'):
            out.append(line)
        out.append("")

    # Inline comments belonging to this review
    review_id = review['id']
    review_inlines = inline_by_review.get(review_id, [])
    top_level = [c for c in review_inlines if c.get('in_reply_to_id') is None]

    if top_level:
        out.append("#### Inline Comments\n")
        for c in sorted(top_level, key=lambda x: (x.get('path', ''), x.get('created_at', ''))):
            out.extend(render_thread(c))
            rendered_inline_ids.add(c['id'])
            # Also mark replies as rendered
            thread = threads.get(c['id'])
            if thread:
                for r in thread['replies']:
                    rendered_inline_ids.add(r['id'])

    out.append("---\n")

# Orphaned inline comments (no matching review, or review_id was null)
orphaned = [c for c in inline_comments
            if c['id'] not in rendered_inline_ids
            and c.get('in_reply_to_id') is None]

if orphaned:
    out.append("## Other Inline Comments\n")
    for c in sorted(orphaned, key=lambda x: x['created_at']):
        out.extend(render_thread(c))

# Empty check
if not pr_data.get('comments') and not reviews and not inline_comments:
    out.append("_No comments found on this PR._\n")

# Write
os.makedirs('.scratch/outputs', exist_ok=True)
with open(f'.scratch/outputs/pr-{PR_NUMBER}-comments.md', 'w') as f:
    f.write('\n'.join(out))

print(f"\u2713 Written to .scratch/outputs/pr-{PR_NUMBER}-comments.md")
print(f"  Reviews: {len(reviews)}, Inline comments: {len(inline_comments)}, Conversation: {len(pr_data.get('comments', []))}")
if resolution_map:
    print(f"  Threads: {resolved_count} resolved, {unresolved_count} unresolved")
    if HIDE_RESOLVED:
        print(f"  (Resolved threads hidden — pass --all to include them)")
```

## Execution Steps

1. `gh repo view --json nameWithOwner -q '.nameWithOwner'` — get REPO (split into OWNER and REPO_NAME for GraphQL)
2. Run these four in parallel:
   ```bash
   gh pr view <number> --json number,title,author,state,headRefName,baseRefName,body,createdAt,comments > /tmp/pr_<number>_main.json
   gh api repos/{REPO}/pulls/<number>/reviews --paginate > /tmp/pr_<number>_reviews.json
   gh api repos/{REPO}/pulls/<number>/comments --paginate > /tmp/pr_<number>_inline.json
   gh api graphql --paginate -f query='
   query($endCursor: String) {
     repository(owner: "{OWNER}", name: "{REPO_NAME}") {
       pullRequest(number: <number>) {
         reviewThreads(first: 100, after: $endCursor) {
           pageInfo { hasNextPage endCursor }
           nodes {
             isResolved
             comments(first: 1) {
               nodes { databaseId }
             }
           }
         }
       }
     }
   }' > /tmp/pr_<number>_threads.json
   ```
3. Write the reference script to `/tmp/pr_reader_<number>.py` (substituting PR_NUMBER)
4. Run the script. If user passed `--all`, pass it through so resolved threads are included:
   ```bash
   python3 /tmp/pr_reader_<number>.py           # default: unresolved only
   python3 /tmp/pr_reader_<number>.py --all     # show all threads including resolved
   ```
5. Read the output file, then return the file path + summary in your final message.

## Output Format

**CRITICAL: Write the full verbatim markdown to a file, then return the path + summary.**

Your final message should contain ONLY:
1. The file path where comments were saved
2. A short summary (3-8 bullet points) covering: how many comments/reviews, who commented, key topics raised, any action items or requests for changes, resolution stats (X resolved / Y unresolved threads)

Do NOT paste the full verbatim comment text into your final message — it's in the file.

## Important Rules

- **VERBATIM IN FILE, SUMMARY IN MESSAGE**: Write the complete, unmodified text of every comment and the PR description to the output file. Return only the file path and a short summary in your final message.
- **No PR diff or code analysis**: Focus on comments only, not code changes.
- **ALWAYS use `gh api` for reviews and inline comments**: Never use `gh pr view --json reviews` — its IDs are GraphQL node IDs that don't match inline comment `pull_request_review_id` fields.
- **Preserve markdown formatting** in comment bodies (code blocks, links, images, etc.).
- **Sort chronologically** within each thread.
- **Date formatting**: Convert ISO timestamps to human-readable format (e.g., "Jan 7, 2025 at 12:46 PM UTC").
- **Thread nesting**: Use blockquote nesting (`>`, `>>`, `>>>`) to show reply depth, up to 3 levels.

## Error Handling

- If `gh` CLI is not authenticated, inform the user to run `gh auth login`.
- If the PR number doesn't exist, report the error clearly.
- If the repository cannot be detected, ask the user to specify the repo in `owner/repo` format.
- If all sources return empty, confirm "No comments found on this PR."
