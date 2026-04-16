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

Karpathy's original design is elegant and works well up to a few hundred wiki pages. Beyond that, navigating a flat folder of markdown files degrades — and the index.md approach has no semantic understanding, no metadata filtering, and no relevance scoring.

Moorcheh solves exactly that. By uploading your wiki pages to a Moorcheh namespace after every ingest, your agent gains:

- **ITS semantic search** — Information-Theoretic Search that scores relevance without ANN/HNSW approximation
- **Metadata filtering** — filter by page type, tags, date, source
- **Namespace isolation** — clean separation between topics or teams
- **No scale ceiling** — the same workflow at 50 pages or 5,000

The wiki still lives on disk as plain markdown. Obsidian still works. Git still works. Moorcheh is the search and memory layer that sits underneath — invisible until you need it, essential when you do.

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

With Moorcheh, the search layer matches the quality of the wiki itself.

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

- A [Moorcheh account](https://console.moorcheh.ai) (free tier available)
- An AI agent: [Claude Code](https://claude.ai/code), [Cursor](https://cursor.sh), Codex, Gemini CLI, or any agent that reads `CLAUDE.md` / `AGENTS.md`
- [Obsidian](https://obsidian.md) (free — optional but strongly recommended)

### 1. Clone and install

```bash
git clone https://github.com/moorcheh-ai/llm-wiki
cd llm-wiki

# Install Moorcheh Agent Skills into your agent
npx skills add moorcheh-ai/agent-skills

# Set your API key
export MOORCHEH_API_KEY="your-api-key"
```

Get your API key at [console.moorcheh.ai](https://console.moorcheh.ai).

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

| | Traditional RAG | LLM Wiki + Moorcheh |
|---|---|---|
| Knowledge accumulation | None — re-derived every query | Compounds with every source and query |
| Cross-document connections | Re-synthesized each time | Already built into the wiki |
| Search quality | Keyword or approximate vector | ITS semantic scoring with no ANN drift |
| Metadata filtering | Limited | Full — type, tag, date, source |
| Scale ceiling | Degrades with volume | Designed for scale |
| Transparency | Black-box chunks | Readable, editable markdown pages |
| Version history | None | Git — full history, branching, collaboration |
| Session persistence | Lost on close | Permanent — wiki + Moorcheh namespace |

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

*Built on Karpathy's LLM Wiki pattern. Extended by [Moorcheh](https://moorcheh.ai).*
