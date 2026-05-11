---
description: Create Redis Jira tickets as a TSE — Bug from Zendesk PDF, multi-cluster RCA from Zendesk + Jira PDFs, or impact score estimation. Uses the tse-jira-ticket-creation skill and the claude.ai Atlassian MCP.
argument-hint: <bug|rca|score> [files...]
---

# /tse-jira

Shortcut for the `tse-jira-ticket-creation` skill. Always confirms a preview before creating any Jira issue.

## Usage

```
/tse-jira bug <zendesk-pdf> [related-jira-pdfs...]
/tse-jira rca <zendesk-pdfs...> -- <jira-pdfs...>
/tse-jira score <zendesk-pdf | jira-pdf | JIRA-KEY | "free text">
```

## Subcommands

### `/tse-jira bug <zendesk-pdf> [related-jira-pdfs...]`

Create a Bug Jira from a Zendesk PDF. Optionally attach related Jira PDFs to be linked via `Relates`.

**Input:**
- 1st arg: path to Zendesk PDF (required)
- 2nd+ args: paths to related Jira PDFs (optional)

**Behavior:**
1. Invoke `tse-jira-ticket-creation` skill, Workflow A
2. Read PDFs, compute impact score, auto-detect project (RED/MOD/DOC/RDSC)
3. Map fields per `references/zendesk-bug-mapping.md`
4. Preview the structured ticket
5. **Ask the user to confirm** before calling `mcp__claude_ai_Atlassian__createJiraIssue`
6. On confirmation, create the Bug and (if related Jira PDFs were provided) call `createIssueLink` for each
7. Return the new Jira key + browse URL

**Example:**
```
/tse-jira bug ~/Downloads/redislabs.zendesk.com_tickets_154045_print.pdf
/tse-jira bug ticket_154045.pdf RED-172012.pdf RED-172734.pdf
```

### `/tse-jira rca <zendesk-pdfs...> -- <jira-pdfs...>`

Create a multi-cluster RCA. Both Zendesk and Jira PDFs are required — the `--` separator splits them.

**Input:**
- Args before `--`: Zendesk PDF paths (one or more)
- Args after `--`: Jira PDF paths (one or more, related bug Jiras)
- Will also prompt for: customer name, date (MM/DD/YY), cluster names, regions, affected component

**Behavior:**
1. Invoke `tse-jira-ticket-creation` skill, Workflow B
2. Read all PDFs
3. Extract timeline events, bug summaries, log patterns, support package links
4. Ask the user for the missing metadata (customer/date/clusters/regions/component) in one batched question
5. Build the RCA per `references/rca-template.md`
6. Preview the full description
7. **Ask the user to confirm** before calling `createJiraIssue`
8. On confirmation, create the RCA in the "Root Cause Analysis" project
9. Call `createIssueLink` for each related bug Jira (`Relates` type)
10. Return RCA key + browse URL + a checklist of "still needs human input" items

**Example:**
```
/tse-jira rca ZD-146983.pdf ZD-146173.pdf ZD-146404.pdf -- RED-172012.pdf RED-172734.pdf
```

### `/tse-jira score <input>`

Compute the impact score without creating any ticket. Triage / planning tool.

**Input** (any one of):
- Path to a Zendesk PDF
- Path to a Jira PDF
- Existing Jira key (e.g., `RED-172734`) — fetched via `mcp__claude_ai_Atlassian__getJiraIssue`
- Quoted free text describing the issue

**Behavior:**
1. Invoke `tse-jira-ticket-creation` skill, Workflow C
2. Source the content (read PDF, fetch Jira, or use text)
3. Apply the 6-component model from `references/impact-score-model.md`
4. Output structured breakdown:
   ```
   IMPACT SCORE: <n> (<BAND>)
   Base: <n>  Multipliers: Support=<n> Account=<n>

   | Component | Score | Max | Reasoning |
   | ...       | ...   | ... | ...       |
   ```
5. Do **not** create a ticket.

**Examples:**
```
/tse-jira score ~/Downloads/redislabs.zendesk.com_tickets_154045_print.pdf
/tse-jira score RED-172734
/tse-jira score "DMC high CPU on Azure customer rediscluster-ktcsproda11, multiple recurrences, no SLA breach yet, manual restart workaround"
```

## Prerequisites

This command requires the **claude.ai Atlassian MCP** to be authenticated. If you see an auth error on first run:

1. Run `mcp__claude_ai_Atlassian__authenticate` (or use `/mcp` in Claude Code and re-auth)
2. Confirm your Redis Labs cloud ID via `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources` — should return `06f73ca7-8f2c-4392-b40a-08288e9d0ba3` for `redislabs.atlassian.net`

No environment variables or API tokens needed — the claude.ai MCP handles auth.

## Safety

- **No silent creation.** Every `bug` or `rca` invocation previews the ticket and waits for explicit user confirmation.
- **PII guard.** If the PDF content includes phone numbers, internal customer emails, or other PII, the skill will flag it and ask you to redact before posting.
- **No auto-transition.** The new ticket starts in its default workflow state. You transition it manually.
- **Editing existing tickets is not in scope here** — for that use the ECC `jira-integration` skill or `/jira` command.

## Related

- **Skill:** `skills/tse-jira-ticket-creation/` (full reference docs in `references/`)
- **Complementary:** `everything-claude-code:jira-integration` skill / `/jira` for retrieving, commenting on, and transitioning existing tickets
- **Inspired by:** `~/Downloads/marko-projects/jira-helper` (Python CLI version, generates markdown for copy/paste rather than creating tickets directly)
