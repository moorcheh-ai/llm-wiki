# Moorcheh Agent Skills — Bug Report & Fix Instructions

**Date:** 2025-07-14
**Reported by:** User testing llm-wiki integration with Moorcheh agent skills
**Skills repo:** `moorcheh-ai/agent-skills`
**SDK version tested:** `moorcheh-sdk 1.3.1`

---

## Summary of Issues Found

During a real-world session using the Moorcheh agent skills to build an LLM Wiki (ingest a PDF, create wiki pages, upload to Moorcheh, query via RAG), we encountered 6 issues. Two are critical (cause failures), two are high priority (cause data loss or broken workflows), and two are medium (cause friction on Windows).

---

## Issue 1: CRITICAL — Outdated default model ID in answer endpoint

### Problem
The SDK's `answer.generate()` method defaults to `anthropic.claude-sonnet-4-20250514-v1:0`, which is no longer authorized on Moorcheh's Bedrock backend. This causes a `500 Internal Server Error` with an `AccessDeniedException` on every RAG call that doesn't explicitly override the model.

### Where it appears
- **SDK default:** `answer.generate()` signature has `ai_model: str = 'anthropic.claude-sonnet-4-20250514-v1:0'`
- **Reference doc:** `references/generate_answer.md` — response example shows `anthropic.claude-sonnet-4-5-20250929-v1:0` (also outdated)
- **Reference doc:** `references/generate_answer.md` — parameter table says `aiModel` (camelCase) but SDK uses `ai_model` (snake_case)

### Working model ID
`anthropic.claude-sonnet-4-6` — confirmed working in our session.

### Fix required
1. **SDK:** Update the default value of `ai_model` parameter in `answer.generate()` to `anthropic.claude-sonnet-4-6`
2. **`references/generate_answer.md`:**
   - Update the parameter table: change `aiModel` to `ai_model` to match the SDK
   - Update the default model name in the description
   - Update the response example to show the current model ID
   - Add a note that the model ID may need updating as new models are released
3. **`scripts/generate_answer.py`:** Add a `--model` argument so users can override the model without editing code

---

## Issue 2: CRITICAL — Missing `upload_file` endpoint in skills

### Problem
The SDK has a `client.documents.upload_file()` method that uploads files directly (`.md`, `.pdf`, `.txt`, `.docx`, `.xlsx`, `.json`, `.csv`) via `POST /namespaces/{name}/upload-file` with multipart/form-data. This endpoint is **not documented** in the agent skills at all. As a result, agents default to the `upload_text` workflow which requires:
1. Reading file content into memory
2. Building a JSON payload
3. Uploading via the documents API

This is error-prone and led to Issue 3 (data loss).

### Fix required
1. **Create `references/upload_file.md`** documenting the endpoint, SDK method, supported file types, 10MB limit, and when to use it vs `upload_text`
2. **Create `scripts/upload_file.py`** with `--file` (single) and `--dir` (batch) modes
3. **Update `SKILL.md`** to list `upload_file` as the **preferred method** for local files under Data Operations, above `upload_text`

---

## Issue 3: HIGH — No file safety guidance for upload workflows

### Problem
When an agent uses `upload_text` to upload local files, it may read and modify source files in the same operation (e.g., to flip a `moorcheh_uploaded` frontmatter flag). A Python one-liner that opens a file for read and write in the same expression can truncate the file to 0 bytes. This happened during our session — 9 wiki markdown files were wiped to empty.

### Fix required
1. **Add a "File Safety" section to `SKILL.md`** instructing agents to:
   - Always prefer `upload_file` over `upload_text` for local files
   - Never combine read and write operations on the same file in one expression
   - Separate upload from metadata flag updates
   - Use the explicit read → modify in memory → write back pattern
2. **Add a safety note to `references/upload_text.md`** warning about file corruption when reading local files for upload

---

## Issue 4: HIGH — `list_namespaces.py` crashes on API response format

### Problem
The script assumes `client.namespaces.list()` returns a list, but the SDK returns a dict with a `namespaces` key: `{"namespaces": [...]}`. The script iterates directly and crashes with `AttributeError: 'str' object has no attribute 'get'`.

### Current broken code (line 13):
```python
namespaces = client.namespaces.list()
# ...
for ns in namespaces:  # iterates over dict keys, not namespace objects
```

### Fix required
```python
result = client.namespaces.list()
namespaces = result.get("namespaces", []) if isinstance(result, dict) else result
```

---

## Issue 5: MEDIUM — Unicode emoji characters crash scripts on Windows

### Problem
All scripts use emoji characters (✅ ❌ 📁 ⏳) in print statements. On Windows with `cp1252` encoding (the default), these cause `UnicodeEncodeError` and the script crashes — even when the underlying operation succeeded. This masks success/failure status.

### Affected scripts
- `list_namespaces.py` — `📁` and `❌`
- `create_namespace.py` — `✅` and `❌`
- `upload_text.py` — `✅`, `❌`, `⏳`
- `search.py` — `❌`
- `generate_answer.py` — `❌`

### Fix required
Either:
- **Option A (recommended):** Replace emoji with ASCII equivalents: `[OK]`, `[ERROR]`, `[INFO]`, `[WAIT]`
- **Option B:** Add `# -*- coding: utf-8 -*-` and set `PYTHONIOENCODING=utf-8` or wrap prints in try/except with ASCII fallback

---

## Issue 6: MEDIUM — SDK parameter naming mismatch in reference docs

### Problem
The `references/generate_answer.md` documents API parameters in camelCase (`aiModel`, `chatHistory`, `headerPrompt`, `footerPrompt`, `structuredResponse`) but the Python SDK uses snake_case (`ai_model`, `chat_history`, `header_prompt`, `footer_prompt`). The Python SDK examples in the same doc also use camelCase, which will fail.

### Affected section in `references/generate_answer.md`:
- Parameter table uses `aiModel` — SDK expects `ai_model`
- Python SDK example uses `chatHistory=` — SDK expects `chat_history=`

### Fix required
- Keep camelCase in the REST API / curl examples (that's the API format)
- Use snake_case in all Python SDK examples
- Add a note clarifying the naming convention difference between REST API and Python SDK

---

## Checklist for the fixing agent

- [ ] **Issue 1:** Update default model ID to `anthropic.claude-sonnet-4-6` in SDK, reference doc, and script
- [ ] **Issue 2:** Create `references/upload_file.md` and `scripts/upload_file.py`; update `SKILL.md`
- [ ] **Issue 3:** Add file safety section to `SKILL.md` and warning to `references/upload_text.md`
- [ ] **Issue 4:** Fix `list_namespaces.py` to handle dict response format
- [ ] **Issue 5:** Replace emoji with ASCII in all scripts, or add encoding fallback
- [ ] **Issue 6:** Fix parameter naming in `references/generate_answer.md` Python examples

---

## How to test

```bash
# Set API key
export MOORCHEH_API_KEY="your-key"

# Test Issue 1 fix: should not get 500 error
python scripts/generate_answer.py --namespace "test" --query "hello"

# Test Issue 2 fix: upload_file should work
python scripts/upload_file.py --namespace "test" --file "test.md"

# Test Issue 4 fix: should list namespaces without crash
python scripts/list_namespaces.py

# Test Issue 5 fix: run all scripts on Windows cmd.exe (not PowerShell)
# None should crash with UnicodeEncodeError

# Test Issue 6 fix: Python SDK examples in docs should use snake_case
```
