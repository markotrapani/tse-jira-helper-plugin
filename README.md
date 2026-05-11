# TSE Jira Helper Plugin

A Claude Code plugin for Redis **Technical Support Engineers**: create Bug Jiras from Zendesk PDFs, multi-cluster RCA Jiras by cloning the canonical RCA-41 template, and compute the 8-130 impact score — all through the claude.ai Atlassian MCP, no API tokens required.

**Grounded in Redis Customer Support team standards** ([Confluence](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958)) and verified against the live `redislabs.atlassian.net` schema. Not based on guesses.

> **Spiritual successor to [`jira-helper`](https://github.com/markotrapani/jira-helper).** Same impact scoring model and conceptual field mapping, but Claude actually creates tickets via MCP instead of generating markdown for copy/paste.

## Why this exists

Two existing tools each cover half the problem:

- **`everything-claude-code/jira-integration`** — generic `/jira get|comment|transition|search` for *existing* tickets. No creation logic.
- **`redislabsdev/agent-skills/jira-ticket-creation`** — full creation workflow but hardcoded to the Core Infra R&D team (RED project only, specific sprints, 3 components).

TSEs file across **many projects** (RED, MOD, DOC, RDSC, RCA) and rarely care about sprints. This plugin fills that gap with:

- **Multi-project support** — auto-detects RED / MOD / DOC / RDSC from ticket content; supports any other project
- **Sprint-blank** by default — per Support docs
- **Severity is TSE-judged**, not computed (Support docs are explicit on this)
- **Priority left at Medium** by default — PM sets later during triage
- **Three TSE-specific workflows**: Bug from Zendesk, multi-cluster RCA by cloning RCA-41, impact scoring
- **Standards-aligned defaults**: `CS` / `Support` labels; Azure-specific tagging; A-A mapping table; log-reference format; Azure post-save RCA-template field
- **Impact-score breakdown posted as a comment**, not just a field (per Support standard)

## Authoritative Sources

Every workflow rule is grounded in these Confluence docs (re-read on doubt):

1. [**Jira creation for Support**](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958) — CS team's Jira filing guide
2. [**Jira - Impact Score**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553) — 6-component scoring model
3. [**RCA Initiation and Data Collection Procedure**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753) — RCA procedure (clone RCA-41)
4. [**Internal R&D RCA Process**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4571660292) — overall RCA process and KPIs
5. [**RCA-41**](https://redislabs.atlassian.net/browse/RCA-41) — canonical RCA template ticket

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

The plugin uses the **claude.ai Atlassian MCP** (`mcp__claude_ai_Atlassian__*` tools) for all Jira calls. You must have it connected:

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
/tse-jira bug   <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+]
/tse-jira rca   <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]
/tse-jira score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]
```

The first set of args is **required** (one or more). The `--` separator marks the start of **optional** supporting inputs.

### Workflow 1 — Bug Jira from Zendesk

**Inputs:** ≥1 Zendesk PDF (required), related Jira PDFs/keys (optional).

```bash
/tse-jira bug ~/Downloads/redislabs.zendesk.com_tickets_154045_print.pdf
/tse-jira bug ticket_154045.pdf ticket_154046.pdf
/tse-jira bug ticket_154045.pdf -- RED-172012 RED-172734
```

What happens:
1. Reads the Zendesk PDF(s)
2. Extracts customer, summary, description, ticket ID
3. Computes the 8-130 impact score (6 components × multipliers) — **as a recommendation; team leader confirms**
4. Auto-detects project: RED (default), MOD if modules detected, DOC if docs-only, RDSC if RDI keywords
5. **Asks you to confirm Severity** (TSE-judged based on customer impact — not derived from impact score)
6. Maps all Support-standard fields:
   - Project, Issue Type (Bug), Summary (Azure: include cache name + region)
   - Severity (`customfield_10180`) — your judgment call
   - Priority — left at default `Medium` (PM bumps later)
   - Component (`customfield_10181`) — single-select, detected from content
   - Environment (`customfield_10025`) — `Production`
   - Product (`customfield_10026`) — `RS (Redis Software)` / `RCP` / `RCE`
   - Reported Version/Build
   - Affected Organizations (`customfield_10595`) — customer dropdown
   - Zendesk ID/s (`customfield_10036`) — numbers only
   - Workaround, Data loss / Data unavailable / Downtime (Y/N)
   - Event Status, Major Prod Channel, Metrics (Grafana link)
   - Impact Score number
   - Labels: always `CS` / `Support`; Azure tickets add `Azure-Integration` + `ACRE`/`AMR`; add `Azure_RCA_req` if RCA needed
7. Shows preview of every field; you confirm
8. Creates the Bug via MCP
9. **Posts the impact-score breakdown as a comment** (per Support standard, not as a field)
10. Links related Jiras (if provided) via `Relates`
11. For Azure tickets: populates `customfield_10063` (RCA) with the `0. Incident short description:` template
12. Returns Jira key + browse URL

### Workflow 2 — Multi-cluster RCA

**Inputs:** ≥1 Jira (PDF or live key) **required** — the related bug Jiras. ≥0 Zendesk PDFs (optional) for customer-impact context.

```bash
/tse-jira rca RED-172012 RED-172734 -- ZD-146983.pdf ZD-146173.pdf
/tse-jira rca RED-172012.pdf RED-172734.pdf
```

What happens:
1. Reads all Jiras (PDFs and/or live via MCP) and Zendesk PDFs
2. **Azure prerequisite check**: refuses if creating an Azure RCA without a RED/MOD bug among inputs (per Support docs)
3. Extracts bug summaries, action item drafts, log patterns, support-package S3 paths
4. Asks you once (batched): customer, date, clusters, start/end UTC, product, affected components, contributors
5. Builds RCA payload modeling **RCA-41's defaults**:
   - Project `RCA`, Type `RCA` (id 10590) — NOT Support RCA
   - Title: `<Customer> - RCA <mm/dd/yyyy>` (or ClusterID / Major Service for multi-customer)
   - Description = Summary + Timeline table only (everything else in custom fields)
   - Custom fields: Start/End time (UTC), Zendesk list, Slack channel, Initial Root Cause, Action items table (with placeholders for Description/Type/Owner/Ticket), Cluster ID, Account name, Account ID, Product, Affected component, Is Customer RCA needed? = Yes, Contributors
   - Status: `Data Collection` (initial)
6. Preview, you confirm
7. Creates the RCA
8. Links each related bug via `createIssueLink` (type `Relates`)
9. Returns RCA key + browse URL + checklist of placeholders to fill manually:
   - Final Root Cause (Engineering owns)
   - Action item owners + Jira ticket keys
   - Customer RCA URL when generated
10. Reminder: transition `Data Collection` → `Root Cause and Action Items` when data entry complete (Slack notifications auto-post to `#root-cause-analysis`)

### Workflow 3 — Impact Score Only

**Inputs:** ≥1 Jira (PDF or live key) **required**. Optional Zendesk PDFs after `--` supplement customer/frequency context.

No ticket creation:

```bash
/tse-jira score RED-172734
/tse-jira score RED-172734 RED-172012
/tse-jira score RED-172734 -- ZD-146983.pdf ZD-146173.pdf
```

Output:
```
IMPACT SCORE: 78.0 (HIGH)
Base: 78  Multipliers: CloudOps=0, Customer=0

| Component         | Score | Max | Reasoning                          |
|-------------------|-------|-----|------------------------------------|
| Impact & Severity | 30    | 38  | P2 — service degraded              |
| Customer ARR      | 15    | 15  | Azure (>$1M)                       |
| SLA Breach        | 8     | 8   | Breach claim in ticket             |
| ...               | ...   | ... | ...                                |

Per Support standard, the team leader should confirm this score before applying.
```

After scoring, the skill offers (on your explicit yes) to apply the score to the Jira(s) by setting `customfield_10585` and posting a breakdown comment.

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

Full model with worked examples: [`skills/tse-jira-ticket-creation/references/impact-score-model.md`](skills/tse-jira-ticket-creation/references/impact-score-model.md).

## Project Auto-Detection (Bug Workflow)

| Project | Match Rules                                                                                  |
|---------|----------------------------------------------------------------------------------------------|
| RDSC    | RDI, Redis Data Integration, Debezium, pipeline yml, CDC pipeline, jmespath, add_field      |
| MOD     | Module commands (`ft.`, `json.`, `ts.`, `bf.`), module version strings (`search:8.2.8`), `[RediSearch ...]` brackets |
| DOC     | Pure documentation issues — typos, broken links, no operational impact                       |
| RED     | Everything else (default)                                                                    |

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
│           ├── jira-schema.md         # real field IDs, projects, link types (verified)
│           ├── impact-score-model.md  # 6-component model + multipliers + SLA thresholds
│           ├── zendesk-bug-mapping.md # Bug filing rules per CS Support standards
│           └── rca-template.md        # RCA Jira creation per DevOps procedure + RCA-41
├── commands/
│   └── tse-jira.md          # /tse-jira slash command
├── README.md
└── LICENSE
```

## Safety

- **No silent ticket creation.** Every bug / rca workflow previews fields and waits for explicit confirmation.
- **No auto-transition.** Tickets start in their default workflow state.
- **PII guard.** If PDFs contain phone numbers / internal emails, the skill flags before posting.
- **No edits to existing tickets** without showing a diff first.
- **Azure RCA gated.** Won't create an Azure RCA without a RED/MOD bug among the inputs (per Support docs).
- **Score is a recommendation.** Always flagged as needing team leader confirmation.

## Related Tools

- [`everything-claude-code/jira-integration`](https://github.com/everything-claude-code/everything-claude-code) — generic Jira read/comment/transition/search
- [`redislabsdev/agent-skills/jira-ticket-creation`](https://github.com/redislabsdev/agent-skills) — Core Infra R&D ticket creation
- [`markotrapani/jira-helper`](https://github.com/markotrapani/jira-helper) — Python CLI version (impact scoring, RCA generation; outputs markdown for copy/paste)

## License

MIT — see [LICENSE](./LICENSE).

## Author

Marko Trapani &lt;marko.trapani@redis.com&gt; — Redis Technical Support Engineer III
