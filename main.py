#!/usr/bin/env python3
"""Publish the one-line epitaph for the make.fun bounty
"Famous Last Words: The Funniest Epitaph".

The line lives in entry.txt next to this file. This program reads
it as raw bytes, checks it against the gate (UTF-8, one line,
1-150 characters, not only white space) and writes the exact bytes
to entry.txt in the output directory. Nothing is stripped or
re-encoded: the published bytes are byte-identical to the source,
trailing newline included. After writing, the file is read back
and compared byte for byte. Stdlib only; no network, no clock,
no randomness, so two runs always produce identical output.

Output directory: --output-dir, else $MAKEFUN_OUTPUT_DIR, else /output.
Options: --output-dir <dir>, --verify-only, --quiet.
Exit codes: 0 success, 1 entry fails the gate or cannot be written.
"""

import argparse
import os
import sys
from pathlib import Path

MAX_CHARS = 150


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish the epitaph entry.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--quiet", action="store_true",
                        help="print nothing on success")
    args = parser.parse_args()

    src = Path(__file__).resolve().parent / "entry.txt"
    try:
        data = src.read_bytes()
    except OSError as exc:
        print(f"Invalid: cannot read entry.txt: {exc}", file=sys.stderr)
        return 1
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        print(f"Invalid: entry.txt is not valid UTF-8: {exc}", file=sys.stderr)
        return 1
    line = text[:-1] if text.endswith("\n") else text
    if not line or line.isspace():
        print("Invalid: entry is empty or only white space", file=sys.stderr)
        return 1
    if "\n" in line or "\r" in line:
        print("Invalid: entry must be a single line", file=sys.stderr)
        return 1
    if len(line) > MAX_CHARS:
        print(f"Invalid: entry is {len(line)} chars, over {MAX_CHARS}", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"Valid: {len(line)} characters, {len(data)} bytes")
    if args.verify_only:
        return 0
    out_dir = Path(args.output_dir or os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "entry.txt"
        out_path.write_bytes(data)
        if out_path.read_bytes() != data:
            raise OSError("published entry does not match entry.txt")
    except OSError as exc:
        print(f"Invalid: cannot write output: {exc}", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"Wrote entry.txt to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
