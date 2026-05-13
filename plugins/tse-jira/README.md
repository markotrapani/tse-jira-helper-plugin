# tse-jira

Claude Code plugin for filing Redis Bug / RCA Jiras from Zendesk PDFs, plus 8-130 impact score estimation. Standards-aligned, dry-run-by-default, no Jira API tokens needed (uses the claude.ai Atlassian MCP).

> 📣 **Looking for the team-friendly one-pager?** → [`SHARING.md`](./SHARING.md) (also published to [Confluence](https://redislabs.atlassian.net/wiki/spaces/CS/pages/6290243622))
>
> **Marketplace overview** (umbrella, contribution guide): [`../../README.md`](../../README.md) · [`../../SHARING.md`](../../SHARING.md)

## What it does

Four slash commands:

| Command | Purpose |
|---|---|
| `/tse-jira:new` | Interactive router — asks Bug / RCA / Impact Score, then walks you through |
| `/tse-jira:bug` | Bug Jira from one or more Zendesk PDFs |
| `/tse-jira:rca` | Multi-cluster RCA by cloning the canonical RCA-41 template |
| `/tse-jira:score` | Impact Score estimation (read-only) |

Every Bug / RCA workflow defaults to dry-run — writes a local markdown + Jira-styled HTML preview first; you review in your browser, then say `publish this preview` to actually file. Each command also drops into interactive mode when invoked without args.

## Install (5 steps, ~3 minutes)

### Step 1 — Prerequisites

| Need | How |
|---|---|
| Claude Code installed | macOS: `brew install --cask claude-code` · other OS: [claude.ai/code](https://claude.ai/code) |
| Signed into Claude Code as Redis | `/login` → `@redis.com` Google account |
| claude.ai Atlassian MCP authenticated | `/mcp` → find `Atlassian` → `Authenticate` → Redis Labs Atlassian account |

Verify Atlassian is connected:

```
mcp__claude_ai_Atlassian__getAccessibleAtlassianResources
```

→ should return `redislabs.atlassian.net` (id `06f73ca7-8f2c-4392-b40a-08288e9d0ba3`).

### Step 2 — Install the plugin

```
/plugin marketplace add markotrapani/redis-tse-tools
/plugin install tse-jira
/reload-plugins
```

### Step 3 — Add the safety net (strongly recommended)

**What it does.** Tells Claude Code "before running any Jira/Confluence write, pause and ask me to approve." It's a backstop independent of the plugin's own dry-run logic — even if the plugin (or any other Claude Code agent) ever tries to fire a write you didn't expect, you get a chance to refuse.

**Why you want it.** The plugin already requires you to say the word `publish` before it writes anything. The safety net is a second layer: it catches the case where the plugin's logic is bypassed (a future bug, an unusual prompt that confuses the agent, an entirely different plugin that also uses the Atlassian MCP). Two layers, both have to fail for an unintended write to land.

**What you'll see at use time.** When the plugin fires `createJiraIssue` (or any of the other write tools), Claude Code pauses and asks something like:

```
Run mcp__claude_ai_Atlassian__createJiraIssue?
[1] approve once   [2] approve for this session   [3] deny
```

You confirm. One click per write — minimal friction, large peace of mind.

**How to set it up.** Open `~/.claude/settings.json` in your editor and merge in this `permissions.ask` block (create the file if it doesn't exist, or add the entries if `permissions.ask` already exists):

```jsonc
{
  "permissions": {
    "ask": [
      // 6 Jira write tools
      "mcp__claude_ai_Atlassian__createJiraIssue",
      "mcp__claude_ai_Atlassian__editJiraIssue",
      "mcp__claude_ai_Atlassian__transitionJiraIssue",
      "mcp__claude_ai_Atlassian__addCommentToJiraIssue",
      "mcp__claude_ai_Atlassian__createIssueLink",
      "mcp__claude_ai_Atlassian__addWorklogToJiraIssue",
      // 4 Confluence write tools
      "mcp__claude_ai_Atlassian__createConfluencePage",
      "mcp__claude_ai_Atlassian__updateConfluencePage",
      "mcp__claude_ai_Atlassian__createConfluenceFooterComment",
      "mcp__claude_ai_Atlassian__createConfluenceInlineComment"
    ]
  }
}
```

The list covers the 10 Atlassian *write* operations the plugin (or any other agent) might call. Read operations (search, get, list) are not in the list — those don't change anything, no prompt needed.

Full rationale and threat model: [`../../SECURITY.md`](../../SECURITY.md).

### Step 4 — Verify

```
/plugin
```
Should list `tse-jira (0.14.2)` enabled.

```
/tse-jira:new
```
Should ask "Bug / RCA / Impact Score?" via an interactive prompt. Cancel — install verified.

### Step 5 — First use

Pick a Zendesk PDF you've downloaded. Then:

```
/tse-jira:bug ~/Downloads/path/to/your-zendesk-ticket.pdf
```

The plugin reads the PDF + any sibling screenshots, auto-detects customer / project / related Jiras, asks you for severity, optionally walks the relevant codebase, then **writes a dry-run preview** at `~/tse-jira-previews/...` and auto-opens the HTML in your browser. **No MCP writes yet.**

Review the preview. If it looks right, reply:

```
publish this preview
```

The skill asks one final confirmation, then fires `createJiraIssue` + `createIssueLink` calls (your harness prompts per the safety net). You get back the new Jira key + a checklist of remaining manual steps (file attachments, Impact Score Sheet screenshot paste).

## Common usage

```
# Interactive router (recommended starting point)
/tse-jira:new

# Direct CLI form — default dry-run
/tse-jira:bug   <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+]
/tse-jira:rca   <zendesk-pdfs>+  -- <jira-pdfs-or-keys>+
/tse-jira:score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]

# Publish: actually file (harness prompts per write call)
/tse-jira:bug   <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+] --publish
/tse-jira:rca   <zendesk-pdfs>+  -- <jira-pdfs-or-keys>+ --publish
```

For the full per-workflow walkthrough, see [`SHARING.md`](./SHARING.md). For the underlying skill instructions, see [`skills/tse-jira-ticket-creation/SKILL.md`](./skills/tse-jira-ticket-creation/SKILL.md).

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Unknown command: /tse-jira:bug` | Plugin not loaded | `/plugin marketplace update redis-tse-tools` → `/plugin install tse-jira` → `/reload-plugins` |
| `getAccessibleAtlassianResources` empty / errors | Atlassian MCP not authenticated | `/mcp` → re-authenticate `Atlassian` with `@redis.com` |
| "Affected Organizations not auto-resolved" in pre-flight | Customer name didn't surface in first 5 pages of the 9,253-option dropdown | Jira still creates; manually pick the customer in the Affected Orgs dropdown from the browser post-publish |
| `createJiraIssue` rejected: "Operation value must be an Atlassian Document" | Custom textarea field passed a string instead of ADF | Plugin bug — file an issue. Workaround: drop the field, add manually in browser. |
| `createJiraIssue` rejected: "Seen By Customer is required" | Production validation rule | Plugin auto-populates `customfield_10027`. If you still hit it, the customer name is non-standard — pick from dropdown in browser. |
| `publish this preview` said but nothing fires | Skill needs the literal word `publish` — "yes" / "go" don't count | Reply with a message containing `publish` |
| Want to file against a non-RED/MOD/DOC/RDSC project | Plugin supports interactive override | After project auto-detection, override with any project key (`OPCR`, `IR`, `PRB`, etc.) |
| Multi-account auth confusion (personal vs Redis) | `~/.claude/` is shared across identities | See [`SHARING.md`](./SHARING.md) → "What if I want to do personal Claude Code work alongside Redis?" for `CLAUDE_CONFIG_DIR` profile separation |

## More

- **Full skill instructions:** [`skills/tse-jira-ticket-creation/SKILL.md`](./skills/tse-jira-ticket-creation/SKILL.md)
- **Field reference:** [`skills/tse-jira-ticket-creation/references/jira-schema.md`](./skills/tse-jira-ticket-creation/references/jira-schema.md)
- **Impact Score model:** [`skills/tse-jira-ticket-creation/references/impact-score-model.md`](./skills/tse-jira-ticket-creation/references/impact-score-model.md)
- **Future direction:** [`ROADMAP.md`](./ROADMAP.md)
- **Team-friendly one-pager** (also published to Confluence): [`SHARING.md`](./SHARING.md)
- **JIRA Admin requests we're waiting on:** [`JIRA_ADMIN_REQUESTS/`](./JIRA_ADMIN_REQUESTS/)
