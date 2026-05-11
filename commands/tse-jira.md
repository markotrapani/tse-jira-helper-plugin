---
description: Create Redis Jira tickets as a TSE — Bug from Zendesk PDFs, RCA by cloning RCA-41 (Jira + Zendesk PDFs), or impact score estimation. Uses the tse-jira-ticket-creation skill and the claude.ai Atlassian MCP. Aligned with Redis CS Support team Confluence standards.
argument-hint: <bug|rca|score> <required-inputs>+ [-- <optional-inputs>+]
---

# /tse-jira

Shortcut for the `tse-jira-ticket-creation` skill. Always confirms a preview before creating any Jira issue. Aligned with Redis Customer Support team standards documented in [Confluence](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958).

## Usage

```
/tse-jira bug   <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+]
/tse-jira rca   <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]
/tse-jira score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]
```

**Input contract** — the first set of args is **required** (one or more), the optional second set after `--` provides supporting context.

## Subcommands

### `/tse-jira bug <zendesk-pdf>+ [-- <jira-pdfs>+]`

Create a Bug Jira from one or more Zendesk PDFs. Optionally attach related Jira PDFs to be linked via `Relates`.

**Required:** one or more Zendesk PDF paths
**Optional:** related Jira PDFs or live Jira keys (after `--`)

**Behavior** — invokes `tse-jira-ticket-creation` skill, Workflow A:
1. Reads the Zendesk PDF(s)
2. Extracts customer, summary, description, ticket ID, etc.
3. Computes the 8-130 impact score (recommendation, team leader confirms)
4. Auto-detects project: RED (default), MOD (modules), DOC (docs), RDSC (RDI)
5. Asks the TSE to confirm Severity (TSE-judged, not impact-derived)
6. Maps all Support-standard fields (labels include `CS` / `Support`; Azure tickets get `Azure-Integration` + `ACRE`/`AMR`)
7. Leaves Priority at default `Medium` (PM sets later)
8. Builds description with Customer Expectations, A-A mapping (if applicable), log-ref format
9. Shows you a preview of every field
10. **Asks you to confirm** before posting
11. Creates the Bug via MCP
12. Posts impact-score breakdown as a **comment** (per Support standard)
13. Links related Jira PDFs (if any) via `Relates` (id 10003)
14. For Azure tickets: post-save `editJiraIssue` to populate `customfield_10063` (RCA) with the `0. Incident short description:` template

**Examples:**
```
/tse-jira bug ~/Downloads/redislabs.zendesk.com_tickets_154045_print.pdf
/tse-jira bug ticket_154045.pdf ticket_154046.pdf
/tse-jira bug ticket_154045.pdf -- RED-172012.pdf RED-172734.pdf
/tse-jira bug ticket_154045.pdf -- RED-172012
```

### `/tse-jira rca <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]`

Create a multi-cluster RCA by cloning RCA-41's defaults. Requires at least one Jira (the related bug Jira(s) that feed the root cause analysis).

**Required:** one or more Jira PDFs OR live Jira keys
**Optional:** Zendesk PDFs (after `--`) for customer-impact context

You'll also be asked once for:
- Customer name (or ClusterID / Major Service for multi-customer)
- Incident date (`mm/dd/yyyy`)
- Cluster names
- Start time and End time (UTC)
- Product: `Redis Cloud` / `Redis Software` / `AMR`
- Affected components (multi-select from 44 options)
- Contributors

**Behavior** — invokes `tse-jira-ticket-creation` skill, Workflow B:
1. Reads all Jira (PDF or live) and Zendesk PDFs
2. **Azure prerequisite check**: refuses if Azure RCA without a RED/MOD bug among the inputs
3. Extracts bug summaries, action items drafts, log patterns from Jira PDFs
4. Extracts customer impact, support-package paths from Zendesk PDFs
5. Builds RCA payload modeling RCA-41 defaults:
   - Project: `RCA` (10245), Type: `RCA` (10590) — **NOT Support RCA**
   - Title: `<Customer> - RCA <mm/dd/yyyy>` (or ClusterID / Major Service)
   - Description: Summary + Timeline (everything else in custom fields)
   - Custom fields: Initial Root Cause, Action items table (with red instruction line), Cluster ID, Account name, Product, Zendesk list, Slack channel, etc.
   - Reporter: current user
   - Status: `Data Collection` (initial)
6. Shows you the rendered preview
7. **Asks you to confirm** before posting
8. Creates the RCA in the "Root Cause Analysis" project
9. Links each related bug via `createIssueLink` (type `Relates`)
10. Returns RCA key + browse URL + checklist of placeholders (Final Root Cause, action item owners, etc.)
11. Reminder to transition `Data Collection` → `Root Cause and Action Items` when data entry is complete

**Examples:**
```
/tse-jira rca RED-172012.pdf RED-172734.pdf -- ZD-146983.pdf ZD-146173.pdf
/tse-jira rca RED-172012 RED-172734
/tse-jira rca RED-172012.pdf
```

### `/tse-jira score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]`

Compute the impact score for one or more existing Jira tickets without creating anything. Triage / planning tool.

**Required:** one or more Jira inputs (PDF or live key)
**Optional:** Zendesk PDFs (after `--`) for supplemental customer/frequency context

**Behavior** — invokes `tse-jira-ticket-creation` skill, Workflow C:
1. Sources content (live Jira via `getJiraIssue`; PDFs via Read; Zendesk PDFs supplement)
2. Applies the 6-component model with multipliers (CloudOps / Customer)
3. Outputs structured breakdown:
   ```
   IMPACT SCORE: 78.0 (HIGH)
   Base: 78  Multipliers: CloudOps=0, Customer=0

   | Component         | Score | Max | Reasoning                          |
   |-------------------|-------|-----|------------------------------------|
   | Impact & Severity | 30    | 38  | P2 — service degraded              |
   | Customer ARR      | 15    | 15  | Azure (>$1M)                       |
   | ...               | ...   | ... | ...                                |

   Per Support standard, the team leader should confirm this score before applying.
   ```
4. Does **not** create or modify any ticket.
5. Offers (on explicit user "yes"): apply the score to the Jira(s) by setting `customfield_10585` and posting a breakdown comment.

**Examples:**
```
/tse-jira score RED-172734
/tse-jira score RED-172734 RED-172012
/tse-jira score RED-172734.pdf -- ZD-146983.pdf ZD-146173.pdf
/tse-jira score RED-172012 RED-172734 -- support_ticket_154045.pdf
```

## Prerequisites

This command requires the **claude.ai Atlassian MCP** to be authenticated. If you see an auth error on first run:

1. Run `/mcp` in Claude Code → Atlassian → Authenticate (sign in with your Redis Labs Atlassian account)
2. Confirm your Redis Labs cloud ID via `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources` — should return `06f73ca7-8f2c-4392-b40a-08288e9d0ba3` for `redislabs.atlassian.net`

No environment variables or API tokens needed.

## Safety

- **No silent creation.** Every `bug` / `rca` invocation previews the ticket and waits for explicit user confirmation.
- **PII guard.** If source PDFs contain phone numbers, internal customer emails, or other PII, the skill flags it and asks you to redact before posting.
- **No auto-transition.** New tickets start in default workflow state — you transition manually.
- **No auto-edits.** Existing ticket fields are never overwritten without showing a diff first.
- **Score is a recommendation.** Per Support docs, impact scores should be confirmed by the team leader.
- **Azure RCA needs a Bug.** The skill refuses to create an Azure RCA without a RED/MOD bug among the related Jiras (per Support docs).

## Related

- **Skill:** [`skills/tse-jira-ticket-creation/`](../skills/tse-jira-ticket-creation/SKILL.md) — full reference docs in `references/`
- **Complementary:** [`everything-claude-code/jira-integration`](../../everything-claude-code/skills/jira-integration/) + `/jira` for retrieving / commenting on / transitioning existing tickets
- **Inspired by:** [`~/Downloads/marko-projects/jira-helper`](https://github.com/markotrapani/jira-helper) (Python CLI version that generates markdown rather than creating tickets directly)
