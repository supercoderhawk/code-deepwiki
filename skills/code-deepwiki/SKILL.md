---
name: code-deepwiki
description: Generate multi-page technical wiki documentation from source code repositories with a DeepWiki-style workflow (repository scan, wiki structure planning, per-page generation, and quality validation). Use when asked to create codebase documentation, architecture guides, or repo wiki content from a local path or GitHub/GitLab/Bitbucket URL, including private repositories.
---

# Code DeepWiki

## Overview

- Use a DeepWiki-style four-stage workflow to convert a source repository into a multi-page technical wiki.
- Default output language is `English`; if the user explicitly requests another language, use the requested language.
- Default hard constraints:
  - Each page must reference at least 5 source files.
  - The first block on each page must be `<details><summary>Relevant source files</summary>`.
  - Mermaid flowcharts must use `graph TD`; `graph LR` is not allowed.
  - Key conclusions must include citations in `Sources: [path:start-end]()` format.

## Input Specification

- Repository input (choose one):
  - Local path: `--repo-path`
  - Remote URL: `--repo-url` (supports GitHub/GitLab/Bitbucket)
- Private repositories:
  - Use `--token-env <ENV_NAME>` to read the token from an environment variable.
  - Logs and error messages must be redacted; never print raw tokens.
- Document language:
  - Use `--output-language` to set the target wiki language.
  - Default is `English`.
- File filtering:
  - include: `--include-dirs`, `--include-files`
  - exclude: `--exclude-dirs`, `--exclude-files`
- Output directory:
  - Use `--out-dir` to set artifact output path; default is `docs/code-deepwiki/`.

## Four-Stage Workflow

### Step 1: Scan Repository Context

- Run `scripts/scan_repo_context.py` to generate:
  - `file_tree.txt`
  - `readme.md`
  - `source_manifest.json`
- Keep this step focused on collection and normalization only; do not generate wiki content with LLMs here.

### Step 2: Generate Wiki Structure

- Use the "Wiki Structure" template in `references/prompt_templates.md`.
- Inputs: `file_tree.txt` and `readme.md`.
- Outputs:
  - `wiki_structure.json`
  - `index.md` (table-of-contents page, derived from `wiki_structure.json`)

### Step 3: Generate Page Content Sequentially

- Use `wiki_structure.json` to generate `pages/*.md` one page at a time.
- Enforce these rules on every page:
  - First block is a `<details>` source-file block.
  - At least 5 source files are cited.
  - Mermaid flowcharts use `graph TD`.
  - Key conclusions throughout the page include `Sources:` citations.

### Step 4: Quality Validation and Fallback

- Run `scripts/validate_wiki_output.py` as the quality gate.
- On validation failure, apply targeted fallback by issue type:
  - XML or structure issues: go back to Step 2 and rebuild structure.
  - Insufficient source coverage: go back to Step 3 and expand source file coverage.
  - Mermaid direction violations: fix only affected blocks and re-run validation.

## Output Directory Convention

- `docs/code-deepwiki/index.md`
- `docs/code-deepwiki/pages/*.md`
- `docs/code-deepwiki/wiki_structure.json`
- `docs/code-deepwiki/source_manifest.json`
- `docs/code-deepwiki/file_tree.txt`
- `docs/code-deepwiki/readme.md`

## Standard Command Templates

- Local repository scan:

```bash
pipenv run python scripts/scan_repo_context.py \
  --repo-path /absolute/path/to/repo \
  --output-language English \
  --out-dir docs/code-deepwiki
```

- Remote repository scan (public repo):

```bash
pipenv run python scripts/scan_repo_context.py \
  --repo-url https://github.com/owner/repo \
  --output-language English \
  --out-dir docs/code-deepwiki
```

- Remote repository scan (private repo):

```bash
export DEEPWIKI_REPO_TOKEN="your_token"
pipenv run python scripts/scan_repo_context.py \
  --repo-url https://github.com/owner/private-repo \
  --token-env DEEPWIKI_REPO_TOKEN \
  --output-language Japanese \
  --out-dir docs/code-deepwiki
```

- Wiki quality validation:

```bash
pipenv run python scripts/validate_wiki_output.py \
  --wiki-dir docs/code-deepwiki \
  --min-source-files 5
```

## Reference Loading Strategy

- Read `references/deepwiki_method_notes.md` when you need workflow/method details.
- Read `references/prompt_templates.md` when you need reusable prompts directly.
- Unless the task requires it, avoid loading all reference files at once to keep context efficient.
