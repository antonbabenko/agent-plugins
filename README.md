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
| [code-intelligence](plugins/code-intelligence/skills/code-intelligence/SKILL.md) | inline | Language-agnostic code navigation discipline: when to use a language server vs exact-text vs fuzzy search, position-anchored LSP calls, a degradation gate, and first-line tool-substitution disclosure. |

## Why these plugins

These are not prose guides - they are executable discipline the agent loads on
demand and applies while it works.

- **Fewer wrong tools, fewer silent failures.** `code-intelligence` stops the
  common failure modes directly: blind text-replace renames, accepting "the
  tool is broken" without proof, presenting a keyword grep as a complete
  answer. `terraform-skill` routes a request to its actual failure mode
  (identity churn, secret exposure, blast radius, state corruption) before
  generating code.
- **Honest by construction.** Any tool substitution or skipped step is stated
  on the first line of the response, not buried later - so you can trust what
  the agent says it did.
- **Token-lean.** Progressive disclosure: a short `SKILL.md` entry point routes
  to reference files that load only when the task needs them. The agent does
  not carry the whole guide in context.
- **Portable.** One discipline across Claude Code, Cursor, Copilot, Gemini CLI,
  OpenCode, and Codex - no per-host retraining.
- **Composable and pinned.** Generic skills (`code-intelligence`) provide the
  base discipline; domain skills (`terraform-skill`) extend it. Each plugin is
  versioned and released independently, so an upgrade to one never moves
  another.

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
# Inline plugins live under plugins/<name>/ - symlink one into ~/.claude/plugins:
ln -s "$(pwd)/agent-plugins/plugins/code-intelligence" ~/.claude/plugins/code-intelligence
# External plugins (e.g. terraform-skill) are not in this repo - install them
# from their own repo / marketplace ref instead.
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
