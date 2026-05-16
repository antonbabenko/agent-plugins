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

Works with any compatible agent (Claude Code, Cursor, Copilot, Gemini CLI, OpenCode, Codex, and more):

```bash
npx skills add https://github.com/antonbabenko/terraform-skill
```

### Claude Code

```bash
/plugin marketplace add antonbabenko/agent-plugins

/plugin install code-intelligence@antonbabenko
/plugin install terraform-skill@antonbabenko
```

### Codex

```bash
codex plugin marketplace add antonbabenko/agent-plugins
```

Then run `codex`, open `/plugins`, select **Agent Plugins**, and install
`code-intelligence` or `terraform-skill`.

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

> Do not also add `antonbabenko/terraform-skill` as a marketplace. It uses the
> same marketplace name as this repo and the two will clash. Install
> `terraform-skill` from here, or as a standalone skill from its own repo - not
> both.

## Plugins

### code-intelligence

> Stops blind text-replace renames and "the tool is broken" guesses: the agent picks language-server vs text vs fuzzy search correctly for the task, and says so on the first line when it has to swap one tool for another.

```bash
/plugin install code-intelligence@antonbabenko
```

Try:

- `Rename the vpc_id variable across this Terraform module`
- `Find every reference to aws_s3_bucket.this before I change it`

Check your setup (Claude Code): `/code-intelligence:doctor`

### [terraform-skill](https://github.com/antonbabenko/terraform-skill)

> Routes a Terraform or OpenTofu request to its real failure mode - identity churn, secret exposure, blast radius, state corruption - before generating code, instead of emitting plausible-looking HCL that breaks on apply.

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

## Why these plugins

- **Honest by construction.** Any tool substitution or skipped step is stated
  on the first line of the response, so you can trust what the agent reports.
- **Token-lean.** A short `SKILL.md` routes to reference files that load only
  when the task needs them. The agent does not carry the whole guide in
  context.
- **Portable.** One discipline across Claude Code, Cursor, Copilot, Gemini CLI,
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
