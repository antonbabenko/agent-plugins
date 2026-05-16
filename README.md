# agent-plugins

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Anton Babenko's collection of agent skills and plugins for AI coding agents
(Claude Code, Cursor, Copilot, Gemini CLI, OpenCode, Codex). It is a single
Claude Code marketplace; each plugin is independent and versioned separately.
Plugins are either **external** (referenced from their own repo) or **inline**
(content lives here).

## Plugins

| Plugin | Type | Description |
|--------|------|-------------|
| [terraform-skill](https://github.com/antonbabenko/terraform-skill) | external | Writing, reviewing, and debugging Terraform/OpenTofu modules, tests, CI, scans, and state ops. Pinned via `source.ref`. |

## Installation

### Claude Code

```bash
/plugin marketplace add antonbabenko/agent-plugins
/plugin install terraform-skill@antonbabenko
```

Install any other plugin the same way: `/plugin install <plugin>@antonbabenko`.

### Other agents

Plugins follow the [Agent Skills](https://agentskills.io) layout
(`skills/<name>/SKILL.md`). Clone the repo and point your host at the plugin
directory, for example:

```bash
git clone https://github.com/antonbabenko/agent-plugins.git
# Claude Code (manual): symlink a plugin into ~/.claude/plugins
ln -s "$(pwd)/agent-plugins/plugins/terraform-skill" ~/.claude/plugins/terraform-skill
```

For per-host instructions (Cursor, Copilot, Gemini CLI, OpenCode, Codex,
Antigravity) see that plugin's `SKILL.md` and the
[Agent Skills](https://agentskills.io) docs.

## Versioning

Each plugin is released independently.

- **External plugins** release in their own repos and are pinned here by
  `source.ref` in `.claude-plugin/marketplace.json`.
- **Inline plugins** release from this repo: a push to `master` with a
  plugin-scoped conventional commit (e.g. `feat(<plugin>): ...`) bumps only
  that plugin and tags it `<plugin>-vX.Y.Z`.

See [CLAUDE.md](CLAUDE.md) for the full release model.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CLAUDE.md](CLAUDE.md). Report bugs
or request features via
[GitHub Issues](https://github.com/antonbabenko/agent-plugins/issues).

## License

Apache 2.0. See [LICENSE](LICENSE).
