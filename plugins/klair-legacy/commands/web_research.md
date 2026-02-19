# Web Research Command

You are conducting efficient web research to answer the user's query with high-quality, well-sourced information.

## Research Query
The user wants to research:
```
{{ARGS}}
```

## Workflow

### Phase 1: Research Strategy
Launch a Plan agent to analyze the query and determine **3 strategic search query variations** that approach the topic from different angles.

The Plan agent should:
- Break down the query into key aspects
- Identify 3 specific web search queries (different angles/perspectives)
- Consider what types of sources would be most valuable
- Return the 3 search queries

### Phase 2: Broad Search
**Ask the user:**
1. Path to store research results (default: current directory)
2. Name for the research folder

Then launch **3 Task agents in parallel** (use single message with multiple Task tool calls). Each agent should:
- Execute one web search query using WebSearch tool
- Collect search results (URLs, titles, snippets)
- Return structured list of results
- **Do NOT use WebFetch yet**

### Phase 3: Smart Selection
After all search agents complete:
1. Consolidate all search results from the 3 searches
2. Analyze and select **10-15 most relevant URLs** based on:
   - Relevance to the original query
   - Source authority (official docs, established sites)
   - Diversity of perspectives
   - Recency of content
3. Create **`search_references.md`** containing:
   - All search results organized by search query (with URLs and descriptions)
   - Clear marking of the 10-15 selected URLs for deep-dive (use ⭐ or similar marker)

### Phase 4: Deep Dive
Create `references/` folder, then launch **10-15 Task agents in parallel** (one per selected URL). Each agent should:
- Use WebFetch to retrieve detailed content from assigned URL
- Extract ONLY information relevant to the original query
- Synthesize key points, quotes, and evidence
- Save to `references/reference_01.md`, `reference_02.md`, etc. (sequential numbering)
- Include source URL at the top of each file

**Important**: Launch all agents in a single message with multiple tool calls for maximum efficiency.

### Phase 5: Final Synthesis
After all deep-dive agents complete:
1. Read all reference files from the references/ folder
2. Create **`answer.md`** with:
   - Concise summary answering the original query (2-3 paragraphs)
   - Key findings with references to supporting files (e.g., "See reference_03.md")
   - Well-structured markdown with headers and lists

## Output Structure
```
[user-path]/[research-folder]/
├── answer.md
├── search_references.md
└── references/
    ├── reference_01.md
    ├── reference_02.md
    └── ...
```

## Important Guidelines
- Focus on accuracy and source quality
- Extract only relevant information in reference files (not everything from the page)
- Use clear, scannable markdown formatting
- Launch Task agents in parallel for efficiency
- Keep files concise and targeted to the original query
- If information is limited, note this explicitly in answer.md

## Success Criteria
- User receives a clear, concise answer to their query
- 10-15 high-quality sources investigated in depth
- All claims backed by evidence in reference files
- Clean folder structure with exactly 3 components (answer.md, search_references.md, references/)
- Execution completes efficiently with parallel processing
