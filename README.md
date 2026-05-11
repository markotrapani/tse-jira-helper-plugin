# TSE Jira Helper Plugin

A Claude Code plugin for Redis **Technical Support Engineers**: create Bug Jiras from Zendesk PDFs, multi-cluster RCA Jiras from Zendesk + Jira PDFs, and compute the 8-130 TSE impact score — all through the claude.ai Atlassian MCP, no API tokens required.

> **Spiritual successor to [`jira-helper`](https://github.com/markotrapani/jira-helper).** Same impact scoring model and Zendesk→Jira field mapping, but Claude actually creates the tickets via MCP instead of generating markdown for copy/paste.

## Why this exists

Two existing tools each cover half the problem:

- **`everything-claude-code/jira-integration`** — generic `/jira get|comment|transition|search` for *existing* tickets. No creation logic.
- **`redislabsdev/agent-skills/jira-ticket-creation`** — full creation workflow but hardcoded to the Core Infra R&D team (RED project, specific sprints, 3 components).

TSEs file across **many projects** (RED, MOD, DOC, RDSC, RCA) and rarely care about sprints. This plugin fills that gap with:

- **Multi-project support** — auto-detects RED / MOD / DOC / RDSC from ticket content; supports any other project on `redislabs.atlassian.net`
- **Sprint-optional** — defaults to backlog; only asks about sprint if you explicitly want it
- **All component options** — fetched dynamically per project, no hardcoded list
- **TSE-specific workflows** — Zendesk PDF → Bug, multi-cluster RCA, impact scoring

## Installation

### Via Claude Code plugin marketplace (recommended)

```bash
# 1. Add this marketplace
/plugin marketplace add markotrapani/tse-jira-helper-plugin

# 2. Install the plugin
/plugin install tse-jira-ticket-creation
```

### Manual install

```bash
git clone https://github.com/markotrapani/tse-jira-helper-plugin.git
cp -r tse-jira-helper-plugin/skills/tse-jira-ticket-creation ~/.claude/skills/
cp tse-jira-helper-plugin/commands/tse-jira.md ~/.claude/commands/
```

## Prerequisites

The plugin uses the **claude.ai Atlassian MCP** (`mcp__claude_ai_Atlassian__*` tools) for all Jira API calls. You must have it connected:

```bash
# In Claude Code
/mcp
# Find Atlassian → Authenticate → sign in with your Redis Labs Atlassian account
```

No `JIRA_URL`, `JIRA_EMAIL`, or `JIRA_API_TOKEN` needed — auth is handled by the claude.ai MCP.

Confirm with:
```
mcp__claude_ai_Atlassian__getAccessibleAtlassianResources
```
Expected to return a resource with URL `https://redislabs.atlassian.net` and id `06f73ca7-8f2c-4392-b40a-08288e9d0ba3`.

## Usage

### Quick reference

```
/tse-jira bug <zendesk-pdf> [related-jira-pdfs...]
/tse-jira rca <zendesk-pdfs...> -- <jira-pdfs...>
/tse-jira score <zendesk-pdf | jira-pdf | JIRA-KEY | "free text">
```

### Workflow 1 — Bug Jira from Zendesk

Inputs: **Zendesk PDF (required) + related Jira PDFs (optional)**.

```
/tse-jira bug ~/Downloads/redislabs.zendesk.com_tickets_154045_print.pdf
```

What happens:
1. Reads the Zendesk PDF
2. Extracts customer, summary, description, ticket ID, etc.
3. Computes the 8-130 impact score (6 components × multipliers)
4. Auto-detects project: RED (default), MOD if modules detected, DOC if docs-only, RDSC if RDI keywords
5. Maps priority + severity from the score band
6. Shows you a preview of every field
7. **Asks you to confirm** before posting
8. Creates the Bug via MCP and returns the new key + URL

If you pass related Jira PDFs, they get added as `Relates` issue links after creation.

### Workflow 2 — Multi-cluster RCA

Inputs: **Zendesk PDFs and Jira PDFs (both required)**.

```
/tse-jira rca ZD-146983.pdf ZD-146173.pdf -- RED-172012.pdf RED-172734.pdf
```

What happens:
1. Reads all PDFs in parallel
2. Extracts timeline events, log patterns, support package links from Zendesk PDFs
3. Extracts bug summaries, initial root cause hypotheses, action items from Jira PDFs
4. Asks you once for: customer name, date, cluster names, regions, affected component
5. Builds the full RCA description (summary, timeline table, logs section, links, action items table)
6. Shows you the rendered preview
7. **Asks you to confirm** before posting
8. Creates the RCA in the "Root Cause Analysis" project
9. Links each related bug via `createIssueLink`
10. Returns the RCA key + checklist of placeholders (Final Root Cause, action item owners) for you to fill

### Workflow 3 — Impact Score Only

Just want to know what the score would be? No ticket creation:

```
/tse-jira score ~/Downloads/redislabs.zendesk.com_tickets_154045_print.pdf
/tse-jira score RED-172734
/tse-jira score "DMC high CPU on Azure customer, multiple recurrences, no SLA breach"
```

Output:
```
IMPACT SCORE: 78.0 (HIGH)
Base: 78  Multipliers: Support=0, Account=0

| Component         | Score | Max | Reasoning                          |
|-------------------|-------|-----|------------------------------------|
| Impact & Severity | 30    | 38  | P2 — service degraded              |
| Customer ARR      | 15    | 15  | Azure (>$1M)                       |
| SLA Breach        | 8     | 8   | Breach claim in ticket             |
| ...               | ...   | ... | ...                                |
```

## The Impact Score Model

Six components × optional multipliers, range **8 – 130**:

| Component         | Range | What it measures                                         |
|-------------------|-------|----------------------------------------------------------|
| Impact & Severity | 0-38  | P1=38, P2=30, P3=22, P4=16, P5=8                         |
| Customer ARR      | 0-15  | >$1M=15, $500K-1M=13, $100K-500K=10                      |
| SLA Breach        | 0/8   | Binary                                                   |
| Frequency         | 0-16  | >4 occurrences=16, 2-4=8, single=0                       |
| Workaround        | 5-15  | None=15, performance-impact=12, complex=10, simple=5     |
| RCA Action Item   | 0/8   | Linked to an RCA = 8                                     |
| Support multiplier| 0-15% | Account at retention risk                                |
| Account multiplier| 0-15% | Blocking support team workflow                           |

| Final Score | Priority Band |
|-------------|---------------|
| 90-130+     | CRITICAL      |
| 70-89       | HIGH          |
| 50-69       | MEDIUM        |
| 30-49       | LOW           |
| 8-29        | MINIMAL       |

Full model with keyword indicators and worked examples: see [`skills/tse-jira-ticket-creation/references/impact-score-model.md`](skills/tse-jira-ticket-creation/references/impact-score-model.md).

## Project Auto-Detection

For the Bug workflow, the project is auto-detected from ticket content (you can always override):

| Project | Match Rules                                                                                  |
|---------|----------------------------------------------------------------------------------------------|
| RDSC    | RDI, Redis Data Integration, Debezium, pipeline yml, CDC pipeline, jmespath, add_field      |
| MOD     | Module commands (`ft.`, `json.`, `ts.`, `bf.`), module version strings (`search:8.2.8`), `[RediSearch ...]` brackets |
| DOC     | Pure documentation issues — typos, broken links, no operational impact                       |
| RED     | Everything else (default) — Redis Software / Cloud operational issues                        |

## Plugin Layout

```
tse-jira-helper-plugin/
├── .claude-plugin/
│   ├── plugin.json          # plugin manifest
│   └── marketplace.json     # marketplace listing (single-plugin)
├── skills/
│   └── tse-jira-ticket-creation/
│       ├── SKILL.md         # main skill
│       └── references/
│           ├── impact-score-model.md
│           ├── zendesk-bug-mapping.md
│           └── rca-template.md
├── commands/
│   └── tse-jira.md          # /tse-jira slash command
├── README.md
└── LICENSE
```

## Safety

- **No silent ticket creation.** Every bug or rca workflow previews fields and waits for explicit confirmation.
- **No auto-transition.** Tickets start in their default workflow state.
- **PII guard.** If the source PDFs contain phone numbers or internal emails, the skill flags them before posting.
- **No edits to existing tickets.** Use the ECC `jira-integration` skill / `/jira` command for that.

## Related Tools

- [`everything-claude-code/jira-integration`](https://github.com/everything-claude-code/everything-claude-code) — generic Jira read/comment/transition/search
- [`redislabsdev/agent-skills/jira-ticket-creation`](https://github.com/redislabsdev/agent-skills) — Core Infra R&D ticket creation
- [`markotrapani/jira-helper`](https://github.com/markotrapani/jira-helper) — Python CLI version (impact scoring, RCA generation; outputs markdown for copy/paste)

## License

MIT — see [LICENSE](./LICENSE).

## Author

Marko Trapani &lt;marko.trapani@redis.com&gt; — Redis Technical Support Engineer III
