#!/usr/bin/env python3
"""
Validate whether DeepWiki output documents conform to structure and citation rules.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


CITATION_LINE_RE = re.compile(
  r"^\s*Sources:\s*\[[^\]]+:\d+(?:-\d+)?\]\(\)(\s*,\s*\[[^\]]+:\d+(?:-\d+)?\]\(\))*\s*$"
)
H1_RE = re.compile(r"^\s*#\s+\S+")
DETAILS_SUMMARY = "<summary>Relevant source files</summary>"


def discover_markdown_files(wiki_dir: Path, all_markdown: bool) -> List[Path]:
  if all_markdown:
    files = [item for item in wiki_dir.rglob("*.md") if item.is_file()]
    return sorted(files)

  files: List[Path] = []
  index_path = wiki_dir / "index.md"
  if index_path.is_file():
    files.append(index_path)

  pages_dir = wiki_dir / "pages"
  if pages_dir.exists() and pages_dir.is_dir():
    files.extend(item for item in pages_dir.rglob("*.md") if item.is_file())

  return sorted(set(files))


def find_details_block(lines: List[str]) -> Tuple[List[str], int, int, str]:
  start = -1
  for index, line in enumerate(lines):
    if line.strip():
      start = index
      break
  if start < 0:
    return [], -1, -1, "File is empty or contains only whitespace."
  if lines[start].strip() != "<details>":
    return [], start, -1, "The first non-empty line must be <details>."

  end = -1
  for index in range(start + 1, len(lines)):
    if lines[index].strip() == "</details>":
      end = index
      break
  if end < 0:
    return [], start, -1, "Missing closing </details> tag."

  block = lines[start : end + 1]
  text = "\n".join(block)
  if DETAILS_SUMMARY not in text:
    return block, start, end, "Details block is missing <summary>Relevant source files</summary>."
  return block, start, end, ""


def count_sources_in_details(block: List[str]) -> int:
  link_re = re.compile(r"^\s*-\s*\[([^\]]+)\]\([^)]+\)\s*$")
  plain_re = re.compile(r"^\s*-\s*([^\n]+?)\s*$")
  sources = set()
  for line in block:
    match = link_re.match(line)
    if match:
      value = match.group(1).strip()
      if value:
        sources.add(value)
      continue
    match = plain_re.match(line)
    if match:
      value = match.group(1).strip()
      if value and not value.startswith("<!--"):
        sources.add(value)
  return len(sources)


def extract_mermaid_blocks(lines: List[str]) -> List[List[str]]:
  blocks: List[List[str]] = []
  inside = False
  buffer: List[str] = []
  for line in lines:
    stripped = line.strip().lower()
    if not inside and stripped.startswith("```mermaid"):
      inside = True
      buffer = []
      continue
    if inside and line.strip().startswith("```"):
      blocks.append(buffer)
      inside = False
      buffer = []
      continue
    if inside:
      buffer.append(line.rstrip("\n"))
  return blocks


def validate_mermaid_blocks(blocks: List[List[str]]) -> List[str]:
  errors: List[str] = []
  graph_re = re.compile(r"^\s*graph\s+([A-Za-z]+)\b")
  for block_index, block in enumerate(blocks, start=1):
    for line in block:
      match = graph_re.match(line)
      if not match:
        continue
      direction = match.group(1).upper()
      if direction == "LR":
        errors.append(f"Mermaid block #{block_index} uses graph LR (forbidden).")
      elif direction != "TD":
        errors.append(f"Mermaid block #{block_index} must use graph TD, found graph {direction}.")
      break
  return errors


def validate_single_file(path: Path, min_source_files: int) -> List[str]:
  errors: List[str] = []
  text = path.read_text(encoding="utf-8", errors="replace")
  lines = text.splitlines()

  if not any(H1_RE.match(line) for line in lines):
    errors.append("Missing H1 title (# ...).")

  details_block, _, _, detail_error = find_details_block(lines)
  if detail_error:
    errors.append(detail_error)
  else:
    source_count = count_sources_in_details(details_block)
    if source_count < min_source_files:
      errors.append(f"Details source file count is too low: {source_count} < {min_source_files}.")

  source_lines = [line.strip() for line in lines if "Sources:" in line]
  if not source_lines:
    errors.append("Missing Sources: citation line.")
  else:
    for line in source_lines:
      if not CITATION_LINE_RE.match(line):
        errors.append(f"Invalid Sources citation format: {line}")

  mermaid_blocks = extract_mermaid_blocks(lines)
  errors.extend(validate_mermaid_blocks(mermaid_blocks))
  return errors


def run_validation(wiki_dir: Path, min_source_files: int, all_markdown: bool) -> int:
  if not wiki_dir.exists() or not wiki_dir.is_dir():
    print(f"[ERROR] Wiki directory does not exist: {wiki_dir}", file=sys.stderr)
    return 1

  markdown_files = discover_markdown_files(wiki_dir, all_markdown=all_markdown)
  if not markdown_files:
    if all_markdown:
      print(f"[ERROR] No markdown files found under: {wiki_dir}", file=sys.stderr)
    else:
      print(
        f"[ERROR] No wiki markdown files found. Expected {wiki_dir / 'index.md'} or files under {wiki_dir / 'pages'}.",
        file=sys.stderr,
      )
    return 1

  findings: List[str] = []
  for file_path in markdown_files:
    issues = validate_single_file(file_path, min_source_files=min_source_files)
    for issue in issues:
      findings.append(f"{file_path}: {issue}")

  if findings:
    print(f"[ERROR] Validation failed with {len(findings)} issue(s):", file=sys.stderr)
    for index, item in enumerate(findings, start=1):
      print(f"{index}. {item}", file=sys.stderr)
    return 1

  print(f"[OK] Validation passed. Checked {len(markdown_files)} markdown file(s).")
  return 0


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Validate DeepWiki markdown output.")
  parser.add_argument("--wiki-dir", required=True, help="Directory containing wiki markdown files.")
  parser.add_argument(
    "--min-source-files",
    type=int,
    default=5,
    help="Minimum number of source files required in the details block.",
  )
  parser.add_argument(
    "--all-markdown",
    action="store_true",
    help="Validate all markdown files under wiki-dir (legacy behavior).",
  )
  return parser


def main() -> int:
  args = build_parser().parse_args()
  wiki_dir = Path(args.wiki_dir).expanduser().resolve()
  return run_validation(
    wiki_dir,
    min_source_files=args.min_source_files,
    all_markdown=args.all_markdown,
  )


if __name__ == "__main__":
  raise SystemExit(main())
