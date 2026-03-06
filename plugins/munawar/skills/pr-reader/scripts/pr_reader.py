#!/usr/bin/env python3
"""PR Comment Reader - organizes fetched PR comment JSON files into markdown.

Usage:
    python3 pr_reader.py <pr_number> [--all] [--output-dir <dir>]

Expects these files in /tmp/:
    pr_<number>_main.json     — gh pr view output
    pr_<number>_reviews.json  — REST API reviews
    pr_<number>_inline.json   — REST API inline comments
    pr_<number>_threads.json  — GraphQL review thread resolution status
"""
import json
import os
import re
import sys
from datetime import datetime
from collections import defaultdict


def parse_args():
    args = sys.argv[1:]
    if not args:
        print("Usage: pr_reader.py <pr_number> [--all] [--output-dir <dir>]", file=sys.stderr)
        sys.exit(1)

    pr_number = args[0]
    show_all = "--all" in args
    output_dir = ".scratch/outputs"

    for i, a in enumerate(args):
        if a == "--output-dir" and i + 1 < len(args):
            output_dir = args[i + 1]

    return pr_number, show_all, output_dir


def parse_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y at %I:%M %p UTC")
    except Exception:
        return date_str


def strip_bot_noise(body, author):
    if 'cursor' not in author.lower() and 'bugbot' not in author.lower():
        return body
    desc_match = re.search(
        r'<!-- DESCRIPTION START -->(.*?)<!-- DESCRIPTION END -->',
        body, flags=re.DOTALL
    )
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


def load_thread_resolution(pr_number):
    """Load thread resolution status from GraphQL output."""
    resolution_map = {}
    try:
        with open(f'/tmp/pr_{pr_number}_threads.json') as f:
            raw = f.read()
        decoder = json.JSONDecoder()
        pos = 0
        while pos < len(raw):
            raw_stripped = raw[pos:].lstrip()
            if not raw_stripped:
                break
            obj, end = decoder.raw_decode(raw_stripped)
            pos += len(raw) - len(raw_stripped) - pos + end
            nodes = (obj.get('data', {})
                     .get('repository', {})
                     .get('pullRequest', {})
                     .get('reviewThreads', {})
                     .get('nodes', []))
            for node in nodes:
                comments = node.get('comments', {}).get('nodes', [])
                if comments:
                    db_id = comments[0].get('databaseId')
                    if db_id is not None:
                        resolution_map[db_id] = node.get('isResolved', False)
    except FileNotFoundError:
        pass
    return resolution_map


def render_inline_comment(comment, depth=0):
    lines = []
    prefix = '>' * (depth + 1) + ' '
    author = comment['user']['login']
    b = strip_bot_noise(comment['body'], author)
    lines.append(f"{prefix}**@{author}** \u2014 {parse_date(comment['created_at'])}")
    for line in b.split('\n'):
        lines.append(f"{prefix}{line}")
    lines.append("")
    return lines


def main():
    pr_number, show_all, output_dir = parse_args()
    hide_resolved = not show_all

    # Load data
    with open(f'/tmp/pr_{pr_number}_main.json') as f:
        pr_data = json.load(f)

    with open(f'/tmp/pr_{pr_number}_reviews.json') as f:
        reviews = json.load(f)

    with open(f'/tmp/pr_{pr_number}_inline.json') as f:
        inline_comments = json.load(f)

    resolution_map = load_thread_resolution(pr_number)
    resolved_count = sum(1 for v in resolution_map.values() if v)
    unresolved_count = sum(1 for v in resolution_map.values() if not v)

    # Group inline comments by review and into threads
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

    def render_thread(top_comment):
        comment_id = top_comment['id']
        resolved = resolution_map.get(comment_id, None)

        if hide_resolved and resolved is True:
            return []

        lines = []
        file_path = top_comment.get('path', 'unknown')
        line_num = top_comment.get('line') or top_comment.get('original_line') or '?'

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

    # Build output
    out = []

    # Header
    out.append(f"# PR #{pr_data['number']}: {pr_data['title']}")
    out.append(
        f"**Author:** @{pr_data['author']['login']} | "
        f"**State:** {pr_data['state']} | "
        f"**Branch:** `{pr_data['headRefName']}` \u2192 `{pr_data['baseRefName']}`"
    )
    if resolution_map:
        filter_note = (" | \u26a0\ufe0f **Showing unresolved only** (pass --all for everything)"
                       if hide_resolved else "")
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

    # Code Reviews with inline comments
    out.append("## Code Reviews\n")
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

        review_id = review['id']
        review_inlines = inline_by_review.get(review_id, [])
        top_level = [c for c in review_inlines if c.get('in_reply_to_id') is None]

        if top_level:
            out.append("#### Inline Comments\n")
            for c in sorted(top_level, key=lambda x: (x.get('path', ''), x.get('created_at', ''))):
                out.extend(render_thread(c))
                rendered_inline_ids.add(c['id'])
                thread = threads.get(c['id'])
                if thread:
                    for r in thread['replies']:
                        rendered_inline_ids.add(r['id'])

        out.append("---\n")

    # Orphaned inline comments
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
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'pr-{pr_number}-comments.md')
    with open(output_path, 'w') as f:
        f.write('\n'.join(out))

    print(f"\u2713 Written to {output_path}")
    print(f"  Reviews: {len(reviews)}, Inline comments: {len(inline_comments)}, Conversation: {len(pr_data.get('comments', []))}")
    if resolution_map:
        print(f"  Threads: {resolved_count} resolved, {unresolved_count} unresolved")
        if hide_resolved:
            print(f"  (Resolved threads hidden — pass --all to include them)")


if __name__ == '__main__':
    main()
