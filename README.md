# code-deepwiki Skills Repository

This repository packages the `code-deepwiki` skill in a standard multi-skill-compatible layout:

- Canonical skill path: `skills/code-deepwiki`
- Skill purpose: generate multi-page technical wiki documentation from local or remote code repositories (GitHub/GitLab/Bitbucket), with source citations and output validation.

## Repository Layout

```text
.
├── README.md
├── .gitignore
├── skills/
│   └── code-deepwiki/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       ├── references/
│       └── scripts/
└── tools/
    ├── install/
    └── publish/
```

## Install with Vercel Skills CLI (`npx skills`)

Install from local repository path:

```bash
npx -y skills add . --skill code-deepwiki
```

Install from a remote GitHub repository:

```bash
npx -y skills add https://github.com/<owner>/<repo> --skill code-deepwiki
```

Install specifically for Claude Code:

```bash
npx -y skills add . --skill code-deepwiki --agent claude-code
```

Install specifically for GitHub Copilot:

```bash
npx -y skills add . --skill code-deepwiki --agent github-copilot
```

Global install example:

```bash
npx -y skills add . --skill code-deepwiki --agent claude-code --global --yes
```

## Install with Smithery CLI

Install by Smithery namespace/slug:

```bash
npx -y @smithery/cli skill add <namespace>/<slug> --agent claude-code
```

Install by skill URL:

```bash
npx -y @smithery/cli skill add https://smithery.ai/skills/<namespace>/<slug> --agent github-copilot
```

List available Smithery target agents:

```bash
npx -y @smithery/cli skill agents
```

## Helper Install Scripts

Use wrapper scripts from `tools/install`:

```bash
# npx skills wrapper
bash tools/install/install_via_skills.sh --source . --agent claude-code --yes

# Smithery wrapper
bash tools/install/install_via_smithery.sh --skill <namespace>/<slug> --agent github-copilot
```

## Usage After Installation

Example prompts:

```text
Use $code-deepwiki to generate a multi-page technical wiki for this repository.
```

```text
Use $code-deepwiki to document architecture, core modules, and data flow for this repo in English.
```

```text
Use $code-deepwiki to generate wiki pages for https://github.com/owner/repo with strict citations.
```

## Local Validation

Check repository structure and skill discovery:

```bash
find . -maxdepth 3 -type f
npx -y skills add . --list
npx -y skills add . --list --skill code-deepwiki
```

Check agent-target options:

```bash
npx -y skills add . --list --agent claude-code
npx -y skills add . --list --agent github-copilot
```

Smoke-test Python scripts at canonical path:

```bash
python3 -m py_compile skills/code-deepwiki/scripts/scan_repo_context.py
python3 -m py_compile skills/code-deepwiki/scripts/validate_wiki_output.py
```

## Smithery Publish/Update Guide

See `tools/publish/README.md` for:

- prerequisites (`smithery auth login`, namespace ownership, token scope)
- publish via Smithery console/UI
- publish or update via API workflow with `tools/publish/smithery_payload.template.json`
