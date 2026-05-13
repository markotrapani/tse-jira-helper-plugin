# `fields.json` schema for `render-html-preview.py`

The skill writes a JSON file matching this shape, then invokes the script. Two top-level keys:

```jsonc
{
  "scalars": {
    // Every {PLACEHOLDER} in preview-template.html that's a single
    // string value. Keys are placeholder names WITHOUT braces.
    "TICKET_KEY_OR_PREVIEW": "RED-XXXXX",
    "SUMMARY": "Terraform [Aetna]: ...",
    "TYPE": "Bug",
    "STATUS": "To Do",
    "PROJECT": "RED",
    "PROJECT_NAME": "Redislabs (RED)",
    "CANONICAL_ANCHOR": "RED-194253",
    "ISO_TIMESTAMP": "2026-05-13T03:27:20Z",
    "SKILL_VERSION": "0.14.0",
    "PRIORITY": "Medium",
    "SEVERITY": "2 - Medium",
    "REPORTER": "Marko Trapani",
    "ASSIGNEE": "Automatic",
    "SPRINT": "(blank)",
    "COMPONENT": "Cloud API",
    "ENVIRONMENT": "Production",
    "PRODUCT": "RCP(RV/Pro/Flexible)",
    "REPORTED_VERSION": "Terraform 1.9.8, rediscloud 2.15",
    "AFFECTED_ORGS": "Aetna",
    "SEEN_BY": "Aetna",
    "ZENDESK_IDS": "162249",
    "ICM_IDS": "n/a",
    "IMPACT_SCORE": "59",
    "IMPACT_BAND": "MEDIUM",
    "FOUND_BY": "Prod/Customer",
    "ISSUE_SOURCE": "Product Bug",
    "DATA_LOSS": "No",
    "DATA_UNAVAIL": "No",
    "DOWNTIME": "No",

    // Long-form HTML blocks — already converted from markdown to HTML
    // by the skill (using its own markdown→HTML logic, since the
    // template substitution is opaque about content).
    "DESCRIPTION_HTML": "<h2>Summary</h2><p>...</p>...",
    "WORKAROUND_HTML": "<p><strong>No reliable workaround.</strong>...</p>",
    "COMMENT_HTML": "<!-- v0.13+: comment section is removed -->",

    // Raw API payload JSON (pretty-printed, multi-line is fine)
    "CREATE_PAYLOAD_JSON": "{...}",
    "COMMENT_PAYLOAD_JSON": "<!-- not applicable in v0.13+ -->",
    "LINK_PAYLOADS_JSON": "[{...}, {...}]",

    // Audit / debug paths
    "MD_PATH": "~/tse-jira-previews/RED-bug-<ts>.md",
    "HTML_PATH": "~/tse-jira-previews/RED-bug-<ts>.html",

    "SCREENSHOT_SOURCE_DIR": "~/Downloads/packages/162249/"
  },

  "loops": {
    // Arrays expanded by the script into repeating lines in the
    // template. Each loop kind has a specific shape:

    "preflight_checks": [
      // Each item is a fully-formatted <li> fragment (so the script
      // writer can apply class="warning" / "error" on a per-item basis).
      "<li>Project RED resolved to id 10020</li>",
      "<li>Bug issue type resolved to id 10004</li>",
      "<li class=\"warning\">Affected Orgs not auto-resolved...</li>"
    ],

    "issue_links": [
      // Each item is a structured object — the script renders the full
      // .issue-link <div> block from these fields.
      {
        "link_type": "Relates",
        "linked_key": "RED-176559",
        "linked_summary": "Customer is unable to use the Redis Cloud API..."
      },
      {
        "link_type": "Relates",
        "linked_key": "RED-184754",
        "linked_summary": "Need clarity for GCP CMEK deletion..."
      }
    ],

    "labels": [
      "CS",
      "terraform-provider",
      "active-active"
    ],

    "screenshots_to_attach": [
      "Override Region block.png",
      "AA East Fail.png",
      "AA West Fail.png",
      "image (1).png",
      "taxi-tf-gcp-redis-cloud-AA-database-feature-remote-backup.zip"
    ]
  }
}
```

## How the script handles loops

For each loop kind, the script finds the single example line/block in `preview-template.html` (matching the kind's placeholder tokens) and replaces it with one rendered line/block per array element. The replacement is in-place, so the surrounding HTML structure (containers, headings, footers) stays intact.

This is intentionally minimal templating — no Jinja, no Mustache, no dependencies. Pure stdlib `str.replace` and `re.sub`.

## When to update this schema

- Whenever the skill needs a new placeholder added to `preview-template.html`, add the placeholder name to both the template AND to `SCALAR_PLACEHOLDERS` in `render-html-preview.py`. Then document it here.
- Whenever a new loop kind is needed, add it to `LOOP_KINDS` in the script with the matching expansion logic.

## Skill responsibility

The skill (`SKILL.md` Workflow A) is responsible for:

1. Collecting all the field values during the bug interactive flow.
2. Converting the markdown description body to HTML (for `DESCRIPTION_HTML`) — this is the skill's responsibility, not the script's. Use the same markdown-to-HTML conversion rules consistently (H2 → `<h2>`, fenced code → `<pre><code>`, tables → `<table>`, etc.).
3. Writing the fields.json file (typically to a tmp path like `~/tse-jira-previews/RED-bug-<ts>.fields.json`).
4. Invoking the script via `Bash` tool with `--template`, `--input`, `--output`.
5. (Optional) deleting the fields.json after the HTML is written, since the .md preview file holds the same content in human-readable form.

This division means the script never has to know about Jira semantics — it's a dumb template engine. The skill carries all the domain knowledge.
