# Code DeepWiki Method Notes

## 1. Goals and Boundaries

- Goal: Generate multi-page wiki documentation from a code repository with output that is structured, traceable, and verifiable.
- Boundary: This method only covers the "code-to-documentation" pipeline. It does not introduce business-system changes and does not perform deployments.
- Core idea: structure first, content second; evidence first, conclusions second.
- Language policy: output language is configurable via `--output-language`, with default `English`.

## 2. Four-Stage Process

### Stage A: Repository Scan

- Input: local path or remote URL.
- Processing:
  - Collect file tree
  - Extract README
  - Generate source-file manifest (code files prioritized)
- Output:
  - `file_tree.txt`
  - `readme.md`
  - `source_manifest.json`

### Stage B: Wiki Structure Design

- Input: `file_tree.txt` and `readme.md`.
- Processing:
  - Plan page and section relationships
  - Bind candidate source files to each page
- Output:
  - `wiki_structure.json`
  - `index.md`

### Stage C: Per-Page Content Generation

- Input: `wiki_structure.json` and `source_manifest.json`.
- Processing:
  - Generate pages sequentially to avoid context contamination from concurrency
  - Keep consistent page format and citation rules
- Output:
  - `pages/*.md`

### Stage D: Quality Validation

- Input: `index.md` and `pages/*.md`.
- Validation checks:
  - H1 title
  - `<details>` source-file block
  - Minimum source-file count
  - `Sources:` citation format
  - Mermaid direction rules
- Output:
  - Pass: exit code 0
  - Fail: issue list + non-zero exit code

## 3. Key Design Constraints

- Every page must be traceable: conclusions must be grounded in code evidence.
- The first page block must be the source-file block so reviewers can locate evidence quickly.
- Enforce `graph TD` for flow diagrams to avoid readability issues from horizontal diagrams on narrow screens.
- When structure output is malformed, prefer fallback to the structure stage instead of hard-fixing at page stage.

## 4. File Filtering Strategy

- By default, exclude common noise directories such as `.git`, `node_modules`, and `__pycache__`.
- Support simultaneous include and exclude usage:
  - include for precise focus
  - exclude for supplemental noise filtering
- Private repository tokens are read from environment variables only and are never written to output artifacts.

## 5. Failure Fallback Strategy

- Structure output is not parseable:
  - Re-run the structure-generation template
  - Retry with reduced context focused on core directories
- Page citations are insufficient:
  - Expand candidate files for that page
  - Regenerate with at least 5 source files
- Mermaid validation fails:
  - Repair only the offending diagram blocks
  - Re-run validation without full regeneration

## 6. Recommended Execution Order

1. Run the scan script first to establish a stable context baseline.
2. Generate structure next and do a quick manual review of page partitioning.
3. Generate pages sequentially to prevent citation mismatch caused by concurrency.
4. Run the validation script last as the release gate.
