# `tse-jira` — Claude Code plugin for filing Redis Jiras from Zendesk

> **One-pager designed for sharing with the Redis CS / Support team.** Copy this into a Confluence page, Slack thread, or email. Self-contained.
>
> `tse-jira` is one plugin in the [**redis-tse-tools**](../../SHARING.md) Claude Code marketplace — the umbrella for TSE-focused Claude Code plugins maintained by the CS team. See the marketplace doc for what else is in there and how to add your own plugin.
>
> 🌐 **Also available in Confluence** (CS space → Support Tools → Redis TSE Tools): [tse-jira — Claude Code plugin for filing Jiras from Zendesk](https://redislabs.atlassian.net/wiki/spaces/CS/pages/6290243622). The repo version (this file) is the canonical source; Confluence mirrors it.

---

## What is it?

A Claude Code plugin that turns a Zendesk PDF (and optionally a few related Jira keys) into a complete, standards-compliant Redis Jira Bug or RCA. Reviews the draft locally first, then files via the claude.ai Atlassian MCP — no Jira API tokens to manage.

**Three workflows:**

| Slash command | What it does | Inputs |
|---|---|---|
| `/tse-jira:new` | Interactive router — asks Bug / RCA / Impact Score, then walks you through | (no args; asks for everything) |
| `/tse-jira:bug` | Bug Jira from Zendesk PDF | ≥1 Zendesk PDF (+ optional related Jiras) |
| `/tse-jira:rca` | Multi-cluster RCA by cloning RCA-41 | ≥1 Zendesk PDF AND ≥1 related Jira |
| `/tse-jira:score` | Impact score estimation (read-only) | ≥1 Jira (PDF or key) |

**Dry-run by default.** Every bug/RCA writes a local markdown + Jira-styled HTML preview first. You review in your browser, then say `publish this preview` to actually file.

---

## Why use it?

- **Standards-aligned by default.** Fields filled per [Redis CS Jira creation guide](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958). `CS` / `Support` labels, severity TSE-judged, priority left at Medium, sprint blank.
- **Multi-project.** Auto-detects RED / MOD / DOC / RDSC from ticket content. Works on any project you have access to.
- **Real Jira UI layout.** Description body holds narrative only; Workaround / Impact Score details / Action Items go in their dedicated custom-field sections (corrected v0.13).
- **Auto-infers related Jiras** from PDF text + Glean Search.
- **Codebase-grounded "Possible Root Cause"** (optional) — walks the Redis-owned source tree at the customer's reported version to ground hypotheses in real file:line refs.
- **8-130 Impact Score** auto-computed using the [DevOps impact score model](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553) — flagged as recommendation, team leader confirms.
- **Humility with R&D.** Code-level hypotheses framed as "Possible Root Cause (TSE hypothesis — please verify)" with a one-line AI-acknowledgment. "Asks for R&D" instead of "Suggested Fix".

---

## Install (5 steps, ~3 minutes)

### Step 1 — Prerequisites

- **Claude Code** installed. macOS: `brew install --cask claude-code`. Other OS: [claude.ai/code](https://claude.ai/code).
- **Signed into Claude Code with your `@redis.com` account.**
- **claude.ai Atlassian MCP authenticated.** In Claude Code: `/mcp` → find `Atlassian` → `Authenticate` → sign in with your Redis Labs Atlassian account.

Verify Atlassian:
```
mcp__claude_ai_Atlassian__getAccessibleAtlassianResources
```
→ should return `redislabs.atlassian.net` with id `06f73ca7-8f2c-4392-b40a-08288e9d0ba3`.

### Step 2 — Install the plugin

In Claude Code:

```
/plugin marketplace add markotrapani/redis-tse-tools
/plugin install tse-jira
/reload-plugins
```

### Step 3 — Add the safety net (strongly recommended)

Add this to your `~/.claude/settings.json` so Claude Code prompts before any Atlassian write call:

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

### Step 4 — Verify

```
/plugin
```
Should list `tse-jira (0.14.1)` enabled. Then:

```
/tse-jira:new
```
You should see "Bug / RCA / Impact Score?" — that's the router. Cancel the flow (Ctrl+C) — install verified.

### Step 5 — First use

Pick a Zendesk PDF you've downloaded for a real or test ticket. In Claude Code:

```
/tse-jira:bug ~/Downloads/path/to/your-zendesk-ticket.pdf
```

The plugin will:
1. Read the PDF + sibling screenshots
2. Auto-detect customer, project, related Jiras
3. Ask you for severity + clarifications
4. Optionally walk the relevant codebase
5. **Write a dry-run preview** at `~/tse-jira-previews/...{md,html}` and auto-open the HTML in your browser
6. **STOP** — no MCP writes yet

If the preview looks right, reply:

```
publish this preview
```

It'll fire `createJiraIssue` + `createIssueLink` calls (you'll get a permission prompt per call from the safety net). You get back the new Jira key + a checklist of remaining manual steps (file attachments, Impact Score Sheet screenshot paste).

---

## Common questions

**Q: What if I'm not sure which subcommand to use?**
Just run `/tse-jira:new` — it's the interactive router. Walks you through everything.

**Q: Will it accidentally file a Jira?**
No. Dry-run is the default. To publish you have to say a message containing the literal word `publish`. Even then, the safety net prompts per write call.

**Q: What if my Zendesk PDF has customer-provided screenshots?**
The skill auto-detects sibling images (PNG/JPG/GIF/WEBP) in the same directory and inserts paste-here markers at the right spots in the description. You drag-and-drop the images in the browser post-create.

**Q: What about Azure ACRE / AMR tickets?**
Supported. The skill detects Azure signals and adds `Azure-Integration` + `ACRE`/`AMR` labels, plus populates the RCA template section 0 for the customer-facing Microsoft automation.

**Q: Does it post a comment with the impact score breakdown?**
**No (as of v0.13).** That was old guidance. The breakdown goes in the `customfield_10681` (Impact Score details) field — the dedicated Jira UI section below the description. The TSE pastes a Google Sheet row screenshot into that field after publish.

**Q: Can I file against a project that isn't RED/MOD/DOC/RDSC?**
Yes. After project auto-detection, you can override with any project key (`OPCR`, `IR`, `PRB`, etc.). The skill fetches field metadata dynamically.

**Q: What if I want to do personal Claude Code work alongside Redis?**
Use the `CLAUDE_CONFIG_DIR` env var per-profile. Add shell aliases to `~/.zshrc`:

```bash
claude-redis() { CLAUDE_CONFIG_DIR="$HOME/.claude-redis" command claude "$@"; }
claude-personal() { CLAUDE_CONFIG_DIR="$HOME/.claude-personal" command claude "$@"; }
```

Then bootstrap each profile from your current state (only once):

```bash
cp -R ~/.claude ~/.claude-redis
cp ~/.claude.json ~/.claude-redis/.claude.json
mkdir -p ~/.claude-personal
```

Now `claude-redis` opens a Redis-authed session; `claude-personal` opens a fresh personal-account session. Independent profiles, no cross-contamination.

---

## Help, feedback, contributions

- **Found a bug or have a suggestion?** Post in the Redis CS team Slack channel or file an issue at https://github.com/markotrapani/redis-tse-tools/issues.
- **Want to read the full skill instructions?** [`skills/tse-jira-ticket-creation/SKILL.md`](./skills/tse-jira-ticket-creation/SKILL.md).
- **Want to see what's coming?** [`ROADMAP.md`](./ROADMAP.md).
- **Want the full feature reference + troubleshooting table?** [`README.md`](../../README.md).

---

## Quick links

- **Marketplace repo:** https://github.com/markotrapani/redis-tse-tools
- **Plugin docs:** [`SKILL.md`](./skills/tse-jira-ticket-creation/SKILL.md)
- **Impact Score Sheet:** https://docs.google.com/spreadsheets/d/13HQaZGXtsRi0hWxqU0oQXTmQw1LfnnrkBGl3Y5-c1Sk/edit?gid=0#gid=0
- **Jira creation guide (Confluence):** https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958
- **Impact Score doc (Confluence):** https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553
- **RCA procedure (Confluence):** https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753

---

*Plugin author: Marko Trapani (marko.trapani@redis.com), Redis Technical Support Engineer III. Distributed under MIT license. Last updated 2026-05-13 for v0.14.1.*
