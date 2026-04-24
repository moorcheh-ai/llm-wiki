# Upload Text Data

Upload text documents to a text namespace for semantic search and AI-powered operations. Documents are automatically embedded and indexed.

## API

```
POST https://api.moorcheh.ai/v1/namespaces/{namespace_name}/documents
```

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `documents` | array | Yes | Array of document objects |

### Document Object

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique document identifier |
| `text` | string | Yes | Document text content |
| `*` | any | No | Any additional key-value pairs become metadata |

### Example

```bash
curl -X POST "https://api.moorcheh.ai/v1/namespaces/my-documents/documents" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $MOORCHEH_API_KEY" \
  -d '{
    "documents": [
      {
        "id": "doc-001",
        "text": "Machine learning is a subset of AI that enables computers to learn from data.",
        "title": "Intro to ML",
        "category": "education",
        "author": "Dr. Smith"
      },
      {
        "id": "doc-002",
        "text": "Neural networks are computing systems inspired by biological neural networks.",
        "title": "Neural Networks",
        "category": "education"
      }
    ]
  }'
```

### Response

```json
{
  "status": "success",
  "message": "2 documents uploaded successfully to namespace 'my-documents'",
  "upload_id": "upload_1234567890",
  "namespace_name": "my-documents",
  "documents_processed": 2,
  "processing_status": "in_progress",
  "uploaded_documents": [
    { "id": "doc-001", "status": "processing", "character_count": 78 },
    { "id": "doc-002", "status": "processing", "character_count": 75 }
  ]
}
```

## Python SDK

```python
from moorcheh_sdk import MoorchehClient

with MoorchehClient(api_key="your-api-key") as client:
    docs = [
        {
            "id": "doc-001",
            "text": "Machine learning is a subset of AI...",
            "title": "Intro to ML",
            "category": "education"
        },
        {
            "id": "doc-002",
            "text": "Neural networks are computing systems...",
            "title": "Neural Networks",
            "category": "education"
        }
    ]
    result = client.documents.upload(
        namespace_name="my-documents",
        documents=docs
    )
    print(f"Uploaded {result['documents_processed']} documents")
```

## Script

```bash
uv run skills/moorcheh/scripts/upload_text.py \
  --namespace "my-documents" \
  --file "data.json"
```

## Important Notes

- Documents are processed **asynchronously** — allow a few seconds for indexing before searching
- All fields except `id` and `text` become searchable metadata
- Use metadata for filtering (e.g., `#category:education`)
- The namespace must be of type `"text"`

## CRITICAL: File Safety When Uploading Local Files

**Always open source files in read-only mode (`'r'`) when reading content for upload.** Never combine reading and writing in the same operation. If you need to update metadata flags (e.g. `moorcheh_uploaded: true`) after upload, do it as a separate step: read the full content into memory first, then close the file, then write the modified content back. Failing to follow this pattern can truncate files to 0 bytes.
