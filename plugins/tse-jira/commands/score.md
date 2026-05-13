---
description: Compute the 8-130 impact score for one or more existing Jira tickets. Inherently read-only — no --publish flag needed. After scoring, optionally applies the score to the Jira on explicit user request.
argument-hint: <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]
---

# /tse-jira:score

Shortcut for the `tse-jira-ticket-creation` skill — Workflow C (impact score estimation). Triage / planning tool. **Inherently read-only — no `--publish` flag needed.** After scoring, the skill can optionally apply the score to the Jira(s) only when you explicitly say "publish to RED-NNN". Based on the Redis [Jira Impact Score doc](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553).

## Usage

```
/tse-jira:score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]
```

**Input contract** — one or more Jira PDFs or live Jira keys are **required**. The optional second set after `--` provides Zendesk PDFs for supplemental customer/frequency context.

### Invoking without arguments — interactive mode (v0.12+)

`/tse-jira:score` with no arguments drops into **interactive mode**: asks for the Jira key(s) or PDF path(s), then offers supplemental Zendesk context. Validation runs as you go — malformed keys re-prompt, live keys are verified via `getJiraIssue` (read-only). See [SKILL.md → Interactive Mode](../skills/tse-jira-ticket-creation/SKILL.md).

## Behavior

Invokes the `tse-jira-ticket-creation` skill, Workflow C:
1. Sources content (live Jira via `getJiraIssue`; PDFs via Read; Zendesk PDFs supplement)
2. Applies the 6-component model with multipliers (CloudOps / Customer):
   - Impact & Severity (0–38)
   - Customer ARR (0–15)
   - SLA Breach (0 / 8)
   - Frequency (0–16)
   - Workaround (5–15)
   - RCA Action Item (0 / 8)
   - × CloudOps multiplier (0–15%)
   - × Customer multiplier (0–15%)
   - → Final score 8–130
3. Outputs structured breakdown (markdown table)
4. Does **not** create or modify any ticket
5. After scoring, offers (on explicit user "publish to RED-NNN"): apply the score to the Jira(s) by setting `customfield_10585` and posting a breakdown comment

## Examples

```
/tse-jira:score RED-172734
/tse-jira:score RED-172734 RED-172012
/tse-jira:score RED-172734 -- ZD-146983.pdf ZD-146173.pdf
```

## Prerequisites

### Claude.ai Atlassian MCP authenticated (for live Jira fetches)

```
/mcp
# Find Atlassian → Authenticate → sign in with your Redis Labs Atlassian account
```

Confirm with `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources` — should return id `06f73ca7-8f2c-4392-b40a-08288e9d0ba3` for `redislabs.atlassian.net`.

Not strictly required if all inputs are PDFs.

## Safety

- **Read-only by default.** No MCP writes unless you explicitly say "publish to RED-NNN".
- **Score is a recommendation.** Per Support docs, impact scores should be confirmed by the team leader before any field updates.
- **Top-level go doesn't cover later steps.** Each destructive write call re-confirms.

## Related

- **Skill:** [`../skills/tse-jira-ticket-creation/SKILL.md`](../skills/tse-jira-ticket-creation/SKILL.md) — Workflow C + scoring model in `references/impact-score-model.md`
- **Sibling commands:** `/tse-jira:bug`, `/tse-jira:rca`
- **Harness safety:** [`SECURITY.md`](../../../SECURITY.md)
