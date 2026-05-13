# redis-tse-tools

Umbrella **Claude Code marketplace** for Redis Technical Support Engineers. Currently hosts one plugin; future ones (RCA tooling, support-package analyzers, Grafana helpers, etc.) will land here too.

> 📣 **New TSE? Just want to use it?**
> - **Marketplace overview** (what this is, contribution guide for new plugins):
>   - In Confluence (CS space → Support Tools): [Redis TSE Tools — Claude Code marketplace for the CS team](https://redislabs.atlassian.net/wiki/spaces/CS/pages/6290178075)
>   - In this repo: [`SHARING.md`](./SHARING.md)
> - **`tse-jira` plugin — 60-second install + first-use:**
>   - In Confluence: [tse-jira — Claude Code plugin for filing Jiras from Zendesk](https://redislabs.atlassian.net/wiki/spaces/CS/pages/6290243622)
>   - In this repo: [`plugins/tse-jira/SHARING.md`](./plugins/tse-jira/SHARING.md)
>
> Confluence is the easier landing point for TSEs new to the marketplace. The repo files are the canonical source; Confluence mirrors them and may lag.

## Plugins in this marketplace

### `tse-jira` (v0.14.1)

Create Bug Jiras from Zendesk PDFs, multi-cluster RCA Jiras by cloning the canonical RCA-41 template, and compute the 8-130 impact score — all through the claude.ai Atlassian MCP, no API tokens required.

**Four slash commands:**
- `/tse-jira:new` — interactive router; asks Bug / RCA / Impact Score, then walks you through the inputs (recommended starting point for new users)
- `/tse-jira:bug <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+] [--publish]`
- `/tse-jira:rca <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+] [--publish]`
- `/tse-jira:score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]`

**Interactive mode (v0.12+)** — each command also falls back to prompts when invoked without args. Validates inputs as you go: PDF paths via `ls`, Jira keys regex-checked then verified via `getJiraIssue` (read-only). Re-prompts on bad input.

**Grounded in Redis Customer Support team standards** ([Confluence](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958)) and verified against the live `redislabs.atlassian.net` schema. Not based on guesses.

**Spiritual successor to [`jira-helper`](https://github.com/markotrapani/jira-helper)** — same impact scoring model and conceptual field mapping, but Claude actually creates tickets via MCP instead of generating markdown for copy/paste.

[→ Full plugin docs](./plugins/tse-jira/skills/tse-jira-ticket-creation/SKILL.md) · [→ Roadmap](./plugins/tse-jira/ROADMAP.md) · [→ Plugin sharing guide](./plugins/tse-jira/SHARING.md) · [→ Marketplace sharing guide](./SHARING.md)

#### What's new

- **v0.14.1** *(2026-05-13, docs)* — README install guide overhaul + `SHARING.md` for team distribution + Confluence-ready one-pager. No behavior change.
- **v0.14.0** *(2026-05-13)* — Four targeted improvements from real-use feedback:
  - **HTML preview script** (`scripts/render-html-preview.py`) replaces write-from-scratch (~30s of agent token gen → ~1s)
  - **Glean Search** for semantically-related Jiras beyond what the Zendesk PDF cites
  - **Expand-macro hint markers** for long technical content (manual wrap in Jira UI post-publish)
  - **Terraform Provider component** request artifact drafted (`JIRA_ADMIN_REQUESTS/`) — pending Admin filing
- **v0.13.0** *(2026-05-13)* — Real-Jira-UI corrections folded into the skill: metadata content (Workaround, Impact Score details, Action Items) goes in **dedicated custom-field sections**, not duplicated as body H2s. Plus image-paste markers, optional `## Customer Impact`, horizontal-rule separators, one-line AI-acknowledgment, Zendesk-is-not-Jira relevance filter, auto-infer related Jiras from PDF text.
- **v0.12.1** *(2026-05-12, docs)* — added `ROADMAP.md`.
- **v0.12.0** *(2026-05-12)* — interactive mode + `/tse-jira:new` router. RCA requires ≥1 Zendesk PDF in addition to ≥1 Jira (cluster-incident-shape exception preserved). Real-TSE-practice corrections from first production filing: integer Impact Score field, TSE-humble framing for code analysis ("Possible Root Cause — please verify" + "Asks for R&D"), compact title form `Topic [Customer]: symptom`, no fabricated content.
- **v0.11.0** *(2026-05-12)* — plugin renamed `tse-jira-ticket-creation` → `tse-jira`; commands split into 3 namespaced entries.

---

## 🚀 Quick install (TSE-friendly, 5 steps)

### Step 1 — Prerequisites

| What | How |
|---|---|
| Claude Code installed | macOS: `brew install --cask claude-code` (or download from claude.ai/code). Other OS: see [claude.ai/code](https://claude.ai/code) |
| Authenticated as Redis | In Claude Code: `/login` → sign in with your `@redis.com` Google account |
| **claude.ai Atlassian MCP connected** | In Claude Code: `/mcp` → find `Atlassian` → `Authenticate` → sign in with your Redis Labs Atlassian account |

**Verify Atlassian MCP is connected** before proceeding:
```
mcp__claude_ai_Atlassian__getAccessibleAtlassianResources
```
Should return a resource with URL `https://redislabs.atlassian.net` and id `06f73ca7-8f2c-4392-b40a-08288e9d0ba3`. If not, redo the `/mcp` authentication step.

### Step 2 — Add the marketplace + install the plugin

```bash
# In Claude Code:
/plugin marketplace add markotrapani/redis-tse-tools
/plugin install tse-jira
/reload-plugins
```

`/reload-plugins` should report **31 skills** (or more) — that confirms `tse-jira` loaded.

### Step 3 — Add the safety net (strongly recommended)

The plugin defaults to dry-run, but for belt-and-suspenders safety add this `permissions.ask` block to your `~/.claude/settings.json` so Claude Code prompts before every Atlassian write call:

```jsonc
{
  "permissions": {
    "ask": [
      "mcp__claude_ai_Atlassian__createJiraIssue",
      "mcp__claude_ai_Atlassian__editJiraIssue",
      "mcp__claude_ai_Atlassian__transitionJiraIssue",
      "mcp__claude_ai_Atlassian__addCommentToJiraIssue",
      "mcp__claude_ai_Atlassian__createIssueLink",
      "mcp__claude_ai_Atlassian__addWorklogToJiraIssue",
      "mcp__claude_ai_Atlassian__createConfluencePage",
      "mcp__claude_ai_Atlassian__updateConfluencePage",
      "mcp__claude_ai_Atlassian__createConfluenceFooterComment",
      "mcp__claude_ai_Atlassian__createConfluenceInlineComment"
    ]
  }
}
```

Full rationale: [`SECURITY.md`](./SECURITY.md).

### Step 4 — Verify

In Claude Code:

```
/plugin
```
Should list `tse-jira (0.14.1)` with status `installed / enabled`. Type:

```
/tse-jira:new
```
You should see the router ask "Bug / RCA / Impact Score?" via an interactive prompt. Cancel the flow (Ctrl+C / `cancel`) — install is verified.

### Step 5 — First use (walkthrough)

Pick a real or test Zendesk PDF you've downloaded. Then:

```
/tse-jira:bug ~/Downloads/path/to/your-zendesk-ticket.pdf
```

The plugin will:
1. Read the PDF + any sibling screenshots in the same directory
2. Auto-detect customer, project, related Jiras (PDF text + Glean Search)
3. Ask you for severity (TSE-judged) and any clarifications
4. Optionally walk the relevant Redis-owned codebase to ground "Possible Root Cause" / "Related Code Paths"
5. **Write a dry-run preview** at `~/tse-jira-previews/<project>-bug-<timestamp>.{md,html}` and auto-open the HTML in your browser
6. **STOP — no MCP writes yet**

Review the preview. If it looks right, reply:

```
publish this preview
```

The skill asks one final confirmation, then fires `createJiraIssue` + `createIssueLink` calls (your harness will prompt per the safety net from Step 3). You get back a new Jira key and a checklist of remaining manual steps (file attachments, Impact Score Sheet screenshot).

---

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
- **Standards-aligned defaults**: `CS` / `Support` labels; Azure-specific tagging; A-A mapping table; log-reference format
- **Description body vs custom fields, done right** — Workaround / Impact Score details / Action Items go in dedicated Jira fields, not duplicated as body H2 sections (corrected in v0.13 after real-Jira-UI review)
- **Dry-run by default** — preview files at `~/tse-jira-previews/` before any write hits Jira

## Authoritative Sources

Every workflow rule in `tse-jira` is grounded in these Confluence docs (re-read on doubt):

1. [**Jira creation for Support**](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958) — CS team's Jira filing guide
2. [**Jira - Impact Score**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553) — 6-component scoring model
3. [**RCA Initiation and Data Collection Procedure**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753) — RCA procedure (clone RCA-41)
4. [**Internal R&D RCA Process**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4571660292) — overall RCA process and KPIs
5. [**RCA-41**](https://redislabs.atlassian.net/browse/RCA-41) — canonical RCA template ticket

## Dry-run is the default

**The Bug and RCA workflows do NOT write to Jira by default.** They produce local markdown + Jira-styled HTML preview files at `~/tse-jira-previews/<project>-<workflow>-<timestamp>.{md,html}` that you review before publishing.

To actually file:
- Add `--publish` to the slash command, OR
- Run a dry-run first, review the preview, then say something containing the word "**publish**" (e.g., `publish this preview`)

The Impact Score workflow is inherently read-only and doesn't have a publish step.

See [SECURITY.md](./SECURITY.md) for the full safety model.

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

The first set of args is **required**. The `--` separator marks the start of additional inputs. `--publish` enables publish mode (default is dry-run). `score` is inherently read-only — no `--publish` flag.

**Each command also drops into interactive mode** if invoked without args or with insufficient inputs.

### Workflow 0 — `/tse-jira:new` — interactive router

Asks "Bug / RCA / Impact Score?" then walks you through the inputs (PDF paths, related Jiras, severity, etc). Validates as it goes. Best starting point for new users.

### Workflow 1 — `/tse-jira:bug` — Bug Jira from Zendesk

**Inputs:** ≥1 Zendesk PDF (required), related Jira PDFs/keys (optional — auto-inferred from PDF text + Glean Search).

```bash
/tse-jira:bug ~/Downloads/redislabs.zendesk.com_tickets_162249_print.pdf
/tse-jira:bug ticket_162249.pdf -- RED-176559 RED-184754
```

### Workflow 2 — `/tse-jira:rca` — Multi-cluster RCA

**Inputs (both required as of v0.12):** ≥1 Zendesk PDF AND ≥1 Jira (PDF or live key). Cluster-incident-shape RCAs are the exception (automation-initiated, no customer Zendesk).

```bash
/tse-jira:rca RED-172012 RED-172734 -- ZD-146983.pdf ZD-146173.pdf
```

### Workflow 3 — `/tse-jira:score` — Impact Score Only

**Inputs:** ≥1 Jira (PDF or live key) **required**. Optional Zendesk PDFs after `--` supplement customer/frequency context. No ticket creation by default.

```bash
/tse-jira:score RED-172734
/tse-jira:score RED-172734 RED-172012 -- ZD-146983.pdf
```

## 🔧 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `/tse-jira:bug: Unknown command` | Plugin not loaded | `/plugin marketplace update redis-tse-tools` → `/plugin install tse-jira` → `/reload-plugins`. Then `/plugin` should list `tse-jira`. |
| `getAccessibleAtlassianResources` returns empty / errors | Atlassian MCP not authenticated for your Redis account | `/mcp` → find `Atlassian` → re-authenticate with `@redis.com` Atlassian login. |
| Skill says "Affected Organizations not auto-resolved" in pre-flight | Customer name didn't surface in first 5 pages of the 9,253-option dropdown | The Jira will still create; you'll just need to manually pick the customer in the Affected Orgs dropdown from the browser after publish. Skill will tell you which customer to pick. |
| `createJiraIssue` rejected with "Operation value must be an Atlassian Document" | Custom textarea field passed a string instead of ADF | Plugin bug — file an issue. Workaround: drop the offending field from the publish and add it manually in the browser. |
| `createJiraIssue` rejected with "Seen By Customer is required" | Project workflow rule on Environment=Production | Plugin auto-populates `customfield_10027` (Seen by Customer/s) — if you're still hitting this, the resolution may be a non-standard customer name. Manually pick from the dropdown in browser post-create. |
| HTML preview write was unexpectedly slow | Pre-v0.14 — plugin was writing the whole template from scratch | Update to v0.14.1+ which uses the `scripts/render-html-preview.py` template substitution. |
| Multi-account auth confusion (personal vs Redis) | `~/.claude/` is shared across identities | See `SHARING.md` for `CLAUDE_CONFIG_DIR`-based profile separation (set up `claude-redis` / `claude-personal` aliases in `~/.zshrc`). |
| "publish this preview" said but nothing happens | The skill is waiting for explicit `publish` keyword — "yes" / "go" / "looks good" don't count | Reply with a message containing the literal word **publish** referencing the preview file. |
| Want to file against a non-RED/MOD/DOC/RDSC project | Plugin supports any project via interactive override | After project auto-detection prompt, override with the project key (e.g., `OPCR`, `IR`, `PRB`). Skill will fetch field metadata dynamically. |

## The Impact Score Model

Six components × optional multipliers, range **8 – 130** (integer). Per [Confluence](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553):

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

**Where it lands in the Jira (v0.13+):** the integer score goes in `customfield_10585` (Impact Score). The full 6-component breakdown goes in `customfield_10681` (Impact Score details) — the **dedicated UI field section below the description**, NOT a body H2. TSE pastes a screenshot of the Google Sheet row into that field post-create.

Full model with worked examples: [`plugins/tse-jira/skills/tse-jira-ticket-creation/references/impact-score-model.md`](./plugins/tse-jira/skills/tse-jira-ticket-creation/references/impact-score-model.md).

## Project Auto-Detection (Bug Workflow)

| Project | Match Rules                                                                                  |
|---------|----------------------------------------------------------------------------------------------|
| RDSC    | RDI, Redis Data Integration, Debezium, pipeline yml, CDC pipeline, jmespath, add_field      |
| MOD     | Module commands (`ft.`, `json.`, `ts.`, `bf.`), module version strings (`search:8.2.8`), `[RediSearch ...]` brackets |
| DOC     | Pure documentation issues — typos, broken links, no operational impact                       |
| RED     | Everything else (default)                                                                    |

Skill asks you to confirm if auto-detection confidence is medium/low.

## Marketplace Layout

```
redis-tse-tools/                              ← marketplace repo
├── .claude-plugin/
│   └── marketplace.json                      ← lists all plugins
├── plugins/
│   └── tse-jira/                             ← plugin (v0.14.1)
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── ROADMAP.md                         ← forward-looking plan
│       ├── JIRA_ADMIN_REQUESTS/               ← draft requests to file
│       │   └── add-terraform-component.md
│       ├── scripts/                           ← (v0.14+) helper scripts
│       │   ├── render-html-preview.py         #   template-substitution rendering
│       │   └── fields.schema.md
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
├── SHARING.md                                 ← 60-second guide for team distribution
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
- **Field-correct by default (v0.13+).** Workaround / Impact Score details / Action Items go in dedicated Jira custom fields, not duplicated as body H2 sections.

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
