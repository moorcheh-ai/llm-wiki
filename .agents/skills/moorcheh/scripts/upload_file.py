#!/usr/bin/env python3
"""Upload files directly to a Moorcheh namespace."""

import argparse
import glob
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from moorcheh_conn import get_client

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".json", ".txt", ".csv", ".md"}


def upload_single(client, namespace, file_path):
    """Upload a single file and return success status."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(f"  Skipped (unsupported type): {file_path}")
        return False

    try:
        result = client.documents.upload_file(
            namespace_name=namespace,
            file_path=file_path,
        )
        name = result.get("fileName", os.path.basename(file_path))
        size = result.get("fileSize", "?")
        print(f"  Uploaded: {name} ({size} bytes)")
        return True
    except Exception as e:
        print(f"  Error uploading {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Upload files to Moorcheh namespace")
    parser.add_argument("--namespace", required=True, help="Target namespace name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Single file path to upload")
    group.add_argument("--dir", help="Directory of files to upload")
    parser.add_argument(
        "--ext",
        default=".md",
        help="File extension filter when using --dir (default: .md)",
    )
    args = parser.parse_args()

    client = get_client()
    uploaded = 0
    failed = 0

    if args.file:
        if not os.path.exists(args.file):
            print(f"File not found: {args.file}")
            sys.exit(1)
        success = upload_single(client, args.namespace, args.file)
        uploaded += 1 if success else 0
        failed += 0 if success else 1
    else:
        pattern = os.path.join(args.dir, "**", f"*{args.ext}")
        files = sorted(glob.glob(pattern, recursive=True))
        if not files:
            print(f"No {args.ext} files found in {args.dir}")
            sys.exit(1)

        print(f"Uploading {len(files)} file(s) to '{args.namespace}'...\n")
        for fp in files:
            success = upload_single(client, args.namespace, fp)
            uploaded += 1 if success else 0
            failed += 0 if success else 1
            time.sleep(0.2)  # brief pause between uploads

    print(f"\nDone: {uploaded} uploaded, {failed} failed")


if __name__ == "__main__":
    main()
