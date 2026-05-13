# `redis-tse-tools` — Claude Code marketplace for the Redis CS / Support team

> **One-pager designed for sharing with the Redis CS / Support team.** Copy this into a Confluence page, Slack thread, or email. Self-contained.
>
> This is the **umbrella marketplace doc**. For details on a specific plugin, follow the link in the table below.
>
> 🌐 **Also available in Confluence** (CS space → Support Tools): [Redis TSE Tools — Claude Code marketplace for the CS team](https://redislabs.atlassian.net/wiki/spaces/CS/pages/6290178075). The repo version (this file) is the canonical source; Confluence mirrors it.

---

## What is it?

`redis-tse-tools` is a **Claude Code marketplace** — a Git repo Claude Code can fetch from to install one or more **plugins**. Each plugin is a self-contained bundle of slash commands, skills, and references that extend Claude Code with TSE-focused workflows.

**Why a marketplace and not just one plugin?** Because TSE work spans many domains — Jira filing, RCA drafting, support-package analysis, Grafana dashboards, K8s troubleshooting, etc. Each can be its own plugin, versioned and installable independently. The marketplace is the umbrella that lets the team:

1. **Discover** what TSE-focused Claude Code tooling exists.
2. **Install** any combination of plugins with two commands.
3. **Contribute** new plugins for novel workflows without disrupting existing ones.

---

## Currently available plugins

| Plugin | Latest version | Purpose | Plugin doc |
|---|---|---|---|
| `tse-jira` | v0.14.1 | File Bug / RCA Jiras from Zendesk PDFs; compute 8-130 impact scores. Real-Jira-UI-aware, dry-run-by-default. | [`plugins/tse-jira/SHARING.md`](./plugins/tse-jira/SHARING.md) |
| *(more to come — RCA tooling, support-package analyzers, Grafana helpers, etc.)* | — | — | — |

---

## Installing the marketplace (one-time, 30 seconds)

In Claude Code:

```
/plugin marketplace add markotrapani/redis-tse-tools
```

That registers the marketplace. Then install whichever plugins you want:

```
/plugin install tse-jira
/reload-plugins
```

For full TSE-specific install steps (prerequisites, safety net, verification, first-use walkthrough), see the plugin's own SHARING doc — e.g., [`plugins/tse-jira/SHARING.md`](./plugins/tse-jira/SHARING.md).

---

## Adding a new plugin to the marketplace

If you build a Claude Code plugin that helps the TSE team and want to distribute it through this marketplace, the process is:

### Step 1 — Build the plugin in a fork / branch

Each plugin lives in `plugins/<plugin-name>/` and is fully self-contained. The minimal structure:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # name + version + description + author
├── commands/                # /slash-command markdown files (with frontmatter)
├── skills/                  # SKILL.md(s) — workflow instructions
│   └── <skill-name>/
│       ├── SKILL.md
│       └── references/      # field IDs, canonical examples, templates
├── scripts/                 # (optional) helper scripts (Python, shell)
├── ROADMAP.md               # (optional) forward-looking plan
└── SHARING.md               # 60-second TSE-facing distribution doc
```

`plugin.json` minimal contents:

```jsonc
{
  "name": "<plugin-name>",
  "version": "0.1.0",
  "description": "What this plugin does, in one sentence.",
  "author": { "name": "Your Name", "email": "your.email@redis.com" },
  "homepage": "https://github.com/markotrapani/redis-tse-tools",
  "repository": "https://github.com/markotrapani/redis-tse-tools",
  "license": "MIT",
  "keywords": ["..."]
}
```

### Step 2 — Register the plugin in `.claude-plugin/marketplace.json`

Add an entry to the `plugins` array:

```jsonc
{
  "plugins": [
    { /* existing tse-jira entry */ },
    {
      "name": "<plugin-name>",
      "source": "./plugins/<plugin-name>",
      "description": "What this plugin does.",
      "version": "0.1.0",
      "category": "support",
      "tags": ["..."]
    }
  ]
}
```

Bump the marketplace `metadata.version` too.

### Step 3 — Test locally before shipping

In Claude Code:

```
/plugin marketplace update redis-tse-tools
/plugin install <plugin-name>
/reload-plugins
```

Verify the plugin loads, slash commands resolve, and the skill activates. Iterate.

### Step 4 — PR or push to main

Open a pull request against the `redis-tse-tools` repo (or commit directly if you have write access). Once merged, anyone who has `/plugin marketplace update redis-tse-tools` configured will see the new plugin available.

### Step 5 — Write a SHARING.md for your plugin

Follow the [`plugins/tse-jira/SHARING.md`](./plugins/tse-jira/SHARING.md) template:

- What the plugin does (3-4 sentences)
- Why use it (a few bullets)
- Install (5-step flow)
- First use walkthrough
- Common questions
- Quick links

This is what teammates will see in your plugin's Confluence sub-page.

---

## Conventions across plugins in this marketplace

To keep things consistent for the TSE team:

- **Dry-run by default.** Any plugin that writes to Jira / Confluence / external systems should default to a local-preview mode and require explicit user authorization before firing writes.
- **Real-Jira-UI awareness.** Plugins that create Jiras should put metadata content (Workaround, Impact Score details, etc.) in the **dedicated custom-field sections**, not duplicated as description-body H2s. See `tse-jira` v0.13 for the canonical implementation.
- **Standards-aligned defaults.** Field choices should match the [Redis CS Jira creation guide](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958) and other Confluence-documented Support team practices.
- **Permissions-aware.** TSEs are encouraged to add Atlassian write tools to `permissions.ask` in `~/.claude/settings.json`. Plugins should respect that and not bypass via `--no-verify`-style flags.
- **PII guard.** If a plugin reads customer PDFs and writes anywhere external, it should detect / flag PII (phone numbers, internal customer emails) before posting.
- **Memory-friendly.** When a plugin learns user preferences via Claude Code memory, those preferences should be plugin-scoped (named in a way that makes the source clear, e.g., `feedback-<plugin>-<topic>.md`).

---

## Architecture / repo

- **Repo:** https://github.com/markotrapani/redis-tse-tools
- **Marketplace manifest:** `.claude-plugin/marketplace.json` (lists all plugins + their source paths)
- **Plugin manifest:** `plugins/<name>/.claude-plugin/plugin.json` (per-plugin)
- **License:** MIT (per `LICENSE`)
- **Maintainer:** Marko Trapani (marko.trapani@redis.com), Redis Technical Support Engineer III

The marketplace currently versions as `v0.14.1` (matching the latest plugin release).

---

## Quick links

- **Marketplace repo:** https://github.com/markotrapani/redis-tse-tools
- **Marketplace README** (full feature reference, troubleshooting): [`README.md`](./README.md)
- **`tse-jira` plugin doc:** [`plugins/tse-jira/SHARING.md`](./plugins/tse-jira/SHARING.md)
- **Issue tracker:** https://github.com/markotrapani/redis-tse-tools/issues

---

## Help, feedback, contributions

- **Found a bug or have a suggestion for an existing plugin?** Post in the Redis CS team Slack channel or file an issue at https://github.com/markotrapani/redis-tse-tools/issues.
- **Want to add a new plugin?** Follow the steps above, then open a PR. Happy to pair on it if you're new to Claude Code plugin authoring.
- **Want to share this with someone outside the CS team?** The repo is currently maintained on Marko's personal GitHub. Future state: migrate to a Redis-organization GitHub if uptake grows beyond the CS team.

---

*Marketplace maintained by Marko Trapani (marko.trapani@redis.com). Distributed under MIT license. Last updated 2026-05-13 for v0.14.1.*
