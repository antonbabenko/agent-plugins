# Agent Plugins for AI Coding Agents

[![Agent Skills](https://img.shields.io/badge/Agent-Skills-5865F2)](https://agentskills.io)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-marketplace-D97757)](https://code.claude.com/docs/en/plugins-reference)
[![Codex](https://img.shields.io/badge/Codex-marketplace-000000)](https://github.com/openai/codex)
[![CI](https://github.com/antonbabenko/agent-plugins/actions/workflows/validate.yml/badge.svg)](https://github.com/antonbabenko/agent-plugins/actions/workflows/validate.yml)

Executable discipline for AI coding agents (Claude Code, Cursor, Copilot,
Gemini CLI, OpenCode, Codex) - skills the agent loads on demand and applies
while **it works**, not prose guides _it ignores_.

Agent Plugins is a plugin marketplace for Claude Code and OpenAI Codex.

## Install

### npx skills - recommended for any Agent Skills host

Works with any compatible agent (Claude Code, Cursor, Copilot, Gemini CLI, OpenCode, Codex, and more). Each command is independent - run the one(s) you want:

```bash
# code-intelligence (this repo's inline skill)
npx skills add https://github.com/antonbabenko/agent-plugins

# terraform-skill (its own repo)
npx skills add https://github.com/antonbabenko/terraform-skill
```

### Claude Code

```bash
/plugin marketplace add antonbabenko/agent-plugins

/plugin install code-intelligence@antonbabenko
/plugin install terraform-skill@antonbabenko
/plugin install claude-delegator@antonbabenko
```

### Codex

```bash
codex plugin marketplace add antonbabenko/agent-plugins
```

Then run `codex`, open `/plugins`, select **Agent Plugins**, and install
`code-intelligence`, `terraform-skill`, or `claude-delegator`.

For other hosts, expand below.

<!-- prettier-ignore-start -->

<details>
<summary>Gemini CLI</summary>

External plugin (`terraform-skill`) installs as an extension from its own repo:

```bash
gemini extensions install https://github.com/antonbabenko/terraform-skill
```

The inline `code-intelligence` has no standalone repo. Clone the Agent Plugins
repo and point Gemini at `plugins/code-intelligence` per Gemini's
skill-discovery docs, or install it through Claude Code or Codex.
</details>

<details>
<summary>Cursor</summary>

```bash
# external plugin (terraform-skill) - from its own repo
git clone https://github.com/antonbabenko/terraform-skill.git ~/.cursor/skills/terraform-skill

# inline plugin (code-intelligence) - from this repo
git clone https://github.com/antonbabenko/agent-plugins.git
ln -s "$(pwd)/agent-plugins/plugins/code-intelligence" ~/.cursor/skills/code-intelligence
```

Cursor auto-discovers skills from `.agents/skills/` and `.cursor/skills/`.
</details>

<details>
<summary>Copilot</summary>

```bash
git clone https://github.com/antonbabenko/terraform-skill.git ~/.copilot/skills/terraform-skill
git clone https://github.com/antonbabenko/agent-plugins.git
ln -s "$(pwd)/agent-plugins/plugins/code-intelligence" ~/.copilot/skills/code-intelligence
```

Copilot auto-discovers skills from `.copilot/skills/`.
</details>

<details>
<summary>OpenCode</summary>

```bash
git clone https://github.com/antonbabenko/terraform-skill.git ~/.agents/skills/terraform-skill
git clone https://github.com/antonbabenko/agent-plugins.git
ln -s "$(pwd)/agent-plugins/plugins/code-intelligence" ~/.agents/skills/code-intelligence
```

OpenCode auto-discovers skills from `.agents/skills/`, `.opencode/skills/`, and
`.claude/skills/`.
</details>

<details>
<summary>Codex (OpenAI) - clone fallback</summary>

Prefer the Codex marketplace block above. Plain skills-directory fallback:

```bash
git clone https://github.com/antonbabenko/terraform-skill.git ~/.agents/skills/terraform-skill
git clone https://github.com/antonbabenko/agent-plugins.git
ln -s "$(pwd)/agent-plugins/plugins/code-intelligence" ~/.agents/skills/code-intelligence
```

Codex auto-discovers skills from `~/.agents/skills/` and `.agents/skills/`.
Update with `git pull` in each clone.
</details>

<details>
<summary>Antigravity</summary>

```bash
git clone https://github.com/antonbabenko/terraform-skill.git ~/.antigravity/skills/terraform-skill
git clone https://github.com/antonbabenko/agent-plugins.git
ln -s "$(pwd)/agent-plugins/plugins/code-intelligence" ~/.antigravity/skills/code-intelligence
```

Update with `git pull` in each clone.
</details>

<details>
<summary>Kiro (Powers)</summary>

These skills are also [Kiro Powers](https://kiro.dev/docs/powers/) (a
`POWER.md` generated from the same `SKILL.md` - shared content, not forked).
In Kiro: **Powers panel → "Add power from GitHub"**, then paste:

```text
# terraform-skill (root POWER.md; bundles optional read-only terraform-mcp-server)
https://github.com/antonbabenko/terraform-skill

# code-intelligence (POWER.md under the plugin subdir)
https://github.com/antonbabenko/agent-plugins/tree/master/plugins/code-intelligence
```

Kiro activates a power on keyword match (e.g. "terraform", "lsp", "rename").

> Notes. Kiro installs a power from a GitHub repo URL, not from a marketplace
> manifest - the `.kiro/plugins/marketplace.json` in this repo mirrors the
> `.agents`/`.claude-plugin` manifests for pin-sync parity only; Kiro does not
> consume it for install today. Kiro discovering a `POWER.md` under a
> subdirectory (the `code-intelligence` path above) is the documented install
> shape; if your Kiro build only accepts a repo-root `POWER.md`, clone the repo
> and install `code-intelligence` from the local `plugins/code-intelligence`
> path instead.

</details>

<details>
<summary>Manual (Claude Code - symlink a local clone)</summary>

```bash
git clone https://github.com/antonbabenko/agent-plugins.git
mkdir -p ~/.claude/plugins
# inline plugins live under plugins/<name>/
ln -s "$(pwd)/agent-plugins/plugins/code-intelligence" ~/.claude/plugins/code-intelligence
```

Claude Code autodiscovers `skills/<name>/SKILL.md` on next launch. Edits to the
clone are picked up live. External plugins (e.g. `terraform-skill`) are not in
this repo - install them from their own repo instead.
</details>

<!-- prettier-ignore-end -->

## Plugins

### code-intelligence

> Stops blind text-replace renames and "the tool is broken" guesses: the agent picks language-server vs text vs fuzzy search correctly for the task, and says so on the first line when it has to swap one tool for another.

**tldr** - what changes with the plugin:

| Prompt | Without the plugin | With the plugin |
|--------|--------------------|-----------------|
| Rename `var.tags` to `var.resource_tags` across the module | Blind `grep`/replace - misses position scoping, collides with same-named symbols in child modules, no post-edit validate | terraform-ls has no rename provider, so it runs the safe manual workflow: `findReferences` at an anchored position -> fresh per-file Read -> edit -> `validate` |
| Find every reference to `aws_s3_bucket.this` before changing it | One regex; may over/under-match, then claims "found all" | Position-anchored `findReferences`; on an uninitialized workspace it says so on line 1 and discloses the `rg` fallback |
| `rg` looks missing so the agent reaches for `grep` | Silent tool swap - you never learn coverage dropped | Proves the tool is really absent first; states the substitution on the first line |

The semantic rows above need a language server installed (here `terraform-ls`).
Without one the plugin still helps: it discloses the `rg` fallback on the first
line instead of pretending the text search was exhaustive. Check your setup
with `/code-intelligence:setup-code-intelligence`.

```bash
/plugin install code-intelligence@antonbabenko
```

Try:

- `I need to change var.vpc_id - what references it?`
- `Where does local.name_prefix come from?`
- `What can I set on this aws_s3_bucket resource?`
- `Is output.cluster_endpoint used anywhere before I change its type?`
- `Did you really find all the references, or just text matches?`

Check your setup (Claude Code): `/code-intelligence:setup-code-intelligence`

### [terraform-skill](https://github.com/antonbabenko/terraform-skill)

> Routes a Terraform or OpenTofu request to its real failure mode - identity churn, secret exposure, blast radius, state corruption - before generating code, instead of emitting plausible-looking HCL that breaks on apply.

**tldr** - what changes with the plugin:

| Prompt | Without the plugin | With the plugin |
|--------|--------------------|-----------------|
| Create a VPC module | Plausible HCL, no tests, no version guards | Routes to the failure mode first; module + native tests + version-aware guards |
| Configure S3 backend with state locking | May emit DynamoDB locking (outdated) | TF 1.10+ S3 native `use_lockfile`; flags DynamoDB as no longer required |
| Change a resource's address | Text rename -> destroy/recreate on apply | `moved` block + `plan` shows 0 destroy; blast radius checked before generating code |

```bash
/plugin install terraform-skill@antonbabenko
# or, on any Agent Skills host:
npx skills add https://github.com/antonbabenko/terraform-skill
```

Try:

- `Create a VPC module with native tests`
- `Configure S3 backend with state locking`

Source and detail: [github.com/antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill).
The full per-host install list lives in that repo's README.

### [claude-delegator](https://github.com/antonbabenko/claude-delegator)

> Gives the agent five GPT (Codex), Gemini, and Grok (xAI) expert subagents - it
> delegates the hard call (architecture, plan review, scope, code review,
> security) instead of guessing alone, and synthesizes the result rather than
> pasting it raw.

**tldr** - what changes with the plugin:

| Prompt | Without the plugin | With the plugin |
|--------|--------------------|-----------------|
| Is this auth flow secure? | One model's single take | Security Analyst expert reviews; verdict synthesized, not raw |
| Review this migration plan | Self-review, same blind spots | Plan Reviewer expert validates before you execute |
| Get GPT, Gemini, and Grok to agree on this design | Manual back-and-forth | `consensus` runs an arbiter-mediated GPT + Gemini + Grok + Claude loop to a signed-off plan |

Each expert runs advisory (read-only) or implementation (`workspace-write`).

```bash
/plugin install claude-delegator@antonbabenko
/claude-delegator:setup
```

Requires at least one provider: [Codex CLI](https://github.com/openai/codex), [~~Gemini~~ Antigravity CLI](https://antigravity.google/docs/gcli-migration), or [Grok (xAI)](https://docs.x.ai/overview); `/setup` guides you through it. Grok is advisory-only (it reviews and votes but cannot change files and write code).

Bundled commands:

### 🔥 Magic happens here 🔥

- `/claude-delegator:consensus` - arbiter-mediated GPT + Gemini + Grok + Claude convergence loop. Relentlessly arguing, as if they have nothing else to do!

### Ask once

- `/claude-delegator:ask-gpt` - one-shot GPT (Codex) second opinion
- `/claude-delegator:ask-gemini` - one-shot Gemini second opinion
- `/claude-delegator:ask-grok` - one-shot Grok (xAI) second opinion (advisory-only)
- `/claude-delegator:ask-all` - GPT + Gemini + Grok in parallel, synthesized

### Setup and Maintainance

- `/claude-delegator:setup` - configure Codex/Gemini/Grok MCP servers + rules
- `/claude-delegator:uninstall` - remove MCP config, rules, and aliases
- `/claude-delegator:grok-files` - list or prune Grok-uploaded files (storage cleanup)

Use `consensus` when the plan must be right - the external models vote and
Claude adjudicates to agreement, ideal for high-stakes planning and design. Use
the `ask-*` commands for a quicker single or parallel opinion when you just want
a fast second take.

`/setup` can also install short aliases (`/ask-gpt`, `/ask-gemini`, `/ask-grok`,
`/ask-all`, `/consensus`, `/grok-files`); opt-in, never overwrites an existing
command.

Source and detail: [github.com/antonbabenko/claude-delegator](https://github.com/antonbabenko/claude-delegator).

## Why these plugins

- **Honest by construction.** Any tool substitution or skipped step is stated
  on the first line of the response, so you can trust what the agent reports.
- **Token-lean.** A short `SKILL.md` routes to reference files that load only
  when the task needs them. The agent does not carry the whole guide in
  context.
- **Portable.** One discipline across Claude Code, Cursor, Copilot, Antigravity CLI,
  OpenCode, and Codex, with no per-host retraining.
- **Composable and pinned.** Generic skills give the base discipline; domain
  skills extend it. Each plugin is released independently, so upgrading one
  never moves another.

## Author

Built and maintained by Anton Babenko - [LinkedIn](https://linkedin.com/in/antonbabenko), [X/Twitter](https://x.com/antonbabenko).

## Contributing

The model and the test requirements are in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0. See [LICENSE](LICENSE).
