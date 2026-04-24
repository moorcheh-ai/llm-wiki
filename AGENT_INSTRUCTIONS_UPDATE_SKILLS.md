# Agent Instructions: Update Moorcheh Agent Skills & LLM Wiki

**Date:** 2025-07-14
**Context:** These instructions come from a real-world session building an LLM Wiki from a 212-page PDF (365K characters). The session uncovered bugs, missing features, and workflow improvements that need to be pushed upstream to two repos.

**Target repos:**
1. `moorcheh-ai/agent-skills` — The Moorcheh agent skills package
2. `moorcheh-ai/llm-wiki` — The LLM Wiki starter repo

---

## Part 1: Moorcheh Agent Skills (`moorcheh-ai/agent-skills`)

### Issue 1: CRITICAL — Outdated default model ID in answer endpoint

**Problem:** The SDK's `answer.generate()` defaults to `anthropic.claude-sonnet-4-20250514-v1:0`, which returns a 500 error (Bedrock `AccessDeniedException`). Every RAG call fails unless the user manually overrides the model.

**Fix:**
- **SDK:** Update default `ai_model` parameter to `anthropic.claude-sonnet-4-6`
- **`references/generate_answer.md`:**
  - Parameter table says `aiModel` (camelCase) but SDK uses `ai_model` (snake_case) — fix the Python examples to use snake_case
  - Update the default model name in the description
  - Update the response example model ID
  - Add a note: "The default model may change as new models are released. Override with `ai_model` parameter if needed."
- **`scripts/generate_answer.py`:** Add a `--model` CLI argument so users can override without editing code

### Issue 2: CRITICAL — Missing `upload_file` endpoint

**Problem:** The SDK has `client.documents.upload_file()` that uploads files directly via multipart/form-data (`POST /namespaces/{name}/upload-file`). Supports `.md`, `.pdf`, `.txt`, `.docx`, `.xlsx`, `.json`, `.csv` up to 10MB. This endpoint is not documented in the skills at all.

Without it, agents default to the `upload_text` workflow (read file → build JSON → upload), which is error-prone and caused data loss in our session (see Issue 3).

**Fix:**
- **Create `references/upload_file.md`** with:
  - API endpoint, supported file types, 10MB limit
  - curl example, Python SDK example
  - "When to use this vs upload_text" comparison table
  - Note: "This is the safest method for uploading local files since the agent never reads or modifies source files"
- **Create `scripts/upload_file.py`** with:
  - `--namespace` and `--file` for single file upload
  - `--namespace` and `--dir` for batch upload of all files in a directory
  - `--ext` filter (default `.md`)
- **Update `SKILL.md`:** List `upload_file` FIRST under Data Operations as the **preferred method** for local files, above `upload_text`

### Issue 3: HIGH — No file safety guidance for upload workflows

**Problem:** When using `upload_text`, agents may read and modify source files in the same Python expression (e.g., to flip a `moorcheh_uploaded` frontmatter flag). This truncated 9 wiki files to 0 bytes in our session.

**Fix:** Add a "CRITICAL: File Safety During Upload" section to `SKILL.md`:
- Always prefer `upload_file` over `upload_text` for local files
- Never combine read and write on the same file in one expression
- Separate upload from metadata flag updates
- Include the safe pattern:
  ```python
  # Step 1: Read
  with open(path, 'r', encoding='utf-8') as f:
      content = f.read()
  # Step 2: Modify in memory
  content = content.replace('moorcheh_uploaded: false', 'moorcheh_uploaded: true')
  # Step 3: Write back
  with open(path, 'w', encoding='utf-8') as f:
      f.write(content)
  ```
- Also add a shorter warning to `references/upload_text.md`

### Issue 4: HIGH — `list_namespaces.py` crashes on API response format

**Problem:** Script assumes `client.namespaces.list()` returns a list, but SDK returns `{"namespaces": [...]}`. Crashes with `AttributeError: 'str' object has no attribute 'get'`.

**Fix:** Change line ~13:
```python
result = client.namespaces.list()
namespaces = result.get("namespaces", []) if isinstance(result, dict) else result
```

### Issue 5: MEDIUM — Unicode emoji crashes on Windows

**Problem:** All scripts use emoji (✅ ❌ 📁 ⏳) in print statements. On Windows `cp1252` encoding, these crash with `UnicodeEncodeError` — even when the underlying operation succeeded.

**Affected:** `list_namespaces.py`, `create_namespace.py`, `upload_text.py`, `search.py`, `generate_answer.py`

**Fix:** Replace emoji with ASCII: `[OK]`, `[ERROR]`, `[INFO]`, `[WAIT]`

### Issue 6: MEDIUM — Parameter naming mismatch in reference docs

**Problem:** `references/generate_answer.md` uses camelCase (`aiModel`, `chatHistory`) in Python SDK examples, but the SDK uses snake_case (`ai_model`, `chat_history`). The examples will fail.

**Fix:**
- Keep camelCase in REST API / curl examples (that's the wire format)
- Use snake_case in all Python SDK examples
- Add a note: "REST API uses camelCase. Python SDK uses snake_case."

---

## Part 2: LLM Wiki Repo (`moorcheh-ai/llm-wiki`)

### Feature 1: Deep Ingest workflow for large documents

**Problem:** Documents exceeding the LLM prompt window (~200K chars) get silently truncated. The agent only processes the first portion and never sees the rest. There is no error or warning.

**Solution:** Add a "Deep Ingest" workflow to the cookbooks. The key insight is that Moorcheh handles all file extraction, chunking, and indexing — the agent never needs to read the raw file locally.

1. Upload the raw file to a Moorcheh **staging namespace** via `upload_file` — Moorcheh extracts text, chunks it, and indexes it automatically (supports PDF, DOCX, XLSX, TXT, CSV, JSON, MD)
2. Wait for indexing (~15 seconds)
3. Agent queries the staging namespace to discover the document's structure (e.g., `query="table of contents chapters sections"` with `top_k=20`)
4. Agent queries chapter-by-chapter (`top_k=15`) to retrieve full content for each section
5. Agent builds wiki pages locally from the retrieved content (same as standard ingest)
6. Batch upload all wiki .md files to the **wiki namespace** via `upload_file`
7. Delete the staging namespace

**No local extraction needed.** No pymupdf, no text parsing, no TOC extraction scripts. Moorcheh handles all of that. The agent's only job is to upload the file and then query it.

**Files to create:**
- `references/deep_ingest.md` — Full workflow documentation with when-to-use guide
- `scripts/deep_ingest.py` — Simple script that creates a staging namespace and uploads the file. The agent handles the rest via search queries.

**Files to update:**
- `SKILL.md` in `moorcheh-cookbooks` — Add Deep Ingest to the cookbook index
- `CLAUDE.md` — Add deep ingest as an alternative to standard ingest for large documents
- `AGENTS.md` — Same update

**When to use:**

| Document size | Method |
|---|---|
| < 100K characters (text) | Standard ingest (read file directly) |
| 100K–200K characters (text) | Standard ingest (verify no truncation) |
| > 200K characters | Deep ingest |
| Any binary format (PDF/DOCX/XLSX) | Deep ingest — always safer, Moorcheh handles extraction |

### Feature 2: Update INGEST workflow in CLAUDE.md and AGENTS.md

Add to the INGEST section:

```
**For large documents (> 200K characters or any PDF/DOCX/binary format):**
Use the Deep Ingest workflow instead of reading the file directly.
See references/deep_ingest.md for the full procedure.

The agent should:
1. Check file type and size before reading
2. If binary format (PDF, DOCX, XLSX) or > 200K chars:
   - Upload the file to a Moorcheh staging namespace via upload_file
   - Moorcheh handles extraction, chunking, and indexing automatically
   - Query the staging namespace to build wiki pages
3. If plain text < 200K chars: standard ingest (read directly)
```

### Feature 3: Update upload instructions to use `upload_file`

In both `CLAUDE.md` and `AGENTS.md`, the Moorcheh upload step currently says:
```
/moorcheh:upload namespace "wiki-<topic>" file "<path-to-page.md>"
```

Update to explicitly recommend `upload_file` for local files:
```
# Preferred: upload file directly (agent never reads/modifies the file)
client.documents.upload_file(namespace_name="wiki-<topic>", file_path="wiki/<page>.md")

# Or batch upload all wiki pages:
python .agents/skills/moorcheh/scripts/upload_file.py --namespace "wiki-<topic>" --dir "wiki/"
```

### Feature 4: Add file type and size check to ingest workflow

Add a pre-check at the start of every ingest:
```
Before reading any source file:
1. Check file extension and size
2. If binary format (PDF, DOCX, XLSX) or file exceeds 200K characters:
   - Inform the user: "This document will be ingested via Moorcheh deep ingest."
   - Upload to staging namespace via upload_file (Moorcheh handles extraction)
   - Switch to deep ingest workflow automatically
3. If plain text < 200K chars: proceed with standard ingest
```

---

## Part 3: Testing Checklist

After applying all changes, verify:

- [ ] `python scripts/generate_answer.py --namespace "test" --query "hello"` — no 500 error
- [ ] `python scripts/upload_file.py --namespace "test" --file "test.md"` — uploads successfully
- [ ] `python scripts/upload_file.py --namespace "test" --dir "wiki/"` — batch uploads all .md files
- [ ] `python scripts/list_namespaces.py` — lists namespaces without crash
- [ ] All scripts run on Windows cmd.exe without `UnicodeEncodeError`
- [ ] Python SDK examples in all reference docs use snake_case parameters
- [ ] Deep ingest script extracts TOC from a PDF and uploads to staging
- [ ] `CLAUDE.md` and `AGENTS.md` reference deep ingest for large documents
- [ ] `SKILL.md` lists `upload_file` as preferred upload method

---

## Summary of What We Proved

In a single session, we ingested a 212-page physics book into an LLM Wiki:

1. **First attempt (standard ingest):** 365K chars truncated at ~200K. Agent silently dropped ~45% of the book (Einstein's GTR through Quantum Mechanics and the author's Queries). 9 wiki pages created, but incomplete.

2. **Deep ingest via Moorcheh:** Uploaded the raw file to a staging namespace (Moorcheh handled extraction and chunking) → queried 11 missing chapters → built 5 additional wiki pages covering the entire book. Zero truncation. No local text extraction needed.

3. **Batch upload via `upload_file`:** All 19 wiki pages uploaded to `wiki-personal` namespace in one command. No file corruption. No JSON building. No reading source files.

4. **RAG query:** Asked "What are the shortcomings of the Michelson-Morley experiments?" → Moorcheh returned a comprehensive, cited answer from the wiki using ITS semantic search + Claude Sonnet 4.

**The conclusion:** Moorcheh transforms the LLM Wiki from a pattern limited by the prompt window into a scalable knowledge system. It handles ingestion of large files in any format, provides the semantic search layer the wiki needs at scale, and closes the loop by making every wiki page and every query compound into a richer knowledge base.
