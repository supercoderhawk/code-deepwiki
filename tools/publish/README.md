# Smithery Publish / Update Guide

This repository supports Smithery installation and publication workflows for the `code-deepwiki` skill.

## Prerequisites

1. Install Smithery CLI (or use `npx -y @smithery/cli`).
2. Authenticate:

```bash
npx -y @smithery/cli auth login
```

3. Ensure you own or can publish to the target Smithery namespace.
4. Ensure your token has the required scope for skills publish/update operations.

## Option A: Publish via Smithery Console / UI

1. Open Smithery skill publishing UI.
2. Create or update a skill record.
3. Point the skill source to this repository (`gitUrl`) and set metadata.
4. Verify that installation works via:

```bash
npx -y @smithery/cli skill add <namespace>/<slug> --agent claude-code
```

## Option B: Publish / Update via API Workflow

Use a payload derived from `tools/publish/smithery_payload.template.json`.

1. Copy and fill template:

```bash
cp tools/publish/smithery_payload.template.json tools/publish/smithery_payload.json
```

2. Fill these fields at minimum:
- `title`
- `description`
- `prompt`
- `gitUrl`

3. Configure endpoint and token:

```bash
export SMITHERY_API_TOKEN="<your-token>"
export SMITHERY_SKILLS_ENDPOINT="https://api.smithery.ai/v1/skills"
```

4. Create/publish:

```bash
curl -X POST "$SMITHERY_SKILLS_ENDPOINT" \
  -H "Authorization: Bearer $SMITHERY_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data @tools/publish/smithery_payload.json
```

5. Update (example pattern):

```bash
curl -X PUT "$SMITHERY_SKILLS_ENDPOINT/<namespace>/<slug>" \
  -H "Authorization: Bearer $SMITHERY_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data @tools/publish/smithery_payload.json
```

## Guidance for `gitUrl` and Skill Identification

- `gitUrl` should point to this repository root.
- Skill identifier should resolve to `code-deepwiki` under `skills/code-deepwiki`.
- Keep `SKILL.md` frontmatter `name` as `code-deepwiki`.

## Verify Published Skill

After publish/update:

```bash
npx -y @smithery/cli skill search code-deepwiki
npx -y @smithery/cli skill add <namespace>/<slug> --agent github-copilot
```

> Note: If your organization uses a different Smithery API base URL or versioned endpoint,
> set `SMITHERY_SKILLS_ENDPOINT` accordingly.
