# LLM Wiki + Moorcheh

**Andrej Karpathy's self-maintaining knowledge base pattern — extended with Moorcheh's Information-Theoretic Search for persistent, scalable, semantic memory.**

> *"The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping. And bookkeeping is exactly what AI is best at."*
> — Andrej Karpathy

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-moorcheh--ai-0D9488)](https://github.com/moorcheh-ai/agent-skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What Is This?

In April 2026, Andrej Karpathy published a [GitHub Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) describing a pattern he'd been using for personal research: instead of querying raw documents with RAG on every question, let an LLM **build and maintain a structured wiki** from your sources — once — and query that.

The idea went viral. 5,000+ stars, 1,900+ forks, 485+ comments in days. The community immediately started building on it.

**This repo is the Moorcheh-enhanced version of that pattern.**

---

## Why You Need Moorcheh

Karpathy's original design is elegant, but it has two fundamental limitations:

**1. It silently fails on large documents.** The LLM prompt window has a hard limit (~200K characters). When you ingest a book, a research paper, or a technical manual that exceeds this limit, the agent truncates the file with no error and no warning. A 365K-character book loses ~45% of its content. You get an incomplete knowledge base and you don't even know it.

**2. It can't handle binary formats.** PDFs, Word documents, spreadsheets — the most common document formats in the real world — require extraction tools just to read. That's another dependency, another point of failure, and another reason your ingest might silently produce incomplete results.

Moorcheh solves both problems. When you combine LLM Wiki with Moorcheh's backend:

- **Full document ingestion** — Upload any file (PDF, DOCX, XLSX, TXT, CSV, MD) directly to Moorcheh. It handles extraction, chunking, and indexing. The agent queries Moorcheh chapter-by-chapter to build wiki pages with **zero truncation**, regardless of file size.
- **ITS semantic search** — Information-Theoretic Search that scores relevance without ANN/HNSW approximation. Your wiki becomes searchable at any scale.
- **Metadata filtering** — filter by page type, tags, date, source
- **Namespace isolation** — clean separation between topics or teams
- **Persistent memory** — wiki pages survive session resets. Your knowledge base is permanent.
- **No scale ceiling** — the same workflow at 50 pages or 5,000

The wiki still lives on disk as plain markdown. Obsidian still works. Git still works. Moorcheh is the backend that makes it all work at scale — handling the file extraction, semantic indexing, and persistent storage that local LLMs simply cannot do.

> **You will need a free Moorcheh API key.** Sign up at [console.moorcheh.ai](https://console.moorcheh.ai) and generate your key in the API Keys section. The free tier is sufficient for personal wikis.

---

## The Core Idea

Most AI knowledge tools work like this:

```
Question → Search raw documents → Generate answer → Answer disappears
```

LLM Wiki works like this:

```
New source → Agent builds/updates wiki pages → Wiki compounds over time
Question   → Agent searches wiki → Cited answer → Answer saved back to wiki
```

**The wiki is a persistent, compounding artifact.** Every source you add and every question you ask makes it richer. The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read.

With Moorcheh, the search layer matches the quality of the wiki itself — and the ingestion layer can handle documents of any size and format.

```
Original LLM Wiki:          raw file → LLM reads directly → truncated at prompt window
LLM Wiki + Moorcheh:        raw file → Moorcheh extracts & indexes → agent queries → full coverage
```

---

## Architecture

```
project-root/
├── CLAUDE.md          ← Schema for Claude Code / Claude-based agents
├── AGENTS.md          ← Schema for Codex, Gemini CLI, Windsurf, Copilot
├── llm-wiki.md        ← Karpathy's original idea file (reference)
│
├── raw/               ← Your source documents
│   ├── .gitkeep
│   └── assets/        ← Downloaded images (Obsidian Web Clipper)
│
├── wiki/              ← Agent-generated knowledge base
│   ├── index.md       ← Master catalog: every page + one-line summary
│   ├── log.md         ← Append-only activity timeline
│   ├── overview.md    ← Big-picture synthesis
│   ├── glossary.md    ← Terms, definitions, style rules
│   └── sources/       ← One summary per raw document
│
└── .obsidian/         ← Pre-configured vault (graph view, hotkeys, sidebar)
```

**Three layers:**

| Layer | Folder | Owner |
|---|---|---|
| Raw sources | `raw/` | You — immutable, never modified by agent |
| The wiki | `wiki/` | Agent — creates, updates, cross-references |
| The schema | `CLAUDE.md` / `AGENTS.md` | You + agent — edit to fit your domain |

**The Moorcheh layer** sits alongside the wiki: after every ingest, new and updated pages are uploaded to a Moorcheh namespace. Queries go to Moorcheh first, not to `index.md`.

---

## Quickstart

### Prerequisites

- A **[Moorcheh API key](https://console.moorcheh.ai)** — sign up for free, then go to API Keys to generate one
- An AI agent: [Claude Code](https://claude.ai/code), [Cursor](https://cursor.sh), Codex, Gemini CLI, or any agent that reads `CLAUDE.md` / `AGENTS.md`
- [Obsidian](https://obsidian.md) (free — optional but strongly recommended)

### 1. Clone and install

```bash
git clone https://github.com/moorcheh-ai/llm-wiki
cd llm-wiki

# Install Moorcheh Agent Skills into your agent
npx skills add moorcheh-ai/agent-skills

# Install the Python SDK
pip install moorcheh-sdk

# Set your API key (get one free at console.moorcheh.ai)
export MOORCHEH_API_KEY="your-api-key"
```

> **Don't have an API key yet?** Go to [console.moorcheh.ai](https://console.moorcheh.ai), create a free account, and generate your key in the API Keys section. The key looks like `KJ3GgW...bhwx` and goes in the `MOORCHEH_API_KEY` environment variable.

### 2. Run onboarding and create your namespace

In your agent:

```
/moorcheh:quickstart
```

Then create a namespace for your wiki. Use the `wiki-<topic>` convention:

```
/moorcheh:namespaces
```

Examples: `wiki-research`, `wiki-product`, `wiki-competitive`, `wiki-personal`

### 3. Open in your agent + Obsidian

- Open the project folder in your agent (Claude Code, Cursor, etc.)
- Open the same folder as an Obsidian vault
- The agent reads `CLAUDE.md` automatically and understands the full wiki structure

### 4. Drop a source and ingest

```bash
# Any document works
cp ~/Downloads/my-report.pdf raw/
```

Then in your agent:

```
ingest raw/my-report.pdf
```

The agent will:
- Read the document
- Discuss key takeaways with you
- Create `wiki/sources/my-report.md`
- Create or update entity and concept pages
- Extend the glossary
- Update the index and overview
- Upload all new/updated pages to your Moorcheh namespace
- Log everything with a timestamp

Watch the pages appear in Obsidian's graph view in real time.

### 5. Ask questions

```
What are the main risks identified across all my sources?
```

The agent searches Moorcheh with ITS scoring, reads the top pages, and synthesizes a cited answer. If the answer is worth keeping, it saves it as `wiki/analysis/<slug>.md` and uploads it — your questions compound the wiki just like sources do.

### 6. Lint occasionally

```
lint
```

Every 10 ingests or so. The agent checks for contradictions, orphan pages, stale claims, missing cross-references, and Moorcheh sync gaps.

---

## Three Core Operations

### Ingest

```
ingest raw/<filename>
```

Agent reads the source → creates/updates wiki pages → uploads to Moorcheh → logs the run.
One source typically touches 10–15 wiki pages.

### Query

Ask any question in natural language.

Agent searches Moorcheh first (ITS scoring + optional metadata filters), reads top pages, synthesizes a cited answer. Valuable answers are saved back as `wiki/analysis/` pages.

**With metadata filters:**
```
What entity pages do we have about competitors? #type:entity #tags:competitive
What was added in the last month? #created:2026-03
```

### Lint

```
lint
```

Agent health-checks for: contradictions, orphan pages, stale claims, concept gaps, glossary coverage, Moorcheh sync status.

### Deep Ingest (Large Documents)

For documents that exceed the LLM prompt window (200K+ characters) or binary formats (PDF, DOCX, XLSX):

```
ingest raw/large-book.pdf
```

The agent automatically detects large/binary files and switches to Deep Ingest:

1. Uploads the raw file to a Moorcheh **staging namespace** — Moorcheh extracts text, chunks, and indexes automatically
2. Queries the staging namespace chapter-by-chapter to retrieve full content
3. Builds wiki pages from the results (same quality as standard ingest, but with zero truncation)
4. Batch uploads all wiki pages to the permanent wiki namespace
5. Deletes the staging namespace

**Why this matters:** Standard LLM Wiki silently truncates large files at the prompt window boundary. A 365K-character book loses ~45% of its content with no error. Deep Ingest via Moorcheh guarantees full coverage for any file size and format.

---

## Moorcheh Commands

```bash
# Semantic search with ITS scoring
/moorcheh:search query "<terms>" namespaces "wiki-<topic>" top_k 10

# Search with metadata filter
/moorcheh:search query "<terms> #type:entity" namespaces "wiki-<topic>"
/moorcheh:search query "<terms> #tags:competitive" namespaces "wiki-<topic>"

# RAG-powered answer generation
/moorcheh:answer query "<question>" namespace "wiki-<topic>"

# Upload a wiki page
/moorcheh:upload namespace "wiki-<topic>" file "wiki/<page>.md"

# Explore a namespace (coverage, gaps)
/moorcheh:explore namespace "wiki-<topic>"

# List all namespaces
/moorcheh:namespaces
```

---

## Tips

**Ingest one source at a time.** Stay involved — read the summaries, guide what to emphasize. Batch ingestion works but loses nuance.

**Save your best questions.** When the agent produces a useful answer, save it as a wiki page. Analysis compounds just like sources do.

**Use Obsidian graph view** (Cmd+G). The visual map shows which pages are hubs, which are isolated, and how your knowledge connects. It's the most satisfying way to watch your wiki grow.

**Edit the schema.** `CLAUDE.md` is not locked. If you need a new page type for your domain — `api-endpoint`, `customer-segment`, `recipe` — add it to the schema and tell the agent. The wiki adapts.

**Check the glossary before writing.** Every time you write something based on the wiki, open `wiki/glossary.md` first. It has the right terms, the deprecated ones, and the reasons behind each choice.

**Use Obsidian Web Clipper** to convert web articles to markdown. Drop the `.md` file into `raw/` and ingest.

---

## Page Types and Frontmatter

Every wiki page includes YAML frontmatter:

```yaml
---
type: entity | concept | source | comparison | analysis | overview | glossary
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw-file-1.pdf, raw-file-2.md]
tags: [tag1, tag2]
moorcheh_uploaded: false   # flipped to true after upload
---
```

The `moorcheh_uploaded` flag is your sync status tracker. The agent maintains it automatically. Run `lint` to find any pages that slipped through.

---

## Namespace Convention

| Wiki purpose | Namespace |
|---|---|
| Research topic | `wiki-<topic>` |
| Product knowledge | `wiki-product` |
| Competitive intelligence | `wiki-competitive` |
| Personal knowledge | `wiki-personal` |
| Team / internal | `wiki-team` |

For multiple concurrent wikis, create one namespace per topic. They stay completely separate in Moorcheh.

---

## Why Not Just RAG?

| | Traditional RAG | LLM Wiki (no Moorcheh) | LLM Wiki + Moorcheh |
|---|---|---|---|
| Knowledge accumulation | None — re-derived every query | Compounds over time | Compounds over time |
| Large document support | Chunk-based (lossy) | **Silent truncation at prompt window** | **Full coverage via Moorcheh extraction** |
| File format support | Depends on pipeline | Text/markdown only | PDF, DOCX, XLSX, TXT, CSV, JSON, MD |
| Cross-document connections | Re-synthesized each time | Built into the wiki | Built into the wiki |
| Search quality | Keyword or approximate vector | Flat index.md | ITS semantic scoring with no ANN drift |
| Metadata filtering | Limited | None | Full — type, tag, date, source |
| Scale ceiling | Degrades with volume | Degrades past ~300 pages | Designed for scale |
| Transparency | Black-box chunks | Readable markdown | Readable markdown |
| Version history | None | Git | Git |
| Session persistence | Lost on close | Lost on close | Permanent — wiki + Moorcheh namespace |

The middle column is the key insight: **the original LLM Wiki pattern is great for small documents but breaks silently on large ones.** Moorcheh is what makes it production-ready.

---

## Related Projects

- [moorcheh-ai/agent-skills](https://github.com/moorcheh-ai/agent-skills) — Moorcheh Agent Skills (install with `npx skills add`)
- [Karpathy's original llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — The idea file this is based on
- [balukosuri/llm-wiki-karpathy](https://github.com/balukosuri/llm-wiki-karpathy) — A great beginner-friendly implementation of the base pattern

---

## Resources

- [Moorcheh Documentation](https://docs.moorcheh.ai)
- [Moorcheh Console](https://console.moorcheh.ai)
- [Python SDK](https://docs.moorcheh.ai/python-sdk/introduction)
- [MCP Server](https://docs.moorcheh.ai/integrations/mcp/overview)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Getting Your Moorcheh API Key

1. Go to [console.moorcheh.ai](https://console.moorcheh.ai)
2. Sign up for a free account
3. Navigate to the **API Keys** section
4. Click **Generate New Key**
5. Copy the key and set it as an environment variable:
   ```bash
   # Linux / macOS
   export MOORCHEH_API_KEY="your-api-key"

   # Windows PowerShell
   $env:MOORCHEH_API_KEY = "your-api-key"

   # Windows CMD
   set MOORCHEH_API_KEY=your-api-key
   ```

The free tier includes enough namespaces and storage for personal wikis. See [Moorcheh pricing](https://moorcheh.ai) for team and enterprise tiers.

---

*Built on Karpathy's LLM Wiki pattern. Extended by [Moorcheh](https://moorcheh.ai).*
