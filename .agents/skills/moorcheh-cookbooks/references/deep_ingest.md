# Deep Ingest — Large Document Ingestion via Moorcheh

A reusable workflow for ingesting large documents (books, reports, manuals) that exceed the LLM prompt window. Instead of trying to read the entire document at once, this workflow uploads the raw file to Moorcheh — which handles all extraction, chunking, and indexing — then the agent queries chapter by chapter to build wiki pages with full coverage.

## The Problem

Large documents (200K+ characters) get truncated when read into an LLM prompt window. The agent only processes the first portion, silently dropping the rest. There is no error — the agent simply never sees the later content. Binary formats (PDF, DOCX, XLSX) compound the problem since they require extraction before reading.

## The Solution: Upload First, Query to Build

```
Raw file → upload_file to Moorcheh staging → Moorcheh extracts, chunks, indexes
         → Agent queries staging chapter-by-chapter → Builds wiki pages from results
         → Wiki pages uploaded to wiki namespace via upload_file
         → Delete staging namespace
```

**No local extraction needed.** No pymupdf, no text parsing, no TOC scripts. Moorcheh handles extraction for PDF, DOCX, XLSX, TXT, CSV, JSON, and MD files automatically.

## Prerequisites

- Moorcheh API key set
- A wiki namespace already created (e.g. `wiki-personal`)
- The `upload_file` skill available

## Workflow

### Step 1: Upload the raw file to a staging namespace

Create a temporary staging namespace and upload the full document. Moorcheh extracts text, chunks it, and indexes it for semantic search.

```python
from moorcheh_sdk import MoorchehClient

client = MoorchehClient(api_key=os.environ["MOORCHEH_API_KEY"])

# Create staging namespace
client.namespaces.create(namespace_name="staging-ingest", type="text")

# Upload the raw file — Moorcheh handles extraction and indexing
client.documents.upload_file(
    namespace_name="staging-ingest",
    file_path="raw/book.pdf"
)
```

Wait 10–15 seconds for Moorcheh to finish processing.

**Note:** If the file exceeds 10MB, extract text to a `.txt` file first and upload that instead.

### Step 2: Discover the document structure

Query the staging namespace to find chapters, sections, and topics:

```python
results = client.similarity_search.query(
    namespaces=["staging-ingest"],
    query="table of contents chapters sections topics",
    top_k=20
)
```

The agent reads the results to identify the document's structure and plan which chapters to query.

### Step 3: Query chapter-by-chapter to build wiki pages

For each chapter or topic, search the staging namespace to retrieve the relevant content:

```python
results = client.similarity_search.query(
    namespaces=["staging-ingest"],
    query="<chapter title or topic>",
    top_k=15  # use high top_k for full chapter coverage
)
```

The agent reads the search results and creates/updates wiki pages following the standard ingest workflow (source summary, entity pages, concept pages, glossary, index, overview).

### Step 4: Upload finished wiki pages to the wiki namespace

Use `upload_file` to batch upload all wiki pages:

```bash
python .agents/skills/moorcheh/scripts/upload_file.py \
  --namespace "wiki-personal" --dir "wiki/"
```

### Step 5: Clean up the staging namespace

```python
client.namespaces.delete(namespace_name="staging-ingest")
```

## Script

```bash
# Upload file to staging (Moorcheh handles extraction)
python .agents/skills/moorcheh/scripts/deep_ingest.py \
  --file "raw/book.pdf" \
  --wiki-namespace "wiki-personal" \
  --staging-namespace "staging-ingest"
```

The script creates the staging namespace, uploads the file, waits for indexing, and prints instructions for the agent to proceed with chapter-by-chapter queries.

## When to Use Deep Ingest vs Standard Ingest

| Document | Method |
|---|---|
| Plain text < 100K characters | Standard ingest (read file directly) |
| Plain text 100K–200K characters | Standard ingest may work, verify no truncation |
| Plain text > 200K characters | **Deep ingest** |
| Any PDF, DOCX, XLSX | **Deep ingest** — always safer, Moorcheh handles extraction |

## Important Notes

- The staging namespace is temporary — delete it after the ingest is complete
- Use `top_k=15` or higher when querying chapters to ensure full coverage
- Wait 10–15 seconds after `upload_file` before querying — Moorcheh needs time to index
- The agent should process one chapter at a time, creating/updating wiki pages incrementally
- After all chapters are processed, run a final pass to update `index.md`, `overview.md`, and `glossary.md`
- If the raw file exceeds 10MB, extract text to `.txt` first — the 10MB limit is on the upload, not on the content Moorcheh can index
