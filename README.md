# redis-tse-tools

Umbrella **Claude Code marketplace** for Redis Technical Support Engineers. Hosts one or more plugins that extend Claude Code with TSE-focused workflows.

> 📣 **Just want to use it?**
> - **In Confluence (CS space → Support Tools):** [Redis TSE Tools — Claude Code marketplace for the CS team](https://redislabs.atlassian.net/wiki/spaces/CS/pages/6290178075)
> - **Contribution / sharing doc in this repo:** [`SHARING.md`](./SHARING.md)
>
> For a specific plugin's install + usage docs, follow the plugin link in the table below.

## Plugins

| Plugin | Version | Purpose | Plugin docs |
|---|---|---|---|
| [`tse-jira`](./plugins/tse-jira/) | v0.14.2 | File Bug / RCA Jiras from Zendesk PDFs; compute 8-130 impact scores. Real-Jira-UI-aware, dry-run-by-default. | [README](./plugins/tse-jira/README.md) · [SHARING](./plugins/tse-jira/SHARING.md) · [SKILL](./plugins/tse-jira/skills/tse-jira-ticket-creation/SKILL.md) · [ROADMAP](./plugins/tse-jira/ROADMAP.md) |

## Install the marketplace

In Claude Code:

```
/plugin marketplace add markotrapani/redis-tse-tools
```

That registers the marketplace. Then install whichever plugin(s) you want — each plugin's own README has install + first-use steps:

```
/plugin install tse-jira
/reload-plugins
```

## Contributing — adding a new plugin

See [`SHARING.md`](./SHARING.md) → "Adding a new plugin to the marketplace" for the 5-step contribution guide (directory structure, `plugin.json` template, `marketplace.json` registration, local testing, PR flow).

## Repo layout

```
redis-tse-tools/
├── .claude-plugin/marketplace.json          ← lists all plugins
├── plugins/<plugin-name>/                   ← each plugin is self-contained
│   ├── .claude-plugin/plugin.json
│   ├── README.md                            ← plugin install + usage
│   ├── SHARING.md                           ← Confluence-mirror team distribution doc
│   ├── ROADMAP.md
│   ├── commands/                            ← /slash-command files
│   ├── skills/                              ← SKILL.md(s) + references
│   └── scripts/                             ← (optional) helper scripts
├── README.md                                ← you are here (marketplace level)
├── SHARING.md                               ← marketplace-level team distribution doc
├── SECURITY.md
└── LICENSE
```

## License

MIT — see [LICENSE](./LICENSE).

## Author

Marko Trapani &lt;marko.trapani@redis.com&gt; — Redis Technical Support Engineer III
