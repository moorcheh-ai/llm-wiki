#!/usr/bin/env python3
"""Deep Ingest: Upload a large document to Moorcheh staging, extract TOC, and
prepare chapter-by-chapter queries for wiki building.

This script handles Steps 1-2 of the deep ingest workflow:
  1. Extract TOC from the document (PDF only for now)
  2. Upload the raw file to a staging namespace
  3. Output the chapter list for the agent to process

The agent then uses the chapter list to query Moorcheh and build wiki pages.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "moorcheh", "scripts"))
from moorcheh_conn import get_client


def extract_toc_pdf(file_path):
    """Extract table of contents from a PDF using pymupdf."""
    try:
        import fitz
    except ImportError:
        print("[ERROR] pymupdf not installed. Run: pip install pymupdf")
        sys.exit(1)

    doc = fitz.open(file_path)
    toc = doc.get_toc()

    if toc:
        chapters = [{"level": level, "title": title, "page": page} for level, title, page in toc]
        doc.close()
        return chapters

    # Fallback: extract text from first 10 pages and look for TOC
    print("[INFO] No embedded TOC found. Scanning first pages for chapter list...")
    text = ""
    for i in range(min(10, len(doc))):
        text += doc[i].get_text()
    doc.close()

    chapters = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5 or len(line) > 120:
            continue
        parts = line.rsplit(None, 1)
        if len(parts) == 2 and parts[1].isdigit():
            title = parts[0].strip()
            page = int(parts[1])
            if title and page > 0:
                chapters.append({"level": 1, "title": title, "page": page})

    return chapters


def extract_toc(file_path):
    """Extract TOC based on file type."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_toc_pdf(file_path)
    else:
        print(f"[INFO] TOC extraction not supported for {ext}. Agent will need to determine chapters manually.")
        return []


def main():
    parser = argparse.ArgumentParser(description="Deep Ingest: upload large docs to Moorcheh staging")
    parser.add_argument("--file", required=True, help="Path to the source document")
    parser.add_argument("--wiki-namespace", required=True, help="Target wiki namespace (e.g. wiki-personal)")
    parser.add_argument("--staging-namespace", default="staging-ingest", help="Staging namespace name (default: staging-ingest)")
    parser.add_argument("--skip-upload", action="store_true", help="Skip upload (staging already has the file)")
    parser.add_argument("--output", default=None, help="Output file for chapter list JSON")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"[ERROR] File not found: {args.file}")
        sys.exit(1)

    client = get_client()

    # Step 1: Extract TOC
    print(f"[1/3] Extracting table of contents from {os.path.basename(args.file)}...")
    chapters = extract_toc(args.file)
    if chapters:
        print(f"       Found {len(chapters)} chapters/sections")
    else:
        print("       No chapters found. Agent will query by topic instead.")

    # Step 2: Create staging namespace and upload
    if not args.skip_upload:
        print(f"[2/3] Creating staging namespace '{args.staging_namespace}'...")
        try:
            client.namespaces.create(namespace_name=args.staging_namespace, type="text")
            print(f"       Created '{args.staging_namespace}'")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"       Namespace '{args.staging_namespace}' already exists, reusing")
            else:
                print(f"[ERROR] {e}")
                sys.exit(1)

        print(f"[3/3] Uploading {os.path.basename(args.file)} to staging...")
        try:
            result = client.documents.upload_file(
                namespace_name=args.staging_namespace,
                file_path=args.file,
            )
            size = result.get("fileSize", "?")
            print(f"       Uploaded ({size} bytes). Waiting for indexing...")
            time.sleep(15)
            print("       Indexing complete (estimated).")
        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
            sys.exit(1)
    else:
        print("[2/3] Skipping upload (--skip-upload)")
        print("[3/3] Skipping upload")

    # Output chapter list
    output = {
        "source_file": os.path.basename(args.file),
        "staging_namespace": args.staging_namespace,
        "wiki_namespace": args.wiki_namespace,
        "chapters": chapters,
        "instructions": (
            "For each chapter, query the staging namespace with top_k=20 to retrieve "
            "the full chapter content. Use the results to create/update wiki pages. "
            "After all chapters are processed, upload all wiki pages to the wiki "
            "namespace using upload_file, then delete the staging namespace."
        ),
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\nChapter list saved to {args.output}")
    else:
        print("\n" + "=" * 60)
        print("DEEP INGEST READY")
        print("=" * 60)
        print(f"Source: {output['source_file']}")
        print(f"Staging: {output['staging_namespace']}")
        print(f"Wiki: {output['wiki_namespace']}")
        print(f"Chapters: {len(chapters)}")
        print()
        if chapters:
            for i, ch in enumerate(chapters, 1):
                indent = "  " * (ch["level"] - 1)
                print(f"  {i:2d}. {indent}{ch['title']} (p.{ch['page']})")
        print()
        print("Next: Agent should query each chapter from the staging namespace")
        print("      and build wiki pages from the results.")


if __name__ == "__main__":
    main()
