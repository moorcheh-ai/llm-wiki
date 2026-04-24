# Upload File

Upload a file directly to a text namespace. The file is automatically processed to extract text, generate embeddings, and index for semantic search. **This is the preferred method for uploading local files** — it avoids reading file content into memory and eliminates the risk of accidental file corruption.

## API

```
POST https://api.moorcheh.ai/v1/namespaces/{namespace_name}/upload-file
```

Content-Type: `multipart/form-data`

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `file` | file | Yes | The file to upload |

### Supported File Types

`.pdf`, `.docx`, `.xlsx`, `.json`, `.txt`, `.csv`, `.md`

### Maximum File Size

10 MB

### Example

```bash
curl -X POST "https://api.moorcheh.ai/v1/namespaces/my-documents/upload-file" \
  -H "x-api-key: $MOORCHEH_API_KEY" \
  -F "file=@document.md"
```

### Response

```json
{
  "success": true,
  "message": "File uploaded successfully",
  "namespace": "my-documents",
  "fileName": "document.md",
  "fileSize": 3771,
  "execution_time": 0.755
}
```

## Python SDK

```python
from moorcheh_sdk import MoorchehClient

with MoorchehClient(api_key="your-api-key") as client:
    # Upload a single file
    result = client.documents.upload_file(
        namespace_name="my-documents",
        file_path="wiki/page.md"
    )
    print(f"Uploaded: {result['fileName']} ({result['fileSize']} bytes)")
```

## Script

```bash
# Single file
uv run skills/moorcheh/scripts/upload_file.py \
  --namespace "my-documents" \
  --file "wiki/page.md"

# All markdown files in a directory
uv run skills/moorcheh/scripts/upload_file.py \
  --namespace "my-documents" \
  --dir "wiki/"
```

## When to Use This vs Upload Text

| Use `upload_file` when... | Use `upload_text` when... |
|---|---|
| You have local files (.md, .pdf, .txt, etc.) | You have text content already in memory |
| You want to avoid reading/modifying source files | You need to attach custom metadata per document |
| You're uploading wiki pages from disk | You're building documents programmatically |

## Important Notes

- Files are processed **asynchronously** — allow a few seconds for indexing before searching
- The file is opened in **read-only binary mode** by the SDK — source files are never modified
- File name becomes the document identifier in the namespace
- This is the **safest method** for uploading local files since the agent never needs to read or write the source files
