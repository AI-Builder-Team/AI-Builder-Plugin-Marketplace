---
name: web-research
description: Web search, research, and page scraping via Perplexity + Firecrawl
argument-hint: "<query or URL>"
allowed-tools: [Bash, Read]
---

# Web Research

You have been given the following research request:

> $ARGUMENTS

## Your Task

Analyze the request, choose the appropriate mode, and run the command. Then synthesize results for the user.

### Step 1: Choose mode

- If it's a **URL** (starts with http/https) → use `--scrape`
- If it's a **simple factual question** (quick lookup, single fact) → use `--ask`
- If it's a **comparison or multi-source analysis** → use `--research`
- If it needs **reasoning about tradeoffs or decisions** → use `--reason`
- If it needs **exhaustive multi-source deep coverage** AND the user explicitly asks for deep research → use `--deep`
- If the user explicitly wants **raw ranked search results** → use `--search`

**Default to `--research` when unsure.** Do NOT use `--deep` unless the user explicitly asks for exhaustive/deep coverage (it's the slowest and most expensive mode).

### Step 2: Run the command

```bash
uv run --directory ~/.claude python ~/.claude/scripts/web_research.py --<mode> "$ARGUMENTS"
```

IMPORTANT: Always use `--directory ~/.claude` so uv finds the pyproject.toml with dependencies.

### Step 3: Follow up (bounded)

If the initial results include source URLs that look highly relevant and the answer feels incomplete, follow up by scraping **up to 4 of the most promising URLs**. Run scrapes in parallel where possible.

**Budget:** Maximum **10 research/ask/reason calls**, with up to **4 scrapes per research call** to read the most relevant sources in full. Synthesize what you have once you've exhausted useful leads or hit the limit.

### Step 4: Synthesize

After gathering results, write a clear summary for the user. Include source URLs at the end. Do NOT make additional API calls after synthesizing.

---

## Command Reference

### Modes

| Mode | Perplexity Model | Purpose | Cost |
|------|-----------------|---------|------|
| `--ask` | sonar | Quick fact with AI answer | Low |
| `--search` | (direct search) | Ranked results, no AI synthesis | Low |
| `--research` | sonar-pro | AI combines multiple sources | Medium |
| `--reason` | sonar-reasoning-pro | Chain-of-thought analysis | High |
| `--deep` | sonar-deep-research | Exhaustive multi-source research | Very High |
| `--scrape` | (firecrawl) | Fetch full page content from URL | Low |

### Search options (for `--search`)
| Parameter | Description |
|-----------|-------------|
| `--max-results N` | Number of results (1-20, default: 10) |
| `--recency` | Filter: `day`, `week`, `month`, `year` |
| `--domains` | Limit to specific domains |

### Scrape options (for `--scrape`)

**IMPORTANT:** `--scrape` takes ONLY a URL. Do NOT pass additional query text after the URL -- it will cause an argparse error.
```bash
# Correct:
uv run --directory ~/.claude python ~/.claude/scripts/web_research.py --scrape "https://example.com/page"

# WRONG (will fail):
uv run --directory ~/.claude python ~/.claude/scripts/web_research.py --scrape "https://example.com/page" "tell me about X"
```

| Parameter | Description |
|-----------|-------------|
| `--format` | `markdown`, `html`, `text` (default: markdown) |
| `--full-page` | Include sidebars/nav (default: main content only) |

### Global options
| Parameter | Description |
|-----------|-------------|
| `--model` | Override Perplexity model selection |

## API Keys Required

- `PERPLEXITY_API_KEY` — for search/ask/research/reason/deep modes
- `FIRECRAWL_API_KEY` — for scrape mode

Both loaded from environment or `~/.claude/.env`.
