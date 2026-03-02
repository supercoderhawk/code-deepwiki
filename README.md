# code-deepwiki Skills Repository

This repository packages the `code-deepwiki` skill in a standard multi-skill-compatible layout:

- Canonical skill path: `skills/code-deepwiki`
- Skill purpose: generate multi-page technical wiki documentation from local or remote code repositories (GitHub/GitLab/Bitbucket), with source citations and output validation.

## Repository Layout

```text
.
├── README.md
├── auth.json
├── .gitignore
├── .claude-plugin/
│   └── marketplace.json
├── skills/
│   └── code-deepwiki/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       ├── references/
│       └── scripts/
└── tools/
    ├── install/
    └── publish/
        ├── push_to_skills_sh.sh
        └── smithery_payload.template.json
```

`.claude-plugin/marketplace.json` exposes this repository as a Claude plugin marketplace catalog entry.

## `auth.json` (Local Secrets)

Create `auth.json` at repository root and store runtime keys there. This file is ignored by Git to prevent secret leakage.

```json
{
  "DEEPWIKI_REPO_TOKEN": "",
  "SMITHERY_API_KEY": "",
  "SMITHERY_API_TOKEN": "",
  "SMITHERY_SKILLS_ENDPOINT": "https://api.smithery.ai/v1/skills"
}
```

Notes:
- `auth.json` is local-only and should never be committed.
- Script behavior: environment variables still have highest priority.
- Fallback behavior: when env vars are absent, scripts can read matching keys from `auth.json`.

## Install with Vercel Skills CLI (`npx skills`)

Install from local repository path:

```bash
npx -y skills add . --skill code-deepwiki
```

Install from a remote GitHub repository:

```bash
npx -y skills add https://github.com/supercoderhawk/code-deepwiki --skill code-deepwiki
```

Install using `owner/repo` shorthand (recommended for skills.sh discoverability):

```bash
npx -y skills add supercoderhawk/code-deepwiki --skill code-deepwiki
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

Install by Smithery namespace/slug (`supercoderhawk/code-deepwiki`):

```bash
npx -y @smithery/cli skill add supercoderhawk/code-deepwiki --agent claude-code
```

Install by skill URL:

```bash
npx -y @smithery/cli skill add https://smithery.ai/skills/supercoderhawk/code-deepwiki --agent github-copilot
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

# npx skills wrapper (remote source, Codex)
bash tools/install/install_via_skills.sh --source supercoderhawk/code-deepwiki --agent codex --yes

# Smithery wrapper
bash tools/install/install_via_smithery.sh --skill supercoderhawk/code-deepwiki --agent github-copilot

# Smithery wrapper with explicit auth file
bash tools/install/install_via_smithery.sh --skill supercoderhawk/code-deepwiki --agent github-copilot --auth-file ./auth.json
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
Use $code-deepwiki to generate wiki pages for https://github.com/supercoderhawk/code-deepwiki with strict citations.
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

## Publish to skills.sh (for `npx skills` / Codex discoverability)

There is no dedicated publish endpoint in `skills.sh`. Visibility is driven by `npx skills` install telemetry.

1. Push this repository publicly to GitHub (`supercoderhawk/code-deepwiki`).
2. Trigger a remote install event with `npx skills add`:

```bash
npx -y skills add supercoderhawk/code-deepwiki --skill code-deepwiki --agent codex --yes
```

To install it into your own Codex environment at the same time:

```bash
npx -y skills add supercoderhawk/code-deepwiki --skill code-deepwiki --agent codex --global --yes
```

3. Verify discovery results:

```bash
npx -y skills find code-deepwiki
```

4. Optional helper script:

```bash
bash tools/publish/push_to_skills_sh.sh --agent codex
```

Notes:
- If telemetry is disabled (`DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1`), install events may not contribute to ranking/discovery.
- Use remote source (`owner/repo` or GitHub URL), not local `.` path, when you want skills.sh attribution.

Private repo scan with auth.json fallback token:

```bash
python3 skills/code-deepwiki/scripts/scan_repo_context.py \
  --repo-url https://github.com/owner/private-repo \
  --token-env DEEPWIKI_REPO_TOKEN \
  --auth-file ./auth.json \
  --out-dir docs/code-deepwiki
```

## Publish/Update Guides

See `tools/publish/README.md` for:

- skills.sh discovery flow (`npx skills add` telemetry + `skills find` verification)
- helper script `tools/publish/push_to_skills_sh.sh`
- Smithery prerequisites (`smithery auth login`, namespace ownership, token scope)
- Smithery publish via console/UI or API (`tools/publish/smithery_payload.template.json`)
