---
name: moorcheh
description: Use this skill to interact with Moorcheh, the Universal Memory Layer for Agentic AI. Provides semantic search with ITS (Information-Theoretic Scoring), namespace management, text and vector data operations, and AI-powered answer generation (RAG). Use when building applications that need semantic search, knowledge bases, document Q&A, AI memory systems, or retrieval-augmented generation.
---

# Moorcheh — Universal Memory Layer Operations

This skill provides comprehensive access to the Moorcheh platform including namespace management, data operations, semantic search with ITS scoring, and AI-powered answer generation.

## Moorcheh Account

If the user does not have an account yet, direct them to the console to register and create a free account.

Create a Moorcheh account at [console.moorcheh.ai](https://console.moorcheh.ai).

## Environment Variables

```bash
export MOORCHEH_API_KEY="your-api-key-here"
```

For full environment setup, see [Environment Requirements](references/environment_requirements.md).

## Script Index

### Namespace Management

- [Create Namespace](references/create_namespace.md): Use to **create a new text or vector namespace** for organizing data. Text namespaces handle automatic embedding; vector namespaces require pre-computed embeddings.
- [List Namespaces](references/list_namespaces.md): Use to **discover what namespaces exist** in the account. This should be the first step before any operation.
- [Delete Namespace](references/delete_namespace.md): Use to **permanently remove a namespace** and all its data. This action is irreversible.

### Data Operations

- [Upload File](references/upload_file.md): **Preferred method for local files.** Upload `.md`, `.pdf`, `.txt`, `.docx`, `.xlsx`, `.json`, or `.csv` files directly to a text namespace. The file is never read or modified by the agent — Moorcheh handles extraction and embedding.
- [Upload Text Data](references/upload_text.md): Use to **upload text documents with metadata** to a text namespace when you have content in memory or need custom metadata per document.
- [Upload Vectors](references/upload_vectors.md): Use to **upload pre-computed vector embeddings** to a vector namespace. Best when you have your own embedding pipeline.
- [Delete Data](references/delete_data.md): Use to **remove specific documents or vectors** from a namespace.
- [Create Example Data](references/example_data.md): Use to **create sample data for demos and testing** when no data is available.

### Search & AI

- [Semantic Search](references/search.md): **Primary search operation.** Performs semantic search across one or more namespaces using ITS scoring. Supports text queries, metadata filters, keyword filters, and relevance thresholds.
- [Generate AI Answer](references/generate_answer.md): Use to **generate AI-powered answers from your data (RAG)**. Searches relevant context and synthesizes a natural-language answer. Supports chat history, custom prompts, and structured output.

## Recommendations

- Always run **List Namespaces** first to discover available data before searching or uploading.
- For text data, prefer **text namespaces** — Moorcheh handles embedding automatically.
- Use **ITS scoring thresholds** (0.0–1.0) to control result quality. Higher = stricter matching.
- The **Generate Answer** endpoint is the primary RAG capability — use it for Q&A over documents.

## CRITICAL: File Safety During Upload

**Always prefer `upload_file` over `upload_text` when uploading local files.** The `upload_file` endpoint sends the file directly to Moorcheh without the agent ever reading or modifying it — eliminating the risk of accidental file corruption.

If you must use `upload_text` (e.g. for custom metadata), follow these rules:

1. **Read files in read-only mode.** Open files only with `open(path, 'r')` to read their content. Never open source files for writing during the upload step.
2. **Separate upload from metadata updates.** If you need to update frontmatter flags (e.g. `moorcheh_uploaded: true`) after a successful upload, do it as a distinct step — read the full content first, close the file, then write the updated content.
3. **Never use read-write one-liners** like `open(f).read()` combined with `open(f, 'w').write()` in the same expression or loop — this can truncate files to 0 bytes.
4. **Preferred pattern for flag updates:**
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

## Output Formats

- Search results include `id`, `score`, `label` (relevance category), `text`, and `metadata`.
- AI answers include `answer`, `model`, `contextCount`, and optional `structuredData`.

## Error Handling

- `401 Unauthorized`: Verify `MOORCHEH_API_KEY` is set and valid
- `404 Namespace not found`: Create the namespace first or check spelling (case-sensitive)
- `400 Vector dimension mismatch`: Ensure vectors match the namespace's configured dimension
- `429 Too Many Requests`: Implement exponential backoff
