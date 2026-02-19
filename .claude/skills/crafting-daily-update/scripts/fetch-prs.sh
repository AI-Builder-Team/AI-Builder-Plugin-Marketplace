#!/bin/bash

# Fetch PRs for daily standup update
# Returns JSON with merged (N days ago) and open PRs for current user
# For merged PRs, includes reviewer information
# Usage: fetch-prs.sh [--merged-days N]

set -e

# Default to 1 day if not specified
MERGED_DAYS=${1:-1}

# Calculate the date N days ago (handle both macOS and Linux)
if date -v-${MERGED_DAYS}d +%Y-%m-%d &>/dev/null; then
    # macOS
    LOOKBACK_DATE=$(date -v-${MERGED_DAYS}d +%Y-%m-%d)
else
    # Linux
    LOOKBACK_DATE=$(date -d "$MERGED_DAYS days ago" +%Y-%m-%d)
fi

echo "Fetching PRs for $(gh api user -q .login)..." >&2
echo "Looking for PRs merged on or after: $LOOKBACK_DATE (last $MERGED_DAYS days)" >&2
echo "" >&2

# Fetch PRs merged in the last N days and enrich with reviewer info
echo '{"merged":'
gh pr list \
    --author "@me" \
    --state merged \
    --search "merged:>=$LOOKBACK_DATE" \
    --json number,title,url,body,reviews \
    --limit 100

# Fetch open PRs
echo ',"open":'
gh pr list \
    --author "@me" \
    --state open \
    --json number,title,url,body \
    --limit 100

echo '}'
