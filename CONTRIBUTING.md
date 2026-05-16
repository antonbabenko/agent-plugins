# Contributing to agent-plugins

Thanks for helping improve these agent plugins. This repo is a multi-plugin
marketplace; read [CLAUDE.md](CLAUDE.md) for the architecture, content
standards, and the per-plugin release model before contributing.

## Quick Start

1. Fork the repository.
2. Create a feature branch.
3. Make changes following the guidelines below.
4. Test your changes (see Testing).
5. Open a pull request (the template is enforced).

## When to Contribute

**Good contributions:**

- ✅ New plugins that are useful, self-contained skills
- ✅ New best practices with community consensus
- ✅ Corrections to outdated or incorrect information
- ✅ Sharper organization, better examples, clearer structure
- ✅ Version-specific updates for tools a plugin targets

**Not suitable:**

- ❌ Personal preferences without community consensus
- ❌ Untested content changes (show baseline -> improved evidence)
- ❌ Content that merely duplicates existing agent knowledge
- ❌ Hand-edited version numbers (CI owns them)

## Adding a Plugin

**External** (content + releases in its own repo) — manifest entry only:

1. Add a `plugins[]` entry to `.claude-plugin/marketplace.json`: `name`,
   `source: { "source": "github", "repo": "owner/repo", "ref": "vX.Y.Z" }`,
   `description`, optional `category` / `keywords`, optional `version`
   (manual mirror of the ref).
2. No local content, CHANGELOG, tests, or scoped-commit release. Update by
   bumping `source.ref` (and the mirrored `version`).

**Inline** (content lives here):

1. `plugins/<plugin>/skills/<plugin>/SKILL.md` with valid frontmatter
   (`name`, `description`; optional `metadata.version`).
2. Add a `plugins[]` entry: `name`, `source: ./plugins/<plugin>`,
   `description`, `version` (`0.1.0`), optional `category` / `keywords`.
3. `plugins/<plugin>/CHANGELOG.md` (may be empty; CI prepends to it).
4. The manifest `version` must equal the SKILL.md `metadata.version` (and the
   `.codex-plugin/plugin.json` `version`, if the plugin ships one). CI
   enforces this.
5. `plugins/<plugin>/tests/baseline-scenarios.md` is **required** and
   CI-enforced (see Testing). It must contain at least one `## Scenario ...`,
   a `## Running These Tests` protocol, and a `### Success Criteria` list.

See CLAUDE.md "SKILL.md Architecture" and the "LLM Consumption Rules" for
content shape and token discipline.

## Commits & Releases

Releases are automated and **per-plugin, for inline plugins only**. A commit
qualifies for a plugin when it changes release-worthy content under
`plugins/<plugin>/` (anything except `tests/` and the CI-managed
`CHANGELOG.md`), or when its subject is scoped to that plugin
(`feat(<plugin>): ...`, back-compat). The commit **type** sets the bump.
External plugins release upstream; update them here by bumping `source.ref`.

| Qualifying commit type | Result |
|------------------------|--------|
| `feat: ...` (or scoped) | minor bump |
| `fix:` / `perf:` / `refactor:` (or scoped) | patch bump |
| `feat!:` or `BREAKING CHANGE:` in body | major bump |
| `chore`/`docs`/`ci`/`test`, or no conventional type | no release |
| touches only `tests/`, `CHANGELOG.md`, or no plugin content | no release |

PRs are squash-merged, so the squash subject's type plus the changed paths
drive the release; set the subject type deliberately. A squash touching two
plugins bumps both.

## Testing

Tests are **required**, not optional. This is documentation, not code, so
"tests" are behavioral regression scenarios run against a real agent host.

**Every inline plugin must ship `plugins/<plugin>/tests/baseline-scenarios.md`**
with this structure (CI fails the PR if it is missing or incomplete):

```text
# Baseline Scenarios
<intro: compare WITHOUT vs WITH the skill>

## Running These Tests
<the WITHOUT -> WITH -> compare -> gate protocol>

## Scenario 1: <name>
### Test Prompt
### Expected Baseline Behavior (WITHOUT skill)
### Target Behavior (WITH skill)
### Pressure Variations
### Success Criteria        <- checkbox list, the pass/fail bar
## Scenario 2: ...
```

`plugins/code-intelligence/tests/baseline-scenarios.md` is the canonical
example - copy its shape.

**Every content PR must:**

1. First validate locally with the commands in
   [CLAUDE.md](CLAUDE.md#validation).
2. Run the scenarios per that file's `## Running These Tests`: capture each
   prompt's output with the plugin OFF (baseline), then ON (target).
3. Confirm every scenario meets its `### Success Criteria` and introduces no
   new rationalizations. A single failing scenario blocks the PR.
4. When a PR adds or changes a behavior, add or update a scenario so the
   behavior stays covered.
5. Paste the baseline and target transcripts into the PR template (or `/tmp`) -
   never commit them under `plugins/`.

## CI

`validate.yml` runs on every PR touching `plugins/**` or `.claude-plugin/**`:
frontmatter, size, **inline plugin tests present** (baseline-scenarios.md with
scenarios + run protocol + success criteria), manifest validity, manifest <->
SKILL.md <-> `.codex-plugin/plugin.json` version sync, broken links, and
markdown lint.

Every step in **Validate Skill Files** is blocking - markdown lint included
(no `continue-on-error`). One red step fails the whole check.

Merge policy: **do not merge a PR with a red `Validate Skill Files`.** This is
enforced by policy and the visible failing check, not by a server-side merge
block - the per-plugin release pipeline pushes version bumps straight to
`master`, so a hard required-status-check on the branch would also block
releases. Treat a red check as a hard stop anyway; fix it before merge.

## Reporting Issues

Use [GitHub Issues](https://github.com/antonbabenko/agent-plugins/issues).
Include the plugin name, your agent host, and a reproducible prompt.
