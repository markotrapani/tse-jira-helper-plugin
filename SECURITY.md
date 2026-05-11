# Security & Safety Guarantees

This plugin writes to `redislabs.atlassian.net` — a shared production system. Mistakes are expensive (R&D noise, customer-visible bugs, audit trail issues). The plugin uses a **two-layer protection model** to make those mistakes hard.

## Layer 1 — Harness-level (Claude Code `permissions.ask`)

**This is the strong guarantee.** Even if the skill instructions are misread, Claude Code will refuse to call the listed tools without prompting you first.

### Setup

Add the following to your `~/.claude/settings.json` under `"permissions"`:

```jsonc
{
  "permissions": {
    "ask": [
      "mcp__claude_ai_Atlassian__createJiraIssue",
      "mcp__claude_ai_Atlassian__editJiraIssue",
      "mcp__claude_ai_Atlassian__createIssueLink",
      "mcp__claude_ai_Atlassian__addCommentToJiraIssue",
      "mcp__claude_ai_Atlassian__transitionJiraIssue",
      "mcp__claude_ai_Atlassian__addWorklogToJiraIssue",
      "mcp__claude_ai_Atlassian__createConfluencePage",
      "mcp__claude_ai_Atlassian__updateConfluencePage",
      "mcp__claude_ai_Atlassian__createConfluenceFooterComment",
      "mcp__claude_ai_Atlassian__createConfluenceInlineComment"
    ]
  }
}
```

**Merge with your existing settings — don't replace.** If you already have a `"permissions"` block, add the `"ask"` array alongside your existing `"allow"` and `"deny"` arrays.

### What this does

- `"ask"` = Claude Code prompts you Allow / Deny / Deny+Reason on each individual call to one of these 10 tools.
- The skill **cannot bypass this** — the permission check happens at the harness layer, before the MCP request fires.
- Read-only Atlassian tools (`getJiraIssue`, `getJiraProjectIssueTypesMetadata`, `searchJiraIssuesUsingJql`, etc.) are unaffected — only writes ask.

### Caveat: `defaultMode: "bypassPermissions"`

If your `~/.claude/settings.json` has `"defaultMode": "bypassPermissions"`, specific `ask` rules should still take precedence — but if you ever observe a write going through without a prompt, switch to one of:

- `"defaultMode": "default"` (prompt for unknown tools, respect explicit allow/ask/deny)
- Move the 10 tools from `"ask"` to `"deny"` and explicitly remove from deny when you want to publish

### Alternative: full deny

If you want an even stronger guarantee (i.e., no writes possible without you first editing `settings.json`), use `"deny"` instead of `"ask"`. The downside is more friction — you have to edit settings to publish each time.

## Layer 2 — Skill-level (dry-run default + explicit "publish" keyword)

The `tse-jira-ticket-creation` skill defaults to **dry-run mode**. In dry-run:

- The skill produces a markdown preview file at `~/tse-jira-previews/<project>-<workflow>-<timestamp>.md`
- The preview mimics the Jira issue view (header, description, custom fields, comment, links) plus an appendix with the raw API payloads
- **No MCP write tool is called**

To convert a dry-run into a publish, you must either:

1. Invoke the slash command with the `--publish` flag, OR
2. After reviewing the preview file, send a message containing the word **"publish"** referring to the preview (e.g., "publish this preview", "publish ~/tse-jira-previews/RED-bug-...md")

**Implicit confirmations are not enough.** The skill is documented to reject `yes`, `go`, `looks good`, `proceed` as ambiguous and ask for a publish keyword explicitly. This rule is in the skill's [memory feedback file](https://github.com/markotrapani/redis-tse-tools) (a prior session bug led to this guardrail).

## Layer 3 — Audit trail

Every preview file (both dry-run and publish) is saved to `~/tse-jira-previews/`. After a publish, the file is amended with an "Actual API responses" section showing:

- New Jira key
- Comment id
- Each issue link's outcome
- Edit results (for Azure post-save step)

So even successful publishes leave a local record you can audit later.

## Threat model & what this does NOT protect against

- **Compromised local machine.** Anyone with write access to your `~/.claude/settings.json` can disable the protection. The skill's dry-run rule is also just a markdown file — anyone modifying it can change behavior.
- **MCP server impersonation.** This plugin trusts the claude.ai Atlassian MCP. If that's compromised, the protection above doesn't help.
- **Authenticated-as-other-user mistakes.** The skill uses your Jira identity. If you're authenticated as a high-privilege account, the protection limits what you accidentally fire — but not what you can intentionally do.
- **Read access.** The plugin reads `getJiraIssue`, project schemas, customer dropdowns, etc. without prompts. If you're concerned about read-side data exposure, separately deny those tools.

## Reporting issues

If you find a way to bypass the dry-run / publish-keyword rule, open an issue on [github.com/markotrapani/redis-tse-tools](https://github.com/markotrapani/redis-tse-tools) — the failure mode is worth documenting and patching.
