# redis-tse-tools

Umbrella **Claude Code marketplace** for Redis Technical Support Engineers. Currently hosts one plugin; future ones (RCA tooling, support-package analyzers, Grafana helpers, etc.) will land here too.

## Plugins in this marketplace

### `tse-jira` (v0.12.1)

Create Bug Jiras from Zendesk PDFs, multi-cluster RCA Jiras by cloning the canonical RCA-41 template, and compute the 8-130 impact score — all through the claude.ai Atlassian MCP, no API tokens required.

**Four slash commands:**
- `/tse-jira:new` — interactive router; asks Bug / RCA / Impact Score, then walks you through the inputs (recommended starting point)
- `/tse-jira:bug <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+] [--publish]`
- `/tse-jira:rca <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+] [--publish]`
- `/tse-jira:score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]`

**Interactive mode (v0.12+)** — each command also falls back to interactive prompts when invoked without args (or with ambiguous args). Validates inputs as you go: PDF paths via `ls`, Jira keys regex-checked then verified via `getJiraIssue` (read-only). Re-prompts on bad input rather than coasting forward.

**Grounded in Redis Customer Support team standards** ([Confluence](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958)) and verified against the live `redislabs.atlassian.net` schema. Not based on guesses.

**Spiritual successor to [`jira-helper`](https://github.com/markotrapani/jira-helper)** — same impact scoring model and conceptual field mapping, but Claude actually creates tickets via MCP instead of generating markdown for copy/paste.

[→ Full plugin docs](./plugins/tse-jira/skills/tse-jira-ticket-creation/SKILL.md) · [→ Roadmap](./plugins/tse-jira/ROADMAP.md)

#### What's new

- **v0.12.1** — added `ROADMAP.md` with performance / skill-encoded rules / discovery / UX / publishing themes. Docs-only.
- **v0.12.0** — interactive mode + `/tse-jira:new` router. RCA workflow now requires ≥1 Zendesk PDF in addition to ≥1 Jira (cluster-incident-shape exception preserved). Folds in real-TSE-practice corrections from the first production filing: integer Impact Score field, content goes in dedicated custom-field sections (Workaround / Impact Score details / Action Items), TSE-humble framing for code analysis ("Possible Root Cause — please verify" + "Asks for R&D"), compact title form `Topic [Customer]: symptom`, AI-assisted analysis acknowledged in the description, no fabricated content.
- **v0.11.0** — plugin renamed `tse-jira-ticket-creation` → `tse-jira`; commands split into 3 namespaced entries.

## Installation

### Add the marketplace + install plugin(s)

```bash
# 1. Add this marketplace
/plugin marketplace add markotrapani/redis-tse-tools

# 2. Install plugin(s) — currently just one
/plugin install tse-jira
```

### ⚠️ Strongly recommended: harness-level safety net

After installing, add the 10 Atlassian write tools to your `permissions.ask` list in `~/.claude/settings.json`. This ensures Claude Code will prompt before any write to Jira/Confluence, regardless of skill instructions.

See [**SECURITY.md**](./SECURITY.md) for the exact JSON snippet and rationale.

## Why this exists

Two existing tools each cover half the problem:

- **`everything-claude-code/jira-integration`** — generic `/jira get|comment|transition|search` for *existing* tickets. No creation logic.
- **`redislabsdev/agent-skills/jira-ticket-creation`** — full creation workflow but hardcoded to the Core Infra R&D team (RED project only, specific sprints, 3 components).

TSEs file across **many projects** (RED, MOD, DOC, RDSC, RCA) and rarely care about sprints. `tse-jira` fills that gap with:

- **Multi-project support** — auto-detects RED / MOD / DOC / RDSC from ticket content; supports any other project
- **Sprint-blank** by default — per Support docs
- **Severity is TSE-judged**, not computed (Support docs are explicit on this)
- **Priority left at Medium** by default — PM sets later during triage
- **Three TSE-specific workflows**: Bug from Zendesk, multi-cluster RCA by cloning RCA-41, impact scoring
- **Standards-aligned defaults**: `CS` / `Support` labels; Azure-specific tagging; A-A mapping table; log-reference format; Azure post-save RCA-template field
- **Impact-score breakdown posted as a comment**, not just a field (per Support standard)
- **Dry-run by default** — preview files at `~/tse-jira-previews/` before any write hits Jira

## Authoritative Sources

Every workflow rule in `tse-jira` is grounded in these Confluence docs (re-read on doubt):

1. [**Jira creation for Support**](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958) — CS team's Jira filing guide
2. [**Jira - Impact Score**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553) — 6-component scoring model
3. [**RCA Initiation and Data Collection Procedure**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753) — RCA procedure (clone RCA-41)
4. [**Internal R&D RCA Process**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4571660292) — overall RCA process and KPIs
5. [**RCA-41**](https://redislabs.atlassian.net/browse/RCA-41) — canonical RCA template ticket

## Dry-run is the default

**The Bug and RCA workflows do NOT write to Jira by default.** They produce a local markdown preview file at `~/tse-jira-previews/<project>-<workflow>-<timestamp>.md` that you review before publishing.

To actually file:
- Add `--publish` to the slash command, OR
- Run a dry-run first, review the preview, then say "publish this preview"

The Impact Score workflow is inherently read-only and doesn't have a publish step (it has a small follow-up to apply the score to a ticket, which counts as publish).

See [SECURITY.md](./SECURITY.md) for the full safety model.

## Prerequisites

The Jira plugin uses the **claude.ai Atlassian MCP** (`mcp__claude_ai_Atlassian__*` tools) for all Jira calls. You must have it connected:

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

## Usage — four slash commands

### Quick reference

```
# Interactive router (v0.12+): asks bug/rca/score, then walks you through inputs
/tse-jira:new

# Direct CLI form — default dry-run (writes .md + .html preview, no MCP writes)
/tse-jira:bug   <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+]
/tse-jira:rca   <zendesk-pdfs>+  -- <jira-pdfs-or-keys>+
/tse-jira:score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]

# Publish: actually fires MCP writes (harness still asks for confirmation per permissions.ask)
/tse-jira:bug   <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+] --publish
/tse-jira:rca   <zendesk-pdfs>+  -- <jira-pdfs-or-keys>+ --publish
```

The first set of args is **required** (one or more). The `--` separator marks the start of additional inputs (related Jiras for bug, Jiras-feeding-RCA for rca, supplemental Zendesk for score). `--publish` enables publish mode (default is dry-run). `score` is inherently read-only — no `--publish` flag.

**Each command also drops into interactive mode** if invoked without args or with insufficient inputs. The skill validates as it goes — PDF paths via `ls`, Jira keys via `getJiraIssue` (read-only) — and re-prompts on bad input rather than coasting forward.

### Workflow 0 — `/tse-jira:new` — interactive router

The simplest starting point. Three questions:

1. **Bug / RCA / Impact Score?** Picks the workflow.
2. **Where are the inputs?** Asks for PDF path(s), related Jiras, then any workflow-specific batched questions (severity for bug; customer / date / clusters for rca).
3. **Codebase investigation?** (Bug only) — asks before walking the Redis-owned source tree to ground "Possible Root Cause" / "Related Code Paths" in real file:line refs.

Then writes the dry-run preview and stops. Same publish flow as the direct commands.

### Workflow 1 — `/tse-jira:bug` — Bug Jira from Zendesk

**Inputs:** ≥1 Zendesk PDF (required), related Jira PDFs/keys (optional).

```bash
/tse-jira:bug ~/Downloads/redislabs.zendesk.com_tickets_162249_print.pdf
/tse-jira:bug ticket_162249.pdf -- RED-176559 RED-184754
```

What happens:
1. Reads the Zendesk PDF(s)
2. Extracts customer, summary, description, ticket ID
3. Computes the 8-130 impact score (6 components × multipliers) — **as a recommendation; team leader confirms**
4. Auto-detects project: RED (default), MOD if modules detected, DOC if docs-only, RDSC if RDI keywords
5. **Asks you to confirm Severity** (TSE-judged based on customer impact — not derived from impact score)
6. Maps all Support-standard fields (Severity, Component, Environment=Production, Product, Reported Version, Affected Organizations dropdown, Zendesk ID, Workaround, Data loss / unavail / Downtime, Impact Score, Labels including `CS`/`Support` + Azure tags)
7. Writes preview file at `~/tse-jira-previews/RED-bug-<timestamp>.md`
8. **In publish mode**: asks for final confirmation, then creates the Bug + posts impact-score breakdown comment + links related Jiras via `Relates`. For Azure tickets: populates `customfield_10063` with the `0. Incident short description:` template.
9. Returns Jira key + browse URL

### Workflow 2 — `/tse-jira:rca` — Multi-cluster RCA

**Inputs:** ≥1 Jira (PDF or live key) **required** — the related bug Jiras. ≥0 Zendesk PDFs (optional) for customer-impact context.

```bash
/tse-jira:rca RED-172012 RED-172734 -- ZD-146983.pdf ZD-146173.pdf
```

What happens:
1. Reads all Jiras (PDFs and/or live via MCP) and Zendesk PDFs
2. **Azure prerequisite check**: refuses if creating an Azure RCA without a RED/MOD bug among inputs (per Support docs)
3. Extracts bug summaries, action item drafts, log patterns, support-package S3 paths
4. Asks you once (batched): customer, date, clusters, start/end UTC, product, affected components, contributors
5. Builds RCA payload modeling **RCA-41's defaults** (project=RCA, type=10590, title `<Customer> - RCA <mm/dd/yyyy>`, description=Summary+Timeline, custom fields populated per Support standards)
6. Writes preview file at `~/tse-jira-previews/RCA-rca-<timestamp>.md`
7. **In publish mode**: asks for final confirmation, then creates the RCA, links each related bug via `Relates`
8. Returns RCA key + browse URL + checklist of placeholders + transition reminder

### Workflow 3 — `/tse-jira:score` — Impact Score Only

**Inputs:** ≥1 Jira (PDF or live key) **required**. Optional Zendesk PDFs after `--` supplement customer/frequency context.

No ticket creation by default. After scoring, the skill offers (on explicit "apply") to set `customfield_10585` and post a breakdown comment.

```bash
/tse-jira:score RED-172734
/tse-jira:score RED-172734 RED-172012 -- ZD-146983.pdf
```

## The Impact Score Model

Six components × optional multipliers, range **8 – 130**. Per [Confluence](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553):

| Component         | Range | What it measures                                         |
|-------------------|-------|----------------------------------------------------------|
| Impact & Severity | 0-38  | P1=38, P2=30, P3=22, P4=16, P5=8                         |
| Customer ARR      | 0-15  | >$1M=15, $500K-1M=13, $100K-500K=10                      |
| SLA Breach        | 0/8   | Binary; specific thresholds per topology                 |
| Frequency         | 0-16  | >4 occurrences=16, 2-4=8, single=0                       |
| Workaround        | 5-15  | None=15, perf-impact=12, complex=10, simple=5            |
| RCA Action Item   | 0/8   | Linked to RCA = 8                                        |
| **CloudOps multiplier** | 0-15% | Release blocker / high operational risk             |
| **Customer multiplier** | 0-15% | Renewal / churn / trust impact                      |

| Final Score | Priority Band |
|-------------|---------------|
| 90-130+     | CRITICAL      |
| 70-89       | HIGH          |
| 50-69       | MEDIUM        |
| 30-49       | LOW           |
| 8-29        | MINIMAL       |

> The "Priority Band" informs prioritization expectations to R&D — it's **separate** from the Jira `Priority` system field (left at default `Medium`, PM-set) and the Jira `Severity` custom field (TSE-judged customer impact). Don't conflate the three.

Full model with worked examples: [`plugins/tse-jira/skills/tse-jira-ticket-creation/references/impact-score-model.md`](./plugins/tse-jira/skills/tse-jira-ticket-creation/references/impact-score-model.md).

## Project Auto-Detection (Bug Workflow)

| Project | Match Rules                                                                                  |
|---------|----------------------------------------------------------------------------------------------|
| RDSC    | RDI, Redis Data Integration, Debezium, pipeline yml, CDC pipeline, jmespath, add_field      |
| MOD     | Module commands (`ft.`, `json.`, `ts.`, `bf.`), module version strings (`search:8.2.8`), `[RediSearch ...]` brackets |
| DOC     | Pure documentation issues — typos, broken links, no operational impact                       |
| RED     | Everything else (default)                                                                    |

## Marketplace Layout

```
redis-tse-tools/                              ← marketplace repo
├── .claude-plugin/
│   └── marketplace.json                      ← lists all plugins
├── plugins/
│   └── tse-jira/                             ← plugin (v0.12.1)
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── ROADMAP.md                         ← forward-looking plan
│       ├── skills/
│       │   └── tse-jira-ticket-creation/
│       │       ├── SKILL.md
│       │       └── references/
│       │           ├── jira-schema.md         # real field IDs, projects, link types
│       │           ├── impact-score-model.md  # 6-component model + SLA thresholds
│       │           ├── zendesk-bug-mapping.md # Bug filing rules per CS standards
│       │           ├── rca-template.md        # RCA Jira per DevOps procedure + RCA-41
│       │           ├── preview-template.html  # Jira-mimicking HTML preview
│       │           └── canonical-jiras/       # 12 canonical examples for anchoring
│       └── commands/
│           ├── new.md                         # /tse-jira:new (interactive router, v0.12+)
│           ├── bug.md                         # /tse-jira:bug
│           ├── rca.md                         # /tse-jira:rca
│           └── score.md                       # /tse-jira:score
├── README.md                                  ← you are here
├── SECURITY.md                                ← harness-level safety net guide
└── LICENSE
```

## Safety

- **No silent ticket creation.** Every bug / rca workflow writes a preview file first; publish requires explicit `--publish` or "publish this preview"
- **No auto-transition.** Tickets start in their default workflow state.
- **PII guard.** If PDFs contain phone numbers / internal emails, the skill flags before posting.
- **No edits to existing tickets** without showing a diff first.
- **Azure RCA gated.** Won't create an Azure RCA without a RED/MOD bug among the inputs (per Support docs).
- **Score is a recommendation.** Always flagged as needing team leader confirmation.
- **Harness-level safety net.** With the recommended `permissions.ask` rules from [SECURITY.md](./SECURITY.md), Claude Code will additionally prompt for every write call.

## Related Tools

- [`everything-claude-code/jira-integration`](https://github.com/everything-claude-code/everything-claude-code) — generic Jira read/comment/transition/search
- [`redislabsdev/agent-skills/jira-ticket-creation`](https://github.com/redislabsdev/agent-skills) — Core Infra R&D ticket creation
- [`markotrapani/jira-helper`](https://github.com/markotrapani/jira-helper) — Python CLI version (impact scoring, RCA generation; outputs markdown for copy/paste)

## Contributing

This marketplace is structured to accept new plugins:

```
plugins/
└── <new-plugin-name>/
    ├── .claude-plugin/
    │   └── plugin.json
    └── ...
```

Add an entry to `.claude-plugin/marketplace.json` with `"source": "./plugins/<new-plugin-name>"` and bump the marketplace `version`.

## License

MIT — see [LICENSE](./LICENSE).

## Author

Marko Trapani &lt;marko.trapani@redis.com&gt; — Redis Technical Support Engineer III
