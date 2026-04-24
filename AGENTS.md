# LLM Wiki — Moorcheh Edition
## Agent Instructions (AGENTS.md)

> This file is the equivalent of CLAUDE.md for agents that use AGENTS.md as their
> instruction file: OpenAI Codex, Gemini CLI, Windsurf, GitHub Copilot, and others.
> The content is identical to CLAUDE.md — only the filename differs.
>
> Original LLM Wiki pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
> Moorcheh Agent Skills: https://github.com/moorcheh-ai/agent-skills

---

## Directory Structure

```
project-root/
├── AGENTS.md              ← This file
├── CLAUDE.md              ← Same content, for Claude-based agents
├── raw/                   ← Source documents (read-only)
│   └── assets/            ← Downloaded images
├── wiki/                  ← Agent-generated knowledge base
│   ├── index.md
│   ├── log.md
│   ├── overview.md
│   ├── glossary.md
│   └── sources/
└── .obsidian/             ← Obsidian vault config
```

**Rule:** Read from `raw/`, write to `wiki/`. Never modify `raw/`. Never write wiki pages manually.

---

## Moorcheh Setup

```bash
npx skills add moorcheh-ai/agent-skills
export MOORCHEH_API_KEY="your-api-key"
```

Create a namespace for this wiki at [console.moorcheh.ai](https://console.moorcheh.ai).
Namespace naming convention: `wiki-<topic>` (e.g., `wiki-research`, `wiki-product`).

---

## Page Frontmatter

Every wiki page must include:

```yaml
---
type: entity | concept | source | comparison | analysis | overview | glossary
title: <title>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [list of raw files this page draws from]
tags: [tag1, tag2]
moorcheh_uploaded: false   # flip to true after uploading
---
```

---

## SESSION START

1. Read this file to reload instructions
2. Read `wiki/index.md` for wiki overview
3. Read last 10 entries of `wiki/log.md`
4. Find pages where `moorcheh_uploaded: false` and sync them

---

## INGEST

**Trigger:** `ingest raw/<filename>`

**Pre-check:** Before reading any source file, check its type and size:
- If **binary format** (PDF, DOCX, XLSX) or **> 200K characters**: use **DEEP INGEST** (below)
- If plain text/markdown under 200K characters: proceed with Standard Ingest

Large documents silently truncate in the LLM prompt window with no error. Deep Ingest eliminates this.

**Standard Ingest (small text files):**

1. Read source from `raw/`
2. Discuss key takeaways with user
3. Create `wiki/sources/<slug>.md`
4. Create or update entity and concept pages; flag contradictions with `> ⚠️ CONTRADICTION:`
5. Update `wiki/glossary.md`
6. Update `wiki/index.md`
7. Update `wiki/overview.md` if big picture shifted
8. Append to `wiki/log.md`: `## [YYYY-MM-DD] ingest | <Title>`
9. **Moorcheh:** Upload all new/updated pages using `upload_file` (preferred):
   ```python
   client.documents.upload_file(namespace_name="wiki-<topic>", file_path="wiki/<page>.md")
   ```
   Or batch: `python .agents/skills/moorcheh/scripts/upload_file.py --namespace "wiki-<topic>" --dir "wiki/"`
10. Log: `Moorcheh: uploaded N pages to "wiki-<topic>"`

---

## DEEP INGEST

**Trigger:** `ingest raw/<filename>` where file is PDF, DOCX, XLSX, or > 200K characters.

Moorcheh handles extraction, chunking, and indexing. The agent never reads the raw file.

1. Create staging namespace: `client.namespaces.create(namespace_name="staging-<slug>", type="text")`
2. Upload raw file: `client.documents.upload_file(namespace_name="staging-<slug>", file_path="raw/<file>")`
3. Wait 10–15 seconds for indexing
4. Discover structure: query `"table of contents chapters sections"` with `top_k=20`
5. Query chapter-by-chapter (`top_k=15`) to retrieve full content
6. For each chapter: follow Standard Ingest steps 2–8 (discuss, create pages, update glossary/index/overview)
7. Batch upload wiki pages: `upload_file.py --namespace "wiki-<topic>" --dir "wiki/"`
8. Delete staging: `client.namespaces.delete(namespace_name="staging-<slug>")`
9. Log: `## [YYYY-MM-DD] deep-ingest | <Title>` with method, pages created, staging deleted

---

## QUERY

**Trigger:** User asks a question

1. Search Moorcheh first:
   ```
   /moorcheh:search query "<key concepts>" namespaces "wiki-<topic>" top_k 8
   ```
2. Use metadata filters when relevant:
   ```
   /moorcheh:search query "<query> #type:entity" namespaces "wiki-<topic>"
   ```
3. Read returned pages fully
4. Synthesize answer with citations (wiki links, not raw source links)
5. Ask: "Should I save this as a wiki page?"
6. If yes: create `wiki/analysis/<slug>.md`, update index, upload to Moorcheh

**Fallback (Moorcheh unavailable):** Read `wiki/index.md` → drill into relevant pages.

---

## GENERATE

**Trigger:** `answer: <question>`

```
/moorcheh:answer query "<question>" namespace "wiki-<topic>"
```

Save result as `wiki/analysis/<slug>.md` if valuable.

---

## LINT

**Trigger:** `lint`

1. Find `⚠️ CONTRADICTION:` markers
2. Find orphan pages (no inbound links)
3. Find stale claims
4. Find concept gaps
5. Check glossary coverage
6. Run: `/moorcheh:explore namespace "wiki-<topic>"`
7. Find pages with `moorcheh_uploaded: false` and sync them
8. Append to log: `## [YYYY-MM-DD] lint | <results>`

---

## Writing Conventions

- Use `[[page-name]]` wiki links for all entities, concepts, and sources
- Mark contradictions: `> ⚠️ CONTRADICTION: <description>`
- Every page linked from at least one other page and from `index.md`
- Keep `moorcheh_uploaded` frontmatter accurate at all times

---

## Moorcheh Command Reference

```bash
/moorcheh:search query "<terms>" namespaces "wiki-<topic>" top_k 10
/moorcheh:search query "<terms> #type:entity" namespaces "wiki-<topic>"
/moorcheh:answer query "<question>" namespace "wiki-<topic>"
/moorcheh:upload namespace "wiki-<topic>" file "wiki/<page>.md"
/moorcheh:namespaces
/moorcheh:explore namespace "wiki-<topic>"
```
