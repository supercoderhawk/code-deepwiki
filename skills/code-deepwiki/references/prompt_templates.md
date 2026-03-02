# Prompt Templates

## Wiki Structure Template

Replace placeholders in this template and use it directly.
`{OUTPUT_LANGUAGE}` should come from `--output-language` (default: `English`).

```text
You are a senior software architect. Design a multi-page technical wiki structure from the repository context.

Requirements:
1. Output language: {OUTPUT_LANGUAGE}
2. Number of pages: {PAGE_COUNT_RANGE}
3. Every page must cover a clear topic and map to concrete file evidence
4. Output must be strict XML only, with no explanation text

<file_tree>
{FILE_TREE_TEXT}
</file_tree>

<readme>
{README_TEXT}
</readme>

Return this XML schema:
<wiki_structure>
  <title>...</title>
  <description>...</description>
  <pages>
    <page id="page-1">
      <title>...</title>
      <description>...</description>
      <importance>high|medium|low</importance>
      <relevant_files>
        <file_path>src/...</file_path>
      </relevant_files>
      <related_pages>
        <related>page-2</related>
      </related_pages>
    </page>
  </pages>
</wiki_structure>

Formatting rules:
- Return ONLY XML (no markdown fences, no prose)
- Start directly with <wiki_structure>
- End directly with </wiki_structure>
```

## Page Generation Template

Replace placeholders in this template and use it directly.
`{OUTPUT_LANGUAGE}` should come from `--output-language` (default: `English`).

```text
You are a senior technical writer. Generate one wiki page from the provided source files.

Hard requirements:
1. Document language: {OUTPUT_LANGUAGE}
2. The first block MUST be:
<details>
<summary>Relevant source files</summary>

- [path/to/file1](...)
- [path/to/file2](...)
- [path/to/file3](...)
- [path/to/file4](...)
- [path/to/file5](...)

</details>
3. At least 5 source files must be cited
4. The page must include H1 title: # {PAGE_TITLE}
5. Key conclusions must use citation format `Sources: [path:start-end]()`
6. Mermaid flowcharts may only use `graph TD`; `graph LR` is forbidden
7. Output markdown body only; do not output extra explanations
8. Do not add any preface before the opening `<details>` block
9. Every significant claim, diagram, table, or code snippet must include `Sources:` citations

Page topic: {PAGE_TITLE}
Page description: {PAGE_DESCRIPTION}

<relevant_files>
{RELEVANT_FILES_LIST}
</relevant_files>

<source_context>
{SOURCE_CONTEXT_TEXT}
</source_context>
```

## Repair Template (For Validation Failures)

```text
Fix the following issues in this wiki page without losing original information:

File: {PAGE_PATH}
Issue list:
{ISSUE_LIST}

Repair requirements:
1. Keep the existing section structure
2. After repair, all requirements must pass:
   - H1 title exists
   - First `<details>` source block exists and contains at least 5 source files
   - `Sources:` citation format is valid
   - Mermaid flowcharts use `graph TD`
3. Output only the full repaired markdown text
```
