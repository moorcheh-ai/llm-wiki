# LLM Wiki — Moorcheh Edition
## Schema & Agent Instructions

> This is an enhanced version of Karpathy's llm-wiki.md pattern,
> augmented with Moorcheh's Information-Theoretic Search (ITS) for
> persistent, scalable, semantically-rich knowledge retrieval.
>
> Original pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
> Moorcheh Agent Skills: https://github.com/moorcheh-ai/agent-skills

---

## 🗂️ Directory Structure

```
project-root/
├── CLAUDE.md              ← This file — agent instructions
├── raw/                   ← Your source documents (read-only, never modified)
│   └── assets/            ← Downloaded images from clipped articles
├── wiki/                  ← LLM-generated knowledge base (agent writes here)
│   ├── index.md           ← Master catalog: every page, one-line summary, category
│   ├── log.md             ← Append-only activity log (## [YYYY-MM-DD] prefix)
│   ├── overview.md        ← Big-picture synthesis — evolves with every ingest
│   ├── glossary.md        ← Terms, definitions, deprecated names, style rules
│   └── sources/           ← One summary page per raw document
└── .obsidian/             ← Obsidian vault config (graph view, hotkeys, sidebar)
```

**Rule:** The agent reads from `raw/` but never writes to it. The agent owns `wiki/`.
The human never writes wiki pages manually — the agent handles all bookkeeping.

---

## 🧠 Moorcheh Integration

### Why Moorcheh

The file-based wiki is sufficient up to ~300 pages. Beyond that, navigation and
search degrade. Moorcheh solves this with its Information-Theoretic Search (ITS)
architecture, which computes semantic relevance without approximate nearest-neighbor
(ANN/HNSW) search — delivering better recall at any scale, with zero drift.

Additionally, Moorcheh adds:
- **Namespace isolation** — separate namespaces per topic or team
- **Metadata filtering** — filter by date, source, type, tag
- **Persistent memory** — wiki pages survive session resets
- **RAG-powered answers** — structured Q&A generation from wiki content

### Setup (one-time)

```bash
# 1. Install Moorcheh Agent Skills into your agent
npx skills add moorcheh-ai/agent-skills

# 2. Set your API key (get one free at console.moorcheh.ai)
export MOORCHEH_API_KEY="your-api-key"

# 3. Run onboarding
/moorcheh:quickstart

# 4. Create a namespace for this wiki
/moorcheh:namespaces create  →  name it after your topic (e.g., "wiki-research")
```

### Namespace Convention

| Wiki purpose        | Namespace name        |
|---------------------|-----------------------|
| Research topic      | `wiki-<topic>`        |
| Product knowledge   | `wiki-product`        |
| Competitive intel   | `wiki-competitive`    |
| Personal knowledge  | `wiki-personal`       |
| Team / internal     | `wiki-team`           |

---

## 📄 Page Types

The wiki contains the following page types. Every page should include YAML frontmatter.

```yaml
---
type: <type>          # entity | concept | source | comparison | analysis | overview | glossary
title: <title>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [source1.md, source2.md]   # raw files this page draws from
tags: [tag1, tag2]
moorcheh_uploaded: false            # flip to true after uploading to Moorcheh
---
```

| Type         | Purpose                                                              |
|--------------|----------------------------------------------------------------------|
| `entity`     | A person, company, product, or named thing                          |
| `concept`    | An idea, technique, or theme                                        |
| `source`     | Summary of one raw document                                         |
| `comparison` | Side-by-side analysis of two or more entities/approaches            |
| `analysis`   | Answer to a query worth preserving — saved from a Query session      |
| `overview`   | Big-picture synthesis across all sources                            |
| `glossary`   | Canonical terms, definitions, deprecated names                      |

---

## ⚙️ Workflows

### 🔵 SESSION START

At the beginning of every session:
1. Read `CLAUDE.md` (this file) to reload instructions
2. Read `wiki/index.md` for an overview of what's in the wiki
3. Read `wiki/log.md` (last 10 entries) to understand recent activity
4. Check for any `moorcheh_uploaded: false` pages in `wiki/` that need syncing

---

### 🟢 INGEST — Adding a New Source

**Trigger:** User says `ingest raw/<filename>`

**Standard LLM Wiki steps:**

1. Read the source file from `raw/`
2. Discuss key takeaways with the user — ask what to emphasize
3. Create `wiki/sources/<slug>.md` (type: source)
4. Extract entities, concepts, and claims. For each:
   - If a page exists: update it, flag any contradictions with `> ⚠️ CONTRADICTION:` blockquotes
   - If no page exists: create it
5. Add new terms to `wiki/glossary.md`
6. Update `wiki/index.md` with all new/updated pages
7. Update `wiki/overview.md` if the big picture has shifted
8. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <Source Title>
   Pages created: X | Updated: Y | Contradictions: Z
   ```

**Moorcheh enhancement — after standard steps:**

9. Upload all new and updated wiki pages to Moorcheh:
   ```
   /moorcheh:upload namespace "wiki-<topic>" file "<path-to-page.md>"
   ```
   Upload each new or updated page individually. After uploading, flip
   `moorcheh_uploaded: true` in the page's frontmatter.

10. Append to log:
    ```
    Moorcheh: uploaded N pages to namespace "wiki-<topic>"
    ```

---

### 🔍 QUERY — Answering Questions

**Trigger:** User asks a question about the wiki content

**Moorcheh-first approach (preferred at any scale):**

1. Parse the question for key concepts and entities
2. Search Moorcheh first with ITS scoring:
   ```
   /moorcheh:search query "<key concepts>" namespaces "wiki-<topic>" top_k 8
   ```
3. Use metadata filters when the query is time- or type-specific:
   ```
   /moorcheh:search query "<query> #type:entity" namespaces "wiki-<topic>"
   /moorcheh:search query "<query> #tags:competitive" namespaces "wiki-<topic>"
   ```
4. Read the returned pages fully before synthesizing an answer
5. Synthesize an answer with citations (link to wiki pages, not raw sources)

**Fallback — file-based approach (when Moorcheh is unavailable):**

1. Read `wiki/index.md` to identify relevant pages
2. Read those pages directly
3. Synthesize answer from wiki content

**For all queries:**

6. Ask: "Should I save this answer as a wiki page?"
7. If yes: create `wiki/analysis/<slug>.md` (type: analysis), update index
8. If yes and Moorcheh is connected: upload the new analysis page

---

### 🟡 GENERATE (RAG-Powered Answer)

**Trigger:** User says `answer: <question>` or requests a structured answer

Use Moorcheh's answer generation for higher-quality, cited responses:

```
/moorcheh:answer query "<question>" namespace "wiki-<topic>"
```

This combines ITS retrieval with LLM generation for structured, source-cited output.
Save the result as an analysis page if valuable.

---

### 🔴 LINT — Health Check

**Trigger:** User says `lint` or "health check the wiki"

**Standard LLM Wiki checks:**

1. Scan all pages for contradictions (look for `⚠️ CONTRADICTION:` markers)
2. Find orphan pages: pages with no inbound links from other wiki pages
3. Find stale claims: pages whose `sources` reference raw files that have since been superseded
4. Find concept gaps: entities/concepts mentioned in pages but lacking their own page
5. Check glossary coverage: are all technical terms in the glossary?
6. Report findings and ask which fixes to apply

**Moorcheh enhancement:**

7. Run namespace exploration to surface coverage gaps:
   ```
   /moorcheh:explore namespace "wiki-<topic>"
   ```
8. Find wiki pages not yet uploaded to Moorcheh (frontmatter: `moorcheh_uploaded: false`)
9. Suggest new search queries to investigate based on gaps

Log the lint run:
```
## [YYYY-MM-DD] lint | wiki-<topic>
Issues found: X contradictions, Y orphans, Z gaps
Moorcheh sync: N pages uploaded
```

---

## 🗒️ Index Format

`wiki/index.md` format — updated on every ingest:

```markdown
# Wiki Index — <Topic>
Last updated: YYYY-MM-DD | Pages: N | Sources: N

## Entities
- [[entity/company-name]] — One-line description (N sources)
- [[entity/person-name]] — One-line description

## Concepts
- [[concept/idea-name]] — One-line description

## Sources
- [[sources/article-slug]] — "Article Title" (YYYY-MM-DD)

## Comparisons
- [[comparison/a-vs-b]] — What it compares

## Analysis
- [[analysis/query-slug]] — Question this answers (YYYY-MM-DD)
```

---

## 📋 Log Format

`wiki/log.md` — append-only, newest at top:

```markdown
# Wiki Activity Log

## [YYYY-MM-DD] ingest | <Source Title>
Pages created: X | Updated: Y | Contradictions: Z
Moorcheh: uploaded N pages to "wiki-<topic>"

## [YYYY-MM-DD] query | <Question summary>
Answer saved: yes/no | Page: [[analysis/slug]]
Moorcheh: retrieved via ITS search

## [YYYY-MM-DD] lint | wiki-<topic>
Issues: X contradictions, Y orphans, Z gaps
Moorcheh sync: N pages uploaded
```

Parse tip: `grep "^## \[" wiki/log.md | head -10` for recent history.

---

## ✏️ Writing Conventions

- **Links:** Use `[[page-name]]` wiki links. Every entity, concept, and source referenced in a page must be linked.
- **Contradictions:** Mark with `> ⚠️ CONTRADICTION: <description>` blockquotes so they are easy to find and resolve.
- **Quotes:** Use `> "exact quote" — Source Name` blockquotes for direct quotes from raw sources.
- **Frontmatter:** Every page must have complete YAML frontmatter including `moorcheh_uploaded` status.
- **Headings:** H1 = page title; H2 = main sections; H3 = subsections. Keep consistent.
- **No orphans:** Every new page must be linked from at least one existing page plus `index.md`.

---

## 💡 Tips

- **Ingest one source at a time** and stay involved — read summaries, guide emphasis. Batch ingestion loses nuance.
- **Save your best queries** — analysis pages compound the wiki just like ingested sources do.
- **Use Obsidian graph view** (Cmd+G) often — it shows you hubs, orphans, and connection density.
- **Moorcheh namespaces are your topics** — one namespace per distinct knowledge domain.
- **Use metadata filters aggressively** — `#type:entity`, `#tags:competitive`, `#created:2026` narrow results instantly.
- **Don't write wiki pages yourself** — your job is to find good sources and ask good questions. Let the agent do the bookkeeping.
- **Sync after every ingest** — the `moorcheh_uploaded` flag in frontmatter is your sync status tracker.

---

## 🔧 Moorcheh Command Reference

```bash
# Search with ITS scoring
/moorcheh:search query "<terms>" namespaces "wiki-<topic>" top_k 10

# Search with metadata filter
/moorcheh:search query "<terms> #type:entity" namespaces "wiki-<topic>"

# Generate RAG-powered answer
/moorcheh:answer query "<question>" namespace "wiki-<topic>"

# Upload a wiki page
/moorcheh:upload namespace "wiki-<topic>" file "wiki/<path>.md"

# List namespaces
/moorcheh:namespaces

# Explore a namespace (coverage, gaps)
/moorcheh:explore namespace "wiki-<topic>"
```

---

## 📌 Why This Works

The LLM Wiki pattern solves the fundamental problem with RAG: knowledge is compiled
once and maintained, not re-derived on every query. Moorcheh takes this further by
replacing the file-index navigation with ITS semantic search — so queries get
better results, faster, at any scale, with metadata precision traditional RAG cannot
provide.

The human's job: find good sources, ask good questions.
The agent's job: ingest, maintain, cross-reference, upload, search.
The wiki's job: compound.

> "The tedious part of maintaining a knowledge base is not the reading or the thinking —
> it's the bookkeeping. And bookkeeping is exactly what AI is best at." — Karpathy
